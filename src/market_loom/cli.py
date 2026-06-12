"""Command-line entry point for Market Loom."""

from __future__ import annotations

import argparse
from datetime import date
import json
from typing import Final

from market_loom import __version__


COMMAND_PHASES: Final[dict[str, str]] = {
    "init": "Phase 3",
    "sync": "Phase 3",
    "audit-data": "Phase 3",
    "build-reference-staging-db": "Phase 4",
    "build-research-source-db": "Phase 4",
    "audit-market-data-quality": "Phase 5",
    "check-research-source-contract": "Phase 5",
    "export-normalized-bars": "Phase 5",
    "inspect-db": "Phase 4",
    "export-dashboard": "Phase 4",
    "serve": "Phase 4",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="market-loom",
        description=(
            "Market Loom: local A-share data weaving, DuckDB research source "
            "construction, and data quality auditing."
        ),
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"market-loom {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command")
    _add_init_command(subparsers)
    _add_sync_command(subparsers)
    _add_audit_data_command(subparsers)
    _add_reference_staging_command(subparsers)
    _add_research_source_command(subparsers)
    _add_market_data_quality_command(subparsers)
    _add_research_source_contract_command(subparsers)
    _add_export_normalized_bars_command(subparsers)
    _add_inspect_db_command(subparsers)
    _add_export_dashboard_command(subparsers)
    _add_serve_command(subparsers)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 0
    return _command_unavailable(args.command)


def _add_init_command(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    command = subparsers.add_parser(
        "init",
        help="Create local config templates and output directories.",
    )
    command.add_argument("--workspace", default=".", help="Workspace root directory.")


def _add_sync_command(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    command = subparsers.add_parser("sync", help="Sync A-share datasets into a raw DuckDB.")
    command.add_argument("--raw-db", default="output/raw.duckdb")
    command.add_argument("--config", default="config/data_sources.toml")
    command.add_argument("--only", default="")
    command.add_argument("--reset", default="")
    command.add_argument("--since", default="")
    command.add_argument("--until", default="")
    command.add_argument("--dry-run", action="store_true", default=False)


def _add_audit_data_command(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
) -> None:
    command = subparsers.add_parser("audit-data", help="Run checks on a raw DuckDB.")
    command.add_argument("--raw-db", default="output/raw.duckdb")
    command.add_argument("--out-dir", default="output/audit")


def _add_reference_staging_command(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
) -> None:
    command = subparsers.add_parser(
        "build-reference-staging-db",
        help="Stage PIT benchmark, industry, and market-event reference tables.",
    )
    command.add_argument("--target-db", default="output/pit_reference_staging.duckdb")
    command.add_argument("--start-date", default="20140101")
    command.add_argument("--end-date", default="")
    command.add_argument("--benchmark", action="append", default=[])
    command.add_argument("--industry-level", action="append", choices=["L1", "L2", "L3"], default=[])
    command.add_argument("--index-weight-window-months", type=int, default=1)
    command.add_argument("--stage-market-events", action="store_true")
    command.add_argument("--market-event-start-date", default="")
    command.add_argument("--market-event-end-date", default="")
    command.add_argument("--market-event-page-size", type=int, default=5000)
    command.add_argument("--market-event-request-interval-seconds", type=float, default=0.0)
    command.add_argument("--token", default="")


def _add_research_source_command(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
) -> None:
    command = subparsers.add_parser(
        "build-research-source-db",
        help="Build the PIT research DuckDB from a localized raw DuckDB.",
    )
    command.add_argument("--source-db", default="output/raw.duckdb")
    command.add_argument("--target-db", default="output/research_source.duckdb")
    command.add_argument("--supplemental-db", default="")


def _add_market_data_quality_command(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
) -> None:
    command = subparsers.add_parser(
        "audit-market-data-quality",
        help="Write a JSON quality audit for a research-source DuckDB.",
    )
    command.add_argument("--source-db", "--db", dest="source_db", default="output/research_source.duckdb")
    command.add_argument(
        "--output",
        "--output-json",
        dest="output",
        default=f"output/audits/market_data_quality_{date.today().strftime('%Y%m%d')}.json",
    )
    command.add_argument("--min-official-ratio", type=float, default=None)
    command.add_argument("--fail-on-missing-limit", action="store_true")
    command.add_argument("--fail-on-high-severity", action="store_true")
    command.add_argument("--max-unresolved-adj-factor-jump", type=int, default=None)
    command.add_argument("--max-missing-limit", type=int, default=None)


def _add_research_source_contract_command(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
) -> None:
    command = subparsers.add_parser(
        "check-research-source-contract",
        help="Check whether a research-source DuckDB satisfies the public data contract.",
    )
    command.add_argument("--db", default="output/research_source.duckdb")


def _add_export_normalized_bars_command(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
) -> None:
    command = subparsers.add_parser(
        "export-normalized-bars",
        help="Export stock_bar_normalized_daily as Parquet or CSV.",
    )
    command.add_argument("--db", default="output/research_source.duckdb")
    command.add_argument(
        "--output-dir",
        default="output/exports/stock_bar_normalized_daily",
    )
    command.add_argument("--format", choices=["parquet", "csv"], default="parquet")


def _add_inspect_db_command(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
) -> None:
    command = subparsers.add_parser("inspect-db", help="Print a DuckDB table summary as JSON.")
    command.add_argument("--db", default="output/research_source.duckdb")


def _add_export_dashboard_command(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
) -> None:
    command = subparsers.add_parser("export-dashboard", help="Write a standalone HTML data dashboard.")
    command.add_argument("--db", default="output/research_source.duckdb")
    command.add_argument("--out", default="output/dashboard.html")


def _add_serve_command(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    command = subparsers.add_parser("serve", help="Serve the local data dashboard.")
    command.add_argument("--db", default="output/research_source.duckdb")
    command.add_argument("--host", default="127.0.0.1")
    command.add_argument("--port", type=int, default=8765)


def _command_unavailable(command: str) -> int:
    _dump_json(
        {
            "available_after": COMMAND_PHASES[command],
            "command": command,
            "error": "Command unavailable in this migration phase",
        }
    )
    return 2


def _dump_json(payload: object) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    raise SystemExit(main())
