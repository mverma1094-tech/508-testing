"""Keyboard-only and form-error tests (what a tester checks with Tab/Enter/Space before opening NVDA)."""
import pytest

from conftest import ALL_VERSIONS

FOCUS_INDICATOR_JS = """() => {
  const el = document.activeElement;
  const s = getComputedStyle(el);
  const outline = s.outlineStyle !== 'none' && parseFloat(s.outlineWidth) > 0;
  const shadow = s.boxShadow && s.boxShadow !== 'none';
  return { tag: el.tagName, text: (el.innerText || el.id || '').trim().slice(0, 40), visible: outline || shadow };
}"""


def tab_stops(page, limit=30):
    """Press Tab repeatedly and record each focused element until focus leaves the page."""
    stops = []
    for _ in range(limit):
        page.keyboard.press("Tab")
        info = page.evaluate(FOCUS_INDICATOR_JS)
        if info["tag"] == "BODY":
            break
        stops.append(info)
    return stops


@pytest.mark.parametrize("version", ALL_VERSIONS)
def test_skip_link_is_first_and_moves_focus_to_main(open_page, version):
    """WCAG 2.4.1 Bypass Blocks (A)."""
    page = open_page(version)
    page.keyboard.press("Tab")
    first = page.evaluate("document.activeElement.getAttribute('href')")
    assert first == "#main", f"First Tab stop should be the skip link, got href={first!r}"
    page.keyboard.press("Enter")
    focused = page.evaluate("document.activeElement.id")
    assert focused == "main", f"Skip link should move focus to <main>, focus is on #{focused}"


@pytest.mark.parametrize("version", ALL_VERSIONS)
def test_submit_is_reachable_by_keyboard(open_page, version):
    """WCAG 2.1.1 Keyboard (A): every action available by mouse is available by keyboard."""
    page = open_page(version)
    stops = tab_stops(page)
    assert any(s["text"].lower().startswith("submit") for s in stops), (
        "Submit control never receives keyboard focus. Tab order: " + str([s["text"] for s in stops])
    )


@pytest.mark.parametrize("version", ALL_VERSIONS)
def test_every_tab_stop_has_visible_focus(open_page, version):
    """WCAG 2.4.7 Focus Visible (AA)."""
    page = open_page(version)
    stops = tab_stops(page)
    assert stops, "No focusable elements found"
    invisible = [f"{s['tag']} '{s['text']}'" for s in stops if not s["visible"]]
    assert not invisible, "Elements with no visible focus indicator:\n" + "\n".join(invisible)


@pytest.mark.parametrize("version", ALL_VERSIONS)
def test_errors_are_announced_and_linked_to_fields(open_page, version):
    """WCAG 3.3.1 Error Identification (A), 1.4.1 Use of Color (A), 4.1.3 Status Messages (AA).

    Submit the empty form with the keyboard. Errors must be described in text,
    tied to each field with aria-invalid + aria-describedby, and focus must move
    to an error summary so screen reader users hear about the problem.
    """
    page = open_page(version)
    page.locator("#name").focus()
    page.keyboard.press("Enter")  # implicit form submission from a text field

    focused_role = page.evaluate("document.activeElement.getAttribute('role')")
    assert focused_role == "alert", "Focus should move to an error summary with role=alert"

    name = page.locator("#name")
    assert name.get_attribute("aria-invalid") == "true", "Invalid field is missing aria-invalid=true"
    described = (name.get_attribute("aria-describedby") or "").split()
    assert "name-error" in described, "Field is not linked to its error text via aria-describedby"
    assert page.locator("#name-error").inner_text().strip(), "Error text is empty"


@pytest.mark.parametrize("version", ALL_VERSIONS)
def test_error_summary_links_move_focus_to_field(open_page, version):
    """WCAG 3.3.1 / 2.4.3 Focus Order (A)."""
    page = open_page(version)
    page.locator("#name").focus()
    page.keyboard.press("Enter")
    page.keyboard.press("Tab")  # first link inside the focused error summary
    page.keyboard.press("Enter")
    assert page.evaluate("document.activeElement.id") == "name"


@pytest.mark.parametrize("version", ALL_VERSIONS)
def test_success_message_is_a_live_status(open_page, version):
    """WCAG 4.1.3 Status Messages (AA): confirmation is announced without moving focus."""
    page = open_page(version)
    page.fill("#name", "Test User")
    page.fill("#email", "test.user@example.com")
    page.fill("#phone", "703-555-0100")
    page.select_option("#county", "North")
    page.fill("#household", "2")
    page.locator("#household").press("Enter")
    status = page.locator("[role=status]")
    assert status.count() == 1, "No role=status live region for the confirmation message"
    assert "submitted" in status.inner_text().lower()


@pytest.mark.parametrize("version", ALL_VERSIONS)
def test_disclosure_button_exposes_state(open_page, version):
    """WCAG 4.1.2 Name, Role, Value (A): toggle buttons report expanded/collapsed."""
    page = open_page(version)
    btn = page.locator("button[aria-controls]")
    assert btn.count() == 1, "Help control is not a button with aria-controls"
    assert btn.get_attribute("aria-expanded") == "false"
    btn.focus()
    page.keyboard.press("Space")
    assert btn.get_attribute("aria-expanded") == "true"
    assert page.locator("#" + btn.get_attribute("aria-controls")).is_visible()
