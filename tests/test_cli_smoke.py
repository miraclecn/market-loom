import subprocess
import sys
from pathlib import Path


def test_cli_help_runs():
    src_path = Path(__file__).resolve().parents[1] / "src"
    result = subprocess.run(
        [sys.executable, "-m", "market_loom.cli", "--help"],
        check=False,
        text=True,
        capture_output=True,
        env={"PYTHONPATH": str(src_path)},
    )

    assert result.returncode == 0
    assert "Market Loom" in result.stdout
    assert "--version" in result.stdout
