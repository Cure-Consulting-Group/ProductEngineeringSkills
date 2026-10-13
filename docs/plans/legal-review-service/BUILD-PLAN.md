# Legal service build plan

Parent: [PRD-LEGAL-001 / RFC-LEGAL-001](README.md). Date: 2026-10-12.
Status: foundation implemented; durable workflow implementation underway. Story points are relative sizing, not delivery promises.

The user expanded the destination to a portfolio-wide legal practice platform on 2026-10-12.
The runtime's `docs/COMPLETION-SCOPE.md` now defines the broad coverage and completion phases;
`docs/PORTFOLIO-BASELINE.md` grounds practice/jurisdiction priorities in all local product repositories.
This backlog remains the first service release, not the full estimate for every practice area.

## 1. Sequence and capacity

Plan for one backend/platform engineer, fractional integration/UI work, and scheduled legal/security reviewers. Provisional schedule: 6–9 calendar weeks to a controlled production pilot, assuming reviewer availability, identity setup, and source access. This is a planning range, not a contracted estimate. Re-estimate after Sprint 0; broader jurisdictions, scanned-document OCR, licensed research, and regulated-data deployments add scope.

| Phase | Provisional duration | Deliverable / gate |
|---|---|---|
| Sprint 0: decisions and fixtures | 3–5 working days | Verified domains, project/identity choice, reviewer, model candidates, artifact manifest |
| Foundation | 1 week | Dev infrastructure, project authorization, contracts, durable job execution |
| Review engine | 1–2 weeks | Vertex integration, ingestion, source retrieval, reports, cost accounting |
| Integrations | 1–2 weeks | MCP and minimal console use the same authorized handlers |
| Validation and pilot | 1–2 weeks | Professional review, failure testing, 20 paired pilot reviews |
| Production hardening | 1 week | Approved environment, operations, canary, rollback, second-project isolation |

Dependency chain: discovery → identity and schema → queue/ingestion → retrieval and runtime → API/MCP/console → quality evaluation → pilot → production. UI can use synthetic contracts once API schemas are settled. No project integration needs direct database permission.

Named responsibilities must be assigned before Sprint 1: accountable product owner, platform/incident owner, engineer, project integration owner, legal reviewer, CPA/tax reviewer if QSBS is enabled, and security reviewer. The product owner sets coverage and budget; the legal reviewer validates analysis; the platform owner owns service reliability. No role is implied to be staffed today.

## 2. Proposed runtime layout

Create a separate runtime repository after the scope is accepted:

```text
cure-agent-services/
  apps/api/                 # authenticated intake, status, access policy
  apps/worker/              # bounded review jobs
  apps/mcp/                 # client auth and legal tool adapter
  apps/console/             # minimal internal review UI
  packages/contracts/      # strict schemas, OpenAPI, typed client
  packages/legal/          # profile selection, prompts, evidence validation
  packages/context/        # project-scoped ingestion and retrieval
  packages/vertex/         # Vertex calls, usage, retry, model configuration
  packages/policy/         # identity, membership, classifications, budgets
  bundles/legal/           # generated immutable skill artifact + manifest
  infra/terraform/         # dev/staging/prod modules and environment config
  evals/legal/             # approved synthetic/redacted fixtures and graders
  docs/adr/                # final hosting/auth/data/retention decisions
  docs/runbooks/           # incident, rollback, deletion, failed-job recovery
```

Use TypeScript for service/contracts to match the bootstrap and major portfolio backends. Choose runtime framework and SDK versions after checking maintained primary documentation. Inspect the existing DistrictZero provider package and FinOps shared-client work before creating a new Vertex wrapper; reuse compatible resilience and attribution behavior, with no broad migration bundled into this build.

## 3. Epics and stories

Every story below inherits: engineer review; relevant tests and contract updates; sanitized telemetry; no secret exposure; documented failure behavior. Legal-domain stories require domain-review evidence. Acceptance criteria are intended for the future build; no tests were added or run for this planning-only work.

### EPIC-LEGAL-01 — discovery and domain packaging

Goal: determine exactly which capabilities the service can ship. Depends on PRD-LEGAL-001.

| Story | Points | User story and acceptance criteria |
|---|---:|---|
| LEG-001 | 3 | As a platform owner, I need live hosting evidence. Given accessible GCP projects, when discovery runs, then record relevant projects, workloads, billing, parent, API availability, and the proposed dev/prod boundary without mutation. |
| LEG-002 | 5 | As a domain owner, I need verified skills. Given repository and installed catalogs, when sources are reconciled, then every enabled capability has licensed source files, hashes, an owner, tool policy, and a review status; missing research skills remain disabled. |
| LEG-003 | 3 | As a product owner, I need a bounded pilot. Given candidate projects, when onboarding is agreed, then record allowed data, jurisdictions, profiles, provider location, reviewer availability, and utility baseline. |
| LEG-004 | 5 | As a legal reviewer, I need reference cases. Given scoped domains, when 60 fixtures are prepared, then each has expected findings, source requirements, jurisdiction/date facts, and a professional-review rubric. |

Exit: hosting/auth/data decisions documented; bundle source reconciled; pilot owner and domain reviewer identified. LEG-001 has initial evidence in PORTFOLIO-SERVICES.md; detailed IAM/network/data assessment is still required.

### EPIC-LEGAL-02 — infrastructure, identity, and contracts

Depends on EPIC-LEGAL-01.

| Story | Points | User story and acceptance criteria |
|---|---:|---|
| LEG-005 | 5 | As an operator, I need reproducible environments. Given approved placement, when Terraform applies to dev, then API, worker, queue, stores, identities, monitoring, and least-privilege grants exist with no product database grants. |
| LEG-006 | 5 | As a project owner, I need isolation. Given two principals in two projects, when either lists, submits, reads, exports, deletes, or continues a review, then access is confined to explicit membership and action grants. |
| LEG-007 | 3 | As an integrator, I need strict contracts. Given API-LEGAL-001, when a request is validated, then unknown fields, invalid artifacts, budgets, states, and enums are rejected with typed errors; schema versions are recorded. |
| LEG-008 | 5 | As an operator, I need separate identity paths. Given a GCP backend and a user client, when they authenticate, then IAM and user/OAuth paths validate issuer/audience and preserve verifiable caller identity to the same policy layer. |

Exit: dev infrastructure and authorization contracts work; unauthenticated and cross-project requests fail before provider access.

### EPIC-LEGAL-03 — durable jobs and bounded spending

Depends on EPIC-LEGAL-02.

| Story | Points | User story and acceptance criteria |
|---|---:|---|
| LEG-009 | 5 | As a caller, I need durable submission. Given a valid idempotent request, when queue delivery fails or repeats, then one logical job exists, an outbox/reconciliation path recovers dispatch, and state updates respect worker leases. |
| LEG-010 | 5 | As a project owner, I need spend limits. Given concurrent submissions near a budget ceiling, when reservations occur, then atomic checks prevent new unreserved calls; caps include retries and follow-ups; costs retain product attribution. |
| LEG-011 | 3 | As a caller, I need honest job state. Given timeout, cancellation, missing facts, or provider failure, when execution stops, then status and partial output reflect the reason and unused reservations are released. |
| LEG-012 | 3 | As an operator, I need bounded retries. Given ambiguous provider completion or repeated delivery, when retry occurs, then attempts and usage are recorded, transient-only retry limits apply, and stranded jobs become visible failures. |

Exit: deterministic failure and race scenarios prove state/budget behavior before adding full model work.

### EPIC-LEGAL-04 — ingestion and authority retrieval

Depends on EPIC-LEGAL-02 and scoped source policy.

| Story | Points | User story and acceptance criteria |
|---|---:|---|
| LEG-013 | 5 | As a submitter, I need safe uploads. Given permitted text/Markdown/PDF artifacts, when uploaded, then size, MIME, project ownership, classification, expiration, secret scanning, and extraction limits are enforced; unsupported OCR formats are rejected clearly. |
| LEG-014 | 5 | As a reviewer, I need reliable document references. Given normalized artifacts, when the agent retrieves context, then page/section/span and artifact version identify the original evidence; tenant and permission boundaries apply. |
| LEG-015 | 5 | As a legal reviewer, I need relevant public authority. Given an abstract legal query, when retrieval runs, then source types, jurisdiction, provision/date, retrieval time, and provenance are retained without confidential query content. |
| LEG-016 | 5 | As a security owner, I need controlled retrieval. Given private-IP URLs, redirect tricks, oversized responses, hostile documents, or embedded instructions, when ingestion/retrieval occurs, then unsafe fetches are blocked and instructions cannot grant tools or change authorization. |

Exit: approved evidence is reproducible; public-source lookup and document ingestion pass policy/failure cases; licensed-source retention constraints are explicit.

### EPIC-LEGAL-05 — Vertex review runtime and quality

Depends on EPIC-LEGAL-03/04 and LEG-002/004.

| Story | Points | User story and acceptance criteria |
|---|---:|---|
| LEG-017 | 5 | As an operator, I need an approved model configuration. Given Vertex model candidates, when evaluated, then location, model resolution/version, retention/security features, quotas, token pricing assumptions, and workload authentication are recorded. |
| LEG-018 | 5 | As a caller, I need domain-specific review. Given an enabled profile, when a job runs, then only its approved bundle/tools load, the runtime enforces iteration/time/spend caps, and missing jurisdiction or facts produce follow-up questions. |
| LEG-019 | 5 | As a reviewer, I need supported findings. Given a generated report, when validated, then every material claim maps to evidence and appropriate authority or is explicitly qualified as unsupported/partial; malformed reports never become successful answers. |
| LEG-020 | 5 | As a domain owner, I need a release gate. Given fixtures and a candidate model/bundle, when evaluation runs, then rubric scores, citation failures, critical omissions, uncertainty handling, and regressions are recorded and blocking thresholds apply. |

Exit: enabled domains pass professional and deterministic review gates; out-of-coverage requests are qualified rather than improvised.

### EPIC-LEGAL-06 — MCP, console, and project onboarding

Depends on API schemas and identity; production use depends on EPIC-LEGAL-05.

| Story | Points | User story and acceptance criteria |
|---|---:|---|
| LEG-021 | 5 | As a coding agent, I need legal tools. Given an authorized client, when it submits a question/review, polls, lists, or answers a follow-up, then strict MCP schemas and honest side-effect annotations wrap the same core handlers. |
| LEG-022 | 5 | As a business owner, I need a review console. Given membership, when I submit, view, continue, export, or cancel a case, then UI states match job/report outcomes and show sources, limitations, costs, and professional-review status. |
| LEG-023 | 3 | As a qualified reviewer, I need attributed decisions. Given reviewer access, when I record acceptance, dismissal, or requested changes, then identity, qualification, time, rationale, and report version are append-only and cannot be forged by an agent. |
| LEG-024 | 3 | As a project owner, I need repeatable onboarding. Given opt-in project config, when bootstrap runs, then managed connection/routing instructions are added without credentials or clobbering local edits; diagnostics check connectivity, not legal adequacy. |

Exit: an actual desktop client and console complete submit → follow-up → report → disposition; a second project demonstrates isolation. No credentials committed to client configs.

### EPIC-LEGAL-07 — retention, operations, and pilot

Depends on EPIC-LEGAL-02 through 06.

| Story | Points | User story and acceptance criteria |
|---|---:|---|
| LEG-025 | 5 | As a project owner, I need data lifecycle controls. Given expiry/deletion/hold policy, when cleanup runs, then uploads, normalized context, reports, exports, caches, and orphan artifacts are covered; backup/provider limitations are disclosed. |
| LEG-026 | 3 | As an operator, I need actionable monitoring. Given stage failures, queue delay, provider error, or budget exhaustion, when thresholds trigger, then sanitized telemetry identifies the run/project and links to recovery guidance. |
| LEG-027 | 5 | As a release owner, I need safe promotion. Given a passing release, when canary/rollback executes, then image/bundle/model/schema provenance is preserved, in-flight jobs remain interpretable, and prior report formats stay readable. |
| LEG-028 | 5 | As a product owner, I need pilot evidence. Given at least 20 paired reviews, when the pilot ends, then reviewer preparation time, corrections, referral rate, latency, per-case cost, and critical failures inform a documented go/no-go decision. |

Exit: production rollout gate below passed; service owner accepts operating responsibility.

### EPIC-LEGAL-08 — later integrations

These are separately estimated after pilot; they are not required for the first production release.

- LEG-029 (5): opt-in GitHub diff review. Given an installed project App and exact commit, when a PR event arrives, then only approved files reach the review; duplicate events reuse the logical review; posting findings requires separately authorized write scope.
- LEG-030 (5): authority/document change re-review. Given a tracked source or artifact change, when a project opts in, then a new report version explains affected findings and bounded cost; no silent edits to old reports.
- LEG-031 (8): isolated product deployment. Given a project's approved regulated-data policy, when the legal worker is deployed locally, then matter context and reports remain in that project and central telemetry contains no prohibited identifiers/content.
- LEG-032 (5): explicit document drafting. Given an authorized human request and required entity/document facts, when drafting runs, then it creates a separately labeled draft under the project's policy with no signing/publication tools.

Split LEG-031 into smaller stories after the first product's data and provider requirements are known.

## 4. Verification specification

| ID | Boundary | Required cases |
|---|---|---|
| TEST-LEGAL-01 | Auth and tenant isolation | Missing/expired/wrong-audience token; revoked membership; forged project; unauthorized artifact/export/follow-up/disposition; enumeration |
| TEST-LEGAL-02 | API/MCP contracts | Valid shapes; unknown fields; async handles; tool errors; pagination; actual client interoperability |
| TEST-LEGAL-03 | Queue and state | Duplicate request/delivery; failed enqueue; worker crash; expired lease; concurrent workers; retry cap; cancellation; stranded-job recovery |
| TEST-LEGAL-04 | Budgets | Concurrent reservation; partial refunds; retry/follow-up spend; daily window; unknown pricing; kill switch |
| TEST-LEGAL-05 | Context/retrieval | Secret-bearing file; spoofed MIME; corrupted/oversized PDF; redirect/private IP/metadata; hostile instructions; unsupported jurisdiction; stale authority |
| TEST-LEGAL-06 | Legal quality | 60 golden cases; correct evidence/citation support; missing facts; conflicting rules; effective dates; critical findings; source unavailability |
| TEST-LEGAL-07 | Lifecycle | TTL while active; all storage surfaces; abandoned upload; legal hold; export expiry; backup/provider retention disclosure |
| TEST-LEGAL-08 | Release/operations | Provider outage; schema/model mismatch; canary regression; rollback; compatible stored reports; monitoring without prompt leakage |

## 5. Production rollout gate

1. Coverage and jurisdictions are explicit; a qualified reviewer signs off on enabled domain fixtures.
2. Required isolation, injection, retrieval, contract, lifecycle, job, and budget cases pass.
3. No fabricated citations, unresolved critical omissions, or severe access failures in release evaluation.
4. Pilot utility, correction rate, latency, and spend are reviewed; uncertain answers remain identifiable.
5. Dedicated staging/prod placement, identity, location, retention, provider settings, and budget are recorded.
6. Incident owner, kill switch, rollback, deletion, and failed-job recovery are demonstrated.
7. A second authorized project can use the service without seeing the pilot's cases.
8. Proposed placement-policy conflict and regulated-runtime limits are resolved for the actual deployment scope.

The user has authorized implementation and benchmarking, including development provisioning and
using an available billing slot. Production readiness still requires the concrete release evidence
above, including professional validation and approved data processing; incomplete tests cannot
be represented as a passed release gate.

## 6. First implementation package

Start LEG-001 through LEG-004. Produce hosting/auth/data ADRs, a verified legal bundle manifest, scoped synthetic fixtures, runtime directory skeleton, and schemas. Re-estimate the remaining backlog using those results. Then implement the dev foundation and durable job flow before enabling real Vertex reviews.
