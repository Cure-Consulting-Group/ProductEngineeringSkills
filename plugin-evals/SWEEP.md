# T85 Δ sweep — with vs without the plugin, n≥3, top 20 skills by traffic

**Acceptance (BACKLOG T85):** RESULTS.md carries an n≥3 Δ for every covered skill, and the
skills with Δ≈0 are listed for T88. `plugin-evals/sweep.py` produces both.

## Run it

```bash
python3 scripts/check-plugin-evals.py                 # free; must be green
python3 plugin-evals/sweep.py --dry-run               # free; prints the selection, the estimate, the exact command
python3 plugin-evals/sweep.py --max-cost-usd 150 --model claude-opus-5-5
```

The script then:
1. Picks the skills (next section).
2. Runs `claude plugin eval <repo> --runs 3 --ablation with-without --trust-plugin --scaffold
   --no-publish --threshold 0 -j 4 --max-cost-usd <cap> --allow-tools Write Edit "Bash(python3 *)"
   "Bash(ls *)" "Bash(grep *)" --tag <skills…>`. The cap covers the **whole sweep**, not each
   case. `--threshold 0` is set because the sweep measures Δ; gating is Ring 0's job.
3. Converts `aggregate-result.json` into `evals/results/<stamp>-skill.json`. This uses
   run-evals.py's format (`<case>|claude|on|off`, `pass_rate`, `n`, `ci95`, `flaky`) plus
   `skill_deltas`, `selection`, `costUsd` and `partial`.
4. Regenerates `evals/RESULTS.md`: the existing table, a per-skill Δ table, the **Δ≈0
   (|Δ| < 5%) list for T88**, and the Δ<0 list.

Exit codes:
- **0:** done.
- **2:** partial. The cost cap was hit or auth failed. The partial results are still written
  and flagged.

To re-render from a finished run without spending anything:
`--from-result plugin-evals/results/sweep-<stamp>/aggregate-result.json`.

Other flags:
- `--skills a,b,c` overrides the ranking.
- `--runs` below 3 is refused unless you pass `--allow-low-n`.

**Pin `--model`.** Otherwise a model rollout shows up as a plugin Δ.

## How "top 20 by traffic" is derived

For each skill, traffic is the **max** of two sources over the last 90 days (`--days`):
- **T35 telemetry:** `~/.cure/telemetry/skill-usage.jsonl`, written by `hooks/cure_guard.py
  telemetry`.
- **Local Claude Code transcripts:** `Skill` tool calls in `~/.claude/projects/**/*.jsonl`.

It's the max, not the sum, because the hook and the transcript record the same invocation.
Names are normalised from the `cure-product-engineering:` prefix. Non-library skills such as
artifact-design and tri-lane are dropped.

**Today the traffic signal is thin, and the selection says so.** On 2026-10-24 this machine had
77 telemetry rows and the transcripts showed Skill calls for only five library skills:
design-studio 14, sdlc 2, product-manager 2, web-design-expert 1, ios-architect 1. Traffic can
therefore rank only the first three slots. The other two have no case yet, and the sweep reports
them so cases can be written. The rest of the order falls back to:

1. the **T85 risk list**, in ticket order: security-review, compliance-architect,
   qsbs-compliance, data-migration, return-review/tax-preparation, public-sector-contracting,
   engagement-automation, cure-infra-bootstrap, nextjs-feature-scaffold, then the T81 routing
   skills: firebase-architect, database-architect, finops, performance-review,
   product-manager, project-manager, legal-doctrine, legal-research, design-studio;
2. then the number of cases, then the name.

Only skills with a case can be swept. Ring 0 tags (`check-plugin-evals.py`) define coverage.

The `--dry-run` selection on 2026-10-24 was 20 skills over 34 cases:
- **By traffic:** design-studio, product-manager, sdlc.
- **From the T85 risk list:** security-review, compliance-architect, qsbs-compliance,
  data-migration, return-review, public-sector-contracting, engagement-automation,
  cure-infra-bootstrap, nextjs-feature-scaffold, firebase-architect, database-architect, finops,
  performance-review, project-manager, legal-doctrine, legal-research.
- **By case count:** incident-response.

The run is 34 × 3 × 2 = **204 agent runs**. That's about **\$92** at \$0.45/run, against a
\$150 cap.

Rerun `--dry-run` on the final branch; the list changes as telemetry accrues. When the fleet
shares telemetry, point `--telemetry` at the merged file.

## Cost evidence

Smoke, 2026-10-24, claude 2.1.306: `public-sector-city-contract`, 1 run × 2 arms, \$0.33 total.
- W/OUT: \$0.10, 2 turns.
- WITH: \$0.23, 3 turns.

Scaffolded write cases (nextjs, data-migration) and the ported design-studio tasks run longer;
\$0.45/run is the planning figure. Check the first sweep's `costUsd`, then set `--est-run-usd`
to match.

## Reading the result

| Signal | Meaning | Action |
|---|---|---|
| Δ > 0, skill-fired ✓ | The skill adds measured value | Keep |
| Δ≈0, skill-fired ✓ | It routes but adds nothing over the bare model | T88: rework the content or prune |
| Δ≈0, skill-fired ✗ | It never fired, so Δ says nothing about the content | T81: fix the description first |
| Δ < 0 | The plugin made the answer worse | Read the report (`--keep-temp` on a 1-run rerun of that case) |
| WITH low on both arms | The grader may be miscalibrated | Rerun that case with `--runs 1 --ablation none --keep-temp`, read the reply, then fix the grader |

Sequence it on the final Wave 7 branch, after T79, T80 and T81. Before that:
- engagement-automation's with-arm is expected to fail (the skill still says Codex and agy
  can't schedule).
- The routing cases test the old descriptions.

After a complete run, commit `evals/results/<stamp>-skill.json` and `evals/RESULTS.md`.

**Calibration note.** `scripts/audit-library.py` caps any skill whose measured Δ ≤ 0 at 8.0. It
reads the newest `evals/results/*-skill.json`, but maps skills to tasks through
`evals/index.json`. So only the ported `t01…t20` cases calibrate until the audit also reads
this file's `skill_deltas`.
