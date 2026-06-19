# infrastructure-scaffold: detailed reference

> Reference material for the `infrastructure-scaffold` skill, split out for progressive disclosure. Loaded on demand from SKILL.md.

## Contents
- Step 3: Firebase Infrastructure
- Step 4: GCP Infrastructure
- Step 6: Docker Configuration

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
