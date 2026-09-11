# Tax domain

Twelve skills for doing real tax work — preparation, planning, review, and the
professional standards that govern all of it — grounded in the Internal Revenue
Code and pinned to **tax year 2026**.

## Disclaimer
This skill produces draft analysis and workpapers, not tax, legal, or accounting advice. Nothing it produces is filing-ready until a licensed CPA, enrolled agent, or tax attorney has reviewed it. Model output is not authority and does not establish reasonable cause (see `cpa-standards`).

These skills carry doctrine, not clients. Everything taxpayer-specific lives in
the consuming project's `.claude/tax-profile.md` — see `TAX-PROFILE-TEMPLATE.md`
in this directory. Skills refer to a project's tax tooling by **binding name**
(`constants`, `calculator`, `validator`, …) so they work unchanged in a project
that has no tax engine at all.

## The skills

| Skill | Use it when |
|---|---|
| **irc-lookup** | A position needs a statutory basis. Authority hierarchy, citation format, and the OBBBA change log. Foundation for everything else. |
| **deductions-and-credits** | "What can I deduct / what credits apply." The benefit catalog with tests, limits, and substantiation. |
| **tax-strategies** | "How do I pay less." Planning moves, screened through the anti-abuse doctrines. Includes the method for building a per-entity playbook. |
| **software-dev-tax** | §174A and §41 treatment of platform development — QREs, the internal-use software rules, the pre-release boundary, per-repo allocation. |
| **tax-preparation** | Building an actual return and the accountant handoff package. |
| **return-review** | A return is computed and needs checking before it goes out. Mandatory pass. |
| **audit-risk-substantiation** | How risky is this, what defends it, and what happens if it loses. |
| **tax-recommendations** | Turning analysis into a ranked, dated, quantified action list. |
| **estimated-tax-compliance** | Quarterly payments, safe harbors, withholding, and the recurring calendar. |
| **nonprofit-dissolution** | Winding down a New York not-for-profit and closing out its exempt-organization filings. |
| **cpa-standards** | Professional standards — Circular 230, SSTS, §7216, workpapers. Applies to every work product. |
| **cpa-benchmark** | Measuring whether any of this is actually right. Runnable scored question bank. |

## How they fit together

```
irc-lookup ──────────── authority for everything below
     │
     ├── deductions-and-credits ─┐
     ├── tax-strategies ─────────┤
     │        │                  ├──→ tax-recommendations ──→ deliverable
     │        └── entity-playbook┘
     ├── software-dev-tax ───────┘   (R&E and the research credit)
     │
     ├── tax-preparation ──→ return-review ──→ accountant handoff
     │        └── estimated-tax-compliance (runs all year)
     │
     ├── nonprofit-dissolution ── the exempt-org wind-down track
     │
     └── audit-risk-substantiation ── risk rating on every position

cpa-standards  ── governs how all of the above is performed and documented
cpa-benchmark  ── measures whether it is correct
```

## Conventions used throughout

**Verification status** on every factual claim:

| Flag | Meaning |
|---|---|
| `VERIFIED` / `ENGINE` | Read against primary text, or against a reconciled `constants` binding |
| `CATALOG` | From a curated section catalog; summary only |
| `RECALL` / `VERIFY` | Model knowledge or an unconfirmed provision — **not filing-ready** |

Nothing reaches a return on `RECALL`. Recalled section *numbers* are a search
index; recalled *amounts* are a hypothesis to verify.

**Risk ratings**: Conservative / Moderate / Aggressive, always with the reason
named.

**Citation format**: `IRC §199A(b)(2)(B)` in prose, `26 USC S 199A` in code
comments and datastore keys.

## Start here

```bash
cd skills/tax/cpa-benchmark/benchmark
node run.mjs stats     # what the bank covers
node run.mjs sources   # bundled sets plus any project overlay
```

The benchmark ships **52 portable questions** across `reg-core`, `tcp-planning`,
and `software-and-exempt`, graded against the CPA exam's scaled pass mark of 75.
A project adds its own applied questions — built on its real entities and
figures — in `.claude/tax-benchmark/questions/`, which is auto-discovered and
merged. Those stay in the project; they never come back here.

## Known limitations

- **OBBBA items marked `VERIFY`** — notably the §1202 tiering, §168(n), §461(l)
  thresholds, and the 1099 threshold change — need confirmation against primary
  text before filing use. See `irc-lookup/reference/obbba-changes.md`.
- **State coverage is thin.** New York and Delaware appear as worked examples of
  patterns every state has; no state's rules are modelled comprehensively.
- **Benchmark coverage gaps** are listed honestly in
  `cpa-benchmark/reference/blueprint-coverage.md` — estate and gift, trusts,
  international, payroll mechanics, and partnership depth are the significant
  ones.
- **Nothing here is a substitute for a preparer who signs.** `cpa-standards` is
  explicit that model output is never authority and never a reasonable-cause
  defense.

## Maintenance

Re-run the benchmark and re-verify numeric content on: any change to the
project's `constants` binding, a new tax year, new legislation, and before each
filing season. A skill that quietly carries last year's threshold is worse than
one that says it does not know.
