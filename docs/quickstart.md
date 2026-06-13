# Market Loom Quickstart

Market Loom is a local data-foundation toolkit for A-share ingestion, DuckDB research-source construction, point-in-time normalization, quality checks, exports, and dashboards. The CLI is `market-loom`; the Python package is `market_loom`.

Market Loom was split from alpha-data as the open-source data-foundation layer.

## Install

```bash
python -m pip install -e ".[dev]"
```

Install optional provider adapters only when you plan to call provider SDKs:

```bash
python -m pip install -e ".[providers]"
```

## Run The No-Token Demo

The demo uses synthetic data only and writes ignored outputs under `output/demo/`.

```bash
python examples/demo_fixture/build_demo.py

market-loom build-research-source-db \
  --source-db output/demo/raw.duckdb \
  --target-db output/demo/research_source.duckdb \
  --supplemental-db output/demo/supplemental.duckdb

market-loom check-research-source-contract \
  --db output/demo/research_source.duckdb

market-loom audit-market-data-quality \
  --db output/demo/research_source.duckdb

market-loom export-dashboard \
  --db output/demo/research_source.duckdb \
  --out output/demo/dashboard.html
```

## Useful Next Commands

```bash
market-loom --help
market-loom inspect-db --db output/demo/research_source.duckdb
market-loom export-normalized-bars --db output/demo/research_source.duckdb --format csv
```

## Boundary

Market Loom provides data contracts and quality evidence. It does not provide predictions, portfolio targets, orders, strategy rules, model training, live trading, or redistribution rights for third-party data.
