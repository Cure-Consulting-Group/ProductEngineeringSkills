# Cloud placement and reusable portfolio services

Date: 2026-10-12. Parent: [legal service scope](README.md).

## 1. Live GCP evidence

Read-only discovery used `gcloud projects list`, `gcloud projects describe`, `gcloud billing projects describe`, `gcloud billing accounts list`, `gcloud run services list`, and `gcloud services list --enabled`. No infrastructure or account changes were made. Results cover resources accessible to the current CLI identity, not every possible Cure account or organization. IAM bindings, ingress, database contents, contractual data permissions, and full resource inventories were not assessed.

25 active accessible projects were returned. Relevant host candidates:

| Project | Display name | Observed workload | Billing / APIs |
|---|---|---|---|
| `academic-moon-123900` | CureConsultingGroup | Website and 13 additional Cloud Run services/functions covering blog, blueprint, booking, contact, leads, newsletters, and subscribers | Billing enabled on Firebase Payment; Firebase, Firestore, Cloud Run enabled; Vertex AI and Cloud Tasks not in enabled-API results |
| `cure-finops-ops` | Cure FinOps Ops | Six Cloud Run services: alert mailer, billing watchdog, GitHub billing ingest, limits check, policy check, snapshot | Billing enabled on Main Billing; Firebase, Firestore, Cloud Run enabled; Vertex AI and Cloud Tasks not in enabled-API results |

Neither candidate shows an organization parent in the inspected metadata/listing. This is consistent with historical FinOps notes, but is not an organization-wide census. A separate project `unified-maxim-pxpq9` has a folder parent; no further conclusions were drawn about that hierarchy.

Existing open billing accounts: **Firebase Payment**, **Main Billing**, **Cure Consulting Billing**, and **consulting websites**. One account named My Billing Account is closed. The Cure-branded website project's billing is not currently the account named Cure Consulting Billing. The FinOps operations project's billing is Main Billing.

Other accessible product project IDs include `autograph-health`, `level-5-scribe-beta-8842`, `iep-and-thrive`, `vendly-production`, `hooptrace-prod`, `statledger-dev`, `initiated-recruiting-staging`, `carbide-ether-123900`, `hbcyou-121cc`, `flowmind-ios`, `bloomkeeping-prod`, and `bloomkeeping-staging`. Treat IDs as discovery evidence, not proof that every corresponding application is active or ready for onboarding.

Recommendation: create dedicated agent-services environments under Cure ownership, paid by Cure Consulting Billing. Keep the consulting website and existing FinOps data/identities separate. Reuse FinOps for chargeback visibility, budget reporting, and operational links; do not give the legal worker billing-governance credentials.

A Cure website navigation link may lead to the internal console later. Sharing a branded entry point does not require sharing its runtime service account, database, or project.

## 2. Existing architecture proposals

The FinOps repository contains proposed, pending-approval ADRs:

- `docs/adr/0009-agent-placement.md`: favors per-product deployment, Cloud Run Jobs for scheduled work, CI for repository work, local interactive agents, and strict product data boundaries.
- `docs/adr/0008-shared-llm-client.md`: proposes a shared TypeScript provider package based on DistrictZero with product attribution and common resilience.

These are proposals, not confirmed accepted policy. Do not silently overwrite or treat them as deployed mechanisms. This legal RFC proposes a bounded shared consultation exception: authorized submitted context, durable jobs, no product database grants, separate project permissions, explicit per-product cost allocation, and isolated deployments for prohibited context.

Shared project-level billing cannot provide the same separation as per-product Vertex projects. An operator must choose either internal chargeback in the shared pilot or per-product inference/workers when provider billing isolation is required. Carry product attribution in both. The proposed exception and existing regulated-runtime register must be resolved before deployment.

## 3. Portfolio evidence

Candidate mapping is based on inspected local README/STATE documents; project status may have changed. No full portfolio registry was found in the searched project paths. Consolidate ownership, active products, aliases, environments, sensitivity, and integrations during service onboarding. Do not count worktrees, experiments, or renamed products as independent services.

| Product / source | Observed purpose | Likely legal questions |
|---|---|---|
| Initiated Recruiting — `initiated-recruiting/README.md` | Girls' basketball recruiting/scouting | Athlete profiles, recruiting claims, consent, NIL-related workflows and contracts |
| StatLedger — `statledger/README.md` | Basketball statistics capture/reporting | Player identity, publishing/sharing, media and data rights |
| CourtCast — `CourtCast/README.md` | Current restart focuses on basketball highlights; historical SaaS claims are qualified | Footage permissions, athlete likeness, content distribution |
| LearnLift — `SPEDTECH/README.md` | K–4 reading/phonics intervention | Age bands, parent/school roles, student progress data, processor contracts |
| IEP & Thrive — `iep-and-thrive/STATE.md` | Reading product and tutoring, with product audit backlog | Consent, student records, signed documents, tutoring agreements |
| Autograph — `Level5/README.md` | Ambient medical documentation and EHR workflow | Provider agreements, privacy architecture, vendor/data obligations; no central PHI pilot |
| Vendly — `Vendly/README.md` | Merchant inventory/POS across US and LATAM | Merchant contracts, refunds, processors, jurisdiction-specific terms |
| FinOps watchdog — `cure-finops-watchdog/README.md` and ADRs | Existing cross-project billing/governance capabilities | Shared-service attribution and operational controls |

RashadTax's README is mostly application setup; detailed product scope was not established in this pass. DistrictZero's short README is insufficient, so its documented shared provider work is used only as reuse evidence. Further recommendations for those products require targeted discovery.

The legal pilot should begin with redacted consulting contracts to validate intake, evidence, and review history, then Initiated Recruiting synthetic feature questions. Education and healthcare profiles need domain-specific evaluation and strict data classification before onboarding.

## 4. Other services using the same pattern

Priorities below are architecture recommendations grounded in the portfolio and available skills. They are not approved builds or claims of existing production capabilities.

| Priority | Shared service | Portfolio fit | Reusable skills/agents | Boundary |
|---|---|---|---|---|
| 1 after legal | Security and privacy review | All Firebase/web/mobile projects; especially merchant, education, and healthcare products | security-review, firebase-security-auditor, env-secrets-manager, compliance-architect | Approved diffs/rules/schema only; no secret values or broad production read grants; privacy reviews complement legal review |
| 2 | FinOps consultation | Existing FinOps watchdog and shared Vertex spend | finops, financial-analyst, burn-rate-tracker | Extend existing watchdog query/report capabilities; preserve billing-data access scopes; approval for cost-changing actions |
| 3 | Release readiness | Recruiting, StatLedger, Vendly, LearnLift, native apps | release-management, feature-audit, accessibility-audit, uat | Consume existing CI/staging evidence; distinguish absent evidence from pass; human release decision |
| 4 | Accessibility and design review | Reading products, merchant app, medical workflows, native/web portfolio | accessibility-audit, product-design, platform design skills | Scoped screenshots/component exports plus deterministic tooling; separate actual runtime accessibility verification |
| 5 | Tax and entity review | Cure entities and tax-related work | tax-analyst, return-review, estimated-tax-compliance, qsbs-compliance | CPA/tax-attorney review; isolated financial context; no filing, payments, or central tax identifiers by default |
| 6 | Product and delivery advisor | Shared feature scoping and portfolio planning | product-manager, sdlc, technical-estimation, project-manager | Project-specific roadmap and capacity; do not expose client budgets between projects |
| 7 | Marketing/brand review | Recruiting/media, merchant products, consulting website | product-marketing, brand-guardian, seo-content-engine | Approved content/media; separate publishing credentials and human authorization |

Readiness checks should combine deterministic evidence collectors with LLM interpretation. A shared agent cannot replace missing CI, real-device accessibility checks, or observed deployment health. FinOps is already a cross-project system, so wrap or extend its existing authorized APIs rather than rebuilding its data pipeline.

## 5. Shared foundation and domain ownership

Reusable foundation: identity/membership, project registry, asynchronous job lifecycle, budget reservations, artifact access, usage telemetry, API/MCP adapters, skill provenance, report versioning, retention, and deployment templates.

Domain-owned: enabled tools, evidence requirements, source hierarchy, jurisdictions, prompts, professional review, output schema, scoring rubric, prohibited actions, and acceptance thresholds. Avoid one giant model context containing every Cure skill. Each request routes to one explicitly enabled domain/profile; cross-domain consultations are separately authorized jobs with explicit context transfer.

Centralize policy and approved bundles where permitted; deploy execution near restricted data when required. This is a shared service pattern with multiple deployment options, not a requirement to move every product's production data to a common project.

## 6. Expansion gate

Build legal first. Add security/privacy only after legal demonstrates authorization isolation, durable execution, spend control, usable reports, and repeatable deployment. Extend FinOps through its existing system. Extract common runtime packages when a second domain demonstrates real shared code. Each later service gets its own PRD, source/coverage inventory, data classification, eval rubric, professional owner where needed, and deployment decision.

A shared-services directory can eventually expose enabled domains and endpoints for each project. A general autonomous dispatcher, shared global memory, vector database across all client documents, and agent-to-agent network are not prerequisites for the legal pilot.
