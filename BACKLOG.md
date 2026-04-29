# BACKLOG

Internal improvement backlog. Captured 2026-04-29 from comparative evaluation against `alirezarezvani/claude-skills` (235 skills, 13K stars, 12-tool support).

This repo is **internal-only** — not for public distribution, no marketplace. Tickets reflect that constraint.

---

## Resolution Status (2026-04-29)

All initial tickets resolved in a single batch session.

| # | Ticket | Status | Outcome |
|---|--------|--------|---------|
| T1 | Filesystem reorg | ✅ Done | 75 skills moved into 7 domain folders: engineering (39), platform (10), product (10), business (7), marketing (4), security (4), legal (1) |
| T2 | Personas | ✅ Done | 4 personas: cure-tech-lead, cure-product-lead, cure-engagement-pm, cure-solo-consultant |
| T3 | Scripts pattern + 5 pilots | ✅ Done | 7 stdlib Python scripts across dora-metrics, engineering-cost-model, saas-financial-model, burn-rate-tracker, accessibility-audit; convention doc + smoke test |
| T4 | 8 POWERFUL skills | ✅ Done | mcp-server-builder, rag-architect, agent-designer, agent-workflow-designer, monorepo-navigator, git-worktree-manager, env-secrets-manager, interview-system-designer (+ Gemini parity) |
| T5 | Skill security auditor | ✅ Done | New agent + PreToolUse hook on Write/Edit to skills/agents/personas |
| T6 | Self-improving memory | ✅ Done | New skill + 3 templates (MEMORY.md.template, feedback_template.md, project_template.md) |
| T7 | Internal overview doc | ✅ Done | scripts/generate-overview.py + docs/OVERVIEW.md (re-runnable) |

**Net delta:** 65 → 75 skills, 34 → 35 agents, 0 → 4 personas. Bootstrap test suite (106 tests) still green. JSON configs valid. All bundled scripts pass `--help` smoke test.

Detailed tickets below kept for historical reference.

---

## T1 — Reorganize `skills/` into domain subfolders

**Status:** Pending — needs user confirmation before starting

**Scope:**
Move flat `skills/{name}/SKILL.md` into `skills/{domain}/{name}/SKILL.md`. Domains: `engineering`, `product`, `marketing`, `business`, `legal`, `security`, `platform`.

**Why:** With 66 skills (and growing toward ~100 after T4 + T6), the flat structure is becoming hard to navigate. Domain subfolders match how skills are already grouped in `CLAUDE.md`.

**Why this changed from the eval:** Originally framed as marketplace sub-plugin bundles. Without a marketplace, granular install loses its value — this becomes a pure navigation/maintenance benefit.

**Blast radius:** Medium-high. Moving 66 directories breaks every reference: hooks/hooks.json, bootstrap CLI templates, plugin.json globs, internal links in CLAUDE.md, gemini-skills mirror.

**Acceptance:**
- [ ] All `skills/{name}/` → `skills/{domain}/{name}/`
- [ ] `gemini-skills/` mirrored
- [ ] `hooks/hooks.json` paths updated
- [ ] `bootstrap/` templates updated
- [ ] `CLAUDE.md` repo structure section updated
- [ ] Plugin still loads cleanly (smoke test)
- [ ] No broken internal links (grep for stale paths)

**Effort:** ~1 day with careful grep-and-replace. Worth doing in one PR.

---

## T2 — Add personas (engagement archetypes)

**Status:** In progress (subagent drafting)

**Scope:**
New top-level `personas/` folder. Four initial personas tailored for Cure consulting engagements:
- `cure-tech-lead` — engineering lead on a client engagement
- `cure-product-lead` — product/PM lead
- `cure-engagement-pm` — program/project manager
- `cure-solo-consultant` — single consultant, cross-domain

Each persona = identity + when-to-use + curated skill loadout + curated agent loadout + decision frameworks + voice + anti-patterns. References only skills/agents that already exist.

**Why:** Genuine architectural gap. Skills answer "how", agents answer "what", personas answer "who is thinking". Maps cleanly to Cure's engagement model — "spin up a tech-lead persona for this engagement."

**Blast radius:** Low — purely additive.

**Acceptance:**
- [ ] `personas/cure-tech-lead.md`
- [ ] `personas/cure-product-lead.md`
- [ ] `personas/cure-engagement-pm.md`
- [ ] `personas/cure-solo-consultant.md`
- [ ] Each references only existing skills/agents (verified via glob)
- [ ] `CLAUDE.md` updated with personas section
- [ ] `bootstrap/` CLI optionally provisions personas/ into client repos

**Effort:** ~1 day for the 4 files + CLAUDE.md update.

---

## T3 — Bundled stdlib scripts pattern + 5 pilot skills

**Status:** Pending

**Scope:**
Establish convention: each skill MAY ship `skills/{name}/scripts/*.py` — Python stdlib only, zero pip installs, all support `--help` and `--json`. Update SKILL.md to reference the script.

Pilot on five skills where executable tooling is highest-value:
1. **dora-metrics** — `deployment_frequency.py`, `mttr_calculator.py`, `change_failure_rate.py`
2. **engineering-cost-model** — `cost_estimator.py` (dev hours × rate + infra)
3. **saas-financial-model** — `unit_economics.py` (MRR, churn, LTV/CAC)
4. **burn-rate-tracker** — `runway_calculator.py` (cash, monthly burn, scenarios)
5. **accessibility-audit** — `wcag_check.py` (run static checks, parse axe output)

**Why:** Skills become *executable*, not just instructional. Reproduces alirezarezvani's "305 stdlib Python tools" pattern, which is the single biggest reason their skills feel production-grade.

**Blast radius:** Low — additive.

**Acceptance:**
- [ ] Convention documented in `CLAUDE.md` (script naming, stdlib-only rule, --help/--json convention)
- [ ] 5 pilot skills each have ≥1 working script
- [ ] Each script verified to run with `python3 scripts/<name>.py --help`
- [ ] Each SKILL.md references its script(s) with usage examples
- [ ] Optional: `scripts/verify-skill-scripts.sh` that runs `--help` on all of them as a smoke test

**Effort:** ~3 days for pattern + 5 pilots.

---

## T4 — Port 8 POWERFUL-tier engineering skills

**Status:** Pending

**Scope:**
Add 8 new skills, each shaped to Cure's consulting profile:

| Skill | Why for Cure |
|---|---|
| **mcp-server-builder** | Clients increasingly want MCP integrations |
| **rag-architect** | AI feature builds — chunking, retrieval eval |
| **agent-designer** | Multi-agent orchestration for client products |
| **agent-workflow-designer** | Sequential/parallel/router/orchestrator/evaluator patterns |
| **monorepo-navigator** | Most client codebases are monorepos (Turborepo/Nx/pnpm) |
| **git-worktree-manager** | Parallel work on client engagements |
| **env-secrets-manager** | Every engagement has `.env` hygiene needs |
| **interview-system-designer** | Hiring help for client teams |

Each skill follows the Cure SKILL.md format:
- YAML frontmatter (`name`, `description`, `argument-hint`, `allowed-tools` if read-only, `disable-model-invocation` if sensitive)
- Step 1: Classify (what flavor of the problem)
- Step 2: Gather Context
- Step 3+: Framework / Output

**Why:** Closes the largest skill-breadth gap with alirezarezvani while only including skills that fit consulting work.

**Blast radius:** Low — additive.

**Acceptance:**
- [ ] 8 SKILL.md files in `skills/{name}/SKILL.md`
- [ ] 8 Gemini parity files in `gemini-skills/{name}.skill`
- [ ] Each links to relevant Cure rules where applicable (e.g., mcp-server-builder → web.md and python.md)
- [ ] T3-pattern scripts where executable tooling makes sense (especially: agent-designer, env-secrets-manager, monorepo-navigator)

**Effort:** ~1 day per skill. Parallelizable across subagents — could be 1 calendar day if 4 subagents run in parallel.

---

## T5 — Skill security auditor agent + hook

**Status:** Pending

**Scope:**
- New agent `agents/skill-security-auditor.md` — scans SKILL.md, agent files, and `personas/*.md` for security risks before they enter the repo.
- Detects: command injection patterns, code execution risks (`eval`, `exec`, dynamic imports without validation), data exfiltration, prompt injection patterns, supply chain risks (untrusted URLs, pinned-by-tag dependencies).
- Returns `PASS / WARN / FAIL` with remediation guidance. Uses `audit-report` output style.
- Wire into `hooks/hooks.json` `PreToolUse` for `Write` ops on `skills/**`, `agents/**`, `personas/**`.

**Why:** This repo IS a plugin that gets installed into client environments. Supply-chain hygiene matters — both for our own additions and for any community-contributed skills we adopt.

**Blast radius:** Low. The hook adds latency on writes to those paths only.

**Acceptance:**
- [ ] `agents/skill-security-auditor.md` agent definition
- [ ] Agent uses Read-only tools
- [ ] Documented detection rules with examples
- [ ] PreToolUse hook entry that triggers on `Write` to `skills/**` / `agents/**` / `personas/**`
- [ ] CI step (optional, deferred): run auditor on all skills in `.github/workflows/` on PR

**Effort:** ~2 days.

---

## T6 — Self-improving memory skill

**Status:** Pending

**Scope:**
New skill `skills/self-improving-memory/SKILL.md` codifies Cure's pattern for auto-memory curation, applicable both inside this repo and inside client engagements bootstrapped from this repo.

Captures:
- When to save each memory type (user/feedback/project/reference) — the rules already in our CLAUDE.md auto-memory section
- Pattern detection: when ≥3 similar feedback memories accumulate, propose extracting them as a `feedback` rule or as a new skill
- Memory health checks: identify stale memories, contradictions, duplicates
- How to seed `MEMORY.md` for a new client engagement

**Why:** We already use auto-memory inside this repo. Formalizing the pattern as a skill makes it portable — every client engagement gets the same memory hygiene.

**Blast radius:** Low — additive.

**Acceptance:**
- [ ] `skills/self-improving-memory/SKILL.md` with Cure format
- [ ] Optional script `scripts/memory_health_check.py` (T3 pattern)
- [ ] Bootstrap CLI provisions a starter `MEMORY.md` template
- [ ] Gemini parity version

**Effort:** ~2 days.

---

## T7 — Internal overview doc

**Status:** Pending

**Scope:**
Single `docs/OVERVIEW.md` (or small `docs/` tree if it gets long) — internal-only reference, NOT a public mkdocs site.

Auto-generated content:
- All skills with one-line descriptions, grouped by domain
- All agents with one-line purpose + tool access
- All personas with one-line identity
- All hooks: which event, what they do
- All rules: which globs trigger them
- All output styles
- MCP servers configured
- LSP servers configured
- Bootstrap CLI commands

Generator: `scripts/generate-overview.py` — reads frontmatter from each file, emits the markdown. Re-run after adding new skills/agents.

**Why:** "What does this plugin actually do?" is an annoying question to answer from memory. One file, single source of truth.

**Blast radius:** Low — additive.

**Acceptance:**
- [ ] `scripts/generate-overview.py` (stdlib only, T3 pattern)
- [ ] Generated `docs/OVERVIEW.md`
- [ ] Convention: regenerate on every skill/agent/persona add (mention in CLAUDE.md, optionally enforce via PreCommit hook later)

**Effort:** ~3 days. Could be ~1 day if we keep the generator simple.

---

## Dropped from original eval

- **Marketplace sub-plugin bundles** — repo is internal, no public distribution
- **T8 multi-tool conversion** (Cursor/Codex/Windsurf/etc.) — only worth doing if we actually have client demand for those tools
- **C-suite advisor expansion** (10 advisor roles) — not selling this service
- **Marketing pod expansion** (44 marketing skills) — not selling this service

---

## Order of execution (suggested)

1. **T2** (personas) — small, additive, fills real gap
2. **T6** (self-improving memory) — small, additive
3. **T3** (scripts pattern + 5 pilots) — establishes convention used by T4, T5, T7
4. **T5** (skill security auditor) — defensive, useful before T4 lands large skill batch
5. **T4** (8 POWERFUL skills) — largest batch, parallelize via subagents
6. **T7** (overview doc) — last, since it consumes everything else
7. **T1** (filesystem reorg) — last, blast radius highest, do once everything else is stable

T1 deliberately last so we only re-shuffle paths once.
