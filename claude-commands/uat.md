# User Acceptance Testing (UAT)

End-to-end UAT framework covering plan generation, execution, stakeholder sign-off, and go/no-go release gates. UAT is the last quality gate before production — treat it that way. No feature ships without explicit stakeholder sign-off against acceptance criteria.

## Pre-Processing (Auto-Context)

Project context, gathered before the skill runs. Values are injected inline below; in an environment that does not execute them (e.g. Gemini), run the shown commands instead.

- Portfolio: !`sed -n '1,40p' PORTFOLIO.md 2>/dev/null || echo "(no PORTFOLIO.md)"`
- Stack manifest: !`head -40 package.json 2>/dev/null || head -40 build.gradle.kts 2>/dev/null || head -20 Podfile 2>/dev/null || echo "(none detected)"`
- Recent commits: !`git log --oneline -5 2>/dev/null || echo "(not a git repo)"`
- Layout: !`ls src/ app/ lib/ functions/ 2>/dev/null | head -25`

Use this context to tailor all output to the actual project.

## Step 1: Classify the UAT Need

Determine the UAT type before building the plan. The type dictates scope, depth, stakeholder involvement, and timeline.

| UAT Type | Trigger | Scope | Typical Duration |
|---|---|---|---|
| **New Feature UAT** | Feature development complete, merged to staging | All acceptance criteria from PRD/stories, full happy path + edge cases | 2-5 business days |
| **Regression UAT** | Major refactor, dependency upgrade, or platform migration | Critical user journeys re-verified, no behavioral regressions | 1-3 business days |
| **Release Candidate UAT** | Release branch cut, all features integrated | Full release scope — every feature, integration point, and cross-platform behavior | 3-5 business days |
| **Hotfix Validation** | Production bug fixed, patch deployed to staging | Narrow scope — verify fix, confirm no side effects on adjacent flows | 2-4 hours |

If the UAT type is unclear, ask before proceeding. A hotfix validation and a release candidate UAT require fundamentally different plans.

## Automated Context Gathering

Before creating UAT plan:
1. Glob for existing test specs, PRD files, acceptance criteria documents
2. Read any found specs to extract testable requirements
3. Grep for feature flags that control the features under test

## Artifact Generation (Required)

Generate using Write:
1. **UAT plan**: `docs/uat/uat-plan.md` — using test-plan output style
2. **Test cases**: `docs/uat/test-cases.md` — detailed test cases with steps and expected results
3. **Sign-off form**: `docs/uat/sign-off.md` — stakeholder approval template
4. **Bug triage template**: `docs/uat/bug-triage.md` — severity classification guide

## Step 2: Gather Context

Collect all inputs before writing the UAT plan. Missing context produces incomplete plans.

| Input | Required | Source | Notes |
|---|---|---|---|
| Feature name/release version | Yes | PM/Tech Lead | Short identifier for tracking |
| Acceptance criteria | Yes | PRD, user stories, Jira/Linear tickets | Use `/sdlc` skill output if available |
| Stakeholder list | Yes | PM/Product Owner | Who tests, who signs off, who has veto power |
| Target environment | Yes | Engineering | Staging URL, build number, feature flags |
| Platform(s) | Yes | Engineering | Android, iOS, Web, or combination |
| Compliance requirements | Optional | Legal/Security | HIPAA, SOC 2, PCI-DSS, GDPR constraints on test data |
| Known risks or limitations | Optional | Engineering | Technical debt, known issues, incomplete integrations |
| Previous UAT results | Optional | QA/PM | Baseline for regression comparison |
| Release deadline | Yes | PM | Hard date vs. flexible — drives go/no-go pressure |

If acceptance criteria do not exist, **stop and create them first** using the `/sdlc` skill. UAT without acceptance criteria is opinion-based testing — it proves nothing.

## Step 3: UAT Plan Generation

### 3.1 Acceptance Criteria Extraction

Pull acceptance criteria from every source and normalize them into testable statements.

```
Format: Given [precondition], When [action], Then [expected result]

Source priority:
  1. PRD acceptance criteria (authoritative)
  2. User story acceptance criteria (detailed)
  3. Design specs / prototypes (visual and interaction behavior)
  4. API contracts (response shapes, error codes)
  5. Edge cases identified during code review or /feature-audit
```

Every acceptance criterion becomes one or more test scenarios. If a criterion cannot be tested manually, flag it and specify the automated verification method.

### 3.2 Test Scenario Matrix

Build the full scenario matrix. Every scenario has exactly one expected outcome.

| ID | Category | Scenario | Precondition | Steps | Expected Result | Platform | Priority |
|---|---|---|---|---|---|---|---|
| UAT-001 | Happy Path | [Primary success flow] | [Setup state] | [1. 2. 3.] | [Expected outcome] | All | P0 |
| UAT-002 | Happy Path | [Secondary success flow] | [Setup state] | [1. 2. 3.] | [Expected outcome] | All | P0 |
| UAT-003 | Edge Case | [Boundary condition] | [Setup state] | [1. 2. 3.] | [Expected outcome] | All | P1 |
| UAT-004 | Error State | [Invalid input / failure] | [Setup state] | [1. 2. 3.] | [Error handling] | All | P1 |
| UAT-005 | Cross-Platform | [Platform-specific behavior] | [Setup state] | [1. 2. 3.] | [Platform expectation] | Specific | P1 |
| UAT-006 | Accessibility | [Screen reader / keyboard nav] | [AT enabled] | [1. 2. 3.] | [Accessible outcome] | All | P1 |
| UAT-007 | Performance | [Load time / responsiveness] | [Standard conditions] | [1. 2. 3.] | [Within budget] | All | P2 |
| UAT-008 | Offline/Degraded | [No connectivity / poor signal] | [Airplane mode / throttled] | [1. 2. 3.] | [Graceful handling] | Mobile | P1 |

**Priority definitions:**
- **P0** — Core functionality. If this fails, the feature does not work. Blocks release.
- **P1** — Important behavior. If this fails, the feature works but with significant gaps. Must-fix before release.
- **P2** — Nice-to-have verification. If this fails, can ship with known issue documented.

### 3.3 Environment Checklist

Verify the testing environment before UAT begins. A broken environment wastes stakeholder time and erodes trust.

```
PRE-UAT ENVIRONMENT CHECKLIST
[ ] Staging environment deployed with correct build/version
[ ] Build version documented: _______________
[ ] Feature flags enabled for UAT scope:
    [ ] Flag: _____________ = ON/OFF
    [ ] Flag: _____________ = ON/OFF
[ ] Test data seeded (accounts, content, transactions)
[ ] Test accounts created with required roles/permissions
    (see /test-accounts skill for account provisioning)
[ ] Third-party integrations in test/sandbox mode:
    [ ] Stripe: test mode with test API keys
    [ ] Payment processor: sandbox environment
    [ ] Email/SMS: intercepted or using test recipients
    [ ] Analytics: dev/staging property (not production)
[ ] Backend/API pointing to staging (not production)
[ ] Database seeded with representative data volume
[ ] Push notifications configured for staging
[ ] Deep links / Universal Links configured for staging domain
[ ] SSL certificates valid on staging
[ ] VPN/network access configured for all testers
```

### 3.4 Stakeholder Roles Table

Define who does what. Ambiguity in roles means gaps in coverage.

| Role | Person | Responsibilities | Sign-Off Authority |
|---|---|---|---|
| **UAT Lead** | [Name] | Owns the UAT plan, coordinates sessions, triages bugs, produces report | Final go/no-go recommendation |
| **Product Owner** | [Name] | Validates acceptance criteria are met, tests business logic scenarios | Yes — business sign-off |
| **Design Lead** | [Name] | Validates visual fidelity, interaction patterns, brand consistency | Yes — design sign-off |
| **Engineering Lead** | [Name] | Available for bug investigation, environment fixes, explains technical constraints | Yes — technical sign-off |
| **QA Tester** | [Name] | Executes test scenarios systematically, documents findings with evidence | No — reports to UAT Lead |
| **Domain Expert** | [Name] | Tests domain-specific workflows (finance, healthcare, legal) | Yes — domain sign-off |
| **Accessibility Tester** | [Name] | Screen reader pass, keyboard navigation, WCAG AA verification | Advisory — escalates to UAT Lead |

Minimum viable sign-off requires: **Product Owner + Engineering Lead**. All other sign-offs are recommended but scope-dependent.

## Step 4: UAT Execution Framework

See [reference/details.md](reference/details.md) (section “Step 4: UAT Execution Framework”) for full detail.

## Step 5: Sign-Off and Go/No-Go Gate

### 5.1 Go/No-Go Decision Matrix

The go/no-go decision is data-driven, not opinion-driven. Score each criterion and calculate the weighted result.

```
GO / NO-GO DECISION MATRIX
Feature/Release: _______________
Date: _______________
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
┌──────────────────────────────────┬────────┬────────┬───────┬───────┐
│ Criterion                        │ Weight │ Status │ Score │ Notes │
├──────────────────────────────────┼────────┼────────┼───────┼───────┤
│ All P0 scenarios pass            │  30%   │ GO/NOGO│ X/30  │       │
│ All P1 scenarios pass            │  25%   │ GO/NOGO│ X/25  │       │
│ No open P0 bugs                  │  20%   │ GO/NOGO│ X/20  │       │
│ No open P1 bugs (or risk-accepted)│ 10%   │ GO/NOGO│ X/10  │       │
│ Accessibility pass (WCAG AA)     │  5%    │ GO/NOGO│ X/5   │       │
│ Performance within budget        │  5%    │ GO/NOGO│ X/5   │       │
│ Cross-platform parity verified   │  5%    │ GO/NOGO│ X/5   │       │
├──────────────────────────────────┼────────┼────────┼───────┼───────┤
│ TOTAL                            │ 100%   │        │ X/100 │       │
└──────────────────────────────────┴────────┴────────┴───────┴───────┘

Decision thresholds:
  GO           >= 90/100   All P0 criteria must be GO.
  CONDITIONAL  70-89/100   Ship with documented conditions and timeline for resolution.
  NO-GO        < 70/100    Do not release. Fix and re-test.

Hard blockers (automatic NO-GO regardless of score):
  - Any open P0 bug
  - Data loss or corruption scenario
  - Security vulnerability (auth bypass, data exposure)
  - Crash on critical user journey
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.2 Sign-Off Template

```
STAKEHOLDER SIGN-OFF
Feature/Release: _______________
Build/Version: _______________
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
┌──────────────────┬──────────────┬──────────┬────────────┬─────────┐
│ Stakeholder      │ Role         │ Decision │ Conditions │ Date    │
├──────────────────┼──────────────┼──────────┼────────────┼─────────┤
│ [Name]           │ Product Owner│ GO/NOGO  │ [if any]   │ [date]  │
│ [Name]           │ Eng Lead     │ GO/NOGO  │ [if any]   │ [date]  │
│ [Name]           │ Design Lead  │ GO/NOGO  │ [if any]   │ [date]  │
│ [Name]           │ Domain Expert│ GO/NOGO  │ [if any]   │ [date]  │
│ [Name]           │ UAT Lead     │ GO/NOGO  │ [if any]   │ [date]  │
└──────────────────┴──────────────┴──────────┴────────────┴─────────┘

Conditional sign-off means: "GO, provided the following are resolved by [date]:"
  1. [Condition]
  2. [Condition]

If ANY stakeholder signs NO-GO, the release is blocked until their concern is resolved.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.3 Rollback Plan

Every release must have a rollback plan documented before the go/no-go decision. No rollback plan = automatic NO-GO.

```
ROLLBACK PLAN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Trigger:    [Conditions that trigger rollback — e.g., crash rate > 2%, P0 bug in production]
Owner:      [Who initiates rollback]
Steps:
  1. [Disable feature flag / revert deployment]
  2. [Verify rollback successful]
  3. [Notify stakeholders]
  4. [Monitor for 30 minutes post-rollback]
Data:       [Any data migration rollback needed? Firestore document versioning?]
Comms:      [Who communicates to users if needed — support team, status page]
Post-mortem:[Schedule within 48 hours of rollback]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.4 Release Notes Draft

Generate release notes from UAT findings. UAT testers know the feature better than anyone at this point.

```
RELEASE NOTES (from UAT findings)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Version: _______________
Date: _______________

NEW
  - [Feature/capability added — user-facing language]

IMPROVED
  - [Enhancement to existing feature — what's better for the user]

FIXED
  - [Bug fixed during UAT — what was broken and is now resolved]

KNOWN ISSUES
  - [P2 bugs shipping with this release — workaround if available]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Step 6: UAT Report

Produce the full UAT report after all sessions are complete and sign-off is collected.

```
═══════════════════════════════════════════════════════════════
UAT REPORT
Feature/Release: [NAME]
Version/Build: [VERSION]
Date: [TODAY]
UAT Lead: [NAME]
═══════════════════════════════════════════════════════════════

EXECUTIVE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Decision:      GO / CONDITIONAL / NO-GO
Total Scenarios: [N]
Passed:         [N] ([X]%)
Failed:         [N] ([X]%)
Blocked:        [N] ([X]%)
Not Executed:   [N] ([X]%)
Open Blockers:  [N] P0 / [N] P1 / [N] P2
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PASS RATE BY CATEGORY
┌──────────────────────┬──────────┬────────┬─────────┬────────┐
│ Category             │ Total    │ Passed │ Failed  │ Rate   │
├──────────────────────┼──────────┼────────┼─────────┼────────┤
│ Happy Path           │ [N]      │ [N]    │ [N]     │ [X]%   │
│ Edge Cases           │ [N]      │ [N]    │ [N]     │ [X]%   │
│ Error States         │ [N]      │ [N]    │ [N]     │ [X]%   │
│ Cross-Platform       │ [N]      │ [N]    │ [N]     │ [X]%   │
│ Accessibility        │ [N]      │ [N]    │ [N]     │ [X]%   │
│ Performance          │ [N]      │ [N]    │ [N]     │ [X]%   │
│ Offline/Connectivity │ [N]      │ [N]    │ [N]     │ [X]%   │
├──────────────────────┼──────────┼────────┼─────────┼────────┤
│ TOTAL                │ [N]      │ [N]    │ [N]     │ [X]%   │
└──────────────────────┴──────────┴────────┴─────────┴────────┘

DETAILED FINDINGS
┌────────┬──────────────────────┬─────────────────┬─────────────────┬──────────┬─────────┐
│ ID     │ Scenario             │ Expected        │ Actual          │ Severity │ Status  │
├────────┼──────────────────────┼─────────────────┼─────────────────┼──────────┼─────────┤
│ UAT-001│ [Scenario desc]      │ [Expected]      │ [Actual]        │ P0/P1/P2 │ PASS/FAIL│
│ UAT-002│ [Scenario desc]      │ [Expected]      │ [Actual]        │ P0/P1/P2 │ PASS/FAIL│
│ ...    │                      │                 │                 │          │         │
└────────┴──────────────────────┴─────────────────┴─────────────────┴──────────┴─────────┘

For every FAILED scenario:
  - Screenshot or screen recording: REQUIRED (attach or link)
  - Bug ticket: REQUIRED (link to issue tracker)
  - Workaround: document if available

BUG SUMMARY
┌────────────┬───────┬───────┬─────────┬─────────┐
│ Severity   │ Found │ Fixed │ Open    │ Deferred│
├────────────┼───────┼───────┼─────────┼─────────┤
│ P0 Blocker │ [N]   │ [N]   │ [N]     │ 0       │
│ P1 Must-Fix│ [N]   │ [N]   │ [N]     │ [N]     │
│ P2 Known   │ [N]   │ [N]   │ [N]     │ [N]     │
│ P3 Enhance │ [N]   │ [N]   │ [N]     │ [N]     │
├────────────┼───────┼───────┼─────────┼─────────┤
│ TOTAL      │ [N]   │ [N]   │ [N]     │ [N]     │
└────────────┴───────┴───────┴─────────┴─────────┘

PLATFORM-SPECIFIC RESULTS
  Android: [summary — devices tested, OS versions, Play Store internal track verified]
  iOS:     [summary — devices tested, iOS versions, TestFlight distribution verified]
  Web:     [summary — browsers tested, responsive breakpoints verified]

CARRY-FORWARD ITEMS
Items not resolved in this UAT cycle. Must be tracked in the next sprint.
┌────────┬────────────────────────────┬──────────┬───────────────┬────────────┐
│ ID     │ Description                │ Severity │ Assigned To   │ Target     │
├────────┼────────────────────────────┼──────────┼───────────────┼────────────┤
│ CF-001 │ [Item description]         │ P1/P2    │ [Name]        │ Sprint [N] │
│ CF-002 │ [Item description]         │ P1/P2    │ [Name]        │ Sprint [N] │
└────────┴────────────────────────────┴──────────┴───────────────┴────────────┘

SIGN-OFF STATUS
  [See Step 5.2 Sign-Off Template — paste completed version here]

RECOMMENDATIONS
  - [Process improvements for next UAT cycle]
  - [Test automation candidates identified during UAT]
  - [Environment or tooling improvements needed]

NEXT ACTIONS
[ ] All P0 bugs verified fixed and re-tested
[ ] All P1 bugs fixed or risk-accepted with written justification
[ ] Sign-off collected from all required stakeholders
[ ] Carry-forward items added to backlog with ticket references
[ ] Release notes finalized and reviewed by PM
[ ] Rollback plan reviewed and approved by Engineering Lead
[ ] Monitoring dashboards configured for post-release (crash rate, error rate, key metrics)
[ ] Post-release check scheduled (1 hour, 24 hours, 72 hours after deploy)
═══════════════════════════════════════════════════════════════
```

## Related Skills

- `/sdlc` — Generate acceptance criteria, PRDs, and user stories that feed into UAT
- `/testing-strategy` — Automated testing pyramid and CI integration (complements manual UAT)
- `/feature-audit` — Post-completion code audit (run before UAT to catch technical gaps)
- `/accessibility-audit` — Deep WCAG 2.2 compliance audit (invoke for thorough a11y verification during UAT)
- `/security-review` — Security review for auth, data, and API concerns found during UAT
- `/incident-response` — If UAT reveals production issues or rollback is needed post-deploy
