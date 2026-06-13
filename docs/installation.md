# Market Loom Installation

Market Loom uses `market-loom` for the CLI and `market_loom` for Python imports.

## Requirements

- Python 3.11 or newer.
- A local checkout of the Market Loom repository.
- DuckDB is installed through the Python package dependencies.

## Development Install

```bash
python -m pip install -U pip
python -m pip install -e ".[dev]"
market-loom --help
```

## Provider Extras

Provider SDKs are optional. Install them only for real ingestion work:

```bash
python -m pip install -e ".[providers]"
```

The no-token demo does not require provider extras:

```bash
python examples/demo_fixture/build_demo.py
```

## Python Import Check

```bash
python - <<'PY'
import market_loom
print(market_loom.__version__)
PY
```

## Generated Files

Generated DuckDB databases, exports, dashboards, and audits belong under `output/` and are ignored by git.
