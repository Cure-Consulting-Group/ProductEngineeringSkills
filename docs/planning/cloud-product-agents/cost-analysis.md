# Cost analysis — cloud product agents

Prepared 2026-09-27. USD. Internal planning estimate; no fixed spending ceiling selected. User requested founder time plus existing AI subscriptions, with cash and time reported separately.

## 1. Decision and estimate basis

Recommended sequence: a small proof using existing tooling, a read-only pilot, then a two-product service with bounded repair PRs. Do not build the complete service before measuring actionable findings and coordination time saved.

The full platform covers eight epics and eighteen stories in [backlog.md](backlog.md). Its two-product modeled monthly cash is about $96 read-only, $357 balanced, or $1,115 intensive. A 25% cash reserve gives planning envelopes of about $120, $446, or $1,394. These are usage scenarios, not performance guarantees or confidence intervals.

Founder-active build effort is 115–187 hours for the read-only pilot and another 134–245 hours for expansion; cumulative 250–432 hours including one 20% time reserve. Existing AI subscriptions assist this work, but no assumed productivity multiplier or free cloud inference is used. Full build incremental API/test/cloud allowance is $150–500; it is a planning allowance, not measured consumption. Existing subscriptions and existing product hosting bills remain separate and their actual amounts were not supplied.

Prices were checked against the linked vendor pages on 2026-09-27. Model inputs are in [assumptions.json](assumptions.json); exact outputs, sensitivities, and twelve-month totals are in [cost-results.md](cost-results.md). Calculator uses standard/global token prices, short-context OpenAI rates, and single-region us-central1 cloud rates. Account entitlements, actual invoice rates, regions, and residency requirements must be verified at implementation.

This is an early decomposed planning estimate. Effort ranges are judgment estimates with named integration risks; they are not statistically validated confidence bands. There is no completed-platform reference class or actual founder productivity data. Meter the first pilot week and reforecast.

## 2. Token rates and routing

All token rates below are USD per million billed tokens, using standard processing. Selected model availability and API account access are prerequisites, not assumed entitlements.

| Role | Model rate basis | Input | Output |
|---|---|---:|---:|
| Routing and small summaries | GPT-6 Luna | $0.10 | $0.50 |
| PM, design, behavior follow-up | Claude Sonnet 5 | $2 | $10 |
| Engineering review and implementation | GPT-6 Sol | $2 | $10 |
| Deep investigation and independent repair review | Claude Opus 5.5 | $4 | $20 |

Sources: [OpenAI API pricing](https://developers.openai.com/api/docs/pricing), [Claude API pricing](https://platform.claude.com/docs/en/about-claude/pricing). Provider diversity is an evaluation choice; it does not guarantee correctness. Cheaper routing must pass the same relevant evaluation as other tiers.

No cached-input or batch discounts are deducted. Cache creation can itself cost more than ordinary input; daily schedules cannot assume yesterday's prompt cache is still valid. Long-context, fast/priority, regional routing, paid tools, image and reasoning usage can change the bill. Use cumulative provider-metered tokens; do not estimate cost from only the final answer or count an entire agent task as one prompt.

| Work order type | Cumulative input / output assumptions | Base token cost before retries |
|---|---|---:|
| Triage | Luna: 12k / 1k | $0.0017 |
| PM review | Sonnet: 100k / 10k | $0.30 |
| Design review | Sonnet: 140k / 12k, including billed image-equivalent input | $0.40 |
| Engineering review | Sol: 160k / 16k | $0.48 |
| Deep investigation | Opus: 600k / 25k across multiple calls | $2.90 |
| Repair + independent review | Sol: 1.2M / 70k; Opus: 300k / 20k across multiple calls | $4.70 |
| Release behavior follow-up | Sonnet: 100k / 8k | $0.28 |

The numbers are workload assumptions, not benchmark measurements. Apply 30% LLM retry/context overhead once. A repair attempt consumes its budget even if it fails or is rejected. At assumed 60% acceptance, its LLM allowance is about $10.18 per accepted fix before human review, CI, and shared services. Actual acceptance and token trajectories must be measured.

## 3. Monthly workload scenarios

Counts are totals across **two products**, over a 30-day operating month. Triage handles many events cheaply; it does not launch every specialist on every event.

| Work item | Read-only | Balanced | Intensive |
|---|---:|---:|---:|
| Triage events | 120 | 600 | 2,400 |
| PM review runs | 8 | 60 | 120 |
| Design review runs | 8 | 24 | 60 |
| Engineering reviews | 40 | 120 | 400 |
| Deep investigations | 4 | 8 | 24 |
| Repair attempts including independent reviewer | 0 | 16 | 60 |
| Release follow-ups | 20 | 40 | 120 |
| Lightweight browser probes | 60 | 180 | 600 |
| Incremental Linux CI minutes | 600 | 1,800 | 4,800 |
| Incremental macOS CI minutes | 160 | 320 | 960 |
| Retained evidence, GiB | 25 | 80 | 250 |

Linux/macOS entries are additional validation attributable to this platform, including expected retries. Existing CI costs already incurred by ordinary product work are excluded. Never add the same run to both existing product bills and platform incremental costs. These minutes are allowances; the platform does not introduce nightly full suites or change existing mobile trigger policies. Browser probes execute in Cloud Run and are separate from CI minutes.

Workload does not equal improvements shipped. Balanced 16 attempts yields an illustrative 9.6 accepted PRs at the assumed rate; deployment and product outcome success remain separately tracked.

## 4. Infrastructure rates and assumptions

Free tiers and existing included CI minutes are deliberately not deducted: they may already be used by other projects. Actual marginal cash can therefore be lower than the gross list-rate model. Cloud resources scale to zero when idle; no database server, GPU, always-on worker or paid dashboard hosting subscription is planned.

| Component | Rate / modeling basis | Source |
|---|---|---|
| Cloud Run jobs | $0.000018/vCPU-second + $0.000002/GiB-second; model 2 vCPU, 4 GiB; one-minute minimum | [Cloud Run pricing](https://cloud.google.com/run/pricing) |
| Control API | $0.000024/vCPU-second, $0.0000025/GiB-second, $0.40/million requests; model 1 vCPU/1 GiB, no minimum instances | [Cloud Run pricing](https://cloud.google.com/run/pricing) |
| Firestore | $0.03/100k reads; $0.09/100k writes; approximately $0.15/GiB-month state storage | [Firestore pricing](https://cloud.google.com/firestore/pricing) |
| Cloud Storage | Approximately $0.02/GiB-month standard regional storage; $0.12/GiB evidence download assumption | [Storage pricing](https://cloud.google.com/storage/pricing) |
| Cloud Logging | $0.50/GiB ingested, default 30-day retention; gross before free allotment | [Observability pricing](https://cloud.google.com/products/observability/pricing) |
| Pub/Sub | $40/TiB combined publish/delivery throughput, gross before free allotment | [Pub/Sub pricing](https://cloud.google.com/pubsub/pricing) |
| Cloud Scheduler | $0.10/shared job/month, gross before free allotment | [Scheduler pricing](https://cloud.google.com/scheduler/pricing) |
| Secret Manager | Approximately $0.06/active version/month; $0.03/10k accesses | [Secret Manager pricing](https://cloud.google.com/secret-manager/pricing) |
| GitHub standard runners | Linux 2-core $0.006/min; standard macOS $0.062/min | [Actions runner pricing](https://docs.github.com/en/billing/reference/actions-runner-pricing) |
| Optional model web search | $10/1,000 calls plus metered model tokens, already included in token assumptions | [OpenAI API pricing](https://developers.openai.com/api/docs/pricing) |

Monthly job time assumptions are 1/3/6/5/12/35/4 minutes for triage/PM/design/engineering/deep/repair/follow-up, plus 30% retry overhead. Each browser probe is 4 minutes plus the same overhead. Jobs use the allocated CPU/memory throughout their lifetime, including network/model waits. API active-time assumptions are 900/3,600/14,400 seconds. Installation/build startup and actual tool time can exceed these; validate during pilot. Repair cap is 60 minutes per attempt, above the modeled 45.5 minutes including retry allowance.

Ancillary monthly allowances, clearly separate from vendor-priced usage: $10/$20/$50 for artifact operations, container registry and control-state backup exports; $10/$25/$60 for metric queries and monitoring not otherwise modeled. These need decomposition from measured usage at pilot start; they are not quoted vendor package prices. GCS standard operations, if itemized later, are $0.005/1k Class A and $0.0004/1k Class B in a regional flat-namespace bucket. [Storage pricing](https://cloud.google.com/storage/pricing).

Daily state backups and evidence retention are included in ancillary/storage assumptions. No new commercial analytics, email, Slack, vector database, device farm, or agent-platform subscription is purchased in the model. Adding one adds its actual rate. No taxes, currency conversion, negotiated discounts, or paid human incident coverage are included.

## 5. Results and cash/time separation

| Scenario | Incremental modeled cash/month | With 25% reserve | Founder operating hours/month |
|---|---:|---:|---:|
| Read-only | $96 | $120 | 6–10 |
| Balanced, 16 repair attempts | $357 | $446 | 13–22 |
| Intensive, 60 repair attempts | $1,115 | $1,394 | 30–56 |

Founder operating time = finding/digest oversight + platform maintenance + 0.3–0.6 active hours per repair attempt. This includes review of rejected repairs. It excludes human implementation of problems the agent cannot solve, customer research, production releases that already require owner time, and discretionary new feature development. Those are additional work if needed; the model does not promise to eliminate them.

Example balanced monthly composition: $255 inference; about $11 worker/browser/control compute; about $15 state/evidence/logging/scheduling/secrets; $31 incremental CI; $2 search; $45 ancillary allowances. Exact categories and rounding are in generated reports. Primary cash risk is repeated large-context reviews and repairs; primary effort risk is environment/test instability requiring human intervention. macOS minutes are tracked separately to expose expensive validation patterns.

Twelve operating months **after full launch**, plus one full-build cash allowance: balanced $4,430–4,780 modeled incremental cash, or $5,500–5,850 with cash reserve. Founder build time is 250–432 hours in addition to 154–259 operating hours/year. This is not a calendar-year spending forecast; it intentionally assumes 12 full operating months rather than pretending all development and launch happen on day one.

Existing subscription invoices are baseline cash, not zero-cost accounts. Monthly total outflow = existing subscriptions + existing product infrastructure + modeled platform incremental cash + any new purchased service. No dollars are assigned to founder labor unless an optional opportunity-value rate is chosen.

## 6. Sensitivity and economics

Balanced 2× cumulative token usage raises modeled cash to about $611/month; 5× raises it to $1,375/month before reserve. A nominally cheap model reading the entire repository repeatedly can still dominate spend. Keep retrieved context bounded and reuse immutable evidence.

At the same per-product workload, balanced projection is approximately $891/month for five products and $1,781/month for ten, before reserve. Founder hours scale to 32–54 and 64–108 respectively. This reveals the need to tighten review scope and delegate accepted work as the portfolio grows; adding products is not free. Additional onboarding: 16–32 founder-active hours/product plus 20% reserve, assuming standard connectors and working fixtures.

Assume balanced midpoint operating time of 17.2 hours/month and full-build midpoint 340.8 hours:

| Current manual coordination | Illustrative net hours saved/month | Founder build-time payback |
|---|---:|---:|
| 20 hours/month | 2.8 | About 122 months |
| 40 hours/month | 22.8 | About 15 months |
| 60 hours/month | 42.8 | About 8 months |

This payback measures time, not cash ROI. It conservatively subtracts platform maintenance and repair-review time but credits no development acceleration or avoided defects. Baseline must measure the same coordination scope; if repairs are additional work, report them separately in pilot results. Revenue gains, incident avoidance and faster shipping are possible benefits, not included savings.

At 40 baseline hours and an optional founder-time value of $100/$150/$200 per hour, 22.8 saved hours represent $2,280/$3,420/$4,560 opportunity value/month before cloud cost. Deduct the $446 planning envelope for a conservative net of about $1,834/$2,974/$4,114. This does not create cash in the bank unless the recovered time replaces paid work or produces attributable revenue.

## 7. Build versus reuse versus managed workers

| Approach | Founder effort | Incremental operating basis | Trade-off |
|---|---|---|---|
| Minimal proof using existing skills/tests and report artifacts | 24–40 hours: access/schedule 6–10, profiles 6–10, targeted fixtures 6–10, adjudication/report 6–10 | Use read-only scenario as conservative ceiling; narrower workload should meter lower | Validates usefulness; no full dashboard, durable repair lifecycle or comprehensive coverage |
| Full shared service, self-hosted workers | 250–432 hours including reserve | Balanced about $357/month modeled | Complete task/evidence/repair/outcome ownership; largest initial build effort |
| Shared service with provider-managed agent workers | Control/integration/dashboard work still required; no unverified build-time discount assumed | Claude managed runtime $0.08/session-hour plus ordinary token/tool usage | Can remove some execution plumbing; access, interoperability, replay and sandbox fit must be tested |

Managed runtime price source: [Claude Managed Agents pricing](https://platform.claude.com/docs/en/about-claude/pricing#claude-managed-agents-pricing). At identical modeled worker duration and tokens, replacing agent-worker Cloud Run compute changes balanced spend by only about **-$4/month**. Browser probes, mobile CI, database and coordinator remain. The stronger reason to use managed execution is reduced implementation/operations effort, not this small runtime delta. No Batch discount is assumed for managed sessions.

Three-year cash-only illustration, flat rates and workloads: full self-hosted balanced $12,990–13,340 including one build allowance, or $16,200–16,550 with operating reserves. Founder effort adds 250–432 build hours plus approximately 461–778 operating hours. This projection has no annual price escalation and excludes expansion; reforecast each year. There is no validated off-the-shelf product quote that covers these complete requirements, so the package does not claim a SaaS buy option is cheaper.

## 8. Budget controls and pilot decision

No monthly ceiling has been selected. Architecture defines per-task proposed limits, transactional reservations, concurrent-run caps and a kill switch. Choose a monthly envelope after the pilot measures token trajectories and useful throughput. Keep a critical-review reserve and pause discretionary deep reviews before overrunning it; do not use cloud billing alerts as the sole enforcement mechanism.

Start with the 24–40 hour minimal proof if the manual baseline is unknown or below about 40 hours/month. Expand to the scoped read-only pilot if findings are accurate and schedules are reliable. Proceed to the full two-product repair platform only when net founder time savings, accepted fixes, and actual costs justify the additional build effort. A full build solely to save a few monthly check-in hours is hard to justify.

Reforecast triggers: cumulative tokens above 2× baseline; repair acceptance below 60%; more than 0.6 founder hours/repair; stale environments or unreproducible suites; changes in provider models/rates; additional paid tools; mobile runner needs; new product onboarding exceeding 32 hours. Record actuals weekly during pilot and monthly thereafter.
