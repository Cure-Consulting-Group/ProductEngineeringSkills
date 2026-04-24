---
name: burn-rate-tracker
version: "1.0.0"
description: "Model burn rates, runway scenarios, break-even analysis, and cash flow projections for multi-product venture studios"
when_to_use: "Use when modeling portfolio burn rates, runway scenarios, or cash flow projections. NOT for SaaS unit economics (use saas-financial-model). NOT for cloud cost optimization (use finops)."
argument-hint: "[product-or-portfolio]"
allowed-tools: ["Read", "Grep", "Glob", "WebSearch"]
---

# Burn Rate Tracker

## Pre-Processing (Auto-Context)

Before starting, gather project context silently:
- Read `PORTFOLIO.md` if it exists in the project root or parent directories for product/team context
- Run: `cat package.json 2>/dev/null || cat build.gradle.kts 2>/dev/null || cat Podfile 2>/dev/null` to detect stack
- Run: `git log --oneline -5 2>/dev/null` for recent changes
- Run: `ls src/ app/ lib/ functions/ 2>/dev/null` to understand project structure
- Use this context to tailor all output to the actual project

Model burn rates, runway scenarios, and cash flow projections for multi-product venture studios. Built for Cure Consulting Group's portfolio: Vendly (LATAM merchant OS), Autograph (AI medical scribe), The Initiated (women's basketball recruiting), Antigravity (AI agent orchestration), TwntyHoops (basketball media/events). Every dollar should be traceable to a product, and every product should have a path to sustainability.

## Step 1: Classify the Analysis Type

| Type | When to Use | Output |
|------|------------|--------|
| Single product burn | Analyzing one portfolio company | Monthly burn, runway, break-even for that product |
| Portfolio burn | Studio-wide financial view | Aggregated burn across all products with allocation |
| Runway scenario | Planning fundraise timing or cost cuts | Conservative/base/optimistic/zero-revenue projections |
| Break-even analysis | Product reaching sustainability | Revenue needed per product and for portfolio |
| Budget planning | Quarterly or annual planning cycle | Forward-looking budget with targets per product |
| Cost reduction modeling | Runway getting tight | Tiered cost-cutting plan with runway impact |

## Step 2: Gather Context

1. **Products** — which portfolio companies are active? (Vendly, Autograph, The Initiated, Antigravity, TwntyHoops)
2. **Cash position** — total cash in bank across all accounts?
3. **Revenue per product** — monthly revenue by product line (even if zero)?
4. **Fixed costs** — salaries, rent, insurance, software subscriptions?
5. **Variable costs** — infrastructure (Firebase, GCP, AI APIs), payment processing, marketing?
6. **Team structure** — headcount per product, shared resources, contractors?
7. **Recent changes** — any new hires, product launches, or cost increases in last 90 days?
8. **Fundraising status** — any active raise? Expected close date? Bridge financing?

## Step 3: Burn Rate Components

```
FIXED COSTS (predictable, don't change with usage)

Category              Examples                                    Frequency
──────────────────────────────────────────────────────────────────────────────
Salaries              Full-time team, founders' comp               Monthly
Benefits              Health insurance, 401k, equity admin         Monthly
Rent / Coworking      Office space, hot desks                      Monthly
Insurance             D&O, E&O, general liability, cyber           Monthly/Annual
Legal retainer        Corporate counsel, IP, compliance            Monthly
Accounting            Bookkeeping, tax prep, audit                 Monthly/Quarterly
Software (core)       GitHub, Slack, Notion, Figma, GSuite        Monthly
Payroll processing    Gusto, Rippling, etc.                        Monthly

VARIABLE COSTS (scale with usage, customers, or decisions)

Category              Examples                                    Driver
──────────────────────────────────────────────────────────────────────────────
Cloud infrastructure  Firebase, GCP, AWS, Vercel                   Users/requests
AI API costs          OpenAI, Anthropic, Google AI                 Tokens/requests
Payment processing    Stripe fees (2.9% + $0.30)                   Transaction volume
Marketing             Ads, content, events, sponsorships           Campaign decisions
Contractors           Design, specialized engineering, legal        Project-based
Travel                Conferences, client meetings, recruiting     As needed
Data services         Analytics tools, data providers              Scale-dependent

PRODUCT ALLOCATION

Every cost falls into one of three buckets:
  1. Product-specific — directly attributable (e.g., Autograph's HIPAA compliance tools)
  2. Shared — benefits multiple products (e.g., shared infrastructure, design team)
  3. Studio overhead — benefits the entity, not a product (e.g., accounting, legal)

Allocation rules (pick ONE method and be consistent):
  - Headcount ratio: shared costs split by number of people on each product
  - Revenue ratio: shared costs split by revenue contribution (use for mature products)
  - Equal split: only when products are at similar stages (rarely appropriate)

  Recommended: headcount ratio for early-stage portfolio (most costs are people)
```

## Step 4: Burn Rate Calculations

```
GROSS BURN
  = Total monthly expenses (before any revenue)
  = Fixed costs + variable costs
  This is what you spend regardless of revenue.

NET BURN
  = Total monthly expenses - total monthly revenue
  = Gross burn - revenue
  This is how much cash you actually lose each month.

RUNWAY
  = Cash balance / net burn rate
  = Number of months until cash hits zero
  Rule: this is a point-in-time calculation — recalculate monthly

PER-PRODUCT BURN
  = Product-specific costs + allocated shared costs + allocated overhead
  Calculate for each portfolio company independently.

  Example:
  | Product | Direct Costs | Shared Allocation | Overhead Allocation | Total Burn | Revenue | Net Burn |
  |---------|-------------|-------------------|--------------------:|------------|---------|----------|
  | Vendly | $8,000 | $3,000 | $1,500 | $12,500 | $4,000 | $8,500 |
  | Autograph | $12,000 | $4,000 | $1,500 | $17,500 | $2,000 | $15,500 |
  | The Initiated | $5,000 | $2,000 | $1,500 | $8,500 | $500 | $8,000 |
  | Antigravity | $15,000 | $5,000 | $1,500 | $21,500 | $1,000 | $20,500 |
  | TwntyHoops | $4,000 | $1,500 | $1,500 | $7,000 | $3,000 | $4,000 |
  | TOTAL | $44,000 | $15,500 | $7,500 | $67,000 | $10,500 | $56,500 |

BURN RATE TREND
  Track month-over-month:
    Burn increasing + revenue flat = problem
    Burn stable + revenue growing = healthy
    Burn decreasing + revenue growing = excellent
    Burn increasing + revenue increasing faster = acceptable (investing in growth)

  Rule: if net burn increases 3 months in a row without corresponding revenue growth, something is wrong
```

## Step 5: Runway Scenarios

```
Model four scenarios — always. Present all four to leadership.

CONSERVATIVE (plan for this)
  Revenue: flat (no growth from current level)
  Costs: grow 5% per quarter (hiring, infrastructure scaling)
  Assumption: worst realistic case without catastrophic events

BASE CASE (budget to this)
  Revenue: grows at current MoM rate
  Costs: stable (current run rate maintained)
  Assumption: things continue as they are today

OPTIMISTIC (don't count on this)
  Revenue: accelerates (e.g., 2x current growth rate)
  Costs: stable or slight increase
  Assumption: a key bet pays off (new customer segment, viral growth, enterprise deal)

ZERO REVENUE (survival mode)
  Revenue: $0 (all customers churn or product fails)
  Costs: current level (before any cuts)
  Assumption: how long can we survive with zero income?

SCENARIO TABLE
| Scenario | Monthly Burn | Monthly Revenue | Net Burn | Runway (months) |
|----------|-------------|----------------|----------|-----------------|
| Conservative | $X | $X | $X | X |
| Base Case | $X | $X | $X | X |
| Optimistic | $X | $X | $X | X |
| Zero Revenue | $X | $0 | $X | X |

SCENARIO PROJECTIONS (12-month)
For each scenario, project month-by-month:
| Month | Revenue | Expenses | Net Burn | Cash Balance |
|-------|---------|----------|----------|-------------|
| 1 | $X | $X | $X | $X |
| 2 | $X | $X | $X | $X |
| ... | | | | |
| 12 | $X | $X | $X | $X |

Highlight:
  ⚠ Months where runway dips below 6 months (DANGER ZONE — start fundraising)
  🔴 Months where runway dips below 3 months (CRITICAL — execute cost cuts immediately)
  ✅ Month where cash flow turns positive (break-even achieved)
```

## Step 6: Break-Even Analysis

```
PER-PRODUCT BREAK-EVEN
  For each product, calculate:
    Break-even revenue = product-specific costs + allocated shared costs + allocated overhead
    Break-even MRR = break-even revenue (if subscription model)
    Break-even customers = break-even MRR / ARPU

  Example:
  | Product | Monthly Cost (allocated) | Current Revenue | Gap | Break-Even Customers |
  |---------|------------------------|-----------------|-----|---------------------|
  | Vendly | $12,500 | $4,000 | -$8,500 | 250 merchants @ $50 |
  | Autograph | $17,500 | $2,000 | -$15,500 | 35 clinics @ $500 |
  | The Initiated | $8,500 | $500 | -$8,000 | 160 recruits @ $53 |
  | Antigravity | $21,500 | $1,000 | -$20,500 | 22 enterprises @ $1,000 |
  | TwntyHoops | $7,000 | $3,000 | -$4,000 | varies (ads + events) |

PORTFOLIO BREAK-EVEN
  Total monthly cost: $67,000
  Total monthly revenue: $10,500
  Gap: $56,500
  Portfolio break-even: need $67,000/month total revenue across all products

TIME TO BREAK-EVEN (at current growth rates)
  Calculate for each scenario:
    months_to_breakeven = months until cumulative revenue >= cumulative costs

  If growth rate insufficient to reach break-even before cash runs out:
    → either raise capital or cut costs. There is no third option.

SENSITIVITY ANALYSIS
  What moves the break-even date the most?

  | Change | Break-Even Impact |
  |--------|------------------|
  | Add 1 engineer ($12K/mo) | +X months to break-even |
  | Cut 1 engineer | -X months to break-even |
  | Double marketing spend | +X months (if CAC payback > 6 months) |
  | 50% revenue acceleration | -X months to break-even |
  | Reduce AI API costs 40% | -X months to break-even |
  | Sunset lowest-performing product | -X months to break-even |

  Rule: headcount is almost always the largest lever. One hire can move break-even by months.
```

## Step 7: Cost Reduction Playbook

```
TIER 1 — EASY WINS (implement this week, minimal disruption)

  Action                               Estimated Monthly Savings
  ──────────────────────────────────────────────────────────────
  Audit and cancel unused SaaS         $200-1,000
  Downgrade dev/staging environments   $100-500
  Remove unused cloud resources        $100-500
  Switch to annual billing (savings)   $100-300
  Optimize AI model routing            $200-2,000
    (use Haiku/4o-mini for simple tasks instead of Opus/GPT-4)
  Enable Firebase offline caching      $50-200 (reduced reads)
  Delete unused Cloud Functions         $50-100

  Total Tier 1 potential: $800-4,600/month

TIER 2 — MODERATE EFFORT (implement this month, some process change)

  Action                               Estimated Monthly Savings
  ──────────────────────────────────────────────────────────────
  Implement AI response caching        $500-3,000
  Right-size Cloud Function memory     $200-1,000
  Reduce marketing spend to            $1,000-5,000
    highest-ROI channels only
  Renegotiate vendor contracts         $200-1,000
  Move from per-seat to team plans     $100-500
  Consolidate monitoring/observability  $100-300
  Reduce CI/CD build minutes           $50-200

  Total Tier 2 potential: $2,150-11,000/month

TIER 3 — HARD DECISIONS (implement if runway < 6 months)

  Action                               Estimated Monthly Savings
  ──────────────────────────────────────────────────────────────
  Reduce headcount (last resort)       $8,000-15,000 per person
  Pause hiring for open roles          $10,000-15,000 per role
  Sunset underperforming product       $5,000-20,000
  Reduce founder compensation          $2,000-10,000
  Close office / go fully remote       $2,000-5,000
  Defer contractor work                $3,000-10,000

  Total Tier 3 potential: $30,000-75,000/month

NEVER CUT:
  - Security and compliance tooling (breach costs >> tool costs)
  - Core product quality (shipping broken product kills retention faster than saving money)
  - Customer support response time (churn accelerates when support degrades)
  - Legal essentials (D&O insurance, corporate counsel retainer)
  - Data backups (losing data is existential)
```

## Step 8: Cash Flow Projection Template

```
12-MONTH CASH FLOW PROJECTION — [COMPANY/PORTFOLIO]
Date: [TODAY]
Starting Cash: $[X]

| | Month 1 | Month 2 | Month 3 | ... | Month 12 |
|---|---------|---------|---------|-----|----------|
| REVENUE | | | | | |
| Vendly | $X | $X | $X | | $X |
| Autograph | $X | $X | $X | | $X |
| The Initiated | $X | $X | $X | | $X |
| Antigravity | $X | $X | $X | | $X |
| TwntyHoops | $X | $X | $X | | $X |
| **Total Revenue** | **$X** | **$X** | **$X** | | **$X** |
| | | | | | |
| EXPENSES | | | | | |
| Salaries & Benefits | $X | $X | $X | | $X |
| Contractors | $X | $X | $X | | $X |
| Cloud Infrastructure | $X | $X | $X | | $X |
| AI API Costs | $X | $X | $X | | $X |
| Marketing | $X | $X | $X | | $X |
| Software & Tools | $X | $X | $X | | $X |
| Legal & Accounting | $X | $X | $X | | $X |
| Insurance | $X | $X | $X | | $X |
| Other | $X | $X | $X | | $X |
| **Total Expenses** | **$X** | **$X** | **$X** | | **$X** |
| | | | | | |
| **Net Cash Flow** | **$X** | **$X** | **$X** | | **$X** |
| **Ending Balance** | **$X** | **$X** | **$X** | | **$X** |
| **Runway (months)** | **X** | **X** | **X** | | **X** |

STATUS FLAGS:
  Runway > 12 months:   HEALTHY — focus on growth
  Runway 9-12 months:   MONITOR — begin fundraise prep
  Runway 6-9 months:    DANGER — actively fundraise, prepare Tier 1-2 cuts
  Runway 3-6 months:    CRITICAL — execute cuts NOW, emergency fundraise
  Runway < 3 months:    EXISTENTIAL — Tier 3 cuts, bridge financing, or wind-down planning

ASSUMPTIONS (document every assumption — this is what investors will challenge):
  - Revenue growth rate per product: [X]% MoM
  - Hiring plan: [X] new hires in months [X-X]
  - Infrastructure cost growth: [X]% per quarter
  - Marketing spend: $[X]/month (constant / growing / seasonal)
  - One-time costs: [list any expected one-time expenses]
  - Fundraise timing: $[X] expected in month [X] (model with AND without this)
```

## Step 9: Decision Framework

```
USE THIS FRAMEWORK WHEN RUNWAY IS TIGHTENING

RAISE CAPITAL IF:
  ✅ Runway < 9 months AND growth rate justifies investor confidence
  ✅ You have product-market fit signals (retention, NPS, revenue growth)
  ✅ The raise will fund a clear milestone (not just "more time")
  ✅ Market conditions support fundraising (check recent comparable rounds)
  Rule: start the process at 9 months runway. It takes 3-6 months to close.

CUT COSTS IF:
  ✅ Runway < 6 months AND no raise is imminent
  ✅ Growth has stalled and spending isn't driving improvement
  ✅ You can cut without destroying the product that's working
  Rule: cut once, cut deep. Multiple small cuts destroy morale worse than one decisive action.

DOUBLE DOWN IF:
  ✅ A product is at an inflection point (growth accelerating, retention improving)
  ✅ Unit economics are healthy (LTV:CAC > 3:1, gross margin > 60%)
  ✅ Increased investment has a clear causal link to faster growth
  ✅ You have runway to absorb the increased burn (> 12 months after increase)
  Rule: only double down on one product at a time. Spreading capital across five bets dilutes all of them.

SUNSET A PRODUCT IF:
  ✅ Product has been live > 6 months with no path to sustainability within 2 quarters
  ✅ Retention is poor (<20% month-1 retention) and not improving
  ✅ The team's time would create more value on another product
  ✅ Customers can be migrated or wound down gracefully
  Rule: sunsetting is not failure — it's capital allocation discipline.
  Rule: communicate the decision to the team with honesty and a clear plan for redeployment.

PORTFOLIO PRIORITIZATION (for multi-product studios)
  Rank products quarterly on:
    1. Revenue trajectory (growing, flat, declining)
    2. Unit economics (healthy, break-even, negative)
    3. Market opportunity (large and growing, niche, shrinking)
    4. Team strength (A-team, adequate, struggling)
    5. Strategic value (core to studio thesis, adjacent, experiment)

  Allocate capital proportionally. The product with the best combination gets the most resources.
  Never split resources equally across products — that guarantees mediocrity everywhere.
```

## Artifact Generation (Required)

Generate using Write:
1. **Burn report**: `docs/burn-rate-report.md` — current month analysis with scenarios
2. **Cash flow projection**: `docs/cash-flow.md` — 18-month runway projection
3. **Budget alerts config**: `monitoring/budget-alerts.json` — alert thresholds for cloud spend

## Step 10: Output

```
BURN RATE ANALYSIS — [COMPANY/PORTFOLIO]
Date: [TODAY]
Period: [MONTH/QUARTER/YEAR]

SUMMARY
┌──────────────────────────┬────────────────────────────────────┐
│ Field                    │ Value                              │
├──────────────────────────┼────────────────────────────────────┤
│ Cash Balance             │ $[X]                               │
│ Monthly Gross Burn       │ $[X]                               │
│ Monthly Revenue          │ $[X]                               │
│ Monthly Net Burn         │ $[X]                               │
│ Runway (base case)       │ [X] months                         │
│ Runway (conservative)    │ [X] months                         │
│ Burn Rate Trend          │ [Increasing / Stable / Decreasing] │
│ Break-Even Target        │ $[X] MRR                           │
│ Months to Break-Even     │ [X] months (base case)             │
│ Status                   │ [HEALTHY / MONITOR / DANGER / CRITICAL] │
└──────────────────────────┴────────────────────────────────────┘

DELIVERABLES GENERATED:
  - [ ] Per-product burn rate breakdown with allocation
  - [ ] Four-scenario runway projection (conservative, base, optimistic, zero-revenue)
  - [ ] 12-month cash flow projection
  - [ ] Break-even analysis per product and portfolio
  - [ ] Sensitivity analysis (what moves break-even most)
  - [ ] Cost reduction playbook (Tier 1/2/3 with estimated savings)
  - [ ] Decision framework recommendation (raise / cut / double down / sunset)

RECOMMENDED ACTION:
  [Based on runway and growth trajectory, recommend the primary action]

RELATED SKILLS:
  - /saas-financial-model — unit economics and pricing model per product
  - /engineering-cost-model — infrastructure cost breakdown
  - /finops — cloud cost optimization (Tier 1-2 cost reductions)
  - /fundraising-materials — if the recommendation is to raise capital
  - /portfolio-registry — portfolio-level product tracking
```
