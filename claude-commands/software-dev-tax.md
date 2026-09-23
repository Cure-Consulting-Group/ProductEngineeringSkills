# Software Development Cost Taxation

For a company that builds software, this is usually the largest and least
documented item on the return. A year of platform engineering is worth a
substantial deduction and credit — but only to the extent it was **compensated**,
**domestic**, **pre-release**, and **documented at the time**. **Done when**
every repo has a tax character, spend is split §174A / §162 / §195 / foreign,
QREs are sized by category with the founder-wage gap stated, and the evidence
gaps are listed.

## Disclaimer
This skill produces draft analysis and workpapers, not tax, legal, or accounting advice. Nothing it produces is filing-ready until a licensed CPA, enrolled agent, or tax attorney has reviewed it. Model output is not authority and does not establish reasonable cause (see `cpa-standards`).

## The three questions, in order

Every dollar of development spend answers these three. Get them in the wrong
order and the analysis breaks.

```
1. IS IT DEDUCTIBLE, AND UNDER WHAT SECTION?   → §174A vs §162 vs §195
2. DOES IT ALSO EARN A CREDIT?                 → §41 four-part test + IUS rules
3. CAN YOU PROVE IT?                           → wages, allocation, contemporaneous records
```

Question 1 is nearly always "yes, §174A." Question 2 is where the money is.
Question 3 is where claims die.

## 1. Characterization — §174A is mandatory, not elective

**Software development is statutorily R&E.** §174A(d)(3) (domestic; §174(c)(3)
is the foreign-R&E counterpart) treats any amount paid or incurred in connection
with developing software as an R&E expenditure (verified 2026-09-23, 26 U.S.C.
§174A). It is a characterization rule, not an election, so it cannot be moved to
§162 for simplicity.

| Cost | Treatment (TY2025 onward) |
|---|---|
| **Domestic software development** | **§174A — currently deductible in full** (OBBBA restored immediate expensing) |
| **Foreign software development** | Still capitalized and amortized over **15 years** (§174(a)) — offshore contractors are dramatically less tax-efficient |
| Post-release routine maintenance, bug fixes, content updates | §162 ordinary business expense |
| Costs of a genuinely **new trade or business** before it begins | §195 startup — **except qualifying R&E, which is §174A** (see below) |
| Purchased software / acquired IP | §197 amortization or §179, not §174A |

### §174A vs §195 — the distinction that decides the year

§195(c)(1) excludes from startup expenditures any amount deductible under §174
or §174A (OBBBA conforming amendment; verified 2026-09-23), and *Snow
v. Commissioner*, 416 U.S. 500 (1974), holds that §174 reaches research connected
with a trade or business the taxpayer *intends* to carry on. So the test is not
whether revenue has started. Qualifying software R&E is §174A — currently
deductible — both in an operating company **and** in a pre-revenue entity with a
realistic prospect of entering the business the software serves. What §195
captures is the *non-R&E* pre-opening cost: market studies, recruiting, pre-launch
advertising, and the general overhead of getting ready. A pre-revenue entity
therefore splits its spend: qualifying development under §174A, everything else
under §195. Document the realistic prospect — a business plan, a launch path, the
licence being pursued — because that is what the position rests on. An entity
doing research it does not intend to exploit itself (funded for, or transferred
to, another party) does not reach §174A this way. Get this wrong and the deduction
lands in the wrong year entirely.

### Transition relief — two separate items (Rev. Proc. 2025-28)
1. **Small-business retroactive election — EXPIRED.** Small businesses (≤ \$31M
   average gross receipts for 2025) could apply §174A retroactively to 2022–2024
   by amended returns (or an election statement with the 2024 return). The
   deadline was the **earlier of 2026-07-06 or the §6511 refund limitations
   period** for each year. As of 2026-09-23 it has **passed** — do not present it
   as available (verified 2026-09-23, Rev. Proc. 2025-28). Only confirm
   whether it *was* made.
2. **Catch-up of unamortized 2022–2024 domestic R&E — still relevant.** Any
   taxpayer (not only small businesses) may deduct the remaining unamortized
   2022–2024 domestic R&E in full in its first tax year beginning after 2024, or
   ratably over that year and the next (2025 and 2026 for calendar-year filers),
   via an automatic method change (statement in lieu of Form 3115). **Check
   whether the entity is carrying capitalized 2022–2024 domestic R&E on the
   books** — nothing on the current return points at it. If the 2025 return is
   already filed, check what was elected; a ratable election still produces a
   2026 deduction. `VERIFY` the mechanics against Rev. Proc. 2025-28 before filing.

Current-year §174A expensing of domestic R&E (tax years beginning after 2024) is
unaffected by either item.

## 2. The §41 credit — where software gets favorable treatment

### Four-part test (§41(d)), applied to software

| Element | What satisfies it in software |
|---|---|
| **Permitted purpose** | New or improved **function, performance, reliability, or quality** of a product. Note what is absent: appearance and taste do not count. A new inference pipeline qualifies; a redesigned marketing page does not. |
| **Technological in nature** | Relies on principles of computer science. Software clears this almost automatically. |
| **Elimination of uncertainty** | Uncertainty as to **capability** (can it be done), **method** (how), or **appropriate design**. Must exist at the outset. |
| **Process of experimentation** | Systematically **evaluating alternatives** — prototyping, A/B of architectures, benchmarking models, iterating on failures. Substantially all (≥80%) of the activities must constitute such a process. |

### Internal-use software — the trap you mostly avoid

Internal-use software (IUS) must clear an additional **high threshold of
innovation** test: innovative, involves significant economic risk, and not
commercially available. It is hard to meet.

**Software developed for sale, lease, or license to third parties is NOT
internal-use software** and is exempt from that test entirely.

Classify every repo before computing anything — the test that applies is decided
here, not at the credit computation:

| Character | Example | IUS test applies? |
|---|---|---|
| Sold, leased, or licensed to third parties | A shipped app, a SaaS product, anything with customers | **No** — exempt. Four-part test only, the best posture. |
| Mixed use | A platform that serves both customers and the company itself | Determine per product; see the dual-function safe harbor below |
| Purely internal tooling | Internal dashboards, back-office systems, the company's own automation | **Yes** — the high threshold of innovation applies. Assume no credit absent a strong case. |

Record the classification per repo in the project's tax profile, with the
evidence for it. It is a factual determination that has to be defensible years
later, when the product's history is no longer obvious.

**Dual-function software** (both internal and third-party facing) has a safe
harbor at Reg. §1.41-4(c)(6): if at least 10% of use is by third parties, 25% of
the dual-function subset's QREs may be included.

### Statutory exclusions — §41(d)(4)

The ones that bite software shops: research **after commercial production
begins** (below), **adaptation** to one customer's requirements, **foreign**
research, and **funded** research — another party bears the economic risk or the
taxpayer keeps no substantial rights, which is typical of client work.

### The pre-release boundary

"Research after commercial production begins" is the exclusion that governs this
year. Once a product is **functionally ready for its intended commercial use**,
subsequent work is generally maintenance, not research — unless it is a genuinely
new component with its own uncertainty.

Pre-release development is the most favorable posture available, and the window
closes product by product. Fix the release date per product and separate pre-
from post-release effort in the records as it happens; a boundary reconstructed
after launch is far weaker evidence.

## 3. QRE categories — what actually counts

| Category | Section | Rate | Notes |
|---|---|---|---|
| **Wages** | §41(b)(2)(D) | 100% | **Box 1 W-2 wages** for qualified services: performing research, **directly supervising**, or **directly supporting** it. |
| **Supplies** | §41(b)(2)(C) | 100% | Tangible property used and consumed. Not capital, not general overhead. |
| **Computer rental / cloud** | §41(b)(2)(A)(iii) | 100% | Third-party compute used **in qualified research** — dev/test/training workloads on AWS, GCP, Firebase. **Production hosting of a released product is not research.** Allocate. |
| **Contract research** | §41(b)(3) | **65%** | Only if the taxpayer **bears the economic risk** and **retains substantial rights**. A fixed-fee contractor who keeps the IP is funded research and qualifies for nothing. |

### The substantially-all rule
If **≥80%** of an employee's time is spent on qualified services, **100%** of that
employee's wages are a QRE. Below 80%, allocate actual qualified time. This makes
a dedicated engineer far more efficient than a split-role person, and it rewards
accurate time records.

### The founder wage problem — usually the binding constraint

**Uncompensated founder labor generates zero QREs.** There is no imputation, no
fair-value substitute, no way around it. A credit claimed by a company whose
engineering is done by unpaid founders collapses to supplies plus 65% of
contractor spend — which is typically a small fraction of what the work was
actually worth. This is the single most common way a young software company
under-claims §41.

For a C corporation the owner **can** be a W-2 employee, so this is fixable — but
only prospectively, and only with real payroll: withholding, 941s, W-2. Establishing
compensation also unlocks the **§41(h) payroll offset** (up to \$500,000 of credit a year for tax years beginning after 2022 — the first
\$250,000 against the employer share of Social Security tax, the rest against
the employer share of Medicare tax), which is what converts a useless
credit carryforward into cash at a company with no tax liability.

**Sequence**: reasonable compensation analysis → payroll → wage QREs → credit →
§41(h) election on the timely filed original return.

## Computation method

Use the **Alternative Simplified Credit**: 14% of QREs over 50% of the prior
three years' average QREs; **6% of current-year QREs if there were no QREs in any
of the prior three years**. The regular method's base-period computation is
impractical for a young company.

Then decide the **§280C(c) election**: take the credit reduced by 21% and keep the
full §174A deduction, or take the full credit and reduce the deduction. Compute
both.

## Book-tax difference — do not skip this

Book and tax now diverge, and the difference lands on **Schedule M-1**:

| | Book | Tax |
|---|---|---|
| Internal-use software | ASC 350-40 — capitalize after the preliminary project stage | §174A — expense currently |
| Software to be sold | ASC 985-20 — capitalize after technological feasibility | §174A — expense currently |

If the books capitalize development and the return expenses it, that is a real
M-1 adjustment with a deferred tax consequence. Reconcile it deliberately rather
than letting the two systems silently disagree.

### Basis consequence when IP moves to a new entity
Expensing development under §174A leaves the IP with **little or no tax basis**,
and a §351 contribution carries that basis over for general purposes. For §1202
only, stock received for property takes a basis of **no less than the property's
FMV** and a holding period starting at the exchange (§1202(i); verified
2026-09-23, 26 U.S.C. §1202). So the 10×-basis cap is measured off FMV at
contribution, but pre-contribution appreciation is never excludable. Get a
contemporaneous valuation of the IP at contribution; without one, the \$15M cap
(post-2025-07-04 stock; indexed after 2026) governs by default.

## Reference files

- `reference/qre-qualification.md` — read when a specific activity's
  qualification is in doubt; worked software scenarios, IUS, exclusions.
- `reference/cost-taxonomy.md` — read when setting up or auditing the books;
  account structure and allocation by product and entity.
- `reference/repo-inventory-template.md` — read when classifying repos; the
  per-repo intake sheet (product, entity, tax character, evidence).

## Scripts

`cure-repo-activity` (on PATH while the plugin is enabled; otherwise
`python3 <plugin>/skills/tax/software-dev-tax/scripts/repo_activity.py`) extracts
per-repo, per-author, per-month commit activity as corroboration for time
allocation. Commit dates are set by the committer, so weight rises with remote
logs, protected branches, or signed commits. It shows *that* work happened, not
that it met the four-part test, so it does not replace a time study.

```bash
cure-repo-activity ~/code --year <tax-year> --json
```

## Related skills

`deductions-and-credits` (§41 in the credit catalog), `tax-strategies`
(§174A/§41 coordination, entity playbook), `audit-risk-substantiation` (R&D is a
high-scrutiny claim), `tax-preparation` (Form 6765, Form 8974, Form 3115).
