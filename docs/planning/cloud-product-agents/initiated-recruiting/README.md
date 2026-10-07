# Initiated Recruiting — cloud product-agent integration

Prepared 2026-09-28. Status: proposed; no new agent, connector, schedule or product code has been deployed. This is the **second-product integration** of the [shared Cure platform](../README.md), following the HoopTrace measurement decision. It does not create a second coordinator, queue, dashboard or cross-product cost center.

| Artifact | Purpose |
|---|---|
| [scope.md](scope.md) | Recruiting-specific journeys, success measures, autonomy and rollout |
| [architecture.md](architecture.md) | Product adapters, identities, events and evidence flow into the shared platform |
| [backlog.md](backlog.md) | Epics, stories, acceptance criteria and effort |
| [sprint-plan.md](sprint-plan.md) | Six two-week sprints at 20 focused founder hours/week, including a four-week comparison |
| [cost-analysis.md](cost-analysis.md) | Incremental-only costs, cash/time separation and measurement economics |
| [assumptions.json](assumptions.json) | Editable Recruiting workload and effort; inherits shared price/worker assumptions |
| [cost_model.py](cost_model.py) | Offline model for Recruiting's incremental usage |
| [cost-results.md](cost-results.md) | Generated scenario, sensitivity and labor-hour results |
| [cost-breakdown.csv](cost-breakdown.csv) | Spreadsheet-ready incremental line items |

Recalculate from this repository:

```sh
python3 docs/planning/cloud-product-agents/initiated-recruiting/cost_model.py
```

The script writes only the generated reports in this directory. It does not access Firebase, GitHub, analytics or payment accounts.

The first product slice is profile claim, coach verification/Terminal access, and discovery/recruiting board behavior. Later checks add data freshness, design, and analytics assessment. Authorization correctness and truthful product data outrank speculative funnel optimization. Synthetic tests use emulator/staging identities, while production analytics are read only and aggregated.
