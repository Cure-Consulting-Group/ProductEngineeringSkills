# Feature Flags

**Outcome:** a flag (or flag system) that is safe when the provider is unreachable, has an owner and
an expiry, rolls out in stages with rollback triggers, and gets removed on schedule. Done when the
flag exists in code behind a provider abstraction, is in the registry, and has a cleanup date.

Invariants (each exists because it has burned a release):
- Safe defaults — if the flag service is unreachable, the app must still work with the default value.
- Kill switches evaluate remotely and take effect without a deploy or app update.
- Every temporary flag has an owner and a max age (table in Step 6); overdue flags are tech debt with a ticket.
- Don't nest flags more than two levels — the combinations become untestable.

## Pre-Processing (Auto-Context)

Context (pre-filled in Claude Code; in other runtimes run these commands first):

- Flag provider in use: !`grep -rlE "remote-config|RemoteConfig|launchdarkly|LaunchDarkly|@vercel/edge-config|statsig|flagsmith" --include=*.json --include=*.kts --include=Podfile --include=Package.swift --exclude-dir=node_modules --exclude-dir=.git . 2>/dev/null | head -4 | grep . || echo "(no flag SDK detected)"`
- Flag registry: !`ls config/feature-flags.yml flags.yml 2>/dev/null | head -2 | grep . || echo "(no registry)"`

## Step 1: Classify

| Flag type | Prefix | Purpose | Max age |
|---|---|---|---|
| Release toggle | `release_` | Gate unfinished or staged work | 60 days |
| Experiment | `exp_` | A/B test a hypothesis | 45 days (includes analysis) |
| Ops / kill switch | `ops_` | Disable a feature in an incident | Permanent; annual review |
| Permission | `perm_` | Entitlement / segment access | 1 year; re-justify |

Also classify the request: **add a flag** (Steps 3–5), **plan a rollout** (Step 5), **hygiene/cleanup**
(Step 6), or **question** (answer only).

## Step 2: Gather Context

Ask only for what is missing: what is flagged and why, platforms (Android, iOS, web, Cloud Functions),
provider (default: Firebase Remote Config for Firebase-stack projects; LaunchDarkly when the client
already pays for it), targeting needs (user ID, app version, country, tier, percentage), how fast it must
be disabled, and interactions with existing flags.

## Step 3: Architecture

- Names: `{prefix}_{feature}[_{variant}]`, snake_case, ≤50 chars, no version numbers (use variants).
- Features never call the provider SDK directly — one `FeatureFlagProvider` abstraction per platform, with local defaults compiled in (XML/plist/JSON) so first launch works offline.
- Mobile: `minimumFetchInterval` 0 in debug, 3600s in release; use Remote Config real-time listeners for kill switches so they apply without waiting for the next fetch.
- Web: evaluate server-side (Server Component / route handler) and pass values to the client to avoid a flash of the wrong UI.
- Registry: `config/feature-flags.yml` with `name, type, owner, created, max_age, status, platforms, ticket, cleanup_pr`.

Read `reference/details.md` when writing the provider for a platform — it has the Android (Hilt),
iOS (async/await), and Next.js (Admin SDK server templates or Vercel Edge Config) implementations.

## Step 4: Experiments

Flags carry the assignment; statistics belong to the ab-test-analyst agent — hand it the hypothesis,
primary/guardrail metrics, baseline, and MDE for sample size and the readout. For Remote Config
experiments, prefer **Firebase A/B Testing**, which assigns variants and computes results itself.

Instrumentation rules for Google Analytics for Firebase:
- Set the user with `setUserId`; don't send `user_id` or timestamps as event params (the ID is PII in params, and every event already carries `event_timestamp`).
- Log the variant once as a user property (e.g. `exp_checkout_single_page = treatment_b`) or an `experiment_assigned` event with `experiment` and `variant` params.
- In the BigQuery export, events live in `events_*` date-sharded tables with params nested in `event_params` — read them with `UNNEST(event_params)`, not flat columns.
- Fix the duration from the sample size before launch and decide at that point; extending "until significant" is peeking.

## Step 5: Progressive Rollout

For Firebase, use **Remote Config rollouts** (percentage stages with Crashlytics and Analytics
monitoring per rollout, and one-click rollback). Cure default stages:

| Stage | Audience | Hold | Advance when |
|---|---|---|---|
| Internal | Team UIDs / debug builds | 2–5 days | No crashes, team sign-off |
| Canary | 1% | 1–3 days | Crash-free and error rate at baseline, p95 unchanged |
| Early | 10% | 3–5 days | Above + support volume flat |
| Half | 50% | 3–7 days | Above + experiment metrics positive (if any) |
| Full | 100% | 7 days | Stable → open the cleanup ticket |

Roll back at any stage if crash rate rises >0.5 points or error rate >1 point over baseline, p95 latency
rises >50%, or on-call flips the kill switch.

## Step 6: Hygiene and Cleanup

- A scheduled CI job (weekly) compares flag references in code to the registry: in code but not registry → undocumented; in registry but not code → delete from provider; past max age → open a cleanup issue. Use `actions/checkout@v7` (current major, verified 2026-09-23 against the actions/checkout releases).
- PRs that add/change/remove a flag fill a "Feature Flags" table in the PR template (action, name, type, owner, cleanup date).
- Cleanup PR: keep the winning path, delete the losing path and its tests, remove local defaults, provider entry, and registry row; confirm no other flag depends on it.
- Budget ~10% of each sprint for flag cleanup until the overdue list is empty.

## Code/Artifact Generation

Applies when Step 1 is "add a flag" or "hygiene" and the project lacks the piece. Write only what's missing:

1. The provider abstraction + the new flag with its safe default (platforms in scope).
2. `config/feature-flags.yml` registry entry (create the file if absent).
3. `scripts/check-dead-flags.sh` cross-referencing registry and code.
4. `.github/workflows/flag-hygiene.yml` on a weekly schedule running that script.

Deliver the requested flag; don't refactor unrelated feature code. Related: release-management
(coordinate flags with store releases), analytics-implementation (event taxonomy), testing-strategy
(test both flag states).
