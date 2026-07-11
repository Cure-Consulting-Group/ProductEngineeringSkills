---
name: env-secrets-manager
description: ".env hygiene, secret leak detection, rotation playbooks, and migration to managed secret stores — read-only audits"
when_to_use: "Use when designing .env schema, auditing for leaked secrets, responding to a leak, planning rotation, or migrating to a secret manager. NOT cloud-IAM design (security-review) or infra scaffolding (infrastructure-scaffold)."
argument-hint: "[scope: greenfield | audit | leak-response | rotation | migrate]"
allowed-tools: ["Read", "Grep", "Glob", "Bash"]
context: fork
---

# Environment Secrets Manager

Read-only skill for auditing and designing how a codebase handles environment variables and secrets. This skill never writes to `.env` files directly — it produces schemas, audit reports, runbooks, and migration plans for the team to apply. The default operating assumption: every secret in a `.env` file is one careless commit away from being public.

## Pre-Processing (Auto-Context)

Project context, gathered before the skill runs. Values are injected inline below; in an environment that does not execute them (e.g. Gemini), run the shown commands instead.

- Portfolio: !`sed -n '1,40p' PORTFOLIO.md 2>/dev/null || echo "(no PORTFOLIO.md)"`
- Stack manifest: !`head -40 package.json 2>/dev/null || head -40 build.gradle.kts 2>/dev/null || head -20 Podfile 2>/dev/null || echo "(none detected)"`
- Recent commits: !`git log --oneline -5 2>/dev/null || echo "(not a git repo)"`
- Layout: !`ls src/ app/ lib/ functions/ 2>/dev/null | head -25`

Use this context to tailor all output to the actual project.

Additionally gather (domain-specific):
- Glob for: `.env*`, `.envrc`, `*.env`, `secrets/**`, `**/serviceAccount*.json` to map current secret surface
- Run: `git ls-files | grep -E '\.env($|\.[a-z]+$)' 2>/dev/null` to detect any committed env files (red flag)

Never print actual secret values. If a secret value is detected during scanning, redact it as `[REDACTED:KEY_NAME]` in all output.

## Step 1: Classify the Engagement

| Scope | Trigger | Primary Output |
|-------|---------|----------------|
| Greenfield design | New project, no existing `.env` | Schema design + `.env.example` blueprint + boot validation pattern |
| Audit | Existing repo, no known incident | Findings report with severity, file:line refs, remediation effort |
| Leak response | Secret pushed to git / leaked in logs / exposed in client-side bundle | Incident timeline + revoke-rotate-deploy-verify runbook |
| Rotation cadence | "How often should we rotate X?" | Per-credential rotation matrix + automation hooks |
| Manager migration | Moving off `.env` to Doppler / Secret Manager / Vault | Phased rollout plan with shimming and cutover criteria |

If the request is ambiguous, ask which scope before proceeding. Don't pretend to do all five at once — each has different deliverables and different audiences.

## Step 2: Gather Context

Ask (or infer from auto-context):

1. **Environment count** — local, dev, staging, prod, preview-per-PR? Each is a separate config surface.
2. **Team size and trust model** — solo, 2-5, 10+? Does every engineer need every secret, or are prod secrets restricted to ops?
3. **Existing secret manager** — None / Doppler / 1Password CLI / AWS Secrets Manager / GCP Secret Manager / HashiCorp Vault / Infisical / Akeyless? Don't recommend a migration before knowing what's already there.
4. **Language / framework** — affects validation library choice (`zod`, `envalid`, `pydantic-settings`, `viper`, `figment`).
5. **Deployment target** — Vercel / Firebase / Cloud Run / EKS / bare VMs? Each has a native secret-injection path that should replace `.env` in production.
6. **Compliance posture** — SOC 2, HIPAA, PCI? Audit-trail requirements change the recommendation.
7. **Incident history** — has a secret leaked before? If yes, was it rotated and was the leak vector closed?

## Step 3: Schema Design (.env.example as Source of Truth)

The `.env.example` file is the contract. Every variable the app reads at boot must appear there. Anything in a developer's `.env` that isn't in `.env.example` is an undocumented dependency.

### Naming Conventions
- `UPPER_SNAKE_CASE` — no exceptions, no mixed case, no dots, no dashes.
- Group by domain prefix:
  ```
  DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME
  AUTH_JWT_SECRET, AUTH_SESSION_TTL_SECONDS, AUTH_ALLOWED_ORIGINS
  STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET, STRIPE_PUBLIC_KEY
  SENDGRID_API_KEY, SENDGRID_FROM_ADDRESS
  REDIS_URL
  SENTRY_DSN, SENTRY_ENVIRONMENT
  APP_ENV, APP_BASE_URL, APP_LOG_LEVEL
  ```
- Public-by-design variables (client bundle, mobile build) get an explicit prefix: `NEXT_PUBLIC_`, `VITE_`, `EXPO_PUBLIC_`, `REACT_NATIVE_`. If a key has that prefix, treat it as public and never put a server secret behind it.
- Booleans: `true` / `false` literal strings, parsed at boot. Numerics: parse explicitly, never read as string-and-pray.

### Required vs. Optional
Annotate every variable in `.env.example`:
```
# REQUIRED — server will refuse to start without this
DB_URL=postgres://user:pass@host:5432/db

# REQUIRED in production, OPTIONAL locally (falls back to console transport)
SENDGRID_API_KEY=

# OPTIONAL — defaults to "info"
APP_LOG_LEVEL=info
```

### Boot-Time Validation (Required Pattern)
Every service must validate its env at startup and fail loud with a clear message. Recommend (do not write — recommend) one of:
- TypeScript / Node: `zod` or `envalid` schema in `src/env.ts`, imported once at boot.
- Python: `pydantic-settings` `BaseSettings` class.
- Go: `kelseyhightower/envconfig` or `spf13/viper` with required tags.
- Rust: `figment` or `envy` with `Deserialize` and explicit defaults.

Failure mode: process exits with code 1 and prints which variables are missing. Never silently default a secret.

## Step 4: Leak Detection

Run these as a layered defense — pre-commit, CI, and history scan.

### History Scan (Run Once on Every New Engagement)
```bash
# Trufflehog — broad detector, scans full git history
trufflehog git file://. --only-verified

# Gitleaks — fast, pattern-based, supports custom rules
gitleaks detect --source . --redact --report-path gitleaks-report.json

# git-secrets — AWS-focused, lighter weight
git secrets --scan-history
```

If any of these find a verified leak in history: do not just delete the file in HEAD. The secret is in the git objects forever. Treat as leak-response (Step 5).

### Pre-Commit Hook (Block Before Push)
Recommend installing `gitleaks` or `trufflehog` as a `pre-commit` hook via the `pre-commit` framework. The hook should fail the commit if a candidate secret is detected. Document the override path (`--no-verify`) and make it auditable — abuse of `--no-verify` is itself a finding.

### CI Check (Catch What Slips Past)
Add a CI job that re-runs the scanner on the diff and on full history weekly. Failures must block merge. Output the report as a build artifact, never echo raw matches into the log.

### Common Leak Vectors to Search
| Vector | Grep / Search |
|--------|---------------|
| `.env` committed | `git ls-files \| grep -E '\.env'` |
| Secrets in client bundle | Grep build output for `sk_live`, `AIza`, `ghp_`, `AKIA` |
| Secrets in CI logs | Search workflow runs for printed env values; `set -x` with secrets is a finding |
| Secrets in error messages | Stack traces echoing connection strings |
| Secrets in Slack / Linear / GitHub issues | Out of scope for code, but flag the policy gap |
| Secrets in Docker images | `docker history IMAGE` and `dive IMAGE` to inspect layers |
| Secrets in mobile bundles | iOS `Info.plist`, Android `BuildConfig`, decompiled APK strings |

## Step 5: Leak Response Runbook

When a secret has demonstrably leaked, follow this order. Speed matters more than perfection.

```
1. DETECT — confirm leak (which secret, which surface, when, who saw it)
2. REVOKE — disable the credential at the issuing system FIRST
                (Stripe dashboard, GCP IAM, AWS console, GitHub PAT settings)
                Revoke before rotating — a rotated-but-not-revoked key is still live
3. ROTATE — generate a replacement credential with new value
4. DEPLOY — push new value to all environments that consume it
                Use blue/green or rolling restart; never edit prod env in place
5. VERIFY — health-check every service that depends on the credential
                Check error rates for the next 30 minutes
6. SCRUB — remove the leaked value from the original surface where possible
                Force-push history rewrite (BFG / git-filter-repo) if leak was in git
                Note: history rewrite does NOT undo the leak — assume it was scraped
7. POSTMORTEM — document timeline, blast radius, prevention
                File a finding in the repo's incident log
```

### Minimum-Downtime DB Credential Rotation
Database credentials need a special pattern because the app is always reading them.
```
1. Add a NEW database user (DB_USER_NEXT) with the same grants
2. Deploy app config that supports BOTH credentials, preferring NEXT
   (or use a connection-pool-level swap)
3. Verify NEXT is in use (query pg_stat_activity / SHOW PROCESSLIST)
4. Revoke the OLD user's grants — but keep the user for 24h in case of rollback
5. Redeploy with only NEXT configured
6. Drop the OLD user after 24h soak
```

For services that support it (Cloud SQL, RDS), prefer IAM-based auth so credentials are short-lived tokens, not static passwords.

## Step 6: Secret Manager Migration

Don't migrate everything in one PR. Phase the rollout.

| Phase | Action | Exit Criteria |
|-------|--------|---------------|
| 0. Inventory | List every secret across every environment, with consumer service and owner | Spreadsheet with no "unknown" rows |
| 1. Choose manager | Doppler (devex-first) / GCP Secret Manager (GCP-native) / AWS Secrets Manager (AWS-native) / 1Password CLI (small teams) / Vault (regulated) | ADR written, team aligned |
| 2. Shim | App reads from manager **with `.env` fallback**. New code uses manager API; old code keeps working | Both paths green in CI |
| 3. Migrate per-service | One service at a time, lowest-risk first (background workers, then APIs, then auth-critical) | Each service flips, observed for 1 week |
| 4. Remove fallback | Delete `.env` reading code path. App refuses to start without manager | All services in steady state for 2 weeks |
| 5. Cleanup | Delete `.env.production` files from any deploy pipeline; rotate all migrated secrets (assume the migration window itself was a leak risk) | Zero `.env*` files in any prod artifact |

### Workload Identity Over Static Tokens
On GCP, AWS, and Kubernetes, prefer workload identity (service accounts attached to compute) over static API tokens to the secret manager. Eliminates the "token to fetch tokens" bootstrap problem. Document this preference in the ADR.

## Step 7: Local Development

| Rule | Why |
|------|-----|
| `.env.example` is committed | Source of truth for required vars |
| `.env`, `.env.local`, `.env.*.local` are in `.gitignore` | Never commit |
| New developers run `cp .env.example .env` and fill blanks | Onboarding contract |
| Team-shared dev secrets go through a tool, not Slack | Doppler, 1Password CLI, dotenv-vault, Infisical CLI |
| `.envrc` (direnv) is acceptable, but must also be in `.gitignore` if it contains values | Common foot-gun |
| README documents how to obtain each secret | Reduces "ask the lead in DM" pattern |

Anti-pattern: a Slack channel called `#dev-credentials` where people paste `.env` contents. This is a finding even if the channel is private.

## Step 8: Production

| Platform | Native Secret Path (Use This) | Avoid |
|----------|-------------------------------|-------|
| Vercel | Project Environment Variables (UI or `vercel env`) | `.env` files in the deploy artifact |
| Firebase Functions / Cloud Run | GCP Secret Manager + workload identity | `functions:config:set` (deprecated for secrets) |
| AWS Lambda / ECS | Secrets Manager / Parameter Store + IAM role | Secrets in task definition env block |
| Kubernetes | External Secrets Operator pulling from a manager + IRSA / Workload Identity | Plain `Secret` objects (base64 ≠ encrypted) |
| Bare VMs / Docker Compose | Manager fetched at boot via init script | `.env` baked into image |
| Mobile | Build-time injection of public values only; server-side proxy for everything else | API keys in app bundle |

### Container Hygiene
- Never `COPY .env .env` in a Dockerfile.
- Never `ARG` a secret — `ARG` values appear in image layer metadata.
- Use `--secret` (BuildKit) for build-time secrets; runtime secrets come from the orchestrator.
- Add `.env*` to `.dockerignore` (with `!.env.example` if the example is needed at build).

## Step 9: Audit Report Output

```
ENVIRONMENT SECRETS AUDIT
Project: [NAME]
Date: [DATE]
Auditor: [NAME], Cure Consulting Group

SCOPE
  Environments reviewed: local, dev, staging, prod
  Repos reviewed: [LIST]
  Time window: [DATE_RANGE]

FINDING SUMMARY
┌───────────────────────────────┬──────────┬───────┐
│ Category                      │ Severity │ Count │
├───────────────────────────────┼──────────┼───────┤
│ Committed secrets in history  │ CRITICAL │   X   │
│ Missing boot-time validation  │ HIGH     │   X   │
│ Public prefix on server keys  │ HIGH     │   X   │
│ No rotation cadence           │ MEDIUM   │   X   │
│ .env in Docker image          │ HIGH     │   X   │
│ Secrets via Slack/email       │ MEDIUM   │   X   │
│ Missing .env.example entries  │ LOW      │   X   │
└───────────────────────────────┴──────────┴───────┘

CRITICAL (revoke + rotate today):
  1. [SECRET_NAME] — committed in [COMMIT_SHA] at [PATH]:[LINE] — [REMEDIATION]

HIGH (fix this sprint):
  1. [Issue] — [Risk] — [Fix] — [Effort]

MEDIUM (next quarter):
  1. ...

ROTATION MATRIX
┌─────────────────────┬──────────────┬────────────┬──────────────┐
│ Credential          │ Cadence      │ Method     │ Owner        │
├─────────────────────┼──────────────┼────────────┼──────────────┤
│ DB password         │ 90 days      │ Automated  │ Platform     │
│ Stripe secret key   │ On personnel │ Manual     │ Finance lead │
│ JWT signing secret  │ 30 days      │ Automated  │ Backend      │
│ Service account key │ 60 days      │ Workload ID│ Platform     │
│ Third-party API     │ 180 days     │ Manual     │ Service owner│
└─────────────────────┴──────────────┴────────────┴──────────────┘
```

## When NOT to Use This Skill

- **Cloud IAM design** — use `/security-review` and the cloud provider's IAM tooling.
- **Full infrastructure setup** — use `/infrastructure-scaffold`; this skill assumes infra exists.
- **Secret-storing applications** (e.g., a password manager you're building) — that's a cryptography problem, not a config-hygiene problem.
- **Encrypted-at-rest data** for end users — use field-level encryption guidance from `/security-review`.
- **You want me to write the actual `.env` file** — this skill is read-only. Write the values yourself in your secret manager or local `.env`.

## Anti-Patterns (All Findings)

- `.env` baked into a Docker image or Kubernetes ConfigMap.
- Secrets echoed in CI logs (any `set -x`, `printenv`, `env | grep` against secrets).
- Sharing `.env` via Slack DM, email, Notion, Google Doc.
- "Temporary" hardcoded secret with a `// TODO: move to env` comment older than 7 days.
- Public prefix (`NEXT_PUBLIC_`, `VITE_`) on a server-only secret.
- Single shared production secret used by every developer for "easier debugging."
- No rotation cadence — same Stripe key in use for 4 years.
- Secrets in mobile app bundles (decompiled APK / IPA reveals all).
- Service-to-service auth using a long-lived bearer token instead of workload identity.
- A single `OPS_GOD_KEY` env var with broad permissions used "to make CI work."
- `git push --force` to "remove" a leaked secret — the value is already scraped; rotate it.

## Cross-References

- `/security-review` — broader OWASP audit; this skill is the secrets-specific deep dive.
- `/infrastructure-scaffold` — for generating the `.env.example` and IAM scaffolding when standing up new infra.
- `/incident-response` — when a leak escalates to a full security incident.
- `/ci-cd-pipeline` — for wiring leak scanners into GitHub Actions.
- `/client-handoff` — credential transfer protocol when ending an engagement.
