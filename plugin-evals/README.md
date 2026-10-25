# plugin-evals — the `claude plugin eval` suite

The manifest declares this directory (`"experimental": {"evals": "plugin-evals"}` in
`.claude-plugin/plugin.json`), so `claude plugin eval .` finds it without `--eval-dir`.
`evals/` holds the legacy harness for the Codex/agy matrix (see `evals/README.md`).

**61 cases, 47 skills** (count with `python3 scripts/check-plugin-evals.py`).

## Before you run anything

- **Claude Code 2.1.269 or later** (`claude --version`).
- **git 2.31 or later, if git is installed** (`git --version`). With an older git,
  `claude plugin eval` stops before the first case and exits 1. It needs `GIT_CONFIG_COUNT`
  (git 2.31) to switch off repo hooks and credential helpers during runs. 2.1.283+ enforces
  this; older builds ran unprotected. `plugin-evals/sweep.py` checks it too.
- **Every run is a real model call billed to the account**, and so is every `llm` grader
  (none ship yet). A case is `runs` (default 3) × 2 arms: WITH the plugin, and W/OUT it as the
  baseline. Always set **`--max-cost-usd`**. The ceiling is checked before each run starts, so
  overspend is bounded by the runs already in flight (`-j`). When it's hit, the command exits
  **2** with `partial: true`. Keep partial results out of trends.
- **`--trust-plugin`** is required whenever the run can't prompt: CI, a non-TTY shell, or
  `--json`. Without it the run is refused with exit 1. It doesn't imply `--scaffold`,
  `--allow-tools`, or `--mocks off`.
- **`--scaffold`** runs each case's `fixture.sh` as you, with a minimal env and a 120 s cap.
  Only use it on this suite.
- **Tool grants:** runs get only the read-only tools in `allowed_tools`. File-writing cases need
  `--allow-tools Write Edit`; t20 needs `"Bash(python3 *)"`. Any Bash grant runs under the OS
  sandbox. Neither `allowed_tools` nor a skill's `allowed-tools` can widen a grant.
- Exit codes: 0 pass · 1 below `--threshold` (default **1.0**), load error, untrusted, or bad
  option · 2 partial (cost ceiling or auth) · 130/143 interrupted. Δ never changes the exit code.

## Layout

```
plugin-evals/<case>/prompt.md      frontmatter (tags = skill names, limits, allowed_tools) + user-phrased prompt
plugin-evals/<case>/graders/*.md   result grader(s) + a tool_used: Skill "skill-fired" indicator
plugin-evals/<case>/case.yaml      only when the case has fixtures: context.scaffold_script: fixture.sh
plugin-evals/sweep.py, SWEEP.md    the n≥3 with/without Δ sweep (T85)
plugin-evals/results/              run output (gitignored)
```

## Case families

| Family | Cases | What it measures |
|---|---|---|
| Ported golden tasks (tag `ported`) | `t01…t20` (t16 stays in `evals/tasks/`) | Generic correctness. The T60 pilot found Δ≈0 here under Opus 5.5 |
| Routing (tag `routing`) | `route-*` | Whether `description` alone routes. Prompts never name the skill. `not-<skill>.md` graders (`min: 0, max: 0`) assert the neighbouring skill did **not** fire (the T81 single-owner boundaries) |
| Negative (tag `negative`) | `route-legal-doc-no-auto`, `route-proposal-no-auto` | `disable-model-invocation` skills never auto-fire (`arm: both`) |
| T85 risk cases | `security-review-nextjs-firebase`, `compliance-architect-kids-health`, `qsbs-compliance-two-regimes`, `data-migration-firestore-backfill`, `return-review-schedule-c`, `public-sector-city-contract`, `engagement-automation-cross-runtime`, `cure-infra-bootstrap-pci`, `nextjs-scaffold-notes-feature` | **Cure-specific** value the bare model doesn't reliably produce: current facts (OWASP 2025, OBBBA §1202/§174A, COPPA 2025, Next 16/Zod 4), Cure positions, Cure tooling. All graders are deterministic (`regex`/`file_exists`). No `llm` graders |

Every case has a `tool_used: Skill` grader. In a two-arm run it is an unscored "plugin fired"
indicator; it is scored under `--ablation none`.

Two T85 cases depend on work in flight:
- `engagement-automation-cross-runtime` is **expected to fail the with-arm until T79** fixes
  engagement-automation:16 (Antigravity `/schedule` + sidecar Automations, Codex Automations).
- The T81 routing cases (`route-security-review-prelaunch`, `route-design-studio-redesign`,
  `route-firebase-architect-firestore-model`, `route-database-architect-postgres-index`,
  `route-finops-live-bill`, `route-performance-review-cwv`, `route-product-manager-prioritize`,
  `route-project-manager-sprint`, `route-legal-doctrine-bar-question`) are its acceptance test.
  Run them on the branch where T81's rewritten descriptions have landed.

## Commands

```bash
# Zero-cost structural check (CI): every case parses, has graders, tags are skills
python3 scripts/check-plugin-evals.py

# One case, one arm, cheap iteration (add --keep-temp to read what Claude produced)
claude plugin eval . --case route-finops-live-bill --runs 1 --ablation none \
  --trust-plugin --no-publish --max-cost-usd 2

# Ring 0 (scripts/release.sh does this): cases for skills changed since the last tag
claude plugin eval . --tag $(python3 scripts/check-plugin-evals.py --changed-tags "$(git describe --tags --abbrev=0)") \
  --runs 1 --ablation none --scaffold --allow-tools Write Edit --trust-plugin --threshold 0.5

# T85 Δ sweep: top 20 skills by traffic, n=3 per arm, one total cost cap (see SWEEP.md)
python3 plugin-evals/sweep.py --dry-run              # selection + estimate, spends nothing
python3 plugin-evals/sweep.py --max-cost-usd 150     # runs it, writes evals/RESULTS.md

# Full suite: 61 cases × 3 runs × 2 arms = 366 agent runs
claude plugin eval . --trust-plugin --scaffold -j 4 --no-publish \
  --allow-tools Write Edit "Bash(python3 *)" --threshold 0.67 --max-cost-usd 200
```

Put the target (`.`) before `--tag`, `--allow-tools` and `--json`: those flags take lists or an
optional path and will swallow a target that follows them.

Read `Δ` (WITH − W/OUT) as the skill's measured value. If skill-fired passes and Δ ≤ 0, the
skill routes but doesn't help. If skill-fired fails, the description has a routing problem.

## Writing a case

Start from a real failure: a wave ticket, an engagement bug, a canary regression. Write the
prompt the way a user would, without naming the skill. Grade what only the skill would know:
a Cure position, a post-cutoff fact, a Cure tool or path. Generic correctness the bare model
already has measures nothing (T60). Use a `regex` over the reply or a produced file, plus the
skill-fired indicator. Use an `llm` grader only for short output with concrete PASS/FAIL
conditions. Tags must be real skill names, or one of `routing`, `negative`, `ported`,
`substitution`, `pilot`. The validator enforces this, and Ring 0 selects cases by tag.
