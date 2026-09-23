# User Acceptance Testing (UAT)

**Outcome:** a UAT plan whose scenarios trace to acceptance criteria, executed against a verified
staging build, ending in a documented GO / CONDITIONAL / NO-GO decision with stakeholder sign-off
and a rollback plan. UAT is the last gate before production; nothing ships without explicit sign-off
against acceptance criteria. Match length to the need; no filler sections or restated summaries.

## Pre-Processing (Auto-Context)

Context — run these read-only commands first; skip any that fail or aren't permitted (they only tailor the output):

- Specs and criteria: `ls docs/prd docs/stories docs/uat 2>/dev/null | head -8 | grep . || echo "(no docs/prd, docs/stories, or docs/uat)"`
- Platforms present: `ls package.json build.gradle.kts Podfile Package.swift 2>/dev/null | head -4 | grep . || echo "(none detected)"`

Before planning, read the PRD/stories for the feature and search for the feature flags that gate it.

## Step 1: Classify

| Type | Trigger | Scope | Typical duration |
|---|---|---|---|
| New feature | Feature merged to staging | Every acceptance criterion, happy path + edge cases | 2–5 business days |
| Regression | Major refactor, dependency upgrade, migration | Critical journeys re-verified | 1–3 days |
| Release candidate | Release branch cut | Full release scope, integrations, cross-platform | 3–5 days |
| Hotfix validation | Patch on staging | The fix + adjacent flows | 2–4 hours |

If the type is unclear, ask — a hotfix and an RC need different plans.

## Step 2: Gather Context

Required: feature/release and build, acceptance criteria, stakeholders (who tests, who signs, who can
veto), environment (staging URL, build number, flags), platforms, release deadline. Optional:
compliance constraints on test data (HIPAA, PCI, GDPR), known issues, prior UAT results.

No acceptance criteria → stop and create them first with the sdlc skill. UAT without criteria is
opinion-based testing.

## Step 3: Plan

**Criteria → scenarios.** Normalize each criterion to Given / When / Then; each becomes one or more
scenarios with exactly one expected result. Source priority: PRD → stories → design specs → API
contracts → edge cases from feature-audit. Criteria that can't be tested manually get an automated
verification method named.

**Scenario matrix** columns: ID, category (happy path, edge, error, cross-platform, accessibility,
performance, offline), scenario, precondition, steps, expected result, platform, priority.

- **P0** — core function; failure means the feature doesn't work.
- **P1** — significant gap; must be fixed or explicitly risk-accepted in writing by the Product Owner.
- **P2** — can ship as a documented known issue.

**Environment gate** (verify before inviting stakeholders — a broken staging wastes their time):
correct build deployed and recorded; UAT flags set; test data and role-based accounts seeded (the
test-accounts skill); Stripe and other payments in test mode; email/SMS intercepted; analytics on a
non-production property; backend pointed at staging; push, deep links, and TLS working on the staging
domain; distribution via Play internal testing track and TestFlight, not side-loaded builds.

**Roles:** UAT Lead (owns plan, triage, report, recommendation), Product Owner (business sign-off),
Engineering Lead (technical sign-off, environment fixes), plus Design Lead, Domain Expert, QA, and
Accessibility tester as scope requires. Minimum sign-off: Product Owner + Engineering Lead.

## Step 4: Execute

Run time-boxed sessions by scenario group, log every result with evidence (screenshot or recording
for each failure, linked bug ticket), and triage bugs as they're found. Read `reference/details.md`
when running sessions — it has the session structure, in-session triage rules, the device/browser
matrix, and the accessibility and offline checks.

## Step 5: Go/No-Go Gate

**Hard gates — any one is an automatic NO-GO, whatever else passes:**
- Any P0 scenario failing or any open P0 bug
- Any P1 scenario failing or open P1 bug that is not fixed or risk-accepted in writing
- Data loss or corruption, a security vulnerability (auth bypass, data exposure), or a crash on a critical journey
- No rollback plan
- Any required stakeholder signs NO-GO (blocked until their concern is resolved)

**Soft criteria** (only once every hard gate passes): accessibility pass (WCAG AA), performance within
budget, cross-platform parity, P2 volume. All met → **GO**. Some unmet with owners and dates → **CONDITIONAL**
(ship with written conditions). Unmet in a way users will notice on a core journey → **NO-GO**.

Read `reference/templates.md` when writing the sign-off form, rollback plan, release notes, or final
report.

## Step 6: Report and Artifacts

Report: decision, pass/fail/blocked counts by category, every failed scenario with severity and
ticket, bug summary by severity, platform results (devices, OS versions, distribution verified),
carry-forward items with owners, sign-off table, and post-release checks (1h / 24h / 72h).

Write files only when the user wants them, and only those the phase needs: `docs/uat/uat-plan.md`
(plan: scope, scenario matrix, environment gate, roles, pass/fail criteria), `docs/uat/test-cases.md`,
`docs/uat/sign-off.md`, `docs/uat/report.md`.

Related: testing-strategy (automated coverage), accessibility-audit (deep WCAG pass),
security-review (security findings in UAT), incident-response (post-deploy rollback).
