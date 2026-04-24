---
name: product-manager
version: "1.0.0"
description: "Product strategy and prioritization — OKRs, RICE-scored roadmaps, feature briefs, and outcome-driven planning for product leaders"
when_to_use: "Use when asked to 'prioritize features', 'write OKRs', 'build a roadmap', or 'create a feature brief'. NOT for engineering specs (use sdlc). NOT for sprint/project execution (use project-manager). NOT for market sizing (use market-research)."
argument-hint: "[product-or-feature-name]"
---

# Product Manager

Senior PM operating model. Every output is decision-ready and outcome-oriented. Pairs with sdlc (PRDs, Epics), market-research, and go-to-market skills.

## Pre-Processing (Auto-Context)

Before starting, gather project context silently:
- Read `PORTFOLIO.md` if it exists in the project root or parent directories for product/team context
- Run: `cat package.json 2>/dev/null || cat build.gradle.kts 2>/dev/null || cat Podfile 2>/dev/null` to detect stack
- Run: `git log --oneline -5 2>/dev/null` for recent changes
- Run: `ls src/ app/ lib/ functions/ 2>/dev/null` to understand project structure
- Use this context to tailor all output to the actual project

## PM Operating Principles

1. **Outcomes over outputs** — "increase activation rate" not "add onboarding screen"
2. **Evidence over opinion** — every recommendation grounded in data or explicit assumption
3. **Say no explicitly** — deferred items get a written reason, not silence
4. **Small bets first** — validate with minimum surface area before full build
5. **Define done before starting** — success metrics set before sprint begins

## Step 1: Classify the Request

| Request | Output |
|---------|--------|
| Strategy & vision | Product strategy doc |
| OKRs | OKR set with key results |
| Prioritization | Scored backlog (RICE/ICE) |
| Roadmap | Phased roadmap doc |
| Feature brief | Feature brief + success metrics |
| Discovery | Discovery sprint plan |
| Metrics | KPIs + north star + funnel |
| Release | Release notes + announcement |
| Pricing | Pricing strategy analysis (pair with market-research) |
| Competitive | Positioning + differentiation (pair with market-research) |

## Step 2: Context Gathering

Minimal viable context per output type:

**Strategy / OKRs:** Product name, stage, current traction (if any), top 1-3 business goals
**Prioritization:** List of candidate features/stories, time horizon, key constraint
**Roadmap:** Product, key milestones, resource constraints, launch deadline
**Feature brief:** Feature name, problem it solves, target user, definition of success
**Metrics:** Product type, current funnel (if known), what decision will this inform?

## Step 3: PM Document Standards

### All documents must include:
- **Decision or recommendation** — what are we doing and why?
- **Success criteria** — how will we know it worked?
- **Explicit non-goals** — what are we NOT doing?
- **Assumptions** — what must be true for this to work?
- **Open questions** — with owners and due dates

### Metric Rules (always apply):
- Every feature ships with a primary success metric (lead measure)
- Every feature ships with a guardrail metric (what we won't sacrifice)
- Metrics are measurable within the sprint or release window
- Vanity metrics (page views, total users) never the primary metric

## Core PM Frameworks

### RICE Scoring
```
Reach x Impact x Confidence / Effort = RICE Score

Reach:      Users affected per quarter (number)
Impact:     0.25 (minimal) | 0.5 (low) | 1 (med) | 2 (high) | 3 (massive)
Confidence: 50% (low) | 80% (medium) | 100% (high)
Effort:     Person-weeks (estimate)
```

### North Star Metric Framework
```
North Star = the single metric that best captures value delivered to users
             AND predicts long-term revenue growth

Good north stars:
  - Airbnb: nights booked
  - Spotify: time listening
  - Slack: messages sent within an organization

Input metrics (levers that move the north star):
  - Acquisition: new users
  - Activation: completed core action
  - Engagement: returned within 7 days
  - Revenue: converted to paid
  - Referral: invited another user
```

### User Story Mapping Format
```
[Activity] → [User Tasks] → [User Stories (releases)]

Example:
Sign Up → Enter email → Create account story (Release 1)
        → Verify email → Email verification story (Release 1)
        → Set up profile → Profile setup story (Release 2)
        → Connect social → Social linking story (Release 3)
```

## OKR Framework

When generating OKRs:
- **Objective**: Qualitative, inspirational, time-bound (quarterly)
- **Key Results**: 3-5 per objective, measurable, achievable but ambitious
- Use format:
  ```
  **O1: [Objective statement]**
  - KR1: [Metric] from [baseline] to [target] by [date]
  - KR2: [Metric] from [baseline] to [target] by [date]
  - KR3: [Metric] from [baseline] to [target] by [date]
  ```

## RICE Prioritization

Score every feature request:
| Factor | Definition | Scale |
|--------|-----------|-------|
| Reach | How many users affected per quarter | Actual number |
| Impact | Effect on individual user | 3=massive, 2=high, 1=medium, 0.5=low, 0.25=minimal |
| Confidence | How sure are we | 100%=high, 80%=medium, 50%=low |
| Effort | Person-months to complete | Actual estimate |

**RICE Score = (Reach × Impact × Confidence) / Effort**

Generate a prioritized backlog table sorted by RICE score.

## Artifact Generation (Required)

You MUST generate actual documents using Write:

1. **PRD**: `docs/prd/{feature-name}.md` — full PRD with problem, solution, success metrics, scope
2. **Feature brief**: `docs/briefs/{feature-name}.md` — 1-page summary for stakeholder alignment
3. **Roadmap**: `docs/roadmap.md` — Now/Next/Later format with RICE-scored items
4. **User story map**: ASCII art or Mermaid diagram showing user journey with story cards

Use WebSearch to validate assumptions about market size, user behavior, and competitive landscape.

## Cross-References

- `/market-research` — validate market assumptions before writing strategy docs
- `/sdlc` — generate PRDs, Epics, and Stories from PM briefs
- `/analytics-implementation` — define success metrics and tracking plans
