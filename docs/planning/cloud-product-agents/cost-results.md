# Generated cost results

Pricing check date: 2026-09-27. USD; incremental platform cash only.
No free-tier, cache, batch, plan allowances, or subscription credits deducted. Ancillary lines are planning allowances.
Monthly tokens/worker runtime include 30% retry allowance; planning reserve adds 25% headroom.

| Scenario | Products | LLM/month | Modeled cash/month | With reserve/month | Founder hours/month | Repair attempts |
|---|---:|---:|---:|---:|---:|---:|
| lean_readonly | 2 | $54.87 | $96.12 | $120.15 | 6.0–10.0 | 0 |
| balanced | 2 | $254.57 | $356.67 | $445.84 | 12.8–21.6 | 16 |
| intensive | 2 | $833.66 | $1,114.84 | $1,393.55 | 30.0–56.0 | 60 |

## Monthly line items

| Item | lean_readonly | balanced | intensive |
|---|---:|---:|---:|
| LLM: triage | $0.27 | $1.33 | $5.30 |
| LLM: product_review | $3.12 | $23.40 | $46.80 |
| LLM: design_review | $4.16 | $12.48 | $31.20 |
| LLM: engineering_review | $24.96 | $74.88 | $249.60 |
| LLM: deep_investigation | $15.08 | $30.16 | $90.48 |
| LLM: repair_bundle | $0.00 | $97.76 | $366.60 |
| LLM: release_followup | $7.28 | $14.56 | $43.68 |
| Cloud Run: agent workers | $1.78 | $8.03 | $27.41 |
| Cloud Run: browser probes | $0.82 | $2.47 | $8.24 |
| Cloud Run: control API | $0.03 | $0.11 | $0.45 |
| Firestore: reads | $0.07 | $0.30 | $1.20 |
| Firestore: writes | $0.07 | $0.27 | $0.90 |
| Firestore: state storage | $0.15 | $0.45 | $1.20 |
| Storage: retained evidence | $0.50 | $1.60 | $5.00 |
| Storage: evidence egress | $0.60 | $2.40 | $9.60 |
| Logging: ingestion | $2.50 | $7.50 | $20.00 |
| Pub/Sub: throughput | $0.01 | $0.04 | $0.16 |
| Scheduler: shared jobs | $0.30 | $0.60 | $1.20 |
| Secret Manager: versions | $0.36 | $0.60 | $1.20 |
| Secret Manager: access | $0.03 | $0.09 | $0.30 |
| GitHub: incremental Linux CI | $3.60 | $10.80 | $28.80 |
| GitHub: incremental macOS CI | $9.92 | $19.84 | $59.52 |
| Search: optional research calls | $0.50 | $2.00 | $6.00 |
| Allowance: artifact_operations_registry_backups | $10.00 | $20.00 | $50.00 |
| Allowance: analytics_queries_and_monitoring | $10.00 | $25.00 | $60.00 |
| Existing subscriptions: incremental | $0.00 | $0.00 | $0.00 |

## Founder build effort

Two-product initial build. Component estimates include implementation and targeted testing; 20% time reserve added once.

| Stage | Hours including reserve | Weeks at 20 active hours/week, before observation gates | Incremental build cash allowance |
|---|---:|---:|---:|
| pilot | 115.2–187.2 | 5.8–9.4 | $50.00–$150.00 |
| expansion | 134.4–244.8 | 6.7–12.2 | $100.00–$350.00 |
| full | 249.6–432.0 | 12.5–21.6 | $150.00–$500.00 |

Pilot observation: 2 weeks; expansion validation: about 4 weeks. Gates and access delays are additional calendar constraints.

## Twelve-month operating period after full launch

Includes full-build cash allowance once, plus 12 operating months; excludes existing product bills and subscriptions.

| Scenario | Incremental cash including build allowance | Cash envelope with operating reserve | Founder operating hours/year |
|---|---:|---:|---:|
| lean_readonly | $1,303.39–$1,653.39 | $1,591.74–$1,941.74 | 72.0–120.0 |
| balanced | $4,430.02–$4,780.02 | $5,500.03–$5,850.03 | 153.6–259.2 |
| intensive | $13,528.05–$13,878.05 | $16,872.56–$17,222.56 | 360.0–672.0 |

Founder build hours are additional to operating hours. For a pilot-only choice, use the pilot cash allowance rather than the full-build allowance.

## Token and retry sensitivity

| Scenario | Base modeled cash | 2× tokens | 5× tokens | No retry overhead | 2× billed attempts/runtime |
|---|---:|---:|---:|---:|---:|
| lean_readonly | $96.12 | $150.98 | $315.58 | $82.85 | $127.06 |
| balanced | $356.67 | $611.23 | $1,374.93 | $295.50 | $499.40 |
| intensive | $1,114.84 | $1,948.50 | $4,449.49 | $914.23 | $1,582.93 |

2×/5× token sensitivity changes LLM tokens only; retry sensitivity changes LLM usage and worker/browser runtime. CI minutes and ancillary allowances are already budgeted totals.

## Portfolio scale — balanced profile

| Products | Modeled monthly cash | With reserve | Monthly founder hours |
|---|---:|---:|---:|
| 2 | $356.67 | $445.84 | 12.8–21.6 |
| 5 | $890.77 | $1,113.46 | 32.0–54.0 |
| 10 | $1,780.94 | $2,226.18 | 64.0–108.0 |

Scale assumes identical per-product workloads and founder allocations; only shared Scheduler jobs remain fixed. Not a capacity guarantee. New product onboarding is 16–32 active hours each plus 20% time reserve.

## Time payback — balanced profile

Illustrative baseline coordination hours only; do not count development acceleration or avoided incidents without observation.

| Manual coordination baseline/month | Net hours saved using midpoint operating time | Build time payback at midpoint full-build hours | Cash envelope break-even value per saved hour |
|---|---:|---:|---:|
| 20 | 2.8 | 121.7 months | $159.23 |
| 40 | 22.8 | 14.9 months | $19.55 |
| 60 | 42.8 | 8.0 months | $10.42 |

Savings are conditional assumptions, not forecasts. Founder time has no cash salary assigned. At optional $100/$150/$200 per hour, value = saved hours × rate minus operating cash; this is opportunity value, not booked cash savings.

## Repair unit economics and managed-runtime comparison

Repair-bundle LLM allowance per attempt: $6.11; at assumed 60% acceptance: $10.18 LLM per accepted repair. This excludes CI, human review and shared platform overhead.
Balanced assumed accepted repairs/month: 9.6; acceptance is a pilot target, not measured throughput.
Replacing only modeled agent-worker compute with managed sessions at $0.08/session-hour changes balanced cash by -$3.97/month, if runtime and tokens are identical. Browser/CI/control costs remain. Validate managed runtime feature/access fit separately.
