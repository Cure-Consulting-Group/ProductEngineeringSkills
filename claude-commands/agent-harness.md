# Agent Harness

An agent is the model plus its harness: the docs it reads, the checks that run on its work, and
the permissions around it. This skill installs the six-part kit Cure piloted in
cure-finops-watchdog (ADR-0012) and proved on DistrictZero and statledger. It is done when the
repo has every item below, each acceptance check has passed, and the work is on a PR with the
evidence in its body. It never pushes to the default branch and never merges.

## Step 1: Classify

| Repo state | Do |
|---|---|
| No `CLAUDE.md`/`AGENTS.md` | Write `AGENTS.md` from `templates/AGENTS.md`; `CLAUDE.md` is `@AGENTS.md` |
| `CLAUDE.md` exists, **not** cited by code | `git mv CLAUDE.md AGENTS.md`, then a new `CLAUDE.md` = `@AGENTS.md` plus Claude-only notes |
| `CLAUDE.md` cited by code or tests (`grep -rn "CLAUDE.md §"`) | Keep it in place. Add `AGENTS.md` as the map, start `CLAUDE.md` with `@AGENTS.md`, and point Codex at the cited sections |
| `claude.manifest.json` present | Stop. Managed fences belong to `cure-infra-bootstrap`; add the kit outside them only |

## Step 2: Gather context (before writing anything)

- `git fetch` and work in a worktree off `origin/<default>`. Local clones run hundreds of commits
  stale; every claim in the PR must hold at origin.
- **Measure every suite** the gate could run: typecheck, lint, unit tests per package. Write the
  seconds down. This decides the gate's shape (Step 3, K2).
- Find the **production entry points**: deploy scripts, `firebase deploy`, `terraform apply`,
  release workflows, **tag triggers** (`on: push: tags`), store upload/promote CLIs.
- Find rules already **enforced**: rules tests, lint scripts, workflow tests, parity tests. The
  Controls table cites them; don't duplicate them.
- Check for a **vendored library**: tracked `.claude/agents`, `.claude/commands`,
  `.claude/output-styles`, `.claude/personas`, an inert `.claude/hooks/hooks.json`, and an
  `@cure-consulting-group/product-engineering-skills` dependency whose postinstall re-vendors it.
- Size the state file (`wc -lc STATE.md` or `.agents/STATE.md`). Every session reads it first.
- See which CI jobs run on **every** PR. Contract tests belong in one of them; a job that runs only
  in the merge queue never shows them on the PR.

## Step 3: Install the kit

| # | Item | Template | Acceptance |
|---|---|---|---|
| K1 | `AGENTS.md` map, ≤150 lines: commands, layout, knowledge pointers, Controls table, incident-born gotchas, working rules | `templates/AGENTS.md` | Line count ≤150; the K4 doc-paths test passes |
| K2 | One gate, `scripts/verify.sh`, under 60s, silent with `--quiet` on green | `templates/verify.sh` | Timed run under 60s with every tree touched |
| K3 | `.claude/settings.json`: Stop hook running K2; `ask` for deploys, applies, release tags; `deny` for irreversible deletes | `templates/settings.json`, `templates/verify-on-stop.sh` | Probe: failing test gives exit 2 with the failure; `stop_hook_active` gives 0; green gives 0; a repeat stop is skipped |
| K4 | Contract tests for the repo's top prose rules (≥3, always including doc paths), each failure message stating the fix | `templates/harness-contracts.test.ts` (vitest), `templates/test_harness_contracts.py` (pytest) | Each test fails under a mutation that breaks its rule; record the table in the PR |
| K5 | Hygiene: de-vendor the library, ignore lane worktrees, archive old state-file entries | none | `git ls-files .claude` shows project files only; state file is newest-first with history in an archive |
| K6 | Measure: harness-shaped error rate 14 days before and after merge | `v_agent_harness_daily` (watchdog) | Before/after numbers in a PR comment |

### K1: the map

- One row per command an agent needs, exactly as it runs (copy from CI, not memory).
- The **Controls** table is the core. Every rule that matters gets a row naming what enforces it:
  a test path, a lint script, a hook, `.claude/settings.json`. Unenforced rules say `prose`;
  readers treat those as the rules most likely to be broken.
- Gotchas are things that each cost a real incident, one or two lines, with the fix.
- Keep the working rules in the template: fetch before judging state, one plain command per Bash
  call in an isolated worktree, Monitor instead of `sleep`, branch and PR.

### K2: the gate

- If every suite finishes in under ~45s together, run whole suites for each touched tree. Mapping
  changed files to tests is only worth it when a suite alone blows the budget.
- When you must map, map a changed `foo.ts` to its sibling `foo.test.ts`. `vitest related` breaks
  on module graphs that import non-JS assets.
- Reuse CI's own path filters for "touched", so local and CI agree on what a change affects.
- Native builds (Xcode, Gradle) take minutes. Leave them in CI or a pre-push hook and list their
  commands in K1.
- Installs: check each lockfile against `node_modules/.package-lock.json` and run `npm ci` only
  when stale.

### K3: permissions and the hook

- `ask`, not `allow`, for anything that reaches production. Tag pushes count when a workflow
  triggers on tags.
- `deny` for irreversible deletes: projects, databases, secrets, `bq rm`.
- If `.gitignore` whitelists `.claude/`, name `.claude/hooks/verify-on-stop.sh` and
  `.claude/settings.json` exactly. Installs drop vendored hook files that must stay out.
- Ignore `.claude/.verify-stamp`.

### K4: contracts

- Always include the doc-paths test. It skips globs, placeholders, build output and gitignored
  paths (`git check-ignore --no-index`), because docs name machine-local paths on purpose.
- Good contracts are cheap and repo-specific: no `schedule:`/cron (org policy 2026-08-08), deploy
  scripts call the project guard first, named database never `(default)`, backfills ship with
  tests, state-file line cap, no root-level reports, library not vendored.
- Never read a path that a CI-skipping class of PR can change (e.g. a notes tree that skips CI).
- Mutation-check each one: break the rule, see the test fail, restore. Script it so the tree is
  restored even when a step fails.

### K5: hygiene

- De-vendoring has two halves: delete the tracked files **and** remove the npm dependency, or the
  next `npm ci` puts them back.
- Archive state-file entries verbatim to a dated file (`docs/state-archive/STATE-through-<month>.md`),
  and leave a pointer line at the top of the live file. Don't rewrite the current handoff; that
  belongs to the owner.

## Step 4: Verify

Run the gate on the finished branch, time it, probe the hook (K3), and run the mutation script
(K4). All four results go in the PR body. CI must be green on the PR before you report done.

## Step 5: Open the PR and report

- Title `chore(harness): … (H-<ticket>)`. In the body, give a section per kit item, the hook
  probe table, the mutation table, and the measured timings.
- Under "For the reviewer", list what the owner must decide: line counts over target, contracts
  that will trip on purpose, conflicts with open branches (a `CLAUDE.md` → `AGENTS.md` rename
  conflicts with every branch that edits `CLAUDE.md`), and dead CI steps left for a follow-up.
- Report the PR link, CI state, and anything left for the owner. Merging is the owner's call.

## Rules

- Write only what was verified at origin; a wrong line in `AGENTS.md` is acted on as fact.
- No production allows in committed settings, ever. If one exists, move it to `ask` and say why.
- The Stop hook blocks at most once per turn (`stop_hook_active`) and never loops.
- Don't add a `schedule:` trigger to run any of this.

## Related Skills

- `project-bootstrap`: writes the first `CLAUDE.md`/`STATE.md` by interview; run this skill after it.
- `cure-infra-bootstrap`: manifest-managed files; the kit goes outside its fences.
- `ci-cd-pipeline`, `testing-strategy`: when CI itself lacks the suites the gate should mirror.
- `parallel-agent-orchestration`: shell discipline for agents in isolated worktrees.
