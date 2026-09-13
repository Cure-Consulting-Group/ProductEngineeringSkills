# Tri-Lane manual arm, week of 14 September 2026 (T49 part 2)

**Why:** the pre-registered rule in `tri-lane/BENCHMARK.md` compares tri-lane to a `manual` arm. None exists, because the fleet adopted the doctrine outright. The cost proxy (`TRI-LANE-COST-PROXY-2026-09-13.md`) flips sign with the commit denominator; only this arm returns a verdict.

**Where:** statledger, the highest-volume repository (18 of the 56 delegate tasks in the first ten days).

**Mix:** eight tasks, matched to statledger's own delegate mix over the ten days (impl 8, infra 4, security 3, debug 2, tests 1, inferred from objectives and FILES):

| Kind | Tasks | Examples of the shape |
|---|---:|---|
| `impl` | 4 | A bounded feature or UI wiring with a deterministic VERIFY |
| `infra` | 2 | CI, release gate, build, or tooling change |
| `security` | 1 | Firestore rules, auth, or privacy path |
| `debug` | 1 | A reproducible bug with a failing test to turn green |

**Before the first task (readiness):**
1. Merge PR #58 and update the plugin where it is installed: `claude plugin update cure-tri-lane@cure` at user scope and in each project that pins it (initiated-recruiting and this repo pin 1.9.2 at project scope). Until then the projects run 1.9.2, which logs nothing.
2. Confirm the session model and effort you will freeze: `python3 $S/lane-log.py start --task probe --arm manual && python3 $S/lane-log.py end --task probe --route manual --status refused --notes probe` prints them (today: `claude-fable-5-1[1m]` at `xhigh`, from `modelSettings` in `settings.json`). Both arms must record the same pair for the week; `/model` changes break the freeze.
3. The tri-lane side of the rule counts only lifecycle-logged rows (the backfill has no effort recorded, so it cannot satisfy the fixed-model gate; `--include-backfill` overrides, dishonestly). Eight tri-lane tasks must also land in the same week under the same model, in statledger or elsewhere. At the ten-day pace (57 Codex tasks) that is not the constraint.

**Frozen for the week:** session model and effort as they are today (`~/.claude/settings.json`; the record captures them, and `benchmark-report.py` refuses a verdict if they vary between arms). No Codex or Antigravity lanes on these eight; Codex used by hand in another terminal is allowed and is picked up from the account logs (`codex_account`), which is the one place that figure is legitimate.

**Per task, typed (the manual arm has no worktree lifecycle):**

```bash
S="$HOME/.claude/plugins/cache/cure/cure-tri-lane/1.14.0/skills/tri-lane/scripts"   # or $CLAUDE_PLUGIN_ROOT/skills/tri-lane/scripts
python3 $S/lane-log.py start --task m-01 --arm manual --kind impl          # before the first prompt
# ... do the task the old way ...
python3 $S/lane-log.py end   --task m-01 --route manual --status complete  # when merged or abandoned
```

Within seven days of each `end`, when a defect from that task surfaces (or does not):

```bash
python3 $S/lane-log.py update --task m-01 --escaped-defects 0
```

The SessionStart hook prints any window that is due.

**Reading the result:** `python3 $S/benchmark-report.py --all-projects` returns "keep measuring" until eight tasks exist in both arms with closed windows and one frozen model, then `adopt tri-lane` or `do not adopt as-is`. The tri-lane side already has 56 delegate rows from the backfill; only the 27 with non-overlapping Claude windows count toward its median, and new lifecycle-logged tasks add to it every day. `benchmark-dashboard.py --all-projects` shows the three checks.

**Do not:** log a manual task after the fact from memory; change model or effort mid-week; put all eight in one day; skip the defect check.

**Status:** go given 2026-09-13. Start: Monday 14 September. Read: on or after Monday 28 September, when the last seven-day window closes.
