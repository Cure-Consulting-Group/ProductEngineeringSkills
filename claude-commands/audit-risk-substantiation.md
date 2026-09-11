# Audit Risk & Substantiation

Two jobs: **assess** exposure honestly, and **build the file** that answers it
before anyone asks.

The controlling insight: audits are won or lost on documentation that existed
**before** the notice arrived. A position created at examination is worth a
fraction of the same position documented contemporaneously — and for §274(d)
categories and §170 acknowledgments, after-the-fact documentation is worth
nothing at all.

## Risk framing — the honest version

Risk has two independent dimensions. Conflating them produces bad decisions.

| Dimension | Question | Drives |
|---|---|---|
| **Detection likelihood** | How likely is this to be examined? | Nothing about whether to take the position |
| **Sustainability** | If examined, does it survive on the merits? | Everything |

**Audit probability may not enter the analysis** (Circular 230 §10.37). It is
relevant only to *operational* decisions — how much to invest in documentation,
whether to disclose to start the statute running. It is never a reason to take a
position that would not otherwise be taken, and it must never appear in a
workpaper.

## Scoring a position

```
1. MERITS      Authority tier + confidence standard.
               → irc-lookup/reference/authority-hierarchy.md
2. PROOF       Does the substantiation exist, contemporaneously?
               → deductions-and-credits/reference/substantiation-by-deduction.md
3. PENALTY     What is the exposure if lost?  → reference/penalty-map.md
4. DISCLOSURE  Required? Beneficial?          → reference/penalty-map.md
5. DOCTRINE    Economic substance and friends → tax-strategies/reference/anti-abuse-doctrines.md
```

Output: **Conservative / Moderate / Aggressive**, with the specific weakness
named. "Moderate risk" with no stated reason is not an assessment.

## The decision that matters

```
Substantial authority (~40%)?    → file, no disclosure needed
Reasonable basis only (~20%)?    → file ONLY with Form 8275 / 8275-R
Neither?                         → do not take it; advise in writing
Tax shelter / reportable?        → MLTN required + Form 8886
Economic substance failure?      → do not take it. 40% strict liability,
                                   no reasonable cause, no opinion helps
```

Disclosure defeats the substantial-understatement penalty but does **not** help
for negligence, listed transactions, or §7701(o) failures — and it advertises the
issue. Weigh both.

## Engine support

Where the project has an `audit-risk` binding, it produces a scored risk profile
from a taxpayer profile. Treat the score as a **prompt for judgment**, not a
verdict — no scorer can see whether the documentation actually exists. Where
there is no such binding, score by hand against `reference/audit-triggers.md`;
the triggers are the substance and the code is only a convenience.

## Building the defense file

For every position rated Moderate or above, before filing:

```
[ ] FIRAC position memo, dated before the filing date
      → cpa-standards/reference/workpaper-standards.md
[ ] Primary substantiation (receipts, logs, contracts, appraisals)
[ ] Contemporaneous corroboration (calendar, email, minutes, photos)
[ ] Third-party support (comp study, appraisal, benchmark data, venue quotes)
[ ] Computation workpaper showing the derivation
[ ] Authority file: the sections, regs, and rulings actually relied on
[ ] Disclosure form if required, prepared and attached
```

**Contemporaneous means created at or near the time of the event.** A calendar
entry from the day of a meeting outweighs a memo written two years later, even
when both say the same thing.

## If a notice arrives

1. **Read what it actually is.** CP2000 (automated underreporter matching) is not
   an audit; correspondence, office, and field examinations differ substantially
   in scope and posture.
2. **Note the response deadline.** Most are 30 days. Missing it converts a
   negotiation into a default assessment.
3. **Pull the workpaper file** before responding. Answer from the file, not from
   memory.
4. **Answer only what was asked.** Volunteering scope is the most common
   self-inflicted wound in an examination.
5. **Respond in writing**, with the authority and the documents attached.
6. **Escalate** to the accountant of record and, where warranted, counsel:
   anything with fraud exposure, a listed transaction, a QSBS qualification
   question, or a material position where the taxpayer is also the preparer.
7. Preserve appeal rights — 30-day letter → Appeals; 90-day statutory notice →
   Tax Court petition (**the 90 days is jurisdictional and cannot be extended**).

## Reference files

- `reference/penalty-map.md` — every relevant penalty with rate, trigger,
  defense, and whether disclosure helps.
- `reference/audit-triggers.md` — what statistically and structurally draws
  examination, and how to build the group's exposure profile.

## Related skills

`cpa-standards` (preparer obligations), `irc-lookup` (authority strength),
`deductions-and-credits` (substantiation requirements),
`tax-strategies` (doctrine screening), `return-review`.
