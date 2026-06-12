# Market Loom

Market Loom is an open-source data foundation for local A-share market data ingestion, DuckDB research-source construction, point-in-time normalization, contract checking, data quality auditing, export, and local dashboard serving.

It is intended to be a reusable data infrastructure project. It is not a personal trading system and does not include private strategy code, account configuration, provider credentials, or real market data dumps.

## Boundary

Market Loom:

- is a data foundation;
- does not provide investment advice;
- does not generate trading signals;
- does not train models;
- does not run backtests;
- does not place orders;
- does not redistribute third-party market data.

Provider SDKs and market data access are the user's responsibility. Users must comply with the terms of their selected data providers.

## Install

```bash
python -m pip install -e ".[dev]"
```

Optional provider SDKs:

```bash
python -m pip install -e ".[providers]"
```

## CLI

```bash
market-loom --help
```

The current CLI includes local workspace initialization, ingestion dry runs, raw data sync wiring, raw data audit wiring, research-source DuckDB construction, reference staging, database inspection, contract checks, market-data quality audits, normalized bar export, dashboard export, and dashboard serving.

## Development

```bash
python -m pip install -e ".[dev]"
pytest -q
python -m compileall src
```

## License

Market Loom is licensed under Apache-2.0. See [LICENSE](LICENSE).
