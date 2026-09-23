---
name: chaos-engineering
description: "Designs resilience tests: failure-mode catalogs, game days, fault injection, degradation audits. Use when planning a game day, testing fallbacks, or adding chaos tests to CI on Firebase/GCP."
when_to_use: "NOT for DR plans and backups (use disaster-recovery), live incidents (use incident-response), or load testing (use performance-review)."
argument-hint: "[service-or-project]"
context: fork
metadata:
  verified: 2026-09-23
---

# Chaos Engineering

Resilience testing for Cure's Firebase/GCP stacks with mobile and web clients. **Done when** the
deliverable for the Step-1 type exists: each failure mode has a steady-state hypothesis, an injection
method with a blast-radius limit, an abort criterion, and an expected fallback. Chaos without
observability is just breaking things — if alerts and dashboards don't exist, the first deliverable is
the gap list, not an experiment. Match length to the need; no filler sections or restated summaries.

## Pre-Processing (Auto-Context)

Context (pre-filled in Claude Code; in other runtimes run these commands first):

- Firebase config: !`(cat firebase.json 2>/dev/null || echo "(no firebase.json)") | head -25`
- Existing resilience code: !`(grep -rlE 'circuit|retry|backoff|timeout' src functions/src lib app 2>/dev/null || echo "(none found)") | head -10`
- CI workflows: !`(ls .github/workflows/ 2>/dev/null || echo "(none)") | head -10`

## Step 1: Classify

| Type | When | Output |
|---|---|---|
| Failure Mode Analysis | Before launch or after architecture change | Failure-mode catalog: severity, likelihood, detection, fallback |
| Game Day Planning | Quarterly or before a major launch | Game-day runbook: scope, safety controls, abort criteria |
| Automated Chaos | Teams at maturity level 2+ (below) | CI fault-injection workflow with steady-state checks |
| Graceful Degradation Audit | After incidents or in architecture review | Degradation matrix: failure → observed vs expected behavior, with severity |

## Step 2: Gather Context

Ask only what the repo doesn't show: critical paths (auth, payments, sync), external dependencies
(Stripe, email, OAuth, CDNs), monitoring maturity (dashboards, alerts, tracing), on-call and
runbooks, whether production testing is allowed, and existing recovery levers (flags, rollback).

## Step 3: Failure-Mode Catalog (Cure stack starting set)

| Failure | Likelihood | Impact | Detection |
|---|---|---|---|
| Cloud Functions / Cloud Run errors or timeouts | High | High | Error-rate / 5xx alert |
| Cold-start storm after scale-to-zero | High | Medium | p95 latency spike |
| Cloud Run OOM / instance crash | Medium | High | Restarts, 503s |
| Firestore `RESOURCE_EXHAUSTED` / hotspot contention | Medium | High | Error codes in logs |
| Firestore unavailable | Low | Critical | All reads/writes fail |
| Auth provider / OAuth down | Low | Critical | Login and refresh failures |
| Secret or config unavailable | Low | Critical | Startup or auth failures |
| Stripe API down | Low | Critical | Payment failures |
| Email/push provider down | Medium | Low | Delivery lag |
| Analytics ingestion down | Medium | None | Data gap only |

Extend with the project's own dependencies; drop rows that don't apply.

## Step 4: Cure Resilience Defaults (what the experiments verify)

**Timeouts — one table.** Client-side and server-side timeouts are different layers; set both.

| Call | Timeout | Retry |
|---|---|---|
| Client → API (user waiting) | 5 s, then show an error or cached data | None automatic; offer retry |
| Function/Cloud Run handling a user request | 30 s function timeout | — |
| Server → third-party API (Stripe, email) | 10 s | 3 tries, exponential backoff + jitter, idempotency key required |
| Webhook handler | Acknowledge < 10 s, process async (Cloud Tasks / Pub/Sub) | Provider retries |
| Background / event function | 300 s (v2 event functions cap at 540 s) | Platform retry on, handler idempotent |

Firebase client SDKs retry Firestore/Auth themselves — don't wrap them in circuit breakers. Use
breakers only around third-party HTTP dependencies.

**Fallbacks** (the degradation matrix checks these):
Stripe down → "payments temporarily unavailable" + queue intent via Cloud Tasks, never a double
charge on recovery · Auth down → existing sessions continue, new logins disabled with a message ·
Firestore reads fail → offline cache with "last updated" indicator · writes fail → local queue,
"saved offline" · analytics down → drop silently, never block the user · search down → basic
Firestore query.

**Kill switches.** Every major feature has a Remote Config flag (plus `maintenance_mode` and
`force_update_version`). Use **real-time Remote Config** (`onConfigUpdate` listeners, available on
Android, iOS, and web) so a kill switch lands in seconds; apps that only fetch on an interval wait
for their fetch interval. Test each kill switch monthly — untested switches fail when needed.

## Step 5: Game Day

**Plan:** 2–3 failure modes per game day, staging first (production only at maturity 3+), explicit
blast radius (one service, one region, or a traffic percentage), 1–2 hours. Roles: experiment lead,
observer, on-call ready to intervene, a product stakeholder judging user impact. Write the steady
state first: error rate < X%, p95 < X ms, a business metric (orders/min).

**Safety controls (all required before T+0):** a tested way to stop the injection, a rollback
procedure, on-call present, support notified (production), dashboards open.

**Timeline:** T-30 confirm steady state · T-5 go/no-go · T+0 inject · T+1 did alerts fire and
fallbacks engage? · T+5 blast radius within bounds? · T+30 remove injection · T+35 verify recovery ·
T+45 debrief with owned action items.

**Abort immediately** if blast radius exceeds plan, rollback doesn't work, an unrelated real incident
starts, or any data loss or corruption appears.

### Injection methods (Firebase / GCP)

| Target | Method |
|---|---|
| Cloud Run / Functions v2 (both run on Cloud Run) — errors | Deploy a revision with fault injection enabled and send it a slice of traffic: `gcloud run services update-traffic SVC --to-revisions=FAULTY_REV=10` |
| Cloud Run — full unavailability | `gcloud run services update SVC --ingress=internal` (external callers get 404/403), or remove the `roles/run.invoker` binding for the caller; restore after. (Setting max instances to 0 does **not** make a service unavailable.) |
| Firestore — denial | Deploy security rules that deny one collection (staging, or emulator) |
| Latency / errors in app code | `CHAOS_MODE` env var or a chaos Remote Config flag read by fault-injection middleware; DI swap to a failing client in tests |
| Region / geography | Cloud Armor rule blocking a region in front of the LB |
| Mobile | `maintenance_mode`, `force_update_version`, per-feature kill switches; Network Link Conditioner (iOS) / emulator network throttling (Android) |
| Local | Firebase Emulator Suite: change rules live, stop the Firestore emulator, inject latency |

## Step 6: Automated Chaos in CI

Weekly scheduled workflow against **staging** only: deploy → record steady state → enable fault
injection (flag or revision traffic split) → run `test:chaos` asserting degraded-but-correct behavior
(error rate < 10%, fallbacks engaged, no data loss) → disable → assert recovery within the
hypothesis window. Follow `rules/cicd.md` (SHA-pinned actions, keyless auth — see `ci-cd-pipeline`).

**Hypothesis template:** "When [failure] is injected, the system [expected behavior] with [acceptable
degradation] and recovers within [time]." Example: "When Stripe is unreachable, checkout shows a
clear error and offers a notification, with no duplicate charges after recovery."

**Maturity levels:** 0 ad hoc → 1 quarterly manual game days in staging → 2 weekly automated
staging chaos → 3 controlled production chaos with traffic limits and automated rollback → 4
SLO-gated resilience checks on every deploy. Recommend only the next level up.

## Output

Report: maturity level, failure modes cataloged, fallbacks verified vs missing (each gap with
severity), game days run and last date, kill switches and last test date, and the next-level
recommendations.

## Code/Artifact Generation

Applies only when Step 1 classified the request as below; adapt to existing resilience code first.

| Classification | Write |
|---|---|
| Failure Mode Analysis | `docs/failure-modes.md` |
| Game Day Planning | `docs/game-day-runbook.md` |
| Automated Chaos | `src/middleware/chaos.ts` (flag-gated latency/error injection, off by default and impossible to enable in production without the flag), `.github/workflows/chaos.yml`, deep health check endpoint if none exists |
| Graceful Degradation Audit | Findings only; a circuit breaker (`src/lib/circuit-breaker.ts`) only if the audit finds an unprotected third-party call and the user wants the fix |

## Cross-References

- `incident-response` — when chaos reveals a real problem
- `disaster-recovery` — region-loss and data-corruption planning
- `testing-strategy` — unit/integration tests that complement chaos tests
- `performance-review` — load and latency under stress
