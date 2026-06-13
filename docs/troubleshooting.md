# Market Loom Troubleshooting

Use `market-loom` for CLI commands and `market_loom` for Python imports.

## Command Not Found

Install the project in editable mode:

```bash
python -m pip install -e ".[dev]"
market-loom --help
```

## Import Errors

Check that the active Python environment can import `market_loom`:

```bash
python - <<'PY'
import market_loom
print(market_loom.__version__)
PY
```

## DuckDB Lock Errors

Run write commands sequentially. `market-loom audit-market-data-quality` materializes quality flags and needs write access to the DuckDB file.

## Missing Provider Packages

Provider packages are optional:

```bash
python -m pip install -e ".[providers]"
```

Use the no-token demo when you want to avoid provider SDKs:

```bash
python examples/demo_fixture/build_demo.py
```

## Contract Check Fails

Run:

```bash
market-loom inspect-db --db output/demo/research_source.duckdb
market-loom check-research-source-contract --db output/demo/research_source.duckdb
```

Confirm `daily_bar_pit`, `tradeability_state_daily`, and `stock_bar_normalized_daily` exist and contain the required normalized columns.

## Quality Audit Has Warnings

Warnings such as `MISSING_LIMIT`, `MISSING_INDUSTRY_CODE`, `INCOMPLETE_TRADING_DATE`, and `UNRESOLVED_ADJ_FACTOR_JUMP` are expected in the synthetic demo. Downstream consumers should read `data_quality_usability_flags`.
