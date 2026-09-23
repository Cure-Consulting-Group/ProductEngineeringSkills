---
name: dcf-modeling
description: "Builds a discounted cash flow valuation: unlevered FCF, WACC, terminal value, equity bridge. Use when estimating intrinsic value or a per-share price from projected cash flows."
when_to_use: "NOT for peer multiples (use comps-analysis) or pre-revenue startup rounds (use investor-reporting and fundraising-materials)."
argument-hint: "[company-or-ticker]"
---

# Discounted Cash Flow (DCF) Modeling

**Outcome:** enterprise value, equity value, and value per share, with a WACC × terminal-growth
sensitivity grid and every assumption sourced and dated. **Done when** the equity bridge
reconciles, the terminal value's share of EV is reported, and the Gordon and exit-multiple
methods have been cross-checked. Not investment advice. Match length to the need; no filler
sections or restated summaries.

In Claude Code the `investment-banker` agent pairs this with `comps-analysis`.

## Step 1: Classify

- **Operating company with positive or near-positive FCF:** full 5–10 year UFCF DCF.
- **Pre-revenue or early startup** (most Cure portfolio questions): a DCF is mostly terminal value
  and false precision. Say so, then value off recent rounds and comps; run a DCF only as a
  scenario check.

## Step 2: Gather

Historical financials from filings (SEC EDGAR for public companies); management or consensus
projections with source; current risk-free rate (10-year Treasury yield, dated), an equity risk
premium from a named, dated source (e.g. Damodaran's current estimate), beta source, pre-tax cost
of debt, target capital structure. Search the web for current values; never use remembered rates.

## Step 3: Gotchas that change the answer

- **Equity bridge:** Equity = EV − net debt − minority interest − preferred (+ non-operating
  assets not in the cash flows). Net debt = debt − cash, so never add cash back again.
- **Mid-year convention** for flows that arrive through the year; state whether it is used.
- **Normalize the terminal year:** capex consistent with growth (above D&A when growing), NWC
  growing with revenue, margin at steady state.
- **Terminal growth** at or below long-run nominal GDP / the risk-free rate; g ≥ WACC is an error.
- **Cross-check:** implied exit multiple from the Gordon value vs. peer multiples, and vice versa.
- **Flag terminal value > 75% of EV.**
- **SBC** is a real cost — treat it as cash or dilute the share count, not neither.
- Use target (not current) capital-structure weights to avoid WACC circularity.
- Per-share value uses diluted shares (treasury stock method).

## Output

```markdown
## DCF Valuation: [Target] — as of [date]
UFCF forecast table (years × revenue, EBIT, taxes, D&A, capex, ΔNWC, UFCF, PV)
WACC [X]% (rf [X]% [date], ERP [X]% [source], beta [X] [source]) | g [X]% | exit multiple [X]x
EV $[X] (TV = [X]% of EV) → equity $[X] → $[X]/share vs current $[X] ([X]% premium/discount)
Sensitivity: WACC ±0.5–1.0% × g ±0.5%
Gordon vs exit-multiple cross-check: [values, gap explained]
```
