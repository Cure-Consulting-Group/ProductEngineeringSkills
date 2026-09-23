# Tax Return Preparation

Turns facts into a return a CPA can sign. `deductions-and-credits` finds the
benefit and `tax-strategies` plans the structure; this skill builds the return.

**Done when** every line traces to source, every election is identified, the
workpaper file meets the quality bar below, and `return-review` has run in a
separate pass. Deliver the return package and open-items list; don't add
unrequested planning sections.

## Disclaimer
This skill produces draft analysis and workpapers, not tax, legal, or accounting advice. Nothing it produces is filing-ready until a licensed CPA, enrolled agent, or tax attorney has reviewed it. Model output is not authority and does not establish reasonable cause (see `cpa-standards`). Never file, e-file, pay, or sign: a return transmitted without a signing preparer's review leaves the taxpayer with no reasonable-cause defense.

## Operating model

Cure default: **prepare in-house, the accountant of record signs and transmits.**
The deliverable is an **accountant handoff package**; the only direct-filing lane
worth running in-house is **IRIS for 1099s** (no EFIN needed). Transmitting
returns in-house needs an EFIN, an ERO, and preparer registration — don't assume
it. Build to handoff standard: every number traceable to a source, every position
memoed, every open item flagged rather than quietly resolved.

## Return map

Build this table for the actual group before starting — one row per entity, from
the project's tax profile. The form follows the **entity's tax classification**,
which is not always what its name or its operating agreement suggests: confirm it
against the filed election and the prior return, not the label.

| Entity type | Return | Due (calendar year) | Extended | Watch for |
|---|---|---|---|---|
| C corporation | Form 1120 | Apr 15 | Oct 15 (Form 7004) | State franchise reports on their own earlier schedule — a Delaware annual report is due Mar 1 regardless of income |
| S corporation | Form 1120-S + K-1s | **Mar 15** | Sep 15 | K-1s drive the owner's 1040; shareholder basis schedules are the most commonly missing workpaper |
| Multi-member LLC / partnership | Form 1065 + K-1s | **Mar 15** | Sep 15 | Late-filed K-1s cascade into extended personal returns |
| Single-member LLC | Schedule C on the 1040 | Apr 15 | Oct 15 | **Confirm membership** — a second member converts it to a 1065 with a Mar 15 deadline |
| Pre-operating entity | Whatever its classification requires | same | same | Qualifying R&E under §174A; non-R&E startup costs under §195; no §162 deductions until the business begins |
| Individual | Form 1040 | Apr 15 | Oct 15 (Form 4868) | Every K-1 above has to land before this one can be finished |

**Extension extends time to file, never time to pay.** Estimate and pay with the
extension or §6651(a)(2) failure-to-pay plus interest starts running.

## Workflow

### 1. Open the year
Pass the tax year explicitly to every `calculator`/`constants` call. Pull the
prior-year return and the **carryforward schedule** first; nothing else starts
until carryforwards are in hand.

### 2. Gather and reconcile source documents
Read `reference/document-checklist.md` when building the request list for a
new entity or income type. The reconciliation step is what separates a return
from a guess:
- 1099-NEC/MISC/K totals **reconciled to reported gross receipts**, with
  differences explained in writing. Revenue is almost always higher than the
  1099s (direct sales, cash, sub-threshold payers) — document why.
- Merchant deposits (Stripe, the app stores, direct) reconciled to revenue.
  **Where a platform is merchant of record — the app stores typically are — gross
  versus net reporting differs from a payment processor**, and the commission is
  generally a deduction rather than a revenue reduction, depending on the
  agreement. Get this right; it changes gross receipts, which drives several
  thresholds downstream.
- Bank statements reconciled to books.
- Document extraction (W-2, 1099-NEC/MISC/INT/DIV/B/R, 1098) through the
  `document-ai` binding where the project has one. **Extraction output is a
  draft** — tie every extracted figure back to the document image before use.

### 3. Classify and post
Classify expenses, map Schedule C items, and populate COGS through the project's
posting steps. Every non-obvious classification gets a note: "Software \$4,200"
is not a workpaper.

### 4. Compute
- Compute the return through the `calculator` binding, including SE tax, QBI, AMT,
  credits, and the schedules the project supports.
- Compute depreciation (MACRS, §179, bonus) and reconcile the schedule to the
  fixed asset register — additions, disposals, carryforward.
- Compute the home-office deduction and Form 8829.

### 5. Elections
Identify every election **before** finalizing — several must be on a timely filed
*original* return and cannot be added later. Run the review checklist in
`reference/elections-and-deadlines.md` on every return.

### 6. Assemble
Use the project's form-mapping, PDF, and package-export steps where they exist.
Workpaper file per `cpa-standards/reference/workpaper-standards.md`.

### 7. Validate before handoff
Run `return-review` in a separate pass (a fresh session, or a subagent if your
runtime supports one); the same pass that built the return cannot catch its own
framing errors. The `validator` binding's machine checks are necessary, not
sufficient.

## Information return obligations

Any entity that pays contractors owes these. They are **separate from the income
tax return**, due earlier, and missing them draws per-form penalties that rarely
have a reasonable-cause story.

| Form | Due to recipient | Due to IRS | Trigger |
|---|---|---|---|
| **1099-NEC** | Jan 31 | **Jan 31** (no extension in practice) | Nonemployee compensation. Threshold **\$2,000 for payments made in 2026 or later** (was \$600), indexed from 2027 (verified 2026-09-23, Rev. Proc. 2025-32 §2.15). The §3406 backup-withholding trigger moved with it. |
| **1099-MISC** | Jan 31 | Feb 28 paper / Mar 31 e-file | Rents, other income |
| **W-2 / W-3** | Jan 31 | Jan 31 | Any payroll |
| **1042-S** | Mar 15 | Mar 15 | Payments to foreign persons |

- **Collect a W-9 before the first payment, not at year end.** Without a TIN,
  §3406 backup withholding at 24% is mandatory, and the liability is the payer's.
- E-file threshold is **10 or more information returns in aggregate** — filed
  through **IRIS**, which is generally the one direct-filing lane worth running
  in-house, since it needs no EFIN.
- Penalties under §6721/§6722 are **per form, per failure** (recipient copy and
  IRS copy are separate failures) and escalate with lateness; amounts in
  `audit-risk-substantiation/reference/penalty-map.md`.

## Quality bar

A return is ready for handoff when:

- Every line traces to a lead schedule, and every lead schedule to source.
- Every material variance from prior year is explained **in writing**.
- Every non-routine position has a FIRAC memo dated **before** the filing date.
- The carryforward schedule is rolled forward and reconciles.
- Zero open items. An unresolved question is not a rounding difference.
- A separate review pass has signed off.

_Draft for professional review — not tax advice. A licensed CPA, EA, or tax attorney must review before filing, paying, or acting._

## Reference files

- `reference/document-checklist.md` — read when requesting documents; lists what
  to collect by entity and income type and the reconciliation each supports.
- `reference/elections-and-deadlines.md` — read before finalizing any return;
  every election, its statement, deadline, and whether late relief exists.
- `reference/filing-calendar-2026.md` — read when dating deliverables for TY2026.
  For another year, rebuild the dates from the IRS calendar.

## Related skills

`deductions-and-credits`, `return-review` (mandatory before handoff),
`estimated-tax-compliance`, `cpa-standards`, `audit-risk-substantiation`.
