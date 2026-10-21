"""Build reports/accessibility-report.html from the axe JSON files and the defect log.

Run the test suite first (it writes reports/axe-before.json and reports/axe-after.json):
    pytest && python scripts/generate_report.py
"""
import csv
import html
import json
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORTS = ROOT / "reports"
SEVERITY_ORDER = ["Critical", "High", "Medium", "Low"]
IMPACT_ORDER = ["critical", "serious", "moderate", "minor"]


def load_axe(version):
    path = REPORTS / f"axe-{version}.json"
    if not path.exists():
        raise SystemExit(f"{path} not found. Run `pytest` first.")
    return json.loads(path.read_text())


def esc(value):
    return html.escape(str(value))


def axe_rows(results):
    rows = sorted(results["violations"], key=lambda v: IMPACT_ORDER.index(v["impact"] or "minor"))
    out = []
    for v in rows:
        # axe tags success criteria like "wcag143" -> 1.4.3 (and "wcag1410" -> 1.4.10)
        sc = ", ".join(f"{t[4]}.{t[5]}.{t[6:]}" for t in v["tags"]
                       if t.startswith("wcag") and t[4:].isdigit() and len(t) >= 7)
        targets = "<br>".join(esc(", ".join(n["target"])) for n in v["nodes"])
        out.append(f"<tr><td><span class='pill {esc(v['impact'])}'>{esc(v['impact'])}</span></td>"
                   f"<td><code>{esc(v['id'])}</code></td><td>{esc(v['help'])}</td>"
                   f"<td>{esc(sc)}</td><td><code>{targets}</code></td></tr>")
    return "\n".join(out) or "<tr><td colspan='5'>No violations.</td></tr>"


def main():
    before, after = load_axe("before"), load_axe("after")
    with open(ROOT / "docs" / "defect-log.csv", newline="") as f:
        defects = list(csv.DictReader(f))

    by_sev = Counter(d["Severity"] for d in defects)
    axe_found = sum(1 for d in defects if d["Found By"].startswith("axe"))
    fixed = sum(1 for d in defects if d["Status"].startswith("Fixed"))

    defect_rows = "\n".join(
        f"<tr><td>{esc(d['ID'])}</td><td><span class='pill {d['Severity'].lower()}'>{esc(d['Severity'])}</span></td>"
        f"<td>{esc(d['Title'])}</td><td>{esc(d['WCAG SC'])} ({esc(d['Level'])})</td>"
        f"<td>{esc(d['Found By'])}</td><td>{esc(d['Fix Applied'])}</td><td>{esc(d['Status'])}</td></tr>"
        for d in sorted(defects, key=lambda d: SEVERITY_ORDER.index(d["Severity"]))
    )
    sev_summary = " · ".join(f"{by_sev.get(s, 0)} {s}" for s in SEVERITY_ORDER if by_sev.get(s))

    page = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Section 508 Audit Report | Riverbend County Demo</title>
<style>
:root {{ --ink:#1c2430; --muted:#4f5b6b; --line:#d5dbe3; --bg:#f6f8fb; --navy:#1f3a5f;
  --crit:#9b1c1c; --high:#b45309; --med:#1d4ed8; --ok:#166534; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; font:15px/1.55 system-ui, -apple-system, "Segoe UI", Arial, sans-serif; color:var(--ink); background:var(--bg); }}
header {{ background:var(--navy); color:#fff; padding:28px 16px; }}
header div, main {{ max-width:1080px; margin:0 auto; }}
header h1 {{ margin:0 0 4px; font-size:26px; }} header p {{ margin:0; opacity:.9; }}
main {{ padding:24px 16px 48px; }}
h2 {{ font-size:19px; margin:32px 0 10px; }}
.cards {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(170px,1fr)); gap:12px; }}
.card {{ background:#fff; border:1px solid var(--line); border-radius:8px; padding:14px 16px; }}
.card b {{ display:block; font-size:28px; }} .card span {{ color:var(--muted); font-size:13px; }}
.table-wrap {{ overflow-x:auto; background:#fff; border:1px solid var(--line); border-radius:8px; }}
table {{ border-collapse:collapse; width:100%; min-width:760px; font-size:14px; }}
th, td {{ text-align:left; padding:8px 10px; border-bottom:1px solid var(--line); vertical-align:top; }}
th {{ background:#eef2f7; }}
code {{ font-size:12.5px; word-break:break-word; }}
.pill {{ display:inline-block; padding:1px 8px; border-radius:99px; color:#fff; font-size:12px; font-weight:600; text-transform:capitalize; }}
.critical {{ background:var(--crit); }} .serious, .high {{ background:var(--high); }}
.moderate, .medium {{ background:var(--med); }} .minor, .low {{ background:var(--muted); }}
.note {{ color:var(--muted); font-size:14px; }}
</style></head>
<body>
<header><div><h1>Section 508 / WCAG 2.1 AA Audit</h1>
<p>Riverbend County Benefits Application (fictional demo) · generated {date.today():%B %d, %Y} · axe-core {esc(before['testEngine']['version'])}</p></div></header>
<main>
<h2>Summary</h2>
<div class="cards">
  <div class="card"><b>{len(defects)}</b><span>defects logged ({esc(sev_summary)})</span></div>
  <div class="card"><b>{axe_found} of {len(defects)}</b><span>found by automated axe scan alone</span></div>
  <div class="card"><b>{len(before['violations'])} → {len(after['violations'])}</b><span>axe rule violations, before → after</span></div>
  <div class="card"><b>{fixed}/{len(defects)}</b><span>defects fixed and verified</span></div>
</div>
<p class="note">Automated scanning caught {axe_found} of {len(defects)} issues. The rest (placeholder-only labels,
removed focus outlines, a keyboard-inaccessible submit control, color-only errors, vague links) needed keyboard
testing, custom checks, and manual review, which is why a 508 audit can't stop at an automated scan.</p>

<h2>Defect log</h2>
<div class="table-wrap"><table>
<thead><tr><th scope="col">ID</th><th scope="col">Severity</th><th scope="col">Issue</th><th scope="col">WCAG</th>
<th scope="col">Found by</th><th scope="col">Fix</th><th scope="col">Status</th></tr></thead>
<tbody>{defect_rows}</tbody></table></div>

<h2>Automated scan: before remediation</h2>
<div class="table-wrap"><table>
<thead><tr><th scope="col">Impact</th><th scope="col">Rule</th><th scope="col">Description</th><th scope="col">WCAG SC</th><th scope="col">Elements</th></tr></thead>
<tbody>{axe_rows(before)}</tbody></table></div>

<h2>Automated scan: after remediation</h2>
<p>{len(after['violations'])} violations · {len(after['passes'])} rules passed · {len(after['incomplete'])} needing manual review.</p>
</main></body></html>"""

    REPORTS.mkdir(exist_ok=True)
    out = REPORTS / "accessibility-report.html"
    out.write_text(page)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
