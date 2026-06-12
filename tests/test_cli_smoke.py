import json
import os
import subprocess
import sys
from pathlib import Path


REQUIRED_COMMANDS = [
    "init",
    "sync",
    "audit-data",
    "build-reference-staging-db",
    "build-research-source-db",
    "audit-market-data-quality",
    "check-research-source-contract",
    "export-normalized-bars",
    "inspect-db",
    "export-dashboard",
    "serve",
]


def _env() -> dict[str, str]:
    src_path = Path(__file__).resolve().parents[1] / "src"
    return {**os.environ, "PYTHONPATH": str(src_path)}


def _run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "market_loom.cli", *args],
        check=False,
        text=True,
        capture_output=True,
        env=_env(),
    )


def test_cli_help_runs():
    result = _run_cli("--help")

    assert result.returncode == 0
    assert "Market Loom" in result.stdout
    assert "--version" in result.stdout


def test_cli_help_exposes_phase_2_command_surface_without_old_names():
    result = _run_cli("--help")

    assert result.returncode == 0
    for command in REQUIRED_COMMANDS:
        assert command in result.stdout
    assert "alpha-data-local" not in result.stdout
    assert "Alpha Data Local" not in result.stdout
    assert "alpha_data_local" not in result.stdout


def test_cli_version_runs_without_old_names():
    result = _run_cli("--version")

    assert result.returncode == 0
    assert "market-loom 0.1.0" in result.stdout
    assert "alpha" not in result.stdout.lower()


def test_contract_command_is_wired_and_reports_missing_default_db():
    result = _run_cli("check-research-source-contract")

    assert result.returncode == 1
    assert "database does not exist" in result.stderr
    assert "ModuleNotFoundError" not in result.stderr
