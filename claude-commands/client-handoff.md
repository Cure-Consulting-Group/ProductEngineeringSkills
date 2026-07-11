# Client Handoff

Structured handoff framework for consulting engagements at Cure Consulting Group. Every project leaves the client with complete documentation, operational runbooks, secure credential transfers, and a knowledge transfer plan. No project is "done" until the client can operate it independently.

## Pre-Processing (Auto-Context)

Before starting, gather project context silently:
- Read `PORTFOLIO.md` if it exists in the project root or parent directories for product/team context
- Run: `cat package.json 2>/dev/null || cat build.gradle.kts 2>/dev/null || cat Podfile 2>/dev/null` to detect stack
- Run: `git log --oneline -5 2>/dev/null` for recent changes
- Run: `ls src/ app/ lib/ functions/ 2>/dev/null` to understand project structure
- Use this context to tailor all output to the actual project

## Step 1: Classify the Handoff Type

| Type | Scope | Timeline | Key Deliverables |
|------|-------|----------|-----------------|
| Full project handoff | Complete transfer of ownership — code, infra, accounts, knowledge | 2-4 weeks | Full documentation package, all credentials, KT sessions, shadowing period |
| Phase completion | Milestone delivery within ongoing engagement — hand off a module or feature | 3-5 days | Module docs, integration guide, test results, demo recording |
| Maintenance transition | Move from active development to support/maintenance mode | 1-2 weeks | Runbooks, monitoring setup, SLA agreement, escalation paths |
| Emergency handoff | Unplanned transfer — consultant unavailable, client relationship change | 1-3 days | Priority: credentials + deployment ability + critical runbooks |

## Automated Discovery

Before creating handoff package, auto-scan the project:
1. **Architecture**: Glob for all major file types, count by extension, detect frameworks
2. **Dependencies**: Read package.json/build.gradle for dependency inventory
3. **Infrastructure**: Glob for Docker, Terraform, firebase.json configs
4. **Environment vars**: Glob for .env.example to document required variables
5. **CI/CD**: Read .github/workflows/ to document deployment process

## Artifact Generation (Required)

Generate handoff documentation using Write:
1. **Architecture diagram**: `docs/handoff/architecture.md` — Mermaid diagram of system components
2. **Dependency inventory**: `docs/handoff/dependencies.md` — all deps with versions and purposes
3. **Runbook**: `docs/handoff/runbook.md` — using runbook output style
4. **Credential checklist**: `docs/handoff/credentials.md` — all services requiring access
5. **Maintenance SLA**: `docs/handoff/maintenance-sla.md` — response times, update schedule

## Step 2: Gather Context

1. **Client technical maturity** -- does the receiving team have senior engineers, junior team, or non-technical stakeholders? This determines documentation depth.
2. **Receiving team size** -- how many people need to be onboarded, and what are their roles (backend, frontend, mobile, DevOps)?
3. **Ongoing support scope** -- will Cure continue with a maintenance retainer, or is this a clean break?
4. **Timeline** -- when must the client be fully self-sufficient? Are there contractual deadlines?
5. **Project complexity** -- how many services, platforms, third-party integrations, and environments?
6. **Client's existing tooling** -- do they use different CI/CD, monitoring, or project management tools than what was built?
7. **Compliance requirements** -- SOC 2 audit trail, HIPAA documentation, data handling procedures?

## Step 3: Handoff Documentation Package

### 3.1 Architecture Overview

```
ARCHITECTURE DOCUMENT
Project: [PROJECT_NAME]
Version: [X.Y.Z]
Last Updated: [DATE]
Author: [NAME], Cure Consulting Group

SYSTEM OVERVIEW
  [2-3 paragraph description of what the system does, who uses it,
   and the key business problems it solves.]

ARCHITECTURE DIAGRAM
  [Include a Mermaid or ASCII diagram showing all services,
   data flows, and external integrations.]

  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
  │  Mobile App  │───→│  Firebase    │───→│  Cloud       │
  │  (iOS/Android)│   │  Auth        │    │  Functions   │
  └──────────────┘    └──────────────┘    └──────┬───────┘
                                                 │
                      ┌──────────────┐    ┌──────┴───────┐
                      │  Stripe      │←───│  Firestore   │
                      │  Payments    │    │  Database    │
                      └──────────────┘    └──────────────┘

COMPONENT RESPONSIBILITIES
┌────────────────────┬──────────────────────────────────────────────┐
│ Component          │ Responsibility                               │
├────────────────────┼──────────────────────────────────────────────┤
│ Mobile App         │ User-facing iOS/Android application          │
│ Next.js Web App    │ Web dashboard and marketing site             │
│ Cloud Functions    │ API endpoints, webhooks, background tasks    │
│ Firestore          │ Primary datastore, real-time sync            │
│ Firebase Auth      │ Authentication, user management              │
│ Cloud Storage      │ File uploads, media storage                  │
│ Stripe             │ Payment processing, subscriptions            │
│ SendGrid           │ Transactional and marketing email            │
│ Firebase Analytics │ Event tracking, user behavior                │
└────────────────────┴──────────────────────────────────────────────┘

DATA FLOW
  [Describe the primary data flows: user signup, order creation,
   payment processing, notification delivery, etc.]

TECHNOLOGY STACK
┌─────────────────┬──────────────────────────────────┐
│ Layer           │ Technology                        │
├─────────────────┼──────────────────────────────────┤
│ Mobile (Android)│ Kotlin, Jetpack Compose, Hilt    │
│ Mobile (iOS)    │ Swift, SwiftUI                   │
│ Web Frontend    │ Next.js, TypeScript, Tailwind    │
│ Backend         │ Firebase Cloud Functions v2      │
│ Database        │ Firestore                        │
│ Auth            │ Firebase Authentication           │
│ Payments        │ Stripe                           │
│ CI/CD           │ GitHub Actions                   │
│ Hosting         │ Firebase Hosting / Vercel        │
│ Monitoring      │ Crashlytics, Sentry, Cloud Mon.  │
└─────────────────┴──────────────────────────────────┘
```

### 3.2 Environment Guide

```
ENVIRONMENT INVENTORY
┌─────────────┬────────────────────┬───────────────┬──────────────────┐
│ Environment │ Firebase Project   │ URL           │ Deploy Method    │
├─────────────┼────────────────────┼───────────────┼──────────────────┤
│ Development │ project-dev        │ localhost     │ Manual / emulator│
│ Staging     │ project-staging    │ staging.app   │ Auto on main     │
│ Production  │ project-prod       │ app.com       │ Manual approval  │
└─────────────┴────────────────────┴───────────────┴──────────────────┘

ACCESS INSTRUCTIONS
  Development:
    1. Clone repository: git clone [REPO_URL]
    2. Install dependencies: npm install
    3. Copy .env.example to .env.local and fill in dev values
    4. Start emulators: firebase emulators:start
    5. Start app: npm run dev

  Staging:
    1. Access Firebase Console: console.firebase.google.com (project-staging)
    2. Deploys happen automatically on push to main branch
    3. Staging URL: https://staging.app.com

  Production:
    1. Access Firebase Console: console.firebase.google.com (project-prod)
    2. Deploy requires GitHub Actions workflow approval
    3. Production URL: https://app.com

CREDENTIALS LOCATION
  See Step 5 (Credential and Access Transfer) for complete inventory.
  All credentials are stored in [1Password vault / GCP Secret Manager].
  Never stored in: email, Slack, plain text files, git repositories.
```

### 3.3 Dependency Inventory

```
THIRD-PARTY SERVICE INVENTORY
┌────────────────┬──────────────┬──────────────┬─────────────┬───────────────┐
│ Service        │ Purpose      │ Account Owner│ License/Plan│ Expiry/Renewal│
├────────────────┼──────────────┼──────────────┼─────────────┼───────────────┤
│ Firebase       │ Backend      │ client@co    │ Blaze (PAYG)│ N/A           │
│ Stripe         │ Payments     │ client@co    │ Standard    │ N/A           │
│ SendGrid       │ Email        │ client@co    │ Pro ($90/mo)│ [DATE]        │
│ Sentry         │ Error tracking│ cure@cure   │ Team        │ [DATE] ←XFER │
│ Vercel         │ Web hosting  │ cure@cure    │ Pro ($20/mo)│ [DATE] ←XFER │
│ GitHub         │ Source code  │ client-org   │ Team        │ [DATE]        │
│ Apple Dev      │ iOS publish  │ client@co    │ $99/year    │ [DATE]        │
│ Google Play    │ Android pub  │ client@co    │ $25 one-time│ N/A           │
│ Cloudflare     │ DNS/CDN      │ client@co    │ Free        │ N/A           │
│ PagerDuty      │ Alerting     │ cure@cure    │ Basic       │ [DATE] ←XFER │
└────────────────┴──────────────┴──────────────┴─────────────┴───────────────┘

Services marked ←XFER must be transferred to client ownership before handoff.

API KEY INVENTORY
  See Step 5 for complete credential list and transfer protocol.

LICENSE AND CERTIFICATION EXPIRY
  ┌────────────────────────┬──────────────┬─────────────────────────────┐
  │ Item                   │ Expiry Date  │ Renewal Action              │
  ├────────────────────────┼──────────────┼─────────────────────────────┤
  │ SSL Certificate        │ Auto-renew   │ Managed by Vercel/CF        │
  │ Apple Push Cert (APNs) │ [DATE]       │ Renew in Apple Dev Portal   │
  │ Android Signing Key    │ Never        │ Stored in Google Play Console│
  │ Domain registration    │ [DATE]       │ Renew via registrar         │
  │ Apple Dev Program      │ [DATE]       │ Auto-renew or manual        │
  └────────────────────────┴──────────────┴─────────────────────────────┘
```

### 3.4 Known Issues and Tech Debt Registry

```
KNOWN ISSUES / TECH DEBT
┌────┬──────────────────────────────────┬──────────┬──────────────────────┬────────────┐
│ #  │ Issue                            │ Severity │ Recommended Fix      │ Est. Effort│
├────┼──────────────────────────────────┼──────────┼──────────────────────┼────────────┤
│ 1  │ [Description of known issue]     │ High     │ [How to fix it]      │ 2-3 days   │
│ 2  │ [Description of tech debt]       │ Medium   │ [Refactoring needed] │ 1 week     │
│ 3  │ [Description of limitation]      │ Low      │ [Enhancement path]   │ 2-3 days   │
│ 4  │ [Scaling concern]                │ Medium   │ [Architecture change]│ 1-2 weeks  │
│ 5  │ [Missing test coverage area]     │ Medium   │ [Tests to write]     │ 3-5 days   │
└────┴──────────────────────────────────┴──────────┴──────────────────────┴────────────┘

Priority order for addressing: fix all High items before launch/handoff.
Medium items should be scheduled within the first 3 months post-handoff.
Low items are backlog — address when convenient.
```

## Step 4: Runbook Generation

See [reference/details.md](reference/details.md) (section “Step 4: Runbook Generation”) for full detail.

## Step 5: Credential and Access Transfer

### Credential Inventory

```
CREDENTIAL INVENTORY
┌────────────────────────┬───────────────────┬───────────────┬──────────────┐
│ Credential             │ Type              │ Current Holder│ Transfer To  │
├────────────────────────┼───────────────────┼───────────────┼──────────────┤
│ Firebase Admin SA      │ Service account   │ Cure GCP      │ Client GCP   │
│ Stripe API keys        │ API key pair      │ Client Stripe │ N/A (already)│
│ SendGrid API key       │ API key           │ Cure account  │ Client acct  │
│ Sentry DSN             │ Project key       │ Cure Sentry   │ Client Sentry│
│ Apple signing cert     │ Certificate       │ Client Apple  │ N/A (already)│
│ Android keystore       │ Signing key       │ Cure local    │ Client vault │
│ GitHub deploy key      │ SSH key           │ Cure GitHub   │ Client GitHub│
│ CI/CD secrets          │ GitHub Secrets    │ Cure repo     │ Client repo  │
│ Domain registrar       │ Account login     │ Client acct   │ N/A (already)│
│ PagerDuty account      │ Account login     │ Cure account  │ Client acct  │
└────────────────────────┴───────────────────┴───────────────┴──────────────┘
```

### Transfer Protocol

```
SECURE CREDENTIAL TRANSFER PROTOCOL

Rules:
  ✗ NEVER send credentials via email
  ✗ NEVER send credentials via Slack / Teams / chat
  ✗ NEVER commit credentials to git repositories
  ✗ NEVER share credentials in shared documents (Google Docs, Notion)

Approved Transfer Methods:
  ✓ 1Password shared vault (preferred)
  ✓ GCP Secret Manager (for service accounts and API keys)
  ✓ AWS Secrets Manager (if AWS-based)
  ✓ Bitwarden Send (encrypted, expiring link)
  ✓ In-person transfer on client hardware

Transfer Steps:
  1. Create credential inventory (table above)
  2. Client creates new accounts/keys where possible (new Sentry project, new SendGrid account)
  3. For credentials that cannot be regenerated:
     a. Transfer via approved method
     b. Client confirms receipt
     c. Client rotates credentials to new values
  4. Cure revokes own access within 48 hours of confirmed transfer
  5. Client verifies all services are functional with new credentials
  6. Cure deletes all copies of client credentials from Cure systems

Post-Transfer Access Revocation:
  - [ ] Remove Cure team from Firebase project (all environments)
  - [ ] Remove Cure team from GitHub organization/repository
  - [ ] Remove Cure team from Stripe account
  - [ ] Remove Cure team from Vercel project
  - [ ] Remove Cure team from App Store Connect
  - [ ] Remove Cure team from Google Play Console
  - [ ] Rotate all shared API keys
  - [ ] Disable Cure service accounts
  - [ ] Remove Cure from PagerDuty/Opsgenie
```

## Step 6: Knowledge Transfer Plan

### Session Schedule

```
KNOWLEDGE TRANSFER SESSION PLAN

Session 1: Architecture Overview (2 hours)
  Audience: Full receiving team
  Content:
    - System architecture walkthrough (using architecture doc)
    - Design decisions and trade-offs
    - Key business logic explanation
    - Q&A
  Deliverable: Recording uploaded to client's shared drive

Session 2: Codebase Tour (3 hours)
  Audience: Engineering team
  Content:
    - Repository structure and conventions
    - Key modules and their interactions
    - How to add a new feature (live walkthrough)
    - Testing strategy and how to run tests
    - Code review standards and PR process
  Deliverable: Recording + annotated code tour document

Session 3: Deployment and Operations (2 hours)
  Audience: Engineering team + DevOps/SRE
  Content:
    - CI/CD pipeline walkthrough
    - Live deployment to staging (with audience following along)
    - Monitoring dashboards tour
    - Incident response walkthrough
    - Rollback demonstration
  Deliverable: Recording + deployment runbook verified

Session 4: Infrastructure and Cost (1.5 hours)
  Audience: Engineering lead + finance stakeholder
  Content:
    - Cloud infrastructure overview
    - Cost breakdown by service
    - Scaling considerations and limits
    - Budget alerts and cost optimization tips
  Deliverable: Recording + cost model spreadsheet

Session 5: Q&A and Shadowing Kickoff (1 hour)
  Audience: Full receiving team
  Content:
    - Open Q&A on anything from previous sessions
    - Define shadowing period expectations
    - Establish communication channels for the transition period
  Deliverable: Shadowing schedule + communication plan
```

### Video Recording Requirements

```
Recording Standards:
  - Record every KT session (Zoom, Google Meet, or Loom)
  - Resolution: 1080p minimum
  - Include screen share with code/architecture visible
  - Upload to client's permanent storage within 24 hours
  - Name format: KT-[SESSION#]-[TOPIC]-[DATE].mp4
  - Include chapter markers or timestamps in description
  - Store alongside project documentation (not in personal drives)
```

### Shadowing Period

```
SHADOWING PERIOD: [2-4 weeks recommended]

Week 1-2: Cure leads, client shadows
  - Client team observes deployments, incident responses, routine tasks
  - Client team asks questions in real-time
  - Cure documents every question (becomes FAQ for handoff doc)

Week 3-4: Client leads, Cure shadows
  - Client team performs deployments, handles issues independently
  - Cure available for questions but doesn't intervene unless asked
  - Cure provides feedback after each activity

Communication during shadowing:
  - Shared Slack channel: #project-handoff-[name]
  - Response SLA: within 4 business hours
  - Escalation: if no response in 4 hours, email [CURE_LEAD]
```

## Step 7: Maintenance SLA Template

### Tier Definitions

```
MAINTENANCE SLA — [PROJECT_NAME]
Effective: [START_DATE]
Term: [DURATION — typically 3, 6, or 12 months]

SEVERITY DEFINITIONS AND RESPONSE TIMES
┌──────────┬──────────────────────────────────┬──────────────┬───────────────┐
│ Severity │ Definition                       │ Response Time│ Resolution    │
├──────────┼──────────────────────────────────┼──────────────┼───────────────┤
│ P0       │ Service down, data loss, security│ 1 hour       │ 4 hours       │
│          │ breach, payment processing broken │ (24/7)       │               │
├──────────┼──────────────────────────────────┼──────────────┼───────────────┤
│ P1       │ Core feature broken, no          │ 4 hours      │ 1 business day│
│          │ workaround, significant users     │ (bus. hours) │               │
├──────────┼──────────────────────────────────┼──────────────┼───────────────┤
│ P2       │ Feature degraded, workaround     │ 1 business   │ 3 business    │
│          │ available, minor user impact      │ day          │ days          │
├──────────┼──────────────────────────────────┼──────────────┼───────────────┤
│ P3       │ Cosmetic issue, enhancement,     │ 2 business   │ Next sprint   │
│          │ non-urgent bug                    │ days         │ (best effort) │
└──────────┴──────────────────────────────────┴──────────────┴───────────────┘
```

### Scope Definition

```
IN SCOPE:
  - Bug fixes for existing functionality
  - Security patches and dependency updates
  - Infrastructure maintenance (scaling, certificate renewal)
  - Monitoring and alerting response
  - Minor configuration changes
  - Database maintenance (index optimization, cleanup)

OUT OF SCOPE:
  - New feature development (requires separate SOW)
  - Design changes or UI overhaul
  - Platform migration (e.g., moving from Firebase to AWS)
  - Third-party service changes initiated by client
  - Performance optimization beyond current baseline

CHANGE REQUEST PROCESS:
  1. Client submits request via [Jira / Linear / email]
  2. Cure triages within 1 business day
  3. If in-scope: schedule into next maintenance window
  4. If out-of-scope: provide estimate for separate SOW
  5. All changes deployed through standard CI/CD pipeline
```

### Billing Structure

```
BILLING OPTIONS

Option A — Monthly Retainer: [X] hrs/month included, no rollover; overage at
  $[RATE]/hr; P0 incidents covered outside retainer hours at no extra cost;
  monthly usage report provided.
Option B — Time & Materials: $[RATE]/hr, 1-hr minimum per incident; P0 premium
  1.5x outside business hours; weekly timesheet for approval; Net 30 terms.
Option C — Hybrid: [X]-hr retainer for routine maintenance plus T&M for
  incidents beyond it; quarterly review to adjust retainer size.
```

## Step 8: Sign-Off Checklist

```
CLIENT HANDOFF SIGN-OFF CHECKLIST
Project: [PROJECT_NAME]
Date: [DATE]
Cure Representative: [NAME]
Client Representative: [NAME]

DOCUMENTATION
  - [ ] Architecture overview document delivered and reviewed
  - [ ] Environment guide with all URLs and access instructions
  - [ ] Dependency inventory with license expiry dates
  - [ ] Known issues / tech debt registry reviewed with client
  - [ ] API documentation complete and accessible

RUNBOOKS
  - [ ] Deployment runbook for all platforms (web, mobile, functions)
  - [ ] Incident response runbook with escalation paths
  - [ ] Common troubleshooting guide (top 10 issues)
  - [ ] Monitoring runbook (dashboards, alerts, what they mean)

CREDENTIALS AND ACCESS
  - [ ] Credential inventory complete
  - [ ] All credentials transferred via approved secure method
  - [ ] Client confirmed receipt and tested all credentials
  - [ ] Cure access revoked from all client systems
  - [ ] All API keys rotated post-transfer
  - [ ] Client can deploy independently to all environments

KNOWLEDGE TRANSFER
  - [ ] All KT sessions completed per schedule
  - [ ] All sessions recorded and uploaded to client storage
  - [ ] Shadowing period completed
  - [ ] Client team performed at least one independent deployment
  - [ ] FAQ document from KT questions delivered

MAINTENANCE (if applicable)
  - [ ] SLA document signed by both parties
  - [ ] Escalation contacts confirmed
  - [ ] Communication channels established
  - [ ] Billing terms agreed

SOURCE CODE
  - [ ] All repositories transferred to client ownership
  - [ ] Branch protection rules configured
  - [ ] CI/CD pipelines running under client accounts
  - [ ] All git history preserved

SIGN-OFF
  Client Representative: _________________________ Date: _________
  Cure Representative:   _________________________ Date: _________

  By signing, both parties confirm receipt of all handoff deliverables
  and acknowledge the transition of operational responsibility.
```

Cross-references: Use `/project-manager` for sprint planning during the handoff phase. Use `/incident-response` for building the incident runbooks included in the handoff package. Use `/infrastructure-scaffold` for documenting the infrastructure being handed off. Use `/legal-doc-scaffold` for generating the maintenance SLA and SOW documents.
