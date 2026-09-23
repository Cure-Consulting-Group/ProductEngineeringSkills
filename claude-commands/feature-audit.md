# Feature Audit

> **READ-ONLY SKILL.** Produce analysis only: do not edit files, do not run
> mutating commands, and do not create or delete resources. Under Claude Code
> the `disallowed-tools` frontmatter above blocks Write and Edit (`allowed-tools`
> only pre-approves tools; it restricts nothing).
> Bash stays available for read-only inspection (grep, git log, scanners), so even
> under Claude Code "no mutating commands" is advisory, not enforced.
> **Other runtimes do not enforce it** — Codex and Antigravity ignore those
> fields, and activation there can widen rather than narrow file access — so on
> any runtime other than Claude Code this paragraph is the only guardrail.

**Outcome:** a scored gap report for one shipped feature, every finding with platform, file/layer,
severity (Critical / High / Medium / Low), confidence, and a concrete fix; missing tests come with a
minimal stub. Report everything you find — ranking happens in the report, not by omission. Done
when every entry and exit point of the feature has been traced on each platform it ships on.

## Pre-Processing (Auto-Context)

Context — run these read-only commands first; skip any that fail or aren't permitted (they only tailor the output):

- Platforms present: `ls package.json build.gradle.kts Podfile Package.swift firebase.json 2>/dev/null | head -5 | grep . || echo "(none detected)"`
- Recent commits: `git log --oneline -8 2>/dev/null || echo "(not a git repo)"`

## Step 1: Classify

Identify the feature and the platforms it ships on (from the context above and the user). Scale depth
to size: a single-screen change gets the phases that apply to it, not a 120-point scorecard. If the
feature name or scope is ambiguous, ask once; in an unattended run, state the assumed scope and proceed.

Detect the iOS architecture before judging it: TCA features get the TCA checks below; MVVM/Observation
features get equivalent checks (async error paths, cancellation, state owned by the view model). Don't
flag MVVM as a defect — technology-radar puts MVVM in Adopt and TCA in Trial.

## Step 2: Gather Context and Scan

Find the feature's files (search by feature name across `*.kt`, `*.swift`, `*.ts`/`*.tsx`,
`functions/**`, `*.rules`) and run quick searches before the phases:

- Empty or swallowed `catch` blocks; async calls with no error path.
- Test files vs source files per platform (flag layers with no tests at all).
- Secret-looking literals (`sk_live_`, `pk_live_`, `ghp_`, `AIza`, `AKIA`), unparameterized queries, unvalidated public inputs.
- Firestore collections the feature touches vs rules that cover them.

## Step 3: Boundary Mapping

Every entry point (UI trigger, deep link / Universal Link / App Link, push, background job), every exit
(success, error, navigation, callback), the data flow (input → transform → persistence), and external
dependencies (APIs, Firestore paths, Stripe, SDKs). A dependency with no failure handling is a finding.
Trace the chain per platform: Android `UiEvent → ViewModel → Repository → DataSource`; iOS TCA
`Action → Reducer → Effect` (or View → ViewModel → Client); Web route → Server Component/Action → data layer.

## Step 4: Logic and Wiring Gaps

- **All:** unvalidated state (null, empty, signed-out), business rules that differ between layers or platforms, magic values that belong in constants or Remote Config, missing debounce on user-triggered writes, races.
- **Android:** error handling, loading state, and cancellation (`viewModelScope`) on every async call; Hilt graph complete; StateFlow collected lifecycle-aware; nav graph wired.
- **iOS (TCA):** effects use `.run` with `do/catch` mapping failures to actions (`TaskResult` is deprecated in TCA 1.x); `.cancellable(id:)` on long effects; no state mutation outside reducers; no meaningful action returning `.none` silently; `testValue` for every live dependency.
- **Web:** Server Actions validate input and check auth; error and loading boundaries exist for the route; no secrets in client bundles.
- **Firebase/Stripe:** rules cover every collection touched; functions return typed errors; transactions where writes race; webhooks idempotent; Stripe and Firestore customer records agree.

## Step 5: Tests, Security, Accessibility, Analytics, Docs

Rate each ✅ covered / ⚠️ partial / ❌ missing:

- **Tests:** Android ViewModel + repository tests with fakes, Compose UI test for the main path; iOS `TestStore` exhaustive tests for every action and effect (or view-model tests); Web component + E2E for the critical path; Firestore rules tested in the Emulator Suite. Coverage thresholds come from testing-strategy — don't restate them.
- **Security:** the Step 2 scan results plus auth checks on every new endpoint/callable. Escalate to security-review if anything is Critical.
- **Accessibility:** labels on new interactive elements, touch targets, dynamic type/font scaling, contrast on new colors. Escalate to accessibility-audit for a full pass.
- **Analytics:** the feature's key events fire with the names in the tracking plan (analytics-implementation).
- **Docs:** README/changelog/API docs updated where the feature changes behavior.

## Step 6: Report

```
FEATURE AUDIT — [feature] — [date]
Platforms: [Android | iOS | Web | Backend]

SCORECARD (0–10 per applicable cell; omit platforms the feature doesn't ship on)
Category        Android  iOS  Web  Backend
Boundary
Logic/Wiring
Tests
Sec/A11y/Analytics/Docs
Status: 🟢 ≥80%  🟡 60–79%  🔴 <60%

FINDINGS (all of them, highest severity first)
# | Severity | Confidence | Platform | File/Layer | Gap | Fix

MISSING TESTS
# | Platform | Test | Type | Minimal stub

CROSS-PLATFORM INCONSISTENCIES
# | Behavior/contract | Risk | Fix

NEXT ACTIONS
Critical → block merge · High → next sprint · Medium/Low → backlog
```

Match length to the feature; no restated summaries.

## Recurring Mode

This is a recurring goal, not a one-shot (mechanism trade-offs: the `engagement-automation` skill).

- **Cadence:** monthly
- **Session loop:** none — session loops expire after 7 days, so a monthly cadence never fires in-session; it belongs in the cloud routine below.
- **Unattended:** cloud routine — audit each feature merged in the last month (from merge history) with this skill, using the assumed-scope rule in Step 1 instead of asking. Recipes: docs/AUTOMATION.md in the plugin repo.
- **Budget:** ~120k tokens/run; cap at one run per monthly period.
- **Guardrails:** the audit itself is read-only; the routine (not the skill) delivers the combined report as an issue; report on failure rather than retrying.
