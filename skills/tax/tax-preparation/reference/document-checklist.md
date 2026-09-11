# Source Document Checklist

Organize by entity, then by type. Every document supports a **reconciliation** —
collecting it without tying it out accomplishes nothing.

## Individual (Form 1040)

```
INCOME
[ ] W-2, all employers                → wages, withholding, box 12 codes
[ ] 1099-NEC / 1099-MISC              → reconcile to Schedule C gross receipts
[ ] 1099-K (merchant/payment apps)    → threshold restored to $20k/200 txns (statutory, not indexed)
[ ] 1099-INT / 1099-DIV               → reconcile to brokerage year-end summary
[ ] 1099-B + cost basis detail        → check for missing/incorrect basis on
                                        noncovered lots; wash sale adjustments
[ ] 1099-R                            → check box 7 code; rollovers vs distributions
[ ] SSA-1099                          → taxability computation
[ ] K-1s (1065 / 1120-S / 1041)       → often the last to arrive; extend if needed
[ ] Schedule K-3 if any foreign items
[ ] Crypto transaction history        → property, not currency (Notice 2014-21)

DEDUCTIONS / CREDITS
[ ] 1098 mortgage interest            → acquisition vs equity debt tracing
[ ] 1098-T tuition                    → reconcile to actual payments, not billed
[ ] 1098-E student loan interest
[ ] Property tax bills, state estimates paid → SALT (watch the phase-down)
[ ] Charitable acknowledgments        → CWA required at $250+, BEFORE filing
[ ] HSA Form 5498-SA / 1099-SA
[ ] Childcare provider name, address, TIN → Form 2441 fails without the TIN
[ ] Estimated payment record + IRS transcript

CARRYFORWARDS (from prior year — get these FIRST)
[ ] NOL, capital loss, §179, credits, passive, at-risk, basis, AMT credit
```

## Schedule C / single-member LLC

```
[ ] Full-year P&L and general ledger
[ ] Bank + credit card statements, all business accounts
[ ] Merchant processor reports (Stripe, app stores, PayPal, Square)
      → where the platform is merchant of record, confirm gross vs net
        treatment; commission is generally an expense, not a revenue offset
[ ] 1099s received → reconcile to gross receipts, explain the difference
[ ] Fixed asset additions + disposals with invoices and in-service dates
[ ] Prior-year depreciation schedule
[ ] Vehicle: total miles, business miles, contemporaneous log  [§274(d)]
[ ] Home office: square footage, home expenses, exclusive-use evidence
[ ] Inventory: beginning, purchases, ending, method  [§263A / §471(c)]
[ ] 1099s ISSUED to contractors + W-9s on file
[ ] Business-use % support for mixed items (phone, internet)
```

## Partnership (Form 1065)

```
[ ] Operating agreement + any amendments
[ ] Trial balance and adjusting entries
[ ] Capital account rollforward per partner (tax basis)  [required disclosure]
[ ] Contributions and distributions by partner
[ ] Debt schedule with recourse / nonrecourse / qualified nonrecourse split
[ ] Guaranteed payments  [§707(c)]
[ ] Special allocations + substantial economic effect support  [§704(b)]
[ ] §704(c) built-in gain/loss on contributed property
[ ] Partner ownership % changes with dates
[ ] Prior-year K-1s
```

## C corporation (Form 1120)

```
[ ] Trial balance, book financial statements
[ ] Book-to-tax differences → Schedule M-1 / M-3
[ ] Retained earnings rollforward → Schedule M-2
[ ] Officer compensation detail  → Form 1125-E
[ ] Payroll registers, 941s, W-2/W-3 reconciliation
[ ] Fixed assets + depreciation schedule
[ ] NOL carryforward schedule by year  [§172, 80% limit]
[ ] R&D credit support:
      [ ] project descriptions + four-part test analysis
      [ ] wage QREs with time allocation   ← usually the weakest item
      [ ] contractor agreements (economic risk, rights retained) → 65%
      [ ] supply and cloud costs
      [ ] §280C(c) election decision
      [ ] §41(h) payroll offset eligibility (gross receipts history)
[ ] Intercompany agreements + invoices  [§482]
[ ] Stock ledger, cap table, any issuances or redemptions
[ ] QSBS evidence at each issuance (gross assets before/after)
[ ] Board minutes — especially business-needs support for retained earnings [§531]
[ ] State: franchise/income return in each state of nexus; annual report in the state of incorporation
[ ] App-level P&L for each incubated product
```

## Common reconciliation failures

| Symptom | Usual cause |
|---|---|
| Revenue < sum of 1099s | Missing income, or a 1099 issued to the wrong entity |
| Revenue > sum of 1099s | Normal — direct/sub-threshold sales. **Document it**, do not "fix" it |
| Merchant deposits ≠ revenue | Refunds, chargebacks, fees netted, timing at year end, reserve holds |
| Book income ≠ tax income | Expected — that is Schedule M-1. Every difference itemized |
| Depreciation ≠ prior schedule | Disposals not removed, or a method change made silently |
| Basis unsupported | The most common small-entity audit loss. Rebuild it now, not later |
| Entity name mismatch on a 1099 or contract | Known portfolio issue — undermines §351 and §482 positions. Correct it |
