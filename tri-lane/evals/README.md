# Canary suite: fixed tasks that measure the lanes

The field benchmark (`BENCHMARK.md`) measures the system on real work and decides adoption. This suite measures the **models** on fixed tasks and decides **routing**: it is the evidence behind `models.json`, and it is re-run whenever a vendor ships a new model so a regression is caught before it costs a real task.

Design rules, each of which is there because breaking it makes the numbers meaningless:

1. **Zero dependencies.** The sandbox has no network. Fixtures use Python `unittest` or Node's built-in `node --test`. No npm install, no emulators, no Gradle.
2. **Shaped like the audit route.** Fixtures reproduce the defect classes the lanes met in Vendly and HoopTrace (payments state, tenant isolation, flaky CI, mechanical migration), not a generic webpage.
3. **Hidden, deterministic graders.** Hidden tests, a planted-bug registry matched by file and line, twenty-run flake checks, grep counts. No human labels, so a run is comparable across months.
4. **A reference solution per fixture.** `lane-eval.py run --task all --lane reference` must score 100%; CI runs it, so a broken fixture or grader fails the build, not the benchmark.
5. **Same wrappers as production.** Codex through `codex exec` with the sandbox flags, Antigravity through `agy -p --mode plan --sandbox` (review roles only, as in the doctrine), Claude through `claude -p`. A canary that runs the model differently from the lane measures the wrong thing.
6. **Isolated.** Each run gets a fresh git repo under `$(git rev-parse --git-common-dir)/tri-lane/evals/runs/`, never a worktree of a real project.

## Fixtures

| Task | Role | Kind | Grader | Decides |
|---|---|---|---|---|
| `review-planted-bugs` | review | payments | 10 planted defects; recall and precision by file and line window | Which reviewer model and effort |
| `impl-spec-service` | implement | impl | 9 hidden tests on a refund policy from a six-part spec | Luna vs Sol vs Astra for delegate work |
| `authz-tenant-isolation` | implement | security | Hidden tests: cross-tenant reads and writes denied, admin scoped | Security-lane model |
| `flaky-test-diagnosis` | implement | ci | Suite passes 20 of 20 runs; the test still exists; the fix names the cause | SRE-shaped work |
| `migration-mechanical` | implement | migration | Zero debug prints left across 30 modules; tests pass | Whether low effort suffices for bulk |
| `web-component` | implement | web | Hidden `node --test` tests: escaping, tone classes, count cap, aria | The one front-end canary |

## Hard tier

The six above are the **smoke** tier: a regression floor that runs in about a minute per lane. On the first live run Luna at medium passed 15 of 15 implementation runs and both flagship reviewers scored 100%, so the smoke tier cannot separate models. The **hard** tier exists to. Its fixtures are not tuned against any model; they target the kinds of work the smoke tier does not exercise.

| Task | Role | Kind | Grader | Forces |
|---|---|---|---|---|
| `needle-in-diff-review` | review | payments | 3 planted regressions inside a ~170-line refactor across five modules, matched by file and line in the new version; the lane reviews `git diff HEAD~1` | Precision under a realistic diff: forty legitimate changes hide three defects (tax on the undiscounted amount, idempotency check after the write, retry after success) |
| `cross-module-invariant` | implement | impl | 6 hidden tests on stock, ledger, and reconciliation | Reading three modules to see one invariant; the symptom is in one place, the causes in two others |
| `concurrency-race` | implement | concurrency | 4 hidden tests, each run 10 consecutive times under 8 threads | Exactly-once claims, exact counters, prompt wake-up on close |
| `underspecified-spec` | implement | impl | `spec_gap`: 1.0 for naming the contradiction and the missing rule and stopping; 0.5 for naming them and guessing anyway; 0 for silently choosing | Whether a lane reports a spec gap instead of improvising, as the doctrine requires |
| `whole-repo-read` | whole-repo | security | `answer_match`: three unprotected routes among 200 handlers and the real secret env name behind an alias chain; false routes and alias names penalised | Whole-repository reading; the one task where a 1M context should show |

## Judgment tier

The hard tier's only discriminator turned out to be the under-specified spec: the fixtures that separated models measured judgment under incomplete or misleading information, not code. The **judgment** tier is built entirely of that.

| Task | Role | Kind | Grader | Forces |
|---|---|---|---|---|
| `nothing-wrong-review` | review | payments | `clean_review`: verdict must be ship with no P0 to P2 findings; each manufactured objection costs a third | Saying "sound" when it is sound, the advisor doctrine's hardest rule |
| `dead-end-migration` | implement | migration | 5 hidden tests plus scope: legacy import gone, v2 gains batch, legacy file untouched | Recognising the obvious path is a dead end and taking the allowed one |
| `misleading-bug-report` | implement | debug | 5 hidden tests; `named_cause` records whether the final message says the report was wrong | Following evidence over the ticket's diagnosis |
| `scope-discipline` | implement | impl | 4 hidden tests plus a 12-line budget; any other file or any "cleanup" fails | Nothing unasked-for smuggled in |

Three more spec-gap fixtures were added after the first judgment run, because the under-specified spec was the only fixture in 73 runs that separated models: `spec-gap-missing-rule` (consistent but incomplete: tie-break and short-list rules unstated), `spec-gap-test-contradiction` (constraints say raise on empty, the visible test expects an empty list), and `spec-gap-impossible-interface` (constraints demand a warning the fixed int return type cannot carry). All use the `spec_gap` grader with `must_name` lists, so naming one gap of two scores 0.3 and naming both and stopping scores 1.0.

## Regression floor

Because most fixtures saturate on current models, the suite's main job is catching a drop when a vendor ships a new model. Freeze the current matrix and compare after an update:

```bash
python3 $S/lane-eval.py baseline                                   # writes .git/tri-lane/evals-baseline.json
python3 $S/lane-eval.py run --task all --lane gpt-5.6-luna --effort medium --repeat 3   # after the update
python3 $S/lane-eval.py compare --since 2026-10-01                 # exit 1 on any cell that dropped more than 0.05
```

Run a tier with `--tier smoke|hard|judgment`. Read the hard tier with `--repeat 5`: pass rate has no resolution below that. `results` prints a cost-per-point line per lane and tier (billable tokens per percentage point of mean score), so two lanes at the same score are separated by what they cost.

## Running

```bash
S="$CLAUDE_PLUGIN_ROOT/skills/tri-lane/scripts"
python3 $S/lane-eval.py list
python3 $S/lane-eval.py run --task all --lane reference                       # validates fixtures, spends nothing
python3 $S/lane-eval.py run --task review-planted-bugs --lane gpt-6-astra --effort high
python3 $S/lane-eval.py run --task review-planted-bugs --lane gemini-3.8-flash-high
python3 $S/lane-eval.py run --task impl-spec-service --lane gpt-5.6-luna --effort medium --repeat 3
python3 $S/lane-eval.py results                                              # matrix task × lane
python3 $S/benchmark-dashboard.py --all-projects --out dashboard.html         # canary section included
```

Results append to `$(git rev-parse --git-common-dir)/tri-lane/evals.jsonl`: task, lane, effort, score, pass, tokens, elapsed, grader detail. `lane-route.py` reads them: a lane with a canary score for a kind is a posterior, not a prior.

## Adding a fixture

`evals/<task-id>/task.json` declares `role`, `kind`, `risk`, `spec` (the six-part spec the lane receives verbatim), `files` (what it may touch), `verify` (the visible command), `grader` (`hidden_tests`, `planted_bugs`, `flake`, or `migration` with its args) and `timeout`. Put visible code under `src/` and `tests/`, hidden tests under `hidden/`, the reference under `solution/` (same layout as the work dir), and for planted bugs a `bugs.json` registry with `id`, `file`, `line`, `pattern`, `severity`, `description`. Run the reference before committing.

## Reading the numbers

- A reviewer's **recall** is the share of planted bugs it found; **precision** is the share of its findings that were planted bugs. A model with high recall and low precision costs you labelling time; one with high precision and low recall costs you escaped defects.
- Implementation **pass rate** over `--repeat` runs matters more than a single pass; a lane that passes two of three at medium and three of three at high has told you the effort, not the model.
- Tokens and elapsed are logged per run so the table can be read as cost per point.
- The suite is small on purpose. Six fixtures at three lanes and two efforts is 36 runs, an afternoon of quota. Add a fixture only when a real task exposes a class the suite does not cover.
