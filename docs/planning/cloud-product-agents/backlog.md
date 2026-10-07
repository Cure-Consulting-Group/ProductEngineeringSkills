# Implementation backlog — PRD-CPA-001

Date: 2026-09-27. Estimated founder-active hours assume AI-assisted implementation using existing subscriptions; they are not agent runtime hours or contractor quotes. Low/high estimates include component-level implementation and targeted tests. Integration evaluation, operations, and rollout have dedicated lines; do not add a second generic QA/PM percentage. A separate 20% planning reserve covers integration and flake uncertainty. No measured historical effort-to-actual baseline is available for this platform.

## Effort and phase map

| Component | Epic | Pilot hours | Expansion hours | Combined |
|---|---|---:|---:|---:|
| Goals, test/access inventory, baseline | 01 | 8–16 | 0 | 8–16 |
| Durable control plane and task dispatch | 02 | 16–24 | 8–16 | 24–40 |
| GitHub, telemetry, product adapters | 03 | 12–20 | 8–16 | 20–36 |
| Role workflows and tool policy | 04 | 12–20 | 12–20 | 24–40 |
| Findings, evidence, deduplication | 04 | 8–12 | 8–12 | 16–24 |
| Existing QA and synthetic journey adapters | 05 | 8–12 | 8–16 | 16–28 |
| PM/design rubrics and outcome logic | 04/07 | 8–12 | 8–16 | 16–28 |
| Internal dashboard and digest | 06 | 8–12 | 8–16 | 16–28 |
| Repair branches and independent review | 07 | 0 | 24–40 | 24–40 |
| HoopTrace mobile evidence and fixtures | 05 | 0 | 16–32 | 16–32 |
| Evals, reliability, access and rollout gates | 08 | 12–20 | 8–12 | 20–32 |
| Runbooks, onboarding, recovery handoff | 08 | 4–8 | 4–8 | 8–16 |

Totals are calculated in [cost-results.md](cost-results.md) from the same entries in assumptions.json. Points express relative complexity; hours remain the planning basis. Each story references its parent requirements and named tests. Detailed code paths will be selected in a new runtime repository at kickoff; this skill-library repository stores only planning artifacts.

## EPIC-CPA-01 — Product configuration and baseline

Goal: establish authoritative goals, environments, journeys and policies. Dependency: none. Exit: both manifests resolve, manual baseline method agreed, and integration access validated.

- **STORY-CPA-001 (5 points; FR-01, FR-11):** As a product owner, I want versioned product manifests so reviews apply the correct goals and environment. Given a manifest missing release/environment identity, when a review starts, then it is rejected or blocked with the missing fields. Given different products, when a role loads context, then only that product's decisions and allowed journeys are returned. TEST-CONFIG-001: valid/invalid manifest and environment mapping. TASK-CPA-001: inventory docs/STATE/tests, approve journey IDs, define manifest schema and overrides.
- **STORY-CPA-002 (3 points; FR-01):** As a founder, I want a manual-time and evidence baseline so savings are measurable. Given a 7–14 day observation window, when check-in time is recorded, then coordination, coding, and agent review are separated by product. TEST-BASELINE-001: missing baseline remains unknown; no claimed savings. TASK-CPA-002: baseline template and measurement definitions.

## EPIC-CPA-02 — Durable scheduling and execution

Goal: run unattended without duplicate actions or runaway work. Dependencies: 01. Exit: signed events, scheduled sweeps, leases, outbox, and caps survive injected crashes.

- **STORY-CPA-003 (8 points; FR-02, FR-08):** As an operator, I want durable event intake so releases trigger one review. Given duplicate webhook deliveries or an invalid signature, when received, then duplicates reuse the work record and invalid requests do not dispatch. TEST-INTAKE-001: signature, repo scope, duplicate/event reorder, stale release. TASK-CPA-003: intake adapter, schema, transaction/outbox and GCP schedule.
- **STORY-CPA-004 (8 points; FR-02, FR-08, FR-12):** As an operator, I want bounded worker execution so crashes and retries preserve state. Given an expired lease, when the sweeper reconciles it, then it checks running-job state before reassignment. Given a spend reservation or concurrency limit is exhausted, then new discretionary work queues/stops with a reason. TEST-RUNNER-001: crash after claim, duplicate consumer, budget concurrency race, repetition/time caps. TASK-CPA-004: worker launcher, lease heartbeat, dead-letter handling and cost ledger.

## EPIC-CPA-03 — Read connectors and product evidence

Goal: inspect real evidence with bounded access. Dependencies: 01/02. Exit: GitHub, release identity, approved telemetry, and both product adapters produce provenance-bearing results.

- **STORY-CPA-005 (5 points; FR-03, FR-11):** As a reviewer, I want read adapters so findings use current evidence. Given a source is stale, inaccessible or rate-limited, when queried, then its age/error and blocked status are returned without invented measurements. TEST-CONNECTOR-001: credentials expiry, query bounds, source SHA, provider error. TASK-CPA-005: GitHub App read integration, CI artifacts, aggregate metric contract and approved feedback ingestion.
- **STORY-CPA-006 (5 points; FR-03, FR-11):** As a product owner, I want per-product adapters so existing tooling and decisions are reused. Given a known issue or intentionally deferred platform feature, when reviewed, then the finding links the existing record or is classified as planned work. TEST-PRODUCT-001: canonical HoopTrace fixtures and Recruiting Terminal/claim context. TASK-CPA-006: confirm deployed versions, GA4 access, fixture catalogs and current test environment.

## EPIC-CPA-04 — Specialist reviews and validated findings

Goal: useful PM/design/engineering assessments with traceable evidence. Dependencies: 03. Exit: schema-valid roles, evidence storage, duplicate handling and human adjudication meet pilot precision target.

- **STORY-CPA-007 (8 points; FR-04, FR-08):** As a reviewer, I want role-specific tools and instructions so a review stays within its assignment. Given malicious repo text requesting production access, when processed, then the gateway denies the action and logs it. TEST-ROLE-001: injection, tool selection, cross-product reads, instruction pinning. TASK-CPA-007: adapt existing Cure instructions, define tool schemas and prompt/profile versions.
- **STORY-CPA-008 (5 points; FR-05):** As a founder, I want reproducible findings so I can judge them quickly. Given a finding lacks a reproduction or expected behavior, when submitted, then it cannot become a verified defect. Given the same evidence/finding is submitted again, then it updates the existing record. TEST-FINDING-001: evidence gate, deduplication, retraction, stale version. TASK-CPA-008: finding schema, artifacts, internal publication and issue reconciliation.
- **STORY-CPA-009 (5 points; FR-04, FR-13):** As a PM/designer, I want uncertainty-aware review so weak data does not drive automatic changes. Given too few journey starts or contradictory releases, when evaluating a funnel, then the result is insufficient evidence with denominators. Given a screenshot-only usability claim, then it is labeled heuristic. TEST-METRIC-001: no telemetry, small samples, event drift, confounders. TASK-CPA-009: product rubrics, design screenshot evidence and priority scoring.

## EPIC-CPA-05 — Synthetic and mobile validation

Goal: verify behavior without real customer effects or redundant CI. Dependencies: 03/04. Exit: initial journeys run in isolation and CI evidence is reused by exact SHA/config.

- **STORY-CPA-010 (8 points; FR-06, FR-11):** As QA, I want isolated synthetic journeys so failures can be reproduced. Given Recruiting dev mock-admin is enabled, when a permission journey starts, then it refuses to claim valid access verification. Given a test would send a real message or use production credentials, then execution is blocked. TEST-JOURNEY-001: claim, Terminal verified/unverified identities, discovery/board, fixture reset/teardown. TASK-CPA-010: approved account fixtures, Playwright adapter, screenshot/accessibility/network evidence.
- **STORY-CPA-011 (8 points; FR-06, FR-11):** As QA, I want HoopTrace parity evidence so changes preserve game correctness. Given ledger fixture capture/undo/offline replay, then projections match approved truth. Given matching CI already exists, then its artifact is reused; given iOS execution is needed, then only the approved macOS path runs. TEST-PARITY-001: ledger/box-score/PDF agreement, fixture provenance, emulator failure classification. TASK-CPA-011: golden fixtures, web reads, Android/iOS artifact adapters, manual device checklist.

## EPIC-CPA-06 — Internal dashboard and digest

Goal: replace scattered check-ins with visible product state. Dependencies: 02/04. Exit: six scoped views, decisions, evidence links, unknown states and spend history are usable by authorized founder/reviewers.

- **STORY-CPA-012 (8 points; FR-07, FR-12):** As a founder, I want one dashboard so I can assess product health and make decisions. Given a blocked or unreviewed release, then it displays that state instead of green. Given a reviewer lacks product access, then backend and UI deny its records. TEST-DASHBOARD-001: access, empty/loading/error states, keyboard flow, evidence URLs. TASK-CPA-012: screen spec, shared tokens, React routes, authenticated API and finding decision controls.
- **STORY-CPA-013 (3 points; FR-07):** As a founder, I want a concise durable digest so unchanged findings do not demand attention. Given no material change, then a routine record is retained without repeating an urgent alert. Given a new critical verified defect, then it appears in the internal urgent queue. TEST-DIGEST-001: dedup, durable completion, no external sends without authorized connector. TASK-CPA-013: report renderer and daily/weekly templates.

## EPIC-CPA-07 — Repairs and outcome tracking

Goal: advance from findings to reviewable fixes and verified results. Dependencies: pilot 01–06/08 gates pass. Exit: first repair cohort meets acceptance target and follow-ups distinguish behavior from product impact.

- **STORY-CPA-014 (8 points; FR-09, FR-08):** As an engineer, I want a scoped repair workspace so the agent can prepare a safe draft PR. Given a requested change crosses disallowed paths or touches protected actions, then it stops with a proposed plan. Given the base SHA changed before publication, then the task reconciles/revalidates instead of claiming stale success. TEST-REPAIR-001: allowlists, sandbox, idempotent branch/PR, retries, stale head. TASK-CPA-014: clean checkout, per-task identity, patch/test runner and draft publication.
- **STORY-CPA-015 (5 points; FR-09):** As a reviewer, I want independent validation so implementer claims are challenged. Given tests pass but the original reproduction still fails, then the verdict rejects the repair. Given a required tool/test is unavailable, then the verdict is blocked rather than passed. TEST-REVIEW-001: original-case rerun, unrelated changes, reviewer isolation, falsely asserted success. TASK-CPA-015: reviewer profile, evidence reconciliation and human-ready PR summary.
- **STORY-CPA-016 (5 points; FR-10, FR-13):** As a PM, I want release follow-ups so we know whether changes worked. Given a validated PR is merged but not deployed, then outcome remains pending. Given a release occurs, then behavior and 24–72 hour operational checks are scheduled; 7–14 day product outcomes require adequate data. TEST-OUTCOME-001: deploy mismatch, duplicate release, insufficient data, confounding release. TASK-CPA-016: release tracker, metric windows and outcome reports.

## EPIC-CPA-08 — Evaluation, reliability and operations

Goal: make unattended operation measurable and recoverable. Runs alongside 02–07. Exit: pilot/release gates, recovery rehearsal and owner runbook pass.

- **STORY-CPA-017 (8 points; FR-08, FR-12):** As an operator, I want replayable evaluations so prompt/model changes cannot silently degrade behavior. Given a new instruction/model version, then the 50-case set runs before staged enablement. Given adjudicated performance drops more than five points with adequate samples, then promotion is blocked. TEST-EVAL-001: dataset/trajectory replay, human label provenance, metric gates. TASK-CPA-017: dataset, evaluator and cost attribution.
- **STORY-CPA-018 (5 points; FR-12, FR-08):** As an operator, I want liveness and recovery so silent failures are visible. Given a due review is missed or credentials expire, then the next sweep records an exception. Given the global kill switch, then paid dispatch and writes stop while evidence remains readable. TEST-OPS-001: missed schedule, provider outage, expired auth, restore, retention, stop/resume. TASK-CPA-018: dashboard alerts, backups, runbooks and 14-day pilot report.

## Delivery sequence and capacity

Read-only HoopTrace pilot: 01 → 02 → HoopTrace slices of 03 → 04/05 → 06, with 08 throughout. Then complete 07 and perform the four-week measured HoopTrace comparison. After its decision gate, expand to Recruiting adapters and mobile evidence, followed by a separate 30-day wider operating review. [sprint-plan.md](sprint-plan.md) maps story slices to commitments; full two-product stories are complete only when their deferred slices pass. Product/design work and code execution have dependencies; this does not require parallel human teams or delegated agents to create the plan.

At 20 founder-active hours/week, calendar duration is estimated effort divided by 20 plus observation gates; at 10 hours/week it approximately doubles before gates. Observation can overlap expansion only after pilot safety/precision gates pass. Actual access delays and flaky suite stabilization can extend dates. No launch date is committed.

Definition of done: requirements and acceptance criteria reviewed; meaningful targeted tests pass; access/side-effect boundaries exercised; evidence and run costs recorded; relevant integration/UI check completed; operational docs updated; feature switch and recovery path demonstrated. Runtime code changes are reviewed by a human engineer. Automated evaluation does not replace acceptance review.
