# Product Engineering Skills

The complete skill library that Cure Consulting Group uses to build apps, platforms, and products. These skills encode our standards, frameworks, and processes — so every project ships with the same level of rigor.

It is a **Claude Code plugin** (`cure-product-engineering` in the private `cure` marketplace) and also installs into **Codex** and **Antigravity** (see `STATE.md`).

## How It's Organized

```
ProductEngineeringSkills/
├── .claude-plugin/           # plugin.json (version source of truth) + marketplace.json (the `cure` marketplace)
├── skills/{domain}/{name}/   # 106 skills, organized by domain (engineering, platform, product, business, finance, marketing, security, legal, tax)
├── agents/                   # 41 custom agents (subagents); effective tools in .claude/CLAUDE.md
├── personas/                 # 4 engagement archetypes — documentation, nothing loads them
├── hooks/                    # hooks.json + cure_guard.py (command hooks only; see Hooks below)
├── rules/                    # 11 path-specific coding standards (`paths:` frontmatter)
├── tri-lane/                 # cure-tri-lane plugin (Claude + Codex + Antigravity lanes)
├── mods/                     # Claude Code mods (in-process TypeScript hooks) in the cure marketplace
├── plugin-evals/             # `claude plugin eval` cases and the n≥3 Δ sweep
├── bootstrap/                # cure-infra-bootstrap CLI (writes CLAUDE.md, .claude/, rules, settings)
├── claude-commands/          # Legacy command format (npm/vendored path only)
├── .lsp.json                 # LSP servers (TypeScript, Pyright), pinned
├── .mcp.json.example         # Opt-in MCP template (needs per-project secrets); not auto-loaded
├── settings.json             # Default deny rules — copied by npm/bootstrap; a plugin can't ship permissions
├── .claude/CLAUDE.md         # Instructions for developing this repo
├── GEMINI.md, AGENT-GUIDE.md # Other-runtime instructions; prompt-structuring guide
└── docs/OVERVIEW.md          # Generated inventory of every skill, agent, rule, hook (source of truth for lists)
```

## Installation

### What each install path delivers

A plugin can deliver skills, agents, hooks and LSP config. It **cannot** deliver permissions (plugin `settings.json` applies only `agent` and `subagentStatusLine`), path rules, or personas. Those arrive only through the npm postinstall or cure-infra-bootstrap. Details: [docs/CONSUMING-PROJECTS.md](docs/CONSUMING-PROJECTS.md).

### Claude Code: marketplace (recommended)

```
/plugin marketplace add Cure-Consulting-Group/ProductEngineeringSkills
/plugin install cure-product-engineering@cure
```

Or in one step on Claude Code 2.1.275 or later:

```
/plugin install cure-product-engineering --marketplace Cure-Consulting-Group/ProductEngineeringSkills
```

**Updates:** Claude Code turns auto-update **off** by default for third-party marketplaces such as `cure`. Turn it on per machine in `/plugin` → Marketplaces, or run `claude plugin update cure-product-engineering@cure`.

Skills are namespaced: `/cure-product-engineering:sdlc`, `/cure-product-engineering:security-review`, …

### npm package (adds settings and rules)

```bash
# one-time: a PAT with read:packages
npm login --scope=@cure-consulting-group --registry=https://npm.pkg.github.com
npm install @cure-consulting-group/product-engineering-skills
```

The postinstall links the plugin, registers it, copies the path rules into `.claude/rules/`, and merges the deny rules into the project's `.claude/settings.json` (existing settings are kept; nothing is overwritten). Dependabot can track the package for updates.

### cure-infra-bootstrap (manifest-driven project setup)

`/cure-product-engineering:cure-infra-bootstrap`, or the `claude-bootstrap` CLI (`init`, `apply`, `doctor`, `inventory`). It writes CLAUDE.md, `.claude/settings.json` (deny rules, no model pin), rules and opt-in compliance packs.

### Setup script

```bash
/path/to/ProductEngineeringSkills/setup.sh [project-dir]   # or --global
```

Registers the `cure` marketplace, enables the plugin (as an object-shaped `enabledPlugins` entry), installs the rules that match the project type, and creates a project CLAUDE.md.

### Codex and Antigravity

Run `scripts/install-runtimes.sh` on each machine after checkout and after every release. It installs the Codex plugin and exports the Antigravity plugin, then verifies the real installs with zero model calls. See `STATE.md`.

## Inventory

The generated **[docs/OVERVIEW.md](docs/OVERVIEW.md)** lists every skill, agent, persona, rule and hook with its description. Regenerate it with `python3 scripts/generate-overview.py`; CI fails when it is stale. Agent tool access (which agents are genuinely read-only) is in `.claude/CLAUDE.md`.

## Recurring Automation (Loops & Routines)

The library ships a standard maintenance loop, Recurring Mode sections in the goal-shaped skills (finops, burn-rate-tracker, investor-reporting, security-review, and others), and copy-paste cloud-routine recipes in **[docs/AUTOMATION.md](docs/AUTOMATION.md)**. Library upkeep cadence: **[docs/MAINTENANCE.md](docs/MAINTENANCE.md)**. Mechanism selection across Claude Code, Codex and Antigravity: `/cure-product-engineering:engagement-automation`.

The SessionStart hook writes `.claude/loop.md` and workflows only into projects that opt in: a `.cure/` directory, a `claude.manifest.json`, or a CLAUDE.md that names Cure.

## Hooks

Every hook is a **command hook** with a timeout; none calls a model, and none blocks a `/loop` iteration or a routine. The logic lives in `hooks/cure_guard.py` (stdin JSON in, tested by `hooks/test_cure_guard.py`).

| Event | Matcher | What it does |
|---|---|---|
| SessionStart | `startup` | One-line load notice; opt-in provisioning (see above) |
| SessionStart | `compact` | Re-injects the Cure standards after compaction (stdout reaches Claude only on SessionStart, so this replaced a PreCompact hook that never did) |
| UserPromptSubmit | — | Flags destructive operations named in a prompt |
| PreToolUse | `Edit\|Write\|MultiEdit\|NotebookEdit` | Blocks edits to `.env`, lockfiles, credentials, tfstate; static security scan of skill, agent and persona files |
| PreToolUse | `Bash` | Blocks force-push to main/master (`-f`, `--force`, `--force-with-lease`, `+main`), `reset --hard`, `clean -f`, DROP/TRUNCATE outside migrations, `terraform destroy`, `kubectl delete namespace`, `rm -rf` of `/` or home |
| PreToolUse | `Skill` | Local usage telemetry (no network) |
| PostToolUse | `Agent\|Task` | After a write-capable agent finishes, adds a review reminder to the parent's context |
| PostToolUseFailure | — | Classifies the failure and suggests the next step (as additional context) |
| Stop | — | If product source was edited with no test, build or check afterwards, nudges once; silent for /loop, routines, SDK/CI runs, and a second stop in the same turn |

The opt-in tri-lane plugin adds a Bash sandbox guard for Codex and Antigravity lane commands; that one fails closed (`onFailure: "block"`).

## MCP (opt-in template)

`.mcp.json.example` is a template, not something the plugin loads, because every server needs per-project secrets. Copy what you need into the project's `.mcp.json`. Setup and auth: [docs/MCP-SETUP.md](docs/MCP-SETUP.md).

| Server | Transport | Notes |
|---|---|---|
| GitHub | HTTP | PAT header from `${CURE_GITHUB_MCP_PAT}` |
| Sentry | HTTP | OAuth on first use |
| Firebase | stdio | Official `firebase-tools` MCP, pinned version |
| PostgreSQL (DBHub) | stdio | Pinned; connection string in `DSN` |

## LSP

`.lsp.json` (loaded by the plugin): TypeScript (`typescript-language-server`, pinned; Node ≥22) and Python (Pyright, pinned).

## Path-Specific Rules

Rules reach a project only through npm or bootstrap, which copy them into `.claude/rules/`. Each loads only when Claude touches a file matching its `paths:`. The full trigger table is in `.claude/CLAUDE.md`.

| Rule | Standards |
|---|---|
| `android.md` | Clean Architecture, MVI, Compose, Hilt, type-safe navigation |
| `ios.md` | Swift 6 concurrency, SwiftUI + `@Observable`, Swift Testing |
| `web.md` | Next.js App Router, Server Components, Tailwind v4 |
| `firebase.md` | Cloud Functions v2, security rules, typed collections |
| `python.md` | uv, type hints, ruff, FastAPI/Django |
| `go.md` | Effective Go, error handling, project layout |
| `rust.md` | Edition 2024, `thiserror`/`anyhow`, Tokio |
| `sql.md` | Migration safety, indexes, identity/UUIDv7 keys |
| `docker.md` | Multi-stage builds, non-root, layer caching, `compose.yaml` |
| `terraform.md` | Modules, `use_lockfile` state locking, no `-target` in production |
| `cicd.md` | SHA-pinned actions, least-privilege `permissions:`, secrets handling |

## Tech Stack Defaults

These skills assume the following stack (override per-project as needed):

| Layer | Default |
|-------|---------|
| Android | Kotlin, Jetpack Compose, Hilt, MVI, Clean Architecture |
| iOS | Swift 6, SwiftUI, MVVM, structured concurrency |
| Web | Next.js, TypeScript, Tailwind CSS |
| Backend | Firebase (Firestore, Cloud Functions v2, Auth) |
| API | REST (OpenAPI), GraphQL where appropriate |
| Payments | Stripe (client SDKs + server-side via Firebase Functions) |
| AI | Claude, OpenAI, Gemini — production integrations with guardrails |
| Analytics | Firebase Analytics, Mixpanel, or PostHog |
| CI/CD | GitHub Actions, Firebase Deploy, Fastlane (mobile) |
| Testing | JUnit5/MockK (Android), Swift Testing/XCTest (iOS), Vitest/Playwright (Web) |
| Design | 8pt grid, WCAG AA minimum, platform-native patterns |

## Contributing

Authoring standard: [docs/AUTHORING.md](docs/AUTHORING.md). Rules for this repo: `.claude/CLAUDE.md`. In short:

1. Create `skills/{domain}/{name}/SKILL.md` with `name`, `description` (verb first, "Use when…" ending by char 100), `argument-hint`, and `metadata.verified`.
2. Follow the format: Step 1 (Classify), Step 2 (Gather Context), Step 3+ (Framework/Output); opinionated defaults; cross-reference related skills.
3. Run `python3 scripts/audit-library.py` (must stay green), `python3 scripts/sync-metadata.py --write`, `python3 scripts/sync-legacy-commands.py --write`, and `python3 scripts/generate-overview.py`.
4. Release with `scripts/release.sh` (never bump by hand).
