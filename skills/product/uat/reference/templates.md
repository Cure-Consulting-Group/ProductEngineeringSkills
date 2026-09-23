# uat: sign-off, release notes, and report templates

> Read when writing the sign-off form, release notes, or final UAT report (Steps 5–6 of the `uat` skill).

## Stakeholder sign-off

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

## Rollback plan

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

## Release notes draft

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

## UAT report

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
  [Paste the completed stakeholder sign-off table here]

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
