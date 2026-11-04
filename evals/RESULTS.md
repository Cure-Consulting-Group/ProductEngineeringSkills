# Eval Results (generated — do not edit)

Latest sweep: `2026-11-04-0337` mode=`skill` source=`claude plugin eval` (plugin-evals/sweep.py)

| key (task\|backend\|arm) | pass rate | n | 95% CI | flaky |
|---|---|---|---|---|
| data-migration-firestore-backfill|claude|off | 92% | 3 | [0.37, 0.995] | ⚠️ |
| data-migration-firestore-backfill|claude|on | 100% | 3 | [0.438, 1] |  |
| legal-upl-guardrail|claude|off | 100% | 3 | [0.438, 1] |  |
| legal-upl-guardrail|claude|on | 100% | 3 | [0.438, 1] |  |
| nextjs-scaffold-notes-feature|claude|off | 67% | 3 | [0.208, 0.939] | ⚠️ |
| nextjs-scaffold-notes-feature|claude|on | 58% | 3 | [0.164, 0.909] | ⚠️ |
| public-sector-city-contract|claude|off | 50% | 3 | [0.125, 0.875] |  |
| public-sector-city-contract|claude|on | 42% | 3 | [0.091, 0.836] | ⚠️ |
| qsbs-compliance-two-regimes|claude|off | 67% | 3 | [0.208, 0.939] | ⚠️ |
| qsbs-compliance-two-regimes|claude|on | 75% | 3 | [0.256, 0.963] |  |
| route-legal-doctrine-bar-question|claude|off | 100% | 3 | [0.438, 1] |  |
| route-legal-doctrine-bar-question|claude|on | 100% | 3 | [0.438, 1] |  |
| route-legal-doctrine|claude|off | 100% | 3 | [0.438, 1] |  |
| route-legal-doctrine|claude|on | 100% | 3 | [0.438, 1] |  |
| route-legal-research|claude|off | 67% | 3 | [0.208, 0.939] | ⚠️ |
| route-legal-research|claude|on | 67% | 3 | [0.208, 0.939] | ⚠️ |
| route-security-review-prelaunch|claude|off | 100% | 3 | [0.438, 1] |  |
| route-security-review-prelaunch|claude|on | 100% | 3 | [0.438, 1] |  |
| security-review-nextjs-firebase|claude|off | 67% | 3 | [0.208, 0.939] | ⚠️ |
| security-review-nextjs-firebase|claude|on | 67% | 3 | [0.208, 0.939] | ⚠️ |

_Deltas require n≥3 per arm; single-rep results are directional only (t07, 2026-08-14)._
_`pass rate` here is the mean run score (fraction of scored graders passed); `on` = WITH plugin, `off` = W/OUT. `tool_used: Skill` graders are indicators, not scored, in two-arm runs._

## Skill on/off deltas

| skill | Δ pass rate | cases | min n/arm |
|---|---|---|---|
| qsbs-compliance | +8% | 1 | 3 |
| data-migration | +8% | 1 | 3 |
| legal-doctrine | +0% | 3 | 3 |
| security-review | +0% | 2 | 3 |
| legal-research | +0% | 2 | 3 |
| public-sector-contracting | -8% | 1 | 3 |
| nextjs-feature-scaffold | -8% | 1 | 3 |

### Δ≈0 (|Δ| < 5%) — T88 candidates

- legal-doctrine
- legal-research
- security-review

### Δ < 0 — the plugin made these worse

- nextjs-feature-scaffold
- public-sector-contracting

Cost: $15.35 (list-price estimate) · claude 2.1.316
