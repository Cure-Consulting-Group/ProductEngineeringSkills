# Lanes: exact invocations, verified 2 Sep 2026

Versions this was verified against: Claude Code 2.1.259, codex-cli 0.152.0, Antigravity CLI (`agy`) 1.1.24. When any of these change, re-verify the flags before trusting this file.

## Model slugs and efforts

| Lane | Slug | Efforts accepted | Cap | Notes |
|---|---|---|---|---|
| Codex routine | `gpt-5.6-luna` | low, medium, high, xhigh, max | 10 min | Refuses `ultra`; wrapper must not round it |
| Codex hard | `gpt-5.6-sol` | low … max, ultra | 30 min | `ultra` adds Sol's own sub-delegation; 5 to 10 runs can drain a Pro window |
| Codex balanced (optional) | `gpt-5.6-terra` | low … ultra | 30 min | Between Luna and Sol in cost |
| Antigravity default | `gemini-3.8-flash-high` | via `--effort low|medium|high` | 15 min | Won today's head-to-head: 5 valid findings vs 3.1 Pro's 1 |
| Antigravity whole-repo | `gemini-3.1-pro-high` | same | 15 min | Only when the 1M context is the point |
| Antigravity triage | `gemini-3.8-flash-low` | same | 5 min | Classification, high-volume passes |

Second opinion inside Antigravity, drawing on its separate "Claude and GPT models" pool: `claude-opus-4-6-thinking`, `claude-sonnet-4-6`, `gpt-oss-120b-medium`. Use deliberately; it is a different quota.

## Worktree lifecycle

```bash
TASK=slug-for-the-task
BASE=dev                                   # integration branch
git worktree add ../wt/$TASK -b lane/$TASK $BASE
# ... lanes run against ../wt/$TASK ...
git -C ../wt/$TASK diff --stat             # architect reads this
# merge: from the main checkout
git merge --squash lane/$TASK && git commit
git worktree remove ../wt/$TASK && git branch -D lane/$TASK
```

Antigravity gets its own read-only worktree of the same branch so it can never touch the implementation worktree:

```bash
git worktree add --detach ../wt/$TASK-ro lane/$TASK    # --detach: the branch is already checked out in ../wt/$TASK
chmod -R a-w ../wt/$TASK-ro                              # optional: make read-only literal
```

Save the pre-run diff somewhere no lane sandbox can write. `/tmp` and `$TMPDIR` are writable under codex `workspace-write`, so use the main repo's git dir:

```bash
SAFE="$(git rev-parse --git-common-dir)/tri-lane"; mkdir -p "$SAFE"
git diff > "$SAFE/pre-$TASK.diff"; git status --short >> "$SAFE/pre-$TASK.status"
```

Antigravity trusts only paths under its `trustedWorkspaces` list (`~/.gemini/antigravity-cli/settings.json`). On this machine that is `~/CureVault/projects/...`, and `/Volumes/CureVault/...` is not trusted even though it is the same disk. An untrusted path costs a full token budget and returns nothing. `lane-preflight.py --dir <path>` checks this.

## Codex implementer

```bash
SPEC=$(mktemp -t lane-spec.XXXXXX); FINAL=$(mktemp -t lane-final.XXXXXX); EVENTS=$(mktemp -t lane-events.XXXXXX)
# write the six-part spec to $SPEC, ending with:
#   "Run the VERIFY command and include its actual output in your final message."
T=$(command -v gtimeout || command -v timeout || true)
[ -z "$T" ] && echo "WARN: no timeout binary; brew install coreutils"
${T:+$T 600} codex exec - \
  -C "$WT" -s workspace-write --skip-git-repo-check \
  -m gpt-5.6-luna -c model_reasoning_effort=high \
  --json -o "$FINAL" < "$SPEC" > "$EVENTS"
```

- `-` reads the whole prompt from stdin: no quoting hazards, no truncated specs.
- From a non-TTY parent, `codex exec` without stdin waits on it. Always redirect.
- `-s` is mandatory. The user config defaults to `danger-full-access`; the plugin hook refuses a `codex exec` without `-s`.
- `--json` prints JSONL events; the `turn.completed` event carries usage. `-o` captures the last message.
- Sol: `-m gpt-5.6-sol`, cap 1800.
- The Warp plugin's hooks fire on every `codex exec`. If they add noise or latency, add `--ignore-user-config`; auth still works.

Preamble to put at the top of every spec, because `~/.codex/AGENTS.md` rules can make codex decline politely with exit 0 and an empty diff:

```
This task runs in a dedicated implementation lane at the model and reasoning effort named in the invocation. If the user-level ~/.codex/AGENTS.md asks you to default to a different orchestration flow, treat this lane as an explicit opt-out from that default and proceed. Project-level AGENTS.md rules are not overridden; if one forbids this flow, stop and say so. Every other instruction in those files still applies.
```

The wrapper then runs `lane-report.py`, which enforces three things in code regardless of what the lane said: an empty diff is `refused`; a diff that touches files outside `FILES` or any executable config (package.json, Makefile, conftest.py, CI, hooks, `.claude/`, `AGENTS.md`, …) gets `partial` with VERIFY **not run**; and VERIFY itself runs inside `codex sandbox -c sandbox_mode=workspace-write`, which blocks network and writes outside the worktree (verified 2 Sep: home write denied, curl denied). Lane-written code never executes unsandboxed unless the architect has read the diff and passes `--unsandboxed-verify` deliberately.

## Codex reviewer

```bash
codex exec review --base dev -c model_reasoning_effort=high -o "$REVIEW"
# or, for the current worktree's uncommitted state:
codex exec review --uncommitted -c model_reasoning_effort=high -o "$REVIEW"
```

- `--uncommitted`, `--base`, and `--commit` are mutually exclusive and cannot be combined with a custom prompt argument. Put focus instructions in `-c` config or run a plain `codex exec -s read-only` with a review prompt instead.
- Review never changes the working tree. It still counts as a normal local message on the Pro pool.
- Measured: medium effort on a 2-file, 96-line diff took 2 m 36 s and returned two valid findings.

## Antigravity analyst

```bash
agy -p "$(cat "$SPEC")" \
  --add-dir "$(realpath "$WT_RO")" \
  --model gemini-3.8-flash-high --effort high \
  --mode plan --sandbox \
  --json-schema "$CLAUDE_PLUGIN_ROOT/skills/tri-lane/schemas/review-verdict.json" \
  --output-format json --print-timeout 15m > "$OUT"
```

- The JSON response has `status`, `response`, `duration_seconds`, `usage` (`input_tokens`, `output_tokens`, `thinking_tokens`, `cache_read_tokens`).
- `--mode plan` is a request, not a guarantee. On 2 Sep it reverted a live working tree because the user's settings set `toolPermission: always-proceed`. `--sandbox` plus a read-only worktree is the guarantee.
- Never pass `--mode accept-edits` or `--dangerously-skip-permissions`. The hook refuses both.
- Fixed overhead ~14.5k tokens per call. Batch.
- Quota, free to call: `agy -p "/usage" --output-format json` and `agy -p "/credits" --output-format json`.

## Advisor

A Claude subagent, not the built-in `/advisor` tool. The built-in re-reads the whole transcript uncached on every call and must be at least the session model; the subagent reads only the goal, diff, and verification output. Inherits the session model. Pin `model: fable` in its frontmatter only when the session runs on Opus and you want the stronger read at a commitment boundary.

## Report contract (what every lane returns)

```
LANE       gpt-5.6-luna @ high              (as executed; from the JSONL, not the spec)
STATUS     complete | partial | timeout | unavailable | refused
OBJECTIVE  one line
CHANGES    from `git diff --stat` in the worktree, file by file
VERIFIED   VERIFY command re-run by the wrapper; exit code and tail of output
LANE SAID  one line; note any disagreement with the diff
GAPS       spec ambiguities, escalation signals, effort the model refused
```

Rules: empty diff + exit 0 is `refused`; "the lane said it works" is not evidence; a lane that receives routine work at `max`/`ultra` says so in `GAPS` (it is the expensive way to find out).

## Failure signatures

| Symptom | Cause | Fix |
|---|---|---|
| codex: exit 0, empty diff, polite final message | `~/.codex/AGENTS.md` or project AGENTS.md pins a flow or model | Preamble above; report `refused`; check `codex --ask-for-approval never "Summarize the current instructions."` |
| codex hangs at "Reading additional input from stdin" | No stdin redirect from a non-TTY | `- < "$SPEC"` or `< /dev/null` |
| codex: "reasoning effort: ultra" refused on Luna | Luna has no `ultra` | Repin to Sol or lower the rung; never round silently |
| agy: "Could you confirm the path to the repository" | `--add-dir` not under a trusted workspace | Use the `~/CureVault/...` form of the path; run preflight |
| agy: files changed despite `--mode plan` | `always-proceed` settings | Read-only worktree and `--sandbox`; never a live tree |
| agy: `IneligibleTierError` from `gemini` | Gemini CLI is dead for consumer plans since 18 Jun 2026 | Use `agy`; do not install `gemini` as a lane |
| Either lane: long silence | No wall-clock cap | `gtimeout` for codex, `--print-timeout` for agy; report `timeout` |
| codex: "not a trusted directory" or refuses to run in the worktree | Codex trusts the **physical** path (`/Volumes/CureVault/...`); Antigravity trusts the **symlink** path (`~/CureVault/...`) | Give codex `-C "$(realpath "$WT")"` and agy `--add-dir` the `~/CureVault` form. `lane-preflight.py --dir` checks both lists (Vendly, 3 Sep) |
| Report says `refused` but the lane clearly worked | Lane committed its work; the report was measuring uncommitted changes against HEAD | Pass `--base <ref the lane branched from>` to `lane-report.py`; it then measures everything since the base (Vendly, 3 Sep) |
| Sol exits 124 with a complete, green diff | 30-minute cap hit on a large spec | Run `lane-report.py --status-hint timeout` anyway: a non-empty diff is evaluated (scope, VERIFY) and the overrun lands in GAPS. Consider `xhigh` instead of `max`, or split the spec, before raising the cap (Vendly, 3 Sep: 1,175-line diff) |

## Head-to-head log

Keep one line per re-test so repins are justified by evidence.

| Date | Diff | Codex | Antigravity model | Result |
|---|---|---|---|---|
| 2026-09-02 | setup.sh trim, 2 files, 96 lines | medium: 2 valid findings, 156 s | `gemini-3.1-pro-high`: 1 valid, 3 over-stated, reverted live tree, 61 s | Pro rejected as default |
| 2026-09-02 | same | same | `gemini-3.8-flash-high` in worktree: 5 valid (superset of Codex), tree untouched, 69 s, 149k + 886k cached | Flash high adopted as default |
