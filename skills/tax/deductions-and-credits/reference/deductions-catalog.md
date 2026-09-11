# Deduction Catalog

`[constants]` = do not read the figure off this page; pull it for the filing year
from the project's `constants` binding, or from the governing Rev. Proc. via
`irc-lookup`.

## Tier 1 — Above-the-line (§62 adjustments)

These reduce AGI, which cascades into every AGI-sensitive phase-out. Always
maximize these before itemized deductions.

| Deduction | Section | Test / limit |
|---|---|---|
| **Self-employed retirement** | §404(a)(8), §401(c) | Largest lever available. SEP: 25% of net SE income (effectively 20% of net SE earnings after the SE-tax adjustment), cap `[constants]` $72,000 (2026). Solo 401(k): employee deferral `[constants]` $24,500 + $8,000 catch-up at 50, plus employer share, total cap $72,000. Defined benefit: up to `[constants]` $290,000 for older high earners. |
| **Self-employed health insurance** | §162(l) | 100% of premiums for taxpayer, spouse, dependents, and children under 27. **Limited to net SE income** from the business, and **not available for any month eligible for subsidized employer coverage** (including a spouse's plan). Does **not** reduce SE tax. For a >2% S-corp shareholder, premiums must run through W-2 wages (§1372) to qualify. |
| **HSA contribution** | §223 | `[constants]` 2026: $4,400 self / $8,750 family, +$1,000 catch-up at 55. Requires HDHP coverage and no disqualifying coverage. Deductible even without itemizing; triple-tax-advantaged. |
| **One-half of SE tax** | §164(f) | Automatic — 50% of the §1401 tax. |
| **Educator expenses** | §62(a)(2)(D) | Small; screen only if applicable. |
| **Student loan interest** | §221 | Up to $2,500, phased out by MAGI. |
| **Early withdrawal penalty** | §62(a)(9) | Forfeited CD interest. |
| **Alimony (pre-2019 decrees only)** | §215 | Repealed for post-2018 agreements. |

## Tier 2 — Business deductions (§162)

Reduce income **and** SE tax for a sole proprietor / partner. The general test is
**ordinary** (common in the trade) **and necessary** (appropriate and helpful) —
plus the expense must be for a trade or business *carried on* (§183 profit motive).

### Commonly missed
| Deduction | Section | Notes |
|---|---|---|
| **Home office** | §280A(c) | Requires **exclusive and regular use** as the principal place of business or a place to meet clients. Two methods: **simplified** ($5/sq ft up to 300 sq ft = $1,500 max) or **actual** (allocated mortgage interest/rent, insurance, utilities, repairs, depreciation). Actual usually wins for a real office. Limited to net business income; excess carries forward. |
| **Vehicle / mileage** | §162, §274(d) | `[constants]` 2026 standard rate 72.5¢/mi business. Actual-expense method requires business-use percentage. **Once you use actual + accelerated depreciation on a vehicle you cannot switch back to standard.** §274(d) strict substantiation applies: contemporaneous mileage log with date, miles, destination, purpose. Commuting is never deductible. |
| **Startup costs** | §195 | **$5,000 deducted in year one, reduced dollar-for-dollar by startup costs over $50,000; remainder amortized over 180 months** beginning with the month the business begins. Non-R&E costs incurred *before* the business begins are not §162 expenses — they are §195. Qualifying R&E is §174A even in a pre-revenue entity with a realistic prospect of entering the business the research serves. |
| **Organizational costs** | §248 (corp) / §709 (partnership) | Same $5,000 / $50,000 / 180-month mechanics for incorporation, charter, and organizational meeting costs. Legal fees to *issue stock* are neither — they reduce paid-in capital. |
| **R&E expenditures** | §174A | Domestic R&E **immediately deductible** for tax years beginning after 2024 (OBBBA restoration). Foreign R&E still 15-year. Software development is R&E. Coordinate with the §41 credit and the §280C(c) election. |
| **Business meals** | §274(n) | **50% deductible.** The 100% restaurant provision expired after 2022 — do not apply it. Requires: business purpose, taxpayer or employee present, not lavish, and the attendees documented. **Entertainment is 0%** (§274(a)) — a client dinner is a 50% meal, a client's ballgame ticket is nondeductible. |
| **Travel** | §162(a)(2), §274(d) | Deductible when **away from tax home overnight** for business. Primarily-business trips: transportation fully deductible, personal days' lodging/meals not. Strict substantiation. |
| **Education** | Reg. §1.162-5 | Deductible if it **maintains or improves skills in the present business**. Not deductible if it qualifies you for a **new** trade or business (the classic MBA/law-school denial). |
| **Bad debts** | §166 | Business bad debt: ordinary deduction, partial worthlessness allowed. Nonbusiness: short-term capital loss, total worthlessness only. Requires a bona fide **debt** — an unpaid receivable on the cash method has no basis and is not deductible. |
| **Interest** | §163 | Business interest deductible; limited by §163(j) only above the gross-receipts threshold (small businesses exempt). Trace loan proceeds to their use (Reg. §1.163-8T) — the *use* of the money determines the character, not the collateral. |
| **Insurance** | §162 | Liability, E&O, cyber, malpractice. Note: premiums on a policy where the business is the beneficiary of officer life insurance are **not** deductible (§264). |
| **Professional fees** | §162 | Legal and accounting. **But** fees to acquire an asset or to defend title get capitalized (§263), and fees allocable to tax-exempt income are disallowed (§265). |
| **Software / SaaS** | §162 or §179 | Subscriptions expensed; purchased software may be §179'd. |
| **Section 179 expensing** | §179 | `[constants]` 2026: $2.56M limit, $4.09M phase-out threshold. **Limited to business taxable income** — cannot create a loss; excess carries forward. Requires property placed in service and used >50% for business. |
| **Bonus depreciation** | §168(k) | **100% permanent** for property acquired after 2025-01-19. Unlike §179, **can create a loss**. Applies automatically unless you elect out by class. |
| **Qualified production property** | §168(n) | 100% expensing for nonresidential real property used in manufacturing — construction begun after 2025-01-19, before 2029. *Screen any entity acquiring or building production space — and confirm the activity is genuinely manufacturing, not retail.* |

### Employer-side
| Deduction | Section |
|---|---|
| Wages and salaries | §162(a)(1) — must be reasonable; use the `reasonable-compensation` binding where available |
| Employer retirement contributions | §404 |
| Employer health premiums | §162, §106 |
| Payroll taxes | §164(a) |
| Educational assistance ≤ $5,250 | §127 (permanent, indexed; covers student loan payments) |
| Accountable-plan reimbursements | Reg. §1.62-2 — deductible to the entity, **excluded** from employee income. Requires business connection, substantiation within a reasonable time, and return of excess. Without a plan, reimbursements are taxable wages. |

## Tier 3 — OBBBA Schedule 1-A deductions (2025–2028)

**Available in addition to the standard deduction or itemized deductions.** Do
not treat these as itemized. All `[constants]`.

| Deduction | 2026 amount | Phase-out |
|---|---|---|
| Qualified tips | $25,000 | $100 per $1,000 MAGI over $150k / $300k. **MFS ineligible.** |
| Overtime premium | $12,500 single / $25,000 MFJ | Same mechanics. **MFS ineligible.** |
| Senior (65+) | $6,000 per person | 6% of MAGI over $75k / $150k |
| Car loan interest | $10,000 | $200 per $1,000 over $100k / $200k. **New US-assembled vehicles only; leases do not qualify.** |

Capture the applicable income, age, and eligibility inputs in the project's tax
profile before computing these deductions.

## Tier 4 — Itemized (§63(d)) — only if the total beats `[constants]` standard

| Deduction | Section | Limit |
|---|---|---|
| **State and local taxes** | §164 | `[constants]` 2026 cap $40,400 ($20,200 MFS), **phasing down 30% of MAGI over ~$505,000 to a $10,000 floor**. Election between income tax and sales tax. **PTET payments made by the entity bypass the cap entirely** — see `tax-strategies`. |
| **Mortgage interest** | §163(h) | Acquisition indebtedness up to $750,000 ($375,000 MFS) for post-2017 debt; $1M grandfathered. Home equity interest deductible only if used to buy/build/improve the residence. |
| **Charitable contributions** | §170 | 60% of AGI for cash to public charities, 30% for appreciated property (deducted at FMV if long-term capital gain property), 5-year carryforward. **New 0.5%-of-AGI floor under OBBBA — `VERIFY`.** Contributions ≥$250 need a contemporaneous written acknowledgment; >$5,000 non-cash needs a qualified appraisal. |
| **Medical** | §213 | Only the excess over **7.5% of AGI**. Rarely clears in a high-income year. |
| **Casualty losses** | §165(h) | **Federally declared disaster areas only** post-2017. |
| **Investment interest** | §163(d) | Limited to net investment income; carries forward. |
| **Gambling losses** | §165(d) | To the extent of winnings. **OBBBA limited this to 90% of losses — `VERIFY`.** |

**Repealed through 2025 and made permanent by OBBBA**: miscellaneous itemized
deductions subject to the 2% floor (unreimbursed employee expenses, investment
advisory fees, tax prep fees). Do not claim these.

## Tier 5 — Exclusions (better than deductions)

| Exclusion | Section | Note |
|---|---|---|
| **§280A(g) "Augusta rule"** | §280A(g) | Rent your residence to your business for **≤14 days per year**: the entity deducts, you exclude the income entirely. Requires documented FMV (comparable venue quotes), a written lease, a genuine business purpose (board meetings), and minutes. See `tax-strategies`. |
| Employer health coverage | §106 | |
| HSA distributions for medical | §223(f) | |
| §127 educational assistance | §127 | $5,250 |
| De minimis fringe, working condition fringe | §132 | |
| **QSBS gain** | §1202 | The largest exclusion in the Code — see `tax-strategies`. |
| Principal residence gain | §121 | $250k / $500k MFJ, 2-of-5-year ownership and use. |
| Municipal bond interest | §103 | Watch: still counts for Social Security taxability and IRMAA. |
