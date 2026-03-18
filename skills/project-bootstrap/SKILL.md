---
name: project-bootstrap
description: "Bootstrap any project repo with CLAUDE.md and STATE.md — interviews the developer, inspects the codebase, and generates agent coordination files"
argument-hint: "[project-name]"
---

# Project Bootstrap Agent

Initialize any repository's agent coordination layer by generating two files: `CLAUDE.md` (static project identity) and `STATE.md` (dynamic session state). Works by inspecting the codebase autonomously, then interviewing the developer to fill gaps.

Do not generate either file until the interview is complete.

## Pre-Processing (Auto-Context)

Before starting, gather project context silently:
- Read `PORTFOLIO.md` if it exists in the project root or parent directories for product/team context
- Run: `cat package.json 2>/dev/null || cat build.gradle.kts 2>/dev/null || cat Podfile 2>/dev/null` to detect stack
- Run: `git log --oneline -5 2>/dev/null` for recent changes
- Run: `ls src/ app/ lib/ functions/ 2>/dev/null` to understand project structure
- Use this context to pre-fill answers during the developer interview

## Step 1: Codebase Inspection (Autonomous)

Before asking anything, silently inspect the codebase and store results in working memory. Do not print results — use them to pre-fill answers and skip redundant interview questions.

**Run these inspections:**

| Inspection | What to Detect |
|---|---|
| PORTFOLIO.md | Check project root and parent directories for portfolio/team context |
| Project structure | `ls -la`, root directory layout, monorepo vs single module |
| Language/framework | `package.json`, `build.gradle.kts`, `Podfile`, `pubspec.yaml`, `Cargo.toml` |
| CI/CD | `.github/workflows/`, `.circleci/`, `Jenkinsfile` |
| Existing context files | Check if `CLAUDE.md` or `STATE.md` already exist |
| README | First 40 lines for project description |
| Test framework | Files matching `*Test*`, `*Spec*`, `*test*` |
| Firebase | `google-services.json`, `GoogleService-Info.plist`, `firebase.json` |
| Stripe | Stripe references in gradle, package.json, toml files |
| Compliance — HIPAA | PHI, medical, patient, clinical keywords in source |
| Compliance — COPPA | Guardian, minor, dob, parental keywords in source |
| Compliance — GDPR/CCPA | GDPR, CCPA, consent, privacy, data retention keywords |
| Localization | `strings.xml`, `Localizable.strings`, `*.arb`, i18n directories |
| Firestore schema | `firestore.rules`, collection/document references in source |
| Environment config | `.env*` files, flavor/buildType/environment configs |
| CI/CD workflows | Workflow YAML files, deploy/test/lint steps |
| AI APIs | Gemini, Vertex, OpenAI, Anthropic, Bedrock references |
| Pagination patterns | `.limit`, `.pageSize`, `paginate`, `offset` in source |

**If `CLAUDE.md` already exists:** Ask before overwriting — "CLAUDE.md found. Overwrite or merge?"

## Step 2: Developer Interview

Ask the following questions **in a single grouped message**. Do not ask them one by one. Pre-fill any answers you already know from Step 1 and mark them as `[detected]` so the developer can confirm or correct.

```
Bootstrap Interview — Answer all that apply:

1. PROJECT NAME
   What is this project called?

2. PRODUCT DESCRIPTION
   One sentence: what does this product do and who is it for?

3. PLATFORM(S) — Check all that apply:
   [ ] Android (Kotlin / Jetpack Compose)
   [ ] iOS (Swift / SwiftUI)
   [ ] React Web / Next.js
   [ ] Firebase Backend (Firestore / Functions / Auth)
   [ ] Node.js / Express API
   [ ] Other: ___________

4. ARCHITECTURE PATTERN
   Primary architecture? (e.g. MVI, MVVM, TCA, Clean Architecture, Redux)

5. KEY DEPENDENCIES
   Major libraries or services this project uses.
   (e.g. Hilt, Stripe Connect, Gemini API, Vertex AI, Coroutines, Orbit MVI)

6. CURRENT SPRINT GOAL
   What is the team trying to ship RIGHT NOW? One sentence.

7. ACTIVE TASKS
   List up to 5 tasks currently in progress or queued.
   Format: [TASK_ID] Description — Owner (Claude Code | Cursor | Gemini CLI | Human)

8. KNOWN BLOCKERS
   Anything currently blocked or waiting on an external dependency?

9. HARD CONSTRAINTS — Rules agents must NEVER violate:
   (e.g. "Never use LiveData", "All prices in USD cents", "Stripe webhooks require idempotency keys")

10. AGENT OWNERS — Which agents are active on this project?
    [ ] Claude Code (primary engineer)
    [ ] Cursor (code generation / refactor)
    [ ] Gemini CLI (research / review)
    [ ] Antigravity (orchestrator)
    [ ] Other: ___________

11. COMPLIANCE FLAGS — Check all that apply:
    [ ] HIPAA — handles PHI (Protected Health Information)
         If yes → list PHI field names: ___________
    [ ] COPPA — any users under 13, requires guardian consent flow
    [ ] PCI — payments in scope (or fully delegated to Stripe?)
    [ ] GDPR / CCPA — EU or California users
    [ ] None of the above

12. ENVIRONMENTS — List your Firebase projects / build variants:
    Format: [env] → [Firebase project ID] | [Stripe mode: test/live] | [build variant]

13. LOCALES / LANGUAGES
    Default language: ___________
    Additional locales supported: ___________
    String source of truth: [ ] strings.xml  [ ] Localizable.strings  [ ] Firestore Remote Config  [ ] i18n JSON

14. GIT PROTOCOL
    Branching strategy: [ ] Gitflow  [ ] trunk-based  [ ] feature branches  [ ] other: ___
    Commit format: [ ] Conventional Commits  [ ] free-form  [ ] other: ___
    Protected branches (never commit directly): ___________

15. COST GUARDRAIL CONTEXT
    [ ] Using AI APIs (Gemini / Vertex / OpenAI) — need per-call limits
    [ ] Firestore at scale — need pagination enforcement
    [ ] Firebase Functions — need recursion guards
    [ ] Stripe live keys exist in repo — need hard env block
    [ ] None / not applicable yet
```

## Step 3: Generate CLAUDE.md

Generate at repo root. This file is **static** — it defines the project identity and rules for all agents. Agents read it at session start. It changes only when the stack or rules change.

**Required sections (always include):**

- Project header (name + one-sentence description)
- Stack table (layer → technology)
- Architecture (pattern, module structure, state management)
- Key Dependencies (dependency → purpose)
- Agent Roles table
- Rules — Always / Rules — Never
- Git Protocol
- Incident Protocol (P0/P1/P2 table)
- Definition of Done checklist

**Conditional sections (include only when signals are confirmed):**

| Section | Include When |
|---|---|
| Firebase Collections | `google-services.json` detected OR Firebase in dependencies |
| Stripe Configuration | Stripe detected in gradle/package.json |
| Firestore Schema | Firestore reads/writes detected in source files |
| Environment Matrix | Multiple env configs detected OR interview confirms multi-env |
| Compliance — HIPAA | PHI/medical/clinical signals detected OR interview confirms |
| Compliance — COPPA | Minor/guardian/dob signals detected OR interview confirms |
| Compliance — PCI | Stripe detected AND custom card input suspected |
| Compliance — GDPR/CCPA | EU locale or California scope mentioned in interview |
| Locale Configuration | Multiple locale files detected OR interview lists 2+ languages |
| Cost Guardrails — AI | Gemini/Vertex/OpenAI detected in source |
| Cost Guardrails — Stripe | Stripe detected |
| Cost Guardrails — Firestore | Firebase detected |
| Cost Guardrails — Functions | Cloud Functions detected |
| Environment Files | Only list env files that actually exist |

> Never include a compliance section speculatively. Only include it if signals are confirmed by either codebase inspection or explicit interview response.

### CLAUDE.md Template

```markdown
# [PROJECT_NAME]
> [ONE_SENTENCE_DESCRIPTION]

---

## Stack

| Layer       | Technology                          |
|-------------|-------------------------------------|
| [Layer]     | [Technology]                        |

---

## Architecture

- Pattern: [MVI | MVVM | TCA | Clean | etc.]
- Module structure: [describe if monorepo, feature modules, etc.]
- State management: [StateFlow + MVI | TCA Store | Redux | etc.]

---

## Key Dependencies

- [Dependency] — [purpose]

---

## Agent Roles

| Agent         | Responsibility                          |
|---------------|-----------------------------------------|
| Claude Code   | [what Claude Code owns on this project] |
| Cursor        | [what Cursor owns]                      |
| Gemini CLI    | [what Gemini owns]                      |
| Antigravity   | [orchestration scope]                   |

---

## Rules — Always

- [Rule 1]
- [Rule 2]

## Rules — Never

- [Rule 1]
- [Rule 2]

---

## Firebase Collections

| Collection    | Description              | Auth Scope     |
|---------------|--------------------------|----------------|
| [collection]  | [purpose]                | [uid scoped?]  |

*(omit section if Firebase not used)*

---

## Stripe Configuration

- Platform account: [yes/no]
- Connect type: [Express | Standard | Custom | N/A]
- Webhook events handled: [list]
- Idempotency keys: required on all PaymentIntent creates

*(omit section if Stripe not used)*

---

## Environment Files

- `.env.local` — [what it contains]
- `google-services.json` — [Android Firebase config]
- `GoogleService-Info.plist` — [iOS Firebase config]

*(list only what exists)*

---

## Firestore Schema

| Collection         | Key Fields                        | Auth Scope          | Notes                     |
|--------------------|-----------------------------------|---------------------|---------------------------|
| [collection_path]  | [field: type, field: type]        | [uid-scoped? yes/no]| [any migration notes]     |

> Field type must be explicit — never assume. Mismatches between clients cause silent data corruption.
> If a field type changes, add a migration note here and in the Decisions Log.

*(omit section if Firestore not used)*

---

## Environment Matrix

| Env      | Firebase Project       | Stripe Mode | Build Variant | Notes                    |
|----------|------------------------|-------------|---------------|--------------------------|
| dev      | [project-id]-dev       | test        | debug         | local emulator preferred |
| staging  | [project-id]-staging   | test        | release       | CI deploys here          |
| prod     | [project-id]-prod      | live        | release       | manual deploy only       |

> Agents must verify active environment before any Firebase write or Stripe call.
> Never use live Stripe keys outside of prod build variant.

*(customize rows to match actual project environments)*

---

## Compliance Requirements

*(Omit entire section if no compliance flags apply.)*

### HIPAA *(include if PHI is handled)*
- PHI fields: [list field names]
- PHI must never appear in: logs, Crashlytics, analytics events, error messages
- Firebase collections containing PHI: [list paths]
- Encryption at rest: required for all PHI fields in Firestore
- Agents must not add new PHI fields without explicit human approval

### COPPA *(include if any users may be under 13)*
- Guardian consent flow: required before any data collection for minors
- Date of birth collection: must gate all feature access
- No behavioral advertising targeting minors
- Agents must not skip or stub the consent gate — ever

### PCI *(include if payment card data flows through app)*
- Card data: never stored locally, never logged, fully delegated to Stripe SDK
- Stripe Elements / PaymentSheet: required — no custom card input fields
- Agents must not build custom card number, CVV, or expiry input components

### GDPR / CCPA *(include if EU or California users)*
- Data deletion: user-initiated delete must purge all Firestore docs + Auth record
- Consent: explicit opt-in required before analytics or marketing events
- Data export: must be implementable on request

---

## Locale Configuration

| Locale | Language   | Status              | String Source                        |
|--------|------------|---------------------|--------------------------------------|
| en     | English    | default             | [strings.xml / Localizable.strings]  |
| [es]   | [Spanish]  | [active / planned]  | [same / Firestore Remote Config]     |

- Default locale: [en]
- RTL support required: [yes / no]
- Agents must not hardcode user-facing strings — use resource keys only
- New strings must be added to ALL active locale files simultaneously

*(omit section if single-locale only)*

---

## Git Protocol

- Branching strategy: [Gitflow | trunk-based | feature branches]
- Branch naming: `feature/[TASK_ID]-short-description` | `fix/[TASK_ID]-short-description`
- Commit format: [Conventional Commits — `feat:` `fix:` `chore:` `refactor:` `test:`]
- PR requirements: passing CI + STATE.md updated + zero TODO comments + agent review note
- Protected branches — never commit directly: `main`, `release/*`
- Hotfix path: `hotfix/[description]` → PR to `main` + backmerge to `develop`

---

## Cost Guardrails

### AI APIs *(include if Gemini / Vertex / OpenAI detected)*
- Never call AI APIs inside a loop without an explicit item limit
- Always paginate before passing list data to a model
- Cache responses where TTL is acceptable — do not re-call for identical inputs
- Log token usage in dev; alert if single-session cost exceeds $[X]

### Firestore *(include if Firebase detected)*
- Never read an entire collection without `.limit(n)` — max [50] docs per read
- Use compound queries over client-side filtering
- Avoid `onSnapshot` listeners on large collections without scoped queries
- Index all fields used in compound `where` + `orderBy` queries

### Firebase Functions *(include if Cloud Functions detected)*
- No recursive triggers — a Firestore write in a Function must never trigger itself
- All HTTP Functions must have auth middleware — no public endpoints without explicit approval
- Set memory/timeout limits explicitly — do not rely on defaults

### Stripe *(include if Stripe detected)*
- Live keys: environment variable only — never hardcoded, never committed
- Test/live key mismatch guard: assert `BuildConfig.STRIPE_MODE == "test"` in non-prod builds
- Idempotency keys: required on all `PaymentIntent` creates and confirms
- Webhook handlers: must be idempotent — check event ID before processing

---

## Incident Protocol

| Priority | Condition                                              | Agent Action                                              |
|----------|--------------------------------------------------------|-----------------------------------------------------------|
| P0       | Auth broken / payments failing / data loss / PHI leak  | Halt all tasks. Update STATE.md. Notify human immediately.|
| P1       | Core feature degraded / error rate > 5% / deploy fails | Complete current atomic unit. Flag in STATE.md blocker.   |
| P2       | Non-critical bug / UI issue / test failure             | Log in STATE.md unresolved. Continue sprint.              |

> On any P0: agents must stop mid-task, write incident summary to STATE.md under a new
> `## INCIDENT` header, and await human instruction before resuming any work.

---

## Definition of Done

A task is shippable when:
- [ ] Feature logic complete with error handling on all failure paths
- [ ] Unit tests written and passing (ViewModel + Repository minimum)
- [ ] No hardcoded strings, magic numbers, or TODO / FIXME comments
- [ ] Firebase security rules updated to cover any new collections
- [ ] Environment matrix verified — correct project targeted
- [ ] Compliance checklist passed for any PHI, minor, or payment-adjacent changes
- [ ] Locale files updated for all active locales if new strings added
- [ ] STATE.md updated — task marked Done, decisions logged
- [ ] Peer agent review complete (Cursor or Gemini sign-off)
```

## Step 4: Generate STATE.md

Generate at repo root. This file is **dynamic** — agents read AND write it every session. It gets archived (renamed to `STATE_[DATE].md`) at the end of each sprint.

### STATE.md Template

```markdown
# STATE.md — [PROJECT_NAME]
> Session runtime state. Agents read and write this file. Do not edit manually mid-session.

---

## Session Info

| Field          | Value                            |
|----------------|----------------------------------|
| Sprint goal    | [CURRENT_SPRINT_GOAL]            |
| Session opened | [YYYY-MM-DD HH:MM]               |
| Orchestrator   | [Claude Code | Antigravity | etc.]|
| Active branch  | [branch name]                    |

---

## Task Queue

| ID    | Task                              | Owner       | Status       | Blocker              |
|-------|-----------------------------------|-------------|--------------|----------------------|
| [T01] | [task description]                | [owner]     | [status]     | [blocker or —]       |

**Status values:** `Queued` | `In Progress` | `Blocked` | `In Review` | `Done`

---

## Context Handoff Block

> Copy this block verbatim when starting a new agent session on this project.

```
Project: [PROJECT_NAME]
Stack: [condensed stack]
Sprint goal: [CURRENT_SPRINT_GOAL]
Active env: [dev | staging | prod]
Last decision: [most recent architectural or product decision]
Hard constraints: [comma-separated never-rules]
Compliance flags: [HIPAA | COPPA | PCI | GDPR | none]
Active blocker: [blocker or "none"]
Resume from: [task ID and file/line if applicable]
```

---

## Decisions Log

Record any architectural, product, or integration decision made this session.
Format: `[YYYY-MM-DD] [DECISION] — [RATIONALE]`

- [date] [decision] — [why]

---

## Resolved This Session

- [ ] [task that was completed]

---

## Unresolved / Carry Forward

- [ ] [open question or task that did not get resolved]

---

## Agent Handoff Notes

Instructions for the next agent picking up this session:

- **Claude Code →** [what Claude Code left off / what to pick up]
- **Cursor →** [specific file + line or component to work on]
- **Gemini CLI →** [research or review task]
- **Antigravity →** [orchestration directive]

---

## INCIDENT LOG

*(Only populated on P0/P1. Format: `[YYYY-MM-DD HH:MM] [P0|P1] [description] — [status]`)*

---

## Sprint Archive

When the sprint ends, rename this file to `STATE_[SPRINT_END_DATE].md` and create a fresh `STATE.md`.
```

## Step 5: Validation

After generating both files, confirm they exist and display a summary:

```
Bootstrap complete.

CLAUDE.md — [X lines] — Project identity, stack, rules, agent roles, compliance, environments
STATE.md  — [X lines] — Active sprint state, task queue, handoff block, incident log

Sections auto-included:
  [list which optional sections were added and why]

Sections omitted:
  [list which optional sections were skipped and why]

Next steps:
1. Review CLAUDE.md — verify Firestore schema field types and environment project IDs
2. Review STATE.md — confirm task queue matches actual sprint
3. Commit both files to repo root
4. Every agent session starts with: "Read CLAUDE.md and STATE.md before any task"
5. Sprint end: rename STATE.md → STATE_[DATE].md, generate fresh STATE.md

Bootstrap agent signing off.
```

## Agent Self-Rules

- Do not generate `CLAUDE.md` until interview is complete
- Do not hallucinate stack or dependencies — only write what was detected or explicitly stated
- If a section has no data, omit the section entirely rather than leaving placeholders
- `STATE.md` Task Queue must have at least one row — use interview data
- Both files must be written to repo root, not a subfolder
- If `CLAUDE.md` already exists, ask before overwriting: "CLAUDE.md found. Overwrite or merge?"

## Post-Bootstrap Actions

After generating CLAUDE.md and STATE.md:

1. **PORTFOLIO.md integration**: If PORTFOLIO.md exists in a parent directory, offer to add this project as a new entry
2. **Initial sprint 0 tasks**: Based on detected stack, suggest initial setup tasks:
   - CI/CD setup → reference `/ci-cd-pipeline`
   - Security baseline → reference `/security-review`
   - Testing setup → reference `/testing-strategy`
   - Observability → reference `/observability`
3. **Git hooks**: Generate `.husky/pre-commit` with lint and type-check

## Related Skills

- `/sdlc` — Generate SDLC artifacts after bootstrap is complete
- `/ci-cd-pipeline` — Set up CI/CD workflows referenced in the bootstrap
- `/firebase-architect` — Deep-dive Firestore schema and security rules
- `/infrastructure-scaffold` — Generate cloud infrastructure configs
- `/incident-response` — Expand on the incident protocol defined in CLAUDE.md
