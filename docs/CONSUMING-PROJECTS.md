# Adopt the Cure skill library in a project

Copy-paste setup for any Cure project that wants the shared skills, agents,
rules, and hooks. ~2 minutes, one time. Updates are then a single command.

> **Access:** the library lives in the **private** repo
> `Cure-Consulting-Group/ProductEngineeringSkills`. You need to be a member of
> the GitHub org (and be `gh auth login`'d, or have GitHub access configured in
> Claude Code). Nothing here is public.

---

## Step 1 — Add the marketplace (once per machine)

In Claude Code, from any project:

```
/plugin marketplace add Cure-Consulting-Group/ProductEngineeringSkills
```

This registers the private marketplace named **`cure`**. You only do this once
per machine; it's shared across all your projects.

## Step 2 — Install the plugin

```
/plugin install cure-product-engineering@cure
```

You now have all 103 skills, 40 agents, 4 personas, 11 rules, 9 output styles,
and the hooks. Invoke any skill with `/cure-product-engineering:<skill>`, e.g.:

```
/cure-product-engineering:sdlc
/cure-product-engineering:project-bootstrap
```

Agents auto-delegate based on the task, or list them with `/agents`.

## Step 3 — Verify

```
/help          # skills appear under the cure-product-engineering: namespace
/agents        # the 40 agents are listed
```

## Step 4 — Update (the seamless part)

**Zero-command (recommended):** enable auto-update once and never run update
commands again — Claude Code refreshes the cure catalog and updates the plugin
at session start. Either toggle it in the UI (`/plugin` → Marketplaces → cure →
Enable auto-update) or add this to the project's `.claude/settings.json`
(included in the vendored settings.json since v7.4.3):

```json
{
  "extraKnownMarketplaces": {
    "cure": {
      "source": { "source": "github", "repo": "Cure-Consulting-Group/ProductEngineeringSkills" },
      "autoUpdate": true
    }
  }
}
```

This also registers the marketplace itself, so a project carrying this settings
block skips `/plugin marketplace add` — only the one-time
`/plugin install cure-product-engineering@cure` remains.

**Manual (if you prefer pinned-until-you-say-so):**

```
/plugin marketplace update cure          # refresh the catalog
/plugin update cure-product-engineering  # pull the new version
```

No re-vendoring, no file copying, no merge conflicts. Updates arrive only when
the maintainers bump the version, so you never get surprised mid-task.

On first session start after install, the plugin self-provisions two
project-scoped files that plugins cannot ship natively: `.claude/loop.md`
(the Cure maintenance loop — run bare `/loop`) and `.claude/workflows/`
(`/cure-code-audit`, `/cure-release-check`, `/cure-migration-sweep`).
Copy-if-missing only: your local edits are never overwritten, and nothing is
written outside a project (requires `.claude/` or `.git` in the cwd).

---

## Pin a version (optional)

To lock a project to a specific release instead of always taking latest, install
a tagged version:

```
/plugin install cure-product-engineering@cure --version 7.1.0
```

Bump it deliberately when you're ready. Useful for projects under audit or in a
freeze.

## Vendoring instead (only if you must check skills into the project's git)

For air-gapped CI or projects that require the files in-tree:

```
npm install --save-dev @cure-consulting-group/product-engineering-skills
```

The postinstall copies skills into `./.claude/` (skip-if-exists, won't clobber
local edits). To refresh: `CURE_SKILLS_FORCE=1 npm rebuild` — **review the diff
before committing**. Prefer the marketplace path unless you specifically need
in-tree files. See [DISTRIBUTION.md](DISTRIBUTION.md) for the full comparison.

## Manifest + release rings (T31)

Every consuming project declares its install in `.claude/cure-manifest.json`:

```json
{
  "library": "cure-product-engineering",
  "version": "7.4.4",
  "mode": "plugin",           // plugin | vendored | hybrid | none
  "channel": "stable",        // stable | next  (next = canary ring)
  "installed": "2026-08-14",
  "local_skills": ["ledger-invariants"]   // project-owned; never drift-flagged
}
```

- **`mode: plugin` is the fleet standard.** Vendored copies drift silently (the
  2026-08-14 census found 10 projects with 100% of vendored files stale) and
  double-load against the installed plugin. Migrate with
  `scripts/migrate-to-plugin.sh <project-path> [channel]` — removes only
  library-named vendored files, keeps local skills, git shows every deletion.
- **`channel: next` = canary ring.** One active project (currently statledger)
  runs `next`; new releases soak there ≥5 working days before being promoted.
  Promotion is a human call informed by telemetry + eval results. Rollback:
  flip the manifest pin and reinstall the tagged version.
- **Census:** `python3 scripts/fleet-census.py --projects-dir <dir-of-checkouts>`
  reports mode, version lag, drift, local skills, and double-install risk per
  project; exit 1 on problems. Runs weekly via the library maintenance loop
  (CI runners can't reach local checkouts — this is a local check by design).
- **Local skills are the innovation channel, not drift.** Anything in
  `local_skills` is project-owned; at each quarterly re-eval, review them for
  upstreaming into the library.

---

## Paste into the project's CLAUDE.md

So every contributor knows the library is available and how to refresh it, add
this block to the consuming project's `CLAUDE.md`:

```markdown
## Cure skill library

This project uses the shared Cure skill library (private plugin).

- Install once:  `/plugin marketplace add Cure-Consulting-Group/ProductEngineeringSkills`
                 then `/plugin install cure-product-engineering@cure`
- Update:        `/plugin marketplace update cure && /plugin update cure-product-engineering`
- Invoke:        `/cure-product-engineering:<skill>`  (e.g. `:sdlc`, `:project-bootstrap`)
- Inventory:     run `/agents`, or see the library's docs/OVERVIEW.md
```
```

## Skill-listing budget (token economy)

Claude Code caps the per-session skill listing at roughly 1% of model context by
default. With this library's 103 skills installed alongside a project's own
skills, trigger text past the budget gets truncated — those skills stop being
auto-discoverable (explicit `/name` invocation still works).

If auto-discovery seems flaky in a skill-heavy project, raise the budget in the
project's `.claude/settings.json`:

```json
{
  "skillListingBudgetFraction": 0.02
}
```

The library keeps its own trigger text tight (≤350 chars per skill, enforced by
`scripts/audit-library.py`) so it consumes as little of the shared budget as
possible.

---

## Codex CLI

The same repo is a Codex plugin marketplace (`.agents/plugins/marketplace.json`,
marketplace name **`cure`**). In Codex **only the skills load**. The Claude
hooks are fenced off, and agents, personas, rules, and output styles stay on the Claude side.
Measured on codex-cli 0.155.0 (2026-09-23). Re-check with `scripts/codex-smoke.py`
after any Codex upgrade.

### Install (once per machine)

```bash
codex plugin marketplace add Cure-Consulting-Group/ProductEngineeringSkills   # private: needs your GitHub git credentials
codex plugin add cure-product-engineering@cure
codex plugin list | grep @cure            # cure-product-engineering@cure  installed, enabled  <version>
```

Codex installs a **snapshot** into `$CODEX_HOME/plugins/cache/cure/cure-product-engineering/<version>/`.
To take a new release: `codex plugin marketplace upgrade cure && codex plugin add cure-product-engineering@cure`.
Re-running `add` replaces the snapshot (measured). The GitHub source installs about 15 MB. A local checkout
also works as the source (`codex plugin marketplace add /path/to/ProductEngineeringSkills`), but it copies
the working tree as it is, including `.git/` (about 80 MB) and any uncommitted edits.

Verify without a model call:

```bash
python3 scripts/codex-smoke.py   # from a library checkout: throwaway CODEX_HOME, asserts every skill is listed
```

### Invoke

- **Explicit:** `$cure-product-engineering:<skill>` in the prompt, e.g.
  `$cure-product-engineering:sdlc`. `/skills` lists them. This also works for
  the skills hidden from implicit use below.
- **Implicit:** Codex picks a skill from its `description`. Only `name` and
  `description` are read. `when_to_use`, `argument-hint`, `$ARGUMENTS`/`$0`
  substitution and `` !`cmd` `` preprocessing do not exist in Codex.
- **Hidden skills:** skills with `disable-model-invocation: true` (currently
  `proposal-generator`, `legal-doc-scaffold`) ship a generated
  `skills/<domain>/<name>/agents/openai.yaml` with `policy.allow_implicit_invocation: false`. Codex drops them from
  the implicit listing, but `$name` still runs them. `scripts/sync-metadata.py` generates the sidecar.

### Skill-listing budget: set it

Codex budgets the skill catalog at 2% of context by default. With 103 skills
that cuts every description to about 110 characters, which usually drops the "Use when…" clause.
Measured: 6,000 tokens gives about 130 characters, and ≥8,000 gives the full text (longest description today is 344 chars).
Explicit values are **capped at 10,000** (documented), so asking for 12–15k gets you 10k.

```toml
# ~/.codex/config.toml  (or a trusted project's .codex/config.toml)
[skills]
max_context_tokens = 10000
```

Or load a **domain subset** and turn off whole domains you don't use. Disable by
qualified name, which survives version bumps. This is undocumented but measured on 0.155.0. Path entries
must point at a single `SKILL.md`, because a domain directory path is ignored:

```toml
[[skills.config]]
name = "cure-product-engineering:tax-preparation"
enabled = false
```

Generate the block for a whole domain (here `tax`) from a library checkout:

```bash
for f in skills/tax/*/SKILL.md; do n=$(sed -n 's/^name: *//p' "$f" | head -1)
  printf '[[skills.config]]\nname = "cure-product-engineering:%s"\nenabled = false\n\n' "$n"; done
```

### What Codex does NOT enforce, and what to use instead

| Claude-side control | Codex behavior | Enforcement in Codex |
|---|---|---|
| `allowed-tools` / `disallowed-tools` | ignored | `sandbox_mode = "read-only"` for the session, or a custom agent (below) |
| `context: fork` | ignored; runs inline | ask for a subagent explicitly (Codex spawns none unless the prompt, AGENTS.md, or a skill asks) |
| `disable-model-invocation` | ignored | generated `skills/<domain>/<name>/agents/openai.yaml` (above) |
| Plugin hooks (`hooks/hooks.json`) | **fenced**: `.codex-plugin/plugin.json` sets an empty inline `hooks` object | a project's own `<repo>/.codex/hooks.json` or managed `requirements.toml` if you need guards |

The hook fence matters because Codex auto-loads a plugin's `hooks/hooks.json` and
sets `CLAUDE_PLUGIN_ROOT` for it. Once trusted, our Claude hooks would run in Codex: telemetry writes,
session echo, and `.claude/` provisioning. Codex also warns on every run that prompt hooks are unsupported.
Measured: `"hooks": []` does **not** fence, because Codex treats it as undefined.
`{"hooks": {}}` does fence, even with the Claude manifest present.

### Read-only review agents (copy in; plugins can't ship them)

Codex plugins cannot bundle custom agents. The library keeps three at
`.codex/agents/`, each with `sandbox_mode = "read-only"`, which is Codex's only hard tool restriction:

| File | Agent name | Role |
|---|---|---|
| `cure-security-reviewer.toml` | `cure_security_reviewer` | security review of a diff/PR/subsystem |
| `cure-secret-scanner.toml` | `cure_secret_scanner` | leaked-credential inventory, values redacted |
| `cure-tax-reviewer.toml` | `cure_tax_reviewer` | draft tax review for CPA sign-off, never writes taxpayer facts |

```bash
mkdir -p .codex/agents   # project scope (trusted projects only); or ~/.codex/agents for all projects
cp /path/to/ProductEngineeringSkills/.codex/agents/cure-*.toml .codex/agents/
```

Then ask for one by name, for example: "Have cure_security_reviewer review this branch against main."

### Managed AGENTS.md block

Codex reads `AGENTS.md` (32 KiB combined cap by default). Keep the Cure block
small: routing and invariants only. The skills carry the detail. Paste this between the markers and
replace the whole block on update:

```markdown
<!-- cure:begin (managed — replace whole block on update) -->
## Cure skill library

Skills: `cure-product-engineering` Codex plugin (marketplace `cure`). Invoke with
`$cure-product-engineering:<skill>`; `/skills` lists them.

Routing:
- New project or feature scaffold: `project-bootstrap`, then the platform scaffold skill.
- Requirements, PRD, SDLC docs: `sdlc`, `product-manager`.
- Review before merge: `security-review`; delegate to `cure_security_reviewer` if installed.
- Secrets or .env work: `env-secrets-manager`; delegate scans to `cure_secret_scanner`.
- Release: `release-management`. Incident: `incident-response`.
- Tax work: tax skills draft for CPA review only; delegate review to `cure_tax_reviewer`.
- Proposals and legal documents run only on explicit `$name`.

Invariants:
- Never edit `.env*` (except `.env.example`), lock files, credential files, or `*.tfstate` by hand.
- Parameterized queries; validate inputs; no secrets in code, logs, or commits.
- New code ships with tests; run them before calling work done.
- Tax and legal output is a draft for a licensed professional. Never file, pay, sign, or send client data externally.
<!-- cure:end -->
```
