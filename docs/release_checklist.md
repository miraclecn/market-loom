# Market Loom Release Checklist

Run this checklist from a clean Market Loom checkout. The CLI is `market-loom`; the Python package is `market_loom`.

## Required Verification

```bash
pytest -q
market-loom --help
python examples/demo_fixture/build_demo.py
market-loom build-research-source-db --source-db output/demo/raw.duckdb --target-db output/demo/research_source.duckdb --supplemental-db output/demo/supplemental.duckdb
market-loom check-research-source-contract --db output/demo/research_source.duckdb
market-loom audit-market-data-quality --db output/demo/research_source.duckdb
market-loom export-normalized-bars --db output/demo/research_source.duckdb --format parquet
market-loom export-dashboard --db output/demo/research_source.duckdb --out output/demo/dashboard.html
```

## Boundary Review

- No generated DuckDB, Parquet, CSV, HTML dashboard, or audit output is staged.
- No provider credentials are staged.
- No downstream strategy, prediction, portfolio, order, model-training, or live execution logic is staged.
- `docs/consumer_contract.md` still lists fields intentionally outside Market Loom.

## Public Contract Review

Run:

```bash
market-loom check-research-source-contract --db output/demo/research_source.duckdb
```

Do not rename stable public tables or `stock_bar_normalized_daily` columns during a release.
