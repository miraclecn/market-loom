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


def _create_summary_db(path: Path) -> None:
    conn = duckdb.connect(str(path))
    try:
        conn.execute("CREATE TABLE sample_prices (trade_date VARCHAR, code VARCHAR, close DOUBLE)")
        conn.execute("INSERT INTO sample_prices VALUES ('20240102', '000001.SZ', 10.5)")
    finally:
        conn.close()


def test_phase4_build_command_help_is_available():
    for command in ("build-research-source-db", "build-reference-staging-db"):
        result = _run_cli(command, "--help")
        assert result.returncode == 0, result.stderr
        assert "Command unavailable" not in result.stdout
        assert command in result.stdout


def test_phase4_modules_import_with_market_loom_names():
    import market_loom.dashboard as dashboard
    import market_loom.db_summary as db_summary
    import market_loom.market_data_bootstrap as bootstrap
    import market_loom.reference_data_staging as staging

    assert callable(bootstrap.build_research_source_db)
    assert callable(staging.build_tushare_reference_db)
    assert callable(db_summary.summarize_duckdb)
    assert callable(dashboard.write_dashboard)


def test_inspect_db_outputs_json_summary(tmp_path: Path):
    db_path = tmp_path / "summary.duckdb"
    _create_summary_db(db_path)

    result = _run_cli("inspect-db", "--db", str(db_path))

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["database_path"] == str(db_path)
    assert any(table["name"] == "sample_prices" for table in payload["tables"])


def test_export_dashboard_writes_html(tmp_path: Path):
    db_path = tmp_path / "summary.duckdb"
    html_path = tmp_path / "dashboard.html"
    _create_summary_db(db_path)

    result = _run_cli("export-dashboard", "--db", str(db_path), "--out", str(html_path))

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["output_path"] == str(html_path)
    html = html_path.read_text(encoding="utf-8")
    assert "Market Loom" in html
    assert "sample_prices" in html
