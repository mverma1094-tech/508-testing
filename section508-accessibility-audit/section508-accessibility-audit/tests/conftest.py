"""Shared fixtures for the Section 508 / WCAG 2.1 AA test suite."""
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
AXE_JS = ROOT / "node_modules" / "axe-core" / "axe.min.js"
REPORTS = ROOT / "reports"

# Only rules tagged for WCAG 2.0/2.1 A and AA are in scope for Section 508.
WCAG_TAGS = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"]

PAGES = {
    "before": ROOT / "app" / "before" / "index.html",
    "after": ROOT / "app" / "after" / "index.html",
}


def page_param(version):
    """The 'before' page is meant to fail: a strict xfail proves each test catches the defect."""
    if version == "before":
        return pytest.param(version, marks=pytest.mark.xfail(strict=True, reason="intentional defect"))
    return version


ALL_VERSIONS = [page_param("before"), page_param("after")]


@pytest.fixture
def open_page(page):
    def _open(version):
        page.goto(PAGES[version].as_uri())
        page.wait_for_load_state("load")
        return page
    return _open


def run_axe(page, version=None):
    """Inject axe-core, run the WCAG A/AA ruleset, and save the raw results."""
    if not AXE_JS.exists():
        pytest.exit("axe-core not found. Run `npm install` first.", returncode=2)
    page.add_script_tag(path=str(AXE_JS))
    results = page.evaluate(
        "tags => axe.run(document, { runOnly: { type: 'tag', values: tags } })", WCAG_TAGS
    )
    if version:
        REPORTS.mkdir(exist_ok=True)
        (REPORTS / f"axe-{version}.json").write_text(json.dumps(results, indent=2))
    return results
