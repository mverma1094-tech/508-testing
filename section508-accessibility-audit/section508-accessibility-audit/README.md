# Section 508 / WCAG 2.1 AA Accessibility Audit

An end-to-end accessibility testing project: audit an inaccessible government-style web form, log every defect against WCAG 2.1 AA, remediate it, and lock the fixes in with an automated regression suite that runs in CI.

> **Demo only.** "Riverbend County" is a fictional agency. `app/before/` is intentionally inaccessible so the tests have real defects to find.

## Results

| | Before | After |
|---|---|---|
| Defects logged | 19 (5 Critical, 9 High, 5 Medium) | 0 open |
| axe-core WCAG A/AA violations | 8 rules | 0 |
| Automated checks passing | 1 of 19 | 19 of 19 |

**Key finding:** the automated axe scan caught only **8 of the 19** defects. Placeholder-only labels, removed focus outlines, a `<div>` submit button keyboard users couldn't reach, color-only error messages, and vague "click here" links were all missed by axe and found through keyboard testing, custom checks, and code review. That's why Section 508 testing pairs automated scans with manual and assistive-technology testing.

## What's in it

```
app/before/index.html          Inaccessible benefits application form (the system under test)
app/after/index.html           Remediated version
tests/test_axe_scan.py         axe-core scan, WCAG 2.0/2.1 A + AA rules only
tests/test_page_structure.py   Language, title, headings, landmarks, labels, ids, alt text, tables, link text, zoom, reflow
tests/test_keyboard_and_forms.py  Skip link, keyboard reachability, visible focus, error handling, live regions, ARIA state
docs/defect-log.csv            19 defects: WCAG SC, severity, actual vs expected, fix, verifying test
docs/manual-test-plan.md       NVDA, ANDI, zoom, contrast and text-spacing test cases
scripts/generate_report.py     Builds reports/accessibility-report.html from scan results + defect log
.github/workflows/, .gitlab-ci.yml  CI pipelines that run the suite on every push
```

## How the tests work

Every test runs against **both** versions of the page:

- **after** must pass. This is the regression suite that keeps fixes from breaking.
- **before** is marked `xfail(strict=True)`: the test *must* fail on the broken page. If a check ever stops catching its defect, the suite goes red. This proves each test actually detects what it claims to.

Each test's docstring names the WCAG success criterion it covers.

## Run it

Requires Python 3.10+ and Node 18+.

```bash
npm install                                  # axe-core
pip install -r requirements.txt
python -m playwright install chromium
pytest                                       # 20 passed, 18 xfailed
python scripts/generate_report.py            # reports/accessibility-report.html
```

## WCAG coverage

| WCAG 2.1 SC | Level | Covered by |
|---|---|---|
| 1.1.1 Non-text Content | A | axe, custom |
| 1.3.1 Info and Relationships | A | axe, custom, manual |
| 1.4.1 Use of Color | A | custom, manual |
| 1.4.3 Contrast (Minimum) | AA | axe, manual |
| 1.4.4 Resize Text | AA | axe, custom, manual |
| 1.4.10 Reflow | AA | custom, manual |
| 2.1.1 Keyboard | A | custom, manual |
| 2.4.1 Bypass Blocks | A | custom, manual |
| 2.4.2 Page Titled | A | axe, custom |
| 2.4.4 Link Purpose | A | custom, manual |
| 2.4.6 Headings and Labels | AA | custom, manual |
| 2.4.7 Focus Visible | AA | custom, manual |
| 3.1.1 Language of Page | A | axe, custom |
| 3.3.1 Error Identification | A | custom, manual |
| 3.3.2 Labels or Instructions | A | custom, manual |
| 4.1.1 Parsing | A | custom |
| 4.1.2 Name, Role, Value | A | axe, custom, manual |
| 4.1.3 Status Messages | AA | custom, manual |

## Tools

Playwright (Python) · PyTest · axe-core · GitHub Actions / GitLab CI · NVDA · ANDI · WebAIM Contrast Checker

## Background

Section 508 of the Rehabilitation Act requires federal agencies' information and communication technology to be accessible to people with disabilities. The 2017 Revised 508 Standards (36 CFR 1194) incorporate WCAG 2.0 Level A and AA by reference; many agencies now test against WCAG 2.1 AA.
