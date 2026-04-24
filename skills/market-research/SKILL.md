---
name: market-research
version: "1.0.0"
description: "Conduct TAM/SAM/SOM analysis, competitive research, ICP definition, and pricing research"
when_to_use: "Use when conducting TAM/SAM/SOM analysis, competitive research, ICP definition, or pricing research."
argument-hint: "[market-or-product]"
allowed-tools: ["Read", "Grep", "Glob", "WebSearch", "WebFetch"]
---

# Market Research

## Pre-Processing (Auto-Context)

Before starting, gather project context silently:
- Read `PORTFOLIO.md` if it exists in the project root or parent directories for product/team context
- Run: `cat package.json 2>/dev/null || cat build.gradle.kts 2>/dev/null || cat Podfile 2>/dev/null` to detect stack
- Run: `git log --oneline -5 2>/dev/null` for recent changes
- Run: `ls src/ app/ lib/ functions/ 2>/dev/null` to understand project structure
- Use this context to tailor all output to the actual project

Structured market analysis optimized for fast, founder-level decisions. Signal-dense, no padding. Every section has a "so what" implication.

## Research Process

1. **Clarify** — confirm market, product, and decision being made
2. **Search** — use web search for current market data, funding rounds, competitor pricing
3. **Size** — TAM / SAM / SOM with sources
4. **Map competitors** — direct, indirect, and adjacent
5. **Define ICP** — who buys, why, willingness to pay
6. **Analyze pricing** — existing price points, model types, upgrade triggers
7. **Assess** — moats, risks, go/no-go signal

**Always web search** for: competitor pricing pages, recent funding rounds, market reports, company headcounts (LinkedIn), app store reviews (competitor pain points), job postings (proxy for investment areas), and recent news.

## Output Template

Generate a document with these sections:

### Header
```
MARKET-[NNN]: [Market / Opportunity Name] — Research Report
Date: [YYYY-MM-DD]
Prepared for: [Product/Venture Name]
Decision: [What decision does this research support?]
Confidence: High / Medium / Low
Recommendation: Enter | Enter with conditions | Do not enter
```

### 1. Executive Summary
3-5 sentences: market size, key dynamic, our angle, recommendation. Lead with the "so what."

### 2. Market Definition
Market, Stage (Emerging/Growing/Mature/Declining), Geography, Tailwinds, Headwinds.

### 3. Market Sizing
| Segment | Size | Methodology | Source |
|---------|------|-------------|--------|
| TAM | $XB | Top-down or Bottom-up | source + year |
| SAM | $XM | Geo + segment filter | derived |
| SOM | $XM | Realistic 3-yr capture | assumption |

Year 1 Revenue Target: $[X] — requires [N] customers at $[ARPU]

### 4. Competitive Landscape
- Direct competitors table (Company, Funding, Users/ARR, Pricing, Strength, Weakness)
- Indirect competitors / substitutes
- Competitive matrix (feature comparison grid)
- Our differentiation statement

### 5. Ideal Customer Profile (ICP)
Table: Segment, Who they are, Pain point, Current solution, Trigger event, Willingness to pay, Where they are, Decision maker?

### 6. Pricing Analysis
- Market price points table
- Pricing model types in market
- Our pricing recommendation with rationale

### 7. Go-to-Market Channels
Channel fit table with CAC estimates.

### 8. Moats & Defensibility
Evaluate: data network effects, switching costs, brand/trust, proprietary data, regulatory barrier, tech lead.

### 9. Risk Assessment
Risk table: Risk, Likelihood, Impact, Mitigation.

### 10. Key Assumptions to Validate
Assumption, How to Validate, Timeline.

### 11. Go / No-Go Signal
Recommendation with rationale, conditions (if conditional), and next steps.

## Structured Research Queries

When using WebSearch, run these specific queries in order:

1. **Market Size**: "[industry] market size 2025 2026 TAM" + "[industry] growth rate CAGR"
2. **Competitors**: "[competitor name] pricing" + "[competitor name] funding round" + "[competitor name] features"
3. **Trends**: "[industry] trends 2025 2026" + "[industry] disruption technology"
4. **ICP Data**: "[target role] salary survey" + "[target company size] spending on [category]"
5. **Regulatory**: "[industry] regulation [country]" + "[industry] compliance requirements"

Every claim in the output MUST include "(Source: [url/publication], [date])" citation.

## Artifact Generation (Required)

Generate using Write:
1. **Market brief**: `docs/market-research.md` — TAM/SAM/SOM with sources
2. **Competitive matrix**: `docs/competitive-analysis.md` — feature/pricing comparison table
3. **ICP profile**: `docs/icp.md` — detailed ideal customer profile

## Research Quality Standards

- Every market size number needs a source and year
- Every competitor pricing claim should be verified
- ICP willingness-to-pay grounded in evidence
- If data is unavailable, state the assumption explicitly and flag for validation
- No generic claims: "the market is large" → "$4.2B in 2024, growing at 18% CAGR (source)"
