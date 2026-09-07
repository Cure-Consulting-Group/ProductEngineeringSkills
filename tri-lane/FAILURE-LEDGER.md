# Failure ledger

Every failure class the lanes have produced, when it was first seen, what closed it, and whether it is closed. `lane-eval.py failures` reads the machine copy (`failure-ledger.json`) and flags any closed class that reappears. A class that reappears after being closed reopens the clean-week clock in the scorecard.

| Class | Signature | First seen | Closed by | Status |
|---|---|---|---|---|
| infra | Antigravity in plan mode modified a live tree | 2026-09-02 | Lanes run only in worktrees; `--sandbox` hook-enforced (1.0.0) | closed |
| infra | System volume full; lanes writing under `/tmp` stalled | 2026-09-03 | Run dirs on the project volume, `/tmp` excluded from sandbox, disk preflight (1.1.2) | closed |
| infra | Untrusted path form (`/Volumes` vs `~/CureVault`) burned a run | 2026-09-03 | Preflight checks both trust lists (1.1.1) | closed |
| harness | Committed lane diff reported as a refusal | 2026-09-03 | `--base` measures since the branch point (1.1.1) | closed |
| harness | Sol overran its cap with a complete diff | 2026-09-03 | Timeout with a diff is still evaluated (1.1.1) | closed |
| infra | Live worktree removed while the lane ran, twice | 2026-09-03 | Lock, refusal while alive, salvage branch (1.2.0) | closed |
| infra | Sandbox could not write the Gradle cache | 2026-09-03 | Toolchain caches as writable roots (1.2.0) | closed |
| infra | Gradle daemon sockets blocked in sandbox | 2026-09-04 | `--no-daemon --offline` for sandboxed Gradle (1.3.0) | closed |
| harness | Codex rejected the shared review schema (every property must be required) | 2026-09-06 | Strict schema for codex lanes (1.5.1) | closed |
| harness | `codex exec` from a non-terminal waited on stdin | 2026-09-02 | Spec always fed on stdin (1.0.0) | closed |
| fixture | Hidden test asserted behaviour the spec never stated (cross-module reconcile) | 2026-09-06 | Test asserts only the stated invariant; reference corrected (1.6.1) | closed |
| fixture | Race fixture passed on buggy code under the default switch interval | 2026-09-06 | 1 µs switch interval in the hidden tests (1.6.0) | closed |
| fixture | Spec-gap grader rejected natural wording and accepted pasted test names | 2026-09-06 | Default gap pattern, reasoning-only matching, code-style terms (1.8.1, 1.8.2) | closed |
| model | Stalled with no progress (heartbeat) | 2026-09-06 | Detected and killed by the heartbeat watcher; recorded, never retried (1.9.0) | open by design |
| harness | Advisor verdict lost at the turn limit (read-only lane, smallest budget, no output file) | 2026-09-06 | `Write` + `$RUN/advisor.md` first, 15 turns, verdict-from-incomplete-reading rule (1.9.1, #51) | closed |
| harness | Parallel subagent fabricated sibling status ("all four lanes are in") and slept waiting on lanes it could not see | 2026-09-06 | Own-work-only clause in every parallel brief; sibling claims stripped before quoting (1.9.1, #51) | closed |
| harness | Ad-hoc research report existed only in the notification | 2026-09-06 | Every brief names an output path under `$RUN` (1.9.1, #51) | closed |
| harness | Implementer spent its 25 turns on preflight and cache warming, never dispatched codex | 2026-09-06 | Once-per-session preflight reused via `--cached 120`; single `wait`; 40 turns; refuse past turn 10 with no dispatch (1.9.2, #53) | closed |
| harness | Sandboxed VERIFY can never pass on Gradle (lock listener loopback socket denied) | 2026-09-06 | Sandbox network opened for Gradle commands, writes confined, recorded in GAPS (1.9.2, #53) | closed |
| harness | Lane work left uncommitted; git metadata outside the sandbox | 2026-09-06 | `lane-report.py --commit` commits on the lane's behalf (1.9.2, #53) | closed |
| model | Deletion-only diff for a spec file with nothing written back, reported as partial | 2026-09-06 | `refused`, VERIFY skipped, restore and resubmit (1.9.2, #53) | closed |
| harness | `lane-worktree.py status` could not answer "what is live?" without a task | 2026-09-06 | `status` without `--task` lists every lane (1.9.2, #53) | closed |
