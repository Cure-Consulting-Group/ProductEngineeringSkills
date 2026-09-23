# Merger Modeling (Accretion/Dilution)

**Outcome:** year-1 and year-2 pro-forma EPS vs. standalone, % accretion/(dilution), breakeven
synergies, and a synergy-realization sensitivity, with deal assumptions listed. **Done when** the
pro-forma share count and interest lines reconcile and every assumption has a source or is
marked as an assumption. Not investment advice. Match length to the need; no filler sections or
restated summaries.

In Claude Code the `investment-banker` agent runs this alongside the valuation skills.

## Step 1: Classify

- **Public acquirer, EPS-driven:** full accretion/dilution.
- **Private or small-company deal** (the likelier Cure case — e.g. acquiring or selling a studio
  product): EPS is not the test. Model ownership dilution, cash-flow payback, and post-deal
  runway (hand runway to `burn-rate-tracker`) instead.

## Step 2: Gather

Offer price and premium; consideration mix (cash / stock / new debt); acquirer share price
(dated) and diluted shares; rate on new debt and yield on cash used; tax rate; both companies'
projected net income; fair-value write-ups and identified intangibles with useful lives;
transaction and financing fees; synergy estimates with source.

## Step 3: Gotchas that change the answer

- **Interest lines after tax:** new-debt interest and foregone interest on cash both flow
  through at (1 − tax rate).
- **New shares** = stock consideration ÷ acquirer price; use diluted shares (treasury stock
  method) on both sides.
- **PPA:** amortization of identified intangibles and D&A on write-ups reduce pro-forma income;
  write-ups create a deferred tax liability. Goodwill is not amortized under US GAAP for public companies (private companies may elect to) but is tested
  for impairment.
- **Fees:** financing fees amortize; advisory fees hit at close — keep them out of run-rate EPS
  and say so.
- **Synergies phase in** (Cure default: 25% year 1, 75% year 2, 100% year 3) net of cost to
  achieve; revenue synergies shown separately and haircut.
- Report "cash EPS" (excluding deal amortization) only alongside GAAP EPS, labeled.

## Output

```markdown
## M&A Analysis: [Acquirer] / [Target] — as of [date]
Price $[X] ([X]x EBITDA, [X]% premium) | Mix [X]% cash / [X]% stock / [X]% debt
| Metric | Standalone | Pro-forma | Δ% |  (EPS Y1, Y2; share count; net debt/EBITDA)
Breakeven synergies: $[X] pre-tax
Sensitivity: synergy realization 0 / 50 / 100% × premium ±10%
Commentary: leverage, synergy risk, what would make it dilutive
```
