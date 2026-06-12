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


def test_unmigrated_command_returns_clear_json_error():
    result = _run_cli("sync", "--dry-run")

    assert result.returncode == 2
    payload = json.loads(result.stdout)
    assert payload["command"] == "sync"
    assert payload["error"] == "Command unavailable in this migration phase"
    assert payload["available_after"] == "Phase 3"
    assert "ModuleNotFoundError" not in result.stderr
