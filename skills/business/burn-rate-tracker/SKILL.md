---
name: burn-rate-tracker
description: "Models burn, runway scenarios, break-even, and cash-flow projections. Use when asking how long cash lasts, when to raise or cut, or planning a studio or product budget."
when_to_use: "NOT for SaaS unit economics or pricing (use saas-financial-model), cloud-bill optimization (use finops), or investor-facing updates (use investor-reporting)."
argument-hint: "[product-or-portfolio]"
allowed-tools: ["Read", "Grep", "Glob", "WebSearch"]
metadata:
  verified: 2026-09-23
---

# Burn Rate Tracker

> **Advisory skill — writes reports only.** It may write the report files listed under
> Artifact Generation when the user wants a written report; it never edits financial source data
> (ledgers, bank exports, budgets owned by someone else) and never runs mutating commands.
> Nothing enforces this: `allowed-tools` only pre-approves tools, and Codex and Antigravity ignore
> it, so this paragraph is the guardrail in every runtime.

**Outcome:** a runway number per scenario, the month each status threshold is crossed, and one
recommended action (raise / cut / double down / sunset) with the assumptions that drive it.
**Done when** every scenario has a runway in months, every cost is attributed to a product or to
studio overhead, and the recommendation follows from the thresholds below. Match length to the
need; no filler sections or restated summaries.

This skill **owns the Cure runway thresholds.** investor-reporting, saas-financial-model, and
fundraising-materials link here instead of restating them.

## Pre-Processing (Auto-Context)

Context — run these read-only commands first; skip any that fail or aren't permitted (they only tailor the output):

- Portfolio: `sed -n '1,40p' PORTFOLIO.md 2>/dev/null || echo "(no PORTFOLIO.md)"`

Product names, stages, and revenue models come from PORTFOLIO.md (maintained by the
`portfolio-registry` skill). Don't hard-code a product list; if the file is absent, ask which
products are in scope.

## Step 1: Classify the Analysis

| Type | Output |
|------|--------|
| Single product burn | Burn, runway, break-even for one product |
| Portfolio burn | Studio-wide burn with shared-cost allocation |
| Runway scenario | Four-scenario projection (raise/cut timing) |
| Break-even | Revenue and customers needed per product and portfolio |
| Budget planning | Forward budget with targets per product |
| Cost reduction | Tiered cut plan with runway impact |

A question ("how much runway do we have?") gets the number and the status, not the full report.

## Step 2: Gather Context

Cash on hand (all accounts); monthly revenue per product (even if zero); fixed costs (people, rent,
insurance, legal/accounting, core software); variable costs (cloud, AI APIs, payment processing,
marketing, contractors); headcount per product and shared roles; changes in the last 90 days; any
active raise or bridge and its expected close. Label every figure actual vs. estimate.

## Step 3: Allocation — Cure conventions

- Every cost lands in exactly one bucket: **product-specific**, **shared** (benefits several
  products), or **studio overhead** (benefits the entity).
- Allocate shared costs by **headcount ratio** for an early-stage portfolio (people are most of the
  cost). Switch to revenue ratio only for products with material revenue. Equal split is almost
  never right. Pick one method per report and state it.
- Never let allocation hide a product's true burn: show direct and allocated costs as separate
  columns.
- Red flag: net burn up 3 months running without matching revenue growth.

## Step 4: Scenarios — always four

| Scenario | Revenue | Costs | Purpose |
|---|---|---|---|
| Conservative | Flat | +5%/quarter | Plan to this |
| Base | Current MoM growth | Current run rate | Budget to this |
| Optimistic | ~2× current growth | Stable | Don't count on it |
| Zero revenue | \$0 | Current (pre-cut) | Survival floor |

Project month-by-month for 12 months (18 months when the output feeds a raise). Model any
expected raise **with and without** the money. Use the bundled script for the arithmetic:

```bash
cure-runway --cash 1500000 --monthly-burn 120000 --monthly-revenue 30000 \
  --revenue-growth 0.10 --burn-growth 0.02 --json
```

`cure-runway` is on PATH while the plugin is enabled; otherwise run
`python3 <plugin-root>/skills/business/burn-rate-tracker/scripts/runway_calculator.py` with the
same flags (`--help` lists them). Stdlib only.

## Step 5: Runway thresholds (canonical)

| Runway | Status | Action |
|---|---|---|
| > 12 months | HEALTHY | Focus on growth |
| 9–12 months | MONITOR | Prepare the raise: data room, metrics, target list |
| 6–9 months | DANGER | **Start the raise now** (closes take 3–6 months); prepare Tier 1–2 cuts |
| 3–6 months | CRITICAL | Execute cuts now; raise only in parallel |
| < 3 months | EXISTENTIAL | Tier 3 cuts, bridge financing, or wind-down planning |

Status is judged on the **conservative** scenario, not base. Flag the month each scenario crosses
6 and 3 months, and the month cash flow turns positive.

## Step 6: Break-even

Per product: break-even revenue = direct + allocated shared + allocated overhead; break-even
customers = that ÷ ARPU (take ARPU from saas-financial-model when it exists). Portfolio break-even
is total cost vs. total revenue. If no scenario reaches break-even before cash runs out, the
answer is raise or cut; there is no third option.

Sensitivity: show which single change moves break-even most (one hire, one product sunset, AI API
cost, revenue acceleration). Headcount is almost always the largest lever.

## Step 7: Cost reduction tiers

- **Tier 1, this week:** cancel unused SaaS, shrink dev/staging, delete idle cloud resources,
  annual billing, route simple AI calls to a cheaper model tier (hand the detail to `finops`).
- **Tier 2, this month:** AI response caching, right-size functions, cut marketing to the
  highest-ROI channels, renegotiate vendors.
- **Tier 3, only at CRITICAL or worse:** pause hiring, sunset a product, reduce founder comp,
  headcount reduction (last resort).

Estimate savings from the user's actual line items, not generic ranges. **Never cut:** security
and compliance tooling, core product quality, support response time, D&O and counsel, backups.
The cost of a breach or data loss dwarfs any of these line items.

## Step 8: Decision framework

- **Raise** when the conservative scenario is at or below 9 months, there are PMF signals, and
  the money funds a named milestone rather than "more time."
- **Cut** when runway is under 6 months with no term sheet, or growth has stalled despite
  spend. Cut once, cut deep; repeated small cuts cost more morale than one decisive one.
- **Double down** on one product at a time: growth accelerating, LTV:CAC > 3:1, gross margin
  > 60%, and runway still > 12 months after the increase.
- **Sunset** a product live > 6 months with no path to sustainability within 2 quarters, or
  month-1 retention < 20% and not improving. It is capital allocation, not failure.
- Rank products quarterly (revenue trajectory, unit economics, market, team, strategic fit) and
  allocate capital by rank. Never split equally.

## Artifact Generation

Applies when the user wants a written report, or in Recurring Mode. Otherwise answer inline.

1. `docs/burn-rate-report.md` — current month, four scenarios, status, recommendation
2. `docs/cash-flow.md` — month-by-month projection (12 months; 18 when feeding a raise)
3. `monitoring/budget-alerts.json` — only if asked; cloud-spend thresholds come from `finops`

## Output

```
BURN RATE ANALYSIS — [PRODUCT/PORTFOLIO] — [DATE]
Cash [$X] | Gross burn [$X]/mo | Revenue [$X]/mo | Net burn [$X]/mo
Runway: conservative [X] mo | base [X] | optimistic [X] | zero-revenue [X]
Status (conservative): [HEALTHY / MONITOR / DANGER / CRITICAL / EXISTENTIAL]
Break-even: [$X] MRR, month [X] (base)
Recommended action: [raise / cut / double down / sunset] — [one-line why]
Key assumptions: [growth %, hiring plan, one-time costs, raise timing]
```

Related: `saas-financial-model` (unit economics), `finops` (cloud cuts), `investor-reporting`
(board and investor communication), `fundraising-materials` (if the answer is raise).

## Recurring Mode

This is a recurring goal, not a one-shot (mechanism trade-offs: `/engagement-automation`).

- **Cadence:** weekly
- **Session loop:** none — session loops expire after 7 days, so a weekly cadence never fires in-session; it belongs in the cloud routine below.
- **Unattended:** cloud routine — Weekly burn/runway refresh from the latest actuals; alert if runway crosses a scenario threshold. Recipes: docs/AUTOMATION.md in the plugin repo.
- **Budget:** ~60k tokens/run; cap at one run per weekly period.
- **Guardrails:** writes only the runway summary appended to the finance report (advisory — recurring-mode doctrine per AUTOMATION.md, not harness-enforced); no other file changes; report on failure rather than retrying.
