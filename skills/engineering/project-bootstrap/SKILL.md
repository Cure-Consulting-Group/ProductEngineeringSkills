---
name: project-bootstrap
description: "Writes a tailored CLAUDE.md and STATE.md for a repo by interview. Use when onboarding an existing or new repo to agent work by hand, without the Cure manifest CLI."
when_to_use: "NOT for manifest-driven Cure infra with init/apply/doctor (use cure-infra-bootstrap). NOT for app code scaffolds (use nextjs-feature-scaffold, android-feature-scaffold)."
argument-hint: "[project-name]"
---

# Project Bootstrap Agent

Produce two files at repo root: `CLAUDE.md` (static project identity and rules) and `STATE.md`
(session state agents read and write). Done when both exist, every section is backed by a detected
signal or an interview answer, and the user has seen the included/omitted summary.

Boundary: this skill hand-writes the two files from an interview. `cure-infra-bootstrap` runs the
`claude-bootstrap` CLI to provision a manifest-tracked, upgradeable `.claude/` setup. If the project
already has `claude.manifest.json`, stop and use that skill instead — hand edits would drift from it.

## Pre-Processing (Auto-Context)

Context (pre-filled in Claude Code; in other runtimes run these commands first):

- Existing agent files: !`ls CLAUDE.md AGENTS.md GEMINI.md STATE.md claude.manifest.json 2>/dev/null || echo "(none)"`
- Stack manifest: !`ls package.json build.gradle.kts Podfile pubspec.yaml Cargo.toml go.mod pyproject.toml 2>/dev/null || echo "(none detected)"`
- Portfolio: !`sed -n '1,20p' PORTFOLIO.md 2>/dev/null || echo "(no PORTFOLIO.md)"`

## Step 1: Inspect the codebase (silently)

Inspect before asking anything; use results to pre-fill the interview, don't print them.

| Signal | Where to look |
|---|---|
| Stack, monorepo vs single module | root layout, manifests above |
| CI/CD | `.github/workflows/`, `.circleci/`, `Jenkinsfile` |
| Tests | `*Test*`, `*Spec*`, `*.test.*` files and runner config |
| Firebase / Firestore | `google-services.json`, `GoogleService-Info.plist`, `firebase.json`, `firestore.rules` |
| Stripe | Stripe SDK in any manifest |
| Compliance | HIPAA (PHI, patient, clinical), COPPA (guardian, minor, dob), GDPR/CCPA (consent, retention) keywords |
| Localization | `strings.xml`, `Localizable.strings`, `*.arb`, i18n dirs |
| Environments | `.env*`, flavors/buildTypes, multiple Firebase project IDs |
| AI APIs | Anthropic, Gemini, Vertex, OpenAI, Bedrock SDKs or keys |

If `CLAUDE.md` exists, ask "Overwrite or merge?" before going further.

## Step 2: Interview (one grouped message)

Ask everything in a single message; pre-fill detected answers marked `[detected]` for confirmation.

1. Project name and one-sentence description (what, for whom)
2. Platforms and architecture pattern (MVI / MVVM / TCA / Clean / other)
3. Key dependencies and services
4. Current sprint goal, up to 5 active tasks (`[ID] description — owner`), known blockers
5. Hard constraints agents must never violate
6. Active agents: Claude Code, Codex, Antigravity, Cursor, other
7. Compliance: HIPAA (list PHI fields), COPPA, PCI (or fully delegated to Stripe), GDPR/CCPA, none
8. Environments: `env → Firebase project | Stripe test/live | build variant`
9. Locales: default, additional, string source of truth
10. Git protocol: branching, commit format, protected branches
11. Cost guardrails needed: AI API limits, Firestore pagination, Functions recursion, Stripe key guard

Generate nothing until the interview is answered.

## Step 3: Generate CLAUDE.md

Read `reference/details.md` now — it holds the CLAUDE.md and STATE.md templates.

Always include: header, stack, architecture, key dependencies, agent roles, Rules — Always / Never,
git protocol, incident protocol, definition of done.

Include only when confirmed by inspection or interview:

| Section | Include when |
|---|---|
| Firebase Collections / Firestore Schema | Firebase detected / Firestore reads or writes in source |
| Stripe Configuration, Cost Guardrails — Stripe | Stripe detected |
| Environment Matrix | 2+ environments detected or stated |
| Compliance — HIPAA / COPPA / GDPR-CCPA | signal detected or interview confirms |
| Compliance — PCI | Stripe detected and custom card input suspected |
| Locale Configuration | 2+ locales |
| Cost Guardrails — AI | Anthropic, Gemini, Vertex, OpenAI, or Bedrock detected |
| Cost Guardrails — Firestore / Functions | Firebase / Cloud Functions detected |

Never add a compliance section speculatively: an unfounded HIPAA or COPPA section makes agents
enforce rules the project doesn't have, and a missing real one is worse — ask when unsure.

Multi-runtime: Codex reads `AGENTS.md`, not `CLAUDE.md`. If Codex is active, write the content to
`AGENTS.md` and make `CLAUDE.md` a one-line `@AGENTS.md` import (Claude Code documents this pattern).
For Antigravity, Cure repos use `GEMINI.md`; confirm the file your agy version reads before relying on it.

## Step 4: Generate STATE.md

From the template in the same reference file. The Task Queue gets at least one row from the
interview. STATE.md is archived to `STATE_[DATE].md` at sprint end and regenerated.

## Step 5: Report

Print: each file with line count, sections included (and the signal that justified each), sections
omitted (and why), and next steps — review Firestore field types and environment IDs, confirm the
task queue, commit both files. Offer (don't auto-run) the sprint-0 follow-ups: `ci-cd-pipeline`,
`security-review`, `testing-strategy`, `observability`, and adding the project to a parent
`PORTFOLIO.md` if one exists.

## Rules

- Don't invent stack, dependencies, or rules — write only what was detected or stated.
- Omit a section with no data rather than leaving placeholders.
- Write both files at repo root.
- Deliver the two files; don't scaffold code, hooks, or CI unless asked.

## Related Skills

- `cure-infra-bootstrap` — manifest-driven Cure infrastructure (use instead when upgrades and drift checks matter)
- `self-improving-memory` — seed auto-memory alongside these files at engagement start
- `sdlc` — PRDs, ADRs, and backlog after bootstrap
- `firebase-architect`, `incident-response` — deepen the Firestore schema and incident protocol
