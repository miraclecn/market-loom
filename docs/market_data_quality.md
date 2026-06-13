# Market Loom Market Data Quality

Market Loom writes quality evidence with `market-loom audit-market-data-quality`. Python callers can use `market_loom.market_data_quality`.

## Run An Audit

```bash
market-loom audit-market-data-quality --db output/demo/research_source.duckdb
```

Write expanded files:

```bash
market-loom audit-market-data-quality \
  --db output/demo/research_source.duckdb \
  --output-dir output/demo/quality
```

## Issue Types

| Issue type | Severity | Execution restricted |
| --- | --- | --- |
| `MISSING_LIMIT` | `MEDIUM` | true |
| `UNRESOLVED_ADJ_FACTOR_JUMP` | `HIGH` | true |
| `MISSING_INDUSTRY_CODE` | `LOW` | false |
| `INCOMPLETE_TRADING_DATE` | `HIGH` | true |

## Usability Columns

`data_quality_usability_flags` records:

- `usable_for_vpa`
- `usable_for_ml_feature`
- `usable_for_ml_label`
- `usable_for_backtest`
- `execution_restricted`

These fields describe conservative usability, not row deletion. Consumers should handle flagged rows explicitly.

## Threshold Options

```bash
market-loom audit-market-data-quality \
  --db output/demo/research_source.duckdb \
  --fail-on-missing-limit \
  --fail-on-high-severity \
  --max-unresolved-adj-factor-jump 0
```

## Demo Expectations

The synthetic demo intentionally includes missing limits, missing industry classification, an incomplete trading date, and an unresolved adjustment-factor jump so users can inspect quality output before using provider data.
