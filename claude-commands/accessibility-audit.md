# Accessibility Audit

> **READ-ONLY SKILL.** Produce analysis only: do not edit files, do not run
> mutating commands, and do not create or delete resources. Under Claude Code
> the `disallowed-tools` frontmatter above blocks Write/Edit (`allowed-tools`
> only pre-approves tools; it restricts nothing).
> Bash stays available for read-only inspection (grep, git log, scanners), so even
> under Claude Code "no mutating commands" is advisory, not enforced.
> **Other runtimes do not enforce it** — Codex and Antigravity ignore those
> fields, and activation there can widen rather than narrow file access — so on
> any runtime other than Claude Code this paragraph is the only guardrail.

**Outcome:** a WCAG 2.2 AA report for the scoped screens/flows: every finding with platform, success
criterion, file:line or element, severity, confidence, and a concrete fix, plus a release verdict.
**Done when** every screen in scope has been scanned and walked with a screen reader (or the walkthrough
is listed as not performed), and the report below is filled. Match length to the need; no filler sections.

## Pre-Processing (Auto-Context)

Context — run these read-only commands first; skip any that fail or aren't permitted (they only tailor the output):

- Stack manifest: `head -30 package.json 2>/dev/null || head -30 build.gradle.kts 2>/dev/null || head -20 Podfile 2>/dev/null || echo "(none detected)"`
- UI layout: `ls src/ app/ lib/ 2>/dev/null | head -20 || echo "(no src/app/lib)"`

## Step 1: Classify Audit Scope

| Scope | Depth |
|---|---|
| Single screen | Every element |
| Feature flow (checkout, onboarding) | All screens plus transitions, focus hand-off, error states |
| Full app | Critical journeys deep; representative sampling elsewhere |
| Platform-specific | One platform, its assistive tech fully exercised |

If scope is unclear, ask. For full-app audits, name the critical journeys first.

## Step 2: Gather Context

Platform(s); target level (default **WCAG 2.2 AA**); assistive tech to cover (TalkBack, VoiceOver,
Switch/Voice Access); design-system/component library (systemic vs one-off); prior audit baseline.

**Why 2.2 AA is Cure's default, and what the law actually cites** (verified 2026-09-23): the ADA Title II
rule (DOJ, 2024) and EN 301 549 v3.2.1 (the harmonised standard under the European Accessibility Act,
applicable since 2025-06-28) both reference **WCAG 2.1 AA**. Title II compliance dates were extended by
one year in 2026 — large public entities 2027-04-26, smaller entities and special districts 2028-04-26.
EN 301 549 v4.1.1 (WCAG 2.2) was published but its Official Journal citation is pending — confirm before
use. 2.2 AA is a superset of 2.1 AA, so auditing to 2.2 covers both; when a client asks "are we
compliant", report 2.1 AA conformance separately from the 2.2-only criteria (2.4.11, 2.5.7, 2.5.8, 3.2.6,
3.3.7, 3.3.8).

## Step 3: Automated Scan (before manual review)

Run these searches across the scoped code and record every hit with file:line. They are filters that
find candidates, not verdicts — confirm each hit in context.

| Check (SC) | Pattern / target |
|---|---|
| Missing alt (1.1.1) | `<img` without `alt=` in `*.tsx *.jsx *.html`; Compose `Image(`/`Icon(` with `contentDescription = null` on non-decorative images; SwiftUI `Image(` without `.accessibilityLabel` or `decorative:` |
| Unlabeled inputs (1.3.1, 3.3.2) | `<input` without `<label for>`/`aria-label`/`aria-labelledby`; placeholder-only labels; Compose `TextField(` without `label =` |
| Icon-only buttons (4.1.2) | `IconButton` / `<button>` containing only an icon with no accessible name |
| Target size (2.5.8 AA: ≥24×24 CSS px) | Web: `(width|height):\s*(1?[0-9]|2[0-3])px` on interactive elements. Compose: `\.size\((\d|[1-3]\d|4[0-7])\.dp\)` on clickables (below the 48dp platform guideline). SwiftUI: `.frame(width:` below 44 on buttons |
| Focus removed (2.4.7, 2.4.11) | `outline:\s*(none|0)` without a `:focus-visible` replacement; `tabIndex` > 0; `tabIndex={-1}` on interactive elements |
| Color-only meaning (1.4.1) | status/error styling that differs only by color token |
| Fixed font sizes (1.4.4) | Android text in `dp`; web font sizes in `px`; iOS fixed `.font(.system(size:))` without `relativeTo:` |
| Motion (2.3.3) | animations without `prefers-reduced-motion` / `accessibilityReduceMotion` guard |

Touch-target thresholds, stated once: **2.5.8 (AA) = 24×24 CSS px minimum** (or sufficient spacing);
**2.5.5 (AAA) = 44×44**. Platform guidelines are stricter and are Cure's build standard: Android 48×48dp
(`minimumInteractiveComponentSize()`), iOS 44×44pt. A 40dp Android target passes 2.5.8 but fails the
Cure standard — report it as Minor, not as a WCAG failure.

**Bundled script.** `scripts/wcag_check.py` (stdlib; `--help`, `--json`) is a static smoke check of one
HTML file or URL: missing alt, unlabeled inputs, skipped heading levels, missing `lang`, suspicious ARIA
roles, removed outlines. Run it on rendered web pages before the manual pass; it is also on PATH as
`cure-wcag-check` when the plugin is enabled. Run from the skill directory:

```bash
python3 scripts/wcag_check.py --html-file page.html --json
python3 scripts/wcag_check.py --url https://example.com --json
```

## Step 4: Manual Audit

Walk each screen against WCAG 2.2 AA (Perceivable, Operable, Understandable, Robust). The model knows
the criteria; spend attention on the places Cure apps actually fail:

- **Dynamic content**: toasts, snackbars, inline validation, and loading states not announced (live
  regions / `accessibilityLiveRegion` / `AccessibilityNotification.Announcement`).
- **Focus after change**: modal open/close, SPA route change, list item deletion — focus must land somewhere
  sensible and never on `<body>`.
- **Custom components**: bottom sheets, carousels, date pickers, swipe-to-delete — role, state, and a
  single-pointer alternative (2.5.7 dragging).
- **Text scaling**: 200% web zoom and 320px reflow; Android font scale 200% (non-linear scaling, API 34+);
  iOS AX5 Dynamic Type. Truncated or overlapping text is Major.
- **Auth and payments**: 3.3.8 accessible authentication (no cognitive-function test; allow paste and
  password managers); 3.3.7 redundant entry in multi-step forms.
- **Dark mode and high contrast**: re-check contrast in every theme and state (focus, disabled, error).

### Platform APIs to check

**Android (Compose):** `Modifier.semantics { contentDescription; stateDescription; role; heading() }`,
`clearAndSetSemantics {}` to kill duplicate announcements, `mergeDescendants = true` for list rows,
`customActions` for swipe actions, `minimumInteractiveComponentSize()`, `LiveRegionMode.Polite`. Views:
`importantForAccessibility="no"` on decoration, `android:accessibilityLiveRegion`, `labelFor`.

**iOS (SwiftUI):** `.accessibilityLabel/Value/Hint`, `.accessibilityElement(children: .combine)`,
`.accessibilityAddTraits(.isHeader/.isButton)`, `.accessibilityAction`, `.accessibilitySortPriority`,
`.accessibilityHidden` on decoration, `@Environment(\.accessibilityReduceMotion)`,
`@Environment(\.dynamicTypeSize)`, `.accessibilityIgnoresInvertColors()` on photos/media. UIKit:
`UIAccessibility.post(notification: .screenChanged / .layoutChanged / .announcement, …)`.

**Web:** native elements over `<div onclick>`; landmarks; skip link first; `:focus-visible` styles;
`aria-live="polite"` for status, `assertive` only for errors; `aria-expanded/pressed/checked` state;
`aria-hidden` never on focusable elements; `autocomplete` tokens on personal-data inputs (1.3.5); focus
moved to the `<h1>` or main region on route change.

### Tooling (supplements the manual pass; automated tools catch roughly a third of issues)

- Web: axe-core / axe DevTools, `eslint-plugin-jsx-a11y`, Pa11y CI. A Lighthouse accessibility score is
  a smoke signal only — a 100 does not mean AA conformance, so never report it as such.
- Android: Accessibility Scanner, Espresso `AccessibilityChecks.enable()`, Compose
  `composeTestRule.enableAccessibilityChecks()` (ui-test 1.8+; confirm before use on older BOMs), lint
  (`ContentDescription`, `ClickableViewAccessibility`, `LabelFor`).
- iOS: Xcode Accessibility Inspector; `try app.performAccessibilityAudit()` in XCUITest (Xcode 15+).
- Screen-reader matrix: TalkBack (Android app, Chrome Android), VoiceOver (iOS app, Safari iOS, Safari
  macOS), NVDA + Chrome (Windows). Cover every platform in scope; list any combination not tested.

## Step 5: Severity (Cure mapping)

Report **every** finding with severity and confidence (High = confirmed in a walkthrough or unambiguous in
code; Medium = strong code evidence, not exercised; Low = pattern match only). Rank after, never drop.

| Severity | Meaning | Examples | Release |
|---|---|---|---|
| Critical | A user group cannot complete a core task | unlabeled icon-only primary button; keyboard trap; focus lost in checkout; CAPTCHA with no alternative | Blocks release |
| Major | Significant barrier, workaround exists | placeholder-only labels; contrast 3.5:1 on body text; errors not announced; text truncates at 200% | Next sprint |
| Minor | Friction, task completes | redundant announcements; heading level skipped; target 40dp (Cure standard, not WCAG) | Backlog |

## Step 6: Report

```
ACCESSIBILITY AUDIT — [feature/screen] — [date]
Standard: WCAG 2.2 AA (2.1 AA conformance reported separately) | Platforms: [..]
Verdict: PASS (0 Critical, 0 Major) | CONDITIONAL (0 Critical, Majors ticketed) | FAIL (any Critical)

FINDINGS (all, grouped by severity)
| # | Sev | Conf | Platform | SC | Element / file:line | Finding | Fix |

SCREEN READER RESULTS
| Platform | Reader | Result | Notes (or "not tested") |

AUTOMATED TOOLS: axe [n violations] · wcag_check [n] · Scanner [n] · Xcode audit [n]
SYSTEMIC ISSUES: [component-library fixes that clear many findings at once]
2.1 AA CONFORMANCE: [pass/fail + which failures are 2.2-only]
```

## Recurring Mode

This is a recurring goal, not a one-shot (mechanism trade-offs: the `engagement-automation` skill).

- **Cadence:** weekly or per release.
- **Session loop:** session loops expire after 7 days, so a weekly cadence belongs in a `/schedule` cloud
  routine. In-session alternative during an active UI push: `/loop 1d /cure-product-engineering:accessibility-audit`.
- **Unattended:** cloud routine — weekly WCAG 2.2 sweep of changed screens; full sweep per release.
  Recipes: docs/AUTOMATION.md in the plugin repo.
- **Budget:** ~100k tokens/run; cap at one run per weekly period.
- **Guardrails:** this skill stays read-only and returns the report. The routine that invoked it — not the
  skill — files findings as issues, deduplicated against open ones. Report on failure rather than retrying.
