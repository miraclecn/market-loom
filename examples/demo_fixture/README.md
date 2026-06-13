# Demo Fixture

This fixture builds a no-token synthetic Market Loom demo under `output/demo/`.
It does not call provider SDKs, read credentials, or include real market data.

Run from the repository root:

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

The synthetic fixture includes normal daily OHLCV bars, an ST-name window,
a full-day suspension, official limit data, qfq fallback rows, missing and
fallback industry labels, multiple industry levels, an incomplete trading date,
and an unresolved adjustment-factor jump for quality-audit demonstration.
