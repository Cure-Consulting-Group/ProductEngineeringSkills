# Sprint plan — HoopTrace-first cloud product agents

Prepared 2026-09-27. Parent: [PRD-CPA-001](scope.md); stories: [implementation backlog](backlog.md). Planning only; this document does not provision resources, change product code, or enable unattended access.

## 1. Capacity and scope assumptions

Two-week sprints. One founder/engineer, Rashad, owns implementation, acceptance decisions and operations, assisted by existing AI tools. No additional engineer, reviewer or parallel agent team is assumed. User-confirmed capacity is **20 focused hours/week**; focused hours already account for time spent on other projects, so no further focus-factor deduction is applied.

Each sprint has 40 available founder-active hours. Commit no more than 34; reserve 6 for integration failures, unexpected review work and corrections. All estimates include normal implementation, targeted validation and lightweight planning/review. Planned work totals **286 hours**; ten sprint buffers total **60 hours**, for **346 hours** including reserve. Remaining capacity in measurement sprints is uncommitted, not a promise of extra scope. This reserve serves the existing 20% build-risk allowance; do not add that allowance again. The earlier full-platform range remains 250–432 hours, so the upper case can require additional sprints.

Sprints 1–8 cover HoopTrace's web box score, PDF and game-data checks, then a measured repair pilot. Sprints 9–10 are conditional expansion to Initiated Recruiting and mobile integration/hardening. First release does not include mobile capture changes, production data repair, automatic merge/deploy, customer messages, or unrestricted authentication/payment changes.

Week numbers are relative to kickoff. No start date or launch deadline has been agreed. Credentials, hosting, API access, staging freshness and selected repair categories must be configured under the product owner's established permissions at implementation time. A sprint begins only when its dependencies and acceptance criteria are ready.

## 2. Sprint overview

| Sprint | Weeks | Goal / demonstrable result | Planned hours | Buffer | Owner | Gate |
|---|---|---|---:|---:|---|---|
| 1 | 1–2 | One repeatable HoopTrace review and a recorded manual baseline | 28 | 6 | Rashad | G0: environment and measurement ready |
| 2 | 3–4 | Durable cloud scheduling, job state, evidence and spend tracking | 34 | 6 | Rashad | G1: reliable bounded execution |
| 3 | 5–6 | PM, design, engineering and QA produce structured findings | 34 | 6 | Rashad | G2: controlled review quality |
| 4 | 7–8 | Read-only reviews run against relevant releases; dashboard shows evidence | 30 | 6 | Rashad | G3: 14-day shadow results |
| 5 | 9–10 | Scoped engineering prepares draft repairs in isolated branches | 34 | 6 | Rashad | G4: repair boundaries verified |
| 6 | 11–12 | Independent QA and post-release verification complete the loop | 30 | 6 | Rashad | G5: comparison protocol and repair flow ready |
| 7 | 13–14 | First half of controlled live comparison; actual costs/hours captured | 18 | 6 | Rashad | G6: interim measurement integrity |
| 8 | 15–16 | Four-week comparison report and evidence-based expansion decision | 18 | 6 | Rashad | G7: value and quality decision |
| 9 | 17–18 | Integrate Recruiting's initial journeys using the existing platform | 30 | 6 | Rashad | G8: second-product isolation and checks |
| 10 | 19–20 | Mobile evidence, recovery, operating runbook and wider-release readiness | 30 | 6 | Rashad | G9: expansion acceptance |

This is a capacity plan, not measured velocity. Repository commit counts motivated pilot selection but are not used to predict delivered scope. After two sprints, replace assumptions with completed accepted work and actual active hours. If a task exceeds the sprint cap, carry it forward and move the gate; never silently reduce validation.

## 3. Sprint commitments

### Sprint 1 — Environment, baseline and small proof

| Work package | Existing story / requirement | Hours | Owner |
|---|---|---:|---|
| Inventory HoopTrace goals, current issues, release identities and available fixtures | 001/006, HoopTrace slice; FR-01/11 | 6 | Rashad |
| Establish isolated, release-pinned web/PDF fixture environment and known expected outcomes | 011, web/data slice; FR-06/11 | 8 | Rashad |
| Build the smallest repeatable report using existing skills/tests; capture screenshot/test evidence | 007/008, proof slice; FR-04/05 | 8 | Rashad |
| Log current check-in time and register metrics, task classes and baseline workflow | 002; FR-01 | 6 | Rashad |

Deliverable: one saved report showing input/release, expected/actual result, evidence, founder time and inference cost. Baseline observation spans 7–14 days; product implementation work continues normally, with coordination and coding recorded separately. Initial proof is read-only and may be manually invoked; unattended cloud execution is Sprint 2.

Acceptance G0: staging/fixture provenance is known; current approved cases pass; deliberately broken isolated variants produce reproducible failures; report can be reproduced; baseline definitions agreed. If dev is stale, fix/replace the isolated test target before claiming validation. Exit decision: continue the small proof or invest in durable platform work.

### Sprint 2 — Reliable cloud foundation

| Work package | Existing story / requirement | Hours | Owner |
|---|---|---:|---|
| Product config, authenticated intake and Cloud Scheduler trigger | 001/003; FR-01/02 | 8 | Rashad |
| Firestore task state/outbox, Pub/Sub dispatch, lease and retry lifecycle | 004; FR-02/12 | 12 | Rashad |
| Isolated read worker, Cloud Storage artifacts and credential boundaries | 004/005/008; FR-03/05/08 | 8 | Rashad |
| Per-run cost reservations/caps, kill switch and missed-run detection | 004/018; FR-08/12 | 6 | Rashad |

Deliverable: a scheduled cloud review completes while the founder's machine is offline, and its evidence/cost is durable. Test duplicate webhook delivery, worker crash, expired credentials, stalled lease and exhausted task budget. Scheduler is in GCP; do not introduce GitHub Actions cron.

Acceptance G1: duplicate events do not duplicate side effects; retries are bounded; a failed source is blocked rather than green; the kill switch prevents further paid dispatch; each completed or failed run records cost and a reason. No repair credentials enabled.

### Sprint 3 — Specialist reviews and controlled evaluation

| Work package | Existing story / requirement | Hours | Owner |
|---|---|---:|---|
| Versioned PM/design/engineering/QA profiles and role-specific tools | 007; FR-04/08 | 10 | Rashad |
| Findings schema, evidence requirements, existing-issue deduplication | 008; FR-05 | 8 | Rashad |
| PM prioritization and design rubric for approved web/PDF surfaces | 009; FR-04/13 | 6 | Rashad |
| Held-out evaluation cases, deterministic grading and human adjudication | 017; FR-08 | 10 | Rashad |

Deliverable: one release review assigns relevant roles and consolidates evidence without launching all roles on every event. Separate observed defects, heuristics, known planned work and insufficient telemetry. PM assesses the product's existing goals; it does not invent a new roadmap.

Acceptance G2: first controlled bank has at least 40 independently labeled cases covering historical/seeded defects, correct/no-change cases, stale environment, duplicate issue and instruction injection. Repeat representative cases three times to expose instability. Hidden expected answers stay outside worker context; ordinary product contracts/tests remain available. Every actionable finding has expectation, reproduction and evidence. This is a feasibility screen; expand to at least 100 cases per active review profile before broader unattended release and evaluate held-out results separately from tuning cases.

### Sprint 4 — Read-only shadow operation and dashboard

| Work package | Existing story / requirement | Hours | Owner |
|---|---|---:|---|
| GitHub release/CI artifact reuse and deployed-version checks | 005/006/011; FR-03/06/11 | 8 | Rashad |
| Desktop/mobile-width box-score and PDF evidence adapters | 011, web/data slice; FR-06/11 | 8 | Rashad |
| Minimal authenticated dashboard: product, findings, evidence, runs and cost | 012, MVP slice; FR-07 | 8 | Rashad |
| Durable digest, 14-day shadow review and adjudication | 013/017/018; FR-07/12 | 6 | Rashad |

Deliverable: 14 days of background read-only checks with live release evidence and internal results. Existing full suites are reused, not repeated nightly. Report detection latency, actionable precision, blocked runs and actual gross/marginal cash where available. Dashboard MVP is sufficient here; the full six-view platform is completed during expansion.

Acceptance G3: at least 95% scheduled completion within the agreed window; evidence complete on every actionable finding; at least 30 findings adjudicated across controlled/live work, with results reported separately; actionable precision at least 80%; zero forbidden writes. Controlled critical defect detection target at least 90%, with numerator/denominator shown. Small or inconclusive samples require additional observation. Shadow operation proves quality/liveness, not causal time savings, because founder still sees the usual workflow.

### Sprint 5 — Bounded repair preparation

| Work package | Existing story / requirement | Hours | Owner |
|---|---|---:|---|
| Work order schema, approved path/action categories and policy checks | 014; FR-08/09 | 8 | Rashad |
| Isolated branch, targeted tests and safe patch publication | 014; FR-09 | 14 | Rashad |
| Idempotent draft PR creation, stale-base reconciliation and evidence summary | 014; FR-09 | 8 | Rashad |
| Repetition, failed repair, protected-path and permission failure evaluation | 014/017; FR-08 | 4 | Rashad |

Deliverable: an approved isolated case produces a draft patch and PR-ready evidence. Activate external branch/PR writes only for the configured authorized repair categories and repositories; otherwise retain the patch as an internal artifact. No production credential, data repair, merge or deploy tools.

Acceptance G4: forbidden paths/actions are denied by the tool boundary; stale SHA cannot be published as current; retries cannot duplicate PRs; initial repair attempts include failure cases and remain within limits. First test cases are isolated and cannot affect real athletes or live games.

### Sprint 6 — Independent validation and follow-up

| Work package | Existing story / requirement | Hours | Owner |
|---|---|---:|---|
| Independent reviewer checkout and original-failure regression validation | 015; FR-09 | 10 | Rashad |
| Approved release tracking and immediate/24–72 hour behavior checks | 016; FR-10 | 8 | Rashad |
| Outcome states, pending deployment, blocked evidence and insufficient data | 016/012; FR-07/10/13 | 6 | Rashad |
| Freeze comparison definitions, versions and task allocation; readiness review | 002/017/018; FR-08/12 | 6 | Rashad |

Deliverable: finding → patch → independent verdict → human-approved release → verified deployed behavior. Agent review and human acceptance are distinct; a PR passing CI is not automatically a successful deployed outcome.

Acceptance G5: reviewer rejects a patch that passes ordinary tests but fails the original reproduction; missing tests return blocked; post-release evidence references the deployed revision. Controlled repair evaluation must justify enabling the live trial. Comparison protocol is registered before Sprint 7. Insufficient eligible live repairs do not prevent read-only comparison, but cannot support repair-performance claims.

### Sprint 7 — Live comparison, weeks 1–2

| Work package | Existing story / requirement | Hours | Owner |
|---|---|---:|---|
| Operate trial and adjudicate findings/repairs across both arms | 017/018; FR-08/12 | 8 | Rashad |
| Reconcile founder time, retries, provider usage and runner costs | 002/004/017; FR-08 | 6 | Rashad |
| Check matching, sample integrity, failures and contamination | 017; FR-08 | 4 | Rashad |

Deliverable: interim scorecard and complete task-level logs. Avoid feature/model/prompt changes during the trial; emergency changes create a versioned cohort rather than being silently pooled. Do not start Recruiting/mobile integration during the comparison: doing so would confound platform maintenance time and product outcomes.

Acceptance G6: each task has arm, task class, source revision, start/end, founder-active time, quality verdict and all attributable spend. Failures remain in the assigned arm's denominator. Unchanged cases are included. No early success declaration from a favorable first week.

### Sprint 8 — Live comparison, weeks 3–4 and decision

| Work package | Existing story / requirement | Hours | Owner |
|---|---|---:|---|
| Complete trial and final human adjudication | 017/018; FR-08/12 | 8 | Rashad |
| Analyze matched task types, uncertainty, cash and net time savings | 002/017; FR-08 | 6 | Rashad |
| Publish go/extend/restrict/stop decision and recalibrated backlog | 018; FR-12 | 4 | Rashad |

Deliverable: a decision report with raw denominators and cost/time distributions. Aim for at least 20 eligible tasks per arm, spread across review categories, and at least 20 repair attempts before quoting repair acceptance. If four weeks does not provide the volume, extend measurement; do not manufacture production defects or inflate repeated evaluations into independent live tasks. These are initial decision sample targets, not a statistical power calculation.

Acceptance G7: target at least 30% lower net coordination time for comparable scope, at least 80% actionable finding precision, at least 60% accepted independently validated repairs when enough attempts exist, at least 95% due-run completion, zero forbidden writes. Report absolute hours and uncertainty; if the evidence is inconclusive, extend or retain a narrower read-only service. Founder decides whether measured value warrants expansion.

### Sprint 9 — Initiated Recruiting integration (conditional, superseded)

The detailed [Initiated Recruiting R1–R6 plan](initiated-recruiting/sprint-plan.md) supersedes this provisional 30-hour Recruiting slice. Use that plan for implementation and measurement; the table below remains as the original milestone context and its hours must not be added to R1–R6.

| Work package | Existing story / requirement | Hours | Owner |
|---|---|---:|---|
| Recruiting manifest, current environments, approved aggregate metrics | 001/005/006, Recruiting slice; FR-01/03/11 | 8 | Rashad |
| Profile claim, verified-coach Terminal and discovery/board fixtures | 010; FR-06/11 | 12 | Rashad |
| Product-specific PM/design rubrics and auth-mode validity checks | 007/009/010; FR-04/08/13 | 6 | Rashad |
| Cross-product isolation, dashboard selection and adapter acceptance | 012/017; FR-07/08 | 4 | Rashad |

Deliverable: Recruiting uses the existing service with independent permissions and evidence. Verify normal auth and real test roles, with development mock-admin bypass disabled for access checks. Reuse release CI; no Actions cron or real customer messages. Begin read-only onboarding rather than assuming HoopTrace repair permissions transfer.

Acceptance G8: all three agreed journeys produce correct verified/blocked results, known flakes are classified, and neither product can read or mutate the other's private context. Actual onboarding time/cost is compared with the 16–32 hour pre-reserve forecast.

### Sprint 10 — Mobile evidence, hardening and wider-release readiness (conditional)

| Work package | Existing story / requirement | Hours | Owner |
|---|---|---:|---|
| HoopTrace Android/iOS CI evidence adapters and targeted parity fixtures | 011, mobile slice; FR-06/11 | 12 | Rashad |
| Complete dashboard views, product switches and validated context handling | 012/007; FR-07/08 | 6 | Rashad |
| Restore rehearsal, retention, missed-run/auth recovery and runbooks | 018; FR-08/12 | 8 | Rashad |
| Expand held-out evals and publish wider-release acceptance results | 017; FR-08 | 4 | Rashad |

Deliverable: operational two-product service with mobile evidence integrated into existing approved validation cadence. This does not promise new mobile capture features or autonomous device testing. Physical-device acceptance remains a human step. Use already available evaluable cases to expand the evaluation bank; authoring many new ground-truth cases is additional effort if required.

Acceptance G9: deployment/CI provenance is correct; targeted mobile evidence does not introduce redundant costly runs; restore and stop/resume succeed; owner runbook is usable; per-profile quality and access gates pass. If full evaluation coverage or mobile toolchain stabilization exceeds capacity, schedule Sprint 11 instead of waiving it. Broader two-product operation then has its own 30-day follow-up before further portfolio expansion.

## 4. Measurement protocol

Measure two different questions. Controlled tests establish whether the agent detects/repairs known conditions. Live allocation estimates whether it reduces coordination effort at comparable quality. Synthetic case repetition is not user traffic and is not extra independent live tasks.

Current-workflow arm: founder's real existing workflow, including current AI tools. Cloud-assisted arm: service collects evidence, routes roles and prepares findings/repairs; founder records review and correction time. Predefine eligible tasks and randomize within task class/estimated difficulty. Reserve critical production incidents for the normal workflow and report them outside trial; do not delay urgent work to preserve randomization.

Limit contamination: allocate related releases/findings together where one fix would inform another task; keep review evidence in isolated arm records until each assigned task is complete. A founder cannot be blinded to the workflow, so use deterministic outcome checks and a frozen human acceptance rubric. Keep review-level and repair-level measurements separate and compare like-for-like scope.

Record per task: category, assigned arm, source/deployed revision, prompt/model versions, evidence, verdict, founder context/check-in/review/correction minutes, implementation minutes, elapsed time, tokens, tool costs, runner minutes, retries, final patch/deployed status, and duplicate/blocked reason. Define completion before the run. Count failures and rejected outputs, not just successful tasks.

Net coordination benefit = comparable current-workflow coordination time − cloud-assisted coordination/review/correction time − attributable platform operations time. Track common experiment adjudication overhead separately and disclose it; ongoing production human-review cost belongs to the cloud-assisted arm. Build/setup time is a separate investment, never monthly savings. Additional agent-generated work without a comparable task is useful-throughput evidence, not claimed saved time.

Report medians and total active hours, per-class results, actionable precision (confirmed nonduplicate findings / proposed actionable findings), held-out recall (known defects caught / known defects), repair acceptance (accepted independently validated patches / all assigned repair attempts), latency, cost per completed review and accepted repair, and scheduled completion. Show counts and uncertainty; no unsupported causal revenue or retention claims.

## 5. Dependencies, ownership and operating cadence

Rashad is accountable for every sprint and resolves access/product decisions. Agents assist implementation and later act as runtime roles; they do not create additional human delivery capacity. A separate human reviewer may join if available, but is not assumed in the estimate. External platform/auth delays are logged with owner and next action rather than being hidden as agent failures.

Hard dependencies: G0 before cloud review claims; G1 before unattended operation; G2/G3 before repair activation; G4/G5 before repair comparison; G7 before second-product/mobile expansion. Draft work may progress independently only when it does not bypass the gate or distort live measurement.

Lightweight cadence within planned hours: 30-minute planning and 30-minute demo per sprint, 15-minute retrospective and 15-minute refinement; asynchronous status record twice weekly. No daily founder meeting. Review acceptance, actual effort, cost, blockers and reserve use at sprint end. New requests replace lower-priority scope rather than being added silently.

Top risks: stale environments, weak/low-volume comparison samples, incomplete independent expected outcomes, agent repair false confidence, mobile toolchain flakes, and credential access delay. Mitigations are assigned in Sprints 1/3/4/6/8/10 respectively; Rashad owns each. A blocking access or reproducibility problem takes priority over launching additional agent roles.

## 6. Calendar and cash boundaries

At assumed 20 focused hours/week: small proof by end of Sprint 1; read-only platform by end of Sprint 4; repair loop by end of Sprint 6; measured HoopTrace decision by end of Sprint 8. Recruiting then follows its separate [R1–R6 plan](initiated-recruiting/sprint-plan.md), with observation extended if task volume is low; the old Sprint 9 Recruiting milestone is superseded. HoopTrace mobile/hardening in Sprint 10 remains conditional and is a separate workstream that must be scheduled against the same founder capacity rather than assumed concurrent. Full-platform high estimate can add sprints and observation extensions. At 10 hours/week, halve the per-sprint work commitment and split implementation sprints; four-week observation still requires enough tasks. At 30 hours/week, replan dependencies rather than promising every gate finishes 1.5× faster.

Cash planning stays scenario-based: the shared two-product model is $96/month read-only or $357/month balanced before reserve. The later [Recruiting marginal model](initiated-recruiting/cost-analysis.md) estimates product-specific usage on the existing platform; these totals are not additive. Pilot workload is narrower and must be metered; no fixed ceiling or two-product bill is asserted for each sprint. Track setup consumption separately from ongoing inference/CI and show existing subscription cash unchanged. Reforecast at shared Sprints 2/4/8 and Recruiting R1/R4/R6 from actuals. No cash limit is silently approved by this schedule.
