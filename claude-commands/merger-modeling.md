# Merger Modeling (Accretion/Dilution)

This skill provides a structured workflow for analyzing the financial impact of an acquisition on the acquirer's Earnings Per Share (EPS).

## Workflow

### 1. Acquisition Assumptions
Define the deal terms:
- **Purchase Price**: Per share and total transaction value.
- **Mix of Consideration**: % Cash, % Stock, % Debt.
- **Interest Rates**: On new debt and foregone interest on cash.
- **Stock Price**: Acquirer's current price (for share issuance).

### 2. Pro-forma Income Statement
Combine the financials:
- **Revenue**: Sum of Acquirer + Target (+ Revenue Synergies).
- **EBITDA**: Sum of Acquirer + Target (+ Cost Synergies).
- **Interest Expense**: Existing + New Debt Interest - Foregone Interest on Cash.
- **Depreciation & Amortization**: Including incremental D&A from asset write-ups.

### 3. Purchase Price Allocation (PPA)
Account for the premium paid:
- **Identified Intangibles**: Estimate value of brands, customer lists, technology.
- **Goodwill**: Excess of purchase price over fair value of net assets.
- **Deferred Tax Liability (DTL)**: Created from asset write-ups.

### 4. Accretion / Dilution Calculation
- **Pro-forma Net Income**: Consolidated income after tax and interest.
- **New Share Count**: Acquirer shares + New shares issued.
- **Pro-forma EPS**: Pro-forma Net Income / New Share Count.
- **% Accretion / (Dilution)**: (Pro-forma EPS / Standalone EPS) - 1.

### 5. Synergy Analysis
Calculate the "Breakeven Synergies": The amount of cost savings required to make the deal non-dilutive.

## Standard Output Format

```markdown
## M&A Analysis: [Acquirer] / [Target]

### Transaction Overview
- **Purchase Price**: $[X] ([X]x EBITDA)
- **Mix**: [X]% Cash / [X]% Stock / [X]% Debt
- **Synergies Identified**: $[X]

### Accretion / (Dilution) Results
| Metric | Standalone (Acquirer) | Pro-forma | % Change |
|--------|-----------------------|-----------|----------|
| EPS (Year 1) | $[X] | $[X] | [X]% |
| EPS (Year 2) | $[X] | $[X] | [X]% |

### Synergy Sensitivity
| Synergy Realization | 0% | 50% | 100% |
|---------------------|----|-----|------|
| Accretion / (Dilution) | [X]% | [X]% | [X]% |

### Strategic Commentary
- [Analysis of pro-forma leverage]
- [Risk assessment of synergy capture]
- [Impact on cost of capital]
```

## Quality Standards
- **Conservatism**: Model synergies on a "phased-in" basis (e.g., 25% Yr 1, 75% Yr 2).
- **Fully Diluted**: Use treasury stock method for share counts.
- **Detail**: Break out "Cash EPS" (excluding non-cash amortization) if appropriate.
