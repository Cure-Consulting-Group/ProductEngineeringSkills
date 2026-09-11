# Credit Catalog

Ordered by how often they are missed in an owner-operator / startup context.
Dollar figures marked `[constants]` come from the `constants` binding.

## Business credits (§38 general business credit)

### §41 — Research credit  ★ the most commonly under-claimed credit for a software company
- **Test**: qualified research must satisfy the **four-part test** —
  (1) permitted purpose (new/improved function, performance, reliability, quality),
  (2) technological in nature (hard sciences, incl. computer science),
  (3) elimination of uncertainty, (4) process of experimentation.
- **QREs**: in-house wages for qualified services (§41(b)(2)), supplies, cloud
  computing/rental of computer time, and **contract research at 65%** (75% for
  qualified research consortia).
- **Two computation methods**:
  - Regular: 20% of QREs over a base amount.
  - **Alternative Simplified Credit (ASC)**: 14% of QREs over 50% of the prior
    three years' average QREs. If no QREs in any of the prior 3 years, **6% of
    current-year QREs**. Use ASC — the regular method's base-period computation
    is impractical for a young company.
- **§280C(c) election**: reduce the credit by 21% (the corporate rate) to keep
  the full §174A deduction, or take the full credit and reduce the deduction.
  Election made on a timely-filed return.
- **§41(h) payroll offset — critical for pre-revenue companies**: a qualified
  small business (gross receipts < $5M in the credit year, and **no gross
  receipts before the 5-tax-year period ending with the credit year**) may elect
  to apply up to **$500,000** of credit against the **employer share of Social
  Security tax, then Medicare tax** (§3111(f); for tax years beginning after 2022 the first $250,000 offsets Social Security and the rest Medicare), claimed on Form 8974 with Form 941. This turns a
  useless credit carryforward into cash for a company with no income tax
  liability.
- **Forms**: Form 6765. Payroll election requires the election *on the timely
  filed original return* — cannot be made on an amended return.
- **The structural trap**: a company claiming this credit with **zero wage QREs**
  under-claims it by construction. Development labor performed by an owner is a
  QRE only to the extent it is **compensated as wages**. No payroll → no wage QREs
  → the credit collapses to supplies and 65% of contractor spend. Fixing it
  requires reasonable owner compensation on a W-2 first, justified on its own
  terms — not manufactured to produce a credit. See `tax-strategies` →
  `reference/entity-playbook.md`.

### §45S — Paid family and medical leave credit
- 12.5%–25% of wages paid during leave, scaling with the replacement rate.
- Requires a **written policy** meeting §45S(c) before the leave is taken.
- Made permanent by OBBBA.

### §45F — Employer-provided child care
- Percentage of qualified child care facility and resource/referral expenditures,
  subject to an annual cap. Increased by OBBBA — `VERIFY` current rate and cap.
- 10-year recapture if the facility ceases to operate as such.

### §51 — Work opportunity credit
- 25–40% of first-year wages for hires from targeted groups (veterans, long-term
  unemployed, SNAP recipients, ex-felons, designated community residents).
- **Hard deadline**: Form 8850 must be filed with the state workforce agency
  **within 28 days of the employee's start date**. Miss it and the credit is gone.

### §44 — Disabled access credit
- 50% of eligible access expenditures between $250 and $10,250 → max $5,000.
- Eligible small business: ≤ $1M gross receipts or ≤ 30 full-time employees.
- Pairs with the §190 deduction for barrier removal.

### §38 / §39 — Ordering and carryover
- Credits combine into the general business credit, limited to net income tax
  minus the greater of tentative minimum tax or 25% of regular tax over $25,000.
- **Carryback 1 year, carryforward 20 years.** Unused credits are not lost, but
  they are dead money — prefer the §41(h) payroll election when eligible.

## Individual credits

### §24 — Child tax credit
- `[constants]` 2026: $2,200 per qualifying child, $1,700 refundable.
- Phase-out $50 per $1,000 of MAGI over $200,000 / $400,000 MFJ.
- Child must be under 17 at year end and have an **SSN valid for employment**.
- $500 nonrefundable credit for other dependents (§24(h)(4)).

### §25A — Education credits
- **AOTC**: 100% of first $2,000 + 25% of next $2,000 = **$2,500 max**, per
  student, first 4 years of postsecondary, at least half-time, no felony drug
  conviction. **40% refundable** (up to $1,000).
- **Lifetime Learning**: 20% of up to $10,000 = **$2,000 max**, per return,
  unlimited years, non-refundable, covers job-skill courses.
- Cannot claim both for the same student in the same year.
- Requires Form 1098-T. Phase-outs apply — `VERIFY` current ranges.

### §21 — Child and dependent care credit
- 20–35% of up to $3,000 (one qualifying person) / $6,000 (two or more).
- Requires **earned income by both spouses** (or student/disabled status).
- Provider TIN required on Form 2441 — a common failure point.
- Coordinates with §129 dependent care FSA (same $ can't be used twice).

### §25B — Saver's credit
- 10/20/50% of up to $2,000 contributed to a retirement plan, by AGI tier.
- Low AGI only — usually irrelevant here, but screen it in loss years.

### §25D — Residential clean energy
- 30% of solar, solar water heating, fuel cell, wind, geothermal, and **battery
  storage ≥3 kWh**. No dollar cap for most property.
- **Personal residence only** — a business-use portion goes to §48 instead.
- Nonrefundable but carries forward.

### §30D / §25E / §45W — Clean vehicle credits
- Up to $7,500 new (§30D), $4,000 used (§25E), commercial (§45W).
- Subject to MSRP caps, income caps, North American final assembly, and critical
  mineral / battery component sourcing.
- **Statutory termination dates were accelerated by OBBBA — `VERIFY` whether the
  credit is still available for the placed-in-service date before claiming.**

### §32 — Earned income credit
- `[constants]` phase-out tables by dependent count.
- **Investment income limit** disqualifies at a low threshold — screen this first
  for anyone with a brokerage account.
- Due-diligence requirements under §6695(g) apply to the preparer: Form 8867,
  $600+ penalty per failure.

### §901 — Foreign tax credit
- Relevant if any app revenue has foreign withholding (App Store / Stripe payouts
  from non-US jurisdictions).
- Form 1116; de minimis exception under $300/$600 MFJ allows claiming without the
  form.

## Screening checklist

```
[ ] Any wages paid?              → §41(h), §45S, §51, §45F
[ ] Any R&D or software dev?     → §41 (+ §174A deduction)
[ ] Children under 17?           → §24
[ ] Anyone in school?            → §25A
[ ] Paid for child care?         → §21, §129
[ ] Solar / battery / EV?        → §25D, §30D (check termination dates)
[ ] Foreign tax withheld?        → §901
[ ] Accessibility improvements?  → §44 + §190
[ ] Unused credits from prior yr?→ §39 carryforward — check the schedule
```
