# Workpaper Standards

**Test of sufficiency**: a reviewer who has never seen the engagement can
reproduce every number on the return using only the file.

## File index

```
00_ADMIN/            engagement scope, conflicts memo, §7216 consents, fee agreement
01_PY/               prior-year return, transcripts, carryforward schedule (in)
02_SOURCE/           W-2, 1099-*, K-1, 1098, brokerage, bank, merchant statements
03_LEAD/             one lead schedule per return line
04_COMPUTE/          depreciation, basis, QBI, SE tax, home office, comp study
05_RECON/            book-to-tax, bank-to-books, 1099-to-revenue
06_POSITIONS/        memo per non-routine position (FIRAC)
07_ELECTIONS/        each election + proof of timely filing
08_INQUIRY/          due diligence log
09_REVIEW/           diagnostics, review notes, sign-off
10_FILED/            as-filed return, 8879, acknowledgment
11_CARRYFORWARD/     carryforward schedule (out) → next year's 01_PY
```

## Lead schedule format

Every return line traces down to source. Minimum columns:

| Ref | Description | PY amount | CY amount | Variance | Source | W/P ref | Tick |
|---|---|---|---|---|---|---|---|

Tickmark legend, used consistently:

```
✓  agreed to source document
Ⓕ  footed / recomputed
Ⓐ  agreed to prior year return
Ⓡ  reconciled — see reconciliation W/P
Ⓔ  estimate — basis of estimate documented (SSTS No. 4)
Ⓠ  inquiry made — see 08_INQUIRY
⚠  open item — must clear before filing
```

**No return is filed with an open ⚠.**

## Position memo format (FIRAC)

One per non-routine position. Two pages maximum.

```
FACTS       — what actually happened, with dates and amounts.
             Only facts in evidence; assumptions labeled as assumptions.
ISSUE       — the question, framed as a legal issue.
RULE        — controlling section, regulations, rulings, cases.
             Authority tier per irc-lookup/reference/authority-hierarchy.md.
ANALYSIS    — application of rule to facts, INCLUDING contrary authority
             and why it does not control.
CONCLUSION  — the position taken, and the confidence standard reached
             (substantial authority / reasonable basis / MLTN).
DISCLOSURE  — required? Form 8275 / 8275-R / 8886 attached?
PREPARED BY / DATE      REVIEWED BY / DATE
```

Write the memo **before** filing. A memo written after a notice arrives carries
far less weight for the §6664(c) reasonable-cause defense.

## Carryforward schedule — the permanent record

Roll forward every year. Losing this is the most expensive small-practice failure.

| Attribute | Section | PY balance | Generated | Used | CY balance | Expires |
|---|---|---|---|---|---|---|
| Federal NOL | §172 | | | | | indefinite, 80% limit |
| State NOL | | | | | | varies |
| Capital loss carryover | §1212 | | | | | indefinite |
| §179 carryforward | §179(b)(3) | | | | | indefinite |
| General business credit | §39 | | | | | 20 yrs fwd |
| R&D credit (by year) | §41/§39 | | | | | 20 yrs fwd |
| Foreign tax credit | §904(c) | | | | | 10 yrs fwd |
| AMT credit | §53 | | | | | indefinite |
| Charitable carryover | §170(d) | | | | | 5 yrs |
| Passive activity loss | §469 | | | | | until disposition |
| At-risk suspended | §465 | | | | | until at-risk |
| Excess business loss | §461(l) | | | | | becomes NOL |
| Investment interest | §163(d) | | | | | indefinite |
| §163(j) interest | §163(j) | | | | | indefinite |
| Home office carryforward | §280A(c)(5) | | | | | indefinite |

## Permanent file (never purge)

- Entity formation documents, EIN letters, S/C election acknowledgments
- Stock ledger and cap table
- **Basis schedules** — stock basis, debt basis, partner capital accounts, by year
- **QSBS evidence**: gross-asset balance sheets at and immediately after each
  issuance, §1202(e) qualified-trade memo, original issuance documentation
- §83(b) elections with certified mail receipts
- Depreciation schedules for the life of every asset + 3 years
- Intercompany agreements and transfer-pricing documentation
- Real property closing statements and improvement records
- Prior-year returns — all of them

## Review standard

Preparation and review are **separate passes by separate sessions**, and ideally
separate people. The reviewer:

1. Reads the lead schedules before the return, not after.
2. Recomputes at least every derived number over a materiality threshold.
3. Explains every material prior-year variance in writing.
4. Confirms every ⚠ is cleared.
5. Confirms every non-routine position has a memo dated before the filing date.
6. Signs and dates.

Where the taxpayer and preparer are the same person, the review pass is the only
independent control that exists. Do not skip it, and do not perform it in the same
sitting as preparation.
