---
name: portfolio-registry
description: "Creates and maintains PORTFOLIO.md, the registry of every product, stack, team, and stage. Use when setting up the portfolio, registering or updating a product, or health-checking a stale registry."
when_to_use: "NOT for the tech Adopt/Trial/Hold radar itself (technology-radar) or financial runway models (burn-rate-tracker)."
argument-hint: "[portfolio-or-product]"
context: fork
---

# Portfolio Registry

**Outcome:** a current `PORTFOLIO.md` — company overview, one section per product, shared
infrastructure, team allocation, health scorecard, cross-product dependencies, and a ≤500-token AI
session context block — with `[TBD]` for anything unknown and no secrets. Done when the validation
checklist (Step 7) passes. Other skills (sdlc, security-review, engineering-cost-model,
saas-financial-model, incident-response, go-to-market, …) read this file for portfolio context.

**Location.** The canonical file is `PORTFOLIO.md` at the project root (the path every skill's
context block reads). For a cross-project copy, keep one master in a shared repo and import it: add
`@PORTFOLIO.md` to CLAUDE.md, and reference it from AGENTS.md (Codex) or GEMINI.md / Antigravity rules
so every runtime loads it.

## Pre-Processing (Auto-Context)

Context — run these read-only commands first; skip any that fail or aren't permitted (they only tailor the output):

- Existing registry: `grep -m1 -i "last updated" PORTFOLIO.md 2>/dev/null || echo "(no PORTFOLIO.md here)"`
- Registered products: `grep -E '^### ' PORTFOLIO.md 2>/dev/null | head -8 || true`

Read the whole existing PORTFOLIO.md before any update.

## Step 1: Classify

| Request | Do | Output |
|---|---|---|
| Full registry | Interview, generate every section | New PORTFOLIO.md |
| Register one product | Ask about that product only | Updated PORTFOLIO.md |
| Update a product (stage, priority, team, stack) | Edit that section + scorecard + context block | Updated PORTFOLIO.md |
| Decommission | Stage → sunset, record shutdown/migration plan | Updated PORTFOLIO.md |
| Health check | Staleness + consistency audit (Step 7) | Findings + proposed edits |
| Auto-detect | Scan repos the user names (Step 2) | Draft for confirmation |

"Set up the portfolio" / "register everything" → full registry. A named product → register or update.
Otherwise ask once which.

## Step 2: Gather Context

**Interview (full registry).** Accept partial answers; infer and mark `[TBD]` for the rest.
- Company: name (default Cure Consulting Group), model (studio / consultancy / hybrid), headcount, burn, runway.
- Per product: one-liner, stage (idea / MVP / beta / growth / mature / sunset), priority (P0 existential / P1 strategic / P2 opportunistic / P3 maintenance), revenue model and MRR, team and roles, stack, repos, environments (Firebase project IDs, domains), compliance (HIPAA, NCAA, COPPA, GDPR, PCI, SOC 2), locales, sprint goal, top risks, dependencies.
- Shared infra: auth and shared identity, design tokens, analytics, CI/CD, AI models and cost tracking.

**Auto-detect.** Scan only directories the user names (never sweep home directories). Per repo read
`package.json`, `build.gradle(.kts)`, `Podfile`/`Package.swift`, `.firebaserc`, `.github/workflows/`,
README, `git remote -v`, and `git log -1`. Read `.env.example` for environment names; never open
`.env` or other secret files — the registry must stay free of secrets. Present findings for
confirmation before writing.

**Cure defaults** (pre-populate for Cure Consulting Group, then confirm with the user):

1. Vendly — LATAM merchant OS (Android/iOS, Firebase, Stripe, multi-language)
2. Autograph — AI medical scribe (HIPAA, LLM, clinical workflow)
3. The Initiated — women's basketball recruiting (NCAA, B2B+B2C, events)
4. TwntyHoops — basketball media/events (content, community)
5. Cure Consulting Group — the consultancy (client work, this skill library)

## Step 3: Write the Registry

Read `reference/templates.md` when writing or regenerating sections — it holds the company and
per-product tables, radar summary, team roster, health scorecard with scoring criteria, AI session
context block, and maintenance schedule. Read `reference/details.md` when writing the shared
infrastructure and cross-product dependency sections.

Section order: Company Overview → Products → Shared Infrastructure → Technology Radar summary (a
snapshot; the technology-radar skill owns the full radar) → Team Roster & Allocation → Health Scorecard
→ Cross-Product Dependencies → AI Session Context → Maintenance + changelog.

Rules:
- Every section present; `[TBD]` for unknowns rather than omission.
- Model fields name exact model IDs in use, not model families from memory.
- For a single-product update, edit that product's section and every section that summarizes it (scorecard, dependencies, context block); leave the rest unchanged.

## Step 4: Allocation Rules (Cure positions)

- No engineer split across more than two products in a sprint; P0 gets first claim on shared people.
- Key-person risk HIGH = the product stalls >2 weeks if that person leaves.
- Utilization >85% is a red flag (no slack for incidents); contractors don't own critical-path work without a knowledge-transfer plan.
- Hiring priorities fall out of allocation gaps, highest-priority product first.

## Step 5: Health Scorecard

G/Y/R per product for team, tech debt, security, compliance, plus stage, priority, MRR, burn, runway.
Security is R with no audit in 6+ months or any open critical finding. A P0 product at "idea" stage
is an inconsistency to flag.

## Step 6: Maintenance

Update immediately on stage, priority, team, fundraise, compliance, shared-infra, or repo changes.
Stale if last updated >30 days ago, a sprint goal is finished, the roster disagrees with the GitHub
org, MRR is >1 quarter old, or a `[TBD]` is >2 weeks old. Keep a changelog at the bottom; git-track
the file (it contains no secrets).

## Step 7: Validate and Deliver

- [ ] Every product has all fields filled or `[TBD]`; stage and priority are consistent
- [ ] Allocation per person sums to ~100% (flag >120%)
- [ ] Shared infra matches what products reference; dependencies listed on both sides
- [ ] AI Session Context block ≤500 tokens
- [ ] No secrets, keys, or passwords; compliance filled for regulated products

Report what changed and which fields remain `[TBD]`. Suggest engineering-cost-model, security-review,
or saas-financial-model only if the user's next decision needs them.
