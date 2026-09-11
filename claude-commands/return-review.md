# Return Review & Evaluation

The independent second pass. Preparation finds the answer; review proves it.

## Disclaimer
This skill produces draft analysis and workpapers, not tax, legal, or accounting advice. Nothing it produces is filing-ready until a licensed CPA, enrolled agent, or tax attorney has reviewed it. Model output is not authority and does not establish reasonable cause (see `cpa-standards`).

**Rule: review is never performed in the same sitting as preparation.** Where the
preparer and taxpayer are the same person, this pass is the only independent
control that exists. Treat the return as though someone else made it and you are
looking for their mistakes.

## Four layers, in order

Do not skip ahead. Layer 1 failures make layers 2–4 meaningless.

```
1. TIE-OUT      Does every number trace to a source or a computation?
2. INTERNAL     Are the forms consistent with each other?
3. REASONABLE   Do the results make sense given the facts and prior year?
4. OPPORTUNITY  Was anything legitimately available left on the table?
```

## Layer 1 — Tie-out

Every figure on the return resolves to one of: a source document, a computation
workpaper, or a carryforward schedule. Nothing is "from the books" without the
books reconciling.

```
[ ] Wages → W-2s, in total
[ ] Gross receipts → merchant + bank deposits, reconciled, differences explained
[ ] 1099s received → reported income (revenue is usually higher; document why)
[ ] Interest/dividends → 1099s and brokerage year-end summary
[ ] Capital transactions → 1099-B, with basis verified on noncovered lots
[ ] K-1 amounts → the K-1s, box by box
[ ] Withholding and estimates → W-2s, 1099s, and the IRS account transcript
[ ] Depreciation → prior schedule + additions − disposals
[ ] Every carryforward → prior-year carryforward schedule
[ ] Book income → tax income via M-1, every difference itemized
```

### Automated support
Run whatever the project binds as `validator` (pre-filing validation, filing
readiness) plus its golden-file and regression suites before starting the manual
review, so the review spends its attention on judgment rather than arithmetic.

Machine checks are **necessary, not sufficient** — they verify the engine did what
it was told, not that it was told the right thing.

## Layer 2 — Internal consistency

Cross-form relationships that must hold. Full list in
`reference/tie-out-checklist.md`.

High-value checks:
- Schedule C net profit → Schedule SE → the §164(f) one-half deduction
- Schedule SE net earnings → retirement contribution limit
- QBI (§199A) → the W-2 wage / UBIA limitation, and the taxable-income limitation
- AGI → every AGI-driven phase-out actually applied (SALT phase-down, CTC, tips,
  overtime, senior, IRA, student loan)
- 1120 Schedule L → M-1 → M-2, and retained earnings rolling correctly
- Officer compensation on Form 1125-E → W-2s issued → 941 totals
- State return starting point → the correct federal figure, with decoupling
  adjustments applied (NY §280E decoupling, PTET credit, ITC coordination)
- Depreciation on the return → the fixed asset register

## Layer 3 — Reasonableness

Where real errors hide. A return can tie out perfectly and still be wrong.

```
[ ] Effective tax rate — plausible for this income and structure?
[ ] Every material line vs prior year — variance EXPLAINED IN WRITING,
    not merely noted
[ ] Margins consistent with the business model?
[ ] Any expense category that jumped without a business reason?
[ ] Officer comp reasonable for the services actually rendered?  [§162(a)(1)]
[ ] Loss year — is there a genuine profit motive story?  [§183]
[ ] Any round numbers where records should produce precision?
[ ] Home office / vehicle percentages defensible and documented?
[ ] Does the return tell a coherent story about this business?
```

**The narrative test**: read the return as a stranger. Does the picture it paints
match what the business actually is? A services company reporting nominal revenue
alongside a large research credit invites a question — the answer may be perfectly
good, but the answer needs to exist in the file before the question is asked.

## Layer 4 — Missed opportunity

Review is also the last chance to catch what was not claimed.

```
[ ] Run the deductions-and-credits screening checklist against the final numbers
[ ] Credits before deductions — worth ~4x at the margin
[ ] Every election reviewed against elections-and-deadlines.md
[ ] Retirement contribution maximized (many can still be funded post-year-end)
[ ] Carryforwards actually USED where they should be, not just carried
[ ] Accounting method opportunities (§174A retroactive, §471(c))
[ ] Anything the strategy playbook flags for this entity that was not executed
```

## Diagnostic disposition

Every diagnostic gets one of three dispositions, in writing:

| Disposition | Meaning |
|---|---|
| **Cleared** | Fixed. Note what changed. |
| **Accepted** | Reviewed, correct as-is. **Note WHY** — an accepted diagnostic with no explanation is an open item wearing a disguise. |
| **Open** | Unresolved. **The return does not go out with an open item.** |

## Sign-off

```
Reviewed by: ______________________  Date: __________
[ ] All four layers complete
[ ] Zero open items
[ ] Every material variance explained in writing
[ ] Every non-routine position has a memo dated before today
[ ] Carryforward schedule rolled forward and reconciled
[ ] Diagnostics dispositioned
```

_Draft for professional review — not tax advice. A licensed CPA, EA, or tax attorney must review before filing, paying, or acting._

## Output shape

Report findings as: **severity** (blocker / correction / question / opportunity),
**location** (form and line), **the issue**, **the evidence**, **the fix**. Rank
blockers first. Do not bury a material error inside a list of formatting notes.

## Reference files

- `reference/tie-out-checklist.md` — cross-form relationships that must hold, by
  return type.
- `reference/common-errors.md` — the recurring error catalog, ranked by frequency
  and cost, with the detection test for each.

## Related skills

`tax-preparation`, `cpa-standards` (workpaper and review standards),
`audit-risk-substantiation` (what a reviewer's findings imply for exposure),
`cpa-benchmark` (competency behind the review).
