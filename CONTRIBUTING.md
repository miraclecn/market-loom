# Contributing

Market Loom accepts changes that support the open-source data foundation scope.

## Project Boundary

Contributions may add or improve local market data ingestion, provider adapters, DuckDB construction, point-in-time normalization, data quality auditing, contract checks, export, dashboard serving, documentation, tests, and CI.

Do not contribute strategy logic, trading signals, alpha factor research, model training, prediction generation, portfolio construction, backtest engines, order generation, broker integrations, private deployment scripts, provider tokens, real account configuration, or real market data dumps.

## Development Flow

Each migration phase must be developed on its own branch and merged back to `main` through a pull request. Do not make phase changes directly on `main`.

Before requesting review, run the validation commands that apply to the phase.

## Local Checks

```bash
python -m pip install -e ".[dev]"
pytest -q
python -m compileall src
market-loom --help
```

