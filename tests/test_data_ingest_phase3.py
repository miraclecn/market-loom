import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

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


def test_init_creates_placeholder_config_without_real_credentials(tmp_path: Path):
    result = _run_cli("init", "--workspace", str(tmp_path))

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["workspace"] == str(tmp_path)
    assert len(payload["actions"]) == 3

    env_path = tmp_path / ".env"
    config_path = tmp_path / "config" / "data_sources.toml"
    gitkeep_path = tmp_path / "output" / ".gitkeep"
    assert env_path.is_file()
    assert config_path.is_file()
    assert gitkeep_path.is_file()

    env_text = env_path.read_text(encoding="utf-8")
    assert "Market Loom" in env_text
    assert "TUSHARE_TOKEN=your_token_here" in env_text
    assert "alpha-find-v2" not in env_text
    assert "/home/nan" not in env_text


def test_load_data_sources_config_from_init_template(tmp_path: Path):
    init_result = _run_cli("init", "--workspace", str(tmp_path))
    assert init_result.returncode == 0, init_result.stderr

    from market_loom.data_ingest.config_models import load_data_sources_config

    config = load_data_sources_config(tmp_path / "config" / "data_sources.toml")
    assert config.schema_version == 1
    assert config.adapters["tushare"].enabled is True
    assert "daily" in config.enabled_datasets()
    assert config.priority("daily") == ("tushare", "akshare")


def test_sync_dry_run_uses_ingest_layer_and_writes_no_real_data(tmp_path: Path):
    init_result = _run_cli("init", "--workspace", str(tmp_path))
    assert init_result.returncode == 0, init_result.stderr

    result = _run_cli(
        "sync",
        "--dry-run",
        "--raw-db",
        str(tmp_path / "raw.duckdb"),
        "--config",
        str(tmp_path / "config" / "data_sources.toml"),
        "--only",
        "daily",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["success_count"] == 0
    assert payload["failed_count"] == 0
    assert payload["results"]
    assert {item["status"] for item in payload["results"]} == {"skipped"}
    assert not (tmp_path / "raw.duckdb").exists()


def test_optional_adapters_fail_clearly_when_dependency_missing(monkeypatch):
    import builtins

    from market_loom.data_ingest.adapters.akshare_adapter import AKShareAdapter
    from market_loom.data_ingest.adapters.base import AdapterUnavailable

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "akshare":
            raise ImportError("missing akshare")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    adapter = AKShareAdapter(symbols=["000001"])

    with pytest.raises(AdapterUnavailable, match="akshare package not installed"):
        list(adapter.fetch("daily", since="20240101", until="20240102", full=False))
