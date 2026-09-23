---
name: cpa-standards
description: "Applies Circular 230, AICPA SSTS, and §7216 to tax work. Use when deciding if a position can be taken or must be disclosed, or on preparer duties, workpapers, conflicts, or confidentiality."
when_to_use: "NOT for audit likelihood or defense files (audit-risk-substantiation) or finding the authority itself (irc-lookup)."
argument-hint: "[position-or-work-product]"
metadata:
  verified: 2026-09-23
---

# CPA Professional Standards

The other tax skills answer *what the law is*; this one governs *how the work is
performed and documented*. It applies to every work product a return or advice
depends on, and most of all when taxpayer and preparer are the same person,
because that return has no second reviewer. **Done when** each position has a
standard (and disclosure decision), and the work product meets the workpaper and
§7216 rules below, or the gaps are listed.

## The three governing regimes

| Regime | Source | Enforced by | Sanction |
|---|---|---|---|
| **Circular 230** | 31 C.F.R. Part 10 | IRS Office of Professional Responsibility | Censure, suspension, disbarment from practice |
| **AICPA SSTS** | Statements on Standards for Tax Services (enforceable, revised effective 2024) | AICPA / state boards | Membership sanction, license discipline |
| **IRC preparer penalties** | §§6694, 6695, 6700, 6701, 7216 | IRS | Monetary penalties, injunction, criminal exposure |

They overlap but are not identical. A position can satisfy the Code's penalty
thresholds and still violate Circular 230 diligence duties.

## The position standard — decide this before anything is filed

```
Is the position frivolous?                 → Never take it. §6702.
Does it have substantial authority (~40%)? → File, no disclosure required.
Only reasonable basis (~20%)?              → File ONLY with Form 8275/8275-R disclosure.
Neither?                                   → Do not take the position. Advise the client in writing.
Tax shelter or reportable transaction?     → More likely than not (>50%) required, plus Form 8886.
```

The authority ladder is in `irc-lookup/reference/authority-hierarchy.md`;
penalty consequences in `audit-risk-substantiation`.

Audit probability never enters the analysis (Circular 230 §10.37, SSTS 1.1):
"they won't catch it" is not authority, and its appearance in a workpaper is
itself evidence of an unreasonable position.

## Due diligence — Circular 230 §10.22 and §10.34

A preparer may generally rely on information furnished by the taxpayer **without
verifying it**, but may **not ignore the implications** of information known or
furnished, and **must make reasonable inquiries** when the information appears
incorrect, inconsistent, or incomplete.

The trigger to inquire, in practice:

- Numbers that do not reconcile to the source documents.
- A deduction with no plausible business connection.
- A business claiming losses year after year (→ §183 inquiry).
- Round numbers where records should exist ("about \$12,000 of supplies").
- Missing substantiation for a §274(d) category.
- Income that appears low relative to lifestyle or to reported expenses.
- An S corp with distributions and little or no officer compensation.

**Document the inquiry and the answer.** An undocumented inquiry did not happen.

### Enhanced due diligence — §6695(g)
For EITC, CTC/ACTC/ODC, AOTC, and head-of-household status: complete **Form 8867**,
compute with worksheets, apply the knowledge requirement, and retain the records.
Penalty is **per failure, per return** — four credits on one return means four
penalties.

## AICPA SSTS — the revised standards (effective 2024-01-01)

The pre-2024 seven statements ("SSTS No. 1–7") were replaced by four statements
with numbered sections (verified 2026-09-23, AICPA *Statements on Standards for Tax
Services No. 1–4*, effective January 1, 2024). Cite by section, not the old numbers.

| Section | Duty | Practical rule |
|---|---|---|
| **1.1** Advising on tax positions | Position standard (advice) | Comply with the **taxing authority's standard** where it has one — for federal returns that is §6694/Circular 230 (substantial authority; reasonable basis with disclosure; more likely than not for tax shelters/reportable transactions). The SSTS "realistic possibility" floor applies **only** where the taxing authority has no written standard. Never advise a position that exploits audit selection. |
| **1.2** Knowledge of errors | Error discovered | **Inform the client promptly**, recommend corrective action, and explain the consequences. **Do not** notify the IRS without the client's permission. If the client refuses to correct a material error, consider withdrawal. |
| **1.3** Data protection (new) | Safeguard taxpayer data | Reasonable safeguards for taxpayer information; ties to §7216 and the FTC Safeguards Rule. |
| **1.4** Reliance on tools (new) | Software and other tools | A tool's output is the member's responsibility — exercise judgment over what the software or model produced. |
| **2.1** Tax return positions | Position standard (returns) | Same ladder as 1.1 for positions on a return you prepare or sign. Advise the client of penalty risk and the opportunity to disclose. |
| **2.2** Tax return questions | Answers on returns | Make a **reasonable effort to obtain answers to all questions** on the return. Blank is not an answer. |
| **2.3** Reliance on information from others | Procedural diligence | May rely in good faith on client information without verification, but must inquire when it appears incorrect/inconsistent/incomplete, and should consider prior-year returns when feasible. |
| **2.4** Use of estimates | Estimates | Permitted where records are unavailable and the amounts are reasonable — but **must not imply greater accuracy than exists**, and are unavailable where the Code demands strict substantiation (§274(d)). |
| **2.5** Departure from previous positions | Prior-year treatment | A prior year's treatment (even one settled on audit) does not bind the current year. |
| **No. 3** Tax consulting services | Form and content of advice | Advice must reflect professional competence and serve the client's needs; no duty to update unless specifically undertaken. |
| **No. 4** Tax representation services | Representation before a taxing authority | Standards for representing the taxpayer in examinations, appeals and other proceedings. |

## Recordkeeping and workpapers

A workpaper file is complete when a reviewer who has never seen the engagement can
reconstruct every number on the return from it.

**Required contents**
- **Lead schedule** per return line, tying to the underlying detail.
- **Source documents**: W-2s, 1099s, K-1s, bank and brokerage statements.
- **Reconciliations**: book-to-tax, bank-to-books, 1099 totals to reported gross
  receipts.
- **Computations** for anything derived: depreciation schedules, basis schedules,
  QBI, SE tax, home office allocation, reasonable compensation.
- **Carryforward schedule**: NOLs, capital losses, §179 carryforward, credit
  carryforwards, basis, at-risk and passive amounts, AMT credit. **This is the
  most frequently lost document in small practices and the most expensive to
  recreate.**
- **Position memos** for any non-routine item: facts, issue, authority, analysis,
  conclusion, and the confidence standard reached.
- **Inquiry log**: questions asked, answers received, dates.
- **Elections** filed, with proof of timely filing.
- **Review sign-off** and the date.

**Retention**: §6107(b) requires the preparer to retain a copy or list of returns
for 3 years. Substantiation retention periods are in the
`deductions-and-credits` skill. Basis and QSBS records are effectively permanent.

## Confidentiality — §7216 (this one is criminal)

Knowingly or recklessly disclosing or using tax return information other than to
prepare the return is a **misdemeanor**: up to \$1,000 and up to one year, plus a
§6713 civil penalty per disclosure.

**Rules that matter for an AI-assisted practice:**
- Disclosure requires the taxpayer's **written consent**, in a form meeting Reg.
  §301.7216-3 (specific, signed, dated, and obtained before disclosure).
- Sending return information to a third-party service — including an external
  model API — is a **disclosure**. Consent or a qualifying exception must exist.
- Use of return information for anything other than preparing the return (product
  analytics, model training, marketing) requires separate consent.
- Practical rule for any system holding return data: it must not leave the
  taxpayer-scoped store, must not appear in logs, and must not be sent to a
  third-party API without an executed consent or an applicable exception. Where a
  project states security principles of its own, **§7216 is the legal reason
  behind them** — a criminal statute, not a best practice.

## Conflicts of interest — Circular 230 §10.29

A conflict exists when representing one client is directly adverse to another, or
when representation is materially limited by another client, a former client, or
the practitioner's own interest.

Permitted only if: the practitioner reasonably believes competent representation
is possible, it is not prohibited by law, and **each affected client waives in
writing** — retained for 36 months.

**The common in-house case**: in a founder-owned group the same person is owner,
preparer, and beneficiary of every entity at once. Intercompany pricing under §482
is inherently adverse between any two of them — a fee that helps the hub hurts the
spoke, and both returns cannot be optimised at the same time. Document the
allocation as if two unrelated clients were being advised, and note the conflict
in the file.

## Other Circular 230 duties

| § | Duty |
|---|---|
| §10.20 | Furnish information to the IRS promptly unless privileged |
| §10.21 | On knowing of a client's error or omission, **advise the client** of it and of the consequences |
| §10.27 | Contingent fees generally prohibited for preparing an original return |
| §10.28 | Return client records on request, even in a fee dispute |
| §10.30 | No false or misleading solicitation |
| §10.33 | Best practices: clear engagement scope, establish the facts, relate law to facts, advise on the import of conclusions |
| §10.35 | Competence — do not undertake matters you are not competent to handle without associating with someone who is |
| §10.37 | Written advice: base it on reasonable factual and legal assumptions, consider all relevant facts, do not rely on unreasonable representations, and **do not take audit risk into account** |

## Signing and e-filing

A PTIN is required to prepare for compensation (§6109(a)(4)); the signer bears
primary responsibility, and each §6695 failure (sign, copy, retain, PTIN, refund
check) is separately penalized. A **self-prepared return** has no signature duty
but a much weaker §6664(c) reasonable-cause defense, since there is no advisor to
have relied on. That is why Cure prepares in-house and the accountant of record
reviews and transmits.

## Applying this to an AI-assisted workflow

Model output is **not** authority (see the `irc-lookup` hierarchy, Tier 6) and is
not a reasonable-cause defense. Treat it as a first-draft preparer whose work
requires review:

1. Every number traces to a source document or a verified computation.
2. Every position carries a cite with a verification status; nothing filed on
   `RECALL`.
3. Every non-routine position has a written memo before filing, not after.
4. A human with authority signs off, and the sign-off is dated and recorded.
5. Return information stays inside the taxpayer's scoped storage.

## Reference files

- `reference/circular-230-checklist.md` — read at engagement start and before
  sign-off; the engagement-level compliance checklist.
- `reference/workpaper-standards.md` — read when assembling or reviewing a
  workpaper file; index, lead schedule format, sign-off, carryforward template.

## Related skills

`cpa-benchmark` (measure competency against exam-grade standards),
`irc-lookup`, `audit-risk-substantiation`, `return-review`, `tax-preparation`.
