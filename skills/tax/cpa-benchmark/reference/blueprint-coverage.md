# CPA Exam Blueprint Coverage

The CPA exam (post-2024 CPA Evolution) is three Core sections plus one Discipline:

```
CORE       AUD  — Auditing and Attestation
           FAR  — Financial Accounting and Reporting
           REG  — Taxation and Regulation
DISCIPLINE BAR  — Business Analysis and Reporting
           ISC  — Information Systems and Controls
           TCP  — Tax Compliance and Planning
```

This benchmark deliberately covers **REG** and **TCP** only. AUD, FAR, BAR, and
ISC are outside what this system does — it prepares and plans taxes, it does not
audit or produce GAAP financial statements. Claiming coverage there would be
dishonest.

## REG blueprint vs the bank

| Blueprint area | Exam weight | Bank coverage | Gap |
|---|---|---|---|
| **I. Ethics, Professional Responsibilities, Federal Tax Procedures** | 10–20% | 7 questions (Circular 230, SSTS, §7216, §6662, §6654, §6501, §7701(o)) | Adequate |
| **II. Business Law** | 15–25% | **0 questions** | **Not covered by design.** Contracts, agency, UCC, debtor-creditor, and federal securities regulation are outside this system's scope. `contract-reviewer` and outside counsel handle that domain. |
| **III. Federal Taxation of Property Transactions** | 5–15% | 3 questions (§1031, §453(i), §1244) plus related items in TCP | Thin — see gaps below |
| **IV. Federal Taxation of Individuals** | 22–32% | 6 questions (SE tax, AMT, CTC, SALT, wash sales, capital losses) plus most of TCP | Adequate |
| **V. Federal Taxation of Entities** | 23–33% | 6 questions (§179 vs bonus, §195, §1366(d) basis, §351, §531) plus entity items in TCP and portfolio | Adequate |

## TCP blueprint vs the bank

| Blueprint area | Bank coverage |
|---|---|
| **I. Tax Compliance and Planning for Individuals** | Retirement (3), deduction planning (2), property/loss items — good |
| **II. Entity Tax Compliance** | Entity planning (2), loss limitations (2), QBI (3) — good |
| **III. Entity Tax Planning** | Entity structure, transfer pricing, credits — good |
| **IV. Property Transactions (disposition)** | QSBS/exit (3), installment sales — adequate |
| **V. Personal Financial Planning** | **Thin** — see gaps |

## Known gaps — stated honestly

These are real holes. Do not read a passing score as competency in them.

| Gap | Risk | Priority |
|---|---|---|
| **Estate and gift tax** (§2001–2704, unified credit, portability, annual exclusion, GST) | Relevant to QSBS stacking via non-grantor trusts, which the strategy playbook mentions | High if trust planning proceeds |
| **Trust and fiduciary income tax** (Subchapter J, DNI, grantor trust rules §671–679) | Same trigger as above | High if trust planning proceeds |
| **International** (§367 outbound, GILTI, Subpart F, FDII, treaties, FBAR/FATCA) | Revenue from foreign app stores or marketplaces; any non-US contractor | Medium — currently only §901 FTC is covered |
| **Multi-state allocation and apportionment** | Any group with entities formed in one state and operating in another; engine modules for allocation and relocation typically go untested by this bank | Medium-high |
| **Payroll tax compliance mechanics** (941/940/W-2/W-3 filing, deposit schedules, trust fund recovery §6672) | Becomes directly relevant the moment any entity establishes payroll — and establishing payroll is a common recommendation | **High** |
| **Partnership taxation depth** (§704(b) allocations, §704(c), §751 hot assets, §754 elections, basis adjustments) | Only reachable where a real partnership exists; a disregarded SMLLC and an S corp do not raise it | Low unless the group has a partnership |
| **Property transaction depth** (§1231 netting and recapture, §1250 unrecaptured gain, §121 exclusion, §1033) | Only 3 questions today | Medium |
| **Accounting method changes** (§481(a), Form 3115, Rev. Proc. 2015-13) | Required if §174A retroactive relief or a §471(c) inventory method is adopted | Medium |
| **Business law** (REG area II) | Out of scope by design | Not planned |

## Additional coverage gaps the benchmark tests

The benchmark includes permanent questions for these six easily missed areas:

- **S corporation mechanics** — stock and debt basis, ordering rules,
  distributions, and the March 15 deadline.
- **Inventory / COGS** — purchases, ending inventory, and the resulting COGS
  reconciliation.
- **Amended-return procedure** — qualified amended returns under Reg.
  §1.6664-2(c)(3).
- **HSA** — contribution eligibility, limits, and the unextended due-date
  deadline.
- **§72(t) exceptions** — exceptions to the early-distribution penalty and their
  reporting.
- **QBI carryforwards** — treatment of negative qualified business income across
  tax years.

## Closing a gap

1. Write questions **first**, from the statute, before writing the reference
   content. Questions written after the prose tend to test the prose rather than
   the law.
2. Add them to an existing set, or create a new file in `benchmark/questions/` —
   the runner auto-loads it.
3. Derive every numeric answer from the `constants` binding or a cited revenue
   procedure, and record the derivation in the `why` field.
4. Then write or extend the reference file that should make the question
   answerable, and cross-link it.
5. Re-run `node run.mjs stats` to confirm the coverage shift.

Target distribution as the bank grows: no more than 40% recall, at least 35%
analysis-level, and a project's own applied overlay at roughly a quarter of total
questions. Applied accuracy on the entities actually in front of you is what
protects the taxpayer; generic competency only keeps you in the room.
