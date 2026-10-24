# Tri-runtime platform facts — 2026-10-24

Evidence base for Wave 7 (T86). Each fact is **VERIFIED** (a command run on this machine on
2026-10-24, or a primary source quoted) or **UNVERIFIED** (claimed, not confirmed today).
Versions on this machine: Claude Code 2.1.306 (latest 2.1.310), codex-cli 0.163.0 (latest stable
0.164.0), agy 1.4.7 (auto-updated from 1.4.6 during the day). Supersedes
`docs/evaluations/2026-09-23/platform-facts.md` where they disagree. Raw probe output was kept in
the session scratchpad, not the repo; every probe below is reproducible from the command shown.

## Changed since 2026-09-23

| Topic | 2026-09-23 | 2026-10-24 | Status |
|---|---|---|---|
| Claude Code version | 2.1.280 | 2.1.310 latest, 2.1.306 here | VERIFIED |
| Codex version | 0.155.0 | 0.164.0 latest stable (2026-10-23), 0.163.0 here | VERIFIED |
| agy version | 1.2.8 / 1.2.9 | 1.4.7 here | VERIFIED |
| Codex default model | GPT-5.6 Sol | `gpt-6.1-sol`, 500k context (authenticated catalog) | VERIFIED |
| Codex description cut at default budget | ~110 chars (mean 108) on 0.155 | **Depends on the model's context window.** 500k (gpt-6.1-sol, signed in): full text. 272k (every other model, or the bundled catalog when signed out): 101-105 chars (mean 103.6) | VERIFIED |
| Codex listing budget for full text | ≥8000 tokens | ≥7,750 tokens for 104 cure + 1 tri-lane + 4 system skills | VERIFIED |
| `disable-model-invocation` in Codex | ignored; sidecar needed | still ignored; sidecar `agents/openai.yaml` hides 2/106 | VERIFIED |
| `disable-model-invocation` in agy | honored on 1.2.8, not re-measured on 1.2.9 | honored on 1.4.7: `model_invocable: false` for both | VERIFIED |
| Codex lane models | GPT-5.6 Luna / Sol / Terra, GPT-6 Astra | adds `gpt-6-luna`, `gpt-6-sol`, `gpt-6.1-sol`; 5.6 family labelled "older" | VERIFIED |
| agy models | Gemini 3.8 Flash, Gemini 3.1 Pro | Gemini 4 Argon (low/medium/high) and 3.8 Flash; **3.1 Pro no longer listed** | VERIFIED |
| agy rules | 9 model-decision `cure-style-*` rules seen | 20 rules exported, **7 glob rules have `globs: ""` and never apply** | VERIFIED |

## Claude Code (2.1.306 here; 2.1.310 latest)

| Fact | Status | Source |
|---|---|---|
| Latest is 2.1.310; this machine is on 2.1.306 | VERIFIED | `npm view @anthropic-ai/claude-code version` → `2.1.310`; `claude --version` → `2.1.306` |
| `onFailure: "block"` for command and HTTP hooks: a hook that can't start, times out, or exits unexpectedly blocks the action (2.1.295) | VERIFIED | CHANGELOG.md, 2.1.295: https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md |
| The Agent tool takes an `effort` parameter (2.1.292) | VERIFIED | CHANGELOG.md, 2.1.292 |
| Subagents preload at most 32 skills from `skills:`, each once; a subagent with the Skill tool can still invoke the rest (2.1.295) | VERIFIED | CHANGELOG.md, 2.1.295 |
| Opus 5.5, Sonnet 5.5 and Haiku 5.5 default to `medium` effort; every other effort-capable model defaults to `high` (Opus 4.7: `xhigh`) | VERIFIED | https://code.claude.com/docs/en/model-config ("Adjust effort level") |
| A top-level `effortLevel` in the **user** settings file does not apply to Opus 5.5. In project, local, managed or `--settings` files it applies to every model | VERIFIED | same page |
| `/doctor prompt-audit` (alias `/checkup prompt-audit`) audits CLAUDE.md, skills, agents and commands for prompting patterns written for older models (2.1.283) | VERIFIED | CHANGELOG.md, 2.1.283 |
| `claude plugin eval` needs git ≥2.31 when git is installed (2.1.283); `--max-cost-usd` sets a list-price cost ceiling (exit 2 = partial run); `--trust-plugin` skips the first-run trust prompt, recommended for CI | VERIFIED | https://code.claude.com/docs/en/plugin-evals |
| Background plugin auto-update is **off by default** for a third-party marketplace and `marketplace.json` has no field to turn it on. A user enables it under `/plugin` → Marketplaces, or an admin sets `"autoUpdate": true` on the `extraKnownMarketplaces` entry. Without it, users run `/plugin marketplace update cure` | VERIFIED | https://code.claude.com/docs/en/plugins/host-marketplace ("Turn on auto-update") |

The last row contradicts STATE.md line 7 ("auto-updates"); see Integrator requests in the T86 report.

## Codex CLI (0.163.0 here; 0.164.0 latest stable)

| Fact | Status | Source |
|---|---|---|
| 0.164.0 is the latest stable (2026-10-23); 0.165.0-alpha.1 exists | VERIFIED | `gh api repos/openai/codex/releases/latest` → `rust-v0.164.0 2026-10-23`; `npm view @openai/codex dist-tags` |
| Catalog: `gpt-6.1-sol` (priority 1, 500k context, default effort `low`, efforts low…max + ultra), `gpt-6-astra` (272k, default medium, low…ultra), `gpt-6-sol` (272k, medium, low…ultra), `gpt-6-luna` (272k, medium, low…max, **no ultra**), `gpt-5.6-sol`/`-terra`/`-luna` ("older") | VERIFIED | `codex debug models` (signed in) |
| The signed-out bundled catalog lists gpt-6.1-sol at **272k**, not 500k | VERIFIED | `CODEX_HOME=<copy without auth> codex debug models` |
| This machine's `~/.codex/config.toml` sets `model = "gpt-6.1-sol"`, `model_reasoning_effort = "high"`, `skills.max_context_tokens = 10000` | VERIFIED | read-only inspection |
| Listing default = 2% of the model's context window: the cut at the default equals `-c skills.max_context_tokens=5440` (2% of 272k) byte for byte, and `-c model_context_window=200000` gives the same listing as `max_context_tokens=4000` | VERIFIED | `codex debug prompt-input` sweep, see below |
| Docs: "this list uses at most 2% of the model's context window", explicit budget "up to 10,000 tokens" via `skills.max_context_tokens`, "8,000 characters when the context window is unknown" | VERIFIED | https://learn.chatgpt.com/docs/build-skills (redirect from developers.openai.com/codex/skills) |
| Codex shortens descriptions silently: a mid-word cut, no ellipsis, no warning in the prompt. Docs: "If many skills are installed, Codex shortens skill descriptions first"; skills may be omitted "and show a warning" | VERIFIED (behavior on 0.163); "since 0.156" UNVERIFIED (release notes on GitHub only reach 0.158) | prompt-input; same docs page |
| `skill_search` is `stable`, enabled by default; disabling it leaves the listing byte-identical (only message ids and timestamps differ). Its tool surface isn't visible in prompt-input | VERIFIED (flag and no listing effect); tool effect UNVERIFIED | `codex features list`; `codex debug prompt-input --disable skill_search` |
| `disable-model-invocation` still ignored; the generated sidecar `agents/openai.yaml` (`policy.allow_implicit_invocation: false`) hides `legal-doc-scaffold` and `proposal-generator`, so 104/106 are listed | VERIFIED | prompt-input on the installed 7.13.0 plugin |
| A root `plugin.json` with an Agent Plugins `$schema` is recognized. The 0.163 binary contains "root `plugin.json` is not an Agent Plugins manifest; expected `$schema`" and probes `.codex-plugin/plugin.json`, `.claude-plugin/plugin.json`, `.cursor-plugin/plugin.json` | VERIFIED (recognized) | `strings` on the 0.163.0 binary |
| Root `plugin.json` is now **canonical**, with `.codex-plugin` as fallback | UNVERIFIED | no primary doc found; https://learn.chatgpt.com/docs/plugins doesn't say |
| Plugin hooks need review and trust before they run | VERIFIED | https://learn.chatgpt.com/docs/plugins ("Review and trust plugin hooks before they run") |
| From 0.164 that hook approval is tied to the plugin's contents | VERIFIED | 0.164.0 release notes, #54619 "Bind plugin hook approval to plugin contents" |
| GPT-6 Astra authoring guidance: "make the root document a minimal router that points to supporting docs and scripts"; "skill descriptions should be as short as possible while making it clear when the model should use them"; "define completion before starting"; "overly specific guidance can now hinder results"; a mandated stop-for-review "will pull the model toward an earlier stopping point" | VERIFIED | https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra |

### Codex listing measurement (zero model calls)

Method: `codex debug prompt-input` in an empty temp dir. "Default" used a throwaway `CODEX_HOME`
copied from `~/.codex` (plugins, marketplaces, model cache) with the `[skills]` table removed and no
`auth.json`. The machine's own `~/.codex` was only read. Sample: 104 cure-product-engineering skills,
1 cure-tri-lane skill and 4 system skills. Source descriptions: mean 183.6 chars, max 334.

| Budget (tokens) | How it's reached | Cure descriptions shortened | Listed length min / mean / max |
|---|---|---|---|
| 4,000 | `model_context_window=200000` | 105/105 | 49 / 50.7 / 53 |
| 5,440 | **default on any 272k model** (gpt-6-luna, gpt-6-sol, gpt-6-astra, gpt-5.6-*, or gpt-6.1-sol signed out) | 105/105 | **101 / 103.6 / 105** |
| 6,000 | explicit | 105/105 | 123 / 124.3 / 127 |
| 7,000 | explicit | 99/105 | 152 / 161.2 / 163 |
| 7,500 | explicit | 31/105 | — |
| 7,750 | explicit | 0/105 | full text |
| 10,000 | **default on gpt-6.1-sol signed in** (`model_context_window=500000`), and this machine's explicit setting | 0/105 | full text (152 / 183.6 / 334) |

At the 272k default, 82/104 cure descriptions still contain "Use when/for" and only 63 keep two or
more words after it. In source, 7/106 skills start "Use when" after char 100 (max 111; median 82).
**The per-skill cap is about 103 chars, not 110, and only on 272k-context models.** On the default
gpt-6.1-sol model, signed in, the 2% default already reaches the 10k cap and nothing is cut.

`scripts/codex-smoke.py` runs signed out, so it sees the bundled 272k catalog and the 103-char cut
even where a signed-in session would not. Its listing assertions don't depend on the cut.

## Antigravity (agy 1.4.7)

| Fact | Status | Source |
|---|---|---|
| Installed 1.4.7; the changelog's top entries are 1.4.7 and 1.4.6 | VERIFIED | `agy --version`; `agy changelog` |
| Models: `gemini-4-argon-{low,medium,high}`, `gemini-3.8-flash-{low,medium,high}`, `claude-opus-5-5-{low,medium,high}`, `claude-sonnet-5-5-{low,medium,high}`, `gpt-oss-120b-medium`. **No Gemini 3.1 Pro** | VERIFIED | `agy models` |
| `--effort` accepts low, medium, high, xhigh, max | VERIFIED | `agy --help` |
| `agy plugin list --json`: `cure` 7.13.0 enabled at `~/.gemini/config/plugins/cure`, 106 skills, 4 agents, 20 rules | VERIFIED | command output |
| `agy plugin validate --json` on the installed plugin: 0 errors, **7 warnings** "a glob rule needs globs, or it never applies" (cicd, docker, go, python, rust, sql, terraform; each has `globs: ""`). `--strict` exits 1 ("7 warnings"). android, firebase, ios and web carry comma-separated globs (e.g. `"**/*.kt,**/*.java"`) | VERIFIED | command output; rule frontmatter |
| `validate --strict --json` exists | VERIFIED | `agy plugin --help` |
| Validator reports `"hooks": 0` and `"agentPluginsSpec": false` for our export | VERIFIED | same output |
| `disable-model-invocation` honored: `/skills` (zero turns, 0 tokens) returns `model_invocable: false` for `cure:legal-doc-scaffold` and `cure:proposal-generator` only; 106 cure skills listed | VERIFIED | `agy -p "/skills" --add-dir <ws> --mode plan --sandbox --output-format json` |
| `/agents` lists the 4 personas, zero turns | VERIFIED | `agy -p "/agents" …` |
| Gemini 4 Argon visibility fix for `GEMINI_API_KEY` users (1.4.3) | VERIFIED | `agy changelog` |
| Hooks belong at the plugin root (`hooks.json`); glob rules take a comma-separated `globs` string; only the agy CLI loads plugin rules (not the App or IDE) | UNVERIFIED (from the 2026-10-22 facts review; the changelog confirms `hooks.json` validation, not location or App/IDE scope) | — |
| Persona `skills:` scoping | **UNMEASURED** | see note |
| Glob-rule firing | **UNMEASURED** | see note |

Note on the two unmeasured rows: two cheap model prompts (`gemini-3.8-flash-low`, low effort) were
spent and neither settled the question. (1) With `--agent cure-product-lead`, asked to count `cure:`
skills: `COUNT=0` (16,946 input tokens). (2) With no agent, asked to read `Example.kt` and `main.go`
and name the attached rules: `COUNT=0`, `RULES=NONE` for both (28,651 input + 32,609 cached tokens).
The model can't see the `cure:` prefix it was asked about, and the probe workspace was in the
session scratchpad, outside `trustedWorkspaces`, so it proves nothing about scoping or globs. A
third prompt was spent by mistake: `/rules` isn't a slash command in 1.4.7, so it went to the
default model (1 turn, 25,603 tokens, no result kept).

To re-measure, run from a trusted path (any directory under `~/Documents/Cure-Consulting-Group`)
and check a fact the model can't guess. For scoping, ask it to quote one sentence from a skill
outside the persona's `skills:` list. For globs, put a unique sentinel line in a glob rule of a
throwaway workspace plugin and ask the model to repeat it after reading a matching file.

## Tri-lane model catalog (2026-10-24)

One run per proposed default (`lane-eval.py run --no-retry`, n=1). Defaults moved only where the
canary passed. Results are in `.git/tri-lane/evals.jsonl` of the main checkout.

| Rule (models.json) | Before | After | Canary, 2026-10-24 |
|---|---|---|---|
| impl-strings-docs, impl-routine, impl-design-left-to-lane | `gpt-5.6-luna` | `gpt-6-luna` | `impl-spec-service` @ medium: PASS 9/9, 32 s |
| review-default | `gpt-5.6-luna` | unchanged (`gpt-6-luna` listed as a pending alternative) | `review-planted-bugs` @ medium: FAIL 0.863, recall 0.727 (3 of 11 missed), precision 1.0 |
| impl-risk, impl-wide, escalation attempt 2 and 3 | `gpt-5.6-sol` | `gpt-6.1-sol` | `authz-tenant-isolation` @ high: PASS 8/8, 60 s |
| review-crossfile-money | `gpt-5.6-sol` | `gpt-6.1-sol` | `review-planted-bugs` @ high: PASS, recall 1.0, precision 1.0, 203 s |
| impl-underspecified | `gpt-5.6-sol` | unchanged (pending spec-gap canary for `gpt-6.1-sol`) | not run |
| whole-repo | `gemini-3.1-pro-high` (retired) | `gemini-4-argon-high` | `whole-repo-read` @ high: PASS 1.0, 363 s |
| system-review, triage | `gemini-3.8-flash-high` / `-low` | unchanged (still offered) | not needed |
| impl-terminal-sre-migration (shadow) | `gpt-6-astra` | unchanged (still offered) | not run |

## Cross-runtime rule that falls out of all three

`description` is still the only trigger field every runtime reads. Codex shows all of it on the
default gpt-6.1-sol model when signed in. It shows about the first **100 chars** on any 272k-context
model at the default budget, signed out (CI), or with a budget below ~7,750 tokens. Start
"Use when…" by char 85 so at least two trigger words survive the ~103-char cut, keep descriptions
short (the Astra guidance), and keep `skills.max_context_tokens = 10000` in the machine config.
Today 8/106 skills start "Use when" after char 100, 39 after char 90, 57 after char 80.
