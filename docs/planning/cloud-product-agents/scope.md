# PRD-CPA-001 — Cloud product review and improvement

Date: 2026-09-27. Owner and initial decision maker: Rashad Cureton. Proposed name is descriptive, not a branding decision. Version 0.1, planning only.

## 1. Problem and desired behavior

Product maintenance currently requires people to initiate reviews, gather context, check tests, inspect UI, remind implementers, and determine whether fixes worked. Cure already has specialist agent instructions, test suites, analytics taxonomies, and release workflows. These resources lack one durable cross-product execution and evidence service.

The service monitors product signals, performs scheduled and event-triggered reviews, prioritizes verified findings, prepares bounded changes, and verifies behavior and product outcomes. A dashboard shows what changed, what evidence supports a finding, what is blocked, and which decisions need the founder.

Examples grounded in repository state, not newly verified production defects:

- HoopTrace's 2026-09-25 STATE records web/iOS/Android parity work, production/dev divergence, box-score fixtures, and device-specific validation needs. A review must know which release it evaluated and which platform work is deliberately unfinished.
- Initiated Recruiting's STATE records coach verification and program binding, Terminal data freshness, and follow-ups involving scheduled functions. These are suitable review targets, but stale notes must not become new duplicate bug tickets.
- Initiated Recruiting's E2E workflow describes known timing instability. A failed test must be classified as a product regression, infrastructure failure, known test defect, or insufficient evidence.

## 2. Goals and success metrics

The founder retains product ownership. The service reduces coordination and prepares decisions using reproducible evidence. The first measured pilot is HoopTrace's web box score, PDF and game-data consistency; Initiated Recruiting and mobile evidence follow the pilot decision. See [sprint-plan.md](sprint-plan.md) for current sequencing; two-product cost estimates remain the eventual release scope.

| Metric | Baseline | Pilot / release target |
|---|---|---|
| Manual coordination hours | Measure by product for 7–14 days | At least 30% reduction after accounting for agent review and maintenance time |
| Actionable finding precision | Unknown | At least 80% of first 30 adjudicated findings are reproducible, relevant, and not duplicates |
| Detection recall on seeded cases | Unknown | At least 90% of 20 known critical journey defects; report denominator and uncertainty |
| Scheduled review completion | Unknown | At least 95% within 2 hours of scheduled due time during pilot |
| Event triage latency | Unknown | 95th percentile under 15 minutes, excluding provider outages |
| Reviewed release coverage | Inventory first | Every configured release has a recorded verdict or explicit blocked/unknown status |
| Evidence completeness | Unknown | 100% of actionable findings have product, environment, release, expectation, evidence, and reproduction |
| Repair success | Unknown | At least 60% of first 20 repair attempts produce a PR accepted by human review and targeted validation |
| Permission violations | None expected | Zero cross-product access or forbidden production writes in adversarial evaluations |
| Unit economics | Model only | Measure dollars per completed review and accepted improvement; evaluate against time saved |

These are proposed acceptance targets, not claims about current agent performance. Small samples are provisional. No agent may infer product-market fit, causality, revenue uplift, or representative user sentiment from code inspection alone.

## 3. Users and dashboard flow

Initial users are founder/product owner and engineering reviewers. No customer-facing agent interactions are in scope.

Founder opens portfolio overview → chooses product → sees release-aware health summary → opens finding evidence → accepts/defer/rejects priority → reviews prepared PR when available → sees validation and post-release follow-up.

Daily digest: material changes, urgent verified findings, blocked work, decisions required, and cost. Weekly review: recurring friction, outcome hypotheses, prioritized work, metric coverage, and previous changes' measured results. Unchanged findings do not generate repeated alerts.

Dashboard screens: portfolio overview; product health and release coverage; finding detail; work order and PR evidence; run/cost/liveness history; policy configuration. Display unknown and blocked states explicitly rather than synthesizing a single green health score.

## 4. Roles and boundaries

| Role | Inputs | Responsibilities | Deliverables | Boundaries |
|---|---|---|---|---|
| Coordinator | Config, events, due schedules, task state | Route reviews, lease tasks, enforce caps, aggregate results, detect missed runs | Run records, work routing, digest | Policy is enforced by code; the coordinator cannot grant itself tools |
| Product manager | Goals, aggregated analytics, feedback, issue state, release history | Check instrumentation, assess impact, rank findings, define hypotheses and acceptance criteria | Evidence-backed priorities and experiment briefs | Cannot autonomously redefine target audience, roadmap, pricing, or success metrics |
| Product design | Rendered UI, screenshots, design tokens, journeys, accessibility results | Assess discoverability, states, layout, keyboard/touch behavior, consistency | Annotated evidence and bounded design proposals | Heuristic review is labeled; cannot claim to replace user interviews |
| Engineering investigator / implementer | Finding, repo snapshot, relevant skills, tests | Reproduce, identify cause, estimate scope; later prepare branch and draft PR | Reproduction, patch, targeted tests, rollback note | No unrestricted repository writes or production access |
| QA / independent reviewer | Original reproduction, expected behavior, patch, test artifacts | Challenge diagnosis, rerun original case, check regression boundaries | Verified/rejected/blocked verdict with evidence | Cannot approve solely because implementer claims success |

Keep role prompts separate but allow one shared worker runtime. Invoke only relevant roles for each event. Product, design, and code assessment can independently inspect the same immutable release; implementation depends on a verified work order. Use a different provider for high-risk repair review when available, without treating provider diversity as proof.

Reuse existing product-analyst, roadmap-strategist, ux-researcher, accessibility-checker, qa-engineer, code-reviewer, pr-reviewer, api-validator, and relevant skills as versioned instruction inputs. Their current local tool bindings, hooks, and memory settings are not cloud security controls.

## 5. Requirements and priority

| ID | Priority | Requirement | Epic |
|---|---|---|---|
| FR-01 | Must | Register product goals, environments, critical journeys, owner, policies, and approved instruction versions | EPIC-CPA-01 |
| FR-02 | Must | Ingest authenticated release/CI events and GCP schedules; deduplicate and lease durable tasks | EPIC-CPA-02 |
| FR-03 | Must | Read GitHub and aggregated analytics; ingest approved feedback and monitoring evidence | EPIC-CPA-03 |
| FR-04 | Must | Run product, design, engineering, and QA review profiles against identified releases | EPIC-CPA-04 |
| FR-05 | Must | Produce structured findings with evidence and deduplicate against existing issues | EPIC-CPA-04 |
| FR-06 | Must | Execute isolated synthetic journeys and reuse existing CI artifacts | EPIC-CPA-05 |
| FR-07 | Must | Show findings, run history, decisions, release coverage, and costs in an internal dashboard | EPIC-CPA-06 |
| FR-08 | Must | Enforce budgets, scoped identity, audit trail, policy gates, stop conditions, and kill switches | EPIC-CPA-02/08 |
| FR-09 | Must for release; after pilot | Prepare scoped branches and draft PRs with independent validation | EPIC-CPA-07 |
| FR-10 | Must for release | Check deployed behavior and schedule outcome follow-ups after approved releases | EPIC-CPA-07 |
| FR-11 | Must | Integrate both products' agreed web/data journeys; add mobile evidence with existing CI policy | EPIC-CPA-03/05 |
| FR-12 | Must | Record unknown/blocked states, alert on missed execution, replay failure cases | EPIC-CPA-08 |
| FR-13 | Should | Track recurring issues and experiments with minimum data checks | EPIC-CPA-04 |
| FR-14 | Could, later | Formal A2A interoperability for external independently hosted agents | Deferred |
| FR-15 | Could, later | Additional products via product manifest and connector adapters | Deferred |

Out of initial release: automatic production deployment/merge, live data repair, credential or billing changes, migrations, autonomous dependency upgrades, customer outreach, unsolicited social publishing, purchasing services, a general agent marketplace, and a new analytics platform. Human user research remains separate. No synthetic journey may contact real athletes/coaches or charge a real payment method.

## 6. Initial product integration contracts

### Initiated Recruiting

Use current repository state and runtime manifests to resolve environment IDs; do not copy a stale historical URL from a package script. Verify the real auth mode: its AGENTS.md documents a development mock-admin bypass. Role tests must use a production-like build with bypass disabled, real test identities, and Firebase emulators or approved staging.

| Journey / review | Objective and evidence | Cadence |
|---|---|---|
| Profile claim → authenticated dashboard | Approved seeded athlete claims profile; ownership persists; failures are actionable | Post-deploy targeted smoke; daily lightweight synthetic |
| Verified coach → Terminal | Unverified identity is denied; verified identity with correct program binding sees authorized data | Post-deploy in staging/emulator; weekly targeted access review |
| Athlete discovery → detail → board | Search/filter works, public profile loads, board operation succeeds under intended role | Post-deploy smoke; weekly design review |
| Data health and program freshness | Consume integrity/board-parity reports; check compute freshness and binding mismatch summaries | Daily aggregate read; after relevant data-pipeline events |
| Scouting funnel | Use documented GA4 events, completion denominator, and error categories | Weekly PM review; daily anomaly check when volume qualifies |
| Design / accessibility | Mobile/desktop screens, loading/error/empty states, keyboard and automated accessibility checks | Weekly and relevant UI release |

Do not turn existing workflows into scheduled GitHub Actions: the repository explicitly prohibits Actions cron. Consume existing release-run results; independent small synthetic probes execute in GCP. Expand full-suite frequency only through an explicit product policy decision. Production monitoring reads stay outside untrusted PR execution.

### HoopTrace / StatLedger

| Journey / review | Objective and evidence | Cadence |
|---|---|---|
| Sign up → organization → game → first stat | Use canonical funnel names; measure elapsed time only where instrumentation is verified | Weekly PM review; release synthetic on applicable platform |
| Capture → undo → offline → reconnect | Golden events replay to expected ledger/projection; reconnect adds no duplicate stats | Targeted backend fixtures per relevant release; device/emulator at approved gates |
| Game → public box score → PDF | Same fixture produces consistent stats and identity across supported outputs | Relevant release; daily small read-only public fixture smoke |
| Cross-platform parity | Compare only implemented/required behavior; distinguish deliberate pending work from regression | Weekly report; changes to shared contracts |
| Deployment freshness | Record source commit, deployed web/backend version, test environment freshness, and fixture version | Each review; blocked if environment provenance is unavailable |
| Tablet and mobile UX | Landscape/portrait, touch targets, logos, overflow, empty/error states | Weekly web design; mobile at approved CI/manual device gates |

Preserve immutable player IDs, compensating undo events, and published-names/opt-out decisions. Do not redefine public athlete names as a defect. Live data corrections remain owner-controlled. Preserve existing promotion-based iOS validation and Android run constraints. Cloud Run is not an iOS simulator host; macOS work uses existing approved CI and physical-device acceptance remains human.

## 7. Cadence, autonomy, and escalation

Daily: lightweight read-only probes, telemetry freshness, issue deduplication, exception digest. Weekly: PM and design review plus selected deep investigation. Event-driven: release evidence intake, targeted UI/contracts, failure triage. Monthly: agent evaluation, credentials/webhooks/scheduler liveness, unit economics, retention audit.

| Level | Enabled actions | Promotion gate |
|---|---|---|
| A0 shadow | Read approved sources, run synthetic staging checks, write internal reports | Evidence accuracy and scheduling gates pass |
| A1 report | Maintain internal findings; optionally write designated bot-owned GitHub issues/checks | Scoped write policy and deduplication validated |
| A2 repair | Branch in isolated checkout, change allowlisted paths, submit draft PR | At least 30 adjudicated findings and repair permission evaluation; explicit scoped authorization |
| A3 restricted merge | Potential future allowlisted low-risk merge through CI | Separate future decision; excluded from this estimate |

Enabling A1/A2 is a configured authorization step at implementation time. This planning request authorizes preparing these documents, not deployment, publishing findings externally, or changing product code. Once a category is authorized, the system runs that category without asking on every task.

Critical verified findings enter the internal urgent queue immediately. Hypotheses enter the normal review queue. External messages require a configured authorized destination; initial release uses dashboard and digest artifacts, without adding an email/Slack vendor. Irreversible work is escalated with evidence and a prepared proposal. Repeated failure stops and returns a named blocker.

## 8. Outcomes and prioritization

Finding classes: defect, data inconsistency, UX heuristic, product hypothesis, instrumentation gap, flaky test, infrastructure/authentication failure. Only reproduced defects and verified invariants can block a quality gate. A design preference or statistically weak funnel change cannot.

PM ranks by critical-journey impact, affected users/volume, confidence, effort, and product goals. Include unknown denominators; no fabricated RICE reach numbers. Initial repair capacity is bounded by scenario, not an unlimited backlog drain.

Outcome windows: behavior check immediately after release, operational check at 24–72 hours, product metric review at 7–14 days or sufficient sample. Use same event definitions and cohorts; report confounding releases and seasonality. At fewer than 50 relevant journey starts or fewer than 10 failures, report insufficient evidence for an automatic funnel anomaly conclusion. These are conservative screening thresholds, not statistical significance tests or experiment power calculations. Experiments require a separate power/sample design before launch.

## 9. Release phases and exit gates

1. **Discovery and baseline:** current test/environment inventory, validated access, observed manual time, agreed journeys and product goals. Exit: all credentials and tests resolve to correct environment, first baseline report is reproducible.
2. **Read-only pilot:** HoopTrace web box score, PDF and game-data evidence; durable task service, reviews, internal dashboard and spend records. Run 14 days. Exit: completion, evidence, precision, permission and missed-run gates pass.
3. **Measured HoopTrace repair pilot:** bounded repair branches/draft PRs, independent review and outcome tracking. After readiness gates, compare eligible current-workflow and cloud-assisted tasks for four weeks; extend if samples are insufficient. Exit: accepted repair and net time-saved targets pass, no forbidden side effects, measured spend reported.
4. **Two-product expansion:** add Initiated Recruiting's agreed journeys and HoopTrace mobile artifact integration after the pilot decision; run a separate 30-day operating follow-up. Tune budgets and add further products only after onboarding cost and marginal operating cost are measured. Formal A2A and automatic merges remain separate decisions.

Every phase has a product-level feature switch, a global stop switch, a reversible instruction/model version, and preserved run history. Rollback disables scheduling or repair permissions; it does not erase findings or alter product production state.

## 10. Unresolved implementation facts

Verify actual analytics export availability and account permissions; active cloud regions; current plan allowances and provider API access; whether staging is current; existing suite reproducibility and runtime; selected test identities; exact owner-approved repair paths; baseline check-in time; and dashboard identity integration. These affect onboarding and cost. Model numbers remain assumptions until a pilot meters them.
