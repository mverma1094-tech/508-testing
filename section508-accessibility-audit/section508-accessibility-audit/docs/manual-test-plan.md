# Manual Accessibility Test Plan

Automated tools catch roughly a third to half of accessibility issues. In this project, axe found 8 of 19 logged defects. These manual cases cover what automation can't judge: how the page actually sounds and behaves for a screen reader or keyboard user.

**Page under test:** `app/after/index.html` (remediated)
**Standard:** Section 508 (36 CFR 1194, E205.4) / WCAG 2.1 Level AA
**Tools:** NVDA + Firefox or Chrome, keyboard only, ANDI bookmarklet, WebAIM Contrast Checker, browser zoom

> Status column starts as **Not run**. Fill it in only after you execute the case yourself, and record the NVDA/browser versions you used.

## Environment

| Item | Version used |
|---|---|
| OS | |
| Browser | |
| NVDA | |
| ANDI | |

## Test cases

| ID | WCAG SC | Tool | Steps | Expected result | Status |
|---|---|---|---|---|---|
| MT-01 | 2.4.1 Bypass Blocks | Keyboard | Load page, press Tab once, press Enter | "Skip to main content" appears on first Tab; Enter moves focus to the main region | Not run |
| MT-02 | 2.1.1 Keyboard, 2.1.2 No Keyboard Trap | Keyboard | Tab through every control to the end of the page, then Shift+Tab back | Every link, field and button is reachable in a logical order; focus never gets stuck | Not run |
| MT-03 | 2.4.7 Focus Visible | Keyboard | Tab through the page | A clearly visible orange outline is on every focused element | Not run |
| MT-04 | 2.4.2 Page Titled, 3.1.1 Language | NVDA | Open page with NVDA running | NVDA reads "Benefits Application, Riverbend County (Demo)" in an English voice | Not run |
| MT-05 | 1.3.1, 2.4.6 Headings | NVDA | Press Insert+F7, choose Headings | List shows h1 Benefits Application, then h2 Applicant information, Household, Income limits in order | Not run |
| MT-06 | 1.3.1 Landmarks | NVDA | Press D repeatedly | NVDA announces banner, navigation "Primary", main, content info | Not run |
| MT-07 | 3.3.2 Labels, 4.1.2 Name/Role/Value | NVDA | Tab into each form field | Each field announces its label and type, e.g. "Full name, edit, required"; Phone also reads its example hint | Not run |
| MT-08 | 3.3.1 Error Identification, 4.1.3 Status | NVDA | Leave fields empty, press Submit | Focus moves to "There is a problem"; NVDA reads the error list; each link moves focus to its field, which announces "invalid entry" plus its error text | Not run |
| MT-09 | 4.1.3 Status Messages | NVDA | Complete all fields and submit | NVDA announces "Application submitted. Thank you." without focus moving | Not run |
| MT-10 | 4.1.2 Name/Role/Value | NVDA + Keyboard | Focus "Help with household size", press Space twice | NVDA reads "collapsed" then "expanded"; help text appears and disappears | Not run |
| MT-11 | 1.3.1 Tables | NVDA | Move into the income table, use Ctrl+Alt+Arrow keys | Caption is read; moving across cells announces the column header and row header | Not run |
| MT-12 | 2.4.4 Link Purpose | NVDA | Insert+F7, Links list | Every link makes sense out of context | Not run |
| MT-13 | 1.1.1 Non-text Content | ANDI | Run ANDI, open graphics/images module | Logo has alt "Riverbend County seal"; no other images flagged | Not run |
| MT-14 | 1.3.1, 4.1.2 | ANDI | Run ANDI focusable elements module | No danger or warning alerts; every control has an accessible name | Not run |
| MT-15 | 1.4.3 Contrast | Contrast checker | Check body text, hint text, button, error red, focus outline | Text ≥ 4.5:1; focus outline and field borders ≥ 3:1 (1.4.11) | Not run |
| MT-16 | 1.4.4 Resize Text | Browser zoom | Zoom to 200% | All text readable, nothing cut off or overlapping | Not run |
| MT-17 | 1.4.10 Reflow | Browser zoom | Set window to 1280px wide, zoom to 400% | No horizontal scrolling; content stacks in one column | Not run |
| MT-18 | 1.4.12 Text Spacing | Text spacing bookmarklet | Apply WCAG text spacing overrides | No text is clipped or overlaps | Not run |
| MT-19 | 1.4.1 Use of Color | Grayscale filter | View error state in grayscale | Errors are still identifiable by "Error:" text and thicker borders | Not run |

## Reporting a failure

Log it in `docs/defect-log.csv` with: steps to reproduce, actual vs expected, WCAG success criterion, severity, and what NVDA actually announced (quote it word for word, since that's what developers need).
