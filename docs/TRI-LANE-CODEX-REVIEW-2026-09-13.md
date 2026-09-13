# Codex Review of the Tri-Lane Production Benchmark

**Date:** September 13, 2026  
**Reviewer:** Codex  
**Scope:** Section 5, Codex review agenda: model allocation, sandbox toolchain caching, and verification output capture.  
**Source report:** [Tri-Lane Production Review](TRI-LANE-PRODUCTION-REVIEW-2026-09-13.md)  
**Dataset:** [142 benchmark task records](../tri-lane/data/benchmark-tasks-2026-09-13.json)

## Recommendation

Keep Luna as the default and select Sol for consequential changes. Treat the observed 78% Luna / 22% Sol allocation as a description of assigned specs, not a validated optimum. Preserve current effort defaults until comparable task outcomes justify a change.

For toolchain preparation, use immutable dependency snapshots copied or filesystem-cloned into private worktree caches. Check readiness under the actual verification sandbox before starting the model's execution timer. This should remove dependency-download delays from the implementation budget; it cannot eliminate timeouts caused by compilation, tests, unavailable services, or sandbox restrictions.

This review inspected both identical copies of the production report, recomputed dataset counts, and read the routing, preflight, toolchain, and verification scripts. No Gradle, SPM, or Node build benchmark was run. The cache design below is a recommendation, not a measured result.

## 1. What the dataset establishes

| Observation | Count | Interpretation |
|---|---:|---|
| Total task records | 142 | Includes records without assigned lanes or execution evidence |
| Assigned Luna specs | 45 | 77.6% of 58 assigned specs |
| Assigned Sol specs | 13 | 22.4% of 58 assigned specs |
| Records with `has_events` | 57 | Event presence alone does not establish completion |
| Records with nonzero `codex_turns` | 49 | Recorded activity, not a verified success count |
| Records with populated `final_status` | 2 | Insufficient for model-specific success rates |
| Records with populated `verify_cmd` | 0 | Verification commands are absent from this export |
| Records with populated `gaps` | 0 | Cannot infer an absence of gaps |
| Records with nonzero `codex_duration_s` | 0 | Cannot compare durations or quantify timeouts |

The 78/22 split is arithmetically correct for assigned specs. It does not establish the best model allocation, comparative success rates, timeout rates, or cost per accepted result. Missing exported fields may indicate extraction gaps rather than missing execution; inspect underlying run artifacts before drawing conclusions.

The production report's recommendation to standardize Luna at `high` is not established by this dataset. The existing [model table](../tri-lane/skills/tri-lane/models.json) defaults routine implementation to Luna `medium`. Its embedded canary claims were not independently revalidated in this review.

## 2. Model selection and escalation

Select Sol on attempt 1 when the actual change affects money movement, authorization, statutory calculations, concurrency, or state-transition invariants. Keep bounded mechanical implementation on Luna.

Keywords should suggest structured risk flags for assessment, not directly select a model. Refund-button copy and refund accounting have different consequences. Likewise, mentioning a state machine does not establish that the task changes its invariants.

The [router](../tri-lane/skills/tri-lane/scripts/lane-route.py) already gives risk rules precedence over size and kind rules. Extend or normalize risk classification where necessary rather than adding a second keyword-based routing mechanism. Its documented workflow is advisory: suggestions are recorded alongside the architect's actual selection.

Separate infrastructure retries from implementation retries. The current router escalates implementation attempts 2 and 3 without receiving a failure cause. A dependency cache miss, sandbox denial, or unavailable simulator should trigger environment repair and a retry on the same model; it should not consume the capability-escalation attempt counter. Reserve escalation for unresolved implementation or reasoning failures.

Evaluate future routing changes using accepted outcomes, rework, confirmed defects, and cost per accepted task, grouped by task risk and kind. Hold effort and environment comparable when assessing model differences. Do not enforce 78/22 as a quota.

## 3. Current cache handling does not prove readiness

The current [toolchain detector](../tri-lane/skills/tri-lane/scripts/lane_toolchains.py):

- Grants writable access to existing user-level caches, including shared Gradle directories and Xcode DerivedData.
- Checks only root-level markers, missing nested Android/iOS projects and projects represented only by Xcode project/workspace files.
- Includes default cache directories even when an environment override relocates a cache.

The current [preflight](../tri-lane/skills/tri-lane/scripts/lane-preflight.py) checks directory existence, not whether the selected verification target's dependencies are present. An empty cache directory can therefore appear usable. Its session-level cached result is not a dependency-readiness certificate and must not substitute for a check keyed to the current dependency inputs.

## 4. Recommended preparation lifecycle

Introduce a separate `lane-cache.py prepare` operation. Keep preflight a fast readiness check rather than making it perform long, implicit builds.

1. **Describe the build.** Identify explicit project roots, package manager/toolchain versions, lockfiles, and verification targets. Allow repository configuration for monorepos rather than relying only on root-marker detection.
2. **Compute the snapshot key.** Include repository identity, relevant manifests and lockfiles, toolchain versions, OS/architecture, target SDK, build target, and preparation recipe version.
3. **Prepare dependencies.** Use a disposable preparation checkout with network access, reviewed build configuration, an independent timeout, and complete logs. Dependency installation can execute project code; preparation must not silently execute unreviewed lane changes outside their sandbox.
4. **Publish atomically.** Use a per-key lock, write into staging, and publish only completed snapshots. Keep credentials and live process/lock state out of snapshots. Published seeds must remain immutable to consuming lanes.
5. **Materialize private caches.** Copy or filesystem-clone the snapshot into the worktree's private cache directory. Do not use writable shared directories, symlinks, or hardlinks to the seed. Point each toolchain at its private cache and keep build outputs private.
6. **Probe readiness.** Run a bounded check under the same environment and sandbox configuration as final verification. Check dependency availability and any required service access. Mark failure as an environment outcome before dispatching the model.
7. **Dispatch and verify.** Start the model's execution budget only after readiness succeeds. Dependency/configuration changes invalidate the relevant readiness record and require preparation again.

Use the same environment and cache-path configuration for implementation and final verification. Remove automatic grants to shared user caches when private cache paths are configured; otherwise the proposed isolation is incomplete.

### Toolchain-specific treatment

| Toolchain | Preparation | Sandbox consumption |
|---|---|---|
| Gradle | Seed wrapper distributions, dependencies, plugins, and required SDK/toolchain components using the intended build targets. A dependency-report task alone is not proof that all build inputs are available. | Restore into private `GRADLE_USER_HOME`; run verification with `--offline`. Keep project outputs private and validate any socket requirements separately. |
| SPM/Xcode | Resolve the selected project/scheme against committed `Package.resolved`, including required package sources and binary artifacts. | Use a private package-source location and private DerivedData. Pass `-disableAutomaticPackageResolution`; probe actual availability because locked resolution does not guarantee all artifacts are cached. |
| Node | Seed the pinned package manager's download cache and account for lifecycle-script downloads, browser binaries, and native build prerequisites. | Install into worktree-local `node_modules`. For npm, use `npm ci --offline --cache <private-cache> --no-audit --no-fund`. Keep the repository's required install flags consistent. |

Gradle documents portable dependency-cache copies and instructs users to exclude `*.lock` and `gc.properties`. Its shared read-only dependency cache is an optional later optimization and is documented as incubating; a private writable Gradle home is still needed. See [Gradle dependency caching](https://docs.gradle.org/current/userguide/dependency_caching.html).

Apple recommends committed resolved versions and `-disableAutomaticPackageResolution` for direct `xcodebuild` CI workflows. The flag is not an offline-completeness guarantee. See [Apple's Swift package CI guidance](https://developer.apple.com/documentation/xcode/building-swift-packages-or-apps-that-use-them-in-continuous-integration-workflows).

For npm, `--prefer-offline` still permits downloading missing data; use `--offline` for a cache-only installation check. Package lifecycle scripts can have their own network behavior, so the sandbox remains the enforcement boundary. See [npm configuration](https://docs.npmjs.com/cli/v11/using-npm/config/) and [npm ci](https://docs.npmjs.com/cli/commands/npm-ci/).

## 5. Failures cache warming cannot fix

The dataset's `iep-and-thrive / s2-flow-fix` summary reports CoreSimulator disconnection and filesystem permission errors. Cache warming cannot provide service access or missing filesystem permissions.

The current [verification wrapper](../tri-lane/skills/tri-lane/scripts/lane-report.py) also recognizes Gradle's loopback socket requirement and automatically opens sandbox network access for detected Gradle commands. That behavior is broader than an offline dependency policy. A warm cache does not make the socket requirement disappear; validate a compatible execution profile and record its permissions explicitly.

Classify at least these outcomes separately:

- `cache-miss`
- `sandbox-denied`
- `service-unavailable`
- `build-timeout`
- `test-failure`

Acceptance should demonstrate a successful warm-cache verification in a fresh worktree, invalidation after dependency changes, independent writable caches for concurrent worktrees, and no writes to shared user caches. Measure preparation time separately from implementation and verification time. These checks have not yet been run.

## 6. Verification output capture

Capture final verification in a separate `verify.jsonl`, linked to the task's model event stream. Record command, working directory, commit/diff identity, exit code, duration, timeout status, execution profile, and cache key. Store full stdout and stderr in separate artifacts and reference them from the record.

The current wrapper captures output but combines stdout/stderr, retains a tail for reporting, and replaces captured output with a timeout message when a timeout occurs. Preserve partial output on timeout and terminate the verification process tree so timed-out descendants cannot continue writing.

Avoid using filtered console output as the grading source: the recorded `s2-flow-fix` command hid the initial failure behind `grep`. Preserve the underlying build exit status and raw output even when presenting a concise summary.

Structured capture makes grading auditable. It does not by itself make tests deterministic or prove that passing tests cover the acceptance criteria.

## 7. Proposed implementation order

1. Repair verification capture and benchmark export so outcomes, durations, and failure causes survive collection.
2. Add explicit project/toolchain configuration and private cache path support shared by execution and reporting.
3. Implement dependency preparation, immutable snapshot publication, invalidation, and sandbox readiness probes.
4. Separate environment retries from capability escalation, then evaluate structured risk routing using comparable accepted outcomes.

These are proposed changes. This review does not authorize or claim implementation, automatic routing activation, or relaxed sandbox permissions.
