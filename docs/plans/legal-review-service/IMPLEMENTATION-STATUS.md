# Legal service implementation status — 2026-10-12

The user authorized proceeding after checking project/billing capacity and subsequently authorized
using an available billing slot. Runtime source is in the separate local repository
`/Volumes/CureVault/projects/cure-agent-services`; no remote repository has been published.

## Cloud foundation

- 25 accessible active projects before setup; 26 after creating `cure-agent-services-dev`.
- No DELETE_REQUESTED projects or accessible organizations returned by discovery.
- Four open billing accounts: Firebase Payment, Main Billing, Cure Consulting Billing, consulting websites.
- Cure Consulting Billing has five linked projects and rejected the dev link with a billing quota error.
- Firebase Payment had four linked projects and accepted dev; it now has five.
- Main Billing has five and consulting websites seven; their spare capacity was not probed.
- Exact remaining personal project quota and per-account allowances are not exposed by these listings.
- Dev is active and billing-enabled; core service APIs enabled. Production/staging not created.
- Dev has a $50/month alerts-only budget; it is not a hard cap. Bootstrap uses zero minimum and
  one maximum instance, with model execution disabled.

Preferred eventual billing remains Cure Consulting Billing, subject to capacity. Development uses
Firebase Payment with explicit user authorization. No existing product was moved or unlinked.

## Runtime foundation

- Strict request, authority, analysis, job, and attribution contracts; JSON Schema export.
- Project/action permission primitives and server budget ceilings.
- Evidence-reference checks rejecting fabricated source and foreign artifact identifiers.
- Experimental Vertex adapter with bounded output/timeout; disabled by default.
- Official v7.13.0 research/doctrine and legal-agent source reconciled; 33 Markdown files exported
  with commit provenance and content hashes. Professional validation remains pending.
- Private dev bootstrap deploy path; legal endpoints return `review_not_enabled`.
- Dev bootstrap deployed as `legal-api-dev-00001-trn`. Anonymous health request returned 403;
  authenticated health returned 200; legal route returned 503 as intended. Cloud Build succeeded.

Type checking and five policy/schema tests passed. These do not establish legal accuracy or
end-to-end tenant isolation. No legal model request was made.

Runtime README: `/Volumes/CureVault/projects/cure-agent-services/README.md`.
Deployment: `https://legal-api-dev-156283605641.us-central1.run.app` (IAM authentication required).

Next: verified identity adapters, durable project permissions, review jobs/outbox, atomic spend
reservations, controlled retrieval, professional validation, then MCP and console. This is the first
foundation package, not completion of the full service backlog.

## Expanded scope and subsequent work

User requested full implementation and broad legal competence benchmarks. Portfolio baseline now
covers 19 local repositories plus a media-assets directory, with worktrees deduplicated, and flags
unmapped GCP products. It adds NY probate/estates (Finality), financial/crypto triage (CoinbaseTrader),
consumer-health (FlowMind), NY/MA/NJ/CT/PA public-data coverage, and US/DO merchant jurisdiction needs.

Runtime `docs/COMPLETION-SCOPE.md` defines phases through production and practice-specific gates;
`docs/BROAD-BACKLOG.md` adds LEG-033–057. The older pilot estimate does not cover this broad scope.

Durable dev workflow is deployed as revision `legal-api-dev-00003-thr`: verified Google identity,
project membership, idempotency, budget reservation, Cloud Tasks dispatch and terminal refund.
Eleven live checks passed. The worker intentionally returns `research_not_enabled` rather than a
legal conclusion; source retrieval and budgeted legal model execution remain the next package.

Revision `legal-api-dev-00004-jz6` adds the metadata-only durable outbox; all 11 live checks passed
again. A five-minute authenticated Scheduler trigger is provisioned for outbox recovery. Complete
crash/retry/retention and scheduled-delivery validation remain part of the operating test backlog.

Live key-blind Vertex knowledge baseline (`gemini-2.5-flash`): MBE 97.86% bare / 98.57% doctrine;
NYLE 85.19% / 98.15%; MPRE 100% / 100%. 224 MCQs per arm; seven essays per arm generated and
awaiting independent grading. Estimated token spend $0.1551. These are self-authored bar-style
proxies, not an official exam result or deployed-service benchmark.

Two historical Supreme Court packet probes also ran against official PDFs. They are narrow
factual/scope checks, not exhaustive case-law research or a professional readiness certification.

## Research engine development release — 2026-10-13 UTC

Supersedes the model-disabled status above for the public/synthetic `cure-research` pilot only.
Cloud Run revision `legal-api-dev-00010-nh8` implements scoped document ingestion, controlled
official-source retrieval, Vertex memos/contract risks/explicit drafts, server passage citations,
one bounded repair, advisory challenge, cost settlement, follow-ups, exports and dispositions.
Private artifact storage and retention are active; Scheduler delivery succeeded.

Validation: 15 local tests, 11 cloud lifecycle checks and 34 cloud research workflow checks passed.
The memo and draft were marked partial for quality gaps; these counts establish workflow behavior,
not attorney competence. Runtime docs/PHASE-2-VALIDATION.md records actual results and limitations.
Next: MCP/console, matter administration and practical system/quality benchmarks; historical source
coverage, licensed treatment, independently reviewed answers and production gates remain open.

## Shared access update — 2026-10-13 UTC

Private organization repository created: https://github.com/Cure-Consulting-Group/cure-agent-services.
Development revision 00012 implements hosted MCP, a project-bound local MCP adapter, internal
workstation review console, matter intake/reviewer assignments and scoped project/member admin.
The six-task deployed practical runner preserves failures and partial outputs with no quality score
until independently labeled. Fifty local tests and live client/browser/second-tenant checks pass;
see runtime docs/PHASE-3-VALIDATION.md. Full holds/erasure, broader independent quality benchmarks
and production operations remain next gates.
