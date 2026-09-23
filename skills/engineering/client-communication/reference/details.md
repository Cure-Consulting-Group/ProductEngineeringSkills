# client-communication: secondary templates

> Read when the classified need is Sprint Demo, Milestone Report, RAG status, QBR, or meeting
> facilitation. The weekly status, escalation, and executive summary templates live in SKILL.md.

## Sprint Demo Script

```
SPRINT DEMO — Sprint [X] — [Date] — 30 min cap
Presenter: [Name] | Audience: [Names, roles] | Agenda sent 24h before

1. INTRO (2 min)  Theme in 1–2 sentences. Goals: [Goal] — Complete / Partial / Moved
2. WHAT WE BUILT (20 min)
   [Feature] — what it does (1 non-technical sentence)
     Flow: [Navigate to X] → [Do Y] → [Show Z]
     Why it matters: [user / business impact]
   Technical improvements: ≤2 min unless the audience is technical
3. METRICS (3 min)  Completed vs planned; bugs opened/closed/remaining; product KPI movement
4. WHAT'S NEXT (3 min)  Top 3 next-sprint priorities; next milestone — date — status
5. Q&A (2 min)  Capture questions; research items get an owner and a date

FOLLOW-UP within 24h: recording link, summary email, action items
```

Environment checklist: staging checked 1 hour before; realistic test data (not "test123"); test
accounts ready; flow rehearsed end-to-end; fallback screenshots; screen share legible;
notifications silenced; recording on; backup presenter named.

Async recording (for absent stakeholders): 10–15 minutes, intro slide, narrated walkthrough per
feature, closing slide with next steps and decisions needed; link it in the weekly email.

## Milestone Report

```
MILESTONE REPORT — [Project] — [Milestone] — [Date]
Status: [Complete / Partially Complete / At Risk]

GOAL  [1–2 sentences]
ACCEPTANCE CRITERIA  [Criterion]: Met / Not met — why   (Overall X of Y)

DELIVERABLES
  | # | Deliverable | Status (Complete/Partial/Deferred) | Notes |

BUDGET    Allocated \$[X] | Spent \$[Y] ([Z]%) | Forecast \$[W] | Variance [why]
TIMELINE  Planned [Date] | Actual [Date] | Variance [why]
RISKS CARRIED FORWARD  - [Risk — impact — mitigation]
NEXT MILESTONE  [Name] — [Date] — deliverables — dependencies / client decisions needed
```

## RAG Status

```
RAG STATUS — [Project] — [Date]
| Workstream | Status | Summary (what, why, when it recovers) |
```

GREEN: on track, nothing threatening timeline/budget. AMBER: issue with mitigation in progress;
will hit timeline if unresolved by [date]. RED: needs stakeholder action or decision; will hit
timeline/budget without intervention. Anything RED is escalated (SKILL.md Step 4), not just reported.

## Quarterly Business Review (60 min)

1. Quarter recap (5) — objectives set vs met, key deliverables
2. Metrics & health (10) — agreed product metrics, delivery quality, uptime, budget vs plan
3. Demo (10) — the 2–3 most impactful features
4. Challenges & learnings (5) — top issues and how they were resolved
5. Next quarter (10) — 3–5 objectives, milestones, what we need from the client, known risks
6. Discussion (20) — client priorities and feedback

## Meeting Facilitation

Agenda (sent ≥4 hours before; no agenda, no meeting):
```
[Meeting] — [Date] [Time + TZ] — [Duration] — [Link]
Pre-read: [links]
[Time] [Topic] — [Presenter] — Inform / Discuss / Decide
[Time] Action items and next steps — [Facilitator]
```

Decision log (one source of truth; link ADRs from the `sdlc` skill):
```
| # | Date | Decision | Decided by | Context / link |
```

Action items: `[ACTION] [Description] — [one owner] — [specific date]`, sent within 24 hours, tracked
in one system; overdue items are raised at the next meeting.

Default to async (email with a decision deadline, recorded walkthrough) for status and simple
decisions; meet live for demos, escalations, multi-trade-off decisions, and conflict.
