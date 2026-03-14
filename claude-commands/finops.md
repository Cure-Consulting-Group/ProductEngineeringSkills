# FinOps

Cloud financial operations framework for Firebase and GCP projects. Use when setting up cost visibility, optimizing spend, establishing budgets, or building a cost-aware engineering culture. Every dollar spent on infrastructure should be traceable to a feature or user segment.

## Step 1: Classify the FinOps Need

| Type | When to Use | Output |
|------|------------|--------|
| Cost Audit | Monthly or after bill shock — understand where money goes | Per-service cost breakdown, waste identification, optimization recommendations |
| Budget Setup | New project or new fiscal period — set guardrails | Budget alerts, spending limits, anomaly detection |
| Optimization Initiative | Costs growing faster than usage — reduce waste | Right-sizing plan, architecture changes, committed use discounts |
| Cost Allocation | Multi-product or multi-team — assign costs to owners | Tagging strategy, per-team dashboards, chargeback model |
| Forecasting | Planning phase — predict future spend | Growth-based projections, scenario modeling |

## Step 2: Gather Context

1. **Cloud providers** -- Firebase + GCP (primary), Vercel, third-party APIs (Stripe, SendGrid, OpenAI)?
2. **Current monthly spend** -- total and per-service breakdown. If unknown, that is the first deliverable.
3. **Growth trajectory** -- user growth rate, request volume trend, storage growth?
4. **Cost centers** -- single product or multiple? Multiple teams? Need chargeback or showback?
5. **Budget authority** -- who approves spend increases? What is the monthly/quarterly budget cap?
6. **Existing visibility** -- do billing dashboards exist? Are costs tagged? Is anyone reviewing spend regularly?

## Step 3: Cost Visibility

### Billing Dashboard Setup
```
Every project MUST have:
  1. GCP Billing Export to BigQuery (enabled once, runs continuously)
  2. Monthly cost report emailed to engineering lead + finance
  3. Per-service cost dashboard (Looker Studio or Data Studio)
  4. Anomaly alerts for >20% day-over-day increase

Enable billing export:
  GCP Console → Billing → Billing export → BigQuery export → Enable
  Dataset: billing_export (create in same project)

  This gives you raw billing data for custom queries and dashboards.
```

### Cost Allocation Tags
```
Every GCP resource MUST be tagged:

Required labels:
  project: "antigravity"           — which product
  environment: "production"        — dev / staging / production
  team: "backend"                  — owning team
  feature: "payments"              — specific feature (for per-feature cost tracking)
  cost-center: "engineering"       — budget category

Apply labels:
  Cloud Functions:  setGlobalOptions({ labels: { project: "antigravity", ... } })
  Cloud Run:        gcloud run services update SERVICE --labels=project=antigravity
  Cloud Storage:    gsutil label set labels.json gs://BUCKET
  Firestore:        labels set at project level in console

Labels enable:
  - Filter billing by team, feature, environment
  - Answer "How much does the payments feature cost?"
  - Answer "What percentage of spend is dev vs. production?"
```

### Per-Service Cost Breakdown
```
Service                Typical Cost Driver          How to Track
──────────────────────────────────────────────────────────────────
Cloud Functions        Invocations + compute time   Cloud Monitoring → function/execution_count
Firestore              Reads/writes/deletes         Firebase Console → Usage tab
Cloud Storage          Storage volume + egress      GCP Console → Storage → Usage
Cloud Run              CPU + memory per request      Cloud Monitoring → container metrics
Firebase Auth          Monthly active users (MAU)    Firebase Console → Auth → Usage
Firebase Hosting       Bandwidth + storage           Firebase Console → Hosting → Usage
Secret Manager         Access operations              GCP Console → Secret Manager
Cloud Scheduler        Job executions                 Minimal cost, rarely an issue
Networking/Egress      Cross-region data transfer     Often the hidden cost — monitor closely
```

### Per-Environment Breakdown
```sql
-- BigQuery query: monthly cost by environment
SELECT
  labels.value AS environment,
  SUM(cost) AS total_cost,
  SUM(cost) / SUM(SUM(cost)) OVER () * 100 AS pct_of_total
FROM `PROJECT.billing_export.gcp_billing_export_v1_*`
LEFT JOIN UNNEST(labels) AS labels ON labels.key = "environment"
WHERE invoice.month = FORMAT_DATE('%Y%m', CURRENT_DATE())
GROUP BY environment
ORDER BY total_cost DESC;

-- Target: production < 70% of total, dev+staging < 30%
-- If dev/staging > 30%, you have waste to clean up
```

## Step 4: Firebase-Specific Optimization

### Firestore Read/Write Reduction
```
Firestore costs $0.06/100K reads and $0.18/100K writes.
At scale, reads are the dominant cost. Reduce them aggressively.

Optimization                          Estimated Savings
──────────────────────────────────────────────────────────────────
Enable offline persistence             30-50% read reduction (cached locally)
Use onSnapshot listeners wisely        1 read per change, not per poll
Pagination (limit queries to 20-50)    Prevents "read the whole collection"
Denormalize for read-heavy patterns    1 read instead of N joins
Composite indexes                      Fewer reads per query (more efficient)
Security rule optimization             Fewer get() calls in rules
Batch reads (getAll)                   1 API call instead of N

Anti-patterns to eliminate:
  ❌ Reading entire collection to filter client-side
  ❌ Polling with getDoc() instead of using onSnapshot()
  ❌ Storing computed values that could be derived
  ❌ No pagination on list screens
  ❌ get() calls in security rules for every request (cache with custom claims)
```

### Cloud Functions Optimization
```
Cloud Functions cost: invocations ($0.40/M) + compute (CPU-seconds + memory-seconds)

Optimization                          Estimated Savings
──────────────────────────────────────────────────────────────────
Right-size memory (don't use 1GB       Up to 75% compute cost reduction
  when 256MB suffices)
Increase concurrency (80 req/inst)     Fewer instances = less compute
Set maxInstances cap                   Prevents runaway costs from traffic spikes
Reduce cold starts (minInstances=0     Pay nothing when idle
  for low-traffic, =1 for critical)
Combine related functions              Fewer cold starts, shared dependencies
Use Cloud Tasks for async work         Decouple from request lifecycle
Move heavy computation to Cloud Run    Better cost model for long-running tasks

Memory right-sizing guide:
  Simple webhook handler:     128MiB
  Standard API endpoint:      256MiB
  Image processing:           512MiB-1GiB
  PDF generation:             1GiB
  ML inference:               2GiB+ (consider Cloud Run instead)
```

### Storage Lifecycle Policies
```json
{
  "lifecycle": {
    "rule": [
      {
        "action": { "type": "Delete" },
        "condition": { "age": 7, "matchesPrefix": ["tmp/", "cache/", "uploads/processing/"] }
      },
      {
        "action": { "type": "SetStorageClass", "storageClass": "NEARLINE" },
        "condition": { "age": 30, "matchesPrefix": ["uploads/"] }
      },
      {
        "action": { "type": "SetStorageClass", "storageClass": "COLDLINE" },
        "condition": { "age": 90, "matchesPrefix": ["backups/"] }
      },
      {
        "action": { "type": "Delete" },
        "condition": { "age": 365, "matchesPrefix": ["logs/", "analytics-exports/"] }
      }
    ]
  }
}

// Apply: gsutil lifecycle set lifecycle.json gs://BUCKET_NAME
// Estimated savings: 40-60% on storage costs for mature projects
```

### Auth Cost Awareness
```
Firebase Auth pricing:
  Phone auth:              $0.01-0.06 per SMS verification
  Email/password:          Free (unlimited)
  Google/Apple/GitHub:     Free (unlimited)
  Anonymous auth:          Free (unlimited)
  SAML/OIDC (enterprise): $0.015 per MAU above 50 free

Cost traps:
  ❌ SMS verification for every login (use phone auth only for registration)
  ❌ Anonymous auth that never converts (creates orphan accounts)
  ❌ Not cleaning up disabled/unused accounts

Optimizations:
  ✅ Use email link sign-in instead of SMS where possible
  ✅ Convert anonymous users or delete after 30 days
  ✅ Use custom claims instead of Firestore lookups for auth context
```

## Step 5: GCP Optimization

### Committed Use Discounts
```
If your workload is predictable, commit for savings:

Resource              On-Demand      1-Year CUD    3-Year CUD
──────────────────────────────────────────────────────────────
Cloud Run CPU         $0.00002400    -17%          -40%
Cloud Run Memory      $0.00000250    -17%          -40%
Compute Engine        varies         -37%          -55%
Cloud SQL             varies         -25%          -52%

When to commit:
  ✅ Stable production workload running > 6 months
  ✅ Baseline always-on compute (minInstances)
  ❌ Never commit for dev/staging environments
  ❌ Never commit for new projects (wait 3 months for data)
```

### Right-Sizing Recommendations
```
Review monthly — GCP provides right-sizing recommendations in Console:
  GCP Console → Compute Engine → VM Instances → Right-sizing recommendations
  GCP Console → Cloud Run → Services → Metrics (check actual vs. allocated)

Cloud Run right-sizing:
  1. Check actual CPU/memory usage in Cloud Monitoring
  2. If peak memory < 50% of allocation → reduce allocation
  3. If CPU utilization consistently < 30% → reduce CPU or increase concurrency
  4. Set CPU throttling = true (only charge for active request processing)

Cloud Functions right-sizing:
  1. Check execution times in Firebase Console → Functions → Dashboard
  2. If avg execution < 1s with 1GiB memory → try 256MiB
  3. If cold start is the problem → increase minInstances, not memory
```

### Preemptible / Spot Instances
```
For batch processing, ML training, CI/CD runners:
  - Spot VMs: 60-91% discount, but can be preempted with 30s notice
  - Use for: CI/CD build agents, batch data processing, ML training
  - Never for: user-facing services, databases, stateful workloads

  gcloud compute instances create batch-worker \
    --provisioning-model=SPOT \
    --instance-termination-action=STOP \
    --machine-type=e2-standard-4
```

## Step 6: AI/API Cost Management

### Model Tier Routing
```
Not every request needs GPT-4 or Claude Opus.
Route by complexity to minimize cost:

Tier        Model              Cost/1M tokens   Use For
──────────────────────────────────────────────────────────────────
Fast        GPT-4o-mini        $0.15 input      Classification, extraction, simple Q&A
            Claude Haiku       $0.25 input      Validation, formatting, summarization
Standard    GPT-4o             $2.50 input      Most features, content generation
            Claude Sonnet      $3.00 input      Code generation, analysis
Premium     GPT-4              $30.00 input     Complex reasoning (rarely needed)
            Claude Opus        $15.00 input     Critical decisions, legal/financial

Implementation:
  1. Classify request complexity at the edge (use fast tier model)
  2. Route to appropriate tier based on classification
  3. Log cost per request for tracking
  4. Set per-user or per-feature token budgets
```

### Token Budget Management
```typescript
// lib/ai-cost.ts — track and limit AI spend per feature
interface TokenBudget {
  feature: string;
  dailyLimit: number;    // max tokens per day
  monthlyLimit: number;  // max tokens per month
  currentDaily: number;
  currentMonthly: number;
}

// Budget defaults per feature:
const BUDGETS: Record<string, { daily: number; monthly: number }> = {
  "chat-assistant":    { daily: 500_000,   monthly: 10_000_000 },
  "content-generator": { daily: 1_000_000, monthly: 20_000_000 },
  "code-review":       { daily: 200_000,   monthly: 5_000_000 },
  "search-summarize":  { daily: 300_000,   monthly: 8_000_000 },
};

// Check budget before every AI call:
// If daily budget exceeded → queue for tomorrow or downgrade model tier
// If monthly budget exceeded → disable feature, alert engineering
```

### Caching AI Responses
```
Cache identical or similar AI requests to avoid redundant API calls:

Strategy                    Cache TTL     Estimated Savings
──────────────────────────────────────────────────────────────
Exact match (same prompt)   24 hours      20-40% for repeated queries
Semantic similarity         1 hour        10-20% for similar queries
Embedding cache             7 days        Avoids re-embedding same documents
Precomputed responses       30 days       For known common questions

Implementation:
  1. Hash the prompt + model + temperature as cache key
  2. Store in Redis/Firestore with TTL
  3. Check cache before every API call
  4. Log cache hit/miss ratio — target > 30% hit rate
```

## Step 7: Budget Alerts and Governance

### Budget Alert Tiers
```bash
# Set up three-tier budget alerts for every project
gcloud billing budgets create \
  --billing-account=BILLING_ACCOUNT_ID \
  --display-name="PROJECT_NAME Monthly Budget" \
  --budget-amount=500 \
  --threshold-rule=percent=0.5,basis=CURRENT_SPEND \
  --threshold-rule=percent=0.8,basis=CURRENT_SPEND \
  --threshold-rule=percent=1.0,basis=CURRENT_SPEND \
  --threshold-rule=percent=1.2,basis=CURRENT_SPEND \
  --notifications-rule-pubsub-topic=projects/PROJECT_ID/topics/billing-alerts

Alert tiers and response:
  50%  — Informational: email to engineering lead
  80%  — Warning: Slack alert to team channel, review spend
  100% — Action required: freeze non-essential environments, investigate
  120% — Escalation: alert CTO, consider emergency cost reduction
```

### Anomaly Detection
```
Set up day-over-day anomaly detection:

GCP Console → Billing → Budgets & alerts → Create budget
  ✅ Enable "Forecasted spend" alerts
  ✅ Set alert at 100% of forecasted budget

Custom anomaly detection (Cloud Function):
  1. Query BigQuery billing export daily
  2. Compare today's spend to 7-day rolling average
  3. Alert if > 50% above average (could indicate: runaway function, DDoS, misconfigured autoscaling)
  4. Auto-scale-down non-production environments on anomaly detection
```

### Per-Environment Spending Limits
```
Environment      Monthly Cap    Enforcement
──────────────────────────────────────────────────────────────────
Development      $50            Auto-shutdown resources at cap
Staging          $200           Alert at 80%, review at 100%
Production       $2,000+        Alert tiers (50/80/100/120%)
Shared services  $100           Alert at 80%

Enforcement:
  - Dev environments: Cloud Scheduler job to shut down nightly
  - Staging: reduce to zero instances outside business hours
  - Production: never auto-shutdown, but alert aggressively

# Shut down dev Cloud Run services nightly
gcloud scheduler jobs create http dev-shutdown \
  --schedule="0 20 * * MON-FRI" \
  --uri="https://REGION-PROJECT.cloudfunctions.net/shutdownDev" \
  --http-method=POST
```

### Approval Workflow for Cost Increases
```
Any change that increases monthly cost by >$100 requires:
  1. Cost estimate in the PR description
  2. Approval from engineering lead
  3. Updated budget if needed

PR template addition:
  ## Cost Impact
  - [ ] No cost change
  - [ ] Estimated monthly increase: $___
  - [ ] New service/resource: ___ at estimated $___/month
  - [ ] Cost reviewed by: @engineering-lead
```

## Step 8: FinOps Culture

### Unit Economics Per Feature
```
Track cost-per-feature monthly:

Feature              Monthly Cost    Users     Cost/User    Trend
──────────────────────────────────────────────────────────────────
Authentication       $12             10,000    $0.001       Stable
Chat (AI-powered)    $340            2,000     $0.170       Growing
Image uploads        $85             5,000     $0.017       Stable
Search               $45             8,000     $0.006       Stable
Notifications        $20             10,000    $0.002       Stable

Use this to:
  - Identify features that cost more than they're worth
  - Set pricing tiers based on actual cost (AI features = premium tier)
  - Justify infrastructure investments with per-user economics
  - Track if optimization efforts are working (cost/user should decrease)
```

### Cost in Sprint Planning
```
Every sprint planning should include:
  1. Review current month spend vs. budget (5 minutes)
  2. Flag any infrastructure tickets with cost implications
  3. Assign cost tags to new features before development starts
  4. Review optimization backlog — pick 1 cost ticket per sprint

Sprint board labels:
  💰 cost-increase — this ticket will increase infrastructure spend
  💰 cost-reduction — this ticket reduces infrastructure spend
  💰 cost-neutral — no expected cost change
```

### Engineer Cost Awareness
```
Make costs visible to every engineer:

1. Weekly cost Slack bot
   Post to #engineering: "This week's cloud spend: $X (+Y% vs last week)"
   Include top 3 cost drivers

2. Per-PR cost estimation
   GitHub Action that estimates cost impact of infrastructure changes
   Flag PRs that add new Cloud Functions, increase memory, add services

3. Monthly cost review
   15-minute meeting: review spend, celebrate optimizations, plan reductions
   Rotate presenter — every engineer should present once per quarter

4. Cost leaderboard (gamification)
   Track optimization wins per engineer
   Celebrate biggest cost reductions in team retros
```

## Step 9: Output

```
FINOPS REPORT
Project: [NAME]
Date: [TODAY]
Prepared by: [NAME]

COST SUMMARY
┌──────────────────────────┬────────────────────────────────────┐
│ Field                    │ Value                              │
├──────────────────────────┼────────────────────────────────────┤
│ Current Monthly Spend    │ $[X]                               │
│ Budget                   │ $[X]                               │
│ Spend vs. Budget         │ [X%]                               │
│ Month-over-Month Change  │ [+/-X%]                            │
│ Top Cost Driver          │ [Service name: $X]                 │
│ Optimization Potential   │ $[X] / month                       │
│ Cost per User            │ $[X]                               │
│ FinOps Maturity          │ [Crawl / Walk / Run]               │
└──────────────────────────┴────────────────────────────────────┘

DELIVERABLES GENERATED:
  - [ ] Per-service cost breakdown with trend analysis
  - [ ] Cost allocation tags applied to all resources
  - [ ] Budget alerts configured (50%, 80%, 100%, 120%)
  - [ ] Firebase optimization recommendations with estimated savings
  - [ ] GCP right-sizing recommendations
  - [ ] AI/API cost management strategy
  - [ ] Per-environment spending limits
  - [ ] Cost approval workflow for PRs
  - [ ] Monthly cost review process established
  - [ ] Unit economics per feature calculated

RELATED SKILLS:
  - /engineering-cost-model — project-level cost estimation
  - /infrastructure-scaffold — infra configs with cost defaults
  - /saas-financial-model — pricing tiers based on actual costs
  - /performance-review — performance optimization often reduces cost
```
