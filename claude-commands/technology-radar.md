# Technology Radar

**Outcome:** `docs/TECHNOLOGY_RADAR.md` (or a single entry/decision) where every placement rests on
what the dependency scan shows is actually in use, every Hold has a migration target with effort and
quarter, and product divergence is called out. Done when each entry has ring, quadrant, products,
rationale, and owner, and the Step 7 checks hold. Match length to the need; no filler sections or
restated summaries.

## Pre-Processing (Auto-Context)

Context (pre-filled in Claude Code; in other runtimes run these commands first):

- Prior radar: !`grep -m1 -i "last updated" docs/TECHNOLOGY_RADAR.md TECHNOLOGY_RADAR.md 2>/dev/null || echo "(no prior radar)"`
- Portfolio products: !`grep -m6 -E '^#{2,3} ' PORTFOLIO.md 2>/dev/null || echo "(no PORTFOLIO.md)"`

Read the prior radar in full before proposing ring movements.

## Step 1: Classify

| Type | Output |
|---|---|
| Full radar | Complete TECHNOLOGY_RADAR.md |
| Single assessment | One entry with ring, rationale, products, migration plan if Hold |
| Quarterly review | Ring-movement proposals with evidence, new entries, divergence report |
| Migration plan | Product-by-product plan with S/M/L/XL effort and target quarter |
| Tech-debt audit | Hold technologies still in production, prioritized |

## Step 2: Gather Context and Scan

Ask for scope (which products), team satisfaction and pain points, recent trials and their results,
and constraints (budget, staffing, deadlines). Then scan the repos in scope for what is really used:
manifests, lockfiles, version catalogs, CI workflows, IaC. Read `reference/templates.md` for the
per-platform file checklist when running the scan. Count usage per technology across products; for
Assess items, search the web for current releases, deprecations, and advisories (dated sources).

## Step 3: Rings (Cure criteria)

| Ring | Criteria | Action |
|---|---|---|
| Adopt | In 2+ products successfully; team can debug and tune it; no planned deprecation | Default for new work; in project templates |
| Trial | Exactly one product or a POC; a champion; written success criteria and a decision date | Only in the trial product; report quarterly |
| Assess | No production use; a named researcher; re-evaluated next quarter | Prototypes only |
| Hold | Superseded, EOL, security risk, or maintenance > value | No new use; migration plan required |

Common misplacements: Adopt with one product (that's Trial); Assess already in production (Trial or
Adopt); Hold without an exit; listing what the team *wants* rather than what is *running*.

Quadrants: Languages & Frameworks · Tools · Platforms (cloud, BaaS, payments, AI APIs, databases) ·
Techniques.

## Step 4: Entry Format

```markdown
### [Technology]
- **Ring / Quadrant:** Adopt | Trial | Assess | Hold — [quadrant]
- **Products using:** [what runs today, from the scan]
- **Since:** [YYYY-QN]
- **Rationale:** [2–3 specific sentences from real experience]
- **Trial:** success criteria + decision date · **Assess:** researcher + next review
- **Hold:** migrate to [target], effort per product S/M/L/XL, target quarter
- **Owner:** [person or team]
```

For AI providers and models, name exact model IDs in use and date the entry — model names from an
old radar go stale within a quarter.

## Step 5: Default Radar (first run for Cure)

Read `reference/details.md` when generating a first radar for Cure Consulting Group — it holds a
starting draft (Adopt: Kotlin/Compose, Swift/SwiftUI with MVVM, Next.js App Router, Tailwind v4,
Firebase, Stripe, Claude API, GitHub Actions, Playwright; Trial: TCA, Gemini, OpenAI, Turborepo;
Hold: LiveData, UIKit, Pages Router, Jest, Express, XML layouts). Confirm each entry against the scan
before keeping it.

## Step 6: Quarterly Review, Divergence, and Debt

- **Review (first week of each quarter):** diff the dependency scan against last quarter; flag new, removed, and major-bumped dependencies; check Assess items for releases and warning signs; run a short engineer survey (satisfaction 1–5, biggest friction). Propose each movement with evidence, affected products, and required action.
- **Divergence:** two products using different tools for the same job. Converge where it's accidental (Jest vs Vitest, Axios vs fetch, npm vs pnpm, mismatched Node majors); accept where it's platform-driven (Kotlin vs Swift, Espresso vs Playwright) or business-driven (Stripe Connect vs Billing). Read `reference/templates.md` for the check table and report format.
- **Debt priority:** P0 = security/EOL/compliance risk on revenue products (migrate now); P1 = deprecated, rising maintenance (this quarter); P2 = friction on revenue features (next quarter); P3 = cosmetic. Every P0/P1 migration gets an ADR (sdlc).

## Step 7: Write and Check

Applies when Step 1 produces a document. Write `docs/TECHNOLOGY_RADAR.md` using the skeleton in
`reference/templates.md` (summary by ring, movements, entries by ring and quadrant, divergence, debt,
review log), plus `docs/tech-migrations.md` when migrations are planned. Check: every entry has all
fields; every Hold has a migration target; every placement matches the Step 3 criteria and the scan.

## Recurring Mode

This is a recurring goal, not a one-shot (mechanism trade-offs: the `engagement-automation` skill).

- **Cadence:** quarterly
- **Unattended:** cloud routine — quarterly radar refresh: scan diff, ring-movement proposals, Hold items still in production. Recipes: docs/AUTOMATION.md in the plugin repo.
- **Budget:** ~150k tokens/run; cap at one run per quarterly period.
- **Guardrails:** writes only `docs/TECHNOLOGY_RADAR.md` and the divergence report, as a proposal (PR or issue) for the Engineering Lead to approve — ring changes are never applied unreviewed; no code or dependency changes; report on failure rather than retrying.
