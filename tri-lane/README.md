# cure-tri-lane

Opt-in multi-vendor orchestration for Cure Consulting Group engagements. A Claude Code session acts as architect; Codex (GPT-5.6 Luna/Sol) implements spec-determined work and audits correctness; Antigravity (Gemini 3.8 Flash) reviews systems, security rules, infra, and CI and verifies in a browser; a fresh-context Claude advisor gives the final verdict. Every lane runs in its own git worktree and returns a machine-checkable report.

This plugin is independent of `cure-product-engineering`. Installing it changes nothing for machines that do not have it; the library keeps working exactly as before.

## Install

```
claude plugin marketplace add Cure-Consulting-Group/ProductEngineeringSkills   # once per machine; already present if the library is installed
claude plugin install cure-tri-lane@cure
/reload-plugins
```

One install per machine (user scope) covers every project. A project can disable it in its own `.claude/settings.json` under `enabledPlugins`.

## Requirements

| Requirement | Why | Check |
|---|---|---|
| Claude Code ≥ 2.1.255 | Fable 5.1 sessions; plugin hooks | `claude --version` |
| `codex` CLI, logged in with a ChatGPT plan | Codex lanes draw on Codex Pro | `codex login status` |
| `agy` (Antigravity CLI), signed in with a Google AI plan | Antigravity lane draws on the Google pools | `agy -p "/usage" --output-format json` |
| `gtimeout` (coreutils) or `timeout` | Wall-clock caps on lanes | `brew install coreutils` |
| Git repo with an integration branch | Worktrees per lane | — |

No API keys are read or stored. The lanes shell out to the two CLIs, which carry their own logins. Run the preflight to confirm everything at once:

```
python3 "$(claude plugin path cure-tri-lane 2>/dev/null || echo ~/.claude/plugins/cache/cure/cure-tri-lane/*)/skills/tri-lane/scripts/lane-preflight.py" --dir "$PWD"
```

## What you get

- `/cure-tri-lane:tri-lane` — the routing doctrine: declare a route, write the six-part spec, dispatch, verify, advisor, merge.
- Agents `codex-implementer`, `codex-reviewer`, `antigravity-analyst`, `cure-advisor`.
- `scripts/lane-preflight.py` and `scripts/lane-report.py` (stdlib Python, `--help`, `--json`).
- A PreToolUse guard that refuses `codex exec` without an explicit sandbox, any bypass flag, and headless `agy` unless it carries both `--mode plan` and `--sandbox`.
- `lane-report.py` refuses to run VERIFY when a lane touched files outside its `FILES` scope or any executable config, and otherwise runs VERIFY inside `codex sandbox` (no network, writes confined to the worktree). Lane-written code never executes unsandboxed before the diff is read.
- `skills/tri-lane/lanes.md`: exact flags, model slugs, caps, failure signatures, and the head-to-head log that justifies each repin.
- Benchmark harness (`BENCHMARK.md`): `lane-log.py start|end|update|list` records one line per task with Claude, Codex, and Antigravity usage read from their logs plus quota-pool deltas; `usage-window.py` sums Claude and Codex usage between two timestamps for any arm, including the manual flow; `benchmark-report.py` compares arms and applies the pre-registered decision rule.

## The incident that shaped the rails

On 2 Sep 2026, during design testing, Antigravity in plan mode reverted an uncommitted working tree because the machine's `agy` settings auto-approve every tool. The tree was restored from a diff saved beforehand. Hence: no lane ever touches a live tree, sandbox flags are explicit and hook-enforced, and the diff is saved before any cross-vendor run.

## Hard tier (1.6.0)

Five more fixtures built to separate models after the smoke tier saturated: a three-defect needle in a forty-change refactor diff, a cross-module invariant, a concurrency race graded over ten consecutive runs, an under-specified spec that rewards stopping over guessing, and a 200-module whole-repo read. `lane-eval.py run --task all --tier hard --lane <slug> --repeat 5`. `results` now groups by tier and prints cost per point. The smoke fixtures are unchanged.

## Canary suite (1.5.0)

`evals/` holds six fixed tasks cut from the defect classes the lanes met in the field: a payments capture service with ten planted bugs (reviewer recall and precision by line), a refund policy from a six-part spec (hidden tests), a cross-tenant authorization hole (hidden tests), a genuinely intermittent test (20-run flake check plus a named cause), a 30-module print-to-logger migration (grep and tests), and a status-badge component (hidden Node tests). Zero dependencies, hidden deterministic graders, a reference solution per fixture that CI runs to 100%. `lane-eval.py run --task all --lane gpt-6-astra --effort high` runs a model through the suite with the production wrappers; `results` prints the task × lane matrix; the dashboard shows it; `lane-route.py` treats a lane with canary runs as a posterior. See `evals/README.md`.

## Benchmark dashboard (1.4.0)

`benchmark-dashboard.py --all-projects --out dashboard.html` renders the log as one self-contained page: the decision rule with each check passing or blocking, the arms compared measure by measure, Claude tokens per task in run order, confirmed findings by reviewer, reviewer precision, shadow-router agreement, quota pool movement, and a sortable task table. Inline SVG with tooltips and table views, light and dark, no libraries. Regenerate it after every task; publish it as an artifact when you want to share it.

## Self-test, tests, and the capability table (1.3.0)

- `lane-preflight.py --doctor` on a new machine: tool versions, both logins, trusted paths, disk, toolchain caches, quotas, and `lane-selftest.py`, which builds a scratch repo and exercises every rail (hook matrix, refusal on empty diff, scope block, sandbox denial of home and `/tmp`, worktree lock and salvage) in under a minute.
- `tests/test_scripts.py`: stdlib unit tests for every script, run by the library's CI on each PR.
- `models.json` + `lane-route.py suggest`: a dated capability table (public benchmarks as the prior, the project's own log as the posterior) that suggests a lane and effort per task. Shadow mode: the suggestion is logged next to the architect's choice; it never decides.
- `lane-log.py due`: seven-day defect windows that need a check. `start` now records the session model and effort; `end` auto-discovers run-dir files.
- Gradle inside the sandbox runs `--no-daemon --offline`.

## Worktrees and toolchain caches

Create and remove lane worktrees only through `lane-worktree.py`. It writes a lock while a lane runs, refuses to remove a worktree while the lane process is alive, and pushes unmerged commits to `lane/<task>-salvage` before removing. A live Sol lane was orphaned twice in one HoopTrace session by manual cleanup.

The Codex sandbox confines writes to the worktree, so builds cannot take their cache locks (`~/.gradle`, `~/.npm`, `~/.cargo`, …) and a lane can never verify what it wrote. `lane_toolchains.py` detects the repo's toolchains; preflight lists the caches; the implementer passes them as `--add-dir`; the sandboxed VERIFY adds them automatically. Paths are resolved to their physical form because the sandbox rejects symlinked roots. The sandbox has no network, so warm a cold cache on main before the first dispatch.

## Nothing under /tmp

Every lane writes only inside the repo: `$(git rev-parse --git-common-dir)/tri-lane/run/<task>/` holds the spec, events, final message, and a `tmp/` that `TMPDIR` is exported to. The Codex sandbox runs with `/tmp` excluded. A full system volume stalled every lane on 3 Sep 2026; preflight now refuses to dispatch on low disk. Claude Code's own scratchpad and Bash output still live under `/private/tmp`, which the plugin cannot move, so keep the system volume above a few GB.

## Model pins and re-testing

Lane models are named in one place, `skills/tri-lane/lanes.md`. When a model generation changes, re-run the head-to-head on a real diff, log the result there, and repin. Do not pin models in agent frontmatter for lanes; the wrapper agents are Sonnet because they only run commands.

## Not included, on purpose

- OpenAI's `codex-plugin-cc`. Fine to install for manual `/codex:adversarial-review`; do not enable its Stop review gate. The automated lanes here call `codex exec` directly for deterministic, capped, inspectable runs.
- Gemini CLI. Dead for consumer Google plans since 18 June 2026; `agy` is the Google lane.
- Any Stop-hook or timed review loop. One advisor review per deliverable; audit reviews only on the trigger.
