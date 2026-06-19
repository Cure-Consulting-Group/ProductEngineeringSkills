# Equity Research Analysis

This skill provides a structured workflow for analyzing public companies, interpreting market sentiment, and developing investment recommendations.

## Workflow

### 1. Document Parsing & Signal Extraction
- **SEC Filings**: Identify key risks in Item 1A, read MD&A for segment performance, and check footnotes for contingent liabilities.
- **Earnings Transcripts**: Extract guidance, management tone, and key Q&A themes (e.g., pricing power, supply chain).
- **Press Releases**: Analyze headline metrics vs. underlying performance (organic vs. inorganic).

### 2. Catalyst Tracking
Map upcoming events that could move the stock:
- Earnings release dates
- Product launches
- Regulatory decisions (e.g., FDA, FTC)
- Investor days / Conferences
- Macroeconomic prints (CPI, Jobs)

### 3. Consensus Comparison
- Compare management guidance with sell-side analyst expectations.
- Identify "whisper numbers" or areas of potential surprise/disappointment.

### 4. Investment Thesis Development
Synthesize findings into a "Buy/Hold/Sell" framework:
- **Core Thesis**: Why should someone own this stock?
- **Key Pillars**: 3-5 drivers (e.g., market leadership, margin expansion).
- **Risks**: What could break the thesis?
- **Valuation**: Is the stock "cheap" or "expensive" relative to the quality of the business?

## Standard Output Format

```markdown
## Equity Research: [Company Ticker]

### Quick Take: [Recommendation]
**Target Price**: $[X] | **Current Price**: $[X] | **Upside**: [X]%

### Thesis Pillars
1. **[Pillar 1]**: [Evidence from filings/transcripts]
2. **[Pillar 2]**: [Evidence from filings/transcripts]
3. **[Pillar 3]**: [Evidence from filings/transcripts]

### Earnings Digest ([Quarter])
- **Revenue**: $[X] (Beat/Miss by [X]%)
- **EPS**: $[X] (Beat/Miss by [X]%)
- **Guidance**: [Revised Up/Down/Maintained]
- **Key Quote**: "[Management quote from transcript]"

### Catalyst Calendar
| Date | Event | Expected Impact |
|------|-------|-----------------|
| [Date] | [Event] | [High/Med/Low] |

### Risks to Thesis
- [Risk 1]
- [Risk 2]
```

## Quality Standards
- **Objectivity**: Present balanced "Bull Case" and "Bear Case".
- **Source Integrity**: Always cite specific page numbers or transcript timestamps.
- **Data over Sentiment**: Prioritize hard metrics (margins, cash flow) over qualitative management statements.
