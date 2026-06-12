"""Command-line entry point for Market Loom."""

from __future__ import annotations

import argparse

from market_loom import __version__


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
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    parser.parse_args(argv)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

