# Tax Strategy & Planning

Where `deductions-and-credits` claims what already happened, this skill changes
what happens. Planning means arranging facts *before* they occur so a better
Code provision applies.

## Disclaimer
This skill produces draft analysis and workpapers, not tax, legal, or accounting advice. Nothing it produces is filing-ready until a licensed CPA, enrolled agent, or tax attorney has reviewed it. Model output is not authority and does not establish reasonable cause (see `cpa-standards`).

## The five levers — every strategy is one of these

| Lever | Mechanism | Examples |
|---|---|---|
| **Timing** | Move income or deduction between years to arbitrage rates | Accelerate deductions into a high-bracket year, defer income, bunch charitable gifts, install a fiscal year |
| **Character** | Convert a higher-taxed category to a lower one | Ordinary → long-term capital gain, wages → distributions, gain → §1202 excluded gain |
| **Entity** | Put income in a lower-taxed taxpayer | C-corp 21% vs individual 37%, PTET at the entity, spoke-level QSBS |
| **Rate arbitrage across people** | Shift income to a lower-bracket taxpayer | Family employment, gifts of appreciated property |
| **Exclusion** | Keep it out of gross income entirely | §1202, §280A(g), §121, HSA, municipal interest |

If a proposed "strategy" is none of these, it is probably either an ordinary
deduction (use the other skill) or not real.

## Non-negotiable gate

**No strategy is recommended until it passes all five doctrines** in
`reference/anti-abuse-doctrines.md`:

1. **Economic substance** (§7701(o)) — meaningful non-tax change in economic
   position *and* a substantial non-tax purpose. Codified, **strict-liability
   40% penalty** if it fails. No opinion letter saves it.
2. **Business purpose** — a real reason besides taxes.
3. **Substance over form** — what happened, not what was papered.
4. **Step transaction** — the pieces get collapsed into the end result.
5. **Assignment of income** — the earner is taxed; you cannot deflect income by
   redirecting the check.

Plus the arm's-length requirement of §482 for anything between related entities —
in play the moment one entity in a group performs services for another.

A strategy that saves tax and fails a doctrine is not a strategy; it is a penalty
with a delay.

## Workflow

1. **Model the baseline.** Compute current-year tax as-is before proposing
   anything, through the project's `calculator` binding with the tax year set
   explicitly. A strategy quantified against no baseline is a guess.
2. **Identify the binding constraint** — what is actually driving the tax? SE
   tax? A rate cliff? A phase-out? Double taxation? AMT? Strategies that don't
   touch the binding constraint produce noise.
3. **Screen the playbook** (`reference/strategy-playbook.md`) against the facts.
4. **Quantify each candidate**: federal + state + SE/payroll + NIIT delta, net of
   implementation cost, over the **full multi-year horizon** — many strategies
   borrow from a later year rather than creating savings.
5. **Run the doctrine gate.** Kill anything that fails; document why for anything
   that passes.
6. **Score risk**: audit exposure, penalty exposure if lost, and the disclosure
   requirement. See `audit-risk-substantiation`.
7. **Sequence.** Many strategies have deadlines that precede the return
   (elections, plan adoption, entity formation). Produce a dated action list, not
   a menu.
8. **Hand to `tax-recommendations`** for ranking and presentation.

## Deadline discipline — the failure mode that matters most

The most common way a real strategy is lost is a missed election, not a bad idea.
These are unforgiving:

| Election | Deadline | Consequence of missing |
|---|---|---|
| **§83(b)** | **30 days from transfer**, no extensions | Ordinary income on every vesting tranche at then-FMV; QSBS clock delayed. Form 15620 may be used. |
| **S corporation election (Form 2553)** | 2 months 15 days into the year | Taxed as C-corp for the year (late relief under Rev. Proc. 2013-30 may apply) |
| **§41(h) payroll offset** | On the **timely filed original return** | Credit becomes a carryforward instead of cash |
| **Retirement plan adoption** | 401(k) by year end for deferrals; SEP by the return due date incl. extensions | Deduction lost for the year |
| **NY PTET election** | **March 15** of the tax year | Entire SALT workaround unavailable for that year |
| **§1045 QSBS rollover** | 60 days from sale | Gain fully recognized |
| **§1031 exchange** | 45-day ID / 180-day close | Full gain recognition |
| **Form 8850 (WOTC)** | 28 days from hire | Credit lost |
| **§475(f) mark-to-market** | Due date of the *prior* year's return | Wait a full year |

`reference/strategy-playbook.md` carries the deadline for every strategy listed.

## Output shape

For each recommended strategy:

- **Name and IRC basis** — with confidence per `irc-lookup`
- **Mechanism** — which of the five levers, and how it works in two sentences
- **Quantified benefit** — federal / state / SE / NIIT, current year and horizon
- **Requirements** — the elements that must be true, as a checklist
- **Deadline and sequence** — dated
- **Doctrine analysis** — how it survives economic substance and business purpose
- **Risk rating** — Conservative / Moderate / Aggressive, with the authority tier
- **Documentation required** — what must exist contemporaneously
- **Who executes** — the taxpayer, the CPA, or counsel

_Draft for professional review — not tax advice. A licensed CPA, EA, or tax attorney must review before filing, paying, or acting._

## Framing rule

Do not use the word "loophole" in a work product. Every position here is either
supported by authority or it is not taken. Use "strategy," "election,"
"structure," or "planning opportunity," and state the authority tier plainly. If
a client-facing document would embarrass the taxpayer at audit, rewrite it.

## Reference files

- `reference/strategy-playbook.md` — the catalog: ~40 strategies with mechanism,
  requirements, quantification, deadline, and risk rating.
- `reference/anti-abuse-doctrines.md` — the five doctrines, the §7701(o) test,
  reportable transactions, and the kill list of strategies that do not work.
- `reference/entity-playbook.md` — how to build the per-entity playbook for a
  specific group: the questions to answer per entity type, hub-and-spoke and
  spinout sequencing, and QSBS placement.

## Related skills

`irc-lookup`, `deductions-and-credits`, `audit-risk-substantiation`,
`tax-recommendations`, `estimated-tax-compliance` (cash-flow consequences).
