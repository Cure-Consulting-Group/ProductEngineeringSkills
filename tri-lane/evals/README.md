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
