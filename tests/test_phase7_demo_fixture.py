import json
import os
import subprocess
import sys
from pathlib import Path

import duckdb

SRC_PATH = Path(__file__).resolve().parents[1] / "src"
REPO_ROOT = Path(__file__).resolve().parents[1]


def _env() -> dict[str, str]:
    return {**os.environ, "PYTHONPATH": str(SRC_PATH)}


def _run_python(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        check=False,
        text=True,
        capture_output=True,
        cwd=REPO_ROOT,
        env=_env(),
    )


def _run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return _run_python("-m", "market_loom.cli", *args)


def test_demo_fixture_builds_no_token_end_to_end_database(tmp_path: Path):
    output_dir = tmp_path / "demo"
    build_script = REPO_ROOT / "examples" / "demo_fixture" / "build_demo.py"

    build_result = _run_python(str(build_script), "--output-dir", str(output_dir))

    assert build_result.returncode == 0, build_result.stderr
    build_payload = json.loads(build_result.stdout)
    raw_db = output_dir / "raw.duckdb"
    supplemental_db = output_dir / "supplemental.duckdb"
    research_db = output_dir / "research_source.duckdb"
    assert build_payload == {
        "raw_db": str(raw_db),
        "supplemental_db": str(supplemental_db),
    }
    assert raw_db.is_file()
    assert supplemental_db.is_file()

    build_research = _run_cli(
        "build-research-source-db",
        "--source-db",
        str(raw_db),
        "--target-db",
        str(research_db),
        "--supplemental-db",
        str(supplemental_db),
    )
    assert build_research.returncode == 0, build_research.stderr

    contract = _run_cli("check-research-source-contract", "--db", str(research_db))
    assert contract.returncode == 0, contract.stderr
    assert json.loads(contract.stdout)["ok"] is True

    audit_dir = output_dir / "quality"
    audit = _run_cli(
        "audit-market-data-quality",
        "--db",
        str(research_db),
        "--output-dir",
        str(audit_dir),
    )
    assert audit.returncode == 0, audit.stderr
    audit_payload = json.loads(audit.stdout)
    assert audit_payload["ok"] is True
    summary = audit_payload["summary"]
    assert summary["missing_limit_count"] >= 1
    assert summary["missing_industry_code_count"] >= 1
    assert summary["incomplete_trading_date_count"] >= 1
    assert summary["unresolved_adj_factor_jump_count"] >= 1

    dashboard = _run_cli(
        "export-dashboard",
        "--db",
        str(research_db),
        "--out",
        str(output_dir / "dashboard.html"),
    )
    assert dashboard.returncode == 0, dashboard.stderr
    assert (output_dir / "dashboard.html").is_file()

    conn = duckdb.connect(str(research_db), read_only=True)
    try:
        scenarios = dict(
            conn.execute(
                """
                SELECT scenario, is_present
                FROM (
                    SELECT 'normal_bars' AS scenario, count(*) >= 1 AS is_present
                    FROM stock_bar_normalized_daily
                    WHERE code='000001.SZ' AND trade_date='20240102'
                    UNION ALL
                    SELECT 'st_flag', count(*) >= 1
                    FROM stock_bar_normalized_daily
                    WHERE code='300001.SZ' AND trade_date='20240103' AND is_st
                    UNION ALL
                    SELECT 'full_day_suspension', count(*) >= 1
                    FROM stock_bar_normalized_daily
                    WHERE code='300001.SZ' AND trade_date='20240104' AND is_paused
                    UNION ALL
                    SELECT 'limit_up_down', count(*) >= 1
                    FROM stock_bar_normalized_daily
                    WHERE code='000001.SZ' AND trade_date='20240103'
                      AND limit_up IS NOT NULL AND limit_down IS NOT NULL
                    UNION ALL
                    SELECT 'qfq_fallback', count(*) >= 1
                    FROM daily_bar_pit
                    WHERE security_id='920001.BJ' AND price_basis='qfq_fallback'
                    UNION ALL
                    SELECT 'unknown_industry', count(*) >= 1
                    FROM stock_bar_normalized_daily
                    WHERE code='920001.BJ' AND industry_code='UNKNOWN'
                    UNION ALL
                    SELECT 'industry_name_fallback', count(*) >= 1
                    FROM stock_bar_normalized_daily
                    WHERE code='300001.SZ'
                      AND industry_code='801730.SI'
                      AND industry_name='801730.SI'
                    UNION ALL
                    SELECT 'canonical_industry', count(*) = count(DISTINCT code || ':' || trade_date)
                    FROM stock_bar_normalized_daily
                    WHERE code='000001.SZ' AND trade_date='20240102'
                )
                """
            ).fetchall()
        )
    finally:
        conn.close()

    assert all(scenarios.values()), scenarios
