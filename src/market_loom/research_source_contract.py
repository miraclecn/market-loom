from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import duckdb

from .contracts import NORMALIZED_STOCK_BAR_COLUMNS

REQUIRED_BASE_TABLES = (
    "daily_bar_pit",
    "tradeability_state_daily",
)


@dataclass(frozen=True)
class ResearchSourceContractResult:
    ok: bool
    errors: tuple[str, ...]
    warnings: tuple[str, ...]
    required_base_tables: tuple[str, ...]
    normalized_view: str
    required_columns: tuple[str, ...]


def check_research_source_contract(db_path: str | Path) -> ResearchSourceContractResult:
    path = Path(db_path).expanduser().resolve()
    conn = duckdb.connect(str(path), read_only=True)
    errors: list[str] = []
    warnings: list[str] = []
    try:
        existing_tables = _table_names(conn)
        for table in REQUIRED_BASE_TABLES:
            if table not in existing_tables:
                errors.append(f"Missing required base table: {table}")

        normalized_table = "stock_bar_normalized_daily"
        if normalized_table not in existing_tables and normalized_table not in _view_names(conn):
            errors.append(f"Missing required normalized view/table: {normalized_table}")
        else:
            columns = _column_names(conn, normalized_table)
            missing = [c for c in NORMALIZED_STOCK_BAR_COLUMNS if c not in columns]
            if missing:
                if missing == ["industry_name"] and "industry_code" in columns:
                    warnings.append(
                        "industry_name is missing while industry_code exists; industry enrichment is recommended."
                    )
                else:
                    errors.append(
                        "Missing required normalized columns: " + ", ".join(missing)
                    )

        return ResearchSourceContractResult(
            ok=not errors,
            errors=tuple(errors),
            warnings=tuple(warnings),
            required_base_tables=REQUIRED_BASE_TABLES,
            normalized_view=normalized_table,
            required_columns=tuple(NORMALIZED_STOCK_BAR_COLUMNS),
        )
    finally:
        conn.close()


def result_to_dict(result: ResearchSourceContractResult) -> dict[str, Any]:
    return asdict(result)


def _table_names(conn: duckdb.DuckDBPyConnection) -> set[str]:
    rows = conn.execute(
        "SELECT table_name FROM information_schema.tables WHERE table_schema='main'"
    ).fetchall()
    return {name for (name,) in rows}


def _view_names(conn: duckdb.DuckDBPyConnection) -> set[str]:
    rows = conn.execute(
        "SELECT table_name FROM information_schema.views WHERE table_schema='main'"
    ).fetchall()
    return {name for (name,) in rows}


def _column_names(conn: duckdb.DuckDBPyConnection, table_name: str) -> set[str]:
    rows = conn.execute(
        """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema='main' AND table_name=?
        """,
        [table_name],
    ).fetchall()
    return {name for (name,) in rows}

