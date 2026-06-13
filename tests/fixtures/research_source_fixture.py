from __future__ import annotations

from pathlib import Path

import duckdb


def _create_source_db(path: Path) -> None:
    conn = duckdb.connect(str(path))
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
        INSERT INTO stock_basic_ref VALUES
        ('000001.SZ', '000001', '平安银行', '深圳', '银行', '19910403', NULL, 'N', TIMESTAMP '2026-04-22 15:00:00'),
        ('300001.SZ', '300001', '特锐德', '青岛', '电气设备', '20091030', NULL, 'N', TIMESTAMP '2026-04-22 15:00:00'),
        ('688001.SH', '688001', '华兴源创', '苏州', '专用机械', '20190722', NULL, 'N', TIMESTAMP '2026-04-22 15:00:00'),
        ('920001.BJ', '920001', '北交样本', '北京', '专用机械', '20240110', NULL, 'N', TIMESTAMP '2026-04-22 15:00:00')
        """
    )
    conn.execute(
        """
        INSERT INTO raw_namechange VALUES
        ('000001.SZ', '平安银行', '19910403', NULL, '19910403', '证券简称变更', 'tushare.namechange', TIMESTAMP '2026-04-22 15:00:00'),
        ('300001.SZ', 'ST特锐德', '20240102', '20240103', '20240101', 'ST', 'tushare.namechange', TIMESTAMP '2026-04-22 15:00:00')
        """
    )
    conn.execute(
        """
        INSERT INTO raw_kline_unadj VALUES
        ('000001.SZ', '20240102', 10.0, 10.5, 9.9, 10.2, 10.0, 0.2, 2.0, 100.0, 200.0, 'tushare.daily', TIMESTAMP '2026-04-22 15:00:00'),
        ('000001.SZ', '20240103', 10.3, 10.6, 10.1, 10.4, 10.2, 0.2, 1.9608, 110.0, 220.0, 'tushare.daily', TIMESTAMP '2026-04-22 15:00:00'),
        ('300001.SZ', '20240102', 20.0, 21.0, 19.5, 20.5, 20.0, 0.5, 2.5, 90.0, 180.0, 'tushare.daily', TIMESTAMP '2026-04-22 15:00:00'),
        ('688001.SH', '20240102', 30.0, 31.5, 29.8, 31.0, 30.0, 1.0, 3.3333, 80.0, 240.0, 'tushare.daily', TIMESTAMP '2026-04-22 15:00:00')
        """
    )
    conn.execute(
        """
        INSERT INTO raw_kline_qfq VALUES
        ('000001.SZ', '20240102', 15.0, 15.75, 14.85, 15.3, 15.0, 0.3, 2.0, 100.0, 200.0, 'tushare.daily:qfq_repair', TIMESTAMP '2026-04-22 15:00:00'),
        ('000001.SZ', '20240103', 16.48, 16.96, 16.16, 16.64, 16.32, 0.32, 1.9608, 110.0, 220.0, 'tushare.daily:qfq_repair', TIMESTAMP '2026-04-22 15:00:00'),
        ('300001.SZ', '20240102', 40.0, 42.0, 39.0, 41.0, 40.0, 1.0, 2.5, 90.0, 180.0, 'tushare.daily:qfq_repair', TIMESTAMP '2026-04-22 15:00:00'),
        ('688001.SH', '20240102', 36.0, 37.8, 35.76, 37.2, 36.0, 1.2, 3.3333, 80.0, 240.0, 'tushare.daily:qfq_repair', TIMESTAMP '2026-04-22 15:00:00'),
        ('920001.BJ', '20240110', 16.5, 17.05, 16.28, 16.72, 16.5, 0.22, 1.3333, 70.0, 105.0, 'tushare.daily:qfq_repair', TIMESTAMP '2026-04-22 15:00:00')
        """
    )
    conn.execute(
        """
        INSERT INTO raw_adj_factor VALUES
        ('000001.SZ', '20240102', 1.5, 'tushare.adj_factor', TIMESTAMP '2026-04-22 15:00:00'),
        ('000001.SZ', '20240103', 1.6, 'tushare.adj_factor', TIMESTAMP '2026-04-22 15:00:00'),
        ('300001.SZ', '20240102', 2.0, 'tushare.adj_factor', TIMESTAMP '2026-04-22 15:00:00'),
        ('688001.SH', '20240102', 1.2, 'tushare.adj_factor', TIMESTAMP '2026-04-22 15:00:00'),
        ('920001.BJ', '20240110', 1.1, 'tushare.adj_factor', TIMESTAMP '2026-04-22 15:00:00')
        """
    )
    conn.execute(
        """
        INSERT INTO raw_daily_basic VALUES
        ('000001.SZ', '20240102', 10.2, 1.0, 1.2, 0.8, 8.0, 7.8, 1.1, 2.2, 2.1, 0.5, 0.4, 1000.0, 900.0, 800.0, 12000.0, 9000.0, 'tushare.daily_basic', TIMESTAMP '2026-04-22 15:00:00'),
        ('000001.SZ', '20240103', 10.4, 1.1, 1.3, 0.9, 8.1, 7.9, 1.2, 2.3, 2.2, 0.5, 0.4, 1010.0, 910.0, 810.0, 12100.0, 9100.0, 'tushare.daily_basic', TIMESTAMP '2026-04-22 15:00:00'),
        ('300001.SZ', '20240102', 20.5, 2.0, 2.2, 1.1, 30.0, 29.0, 4.0, 5.0, 4.8, 0.0, 0.0, 200.0, 180.0, 150.0, 4200.0, 3075.0, 'tushare.daily_basic', TIMESTAMP '2026-04-22 15:00:00'),
        ('688001.SH', '20240102', 31.0, 3.0, 3.5, 1.4, 60.0, 58.0, 6.0, 7.0, 6.8, 0.0, 0.0, 300.0, 250.0, 220.0, 9300.0, 6820.0, 'tushare.daily_basic', TIMESTAMP '2026-04-22 15:00:00'),
        ('920001.BJ', '20240110', 15.2, 4.0, 4.5, 1.0, 25.0, 24.0, 3.0, 4.0, 3.9, 0.0, 0.0, 150.0, 120.0, 110.0, 2280.0, 1672.0, 'tushare.daily_basic', TIMESTAMP '2026-04-22 15:00:00')
        """
    )
    conn.execute(
        """
        INSERT INTO pit_fina_indicator VALUES
        ('000001.SZ', '20240102', '20231231', 1.23, 10.5, 0.8, 35.0, 18.0, 1.5, 70.0, 3.21, 12.0, 10.0, 8.0, 7.0, 6.0, 5.0),
        ('300001.SZ', '20240103', '20231231', 0.88, 9.5, 0.7, 30.0, 15.0, 1.3, 45.0, 2.11, 22.0, 20.0, 18.0, 17.0, 16.0, 15.0)
        """
    )
    conn.execute(
        """
        INSERT INTO raw_dividend VALUES
        ('000001.SZ', '20231231', '20231231', '实施', 0.0, 0.0, 0.0, 0.19, 0.20, '20240102', '20240103', '20240103', NULL, 'tushare.dividend', TIMESTAMP '2026-04-22 15:00:00'),
        ('300001.SZ', '20231231', '20231231', '实施', 0.0, 0.1, 0.2, 0.0, 0.0, '20240102', '20240103', NULL, '20240103', 'tushare.dividend', TIMESTAMP '2026-04-22 15:00:00'),
        ('688001.SH', '20231231', '20231231', '预案', 0.0, 0.0, 0.0, 0.10, 0.10, '20240102', '20240103', '20240103', NULL, 'tushare.dividend', TIMESTAMP '2026-04-22 15:00:00')
        """
    )
    conn.execute(
        """
        INSERT INTO raw_stk_limit VALUES
        ('000001.SZ', '20240103', 11.22, 9.18, 'tushare.stk_limit', TIMESTAMP '2026-04-22 15:00:00')
        """
    )
    conn.execute(
        """
        INSERT INTO raw_suspend_d VALUES
        ('300001.SZ', '20240102', '全天停牌', '停牌', 'tushare.suspend_d', TIMESTAMP '2026-04-22 15:00:00')
        """
    )
    conn.execute(
        """
        INSERT INTO raw_share_float VALUES
        ('000001.SZ', '20240101', '20240108', 100.0, 1.0, 'holder', '首发原股东限售股份', 'tushare.share_float', TIMESTAMP '2026-04-22 15:00:00')
        """
    )
    conn.execute(
        """
        INSERT INTO raw_repurchase VALUES
        ('000001.SZ', '20240101', '20240109', '实施', '20240131', 10.0, 100.0, 12.0, 8.0, 'tushare.repurchase', TIMESTAMP '2026-04-22 15:00:00')
        """
    )
    conn.close()


def _create_supplemental_pit_db(path: Path) -> None:
    conn = duckdb.connect(str(path))
    conn.execute(
        """
        CREATE TABLE industry_classification_pit (
            security_id VARCHAR,
            industry_schema VARCHAR,
            industry_code VARCHAR,
            effective_at VARCHAR,
            removed_at VARCHAR
        )
        """
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
        INSERT INTO industry_classification_pit VALUES
        ('000001.SZ', 'citics_l1', 'bank', '20200101', NULL),
        ('300001.SZ', 'citics_l1', 'industrial', '20200101', NULL),
        ('688001.SH', 'citics_l1', 'tech', '20200101', NULL)
        """
    )
    conn.execute(
        """
        INSERT INTO benchmark_membership_pit VALUES
        ('CSI 800', '000001.SZ', '20200101', NULL),
        ('CSI 800', '300001.SZ', '20200101', NULL),
        ('CSI 800', '688001.SH', '20200101', NULL)
        """
    )
    conn.execute(
        """
        INSERT INTO benchmark_weight_snapshot_pit VALUES
        ('CSI 800', '000001.SZ', '20240102', 65.0),
        ('CSI 800', '300001.SZ', '20240102', 35.0),
        ('CSI 800', '000001.SZ', '20240103', 55.0),
        ('CSI 800', '688001.SH', '20240103', 45.0)
        """
    )
    conn.execute(
        """
        INSERT INTO index_basic_ref VALUES
        ('000906.SH', '中证800', 'CSI', '中证指数有限公司', '规模指数', '20041231', 1000.0, '20050105')
        """
    )
    conn.execute(
        """
        INSERT INTO raw_index_daily VALUES
        ('000906.SH', '20240102', 5010.0, 5000.0, 5025.0, 4995.0, 4980.0, 30.0, 0.6024, 123456.0, 789012.0, 'tushare.index_daily', TIMESTAMP '2026-04-22 15:00:00'),
        ('000906.SH', '20240103', 5030.0, 5015.0, 5040.0, 5005.0, 5010.0, 20.0, 0.3992, 135790.0, 880000.0, 'tushare.index_daily', TIMESTAMP '2026-04-22 15:00:00')
        """
    )
    conn.close()



def create_research_source_fixture(source_db: Path, supplemental_db: Path) -> None:
    _create_source_db(source_db)
    _create_supplemental_pit_db(supplemental_db)
