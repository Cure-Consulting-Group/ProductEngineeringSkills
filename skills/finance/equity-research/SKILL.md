---
name: equity-research
description: "Analyzes a public company from 10-K/10-Q filings and earnings calls into a thesis and catalysts. Use when digesting earnings, reading SEC filings, or drafting a buy/hold/sell view."
when_to_use: "NOT for building the valuation model itself (use dcf-modeling or comps-analysis) or private-company diligence."
argument-hint: "[company-or-ticker]"
---

# Equity Research Analysis

**Outcome:** a thesis note — recommendation, target price with method, 3–5 evidence-backed
pillars, a bull and bear case, catalyst calendar, and risks. **Done when** every claim cites a
filing section and page or a transcript timestamp, the price is dated, and the target price
traces to a valuation from `dcf-modeling` or `comps-analysis`. Not investment advice. Match length
to the need; no filler sections or restated summaries.

In Claude Code the `equity-analyst` agent runs this workflow end to end.

## Step 1: Classify

Earnings digest (one quarter) · initiation (full thesis) · thesis update (what changed) ·
catalyst check (upcoming events only).

## Step 2: Gather

Latest 10-K and 10-Q from SEC EDGAR (Item 1A risk factors, MD&A, segment note, contingencies);
the latest earnings release and call transcript; guidance history; consensus from a named source
with date; current price with timestamp. Search the web for current documents; don't summarize
from memory.

## Step 3: Conventions and gotchas

- **Public information only.** If the user supplies anything that may be material non-public
  information, stop and say so — acting on it is illegal.
- Reconcile non-GAAP to GAAP before using it; say which one each number is.
- Separate organic from acquired growth and FX effects.
- Compare guidance to consensus and to management's own prior guidance (track record).
- Management tone is evidence only when tied to a number or a changed commitment.
- Present bull and bear cases with explicit assumptions; the recommendation follows from
  the probability-weighted view, not from tone.

## Output

```markdown
## Equity Research: [Ticker] — [Recommendation] — as of [date]
Target $[X] ([method, horizon]) | Price $[X] | Upside [X]%
Pillars: 1. [claim] — [evidence: filing §/page or transcript timestamp] …
Earnings digest: revenue / EPS vs consensus [source], guidance [up/down/maintained], key quote [timestamp]
Bull / Bear: [assumptions → value each]
Catalysts: | Date | Event | Impact |
Risks to thesis: [what would make us wrong, and the signal to watch]
```
