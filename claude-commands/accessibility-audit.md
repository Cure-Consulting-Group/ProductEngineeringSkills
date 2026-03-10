# Accessibility Audit

Comprehensive WCAG 2.2 accessibility audit across Android, iOS, and Web platforms. Evaluates perceivability, operability, understandability, and robustness. Produces a scored compliance report with severity-ranked findings and actionable remediation guidance.

## When to Run

1. **Pre-Release** — Before any feature, screen, or flow ships to production
2. **Explicit Request** — When asked for an accessibility audit, a11y review, WCAG check, or inclusive design review
3. **Regulatory Compliance** — When preparing for ADA, Section 508, EN 301 549, or EAA compliance
4. **Post-Incident** — After an accessibility complaint, failed audit, or assistive technology breakage

Execute all 9 steps in order. Do not skip steps. Do not summarize — audit.

## Step 1: Classify Audit Scope

Determine the scope before beginning. The scope dictates depth and breadth of every subsequent step.

| Scope | Description | Depth |
|---|---|---|
| Single Screen | One view/page in isolation | Deep — every element audited |
| Feature Flow | Multi-screen user journey (e.g., checkout, onboarding) | Deep — all screens plus transitions and state changes |
| Full App | Entire application | Broad — representative sampling per screen, deep on critical paths |
| Platform-Specific | Audit targeting one platform only (Android, iOS, or Web) | Deep — platform idioms and assistive tech fully tested |

If scope is unclear, ask before proceeding. For full app audits, identify critical user journeys first and prioritize those.

## Step 2: Gather Context

Collect the following before auditing:

| Input | Required | Notes |
|---|---|---|
| Platform(s) | Yes | Android, iOS, Web, or combination |
| Target WCAG Level | Yes | AA (minimum) or AAA — default to AA if unspecified |
| Assistive tech requirements | Yes | TalkBack, VoiceOver, Switch Access, Voice Control, screen magnifiers |
| User demographics | Optional | Age range, known disabilities, locale/language considerations |
| Design system/component library | Optional | Helps identify systemic vs. one-off issues |
| Previous audit results | Optional | Baseline for regression tracking |

If target WCAG level is not specified, **default to WCAG 2.2 Level AA**. This is the legally required standard in most jurisdictions and the only defensible baseline.

## Step 3: Perceivable Audit (WCAG Principle 1)

Every piece of information and UI component must be presentable to users in ways they can perceive.

### 3.1 Text Alternatives (1.1.1)
- **Every** non-decorative image has a meaningful text alternative
- Decorative images are explicitly hidden from assistive tech (`role="none"`, `importantForAccessibility=no`, `isAccessibilityElement=false`)
- Complex images (charts, diagrams, infographics) have long descriptions or structured alternatives
- Icon buttons have accessible names — icon-only buttons without labels are a **Critical** finding
- Image text alternatives describe function, not appearance ("Submit form" not "blue button")

### 3.2 Time-Based Media (1.2.x)
- Pre-recorded audio has transcripts
- Pre-recorded video has captions AND audio descriptions where visual-only information is conveyed
- Live audio has real-time captions (Level AA)
- Captions are synchronized, accurate, and include speaker identification and sound effects

### 3.3 Color Contrast (1.4.x)
- **Normal text** (< 18pt / < 14pt bold): minimum **4.5:1** contrast ratio against background
- **Large text** (>= 18pt / >= 14pt bold): minimum **3:1** contrast ratio
- **UI components and graphical objects**: minimum **3:1** contrast ratio against adjacent colors
- Color is **never the sole means** of conveying information (error states, status indicators, chart data)
- Check contrast in all themes: light mode, dark mode, high-contrast mode
- Verify contrast across all component states: default, hover, focus, active, disabled

### 3.4 Text Resizing and Reflow (1.4.4, 1.4.10)
- Content remains functional at **200% text zoom**
- No horizontal scrolling at **320px CSS viewport width** (reflow)
- No loss of content or functionality when text is resized
- Android: `sp` units for text, never `dp` or `px`
- iOS: Dynamic Type supported with all text styles; test at **AX5** size
- Web: relative units (`rem`, `em`, `%`) — no `px` for font sizes

### 3.5 Non-Text Content (1.3.x)
- Information conveyed through visual formatting is also available programmatically
- Data tables have proper headers (`<th>`, `scope`, `headers` attributes)
- Lists use semantic list markup
- Reading order matches visual order
- Content relationships are programmatically determinable

## Step 4: Operable Audit (WCAG Principle 2)

All UI components and navigation must be operable by all users regardless of input method.

### 4.1 Keyboard Navigation (2.1.x)
- **Every** interactive element is reachable and operable via keyboard alone
- Tab order is logical and follows visual layout (no tab traps)
- Focus is never lost after interactions (modal dismissal, dynamic content, route changes)
- Custom keyboard shortcuts do not conflict with assistive tech shortcuts
- No functionality requires specific timings for keystrokes

### 4.2 Focus Management (2.4.x)
- Focus indicator is **always visible** — never suppressed with `outline: none` without replacement
- Focus indicator has minimum **3:1** contrast ratio (WCAG 2.2)
- Focus moves logically after dynamic content changes (dialogs, drawers, toasts)
- Skip links are present and functional on Web (skip to main content)
- Page/screen titles are descriptive and unique
- Focus is trapped inside modals and released on dismissal
- Heading hierarchy is logical (`h1` > `h2` > `h3`, no skipped levels)

### 4.3 Touch Targets (2.5.8 — WCAG 2.2)
- **Android**: minimum **48x48dp** touch target size
- **iOS**: minimum **44x44pt** touch target size
- **Web**: minimum **24x24 CSS px** target size (WCAG 2.2 Level AA), **44x44 CSS px** recommended
- Adequate spacing between adjacent targets (no overlapping touch areas)
- Inline links in body text are exempt but should still be distinguishable

### 4.4 Gesture Alternatives (2.5.x)
- **Every** path-based gesture (swipe, pinch, multi-finger) has a single-pointer alternative
- Drag-and-drop operations have button-based alternatives
- Motion-activated features (shake, tilt) can be disabled and have UI alternatives
- `pointer-events: none` is not used to block interaction on elements that should be interactive

### 4.5 Motion and Animation (2.3.x, 2.2.2)
- Animations respect `prefers-reduced-motion` (Web) / system reduce-motion settings (iOS/Android)
- No content flashes more than **3 times per second**
- Auto-playing content can be paused, stopped, or hidden
- Parallax, auto-scrolling, and auto-advancing carousels have controls

## Step 5: Understandable Audit (WCAG Principle 3)

Information and UI operation must be understandable.

### 5.1 Readable Content (3.1.x)
- Page/screen language is programmatically set (`lang` attribute, `Locale` configuration)
- Language changes within content are marked (`lang` attribute on inline elements)
- Reading level is appropriate for the audience — plain language preferred
- Abbreviations and jargon are expanded on first use or via glossary
- Text alignment is left-aligned (or start-aligned for RTL) — never fully justified

### 5.2 Predictable Navigation (3.2.x)
- Receiving focus does not trigger a change of context
- Changing a setting does not automatically trigger a change of context without warning
- Navigation is consistent across pages/screens
- Components that appear on multiple screens behave identically
- Back navigation works predictably — no broken back stacks

### 5.3 Error Identification and Recovery (3.3.x)
- Errors are identified in text, not just color or icon
- Error messages describe what went wrong **and how to fix it**
- Error messages are associated with the input field programmatically (not just visually)
- Form validation errors are announced to screen readers immediately
- Users can review and correct input before final submission (financial/legal transactions)
- Required fields are indicated both visually and programmatically

### 5.4 Labels and Instructions (3.3.x)
- Every form input has a visible, persistent label — placeholder-only labels are a **Major** finding
- Labels are programmatically associated with their controls
- Required fields are clearly indicated before the user encounters them
- Help text and instructions are provided before the input, not only after error
- Input purpose is programmatically identifiable for autocomplete (`autocomplete`, `textContentType`, `autofillHints`)

## Step 6: Robust Audit (WCAG Principle 4)

Content must be robust enough to be interpreted by a wide variety of assistive technologies.

### 6.1 Semantic Structure
- **Web**: semantic HTML elements used (`<nav>`, `<main>`, `<header>`, `<footer>`, `<article>`, `<section>`, `<aside>`)
- **Web**: ARIA landmarks present and correct (`role="banner"`, `role="navigation"`, `role="main"`, `role="contentinfo"`)
- **Android**: accessibility tree is well-structured — use Layout Inspector to verify
- **iOS**: accessibility tree is well-structured — use Accessibility Inspector to verify
- All elements have correct **roles**, **names**, and **values** in the accessibility tree
- Custom components expose correct semantics (not just visual appearance)

### 6.2 ARIA Usage (Web)
- ARIA is used only when native HTML semantics are insufficient — **first rule of ARIA: don't use ARIA**
- No conflicting roles (e.g., `<button role="link">`)
- All `aria-*` attributes are valid for the element's role
- `aria-label`, `aria-labelledby`, `aria-describedby` references point to existing elements
- Dynamic content regions use `aria-live` appropriately (`polite` for updates, `assertive` for errors)
- `aria-hidden="true"` is never applied to focusable elements
- Toggle/expansion states use `aria-expanded`, `aria-pressed`, `aria-checked` correctly

### 6.3 Screen Reader Testing Matrix

Test the following combinations at minimum:

| Platform | Screen Reader | Browser/Environment |
|---|---|---|
| Android | TalkBack | Native app |
| iOS | VoiceOver | Native app |
| Web (Desktop) | NVDA | Chrome |
| Web (Desktop) | VoiceOver | Safari |
| Web (Mobile) | TalkBack | Chrome Android |
| Web (Mobile) | VoiceOver | Safari iOS |

For each combination, verify:
- All content is announced in logical order
- Interactive elements announce their role, name, state, and value
- Dynamic updates are announced appropriately
- Navigation between elements is complete (no orphaned or unreachable content)
- Custom components are fully operable via screen reader gestures

## Step 7: Platform-Specific Checks

### 7.1 Android

- **`contentDescription`** set on all meaningful `ImageView`, `ImageButton`, and icon-only views
- **`importantForAccessibility`** set to `no` on decorative elements and layout wrappers
- **TalkBack navigation**: swipe through every screen — every interactive element must be reachable and announced correctly
- **Jetpack Compose semantics**:
  - `Modifier.semantics {}` with `contentDescription`, `stateDescription`, `role`
  - `Modifier.clearAndSetSemantics {}` to prevent duplicate announcements from child elements
  - `mergeDescendants = true` for logically grouped content (e.g., list items)
  - Custom actions exposed via `semantics { customActions = listOf(...) }`
- **Live regions**: `android:accessibilityLiveRegion` for dynamic content (snackbars, counters, status updates)
- **Touch target sizing**: enforce 48x48dp minimum via `Modifier.sizeIn(minWidth = 48.dp, minHeight = 48.dp)` or `minimumInteractiveComponentSize()`
- **Heading semantics**: `Modifier.semantics { heading() }` on section headings for TalkBack heading navigation
- **Switch Access and Voice Access**: verify all interactive elements are labeled and reachable

### 7.2 iOS

- **`accessibilityLabel`** set on all meaningful UI elements — concise, descriptive, no redundant type info ("Play" not "Play button")
- **`accessibilityHint`** for non-obvious actions ("Double-tap to start playback")
- **`accessibilityTraits`** correctly assigned (`.button`, `.header`, `.selected`, `.adjustable`, `.image`)
- **VoiceOver testing**: swipe through every screen — verify announcement order, grouping, and custom actions
- **Dynamic Type**: all text scales with `UIFontMetrics` or SwiftUI `.font(.body)` text styles; test at Accessibility sizes (AX1-AX5)
- **SwiftUI accessibility modifiers**:
  - `.accessibilityLabel()`, `.accessibilityValue()`, `.accessibilityHint()`
  - `.accessibilityElement(children: .combine)` for logical grouping
  - `.accessibilityAddTraits()`, `.accessibilityRemoveTraits()`
  - `.accessibilityAction()` for custom actions
  - `.accessibilitySortPriority()` to control reading order
  - `.accessibilityHidden()` for decorative elements
- **UIKit accessibility**:
  - `isAccessibilityElement`, `accessibilityElements`, `accessibilityElementsHidden`
  - `UIAccessibilityPostNotification` for dynamic content changes (`.screenChanged`, `.layoutChanged`, `.announcement`)
- **Reduce Motion**: respect `UIAccessibility.isReduceMotionEnabled` / `@Environment(\.accessibilityReduceMotion)`
- **Bold Text**: support `UIAccessibility.isBoldTextEnabled`
- **Smart Invert**: ensure images and media are flagged with `accessibilityIgnoresInvertColors = true`

### 7.3 Web

- **Semantic HTML**: use `<button>`, `<a>`, `<input>`, `<select>`, `<textarea>` — never `<div onclick>`
- **ARIA landmarks**: `<header>`, `<nav>`, `<main>`, `<aside>`, `<footer>` present on every page
- **Focus management**:
  - `tabindex="0"` only on elements that need to be focusable but are not natively
  - `tabindex="-1"` for programmatic focus (e.g., error summary, modal container)
  - Never use `tabindex` > 0
  - `focus-visible` for keyboard-only focus styles
- **Skip links**: "Skip to main content" link as first focusable element on every page
- **Alt text**: every `<img>` has `alt` attribute — meaningful alt for content images, `alt=""` for decorative
- **Forms**: `<label>` with `for` attribute on every input; fieldsets with legends for radio/checkbox groups
- **Live regions**: `aria-live="polite"` for status updates, `aria-live="assertive"` for errors and alerts
- **Responsive accessibility**: touch targets, contrast, and content order verified at all breakpoints
- **SPA routing**: focus managed on route changes — focus moves to page heading or main content region
- **Reduced motion**: `@media (prefers-reduced-motion: reduce)` disables non-essential animations

## Step 8: Automated Testing Tools

Run automated tools as a **supplement** to manual testing. Automated tools catch approximately 30-40% of accessibility issues. Manual testing is non-negotiable.

### Web
- **axe-core** / **axe DevTools**: run on every page/state — zero violations is the baseline
- **Lighthouse Accessibility**: score must be **95+** for Level AA compliance
- **WAVE**: visual overlay for quick identification of structural issues
- **eslint-plugin-jsx-a11y** (React) or equivalent linter: enforce at build time
- **Pa11y CI**: integrate into CI pipeline for regression prevention

### Android
- **Accessibility Scanner**: run on every screen — resolve all suggestions
- **Espresso AccessibilityChecks**: `AccessibilityChecks.enable()` in UI tests
- **Lint checks**: `MissingContentDescription`, `ClickableViewAccessibility`, `LabelFor`
- **Compose UI test**: `composeTestRule.onNode(hasContentDescription(...))` assertions

### iOS
- **Xcode Accessibility Inspector**: audit every screen — resolve all warnings
- **XCTest accessibility assertions**: `XCTAssertTrue(element.isAccessibilityElement)`
- **Accessibility Audit** (Xcode 15+): `try app.performAccessibilityAudit()`
- **SwiftLint custom rules**: flag missing accessibility modifiers on interactive elements

### Cross-Platform
- **Manual screen reader walkthrough**: non-negotiable for every audit
- **Color contrast analyzers**: Colour Contrast Analyser (CCA), WebAIM Contrast Checker
- **Keyboard-only testing**: navigate entire flow without mouse/touch

## Step 9: Audit Report Output

```
═══════════════════════════════════════════════════════════════
ACCESSIBILITY AUDIT REPORT
Feature/Screen: [NAME]
Date: [TODAY]
Target Standard: WCAG 2.2 Level [AA/AAA]
Platform(s): [Android / iOS / Web]
═══════════════════════════════════════════════════════════════

COMPLIANCE SUMMARY SCORECARD
┌──────────────────────────┬─────────┬─────────┬─────────┬────────┬────────┐
│ WCAG Principle           │ Android │   iOS   │   Web   │ Score  │ Status │
├──────────────────────────┼─────────┼─────────┼─────────┼────────┼────────┤
│ 1. Perceivable           │  X/10   │  X/10   │  X/10   │  X/30  │ pass/fail │
│ 2. Operable              │  X/10   │  X/10   │  X/10   │  X/30  │ pass/fail │
│ 3. Understandable        │  X/10   │  X/10   │  X/10   │  X/30  │ pass/fail │
│ 4. Robust                │  X/10   │  X/10   │  X/10   │  X/30  │ pass/fail │
├──────────────────────────┼─────────┼─────────┼─────────┼────────┼────────┤
│ OVERALL                  │  X/40   │  X/40   │  X/40   │ X/120  │        │
└──────────────────────────┴─────────┴─────────┴─────────┴────────┴────────┘

Scoring: PASS >= 80% | CONDITIONAL 60-79% | FAIL < 60%

CRITICAL FINDINGS (block release — must fix before ship)
Severity: Critical — These issues make content completely inaccessible to one or more user groups.
1. [Platform] — [WCAG SC X.X.X] — [Finding] — [Element/File] — [Remediation]

MAJOR FINDINGS (fix before next release)
Severity: Major — These issues create significant barriers but do not completely block access.
1. [Platform] — [WCAG SC X.X.X] — [Finding] — [Element/File] — [Remediation]

MINOR FINDINGS (fix in backlog)
Severity: Minor — These issues cause inconvenience but do not prevent task completion.
1. [Platform] — [WCAG SC X.X.X] — [Finding] — [Element/File] — [Remediation]

SCREEN READER TEST RESULTS
┌────────────────┬──────────────┬──────────┬─────────────────────────────┐
│ Platform       │ Screen Reader│ Result   │ Notes                       │
├────────────────┼──────────────┼──────────┼─────────────────────────────┤
│ Android        │ TalkBack     │ pass/fail│                             │
│ iOS            │ VoiceOver    │ pass/fail│                             │
│ Web (Desktop)  │ NVDA/Chrome  │ pass/fail│                             │
│ Web (Desktop)  │ VO/Safari    │ pass/fail│                             │
│ Web (Mobile)   │ TalkBack     │ pass/fail│                             │
│ Web (Mobile)   │ VoiceOver    │ pass/fail│                             │
└────────────────┴──────────────┴──────────┴─────────────────────────────┘

AUTOMATED TOOL RESULTS
- axe-core: X violations / X passes
- Lighthouse Accessibility: XX/100
- Android Accessibility Scanner: X suggestions
- Xcode Accessibility Inspector: X warnings

PLATFORM-SPECIFIC ISSUES
1. [Platform] — [Issue] — [Component/File] — [Fix]

CROSS-PLATFORM CONSISTENCY ISSUES
1. [Behavior that differs across platforms] — [Impact on users] — [Fix]

REMEDIATION PRIORITY MATRIX
┌──────────┬──────────────┬──────────────────┬───────────────────────────┐
│ Priority │ Severity     │ Timeline         │ Action                    │
├──────────┼──────────────┼──────────────────┼───────────────────────────┤
│ P0       │ Critical     │ Before release   │ Block deployment          │
│ P1       │ Major        │ Next sprint      │ Schedule immediately      │
│ P2       │ Minor        │ Within quarter   │ Add to backlog            │
└──────────┴──────────────┴──────────────────┴───────────────────────────┘

RECOMMENDATIONS
- [Architectural, process, or tooling improvement for long-term accessibility]

NEXT ACTIONS CHECKLIST
[ ] Fix all CRITICAL findings before release
[ ] Schedule all MAJOR findings for next sprint
[ ] Add all MINOR findings to backlog with ticket references
[ ] Re-run automated tools after fixes to verify resolution
[ ] Conduct manual screen reader re-test on fixed components
[ ] Update component library / design system with accessibility fixes
[ ] Add accessibility checks to CI pipeline if not already present
═══════════════════════════════════════════════════════════════
```
