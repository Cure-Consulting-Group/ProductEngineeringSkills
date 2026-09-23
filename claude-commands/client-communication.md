# Client Communication

**Outcome:** one ready-to-send client artifact (email, escalation, summary, or demo script) in the
right format for the audience, with concrete dates, owners, and a recommendation wherever a decision
is needed. Done when the user can paste it and send it. Match length to the need; no filler sections
or restated summaries.

Cure's stance: bad news delivered early beats bad news delivered well. A RED item that first appears
in an executive summary is a process failure — it should already have been escalated.

## Step 1: Classify the Need

| Need | Output | Default cadence |
|------|--------|-----------------|
| Weekly Status | Email (template below) | Same weekday every week |
| Risk Escalation | Escalation memo (template below) | The day the trigger is met |
| Executive Summary | One-page summary (template below) | Monthly / quarterly |
| Sprint Demo | Demo script + environment checklist | End of sprint |
| Milestone Report / RAG / QBR | Report from the reference file | Phase gate / quarterly |
| Meeting agenda, decision log, action items | Format from the reference file | Per meeting |

Read `reference/details.md` only when the need is Sprint Demo, Milestone/RAG/QBR, or meeting
facilitation — it holds those templates.

## Step 2: Gather Context

Ask the user (or read from the notes/board they point to) — don't invent progress or numbers:

1. **Audience** — technical lead, product owner, C-suite, board? Sets depth and vocabulary.
2. **Progress since last update** — completed items, merged work, decisions made.
3. **Blockers and risks** — what is blocked, by whom, what is needed, impact of delay.
4. **Next milestone** — name, date, on track or at risk.
5. **Timeline and budget** — variance and why, if any.
6. **Relationship** — new client (more formal) or established (more direct).

If a figure is unknown, leave a bracketed placeholder rather than guessing.

## Step 3: Weekly Status Email (the core artifact)

```
Subject: [Project] — Week of [Date] Status

Hi [Name],

PROGRESS THIS WEEK
  - [Completed item — one sentence, outcome-focused]

IN PROGRESS
  - [Item — expected completion date]

NEEDS YOUR ATTENTION
  - [Blocker — what's blocked, what we need from you, by when]
  - [Decision — context, options, our recommendation, deadline]
  (If none: "Nothing needed from you this week.")

NEXT WEEK
  - [Planned item]

TIMELINE & BUDGET
  Timeline: [On track / X days behind — why]
  Budget:   [On track / X% burned — flag if trending over]
  Next milestone: [Name] — [Date] — [On track / At risk]

Best,
[Name]
```

Rules: one screen; concrete dates, never "soon"; client asks go in their own section, never inside
progress; if anything is RED it is escalated separately (Step 4), not just reported here.

## Step 4: Risk Escalation

Escalate when any of these is true (adjust thresholds to the SOW):
- a risk's escalation trigger is met, or a blocker exceeds the team's authority
- timeline impact > 1 week, or budget impact > 10%
- a client or third-party dependency is unresponsive > 3 business days
- a scope change touches committed deliverables

Routing: technical → Eng Lead → CTO; scope → PM → Client PO → Sponsor; budget/contract → PM →
Account Manager → Sponsor; staffing → PM → Delivery Lead → Account Manager. Escalate by call or
formal written memo, never buried in chat, and always with a recommendation and a decision deadline.

```
RISK ESCALATION: [Title]
Project: [Name] | Date: [Date] | From: [Role] | To: [Role]
Priority: [High / Critical] | Decision needed by: [Date]

SITUATION  [2–3 factual sentences. No backstory, no editorializing.]

IMPACT     Timeline: [days/weeks] | Budget: [\$] | Scope: [affected deliverables] | Quality: [risk]

OPTIONS
  A: [Description] — timeline [X], cost [\$X], trade-off [what we give up]
  B: [Description] — timeline [X], cost [\$X], trade-off [...]
  C: Do nothing — delay [X], cost at risk [\$X], consequence [...]

RECOMMENDATION  Option [X], because [one sentence].

NEXT STEPS (if accepted)
  1. [Action] — [Owner] — [Date]
```

Lead with impact; separate fact ("integration needs 2 more weeks") from opinion; own the message —
no blaming team members, vendors, or the client.

## Step 5: Executive Summary

```
EXECUTIVE SUMMARY — [Project] — [Period]

HEALTH   [NN]% complete | Timeline: [G/A/R] | Budget: [G/A/R] | Quality: [G/A/R]

KEY METRICS   [3–5 agreed metrics: shipped features, open P0/P1, uptime, product KPIs]

COMPLETED     - [Accomplishment — business impact, not technical detail]

DECISIONS NEEDED
  1. [Decision — one-line context. Options A/B. Recommend A. Deadline.]
  (If none: "No decisions needed this period.")

RISKS         - [Top risk — mitigation / already escalated]

UPCOMING      [Next milestone — date — key deliverables]

BUDGET        Allocated \$[X] | Spent \$[Y] ([Z]%) | Forecast \$[W]
```

One page maximum; business language; every decision carries a recommendation; no surprises.

## Step 6: Sprint Demo (summary)

30-minute cap: intro and goals recap (2 min) → live walkthrough of completed items, each with one
non-technical sentence on why it matters (20) → metrics (3) → what's next (3) → Q&A (2). Rehearse
once end-to-end on staging with realistic data; capture fallback screenshots; if the live demo
breaks, switch to screenshots — never debug live. Follow up within 24 hours with the recording, the
summary email, and action items (one owner, one date each). Full script and checklist are in the
reference file.

## Artifact Generation

Applies only when the user asks for files or a reusable template set. Otherwise return the drafted
text in the reply. When files are wanted, write only the artifacts for the classified need, under
`docs/comms/` (e.g. `docs/comms/status-YYYY-MM-DD.md`, `docs/comms/escalation-<slug>.md`).

## Related Skills

- `project-manager` — sprint planning, RACI, internal risk register, retros
- `client-handoff` — end-of-engagement transition package
- `sdlc` — ADR format for the decision log
- `product-manager` — roadmap and feature-brief communication
