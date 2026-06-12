import json
import os
import subprocess
import sys
from pathlib import Path

import duckdb

SRC_PATH = Path(__file__).resolve().parents[1] / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))


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


def _create_contract_db(path: Path) -> None:
    conn = duckdb.connect(str(path))
    try:
        conn.execute("CREATE TABLE daily_bar_pit (security_id VARCHAR, trade_date VARCHAR)")
        conn.execute("INSERT INTO daily_bar_pit VALUES ('000001.SZ', '20240102')")
        conn.execute(
            """
            CREATE TABLE tradeability_state_daily (
                security_id VARCHAR,
                trade_date VARCHAR,
                is_suspended BOOLEAN,
                up_limit DOUBLE,
                down_limit DOUBLE,
                source_priority VARCHAR
            )
            """
        )
        conn.execute(
            """
            INSERT INTO tradeability_state_daily VALUES
            ('000001.SZ', '20240102', FALSE, NULL, NULL, 'official')
            """
        )
        conn.execute(
            """
            CREATE TABLE corporate_action_ledger (
                action_id VARCHAR,
                security_id VARCHAR,
                action_type VARCHAR,
                record_date VARCHAR,
                book_date VARCHAR,
                ex_date VARCHAR,
                cash_per_share DOUBLE,
                share_ratio DOUBLE,
                source_table VARCHAR
            )
            """
        )
        conn.execute(
            """
            CREATE VIEW stock_bar_normalized_daily AS
            SELECT
                '20240102'::VARCHAR AS trade_date,
                '000001.SZ'::VARCHAR AS code,
                10.0::DOUBLE AS open,
                10.5::DOUBLE AS high,
                9.5::DOUBLE AS low,
                10.2::DOUBLE AS close,
                10.0::DOUBLE AS prev_close,
                1000.0::DOUBLE AS volume,
                10000.0::DOUBLE AS amount,
                1.2::DOUBLE AS turnover_rate,
                FALSE::BOOLEAN AS is_st,
                FALSE::BOOLEAN AS is_paused,
                NULL::DOUBLE AS limit_up,
                NULL::DOUBLE AS limit_down,
                'UNKNOWN'::VARCHAR AS industry_code,
                'UNKNOWN'::VARCHAR AS industry_name
            """
        )
    finally:
        conn.close()


def test_phase5_command_help_is_available():
    for command in ("audit-market-data-quality", "check-research-source-contract"):
        result = _run_cli(command, "--help")
        assert result.returncode == 0, result.stderr
        assert "Command unavailable" not in result.stdout
        assert command in result.stdout


def test_phase5_modules_import_and_preserve_issue_types():
    from market_loom.market_data_quality import DataQualityIssueType
    from market_loom.research_source_contract import check_research_source_contract

    assert callable(check_research_source_contract)
    assert {item.value for item in DataQualityIssueType} == {
        "MISSING_LIMIT",
        "UNRESOLVED_ADJ_FACTOR_JUMP",
        "MISSING_INDUSTRY_CODE",
        "INCOMPLETE_TRADING_DATE",
    }


def test_check_research_source_contract_cli_accepts_valid_fixture(tmp_path: Path):
    db_path = tmp_path / "research_source.duckdb"
    _create_contract_db(db_path)

    result = _run_cli("check-research-source-contract", "--db", str(db_path))

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["normalized_view"] == "stock_bar_normalized_daily"
    assert "industry_name" in payload["required_columns"]


def test_audit_market_data_quality_writes_json_and_output_dir_files(tmp_path: Path):
    db_path = tmp_path / "research_source.duckdb"
    output_dir = tmp_path / "quality"
    _create_contract_db(db_path)

    result = _run_cli("audit-market-data-quality", "--db", str(db_path), "--output-dir", str(output_dir))

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["output_dir"] == str(output_dir)
    assert (output_dir / "market_data_quality.json").is_file()
    assert (output_dir / "bad_dates.csv").is_file()
    assert (output_dir / "bad_symbols.csv").is_file()
    assert (output_dir / "execution_restricted.csv").is_file()

    audit_payload = json.loads((output_dir / "market_data_quality.json").read_text(encoding="utf-8"))
    assert audit_payload["summary"]["missing_limit_count"] >= 1
