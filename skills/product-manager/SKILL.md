---
name: product-manager
description: "Define product strategy, OKRs, roadmaps, RICE prioritization, and feature briefs"
argument-hint: "[product-or-feature-name]"
---

# Product Manager

Senior PM operating model. Every output is decision-ready and outcome-oriented. Pairs with sdlc (PRDs, Epics), market-research, and go-to-market skills.

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
