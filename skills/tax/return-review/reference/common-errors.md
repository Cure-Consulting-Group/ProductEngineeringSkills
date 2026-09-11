# Common Error Catalog

Ranked by expected cost = frequency × severity. Each carries a detection test.

## Tier 1 — Expensive and common

| # | Error | Detection test | Cost |
|---|---|---|---|
| 1 | **Missing or unsupported basis** | Ask for the basis schedule. If it does not exist as a document, the error is present. | Total disallowance of losses; burden is on the taxpayer |
| 2 | **Carryforwards lost between years** | Compare this year's opening carryforwards to last year's closing. Any silent zero is the error. | Permanent loss of NOLs, credits, suspended losses |
| 3 | **1099s not reconciled to revenue** | Sum 1099s; compare to gross receipts; demand a written explanation of the difference. | AUR notice; understatement penalties |
| 4 | **Unreasonable S corp officer comp** | Compare W-2 wages to distributions and to a benchmark. | Recharacterization + payroll tax + penalties |
| 5 | **§274(d) items without contemporaneous records** | Ask to see the mileage log or meal attendee notes. "I can reconstruct it" = the error. | Total disallowance; Cohan unavailable |
| 6 | **Depreciation schedule not reconciled** | Prior schedule + additions − disposals ≠ current. | Wrong deduction both directions; recapture errors on sale |
| 7 | **Personal expenses in business accounts** | Scan the ledger for categories with no business nexus. | Disallowance + negligence penalty + credibility loss on everything else |

## Tier 2 — Frequently missed money

| # | Error | Detection test |
|---|---|---|
| 8 | **R&D credit under-claimed (no wage QREs)** | Credit claimed but no payroll exists. Extremely common at founder-run software companies. |
| 9 | **§41(h) payroll offset not elected** | Credit carrying forward at a company with no tax liability. |
| 10 | **Retirement contribution not maximized** | Compare actual contribution to the computed limit from net SE earnings. |
| 11 | **Home office not claimed or under-claimed** | Business exists, works from home, no Form 8829 and no simplified deduction. |
| 12 | **QBI deduction missed or mis-limited** | Pass-through income present, §199A line blank or not tested against the wage/UBIA limit. |
| 13 | **PTET election not made** | State tax paid personally on pass-through income while a PTET regime exists. |
| 14 | **Startup costs expensed instead of §195** | Pre-operating entity showing §162 deductions for non-R&E pre-opening costs. Check the business-begins date, while classifying qualifying R&E under §174A even before revenue begins. |
| 15 | **§1244 papers never prepared** | New entity, no §1244 documentation at issuance. Free option forfeited. |

## Tier 3 — Technical errors

| # | Error | Detection test |
|---|---|---|
| 16 | Wrong tax year constants | Pass the tax year explicitly to every `calculator`/`constants` call; never rely on an engine default. |
| 17 | SE tax on the wrong base | Net earnings must be net profit × 0.9235. |
| 18 | Half of SE tax not deducted | §164(f) line blank while Schedule SE has an amount. |
| 19 | State decoupling ignored | State return simply importing the federal number. NY decouples from §280E; state §179/bonus conformity varies. |
| 20 | Phase-outs not applied | AGI above a threshold with the full benefit claimed — SALT phase-down, CTC, tips, overtime, senior deduction. |
| 21 | Wash sales not adjusted | 1099-B disallowed-loss column ignored; IRA repurchases invisible to the broker. |
| 22 | Basis missing on noncovered lots | 1099-B shows blank basis and the return reports zero. |
| 23 | Installment sale recapture spread | §1245 recapture must be fully recognized in year one (§453(i)). |
| 24 | Meals at 100% | The restaurant provision expired after 2022. 50% under §274(n). |
| 25 | Entertainment deducted | 0% since 2018 (§274(a)). |
| 26 | Miscellaneous itemized deductions claimed | Repealed and now permanent — unreimbursed employee expenses, advisory fees, tax prep. |
| 27 | §1031 on personal property | Real property only since 2018. Entity summaries and older planning notes still carry this error — check the source before relying on it. |
| 28 | AMT not computed | Especially now — OBBBA reset the 2026 phase-out threshold down and doubled the rate to 50%. |
| 29 | Guarantee treated as debt basis | S corp shareholder guarantee creates no basis (§1366(d)). |
| 30 | Schedule 1-A deductions treated as itemized | Tips, overtime, senior, and car loan interest are additive to standard or itemized. |

## Tier 4 — Process failures

| # | Error | Why it matters |
|---|---|---|
| 31 | No position memo for a non-routine item | Guts the §6664(c) reasonable-cause defense |
| 32 | Return questions left blank | SSTS No. 2 violation |
| 33 | Estimate used for a strict-substantiation item | SSTS No. 4 violation; disallowance |
| 34 | Diagnostic accepted with no explanation | An open item in disguise |
| 35 | Review performed in the same pass as preparation | No independent control existed |
| 36 | Election statement missing from the file | The election may not have been made at all |
| 37 | Entity name wrong on a contract or 1099 | Undermines §351 and §482 positions, and it is pervasive wherever entities were formed faster than the paperwork. |

## Watch list by entity role

Build the group's own version of this table in the tax profile, then review each
return against its row.

| Role | Watch for |
|---|---|
| **Services hub** | Zero wage QREs; §41(h) not elected; unpapered intercompany fees; §531 as retained earnings grow; personal-service-corporation classification |
| **Product spoke** | §83(b) 30-day clock; IP transferred after value accrued; gross-assets evidence not captured at issuance; §1202(e) qualified-trade analysis never written |
| **Inventory business** | §183 exposure from consecutive losses; inventory capitalization and ending inventory that does not match the story; reflexive bonus depreciation in a loss year; §1031 misapplication |
| **Regulated / pre-licence** | §162 deductions before the business begins; §280E ignored in modeling; business-begins date undocumented |
| **S corporation** | Stock and debt basis schedules missing; guarantee mistaken for debt basis; losses deducted past basis; officer compensation of zero |
