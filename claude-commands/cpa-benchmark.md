# CPA Competency Benchmark

A skill library that *sounds* authoritative and one that *is* authoritative look
identical until something is measured. This skill is the measurement.

It exists for three jobs:
1. **Baseline** — establish, in a number, how well the system reasons about tax.
2. **Regression gate** — after editing constants, engine modules, or skill
   reference files, prove nothing degraded.
3. **Remediation loop** — every miss names the section, the reason, and the
   reference file that should have prevented it.

**Done when** `score` has run, the band is reported, and every miss is mapped to
the reference file that should have carried the rule (or flagged as a gap).

## Running it

Requires Node (`run.mjs`). Run from this skill's `benchmark/` directory — in an
installed plugin, `<plugin>/skills/tax/cpa-benchmark/benchmark`.

```bash
cd <plugin>/skills/tax/cpa-benchmark/benchmark

node run.mjs stats                       # coverage summary
node run.mjs sources                     # which question dirs are in play
node run.mjs list                        # exam mode — questions, no answers
node run.mjs list --set tcp-planning     # one set
node run.mjs list --area QSBS            # one area
node run.mjs template > /tmp/answers.json
node run.mjs score /tmp/answers.json     # grade, report, exit 1 on fail
node run.mjs key --set reg-core          # answer key with citations
```

**Exit code is 0 on pass (≥75%), 1 on fail** — so it drops straight into CI or a
pre-filing gate.

### Self-assessment protocol

To benchmark *yourself* honestly, the order matters:

1. `node run.mjs list` — read the questions **only**.
2. Answer every one **before** looking at any reference file, the key, or the
   engine source. Write them into the template.
3. `node run.mjs score`.
4. For each miss, read the cited section and the `why`, then find which reference
   file in this library should have carried that rule. If none does, **that is the
   finding** — add it.

Consulting the key first produces a number that means nothing. The value is in
the misses.

## The question bank

| Set | Questions | What it tests |
|---|---|---|
| `reg-core` | 22 | REG blueprint: ethics and professional responsibility, federal tax procedure, individual taxation, property transactions, entity taxation |
| `tcp-planning` | 18 | TCP discipline: QBI planning, QSBS and exit, compensation, retirement, entity choice, loss limitations, SALT, credits |
| `software-and-exempt` | 12 | §174A/§41 software development costs, funded research, the IUS rules, and exempt-organization wind-down |

**52 bundled questions**, mixed multiple choice and computational. Every item
carries an IRC citation and an explanation of why the wrong answers are wrong.

### Local question overlays — the set that matters most

Generic competency is table stakes. The harder and more valuable test is whether
the system is right about **one specific taxpayer**, and those questions cannot
ship in a shared library because they are built out of filed figures.

So a project writes its own applied sets and points the runner at them:

```
CPA_BENCHMARK_QUESTIONS=dir1:dir2          # by environment (any runtime)
node run.mjs list --questions <dir>        # or explicitly, per run
.claude/tax-benchmark/questions/*.json     # or auto-discovered from the cwd
```

Same schema; an overlay question sharing an id with a bundled one replaces it.
`node run.mjs sources` prints what loaded and from where.

Applied questions are worth writing for the traps that are structural rather than
arithmetic: a disqualified trade or business silently killing QSBS,
brother-sister corporations that do not consolidate, uncompensated founder labor
producing no wage QREs, a 30-day §83(b) clock, §195 versus §162 at a
pre-operating entity, and the March 15 deadlines that have no late relief.

## Question format

Each item has `id`, `area`, `type` (`mcq` / `numeric` / `short`), `difficulty`
(`remember` / `application` / `analysis`), `q`, optional `choices`, `answer`,
optional `tolerance`, `cite`, and `why` — copy an existing item in
`benchmark/questions/` as the template. Grading: MCQ by exact letter, numeric
within tolerance, `short` flagged for manual grading. New files in
`benchmark/questions/` load automatically.

## Scoring standard

| Band | Reading |
|---|---|
| **90–100%** | Production-grade. Safe to rely on for preparation with review. |
| **75–89%** | Passing (CPA exam scaled mark is 75). Usable, but the weak areas named in the report get human review before filing. |
| **60–74%** | Not reliable. Fix the weak areas before the system touches a return. |
| **<60%** | Do not use for filing work. |

**A passing score is not a license to skip review.** Per the `cpa-standards`
skill, model output is never authority and never a reasonable-cause defense.

## Maintenance — this is the part that decays

The bank is pinned to **tax year 2026** and to the values in the project's
`constants` binding. It rots when the law changes.

Update triggers:
- **New tax year** — every numeric question needs its expected answer re-derived
  from the new year's constants. Do not simply bump the year in the prose.
- **`constants` binding changes** — re-verify every numeric item against the new table.
- **New legislation** — add questions for what changed, and re-check that existing
  items are still correct rather than merely still plausible.
- **A real-world miss** — any time the system gets something wrong on actual work,
  write it into the bank so it can never regress silently. This is the
  highest-value way the bank grows.

Questions whose answers depend on an item marked `VERIFY` in
`irc-lookup/reference/obbba-changes.md` inherit that uncertainty — confirm
against primary text before treating a miss there as a genuine competency gap.
(The §1202 tiering behind TCP-005 was confirmed against the Code on 2026-09-23.)

## Reference files

- `reference/blueprint-coverage.md` — read when adding questions or reporting
  coverage; blueprint mapped to the bank, with known gaps.
- `reference/scoring-rubric.md` — read when grading `short` items or running
  the pre-filing gate.

## Related skills

`cpa-standards` (the professional standards being measured), `irc-lookup`,
`return-review` (the operational counterpart — reviewing an actual return rather
than answering questions).
