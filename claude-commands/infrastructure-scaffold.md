# Infrastructure Scaffold

Outcome: working infrastructure config for the classified need — Firebase-first on GCP, Vercel
for Next.js when chosen, Docker for Cloud Run — with separate projects per environment, secrets
out of the repo, capped scaling, and budget alerts. Done when the configs deploy to a dev project
without edits beyond placeholders (`PROJECT_ID`, `ORG/REPO`) and existing configs were extended
rather than replaced. Deliver what was asked; don't add unrequested services.

## Pre-Processing (Auto-Context)

Context — run these read-only commands first; skip any that fail or aren't permitted (they only tailor the output):

- Existing configs: `ls firebase.json .firebaserc vercel.json Dockerfile docker-compose.yml cloud-run-service.yaml .env.example 2>/dev/null || echo "(none)"`
- Firebase projects: `head -20 .firebaserc 2>/dev/null || echo "(no .firebaserc)"`
- Stack: `head -25 package.json 2>/dev/null || echo "(no package.json)"`

## Step 1: Classify the Infrastructure Need

| Need | Scope |
|------|-------|
| New project setup | Firebase projects, hosting, functions, Docker, env template |
| Environment management | Dev / staging / prod separation, secrets, flags |
| Scaling config | Functions/Cloud Run concurrency and instance caps, CDN caching, pooling |
| Monitoring setup | Uptime checks, alert policies, log sinks (instrumentation code → `observability`) |
| Cost optimization | Budgets, instance caps, storage lifecycle |

## Step 2: Gather Context

Ask only for what's missing: provider mix (Firebase + GCP default, Vercel, AWS), project type
(Next.js, mobile backend, API), expected scale and regions, compliance (HIPAA → only
BAA-covered services, see `compliance-architect`; data residency → region pin), team size.

## Step 3: Firebase and GCP

Cure defaults: one Firebase project per environment (`NAME-dev`, `NAME-staging`, `NAME-prod`),
Functions 2nd gen (`firebase-functions/v2`) with `maxInstances` always set, Cloud Run for
containers, Secret Manager for server secrets, Workload Identity Federation for CI (no JSON
service-account keys), `gcloud storage` (not `gsutil`), Direct VPC egress over connectors.
Read [reference/details.md](reference/details.md) (sections "Step 3" and "Step 4") when writing
`firebase.json`, `.firebaserc`, rules/index stubs, emulator setup, Cloud Run service YAML,
buckets, Secret Manager, Scheduler, VPC, or the CI service account.

## Step 4: Vercel

```json
{
  "framework": "nextjs",
  "installCommand": "npm ci",
  "regions": ["iad1"],
  "headers": [
    { "source": "/api/(.*)", "headers": [{ "key": "Cache-Control", "value": "no-store" }] },
    { "source": "/(.*)", "headers": [
      { "key": "X-Frame-Options", "value": "DENY" },
      { "key": "X-Content-Type-Options", "value": "nosniff" },
      { "key": "Referrer-Policy", "value": "strict-origin-when-cross-origin" }
    ] }
  ]
}
```

- Pin `regions` next to the database (e.g. `iad1` for us-east Firestore/Postgres); a function far
  from its data costs more latency than the edge saves.
- Env vars: `vercel env add NAME <environment>`, `vercel env pull .env.local`. Production = the
  production branch, Preview = PRs; server secrets never get `NEXT_PUBLIC_`.
- Next.js 16 renamed `middleware.ts` to `proxy.ts` (Node runtime by default). `request.geo` and
  `request.ip` were removed in Next 15 — use `geolocation()` / `ipAddress()` from `@vercel/functions`:

```typescript
// proxy.ts
import { NextResponse, type NextRequest } from "next/server";
import { geolocation } from "@vercel/functions";

export const config = { matcher: ["/dashboard/:path*"] };

export function proxy(request: NextRequest) {
  const response = NextResponse.next();
  response.headers.set("x-country", geolocation(request).country ?? "US");
  return response;
}
```

- Domains: `vercel domains add example.com`, then copy the DNS values shown in the project's
  Domains settings. Subdomain CNAMEs are project-specific; the apex A record `76.76.21.21` is still
  accepted, but prefer the value the dashboard shows. Certificates are automatic.

## Step 5: Docker

Multi-stage, non-root user, `npm ci --omit=dev`, current LTS base image (`node:24-alpine`),
`HEALTHCHECK`, port 8080 for Cloud Run; no `version:` key in Compose files. See `rules/docker.md`.
Read [reference/details.md](reference/details.md) (section "Step 6: Docker Configuration") when
writing the Dockerfile or `docker-compose.yml`.

## Step 6: Environments and Secrets

Branch-to-environment mapping follows the Cure branch and release policy owned by
`release-management` (main → staging auto-deploy; production from a release tag with manual
approval in a protected CI environment). Don't restate a different policy here.

| Secret | Store | Access |
|---|---|---|
| Firebase web config | `.env.local` (gitignored) | `NEXT_PUBLIC_*` — not secret, but still per-environment |
| Server API keys, DB URLs | Secret Manager | `defineSecret()` in Functions v2, `--set-secrets` on Cloud Run |
| CI credentials | Workload Identity Federation | `google-github-actions/auth`; no keys stored |
| Encryption keys | Cloud KMS | KMS client |

Commit `.env.example` with every variable named and empty; never commit `.env*`, `*-sa-key.json`,
`*.p12`, `*.keystore`. Feature flags → `feature-flags` skill (Remote Config).

## Step 7: Monitoring Infrastructure

2nd-gen Functions run on Cloud Run, so alert on `cloud_run_revision` metrics; 1st-gen
`cloudfunctions.googleapis.com/*` metrics miss them. An error-rate alert needs a denominator:

```yaml
# monitoring/functions-5xx-ratio.yaml — 5xx ratio > 5% for 5 min
displayName: "Functions 5xx ratio > 5%"
combiner: OR
conditions:
- displayName: "5xx / all requests > 5%"
  conditionThreshold:
    filter: 'resource.type="cloud_run_revision" AND metric.type="run.googleapis.com/request_count" AND metric.labels.response_code_class="5xx"'
    aggregations: [{alignmentPeriod: 60s, perSeriesAligner: ALIGN_RATE, crossSeriesReducer: REDUCE_SUM, groupByFields: ["resource.label.service_name"]}]
    denominatorFilter: 'resource.type="cloud_run_revision" AND metric.type="run.googleapis.com/request_count"'
    denominatorAggregations: [{alignmentPeriod: 60s, perSeriesAligner: ALIGN_RATE, crossSeriesReducer: REDUCE_SUM, groupByFields: ["resource.label.service_name"]}]
    comparison: COMPARISON_GT
    thresholdValue: 0.05
    duration: 300s
# p95 latency: same shape without a denominator —
#   metric.type="run.googleapis.com/request_latencies", ALIGN_PERCENTILE_95, thresholdValue: 2000 (ms)
```

```bash
gcloud monitoring policies create --policy-from-file=monitoring/functions-5xx-ratio.yaml \
  --notification-channels=CHANNEL_ID
gcloud monitoring uptime create NAME-api --uri="https://api.example.com/health" \
  --http-method=GET --period=1 --timeout=10
gcloud logging sinks create bigquery-logs \
  bigquery.googleapis.com/projects/PROJECT_ID/datasets/app_logs \
  --log-filter='resource.type="cloud_run_revision"'
```

SLO targets and burn-rate alerting come from `observability`; this step only provisions them.

## Step 8: Cost Controls

- **Budget** with 50/80/100% alerts on every billing account:
  `gcloud billing budgets create --billing-account=ID --display-name="NAME monthly" --budget-amount=500 --threshold-rule=percent=0.5 --threshold-rule=percent=0.8 --threshold-rule=percent=1.0`.
  Budgets alert; they don't stop spend. For a hard stop, wire budget → Pub/Sub → a function that
  disables billing (dev projects only — it takes production down).
- **Firestore has no spending cap.** Guard it with budget alerts, App Check (blocks scripted
  abuse), query/index review, and per-collection read monitoring.
- **Functions/Cloud Run:** always set `maxInstances`; `minInstances: 0` except latency-critical
  APIs (1); `concurrency: 80` on v2 HTTP functions; scheduled jobs `maxInstances: 1`.
- **Storage lifecycle:** delete `tmp/` at 7 days; Nearline at 30, Coldline at 90 for backups;
  delete logs at 365 unless compliance says otherwise.
- Export billing to BigQuery. For price estimates, use the current GCP/Firebase pricing pages for
  the chosen region — rates differ between regional and multi-region locations (confirm before use).

## Code/Artifact Generation

Applies only when Step 1 classified the request as new project setup, environment management,
scaling config, monitoring setup, or cost optimization with a request to build. Check existing
configs first and extend them.

| Classification | Files |
|---|---|
| New project setup | `firebase.json`, `.firebaserc`, `firestore.indexes.json`, rules stubs (design via `firebase-architect`), `functions/src/index.ts`, `Dockerfile`, `.dockerignore`, `docker-compose.yml`, `vercel.json` (if Vercel), `.env.example` |
| Environment management | `.firebaserc` aliases, `.env.example`, Secret Manager / WIF commands |
| Scaling config | Function options, `cloud-run-service.yaml`, `vercel.json` regions |
| Monitoring setup | `monitoring/*.yaml` policies, uptime and sink commands |
| Cost optimization | Budget command, lifecycle JSON, instance caps |

Terraform is out of scope here — if the client needs IaC modules, follow `rules/terraform.md`
and say so rather than emitting `.tf` files from this skill.

## Cross-References

`firebase-architect` (schema, rules, indexes), `ci-cd-pipeline` (deploy workflows, WIF auth
step), `release-management` (branch and release policy), `observability` (SLOs, SDK
instrumentation), `security-review` (IAM least privilege), `database-architect` (Postgres sizing
and pooling).
