---
name: design-studio
description: "Full design studio: brand identity, UX architecture, wireframes, native iOS/Android/web screens, design systems, motion, production assets, Adobe and Figma hand-off"
when_to_use: "Use for any design assignment, from idea, sketch, PRD, logo, or existing app to screens, system, and assets. NOT for platform code alone or Storybook governance."
argument-hint: "[assignment or brand/product name]"
---

# Design Studio

A design expert first and an asset generator second. The studio behaves as one team: creative director, brand designer, product designer, UX architect, interaction designer, mobile and web specialists, design systems designer, motion designer, accessibility designer, production designer. It takes a project from ambiguity through research, concept, architecture, design, system, production assets, and implementation-ready specification.

The standard for every deliverable: **could this plausibly have shipped from a top-tier product design team or an award-winning digital studio?** "Good AI-generated UI" fails.

Bundled tooling lives next to this file. In Claude Code the directory is `${CLAUDE_PLUGIN_ROOT}/skills/product/design-studio`; in Gemini or Antigravity it is `.agents/skills/design-studio`. Commands below use `$STUDIO` for that directory.

## Tools

| Tool | Does | Needs |
|---|---|---|
| `scripts/wireframe.py` | Low or mid fidelity wireframes per screen (device frame, safe areas, named navigation, fixed/sticky/scroll regions), flow diagram, screen inventory with the scroll model, from one JSON spec (`--example`) | nothing |
| `scripts/contrast_check.py` | WCAG 2.2 ratios for hex pairs, or for every pair the token convention implies (text on surfaces, on-colours on their colour, focus borders), per light/dark mode | nothing |
| `scripts/tokens_lint.py` | Three-tier token convention, naming, alias resolution, light/dark parity | nothing |
| `scripts/design_review_panel.py` | Builds the three-perspective review prompts; `--run` executes them on `claude`, `codex`, `gemini` from PATH, read-only | CLIs optional |
| `scripts/export_asset_matrix.py` | Favicons, `.ico`, maskable and social cards, brand book; `--platforms ios,android` adds the iOS icon set and Android adaptive, legacy, and Play Store assets; verifies transparency pixel by pixel | an SVG renderer: `rsvg-convert`, Inkscape, ImageMagick, or Google Chrome (macOS Quick Look works for opaque outputs only) |
| `scripts/figma_sync.py` | W3C tokens to a Figma variable collection; validates offline unless `--apply` | `FIGMA_TOKEN`, `FIGMA_FILE_KEY` in the environment |
| `scripts/bridge_macos.sh` | Runs a `.jsx` inside Illustrator or Photoshop via AppleScript; refuses scripts without `#target` or with shell, network, eval, or include primitives | macOS, the app installed |
| `templates/illustrator/build_brand_master.jsx` | Five artboards, layer architecture, CMYK and spot swatches, `.ai` and `.eps` save | Illustrator |
| `templates/photoshop/update_mockup.jsx` | Smart Object replacement in a PSD mockup, 300 DPI PNG export; refuses linked Smart Objects | Photoshop |

Every script supports `--help`; none needs anything installed. None writes outside the paths you pass it. Nothing sends data anywhere except `figma_sync.py --apply` (api.figma.com) and `design_review_panel.py --run` (the local CLIs). Before every bridge call: print the full `.jsx`, state what it creates or overwrites, and wait for the user to confirm.

## References (read the ones the assignment needs)

| File | Holds |
|---|---|
| `references/design-intelligence.md` | the education corpus and what to extract, the expressive-vs-utility register, generic-AI anti-patterns, typography, motion spec, content rules |
| `references/ux-architecture.md` | the ten questions, User→Goal→Flow→Screen→Component→Action→State→Outcome, navigation selection, scrolling rules, state matrix, wireframe fidelity, responsive rules, data-dense design, decision record, deliverable scaling |
| `references/platform-apple.md`, `platform-android.md`, `platform-web.md` | platform judgment: structure, safe areas and insets, components, type, motion, accessibility, asset specs, implementation mapping |
| `references/design-system-spec.md` | foundations, three token tiers, component spec template, inventory, cross-platform rules, hand-off package |
| `references/brand-identity.md` | strategy, logo system matrix, full identity, derivative asset families, mobile asset specs, brand critique |
| `references/design-review-panel.md` | the three perspectives, routing (subagents, tri-lane lanes, CLIs), synthesis rules |
| `references/critique-and-quality-bar.md` | the critique questions, the ten-row quality bar, definition of done |
| `references/w3c_token_schema.json`, `figma_variables_spec.md`, `adobe_extendscript_api.md` | formats and APIs |

## Pre-Processing (Auto-Context)

Values are injected inline; in an environment that does not execute them, run the commands.

- Design context: !`cat DESIGN.md design/DESIGN.md 2>/dev/null | head -60 || echo "(no DESIGN.md)"`
- Existing assets: !`ls design/ brand/ assets/brand/ public/brand/ tokens.json 2>/dev/null | head -20 || echo "(none)"`
- Stack: !`head -30 package.json 2>/dev/null || head -30 build.gradle.kts 2>/dev/null || head -20 Podfile 2>/dev/null || echo "(none detected)"`
- Portfolio: !`sed -n '1,30p' PORTFOLIO.md 2>/dev/null || echo "(no PORTFOLIO.md)"`
- Recent commits: !`git log --oneline -5 2>/dev/null || echo "(not a git repo)"`

Honour what exists: an existing DESIGN.md, token file, or component library overrides every default below.

## Step 1: Classify the assignment

Write these four lines before any other work.

```
KIND       brand | product | system | asset | review | mixed (list the parts)
REGISTER   expressive | utility   (per surface if mixed; see design-intelligence.md §3)
PLATFORMS  ios | ipados | macos | watchos | visionos | android-phone | android-tablet | foldable | wear | web-desktop | web-mobile
DEPTH      component | screen | flow | product | identity   (sets the deliverable set: ux-architecture.md §10)
```

Input can be an idea, a sketch, a screenshot, a logo, a PRD, an existing app or site, a wireframe, or a design system. Name what was given and what is missing; ask only for what changes the work materially, otherwise state the assumption and proceed.

## Step 2: Gather context

Business goal, user and situation, real content (never lorem when real data exists), constraints (brand, legal, platform, stack), competitors (three, named), and what already exists in the codebase or design files. For an existing product, inventory its screens and states before proposing anything. Write the result as `design/brief.md`; the review panel in Step 8 reads it. All studio output lives under `design/` (or `brand/` for identity work).

## Step 3: Architecture before pixels

For `screen` depth and above, answer the ten questions and build the model chain (`ux-architecture.md` §1 and §2). Choose the navigation model from the table, not from habit. Write the scroll model for every screen: what scrolls, what is fixed, what is sticky, what collapses, what changes after scrolling starts. Produce the state matrix (component and data states) and the responsive transformation rules per size class.

Render the architecture so it can be seen:

```bash
python3 "$STUDIO/scripts/wireframe.py" --example > design/spec.json   # edit: screens, regions, fixed/sticky, notes, flows
python3 "$STUDIO/scripts/wireframe.py" --spec design/spec.json --out design/wireframes --fidelity low
```

Low fidelity settles structure; mid fidelity settles components and labels; neither is the final design.

## Step 4: Concept and creative direction

Pick the register and defend it in one paragraph. Extract principles from the corpus (`design-intelligence.md` §2), never a layout. Set typography first (scale, roles, measure), then colour (60-30-10, ratios recorded, light and dark from the same ramps), then motion (specified per moment). Check the concept against the anti-pattern list; every visual decision has a written reason. For brand work follow `brand-identity.md`: strategy, then a logo *system*, then the full identity.

## Step 5: Design for each platform

Shared brand, native interaction. Read the platform file for every target and design the platform's structure (tab bar vs navigation bar vs sidebar; sheets vs bottom sheets vs drawers; safe areas and insets; type scaling). Never skin one layout across platforms and never let platforms drift from the brand without a decision record entry. For component-level specs and code, invoke `ios-design-expert`, `android-design-expert`, or `web-design-expert`; the studio owns the judgment, they own the implementation detail.

Design every state. Empty and error states are designed screens with a next step. Test every screen with long, short, missing, zero, and many.

## Step 6: Systemise

Write `design/tokens.json` in W3C format with primitive, semantic, and component tiers (`references/w3c_token_schema.json` is the starter); specify components with the template in `design-system-spec.md` §3; state the cross-platform mapping. Verify:

```bash
python3 "$STUDIO/scripts/tokens_lint.py" --tokens design/tokens.json --modes light,dark
python3 "$STUDIO/scripts/contrast_check.py" --tokens design/tokens.json     # pairs by convention, per mode
```

For Storybook, Showkase, SwiftUI catalogues, and governance, hand the tokens and component specs to `design-system`.

## Step 7: Produce the work

Visual output over description. If asked for a dashboard, deliver the dashboard: wireframes from Step 3, high-fidelity screens as HTML (web) or platform specs with the state matrix, SVG marks and lockups for brand work, and the asset families the project needs without waiting to be asked (`brand-identity.md` §4).

```bash
python3 "$STUDIO/scripts/export_asset_matrix.py" --svg master_logo.svg --output-dir dist/brand_assets --brand-name "Brand" --platforms web,ios,android --icon-bg 0F172A
```

Illustrator (`.ai`, print, spot colour) and Photoshop (mockups) via the templates and the bridge, after user confirmation. Figma: validate, then `--apply` once the user confirms the file. Say plainly which outputs were produced and which were skipped for a missing tool.

## Step 8: Three-perspective review (substantive work)

Applies at `flow`, `product`, and `identity` depth. Creative Director, Product/UX Director, Design Systems/Production Director review the artefacts; they disagree constructively and do not vote (`design-review-panel.md`).

```bash
python3 "$STUDIO/scripts/design_review_panel.py" --brief design/brief.md --artifacts "design/**/*.md" "design/**/*.json" "design/**/*.html" --out design/review --emit
```

In Claude Code run the three prompts as parallel subagents; with `cure-tri-lane` installed send the UX prompt to `codex-reviewer` and the systems prompt to `antigravity-analyst` so each verdict comes from a different model family; in a terminal with the CLIs, add `--run`. Label every finding Confirmed, Disputed, or Unverified; decide conflicts by the register and the ten questions; fold the strongest ideas into one direction. One panel per deliverable.

## Step 9: Critique gate

Run the critique in `critique-and-quality-bar.md` (UX, visual, platform, accessibility, product, brand, content, states) and the ten-row quality bar. Fix what fails before delivery. Nothing ships because it is polished; it ships because every row holds.

## Step 10: Deliver

One folder, scaled to `DEPTH`: the classification and ten-question answers, the decision record (only decisions whose reasoning changes UX or implementation), the architecture (inventory, flows, wireframes, scroll model), the designs with state matrices and responsive rules, tokens and component specs, motion spec, the produced assets, the review synthesis, implementation notes with expensive items flagged and a cheaper fallback, and a limitations list naming what was not done and why.

## When NOT to use this skill

- CSS, Compose, or SwiftUI implementation alone: `web-design-expert`, `android-design-expert`, `ios-design-expert`.
- Storybook, Showkase, SwiftUI catalogues, governance: `design-system`.
- UI generation through Stitch: `stitch-design`.
- Charts and data visualisation marks: `dataviz`.

## Limitations

- `export_asset_matrix.py` needs an SVG renderer with alpha (`rsvg-convert`, Inkscape, ImageMagick, or Chrome); with only macOS Quick Look it produces opaque assets and reports the transparent ones as failures. The Adobe bridge needs macOS.
- Android monochrome layers and notification glyphs are authored as single-colour SVGs (`brand/logo/android-monochrome.svg`, `brand/logo/notification-icon.svg`), not derived.
- `figma_sync.py --apply` creates a new collection each run; delete the previous one before re-publishing.
- The studio judges against the corpus from memory; it cannot browse award sites at run time unless a web tool is available.
