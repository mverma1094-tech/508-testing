"""Structural checks a manual 508 tester (ANDI / code inspection) would perform.

Each test cites the WCAG 2.1 success criterion it covers. Section 508 (36 CFR 1194)
incorporates WCAG 2.0 A/AA by reference; WCAG 2.1 AA is the common agency target.
"""
import re

import pytest

from conftest import ALL_VERSIONS

GENERIC_LINK_TEXT = {"click here", "here", "read more", "more", "link", "learn more"}


@pytest.mark.parametrize("version", ALL_VERSIONS)
def test_page_language_is_set(open_page, version):
    """WCAG 3.1.1 Language of Page (A)."""
    lang = open_page(version).get_attribute("html", "lang")
    assert lang and re.match(r"^[a-z]{2}(-[A-Z]{2})?$", lang), f"<html lang> missing or invalid: {lang!r}"


@pytest.mark.parametrize("version", ALL_VERSIONS)
def test_page_has_descriptive_title(open_page, version):
    """WCAG 2.4.2 Page Titled (A)."""
    title = open_page(version).title().strip()
    assert len(title) >= 5, f"Page title missing or too short: {title!r}"


@pytest.mark.parametrize("version", ALL_VERSIONS)
def test_heading_levels_do_not_skip(open_page, version):
    """WCAG 1.3.1 Info and Relationships (A) / 2.4.6 Headings and Labels (AA)."""
    page = open_page(version)
    levels = page.eval_on_selector_all("h1,h2,h3,h4,h5,h6", "els => els.map(e => +e.tagName[1])")
    assert levels.count(1) == 1, f"Expected exactly one h1, found {levels.count(1)}"
    for prev, cur in zip(levels, levels[1:]):
        assert cur <= prev + 1, f"Heading level jumps from h{prev} to h{cur} (sequence: {levels})"


@pytest.mark.parametrize("version", ALL_VERSIONS)
def test_landmarks_present(open_page, version):
    """WCAG 1.3.1 (A) / 2.4.1 Bypass Blocks (A): screen reader users navigate by landmark."""
    page = open_page(version)
    assert page.locator("main, [role=main]").count() == 1, "Page needs exactly one <main> landmark"
    assert page.locator("nav, [role=navigation]").count() >= 1, "Navigation links should be in a <nav>"


@pytest.mark.parametrize("version", ALL_VERSIONS)
def test_form_controls_have_programmatic_labels(open_page, version):
    """WCAG 1.3.1 (A), 3.3.2 Labels or Instructions (A), 4.1.2 Name, Role, Value (A).

    A placeholder is NOT a label: it disappears on input and is not reliably announced.
    """
    page = open_page(version)
    unlabeled = page.eval_on_selector_all(
        "input:not([type=hidden]), select, textarea",
        """els => els.filter(e =>
              !(e.labels && e.labels.length) &&
              !e.getAttribute('aria-label') &&
              !e.getAttribute('aria-labelledby')
           ).map(e => e.outerHTML.slice(0, 80))""",
    )
    assert not unlabeled, "Form controls without a label:\n" + "\n".join(unlabeled)


@pytest.mark.parametrize("version", ALL_VERSIONS)
def test_ids_are_unique(open_page, version):
    """WCAG 4.1.1 Parsing (A, 2.0/2.1): duplicate ids break label/aria references."""
    page = open_page(version)
    ids = page.eval_on_selector_all("[id]", "els => els.map(e => e.id)")
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    assert not dupes, f"Duplicate id values: {dupes}"


@pytest.mark.parametrize("version", ALL_VERSIONS)
def test_images_have_text_alternatives(open_page, version):
    """WCAG 1.1.1 Non-text Content (A)."""
    page = open_page(version)
    missing = page.eval_on_selector_all("img", "els => els.filter(e => !e.hasAttribute('alt')).length")
    assert missing == 0, f"{missing} <img> element(s) have no alt attribute"


@pytest.mark.parametrize("version", ALL_VERSIONS)
def test_data_tables_have_headers(open_page, version):
    """WCAG 1.3.1 Info and Relationships (A)."""
    page = open_page(version)
    tables = page.locator("table")
    for i in range(tables.count()):
        table = tables.nth(i)
        assert table.locator("th").count() > 0, f"Table {i + 1} has no <th> header cells"
        assert table.locator("caption").count() == 1, f"Table {i + 1} has no <caption>"


@pytest.mark.parametrize("version", ALL_VERSIONS)
def test_link_purpose_is_clear(open_page, version):
    """WCAG 2.4.4 Link Purpose (In Context) (A). axe does not catch this; it's a manual check."""
    page = open_page(version)
    texts = page.eval_on_selector_all("a[href]", "els => els.map(e => e.innerText.trim().toLowerCase())")
    vague = [t for t in texts if t in GENERIC_LINK_TEXT or not t]
    assert not vague, f"Links with vague or empty text: {vague}"


@pytest.mark.parametrize("version", ALL_VERSIONS)
def test_zoom_is_not_disabled(open_page, version):
    """WCAG 1.4.4 Resize Text (AA): users must be able to zoom to 200%."""
    page = open_page(version)
    content = page.get_attribute("meta[name=viewport]", "content") or ""
    assert "user-scalable=no" not in content.replace(" ", ""), "Viewport meta blocks pinch-zoom"
    match = re.search(r"maximum-scale=([\d.]+)", content)
    assert not match or float(match.group(1)) >= 2, f"maximum-scale too low: {content}"


@pytest.mark.parametrize("version", ["before", "after"])
def test_reflow_at_320_css_pixels(open_page, version, page):
    """WCAG 1.4.10 Reflow (AA): no horizontal scrolling at 320px wide (400% zoom equivalent).

    Not every check fails on the 'before' page: its simple layout already reflows,
    so this one is expected to pass on both versions.
    """
    page.set_viewport_size({"width": 320, "height": 640})
    open_page(version)
    overflow = page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
    assert overflow <= 0, f"Content overflows horizontally by {overflow}px at 320px width"
