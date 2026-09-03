# Benchmarking Tri-Lane against the plain library

The question: does Claude architect + Codex + Antigravity lanes beat Claude Code with the Cure library alone, per task, on cost and quality together. The measured risk from the wider community is a flow that wins on quality while spending several times the tokens; so every task records both, and the decision rule is written down before the first task.

## Arms

| Arm | What runs | Logged as |
|---|---|---|
| `manual` | Today's flow: Claude Code with the library; Codex and Antigravity used by hand in other terminals, or not at all | `--arm manual` |
| `tri-lane` | `/cure-tri-lane:tri-lane` doctrine: declared route, lanes in worktrees, advisor once | `--arm tri-lane` |
| `advisor-only` | Tri-lane with no Codex or Antigravity review, only the fresh-context advisor. Isolates cross-vendor review value | `--arm advisor-only` |

## Design

- Two weeks in one repo (Vendly), same person, same session model (`/model` fixed and noted), same effort setting.
- Week 1: `manual`. Week 2: `tri-lane`, with 3 of the tasks run as `advisor-only`.
- Tasks in matched pairs by `--kind`: at least 3 `impl` (spec-determined), 3 `security` or `infra`, 2 `debug`. Aim for 10 per arm; medians are not trustworthy below 8.
- Do not put all the risky work in one week. If the mixes differ, the comparison is void.
- Fix the Claude model for both weeks. Fable versus Opus changes token draw more than the flow does.

## Per task

```bash
S="$HOME/.claude/plugins/cache/cure/cure-tri-lane/1.1.0/skills/tri-lane/scripts"   # or $CLAUDE_PLUGIN_ROOT/skills/tri-lane/scripts

# before you type the first prompt
python3 $S/lane-log.py start --task v-042 --arm tri-lane --kind security

# ... do the task ...

# when it is merged (or abandoned)
python3 $S/lane-log.py end --task v-042 --route audit --lane "gpt-5.6-sol @ max" --status complete \
    --codex-events "$EVENTS" --agy-json "$OUT" \
    --finding codex:2:0:1 --finding agy:1:2:0 --finding advisor:0:0:0 \
    --advisor fix-first --rework 1

# within 7 days, if a bug from this task surfaces in CI, staging, or use
python3 $S/lane-log.py update --task v-042 --escaped-defects 1 --notes "null roster on empty team"
```

`start` snapshots the clock, the two Google pools (`agy -p /usage`, free), and the Codex weekly percentage (from the newest Codex session log). `end` computes elapsed, sums every Claude assistant message in the window from the project's session transcripts (subagents included), sums Codex usage from its session logs, adds Antigravity usage from the JSON files you pass, snapshots the pools again, and appends one line to `.git/tri-lane/benchmark.jsonl`.

For the `manual` arm the same two commands work; Codex and Antigravity use is picked up from their logs and pool deltas, so nothing extra to instrument. Pass `--route manual`.

## What each number means

| Field | Source | Read it as |
|---|---|---|
| `claude.billable_tokens` | input + cache creation + output, from transcripts | The number the flow exists to cut. Cache reads are reported separately because they are cheap and huge. |
| `claude.messages` | count of assistant messages | Turns. A lean architect has fewer. |
| `codex_lane.*` / `codex_logs.*` | lane events file / Codex session logs | Volume that left the Claude pool. `billable_tokens` (uncached input + output) is the figure comparable to Claude's; `total_tokens` includes re-read context like Claude's cache reads. |
| `agy.*` | agy JSON usage | Includes the ~14.5k floor per call; batching shows here. |
| `pool_deltas` | before/after percentages | Real budget effect per pool. Compare each pool to its own ceiling, never token totals across vendors. |
| `elapsed_seconds` | start to end | Every measured multi-agent flow was slower. Know by how much. |
| `route`, `lane`, `status` | what you declared and what happened | Does solo-default hold; do specs get `refused`. |
| `rework`, `escalated` | corrections sent back | Two corrections means the task was misclassified. |
| `findings.<reviewer>` | your Confirmed / Disputed / Unverified labels | The cross-vendor claim under test. Precision per reviewer. |
| `escaped_defects` | bugs found after merge within 7 days | The only quality number that is not self-reported. |

## Decision rule (pre-registered)

Adopt Tri-Lane for the repo when all of these hold with at least 8 tasks per arm:

1. Median Claude billable tokens per task drop by at least a third versus `manual`.
2. Mean escaped defects per task do not rise.
3. Median elapsed per task is at most 1.5x `manual`.

Keep `advisor-only` instead of full Tri-Lane if the Codex and Antigravity reviews together confirm fewer than one finding per task. Drop the Antigravity lane if its confirmed findings per task stay below Codex's while its pool drains faster.

```bash
python3 $S/benchmark-report.py                # Markdown, applies the rule
python3 $S/benchmark-report.py --html ~/Desktop/tri-lane-report.html
python3 $S/benchmark-report.py --json | jq .decision
```

## Things that will skew it

- Changing the Claude model or effort mid-benchmark.
- Comparing token totals across vendors as if they were one unit.
- Logging the task after the fact from memory. `start` before the first prompt, always.
- Counting a lane's own claim of success. Only `lane-report.py` output and your Confirmed labels count.
- One week of unusually hard or easy work. Match the `--kind` mix.
