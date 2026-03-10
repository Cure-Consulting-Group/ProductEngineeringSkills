---
name: saas-financial-model
description: "Model unit economics, MRR/ARR projections, pricing tiers, runway, and break-even analysis"
argument-hint: "[product-name]"
allowed-tools: ["Read", "Grep", "Glob", "WebSearch"]
---

# SaaS Financial Model

Unit economics, revenue modeling, and financial projections for SaaS and subscription businesses. Make pricing decisions with math, not vibes.

## Step 1: Classify the Financial Need

| Need | Output |
|------|--------|
| Unit economics | CAC, LTV, payback period, margins |
| Revenue model | MRR/ARR projections with assumptions |
| Pricing analysis | Tier comparison, willingness-to-pay, margin impact |
| Fundraising model | 12-24 month projection, burn rate, runway |
| Break-even analysis | When does this product cover its costs? |
| Plan comparison | Free vs freemium vs paid — which model wins? |

## Step 2: Gather Context

1. **Product** — what SaaS/subscription product?
2. **Pricing** — current tiers, prices, billing (monthly/annual)?
3. **Current metrics** — users, paying customers, MRR (if exists)?
4. **Acquisition** — how do customers find you? Cost per channel?
5. **Churn** — current monthly churn rate (if known)?
6. **Team cost** — monthly burn (salaries, infra, services)?

## Step 3: Core SaaS Metrics

```
MRR (Monthly Recurring Revenue):
  = sum of all active subscriptions per month
  Components: New MRR + Expansion MRR - Churned MRR - Contraction MRR

ARR (Annual Recurring Revenue):
  = MRR × 12

ARPU (Average Revenue Per User):
  = MRR / total paying customers

CAC (Customer Acquisition Cost):
  = total sales & marketing spend / new customers acquired
  Include: ads, content, sales salaries, tools

LTV (Lifetime Value):
  = ARPU / monthly churn rate
  Alternative: ARPU × average customer lifespan (months)

LTV:CAC Ratio:
  Target: > 3:1 (healthy)
  Warning: < 3:1 (spending too much to acquire)
  Danger:  < 1:1 (losing money on every customer)

Payback Period:
  = CAC / ARPU (in months)
  Target: < 12 months

Monthly Churn Rate:
  = customers lost this month / customers at start of month
  Target: < 5% for SMB, < 2% for mid-market, < 1% for enterprise

Net Revenue Retention (NRR):
  = (Starting MRR + Expansion - Contraction - Churn) / Starting MRR
  Target: > 100% (expansion revenue exceeds churn)
  Best-in-class: > 120%
```

## Step 4: Revenue Projection Model

```
Month-by-month model:

Starting Customers  = previous month ending customers
New Customers       = marketing leads × conversion rate
Churned Customers   = starting customers × churn rate
Ending Customers    = starting + new - churned

MRR                 = ending customers × ARPU
New MRR             = new customers × ARPU
Churned MRR         = churned customers × ARPU
Net New MRR         = new MRR - churned MRR

Costs:
  Infrastructure    = base + (per-user cost × customers)
  Team              = salaries + benefits + contractors
  Marketing         = new customers × CAC
  Tools/Services    = fixed monthly costs

Profit/Loss         = MRR - total costs
Cumulative P&L      = running total (shows path to profitability)
```

## Step 5: Pricing Tier Analysis

```
Pricing framework:

| Tier | Monthly | Annual (discount) | Target Segment | Margin |
|------|---------|-------------------|----------------|--------|
| Free | $0 | - | Lead generation, product-led growth | Negative |
| Starter | $X | $X×10 (17% off) | Solo/small teams, price-sensitive | 60%+ |
| Pro | $Y | $Y×10 (17% off) | Growing teams, power users | 70%+ |
| Enterprise | Custom | Annual only | Large orgs, compliance needs | 80%+ |

Pricing rules:
  - 3 paid tiers maximum (paradox of choice)
  - 10x value gap between cheapest and most expensive
  - Annual discount: 15-20% (improves cash flow + retention)
  - Free tier: only if product-led growth model, with clear upgrade trigger
  - Enterprise: always custom/contact-us (higher deal size)
```

### Value Metric Selection
```
The value metric is what you charge based on. It should:
  ✅ Scale with the customer's success (they pay more as they get more value)
  ✅ Be easy to understand (no complex formulas)
  ✅ Be predictable (customer can forecast their bill)

Common value metrics:
  - Per seat/user (Slack, Notion)
  - Per usage/volume (Stripe, Twilio)
  - Per feature tier (most SaaS)
  - Flat rate (Basecamp)

Best for small business clients: feature-based tiers with clear upgrade triggers
```

## Step 6: Break-Even Analysis

```
Fixed costs (don't change with customers):
  Team salaries, office, tools, base infrastructure

Variable costs (scale with customers):
  Per-user infrastructure, support time, payment processing fees

Gross margin:
  = (Revenue - Variable Costs) / Revenue
  Target: > 70% for SaaS

Break-even point:
  = Fixed Costs / (ARPU - Variable Cost Per Customer)
  = number of customers needed to cover all costs

Example:
  Fixed costs:     $15,000/month (team + tools)
  ARPU:            $49/month
  Variable cost:   $5/customer/month (infra + Stripe fees)
  Break-even:      $15,000 / ($49 - $5) = 341 customers
```

## Step 7: Runway Calculation

```
Cash runway (months):
  = Cash in bank / Monthly burn rate

Monthly burn rate:
  = Total monthly expenses - Total monthly revenue

Example:
  Cash: $200,000
  Monthly expenses: $25,000
  Monthly revenue: $8,000
  Burn rate: $17,000
  Runway: 11.8 months

Rules of thumb:
  - Raise when you have 6+ months runway remaining
  - Default alive: revenue growing fast enough to cover costs before cash runs out
  - Default dead: burn rate exceeds growth trajectory
```

## Step 8: Financial Model Output

```
FINANCIAL MODEL — [PRODUCT NAME]
Date: [TODAY]
Projection Period: 12 months

ASSUMPTIONS
  Starting customers: X
  Monthly new customers: X (growing Y% month-over-month)
  Monthly churn rate: X%
  ARPU: $X
  CAC: $X
  Monthly fixed costs: $X
  Variable cost per customer: $X

UNIT ECONOMICS
  LTV: $X
  LTV:CAC: X:1
  Payback period: X months
  Gross margin: X%

12-MONTH PROJECTION
| Month | Customers | MRR | Costs | Net | Cumulative |
|-------|-----------|-----|-------|-----|------------|
| 1     | ...       | ... | ...   | ... | ...        |
| ...   |           |     |       |     |            |
| 12    | ...       | ... | ...   | ... | ...        |

BREAK-EVEN
  Customers needed: X
  Projected month: Month X

KEY RISKS
  - [Risk 1] — [Impact if realized]
  - [Risk 2] — [Impact if realized]

RECOMMENDATIONS
  - [Pricing/growth/cost recommendation]
```

## Step 9: SaaS Benchmarks

```
For comparison against industry norms:

| Metric | Seed | Series A | Series B+ |
|--------|------|----------|-----------|
| MRR | $10-50K | $100-500K | $1M+ |
| Growth (MoM) | 15-20% | 10-15% | 5-10% |
| Churn (monthly) | 5-7% | 3-5% | 1-3% |
| LTV:CAC | 2-3x | 3-5x | 5x+ |
| Gross Margin | 60-70% | 70-80% | 80%+ |
| NRR | 90-100% | 100-110% | 110-130% |
| Payback (months) | 12-18 | 8-12 | 3-8 |
```
