# Brand Identity Studio: strategy, logo systems, asset families, platform assets

## 1. Strategy before form

Write these down first; every visual choice traces back to them.

- Positioning: who it is for, what it replaces, why it wins, in three sentences.
- Archetype (one primary, one shadow): Creator, Sage, Ruler, Outlaw, Magician, Hero, Everyman, Explorer, Caregiver, Jester, Lover, Innocent.
- Tone axes with a point on each: modern-heritage, playful-serious, minimal-rich, warm-cool, loud-quiet.
- Three words the brand owns; three words it refuses.
- Naming support when asked: 20 candidates across descriptive, evocative, invented, and compound; screen for pronounceability, domain, trademark class conflicts (flag for `legal-compliance`), and meaning in the top five markets.
- Creative direction: a written art direction (subject, light, colour, crop, mood) and a moodboard description with 6 to 9 references named by principle, never to be copied.

## 2. Logo system (never a single logo)

| Asset | Requirement |
|---|---|
| Primary logo | the full lockup as it appears most often |
| Secondary logo | the alternative arrangement (horizontal or stacked, whichever primary is not) |
| Horizontal lockup | mark left, wordmark right; 3:1 to 4:1 |
| Vertical lockup | mark above wordmark; 1:1 to 4:5 |
| Icon or symbol | mark alone; 1:1; must read at 16 px |
| Monogram or wordmark | the letterform-only version for tight spaces |
| Monochrome | one colour, positive |
| Reverse | for dark and photographic backgrounds |
| Small-size version | simplified geometry below about 24 px; fewer counters, thicker strokes |
| Favicon and app-icon interpretation | the mark re-drawn for a square mask, not shrunk |
| Safe space | one x-height or one mark height on all sides, stated as a rule |
| Minimum size | stated in px and mm |
| Misuse examples | six: stretched, recoloured, on busy imagery, rotated, with effects, wrong lockup |

Vector rules: semantic SVG, `viewBox` only, outlined type, minimal anchors, no raster, optical centring checked. Illustrator and Figma hand-off per SKILL.md Steps.

## 3. The full identity

Iconography (grid, stroke weight, corner radius, size ramp), typography (display, text, and utility faces with licensing noted), colour system (60-30-10 with contrast ratios recorded; light and dark), photographic direction, illustration system (style, line, fill, characters or not), pattern and texture derived from the mark, layout principles (grid, margins, alignment rules), motion identity (how the mark animates, the signature easing, a 1-second and a 3-second version), voice and tone (with three rewritten examples), applications (business card, deck, email signature, social, signage, merchandise as relevant).

A logo is not the brand. Deliver a system.

## 4. Derivative asset families (produce proactively)

When an identity is created, determine which of these the project needs and produce them without waiting to be asked:

Web: favicons, SVG icon, manifest icons, OpenGraph, social headers and avatars, email header, 404 and empty-state illustrations.
Marketing: social templates (square, portrait, story), presentation template (title, section, content, closing), ad formats (300x250, 728x90, 1080x1080, 1080x1920), launch graphics, badges.
Product: app icons (all platforms), splash and launch, onboarding illustrations, empty-state illustrations, notification icon, widget mark, store listing graphics.
Print: business card, letterhead, one-pager, signage lockup.

State which were produced and which were skipped with the reason.

## 5. Mobile platform asset specifications

| Platform | Asset | Spec |
|---|---|---|
| iOS | app icon | 1024 x 1024 PNG, opaque, square corners (system masks); dark and tinted variants; alternate icons optional |
| iOS | launch | static launch screen matching first-screen chrome |
| iOS | App Store | screenshots per device family; first three carry the story |
| iOS | widgets and Live Activities | mark at 24 to 40 pt; type roles from the system |
| Android | adaptive icon | 108 dp canvas; foreground mark inside 66 dp safe zone; background layer fills; monochrome alpha layer |
| Android | legacy launcher | 48 dp at mdpi, hdpi, xhdpi, xxhdpi, xxxhdpi (48, 72, 96, 144, 192 px) |
| Android | notification icon | 24 dp, white alpha-only glyph |
| Android | splash | system splash API; icon centred on brand colour |
| Android | Play Store | 512 x 512 icon; 1024 x 500 feature graphic; screenshots per form factor |
| Both | maskable web icon | 512 with content inside the inner 80 percent |

`export_asset_matrix.py --platforms ios,android,web` produces the raster sets from the master SVG, with safe zones respected, and verifies transparency. Author these by hand, next to the logo files:

| File | Canvas | Rule |
|---|---|---|
| `brand/logo/android-monochrome.svg` | `viewBox 0 0 108 108`, glyph inside the centred 66 circle | one fill colour, no strokes, no gradients; the system recolours it |
| `brand/logo/notification-icon.svg` | `viewBox 0 0 24 24`, 2 px padding | white (`#FFFFFF`) only; alpha carries the shape |
| `brand/logo/app-icon.svg` | `viewBox 0 0 1024 1024`, opaque background | the mark re-drawn for the square mask, not shrunk |
| `brand/logo/app-icon-dark.svg` | same | iOS dark and tinted variants when the mark needs it |

## 6. Brand critique

Before delivery: recognisable at 16 px and 16 m; distinct from the three closest competitors (name them); survives monochrome, reverse, and a busy photograph; type and mark share a logic; the palette passes `contrast_check.py`; the motion identity works under Reduce Motion; nothing in it could be mistaken for a template.
