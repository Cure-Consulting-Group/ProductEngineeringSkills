# QRE Qualification for Software

## Decision tree — run per project, not per company

```
Is the work software development?
  └─ NO  → not §174A; ordinary §162 or capital §263
  └─ YES ↓

Was it performed in the United States?
  └─ NO  → §174 foreign: 15-year amortization, and NO §41 credit ever
  └─ YES ↓

§174A: currently deductible.  Now test the credit.

Is the taxpayer funded by another party who bears the risk / takes the rights?
  └─ YES → FUNDED RESEARCH — no credit. (Client work billed at cost-plus
            with the client owning the deliverable is the classic case.)
  └─ NO  ↓

Was it performed AFTER the product was ready for commercial release?
  └─ YES → excluded as "research after commercial production" unless it is a
            genuinely NEW component with its own uncertainty
  └─ NO  ↓

Is the software for sale, lease, or license to third parties?
  ├─ YES → NOT internal-use. Apply the four-part test only.
  ├─ NO  → INTERNAL-USE. Four-part test PLUS high threshold of innovation.
  └─ BOTH → dual function. Reg. §1.41-4(c)(6) safe harbor: if ≥10% third-party
             use, include 25% of the dual-function subset's QREs.
```

## Four-part test — worked through software scenarios

| Scenario | Qualifies? | Reasoning |
|---|---|---|
| Designing a new ML inference pipeline with unknown latency/accuracy tradeoffs; benchmarking three architectures | **Yes** | Uncertainty as to method and appropriate design; alternatives systematically evaluated |
| Building a HIPAA-compliant real-time transcription system where the achievable accuracy is unknown | **Yes** | Capability uncertainty; iterative experimentation |
| Designing a schema and sync strategy for offline-first mobile with conflict resolution | **Yes** | Appropriate-design uncertainty; alternatives tested |
| Integrating Stripe using documented API patterns | **No** | No technological uncertainty — the method is known and published |
| Building a marketing site in a standard framework | **No** | No uncertainty; also style/cosmetic |
| Restyling an existing UI, changing colors and layout | **No** | Explicitly excluded — style, taste, cosmetic |
| Fixing bugs in a shipped product | **No** | Research after commercial production |
| Porting an existing feature to a new platform with no new technical problem | **No** | Duplication / adaptation |
| Customizing a shipped product for one customer's requirements | **No** | Explicitly excluded — adaptation to a particular customer |
| Building a novel matching algorithm where the approach is genuinely unknown at the outset | **Yes** | Method uncertainty; documented alternatives |
| Upgrading a dependency, refactoring for readability | **No** | No uncertainty; routine |
| Prototyping three data models for a new domain and load-testing each | **Yes** | Process of experimentation |

## The uncertainty requirement — the element most often failed

Uncertainty must have existed **at the outset**, and must concern:
- **Capability** — can the desired result be achieved at all?
- **Method** — how should it be achieved?
- **Appropriate design** — which of several possible designs is right?

Uncertainty about **schedule, budget, market fit, or which feature to build** is
not technological uncertainty. "We didn't know if users would like it" is a
business risk, not a §41 QRE.

**The documentation implication**: the file must show what was technically unknown
**before** the work started. A retrospective assertion that "it was hard" is the
weakest possible evidence. Capture it in the design doc, the RFC, or the ticket at
the time.

## Process of experimentation

**Substantially all (≥80%)** of the research activities must constitute a process
of evaluating alternatives. Evidence that satisfies this in a software context:

```
✓ Design documents comparing 2+ approaches with tradeoffs
✓ Spike/prototype branches that were built and abandoned
✓ Benchmark results across candidate implementations
✓ A/B or shadow-mode tests of competing algorithms
✓ Architecture decision records (ADRs) with rejected alternatives
✓ Failed experiments — these are among the BEST evidence, keep them
✗ A single linear implementation with no alternatives considered
✗ "We built it and it worked"
```

Failed and abandoned work qualifies. Do not delete the branches.

## Internal-use software — the high threshold of innovation

Only applies when software is **not** for sale, lease, or license to third
parties. All three must be met:

1. **Innovative** — would result in a reduction in cost, improvement in speed, or
   other measurable improvement that is substantial and economically significant.
2. **Significant economic risk** — substantial resources committed and substantial
   uncertainty, *because of technical risk*, that the resources would be recovered
   in a reasonable period.
3. **Not commercially available** — could not be purchased and used without
   modifications requiring the above.

This is hard to meet. Assume internal tooling fails it unless there is a clear
case.

## Applying this across a portfolio of repos

Provisional classification — **confirm each before relying on it**. See
`repo-inventory-template.md` for the full intake sheet.

| Character | Repos | §41 posture |
|---|---|---|
| **Commercial products**\* (sale/lease/license to third parties) | Every repo behind a shipped or shipping customer-facing product | **Exempt from the IUS test.** Four-part test only. Best posture. |
| **Likely client/consulting work** | client-site-a, client-site-b, agency-website, client-app | **Probably FUNDED research → no credit.** Check who bore the risk and who owns the IP. Still §162/§174A deductible. |
| **Internal tooling** | Repos that serve only the company itself — internal platforms, developer tooling, back-office automation | **Internal-use — high threshold of innovation applies.** Assume no credit absent a strong case. |
| **Needs determination** | Repos whose commercial status or owning entity is unresolved | Classify before year end |

\* A product straddling the line qualifies as commercial only if it is actually sold or licensed out — intent to sell it later is not enough.

### Two consequential notes

**Client work is the biggest risk of over-claiming.** A repo built for a paying
client, where the client owns the deliverable and pays regardless of technical
success, is **funded research** under §41(d)(4)(H) — no credit, for anyone. The
test is who bears the economic risk and who retains substantial rights. Fixed-fee
work with IP assignment to the client fails both. Segregate these repos now.

**A platform sold *to* a §280E industry is probably NOT a §280E problem.** §280E
disallows deductions for a business **trafficking** in a controlled substance. A
software vendor selling a platform to a business in that industry is not itself
trafficking; it is a software business. Keep the software-vendor activity clearly
separated from any trafficking activity, with distinct books, revenue, and
contracts, so the distinction is obvious on its face.

## Substantiation package per project

```
[ ] Project/product name, and the entity that owns it
[ ] Business component identified (the product, process, or software itself)
[ ] Technical uncertainty statement, dated at project start
[ ] Alternatives considered, with the evaluation and outcome
[ ] Evidence of experimentation: ADRs, spikes, benchmarks, abandoned branches
[ ] Start date and the commercial-release date  ← the pre/post boundary
[ ] Personnel: who, role, hours or % allocation, W-2 wages
[ ] Contractors: agreement showing risk allocation and IP ownership
[ ] Cloud/compute allocated between R&D and production hosting
[ ] Whether any of it was client-funded
[ ] Commit history export as corroboration
```

## Time allocation methods, strongest to weakest

1. **Contemporaneous time tracking by project** — the gold standard.
2. **Periodic (e.g. monthly) allocation certifications** signed by the engineer,
   supported by project artifacts.
3. **Post-hoc allocation supported by objective evidence** — commit history,
   ticket assignments, sprint records. Defensible if the evidence is genuinely
   contemporaneous even though the allocation is not.
4. **Estimated percentages with no supporting artifacts** — routinely reduced or
   disallowed on exam.

If contemporaneous tracking did not begin at the start of the year, method 3 is
the realistic target for elapsed periods, and method 1 or 2 should begin for the
remainder. Pair the commit data with a signed allocation memo per person per
project while memories are fresh.
