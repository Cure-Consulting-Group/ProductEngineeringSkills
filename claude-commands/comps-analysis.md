# Comparable Company Analysis (Comps)

This skill provides a structured workflow for performing relative valuation by identifying peer groups and analyzing their trading multiples.

## Workflow

### 1. Peer Group Selection
Identify companies with similar:
- **Sector/Sub-industry**: Core business model and market.
- **Size**: Revenue, Enterprise Value, Market Cap.
- **Growth Profile**: Historical and projected revenue/EBITDA growth.
- **Profitability**: Gross, EBITDA, and Net margins.
- **Geography**: Primary markets and headquarters.

### 2. Data Gathering
For the target and each peer, extract:
- **Market Data**: Share price, shares outstanding, net debt.
- **Financial Metrics (LTM & Projected)**:
    - Revenue
    - EBITDA
    - EBIT
    - Net Income / EPS

### 3. Multiple Calculation
Calculate key valuation multiples:
- **EV / Revenue**: Standard for high-growth/unprofitable tech.
- **EV / EBITDA**: Most common for mature industrial/services.
- **P / E (Price / Earnings)**: Standard for mature companies with stable net income.
- **EV / FCF**: For capital-intensive vs. asset-light comparisons.

### 4. Benchmarking & Statistics
Calculate the peer group statistics:
- Mean and Median
- 25th and 75th Percentiles
- Min and Max

### 5. Valuation Output
Apply the median/mean multiples to the target's metrics to derive an implied valuation range.

## Standard Output Format

```markdown
## Comparable Company Analysis: [Target Name]

### Peer Group Overview
| Company | Revenue (LTM) | EBITDA Margin | EV / EBITDA (LTM) | EV / EBITDA (NFY) |
|---------|---------------|---------------|-------------------|-------------------|
| Peer 1  | $[X]          | [X]%          | [X]x              | [X]x              |
| Peer 2  | $[X]          | [X]%          | [X]x              | [X]x              |
| Peer 3  | $[X]          | [X]%          | [X]x              | [X]x              |
| **Median** | **$[X]**   | **[X]%**      | **[X]x**          | **[X]x**          |

### Implied Valuation Range
- **Low (25th Percentile)**: $[Value]
- **Mid (Median)**: $[Value]
- **High (75th Percentile)**: $[Value]

### Analysis & Commentary
- [Observation on multiple dispersion]
- [Context on target's premium/discount vs peers]
- [Growth vs Margin trade-off analysis]
```

## Quality Standards
- **Clean Architecture**: Separate data extraction logic from valuation calculations.
- **Transparency**: Always cite the source of multiples (e.g., "Trading price as of [Date]").
- **Consistency**: Use standardized definitions for adjusted EBITDA.
