---
name: claude-bootstrap
version: "0.2.0"
description: "Provision Cure's standardized Claude development infrastructure into any project (greenfield or existing). Idempotently scaffolds CLAUDE.md, STATE.md, .claude/{settings.json,skills,agents,rules,hooks}, .cursorrules, .gemini/config.yaml. Manifest-driven, version-pinned, conflict-aware."
when_to_use: "Use to set up a new project with Cure standards, OR to upgrade an existing project's Cure infrastructure to a newer skills version, OR to audit drift across projects. NOT for ad-hoc skill installs (the bootstrap is the only supported path now)."
argument-hint: "[init|apply|doctor|inventory] [flags...]"
allowed-tools: ["Read", "Bash"]
context: fork
---

# Claude Bootstrap

Provisions and maintains the `.claude/` development surface area in any project.

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
3. Find the skills repo source. Priority order:
   - Look for `$CLAUDE_SKILLS_DIR` in env.
   - Look at `~/dev/ProductEngineeringSkills`, `~/Documents/ProductEngineeringSkills`, `/usr/local/lib/cure-skills`.
   - Try `npm root -g` and check for `@cure-consulting-group/product-engineering-skills`.
   - If none found, ask the user to point at the skills repo with `--skills-source`.

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

Build the command from the chosen options. Examples:

```bash
# init for a new web/firebase project with PCI+GDPR
node <path-to-bootstrap>/bin/claude-bootstrap.mjs init \
  --skills-version 5.0.0 \
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

Once `@cure-consulting-group/claude-bootstrap` is published to GitHub Packages,
substitute `npx @cure-consulting-group/claude-bootstrap` for the `node …` form.

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

## Step 6: Verify

After any successful `init` or `apply`:

```bash
node <path-to-bootstrap>/bin/claude-bootstrap.mjs doctor --skills-source ...
```

Should print `no drift detected.`

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
