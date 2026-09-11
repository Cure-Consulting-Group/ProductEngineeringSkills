# Safe Harbor Worksheet

## Individual — §6654

```
STEP 1  Prior-year figures (from the filed return)
        Prior-year AGI                          _________
        Prior-year total tax (Form 1040 line 24) _________

STEP 2  Which prior-year harbor applies?
        Prior-year AGI > $150,000 ($75,000 MFS)?
            YES → required = prior-year tax × 1.10
            NO  → required = prior-year tax × 1.00
        Prior-year safe harbor amount            _________  (A)

STEP 3  Current-year projection
        Projected current-year total tax         _________
        × 90%                                    _________  (B)

STEP 4  Target = lesser of (A) and (B)           _________  (C)

STEP 5  Expected withholding for the year        _________  (D)

STEP 6  Estimates required = (C) − (D)           _________
        ÷ 4 = per quarter                        _________
```

### Worked example

```
Prior-year AGI          $210,000  → over $150,000, so 110% applies
Prior-year total tax     $46,000
(A) 110% harbor          $50,600
Projected current tax    $61,000
(B) 90% of current       $54,900
(C) Target = lesser      $50,600
(D) Withholding          $12,000
Estimates needed         $38,600  →  $9,650 per quarter
```

Paying $50,600 total means **no penalty**, even if the actual liability turns out
to be $61,000. The $10,400 balance is simply due at filing. That is the harbor
working as intended — it is not a shortfall.

## Corporation — §6655

```
Prior-year taxable income under $1,000,000?
   YES → required = lesser of (100% of current-year tax)
                          or (100% of prior-year tax)
   NO  → required = 100% of current-year tax
        (large corporations may use the prior-year harbor for the
         FIRST installment only, then must true up)

Underpayment threshold: $500
Deposits: EFTPS only — electronic is mandatory
```

## Annualized income method — Form 2210 Schedule AI

Required cumulative percentage of the year's tax by period:

| Period | Months | Annualization factor | Required cumulative |
|---|---|---|---|
| Q1 | Jan–Mar | 4 | 22.5% |
| Q2 | Jan–May | 2.4 | 45% |
| Q3 | Jan–Aug | 1.5 | 67.5% |
| Q4 | Jan–Dec | 1 | 90% |

```
For each period:
  1. Actual income through the period end
  2. × annualization factor = annualized income
  3. Compute tax on annualized income
  4. × required cumulative % = required cumulative payment
  5. − payments already made = this period's installment
```

Use when income is genuinely uneven. Requires income records **by period** — if
the books cannot produce them, the method is not available in practice.

## Penalty cure decision tree

```
Discovered a shortfall — what quarter is it?

Before the current quarter's due date
    → pay it now, only the earlier quarters accrue

After Q4 due date but before filing
    → estimated payments can no longer fix earlier quarters
    → BUT increased WITHHOLDING is treated as paid ratably across
      the whole year (§6654(g))
    → if any wages remain, or an IRA/retirement distribution can be taken
      with withholding elected, this can retroactively cure ALL quarters

Already filed
    → compute the penalty on Form 2210
    → check the exceptions:
        [ ] Total tax after withholding/credits < $1,000
        [ ] No prior-year liability (full 12-month year)
        [ ] Casualty, disaster, or unusual circumstance
        [ ] Retired at 62+ or disabled, and the underpayment was
            not willful neglect
```

**The withholding-is-ratable rule is the most valuable fact in this file.** It
converts a year-long problem into a December fix.

## Quarterly tracking

| Q | Due | Target | Paid | Date | Cumulative | On harbor? |
|---|---|---|---|---|---|---|
| Q1 | 2026-04-15 | | | | | |
| Q2 | 2026-06-15 | | | | | |
| Q3 | **2026-09-15** | | | | | |
| Q4 | 2027-01-15 | | | | | |

Reconcile against the **IRS account transcript**, not internal records. Misapplied
payments — wrong year, wrong entity, wrong EIN — are common and only visible on the
transcript. Catching one in September is routine; catching it at filing is a
scramble.

## Multi-entity note

With several entities plus an individual return, payments must be made to the
**right taxpayer with the right EIN for the right period**. A corporate payment applied
to the individual account satisfies neither. Verify each deposit's application on
the transcript within a few weeks of payment.
