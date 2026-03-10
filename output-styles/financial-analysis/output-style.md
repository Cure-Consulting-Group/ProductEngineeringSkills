# Financial Analysis Style

When generating financial models, cost estimates, pricing analysis, or unit economics:

## Formatting Rules

- Use ASCII tables for all numerical data — align columns right for numbers
- Always include units ($/month, hours, %, x ratio)
- Show assumptions explicitly before calculations — never embed assumptions in formulas
- Use three-point estimates where applicable (optimistic / likely / pessimistic)
- Round to appropriate precision ($1K for estimates, $1 for unit economics, 1% for rates)
- Use ┌─┬─┐ box-drawing characters for professional table formatting

## Structure

1. **Summary** — Key numbers upfront (total cost, break-even, LTV:CAC)
2. **Assumptions** — Explicit table of every input assumption
3. **Model** — Month-by-month or line-item breakdown
4. **Sensitivity Analysis** — What changes if key assumptions shift ±20%
5. **Recommendation** — Go/no-go with rationale

## Number Formatting

- Currency: $X,XXX (comma-separated, no cents unless unit economics)
- Percentages: X.X% (one decimal)
- Ratios: X.X:1
- Time: X months / X weeks
- Ranges: $X–$Y (en dash, not hyphen)

## Tone

- Precise — numbers, not adjectives ("$45K" not "affordable")
- Conservative — use pessimistic estimates for costs, optimistic for timelines
- Transparent — label every assumption, flag every risk
- Actionable — end with a clear financial recommendation
