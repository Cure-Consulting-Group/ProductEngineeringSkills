# Evals — skill-library effectiveness

> **Claude path moved (T60, 2026-09-23): use `claude plugin eval` over
> [`plugin-evals/`](../plugin-evals/).** This directory's `run-evals.py`
> harness is kept only for the non-Claude runtimes (`--mode model --backends
> codex,gemini`). The 20 golden tasks below were ported 1:1 into
> `plugin-evals/t01…t20` (same fixtures, score.sh logic as `regex` graders).

## Claude: `claude plugin eval` (plugin-evals/)

The manifest declares the suite (`"experimental": {"evals": "plugin-evals"}` in
`.claude-plugin/plugin.json`), so `--eval-dir plugin-evals` is optional.

```
plugin-evals/<case>/prompt.md        frontmatter (tags = skill names, limits, allowed_tools) + user-phrased prompt
plugin-evals/<case>/graders/*.md     result grader(s) (regex over the produced file / reply) + skill-fired
plugin-evals/<case>/case.yaml        only when the case has fixtures: context.scaffold_script: fixture.sh
plugin-evals/results/                run output (gitignored)
```

- **40 cases, 32 skills**: `t01…t20` ported golden tasks (tag `ported`) and
  `route-*` routing cases (tag `routing`) that never name the skill — they
  measure whether `description` alone routes (T53). `route-legal-doc-no-auto`
  and `route-proposal-no-auto` (tag `negative`) assert the
  `disable-model-invocation` skills are **never** auto-invoked (`min: 0, max: 0,
  arm: both`).
- **Every case** (except t16) has a `tool_used: Skill` grader (a with-only "plugin fired"
  indicator in two-arm runs; scored under `--ablation none`) and a
  deterministic result grader. No `llm` graders yet — nothing needed one.
- `t16-substitution-integrity` still guards the `\$N` escaping bug: its fixture
  skill must deliver `PRICE=$0.15 / SHELL=$1 / CAP=$2,000` verbatim.
  It is slash-invoked (no `Skill` call), so its process grader is a `Write` of
  `DELIVERED.txt`, and the no-plugin arm loads no skills — its `W/OUT` is 0 by
  construction; read `WITH` only.
- Fixtures are `fixture.sh` scaffolds → the run needs `--scaffold`. File-writing
  cases need `--allow-tools Write Edit`; `t20` also needs `"Bash(python3 *)"`
  for `wireframe.py`.

```bash
# Zero-cost structural check (CI): every case parses, has graders, tags are skills
python3 scripts/check-plugin-evals.py

# Quarterly full sweep: 40 cases × 3 runs × 2 arms (with / without plugin) = 240 agent runs
claude plugin eval . --trust-plugin --scaffold -j 4 \
  --allow-tools Write Edit "Bash(python3 *)" --threshold 0.67 --max-cost-usd 150

# One case, one arm, cheap iteration
claude plugin eval . --case route-stripe-subscriptions --runs 1 --ablation none --allow-tools Write Edit

# Ring 0 (scripts/release.sh does this): cases for skills changed since the last tag
claude plugin eval . --tag $(python3 scripts/check-plugin-evals.py --changed-tags "$(git describe --tags --abbrev=0)") \
  --runs 1 --ablation none --scaffold --allow-tools Write Edit --trust-plugin --threshold 0.5
```

Read `Δ` (WITH − W/OUT) as the skill's measured value; `Δ ≤ 0` with the
skill-fired indicator passing means the skill routes but doesn't help. A
failing skill-fired indicator is a routing (description) finding.

---

# Legacy: golden-task harness (T30) — non-Claude runtimes only

The audit (`scripts/audit-library.py`) measures **conformance**. This measures
**effectiveness**: does loading a skill actually change agent output for the
better? Every task here is traceable to a real ticket or real consuming-project
work — no synthetic puzzles.

## Layout

```
evals/
  tasks/<id>/task.json   — prompt, fixtures (inline), skills exercised, provenance
  tasks/<id>/score.sh    — deterministic gate: exit 0 pass / 1 fail
  index.json             — skill → tasks map (drives --changed / Ring 0)
  results/*.json         — dated sweep results (committed)
  RESULTS.md             — generated scoreboard (do not edit)
```

## Running

```bash
# Runtime-selection matrix: same tasks across the non-Claude CLIs, skills on
python3 scripts/run-evals.py --mode model --backends gemini,codex

# Superseded by plugin-evals/ (kept working, no longer used by release.sh):
#   --mode skill (claude on/off A-B), --changed <ref> (old Ring 0)

# Harness self-test without spending tokens
python3 scripts/run-evals.py --mode model --backends mock --reps 1
```

Runs execute in throwaway temp dirs; the "on" arm gets the task's skills
copied into `.claude/skills/`, the "off" arm runs bare with
`--setting-sources project` so user-level plugins can't contaminate it.

## Rules

- **Judges must be cross-family.** Deterministic gates are primary; if a rubric
  judge is used, it must be a different model family than the candidate.
- **Reps:** 3 for sweeps (single runs are noise), 1 for Ring 0.
- **Calibration:** the audit reads the latest skill-mode results — a skill with
  eval coverage and a measured delta ≤ 0 is score-capped at 8.0. Conformance
  alone cannot make an A.
- **Cadence:** the quarterly sweep and Ring 0 now run on `claude plugin eval`
  (above); this harness runs the Codex/agy matrix on the same quarterly cadence.
- **Adding tasks:** new golden tasks come from real failures — a wave ticket, a
  consulting engagement bug, a canary regression. Add them as a `plugin-evals/`
  case first (tags = skill names); mirror into `evals/tasks/` only if the
  Codex/agy matrix needs it.
