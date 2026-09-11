---
name: estimated-tax-compliance
description: Manage estimated payments, withholding, and filing compliance — §6654/§6655 safe harbors, quarterly computation, the annualized income method, and the multi-entity due-date calendar. Use when computing or timing estimates, avoiding an underpayment penalty, or adjusting withholding.
argument-hint: "[quarter-or-entity]"
---

# Estimated Tax & Ongoing Compliance

Estimated tax is the most mechanical thing in this skill library and one of the
most commonly botched, because it has to be right **four times a year** with
incomplete information.

**Resolve the nearest hard date before anything else.** Quarterly installments
and entity due dates move with the calendar — read them off
`reference/safe-harbor-worksheet.md` and the current year's IRS calendar rather
than assuming the one you remember.

## The core rule

The US tax system is pay-as-you-go (§6654). Owing at filing is not the failure —
**not having paid enough as the income was earned** is. The penalty is
interest-rate based and applies quarter by quarter, so paying a large amount in
January does not cure a Q1 shortfall.

## Safe harbors — individuals (§6654)

Pay the **least** of these and no penalty applies, regardless of what is
ultimately owed:

| Safe harbor | Requirement |
|---|---|
| **Current year** | 90% of the current year's actual tax |
| **Prior year** | 100% of the prior year's total tax |
| **Prior year, high income** | **110%** of prior year's tax if prior-year **AGI exceeded \$150,000** (\$75,000 MFS) |

**The prior-year safe harbor is the workhorse.** It is a known, fixed number
available in January, and it is immune to a good year. When income is rising or
uncertain — which describes most young multi-entity groups — use it and stop guessing.

Other outs:
- Total tax after withholding and credits is **under \$1,000** → no penalty.
- No tax liability in the prior year (full 12-month year, US citizen/resident) →
  no penalty regardless.

## Safe harbors — corporations (§6655)

| Safe harbor | Requirement |
|---|---|
| **Current year** | 100% of the current year's tax |
| **Prior year** | 100% of prior-year tax — **available only if prior-year taxable income was under \$1 million** and a return was filed for a full 12-month year showing a liability |

Note the difference: corporations get **no 90% option** and a **large corporation
loses the prior-year harbor** after the first installment. Underpayment threshold
is \$500.

## 2026 due dates

From the `constants` binding for 2026:

| Quarter | Income period | Due |
|---|---|---|
| Q1 | Jan 1 – Mar 31 | **2026-04-15** |
| Q2 | Apr 1 – May 31 | **2026-06-15** |
| Q3 | Jun 1 – Aug 31 | **2026-09-15** |
| Q4 | Sep 1 – Dec 31 | **2027-01-15** |

The quarters are **not equal** — Q2 covers two months, Q3 covers three. Dividing
annual tax by four and paying on those dates is correct for the safe harbor but
wrong for the annualized method.

## Computation

```
1. Determine the target
     min( 90% × projected current-year tax,
          100% or 110% × prior-year tax )

2. Subtract expected withholding for the year
     → the amount that must come from estimates

3. Divide by four, unless using the annualized method

4. Adjust each quarter for actual results to date
```

### Withholding beats estimates

Withholding is **treated as paid ratably across the year** regardless of when it
was actually withheld (§6654(g)). An estimated payment is credited only to the
quarter it is made.

**This is the single most useful cure in the whole area**: a Q1–Q3 shortfall
discovered in November can be fixed by increasing Q4 withholding — from wages, a
bonus, or an IRA distribution with withholding elected — and the penalty for the
earlier quarters disappears. An estimated payment of the same amount on the same
date will not do that.

### Annualized income method

Form 2210 Schedule AI. Compute the required installment based on income **actually
earned through each period** rather than assuming even receipt.

Use it when income is lumpy — an exit, a large Q4 payment, seasonal revenue. It is
substantially more work and requires income records by period, so it is worth it
only when it materially beats the flat method.

## Portfolio application

| Entity | Mechanism |
|---|---|
| **Individual** | Form 1040-ES. Pass-through income from every Schedule C and K-1 entity, plus wages once any entity runs payroll. |
| **C corporation** | Form 1120-W computation, deposits via **EFTPS**. Corporate estimates are **mandatory electronic** — there is no check option. |
| **Pre-revenue corporation** | Same, once it has liability. Pre-revenue usually means none — but **state franchise obligations exist regardless of income**, and they are the ones that get missed. |
| **Pass-through (Schedule C, S corp, partnership)** | The tax lands on the owner's return. A **PTET election** moves state tax to the entity on its own schedule, which changes the owner's state estimate for that year. |

## Withholding optimization

Where the project has a `withholding` binding, model the change before filing a
new W-4; otherwise work it by hand off the current year's Publication 15-T.

- **W-4** is no longer allowance-based. Multiple-job and dependent computations go
  in Steps 2–4; extra flat withholding goes in Step 4(c).
- Getting a large refund means an interest-free loan to the government all year.
  Target a small balance due, within the safe harbor.
- Once any entity in the group runs payroll, owner withholding becomes the
  **primary lever** and
  estimated payments become the backstop rather than the main channel.

## Other ongoing compliance

Beyond estimates, these recur and carry their own penalties:

| Obligation | Cadence | Penalty exposure |
|---|---|---|
| Payroll deposits (941/940) | Semiweekly or monthly per lookback | **§6672 trust fund recovery — 100%, personal, non-dischargeable** |
| Forms 941 | Quarterly | §6651, §6656 |
| Form 940 | Annual | §6651 |
| W-2/W-3 | Jan 31 | §6721/§6722 |
| 1099-NEC/MISC | Jan 31 / Feb–Mar | §6721/§6722, per form, per copy |
| Sales tax (any retail or marketplace activity) | State schedule | State penalties; **often personal liability for a responsible person** |
| NY PTET estimated payments | Quarterly after election | Loss of the benefit |
| DE franchise report | Mar 1 | Penalty + interest, and loss of good standing |
| Annual reports / registered agent | Varies | Administrative dissolution |

Payroll deposits are never a cash-flow lever. §6672 pierces the entity, attaches
personally, and survives bankruptcy.

## Reference files

- `reference/safe-harbor-worksheet.md` — worked computations for both regimes,
  the annualized method, and the penalty cure decision tree.

## Related skills

`tax-preparation` (filing calendar), `tax-recommendations` (cash-flow impact of
strategies), `audit-risk-substantiation` (penalty map), `cpa-standards`.
