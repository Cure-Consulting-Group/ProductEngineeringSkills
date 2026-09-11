---
name: cpa-standards
description: Apply the professional standards a return preparer is held to — Circular 230, the AICPA Statements on Standards for Tax Services, due diligence, workpaper standards, conflicts of interest, and §7216 confidentiality. Use when preparing or reviewing any return or tax advice, or deciding whether a position may be taken or must be disclosed.
argument-hint: "[position-or-work-product]"
---

# CPA Professional Standards

The other tax skills answer *what the law is*. This one governs *how the work is
performed and documented* — the difference between a defensible practice and a
correct answer nobody can rely on.

Apply this skill to every work product that a return or advice depends on, even
when the taxpayer and the preparer are the same person. **Especially** then: the
self-prepared return has no second reviewer, so the standard has to be internal.

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

Details and the full authority ladder are in the `irc-lookup` skill's
`reference/authority-hierarchy.md`. Penalty consequences are in
`audit-risk-substantiation`.

**Never** let audit probability enter the analysis. "They won't catch it" is not a
standard, is not authority, and its appearance in a workpaper is itself evidence
of an unreasonable position.

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

## AICPA SSTS — the seven duties

| SSTS | Duty | Practical rule |
|---|---|---|
| **No. 1** | Tax return positions | Do not recommend or sign a position lacking a realistic possibility of success unless it is not frivolous **and** is disclosed. Advise the client of penalty risk and the opportunity to disclose. |
| **No. 2** | Answers on returns | Make a **reasonable effort to obtain answers to all questions** on the return. Blank is not an answer. |
| **No. 3** | Procedural aspects | May rely in good faith on client information without verification, but must inquire when it appears incorrect/inconsistent/incomplete, and must consider prior-year returns when feasible. |
| **No. 4** | Use of estimates | Estimates are permitted where records are unavailable and the amounts are reasonable — but **must not be presented to imply greater accuracy than exists**, and are unavailable where the Code demands strict substantiation (§274(d)). |
| **No. 5** | Departing from a prior position | A prior year's treatment (even one settled on audit) does not bind the current year. |
| **No. 6** | Knowledge of an error | On discovering an error, **inform the client promptly**, recommend corrective action, and explain the consequences. **Do not** notify the IRS without the client's permission — doing so may violate confidentiality. If the client refuses to correct a material error, consider withdrawal. |
| **No. 7** | Form and content of advice | No standard form required, but advice must reflect professional competence and serve the client's needs. Update advice only when specifically undertaken to do so. |

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

- **PTIN** required for anyone who prepares for compensation (§6109(a)(4)).
- The preparer who signs is the one with **primary responsibility** for the
  substantive accuracy.
- §6695 penalties: failure to sign, failure to furnish a copy to the taxpayer,
  failure to retain, failure to furnish the PTIN, negotiating a client's refund
  check — each is separately penalized.
- **Self-prepared returns**: no PTIN or signature obligation applies, but §6662
  taxpayer accuracy penalties do, and the §6664(c) reasonable-cause defense is
  much weaker when the taxpayer prepared their own return and cannot point to
  advisor reliance. This is the argument for the accountant-of-record model this
  practice uses — prepare in-house, accountant reviews and transmits.

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

- `reference/circular-230-checklist.md` — engagement-level compliance checklist.
- `reference/workpaper-standards.md` — file index, lead schedule format, review
  sign-off, and the carryforward schedule template.

## Related skills

`cpa-benchmark` (measure competency against exam-grade standards),
`irc-lookup`, `audit-risk-substantiation`, `return-review`, `tax-preparation`.
