# Evals — golden-task harness for the skill library (T30)

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
# Skill effectiveness: on/off A-B per task on the claude CLI (3 reps)
python3 scripts/run-evals.py --mode skill

# Runtime-selection matrix: same tasks across CLIs, skills on
python3 scripts/run-evals.py --mode model --backends claude,gemini,codex

# Ring 0 (CI): only the tasks covering skills changed vs main, 1 rep,
# fails on regression vs the previous committed results
python3 scripts/run-evals.py --changed origin/main

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
- **Cadence:** full skill-mode sweep quarterly (see docs/MAINTENANCE.md);
  Ring 0 on every PR touching a covered skill.
- **Adding tasks:** new golden tasks come from real failures — a wave ticket, a
  consulting engagement bug, a canary regression. Add the dir, update
  `index.json` (or re-run the generator), keep `score.sh` deterministic.
