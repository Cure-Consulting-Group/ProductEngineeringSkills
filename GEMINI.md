# ProductEngineeringSkills — Cure Consulting Group

This is the central skill library for all Cure Consulting Group projects. It is distributed as a Claude Code plugin and a set of Gemini skills.

## Project Identity

- **Goal**: Autonomously provide production-grade engineering, product, and business skills to any project.
- **Standards**: Clean Architecture, MVI (Android), MVVM (iOS), Next.js App Router (Web), Firebase (Backend).
- **Distribution**:
  - Claude Code Plugin (manifest in `.claude-plugin/plugin.json`).
  - Google Gemini Skills (`gemini skills/*.skill`).
  - Legacy slash commands (`claude-commands/*.md`).

## Repository Structure

- `skills/{domain}/{name}/SKILL.md`: 75 skills organized by domain. Domains: engineering (39), platform (10), product (10), business (7), marketing (4), security (4), legal (1).
- `skills/{domain}/{name}/scripts/`: Optional bundled Python stdlib scripts (zero pip). See `docs/SCRIPTS_CONVENTION.md`.
- `agents/`: 35 custom subagent definitions in Markdown.
- `personas/`: 4 cross-domain engagement archetypes (tech-lead, product-lead, engagement-pm, solo-consultant).
- `hooks/hooks.json`: Multi-layer automated enforcement (command, prompt, agent — 12 event types).
- `rules/`: 11 path-specific coding standards (Android, iOS, Web, Firebase, Python, Go, Rust, SQL, Docker, Terraform, CI/CD).
- `output-styles/`: 9 custom formatting styles (PRD, code, financial, audit, API spec, ADR, runbook, test plan, alerts).
- `gemini skills/`: Flat `.skill` ZIP archives for importing into Google Gemini workspace.
- `claude-commands/`: Legacy Markdown format for backwards compatibility.
- `.claude-plugin/plugin.json`: Plugin manifest and metadata.
- `.mcp.json` & `.lsp.json`: Pre-configured MCP and LSP server settings.
- `marketplace.json`: Plugin marketplace manifest for distribution.

## Operational Workflows

### Maintenance Commands

- **Generate Gemini Skills**: `./generate-gemini-skills.sh` (converts `skills/{domain}/{name}/SKILL.md` to `.skill` ZIPs).
- **Verify Installation**: `./verify-install.sh` (audits the local installation health).
- **Auto-Update**: `./auto-update.sh` (pulls latest changes and version bumps).
- **Project Setup**: `./setup.sh` (onboards a new project to use these standards).
- **Regenerate Overview**: `python3 scripts/generate-overview.py` (rebuilds `docs/OVERVIEW.md` from frontmatter).
- **Verify Skill Scripts**: `./scripts/verify-skill-scripts.sh` (smoke-tests every bundled skill script via `--help`).

### Development Rules

- **Adding a Skill**:
  1. Create `skills/{domain}/{name}/SKILL.md`. Domain is one of: engineering, platform, product, business, marketing, security, legal.
  2. Include YAML frontmatter: `name`, `description`, `argument-hint`.
  3. Set `allowed-tools: ["Read", "Grep", "Glob"]` if read-only; set `disable-model-invocation: true` if destructive/sensitive.
  4. Sync to `claude-commands/` and run `./generate-gemini-skills.sh`.
  5. Run `python3 scripts/generate-overview.py` to refresh `docs/OVERVIEW.md`.
- **Bundled Scripts**: Python stdlib only, zero pip installs. Every script must support `--help` and ideally `--json`.
- **Adding a Persona**: Create `personas/{name}.md` with frontmatter (`name`, `description`, `type: persona`). Reference only existing skills/agents — never invent names.
- **Versioning**: Bump version in `.claude-plugin/plugin.json` (Major/Minor/Patch). Current version: **6.0.3**.
- **Standards Enforcement**: Follow patterns in `rules/*.md` strictly.

## Tech Stack Defaults

| Layer | Standard |
|-------|----------|
| **Android** | Kotlin, Jetpack Compose, Hilt, MVI, Clean Architecture |
| **iOS** | Swift, SwiftUI, MVVM, Structured Concurrency |
| **Web** | Next.js App Router, TypeScript, Server Components, Tailwind CSS |
| **Backend** | Firebase (Firestore, Cloud Functions v2, Auth) |
| **Payments** | Stripe |
| **CI/CD** | GitHub Actions |
| **Design** | 8pt grid, WCAG AA, platform-native |

## Documentation References

- `README.md`: General overview and installation.
- `CLAUDE.md`: Claude-specific instructions (mirror of this file).
- `AGENT-GUIDE.md`: Comprehensive guide for agent/skill prompting patterns.
- `EVALUATION.md`: Full project evaluation metrics.
- `docs/OVERVIEW.md`: Auto-generated overview of all skills/agents/personas.
- `docs/SCRIPTS_CONVENTION.md`: Convention for bundled Python scripts in skills.
- `BACKLOG.md`: Internal improvement backlog (not for distribution).
