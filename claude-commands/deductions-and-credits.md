# Deductions, Credits & Exclusions

The benefit catalog. Where `tax-strategies` covers structural moves that require
planning, this skill covers what is claimable on a return given facts that
already exist.

## The three benefit types — never confuse them

| Type | Effect | Worth per \$1 at 24% |
|---|---|---|
| **Exclusion** | Never enters gross income (§61) | \$0.24 + keeps AGI down, which protects phase-outs |
| **Deduction** | Reduces taxable income | \$0.24 |
| **Credit** | Reduces tax dollar-for-dollar | \$1.00 |

A credit is worth roughly 4x a deduction at a 24% marginal rate. **Always screen
credits first** — they are more valuable and more often missed.

Within deductions, the ranking is:
1. **Above-the-line** (§62 adjustments) — reduce AGI itself, so they also unlock
   AGI-sensitive benefits. Best.
2. **Business deductions** (§162, on Schedule C / 1120 / 1065) — reduce income
   *and* self-employment tax. Best of all for a sole proprietor.
3. **Schedule 1-A / OBBBA deductions** — available on top of standard or itemized.
4. **Itemized** (§63(d)) — only worth anything above the standard deduction.

## Workflow

1. **Establish the year and filing status.** Pull every limit from the project's
   `constants` binding, never from memory. If the project has no engine, take the
   figures from `irc-lookup` and cite the Rev. Proc. they come from.
2. **Classify every dollar of spend** as: business (§162), personal (§262),
   mixed (allocate), or capital (§263 — depreciate instead).
3. **Run the screens** in `reference/credits-catalog.md` first, then
   `reference/deductions-catalog.md`. Both are ordered by how often they are
   missed, not alphabetically.
4. **Apply the limitation stack** in order — see below. Deductions die in this
   stack far more often than they fail the underlying test.
5. **Check substantiation** for each claimed item against
   `reference/substantiation-by-deduction.md`. A deduction you cannot prove is a
   deduction you will lose, plus a §6662 penalty.
6. **Compare itemized vs standard**, including the OBBBA Schedule 1-A items that
   are additive to both.

## The limitation stack (order matters)

A business loss must survive all four gates, in this sequence:

```
§262/§263  Is it deductible at all, or personal/capital?
   ↓
§704(d)/§1366(d)  Basis — do you have enough to absorb it?
   ↓
§465  At-risk — is the money genuinely at risk?
   ↓
§469  Passive activity — do you materially participate?
   ↓
§461(l)  Excess business loss — is it over the annual cap?
   ↓
Deductible this year (excess carries forward as NOL under §172)
```

Additional gates that kill otherwise-valid deductions:
- **§183 hobby loss** — no profit motive, no deduction. *Screen any activity with
  consecutive loss years: it fails the 3-of-5 presumption.*
- **§280E** — cannabis trafficking disallows everything but COGS. *Applies to
  any cannabis activity once it begins trafficking.*
- **§274(d)** — no substantiation, no deduction, regardless of merit.
- **§267** — related-party payment not deductible until includible by the payee.

## Screening heuristics

Ask these, in this order, when hunting for missed benefit:

- **Is there a business?** If yes, a large class of otherwise-personal spend
  (phone, internet, home office, vehicle, education, travel, health insurance)
  becomes partially deductible.
- **Is there payroll?** Payroll unlocks §41(h) payroll offset, §45S, §45F, §51,
  retirement plan deductions, and the §199A W-2 wage limit. *A company with no
  payroll has zero wage QREs, which is the most common reason an R&D credit comes
  out a fraction of what the work was worth.*
- **Are there children, education, or dependents?** §24, §25A, §21, §129.
- **Is there equipment, software, or a vehicle?** §179, §168(k), §179A, §168(n).
- **Is there R&D or software development?** §174A + §41. Frequently missed by
  founders who think "we're not a lab."
- **Is there retirement capacity?** The largest single deduction available to a
  profitable owner-operator — see `retirement-plan` and the `tax-strategies` skill.
- **Is there health insurance?** §162(l) above-the-line, or an HRA/ICHRA.
- **Did anything get sold, lost, or abandoned?** §165, §1244, §1231.

## Output shape

For each benefit identified:

| Field | Content |
|---|---|
| Benefit | Name and IRC section |
| Test | The elements, as a checklist with pass/fail against actual facts |
| Amount | Computed, showing the limit calculation |
| Where | Form and line |
| Substantiation | What must exist in the file |
| Confidence | Per `irc-lookup` conventions: VERIFIED / CATALOG / RECALL |

Flag anything claimed on `RECALL` numbers before it reaches a return.

## Reference files

- `reference/credits-catalog.md` — credits by category with eligibility tests,
  refundability, carryforward, and ordering rules under §38.
- `reference/deductions-catalog.md` — above-the-line, business, itemized, and
  OBBBA Schedule 1-A deductions with tests and limits.
- `reference/substantiation-by-deduction.md` — what documentation each deduction
  requires, including the §274(d) strict-substantiation categories.

## Related skills

`irc-lookup` (verify any cite), `tax-strategies` (structural moves),
`audit-risk-substantiation` (defending what you claim),
`tax-recommendations` (ranking and presenting findings).
