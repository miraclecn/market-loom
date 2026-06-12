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
    if args.command == "build-reference-staging-db":
        return _run_build_reference_staging_db(args)
    if args.command == "build-research-source-db":
        return _run_build_research_source_db(args)
    if args.command == "inspect-db":
        return _run_inspect_db(args)
    if args.command == "export-dashboard":
        return _run_export_dashboard(args)
    if args.command == "serve":
        return _run_serve(args)
    if args.command == "audit-market-data-quality":
        return _run_audit_market_data_quality(args)
    if args.command == "check-research-source-contract":
        return _run_check_research_source_contract(args)
    if args.command == "export-normalized-bars":
        return _run_export_normalized_bars(args)
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
    command.add_argument("--output-dir", default="")


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


def _run_build_reference_staging_db(args: argparse.Namespace) -> int:
    from market_loom.reference_data_staging import (
        BenchmarkReferenceDefinition,
        build_tushare_reference_db,
    )

    benchmarks = [
        _parse_benchmark_reference(value)
        for value in (args.benchmark or ["CSI 800=000906.SH"])
    ]
    result = build_tushare_reference_db(
        target_db=Path(args.target_db),
        benchmarks=benchmarks,
        start_date=args.start_date,
        end_date=args.end_date or date.today().strftime("%Y%m%d"),
        token=args.token or None,
        industry_levels=tuple(args.industry_level or ["L1", "L2", "L3"]),
        index_weight_window_months=args.index_weight_window_months,
        stage_market_events=args.stage_market_events,
        market_event_start_date=args.market_event_start_date or None,
        market_event_end_date=args.market_event_end_date or None,
        market_event_page_size=args.market_event_page_size,
        market_event_request_interval_seconds=args.market_event_request_interval_seconds,
    )
    _dump_json(result)
    return 0


def _run_build_research_source_db(args: argparse.Namespace) -> int:
    from market_loom.market_data_bootstrap import build_research_source_db

    _dump_json(
        build_research_source_db(
            source_db=Path(args.source_db),
            target_db=Path(args.target_db),
            supplemental_db=Path(args.supplemental_db) if args.supplemental_db else None,
        )
    )
    return 0


def _run_inspect_db(args: argparse.Namespace) -> int:
    from market_loom.db_summary import summarize_duckdb

    _dump_json(summarize_duckdb(Path(args.db)))
    return 0


def _run_export_dashboard(args: argparse.Namespace) -> int:
    from market_loom.dashboard import write_dashboard
    from market_loom.db_summary import summarize_duckdb

    summary = summarize_duckdb(Path(args.db))
    output_path = write_dashboard(summary, Path(args.out))
    _dump_json({"database_path": summary["database_path"], "output_path": str(output_path)})
    return 0


def _run_serve(args: argparse.Namespace) -> int:
    from market_loom.dashboard import serve_dashboard

    print(f"Serving Market Loom at http://{args.host}:{args.port}", file=sys.stderr)
    serve_dashboard(Path(args.db), host=args.host, port=args.port)
    return 0


def _run_audit_market_data_quality(args: argparse.Namespace) -> int:
    from market_loom.market_data_quality import write_market_data_quality_audit

    output_path = (
        Path(args.output_dir) / "market_data_quality.json"
        if args.output_dir
        else Path(args.output)
    )
    report = write_market_data_quality_audit(
        source_db=Path(args.source_db),
        output_path=output_path,
        min_official_ratio=args.min_official_ratio,
        fail_on_missing_limit=args.fail_on_missing_limit,
        fail_on_high_severity=args.fail_on_high_severity,
        max_unresolved_adj_factor_jump=args.max_unresolved_adj_factor_jump,
        max_missing_limit=args.max_missing_limit,
    )
    if args.output_dir:
        _write_market_data_quality_csvs(Path(args.source_db), Path(args.output_dir))
        report["output_dir"] = str(Path(args.output_dir))
    _dump_json(report)
    return 0 if report["ok"] else 1


def _run_check_research_source_contract(args: argparse.Namespace) -> int:
    from market_loom.research_source_contract import (
        check_research_source_contract,
        result_to_dict,
    )

    result = check_research_source_contract(Path(args.db))
    _dump_json(result_to_dict(result))
    return 0 if result.ok else 1


def _run_export_normalized_bars(args: argparse.Namespace) -> int:
    import duckdb

    source_db = Path(args.db).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    format_name = args.format.lower()
    file_name = f"stock_bar_normalized_daily.{'parquet' if format_name == 'parquet' else 'csv'}"
    output_path = output_dir / file_name
    escaped_output_path = str(output_path).replace("'", "''")
    conn = duckdb.connect(str(source_db), read_only=True)
    try:
        if format_name == "parquet":
            conn.execute(f"COPY stock_bar_normalized_daily TO '{escaped_output_path}' (FORMAT PARQUET)")
        else:
            conn.execute(f"COPY stock_bar_normalized_daily TO '{escaped_output_path}' (HEADER, DELIMITER ',')")
    finally:
        conn.close()
    _dump_json({"db": str(source_db), "output_path": str(output_path), "format": format_name})
    return 0


def _write_market_data_quality_csvs(source_db: Path, output_dir: Path) -> None:
    import duckdb

    output_dir.mkdir(parents=True, exist_ok=True)
    conn = duckdb.connect(str(Path(source_db).expanduser().resolve()), read_only=True)
    try:
        _copy_query_to_csv(
            conn,
            """
            SELECT DISTINCT trade_date, issue_type, issue_severity
            FROM data_quality_usability_flags
            WHERE issue_type = 'INCOMPLETE_TRADING_DATE'
            ORDER BY trade_date, issue_type
            """,
            output_dir / "bad_dates.csv",
        )
        _copy_query_to_csv(
            conn,
            """
            SELECT DISTINCT code, issue_type, issue_severity
            FROM data_quality_usability_flags
            WHERE issue_type IN (
                'MISSING_LIMIT',
                'UNRESOLVED_ADJ_FACTOR_JUMP',
                'MISSING_INDUSTRY_CODE'
            )
            ORDER BY code, issue_type
            """,
            output_dir / "bad_symbols.csv",
        )
        _copy_query_to_csv(
            conn,
            """
            SELECT *
            FROM data_quality_usability_flags
            WHERE execution_restricted
            ORDER BY trade_date, code, issue_type
            """,
            output_dir / "execution_restricted.csv",
        )
    finally:
        conn.close()


def _copy_query_to_csv(conn: object, query: str, output_path: Path) -> None:
    escaped_path = str(output_path).replace("'", "''")
    conn.execute(f"COPY ({query}) TO '{escaped_path}' (HEADER, DELIMITER ',')")


def _parse_benchmark_reference(value: str) -> "BenchmarkReferenceDefinition":
    from market_loom.reference_data_staging import BenchmarkReferenceDefinition

    benchmark_id, separator, index_code = value.partition("=")
    if not separator or not benchmark_id.strip() or not index_code.strip():
        raise ValueError(
            "Benchmark references must use '<benchmark_id>=<index_code>', "
            f"got: {value}"
        )
    return BenchmarkReferenceDefinition(
        benchmark_id=benchmark_id.strip(),
        index_code=index_code.strip(),
    )


def _dump_json(payload: object) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    raise SystemExit(main())
