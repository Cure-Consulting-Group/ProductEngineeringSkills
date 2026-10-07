# Comprehensive Engineering Scope & Architecture: Cure Mods Suite

This specification defines the architecture, contracts, security models, failure modes, and verification plans for the ten new Claude Code mods and one mod enhancement in the Cure Consulting Group portfolio.

---

## 1. Portfolio Context & Design Principles

All Cure mods must adhere to the standard established in the v0.2.0 release:
1. **Unsandboxed Execution with Bounded Blast Radius**: Mods run with user privileges. They must never perform unauthenticated network calls, write arbitrary files outside explicit scoped directories (`~/.claude/` or `.claude/`), or invoke shell commands without explicit path sanitization.
2. **Fail-Closed on Policy, Fail-Open on Plumbing**: If a policy violation occurs, refuse or block unless explicitly overridden by an interactive human operator. If internal telemetry, formatting, or directory inspection fails, do not crash the session; report diagnostic warnings and allow work to continue.
3. **Pure Arithmetic & Logic Separation**: Separate core regex parsing, token calculations, and state machines into pure testable modules (`scrub.ts`, `ledger.ts`, `cite.ts`, `claims.ts`, `preview.ts`, `budget.ts`, `egress.ts`, `rules.ts`, `handoff.ts`, `lanes.ts`) isolated from Claude Code runtime side-effects.
4. **Full Test Matrix with Mutation Sensitivity**: Every mod requires 100% pure function unit coverage, simulated end-to-end hook coverage via `claude-code/testing`, and verified mutation coverage where deliberate logic inversions fail the suite.
5. **Standard Manifest & Marketplace Integration**: Each mod is encapsulated under `mods/<name>` with `.claude-plugin/plugin.json`, `hooks/hooks.json`, `tsconfig.json`, and an entry in `.claude-plugin/marketplace.json`.

---

## 2. Detailed Technical Scope by Mod

---

### Mod 1: `cure-secret-scrub` (Secret Redaction on Tool Outputs)

#### Problem Statement
During multi-repo exploration sessions, agents routinely run `Read`, `Grep`, and `Bash` commands across sensitive directories. While `cure-policy-guard` blocks writes of hardcoded secrets, it does not prevent reading existing secrets (e.g., legacy `.env` files, inadvertently unencrypted service account keys, or token dumps), causing sensitive credentials to leak into LLM context windows and vendor logs.

#### Architecture & Hooks
- **Hook**: `tool.call` intercepting `Read`, `Grep`, and `Bash`.
- **Flow**:
  1. Let the tool execute via `const r = await next(e)`.
  2. Inspect output fields: `r.result`, `r.text`, `r.stdout`, `r.stderr`.
  3. Scan strings against high-entropy and structured credential regexes.
  4. Replace identified secrets with placeholder tokens `[REDACTED:<TYPE>]` (e.g. `[REDACTED:GOOGLE_API_KEY]`, `[REDACTED:PRIVATE_KEY]`, `[REDACTED:GITHUB_PAT]`).
  5. If redactions occur, increment session redaction count in plugin state and emit an unobtrusive toast/notification (`$.ui.notify({ message: "cure-secret-scrub: Redacted N credentials from tool output", level: "warning" })`).
- **Command**: `/secret-scrub` displays session redaction count and types of credentials scrubbed.

#### Regex Patterns Covered
- Google API keys: `AIza[0-9A-Za-z-_]{35}`
- GitHub Personal Access Tokens & OAuth: `gh[pousr]_[0-9A-Za-z]{36,}`
- Anthropic API keys: `sk-ant-[a-zA-Z0-9_\-]{40,}`
- OpenAI API keys: `sk-[a-zA-Z0-9]{48,}`
- Stripe secret & live keys: `sk_live_[0-9a-zA-Z]{24,}`, `rk_live_[0-9a-zA-Z]{24,}`
- AWS Access Key IDs: `AKIA[0-9A-Z]{16}`
- PEM Private Key Headers: `-----BEGIN (RSA|EC|DSA|OPENSSH|PGP|PRIVATE) KEY-----[\s\S]*?-----END \1 KEY-----`
- GCP Service Account JSON: `"type":\s*"service_account"[\s\S]*?"private_key":\s*"-----BEGIN PRIVATE KEY-----`

#### Failure Modes & Edge Cases
- **Binary/Garbage output**: Gracefully handles non-string or buffer outputs without crashing.
- **Large output payloads (>1MB)**: Streaming regex or chunked scanning to prevent thread stalling.
- **Benign strings resembling keys**: Preserves dummy keys in test fixtures (`AIzaSyTest...`) if explicitly inside `test/` or `fixture` paths.

#### Mutation Cases
- Removing the private key regex -> fails PEM test.
- Inverting redaction replacement -> leaves raw token in `r.result`, fails integrity check.
- Failing to notify UI -> fails notification dispatch test.

---

### Mod 2: `cure-llm-ledger` (Per-Turn Cost & Attribution Ledger)

#### Problem Statement
Claude Code represents the highest single concentration of Anthropic LLM spend across the Cure portfolio. No native attribution links cost to repository, branch, or subagent tasks, leaving cloud billing reconciliations disconnected from development activity.

#### Architecture & Hooks
- **Hooks**:
  - `turn.step`: Captures usage metrics per step (`input_tokens`, `cache_creation_input_tokens`, `cache_read_input_tokens`, `output_tokens`, `model`).
  - `session.start` / `session.end`: Initializes session tracking and writes roll-up stats.
- **Data Flow**:
  1. Intercept model responses or turn stats.
  2. Map model identifier to pricing table:
     - `claude-3-opus`: $15.00 / $75.00 per MTok (Input / Output); Cache write: $18.75; Cache read: $1.50
     - `claude-3-5-sonnet`: $3.00 / $15.00 per MTok; Cache write: $3.75; Cache read: $0.30
     - `claude-3-5-haiku`: $0.80 / $4.00 per MTok; Cache write: $1.00; Cache read: $0.08
  3. Query repository name and current git branch (`git rev-parse --abbrev-ref HEAD`).
  4. Write atomic JSONL record to `~/.claude/llm-ledger.jsonl` (or path configured in `CURE_LEDGER_PATH`).
- **Command**: `/ledger` renders session breakdown:
  - Total tokens (Input, Cache Read, Cache Write, Output).
  - Total session cost ($).
  - Cost per model.

#### Security & Privacy
- Record strictly numerical metrics, model, repo, branch, session ID, and ISO timestamp.
- **NEVER** write prompt contents, completion text, or tool parameters.

#### Failure Modes
- Git unavailable or outside repo -> defaults `repo` to `"unknown"` and `branch` to `"none"`.
- Ledger directory unwritable -> fails open, emits single warning, logs to memory state.

#### Mutation Cases
- Changing token pricing multiplier -> fails ledger cost accuracy test.
- Swapping cache read vs cache write calculations -> fails billing test.

---

### Mod 3: `cure-cite-check` (Real-Time File Citation Validator)

#### Problem Statement
LLMs frequently hallucinate or assert stale code locations (`path/to/file.ext:425`) when referring to historical files or refactored functions. In automated lanes and advisory sessions, stale citations mislead reviewers and violate Cure's *verify before asserting architecture* doctrine.

#### Architecture & Hooks
- **Hook**: `turn.complete` (and assistant message delivery).
- **Flow**:
  1. Scan assistant output text for file citation patterns:
     - `[file.ext:123]`
     - `` `path/to/file.ext:123` ``
     - `path/to/file.ext:123-145`
     - Markdown links `[...](path/to/file.ext#L123)`
  2. For each extracted citation:
     - Check file existence via `$.fs.exists()`.
     - Count total lines in the file.
     - Validate that cited line number $\le$ file total line count.
     - If quote snippet is extracted, check whether matching string exists within $\pm 20$ lines of the target line.
  3. Aggregate results into: Valid citations, Missing files, Stale line numbers.
  4. If any stale citations are detected:
     - Append a prominent warning note to the turn output:
       `[CURE-CITE-CHECK: 1 of 4 citations stale — src/service.ts:512 exceeds line count (340)]`
- **Command**: `/cite-check` displays history of validated vs stale citations in the session.

#### Failure Modes
- Non-code text with colons (`12:00 PM`, `v1.2.3: release`) -> regex ignores non-path prefixes.
- External URLs with `#L` -> excluded from local checks.

---

### Mod 4: `cure-claim-guard` (DistrictZero Multi-Machine Claim Protection)

#### Problem Statement
In the DistrictZero architecture, development is divided across multiple physical nodes (MacBook Pro vs Mac mini). `CLAUDE.md` specifies that machines must never overwrite rows or files owned by the other machine. Agents without runtime enforcement regularly breach this boundary when operating in batch.

#### Architecture & Hooks
- **Hook**: `tool.call` for `Write`, `Edit`, `MultiEdit`, `NotebookEdit`.
- **Target Patterns**:
  - `scripts/build-<st>-*`
  - `scripts/lib/<st>-*`
  - `scripts/data/<st>*`
  - Any path explicitly mapped in `.agents/state-targets.md`.
- **Flow**:
  1. Detect target file path in write operation.
  2. Check if `.agents/state-targets.md` exists in current project root.
  3. Query current host identity via `scutil --get LocalHostName` or `hostname` (fallback `CURE_MACHINE_NAME`).
  4. Parse table in `.agents/state-targets.md` matching state `<st>` or path prefix.
  5. If target is claimed by another machine:
     - Refuse tool call: `"Blocked by cure-claim-guard: Path claimed by [Machine B] in .agents/state-targets.md"`.
     - In interactive sessions, provide prompt: `Refuse / Override (logged)`.
- **Command**: `/claims` displays current machine name and parsed state claims.

---

### Mod 5: `cure-ci-preview` (Pre-Push GitHub Actions Cost Estimator)

#### Problem Statement
Engineers push commits and create PRs without knowing whether expensive matrix builds (macOS runners at 2x rate, full e2e test suites) will trigger. Accidentally mixing `.agents/` documentation with code forfeits docs-only CI skipping rules.

#### Architecture & Hooks
- **Hook**: `tool.call` on `Bash` matching `git push` or `gh pr create`.
- **Flow**:
  1. Intercept command.
  2. Execute `git diff --name-only origin/HEAD...HEAD` (or `git status --porcelain`).
  3. Analyze changed path patterns against repository workflow rules:
     - Documentation only (`*.md`, `docs/`, `design/`) -> Expected: Skip / Quick Lint ($0.00).
     - Mixed (`.agents/` + `*.ts`) -> Emits warning: "Warning: Committing docs with code breaks CI docs-skip optimization".
     - Mobile iOS (`ios/`, `*.swift`, `Podfile`) -> Triggers macOS runner ($0.016/min $\times 15$ min $\approx$ $0.24).
     - Full backend matrix -> Linux runner ($0.008/min $\times 20$ min $\approx$ $0.16).
  4. Compute projected runner cost ($ USD) and duration.
  5. Display toast/prompt previewing jobs and cost before command proceeds.
- **Command**: `/ci-preview` previews the CI impact of pending unpushed commits.

---

### Mod 6: `cure-agent-budget` (Subagent Concurrency & Cost Optimizer)

#### Problem Statement
Complex autonomous operations spawn arbitrary nested subagents, resulting in exponential token costs and runaway concurrent executions. Many subagents perform read-only research tasks using maximum-tier models (Claude Opus) when lighter models (Sonnet or Haiku) would suffice.

#### Architecture & Hooks
- **Hook**: `agent.spawn` (or subagent launch events).
- **Flow**:
  1. Track active concurrent subagents in plugin session state.
  2. Enforce hard cap (default: 4 concurrent, configurable via `CURE_MAX_SUBAGENTS`).
  3. Inspect subagent role and prompt:
     - If role is `research`, `lookup`, `explorer`, `audit`, or prompt indicates read-only file reading:
     - Check if model was explicitly forced to Opus. If not specified or generic, rewrite model to `claude-3-5-sonnet` (or Haiku).
  4. Track cumulative spawned count and token attribution.
- **Command**: `/agents-budget` displays active subagent count, spawn limit, and cumulative savings.

---

### Mod 7: `cure-egress-guard` (Runtime Outbound AI-Vendor Guard)

#### Problem Statement
Sensitive repositories (Level5 dealing with HIPAA/PHI data, or minors' repositories like Initiated Recruiting, SPEDTECH, LearnLift) strictly prohibit transmitting raw data to consumer AI APIs or unapproved vendors. While code reviews check static imports, ad-hoc `Bash` commands (`curl -X POST api.openai.com...`, `fetch()`) can exfiltrate data at runtime.

#### Architecture & Hooks
- **Hook**: `tool.call` for `Bash` and `WebFetch`.
- **Target Repositories**: Repositories containing `BAA_INVENTORY.md`, `rules/phi-protection.md`, or named in minors' repo list.
- **Flow**:
  1. Intercept bash commands and web requests.
  2. Scan URLs and hostnames against prohibited endpoints:
     - `api.openai.com`
     - `generativelanguage.googleapis.com` (consumer Gemini)
     - `api.anthropic.com` (direct raw curl)
     - Unapproved model aggregators
  3. Scan command arguments for data pipe exfiltration (`cat patient_record.json | curl ...`).
  4. If detected, block command with high-priority security rejection:
     `[CURE-EGRESS-GUARD: Blocked outbound call to unauthorized AI endpoint in PHI/minors repo]`.
- **Command**: `/egress-guard` lists protected repos and egress rules.

---

### Mod 8: `cure-lane-board` (Multi-Lane Tri-Lane Status HUD)

#### Problem Statement
The `tri-lane` orchestrator runs concurrent tasks across Codex implementation worktrees, Antigravity review branches, and Claude architect lanes. Today, engineers must manually run git commands and inspect logs to determine which worktrees are active, clean, or past their defect window.

#### Architecture & Hooks
- **Hook**: `session.start`, `command.run` for `lanes`, `ui.render` for `Pane`.
- **Flow**:
  1. Scan repository for worktrees (`git worktree list`) and branches matching `lane/*`.
  2. For each lane:
     - Read commits ahead/behind `origin/HEAD`.
     - Read porcelain dirty status.
     - Inspect tri-lane run log (`~/.cure/lane-log.jsonl` or `.claude/tri-lane.json`).
     - Check escaped-defect window countdown (hours remaining).
  3. Render structured visual pane with terminal table:
     - Lane Name | Branch | Commits Ahead | Worktree Status | Defect Window
  4. Provide button/command to trigger `lane-log.py update` for completed runs.
- **Command**: `/lanes` toggles or renders the Tri-Lane Dashboard.

---

### Mod 9: `cure-rules-band` (Repository House Rules HUD Banner)

#### Problem Statement
Each repository in the Cure portfolio has unique architectural and legal boundaries (e.g. "Vertex only", "No Cron", "Clean Architecture MVI", "Hash-pinned public claims"). Engineers and models switch contexts between repos frequently and miss critical constraints.

#### Architecture & Hooks
- **Hook**: `ui.render` for `AbovePrompt`.
- **Flow**:
  1. Locate `.cure/rules.json` (or `.claude/rules.json`) in the current workspace.
  2. If missing, auto-detect profile from repository structure (e.g. Level5 -> PHI/Vertex; Android -> Compose/MVI; Next.js -> App Router).
  3. Format a single-line compact, high-contrast banner displayed above the prompt:
     `rules ● Level5 [PHI · Vertex AI Only] · No Cron · 8pt Grid`
  4. Invalidate and re-render if active repository changes.
- **Command**: `/rules` lists detailed rules and documentation references for the current repository.

---

### Mod 10: `cure-handoff` (Autonomous Session Handoff & STATE Generator)

#### Problem Statement
At the end of engineering sessions, updating `STATE.md` with accomplishments, open defects, commits, and handoff notes is performed manually. Human fatigue often leads to incomplete handoffs and loss of continuity across sessions.

#### Architecture & Hooks
- **Hook**: `command.run` on `handoff`.
- **Flow**:
  1. Intercept `/handoff` invocation.
  2. Inspect git activity during current session:
     - `git log --since="today" --oneline`
     - Current uncommitted diffs (`git status --short`)
     - Passing test runs logged in session messages.
  3. Aggregate open warnings or unresolved policy overrides.
  4. Format a standardized `STATE.md` markdown entry:
     - Date & Session ID
     - Shipped Commits & PRs
     - Verified Checks & Test Coverage
     - Open Decisions / Next Steps
  5. Display draft in interactive editor/modal for user review before writing.

---

### Mod Enhancement: `cure-policy-guard` (Actionlint & Status Check Verification)

#### Enhancements
1. **Actionlint on Workflow Write**: When `tool.call` writes or edits `.github/workflows/*.yml`:
   - Run `actionlint` locally if binary exists.
   - If syntax or actionlint errors are found, include them in the prompt warning before the file is written.
2. **Missing Required Status Check Warning**:
   - Check if repository branch protection requires validation checks (preventing unvalidated merges like DistrictZero's build gap).

---

## 3. Work Breakdown & Implementation Schedule

| Phase | Mod / Task | Est. Effort | Deliverables |
|---|---|---|---|
| **Phase 1** | `cure-secret-scrub` | 5h | Pure scrubber, tool wrapper hook, test suite (15+ tests), marketplace entry |
| **Phase 2** | `cure-llm-ledger` | 8h | Pure ledger engine, pricing tables, JSONL writer, `/ledger` command, tests |
| **Phase 3** | `cure-cite-check` | 6h | Pure citation parser, line counter, snippet validator, hook, tests |
| **Phase 4** | `cure-claim-guard` | 5h | Table parser, machine detector, write blocker, `/claims` command, tests |
| **Phase 5** | `cure-ci-preview` | 6h | Path classifier, runner cost model, bash wrapper hook, `/ci-preview`, tests |
| **Phase 6** | `cure-agent-budget` | 4h | Subagent counter, model router, spawn hook, `/agents-budget`, tests |
| **Phase 7** | `cure-egress-guard` | 5h | Egress detector, network/pipe validator, tool blocker, `/egress-guard`, tests |
| **Phase 8** | `cure-rules-band` | 3h | Rules loader, `AbovePrompt` UI component, `/rules` command, tests |
| **Phase 9** | `cure-handoff` | 4h | Git activity scanner, STATE formatter, `/handoff` command, tests |
| **Phase 10** | `cure-lane-board` | 8h | Worktree scanner, status evaluator, `Pane` UI component, `/lanes`, tests |
| **Phase 11** | `cure-policy-guard` upgrade | 3h | Actionlint integration, required check verification, tests update |
| **Phase 12** | Distribution & CI Integration | 3h | Sync `.claude-plugin/marketplace.json`, update `mods/README.md`, full CI audit |

---

## 4. Quality Gate Criteria

Before merging each mod:
1. `claude plugin test mods/<name>` passes with 0 failures.
2. `claude plugin validate mods/<name>` passes cleanly.
3. Every test suite contains both pure unit tests and mocked end-to-end hook executions.
4. Mutation testing pass: at least 3 deliberate inversions caught per mod.
5. All JSON manifests conform strictly to Claude Code plugin schema.
6. Local validation suite (`audit-library.py`, `check-doc-claims.py`, `sync-metadata.py`) remains 100% green.
