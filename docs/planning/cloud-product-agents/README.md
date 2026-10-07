# Cloud product agents — scope and cost package

Prepared 2026-09-27 for Cure Consulting Group. Status: proposed internal platform; no infrastructure or automation has been deployed.

Build one shared cloud service that reviews HoopTrace / StatLedger and Initiated Recruiting, creates evidence-backed work, prepares scoped fixes, and verifies outcomes. Preserve each product's goals and existing release controls. Start with HoopTrace's web box score, PDF and game-data consistency; measure its review/repair pilot, then add Initiated Recruiting and mobile evidence integration.

User preferences: model usage scenarios without a fixed spending ceiling; show founder time separately from cash; assume existing AI subscriptions remain unchanged. Cloud API usage is additional consumption. This is a planning estimate, not a vendor quote or a committed delivery date.

## Package

| Artifact | Purpose |
|---|---|
| [scope.md](scope.md) | Product requirements, role boundaries, product-specific checks, autonomy, metrics, rollout |
| [architecture.md](architecture.md) | Execution, data contracts, access, reliability, agent design, operations |
| [backlog.md](backlog.md) | Traceable epics, stories, acceptance criteria, effort, delivery gates |
| [sprint-plan.md](sprint-plan.md) | HoopTrace-first sprint commitments, capacity, measurement protocol and conditional expansion |
| [cost-analysis.md](cost-analysis.md) | Pricing basis, assumptions, monthly scenarios, build effort, alternatives, economics |
| [assumptions.json](assumptions.json) | Editable rates, workloads, effort, founder oversight, and sensitivity inputs |
| [cost_model.py](cost_model.py) | Offline calculator; recalculates estimates without cloud access |
| [cost-results.md](cost-results.md) | Generated totals, sensitivities, founder hours, and payback |
| [cost-breakdown.csv](cost-breakdown.csv) | Spreadsheet-ready monthly line items |
| [scenario-totals.csv](scenario-totals.csv) | Spreadsheet-ready scenario comparison |
| [Initiated Recruiting integration](initiated-recruiting/README.md) | Second-product scope, architecture, backlog, six-sprint plan and incremental cost model |

Recalculate from this repository:

```sh
python3 docs/planning/cloud-product-agents/cost_model.py
```

The calculator overwrites only its three generated reports in this directory. It does not create agents, access accounts, deploy services, or change product repositories.

## Recommendation

Implement a read-only pilot first. Prove reliable execution, useful findings, and lower founder coordination time before enabling repair branches. Use GCP schedules and short-lived workers; consume existing GitHub CI evidence instead of rerunning complete suites on a timer. Add scoped draft PRs only after their policy and validation gates pass.

Run HoopTrace read-only shadow reviews for 14 days, enable bounded repairs after their gates pass, then perform a four-week controlled live comparison. Expand to the second product and mobile evidence only after the measured decision; broader two-product operation gets its own 30-day follow-up. Keep roadmaps, production releases, migrations, customer messaging, and live data corrections under established human controls. The system should automatically gather evidence and prepare work; human interaction should concentrate on exceptions and ready-to-review changes.

The detailed [Initiated Recruiting plan](initiated-recruiting/README.md) replaces the provisional Recruiting-specific work in shared Sprint 9. Its cost model estimates Recruiting's marginal consumption on this platform; do not add it to the shared two-product scenario total as a second full platform charge.
