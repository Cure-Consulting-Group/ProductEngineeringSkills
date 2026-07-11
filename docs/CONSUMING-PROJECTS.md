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

You now have all 80 skills, 39 agents, 4 personas, 11 rules, 9 output styles,
and the hooks. Invoke any skill with `/cure-product-engineering:<skill>`, e.g.:

```
/cure-product-engineering:sdlc
/cure-product-engineering:project-bootstrap
```

Agents auto-delegate based on the task, or list them with `/agents`.

## Step 3 — Verify

```
/help          # skills appear under the cure-product-engineering: namespace
/agents        # the 39 agents are listed
```

## Step 4 — Update (the seamless part)

When the library ships a new version:

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
default. With this library's 80 skills installed alongside a project's own
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
