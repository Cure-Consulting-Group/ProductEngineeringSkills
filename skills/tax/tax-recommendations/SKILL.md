---
name: tax-recommendations
description: Turn tax analysis into a ranked, quantified action list for a specific taxpayer — screen opportunities, quantify after-tax benefit, score risk and effort, sequence by deadline, and present it so decisions get made. Use when asked what to do, for a tax plan, or to produce a client-facing deliverable.
argument-hint: "[taxpayer-or-entity]"
---

# Tax Recommendations

The delivery layer. Analysis that does not end in a dated, prioritized action list
does not reduce anyone's tax.

## Disclaimer
This skill produces draft analysis and workpapers, not tax, legal, or accounting advice. Nothing it produces is filing-ready until a licensed CPA, enrolled agent, or tax attorney has reviewed it. Model output is not authority and does not establish reasonable cause (see `cpa-standards`).

The failure mode this skill exists to prevent: a list of thirty generic ideas,
unquantified, unranked, with no deadlines — which produces zero action and reads
as padding.

## Principles

1. **Quantified or omitted.** Every recommendation carries a dollar estimate with
   its assumptions stated. "Consider a retirement plan" is not a recommendation;
   "Adopt a solo 401(k) by 12/31 — \$24,500 (indexed annually — confirm for the
   tax year via the `constants` binding) deferral saves ~\$8,900 federal + SE"
   is.
2. **Ranked by net after-tax benefit**, not by how interesting it is.
3. **Deadline-first ordering when a deadline is near.** A \$2,000 item due in three
   weeks outranks a \$20,000 item available all year.
4. **Risk stated, never buried.** Every item shows its rating and authority tier.
5. **One owner, one date, per item.** Unassigned actions do not happen.
6. **Short.** Five executed recommendations beat thirty listed ones. If the list
   exceeds ten, split into "Act now" and "Evaluate later."

## Workflow

### 1. Baseline
Compute current-year tax as-is. Nothing is a "saving" without a baseline. Use the
`calculator` binding with the tax year set explicitly.

### 2. Screen
- Benefits available on existing facts → `deductions-and-credits`
- Structural moves → `tax-strategies`
- Engine screens: the `optimizer` binding, where the project has one
- Engine output is **input to judgment**, not the deliverable. It cannot see
  whether documentation exists, whether the taxpayer will actually execute, or
  what happened last week.

### 3. Quantify
For each candidate, compute the **net after-tax benefit**:

```
  federal tax delta
+ state tax delta
+ SE / payroll tax delta
+ NIIT / Additional Medicare delta
− implementation cost (fees, admin, ongoing burden)
− value of any benefit given up
= net year-one benefit

then: multi-year benefit over the planning horizon
```

**Deferral is not savings.** A strategy that moves income to next year is worth
the time value plus any rate differential — not the full tax. Say which one it is.

With permanent TCJA rates under OBBBA, the pre-2025 "defer because rates rise in
2026" logic is dead. Purge it from any inherited plan.

### 4. Score
See `reference/scoring-model.md`. Three axes: **benefit**, **risk**, **effort**.

### 5. Sequence
Order by deadline first, then by score. Produce dates, not "by year end."

### 6. Present
Use the deliverable template below. Lead with the number.

## Deliverable

```markdown
# Tax Plan — [Entity/Taxpayer] — TY[year]
Prepared [date] · Baseline tax: $X · Identified opportunity: $Y

## Act now (deadline-driven)
| # | Action | Benefit | Deadline | Risk | Owner |

## High value (no near deadline)
| # | Action | Benefit | Effort | Risk | Owner |

## Evaluate
Items needing more facts, a decision, or outside counsel.

## Not recommended
What was considered and rejected, and why. ← do not skip this

_Draft for professional review — not tax advice. A licensed CPA, EA, or tax attorney must review before filing, paying, or acting._
```

**The "not recommended" section is not filler.** It prevents the same rejected
idea returning next quarter, and it demonstrates the analysis was actually
performed. Include anything from the kill list that a reasonable person would ask
about.

### Per-recommendation detail

```
[#] Action                                              $Benefit
    Mechanism    one or two sentences, plus the IRC section
    Requirements checklist of what must be true
    Steps        numbered, concrete, with the owner
    Deadline     an actual date
    Risk         Conservative / Moderate / Aggressive + authority tier
    Docs         what must exist contemporaneously
    Assumptions  what the quantification depends on
```

## Honesty rules

- Show the **downside** and the ongoing burden. An S election saves payroll tax
  *and* creates payroll filings, a comp study, and a separate return, forever.
- Where the number depends on an unverified figure, say so — `RECALL` and
  `VERIFY` flags carry through from `irc-lookup`, they do not get laundered into
  confidence by appearing in a table.
- Do not stack savings that cannot coexist. §179 and bonus on the same asset,
  §21 and §129 on the same dollars, the same deduction claimed at two entities —
  check for double-counting before totaling.
- The headline total must be the **net** of interactions, not the sum of the
  parts. Interacting items are the norm: a deduction that reduces QBI reduces the
  §199A deduction with it.
- Never present a strategy that fails the doctrine gate, even labeled as
  aggressive.

## Reference files

- `reference/scoring-model.md` — the benefit/risk/effort model, interaction
  handling, and worked prioritization examples.

## Related skills

`tax-strategies` (the source catalog), `deductions-and-credits`,
`audit-risk-substantiation` (risk ratings), `estimated-tax-compliance`
(cash-flow consequences), `cpa-standards` (how advice must be framed).
