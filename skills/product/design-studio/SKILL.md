---
name: design-studio
description: "Engineer brand identities, logos, design tokens, and production assets across Adobe Illustrator, Photoshop, and Figma"
when_to_use: "Use when designing logos, brand marks, visual identity systems, vector assets, or design tokens, or when pushing brand assets into Illustrator (.ai), Photoshop (.psd) mockups, or Figma variables. NOT for UI component systems (use design-system) or product screens (use product-design)."
argument-hint: "[brand-or-product-name]"
disable-model-invocation: true
---

# Design Studio: Brand Identity and Logo Engineering

Build agency-grade brand identities, mathematically sound vector marks, and cross-platform design systems, with automated hand-off into **Adobe Illustrator**, **Adobe Photoshop**, and **Figma**.

Bundled tooling lives next to this file. In Claude Code the directory is `${CLAUDE_PLUGIN_ROOT}/skills/product/design-studio`; in Gemini or Antigravity it is `.agents/skills/design-studio`. The commands below use `$STUDIO` for that directory.

| Tool | Does | Needs |
|---|---|---|
| `scripts/bridge_macos.sh` | Runs an ExtendScript (`.jsx`) inside Illustrator or Photoshop via AppleScript | macOS, the app installed; only those two apps are allowed |
| `scripts/figma_sync.py` | Publishes W3C design tokens as a Figma variable collection | `FIGMA_TOKEN` and `FIGMA_FILE_KEY` in the environment; validates offline unless `--apply` is passed |
| `scripts/export_asset_matrix.py` | Favicons, app icons, social cards, `.ico`, and an HTML brand book from one master SVG | macOS (`qlmanage` and `sips`); standard library only |
| `templates/illustrator/build_brand_master.jsx` | Five standard artboards, layer architecture, CMYK and spot swatches, `.ai` and `.eps` save | Illustrator |
| `templates/photoshop/update_mockup.jsx` | Smart Object replacement in a PSD mockup and high-resolution PNG export | Photoshop |
| `references/` | W3C token schema, Figma variables spec, Adobe ExtendScript API notes | read as needed |

Every script supports `--help`; none needs anything installed. None writes outside the paths you pass it. Nothing here sends data anywhere except `figma_sync.py` with `--apply`, which talks only to `api.figma.com`.

The Adobe bridge executes code inside Illustrator or Photoshop with the user's privileges. It refuses scripts without a `#target` line or with shell, network, eval, or include primitives. Before every bridge call: print the full `.jsx`, state what it will create or overwrite, and wait for the user to confirm.

## Design Asset Hierarchy

```
Brand Foundation
  ├── Strategy & Positioning (archetype, tone spectrum, 60-30-10 palette)
  ├── Master Vectors (pure semantic SVG, viewBox math, no raster embeds)
  ├── Production Print & Desktop (Illustrator .ai, artboards, CMYK, spot swatches)
  ├── Realistic Marketing Renders (Photoshop .psd, Smart Object replacement)
  ├── Digital Design System (W3C tokens.json -> Figma variables and auto-layout components)
  └── Multi-Resolution Matrix (favicons, app icons, social cards, HTML brand book)
```

## Pre-Processing (Auto-Context)

Project context, gathered before the skill runs. Values are injected inline below; in an environment that does not execute them (e.g. Gemini), run the shown commands instead.

- Portfolio: !`sed -n '1,40p' PORTFOLIO.md 2>/dev/null || echo "(no PORTFOLIO.md)"`
- Stack manifest: !`head -40 package.json 2>/dev/null || head -40 build.gradle.kts 2>/dev/null || head -20 Podfile 2>/dev/null || echo "(none detected)"`
- Existing brand assets: !`ls design/ brand/ assets/brand/ public/brand/ 2>/dev/null | head -20 || echo "(none)"`
- Recent commits: !`git log --oneline -5 2>/dev/null || echo "(not a git repo)"`

Use this context to tailor every output to the actual product domain and to reuse assets that already exist.

## Step 1: Strategic Discovery

Before generating any visual asset, fix the strategic parameters and write them down; every later step reads them.

1. **Brand archetype**, one primary: Creator (visionary, inventive), Sage (analytical, authoritative), Ruler (premium, structured), Outlaw (disruptive, bold), Magician (transformational), Hero, Everyman.
2. **Tone spectrum**: modern vs heritage, playful vs serious, minimal vs rich. Pick a point on each axis and state why.
3. **Lockup matrix** to deliver:
   - Primary horizontal: logomark left, wordmark right, aspect about 3:1 to 4:1.
   - Stacked vertical: mark above wordmark, about 1:1 to 4:5.
   - Submark or monogram: 1:1 for avatars, app icons, favicons.
   - Monochrome 1-bit: black and white for engraving, embroidery, single-colour print.
4. **Colour philosophy**: 60% dominant neutral, 30% structural brand tint, 10% high-energy accent. Every foreground and background pairing passes WCAG AA (4.5:1) for body text and AAA (7:1) for critical UI. Record the ratios, not just the hexes.

## Step 2: Vector Mathematics and Semantic SVG

All marks originate as clean, hand-written or algorithmically verified SVG.

1. `viewBox="0 0 512 512"` (or the matching aspect ratio); no fixed `width` or `height` attributes.
2. Minimal anchor points; no auto-trace jaggies; relative coordinates where it keeps paths short.
3. Wordmark letterforms outlined to `<path>` so rendering never depends on an installed font.
4. No `<image>` elements or embedded bitmaps inside an SVG.
5. Check optical centring (geometric centre is not optical centre) and a clearspace of at least one logomark height.

## Step 3: Illustrator Automation (`.ai` and print)

1. Adapt `templates/illustrator/build_brand_master.jsx` with the brand name, palette, and SVG paths. It creates five artboards: `01_Primary_Horizontal` (1200 x 400 pt), `02_Stacked_Vertical` (800 x 800), `03_Submark_Icon` (512 x 512), `04_Monochrome_1Bit` (512 x 512), `05_Favicon_Matrix` (400 x 400); layers `[Guides & Clearspace]`, `[Typography - Outlines]`, `[Artwork - Vectors]`, `[Background]`; global CMYK process swatches plus Pantone spot names.
2. Show the user the finished `.jsx` and the save directory, get confirmation, then run it:
   ```bash
   bash "$STUDIO/scripts/bridge_macos.sh" "Adobe Illustrator" "/path/to/build_brand_master.jsx"
   ```
3. Deliverables: `.ai` master with PDF compatibility, `.eps`, print-ready PDF/X.

## Step 4: Photoshop Automation (`.psd` mockups)

1. Choose the mockups (business card, stationery, signage, merchandise) and identify the Smart Object layer in each PSD (for example `REPLACE_LOGO`).
2. Adapt `templates/photoshop/update_mockup.jsx` to open the template, replace the Smart Object contents with the vector mark, and export a 300 DPI PNG.
3. Show the user the finished `.jsx` and which PSD it edits, get confirmation, then run it. The template refuses linked Smart Objects (they would overwrite their source file); embed them first.
   ```bash
   bash "$STUDIO/scripts/bridge_macos.sh" "Adobe Photoshop" "/path/to/update_mockup.jsx"
   ```
4. Without Photoshop, deliver the vector lockups and the asset matrix from Step 6; do not fake a mockup with a raster tool.

## Step 5: Figma Sync and Design Tokens

1. Write `tokens.json` in the W3C Design Tokens format (`references/w3c_token_schema.json`): `color`, `typography`, `spacing`, `radii`, `elevation`.
2. Validate offline first, then publish with `--apply` once the user has confirmed the target file. The token comes only from the environment, never the command line:
   ```bash
   python3 "$STUDIO/scripts/figma_sync.py" --tokens-file tokens.json
   FIGMA_TOKEN=... FIGMA_FILE_KEY=... python3 "$STUDIO/scripts/figma_sync.py" --tokens-file tokens.json --apply
   ```
   Each `--apply` creates a new variable collection; delete the previous one in Figma before re-publishing.
3. Component architecture in Figma: auto-layout frame for mark plus wordmark; variants `Type` (Primary, Stacked, Icon) and `Theme` (Default, Inverted, Monochrome).

## Step 6: Multi-Resolution Asset Matrix

```bash
python3 "$STUDIO/scripts/export_asset_matrix.py" --svg master_logo.svg --output-dir dist/brand_assets --brand-name "Brand"
```

Produces web favicons (16, 32, 48, `.ico`), Apple touch icon 180, Android Chrome 192 and 512, OpenGraph 1200 x 630, Twitter header 1500 x 500, avatar 400 x 400, and `brand_guidelines.html`, a standalone brand book with palette, type, and usage rules.

## Step 7: Output

Deliver a single folder with: the strategy note from Step 1, master SVGs for each lockup, the Illustrator and Photoshop deliverables when the apps were available, `tokens.json`, the asset matrix, and the brand book. State plainly which steps ran and which were skipped for a missing tool.

## When NOT to Use This Skill

- Building UI component libraries, spacing scales, or theming for an app: use `design-system`.
- Designing product screens and flows: use `product-design`.
- Platform-specific screen guidance: use `web-design-expert`, `ios-design-expert`, `android-design-expert`.
