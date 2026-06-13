from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS = REPO_ROOT / "docs"

REQUIRED_DOCS = [
    "quickstart.md",
    "installation.md",
    "data_sources.md",
    "provider_setup.md",
    "consumer_contract.md",
    "research_source_schema.md",
    "market_data_quality.md",
    "dashboard.md",
    "troubleshooting.md",
    "release_checklist.md",
]

INTENTIONALLY_NOT_PROVIDED = [
    "adv20_amount",
    "next_trade_date",
    "next_open",
    "next_limit_up",
    "next_limit_down",
    "next_is_paused",
    "can_buy_next_open",
    "can_sell_next_open",
    "future_ret",
    "future_score",
    "rank_label",
    "predictions",
    "portfolio targets",
    "orders",
    "NAV",
]

RELEASE_COMMANDS = [
    "pytest -q",
    "market-loom --help",
    "python examples/demo_fixture/build_demo.py",
    "market-loom check-research-source-contract --db output/demo/research_source.duckdb",
    "market-loom audit-market-data-quality --db output/demo/research_source.duckdb",
    "market-loom export-normalized-bars --db output/demo/research_source.duckdb --format parquet",
    "market-loom export-dashboard --db output/demo/research_source.duckdb --out output/demo/dashboard.html",
]


def test_phase8_required_docs_exist_and_use_public_names():
    for name in REQUIRED_DOCS:
        path = DOCS / name
        assert path.is_file(), name
        text = path.read_text(encoding="utf-8")
        assert "Market Loom" in text
        assert "market-loom" in text
        assert "market_loom" in text
        assert "alpha-data-local" not in text
        assert "/home/nan" not in text
        assert "TUSHARE_TOKEN=" not in text
        assert "real account" not in text.lower()


def test_consumer_contract_documents_required_boundaries():
    text = (DOCS / "consumer_contract.md").read_text(encoding="utf-8")
    required_sections = [
        "Market Loom responsibilities",
        "Downstream responsibilities",
        "stock_bar_normalized_daily schema",
        "PIT mapping",
        "Fields intentionally not provided",
        "Quality issue interpretation",
        "Downstream issue handling",
        "Known limitations",
    ]
    for section in required_sections:
        assert section in text
    for field in INTENTIONALLY_NOT_PROVIDED:
        assert field in text


def test_release_checklist_includes_required_commands():
    text = (DOCS / "release_checklist.md").read_text(encoding="utf-8")
    for command in RELEASE_COMMANDS:
        assert command in text
