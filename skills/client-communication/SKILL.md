---
name: client-communication
version: "1.0.0"
description: "Generate client-facing artifacts — sprint demo scripts, stakeholder updates, risk escalation reports, and executive status summaries"
when_to_use: "Use when generating sprint demo scripts, stakeholder updates, risk escalation reports, or executive summaries for clients."
argument-hint: "[sprint-or-milestone]"
---

# Client Communication

Generate professional client-facing communication artifacts. Covers sprint demo preparation, weekly status reports, risk escalation frameworks, executive summaries, and meeting facilitation templates. Every client interaction should be structured, concise, and action-oriented. Bad news delivered late is worse than bad news delivered early.

## Pre-Processing (Auto-Context)

Before starting, gather project context silently:
- Read `PORTFOLIO.md` if it exists in the project root or parent directories for product/team context
- Run: `cat package.json 2>/dev/null || cat build.gradle.kts 2>/dev/null || cat Podfile 2>/dev/null` to detect stack
- Run: `git log --oneline -5 2>/dev/null` for recent changes
- Run: `ls src/ app/ lib/ functions/ 2>/dev/null` to understand project structure
- Use this context to tailor all output to the actual project

## Step 1: Classify the Communication Need

| Need | Scope | When to Use |
|------|-------|-------------|
| Sprint Demo | Live or recorded demo of completed work for stakeholders | End of each sprint (biweekly or as agreed) |
| Weekly Status | Written progress update for project stakeholders | Every Monday (or agreed cadence) |
| Risk Escalation | Formal escalation of a risk or blocker that needs stakeholder decision | When a risk exceeds the team's authority to mitigate |
| Milestone Report | Comprehensive report on milestone completion and project health | At each major milestone or phase gate |
| Executive Summary | One-page summary for C-level or board-level audience | Monthly, quarterly, or on request |

## Step 2: Gather Context

1. **Stakeholder audience** -- who is receiving this communication? Technical lead, product owner, C-suite, external client, board? Tailor depth and vocabulary accordingly.
2. **Project phase** -- where are we in the project lifecycle (discovery, build, testing, launch, post-launch)? This sets expectations for what to report.
3. **Recent progress** -- what was completed since the last update? Pull from sprint board, merged PRs, design completions, decisions made.
4. **Blockers and risks** -- what is currently blocked, at risk, or needs a decision? Be specific: what is blocked, by whom, what is needed, what is the impact of delay.
5. **Upcoming milestones** -- what is the next milestone and when? What must happen before then?
6. **Budget and timeline** -- is the project on budget and on schedule? If not, by how much and why?
7. **Tone and relationship** -- is this a new client relationship (more formal) or an established one (more direct)? Adjust formality accordingly.

## Step 3: Sprint Demo Preparation

### Demo Script Template

```
SPRINT DEMO SCRIPT
Sprint: [Sprint number / name]
Date: [Date]
Duration: 30 minutes (hard cap -- respect everyone's time)
Presenter: [Name]
Audience: [Names and roles]

AGENDA (share with attendees 24 hours before)

1. INTRO (2 min)
   "Welcome to Sprint [X] demo. This sprint we focused on [1-2 sentence
   theme]. Here's what we'll walk through today."

   Sprint goals recap:
     - [Goal 1]: [Complete / Partial / Moved to next sprint]
     - [Goal 2]: [Complete / Partial / Moved to next sprint]
     - [Goal 3]: [Complete / Partial / Moved to next sprint]

2. WHAT WE BUILT (20 min)
   Feature/item 1: [Name]
     - What it does (1 sentence, non-technical)
     - Live demo flow:
       Step 1: [Navigate to X]
       Step 2: [Perform action Y]
       Step 3: [Show result Z]
     - Why it matters to users / business

   Feature/item 2: [Name]
     - [Same structure as above]

   Technical improvements (if relevant to audience):
     - [Performance improvement, infrastructure change, etc.]
     - Keep technical details to 2 minutes max unless audience is technical

3. METRICS (3 min)
   - Sprint velocity: [X points completed / Y planned]
   - Bug count: [opened / closed / remaining]
   - Test coverage: [percentage, trend]
   - Key product metrics impact (if measurable)

4. WHAT'S NEXT (3 min)
   Next sprint focus:
     - [Priority 1]
     - [Priority 2]
     - [Priority 3]

   Upcoming milestones:
     - [Milestone]: [Date] — [On track / At risk / explanation]

5. Q&A (2 min)
   "What questions do you have?"
   [Capture questions. If answer requires research, say so and follow up.]

FOLLOW-UP (within 24 hours):
   - Send demo recording link
   - Send sprint summary email (use Weekly Status template, Step 4)
   - Log action items from Q&A with owners and deadlines
```

### Environment Setup Checklist

```
Before every demo:
  - [ ] Staging environment is up and stable (check 1 hour before)
  - [ ] Test data is populated (realistic names, not "test123")
  - [ ] Test accounts are ready (login credentials documented)
  - [ ] Demo flow rehearsed end-to-end at least once
  - [ ] Fallback screenshots captured (in case live demo fails)
  - [ ] Screen sharing tested (resolution, font size legible)
  - [ ] Browser bookmarks set for key screens (avoid fumbling with URLs)
  - [ ] Notifications silenced on presenter's machine
  - [ ] Recording set up (Zoom/Meet recording or Loom)
  - [ ] Backup presenter identified (if primary is unavailable)

If the live demo fails during presentation:
  - Do NOT debug live. Say: "Let me show you this via screenshots
    while we investigate." Switch to fallback screenshots immediately.
  - Follow up with a working recording within 24 hours.
```

### Demo Recording Guidelines (for Async Stakeholders)

```
For stakeholders who cannot attend live:
  Tool: Loom or recorded Zoom/Meet
  Length: 10-15 minutes (tighter than live, no Q&A padding)
  Format:
    - Intro slide: sprint number, date, goals (15 seconds)
    - Screen recording of each feature with voiceover
    - Summary slide: what's next, any decisions needed
    - End with: "Reply with questions or schedule time to discuss."

Upload to shared drive and link in weekly status email.
```

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

## Step 5: Risk Escalation Framework

### Risk Register Template

```
RISK REGISTER — [Project Name]
Last updated: [Date]

┌────┬──────────────────────┬──────────┬────────┬────────────────────┬───────────┬──────────────────┐
│ #  │ Risk                 │ Likelih. │ Impact │ Mitigation         │ Owner     │ Escalation       │
│    │                      │ (H/M/L)  │ (H/M/L)│                    │           │ Trigger          │
├────┼──────────────────────┼──────────┼────────┼────────────────────┼───────────┼──────────────────┤
│ 1  │ Apple rejects app    │ Medium   │ High   │ Pre-review checklist│ iOS Lead │ If rejected,      │
│    │ update               │          │        │ submitted to Apple │           │ escalate within  │
│    │                      │          │        │ review team        │           │ 24 hours         │
├────┼──────────────────────┼──────────┼────────┼────────────────────┼───────────┼──────────────────┤
│ 2  │ Third-party API      │ Low      │ High   │ Build fallback     │ Backend   │ If API is down   │
│    │ deprecation          │          │        │ implementation     │ Lead      │ >4 hours         │
├────┼──────────────────────┼──────────┼────────┼────────────────────┼───────────┼──────────────────┤
│ 3  │ Design scope creep   │ High     │ Medium │ Change request     │ PM        │ If >2 days added │
│    │                      │          │        │ process enforced   │           │ to timeline      │
└────┴──────────────────────┴──────────┴────────┴────────────────────┴───────────┴──────────────────┘

Review cadence: Weekly in team standup. Escalated risks reviewed in client sync.
```

### Escalation Protocol

```
When to escalate:
  - A risk's escalation trigger has been met
  - A blocker cannot be resolved within the team's authority
  - Timeline impact exceeds 1 week (or agreed threshold)
  - Budget impact exceeds 10% (or agreed threshold)
  - A dependency on the client or third party is unresponsive for >3 business days
  - Scope change is requested that affects committed deliverables

Who to escalate to:
  Technical blocker:    Engineering Lead → CTO
  Scope/requirements:   PM → Client Product Owner → Client Sponsor
  Budget/contract:      PM → Account Manager → Client Sponsor
  Timeline:             PM → Client Product Owner (if scope trade-off needed)
  People/resourcing:    PM → Delivery Lead → Account Manager

How to escalate:
  1. Document the issue using the Bad News format (below)
  2. Schedule a call or send a written escalation (do not bury in Slack)
  3. Propose options — never escalate without a recommendation
  4. Set a decision deadline — "We need a decision by [date] to stay on track"
  5. Follow up in writing with the decision and action items
```

### Bad News Delivery Format

```
RISK ESCALATION: [Brief Title]
Project: [Name]
Date: [Date]
From: [Your name / role]
To: [Stakeholder name / role]
Priority: [High / Critical]
Decision needed by: [Date]

SITUATION
  [What happened or what we discovered. Be factual and specific.
   Two to three sentences maximum. Do not editorialize.]

IMPACT
  Timeline: [How many days/weeks will this add, if any]
  Budget:   [Cost impact, if any]
  Scope:    [What features or deliverables are affected]
  Quality:  [Any quality or reliability implications]

OPTIONS
  Option A: [Description]
    - Timeline impact: [X days]
    - Cost impact: [$X]
    - Tradeoff: [What we give up]

  Option B: [Description]
    - Timeline impact: [X days]
    - Cost impact: [$X]
    - Tradeoff: [What we give up]

  Option C: Do nothing
    - Timeline impact: [X days delay]
    - Cost impact: [$X at risk]
    - Risk: [What happens if we don't act]

RECOMMENDATION
  We recommend Option [X] because [one sentence rationale].

NEXT STEPS (if recommendation accepted)
  1. [Action] — [Owner] — [By date]
  2. [Action] — [Owner] — [By date]

Rules for delivering bad news:
  - Never bury the lede. Lead with the impact, not the backstory.
  - Never present a problem without options. Always have a recommendation.
  - Deliver bad news early. A problem discovered Monday should not wait
    until Friday's status report.
  - Separate facts from opinions. "The API integration will take 2 more
    weeks" (fact) vs "I think we might need more time" (vague).
  - Own the message. Do not blame team members, vendors, or the client.
    Focus on what happened and what we do next.
```

## Step 6: Executive Summary Format

### One-Page Executive Summary

```
EXECUTIVE SUMMARY — [Project Name]
Period: [Month Year] or [Quarter Year]
Prepared by: [Name]

PROJECT HEALTH
  ████████████████████░░░░░  78% Complete
  Timeline: ON TRACK  |  Budget: ON TRACK  |  Quality: GREEN

KEY METRICS
  ┌─────────────────────────┬─────────────┐
  │ Metric                  │ Value        │
  ├─────────────────────────┼─────────────┤
  │ Sprint velocity (avg)   │ 42 pts/sprint│
  │ Features shipped        │ 12 this month│
  │ Open bugs (P0/P1)       │ 0 / 3        │
  │ Test coverage           │ 84%          │
  │ Uptime (production)     │ 99.97%       │
  └─────────────────────────┴─────────────┘

COMPLETED THIS PERIOD
  - [Major accomplishment 1 — business impact, not technical detail]
  - [Major accomplishment 2]
  - [Major accomplishment 3]

DECISIONS NEEDED
  1. [Decision — context in 1 sentence. Options: A or B. Recommend: A.]
  2. [Decision — context. Deadline: [Date].]
  (If none: "No decisions needed this period.")

RISKS
  - [Top risk — mitigation in progress / escalated]
  (If none: "No significant risks this period.")

UPCOMING
  Next milestone: [Name] — [Date]
  Key deliverables: [1-2 items]

BUDGET
  Allocated: $[X]  |  Spent: $[Y] ([Z]%)  |  Forecast: $[W]
```

Rules for executive summaries:
- One page maximum. If it does not fit on one page, cut it.
- Lead with project health (green/amber/red or progress bar)
- Use business language, not technical jargon
- Decisions needed should include a recommendation -- executives want to approve, not analyze
- No surprises -- if something is RED here, it was already escalated

### Quarterly Business Review Template

```
QUARTERLY BUSINESS REVIEW
Project: [Name]
Quarter: [Q1/Q2/Q3/Q4 YYYY]
Attendees: [Names]

1. QUARTER RECAP (5 min)
   Objectives set:     [List from last QBR]
   Objectives met:     [X of Y]
   Key deliverables:   [Major features/milestones completed]

2. METRICS & HEALTH (10 min)
   [Product metrics: users, revenue, engagement — whatever was agreed]
   [Engineering metrics: velocity, quality, uptime]
   [Budget status: actual vs. planned]

3. DEMO OF KEY FEATURES (10 min)
   [Show 2-3 most impactful features from the quarter]

4. CHALLENGES & LEARNINGS (5 min)
   [Top 2-3 challenges faced and how they were resolved]
   [Process improvements made]

5. NEXT QUARTER PLAN (10 min)
   Objectives: [3-5 objectives for next quarter]
   Key milestones: [With dates]
   Dependencies: [What we need from the client]
   Risks: [Known risks going into next quarter]

6. DISCUSSION (20 min)
   [Open floor for client questions, priorities, feedback]
```

## Step 7: Meeting Facilitation

### Agenda Template

```
MEETING AGENDA
Meeting: [Name]
Date: [Date] | Time: [Time + timezone] | Duration: [X minutes]
Attendees: [Names]
Location: [Zoom/Meet link or room]

Pre-read (review before meeting):
  - [Link to document 1]
  - [Link to document 2]

Agenda:
  [Time] 1. [Topic] — [Presenter] — [Purpose: Inform / Discuss / Decide]
  [Time] 2. [Topic] — [Presenter] — [Purpose]
  [Time] 3. [Topic] — [Presenter] — [Purpose]
  [Time] 4. Action items and next steps — [Facilitator]

Notes will be shared within 24 hours.

Rule: Every meeting must have an agenda sent at least 4 hours before.
      If there's no agenda, cancel the meeting.
```

### Decision Log

```
DECISION LOG — [Project Name]
Maintained in: [Notion / Google Doc / Confluence — single source of truth]

┌────┬────────────┬───────────────────────────────┬──────────────┬──────────────┐
│ #  │ Date       │ Decision                      │ Decided By   │ Context      │
├────┼────────────┼───────────────────────────────┼──────────────┼──────────────┤
│ 1  │ 2026-01-15 │ Use Firestore over Cloud SQL  │ CTO + Client │ ADR-003      │
│ 2  │ 2026-01-22 │ Launch Android first, iOS Q2  │ Client PO    │ Sprint retro │
│ 3  │ 2026-02-01 │ Approve 2-week timeline ext.  │ Client Exec  │ Escalation   │
└────┴────────────┴───────────────────────────────┴──────────────┴──────────────┘

Rule: Every significant decision is logged with date, who decided, and context.
      This prevents "we never agreed to that" conversations later.
      Link to ADRs (Architecture Decision Records) where applicable.
      → Cross-ref: /sdlc for ADR format
```

### Action Items Format

```
Action items from every meeting:
  [ACTION] [Description] — [Owner] — [Due date]

Examples:
  [ACTION] Share revised timeline with client — @PM — 2026-03-17
  [ACTION] Investigate iOS build failure — @iOS Lead — 2026-03-16
  [ACTION] Approve design mockups for settings screen — @Client PO — 2026-03-18

Rules:
  - Every action item has exactly ONE owner (not "the team")
  - Every action item has a specific due date (not "ASAP" or "next week")
  - Action items are tracked in a single system (Linear, Jira, Notion)
  - Overdue items are flagged in the next meeting, not silently ignored

Send action items within 24 hours of the meeting. Format:
  "Here are the action items from today's meeting. Please reply if
   anything is incorrect or if due dates need adjustment."
```

### Async-First Defaults

```
Default to async communication when possible:

Use async (written) for:
  - Status updates (weekly email, not weekly meeting)
  - Information sharing (Loom video, not presentation meeting)
  - Simple decisions (Slack/email with deadline, not meeting)
  - Code reviews and design feedback (PR comments, Figma comments)

Use sync (meeting) for:
  - Sprint demos (stakeholder engagement matters)
  - Risk escalations (tone and nuance matter)
  - Complex decisions with multiple tradeoffs
  - Relationship building (quarterly business reviews, kickoffs)
  - Conflict resolution (never resolve conflict over email)

Rule: Before scheduling a meeting, ask: "Could this be a Loom video
      or an email with a decision deadline?" If yes, do that instead.
      Respect everyone's time — especially the client's.
```

## Artifact Generation (Required)

Generate communication templates using Write:
1. **Sprint demo script**: `docs/comms/demo-script.md` — talking points, demo flow, Q&A prep
2. **Status report**: `docs/comms/status-report.md` — executive summary with RAG status
3. **Risk escalation**: `docs/comms/risk-escalation.md` — structured escalation with impact analysis
4. **Stakeholder map**: `docs/comms/stakeholder-map.md` — RACI for communications

## Step 8: Output

```
CLIENT COMMUNICATION PLAN
Project: [NAME]
Date: [TODAY]
Prepared by: [NAME]
Client: [Client name / organization]

COMMUNICATION SUMMARY
┌──────────────────────┬────────────────────────────────────┐
│ Field                │ Value                              │
├──────────────────────┼────────────────────────────────────┤
│ Communication Need   │ [From Step 1 classification]       │
│ Audience             │ [Stakeholder roles]                │
│ Project Phase        │ [Discovery / Build / Launch]       │
│ Update Cadence       │ [Weekly / Biweekly / Monthly]      │
│ Demo Cadence         │ [Every sprint / Monthly]           │
│ Escalation Path      │ [PM → Account Mgr → Client Exec]  │
│ Decision Log         │ [Location / URL]                   │
└──────────────────────┴────────────────────────────────────┘

DELIVERABLES GENERATED:
  - [ ] Sprint demo script and environment checklist
  - [ ] Weekly status report template
  - [ ] Milestone report template
  - [ ] RAG status format
  - [ ] Risk register with escalation triggers
  - [ ] Bad news delivery format
  - [ ] Executive summary template
  - [ ] Meeting agenda and action items format
  - [ ] Decision log initialized

CROSS-REFERENCES:
  - /project-manager — for sprint planning and project tracking
  - /sdlc — for ADR format and SDLC artifact generation
  - /product-manager — for roadmap and feature brief communication
```
