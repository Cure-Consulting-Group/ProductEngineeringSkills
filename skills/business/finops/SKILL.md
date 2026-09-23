---
name: finops
description: "Cloud cost optimization for Firebase and GCP: budgets, alerts, right-sizing, labels, AI API spend. Use when a cloud bill spikes, setting budgets, or cutting infra and LLM costs."
when_to_use: "NOT for company runway or burn (use burn-rate-tracker), pricing or unit economics (use saas-financial-model), or pre-build cost estimates (use engineering-cost-model)."
argument-hint: "[project-or-service]"
metadata:
  verified: 2026-09-23
---

# FinOps

**Outcome:** every dollar of cloud and API spend attributed to a product, environment, and
feature, with guardrails (budgets, alerts, caps) and a ranked list of savings with estimated
monthly impact. **Done when** the top cost drivers are named with numbers from the actual bill,
each recommendation has an owner-ready change and a savings estimate, and every unit price you
quote was looked up on the vendor's current pricing page and dated. Match length to the need; no
filler sections or restated summaries.

## Pre-Processing (Auto-Context)

Context (pre-filled in Claude Code; in other runtimes run these commands first):

- Portfolio: !`sed -n '1,20p' PORTFOLIO.md 2>/dev/null || echo "(no PORTFOLIO.md)"`
- Firebase projects: !`cat .firebaserc 2>/dev/null | head -15 || echo "(no .firebaserc)"`
- Function sizing: !`grep -rhoE "memory: *['\"]?[0-9]+[A-Za-z]*|minInstances: *[0-9]+|maxInstances: *[0-9]+" functions/src 2>/dev/null | sort | uniq -c | head -10 || echo "(no functions/src)"`
- IaC surface: !`ls *.tf terraform/ 2>/dev/null | head -10 || echo "(no terraform)"`
- Metered APIs: !`grep -oiE "\"(openai|@anthropic-ai/sdk|@google/genai|@sendgrid/mail|twilio|stripe)\"" package.json functions/package.json 2>/dev/null | sort -u || echo "(none found)"`

## Step 1: Classify

| Type | When | Output |
|------|------|--------|
| Cost audit | Monthly, or after bill shock | Per-service breakdown, waste, ranked savings |
| Budget setup | New project or fiscal period | Budgets, alert tiers, environment caps |
| Optimization | Cost growing faster than usage | Right-sizing, architecture changes, commitments |
| Cost allocation | Multiple products or teams | Label scheme, showback dashboard |
| Forecast | Planning | Growth-driven projection with scenarios |

A question ("why did the bill double?") gets a diagnosis, not the full program.

## Step 2: Gather Context

Providers in play (Firebase/GCP, Vercel, AI APIs, email/SMS); the last 3 months of spend per
service (if unknown, getting it is the first deliverable); growth trend; cost owners and who
approves increases; whether billing export and labels already exist.

## Step 3: Visibility — the baseline every Cure project gets

Without these, spend cannot be attributed, and unattributed spend cannot be cut.

1. **Billing export to BigQuery** (Billing → Billing export → BigQuery), dataset `billing_export`.
2. Per-service dashboard in **Looker Studio** on that export; monthly report to the eng lead and finance.
3. **Labels on every resource** — `product`, `environment` (dev/staging/production), `team`,
   `feature`, `cost-center`. Use the product slug from PORTFOLIO.md.
   - Cloud Functions (v2): `setGlobalOptions({ labels: { product: "<slug>", ... } })`
   - Cloud Run: `gcloud run services update SERVICE --update-labels=product=<slug>,environment=production`
   - Cloud Storage: `gcloud storage buckets update gs://BUCKET --update-labels=product=<slug>`
     (`gsutil` is legacy and leaves the gcloud CLI package after March 2027)
   - Firestore: project-level labels
4. Anomaly alert on > 20% day-over-day increase.

```sql
-- Monthly cost by environment (target: production ≥ 70% of total)
SELECT l.value AS environment, SUM(cost) AS total_cost,
       SUM(cost) / SUM(SUM(cost)) OVER () * 100 AS pct_of_total
FROM `PROJECT.billing_export.gcp_billing_export_v1_*`
LEFT JOIN UNNEST(labels) AS l ON l.key = "environment"
WHERE invoice.month = FORMAT_DATE('%Y%m', CURRENT_DATE())
GROUP BY environment ORDER BY total_cost DESC;
```

Dev + staging above 30% of spend is waste to clean up. Egress and cross-region transfer are the
usual hidden cost; check them explicitly.

## Step 4: Firebase optimization

Read the Firebase reference file (`reference/details.md`) when the audit shows Firestore,
Cloud Functions, Storage, or Auth among the top cost drivers — it has the read-reduction
patterns, function memory guide, lifecycle policy, and auth cost traps.

## Step 5: GCP optimization

**Commitments** — only for stable production load running > 6 months; never for dev/staging or
projects under 3 months old (no data yet).

- Cloud Run: compute **flexible CUDs**, 28% (1-year) / 46% (3-year), apply to instance-based
  billing, jobs, and worker pools (verified 2026-09-23, docs.cloud.google.com/run/cud).
- Compute Engine and Cloud SQL: rates vary by machine family and CUD type — check the current
  CUD page and the Billing → CUD recommender before committing.

**Right-sizing** (monthly):
- Cloud Run: peak memory < 50% of allocation → reduce; CPU consistently < 30% → reduce CPU or
  raise concurrency; request-based billing (CPU only during requests) for spiky services.
- Cloud Functions: short executions on 1 GiB → try 256–512 MiB; cold-start problems are fixed
  with `minInstances`, not memory.
- **Spot VMs** (up to 91% off on-demand, preemptible at any time) for CI runners, batch, and
  training only — never user-facing or stateful services.

## Step 6: AI/API cost management

**Route by capability tier, not by model name.** Model lineups and prices change every few
months, so look up current per-token prices on the provider's pricing page at the time of the
analysis and date them in the report.

| Tier | Typical models (families) | Use for |
|---|---|---|
| Fast / small | Claude Haiku, GPT mini/nano, Gemini Flash / Flash-Lite | Classification, extraction, validation, formatting |
| Standard | Claude Sonnet, GPT standard, Gemini Pro | Most features, generation, code |
| Frontier | Claude Opus, top GPT / Gemini tier | Hard reasoning, high-stakes review — justify per feature |

Levers, roughly in order of payoff:
1. **Prompt caching** for long, stable system prompts and documents (large discount on cached
   input tokens with Anthropic, OpenAI, and Google — check current terms).
2. **Batch APIs** for anything not user-facing (typically ~50% off).
3. Tier routing: classify with a fast model, escalate only when needed.
4. Response caching: exact-match (hash prompt + model + params), TTL by content volatility;
   track hit rate.
5. Per-feature token budgets: daily cap → queue or downgrade tier; monthly cap → disable the
   feature and alert.

Log cost per request by feature; this feeds per-feature unit cost (Step 8). For eval pipelines,
prompt versioning, and model lifecycle, hand off to `llmops`.

## Step 7: Budgets and governance

```bash
gcloud billing budgets create --billing-account=BILLING_ACCOUNT_ID \
  --display-name="PROJECT Monthly Budget" --budget-amount=500USD \
  --threshold-rule=percent=0.5 --threshold-rule=percent=0.8 \
  --threshold-rule=percent=1.0 --threshold-rule=percent=1.2 \
  --threshold-rule=percent=1.0,basis=forecasted-spend \
  --notifications-rule-pubsub-topic=projects/PROJECT_ID/topics/billing-alerts
```

| Threshold | Response |
|---|---|
| 50% | Email the eng lead |
| 80% | Team channel alert; review spend |
| 100% (actual or forecast) | Freeze non-essential environments; investigate |
| 120% | Escalate to CTO; emergency reduction |

Budgets alert; they don't stop spend. Hard caps need automation (a Pub/Sub-triggered function
that scales dev to zero). Cure defaults for environment caps: dev \$50, staging \$200, shared
services \$100, production by forecast — never auto-shutdown production. Dev shuts down nightly
via Cloud Scheduler.

Any PR that adds > \$100/month needs a cost estimate in the description and eng-lead approval.

## Step 8: Unit cost per feature

Track monthly cost, users, and cost/user per feature from the labels. Use it to find features
that cost more than they earn, to price AI-heavy features into upper tiers (hand the numbers to
`saas-financial-model`), and to confirm optimizations worked (cost/user should fall). Review
spend for 5 minutes in sprint planning and take one cost ticket per sprint.

## Code/Artifact Generation

Applies to budget setup and optimization work, or when the user asks for files. An audit or a
question gets the report only.

1. `docs/finops-report.md` — findings, ranked savings, dated price sources
2. `monitoring/budget-alerts.tf` — budget and alert tiers
3. `analytics/cost-queries.sql` — BigQuery cost queries
4. `scripts/right-size-resources.sh` — read-only listing of over-provisioned resources

## Output

```
FINOPS REPORT — [PROJECT] — [DATE]
Spend $X/mo | budget $X | MoM ±X% | top driver [service: $X]
Findings (all, each with severity and estimated $/mo):
  1. [finding] — [evidence from bill/config] — [change] — [$X/mo]
Guardrails: budgets [y/n] | labels [% of spend labeled] | anomaly alert [y/n]
Prices quoted: [vendor page, date checked]
```

Related: `engineering-cost-model` (pre-build estimates), `infrastructure-scaffold` (infra with
cost defaults), `saas-financial-model` (pricing from costs), `llmops` (LLM operations).

## Recurring Mode

This is a recurring goal, not a one-shot (mechanism trade-offs: `/engagement-automation`).

- **Cadence:** weekly
- **Session loop:** none — session loops expire after 7 days, so a weekly cadence never fires in-session; it belongs in the cloud routine below.
- **Unattended:** cloud routine — Weekly cloud-cost delta review: flag anomalies vs last run, right-sizing candidates, budget-alert drift. Recipes: docs/AUTOMATION.md in the plugin repo.
- **Budget:** ~100k tokens/run; cap at one run per weekly period.
- **Guardrails:** writes only the cost report (file or issue); no infra, config, or Terraform changes (advisory — recurring-mode doctrine per AUTOMATION.md, not harness-enforced); report on failure rather than retrying.
