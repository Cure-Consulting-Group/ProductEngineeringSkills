# SaaS Financial Model

> **Advisory skill — writes reports only.** It may write the model files listed under Artifact
> Generation when the user wants them; it never edits billing configuration, price IDs, or
> source data. `allowed-tools` only pre-approves tools and other runtimes ignore it, so this
> paragraph is the guardrail in every runtime.

**Outcome:** unit economics (margin-adjusted LTV, CAC, LTV:CAC, payback) and, when asked, a
12-month MRR projection or tier recommendation, each with its assumptions listed.
**Done when** every metric shows its inputs and every benchmark comparison cites a dated source.
Match length to the need; no filler sections or restated summaries.

## Pre-Processing (Auto-Context)

Context — run these read-only commands first; skip any that fail or aren't permitted (they only tailor the output):

- Portfolio: `sed -n '1,40p' PORTFOLIO.md 2>/dev/null || echo "(no PORTFOLIO.md)"`

Take the product's revenue model and stage from PORTFOLIO.md; ask if it is absent.

## Step 1: Classify

| Need | Output |
|------|--------|
| Unit economics | LTV, CAC, LTV:CAC, payback, gross margin |
| Revenue projection | Month-by-month customers and MRR with cost lines |
| Pricing / tiers | Tier structure, value metric, margin per tier |
| Plan comparison | Free vs freemium vs paid-only, modeled side by side |
| Break-even | Customers needed to cover fixed costs |

Runway, raise timing, and cut decisions go to `burn-rate-tracker`, which owns the runway
thresholds. Don't restate them here.

## Step 2: Gather Context

Pricing and billing cadence; paying customers and MRR; monthly logo churn; sales and marketing
spend and new customers (for CAC); variable cost per customer (infra, AI tokens, payment fees,
support) for gross margin. Mark each input actual vs. assumed.

## Step 3: Cure conventions and gotchas

- **Margin-adjusted is the default.** LTV = ARPU × gross margin ÷ monthly churn. Payback =
  CAC ÷ (ARPU × gross margin). Revenue-only LTV overstates value and understates payback;
  show it only alongside the margin-adjusted figure, labeled.
- **Churn cap for LTV:** if monthly churn is under 1%, cap lifetime at 60 months (common practice); otherwise one
  small churn number produces an absurd LTV.
- **CAC is fully loaded:** ads, content, sales salaries and tools, divided by new *paying*
  customers in the same period (not signups).
- **AI features change gross margin.** Put per-customer token cost in COGS; a product with
  heavy LLM usage rarely hits 70%+ margin without caching and model routing (`finops`).
- Healthy bars Cure uses: LTV:CAC ≥ 3:1, payback ≤ 12 months, gross margin ≥ 70%
  (≥ 60% for AI-heavy products), NRR ≥ 100%.
- Break-even customers = fixed costs ÷ (ARPU − variable cost per customer).

Compute with the bundled script rather than by hand:

```bash
cure-unit-economics --mrr 50000 --customers 200 --churn-rate 0.03 --cac 800 \
  --gross-margin 0.75 --json
```

`cure-unit-economics` is on PATH while the plugin is enabled; otherwise run
`python3 <plugin-root>/skills/business/saas-financial-model/scripts/unit_economics.py` with the
same flags. It reports both revenue and margin-adjusted LTV and margin-adjusted payback
(default gross margin 0.75 — always pass the real one).

## Step 4: Revenue projection

Monthly: starting customers + new − churned = ending; MRR = ending × ARPU; add expansion and
contraction when the product has seat or usage pricing. Costs = fixed + variable × customers +
new customers × CAC. Show cumulative P&L so the break-even month is visible.

## Step 5: Pricing tiers (this skill owns tier structure)

- At most three paid tiers plus an optional free tier; enterprise is "contact us," annual only.
- Annual discount 15–20% (two months free is the common framing).
- A free tier only with a product-led motion and a named upgrade trigger.
- The value metric must scale with customer success and be forecastable by the customer.
- Tier **names** come from the product's pricing page or PORTFOLIO.md; don't invent them.
  Launch messaging for the tiers belongs to `go-to-market`.
- Show margin per tier; AI-heavy features belong in the upper tiers.

## Step 6: Benchmarks

Search the web for current SaaS benchmarks by stage and segment (for example "SaaS median CAC
payback by segment", "net revenue retention benchmarks", "Rule of 40 by stage"). Use named,
dated sources (e.g. the KeyBanc/Sapphire SaaS survey, ICONIQ, SaaS Capital) and cite the year. Treat any undated benchmark table, including one in this
library, as unreliable.

## Artifact Generation

Applies when the user asks for a model document. Otherwise answer inline.

1. `docs/financial-model.md` — assumptions, unit economics, 12-month projection, break-even
2. `docs/pricing-analysis.md` — only for a pricing request
3. `docs/unit-economics.md` — only when asked separately, with a sensitivity table on churn and CAC

## Output

```
FINANCIAL MODEL — [PRODUCT] — [DATE]
Inputs: ARPU $X | churn X%/mo | CAC $X | gross margin X% (actual/assumed per line)
LTV (margin-adj.) $X | LTV:CAC X:1 | payback X mo | break-even X customers (month X)
Benchmark: [metric] vs [source, year] → [above/below]
Risks: [the two assumptions that move the answer most]
Recommendation: [pricing / growth / cost]
```
