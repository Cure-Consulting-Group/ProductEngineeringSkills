---
name: technical-estimation
description: "Build defensible software estimates with explicit uncertainty — decomposition, PERT, reference-class forecasting, risk contingency"
when_to_use: "Use when an estimate will be bid against or held to for years. NOT for quick internal budgeting (use engineering-cost-model). NOT for pricing structure (use proposal-generator)."
argument-hint: "[project-or-scope-name]"
allowed-tools: ["Read", "Grep", "Glob", "Bash", "Write", "Edit", "WebSearch"]
---

# Technical Estimation

Produce estimates you can defend under scrutiny and be held to under contract.

The distinction from casual estimation: **a bid estimate is a commitment, not a forecast.** When a fixed price is locked for five years with no escalator, the estimate *is* the margin. The goal is not a single confident number — it is a range with stated assumptions, an explicit confidence level, and contingency sized to the real risks.

## Pre-Processing (Auto-Context)

- Requirements source: !`ls 01-analysis/requirements-matrix.md docs/PRD*.md 2>/dev/null || echo "(none found)"`
- Comparable past projects: !`ls -d ../*/ 2>/dev/null | head -20`
- Stack manifest: !`head -30 package.json 2>/dev/null || head -30 build.gradle.kts 2>/dev/null || echo "(none)"`
- Repo scale, if estimating against existing code: !`git ls-files 2>/dev/null | wc -l`

## Step 1: Establish what kind of estimate this is

| Type | Target accuracy | Method | When |
|---|---|---|---|
| Rough order of magnitude (ROM) | −25% / +75% | Analogy to past projects | Go/no-go screening |
| Budgetary | −10% / +25% | Parametric + decomposition | Bid pricing |
| Definitive | −5% / +10% | Bottom-up from a task list | Post-award planning |

**State which one you are producing.** Presenting a ROM with the precision of a definitive estimate is the most common estimation failure, and the most expensive. `\$1.8M` implies a rigor that `\$1.5M–\$2.5M` honestly disclaims.

Public-sector bids need a **budgetary** estimate. You cannot produce a definitive estimate from a requirements matrix alone — there is no design yet.

## Step 2: Decompose against the requirements, not the architecture

Estimate against **what the buyer asked for**, so every requirement ID maps to effort and nothing is silently dropped.

```markdown
| Req ID | Component | Optimistic | Likely | Pessimistic | PERT | Confidence |
|---|---|---:|---:|---:|---:|---|
| F-7 | Ride scheduling + 4 provider integrations | 320 | 560 | 1200 | 613 | Low — providers unnamed |
```

**PERT expected value:** `(O + 4M + P) / 6`
**Standard deviation:** `(P − O) / 6`
**Range at ~95% confidence:** `PERT ± 2σ`

Roll up: total PERT is the sum; total σ is `sqrt(Σσᵢ²)` — **not** the sum of the σs. Independent variances add in quadrature, which is why a portfolio of tasks is proportionally less uncertain than any single task. This is the mathematically correct reason not to simply add worst cases.

### Where pessimistic estimates come from

The pessimistic value is not "likely × 2." Derive it from the specific thing that could go wrong:

- Third parties you do not control (unnamed integration partners, buyer-side approvals)
- Technologies nobody on the team has shipped
- Requirements with unresolved ambiguity
- Anything requiring buyer sign-off in a cycle you do not set
- Regulatory or safety review

If you cannot name the failure mode, your pessimistic number is decoration.

## Step 3: Apply reference-class forecasting

Inside-view estimates — summing tasks you can imagine — are systematically optimistic, because you cannot imagine the work you have not thought of. Correct with the outside view.

1. Identify comparable completed projects (yours first, industry data second)
2. Record what they were *estimated* at and what they *actually* cost
3. Compute the historical ratio
4. Apply it to the bottom-up number

```bash
# Survey comparable work already in the workspace
ls -d ../*/ | head -30
```

**If you have no history, say so and use a documented industry multiplier rather than pretending to precision.** Typical inside-view underestimation for greenfield software runs 1.3×–2.0×. For work with regulatory adjacency, novel technology, or many external dependencies, the top of that range is the realistic floor.

Record the multiplier and the reason. An estimate that says "bottom-up 9,800 hrs × 1.4 reference-class = 13,700 hrs" is auditable. One that says "about 14,000 hours" is not.

## Step 4: Separate effort from calendar

Effort (person-hours) and duration (calendar time) are different quantities, and conflating them is how schedules slip before work starts.

| Factor | Effect |
|---|---|
| Utilization | Nobody delivers 40 productive hours/week. Plan 28–32 |
| Onboarding | First 2–4 weeks per person are net-negative |
| Brooks's Law | Adding people to a late project makes it later |
| Buyer-side dependencies | Approvals, access provisioning, stakeholder availability |
| Sequential gates | Pilots, security reviews, and go/no-go gates cannot be parallelized |
| Contract start | Award ≠ kickoff. Negotiation and board approval take weeks to months |

Compute duration from a **staffing profile**, not by dividing hours by an assumed team size:

```markdown
| Phase | Effort (hrs) | Peak FTE | Duration | Gate |
|---|---:|---:|---|---|
| Discovery | 1,400 | 3 | 8–10 wks | Roadmap approval |
| MVP build | 7,200 | 8 | 20–26 wks | Feature complete |
```

Then state the **realistic go-live date including pre-contract time**. A buyer reading "11–14 months" needs to know whether that clock starts at award or at kickoff.

## Step 5: Size the team honestly

List roles, allocation, and — critically — which ones you do not currently have.

```markdown
| Role | Allocation | Have it? | If not |
|---|---|---|---|
| Accessibility specialist | 0.5 FTE | No | Subcontract — must be named in the proposal |
```

**Peak team size is a capacity constraint, not just a cost input.** A firm of six cannot staff a ten-person peak without either hiring or abandoning other clients. If the estimate implies a team you cannot field, the estimate is not the problem — the pursuit is.

Flag specialist gaps explicitly. In public-sector bids, subcontractors usually must be **named in the proposal**, so gaps discovered late cannot be filled at all.

## Step 6: Contingency and risk

Contingency is not padding. It is a priced reserve against named risks.

```markdown
| Risk | Probability | Impact (hrs) | Expected (hrs) | Mitigation |
|---|---:|---:|---:|---|
| Integration partners unnamed at bid time | 70% | 800 | 560 | Price integrations as options |
```

Sum expected values → risk reserve. Add separately from the PERT roll-up, and **show it as a line item**. Buyers respect a named contingency far more than a number quietly inflated by 20%.

Distinguish two categories:
- **Known unknowns** → contingency reserve, owned by the project
- **Unknown unknowns** → management reserve, owned by the firm, typically 5–10%

## Step 7: Non-labor and multi-year costs

Labor is rarely the whole picture, and multi-year contracts change the arithmetic.

| Category | Watch for |
|---|---|
| Cloud infrastructure | Size for the *committed* SLA (HA, auto-scaling), not the happy path |
| Usage-based services | SMS, voice, translation, maps, LLM tokens — scale with adoption |
| Third-party audits | Annual penetration testing, SOC 2 maintenance |
| Insurance | Public-sector limits are often far above commercial norms |
| Store/registration fees | Small but must appear |
| Support and maintenance | Typically 15–25% of build cost annually |

### The fixed-rate trap

When a contract fixes rates for N years with no escalator:

- The **rate card** must stay flat — that is the contractual obligation
- The **annual totals** need not, if the cost form has per-year columns. Forward cost growth belongs in the quantities and totals
- Real compensation erodes annually at the inflation rate. A flat five-year rate is a real-terms pay cut of 15–25%
- Model each year separately and show the margin trajectory

### Usage-based costs with unknown volume

Never absorb open-ended consumption risk in a fixed price. Price as a stated pass-through:

> Assumed volume: N users, X units/user/month. Rate: $__ per unit, at cost plus __% administration. True-up if actual exceeds assumed by more than __%.

Put the assumed volumes in the technical narrative too, so buyer and evaluator see the same numbers.

## Step 8: Present the estimate

Never present a single number. Present a distribution with the assumptions attached.

```markdown
## Estimate summary

**Type:** Budgetary (−10% / +25%)
**Basis:** Bottom-up against 63 requirements × 1.4 reference-class multiplier

| | Hours | At \$165/hr blended |
|---|---:|---:|
| Bottom-up PERT | 10,400 | \$1.72M |
| Reference-class adjusted | 14,560 | \$2.40M |
| Risk reserve (named) | 1,850 | \$0.31M |
| **Budgetary total** | **16,410** | **\$2.71M** |
| 80% confidence range | 13,900–19,200 | \$2.29M–\$3.17M |

**Assumptions this rests on:** <numbered list>
**What would move it most:** <the two or three biggest swing factors>
```

**The assumptions list is the most important part.** It is what converts an estimate from a guess into a defensible position, and it is what you point to when scope changes.

## Step 9: Sanity checks

Before shipping the estimate:

- [ ] Does every requirement ID map to some effort line?
- [ ] Is the pessimistic case tied to a named failure mode?
- [ ] Is σ rolled up in quadrature, not summed?
- [ ] Is the reference-class multiplier stated with its source?
- [ ] Is duration derived from a staffing profile, not hours ÷ team size?
- [ ] Does the peak team exist, or is there a named plan to get it?
- [ ] Is contingency a separate, itemized line?
- [ ] Are multi-year costs modeled per year, not averaged?
- [ ] Is usage-based cost a pass-through with stated assumed volume?
- [ ] Does the summary lead with a range and a confidence level?
- [ ] Would a skeptical reviewer be able to audit every number to its basis?

## Anti-patterns

| Anti-pattern | Why it fails |
|---|---|
| A single number with no range | Implies precision you do not have; you will be held to the number |
| Padding instead of contingency | Invisible, unarguable, and lost in negotiation |
| Estimating only the code | Discovery, testing, docs, training, launch, and support are usually >50% |
| Summing standard deviations | Overstates portfolio uncertainty; use quadrature |
| Ignoring the reference class | Inside-view estimates are optimistic in a known, measurable way |
| Duration = hours ÷ team size | Ignores utilization, onboarding, gates, and buyer dependencies |
| Flat multi-year totals | Real margin erodes every year of a fixed-rate contract |
| Absorbing usage-based risk | Adoption you cannot predict becomes a loss you cannot cap |
| Estimating a team you cannot field | The estimate is fine; the pursuit is the problem |

## Handoff

- Cost structure and rate cards → `engineering-cost-model`
- Pricing strategy and options → `proposal-generator`
- Whether the economics justify the pursuit → `bid-decision`
- Delivery sequencing → `project-manager`
