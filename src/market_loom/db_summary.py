from __future__ import annotations

from pathlib import Path
from typing import Any


RAW_TABLE_NAMES = {
    "stock_basic_ref",
    "pit_fina_indicator",
}

RESEARCH_TABLE_NAMES = {
    "market_trade_calendar",
    "daily_bar_pit",
    "security_master_ref",
    "tradeability_state_daily",
    "benchmark_membership_pit",
    "industry_classification_pit",
    "benchmark_weight_snapshot_pit",
    "corporate_action_ledger",
    "corporate_action_exception_ledger",
}


def summarize_duckdb(db_path: str | Path) -> dict[str, Any]:
    import duckdb

    path = Path(db_path)
    if not path.exists():
        return {
            "database_path": str(path),
            "exists": False,
            "table_count": 0,
            "total_rows": 0,
            "tables": [],
        }

    conn = duckdb.connect(str(path), read_only=True)
    try:
        table_rows = conn.execute(
            """
            SELECT schema_name, table_name
            FROM duckdb_tables()
            WHERE internal = false
            ORDER BY schema_name, table_name
            """
        ).fetchall()
        tables = [
            _table_summary(conn, schema_name=row[0], table_name=row[1])
            for row in table_rows
        ]
    finally:
        conn.close()

    return {
        "database_path": str(path),
        "exists": True,
        "table_count": len(tables),
        "total_rows": sum(int(table["row_count"]) for table in tables),
        "tables": tables,
    }


def _table_summary(conn: Any, *, schema_name: str, table_name: str) -> dict[str, Any]:
    qualified = f"{_quote_identifier(schema_name)}.{_quote_identifier(table_name)}"
    row_count = conn.execute(f"SELECT COUNT(*) FROM {qualified}").fetchone()[0]
    columns = conn.execute(
        """
        SELECT column_name, data_type
        FROM duckdb_columns()
        WHERE schema_name = ? AND table_name = ?
        ORDER BY column_index
        """,
        [schema_name, table_name],
    ).fetchall()
    return {
        "schema": schema_name,
        "name": table_name,
        "layer": _classify_layer(schema_name=schema_name, table_name=table_name),
        "row_count": int(row_count),
        "column_count": len(columns),
        "columns": [
            {"name": column_name, "type": data_type}
            for column_name, data_type in columns
        ],
    }


def _classify_layer(*, schema_name: str, table_name: str) -> str:
    if schema_name == "meta":
        return "meta"
    if table_name in RAW_TABLE_NAMES or table_name.startswith("raw_"):
        return "raw"
    if table_name in RESEARCH_TABLE_NAMES or table_name.endswith("_pit"):
        return "research"
    if "audit" in table_name or "quality" in table_name:
        return "audit"
    return "other"


def _quote_identifier(value: str) -> str:
    return '"' + value.replace('"', '""') + '"'
