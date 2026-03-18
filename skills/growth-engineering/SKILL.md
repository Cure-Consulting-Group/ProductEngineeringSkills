---
name: growth-engineering
description: "Build growth systems — activation funnels, referral programs, lifecycle automation, cohort analysis, and product-led growth patterns"
argument-hint: "[metric-or-feature]"
---

# Growth Engineering

## Pre-Processing (Auto-Context)

Before starting, gather project context silently:
- Read `PORTFOLIO.md` if it exists in the project root or parent directories for product/team context
- Run: `cat package.json 2>/dev/null || cat build.gradle.kts 2>/dev/null || cat Podfile 2>/dev/null` to detect stack
- Run: `git log --oneline -5 2>/dev/null` for recent changes
- Run: `ls src/ app/ lib/ functions/ 2>/dev/null` to understand project structure
- Use this context to tailor all output to the actual project

Build systematic, measurable growth into your product. Growth is not marketing — it is engineering loops that compound over time.

## Step 1: Classify the Growth Need

| Need | Output |
|------|--------|
| Activation optimization | Time-to-value reduction plan + experiment backlog |
| Retention improvement | Engagement loop design + re-engagement automation |
| Referral system | Viral mechanics + invite flow + reward structure |
| Monetization experiment | Paywall strategy + conversion triggers + pricing tests |
| Lifecycle automation | Drip campaigns + behavioral triggers + segmentation rules |
| Cohort analysis | Retention curves + segmented metrics + experiment design |

## Step 2: Gather Context

1. **Product** — what app/platform? B2C, B2B, marketplace?
2. **Current metrics** — DAU/MAU, signup-to-activation rate, D1/D7/D30 retention, conversion rate?
3. **User lifecycle stage** — pre-PMF (find activation), post-PMF (scale acquisition), mature (optimize monetization)?
4. **Analytics stack** — Firebase Analytics, Mixpanel, Amplitude, PostHog? Feature flags tool?
5. **Growth team maturity** — first growth hire, or established experimentation culture?
6. **Constraints** — budget for incentives? Platform restrictions (Apple referral rules, Play Store policies)?

## Step 3: Growth Model — AARRR Pirate Metrics

```
Build your growth model top-down. Measure every stage:

  Acquisition     → How do users find you?
    Metrics: CAC, signups/week, channel mix, organic vs paid ratio
    Goal: lower CAC, diversify channels

  Activation      → Do they experience the core value?
    Metrics: signup-to-activation rate, time-to-value, onboarding completion
    Goal: >60% of signups reach activation within first session

  Retention       → Do they come back?
    Metrics: D1, D7, D30 retention, DAU/MAU ratio, churn rate
    Goal: D30 retention >20% (consumer), >40% (B2B SaaS)

  Revenue         → Do they pay?
    Metrics: conversion rate, ARPU, LTV, LTV:CAC ratio
    Goal: LTV:CAC > 3:1, payback period < 12 months

  Referral        → Do they invite others?
    Metrics: viral coefficient (K), invite send rate, invite accept rate
    Goal: K > 0.3 (assists growth), K > 1.0 (viral growth)

Model the funnel numerically:
  1000 visitors → 200 signups (20% CVR) → 80 activated (40%) →
  32 retained D30 (40%) → 10 paid (31%) → 3 referrals (30%)
  Each referral brings 2 visitors → 6 new top-of-funnel

Track weekly. Build a spreadsheet. Every optimization compounds.
```

## Step 4: Activation Engineering

```
Activation is the most important growth lever. Fix activation before scaling acquisition.

Identify your aha moment:
  1. List all user actions in first 7 days
  2. Segment users: retained (active at D30) vs churned
  3. Compare action frequencies between groups
  4. The action with highest retained-vs-churned delta = aha moment

Time-to-value optimization:
  - Measure time from signup to aha moment (median, p75, p90)
  - Target: aha moment reachable in first session (<5 minutes)
  - Remove every step between signup and core value
  - Pre-fill data, use smart defaults, defer non-essential setup

Onboarding experiments (run sequentially, not in parallel):
  1. Reduce signup fields (test social auth only vs email)
  2. Add interactive walkthrough vs passive tooltips
  3. Personalize first screen based on signup intent
  4. Pre-populate with sample data vs empty state
  5. Guided first action vs free exploration

Progressive disclosure rules:
  - Day 0: core feature only, everything else hidden
  - Day 1-3: introduce secondary features via contextual prompts
  - Day 7+: full feature set available, advanced features highlighted
  - Never show settings, preferences, or admin during onboarding

Empty state strategy:
  - Every empty screen is a growth opportunity
  - Show what the screen looks like when populated (preview/demo data)
  - Single CTA: "Create your first [X]"
  - Include social proof: "[N] users created their first [X] today"
```

## Step 5: Retention Systems

```
Retention is a product problem, not a marketing problem. Build retention into the product.

Engagement loops (every product needs at least one):
  Trigger → Action → Reward → Investment

  Example (fitness app):
    Trigger: push notification "Your workout streak is at 5 days"
    Action: complete today's workout
    Reward: streak badge + progress visualization
    Investment: workout history + streak count (loss aversion)

  Example (SaaS):
    Trigger: email "3 teammates commented on your doc"
    Action: open app, review comments
    Reward: collaborative progress, social validation
    Investment: content created, team context built

Re-engagement triggers:
  At-risk detection (fire before user churns):
    - No session in 2 days → push notification (value reminder)
    - No session in 5 days → email (what they're missing)
    - No session in 14 days → email (personal outreach from founder)
    - No session in 30 days → win-back offer (discount, extended trial)

  Implementation:
    - Cloud Function / cron job checks last_active_at daily
    - Segment users into: active, cooling, at-risk, dormant, churned
    - Different messaging per segment — never generic blasts

Streak and habit mechanics:
  - Show streak count prominently (don't hide it)
  - Grace period: 1 missed day doesn't break streak (reduces anxiety)
  - Weekly cadence is easier than daily for most products
  - Milestone rewards at 7, 30, 100 (celebration + shareable badge)

Push notification strategy:
  - Transactional: immediate (someone replied to you)
  - Re-engagement: max 2/week, never between 9pm-9am local time
  - Always include specific content ("Alex commented on your design")
  - Never generic ("Check out what's new!")
  - A/B test copy, timing, and deep link destination
```

## Step 6: Referral and Viral Mechanics

```
Referral systems only work if the product is already good. Fix retention first.

Viral coefficient calculation:
  K = (invites sent per user) x (conversion rate of invites)
  Example: each user sends 3 invites, 15% accept → K = 0.45
  K > 1.0 = organic viral growth (rare, don't plan for it)
  K > 0.3 = meaningful growth assist (realistic target)

Invite flow design:
  1. Trigger: surface invite prompt after user experiences value
     - After first success: "Share [X] with your team"
     - After milestone: "You've completed 10 workouts — invite a friend"
     - Never: during onboarding, during errors, randomly
  2. Mechanism: pre-filled message with deep link
     - SMS/iMessage (highest conversion on mobile)
     - Email (B2B, professional context)
     - Share sheet (let user pick channel)
     - Copy link (fallback, lowest friction)
  3. Landing: recipient sees personalized invite page
     - "[Sender name] invited you to [Product]"
     - Show what sender has achieved (social proof)
     - One-tap signup (pre-fill referral code)

Reward structures:
  Two-sided rewards outperform one-sided 2-3x:
    "Give $10, get $10" > "Get $10 for each referral"

  Reward types (in order of effectiveness):
    1. Product value: extra storage, premium features, extended trial
    2. Credit: account credit toward subscription
    3. Cash: direct payment (expensive, attracts low-quality referrals)

  Anti-fraud:
    - Require referred user to activate (not just sign up)
    - Cap rewards per user per month
    - Detect duplicate devices/IPs
    - Delay reward payout 7 days (reversible if fraudulent)

Platform-specific share integration:
  iOS:    UIActivityViewController, ShareLink (SwiftUI)
  Android: Intent.ACTION_SEND with chooser, ShareSheet API
  Web:    Web Share API (navigator.share), fallback to copy-link
```

## Step 7: Cohort Analysis and Experimentation

```
Cohort analysis framework:
  Define cohorts by signup week (default) or by:
    - Acquisition channel (organic vs paid vs referral)
    - Platform (iOS vs Android vs Web)
    - Plan tier (free vs paid)
    - Geography (US vs international)
    - Feature exposure (saw feature vs control)

Retention curve analysis:
  Week 0   Week 1   Week 2   Week 4   Week 8   Week 12
  100%     35%      28%      22%      18%      16%

  Healthy curve: flattens after week 4 (found core users)
  Unhealthy curve: never flattens (no product-market fit)

  Compare curves across cohorts. If paid users retain 3x better
  than free users, your activation problem is really a targeting problem.

A/B test design for growth:
  1. Hypothesis: "Reducing signup to 1 field will increase completion by 20%"
  2. Primary metric: signup completion rate
  3. Guardrail metrics: activation rate, D7 retention (watch for quality drop)
  4. Sample size: calculate before launch (minimum detectable effect, power)
  5. Duration: minimum 2 weeks, capture weekly patterns
  6. Analysis: check guardrails first, then primary metric

  Statistical significance:
    - p < 0.05 for primary metric (standard)
    - Run until significance OR pre-determined end date
    - Never peek and stop early on a positive result
    - Use sequential testing if you must monitor continuously

  Guardrail metrics (always monitor):
    - Activation rate (are we getting worse users?)
    - Revenue per user (are we cannibalizing?)
    - Support ticket rate (are we creating confusion?)
    - Error rate (is the variant broken?)

Experiment velocity:
  Target: 2-3 growth experiments per week
  Each experiment: hypothesis, design, ship, measure, document
  Keep a log: experiment name, hypothesis, result, learning
  Share learnings weekly — compound institutional knowledge
```

## Step 8: Product-Led Growth Patterns

```
PLG means the product is the primary driver of acquisition, conversion, and expansion.

Freemium conversion:
  Free tier must be genuinely useful (not a crippled demo):
    - Enough value to create habit and dependency
    - Limits hit naturally through usage growth
    - Upgrade prompt at moment of need, not randomly

  Effective limits:
    Good: 3 projects (hit when engaged), 1GB storage (hit when invested)
    Bad: 7-day trial (arbitrary), watermark on exports (punitive)

Usage-based upgrade triggers:
  - Approaching limit: "You've used 8 of 10 projects" (banner)
  - Hit limit: "Upgrade to create unlimited projects" (modal, not blocking)
  - Team growth: "Invite your 4th teammate — upgrade to Team plan"
  - Feature gate: "Export to PDF is a Pro feature" (show preview first)

  Timing matters:
    - Trigger at moment of highest intent (user trying to do the thing)
    - Never interrupt a flow mid-action
    - Offer monthly AND annual (anchor on annual savings)

Paywall optimization:
  - Show value received so far: "You've created 12 designs with [Product]"
  - Social proof: "Join 50,000 teams using Pro"
  - Risk reversal: "14-day money-back guarantee"
  - Price anchoring: show enterprise tier to make pro look reasonable

Trial design:
  Reverse trial (recommended):
    - Start with full features unlocked
    - After 14 days, downgrade to free tier
    - User has already experienced premium value → higher conversion
  Traditional trial:
    - 14 days of premium, then paywall
    - Requires credit card upfront (higher intent) vs no card (higher volume)
    - Cure default: no credit card required, reverse trial model

Expansion revenue:
  - Seat-based: charge per user, team growth = revenue growth
  - Usage-based: charge per API call, storage, compute
  - Feature-based: unlock tiers as needs grow
  - Best: hybrid seat + usage (predictable base + upside)
```

## Code Generation (Required)

Generate growth infrastructure using Write:

1. **Cohort analysis query**: `analytics/cohort-retention.sql` — BigQuery/PostgreSQL retention query
2. **A/B test sample calculator**: `scripts/sample-size-calculator.ts` — statistical significance calculator
3. **Referral system schema**: `src/referral/schema.ts` — Firestore/PostgreSQL schema for referral tracking
4. **Growth dashboard**: `monitoring/growth-dashboard.json` — dashboard config with AARRR metrics

## Cross-References

- `/analytics-implementation` — event taxonomy and tracking for growth metrics
- `/feature-flags` — experiment infrastructure for A/B tests
- `/customer-onboarding` — activation flow design (growth-engineering extends this)
- `/notification-architect` — push/email delivery for retention campaigns
- `/saas-financial-model` — unit economics that growth must satisfy
- `/stripe-integration` — payment and subscription mechanics for monetization
