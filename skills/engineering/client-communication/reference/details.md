# client-communication: detailed reference

> Reference material for the `client-communication` skill, split out for progressive disclosure. Loaded on demand from SKILL.md.

## Contents
- Step 4: Status Update Templates

## Step 4: Status Update Templates

### Weekly Status Report

```
Subject: [Project Name] — Week of [Date] Status Update

Hi [Client Name],

Here's your weekly update for [Project Name].

PROGRESS THIS WEEK
  - [Completed item 1 — one sentence, outcome-focused]
  - [Completed item 2]
  - [Completed item 3]

IN PROGRESS
  - [Item 1 — expected completion date]
  - [Item 2 — expected completion date]

BLOCKERS / NEEDS YOUR ATTENTION
  - [Blocker 1 — what's blocked, what we need, by when]
  - [Decision needed — context, options, recommendation, deadline]
  (If none: "No blockers this week.")

UPCOMING NEXT WEEK
  - [Planned item 1]
  - [Planned item 2]

TIMELINE & BUDGET
  Timeline: [On track / X days ahead / X days behind — explanation if behind]
  Budget:   [On track / X% burned of total — flag if trending over]
  Next milestone: [Name] — [Date] — [On track / At risk]

Best,
[Your name]
```

Rules for weekly status:
- Send on the same day every week (Monday recommended)
- Keep under 1 page / 1 screen scroll
- Lead with completed work (positive momentum)
- Never bury blockers at the bottom -- they go in their own section
- Use concrete dates, not "soon" or "next week hopefully"
- If there is bad news, put it in BLOCKERS, not buried in progress

### Milestone Report

```
MILESTONE REPORT
Project: [Name]
Milestone: [Milestone name / number]
Date: [Date]
Status: [Complete / Partially Complete / At Risk]

MILESTONE SUMMARY
  This milestone aimed to deliver: [1-2 sentence description]

  Acceptance criteria:
    - [Criterion 1]: [Met / Not met — explanation]
    - [Criterion 2]: [Met / Not met — explanation]
    - [Criterion 3]: [Met / Not met — explanation]

  Overall: [X of Y criteria met]

DELIVERABLES
  ┌────┬──────────────────────────────┬────────────┬───────────────────┐
  │ #  │ Deliverable                  │ Status     │ Notes             │
  ├────┼──────────────────────────────┼────────────┼───────────────────┤
  │ 1  │ [Feature/deliverable name]   │ Complete   │                   │
  │ 2  │ [Feature/deliverable name]   │ Complete   │ [Minor caveat]    │
  │ 3  │ [Feature/deliverable name]   │ Partial    │ [What remains]    │
  │ 4  │ [Feature/deliverable name]   │ Deferred   │ [Moved to M3]     │
  └────┴──────────────────────────────┴────────────┴───────────────────┘

BUDGET
  Budget allocated:    $[X]
  Budget spent:        $[Y] ([Z]%)
  Forecast at complete: $[W]
  Variance:            [Under / Over by $X — explanation]

TIMELINE
  Planned completion:  [Date]
  Actual completion:   [Date]
  Variance:            [On time / X days early / X days late — explanation]

RISKS CARRIED FORWARD
  - [Risk 1 — impact and mitigation plan]
  - [Risk 2 — impact and mitigation plan]

NEXT MILESTONE
  Name: [Next milestone]
  Target date: [Date]
  Key deliverables: [List]
  Dependencies: [External dependencies or decisions needed]
```

### RAG Status Report

```
RAG STATUS — [Project Name] — [Date]

┌──────────────────────┬────────┬──────────────────────────────────────┐
│ Workstream           │ Status │ Summary                              │
├──────────────────────┼────────┼──────────────────────────────────────┤
│ Backend / API        │ GREEN  │ On track. Auth and CRUD complete.     │
│ Frontend / UI        │ AMBER  │ 3 days behind. Design revisions       │
│                      │        │ added scope. Catching up this sprint. │
│ Mobile (Android)     │ GREEN  │ On track. Feature parity with web.    │
│ Mobile (iOS)         │ RED    │ Blocked on Apple review. Submitted    │
│                      │        │ appeal. ETA unknown.                  │
│ Infrastructure       │ GREEN  │ Staging and prod environments ready.  │
│ QA / Testing         │ AMBER  │ Test automation behind by 1 sprint.   │
│                      │        │ Manual testing covering gap.          │
└──────────────────────┴────────┴──────────────────────────────────────┘

RAG definitions:
  GREEN:  On track. No issues or risks that affect timeline/budget.
  AMBER:  Minor issue or risk. Mitigation in progress. May affect timeline
          if not resolved within [timeframe].
  RED:    Significant issue. Stakeholder action or decision needed.
          Will affect timeline/budget without intervention.

Rule: If anything is RED, it must be escalated (not just reported).
      Use the Risk Escalation framework (Step 5).
```
