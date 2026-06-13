# Market Loom Dashboard

Market Loom can export or serve a local DuckDB dashboard through `market-loom`. The implementation lives in the `market_loom.dashboard` module.

## Export HTML

```bash
market-loom export-dashboard \
  --db output/demo/research_source.duckdb \
  --out output/demo/dashboard.html
```

Open `output/demo/dashboard.html` in a browser. The file is a local generated artifact and should not be committed.

## Serve Locally

```bash
market-loom serve \
  --db output/demo/research_source.duckdb \
  --host 127.0.0.1 \
  --port 8765
```

The server exposes:

- `/` for the HTML dashboard.
- `/api/summary` for a JSON summary.

## Dashboard Scope

The dashboard summarizes local DuckDB tables, row counts, layers, and column previews. It is for inspection, not strategy decisions, trading, or data redistribution.
