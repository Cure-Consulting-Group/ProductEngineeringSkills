---
name: market-research
description: "Sourced market research: TAM/SAM/SOM, competitors, ICP, pricing, go/no-go. Use when sizing a market, profiling competitors or buyers, or deciding whether to enter."
when_to_use: "NOT for launch planning (go-to-market), messaging (product-marketing), or tracking competitor features (competitive-intel agent)."
argument-hint: "[market-or-product]"
allowed-tools: ["Read", "Grep", "Glob", "WebSearch", "WebFetch"]
---

# Market Research

> **RESEARCH-ONLY SKILL.** The only files this skill writes are its own report
> files under `docs/` (Step 5), and only when a written report is requested. It
> does not edit code, run mutating commands, or create or delete resources.
> Nothing in the frontmatter enforces this in any runtime (`allowed-tools` only
> pre-approves tools), so this paragraph is the guardrail.

**Outcome:** a sourced, founder-level research report that supports one named decision and ends in
Enter / Enter with conditions / Do not enter. Done when every number has a source and date (or is
labeled an assumption) and each section states its "so what". Match length to the decision; no filler
sections or restated summaries.

## Pre-Processing (Auto-Context)

Context (pre-filled in Claude Code; in other runtimes run these commands first):

- Portfolio products: !`grep -m6 -E '^#{2,3} ' PORTFOLIO.md 2>/dev/null || echo "(no PORTFOLIO.md)"`

Read the matching PORTFOLIO.md section when the research is for an existing portfolio product.

## Step 1: Classify

| Request | Deliver |
|---|---|
| Market entry / new venture | Full report (all Step 4 sections) |
| Sizing only | Sections 1, 3, 10 |
| Competitive scan | Sections 1, 4, 8 |
| ICP / pricing | Sections 1, 5, 6, 10 |
| Quick question | A sourced answer in chat, no document |

## Step 2: Gather Context

Confirm the market, the product or venture, the decision being made, and the geography. Ask only if
the decision is unclear — everything else can be stated as an assumption.

## Step 3: Research

Search the web for current sources and date every one; if no web tool is available, say so and label
figures as recalled and unverified. Queries, with "current year" meaning the actual year at run time:

1. Size: "[industry] market size [current year]", "[industry] CAGR forecast"
2. Competitors: "[competitor] pricing", "[competitor] funding", "[competitor] reviews" (app stores, G2)
3. Trends: "[industry] trends [current year]"
4. ICP: "[role] budget for [category]", job postings as an investment signal
5. Regulation: "[industry] regulation [country]"

Rules: prefer bottom-up sizing (customers × ARPU) and show both when they disagree by >2×; cite
analyst-report TAMs as ranges, not point estimates; verify competitor pricing on the pricing page
itself; no generic claims ("the market is large" → "\$4.2B in 2024, 18% CAGR (source, date)").

## Step 4: Report Sections

```
MARKET-[NNN]: [Market] — Research Report
Date · Prepared for · Decision · Confidence (H/M/L) · Recommendation
```

1. **Executive summary** — size, key dynamic, our angle, recommendation (3–5 sentences).
2. **Market definition** — stage, geography, tailwinds, headwinds.
3. **Sizing** — TAM / SAM / SOM table with method and source; Year-1 revenue target = N customers × ARPU.
4. **Competitors** — direct table (funding, users/ARR, pricing, strength, weakness), substitutes, feature grid, our differentiation in one sentence.
5. **ICP** — segment, pain, current solution, trigger event, willingness to pay, where they gather, decision maker.
6. **Pricing** — market price points, models in use, our recommendation.
7. **Channels** — channel fit with CAC estimates (hand launch detail to go-to-market).
8. **Moats** — network effects, switching costs, proprietary data, regulatory barrier, tech lead.
9. **Risks** — likelihood, impact, mitigation.
10. **Assumptions to validate** — how and by when.
11. **Go / No-Go** — recommendation, conditions, next steps.

## Step 5: Artifact Generation

Applies when the user wants a written report (Step 1 not "quick question"). Write only the files the
classification needs: `docs/market-research.md` (the report), `docs/competitive-analysis.md` (the
grid, for competitive scans), `docs/icp.md` (for ICP work).
