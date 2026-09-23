# Claude Bootstrap

> **This skill writes files.** `init` and `apply` create or rewrite `CLAUDE.md`,
> `STATE.md`, `.claude/` and `claude.manifest.json` in the target project;
> `doctor` and `inventory` are read-only. Before any `init`/`apply`, run the same
> command with `--dry-run`, show the user the per-file plan, and write only after
> they confirm. No runtime enforces this for you (`allowed-tools` grants, it does
> not restrict), so the confirm step is the guardrail.

**Outcome:** the target project's managed files match its `claude.manifest.json` and the pinned
library version; done when `doctor` prints `no drift detected.` (or, for `doctor`/`inventory`, when
the report is delivered). Don't hand-edit managed files or touch unrelated project files.

The actual engine is the npm package `@cure-consulting-group/claude-bootstrap`
(in `bootstrap/` of this repo). This skill is the conversational front door —
it gathers context, asks clarifiers, then shells out to the CLI.

## Step 1: Determine the operation

Decide which mode the user wants:

- **init** — first-time setup. Creates `claude.manifest.json` and scaffolds all
  managed files. Run when the target project has no `claude.manifest.json`.
- **apply** — re-render templates / vendor updated source files / regenerate
  hooks. Run after editing `claude.manifest.json` or after the skills repo
  ships a new version.
- **doctor** — read-only audit. Reports drift between the manifest and the
  files on disk and the source repo. Run before/after upgrades.
- **inventory** — multi-project CSV. Run from a parent dir with several
  Cure projects under it.

Default for an empty project is `init`. Default for one with an existing
manifest is `apply`. Ask the user only if the situation is ambiguous.

## Step 2: Gather context

Before running the CLI, collect (silently):

1. Run `pwd && ls -la && cat claude.manifest.json 2>/dev/null` to see the
   current state.
2. If `init`: detect the stack via `cat package.json build.gradle.kts Podfile go.mod 2>/dev/null` to know what to suggest.
3. Find the skills repo source (the CLI resolves `--skills-source`, then `$CLAUDE_SKILLS_DIR`,
   then the installed npm package). If neither flag nor env var is set, look for a checkout of
   `ProductEngineeringSkills` in the user's usual project root (e.g. `~/dev/`, or an external
   volume such as `/Volumes/<drive>/projects/`) and `npm root -g`; if still not found, ask the
   user for the path. Confirm it contains `.claude-plugin/plugin.json`.

## Step 3: Confirm choices with the user (init only)

For `init`, surface the detected defaults and let the user override:

- Project name (default: from `package.json` or directory name)
- Project type (auto-detected from stack)
- Skills to activate (suggest based on stack):
  - `web` stack → `nextjs-feature-scaffold`, `feature-audit`, `security-review`
  - `firebase` stack → `firebase-architect`
  - `stripe` in deps → `stripe-integration`
  - `android` → `android-feature-scaffold`, `android-design-expert`
  - `ios` → `ios-architect`, `ios-design-expert`
- Compliance flags (HIPAA / PCI / GDPR / COPPA / SOC2)
- Phase (`discovery` / `mvp` / `beta` / `ga` / `maintenance`)

## Step 4: Run the CLI

Build the command from the chosen options. `init` requires `--skills-version`: pin the
version the skills source actually ships (read from its `.claude-plugin/plugin.json`, the
library's single version source) — never a hand-typed number. Examples:

```bash
# init for a new web/firebase project with PCI+GDPR
node <path-to-bootstrap>/bin/claude-bootstrap.mjs init \
  --skills-version "$(node -p "require('<path-to-ProductEngineeringSkills>/.claude-plugin/plugin.json').version")" \
  --skills-source <path-to-ProductEngineeringSkills> \
  --name <project-name> \
  --skill stripe-integration --skill firebase-architect --skill feature-audit \
  --agent pr-reviewer --agent firebase-security-auditor \
  --pci --gdpr

# apply after manifest edits
node <path-to-bootstrap>/bin/claude-bootstrap.mjs apply \
  --skills-source <path-to-ProductEngineeringSkills>

# doctor — read-only drift check
node <path-to-bootstrap>/bin/claude-bootstrap.mjs doctor \
  --skills-source <path-to-ProductEngineeringSkills>

# inventory across many projects
node <path-to-bootstrap>/bin/claude-bootstrap.mjs inventory \
  --skills-source <path-to-ProductEngineeringSkills> \
  ../project-a ../project-b ../project-c
```

`@cure-consulting-group/claude-bootstrap` is published to GitHub Packages (0.3.1 as of
2026-09-23; check with `npm view @cure-consulting-group/claude-bootstrap version
--registry=https://npm.pkg.github.com`). `npx @cure-consulting-group/claude-bootstrap …` works in
place of the `node …` form once the machine's `.npmrc` maps `@cure-consulting-group` to
`https://npm.pkg.github.com` with a token that has `read:packages`; otherwise use the checkout.

## Step 5: Interpret the output

The CLI prints a per-file plan: `[create]`, `[update]`, `[conflict]`,
`[unchanged]`, `[remove]`. Then it writes (unless `--dry-run`) and reports.

Exit codes:
- `0` — success, no changes needed or all changes applied cleanly.
- `1` — manifest invalid, org policy violated, or unrecoverable error.
- `2` — conflicts detected (user-edited managed regions). Existing content
  preserved; intended content saved to `.claude/upgrades/*.conflict`.

If exit code 2: open the `.claude/upgrades/*.conflict` files alongside the
preserved files, merge by hand, then re-run `apply` (the next run will
recompute hashes against the merged content).

## Step 6: Acceptance

After `init` or `apply`, `doctor` against the same `--skills-source` must print
`no drift detected.` Report the per-file plan and the doctor result to the user.

## Constraints

- **Never edit files inside `<!-- CLAUDE-BOOTSTRAP:BEGIN ... END -->` fences
  by hand.** Edit the source template (in the skills repo), then re-run apply.
  User customizations belong outside fences or in `CLAUDE.local.md`.
- **Never edit vendored files (`.claude/skills/*`, `.claude/agents/*`,
  `.claude/rules/*`) by hand.** Same model: change the source skill, then
  re-run apply.
- HIPAA or PCI in `compliance` forces `installMode: vendored`. Do not attempt
  `--install-mode symlink` for compliance-flagged projects.
- Always commit `claude.manifest.json` to the project's repo. It is the
  reproducibility record.
