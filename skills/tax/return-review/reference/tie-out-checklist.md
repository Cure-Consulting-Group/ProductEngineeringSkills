# Tie-Out Checklist — Cross-Form Relationships

Relationships that must hold arithmetically. A break is an error, not a rounding
difference.

## Form 1040 chain

```
W-2 box 1 (all)                     → 1040 line 1a
Schedule C line 31 (net profit)     → Schedule 1 line 3 → 1040 line 8
Schedule C line 31                  → Schedule SE line 2
Schedule SE net earnings            = Schedule C net profit × 0.9235
Schedule SE tax                     → Schedule 2 line 4
Schedule SE tax × 50%               → Schedule 1 line 15  [§164(f)]
Schedule D net                      → 1040 line 7 (capped at −$3,000 ordinary)
Schedule E                          → Schedule 1 line 5
Total Schedule 1 adjustments        → 1040 line 10
1040 line 11 (AGI)                  → drives EVERY phase-out below
Standard or itemized                → 1040 line 12
Schedule 1-A (tips/OT/senior/auto)  → additive, NOT part of line 12
QBI §199A                           → 1040 line 13
Withholding (W-2 box 2 + 1099s)     → 1040 line 25
Estimated payments                  → 1040 line 26  (tie to IRS transcript)
```

### AGI-driven items — confirm each was actually applied
```
[ ] SALT cap phase-down          30% of MAGI over ~$505,000 (2026), floor $10,000
[ ] Child tax credit             $50 per $1,000 over $200k/$400k
[ ] Tips deduction               $100 per $1,000 over $150k/$300k
[ ] Overtime deduction           $100 per $1,000 over $150k/$300k
[ ] Senior deduction             6% of MAGI over $75k/$150k
[ ] Car loan interest            $200 per $1,000 over $100k/$200k
[ ] IRA deductibility            if covered by a plan
[ ] Student loan interest        §221
[ ] Education credits            §25A
[ ] Medical floor                7.5% of AGI
[ ] Charitable ceilings          60% / 30% of AGI (+ new 0.5% floor — VERIFY)
[ ] NIIT                         §1411, $200k/$250k MAGI
[ ] Additional Medicare          §3101(b)(2), $200k/$250k
```

## Schedule C

```
Gross receipts        ≥ sum of 1099-NEC + 1099-MISC + 1099-K  (explain the excess)
Gross receipts        ≈ merchant deposits + direct receipts − refunds/chargebacks
COGS                  = beginning inventory + purchases − ending inventory
Line 13 depreciation  = Form 4562 total for this activity
Line 30 home office   = Form 8829 line 36 OR simplified (≤300 sq ft × $5)
Line 9 car expense    = business miles × 0.725 (2026) OR actual × business %
Net profit line 31    → Schedule SE AND Schedule 1
```

## Form 1120

```
Book income (Schedule L)     → M-1 line 1
M-1 additions/subtractions   → taxable income before NOL and special deductions
NOL deduction                ≤ 80% of taxable income before the NOL  [§172(a)(2)]
Tax                          = taxable income × 21%  [§11]
Officer comp (Form 1125-E)   = W-2s issued to officers = 941 totals for the year
Schedule L retained earnings = prior RE + net income − distributions  (ties to M-2)
Schedule L total assets      = total liabilities + equity
Depreciation (Form 4562)     = fixed asset register roll
R&D credit (Form 6765)       → Form 3800 → tax; or Form 8974 if §41(h) elected
Estimated payments           → IRS account transcript
```

**Balance sheet must balance.** An out-of-balance Schedule L is a blocker, not a
note.

## Form 1065

```
Book income               → Schedule M-1 → Schedule K line 1
Schedule K total          = sum of all K-1s, line by line, box by box
Capital accounts          = beginning + contributions + income − distributions − losses
Ending capital (tax basis)  ties to Schedule L partners' capital
Debt allocation           recourse + nonrecourse + qualified nonrecourse = total debt
Guaranteed payments       → Schedule K line 4 AND deducted on page 1
```

## §199A QBI

```
QBI per activity                    → aggregated (if elected) or separate
Tentative deduction                 = 20% × QBI
If taxable income > threshold:
   Wage/UBIA limit                  = greater of (50% × W-2 wages)
                                       or (25% × W-2 wages + 2.5% × UBIA)
   Phase-in                         over $75,000 single / $150,000 MFJ (2026)
   SSTB                             fully phased out at $276,775 / $553,500
Overall limit                       = 20% × (taxable income − net capital gain)
Minimum (2026+)                     $400 if active QBI ≥ $1,000
```

## Depreciation

```
Prior-year ending basis
  + current-year additions (at cost, placed-in-service date verified)
  − dispositions (with gain/loss and §1245/§1250 recapture computed)
  = current-year depreciable base
§179 claimed                ≤ $2,560,000 (2026), reduced above $4,090,000
§179 claimed                ≤ business taxable income (excess carries forward)
Bonus                       100% of remaining basis unless elected out by class
Total Form 4562             → Schedule C line 13 / 1120 line 20 / 1065 line 16
```

## State (NY)

```
Federal AGI or FTI          → NY starting point
NY additions/subtractions   → decoupling adjustments applied:
    [ ] §280E decoupling (several states allow what federal disallows)
    [ ] §179 / bonus conformity differences
    [ ] PTET addback and corresponding credit
NY ITC                      coordinated with federal expensing on the same asset
Nonresident/part-year       allocation percentage supported by day counts
```

## Prior-year comparison

Build the schedule. Every material variance gets a written explanation.

| Line | PY | CY | Δ | Δ% | Explanation |
|---|---|---|---|---|---|

Materiality: the greater of 10% of the line or a fixed dollar floor appropriate to
the return. **"Business changed" is not an explanation.**
