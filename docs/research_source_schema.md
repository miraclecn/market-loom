# Market Loom Research Source Schema

Market Loom builds a DuckDB research-source database with `market-loom build-research-source-db`. Python callers can use the `market_loom.market_data_bootstrap` module.

## Build Command

```bash
market-loom build-research-source-db \
  --source-db output/demo/raw.duckdb \
  --target-db output/demo/research_source.duckdb \
  --supplemental-db output/demo/supplemental.duckdb
```

## Stable Tables And Views

- `security_master_ref`
- `market_trade_calendar`
- `name_change_history`
- `daily_bar_pit`
- `tradeability_state_daily`
- `stock_bar_normalized_daily`
- `industry_classification_pit`
- `corporate_action_ledger`
- `corporate_action_exception_ledger`
- `dataset_registry`
- `data_spine_registry`
- `build_chain_registry`
- `data_boundary_registry`

## Normalized Bar Contract

`stock_bar_normalized_daily` exposes:

```text
trade_date
code
open
high
low
close
prev_close
volume
amount
turnover_rate
is_st
is_paused
limit_up
limit_down
industry_code
industry_name
```

Run the contract checker after building:

```bash
market-loom check-research-source-contract --db output/demo/research_source.duckdb
```

## Price Basis Rules

- Raw unadjusted rows use source OHLC multiplied by `adj_factor` for adjusted diagnostic fields.
- qfq fallback rows keep qfq prices as the same-basis OHLC values.
- `prev_close` is previous normalized close when available.
- `limit_up` and `limit_down` are normalized to the same price basis as OHLC.

## Industry Rules

- Missing industry maps to `UNKNOWN`.
- Missing `industry_name` falls back to `industry_code`.
- Multiple PIT levels are reduced to one canonical level per bar.

## Python Access

```bash
python - <<'PY'
from market_loom.market_data_bootstrap import build_research_source_db
print(build_research_source_db("output/demo/raw.duckdb", "output/demo/research_source.duckdb", "output/demo/supplemental.duckdb"))
PY
```
