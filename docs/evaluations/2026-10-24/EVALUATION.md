# Evaluation — 2026-10-24: skills, agents, hooks, rules, mods, runtimes

Owner request: "do some more research to ensure all of our skills, tools, hooks, agents are all top notch. even our mods — are there improvements to make with them?" plus one concrete complaint: cc-pr-tracker has no way to clear merged PRs.

**Method.** Five read-only reviews, run in parallel: (1) Claude Code platform facts from the official docs, (2) Codex and Antigravity facts from docs and local CLIs, (3) all 106 skills, (4) agents, hooks, rules, output styles, settings, CI and docs, (5) all 15 Cure mods plus cc-pr-tracker. Every review cites file:line. The highest-stakes claims were re-checked by hand before they became tickets: the contradictory SOW terms, the bootstrap model pin, `memory:` granting Write/Edit, the cure-agent-budget leak and retired model ID, `claude plugin validate --strict` failing, and the empty Antigravity globs. This file is the synthesis. The tickets are Wave 7 in `BACKLOG.md`.

**Verdict.** The library's structure is sound. The audit scores 9.99, there are no `$0` or injection defects, no body is over 307 lines, all 22 scripts pass, and 33/33 guard tests and 61+ tri-lane tests pass. The real problems sit where the audit doesn't look:

1. **What consumers actually receive differs from what the docs say.** The plugin cannot ship permissions, rules or personas.
2. **Three of our hooks print text that Claude never sees.**
3. **Three mods are broken, and one of them is actively harmful.**
4. **A handful of skills contain facts that are wrong or contradict each other.**

---

## 1. What consumers actually get

Plugin installs from the `cure` marketplace deliver skills, `agents/`, `hooks/hooks.json` and `.lsp.json`. Output styles are uncertain (§5). Plugins can't deliver anything else, per the docs, verified 2026-10-24:

| Surface | Docs say | Effect today |
|---|---|---|
| `settings.json`, 35 deny rules | Plugin settings apply only `agent` and `subagentStatusLine`; other keys are dropped | Consumers get **no** deny rules. Only the npm postinstall copies the file, and only when the project has no settings.json yet (`install-plugin.js:38`) |
| `rules/*.md` (11) | Not a plugin component. Only `.claude/rules` and `~/.claude/rules` load | Rules arrive only through npm postinstall or cure-infra-bootstrap (`bootstrap/src/vendor/index.mjs:98-107`) |
| `personas/*.md` (4) | — | Nothing loads them. They are documentation only |
| Root `CLAUDE.md` | Not loaded from a plugin | `claude plugin validate --strict .` **fails** on it (it also wants a README install line) |

**Consequences:**
- `cure_guard.py` is the only safety layer consumers actually get. It doesn't cover force-push (`-f`), `reset --hard`, `git clean -f`, DROP/TRUNCATE, `terraform destroy` or `kubectl delete namespace`. A probe confirmed it lets `git push -f origin main` through.
- The bootstrap settings template pins `"model": "claude-opus-4-7"` (`bootstrap/templates/claude-settings.json.ejs:3`). Every bootstrapped project's session model gets downgraded, against the house rule.
- `setup.sh:170-187` writes `enabledPlugins` as an array. The schema requires an object, and the script crashes when it meets one.

## 2. Rules: one field breaks both runtimes

Seven rules (cicd, docker, go, python, rust, sql, terraform) use scalar `globs:`.
- **Claude Code** reads only `paths` and loads any rule without it unconditionally. In vendored consumers, about 264 lines of Go, Rust, Terraform and other standards sit in context every session, even in a Swift app.
- **The Antigravity exporter** parses only list items (`scripts/export-antigravity.py:217`). It writes `globs: ""`, so those rules never apply in agy (found 2026-10-23; agy validate warns about all seven).

Converting them to a `paths:` list and fixing the exporter fixes both runtimes.

The standards themselves are out of date:
- **ios:** no Swift 6, `@Observable` or Swift Testing.
- **web:** no Next 15/16 async APIs, Cache Components or Tailwind v4.
- **android:** routes should be `@Serializable`.
- **go:** says 1.22 but cites 1.23 iterators.
- **rust:** edition 2021.
- **terraform:** recommends `-target` in production and DynamoDB locking; it should use `use_lockfile`.
- **docker:** uses the end-of-life `node:20`.
- **python:** no uv.
- **sql:** prefers bigserial.

The repo also breaks its own `cicd.md` rule: there are no SHA pins and no `permissions:` block in `validate.yml`.

## 3. Hooks

| Finding | Evidence | Sev |
|---|---|---|
| Our PreCompact "context re-injection", the PostCompact echo and the SubagentStop checklist print to stdout. On those events stdout goes to the debug log, not to Claude, so all three do nothing. README:377 advertises the re-injection | `hooks/hooks.json:37-56,161-170` | High |
| The PostToolUseFailure prompt hook always returns `ok: true`, and the event can't block. Every failed Bash pays for a model call whose output nobody sees | `hooks.json:70-78` | Med |
| The Stop gate asks a tool-less model whether this is a /loop iteration. It never checks `stop_hook_active` or `session_crons`, so "never blocks twice" is prose only. It adds up to 30s to every turn in every consumer | `hooks.json:140-152` | Med |
| SessionStart provisioning writes `.claude/loop.md` and workflows into every git repo, including personal and OSS repos under a user-scope install | `hooks.json:32` | Med |
| Telemetry reads `CLAUDE_TOOL_NAME`, which doesn't exist, so `detail` is always "unknown" | `hooks.json:86` | Med |
| False positives: "swipe" matches "wipe", `src/secrets/` is blocked, and any `src/agents/` counts as the library | `cure_guard.py:32,39,58` | Low |
| The git-status SessionStart hook has no timeout (default 600s) and duplicates Claude Code's own gitStatus | `hooks.json:23` | Low |

The guard stays fail-open. The opt-in tri-lane sandbox guard is the one place `onFailure: "block"` fits. CI's hook gates check only `hooks/hooks.json`; they never check `tri-lane/hooks` or `mods/*`.

## 4. Agents

- **"Read-only" agents can write.** `memory: project` turns on Read, Write and Edit. This session's own agent list shows code-reviewer, accessibility-checker, brand-guardian, ux-researcher, contract-reviewer and legal-compliance with Write and Edit, although their frontmatter says `tools: Read, Grep, Glob` and CLAUDE.md calls them read-only. test-runner also gets Edit. Only skill-security-auditor, legal-analyst and tax-analyst are truly read-only.
- **`isolation: worktree` breaks two agents.** project-bootstrapper can't start a repo from scratch in a worktree. release-coordinator's version bump lands on a throwaway branch.
- **Reviewer overlap.** code-reviewer and pr-reviewer both claim PRs, and both collide with `/code-review`, codex-reviewer and cure-advisor.
- **Pins.** `cure-advisor` pins `effort: high` with no eval behind it. tax-analyst preloads 312 lines, against a cap of about 300.
- **What's fine:** description budget (about 2.1k tokens), no ignored subagent fields, and every preload name resolves.

## 5. Output styles, MCP, LSP

- **Output styles.** They use a nested layout (`<name>/output-style.md`) that isn't documented, and `plugin.json` has no `outputStyles` entry. Four have no frontmatter, and none set `keep-coding-instructions: true`, so selecting one drops the coding prompt. No skill or agent references them.
- **`.mcp.json.example`.** It suggests `mcp-firestore`, a third-party package of unclear provenance run with unpinned `npx -y` and a service-account key. Use the official `firebase-tools mcp` instead.
- **`.lsp.json`.** `npx` runs unpinned.
- **Marketplace text.** It claims "MCP + LSP servers", but no MCP server ships.

## 6. Skills

**Correctness:**
- **The SOW terms contradict each other** (re-checked by hand).

  | Term | proposal-generator | legal-doc-scaffold (owner-approved 2026-09-23) |
  |---|---|---|
  | Liability cap | total contract value (`:216`) | 12 months of fees (`:81`) |
  | Termination notice | 14 days (`:226`) | 30 days (`:82`) |
  | Payment | Net 15 (`:232`) | net-30, pause at 15 days (`:78`) |

- **engagement-automation:16 is wrong** that Codex and Antigravity have no scheduling. agy has `/schedule`, with conversation-scoped timers and cron, plus persistent sidecar Automations. Codex has app/web Automations and `codex cloud exec`.
- **Stale facts:**
  - gcr.io should be Artifact Registry (`infrastructure-scaffold/reference/details.md:201`).
  - "Vertex AI in Firebase" is now Firebase AI Logic (`security-review:116`).
  - The Node 20 decommission line in `firebase-architect:99` dates out on 2026-10-30.
  - design-system recommends Node 20.
  - release-management lacks the Play target-API and App Store SDK deadlines.

**Security:** seven business skills pre-approve unrestricted Bash plus WebSearch/WebFetch while they read third-party PDFs. Four of them have no untrusted-input clause: public-sector-contracting, bid-decision, capture-management and technical-estimation. That makes a prompt injection in a PDF a way to send data out. The tax and finance readers lack the clause too. feature-audit grants only `Read Grep Glob` but runs `git log`.

**Routing:**
- Seven descriptions start their trigger at chars 101–111, right where Codex truncates.
- Eight push the concrete trigger past char 150.
- Five open with a noun phrase instead of a verb.
- These pairs have no single owner:
  - database-architect and firebase-architect both claim Firestore modeling.
  - legal-research and irc-lookup both claim IRC cite checks.
  - infrastructure-scaffold and finops both claim budgets.
  - Three skills restate the Core Web Vitals thresholds.
  - A Stripe review can fire three skills.
- proposal-generator never points at technical-estimation.
- product-design, stitch-design and design-studio use shorthand names that don't resolve.

The review proposes 15 rewrites, all within 350 chars.

**Currency and depth:**
- 30 skills have no `metadata.verified`.
- The weakest skills are technical-blog-writer, the four finance skills (equity-research, merger-modeling, comps-analysis, dcf-modeling), market-research, go-to-market, project-manager, product-manager and sdlc. sdlc is the highest-traffic skill, and adds the least.
- Three skills are close to the 5,000-token re-attach limit with their output contract at the end.
- incident-response runs as `context: fork`, which doesn't suit a live back-and-forth.

**Portability:** all 106 skills carry `argument-hint` and `when_to_use`. Those keys are hard errors on claude.ai uploads and in the Skills API, and nothing exports a portable version.

**Evals:** 35 of 106 skills are covered, and there is no n≥3 Δ for any of them. High-risk skills have no evals at all: security-review, compliance-architect, qsbs-compliance, every tax skill, data-migration, the public-sector skills, the code generators, and engagement-automation.

## 7. Mods

All 15 `@cure` mods are enabled on the owner's machine. Their 172 tests pass, but none of them covers the failures below. No CI job runs them. They aren't in BACKLOG, STATE or the audit. Ten of them shipped together at 0.1.0 in PR #80 and never got IDEAS.md's "mutation pass + live run".

| Mod | Verdict | Top issue |
|---|---|---|
| agent-budget | **Rewrite**, disable now | Its "active" count is machine-global and never reset, so ghost agents fill the cap. Live: it denied a spawn at 2 real agents. It also rewrites research/audit agents to the retired `claude-3-5-sonnet` (`budget.ts:60`); 23 of 357 spawns were affected |
| cite-check | **Fix**, disable now | Resolves paths against the session cwd, so 72% of its flags are false (112/155). It rewrites the answer text and its array is unbounded |
| llm-ledger | **Drop** | Its "session" total is the machine's lifetime ($17,595). It uses Claude-3 prices (2.6× off) and `/ledger` collides with token-ledger |
| secret-scrub | Merge or drop | Duplicates secret-redactor, so output is redacted twice. Redacting Read output breaks a later Edit |
| ci-preview | Drop | Cuts the first character off file names, misses `git -C`, and estimates a flat 15 minutes |
| handoff | Drop | A 3-call git wrapper; a skill does it better |
| egress-guard, claim-guard | Merge into policy-guard | egress spawns git on every Bash call and matches by substring. claim-guard checks paths relative to the cwd and its host match is two-way |
| policy-guard | Keep, host all guard rules | Two git spawns per write. Its secret patterns are copied from secret-scrub |
| rules-band | Fix | Spawns git on every render and shows filler text for unknown repos. It's the third copy of the repo table |
| spend-band | Fix | `timeoutMs: 60000` is over the 30s `$.process.run` cap. It polls per session; it should poll once per machine |
| cache-band | Keep, small fix | Prices every model at the 3.5 Sonnet write rate |
| lane-board, lane-verifier | Keep, parallelize | Sequential git calls can blow the 10s hook limit. lane-verifier hooks `prompt.attachment` and `session.receive`, neither of which is documented |
| image-viewer | Keep | Its pixel cache is never pruned. It relies on the undocumented `prompt.edit` |

**Cross-cutting:**
- **The store is machine-global.** `$.store` is used as session state in four mods.
- **Unbounded arrays.** Several logs and lists grow without a cap.
- **Hot-path subprocesses.** About 7 `tool.call` handlers run on every Bash call.
- **No ask timeouts.** The guards' `$.ui.ask` can stall an unattended session or /loop.
- **Session cwd instead of target path** in six mods.
- **Retired model IDs and prices** are hardcoded. Use `$.session.usage().cost` instead.
- **No `userConfig`** anywhere.
- **Status lines that can't be dismissed.**
- **Install scripts** hide errors and hardcode the mod list.

## 8. cc-pr-tracker: clearing merged PRs

cc-pr-tracker comes from the owner's curated `vetted-mods` marketplace (`../vetted-mods/PINS.md`; upstream is MIT, sezaakgun/cc-pr-tracker).

**Root cause:**
- A done PR is dropped only when a new session starts (`register.tsx:303`).
- A hot reload restores it from `$.state` (`:295-298`).
- The poll timer refreshes every PR, done or not (`:272`).

**Design:**
- **`dropDone` setting** (userConfig `options`): "keep until stopped" (the default, today's behaviour), "after 10 minutes" or "immediately".
- **`doneAt` stamp:** recorded on a PR once its merge alert has fired. A swept PR is dropped from the list.
- **No polling done PRs.** Merged is final. A closed PR stays struck through until it is pasted again.
- **"Clear done (N)" button** on each done row. There is no header row, and adding one would cost a permanent line.
- **`/pr-clear` command.**
- **Tests:** 8 new ones, in the existing `hooks.test.ts` style.

**Path:** open an upstream PR, and if it's needed sooner, pin a local `0.3.1-cure.1` in vetted-mods. Don't fork it into the `cure` marketplace.

## 9. Runtime currency, since 2026-09-23

- **Claude Code** 2.1.310 is out; we're on 2.1.306. New since September:
  - `onFailure: "block"` on hooks.
  - The Agent tool takes `effort`.
  - Subagents preload at most 32 skills.
  - Opus 5.5 and Sonnet 5.5 default to `medium` effort, and a top-level `effortLevel` doesn't apply to Opus 5.5.
  - `/doctor prompt-audit`.
  - Public `plugin-evals` docs: git ≥2.31, `--max-cost-usd`, `--trust-plugin`.
  - Plugin auto-update is off by default for third-party marketplaces.
- **Codex:**
  - 0.164 is the latest; CI pins 0.155.
  - The default model is now GPT-6.1 Sol (500k context), so a 2% listing budget already reaches 10k tokens. Our "110-char truncation" rule is a 0.155 measurement and needs re-measuring.
  - The GPT-6 Astra authoring guidance: route from SKILL.md, keep descriptions short, define completion up front, and don't over-constrain.
  - A root `plugin.json` (the Agent Plugins schema) is now canonical.
  - Plugin hooks need trust, and since 0.164 that approval is tied to the plugin's contents.
- **Antigravity:**
  - agy auto-updated to 1.4.6.
  - Gemini 4 Argon has replaced Gemini 3.1 Pro (tri-lane still names 3.1 Pro).
  - Glob rules take a comma-separated `globs` string.
  - Hooks must sit at the plugin root.
  - `validate --strict --json` exists.
  - Only the agy CLI loads plugin rules; the App and IDE don't.

## 10. Docs that disagree with the repo

- **CLAUDE.md:** 103 skills, 39 agents (and its tables are missing 7 agents), "80 skills compete", "9 event types" (there are 33), and "MCP server configs" (none ship).
- **GEMINI.md:** says version 6.0.3 and gives the read-only `allowed-tools` advice.
- **AGENT-GUIDE, README, CONSUMING-PROJECTS:** 80 or 81 skills; 30, 39 or 40 agents.
- **MAINTENANCE.md:12** says nightly drift runs daily. Its cron was removed in 0752fc0 on 2026-08-09.
- **plugin-evals README:** says 40 cases / 32 skills (it's 43 / 35).

`sync-metadata.py --check` passes despite all of this, so its coverage is the bug.

---

Tickets: BACKLOG.md, Wave 7 (T71–T88). The 2026-10-22 runtime-audit follow-ups in STATE.md map to T79 (engagement-automation), T83 (doc reconciliation), T82 (CI and liveness) and T85 (evals).
