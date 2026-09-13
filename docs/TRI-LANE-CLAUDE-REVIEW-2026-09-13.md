# Claude Review of the Tri-Lane Production Benchmark

**Date:** September 13, 2026
**Reviewer:** Claude (architect and advisor lane), fresh read against the raw run directories and scripts
**Scope:** Section 5, Claude review agenda (spec-validation hook, mandatory advisor, solo ceiling); a claim-by-claim check of the Antigravity report; a source check of the Codex review; the re-scoped Tri-Lane v2 plan
**Source report:** [Tri-Lane Production Review](TRI-LANE-PRODUCTION-REVIEW-2026-09-13.md)
**Sibling review:** [Codex Review](TRI-LANE-CODEX-REVIEW-2026-09-13.md)
**Dashboard:** Tri-Lane Benchmark artifact, republished 13 Sep with this read
**Plan:** BACKLOG.md, Wave 4 (T42–T51)

## Recommendation

Decline both Section 5 proposals as written. Do not adopt the report's "STRONG ADOPT" verdict; the pre-registered decision rule in `BENCHMARK.md` was never run, because nothing it needs was logged. Spend the next release on instrumentation that makes every future task land in `benchmark.jsonl` without a human typing a command, backfill the first 142 tasks from the run directories with inferred fields marked as such, and only then revisit routing, cache preparation, or mandatory gates.

The one number the doctrine exists to cut, Claude billable tokens, is recoverable from local transcripts and was not looked at. A first proxy (below) moves in the wrong direction. It is a proxy, not a verdict, and the plan's first job is to replace it with the real measurement.

## 1. What the export establishes, and what it cannot

All headline token figures in the Antigravity report recompute exactly from `tri-lane/data/benchmark-tasks-2026-09-13.json`. The interpretive claims do not survive contact with the schema.

| Claim (report section) | Status | Basis |
|---|---|---|
| Claude billable offload ≥ 33%: PASSED (§1) | Unsupported | The rule is median *Claude* billable per task, tri-lane versus manual arm. The export holds no Claude tokens and no manual arm. 14.7M is volume that ran on other vendors, not a measured reduction. |
| Review precision > 0 confirmed findings per task: PASSED (§1) | Unsupported | No Confirmed/Disputed/Unverified labels exist; no repository has a `benchmark.jsonl`. 10 of 11 fix-first is a verdict rate on reviews the architect chose to request. |
| Prompt cache 96.1% (§1, §3A) | Verified | 215,150,080 cached, 8,802,380 billable. |
| Worktree isolation 100%, zero live-tree overwrites (§1) | Qualified | Not a field. The failure ledger shows the class closed at 1.0.0 with no reopen. True by absence of incident. |
| Model tiering 77.6 / 22.4 matches intent (§1, §3A) | Qualified | 45 and 13 of 58 assigned specs. "Matches intent" needs outcomes per tier; `final_status` is populated on 2 records. |
| Median 1 turn proves single-shot specs (§3A, §4.1) | Unsupported | `codex exec` is one turn per dispatch by construction. The four 2-turn files hold one `thread.started` and an `error` event: a retry inside one run. |
| Median billable per task 169,304 (§3A) | Qualified | Correct over 49 nonzero runs; the report says 57. Over all 57 the median is 135,929. |
| Antigravity medians 311,222 tokens, 198.7 s (§3B) | Verified | 17 tasks, 25 calls, 5,883,080 total. |
| readiness-scope findings (§3B) | Verified | `agy.json` in that run directory carries exactly those three findings. |
| Advisor 90.9% is an actionable catch rate (§3C) | Qualified | Eight of eleven targets were documents, plans, an RFC, or a brand package. Two were delegate diffs. Whether fixes were applied is unrecorded. |
| Rework root causes: vague FILES, cold caches (§4.1) | Unsupported | `gaps`, `final_status`, `codex_duration_s` are empty on every record. |
| Six-part spec is the highest-leverage artifact (§4.1) | Qualified | All 58 specs on disk are complete. Nothing isolates spec quality from lane, rung, or repository. |

Why the fields are empty: `lane-log.py start` was never run before a task, so `end` could not run after one. `lane-report.py` prints its report and never writes it to the run directory, so status and gaps exist only in a subagent notification. The export was built by hand from `final.md` (Codex's closing message) and `events.jsonl`, which is why it carries tokens and nothing else.

## 2. Codex review, checked against the source

All nine script and dataset claims are correct. Each file named was opened at plugin version 1.9.2.

| Claim | Where |
|---|---|
| Toolchain detector grants shared user caches (Gradle home, DerivedData) as writable roots | `lane_toolchains.py` lines 22, 28, 47 |
| Detector checks root-level markers only | line 38 |
| Default cache dirs included even under an env override | line 44, deliberate |
| Preflight checks directory existence, not dependency readiness | `lane-preflight.py` line 213 |
| Verify wrapper merges stdout/stderr; timeout replaces output | `lane-report.py` `run_verify` |
| Router escalates on attempt number alone | `lane-route.py` lines 78–83 |
| `models.json` defaults routine work to Luna at medium; production used high on 28 of 45 Luna specs | rule `impl-routine` |
| Gradle commands open sandbox network automatically | `needs_network` |
| Dataset counts 57 / 49 / 2 / 0 / 0 / 0 | recomputed |

Where it overreaches: the seven-step cache preparation lifecycle (snapshot keys, per-key locks, immutable seeds, filesystem clones, readiness probes) is designed before anyone has counted cold-cache failures. The ledger shows the Gradle cache and daemon classes closed on 3 and 4 September. The one sandbox failure visible in the summaries (`s2-flow-fix`) was CoreSimulator and filesystem permissions, which the review itself says caching cannot fix. Its implementation order is right: repair capture, then count, then build. The plan holds the cache work behind a count (T46 → gate on T49's data).

Its separation of environment retries from capability escalation is correct and cheap; it ships in Wave 4 (T46).

## 3. Section 5 answers

**Q1. Validate the six-part spec in the PreToolUse hook: no.**
All 58 specs on disk carry all seven sections. The implementer already refuses a spec missing LANE, REASONING, or VERIFY; the report script records a missing VERIFY as a gap. The rework the report describes (vague FILES, cold caches) is invisible to a header check. The guard hook is a 5-second, fail-open safety rail on every Bash call in every consuming project; a quality lint there mixes concerns. Instead: `lane-spec.py check` in the implementer's step 3, validating substance (FILES resolve, rung legal for the lane, VERIFY unfiltered). Backlog priority, T50.

**Q2. Mandatory advisor on every delegate route before PR: not blanket; enforce at the merge gate.**
The doctrine already says "advisor once at the end" on the delegate row; observed compliance is 2 of 56 Codex-only tasks. The missing piece is enforcement and a recorded skip, not a rule. Fifteen advisor transcripts show a median of 116,387 billable Claude tokens per review; blanket coverage of the 54 unreviewed delegate tasks would have cost about 6.3M against 14.7M moved off Claude. Enforcement cannot live in the PreToolUse hook (the advisor is an Agent-tool call; PRs may go through the GitHub MCP tool). Instead: `$RUN/advisor.md` becomes a precondition of `lane-worktree.py remove`, with an explicit, logged skip reason; mandatory for Sol lanes, diffs over about 150 lines, and audit-trigger paths. T45.

**Q3. Tighten the solo ceiling to diffs under 20 lines: cannot be evaluated.**
Routes were never logged. T44 makes the route a file; revisit at 30 logged tasks.

## 4. The Claude-side proxy the report did not run

`usage-window.py` sums Claude and Codex usage from local logs for a project and a window. Ten days before adoption versus the ten days of the review, four repositories:

| Repository | Claude billable, 25 Aug–3 Sep | Claude billable, 4–13 Sep | Assistant messages | Commits (pre → post) |
|---|---:|---:|---:|---|
| statledger | 24.8M | 58.8M | 2,381 → 10,010 | 74 → 122 |
| iep-and-thrive | 0.7M | 33.7M | 38 → 4,530 | 0 → 56 |
| cannabis-retail-platform | 52.8M | 35.7M | 3,965 → 6,372 | 128 → 0 |
| Finality | 0 | 5.4M | 0 → 2,037 | 0 → 24 |

Read with care. Work mix differs between windows; the post window includes review and documentation sessions; commit counts are on the checked-out branch only. What it does show: per statledger commit, Claude billable went from about 335k to about 482k, and assistant message volume quadrupled. The orchestration itself (wrapper agents, advisor, explorer subagents) is Claude spend, and nothing yet nets it against the offload. This is why the pre-registered rule needs its manual arm, and why T49 is a decision for the founder, not a script.

Two measurement defects surfaced while running it: Codex usage from session logs is account-wide, not project-scoped (the same 45.5M / 19.6M appears for every repository), so per-task Codex attribution must come from lane event files only; and Codex billable outside the lanes (19.6M in logs versus 8.8M in lane events) means roughly 11M of Codex use in the window was manual and unlogged.

## 5. Re-scoped plan: Tri-Lane v2, measure before mandate

Full tickets in `BACKLOG.md` Wave 4. In order:

1. **T43** Persist the lane report and verification evidence (`report.json`, `verify.jsonl`, raw stdout/stderr, partial output on timeout).
2. **T42** Automatic start and end at the worktree lifecycle: `add` opens the log record, `remove` closes it with auto-discovered route, lane, status, advisor, tokens.
3. **T44** Route declaration and rework as files; retire the turn-count metric.
4. **T51** Defect windows surfaced at session start; escaped defects stop being zero by construction.
5. **T45** Advisor evidence at the merge gate, with a logged skip (Section 5 Q2).
6. **T46** Failure cause taxonomy on production runs; environment retries no longer advance capability escalation.
7. **T47** Backfill the first 142 tasks from run directories, inferred fields marked; reproducible export replaces the hand-built JSON.
8. **T48** Dashboard: population and coverage panels, evidence-gap tiles, Claude cost when present, "not recorded" when absent.
9. **T49** The cost verdict: retrospective proxy script now; the pre-registered manual arm (8 matched tasks, one repo, one week) needs a go decision.
10. **T50** Spec substance lint (Section 5 Q1 alternative), lowest priority.

Held, with the gate that releases them: Luna-at-high pin (needs outcomes per rung from T42/T47); private-cache preparation lifecycle (needs ≥ 5 `cache-miss` classifications in 30 logged tasks from T46); solo ceiling (needs 30 logged routes from T44).

**Definition of done for the wave:** every dispatched task lands in `benchmark.jsonl` with route, lane, status, advisor verdict, Claude and Codex tokens, and rework, with zero manual flags; `benchmark-report.py` can evaluate all three checks of the pre-registered rule from that data; the 142-task backfill exists with every inferred field marked; the Section 5 gates are enforced at `remove` and every skip is logged with a reason.
