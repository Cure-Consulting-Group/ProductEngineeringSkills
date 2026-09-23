---
name: client-handoff
description: "Builds client handoff packages: architecture, runbooks, credential transfer, KT plan, SLA. Use when handing a project, phase, or support role to a client team or winding down an engagement."
when_to_use: "NOT for weekly status or escalations (use client-communication). NOT for incident response during a live outage (use incident-response)."
argument-hint: "[project-name]"
context: fork
metadata:
  verified: 2026-09-23
---

# Client Handoff

**Outcome:** a handoff package the client team can operate from without Cure — deployable by them,
every credential under their ownership, Cure access revoked. Done when every item in the Step 8
sign-off checklist has an owner and a status. Match length to the need; no filler sections or
restated summaries.

Cure rule: a project is not "done" until the client has performed at least one independent
production deploy and a rollback.

## Pre-Processing (Auto-Context)

Context — run these read-only commands first; skip any that fail or aren't permitted (they only tailor the output):

- Stack manifest: `head -30 package.json 2>/dev/null || head -30 build.gradle.kts 2>/dev/null || echo "(none detected)"`
- Infra and CI files: `ls firebase.json *.tf Dockerfile vercel.json .github/workflows/ fastlane/ 2>/dev/null | head -15 || echo "(none)"`
- Env template: `ls .env.example .env.sample 2>/dev/null || echo "(no .env.example)"`

## Step 1: Classify the Handoff

| Type | Timeline | Priority deliverables |
|------|----------|-----------------------|
| Full project handoff | 2–4 weeks | Everything below + shadowing period |
| Phase completion | 3–5 days | Module docs, integration guide, test results, demo recording |
| Maintenance transition | 1–2 weeks | Runbooks, monitoring, SLA, escalation paths |
| Emergency handoff | 1–3 days | Credentials + ability to deploy + critical runbooks, in that order |

## Step 2: Gather Context

Scan the repo (manifests, infra configs, `.env.example`, CI workflows, `fastlane/`) for the
component, dependency, environment, and deploy inventories. Then ask the user for what the code
can't tell you:

1. Receiving team maturity and roles (senior/junior/non-technical; backend, mobile, DevOps).
2. Ongoing support — retainer or clean break?
3. Self-sufficiency deadline and any contractual dates.
4. Client's own tooling (CI, monitoring, ticketing) if it differs from what was built.
5. Compliance needs (SOC 2 audit trail, HIPAA, data-handling procedures).

## Step 3: Documentation Package

Produce, in this order of importance:

1. **Environment guide** — table of environment → project/account → URL → deploy method
   (e.g. dev: emulator/manual; staging: auto on `main`; prod: manual approval), plus local setup
   steps (clone, install, copy `.env.example`, start emulators, run). State where secrets live
   (1Password vault / Secret Manager) — never the secrets themselves.
2. **Service and account inventory** — service, purpose, account owner, plan, renewal date. Mark
   every service still owned by a Cure account `←XFER`; each must move to client ownership before
   sign-off. Record the plan name, not a price — prices drift; the client confirms current cost
   on their invoice.
3. **Expiry register** — domains, Apple Developer Program membership, SSL (usually auto-renewed),
   APNs. For push, hand off an **APNs auth key (.p8)**, which doesn't expire (it can be revoked),
   instead of a yearly APNs certificate; if the project still uses a certificate, list its expiry
   and recommend migrating. Android: note whether Play App Signing holds the app signing key and
   where the upload key is stored. FCM sends use the HTTP v1 API with a service account — the
   legacy server key no longer works.
4. **Architecture overview** — what the system does and for whom, a Mermaid diagram of services,
   data flows, and external integrations, component responsibilities, stack table.
5. **Known issues / tech-debt register** — issue, severity, recommended fix, effort. High items are
   fixed before handoff or explicitly accepted in writing by the client.

Read `reference/details.md` when drafting the architecture doc, the KT session plan, or the SLA —
it holds those long-form templates.

## Step 4: Runbooks

Format every runbook as numbered steps with exact commands, a verification check after each
deploy step, and a named escalation path. (In Claude Code the `runbook` output style applies this
format; elsewhere, follow it directly.)

**Deployment runbook** — one section per platform actually present:

```
WEB (Vercel / Firebase Hosting)
  1. Merge to main → CI runs lint → test → build → deploy to staging
  2. Verify staging at [URL]
  3. Promote to production via [approval step / release PR]
  4. Verify production at [URL]; tag vX.Y.Z
  Rollback: Vercel — `vercel rollback` (or Instant Rollback in the dashboard);
            Firebase Hosting — console → Hosting → release history → Roll back

CLOUD FUNCTIONS
  1. `npm test` in functions/  2. `firebase deploy --only functions --project <prod-alias>`
  3. Check function logs for errors
  Rollback: redeploy the previous git tag (Functions has no one-click rollback)

iOS    bump version → `fastlane ios release` (or Xcode Cloud) → TestFlight → App Store Connect
       release → watch Crashlytics 24 h
ANDROID bump versionCode → `fastlane android release` → internal track → staged rollout
       10% → 50% → 100% → watch Crashlytics and Play vitals 48 h. Halt the rollout to stop it.
```

**Incident runbook** — first-responder checklist (dashboard, Crashlytics, Sentry, console, function
logs — each with its URL), then symptom → likely cause → check → escalate-to for the top failure
modes of this system. Always cover: app crashes on start (config mismatch), payments failing
(webhook secret rotated / key revoked), function timeouts (cold start or slow downstream), auth
failures (provider config), database slowness (missing composite index, hot document), pushes not
delivered (revoked .p8 key, stale tokens). Use the `incident-response` skill for severity and
comms.

**Troubleshooting guide** — the ten questions the client team will actually ask, drawn from the
project's own history (CI failures, emulator port conflicts, rules rejections, Stripe webhook 400s
from secret mismatch, wrong API base URL per environment, analytics delay — use DebugView).

**Monitoring runbook** — for each alert: what it means and the first thing to check. Thresholds come
from the `observability` skill; don't invent new ones here.

## Step 5: Credential and Access Transfer

Inventory every credential: name, type, current holder, transfer target (service accounts, API
keys, Stripe, Sentry, signing keys and keystores, deploy keys, CI secrets, registrar, paging).

Transfer protocol — credentials never travel over email, chat, shared docs, or git, because those
channels retain copies Cure can't revoke:

1. Prefer regeneration: the client creates new accounts/keys (new Sentry project, new email
   provider key) so nothing is transferred at all.
2. For credentials that can't be regenerated (keystores, registrar logins): transfer through a
   shared password-manager vault, the client's secret manager, an expiring encrypted send, or in
   person; client confirms receipt, then rotates.
3. Cure revokes its own access within 48 hours of confirmed transfer: cloud projects (all
   environments), GitHub org, Stripe, hosting, App Store Connect, Play Console, paging; disable
   Cure service accounts; rotate every shared key.
4. Client verifies every service works on the new credentials; Cure deletes its copies.

## Step 6: Knowledge Transfer

Default five recorded sessions: architecture (2 h, whole team) → codebase tour and "add a feature"
walkthrough (3 h) → deploy and operations incl. a live staging deploy and a rollback (2 h) →
infrastructure and cost (1.5 h, eng lead + finance) → Q&A and shadowing kickoff (1 h). Recordings
go to the client's storage within 24 hours. Shadowing: weeks 1–2 Cure leads and client shadows;
weeks 3–4 client leads, Cure only answers. Every question asked becomes an FAQ entry.

## Step 7: Maintenance SLA (if a retainer continues)

Severity P0 (down, data loss, breach, payments broken) through P3 (cosmetic); in scope = bug fixes,
security patches, dependency updates, infra upkeep; out of scope = new features (separate SOW).
Billing as retainer, T&M, or hybrid. Response and resolution targets and billing terms are
commercial decisions — take them from the SOW; the reference file has a default table. Use the
`legal-doc-scaffold` skill for the signed SLA document.

## Step 8: Sign-Off Checklist

```
HANDOFF SIGN-OFF — [Project] — [Date] — Cure: [Name] / Client: [Name]
DOCUMENTATION  [ ] Env guide  [ ] Service inventory, no ←XFER left  [ ] Expiry register
               [ ] Architecture doc  [ ] Tech-debt register reviewed  [ ] API docs accessible
RUNBOOKS       [ ] Deploy (every platform)  [ ] Incident  [ ] Troubleshooting  [ ] Monitoring
ACCESS         [ ] Credentials transferred via approved channel  [ ] Client rotated keys
               [ ] Cure access revoked everywhere  [ ] Client deployed to prod unaided
               [ ] Client performed a rollback
KT             [ ] Sessions held and recorded  [ ] Shadowing complete  [ ] FAQ delivered
SOURCE         [ ] Repos in client org, history intact  [ ] Branch protection  [ ] CI on client accounts
MAINTENANCE    [ ] SLA signed  [ ] Escalation contacts  [ ] Billing terms (if applicable)
Signatures: Client ______ Date ____   Cure ______ Date ____
```

## Artifact Generation

Applies when the classification calls for a package (full, maintenance, or emergency handoff) and
the user wants files. Write only the sections the handoff type needs, under `docs/handoff/`
(`environment.md`, `services.md`, `architecture.md`, `runbook.md`, `credentials.md`,
`kt-plan.md`, `maintenance-sla.md`, `sign-off.md`). Credentials files list names and locations,
never values. For a question or a single section, answer inline.

## Related Skills

`client-communication` (status during the handoff), `incident-response` (incident runbooks),
`infrastructure-scaffold` (infra docs), `legal-doc-scaffold` (SLA/SOW), `project-manager`
(handoff sprint plan).
