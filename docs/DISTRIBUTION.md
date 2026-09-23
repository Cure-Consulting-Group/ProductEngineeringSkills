# Distribution & Updates

How the Cure skill library ships to projects and how it stays current. There is
**one primary path** (private plugin marketplace), **one opt-in path**
(vendoring), and a **generated Antigravity plugin** (Path 3) for the `agy` runtime, so a
project is never in an ambiguous state.

> **Access:** the marketplace lives in the **private** `Cure-Consulting-Group/ProductEngineeringSkills`
> repo. Only members of the GitHub org can add or install it. Nothing here is
> public; we do **not** submit to the community marketplace.
>
> **Consuming a project?** For copy-paste per-project setup, see
> [CONSUMING-PROJECTS.md](CONSUMING-PROJECTS.md). This file is the architecture/maintainer view.

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

### Second plugin in the same marketplace: `cure-tri-lane` (opt-in)

The marketplace also lists `cure-tri-lane` (source `./tri-lane`), the
multi-vendor orchestration flow: Claude architect, Codex lanes via `codex exec`,
Antigravity lane via `agy`, fresh-context advisor. It is a separate plugin with
its own `tri-lane/.claude-plugin/plugin.json` and version, so installing or
updating it never touches `cure-product-engineering`, and machines without it
behave exactly as before.

```
/plugin install cure-tri-lane@cure        # per machine, user scope; covers every project
```

Requirements (checked at run time by `tri-lane/skills/tri-lane/scripts/lane-preflight.py`,
never at install time): `codex` logged in with a ChatGPT plan, `agy` signed in
with a Google AI plan, `gtimeout`. See `tri-lane/README.md`. The library's audit
and sync scripts deliberately ignore `tri-lane/`; its version is bumped by hand
in its own manifest, and its lane models are pinned only in
`tri-lane/skills/tri-lane/lanes.md`.

---

### Path 1b — Codex CLI (same repo, same `cure` marketplace)

Codex reads `.agents/plugins/marketplace.json` and `.codex-plugin/plugin.json`. Only the
skills load in Codex. Agents, personas, rules and output styles are Claude-side.

    codex plugin marketplace add Cure-Consulting-Group/ProductEngineeringSkills
    codex plugin add cure-product-engineering@cure
    # update: codex plugin marketplace upgrade cure && codex plugin add cure-product-engineering@cure

- **Hooks are fenced.** Codex auto-loads a plugin's `hooks/hooks.json` and sets
  `CLAUDE_PLUGIN_ROOT` for it. The Codex manifest sets `"hooks": {"hooks": {}}` so none of
  our Claude hooks run there. `"hooks": []` does not fence: Codex treats it as undefined.
- **`disable-model-invocation` has a generated Codex twin.** `scripts/sync-metadata.py` writes
  `skills/<domain>/<name>/agents/openai.yaml` with `policy.allow_implicit_invocation: false`
  for every skill that sets it, and `--check` fails on drift.
- **Version** is carried inline in both Codex manifests and synced from
  `.claude-plugin/plugin.json` by `sync-metadata.py`.
- **Verification:** `python3 scripts/codex-smoke.py` installs into a throwaway `CODEX_HOME`
  and asserts through `codex debug prompt-input` (no model call) that every skill is listed and
  none are dropped. Codex silently drops a skill with invalid YAML frontmatter.
- **Read-only agents** (`.codex/agents/*.toml`) can't ship inside a Codex plugin. Consumers
  copy them in, as described in CONSUMING-PROJECTS.md.
- Consumer setup: listing budget, domain subsets, invocation, and what Codex does not enforce.
  See [CONSUMING-PROJECTS.md](CONSUMING-PROJECTS.md#codex-cli).

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

## Path 3 — Antigravity (`agy`): generated flat plugin

Antigravity cannot load this repo as-is. It ignores our manifest's `skills` array of domain
directories (0 skills load) and never scans `skills/<domain>/<name>/`. It loads a **flat**
plugin: `plugin.json {"name":"cure"}` plus `skills/<name>/`. That plugin is generated, not
committed. `dist/` is gitignored, and CI builds it and throws it away.

Where each path loads, per agy version, is recorded in
[evaluations/2026-09-23/platform-facts.md](evaluations/2026-09-23/platform-facts.md). That file
replaces the Wave 2.5 path claims in `BACKLOG.md` (the "universal `.agents/skills/`" claim and
the 2026-09-09 "workspace did not load" result, which was a false negative). Re-probe on every
agy minor release. Discovery semantics changed twice between 1.1.27 and 1.2.8.

**Build and install (per machine, global scope):**
```
python3 scripts/export-antigravity.py --install     # build dist/antigravity/cure, check collisions, agy plugin validate + install
python3 scripts/antigravity-smoke.py                # zero-model check: every skill listed as cure:<name>, every persona in /agents
```
`--install` refuses when a skill or agent name already exists under `~/.gemini`: in
`config/skills/`, the builtin skills, or another installed plugin. Precedence would otherwise
decide silently which skill a name resolves to. `agy plugin install` copies the plugin to
`~/.gemini/config/plugins/cure/`. Skills show up as `cure:<name>`. To update, re-run
`--install`. Nothing updates on its own. `dist/antigravity/cure/EXPORT-MANIFEST.json` records the
source SHA and library version, so a stale install can be spotted.

Measured 2026-09-23 on agy 1.2.9, library 7.9.0:
- `agy plugin validate`: 103 skills and 4 agents processed.
- `agy plugin install` into a throwaway `HOME`: exit 0. The install copied `skills/`, `agents/`
  and `rules/`.
- `agy -p "/skills"`: all 103 listed as `cure:<name>`. `/agents` lists all 4 personas. Neither
  spends a model turn.
- One model run in plan mode activated `cure:dora-metrics` and read its bundled reference file. It
  saw the 9 `cure-style-*` model-decision rules.
- `legal-doc-scaffold` and `proposal-generator` are listed but hidden from the model. They carry
  `disable-model-invocation`, which agy honors, so they run only when asked for by name.

**Per-workspace option (no copy):** an engagement repo can point at an export instead of
installing one. Commit `.agents/skills.json` with
`{"entries":[{"path":"/abs/path/to/dist/antigravity/cure/skills"}]}`. Each entry is scanned **one
level deep**, so it must point at the flat `skills/` dir and never at `skills/<domain>/`. Skills
load unnamespaced. A workspace loads only when agy has one. In the IDE that is the open folder.
Headless `agy -p` needs `--add-dir <repo>`. Without it only builtins load: 17 skills vs 120
measured. A workspace can also carry the whole plugin at `.agents/plugins/cure/`, which is how
the smoke test runs without touching `~/.gemini`.

**What the export changes in each SKILL.md:**
- `when_to_use` is appended to `description`. agy reads only `description`, and the existing
  description text stays first.
- Each inline `` !`cmd` `` becomes "run `cmd`" under a run-first lead-in. agy prints these
  literally and never executes them. The exporter fails if one survives.
- Links to repo files that do not travel (`docs/`, `rules/`, `shared/`, `agents/`, `hooks/`)
  become GitHub URLs on `main`. Consumer-project paths such as `docs/prd/` are left alone.
- `argument-hint`, `allowed-tools`, `disallowed-tools`, `context` and `effort` are dropped.
  `disable-model-invocation` and `metadata` are kept.
- A prose note is prepended where a Claude control does not travel: tool scope, READ-ONLY,
  DESTRUCTIVE, or "runs inline here" for `context: fork`. Skills that already carry a
  READ-ONLY/DESTRUCTIVE/advisory block are left as they are.
- Personas become agy custom agents at `agents/<name>/agent.md`, with `skills:` set to their
  loadout. Path rules become `rules/cure-rule-*.md` (`trigger: glob`). Output styles become
  `rules/cure-style-*.md` (`trigger: model_decision`). Together they total about 32 KB, and no
  file is over 24 KB.

**What you lose compared with Claude Code.** None of the following is enforced in agy:
- Hooks: the Stop quality gate, the skill-security guard, and the PreToolUse deny rules.
- Tool restrictions: `allowed-tools` and `disallowed-tools` become prose.
- `context: fork`: those 17 skills run inline and use the main conversation's context.
- `paths:` auto-activation: those skills become description-routed only.
- `$ARGUMENTS` substitution.
- The 40 Claude subagents.

`--mode plan` does not make a session read-only. Regulated or payment-touching work stays on
Claude Code (see [GUARDRAILS.md](GUARDRAILS.md)).

**Gemini CLI is not a supported target.** On a consumer Google login it can no longer run a
model (`IneligibleTierError … migrate to Antigravity`, measured 2026-09-23 on gemini 0.40.1). It
works only with a Gemini API key or Vertex AI. We ship nothing for it. A project that has a key
can point Gemini CLI at `dist/antigravity/cure/skills/` itself, without support.

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
6. Commits the release and prints the `git tag` / push commands.

CI (`.github/workflows/validate.yml`) runs the same gates on every PR, and
`publish.yml` publishes on version-tagged pushes to `main`.

---

## Mental model

| | Marketplace (Path 1) | Vendoring (Path 2) | Antigravity (Path 3) |
|---|---|---|---|
| Source of truth | this repo | a frozen copy per project | this repo, exported at install time |
| Update | `/plugin update` | re-run force install, commit | re-run `export-antigravity.py --install` |
| Local edits | never touched | risk of clobber on force | never touched (refuses on name collision) |
| Best for | everyone, by default | offline / must-be-in-tree | consultants working in `agy` |
| Skill names | `/cure-product-engineering:<skill>` | `/<skill>` (project-local) | `cure:<skill>` |
