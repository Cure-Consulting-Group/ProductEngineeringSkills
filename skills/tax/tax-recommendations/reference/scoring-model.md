# Scoring & Prioritization Model

## Three axes

### Benefit — net after-tax dollars

```
Year-one net = Δfederal + Δstate + ΔSE/payroll + ΔNIIT
             − implementation cost − ongoing annual cost
             − value of anything given up

Horizon net  = sum over the planning horizon, discounted if material
```

Classify honestly:

| Type | Meaning | How to value |
|---|---|---|
| **Permanent** | Tax never paid | Full amount |
| **Deferral** | Tax paid later | Time value + rate differential only |
| **Rate arbitrage** | Same income, lower rate | The rate difference |
| **Conversion** | Character changed | Rate difference on the converted amount |

Labeling a deferral as a saving is the most common way a plan overstates itself.

### Risk

| Rating | Meaning | Authority | Documentation |
|---|---|---|---|
| **Conservative** | Settled, routine | Statute + regs, clear application | Normal records |
| **Moderate** | Supported but fact-dependent | Statute + regs, facts must be built and held | Contemporaneous file + memo |
| **Aggressive** | Defensible, contested | Substantial authority arguable; expect scrutiny | Third-party support, memo, consider disclosure |
| **Rejected** | Fails a doctrine or lacks reasonable basis | — | Not recommended at any benefit level |

### Effort

| Level | Meaning |
|---|---|
| **Trivial** | A form, an election, a policy document. Hours. |
| **Moderate** | New account, plan adoption, process change. Days. |
| **Heavy** | Entity formation, payroll setup, restructuring, outside advisors. Weeks to months, with ongoing burden. |

## Priority score

```
Priority = (Net benefit × Risk factor) / Effort factor

Risk factor:    Conservative 1.0 · Moderate 0.7 · Aggressive 0.4
Effort factor:  Trivial 1 · Moderate 2 · Heavy 4
```

The risk factor is a **decision weight, not a probability**. It does not encode
audit odds — it encodes the discount for a benefit that may not survive review and
carries penalty exposure.

**Deadline override**: anything whose deadline falls within 60 days moves to the
top regardless of score. A lapsed election has a benefit of zero.

## Interactions — check before totaling

Recommendations are rarely independent. Common interactions:

| Interaction | Effect |
|---|---|
| Deduction ↓ taxable income → ↓ §199A deduction | QBI is 20% of QBI but capped by 20% of taxable income less net capital gain. A big deduction can cost part of the QBI benefit. |
| S corp wage ↓ → ↓ §199A W-2 wage limit | Above the threshold, cutting the wage to save payroll tax can cut the QBI deduction by more. |
| §179 vs bonus on the same asset | Mutually exclusive on the same basis. |
| Retirement contribution ↓ AGI → phase-outs unlock | Positive interaction — often makes the contribution worth more than its face rate. |
| PTET ↓ federal income → ↓ value of other deductions | Ordering matters. |
| Accelerating deductions into a loss year | Worth **less**, not more — the deduction is wasted against zero and only adds to an NOL limited to 80% later. |
| §280C(c) election | Trades credit for deduction; compute both. |
| Any deduction at an entity with an NOL | Deferred value, not current value. |

**Never total the raw savings.** Recompute the return with the full package
applied and take the difference from the baseline. Report that number.

## Worked prioritization — an early-stage software C corp

Illustrative of the method only. The actions are real and common; the ranking for
any given taxpayer requires their actual profile.

| Action | Benefit | Risk | Effort | Score | Deadline |
|---|---|---|---|---|---|
| Establish owner payroll → unlock wage QREs → R&D credit | High, recurring | Moderate | Heavy | High | Before year end to affect TY2026 |
| §41(h) payroll offset election | Converts dead credit to cash | Conservative | Trivial | **Highest** | **Timely filed original return — cannot be added later** |
| Written capitalization policy (de minimis safe harbor) | Small, recurring | Conservative | Trivial | High | **Must be in place Jan 1** |
| Paper intercompany services agreements | Defensive, not dollar-generating | Conservative | Moderate | Medium | Before the spinout closes |
| §174A retroactive review for 2022–2024 | Potentially large one-time | Moderate | Moderate | High | Form 3115 with the return |
| §531 monitoring | Preventive | Conservative | Trivial | Low now | As earnings grow |

Note the pattern: the **highest-scoring item is a trivial-effort election with a
hard deadline**, not the largest-dollar structural change. That is typical, and it
is why deadline-first ordering matters.

## Presentation rules

- Lead with the net number. Not the methodology.
- Round sensibly. `$8,900` reads as an estimate; `$8,943.17` implies precision the
  model does not have and invites argument about the wrong thing.
- One line per recommendation in the summary table; detail below.
- Show the deadline as a **date**, never "year end" or "soon."
- Name an owner. "TBD" means it will not happen.
- Carry `VERIFY` / `RECALL` flags into the deliverable. A number that depends on an
  unconfirmed OBBBA provision must say so where the reader will see it.
