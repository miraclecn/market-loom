from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "ci.yml"


def test_ci_workflow_contains_required_phase9_contract():
    assert WORKFLOW.is_file()
    text = WORKFLOW.read_text(encoding="utf-8")

    for required in (
        "push:",
        "pull_request:",
        "3.11",
        "3.12",
        "python -m pip install -U pip",
        'python -m pip install -e ".[dev]"',
        "pytest -q",
        "market-loom --help",
        "python -m compileall src",
        "python examples/demo_fixture/build_demo.py",
        "market-loom build-research-source-db",
        "market-loom check-research-source-contract",
        "market-loom audit-market-data-quality",
        "market-loom export-dashboard",
    ):
        assert required in text

    forbidden = (
        "TUSHARE_TOKEN",
        "AKSHARE",
        "BAOSTOCK",
        "secrets.",
        "alpha-data-local",
        "/home/nan",
    )
    for value in forbidden:
        assert value not in text
