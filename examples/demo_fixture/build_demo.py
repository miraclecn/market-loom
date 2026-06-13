from __future__ import annotations

import argparse
import json
from pathlib import Path

import duckdb


INGESTED_AT = "2026-04-22 15:00:00"


def build_demo(output_dir: Path) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_db = output_dir / "raw.duckdb"
    supplemental_db = output_dir / "supplemental.duckdb"
    for path in (raw_db, supplemental_db):
        if path.exists():
            path.unlink()
    _build_raw_db(raw_db)
    _build_supplemental_db(supplemental_db)
    return {"raw_db": str(raw_db), "supplemental_db": str(supplemental_db)}


def _build_raw_db(path: Path) -> None:
    conn = duckdb.connect(str(path))
    try:
        _create_raw_schema(conn)
        _insert_stock_reference(conn)
        _insert_name_changes(conn)
        _insert_daily_rows(conn)
        _insert_optional_events(conn)
    finally:
        conn.close()


def _create_raw_schema(conn: duckdb.DuckDBPyConnection) -> None:
    conn.execute(
        """
        CREATE TABLE stock_basic_ref (
            ts_code VARCHAR,
            symbol VARCHAR,
            name VARCHAR,
            area VARCHAR,
            industry VARCHAR,
            list_date VARCHAR,
            delist_date VARCHAR,
            is_hs VARCHAR,
            ingested_at TIMESTAMP
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE raw_namechange (
            ts_code VARCHAR,
            name VARCHAR,
            start_date VARCHAR,
            end_date VARCHAR,
            ann_date VARCHAR,
            change_reason VARCHAR,
            source_table VARCHAR,
            ingested_at TIMESTAMP
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE raw_kline_unadj (
            ts_code VARCHAR,
            trade_date VARCHAR,
            open DOUBLE,
            high DOUBLE,
            low DOUBLE,
            close DOUBLE,
            pre_close DOUBLE,
            change DOUBLE,
            pct_chg DOUBLE,
            vol DOUBLE,
            amount DOUBLE,
            source_table VARCHAR,
            ingested_at TIMESTAMP
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE raw_kline_qfq (
            ts_code VARCHAR,
            trade_date VARCHAR,
            open DOUBLE,
            high DOUBLE,
            low DOUBLE,
            close DOUBLE,
            pre_close DOUBLE,
            change DOUBLE,
            pct_chg DOUBLE,
            vol DOUBLE,
            amount DOUBLE,
            source_table VARCHAR,
            ingested_at TIMESTAMP
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE raw_adj_factor (
            ts_code VARCHAR,
            trade_date VARCHAR,
            adj_factor DOUBLE,
            source_table VARCHAR,
            ingested_at TIMESTAMP
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE raw_daily_basic (
            ts_code VARCHAR,
            trade_date VARCHAR,
            close DOUBLE,
            turnover_rate DOUBLE,
            turnover_rate_f DOUBLE,
            volume_ratio DOUBLE,
            pe DOUBLE,
            pe_ttm DOUBLE,
            pb DOUBLE,
            ps DOUBLE,
            ps_ttm DOUBLE,
            dv_ratio DOUBLE,
            dv_ttm DOUBLE,
            total_share DOUBLE,
            float_share DOUBLE,
            free_share DOUBLE,
            total_mv DOUBLE,
            circ_mv DOUBLE,
            source_table VARCHAR,
            ingested_at TIMESTAMP
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE pit_fina_indicator (
            ts_code VARCHAR,
            ann_date VARCHAR,
            end_date VARCHAR,
            eps DOUBLE,
            roe DOUBLE,
            roa DOUBLE,
            gross_margin DOUBLE,
            netprofit_margin DOUBLE,
            current_ratio DOUBLE,
            debt_to_assets DOUBLE,
            revenue_ps DOUBLE,
            netprofit_yoy DOUBLE,
            dt_netprofit_yoy DOUBLE,
            or_yoy DOUBLE,
            q_sales_yoy DOUBLE,
            assets_yoy DOUBLE,
            equity_yoy DOUBLE
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE raw_dividend (
            ts_code VARCHAR,
            end_date VARCHAR,
            ann_date VARCHAR,
            div_proc VARCHAR,
            stk_div DOUBLE,
            stk_bo_rate DOUBLE,
            stk_co_rate DOUBLE,
            cash_div DOUBLE,
            cash_div_tax DOUBLE,
            record_date VARCHAR,
            ex_date VARCHAR,
            pay_date VARCHAR,
            div_listdate VARCHAR,
            source_table VARCHAR,
            ingested_at TIMESTAMP
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE raw_stk_limit (
            ts_code VARCHAR,
            trade_date VARCHAR,
            up_limit DOUBLE,
            down_limit DOUBLE,
            source_table VARCHAR,
            ingested_at TIMESTAMP
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE raw_suspend_d (
            ts_code VARCHAR,
            trade_date VARCHAR,
            suspend_timing VARCHAR,
            suspend_type VARCHAR,
            source_table VARCHAR,
            ingested_at TIMESTAMP
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE raw_share_float (
            ts_code VARCHAR,
            ann_date VARCHAR,
            float_date VARCHAR,
            float_share DOUBLE,
            float_ratio DOUBLE,
            holder_name VARCHAR,
            share_type VARCHAR,
            source_table VARCHAR,
            ingested_at TIMESTAMP
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE raw_repurchase (
            ts_code VARCHAR,
            ann_date VARCHAR,
            end_date VARCHAR,
            proc VARCHAR,
            exp_date VARCHAR,
            vol DOUBLE,
            amount DOUBLE,
            high_limit DOUBLE,
            low_limit DOUBLE,
            source_table VARCHAR,
            ingested_at TIMESTAMP
        )
        """
    )


def _insert_stock_reference(conn: duckdb.DuckDBPyConnection) -> None:
    conn.executemany(
        "INSERT INTO stock_basic_ref VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        [
            ("000001.SZ", "000001", "Demo Bank", "Shenzhen", "Bank", "19910403", None, "N", INGESTED_AT),
            ("300001.SZ", "300001", "Demo Grid", "Qingdao", "Equipment", "20091030", None, "N", INGESTED_AT),
            ("688001.SH", "688001", "Demo Tech", "Shanghai", "Technology", "20190722", None, "N", INGESTED_AT),
            ("920001.BJ", "920001", "Demo Beijing", "Beijing", "Industrial", "20240102", None, "N", INGESTED_AT),
        ],
    )


def _insert_name_changes(conn: duckdb.DuckDBPyConnection) -> None:
    conn.executemany(
        "INSERT INTO raw_namechange VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        [
            ("000001.SZ", "Demo Bank", "19910403", None, "19910403", "name", "demo.namechange", INGESTED_AT),
            ("300001.SZ", "ST Demo Grid", "20240103", "20240104", "20240102", "ST", "demo.namechange", INGESTED_AT),
        ],
    )


def _insert_daily_rows(conn: duckdb.DuckDBPyConnection) -> None:
    rows = [
        ("000001.SZ", "20240102", 10.00, 10.50, 9.90, 10.20, 10.00, 1.00),
        ("000001.SZ", "20240103", 10.30, 10.60, 10.10, 10.40, 10.20, 1.00),
        ("000001.SZ", "20240105", 10.80, 11.00, 10.60, 10.90, 10.40, 1.30),
        ("300001.SZ", "20240102", 20.00, 20.80, 19.80, 20.40, 20.00, 1.00),
        ("300001.SZ", "20240103", 20.50, 21.00, 20.20, 20.80, 20.40, 1.00),
        ("300001.SZ", "20240104", 20.80, 20.80, 20.80, 20.80, 20.80, 1.00),
        ("300001.SZ", "20240105", 20.90, 21.30, 20.70, 21.10, 20.80, 1.00),
        ("688001.SH", "20240102", 30.00, 31.00, 29.50, 30.50, 30.00, 1.00),
        ("688001.SH", "20240103", 30.60, 31.20, 30.20, 30.90, 30.50, 1.00),
        ("688001.SH", "20240105", 31.00, 31.50, 30.80, 31.30, 30.90, 1.00),
    ]
    qfq_only_rows = [
        ("920001.BJ", "20240102", 16.00, 16.50, 15.80, 16.20, 16.00, 1.10),
        ("920001.BJ", "20240103", 16.20, 16.70, 16.00, 16.40, 16.20, 1.10),
        ("920001.BJ", "20240105", 16.40, 16.90, 16.10, 16.60, 16.40, 1.10),
    ]
    for code, trade_date, open_, high, low, close, pre_close, adj_factor in rows:
        volume = 0.0 if (code, trade_date) == ("300001.SZ", "20240104") else 100.0
        amount = 0.0 if volume == 0.0 else close * volume
        _insert_daily_basic(conn, code, trade_date, close, amount)
        _insert_kline(conn, "raw_kline_unadj", code, trade_date, open_, high, low, close, pre_close, volume, amount)
        _insert_kline(
            conn,
            "raw_kline_qfq",
            code,
            trade_date,
            open_ * adj_factor,
            high * adj_factor,
            low * adj_factor,
            close * adj_factor,
            pre_close * adj_factor,
            volume,
            amount,
        )
        _insert_adj_factor(conn, code, trade_date, adj_factor)
    for code, trade_date, open_, high, low, close, pre_close, adj_factor in qfq_only_rows:
        _insert_daily_basic(conn, code, trade_date, close, close * 80.0)
        _insert_kline(conn, "raw_kline_qfq", code, trade_date, open_, high, low, close, pre_close, 80.0, close * 80.0)
        _insert_adj_factor(conn, code, trade_date, adj_factor)
    conn.executemany(
        "INSERT INTO pit_fina_indicator VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        [
            ("000001.SZ", "20240102", "20231231", 1.2, 10.0, 0.8, 35.0, 18.0, 1.5, 60.0, 3.0, 12.0, 10.0, 8.0, 7.0, 6.0, 5.0),
            ("300001.SZ", "20240103", "20231231", 0.8, 9.0, 0.7, 30.0, 15.0, 1.3, 45.0, 2.0, 20.0, 18.0, 16.0, 15.0, 14.0, 13.0),
        ],
    )


def _insert_daily_basic(
    conn: duckdb.DuckDBPyConnection,
    code: str,
    trade_date: str,
    close: float,
    amount: float,
) -> None:
    conn.execute(
        """
        INSERT INTO raw_daily_basic VALUES
        (?, ?, ?, 1.0, 1.1, 0.8, 10.0, 9.8, 1.2, 2.2, 2.1, 0.2, 0.2,
         1000.0, 900.0, 800.0, ?, ?, 'demo.daily_basic', ?)
        """,
        [code, trade_date, close, amount * 10.0, amount * 8.0, INGESTED_AT],
    )


def _insert_kline(
    conn: duckdb.DuckDBPyConnection,
    table: str,
    code: str,
    trade_date: str,
    open_: float,
    high: float,
    low: float,
    close: float,
    pre_close: float,
    volume: float,
    amount: float,
) -> None:
    conn.execute(
        f"INSERT INTO {table} VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        [
            code,
            trade_date,
            open_,
            high,
            low,
            close,
            pre_close,
            close - pre_close,
            ((close - pre_close) / pre_close) * 100.0,
            volume,
            amount,
            f"demo.{table}",
            INGESTED_AT,
        ],
    )


def _insert_adj_factor(
    conn: duckdb.DuckDBPyConnection,
    code: str,
    trade_date: str,
    adj_factor: float,
) -> None:
    conn.execute(
        "INSERT INTO raw_adj_factor VALUES (?, ?, ?, 'demo.adj_factor', ?)",
        [code, trade_date, adj_factor, INGESTED_AT],
    )


def _insert_optional_events(conn: duckdb.DuckDBPyConnection) -> None:
    conn.executemany(
        "INSERT INTO raw_stk_limit VALUES (?, ?, ?, ?, ?, ?)",
        [
            ("000001.SZ", "20240103", 11.22, 9.18, "demo.stk_limit", INGESTED_AT),
            ("300001.SZ", "20240103", 22.88, 18.72, "demo.stk_limit", INGESTED_AT),
            ("300001.SZ", "20240104", 22.88, 18.72, "demo.stk_limit", INGESTED_AT),
            ("920001.BJ", "20240103", 18.04, 14.76, "demo.stk_limit", INGESTED_AT),
        ],
    )
    conn.execute(
        "INSERT INTO raw_suspend_d VALUES ('300001.SZ', '20240104', '', 'S', 'demo.suspend_d', ?)",
        [INGESTED_AT],
    )
    conn.execute(
        """
        INSERT INTO raw_share_float VALUES
        ('000001.SZ', '20240101', '20240108', 100.0, 1.0, 'demo holder',
         'restricted', 'demo.share_float', ?)
        """,
        [INGESTED_AT],
    )
    conn.execute(
        """
        INSERT INTO raw_repurchase VALUES
        ('000001.SZ', '20240101', '20240109', 'implemented', '20240131',
         10.0, 100.0, 12.0, 8.0, 'demo.repurchase', ?)
        """,
        [INGESTED_AT],
    )


def _build_supplemental_db(path: Path) -> None:
    conn = duckdb.connect(str(path))
    try:
        conn.execute(
            """
            CREATE TABLE industry_classification_pit (
                security_id VARCHAR,
                industry_schema VARCHAR,
                industry_code VARCHAR,
                industry_name VARCHAR,
                effective_at VARCHAR,
                removed_at VARCHAR
            )
            """
        )
        conn.executemany(
            "INSERT INTO industry_classification_pit VALUES (?, ?, ?, ?, ?, ?)",
            [
                ("000001.SZ", "sw2021_l1", "801780.SI", "Bank L1", "20200101", None),
                ("000001.SZ", "sw2021_l2", "801783.SI", "Bank L2", "20200101", None),
                ("000001.SZ", "sw2021_l3", "857831.SI", "Bank L3", "20200101", None),
                ("300001.SZ", "sw2021_l1", "801730.SI", None, "20200101", None),
                ("688001.SH", "sw2021_l1", "801080.SI", "Electronics", "20200101", None),
            ],
        )
        conn.execute(
            """
            CREATE TABLE benchmark_membership_pit (
                benchmark_id VARCHAR,
                security_id VARCHAR,
                effective_at VARCHAR,
                removed_at VARCHAR
            )
            """
        )
        conn.executemany(
            "INSERT INTO benchmark_membership_pit VALUES (?, ?, ?, ?)",
            [
                ("DEMO_INDEX", "000001.SZ", "20200101", None),
                ("DEMO_INDEX", "300001.SZ", "20200101", None),
            ],
        )
        conn.execute(
            """
            CREATE TABLE benchmark_weight_snapshot_pit (
                benchmark_id VARCHAR,
                security_id VARCHAR,
                trade_date VARCHAR,
                weight DOUBLE
            )
            """
        )
        conn.executemany(
            "INSERT INTO benchmark_weight_snapshot_pit VALUES (?, ?, ?, ?)",
            [
                ("DEMO_INDEX", "000001.SZ", "20240102", 60.0),
                ("DEMO_INDEX", "300001.SZ", "20240102", 40.0),
            ],
        )
        conn.execute(
            """
            CREATE TABLE index_basic_ref (
                ts_code VARCHAR,
                name VARCHAR,
                market VARCHAR,
                publisher VARCHAR,
                category VARCHAR,
                base_date VARCHAR,
                base_point DOUBLE,
                list_date VARCHAR
            )
            """
        )
        conn.execute(
            """
            INSERT INTO index_basic_ref VALUES
            ('000000.SH', 'Demo Index', 'DEMO', 'Market Loom', 'synthetic', '20240101', 1000.0, '20240101')
            """
        )
        conn.execute(
            """
            CREATE TABLE raw_index_daily (
                ts_code VARCHAR,
                trade_date VARCHAR,
                close DOUBLE,
                open DOUBLE,
                high DOUBLE,
                low DOUBLE,
                pre_close DOUBLE,
                change DOUBLE,
                pct_chg DOUBLE,
                vol DOUBLE,
                amount DOUBLE,
                source_table VARCHAR,
                ingested_at TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            INSERT INTO raw_index_daily VALUES
            ('000000.SH', '20240102', 1005.0, 1000.0, 1010.0, 998.0, 1000.0, 5.0, 0.5, 10000.0, 50000.0, 'demo.index_daily', ?)
            """,
            [INGESTED_AT],
        )
    finally:
        conn.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the no-token Market Loom demo fixture.")
    parser.add_argument("--output-dir", default="output/demo")
    args = parser.parse_args()
    payload = build_demo(Path(args.output_dir))
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
