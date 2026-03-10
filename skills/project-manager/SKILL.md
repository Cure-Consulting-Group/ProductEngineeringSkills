---
name: project-manager
description: "Run sprint planning, RACI matrices, risk registers, retrospectives, and velocity tracking"
argument-hint: "[project-name]"
---

# Project Manager

Senior TPM / Scrum Master operating model. Ceremonies that serve the team. Integrates with sdlc backlog (Epics, Stories, Tasks).

## Core Ceremonies & Cadence

```
Daily Standup       → 15 min | Yesterday, Today, Blockers — no status theater
Sprint Planning     → 2hr/2wk sprint | Pull from prioritized backlog
Sprint Review       → Demo working software, not slide decks
Retrospective       → 1hr | What worked, what didn't, one experiment next sprint
Backlog Refinement  → 1hr mid-sprint | Groom next sprint's stories
Milestone Check-in  → Weekly | Status vs. plan, risk review
```

## Step 1: Classify the Request

| Request | Output |
|---------|--------|
| Sprint planning | Sprint plan + capacity |
| Project timeline | Phased timeline + Gantt |
| Status report | Stakeholder status update |
| Risk management | Risk register |
| Retrospective | Retro facilitation + output |
| Kickoff | Project kickoff plan |
| Launch readiness | Launch checklist + go/no-go |
| Post-mortem | Blameless post-mortem doc |
| Dependency map | Dependency matrix |
| RACI | Responsibility matrix |

## Step 2: Context Gathering

**Sprint planning:** Team size, velocity (if known), sprint length, backlog items to consider
**Timeline:** Feature list, team size, hard deadline, known dependencies
**Status report:** Audience (exec / engineering / client), current milestone, blockers
**Risk register:** Project scope, team, known constraints, deadline pressure
**Retrospective:** Sprint number, sprint goal, general mood of team

## Project Health Dashboard

Every project gets a weekly health score across 4 dimensions:

```
SCOPE     🟢 On track | 🟡 At risk | 🔴 Scope creep detected
SCHEDULE  🟢 On track | 🟡 1-2 sprints behind | 🔴 3+ sprints behind
QUALITY   🟢 <0.5% crash | 🟡 0.5-2% crash | 🔴 >2% or P0 open
TEAM      🟢 Full capacity | 🟡 1 person out | 🔴 Blocking dependency
```

## RACI Matrix Template

```markdown
## RACI — [Project/Feature Name]

| Activity | [PM] | [Tech Lead] | [Eng] | [Design] | [QA] | [Stakeholder] |
|----------|------|------------|-------|----------|------|--------------|
| PRD approval | A | C | I | C | I | R |
| Architecture decision | I | R | C | I | I | I |
| Sprint planning | R | C | C | I | I | I |
| Design review | C | I | I | R | I | A |
| Code review | I | A | R | I | I | I |
| QA sign-off | I | I | I | I | R | I |
| Release approval | A | C | I | I | C | R |

R = Responsible (does the work)
A = Accountable (owns the outcome, one per row)
C = Consulted (input before decision)
I = Informed (notified after decision)
```

## Dependency Matrix Template

```markdown
## Dependency Map — [Project]

| Story | Depends On | Type | Status | Risk |
|-------|-----------|------|--------|------|
| STORY-005 | STORY-002 (API contract) | Hard | In progress | Med |
| STORY-006 | External: Stripe Connect | External | Unconfirmed | High |
| EPIC-003 | EPIC-001 complete | Hard | Not started | Low |

**External dependencies requiring escalation:**
- [Dependency] — Owner: [Name] — Escalation path: [Who to contact]
```

## Velocity & Capacity Rules

```
Sprint velocity = average story points completed per sprint (last 3 sprints)
Capacity adjustment factors:
  - PTO: -[N] pts per day per engineer
  - On-call week: -20% total capacity
  - Ramp-up (new eng): 50% capacity for first 2 sprints
  - Code review overhead: budget 10% of velocity

Healthy sprint: 85% of velocity committed, 15% buffer for bugs/incidents
Overcommitted sprint: >100% velocity committed = delivery risk, flag immediately
```

## Definition of Ready (Before Story Enters Sprint)

- [ ] Acceptance criteria written in Given/When/Then
- [ ] Design ticket linked and approved (DESIGN-NNN)
- [ ] API spec linked or confirmed N/A
- [ ] Dependencies identified and unblocked
- [ ] Story pointed by the team
- [ ] No open blocking questions
- [ ] Test spec outlined (TEST-UNIT-NNN)
