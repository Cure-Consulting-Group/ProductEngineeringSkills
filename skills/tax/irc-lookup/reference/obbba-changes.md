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

## Rates and the individual base

| Item | Change | Confidence |
|---|---|---|
| Individual rate schedule | TCJA's 10/12/22/24/32/35/37 made **permanent** — no 2026 snap-back to 39.6%. This is the single biggest planning assumption that changed. | `ENGINE` |
| Standard deduction | Permanently elevated and re-indexed. 2026: $16,100 single / $32,200 MFJ / $24,150 HoH. | `ENGINE` |
| Personal exemptions | Remain repealed. | `VERIFY` |
| Senior deduction | New $6,000/person age 65+, 2025–2028, phases out at 6% over $75k single / $150k MFJ. On **Schedule 1-A**; available to itemizers and non-itemizers. | `ENGINE` |
| Tips deduction | Up to $25,000, 2025–2028. Phases out $100 per $1,000 of MAGI over $150k/$300k. **MFS ineligible** — must file MFJ if married. | `ENGINE` |
| Overtime premium deduction | Up to $12,500 single / $25,000 MFJ, 2025–2028, same phase-out mechanics. MFS ineligible. | `ENGINE` |
| Car loan interest | Up to $10,000 on loans for **new US-assembled personal-use vehicles**. Phases out $200 per $1,000 over $100k/$200k. **Leases do not qualify.** | `ENGINE` |
| SALT cap | Raised from $10,000 to $40,000 (2025), $40,400 (2026), indexed thereafter; **phases down 30% of MAGI over ~$505k (2026) to a $10,000 floor**. Reverts to flat $10,000 in 2030. | `ENGINE` |
| PTET workaround | **Preserved** — proposals to limit pass-through entity tax deductions for SSTBs did not survive. State PTET elections remain the primary SALT workaround. | `VERIFY` |
| Child tax credit | $2,200 base (from $2,000), $1,700 refundable, indexed going forward. | `ENGINE` |
| AMT | Exemption phase-out **thresholds reset down** to $500k/$1M and the phase-out **rate doubled from 25% to 50%** starting 2026 — this pulls more upper-middle earners into AMT than the pre-OBBBA path. | `ENGINE` |
| Itemized deduction limitation | New limitation reducing the benefit of itemized deductions for taxpayers in the 37% bracket (effectively capping benefit near 35%). | `VERIFY` |
| Charitable deduction | New above-the-line deduction for non-itemizers; new 0.5%-of-AGI floor for itemizers. | `VERIFY` |

## Business provisions

| Item | Change | Confidence |
|---|---|---|
| **§174 / §174A R&E** | Immediate domestic R&E expensing **restored** for tax years beginning after 2024. Foreign R&E still amortized over 15 years. Small businesses (gross receipts ≤ ~$31M) may apply retroactively to 2022–2024; unamortized 2022–2024 domestic amounts may be recovered over 1 or 2 years. **Directly relevant to any in-house product development.** | `VERIFY` |
| **§168(k) bonus** | 100% bonus made **permanent** for property acquired after 2025-01-19. No more phase-down schedule. | `ENGINE` |
| **§179 expensing** | Limit raised to $2.5M (2025) / $2.56M (2026); phase-out threshold $4M / $4.09M. | `ENGINE` |
| **§168(n) qualified production property** | New 100% expensing for **nonresidential real property used in manufacturing/production**, construction beginning after 2025-01-19 and before 2029. **Potentially large for any entity that acquires or builds production space — but only if the activity is genuinely manufacturing.** | `VERIFY` |
| **§199A QBI** | Made permanent. Phase-in range **widened** to $75k single / $150k MFJ (from $50k/$100k), which softens the SSTB cliff. New **$400 minimum deduction** when active QBI ≥ $1,000 (2026+). | `ENGINE` |
| **§461(l) excess business loss** | Made **permanent** (was scheduled to expire). Disallowed amounts carry forward as NOL. 2026 threshold indexed — **confirm the exact figure**, and check whether the engine encodes it at all. | `VERIFY` |
| **§163(j) interest limitation** | Reverted to the more favorable **EBITDA-based** ATI computation (depreciation and amortization added back). | `VERIFY` |
| **§1202 QSBS** | Materially expanded for stock **acquired after 2025-07-04**: tiered exclusion (50% at 3 years, 75% at 4 years, 100% at 5 years), per-issuer cap raised **$10M → $15M** (indexed after 2026), gross-assets test raised **$50M → $75M**. Stock acquired on or before 2025-07-04 keeps the old rules. **Critical to the timing of any spinout that expects QSBS** — the acquisition date decides which regime applies. | `VERIFY` |
| **§1400Z opportunity zones** | Made permanent with rolling 10-year zone designations beginning 2027. | `VERIFY` |
| **§127 educational assistance** | Made permanent and indexed; continues to cover student loan principal and interest. | `VERIFY` |
| **§45S paid leave credit** | Made permanent. | `VERIFY` |
| **§45F employer child care credit** | Increased. | `VERIFY` |
| 1099-NEC / 1099-MISC threshold | Raised from $600 to $2,000 (indexed), effective for payments after 2025. **Changes contractor reporting obligations for every payer.** | `VERIFY` |
| Form 1099-K threshold | Restored to the old $20,000 / 200-transaction test. | `VERIFY` |

## What did *not* change (common false assumptions)

- **§280E** still disallows deductions for cannabis businesses at the federal
  level. Rescheduling was not enacted by OBBBA. A state that decouples changes the
  state result only — the federal posture is unchanged.
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
