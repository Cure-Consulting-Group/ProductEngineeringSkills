---
name: design-studio-audit-2026-09
description: 2026-09-06 audit of skills/product/design-studio + brand-identity-design returned FAIL; pending consolidation, Pillow removal, Antigravity path fix, JSX review gate
metadata:
  type: project
---

On 2026-09-06 the first audit of `skills/product/design-studio/` and `skills/product/brand-identity-design/` (both untracked, pre-commit) returned FAIL.

**Why:** Both skills were ported from Google Antigravity (bridge header literally says "Antigravity agent CLI"; all script paths use Antigravity's `.agents/skills/...` layout, not `${CLAUDE_PLUGIN_ROOT}`). Two blocking issues: (1) `bridge_macos.sh` runs agent-generated ExtendScript inside Illustrator/Photoshop via `osascript do javascript` with no content gate, which sidesteps every Bash deny rule and PreToolUse guard in this plugin (ExtendScript has `system.callSystem`, `app.system`, `Socket`); (2) `export_asset_matrix.py` and `composite_mockup.py` import Pillow, violating the stdlib-only convention and breaking `scripts/verify-skill-scripts.sh`. `benchmarks/` under the skill also ships a real client name ("The Social Garden") and the maintainer's iCloud paths.

**How to apply:** If these skills reappear for re-audit, verify (a) only one of the two skills survives (they were near-duplicates sharing one scripts dir), (b) the bridge has a JSX denylist scan + APP_NAME whitelist + argv-passed paths, (c) no `from PIL` under `skills/**`, (d) `benchmarks/` moved to `evals/` with client data scrubbed, (e) `--token "$FIGMA_TOKEN"` removed from SKILL.md examples (env only). Re-check the Gemini `.skill` zips were regenerated after fixes; they cannot be read statically.
