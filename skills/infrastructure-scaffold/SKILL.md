---
name: infrastructure-scaffold
version: "1.0.0"
description: "Generate cloud infrastructure configs for Firebase, GCP, Vercel, and Docker with IaC templates and environment management"
when_to_use: "Use when generating cloud infrastructure configs for Firebase, GCP, Vercel, or Docker with IaC templates. NOT for Terraform-specific guidance (follow rules/terraform.md)."
argument-hint: "[project-name]"
---

# Infrastructure Scaffold

Cloud infrastructure configuration generator for Firebase, GCP, Vercel, and Docker. Firebase-first, GCP cloud approach aligned with Cure Consulting Group standards. Every project ships with production-ready infrastructure configs, environment separation, and monitoring from day one.

## Pre-Processing (Auto-Context)

Before starting, gather project context silently:
- Read `PORTFOLIO.md` if it exists in the project root or parent directories for product/team context
- Run: `cat package.json 2>/dev/null || cat build.gradle.kts 2>/dev/null || cat Podfile 2>/dev/null` to detect stack
- Run: `git log --oneline -5 2>/dev/null` for recent changes
- Run: `ls src/ app/ lib/ functions/ 2>/dev/null` to understand project structure
- Use this context to tailor all output to the actual project

## Step 1: Classify the Infrastructure Need

| Need | Scope |
|------|-------|
| New project setup | Full infrastructure scaffold from scratch — Firebase, hosting, Docker, CI/CD integration |
| Environment management | Dev / staging / production separation, secret management, feature flags |
| Scaling config | Cloud Functions concurrency, Cloud Run autoscaling, CDN caching, database connection pooling |
| Monitoring setup | Performance monitoring, error reporting, uptime checks, alerting policies |
| Cost optimization | Billing alerts, instance limits, storage lifecycle, budget quotas |

## Step 2: Gather Context

1. **Cloud provider** — Firebase + GCP (default), Vercel, AWS, or hybrid?
2. **Project type** — web app (Next.js), mobile (Android/iOS), API backend, full stack?
3. **Expected scale** — users, requests/sec, storage volume, geographic regions?
4. **Compliance requirements** — HIPAA, SOC 2, GDPR, data residency?
5. **Team size** — solo dev, small team (2-5), or larger org with role separation?

## Step 3: Firebase Infrastructure

### firebase.json
```json
{
  "hosting": {
    "public": "out",
    "ignore": ["firebase.json", "**/.*", "**/node_modules/**"],
    "rewrites": [
      { "source": "/api/**", "function": "api" },
      { "source": "**", "destination": "/index.html" }
    ],
    "headers": [
      {
        "source": "**/*.@(js|css|map)",
        "headers": [{ "key": "Cache-Control", "value": "public, max-age=31536000, immutable" }]
      },
      {
        "source": "**/*.@(jpg|jpeg|gif|png|svg|webp|avif)",
        "headers": [{ "key": "Cache-Control", "value": "public, max-age=86400, stale-while-revalidate=3600" }]
      }
    ]
  },
  "functions": [
    {
      "source": "functions",
      "codebase": "default",
      "ignore": ["node_modules", ".git", "firebase-debug.log", "firebase-debug.*.log", "*.local"],
      "predeploy": ["npm --prefix \"$RESOURCE_DIR\" run lint", "npm --prefix \"$RESOURCE_DIR\" run build"]
    }
  ],
  "firestore": {
    "rules": "firestore.rules",
    "indexes": "firestore.indexes.json"
  },
  "storage": {
    "rules": "storage.rules"
  },
  "emulators": {
    "auth": { "port": 9099 },
    "functions": { "port": 5001 },
    "firestore": { "port": 8080 },
    "storage": { "port": 9199 },
    "hosting": { "port": 5000 },
    "pubsub": { "port": 8085 },
    "ui": { "enabled": true, "port": 4000 }
  }
}
```

### .firebaserc (Multi-Environment)
```json
{
  "projects": {
    "default": "PROJECT_NAME-dev",
    "dev": "PROJECT_NAME-dev",
    "staging": "PROJECT_NAME-staging",
    "production": "PROJECT_NAME-prod"
  },
  "targets": {
    "PROJECT_NAME-prod": {
      "hosting": {
        "app": ["PROJECT_NAME-prod"]
      }
    }
  }
}
```

Switch environments: `firebase use dev | staging | production`

### firestore.indexes.json
```json
{
  "indexes": [
    {
      "collectionGroup": "orders",
      "queryScope": "COLLECTION",
      "fields": [
        { "fieldPath": "userId", "order": "ASCENDING" },
        { "fieldPath": "createdAt", "order": "DESCENDING" }
      ]
    }
  ],
  "fieldOverrides": []
}
```

### Security Rules (Firestore)
```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {

    // Deny all by default
    match /{document=**} {
      allow read, write: if false;
    }

    // Users — own data only
    match /users/{userId} {
      allow read: if request.auth != null && request.auth.uid == userId;
      allow create: if request.auth != null && request.auth.uid == userId;
      allow update: if request.auth != null && request.auth.uid == userId
                    && !request.resource.data.diff(resource.data).affectedKeys().hasAny(['role', 'createdAt']);
    }

    // Admin access
    match /{path=**} {
      allow read, write: if request.auth != null
                         && get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role == 'admin';
    }
  }
}
```

### Security Rules (Storage)
```
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    match /{allPaths=**} {
      allow read, write: if false;
    }

    match /users/{userId}/{allPaths=**} {
      allow read: if request.auth != null && request.auth.uid == userId;
      allow write: if request.auth != null && request.auth.uid == userId
                   && request.resource.size < 10 * 1024 * 1024
                   && request.resource.contentType.matches('image/.*');
    }
  }
}
```

### Cloud Functions Deployment Config
```typescript
// functions/src/index.ts
import { onRequest } from "firebase-functions/v2/https";
import { setGlobalOptions } from "firebase-functions/v2";

setGlobalOptions({
  region: "us-central1",
  memory: "256MiB",
  timeoutSeconds: 60,
  minInstances: 0,
  maxInstances: 100,
  concurrency: 80,
});

export const api = onRequest({ cors: true }, async (req, res) => {
  // API handler
});
```

### Firebase Emulator Suite Setup
```bash
# Install and start emulators
firebase init emulators
firebase emulators:start

# Start with data import/export for persistence
firebase emulators:start --import=./emulator-data --export-on-exit=./emulator-data

# Run tests against emulators
firebase emulators:exec "npm test"
```

## Step 4: GCP Infrastructure

### Cloud Run (Containerized Services)
```yaml
# cloud-run-service.yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: PROJECT_NAME-api
  annotations:
    run.googleapis.com/ingress: all
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/minScale: "0"
        autoscaling.knative.dev/maxScale: "10"
        run.googleapis.com/cpu-throttling: "true"
        run.googleapis.com/startup-cpu-boost: "true"
    spec:
      containerConcurrency: 80
      timeoutSeconds: 300
      containers:
        - image: gcr.io/PROJECT_ID/PROJECT_NAME-api:latest
          ports:
            - containerPort: 8080
          resources:
            limits:
              cpu: "1"
              memory: "512Mi"
          env:
            - name: NODE_ENV
              value: "production"
          startupProbe:
            httpGet:
              path: /health
              port: 8080
            initialDelaySeconds: 5
            periodSeconds: 10
          livenessProbe:
            httpGet:
              path: /health
              port: 8080
            periodSeconds: 30
```

Deploy: `gcloud run deploy PROJECT_NAME-api --source . --region us-central1 --allow-unauthenticated`

### Cloud Storage (Lifecycle Policies)
```bash
# Create buckets per environment
gsutil mb -l us-central1 gs://PROJECT_NAME-dev-uploads
gsutil mb -l us-central1 gs://PROJECT_NAME-prod-uploads

# Lifecycle policy — delete temp files after 30 days, archive after 90
cat > lifecycle.json << 'EOF'
{
  "lifecycle": {
    "rule": [
      {
        "action": { "type": "Delete" },
        "condition": { "age": 30, "matchesPrefix": ["tmp/"] }
      },
      {
        "action": { "type": "SetStorageClass", "storageClass": "NEARLINE" },
        "condition": { "age": 90, "matchesPrefix": ["backups/"] }
      }
    ]
  }
}
EOF
gsutil lifecycle set lifecycle.json gs://PROJECT_NAME-prod-uploads
```

### Secret Manager
```bash
# Create secrets
echo -n "sk_live_xxx" | gcloud secrets create stripe-secret-key --data-file=-
echo -n "SG.xxx" | gcloud secrets create sendgrid-api-key --data-file=-

# Grant Cloud Functions access
gcloud secrets add-iam-policy-binding stripe-secret-key \
  --member="serviceAccount:PROJECT_ID@appspot.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# Access in Cloud Functions
import { SecretManagerServiceClient } from "@google-cloud/secret-manager";
const client = new SecretManagerServiceClient();
const [version] = await client.accessSecretVersion({
  name: "projects/PROJECT_ID/secrets/stripe-secret-key/versions/latest",
});
```

### Cloud Scheduler (Cron Jobs)
```bash
# Daily cleanup job
gcloud scheduler jobs create http daily-cleanup \
  --schedule="0 3 * * *" \
  --uri="https://us-central1-PROJECT_ID.cloudfunctions.net/dailyCleanup" \
  --http-method=POST \
  --oidc-service-account-email=PROJECT_ID@appspot.gserviceaccount.com \
  --time-zone="America/New_York"

# Weekly report generation
gcloud scheduler jobs create http weekly-report \
  --schedule="0 9 * * MON" \
  --uri="https://us-central1-PROJECT_ID.cloudfunctions.net/generateReport" \
  --http-method=POST \
  --oidc-service-account-email=PROJECT_ID@appspot.gserviceaccount.com \
  --time-zone="America/New_York"
```

### VPC and Networking
```bash
# Create VPC for private services
gcloud compute networks create PROJECT_NAME-vpc --subnet-mode=custom

# Create subnet
gcloud compute networks subnets create PROJECT_NAME-subnet \
  --network=PROJECT_NAME-vpc \
  --region=us-central1 \
  --range=10.0.0.0/24

# VPC connector for Cloud Functions / Cloud Run to access private resources
gcloud compute networks vpc-access connectors create PROJECT_NAME-connector \
  --region=us-central1 \
  --network=PROJECT_NAME-vpc \
  --range=10.8.0.0/28 \
  --min-instances=2 \
  --max-instances=10
```

### IAM Roles and Service Accounts
```bash
# Create service account for CI/CD
gcloud iam service-accounts create ci-deploy \
  --display-name="CI/CD Deploy Service Account"

# Grant minimum required roles
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:ci-deploy@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/firebase.admin"

gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:ci-deploy@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:ci-deploy@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"

# Generate key for GitHub Actions
gcloud iam service-accounts keys create sa-key.json \
  --iam-account=ci-deploy@PROJECT_ID.iam.gserviceaccount.com
```

## Step 5: Vercel / Hosting Infrastructure

### vercel.json
```json
{
  "framework": "nextjs",
  "buildCommand": "npm run build",
  "installCommand": "npm ci",
  "regions": ["iad1"],
  "headers": [
    {
      "source": "/api/(.*)",
      "headers": [
        { "key": "Cache-Control", "value": "no-store, must-revalidate" },
        { "key": "X-Content-Type-Options", "value": "nosniff" }
      ]
    },
    {
      "source": "/(.*)",
      "headers": [
        { "key": "X-Frame-Options", "value": "DENY" },
        { "key": "X-Content-Type-Options", "value": "nosniff" },
        { "key": "Referrer-Policy", "value": "strict-origin-when-cross-origin" }
      ]
    }
  ],
  "redirects": [
    { "source": "/old-path", "destination": "/new-path", "statusCode": 301 }
  ],
  "rewrites": [
    { "source": "/api/:path*", "destination": "/api/:path*" }
  ]
}
```

### Environment Variables Management
```bash
# Set variables per environment
vercel env add NEXT_PUBLIC_FIREBASE_PROJECT_ID     # prompted for value and environment
vercel env add STRIPE_SECRET_KEY                    # production only, encrypted

# Pull env vars locally
vercel env pull .env.local

# Environment scoping
#   Production  → main branch deploys
#   Preview     → PR and branch deploys
#   Development → local via vercel dev
```

### Edge Functions Config
```typescript
// middleware.ts (Next.js Edge Middleware on Vercel)
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export const config = {
  matcher: ["/dashboard/:path*", "/api/:path*"],
};

export function middleware(request: NextRequest) {
  // Geo-based routing, auth checks, rate limiting at the edge
  const country = request.geo?.country || "US";
  const response = NextResponse.next();
  response.headers.set("x-country", country);
  return response;
}
```

### Domain and DNS Setup
```bash
# Add custom domain
vercel domains add example.com
vercel domains add www.example.com

# DNS records required:
#   A     @    76.76.21.21
#   CNAME www  cname.vercel-dns.com

# SSL is automatic via Let's Encrypt
```

### Preview Deployments
```
Every pull request gets a unique preview URL automatically:
  https://PROJECT-NAME-git-BRANCH-NAME-TEAM.vercel.app

Configure in vercel.json or dashboard:
  - Auto-assign custom preview domain
  - Comment on PR with preview link
  - Run checks before promoting to production
```

## Step 6: Docker Configuration

### Multi-Stage Dockerfile (Node.js)
```dockerfile
# --- Build stage ---
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production && cp -R node_modules /production_modules
RUN npm ci
COPY . .
RUN npm run build

# --- Production stage ---
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production

RUN addgroup --system --gid 1001 appgroup && \
    adduser --system --uid 1001 appuser

COPY --from=builder /production_modules ./node_modules
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/package.json ./

USER appuser
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:8080/health || exit 1
CMD ["node", "dist/index.js"]
```

### Multi-Stage Dockerfile (Python)
```dockerfile
# --- Build stage ---
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# --- Production stage ---
FROM python:3.12-slim AS runner
WORKDIR /app

RUN groupadd --system appgroup && \
    useradd --system --gid appgroup appuser

COPY --from=builder /install /usr/local
COPY . .

USER appuser
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')" || exit 1
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "4", "app:create_app()"]
```

### docker-compose.yml (Local Development)
```yaml
version: "3.9"

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
      target: builder
    ports:
      - "3000:3000"
    volumes:
      - .:/app
      - /app/node_modules
    environment:
      - NODE_ENV=development
    env_file:
      - .env.local
    depends_on:
      - redis
    command: npm run dev

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data

  firebase-emulators:
    image: andreysenov/firebase-tools
    ports:
      - "4000:4000"
      - "5001:5001"
      - "8080:8080"
      - "9099:9099"
      - "9199:9199"
    volumes:
      - .:/app
    working_dir: /app
    command: firebase emulators:start --import=./emulator-data

volumes:
  redis-data:
```

### .dockerignore
```
node_modules
.git
.gitignore
.env*
!.env.example
*.md
.firebase
.vercel
coverage
.nyc_output
dist
out
.next
firebase-debug.log
```

### Health Check Endpoint
```typescript
// src/health.ts
import { Router } from "express";

const router = Router();

router.get("/health", async (_req, res) => {
  const checks = {
    uptime: process.uptime(),
    timestamp: Date.now(),
    status: "ok",
  };
  res.status(200).json(checks);
});

router.get("/health/ready", async (_req, res) => {
  // Check downstream dependencies
  try {
    // await db.ping();
    // await redis.ping();
    res.status(200).json({ status: "ready" });
  } catch (error) {
    res.status(503).json({ status: "not ready", error: String(error) });
  }
});

export default router;
```

## Step 7: Environment Management

### Environment Separation Strategy
```
Environment     Firebase Project         Branch        Auto-Deploy
───────────────────────────────────────────────────────────────────
development     PROJECT_NAME-dev         feature/*     No (manual)
staging         PROJECT_NAME-staging     main          Yes
production      PROJECT_NAME-prod        release/*     Yes (with approval)
```

Rules:
- Each environment is a **separate Firebase project** — never share projects across environments
- Production deploys require **manual approval** via GitHub Environment protection rules
- Staging mirrors production config but with test data

### Secret Management
```
Secret Type             Where to Store                  Access Method
────────────────────────────────────────────────────────────────────────
Firebase config         .env.local (gitignored)         NEXT_PUBLIC_* vars
API keys (server)       GCP Secret Manager              secretmanager.accessSecretVersion()
API keys (CI/CD)        GitHub Secrets                  ${{ secrets.KEY_NAME }}
Service accounts        GCP Secret Manager / GitHub     JSON key (never in repo)
Database URLs           GCP Secret Manager              Runtime injection
Encryption keys         GCP KMS                         kms.encrypt() / decrypt()
```

Never commit: `.env`, `*-sa-key.json`, `*.p12`, `*.keystore`, `serviceAccountKey.json`

### Environment Variable Templates (.env.example)
```bash
# .env.example — commit this file, never commit .env or .env.local

# Firebase (client-side, safe to expose)
NEXT_PUBLIC_FIREBASE_API_KEY=
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=
NEXT_PUBLIC_FIREBASE_PROJECT_ID=
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=
NEXT_PUBLIC_FIREBASE_APP_ID=
NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID=

# Server-side only (never prefix with NEXT_PUBLIC_)
FIREBASE_SERVICE_ACCOUNT_KEY=
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
SENDGRID_API_KEY=
DATABASE_URL=

# App config
NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXT_PUBLIC_ENVIRONMENT=development
```

### Feature Flags Infrastructure
```typescript
// lib/feature-flags.ts
import { getRemoteConfig, fetchAndActivate, getValue } from "firebase/remote-config";

const remoteConfig = getRemoteConfig();
remoteConfig.settings.minimumFetchIntervalMillis = 3600000; // 1 hour in prod

// Default values
remoteConfig.defaultConfig = {
  enable_new_checkout: false,
  enable_dark_mode: false,
  max_upload_size_mb: 10,
  maintenance_mode: false,
};

export async function initFeatureFlags() {
  await fetchAndActivate(remoteConfig);
}

export function isEnabled(flag: string): boolean {
  return getValue(remoteConfig, flag).asBoolean();
}

export function getConfigValue(key: string): string {
  return getValue(remoteConfig, key).asString();
}
```

## Step 8: Monitoring & Observability

### Firebase Performance Monitoring
```typescript
// lib/firebase-perf.ts
import { getPerformance, trace } from "firebase/performance";

const perf = getPerformance();

// Custom trace for critical operations
export async function traceOperation<T>(name: string, operation: () => Promise<T>): Promise<T> {
  const t = trace(perf, name);
  t.start();
  try {
    const result = await operation();
    t.putAttribute("status", "success");
    return result;
  } catch (error) {
    t.putAttribute("status", "error");
    throw error;
  } finally {
    t.stop();
  }
}
```

### Cloud Monitoring Alerting Policies
```bash
# Alert on Cloud Functions error rate > 5%
gcloud monitoring policies create \
  --display-name="Cloud Functions Error Rate" \
  --condition-display-name="Error rate exceeds 5%" \
  --condition-filter='resource.type="cloud_function" AND metric.type="cloudfunctions.googleapis.com/function/execution_count" AND metric.labels.status!="ok"' \
  --condition-threshold-value=0.05 \
  --condition-threshold-comparison=COMPARISON_GT \
  --notification-channels=CHANNEL_ID \
  --combiner=OR

# Alert on high latency (p95 > 2s)
gcloud monitoring policies create \
  --display-name="API Latency Alert" \
  --condition-display-name="P95 latency exceeds 2 seconds" \
  --condition-filter='resource.type="cloud_function" AND metric.type="cloudfunctions.googleapis.com/function/execution_times"' \
  --condition-threshold-value=2000 \
  --condition-threshold-comparison=COMPARISON_GT \
  --notification-channels=CHANNEL_ID
```

### Error Reporting (Sentry)
```typescript
// lib/sentry.ts
import * as Sentry from "@sentry/nextjs";

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  environment: process.env.NEXT_PUBLIC_ENVIRONMENT,
  tracesSampleRate: process.env.NODE_ENV === "production" ? 0.1 : 1.0,
  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,
  integrations: [
    Sentry.replayIntegration(),
    Sentry.browserTracingIntegration(),
  ],
  ignoreErrors: [
    "ResizeObserver loop limit exceeded",
    "Non-Error promise rejection captured",
  ],
});
```

### Uptime Checks
```bash
# Create uptime check for production
gcloud monitoring uptime create PROJECT_NAME-web \
  --display-name="Production Web App" \
  --uri="https://example.com" \
  --http-method=GET \
  --check-interval=300 \
  --timeout=10 \
  --regions=usa,europe,asia

# Create uptime check for API
gcloud monitoring uptime create PROJECT_NAME-api \
  --display-name="Production API Health" \
  --uri="https://api.example.com/health" \
  --http-method=GET \
  --check-interval=60 \
  --timeout=10
```

### Log Aggregation
```bash
# Create log sink to BigQuery for analysis
gcloud logging sinks create bigquery-logs \
  bigquery.googleapis.com/projects/PROJECT_ID/datasets/app_logs \
  --log-filter='resource.type="cloud_function" OR resource.type="cloud_run_revision"'

# Create log-based metric for business events
gcloud logging metrics create user-signups \
  --description="Count of user signups" \
  --log-filter='resource.type="cloud_function" AND jsonPayload.event="user_signup"'

# Structured logging in Cloud Functions
import { logger } from "firebase-functions/v2";

logger.info("User signed up", {
  event: "user_signup",
  userId: user.uid,
  method: user.providerData[0]?.providerId,
});
```

## Step 9: Cost Optimization

### Firebase Billing Alerts
```bash
# Set budget alert at project level
gcloud billing budgets create \
  --billing-account=BILLING_ACCOUNT_ID \
  --display-name="PROJECT_NAME Monthly Budget" \
  --budget-amount=500 \
  --threshold-rule=percent=0.5 \
  --threshold-rule=percent=0.8 \
  --threshold-rule=percent=1.0 \
  --notifications-rule-pubsub-topic=projects/PROJECT_ID/topics/billing-alerts \
  --notifications-rule-monitoring-notification-channels=CHANNEL_ID
```

### Cloud Functions Min/Max Instances
```typescript
// Cost-optimized function configuration
import { onRequest } from "firebase-functions/v2/https";
import { onSchedule } from "firebase-functions/v2/scheduler";

// Low-traffic endpoint — scale to zero
export const webhook = onRequest({
  minInstances: 0,
  maxInstances: 10,
  memory: "256MiB",
  timeoutSeconds: 30,
}, handler);

// High-traffic API — keep warm, cap max
export const api = onRequest({
  minInstances: 1,       // avoid cold starts
  maxInstances: 50,      // cap costs
  memory: "512MiB",
  concurrency: 80,       // handle multiple requests per instance
}, handler);

// Scheduled job — minimal resources
export const dailyCleanup = onSchedule({
  schedule: "every day 03:00",
  memory: "256MiB",
  maxInstances: 1,
  timeoutSeconds: 540,
}, handler);
```

### Storage Lifecycle Policies
```json
{
  "lifecycle": {
    "rule": [
      {
        "action": { "type": "Delete" },
        "condition": { "age": 7, "matchesPrefix": ["tmp/", "cache/"] }
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
        "condition": { "age": 365, "matchesPrefix": ["logs/"] }
      }
    ]
  }
}
```

### Budget Alerts and Quotas
```
Cost Control Checklist:
  ✅ Set monthly budget with 50%, 80%, 100% alerts
  ✅ Cap Cloud Functions maxInstances (never unlimited)
  ✅ Set Firestore daily spending limit in console
  ✅ Use storage lifecycle rules to auto-archive/delete
  ✅ Enable per-service billing export to BigQuery
  ✅ Review billing dashboard weekly
  ✅ Set up anomaly detection alerts
  ✅ Use committed use discounts for predictable workloads

Estimated Costs (small-medium project):
  Firebase Hosting        — free tier covers most projects
  Cloud Functions         — $0.40/million invocations + compute time
  Firestore               — $0.06/100K reads, $0.18/100K writes
  Cloud Storage           — $0.020/GB/month (Standard)
  Cloud Run               — $0 when idle, ~$30-50/month at moderate traffic
  Secret Manager          — $0.06/10K access operations
```

## Code Generation (Required)

You MUST generate actual config files using the Write tool:

Based on detected stack, generate the appropriate configs:
- **Firebase**: `firebase.json`, `.firebaserc`, `firestore.rules`, `firestore.indexes.json`, `storage.rules`
- **Docker**: `Dockerfile` (multi-stage), `docker-compose.yml`, `.dockerignore`
- **Vercel**: `vercel.json`
- **Terraform**: `main.tf`, `variables.tf`, `outputs.tf`, `providers.tf`, `backend.tf`
- **Environment**: `.env.example` with all required variables documented

Before generating, use Glob to find existing configs and Read them. Enhance rather than replace.

## Cross-References

- `/ci-cd-pipeline` — for GitHub Actions workflows that deploy these infrastructure configs
- `/firebase-architect` — for Firestore schema and security rules design
- `/security-review` — for IAM least-privilege, secret management, and network security standards
- `/database-architect` — for database instance configuration and connection pooling

## Step 10: Output

Generate all configuration files as ready-to-use artifacts:

```
project-root/
├── firebase.json
├── .firebaserc
├── firestore.rules
├── firestore.indexes.json
├── storage.rules
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── vercel.json                   (if using Vercel)
├── cloud-run-service.yaml        (if using Cloud Run)
├── .env.example
├── lib/
│   ├── feature-flags.ts
│   ├── firebase-perf.ts
│   └── sentry.ts
└── functions/
    └── src/
        └── index.ts
```

Deliver each file with environment-specific placeholders (`PROJECT_NAME`, `PROJECT_ID`) for the team to fill in. All configs should be production-ready with security defaults, cost controls, and monitoring enabled from day one.
