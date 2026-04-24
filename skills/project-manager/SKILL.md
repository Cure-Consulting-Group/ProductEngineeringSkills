---
name: project-manager
version: "1.0.0"
description: "Sprint execution and delivery management — sprint planning, RACI matrices, risk registers, retrospectives, and velocity tracking for engineering teams"
when_to_use: "Use when asked to 'plan a sprint', 'create a RACI', 'run a retro', or 'track velocity'. NOT for product strategy or OKRs (use product-manager). NOT for engineering specs (use sdlc)."
argument-hint: "[project-name]"
---

# Project Manager

## Pre-Processing (Auto-Context)

Before starting, gather project context silently:
- Read `PORTFOLIO.md` if it exists in the project root or parent directories for product/team context
- Run: `cat package.json 2>/dev/null || cat build.gradle.kts 2>/dev/null || cat Podfile 2>/dev/null` to detect stack
- Run: `git log --oneline -5 2>/dev/null` for recent changes
- Run: `ls src/ app/ lib/ functions/ 2>/dev/null` to understand project structure
- Use this context to tailor all output to the actual project

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

## Sprint Planning Framework

### Capacity Calculation
```
Team capacity = (Number of devs × Available days × Focus factor)
Focus factor: 0.7 for teams with on-call, 0.8 for dedicated teams
Story points per sprint = Historical velocity (3-sprint average)
```

### Sprint Ceremony Schedule
| Ceremony | Duration | Frequency | Output |
|----------|----------|-----------|--------|
| Sprint Planning | 2h | Biweekly | Sprint backlog |
| Daily Standup | 15m | Daily | Blockers identified |
| Sprint Review | 1h | Biweekly | Demo + stakeholder feedback |
| Retrospective | 1h | Biweekly | Action items |
| Backlog Refinement | 1h | Weekly | Estimated stories |

## Risk Register Template

| Risk ID | Description | Probability | Impact | Score | Mitigation | Owner | Status |
|---------|-------------|-------------|--------|-------|------------|-------|--------|
| R001 | [risk] | H/M/L | H/M/L | [P×I] | [strategy] | [name] | Open |

## Velocity Tracking

Use git history to estimate velocity:
- Run: `git log --oneline --since="14 days ago" | wc -l` for commit frequency
- Run: `git log --oneline --since="14 days ago" --format="%s" | grep -c "feat:"` for feature commits
- Compare across sprints to identify trends

## Artifact Generation (Required)

Generate using Write:
1. **Sprint plan**: `docs/sprints/sprint-{N}.md` with goals, capacity, committed stories
2. **Risk register**: `docs/risk-register.md` with scored risks and mitigations
3. **RACI matrix**: `docs/raci.md` for current initiative
4. **Retrospective template**: `docs/retro-template.md`
5. **Burndown chart**: ASCII/Mermaid burndown showing ideal vs actual

Use Grep on git log to analyze velocity trends: `git log --format="%ai" --since="90 days ago"` grouped by week.
