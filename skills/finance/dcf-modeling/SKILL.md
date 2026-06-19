---
name: dcf-modeling
description: Performs Discounted Cash Flow (DCF) valuation. Use when you need to calculate intrinsic value based on projected free cash flows, WACC, and terminal value.
argument-hint: "[company-or-ticker]"
---

# Discounted Cash Flow (DCF) Modeling

This skill provides a structured workflow for performing intrinsic valuation by projecting Free Cash Flows to the Firm (FCFF) and discounting them to the present value.

## Workflow

### 1. Forecast Period (typically 5-10 years)
Project the 3 core components:
- **Revenue**: Based on market growth, market share, and pricing.
- **EBITDA / EBIT**: Based on operating leverage and margin expansion/contraction.
- **Taxes**: Apply the marginal or effective tax rate.

### 2. Unlevered Free Cash Flow (UFCF) Calculation
Derived from NOPAT (Net Operating Profit After Tax):
- **(+) Depreciation & Amortization**
- **(-) Capital Expenditures (CapEx)**
- **(-) Change in Net Working Capital (NWC)**
- **= Unlevered Free Cash Flow**

### 3. WACC Calculation (Weighted Average Cost of Capital)
Determine the discount rate:
- **Cost of Equity**: Using CAPM (Risk-Free Rate + Beta * Equity Risk Premium).
- **Cost of Debt**: Pre-tax cost of debt * (1 - Tax Rate).
- **Weights**: Based on target capital structure (Market Value of Equity and Debt).

### 4. Terminal Value (TV)
Calculate value beyond the forecast period:
- **Gordon Growth Method**: UFCF_n * (1 + g) / (WACC - g).
- **Exit Multiple Method**: EBITDA_n * Peer Multiple.

### 5. Enterprise & Equity Value
- **Enterprise Value**: PV of Forecast UFCFs + PV of Terminal Value.
- **Equity Value**: Enterprise Value - Net Debt - Minority Interest + Cash.
- **Per Share Value**: Equity Value / Diluted Shares Outstanding.

## Standard Output Format

```markdown
## DCF Valuation: [Target Name]

### Free Cash Flow Forecast
| Year | 202X | 202X | 202X | 202X | 202X |
|------|------|------|------|------|------|
| UFCF | $[X] | $[X] | $[X] | $[X] | $[X] |
| PV   | $[X] | $[X] | $[X] | $[X] | $[X] |

### Valuation Assumptions
- **WACC**: [X]%
- **Terminal Growth (g)**: [X]%
- **Exit Multiple**: [X]x

### Implied Value
- **Enterprise Value**: $[Value]
- **Equity Value**: $[Value]
- **Implied Share Price**: $[Value]
- **Current Share Price**: $[Value]
- **Premium / (Discount)**: [X]%

### Sensitivity Analysis (Matrix)
| WACC \ g | [g-0.5%] | [g] | [g+0.5%] |
|----------|----------|-----|----------|
| [W+0.5%] | $[V]     | $[V]| $[V]     |
| [WACC]   | $[V]     | $[V]| $[V]     |
| [W-0.5%] | $[V]     | $[V]| $[V]     |
```

## Quality Standards
- **Reasonableness**: Check if terminal value is >75% of total enterprise value (flag if so).
- **Conservative Bias**: Use market-standard equity risk premiums.
- **Transparency**: Explicitly state the source for Beta (e.g., Bloomberg, Damodaran).
