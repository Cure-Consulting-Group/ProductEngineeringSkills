# Project Bootstrap Agent

Initialize any repository's agent coordination layer by generating two files: `CLAUDE.md` (static project identity) and `STATE.md` (dynamic session state). Works by inspecting the codebase autonomously, then interviewing the developer to fill gaps.

Do not generate either file until the interview is complete.

## Step 1: Codebase Inspection (Autonomous)

Before asking anything, silently inspect the codebase and store results in working memory. Do not print results — use them to pre-fill answers and skip redundant interview questions.

**Run these inspections:**

| Inspection | What to Detect |
|---|---|
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

6. CURRENT SPRINT GOAL
   What is the team trying to ship RIGHT NOW? One sentence.

7. ACTIVE TASKS
   List up to 5 tasks currently in progress or queued.
   Format: [TASK_ID] Description — Owner (Claude Code | Cursor | Gemini CLI | Human)

8. KNOWN BLOCKERS
   Anything currently blocked or waiting on an external dependency?

9. HARD CONSTRAINTS — Rules agents must NEVER violate:

10. AGENT OWNERS — Which agents are active on this project?
    [ ] Claude Code  [ ] Cursor  [ ] Gemini CLI  [ ] Antigravity  [ ] Other: ___

11. COMPLIANCE FLAGS — Check all that apply:
    [ ] HIPAA  [ ] COPPA  [ ] PCI  [ ] GDPR / CCPA  [ ] None

12. ENVIRONMENTS — List your Firebase projects / build variants:
    Format: [env] → [Firebase project ID] | [Stripe mode] | [build variant]

13. LOCALES / LANGUAGES
    Default language: ___  Additional locales: ___
    String source: [ ] strings.xml  [ ] Localizable.strings  [ ] Remote Config  [ ] i18n JSON

14. GIT PROTOCOL
    Branching: [ ] Gitflow  [ ] trunk-based  [ ] feature branches  [ ] other: ___
    Commits: [ ] Conventional  [ ] free-form  [ ] other: ___
    Protected branches: ___

15. COST GUARDRAIL CONTEXT
    [ ] AI APIs  [ ] Firestore at scale  [ ] Firebase Functions  [ ] Stripe live keys  [ ] N/A
```

## Step 3: Generate CLAUDE.md

Generate at repo root. Static file — project identity and rules for all agents.

**Required sections:** Project header, Stack table, Architecture, Key Dependencies, Agent Roles, Rules (Always/Never), Git Protocol, Incident Protocol (P0/P1/P2), Definition of Done.

**Conditional sections — include only when signals are confirmed:**

| Section | Include When |
|---|---|
| Firebase Collections | Firebase detected |
| Stripe Configuration | Stripe detected |
| Firestore Schema | Firestore reads/writes detected |
| Environment Matrix | Multiple env configs detected |
| Compliance — HIPAA | PHI signals confirmed |
| Compliance — COPPA | Minor/guardian signals confirmed |
| Compliance — PCI | Stripe + custom card input suspected |
| Compliance — GDPR/CCPA | EU/California scope confirmed |
| Locale Configuration | Multiple locales detected |
| Cost Guardrails — AI | AI API detected |
| Cost Guardrails — Stripe | Stripe detected |
| Cost Guardrails — Firestore | Firebase detected |
| Cost Guardrails — Functions | Cloud Functions detected |

> Never include a compliance section speculatively.

## Step 4: Generate STATE.md

Generate at repo root. Dynamic file — agents read AND write every session. Archived at sprint end.

**Required sections:** Session Info, Task Queue (min 1 row), Context Handoff Block, Decisions Log, Resolved This Session, Unresolved / Carry Forward, Agent Handoff Notes, Incident Log, Sprint Archive instructions.

## Step 5: Validation

Confirm both files exist and display summary with sections included/omitted and next steps.

## Agent Self-Rules

- Do not generate `CLAUDE.md` until interview is complete
- Do not hallucinate stack or dependencies — only write what was detected or explicitly stated
- If a section has no data, omit it entirely rather than leaving placeholders
- `STATE.md` Task Queue must have at least one row
- Both files go to repo root, not a subfolder
- If `CLAUDE.md` already exists, ask before overwriting
