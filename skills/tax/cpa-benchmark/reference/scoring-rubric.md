# Scoring Rubric & Remediation

## Automatic grading

| Type | Rule |
|---|---|
| `mcq` | Exact letter match, case-insensitive |
| `numeric` | Within `tolerance` of `answer`. Currency symbols, commas, and whitespace are stripped before parsing. |
| `short` | Not auto-graded — reported separately for manual review |

## Grading a `short` / research response manually

Score each dimension 0–2. A response passes at **7 of 10**.

| Dimension | 0 | 1 | 2 |
|---|---|---|---|
| **Correct conclusion** | Wrong | Directionally right, materially imprecise | Right |
| **Controlling authority cited** | None or wrong section | Right section, no subsection or regulation | Precise cite including subsection and implementing authority |
| **Elements applied to facts** | Recites the rule only | Applies some elements | Every element applied to the actual facts, with the failing ones named |
| **Limits and exceptions** | Missed | Partially identified | Phase-outs, caps, and disqualifiers all surfaced |
| **Confidence honesty** | Overclaims certainty | Vague hedging | States VERIFIED / CATALOG / RECALL and flags what needs verification |

**Automatic zero**, regardless of the rest, for any response that:
- States a dollar threshold with no source and no verification flag.
- Cites audit probability as a reason to take a position.
- Recommends a position that fails economic substance without saying so.
- Omits a hard deadline (§83(b), PTET, §41(h), Form 8850) on a strategy where one
  applies.

Those four are the failure modes that cause actual harm. A wrong answer is a
knowledge gap; these are process failures.

## The remediation loop

For each miss:

```
1. Read the cited section — primary text, not the explanation.
2. Ask: which reference file in this library SHOULD have prevented this?
     · found it, rule was there      → retrieval failure. The rule is buried or
                                       the SKILL.md does not route to it. Fix the
                                       routing or promote the rule.
     · found it, rule was WRONG      → correct it, and check every sibling claim
                                       in that file written at the same time.
     · no file carries the rule      → coverage gap. Add it.
3. If the miss was numeric, verify the project's `constants` binding agrees with
   the statute — the engine may be wrong, not just the answer.
4. Add a variant question so the same rule is tested from a different angle.
5. Re-run. A fix that does not move the score did not fix anything.
```

**A miss on a project's own applied question is more serious than a miss on
`reg-core`.** Generic tax error is a knowledge gap; error on the actual entity
structure in front of you is a live filing risk. Treat those as P0.

## Pre-filing gate

Before the system's output is used on a real return:

```bash
node run.mjs score answers.json || echo "BLOCKED — remediate before filing"
```

Gate criteria, all required:

```
[ ] Overall score >= 75%
[ ] The project's applied overlay set >= 90% — no exceptions
[ ] Ethics/Professional Responsibility area = 100%
[ ] Zero misses on any question tagged with a hard deadline
[ ] Every VERIFY-flagged item relied on for this return confirmed against
    primary text, and its flag updated
[ ] Human review sign-off recorded per cpa-standards/reference/workpaper-standards.md
```

Ethics is held at 100% deliberately. A competency gap produces a wrong number,
which review catches. An ethics gap produces a §7216 disclosure or an undisclosed
unreasonable position, which review does not catch because nobody is looking for
it.

## Tracking over time

Record each run so drift is visible:

| Date | Overall | reg-core | tcp | portfolio | Trigger | Notes |
|---|---|---|---|---|---|---|
| | | | | | | |

Re-run on: any change to the `constants` binding, any new tax year, any
legislation, before each filing season, and after any material edit to the skill
library.
