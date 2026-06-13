import json
import os
import subprocess
import sys
from pathlib import Path

import duckdb

SRC_PATH = Path(__file__).resolve().parents[1] / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from market_loom.contracts import NORMALIZED_STOCK_BAR_COLUMNS
from market_loom.market_data_bootstrap import build_research_source_db
from market_loom.market_data_quality import materialize_data_quality_usability_flags
from market_loom.research_source_contract import check_research_source_contract
from tests.fixtures.research_source_fixture import create_research_source_fixture


def _env() -> dict[str, str]:
    return {**os.environ, "PYTHONPATH": str(SRC_PATH)}


def _run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "market_loom.cli", *args],
        check=False,
        text=True,
        capture_output=True,
        env=_env(),
    )


def _build_fixture(tmp_path: Path) -> Path:
    source_db = tmp_path / "raw.duckdb"
    supplemental_db = tmp_path / "supplemental.duckdb"
    target_db = tmp_path / "research_source.duckdb"
    create_research_source_fixture(source_db, supplemental_db)
    build_research_source_db(source_db, target_db, supplemental_db)
    return target_db


def test_stock_bar_normalized_daily_schema_prev_close_and_limit_basis(tmp_path: Path):
    db_path = _build_fixture(tmp_path)
    conn = duckdb.connect(str(db_path), read_only=True)
    try:
        columns = [
            row[1]
            for row in conn.execute("PRAGMA table_info('stock_bar_normalized_daily')").fetchall()
        ]
        assert columns == NORMALIZED_STOCK_BAR_COLUMNS

        prev_close = conn.execute(
            """
            SELECT prev_close
            FROM stock_bar_normalized_daily
            WHERE code='000001.SZ' AND trade_date='20240103'
            """
        ).fetchone()[0]
        assert abs(prev_close - 15.3) < 1e-9

        mismatch_count = conn.execute(
            """
            WITH normalized AS (
                SELECT
                    code,
                    trade_date,
                    close,
                    prev_close,
                    lag(close) OVER (PARTITION BY code ORDER BY trade_date) AS previous_close
                FROM stock_bar_normalized_daily
            )
            SELECT count(*)
            FROM normalized
            WHERE previous_close IS NOT NULL
              AND abs(prev_close - previous_close) > 1e-9
            """
        ).fetchone()[0]
        assert mismatch_count == 0

        normalized_limits = conn.execute(
            """
            SELECT limit_up, limit_down
            FROM stock_bar_normalized_daily
            WHERE code='000001.SZ' AND trade_date='20240103'
            """
        ).fetchone()
        raw_limits = conn.execute(
            """
            SELECT up_limit, down_limit
            FROM tradeability_state_daily
            WHERE security_id='000001.SZ' AND trade_date='20240103'
            """
        ).fetchone()
        assert normalized_limits == (17.952, 14.688)
        assert raw_limits == (11.22, 9.18)
    finally:
        conn.close()


def test_qfq_fallback_limits_stay_on_fallback_price_basis(tmp_path: Path):
    source_db = tmp_path / "raw.duckdb"
    supplemental_db = tmp_path / "supplemental.duckdb"
    target_db = tmp_path / "research_source.duckdb"
    create_research_source_fixture(source_db, supplemental_db)

    conn = duckdb.connect(str(source_db))
    try:
        conn.execute(
            """
            INSERT INTO raw_stk_limit VALUES
            ('920001.BJ', '20240110', 18.39, 15.05, 'tushare.stk_limit',
             TIMESTAMP '2026-04-22 15:00:00')
            """
        )
    finally:
        conn.close()

    build_research_source_db(source_db, target_db, supplemental_db)
    conn = duckdb.connect(str(target_db), read_only=True)
    try:
        row = conn.execute(
            """
            SELECT n.close, n.limit_up, n.limit_down, d.adj_factor, d.price_basis
            FROM stock_bar_normalized_daily AS n
            INNER JOIN daily_bar_pit AS d
                ON d.security_id = n.code
               AND d.trade_date = n.trade_date
            WHERE n.code='920001.BJ' AND n.trade_date='20240110'
            """
        ).fetchone()
        assert row == (16.72, 18.39, 15.05, 1.1, "qfq_fallback")
    finally:
        conn.close()


def test_industry_unknown_name_fallback_and_single_canonical_level(tmp_path: Path):
    source_db = tmp_path / "raw.duckdb"
    supplemental_db = tmp_path / "supplemental.duckdb"
    target_db = tmp_path / "research_source.duckdb"
    create_research_source_fixture(source_db, supplemental_db)

    conn = duckdb.connect(str(supplemental_db))
    try:
        conn.execute("DELETE FROM industry_classification_pit WHERE security_id IN ('000001.SZ', '920001.BJ')")
        conn.execute("ALTER TABLE industry_classification_pit ADD COLUMN industry_name VARCHAR")
        conn.execute(
            """
            INSERT INTO industry_classification_pit (
                security_id, industry_schema, industry_code, effective_at, removed_at, industry_name
            ) VALUES
            ('000001.SZ', 'sw2021_l1', '801780.SI', '20200101', NULL, 'Bank L1'),
            ('000001.SZ', 'sw2021_l2', '801783.SI', '20200101', NULL, 'Bank L2'),
            ('000001.SZ', 'sw2021_l3', '857831.SI', '20200101', NULL, 'Bank L3'),
            ('300001.SZ', 'sw2021_l1', '801730.SI', '20200101', NULL, NULL)
            """
        )
    finally:
        conn.close()

    build_research_source_db(source_db, target_db, supplemental_db)
    conn = duckdb.connect(str(target_db), read_only=True)
    try:
        unknown_row = conn.execute(
            """
            SELECT industry_code, industry_name
            FROM stock_bar_normalized_daily
            WHERE code='920001.BJ' AND trade_date='20240110'
            """
        ).fetchone()
        assert unknown_row == ("UNKNOWN", "UNKNOWN")

        fallback_row = conn.execute(
            """
            SELECT industry_code, industry_name
            FROM stock_bar_normalized_daily
            WHERE code='300001.SZ' AND trade_date='20240102'
            """
        ).fetchone()
        assert fallback_row == ("801730.SI", "801730.SI")

        counts = conn.execute(
            """
            SELECT count(*), count(DISTINCT code || ':' || trade_date)
            FROM stock_bar_normalized_daily
            WHERE code='000001.SZ'
              AND trade_date BETWEEN '20240102' AND '20240103'
            """
        ).fetchone()
        canonical_row = conn.execute(
            """
            SELECT industry_code, industry_name
            FROM stock_bar_normalized_daily
            WHERE code='000001.SZ' AND trade_date='20240102'
            """
        ).fetchone()
        assert counts == (2, 2)
        assert canonical_row == ("801780.SI", "Bank L1")
    finally:
        conn.close()


def test_quality_flags_contract_quality_audit_and_cli_smoke(tmp_path: Path):
    db_path = _build_fixture(tmp_path)

    contract = check_research_source_contract(db_path)
    assert contract.ok is True

    materialize_data_quality_usability_flags(db_path)
    conn = duckdb.connect(str(db_path), read_only=True)
    try:
        issue_types = {
            row[0]
            for row in conn.execute(
                "SELECT DISTINCT issue_type FROM data_quality_usability_flags"
            ).fetchall()
        }
        assert "MISSING_LIMIT" in issue_types
        assert "MISSING_INDUSTRY_CODE" in issue_types
    finally:
        conn.close()

    contract_cli = _run_cli("check-research-source-contract", "--db", str(db_path))
    assert contract_cli.returncode == 0, contract_cli.stderr
    assert json.loads(contract_cli.stdout)["ok"] is True

    quality_dir = tmp_path / "quality"
    quality_cli = _run_cli("audit-market-data-quality", "--db", str(db_path), "--output-dir", str(quality_dir))
    assert quality_cli.returncode == 0, quality_cli.stderr
    payload = json.loads(quality_cli.stdout)
    assert payload["ok"] is True
    assert (quality_dir / "market_data_quality.json").is_file()
    assert (quality_dir / "bad_dates.csv").is_file()
    assert (quality_dir / "bad_symbols.csv").is_file()
    assert (quality_dir / "execution_restricted.csv").is_file()
