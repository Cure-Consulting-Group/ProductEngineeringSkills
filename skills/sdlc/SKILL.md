---
name: sdlc
version: "1.0.0"
description: "Generate structured engineering documents — PRDs, ADRs, RFCs, Epics, User Stories, Task specs, and test specs from a feature description"
when_to_use: "Use when the user says 'write a PRD', 'create an ADR', 'draft an RFC', 'break this into stories', or 'spec this out'. NOT for product strategy or OKRs (use product-manager). NOT for sprint planning (use project-manager)."
argument-hint: "[feature-name]"
---

# SDLC Artifact Generator

## Pre-Processing (Auto-Context)

Before starting, gather project context silently:
- Read `PORTFOLIO.md` if it exists in the project root or parent directories for product/team context
- Run: `cat package.json 2>/dev/null || cat build.gradle.kts 2>/dev/null || cat Podfile 2>/dev/null` to detect stack
- Run: `git log --oneline -5 2>/dev/null` for recent changes
- Run: `ls src/ app/ lib/ functions/ 2>/dev/null` to understand project structure
- Use this context to tailor all output to the actual project

Full-cycle software development lifecycle artifact generation for technical product teams. Generates production-grade, opinionated SDLC artifacts aligned with Clean Architecture, SOLID principles, and modern mobile/backend engineering standards.

## Core Principle: Artifact Traceability Chain

```
Vision / Initiative
    └── PRD (Product Requirements Document)
          ├── RFC (Request for Comments) — for non-trivial architectural choices
          ├── ADR (Architecture Decision Record) — one per key decision made
          └── Epics (major phases of work)
                └── Stories (user-facing units of work, with points)
                      ├── Tasks / Subtasks (engineering breakdown)
                      ├── Design Ticket (linked to story)
                      ├── API Spec (if applicable)
                      ├── Unit Test Spec
                      └── E2E / Integration Test Spec (if applicable)
```

## Step 1: Determine What the User Needs

| Request type | Primary artifact | Secondary artifacts |
|---|---|---|
| New feature/product | PRD → Epics → Stories | ADR, RFC, API Spec, Test Specs |
| Architectural decision | ADR | RFC (if pre-decision), Story to implement |
| Backlog generation | Epics + Stories | Test Specs, Design Tickets |
| Single story/ticket | Story + Tasks | Unit Test Spec, Design Ticket |
| RFC for proposal | RFC | ADR (after decision), Stories |
| API definition | API Spec (OpenAPI 3.1) | Stories, Test Spec |

If the user's request is ambiguous, ask: "What's the scope? New feature, architecture decision, or full backlog?"

## Step 2: Gather Context (Required Inputs)

1. **Feature/system name** — e.g., "Stripe Subscription Flow"
2. **Platform** — Android / Backend / Full-stack / Web
3. **Tech stack** — default: Kotlin + Jetpack Compose + Hilt + Firebase + GCP + Stripe
4. **Scope level** — Single story | Feature | Epic | Full product
5. **Any existing constraints** — existing ADRs, API contracts, design system

If missing, infer from context or ask one clarifying question max.

## Step 3: Generate Artifacts

Generate the appropriate artifact type(s) based on the request classification.

## Step 4: Output Format Rules

### Numbering Convention
```
PRD-001          → Product Requirements Document
RFC-001          → Request for Comments
ADR-001          → Architecture Decision Record
EPIC-001         → Epic
STORY-001        → Story (child of an Epic)
TASK-001         → Task (child of a Story)
DESIGN-001       → Design ticket (child of a Story)
TEST-UNIT-001    → Unit test spec
TEST-E2E-001     → E2E/integration test spec
API-001          → API specification
```

### Story Points (Fibonacci)
- 1 pt: Trivial change, config, copy
- 2 pt: Simple, well-understood, <4hrs
- 3 pt: Clear scope, minor unknowns, ~1 day
- 5 pt: Moderate complexity, some unknowns, 1-2 days
- 8 pt: Complex, multiple components, 2-3 days
- 13 pt: Large, should consider splitting
- 21 pt: Must be split before sprint

### Acceptance Criteria Format
Use Given/When/Then (Gherkin-style) for every story:
```
Given [precondition]
When [action]
Then [expected outcome]
And [additional outcome]
```

### Definition of Done (applied to every story)
- [ ] Code reviewed and approved (min. 1 reviewer)
- [ ] Unit tests written and passing (coverage >= 80%)
- [ ] Integration/E2E test written (if applicable)
- [ ] API spec updated (if contract changed)
- [ ] ADR written for any architectural decision made during implementation
- [ ] Feature documentation updated
- [ ] Design QA sign-off (if UI changes)
- [ ] No new lint warnings / detekt violations
- [ ] Feature flag in place (if applicable)

## Step 5: Backlog Ordering Rules

Prioritize using MoSCoW within each Epic:
- **M** (Must Have) — core path, no launch without
- **S** (Should Have) — high value, workaround exists
- **C** (Could Have) — nice-to-have, cut if needed
- **W** (Won't Have this cycle) — explicitly deferred

Sprint sequencing: Infrastructure → Core Data Layer → Business Logic → UI → Integration → Polish/QA

## Output Delivery

- For small requests (1-3 stories): Output inline as structured Markdown
- For medium requests (1 epic, 5-15 stories): Generate a `.md` file
- For large requests (full product, multiple epics): Generate a `.md` file with table of contents and cross-linked references
- Always offer: "Want me to also generate the [ADR / RFC / API spec / test specs] for this?"

## Artifact Generation (Required)

You MUST generate actual documents using Write, not just describe formats:

Based on the classified request type, generate:
- **PRD**: `docs/prd/{name}.md` with full sections (Problem, Solution, Scope, Metrics, Timeline)
- **ADR**: `docs/adr/{NNN}-{title}.md` using architecture-decision output style
- **Epic**: `docs/epics/{name}.md` with user stories and acceptance criteria
- **Task spec**: `docs/tasks/{ticket-id}.md` with implementation plan and test cases
- **RFC**: `docs/rfcs/{name}.md` with context, proposal, alternatives, rollout plan

Before generating, Glob for existing docs (`docs/**/*.md`) to understand numbering and format conventions.

Cross-reference `/project-bootstrap` for new projects — use it first to scaffold directory structure.

## Tech Stack Defaults (override if user specifies otherwise)

```yaml
mobile:
  language: Kotlin
  ui: Jetpack Compose
  architecture: MVI + Clean Architecture (domain/data/presentation layers)
  di: Hilt
  async: Coroutines + StateFlow
  testing: JUnit5 + MockK + Turbine + Robolectric + Espresso / Maestro

backend:
  runtime: Node.js / Python (Cloud Functions) or Kotlin (Ktor)
  infra: GCP (Cloud Run, Pub/Sub, Firestore, BigQuery)
  auth: Firebase Auth
  payments: Stripe API
  testing: JUnit5 / Pytest + Testcontainers

api:
  spec_format: OpenAPI 3.1 (YAML)
  auth: Bearer JWT (Firebase token)
  versioning: /v1/ path prefix

design:
  system: Material Design 3
  handoff: Figma
  tokens: Yes (color, spacing, typography)
```
