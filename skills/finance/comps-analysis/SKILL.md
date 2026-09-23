---
name: comps-analysis
description: "Values a company against trading peers with EV/Revenue, EV/EBITDA, and P/E multiples. Use when benchmarking valuation multiples or pricing a company off public comparables."
when_to_use: "NOT for intrinsic value (use dcf-modeling), M&A accretion (use merger-modeling), or startup rounds and SAFEs (use investor-reporting)."
argument-hint: "[company-or-sector]"
---

# Comparable Company Analysis (Comps)

**Outcome:** an implied valuation range (25th / median / 75th percentile) for the target from a
defensible peer set, with every input sourced and dated. **Done when** the peer table can be
recomputed from the cited sources, exclusions are explained, and the target's premium or discount
is argued, not asserted. Not investment advice. Match length to the need; no filler sections or
restated summaries.

For a full banking workflow (comps + DCF + LBO together), the `investment-banker` agent runs this
skill alongside `dcf-modeling` in Claude Code.

## Step 1: Classify

| Case | Primary multiple |
|---|---|
| Profitable, mature | EV/EBITDA (NTM and LTM), P/E |
| High-growth or unprofitable | EV/NTM revenue; growth-adjusted (EV/Rev ÷ growth) as a cross-check |
| Pre-revenue or private (typical Cure portfolio case) | Recent private rounds in the same stage and sector, then EV/NTM revenue of the nearest public peers with an explicit private-company discount — state the discount and why |

## Step 2: Gather

Peers similar on business model first, then growth, margin, size, geography (4–10 names). For each:
price and date, diluted shares, debt, preferred, minority interest, cash, and LTM/NTM revenue,
EBITDA, EPS. Sources: SEC EDGAR filings (10-K/10-Q) for balance-sheet items, a named market-data
source with timestamp for price and consensus. Search the web for current figures; never reuse
numbers from memory.

## Step 3: Gotchas that change the answer

- **One as-of date** for every price; state it in the table header.
- **Calendarize** fiscal years to a common period before comparing NTM/LTM.
- **EV** = diluted equity value (treasury stock method) + debt + preferred + minority − cash.
- **SBC:** pick one treatment for "adjusted EBITDA" across all peers (Cure default: SBC is an
  expense, not added back) and say so.
- **Leases:** IFRS 16 peers report higher EBITDA than ASC 842 operating-lease peers; adjust or
  don't mix without a note.
- Negative earnings → "NM", never a negative multiple. Exclude outliers by a stated rule
  (e.g. outside 1.5× IQR), listing what was dropped.

## Output

```markdown
## Comparable Company Analysis: [Target] — prices as of [date]
| Company | Rev LTM | Rev growth NTM | EBITDA margin | EV/Rev NTM | EV/EBITDA NTM | P/E NTM | Source |
|---|---|---|---|---|---|---|---|
| **25th / Median / 75th** | | | | | | | |
Excluded: [name — reason]
Implied value (EV → equity): low $[X] / mid $[X] / high $[X]
Premium/discount argument: [growth, margin, scale, risk — with numbers]
```
