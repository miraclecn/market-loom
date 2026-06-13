# Market Loom Provider Setup

Market Loom can run without provider credentials by using the synthetic demo. Provider setup is only needed when using `market-loom sync` against real provider SDKs. Python integrations import `market_loom`.

## No-Token Path

Use this path first:

```bash
python examples/demo_fixture/build_demo.py
market-loom build-research-source-db \
  --source-db output/demo/raw.duckdb \
  --target-db output/demo/research_source.duckdb \
  --supplemental-db output/demo/supplemental.duckdb
```

## Provider Extras

```bash
python -m pip install -e ".[providers]"
market-loom init --workspace .
```

`market-loom init` creates local templates. Edit local files outside version control or use environment variables for provider credentials.

## Dry Run Before Sync

```bash
market-loom sync \
  --raw-db output/raw.duckdb \
  --config config/data_sources.toml \
  --dry-run
```

## Operating Rules

- Keep credentials local.
- Respect provider licenses and rate limits.
- Do not commit provider output databases or exports.
- Do not use Market Loom to redistribute third-party data.
