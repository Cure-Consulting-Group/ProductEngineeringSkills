# Initiated Recruiting — generated incremental cost results

Pricing assumption check: 2026-09-28. USD. One product's marginal usage on the existing shared platform.
No second coordinator, scheduler jobs, dashboard, macOS CI, existing subscriptions or existing product hosting is charged here.
Usage includes 30% retry/token overhead from the shared model; planning envelope adds 25% unused cash headroom.

| Scenario | LLM/month | Modeled incremental cash/month | With reserve/month | Founder operating hours/month | Repair attempts/month |
|---|---:|---:|---:|---:|---:|
| lean_readonly | $28.94 | $49.07 | $61.33 | 3.0–7.0 | 0 |
| balanced | $126.40 | $173.01 | $216.27 | 9.0–17.0 | 8 |
| intensive | $376.08 | $503.61 | $629.51 | 19.0–37.0 | 24 |

## Monthly line items

| Item | lean_readonly | balanced | intensive |
|---|---:|---:|---:|
| LLM: triage | $0.13 | $0.66 | $1.99 |
| LLM: product_review | $2.34 | $9.36 | $28.08 |
| LLM: design_review | $2.08 | $6.24 | $15.60 |
| LLM: engineering_review | $12.48 | $37.44 | $112.32 |
| LLM: deep_investigation | $7.54 | $15.08 | $45.24 |
| LLM: repair_bundle | $0.00 | $48.88 | $146.64 |
| LLM: release_followup | $4.37 | $8.74 | $26.21 |
| Cloud Run: agent workers | $0.94 | $4.01 | $11.90 |
| Cloud Run: browser probes | $0.82 | $1.65 | $4.94 |
| Cloud Run: control API | $0.02 | $0.05 | $0.20 |
| Firestore: reads | $0.03 | $0.09 | $0.27 |
| Firestore: writes | $0.03 | $0.09 | $0.27 |
| Firestore: state storage | $0.07 | $0.22 | $0.60 |
| Storage: retained evidence | $0.30 | $0.80 | $2.40 |
| Storage: evidence egress | $0.24 | $0.72 | $2.16 |
| Logging: ingestion | $1.00 | $3.00 | $9.00 |
| Pub/Sub: throughput | $0.00 | $0.01 | $0.04 |
| Scheduler: shared jobs | $0.00 | $0.00 | $0.00 |
| Secret Manager: versions | $0.12 | $0.24 | $0.36 |
| Secret Manager: access | $0.01 | $0.03 | $0.09 |
| GitHub: incremental Linux CI | $1.44 | $5.40 | $14.40 |
| GitHub: incremental macOS CI | $0.00 | $0.00 | $0.00 |
| Search: optional research calls | $0.10 | $0.30 | $0.90 |
| Allowance: artifact_operations_registry_backups | $5.00 | $10.00 | $30.00 |
| Allowance: analytics_queries_and_monitoring | $10.00 | $20.00 | $50.00 |
| Existing subscriptions: incremental | $0.00 | $0.00 | $0.00 |

## Build investment

Story sum: 82–148 founder-active hours; with one 20% reserve: 98.4–177.6 hours.
At 20 focused hours/week this is 4.9–8.9 equivalent build weeks, before fixed observation windows and access delays.
Incremental setup/test cash allowance: $50.00–$150.00. Existing subscription invoices are unchanged baseline cash.

## Twelve operating months after integration, plus one setup allowance

| Scenario | Modeled incremental cash incl. setup | Envelope incl. operating reserve and setup | Founder operating hours/year |
|---|---:|---:|---:|
| lean_readonly | $638.80–$738.80 | $786.00–$886.00 | 36.0–84.0 |
| balanced | $2,126.16–$2,226.16 | $2,645.20–$2,745.20 | 108.0–204.0 |
| intensive | $6,093.31–$6,193.31 | $7,604.14–$7,704.14 | 228.0–444.0 |

## Token and retry sensitivity

| Scenario | Base cash/month | 2× tokens | 5× tokens | No retry overhead | 2× billed attempts/runtime |
|---|---:|---:|---:|---:|---:|
| lean_readonly | $49.07 | $78.01 | $164.83 | $41.98 | $65.60 |
| balanced | $173.01 | $299.41 | $678.61 | $142.54 | $244.12 |
| intensive | $503.61 | $879.69 | $2,007.92 | $412.94 | $715.18 |

Token variants change LLM tokens only. Retry variants change LLM and Cloud Run worker/browser time. CI and allowances are already monthly totals.

## Time payback illustration — balanced profile

Assumes the same current-workflow task scope and balanced midpoint founder operating time. Values are scenarios, not measured savings.

| Current coordination hours/month | Net hours saved/month | Build-time payback | Cash envelope per saved hour |
|---|---:|---:|---:|
| 12 | -1.0 | No time payback | n/a |
| 25 | 12.0 | 11.5 months | $18.02 |
| 40 | 27.0 | 5.1 months | $8.01 |

Founder build hours are additional to operating hours. Cash per saved hour is an incremental usage hurdle, not an assigned wage. Repair acceptance and product outcomes are not inferred from modeled attempts.
