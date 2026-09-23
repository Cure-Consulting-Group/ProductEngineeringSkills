# SDLC Artifact Generator

Turns a feature description into traceable engineering documents: PRD → RFC/ADR → Epics → Stories →
Tasks and test specs. Done when the requested artifact exists, every story has Given/When/Then
criteria and points, and IDs link each artifact to its parent.

Match length to the need; no filler sections or restated summaries.

## Pre-Processing (Auto-Context)

Context (pre-filled in Claude Code; in other runtimes run these commands first):

- Existing specs (numbering and format to follow): !`{ ls docs/adr docs/rfcs docs/prd docs/epics 2>/dev/null || echo "(none)"; } | head -20`
- Issue templates in force: !`ls .github/ISSUE_TEMPLATE 2>/dev/null || echo "(none)"`
- Stack manifests: !`ls package.json build.gradle.kts Podfile pyproject.toml go.mod 2>/dev/null || echo "(none)"`

## Step 1: Classify

| Request | Primary artifact | Offer next |
|---|---|---|
| New feature/product | PRD → Epics → Stories | ADR, RFC, API spec, test specs |
| Architectural decision | ADR | RFC (if still undecided), implementing story |
| Proposal needing input | RFC | ADR after the decision |
| Backlog generation | Epics + Stories | Test specs, design tickets |
| Single story/ticket | Story + Tasks | Unit test spec |
| API definition | API spec (OpenAPI — version and conventions owned by `api-architect`) | Stories, contract test spec |

Ambiguous scope → ask once: "New feature, architecture decision, or full backlog?"

## Step 2: Gather Context

Feature/system name, platform, stack (defaults below), scope level, and constraints already in force
(existing ADRs, API contracts, design system). Infer what you can; ask at most one question.

## Step 3: Artifact Contracts

Write the sections listed; omit any that genuinely don't apply rather than padding.

- **PRD** — Problem (who, evidence), Goals and non-goals, Success metrics (baseline → target),
  Scope (Must/Should/Could/Won't), User flows, Requirements (functional, non-functional), Risks and
  open questions, Rollout (flag, phases), Epic list.
- **RFC** — Context, Proposal, Alternatives considered (each with why-not), Trade-offs, Rollout and
  migration, Open questions, Decision deadline and deciders.
- **ADR** — Status, Context, Decision, Consequences (positive, negative, follow-ups), Alternatives.
  One decision per ADR; never edit an accepted ADR — supersede it.
- **Epic** — Goal, stories list, dependencies, exit criteria.
- **Story** — "As a … I want … so that …", Given/When/Then criteria, points, linked design/API/test IDs.
- **Task / test spec** — implementation steps with files touched; test cases as input → expected result, including failure paths.

## Step 4: Conventions

**IDs:** `PRD-001`, `RFC-001`, `ADR-001`, `EPIC-001`, `STORY-001`, `TASK-001`, `DESIGN-001`,
`TEST-UNIT-001`, `TEST-E2E-001`, `API-001`. Continue existing numbering.

**Points (Fibonacci):** 1 trivial · 2 <4h · 3 ~1 day · 5 1–2 days · 8 2–3 days · 13 split
recommended · 21 must split before sprint.

**Acceptance criteria:** Given/When/Then for every story.

**Definition of Done (every story):** reviewed by ≥1 engineer; unit tests pass and coverage meets
the `testing-strategy` threshold (that skill owns the number); integration/E2E test if the story
crosses a boundary; API spec updated if the contract changed; ADR for any architectural decision
made during implementation; design QA for UI changes; no new lint violations; feature flag if the
rollout is staged.

**Ordering:** MoSCoW inside each epic; sequence Infrastructure → Data → Business logic → UI →
Integration → Polish/QA.

## Step 5: Deliver

- 1–3 stories, or one ADR the user will paste elsewhere: answer inline.
- Anything larger, or when the repo already keeps specs in `docs/`: write files at the existing
  paths (defaults `docs/prd/{name}.md`, `docs/adr/{NNN}-{title}.md`, `docs/rfcs/{name}.md`,
  `docs/epics/{name}.md`, `docs/tasks/{id}.md`); multi-epic output gets a table of contents.
- Then offer the next artifact from the Step 1 table.

## Cure Stack Defaults (override when the user or repo says otherwise)

- Mobile: Kotlin, Jetpack Compose, MVI + Clean Architecture, Hilt, Coroutines/StateFlow; JUnit5, MockK, Turbine
- Backend: Cloud Functions (TypeScript/Python) or Ktor; GCP (Cloud Run, Pub/Sub, Firestore, BigQuery); Firebase Auth; Stripe
- API: `/v1/` path versioning, Firebase ID token as Bearer
- Design: Material 3, Figma handoff, tokens for color/spacing/type
