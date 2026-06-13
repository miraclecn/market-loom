# Market Loom Consumer Contract

Market Loom exposes data-foundation contracts through DuckDB tables and views. Use `market-loom` for CLI operations and `market_loom` for Python imports.

Market Loom was split from alpha-data as the open-source data-foundation layer.

## Market Loom responsibilities

- Build local DuckDB research-source databases from localized raw and supplemental data.
- Preserve stable public table names and normalized daily-bar fields.
- Normalize daily OHLCV, tradeability, ST, limit, and industry fields into `stock_bar_normalized_daily`.
- Keep rows present even when quality issues exist.
- Materialize `data_quality_usability_flags` so downstream systems can decide whether a row is usable.
- Provide `market-loom check-research-source-contract` and `market-loom audit-market-data-quality`.

## Downstream responsibilities

- Decide whether quality flags are acceptable for a specific workflow.
- Apply any strategy, prediction, portfolio, execution, or reporting logic outside Market Loom.
- Keep provider credentials, provider data, and downstream artifacts out of the Market Loom repository.
- Validate provider licensing before sharing derived outputs.

## stock_bar_normalized_daily schema

| Column | Meaning |
| --- | --- |
| `trade_date` | Trading date as `YYYYMMDD`. |
| `code` | Security identifier such as `000001.SZ`. |
| `open` | Normalized open price. |
| `high` | Normalized high price. |
| `low` | Normalized low price. |
| `close` | Normalized close price. |
| `prev_close` | Previous normalized close when available, otherwise same-basis source `pre_close` for the first available bar. |
| `volume` | Volume in shares. |
| `amount` | Turnover value in CNY. |
| `turnover_rate` | Turnover rate percentage from the source daily-basic layer. |
| `is_st` | Historical ST-name flag derived from name-change windows. |
| `is_paused` | Full-day suspension flag from official suspension data or conservative fallback logic. |
| `limit_up` | Up-limit price normalized to the same price basis as OHLC. |
| `limit_down` | Down-limit price normalized to the same price basis as OHLC. |
| `industry_code` | PIT industry code or `UNKNOWN`. |
| `industry_name` | PIT industry name, falling back to `industry_code`, then `UNKNOWN`. |

## PIT mapping

- `security_master_ref` maps provider security identifiers into stable A-share security metadata.
- `market_trade_calendar` is derived from observed raw daily-basic dates.
- `name_change_history` maps historical names into daily ST windows.
- `industry_classification_pit` is matched by `security_id`, `effective_at`, and `removed_at`.
- When multiple industry levels match one bar, Market Loom chooses one canonical level, prioritizing `sw2021_l1`, then other level-1 schemas, then deterministic schema and code order.
- `tradeability_state_daily` joins official suspension and limit data to `daily_bar_pit`.

## Fields intentionally not provided

Market Loom does not provide downstream look-ahead, signal, portfolio, or execution fields:

- `adv20_amount`
- `next_trade_date`
- `next_open`
- `next_limit_up`
- `next_limit_down`
- `next_is_paused`
- `can_buy_next_open`
- `can_sell_next_open`
- `future_ret`
- `future_score`
- `rank_label`
- `predictions`
- `portfolio targets`
- `orders`
- `NAV`

## Quality issue interpretation

| Issue type | Default interpretation |
| --- | --- |
| `MISSING_LIMIT` | Limit price is missing; execution-sensitive consumers should treat the row conservatively. |
| `UNRESOLVED_ADJ_FACTOR_JUMP` | Adjustment factor changed without sufficient corporate-action evidence; promotion and label-sensitive use should be blocked. |
| `MISSING_INDUSTRY_CODE` | Industry is standardized to `UNKNOWN`; consumers should handle unknown buckets explicitly. |
| `INCOMPLETE_TRADING_DATE` | Bar coverage is unusually sparse for the date; consumers should avoid broad cross-section assumptions. |

## Downstream issue handling

Read `data_quality_usability_flags` before consuming rows. The table records `usable_for_vpa`, `usable_for_ml_feature`, `usable_for_ml_label`, `usable_for_backtest`, and `execution_restricted`. Downstream systems should filter, quarantine, or annotate rows based on those fields instead of deleting Market Loom rows.

## Known limitations

- Market Loom does not guarantee provider completeness.
- Current quality checks are conservative and may flag synthetic or sparse datasets.
- The public contract is daily-bar focused.
- Provider SDK installation and credentials are outside Market Loom.
- Market Loom does not provide investment advice, predictions, portfolio construction, orders, or live execution.
