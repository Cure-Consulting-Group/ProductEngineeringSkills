# Tri-runtime platform facts — 2026-09-23

Evidence base for Wave 5. Each fact is **MEASURED** (probed on this machine), **DOCUMENTED** (source linked),
or **UNKNOWN**. Versions probed: Claude Code 2.1.280, codex-cli 0.155.0, agy 1.2.8, gemini 0.40.1.
Supersedes the Wave 2.5 "verified platform facts" and the 2026-09-09 C5 table where they disagree.
Re-probe on every minor release of any runtime — these move monthly.

## Claude Code 2.1.280 + Opus 5.5

| Fact | Status | Source |
|---|---|---|
| SKILL.md frontmatter now includes `model`, `effort`, `shell`, `arguments`, `background`, `metadata`, `license`, `compatibility` (last three from the Agent Skills spec) | DOCUMENTED | https://code.claude.com/docs/en/skills |
| Listing: `description`+`when_to_use` truncated at 1,536 chars; when `skillListingBudgetFraction` is exhausted, lowest-priority skills drop out of the listing silently (still `/`-invocable) | DOCUMENTED | same |
| `claude plugin eval` (2.1.269+): cases under `evals/` (configurable in plugin.json), 3 runs × with/without-plugin arms, `Δ` reported, graders `regex`/`tool_used`/`tool_order`/`file_exists`/`llm`/`baseline`, MCP mocks, CI gating via `--threshold`. **Default dir collides with our homegrown `evals/`** | DOCUMENTED | https://code.claude.com/docs/en/plugin-evals |
| Opus 5: remove explicit verification / "double-check" instructions (cause over-verification, no quality gain) | DOCUMENTED | https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5 |
| Opus 5: expands task scope on its own — constrain scope explicitly for narrow tasks | DOCUMENTED | same |
| Opus 5: delegates to subagents readily — state when delegation is warranted; caps via `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` / `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS` (2.1.217+) | DOCUMENTED | same |
| Opus 5: review prompts saying "only report high-severity" are followed literally and cut recall — ask for everything, filter in a separate pass | DOCUMENTED | same |
| Opus 5: `low`/`medium` effort give strong quality; re-run effort sweeps carried over from 4.x | DOCUMENTED | same |
| Opus 5: written deliverables run long — calibrate length explicitly | DOCUMENTED | same |
| Library trigger text: 32,320 chars (~8k tokens) for 103 skills + 9,278 chars for 40 agent descriptions per session | MEASURED | this repo |

## Codex CLI 0.155.0

| Fact | Status |
|---|---|
| Reads `name` + `description` only. `when_to_use`, `argument-hint`, `allowed-tools`, `disallowed-tools`, `context: fork` silently ignored | MEASURED |
| **`disable-model-invocation: true` ignored** — skill listed and fired implicitly. Codex equivalent: sidecar `agents/openai.yaml` → `policy.allow_implicit_invocation: false` (hidden from listing, `$name` still works) | MEASURED |
| Listing budget `skills.max_context_tokens` default 2% of context; **with our 103 skills every description is cut to ~110 chars** (mean 108). At 60k budget, full text | MEASURED |
| Domain nesting `skills/{domain}/{name}` discovered; plugin namespaces as `cure-product-engineering:<name>` | MEASURED |
| `` !`cmd` `` rendered literally, never executed; `$ARGUMENTS`/`$0` not substituted; `\$0.15` shows the backslash | MEASURED |
| Invalid-YAML frontmatter → skill silently dropped (`stitch-design`) | MEASURED |
| Our plugin is **not installed** on this machine (`codex plugin list` has no `cure` marketplace) | MEASURED |
| Plugin root `hooks/hooks.json` is auto-loaded without a manifest field (hash-trust gated). Ours assumes Claude env vars / prompt hooks — would misfire | DOCUMENTED + MEASURED (warp plugin); ours UNKNOWN |
| Default system prompt forbids spawning sub-agents unless user/AGENTS.md/skill asks | MEASURED |
| No per-skill tool restriction; enforcement only via `sandbox_mode`, permission profiles, custom agent TOML `sandbox_mode`, or PreToolUse deny hook | DOCUMENTED |
| GPT-5.6 guidance: outcome over steps; ALWAYS/NEVER/MUST only for true invariants; contradictory rules hurt more than missing detail; explicit stop rules + success criteria | DOCUMENTED https://developers.openai.com/api/docs/guides/prompt-guidance-gpt-5p6 |
| Zero-cost regression probe: `codex debug prompt-input` prints the exact model-visible prompt without a model call | MEASURED |

## Antigravity (agy 1.2.8) and Gemini CLI (0.40.1)

| Scope | agy 1.2.8 | gemini 0.40.1 (listing only) |
|---|---|---|
| `<ws>/.agents/skills/` | LOADED — **only with `--add-dir <ws>`** (headless `agy -p` has no workspace otherwise; the 09-09 "did not load" was a false negative) | LOADED (trusted folders only) |
| `<ws>/.agents/skills.json` entries (each scanned one level) | LOADED | NOT LOADED |
| `~/.gemini/config/skills/` | LOADED | NOT LOADED |
| `~/.gemini/skills/`, `~/.gemini/antigravity-cli/skills/` | Listed but **not in model prompt** | LOADED / not tested |
| `~/.agents/skills/` | NOT LOADED | LOADED |
| Nested `<scope>/<domain>/<name>/` | NOT LOADED anywhere | NOT LOADED |
| Installed flat plugin `plugin.json {"name":"cure"}` + `skills/<name>/` | LOADED (100/103 in prompt) | n/a |
| Our Claude manifest as-is (`skills` = array of domain dirs) | validates + installs, **0 skills load** | n/a |

Other agy facts (MEASURED): `when_to_use` ignored; **`disable-model-invocation` honored**; invalid YAML
(`stitch-design`) silently dropped; `` !`cmd` `` rendered literally; no truncation observed at 582 chars;
sibling `reference/` and `scripts/` reachable; `--mode plan --sandbox` still executed a shell command
(plan mode is not read-only); agy plugins can bundle `skills/`, `rules/` (24KB/file, 20k tokens total),
`hooks.json`, `mcp_config.json`, and custom agents with `skills:`/`rules:`/`tools`. Full listing ≈21k input tokens.

**Gemini CLI cannot run a model on this machine**: `IneligibleTierError … migrate to Antigravity`
(no API key / Vertex). Treat Gemini CLI as unsupported for this team unless a key is provisioned.

Gemini 3 guidance (DOCUMENTED): direct language, avoid emphatic/over-persuasive phrasing, context first
and instructions last, delimit with headings/XML.

## Cross-runtime rule that falls out of all three

**`description` is the only trigger field every runtime reads, and Codex shows only its first ~110 chars
at our library size.** 86/103 skills currently keep their "Use when…" text in `when_to_use`.
