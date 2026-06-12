"""Command-line entry point for Market Loom."""

from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import date
import json
from pathlib import Path
import sys
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
    if args.command == "init":
        return _run_init(args)
    if args.command == "sync":
        return _run_sync(args)
    if args.command == "audit-data":
        return _run_audit_data(args)
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


def _run_init(args: argparse.Namespace) -> int:
    from market_loom.data_ingest.init_workspace import init_workspace

    report = init_workspace(Path(args.workspace))
    _dump_json(
        {
            "workspace": str(report.workspace),
            "actions": [
                {"path": str(action.path), "action": action.action}
                for action in report.actions
            ],
        }
    )
    return 0


def _run_sync(args: argparse.Namespace) -> int:
    from market_loom.data_ingest.adapters.akshare_adapter import AKShareAdapter
    from market_loom.data_ingest.adapters.baostock_adapter import BaostockAdapter
    from market_loom.data_ingest.adapters.tushare_adapter import TushareAdapter
    from market_loom.data_ingest.config_models import load_data_sources_config
    from market_loom.data_ingest.orchestrator import sync

    config_path = Path(args.config)
    if not config_path.exists():
        _dump_json({"error": f"Config not found: {config_path}. Run 'market-loom init' first."})
        return 2

    config = load_data_sources_config(config_path)
    adapter_map: dict[str, object] = {}
    if config.adapters.get("tushare") and config.adapters["tushare"].enabled:
        try:
            adapter_map["tushare"] = TushareAdapter()
        except Exception as exc:  # adapter packages and credentials are optional at runtime
            print(f"[WARN] Could not initialise TushareAdapter: {exc}", file=sys.stderr)
    if config.adapters.get("akshare") and config.adapters["akshare"].enabled:
        try:
            adapter_map["akshare"] = AKShareAdapter()
        except Exception as exc:
            print(f"[WARN] Could not initialise AKShareAdapter: {exc}", file=sys.stderr)
    if config.adapters.get("baostock") and config.adapters["baostock"].enabled:
        try:
            adapter_map["baostock"] = BaostockAdapter()
        except Exception as exc:
            print(f"[WARN] Could not initialise BaostockAdapter: {exc}", file=sys.stderr)

    report = sync(
        raw_db_path=Path(args.raw_db),
        config=config,
        adapter_map=adapter_map,
        only=set(args.only.split(",")) if args.only else None,
        reset=set(args.reset.split(",")) if args.reset else None,
        since=args.since or None,
        until=args.until or None,
        dry_run=args.dry_run,
    )
    _dump_json(
        {
            "raw_db_path": report.raw_db_path,
            "started_at": report.started_at,
            "finished_at": report.finished_at,
            "success_count": report.success_count(),
            "failed_count": report.failed_count(),
            "results": [asdict(result) for result in report.results],
        }
    )
    return 0


def _run_audit_data(args: argparse.Namespace) -> int:
    from market_loom.data_ingest.audit import run_audit

    report = run_audit(raw_db_path=Path(args.raw_db), out_dir=Path(args.out_dir))
    _dump_json(asdict(report))
    return 1 if report.overall_status == "blocking_failure" else 0


def _dump_json(payload: object) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    raise SystemExit(main())
