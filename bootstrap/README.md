# @cure-consulting-group/claude-bootstrap

Provisions Cure's Claude development infrastructure into any project. Idempotent, manifest-driven, version-pinned.

## Install

```bash
# from GitHub Packages registry
npm install -g @cure-consulting-group/claude-bootstrap

# or one-shot via npx
npx @cure-consulting-group/claude-bootstrap init --skills-version 5.0.0
```

The package resolves the source skills repo via, in priority order:

1. `--skills-source <path>` flag
2. `$CLAUDE_SKILLS_DIR` environment variable
3. installed `@cure-consulting-group/product-engineering-skills` package

## Commands

```
claude-bootstrap init      [options]   create claude.manifest.json + scaffold managed files
claude-bootstrap apply     [options]   re-render templates against existing manifest
claude-bootstrap doctor    [options]   audit a project for drift; nonzero exit on findings
claude-bootstrap inventory [paths...]  read manifests across many projects, emit CSV
claude-bootstrap version
claude-bootstrap help
```

Run `claude-bootstrap help` for the full flag list.

## What it produces

```
<project>/
├── CLAUDE.md                  # managed-block markdown; user content outside fences preserved
├── STATE.md                   # same model
├── claude.manifest.json       # the contract; commit this
├── .claude/
│   ├── settings.json          # init-only
│   ├── skills/<name>/SKILL.md # vendored from source
│   ├── agents/<name>.md       # vendored from source
│   ├── rules/<name>.md        # vendored from source (auto-derived from stack)
│   ├── hooks/hooks.json       # generated from manifest.hooks
│   └── upgrades/              # conflict files when on-disk diverges from tracked
├── .cursorrules               # generated pointer to CLAUDE.md
└── .gemini/config.yaml        # generated mirror for Gemini CLI parity
```

## Idempotency model

Every managed region — markdown blocks, vendored files, generated files — is hashed in `claude.manifest.json`. On `apply`:

- Block/file hash matches stored hash → safe to overwrite cleanly.
- Block/file hash differs from stored hash → user edited; emit a `.conflict` file under `.claude/upgrades/`, preserve user content in place. Apply exits with code 2.
- Source file unchanged + target unchanged → no write.

Edit outside fences freely. Edit inside fences and you'll get a conflict file with the bootstrap's intended content for you to merge.

## Org policy

If `org.manifest.json` exists at the root of the resolved skills repo, `apply` enforces:

- `bootstrap.minimumSkillsVersion` — projects below this floor cannot apply.
- `skills.required[]` / `skills.forbidden[]` — same for `agents` and `rules`.

Use this to push security-critical changes across all consuming projects.

## Programmatic API

```js
import { createManifest, validateManifest } from "@cure-consulting-group/claude-bootstrap/manifest";
import { planFile } from "@cure-consulting-group/claude-bootstrap/blocks";
import { buildPlan, applyPlan } from "@cure-consulting-group/claude-bootstrap";
```

Sub-paths: `/manifest`, `/blocks`, `/vendor`, `/generated`, `/diagnose`, `/inventory`, `/org`, `/schema`, `/org-schema`.

## Development

```bash
cd bootstrap
npm install
npm test     # 106 tests across manifest, blocks, vendor, generated, org, diagnose, integration
```

## License

MIT
