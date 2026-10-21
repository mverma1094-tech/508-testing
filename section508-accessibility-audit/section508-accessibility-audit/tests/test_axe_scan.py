"""Automated WCAG 2.1 A/AA scan with axe-core (the engine behind axe DevTools)."""
import pytest

from conftest import ALL_VERSIONS, run_axe


def format_violations(violations):
    lines = []
    for v in violations:
        lines.append(f"[{v['impact']}] {v['id']}: {v['help']} ({len(v['nodes'])} element(s))")
        for node in v["nodes"][:3]:
            lines.append(f"    -> {', '.join(node['target'])}")
    return "\n".join(lines)


@pytest.mark.parametrize("version", ALL_VERSIONS)
def test_no_wcag_aa_violations(open_page, version):
    page = open_page(version)
    results = run_axe(page, version)
    violations = results["violations"]
    assert not violations, (
        f"{len(violations)} axe rule(s) failed on '{version}':\n" + format_violations(violations)
    )
