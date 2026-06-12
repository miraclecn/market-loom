# Market Loom Migration Specification for Codex

This document is an execution specification for migrating the open-source data-foundation parts of `alpha-data` into `market-loom`.

Codex must treat this document as the source of truth for the migration. Do not treat it as a user guide. Execute the migration in small, reviewable steps.

---

## 0. Mission

Migrate the reusable, open-source, data-foundation layer from `alpha-data` into `market-loom`.

`market-loom` must become a clean Apache-2.0 open-source project for local A-share market data ingestion, PIT normalization, DuckDB research-source construction, data quality auditing, contract checking, export, and dashboard serving.

`market-loom` must not become a strategy, signal, backtest, model-training, or live-trading project.

---

## 1. Repository Assumptions

Expected local layout:

```text
workspace/
  alpha-data/      # source repository, read-only reference
  market-loom/     # target repository, writable
```

Codex must work inside `market-loom`.

If `alpha-data` is not available locally, stop and report:

```text
BLOCKED: alpha-data source repository not found.
Expected ../alpha-data or a user-provided source path.
```

Do not invent source files.

Do not fetch or reconstruct missing code from memory.

---

## 2. Source and Target

Source repository:

```text
alpha-data
```

Target repository:

```text
market-loom
```

Source package name:

```text
alpha_data_local
```

Target package name:

```text
market_loom
```

Old CLI name:

```text
alpha-data-local
```

New CLI name:

```text
market-loom
```

Old project display name:

```text
Alpha Data Local
```

New project display name:

```text
Market Loom
```

---

## 3. Project Boundary

Market Loom is a data infrastructure project.

It may include:

* local A-share data ingestion
* provider adapter framework
* raw DuckDB construction
* PIT reference staging
* research-source DuckDB construction
* normalized daily bar view
* tradeability state construction
* data quality usability flags
* market data quality audit
* research source contract checks
* normalized bar export
* local dashboard
* JSON summary API
* demo fixture
* documentation
* tests
* CI

It must not include:

* stock selection strategy
* alpha factor research logic
* VPA structure recognition logic
* ML feature training pipeline
* future-return label generation
* model training
* prediction generation
* portfolio construction
* backtest engine
* NAV calculation
* order generation
* QMT integration
* Redis signal bridge
* live trading
* real trading logs
* real market data dumps
* provider tokens
* private account configuration

If any source file contains strategy, signal, backtest, model, or live-trading logic, do not migrate it.

---

## 4. Stable Data Contracts

The following table names are stable public contracts. Do not rename them:

```text
stock_bar_normalized_daily
data_quality_usability_flags
daily_bar_pit
tradeability_state_daily
industry_classification_pit
dataset_registry
security_master_ref
market_trade_calendar
corporate_action_ledger
corporate_action_exception_ledger
```

The following `stock_bar_normalized_daily` columns are stable public contract fields. Do not remove, rename, or change their meaning:

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

Required behavior:

* `prev_close` must be previous normalized close when available.
* First available bar may fall back to same-basis source `pre_close`.
* `limit_up` and `limit_down` must be normalized to the same price basis as OHLC fields.
* If `industry_code` is missing, use `UNKNOWN`.
* If `industry_name` is missing but `industry_code` exists, fallback to `industry_code`.
* If no industry classification matches, set both `industry_code` and `industry_name` to `UNKNOWN`.
* Do not physically delete rows from `stock_bar_normalized_daily` due to quality issues.
* Use `data_quality_usability_flags` to describe downstream usability.

Any change to these contracts is forbidden unless the user explicitly asks for a contract-breaking migration.

---

## 5. Quality Contract

The following issue types must be preserved:

```text
MISSING_LIMIT
UNRESOLVED_ADJ_FACTOR_JUMP
MISSING_INDUSTRY_CODE
INCOMPLETE_TRADING_DATE
```

The following usability fields must be preserved:

```text
usable_for_vpa
usable_for_ml_feature
usable_for_ml_label
usable_for_backtest
execution_restricted
```

Expected default semantics:

| issue_type                 | severity |     VPA | ML feature | ML label | backtest |  execution |
| -------------------------- | -------- | ------: | ---------: | -------: | -------: | ---------: |
| MISSING_INDUSTRY_CODE      | LOW      | allowed |    allowed |  allowed |  allowed |    allowed |
| MISSING_LIMIT              | MEDIUM   | allowed |    allowed |  allowed |  blocked | restricted |
| INCOMPLETE_TRADING_DATE    | HIGH     | blocked |    blocked |  blocked |  blocked | restricted |
| UNRESOLVED_ADJ_FACTOR_JUMP | HIGH     | blocked |    blocked |  blocked |  blocked | restricted |

Do not weaken quality checks to make tests pass.

If tests fail due to changed quality semantics, stop and report the diff.

---

## 6. Open-Source Safety Rules

Never commit or generate:

```text
.env
*.duckdb
*.db
*.sqlite
*.parquet
large real *.csv files
output/
outputs/
data/
provider tokens
Tushare tokens
private server addresses
local absolute paths
real account information
real trading logs
```

Search and remove references to:

```text
/home/nan
chenmolin0624
TUSHARE_TOKEN=<real value>
alpha-find-v2
real account ids
real broker paths
```

Allowed examples:

```text
TUSHARE_TOKEN=your_token_here
output/demo_raw.duckdb
output/demo_research_source.duckdb
```

Demo files must be synthetic and minimal.

---

## 7. Migration Strategy

Execute migration in phases.

Do not perform all phases in one uncontrolled edit.

After each phase:

1. run validation commands that are available,
2. show changed files,
3. summarize behavior changes,
4. report blockers,
5. do not commit unless explicitly asked.

---

# Phase 1 — Initialize Market Loom Project Skeleton

## Goal

Create a clean Apache-2.0 Python project skeleton.

## Required files

Create or update:

```text
README.md
LICENSE
NOTICE
DISCLAIMER.md
DATA_SOURCE_NOTICE.md
SECURITY.md
CONTRIBUTING.md
CHANGELOG.md
.gitignore
.env.example
pyproject.toml
src/market_loom/__init__.py
src/market_loom/cli.py
tests/
docs/
examples/
```

## pyproject.toml requirements

Use:

```toml
[project]
name = "market-loom"
version = "0.1.0"
description = "Local A-share market data weaving, DuckDB research source construction, and data quality auditing"
requires-python = ">=3.11"
```

Required core dependencies:

```text
duckdb
pandas
numpy
```

Optional provider dependencies should be extras:

```text
akshare
baostock
tushare
```

CLI entry point:

```toml
[project.scripts]
market-loom = "market_loom.cli:main"
```

## .gitignore requirements

Must exclude:

```gitignore
.env
*.duckdb
*.db
*.sqlite
*.parquet
*.csv
output/
outputs/
data/
logs/
__pycache__/
.pytest_cache/
.mypy_cache/
.ruff_cache/
dist/
build/
*.egg-info/
```

If demo requires CSV, use `.gitignore` exceptions only for explicit small synthetic files under `examples/`.

## README boundary requirements

README must clearly say:

* Market Loom is a data foundation.
* It does not provide investment advice.
* It does not generate trading signals.
* It does not train models.
* It does not run backtests.
* It does not place orders.
* It does not redistribute third-party market data.

## Validation

Run:

```bash
python -m pip install -e ".[dev]"
market-loom --help
```

If no CLI commands exist yet, `market-loom --help` must still work.

---

# Phase 2 — Migrate CLI

## Source files

From:

```text
../alpha-data/src/alpha_data_local/cli.py
```

To:

```text
src/market_loom/cli.py
```

## Required replacements

Replace:

```text
alpha_data_local -> market_loom
alpha-data-local -> market-loom
Alpha Data Local -> Market Loom
```

Do not replace database table names.

## Commands to preserve

The target CLI should preserve these commands if the corresponding modules are migrated:

```text
init
sync
audit-data
build-reference-staging-db
build-research-source-db
audit-market-data-quality
check-research-source-contract
export-normalized-bars
inspect-db
export-dashboard
serve
```

If a command depends on a module not yet migrated, either:

1. keep the command but import lazily so `market-loom --help` still works, or
2. temporarily mark it unavailable with a clear error message.

Do not silently remove commands.

## Validation

Run:

```bash
market-loom --help
python -m compileall src
```

If tests exist:

```bash
pytest -q
```

---

# Phase 3 — Migrate Data Ingestion Layer

## Source directory

```text
../alpha-data/src/alpha_data_local/data_ingest/
```

## Target directory

```text
src/market_loom/data_ingest/
```

## Include

Migrate reusable ingestion infrastructure:

```text
init_workspace.py
config_models.py
orchestrator.py
audit.py
adapters/
templates/
```

## Provider adapters

Allowed adapters:

```text
tushare_adapter.py
akshare_adapter.py
baostock_adapter.py
```

Adapters must not contain real tokens.

Adapters must fail clearly when optional dependencies are not installed.

Config templates must use placeholders only.

## Required config behavior

`market-loom init` should create:

```text
.env.example or .env template
config/data_sources.toml
output/
```

Do not write real credentials.

## Validation

Run:

```bash
market-loom init --workspace /tmp/market-loom-init-smoke
find /tmp/market-loom-init-smoke -maxdepth 3 -type f | sort
```

Verify no real token is written.

---

# Phase 4 — Migrate Research Source Builder

## Source files

```text
../alpha-data/src/alpha_data_local/market_data_bootstrap.py
../alpha-data/src/alpha_data_local/reference_data_staging.py
../alpha-data/src/alpha_data_local/db_summary.py
../alpha-data/src/alpha_data_local/dashboard.py
```

## Target files

```text
src/market_loom/market_data_bootstrap.py
src/market_loom/reference_data_staging.py
src/market_loom/db_summary.py
src/market_loom/dashboard.py
```

## Requirements

Preserve these capabilities:

* build `security_master_ref`
* build `daily_bar_pit`
* build `industry_classification_pit` from optional supplemental/source DB
* build `tradeability_state_daily`
* build `stock_bar_normalized_daily`
* build `corporate_action_ledger`
* build `corporate_action_exception_ledger`
* build `dataset_registry`
* build optional benchmark/index/reference tables
* support `supplemental_db`
* support `build-research-source-db`
* support `build-reference-staging-db`

## Forbidden changes

Do not rewrite core SQL unless required for import path fixes.

Do not rename contract tables.

Do not remove PIT logic.

Do not remove qfq fallback logic.

Do not remove industry fallback logic.

Do not remove adjustment-factor exception logic.

## Validation

Run:

```bash
python -m compileall src
market-loom build-research-source-db --help
market-loom build-reference-staging-db --help
```

If fixture tests are migrated:

```bash
pytest -q
```

---

# Phase 5 — Migrate Contract and Quality Modules

## Source files

```text
../alpha-data/src/alpha_data_local/market_data_quality.py
../alpha-data/src/alpha_data_local/research_source_contract.py
```

## Target files

```text
src/market_loom/market_data_quality.py
src/market_loom/research_source_contract.py
```

## Requirements

Preserve:

* `data_quality_usability_flags`
* `MISSING_LIMIT`
* `UNRESOLVED_ADJ_FACTOR_JUMP`
* `MISSING_INDUSTRY_CODE`
* `INCOMPLETE_TRADING_DATE`
* quality summary generation
* JSON audit output
* `audit-market-data-quality` command
* `check-research-source-contract` command

## Additional open-source improvement

If safe and small, add support for:

```text
--output-dir
```

to `audit-market-data-quality`, producing:

```text
market_data_quality.json
bad_dates.csv
bad_symbols.csv
execution_restricted.csv
```

If this is too large for the current phase, do not implement it. Create a TODO in docs instead.

## Validation

Run:

```bash
market-loom audit-market-data-quality --help
market-loom check-research-source-contract --help
python -m compileall src
```

If demo fixture exists:

```bash
market-loom check-research-source-contract --db output/demo_research_source.duckdb
market-loom audit-market-data-quality --db output/demo_research_source.duckdb
```

---

# Phase 6 — Migrate and Adapt Tests

## Source tests

Migrate relevant tests from:

```text
../alpha-data/tests/
```

## Target tests

```text
tests/
```

## Required test categories

Keep or create tests for:

```text
stock_bar_normalized_daily schema
prev_close rule
limit_up / limit_down same price basis
qfq fallback
industry_code UNKNOWN handling
industry_name fallback to industry_code
single canonical industry level per bar
data_quality_usability_flags
research source contract check
market data quality audit
CLI smoke
```

## Test constraints

Tests must use synthetic fixture data only.

Tests must not require external network access.

Tests must not require Tushare/AkShare/Baostock credentials.

Tests must not write persistent real data into the repository.

Temporary DuckDB files must be created under temporary directories.

## Validation

Run:

```bash
pytest -q
```

---

# Phase 7 — Add Demo Fixture

## Goal

Provide a no-token demo that lets users run Market Loom end-to-end without third-party credentials.

## Required files

```text
examples/demo_fixture/build_demo.py
examples/demo_fixture/README.md
```

## Demo output

The script may generate files under:

```text
output/demo/
```

or:

```text
output/
```

But these files must be ignored by git.

## Required synthetic scenarios

The demo fixture must cover:

* normal daily OHLCV bars
* ST flag derivation
* full-day suspension
* limit-up / limit-down data
* qfq fallback price basis
* missing industry classification -> UNKNOWN
* missing industry_name -> fallback to industry_code
* multiple industry levels -> choose canonical level
* incomplete trading date
* unresolved adjustment-factor jump if feasible

## Required demo commands

The README must show:

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

## Validation

Run all demo commands.

If a command fails, fix the fixture or code. Do not weaken the contract.

---

# Phase 8 — Documentation

## Required docs

Create:

```text
docs/quickstart.md
docs/installation.md
docs/data_sources.md
docs/provider_setup.md
docs/consumer_contract.md
docs/research_source_schema.md
docs/market_data_quality.md
docs/dashboard.md
docs/troubleshooting.md
docs/release_checklist.md
```

## Documentation rules

Use `Market Loom` as the project name.

Use `market-loom` as the CLI.

Use `market_loom` as the Python package.

Do not use `alpha-data-local` as the current project name.

It is acceptable to mention:

```text
Market Loom was split from alpha-data as the open-source data-foundation layer.
```

Do not include:

```text
/home/nan
real tokens
real account names
real database paths
real market data dumps
private strategy details
```

## consumer_contract.md requirements

Document:

* Market Loom responsibilities
* downstream responsibilities
* `stock_bar_normalized_daily` schema
* PIT mapping
* fields intentionally not provided
* quality issue interpretation
* downstream issue handling
* known limitations

Fields intentionally not provided must include:

```text
adv20_amount
next_trade_date
next_open
next_limit_up
next_limit_down
next_is_paused
can_buy_next_open
can_sell_next_open
future_ret
future_score
rank_label
predictions
portfolio targets
orders
NAV
```

## release_checklist.md requirements

Must include:

```bash
pytest -q
market-loom --help
python examples/demo_fixture/build_demo.py
market-loom check-research-source-contract --db output/demo/research_source.duckdb
market-loom audit-market-data-quality --db output/demo/research_source.duckdb
market-loom export-normalized-bars --db output/demo/research_source.duckdb --format parquet
market-loom export-dashboard --db output/demo/research_source.duckdb --out output/demo/dashboard.html
```

---

# Phase 9 — CI

## Required workflow

Create:

```text
.github/workflows/ci.yml
```

## CI requirements

Run on:

```text
push
pull_request
```

Python versions:

```text
3.11
3.12
```

Required steps:

```bash
python -m pip install -U pip
python -m pip install -e ".[dev]"
pytest -q
market-loom --help
python -m compileall src
```

If demo fixture is present and stable, also run demo smoke test.

Do not require external provider credentials in CI.

---

# Phase 10 — Alpha-data Handoff

After `market-loom` reaches a working `v0.1.0-alpha` state, update `alpha-data` only if explicitly asked.

If asked to update `alpha-data`, add a README notice:

```markdown
# Moved

The open-source data-foundation version of this project is now maintained as Market Loom:

https://github.com/miraclecn/market-loom

This repository is kept for historical reference.
```

Do not delete alpha-data code unless explicitly asked.

---

## 8. Migration Mapping

Use this mapping unless the actual source repository differs.

```text
alpha-data/pyproject.toml
  -> market-loom/pyproject.toml

alpha-data/src/alpha_data_local/
  -> market-loom/src/market_loom/

alpha-data/src/alpha_data_local/cli.py
  -> market-loom/src/market_loom/cli.py

alpha-data/src/alpha_data_local/data_ingest/
  -> market-loom/src/market_loom/data_ingest/

alpha-data/src/alpha_data_local/market_data_bootstrap.py
  -> market-loom/src/market_loom/market_data_bootstrap.py

alpha-data/src/alpha_data_local/reference_data_staging.py
  -> market-loom/src/market_loom/reference_data_staging.py

alpha-data/src/alpha_data_local/market_data_quality.py
  -> market-loom/src/market_loom/market_data_quality.py

alpha-data/src/alpha_data_local/research_source_contract.py
  -> market-loom/src/market_loom/research_source_contract.py

alpha-data/src/alpha_data_local/dashboard.py
  -> market-loom/src/market_loom/dashboard.py

alpha-data/src/alpha_data_local/db_summary.py
  -> market-loom/src/market_loom/db_summary.py

alpha-data/docs/vpa_ml_consumer_contract.md
  -> market-loom/docs/consumer_contract.md

alpha-data/tests/
  -> market-loom/tests/
```

---

## 9. Files to Exclude from Migration

Do not migrate:

```text
output/
outputs/
data/
*.duckdb
*.db
*.sqlite
*.parquet
large real *.csv
.env
.env.*
logs/
private deployment scripts
trading scripts
QMT scripts
Redis signal scripts
strategy notebooks
real reports
real account exports
```

If these are present in source, ignore them.

---

## 10. Required Search Checks

Before finalizing each phase, run equivalent searches:

```bash
grep -R "alpha_data_local" .
grep -R "alpha-data-local" .
grep -R "Alpha Data Local" .
grep -R "/home/nan" .
grep -R "TUSHARE_TOKEN=" .
find . -name "*.duckdb" -o -name "*.parquet" -o -name "*.sqlite" -o -name "*.db"
```

Expected result:

* `alpha_data_local` should not appear unless in migration notes.
* `alpha-data-local` should not appear unless in migration notes.
* `/home/nan` must not appear.
* real tokens must not appear.
* generated DB/export files must not be tracked.

If `*.csv` appears, verify whether it is a tiny synthetic example. If unsure, do not include it.

---

## 11. Allowed Compatibility Mentions

Allowed:

```text
Market Loom was split from alpha-data.
Market Loom provides a consumer contract for downstream VPA/ML pipelines.
```

Forbidden:

```text
alpha-data-local is the current CLI.
Use /home/nan/...
This project generates trading signals.
This project provides investment recommendations.
This project runs live trading.
```

---

## 12. Validation Matrix

Minimum validation before reporting completion:

| Phase     | Required validation                |
| --------- | ---------------------------------- |
| Skeleton  | `market-loom --help`               |
| CLI       | `market-loom --help`, `compileall` |
| Ingestion | `market-loom init` smoke           |
| Builder   | builder help, `compileall`         |
| Quality   | audit/help, contract/help          |
| Tests     | `pytest -q`                        |
| Demo      | full demo smoke                    |
| Docs      | sensitive string scan              |
| CI        | workflow syntax present            |

Final validation:

```bash
python -m pip install -e ".[dev]"
pytest -q
market-loom --help
python -m compileall src
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

If a command is unavailable because the relevant phase is not complete, report it as:

```text
SKIPPED: <command> because <reason>
```

Do not claim validation passed if commands were skipped.

---

## 13. Reporting Format

After each phase, report:

```markdown
## Phase <N> Result

### Changed files
- ...

### Preserved contracts
- ...

### Validation
- [x] command A
- [ ] command B — failed/skipped because ...

### Open-source safety check
- [x] no real DuckDB files
- [x] no provider token
- [x] no local absolute path
- [x] no trading/signal/backtest logic

### Blockers
- None
```

If there are failures, include exact error messages and suggested next steps.

---

## 14. Stop Conditions

Stop and ask for human review if any of the following happens:

* A required source file is missing.
* A migration requires changing `stock_bar_normalized_daily` schema.
* A migration requires renaming stable contract tables.
* Tests only pass after weakening data quality rules.
* Real tokens or real data files are found.
* Source code contains strategy/backtest/trading logic that appears entangled with data code.
* Demo fixture would require real third-party data.
* Provider adapter requires credentials in tests.
* The same module has diverged too much to migrate mechanically.

Do not guess through these cases.

---

## 15. Final Target State

At the end of the migration, `market-loom` should be able to support:

```bash
market-loom init
market-loom sync
market-loom audit-data
market-loom build-reference-staging-db
market-loom build-research-source-db
market-loom check-research-source-contract
market-loom audit-market-data-quality
market-loom export-normalized-bars
market-loom inspect-db
market-loom export-dashboard
market-loom serve
```

The project must remain a clean data-foundation repository.

No strategy logic.

No prediction logic.

No backtest logic.

No order logic.

No live-trading logic.

No real data dumps.

No credentials.

---

## 16. First Action for Codex

Start by inspecting both repositories and produce a migration readiness report.

Do not modify files in the first action.

Run or inspect:

```bash
pwd
git status
find . -maxdepth 3 -type f | sort | head -200
find ../alpha-data -maxdepth 3 -type f | sort | head -200
```

Then report:

```markdown
# Migration Readiness Report

## Target repository
- path:
- current files:
- license present:
- pyproject present:
- package present:

## Source repository
- path:
- package found:
- key files found:
- tests found:

## Suggested first phase
- ...

## Blockers
- ...
```

Only after the readiness report should code migration begin.
