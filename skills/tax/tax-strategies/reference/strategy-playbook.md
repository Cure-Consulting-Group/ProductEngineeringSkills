# Strategy Playbook

Risk ratings: **Conservative** (settled authority, routine) · **Moderate**
(supported, fact-dependent, document carefully) · **Aggressive** (defensible but
contested; expect scrutiny, consider disclosure).

---

## A. Entity structure & character conversion

### A1. S-corp election to reduce self-employment tax — **Moderate**
- **Mechanism**: Character. Net profit of an LLC/sole prop is 100% subject to
  15.3% SE tax (§1401). As an S corp, only **reasonable W-2 wages** bear
  FICA; the residual distribution does not.
- **Requirements**: §1361 eligibility (≤100 shareholders, one class of stock, no
  ineligible shareholders); Form 2553 within 2 months 15 days; **actual payroll
  with withholding and 941s**; reasonable compensation supported by a study.
- **Quantification**: (Net profit − reasonable wage) × 15.3% up to the wage base
  `[constants]` $184,500 (2026), then × 2.9% (+0.9% over the Additional Medicare
  threshold). Net of payroll admin cost (~$1,500–3,000/yr) and lost §199A W-2 wage
  base effects.
- **Trap**: Understating the wage is the #1 S-corp audit issue. The IRS
  recharacterizes distributions as wages with payroll tax, interest, and
  penalties. Also: §199A's W-2 wage limitation means an artificially low wage can
  *reduce* the QBI deduction, partially offsetting the savings.
- **Tooling**: the `reasonable-compensation` binding, where the project has one.
  Whatever produces the number, the file needs comparable-salary evidence behind
  it — the figure alone does not defend itself.
- **Deadline**: Form 2553 by 3/15 for a calendar-year election.

### A2. C-corp for rate arbitrage and reinvestment — **Conservative**
- **Mechanism**: Entity. 21% flat (§11) vs up to 37% individual + 3.8% NIIT.
- **Works when**: earnings are **retained and reinvested**, not distributed.
  Distributed earnings suffer double tax (21% + 20% QDI + 3.8% NIIT ≈ 39.8%).
- **Guardrails**: §531 accumulated earnings tax — 20% penalty on earnings retained
  beyond the reasonable needs of the business over the $250,000 credit ($150,000
  for personal service corporations). Document reasonable business needs
  (Bardahl-style working capital analysis, expansion plans) in board minutes.
  §541 personal holding company tax if 60%+ of income is passive and 5 or fewer
  shareholders own >50%.
- **Where it fits**: correct for a studio or holding company that reinvests
  earnings into new products rather than distributing them.

### A3. Spoke-level QSBS structuring — **Moderate**, high value
- **Mechanism**: Exclusion. §1202 excludes gain on qualified small business stock.
- **Requirements** (all must hold):
  - **C corporation**, domestic, at original issuance to the taxpayer (not
    purchased from another holder)
  - **Gross assets ≤ $75M** (indexed annually — confirm for the tax year via the
    `constants` binding) (OBBBA, from $50M) at all times before and immediately
    after issuance — `VERIFY`
  - **Active business test**: ≥80% of assets used in a **qualified** trade or
    business. §1202(e)(3) **disqualifies**: health, law, engineering,
    architecture, accounting, actuarial science, performing arts, consulting,
    athletics, financial services, brokerage, and any business whose principal
    asset is the reputation or skill of its employees.
  - **Holding period**: post-2025-07-04 stock — 50% at 3 years, 75% at 4 years,
    100% at 5 years. Pre-2025-07-05 stock — 100% at 5 years only. `VERIFY`
  - **Cap**: greater of **$15M** (OBBBA, indexed after 2026; $10M for older
    stock) or **10× aggregate adjusted basis**.
- **Critical structural implication**: a **consulting, health, law, accounting,
  or financial-services company is a disqualified trade or business under
  §1202(e)(3)** — its own stock can never be QSBS, no matter how long it is held.
  In a hub-and-spoke group this means QSBS has to live at the *spoke* level: each
  product company held as a **sibling C-corp owned directly by the founders**,
  not as a subsidiary of the services hub. Decide this at formation; it cannot be
  retrofitted without a taxable reorganization.
- **Timing**: the clock starts at **issuance**. Every month of delay in forming
  and issuing is a month added to the exit horizon.
- **Redemption traps**: §1202(c)(3) — significant redemptions from the issuer
  within a 2-year window around issuance (or 4-year for related-party) can taint
  the stock entirely. Check before any buyback.
- **Documentation**: capture gross assets at issuance contemporaneously; you
  cannot reconstruct it a decade later.

### A4. §1045 rollover — **Conservative**
- Sell QSBS held **>6 months** and reinvest the proceeds in new QSBS within
  **60 days**; gain deferred, holding period tacks.
- Rescue valve when an exit happens before the 5-year (or tiered) mark.

### A5. §1244 ordinary loss on small business stock — **Conservative**
- Up to **$50,000 ($100,000 MFJ) per year** of loss on qualifying stock treated as
  **ordinary** rather than capital — deductible against wage income instead of
  being trapped behind the $3,000 capital loss limit.
- Requires: domestic corporation, ≤$1M of aggregate capital at issuance, stock
  issued for money or property, >50% of gross receipts from operations for 5 years.
- **Free option** — costs nothing to qualify at formation, and the paperwork must
  exist *at issuance*. Do this for every new entity.

### A6. §351 tax-free contribution of IP to a new entity — **Conservative**
- Transfer property to a corporation solely for stock, with the transferors in
  **80% control** immediately after → no gain recognized.
- **Sequencing**: a hub → newco IP assignment must be structured and papered
  **before** value accrues — before the trademark filing, the first regulated
  agreement, and first revenue. IP transferred *after* it has value may be a
  taxable sale or a §482 allocation event rather than a clean contribution.
  Services contributed for stock are **taxable** (§351(d)) — only property qualifies.

### A7. Transfer pricing on hub→spoke services — **Moderate**
- §482 requires arm's-length pricing between commonly controlled entities.
- A hub charging its spokes a services fee moves income to the hub (21% C-corp
  rate) and gives each spoke a deduction. Both directions are examinable, and the
  examiner will ask to see the agreement and the payments.
- **Requirements**: written intercompany services agreement, a defensible method
  (cost-plus is standard for routine back-office services — typically cost plus a
  markup benchmarked to comparables), and contemporaneous documentation.
- The **services cost method** may allow a zero markup for specified low-margin
  covered services — `VERIFY` applicability.

---

## B. Compensation & payroll

### B1. Reasonable compensation calibration — **Moderate**
- Set W-2 wage at the defensible floor, not the minimum imaginable. Factors:
  training and experience, duties and hours, comparable pay for similar services,
  dividend history, payments to non-shareholder employees, and what a comparable
  business would pay (*Watson v. United States*, 8th Cir. 2012 — $24k recharacterized
  to $91k).
- Document with a comp study before the year, not after the notice.

### B2. Accountable plan — **Conservative**, universally underused
- Reg. §1.62-2: entity reimburses employee business expenses → **deductible to the
  entity, excluded from the employee's income, no payroll tax**.
- Requires: business connection, substantiation within a reasonable time (60-day
  safe harbor), return of excess (120-day safe harbor), and a **written plan**.
- Converts otherwise-nondeductible personal outlays (home office as an employee,
  personal phone, personal vehicle) into pre-tax dollars — the only mechanism left
  after §67(g) killed unreimbursed employee expenses.

### B3. Family employment — **Moderate**
- Wages to a child for **actual services at a reasonable rate** are deductible to
  the business and taxed to the child (often at 0% up to the standard deduction),
  and can fund a Roth IRA with earned income.
- **Sole proprietorship or a partnership owned solely by the parents**: wages to a
  child under 18 are exempt from FICA and under 21 from FUTA (§3121(b)(3)(A)).
  **This exemption does not apply if the business is a corporation** — wages paid
  by a corporation to a child bear full payroll tax.
- Requires: real work, timesheets, W-2, and a rate a stranger would receive.
  Assignment-of-income doctrine kills the arrangement if the work is fictional.

### B4. §127 educational assistance — **Conservative**
- Up to $5,250/year, deductible to the entity and excluded to the employee.
  Permanent and indexed under OBBBA; **covers student loan principal and interest**.
- Requires a written plan, no more than 5% of benefits to >5% owners
  (the owner-concentration test is the binding constraint in a one-person company).

---

## C. Retirement — the largest single deduction available

### C1. Solo 401(k) stacking — **Conservative**
- Employee deferral `[constants]` $24,500 (2026) + $8,000 catch-up at 50, **plus**
  employer profit sharing (25% of comp for a corp; ~20% of net SE income for a
  sole prop), total cap `[constants]` $72,000 (2026; +catch-up).
- Beats a SEP for the same income because the employee deferral is not limited by
  the 25% test.
- **Deadline**: plan must be **adopted by year end** for employee deferrals
  (employer contributions can be funded through the extended due date).

### C2. Defined benefit / cash balance plan — **Moderate**
- For a consistently profitable owner over ~45 with high income, deductible
  contributions can reach `[constants]` $290,000 (2026) in benefit-level funding — far
  beyond DC limits.
- Requires an actuary, a multi-year funding commitment, and coverage of eligible
  employees. Expensive; only worth it above roughly $250k–300k of stable profit.
- Can be paired with a solo 401(k) (combined plan limits apply).

### C3. Backdoor and mega-backdoor Roth — **Moderate**
- Backdoor: nondeductible IRA contribution → Roth conversion. **§408(d)(2)
  pro-rata rule aggregates all traditional IRAs** — a pre-existing pre-tax IRA
  balance makes most of the conversion taxable. Fix by rolling pre-tax IRA
  balances into a 401(k) first.
- Mega-backdoor: after-tax 401(k) contributions up to the §415(c) total limit, then
  in-plan Roth conversion. Requires the plan document to permit after-tax
  contributions and in-service distributions.

### C4. Roth conversion in a loss year — **Conservative**, high leverage
- Convert traditional to Roth in a year with an NOL, a low-income year, or before
  a large income year. Fills up low brackets at 10/12/22% permanently.
- **Where it fits**: loss years and the pre-revenue phase of a young entity are
  exactly the window for this — the bracket space is temporary and unused. Model
  it through the `retirement` binding before executing.
- Recharacterization of conversions was repealed — **the conversion is
  irrevocable**, so model carefully before executing.

---

## D. Depreciation & fixed assets

### D1. §179 vs §168(k) bonus — choose deliberately — **Conservative**
| | §179 | §168(k) bonus |
|---|---|---|
| Rate | Elective amount | 100% (permanent post-OBBBA) |
| Can create a loss? | **No** — limited to business taxable income | **Yes** |
| Elective per asset? | Yes, asset by asset | Elect out **by class**, all-or-nothing |
| State conformity | Often decoupled | Often decoupled |
- Use §179 when you want precision (e.g. stop at the point where the next dollar
  of deduction is worth less than a future dollar). Use bonus when you want the
  loss for an NOL or a §461(l) carryforward.
- **Do not blindly expense everything.** In a low-bracket or loss year, deductions
  are worth less than they will be later. Depreciating slowly can beat expensing.

### D2. Cost segregation — **Moderate**
- Engineering study reallocating a building's basis to 5/7/15-year property, which
  is then bonus-eligible. Only relevant once real property is owned.
- Cost ~$5k–15k; worth it above roughly $500k of building basis.
- Triggers §1245 recapture at ordinary rates on sale — a timing play, not free.

### D3. §168(n) qualified production property — **Moderate**, `VERIFY`
- 100% expensing of **nonresidential real property used in manufacturing**,
  construction begun after 2025-01-19 and before 2029.
- **Screen any entity that acquires or builds production space.** This is a new
  and unusually large provision — and it turns on the activity genuinely being
  manufacturing or production, not on how the business describes itself.

### D4. De minimis safe harbor — **Conservative**
- Reg. §1.263(a)-1(f): expense items up to **$2,500 per invoice or item** ($5,000
  with an applicable financial statement) instead of capitalizing.
- Requires a **written capitalization policy in place at the beginning of the tax
  year**. Free money; the only cost is writing the policy once.

---

## E. State & local

### E1. PTET election (NY) — **Conservative**, largest SALT lever
- **Mechanism**: The pass-through entity pays state tax at the entity level and
  deducts it as a business expense (fully deductible, not subject to the §164
  cap); the owner takes a state credit. Blessed by **Notice 2020-75**, and
  **preserved by OBBBA**.
- **NY deadline: March 15 of the tax year** — annual, irrevocable, and there is no
  late relief. Missing it forfeits the entire benefit for that year.
- Applies to LLCs, partnerships, and S corps — **not** to a C corp, which already
  deducts its state tax. Relevant to any pass-through in the group once it
  produces income; irrelevant while it has none.
- Model it through the `salt` binding before the election date.

### E2. SALT cap phase-down management — **Conservative**
- The OBBBA cap phases down 30% of MAGI over `[constants]` ~$505,000 (2026) to a
  $10,000 floor. Between the threshold and the floor there is an effective
  **marginal rate spike**. Managing MAGI across the threshold (timing income,
  retirement contributions, charitable bunching) is worth real money in that band.

### E3. Residency and multi-state allocation — **Moderate**
- NY residency audits are aggressive; the **183-day + permanent place of abode**
  statutory residence test catches people who believe they moved. Domicile change
  requires demonstrable change in the "leave and land" factors.
- Model with the project's multi-state allocation and relocation steps, if it has
  them.

---

## F. Timing

### F1. Charitable bunching + donor-advised fund — **Conservative**
- Concentrate multiple years of giving into one year to clear the standard
  deduction, take the standard deduction in the off years. A DAF gives the
  deduction on funding while distributions to charities happen later.
- Donate **appreciated long-term securities**, not cash: deduct FMV **and** avoid
  the built-in capital gain. Never donate depreciated property — sell it, take the
  loss, donate cash.
- Model the interaction through the `salt` binding, where the project has one.

### F2. Income and expense timing — **Conservative**
- Cash-method: defer year-end invoicing, prepay deductible expenses subject to the
  **12-month rule** (Reg. §1.263(a)-4(f) — the benefit cannot extend beyond the
  earlier of 12 months or the end of the next tax year).
- **Only valuable if the rate differs between the years.** With permanent TCJA
  rates under OBBBA, the old "defer because rates snap back in 2026" logic is
  dead — that assumption must be removed from any pre-2025 plan.

### F3. Tax-loss harvesting — **Conservative**
- Realize capital losses to offset gains; $3,000/yr against ordinary income;
  indefinite carryforward.
- **§1091 wash sale**: 30 days before and after, substantially identical
  securities, **including purchases in an IRA** (which permanently destroys the
  loss rather than deferring it).

### F4. Installment sale (§453) — **Moderate**
- Spread gain over the years payments are received; keeps a large gain from
  spiking into the 20% capital gain bracket and the NIIT.
- **Does not apply** to inventory, dealer property, or depreciation recapture
  (§1245/§1250 recapture is recognized entirely in year one).
- Electing out may be better when rates are rising or the buyer's credit is weak.

---

## G. Business-specific

### G1. §280A(g) Augusta rule — **Aggressive**, well-known to examiners
- Rent your residence to your entity **≤14 days/year**: entity deducts, individual
  excludes the income entirely.
- **Requirements that are actually enforced**: documented FMV from ≥3 comparable
  venue quotes, a written lease, a genuine business purpose (real board or
  strategy meetings with agendas and minutes), and the days counted correctly.
- Rate must be defensible — inflated rates (e.g. $3,000/day for a home office in a
  residential neighborhood) are what generate assessments.
- 14 days is a hard cliff: the 15th day makes **all** of the rent taxable.

### G2. §174A + §41 coordination — **Conservative**, high value here
- Domestic R&E immediately deductible again (OBBBA), *and* eligible for the §41
  credit. Take the §280C(c) reduced-credit election or reduce the deduction.
- Small businesses may retroactively apply §174A to 2022–2024 and recover
  previously capitalized amounts over 1 or 2 years — **check whether the entity
  has unamortized 2022–2024 domestic R&E on the books.** `VERIFY`
- Product development is R&E. For most young software companies the blocker is not
  eligibility — it is the absence of wage QREs, because the engineering was done
  by uncompensated founders.

### G3. §195 startup cost sequencing — **Conservative**
- Pre-operating entities split their spend: qualifying R&E is §174A when there is
  a realistic prospect of entering the business the research serves; non-R&E
  pre-opening costs accumulate under §195, not §162. The **business-begins date**
  controls only the §195-versus-§162 boundary, and it is a factual determination.
- An entity waiting on a licence or approval is in exactly this posture:
  administrative limbo, \$0 revenue, costs accruing. Track qualifying development
  under §174A and the remaining startup spend under §195; fix the start date when
  the approval resolves. Do not deduct non-R&E startup costs currently as §162.

### G4. §183 hobby-loss defense — **Moderate**, mandatory here
- 3-of-5 profitable years creates a **presumption of profit motive**; failing it
  does not automatically lose, but it shifts the practical burden.
- Nine factors (Reg. §1.183-2(b)): businesslike manner, expertise, time and
  effort, appreciation expectation, prior success, history of income/losses,
  amount of occasional profit, financial status, personal pleasure.
- The exposure is any activity with consecutive losses and a personal-interest
  product — the combination is what draws the examination. Mitigation now, not at
  audit — written business plan,
  separate books and bank account, documented pricing changes to reach
  profitability, time logs, and a Form 5213 election to postpone determination if
  appropriate.

### G5. §280E management (cannabis) — **Conservative** in approach
- §280E disallows all deductions and credits except **cost of goods sold** for a
  business trafficking in a controlled substance. Federal rescheduling was not
  enacted by OBBBA.
- The only legitimate lever is careful, defensible **COGS maximization under
  §471** — inventoriable costs are recovered, operating expenses are not. Separate
  any genuinely non-trafficking line of business into its own entity with its own
  books.
- Never model a trafficking business as a normal deduction-bearing business; the deductions it appears to have mostly do not exist.

---

## H. Exit planning

### H1. QSBS stacking and packing — **Aggressive**, `VERIFY` before use
- **Stacking**: gifting QSBS to non-grantor trusts or family members, each of whom
  has their own per-issuer cap. Requires real, completed gifts with gift-tax
  consequences and no retained control.
- **Packing**: contributing appreciated assets pre-issuance to increase basis and
  thereby the 10× cap.
- Both are heavily scrutinized; the trust structuring must be genuine. Counsel
  required — do not implement from a skill file.

### H2. Asset vs stock sale — **Conservative** analysis
- Buyers want assets (basis step-up, §168(k) on the allocation). Sellers want
  stock (single level of tax, QSBS eligibility).
- For a C corp, an asset sale is **double-taxed** — corporate gain plus
  shareholder-level tax on distribution — which usually makes the QSBS stock sale
  dramatically better. Quantify both before negotiating.
- Model both structures through the `exit-planning` binding before negotiating;
  the deal structure is far harder to change once it is papered.

### H3. §1400Z opportunity zone deferral — **Moderate**
- Reinvest capital gain into a QOF within 180 days: defer the gain, and after a
  10-year hold the **appreciation on the QOF investment** is excluded.
- Made permanent by OBBBA with rolling designations from 2027 — `VERIFY` current
  mechanics and deferral end dates before relying on pre-OBBBA rules.
