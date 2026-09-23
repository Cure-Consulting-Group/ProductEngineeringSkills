---
name: project-manager
description: "Sprint and delivery management for engineering teams. Use when planning a sprint, sizing capacity, building a RACI, risk register, dependency map, timeline, or running a retro."
when_to_use: "NOT for OKRs or roadmaps (use product-manager), PRDs/stories (use sdlc), client status emails (use client-communication), or post-mortems (use incident-response)."
argument-hint: "[project-name]"
metadata:
  verified: 2026-09-23
---

# Project Manager

Senior TPM operating model: ceremonies that serve the team, plans built on measured capacity, risks
with owners. Output is the one artifact the request asks for, filled with the user's real data;
done when every row has an owner or a number and open assumptions are listed.

Match length to the need; no filler sections or restated summaries.

## Step 1: Classify the Request

| Request | Output |
|---|---|
| Sprint planning | Sprint plan: goal, capacity, committed stories, buffer |
| Timeline | Phased plan with dependencies (Mermaid `gantt` when dates matter) |
| Risk management | Scored risk register |
| Retrospective | Retro agenda + outcomes (one experiment for next sprint) |
| RACI | Responsibility matrix |
| Dependency map | Dependency matrix with escalation paths |
| Project health | Four-dimension health score (below) |

Route elsewhere: client-facing status updates → `client-communication`; launch go/no-go → `uat`
or `release-management`; post-mortems → `incident-response`; PRDs, epics, stories → `sdlc`.

## Step 2: Gather Context

Ask only for what the chosen output needs:

- **Sprint planning:** team size, sprint length, PTO/on-call, last 3 sprints' completed points, candidate backlog
- **Timeline:** feature list, team size, hard deadline, known dependencies
- **Risk register:** scope, team, constraints, deadline pressure
- **Retrospective:** sprint number, goal, what shipped vs planned
- **RACI / dependencies:** roles on the initiative, external parties

Velocity comes from the tracker (Linear, Jira, GitHub Projects): points or issues completed per
sprint. Commit counts and `feat:` greps are not velocity — they measure commit style, not delivered
scope. With no tracker history, plan from capacity and say the estimate is uncalibrated.

## Step 3: Cure Planning Rules

**Capacity**
```
Capacity = devs × available days × focus factor (0.7 with on-call, 0.8 dedicated)
Velocity = 3-sprint rolling average of completed points
Adjust:  on-call week −20% · new engineer 50% for first 2 sprints · review overhead 10%
Commit 85% of velocity; 15% buffer for bugs/incidents. >100% committed = flag as delivery risk.
```

**Definition of Ready** (story may enter a sprint): Given/When/Then acceptance criteria; design
linked (or N/A); API spec linked (or N/A); dependencies unblocked; pointed by the team; no open
blocking questions; test spec outlined.

**Project health** (weekly):
```
SCOPE     🟢 on track | 🟡 at risk | 🔴 scope creep
SCHEDULE  🟢 on track | 🟡 1–2 sprints behind | 🔴 3+ behind
QUALITY   🟢 <0.5% crash | 🟡 0.5–2% | 🔴 >2% or P0 open
TEAM      🟢 full | 🟡 1 person out | 🔴 blocking dependency
```

**Cadence** (2-week sprint): planning 2h, standup 15m daily, review 1h, retro 1h, refinement 1h weekly.

## Step 4: Templates

**Risk register** — score = probability × impact (H=3, M=2, L=1); anything ≥6 needs a named owner and a dated mitigation.

| Risk ID | Description | P | I | Score | Mitigation | Owner | Status |
|---|---|---|---|---|---|---|---|

**RACI** — exactly one A per row; R does the work, C is consulted before, I informed after.

| Activity | PM | Tech Lead | Eng | Design | QA | Stakeholder |
|---|---|---|---|---|---|---|
| PRD approval | A | C | I | C | I | R |
| Architecture decision | I | A/R | C | I | I | I |
| Code review | I | A | R | I | I | I |
| Release approval | A | C | I | I | C | R |

**Dependency map** — `Story | Depends on | Hard/Soft/External | Status | Risk`, plus an escalation
line (owner, contact) for every external dependency.

## Artifact Generation

Applies when the user wants a file rather than an inline answer. Write only the artifact classified
in Step 1, at a path that matches existing repo conventions (default `docs/sprints/sprint-{N}.md`,
`docs/risk-register.md`, `docs/raci.md`). Don't generate the other templates unasked.
