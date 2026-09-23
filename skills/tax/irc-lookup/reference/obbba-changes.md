# OBBBA — What Changed (P.L. 119-21, enacted 2025-07-04)

The One Big Beautiful Bill Act rewrote enough of the Code that **pre-July-2025
tax knowledge is unsafe as a default** for 2025 and 2026 returns. This file lists
what moved, so a stale assumption gets caught before it reaches a return.

**Confidence key**
- `ENGINE` — the figure is encoded in the project's `constants` binding with a
  cited source, reconciled against the revenue procedure. Trust it to the extent
  that reconciliation actually happened.
- `VERIFY` — directionally correct from statute, but confirm the exact figure,
  effective date, or mechanics against primary text before filing use.

Figures below were checked on 2026-09-23 against Rev. Proc. 2025-32 (2026
inflation adjustments) or the amended Code text unless a row says otherwise.
Re-check them for any other tax year.

## Rates and the individual base

| Item | Change | Confidence |
|---|---|---|
| Individual rate schedule | TCJA's 10/12/22/24/32/35/37 made **permanent** — no 2026 snap-back to 39.6%. This is the single biggest planning assumption that changed. | `ENGINE` |
| Standard deduction | Permanently elevated and re-indexed. 2025: $15,750 / $31,500 / $23,625. 2026: $16,100 single and MFS / $32,200 MFJ / $24,150 HoH. | `ENGINE` |
| Personal exemptions | Remain repealed. | `VERIFY` |
| Senior deduction | New $6,000/person age 65+, 2025–2028, phases out at 6% over $75k single / $150k MFJ. On **Schedule 1-A**; available to itemizers and non-itemizers. | `ENGINE` |
| Tips deduction | Up to $25,000, 2025–2028. Phases out $100 per $1,000 of MAGI over $150k/$300k. **MFS ineligible** — must file MFJ if married. | `ENGINE` |
| Overtime premium deduction | Up to $12,500 single / $25,000 MFJ, 2025–2028, same phase-out mechanics. MFS ineligible. | `ENGINE` |
| Car loan interest | Up to $10,000 on loans for **new US-assembled personal-use vehicles**. Phases out $200 per $1,000 over $100k/$200k. **Leases do not qualify.** | `ENGINE` |
| SALT cap | $40,000 (2025), $40,400 (2026), +1%/yr through 2029; **phases down by 30% of MAGI over $505k (2026; $500k in 2025) to a $10,000 floor**; MFS halves. Flat $10,000 from 2030 (§164(b)(7)). | `ENGINE` |
| PTET workaround | **Preserved** — proposals to limit pass-through entity tax deductions for SSTBs did not survive. State PTET elections remain the primary SALT workaround. | `VERIFY` |
| Child tax credit | $2,200 (from $2,000), permanent; 2026: $2,200, $1,700 refundable, indexed. | `ENGINE` |
| AMT | Exemption phase-out **thresholds reset down** to $500k/$1M (the $1M not indexed before 2027) and the phase-out **rate doubled from 25% to 50%** starting 2026. 2026 exemption $90,100 / $140,200 MFJ. Pulls more upper-middle earners into AMT. | `ENGINE` |
| Itemized deduction limitation | New limitation reducing the benefit of itemized deductions for taxpayers in the 37% bracket (effectively capping benefit near 35%). | `VERIFY` |
| Charitable deduction | 2026+: 0.5%-of-contribution-base floor for itemizers (§170(b)(1)(I), verified); non-itemizer deduction for cash gifts, $1,000 / $2,000 MFJ (§170(p) — confirm amounts). | `VERIFY` |

## Business provisions

| Item | Change | Confidence |
|---|---|---|
| **§174 / §174A R&E** | Immediate domestic R&E expensing **restored** for tax years beginning after 2024. Foreign R&E still amortized over 15 years. Small-business (gross receipts ≤ $31M) retroactive election for 2022–2024 **expired** — deadline was the earlier of 2026-07-06 or the §6511 period (Rev. Proc. 2025-28). Still live: any taxpayer may recover unamortized 2022–2024 domestic amounts in full in the first tax year beginning after 2024 or ratably over that year and the next. **Directly relevant to any in-house product development.** | `VERIFY` |
| **§168(k) bonus** | 100% bonus made **permanent** for property acquired after 2025-01-19. No more phase-down schedule. | `ENGINE` |
| **§179 expensing** | Limit raised to $2.5M (2025) / $2,560,000 (2026); phase-out threshold $4M / $4,090,000. | `ENGINE` |
| **§168(n) qualified production property** | New 100% expensing for **nonresidential real property used in manufacturing/production**, construction beginning after 2025-01-19 and before 2029. **Potentially large for any entity that acquires or builds production space — but only if the activity is genuinely manufacturing.** | `VERIFY` |
| **§199A QBI** | Made permanent. Phase-in range **widened** to $75k single / $150k MFJ (from $50k/$100k), which softens the SSTB cliff. 2026 threshold $201,750 single / $201,775 MFS / $403,500 MFJ. New **$400 minimum deduction** when active QBI ≥ $1,000 (2026+; both indexed after 2026). | `ENGINE` |
| **§461(l) excess business loss** | Made **permanent** (was scheduled to expire). Disallowed amounts carry forward as NOL. 2026 threshold $256,000 / $512,000 MFJ — check the engine encodes it. | `ENGINE` |
| **§163(j) interest limitation** | Reverted to the more favorable **EBITDA-based** ATI computation (depreciation and amortization added back). | `VERIFY` |
| **§1202 QSBS** | Materially expanded for stock **acquired after 2025-07-04**: tiered exclusion (50% at 3 years, 75% at 4 years, 100% at 5 years), per-issuer cap raised **$10M → $15M** (greater of that or 10× basis, unchanged; $15M indexed for tax years beginning after 2026), gross-assets test raised **$50M → $75M** (indexed from 2027); unexcluded gain on 3- and 4-year sales taxed at 28% (tiers, caps, and applicable date confirmed against 26 U.S.C. §1202 text, 2026-09-23). §1045 (60-day rollover of QSBS held >6 months) is a deferral, not an exclusion. Operational tracking lives in `security/qsbs-compliance`, which uses these same figures. Stock acquired on or before 2025-07-04 keeps the old rules. **Critical to the timing of any spinout that expects QSBS** — the acquisition date decides which regime applies. | `ENGINE` |
| **§1400Z opportunity zones** | Made permanent with rolling 10-year zone designations beginning 2027. | `VERIFY` |
| **§127 educational assistance** | Made permanent; continues to cover student loan principal and interest. $5,250 indexed only after 2026. | `ENGINE` |
| **§45S paid leave credit** | Made permanent. | `VERIFY` |
| **§45F employer child care credit** | Cap $500,000 ($600,000 eligible small business) from 2026, indexed after 2026; confirm the new rates. | `VERIFY` |
| **§25C / §25D home energy credits** | **Terminated**: §25D for expenditures after 2025-12-31; §25C for property placed in service after 2025-12-31. Prior-year §25D carryforwards only. (verified 2026-09-23, IRS OBBB FAQs for §§25C/25D/25E/30D/45W) | `ENGINE` |
| **§30D / §25E / §45W clean vehicles** | **Terminated** for vehicles acquired after 2025-09-30 (binding contract + payment by that date still qualifies when placed in service later). (verified 2026-09-23, same IRS FAQs) | `ENGINE` |
| **§21 / §129 dependent care** | 2026+: §21 rate 50%, less 1 point per $2,000 AGI over $15,000 (floor 35%), then 1 point per $2,000 ($4,000 MFJ) over $75,000 ($150,000 MFJ), floor 20% (§21(a)(2)); §129 exclusion $5,000 → $7,500 ($3,750 MFS). Neither indexed. | `ENGINE` |
| 1099-NEC / 1099-MISC threshold | $600 → $2,000 for payments after 2025-12-31, indexed from 2027; backup withholding follows (Rev. Proc. 2025-32 §2.15). **Changes contractor reporting for every payer.** | `ENGINE` |
| Estate and gift | Basic exclusion $15,000,000 for 2026 (GST exemption the same), indexed from 2027. | `ENGINE` |
| Trump accounts | New children's accounts with a one-time $1,000 federal contribution for eligible children (irs.gov/trumpaccounts); confirm eligibility and timing before use. | `VERIFY` |
| Form 1099-K threshold | Restored to the old $20,000 / 200-transaction test. | `VERIFY` |

## What did *not* change (common false assumptions)

- **§280E** was not changed by OBBBA; it still applies to Schedule I/II
  trafficking. Rescheduling is administrative: a 2026-04-23 DOJ order moved
  FDA-approved and state-licensed *medical* marijuana products to Schedule III
  (outside §280E); adult-use marijuana remained Schedule I pending a hearing that
  began 2026-06-29 — confirm its status before use. A state that decouples
  changes the state result only.
- **§1031** remains **real property only**. Any entity summary still listing §1031
  against equipment or inventory is wrong post-TCJA and should not be relied on.
- **Corporate rate** stays 21% flat (§11). No change.
- **NOL rules** (§172): still 80%-of-taxable-income limited, indefinite
  carryforward, no carryback.
- **QSBS disqualified activities** (§1202(e)(3)) unchanged — **consulting,
  health, law, accounting, and financial services are still disqualified**, so
  stock in such a company does not qualify regardless of the new caps.

## How to use this file

1. Before asserting any 2025/2026 number or rule, check whether the topic appears
   above.
2. If it is marked `ENGINE`, pull the value from the `constants` binding and cite
   the revenue procedure recorded there.
3. If it is marked `VERIFY`, treat it as `RECALL` under the `irc-lookup` output
   convention — usable for planning discussion, **not** for a filed position
   until confirmed against primary text.
4. When you verify a `VERIFY` item against primary source, update this file and
   move it to `ENGINE` (or add the figure to the `constants` binding if the engine
   needs it).
