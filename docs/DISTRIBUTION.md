# Distribution & Updates

How the Cure skill library ships to projects and how it stays current. There is
**one primary path** (private plugin marketplace) and **one opt-in path**
(vendoring), so a project is never in an ambiguous state.

> **Access:** the marketplace lives in the **private** `Cure-Consulting-Group/ProductEngineeringSkills`
> repo. Only members of the GitHub org can add or install it. Nothing here is
> public; we do **not** submit to the community marketplace.

---

## Path 1 — Private marketplace (recommended, seamless updates)

This is Claude Code's native plugin mechanism. Install once, update with one command, never clobbers local work.

**One-time, per developer machine:**
```
/plugin marketplace add Cure-Consulting-Group/ProductEngineeringSkills
/plugin install cure-product-engineering@cure
```
(`cure` is the marketplace name in `.claude-plugin/marketplace.json`; `cure-product-engineering` is the plugin.)
(Auth is the member's existing GitHub org access — a private repo stays private.)

**Updating — every project, every developer:**
```
/plugin marketplace update cure-product-engineering   # refresh the catalog
/plugin update cure-product-engineering               # pull the new version
```
Because the plugin declares a `version` in `.claude-plugin/plugin.json`, Claude
Code only offers an update when that field is bumped. No re-vendoring, no git
churn in consuming projects, no clobbered customizations.

**Why this is the default:** single source of truth (this repo), atomic version
pinning, and updates are a command instead of a copy-and-merge.

---

## Path 2 — Vendoring (opt-in: offline or checked-in skills)

Use only when a project must check the skills into *its own* git (air-gapped CI,
auditors who require the files in-tree, etc.).

```
npm install --save-dev @cure-consulting-group/product-engineering-skills
# postinstall (install-plugin.js) copies skills into ./.claude/, flattened.
```
- Skip-if-exists by default (won't clobber local edits).
- `CURE_SKILLS_FORCE=1 npm rebuild` to refresh from upstream — **review the diff before committing**, this overwrites.
- `SKIP_CURE_SKILLS_INSTALL=1` / `CI=1` to skip.

Vendoring freezes a copy; to update you re-run the force step per project. Prefer
Path 1 unless you specifically need in-tree files.

---

## Maintainer release flow (this repo)

Releasing is a single script. It enforces the quality gate, syncs every derived
artifact, and tags — so a release can't ship half-synced.

```
scripts/release.sh patch        # or: minor | major | X.Y.Z
```
What it does, in order:
1. Bumps `version` in `.claude-plugin/plugin.json` (the single source of truth).
2. `sync-metadata.py --write` — propagates version + counts to every doc/config.
3. `audit-library.py --fail-under 9.0 --min-item 7.0` — blocks the release if quality regressed.
4. `fix-library.py --check` — blocks if any inert field / broken ref slipped in.
5. `generate-overview.py` — regenerates `docs/OVERVIEW.md`.
6. `generate-gemini-skills.sh` — regenerates the Gemini `.skill` packages.
7. Commits the release and prints the `git tag` / push commands.

CI (`.github/workflows/validate.yml`) runs the same gates on every PR, and
`publish.yml` publishes on version-tagged pushes to `main`.

---

## Mental model

| | Marketplace (Path 1) | Vendoring (Path 2) |
|---|---|---|
| Source of truth | this repo | a frozen copy per project |
| Update | `/plugin update` | re-run force install, commit |
| Local edits | never touched | risk of clobber on force |
| Best for | everyone, by default | offline / must-be-in-tree |
| Skill names | `/cure-product-engineering:<skill>` | `/<skill>` (project-local) |
