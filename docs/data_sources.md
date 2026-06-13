# Market Loom Data Sources

Market Loom accepts local provider data through the `market-loom` CLI and stores it in DuckDB. The Python package is `market_loom`.

## Source Layers

- Raw provider layer: localized tables such as `stock_basic_ref`, `raw_kline_unadj`, `raw_kline_qfq`, `raw_adj_factor`, `raw_daily_basic`, and optional event tables.
- Supplemental PIT layer: optional tables such as `industry_classification_pit`, benchmark membership, benchmark weights, and index reference data.
- Research-source layer: derived public contracts such as `daily_bar_pit`, `tradeability_state_daily`, `stock_bar_normalized_daily`, and `data_quality_usability_flags`.

## Demo Data

The demo fixture creates synthetic source data:

```bash
python examples/demo_fixture/build_demo.py
market-loom build-research-source-db \
  --source-db output/demo/raw.duckdb \
  --target-db output/demo/research_source.duckdb \
  --supplemental-db output/demo/supplemental.duckdb
```

## Provider Data

Market Loom can be wired to supported provider SDKs through the ingestion commands, but provider accounts, credentials, rate limits, and data licenses are the user's responsibility.

```bash
market-loom init --workspace .
market-loom sync --raw-db output/raw.duckdb --config config/data_sources.toml --dry-run
market-loom audit-data --raw-db output/raw.duckdb --out-dir output/audit
```

## Data Boundary

Do not commit provider tokens, generated DuckDB files, exported data, or local configuration containing secrets. Market Loom does not grant redistribution rights for third-party data.
