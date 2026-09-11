# Anti-Abuse Doctrines & The Kill List

Every strategy passes through this gate before it is recommended. A strategy that
saves tax and fails a doctrine is a penalty with a delay.

---

## 1. Economic substance — §7701(o) (codified 2010)

The only doctrine with a **statutory strict-liability penalty**. A transaction has
economic substance only if **both** prongs are met:

| Prong | Requirement |
|---|---|
| **Objective** | The transaction changes the taxpayer's **economic position in a meaningful way**, apart from federal tax effects |
| **Subjective** | The taxpayer has a **substantial purpose** for entering it, apart from federal tax effects |

**Both**, conjunctively. A transaction with a real business purpose but no
economic change fails. A transaction with economic change but no non-tax purpose
fails.

**Profit-potential test** (§7701(o)(2)): if the taxpayer relies on profit
potential to satisfy the prongs, the **pre-tax profit must be substantial relative
to the expected net tax benefit**. A deal that makes $1 pre-tax to generate
$100,000 of tax benefit fails.

**Penalty**: §6662(b)(6) and §6662(i) impose **20%, increased to 40% if not
adequately disclosed** — and it is **strict liability**. The §6664(c) reasonable-
cause defense **does not apply**. No opinion letter, no advisor reliance, no good
faith saves it.

**Practical test to apply**: *If the tax law changed tomorrow to remove this
benefit, would we still do this transaction?* If the honest answer is no, and
there is no meaningful economic change, do not recommend it.

---

## 2. Business purpose — *Gregory v. Helvering* (1935)

A transaction that complies with the literal words of a statute but serves no
business purpose beyond tax avoidance is disregarded. The taxpayer in *Gregory*
executed a technically perfect reorganization; the Court looked at why and
collapsed it.

**Application**: every entity formed, every intercompany agreement, and every
election needs a stated non-tax reason that a third party would find credible —
liability separation, regulated-data isolation, investor readiness, IP
segregation. Write the reason down **when you do it**, in the minutes.

---

## 3. Substance over form

The tax result follows what actually happened, not what the documents say.

**Failure patterns to avoid**:
- An "employee" who is treated as a contractor but works like an employee
  (§3121(d), Rev. Rul. 87-41 twenty-factor analysis).
- A "loan" to a shareholder with no note, no interest, no repayment schedule, and
  no repayments — recharacterized as a **dividend** (and §7872 imputes interest on
  below-market loans regardless).
- A "rent" payment to an owner with no lease and no market analysis.
- An intercompany services fee with no agreement and no service actually rendered.

**The operative rule**: if the paper and the behavior diverge, the paper loses.
Fix the behavior or fix the paper — do not rely on the paper alone.

---

## 4. Step transaction doctrine

Formally separate steps that are part of a single plan get collapsed into their
end result. Three tests, any of which can apply:

| Test | Trigger |
|---|---|
| **Binding commitment** | An obligation to complete later steps existed at step one |
| **Mutual interdependence** | The steps are meaningless in isolation |
| **End result** | The steps were prearranged parts of a single plan to reach a known result |

**Application to a spinout**: a sequence of "contribute IP to Newco → issue
founder stock → immediately raise outside capital" that is prearranged can be
recast as a single transaction with a very different tax result. Keep genuine
business decision points between the steps, and do not paper later steps before
earlier ones close.

---

## 5. Assignment of income — *Lucas v. Earl* (1930)

Income is taxed to the person who **earns** it; you cannot deflect it by directing
where the check goes. The fruit is taxed to the tree that grew it.

**Failure patterns**:
- Paying a family member for work they did not perform.
- Routing personally-earned consulting fees through an entity that provided
  nothing.
- Assigning a right to income already earned to a lower-bracket taxpayer.

**Distinguish**: transferring the **income-producing property itself** (a gift of
appreciated stock, a genuine transfer of a business interest) *is* effective. The
line is between giving away the tree and giving away the fruit.

---

## 6. §482 — arm's-length pricing between controlled entities

Not a judicial doctrine but a broad statutory reallocation power. The Commissioner
may reallocate income, deductions, and credits among commonly controlled entities
to prevent evasion or clearly reflect income.

**Directly in play**: any entity in a commonly controlled group charging another
for a shared team, shared tooling, or back-office services.

**Requirements**: written intercompany agreement, a specified method (cost-plus is
standard for routine back-office and shared-team services), benchmarking support,
and consistent actual invoicing and payment. Fees that are booked but never paid,
or that swing year to year to hit a target income number, invite reallocation.

---

## Reportable and listed transactions

Separate from the doctrines: some transactions must be **disclosed** regardless of
merit.

| Category | Obligation |
|---|---|
| **Listed transactions** | Specifically identified by the IRS as abusive. Disclose on **Form 8886**. §6707A penalty for failure: up to $100,000 individual / $200,000 entity, **regardless of whether the position was correct**. |
| **Transactions of interest** | Potentially abusive, under study. Same Form 8886 obligation. |
| **Confidential transactions** | Advisor-imposed confidentiality with a fee. |
| **Contractual protection** | Fees refundable if tax benefits fail. |
| **Loss transactions** | Losses over statutory thresholds. |
| **Material advisors** | Form 8918 disclosure and list maintenance (§6111, §6112). |

If a promoter presents a strategy with an NDA and a contingent fee, those two
features alone are reportable-transaction indicia. Decline.

---

## The kill list — strategies that do not work

These recur in founder and small-business circles. They are wrong. Do not
recommend, and push back if proposed.

| Claim | Why it fails |
|---|---|
| "Form a Nevada/Wyoming LLC to avoid NY tax" | Income is sourced where it is earned and taxed where you are domiciled. The out-of-state entity just adds a filing obligation and a foreign qualification. |
| "Pay yourself $0 salary from the S corp" | §162(a)(1) reasonable compensation. Distributions get recharacterized as wages with payroll tax, interest, and penalties. |
| "Deduct the whole G-Wagon over 6,000 lbs" | Heavy-vehicle §179 exists, but requires >50% **documented** business use, §274(d) logs, and produces §1245 recapture on disposition. Personal use of a company vehicle is taxable income. |
| "Write off the family vacation as a board meeting" | §162 ordinary and necessary + §274(d) substantiation + business purpose. Fails all three. |
| "Deduct the home gym as employee wellness" | §262 personal expense. |
| "1031 exchange the manufacturing equipment" | **§1031 is real property only** post-TCJA. Personal property exchanges were repealed; an entity summary that still lists §1031 for equipment is out of date and should not be relied on. |
| "Put the kids on payroll" (from a corporation) | Wages must be for real services at a reasonable rate; and the FICA/FUTA exemption for children applies only to sole proprietorships and parent-only partnerships, **not corporations**. |
| "Convert the C-corp to an S-corp right before the sale" | §1374 built-in gains tax for 5 years, and it destroys §1202 QSBS eligibility (which requires C-corp status throughout). |
| "Charitable remainder trust to zero out the gain" | Real structure, but requires irrevocably parting with the asset. Usually proposed without disclosing that. |
| "Captive insurance for a business this size" | §831(b) micro-captives are a **listed transaction**. Form 8886, and the IRS has won nearly every case. |
| "Cost segregation on a rented apartment" | You must own the property and have basis in it. |
| "Deduct commuting because I stop at a client on the way" | Commuting is nondeductible (Reg. §1.162-2(e)). A stop does not convert the trip. |
| "The corporation lends me money instead of paying wages" | Recharacterized as compensation or a dividend absent a real note, market interest, and repayment (§7872). |
| "Crypto is a like-kind exchange" | Never was for post-2017 years, and the IRS position rejected it before that (Notice 2014-21 treats crypto as property; §1031 is real property only). |
