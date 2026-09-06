# Design Intelligence: the corpus, the register, and what to refuse

Read this before concept work. It is judgment, not a style library.

## 1. The bar

Every deliverable is measured against one question: **could this plausibly have shipped from a top-tier product design team or an award-winning digital studio?** "Clean AI UI" fails that test. Distinctive, appropriate, and behaviourally complete passes it.

## 2. The education corpus

Study the principles behind work recognised in roughly the last five years by: Webby Awards, Awwwards, CSS Design Awards, Red Dot, iF Design, Apple Design Awards, Google Play editorial and design awards, Fast Company Innovation by Design, Communication Arts, D&AD.

Studios and teams whose public work is worth dissecting: Active Theory, Immersive Garden, BASIC/DEPT, AREA 17, Pentagram, Huge, Merci-Michel, Obys, Unseen Studio, Noomo, MONOGRID, Fabrique, Q42, Refokus, 14islands, Lusion, Buttermax, ET Studio, AWD Agency; and the internal teams at Apple, Google, Spotify, Airbnb, Stripe, Linear, Dropbox, Cash App.

What to extract from any reference, in this order:

| Lens | Question to answer about the reference |
|---|---|
| Composition | Where is the weight, and what is deliberately empty? |
| Typography | How many sizes carry the whole hierarchy? (Usually 4 to 6.) |
| Editorial hierarchy | What do you read first, second, third, and why? |
| Grid | What is the column logic, and where does it break on purpose? |
| Density | How much information per viewport, and how is it made scannable? |
| Motion | What moves, why, for how long, and what stays still? |
| Transitions | How does the user keep orientation between states? |
| Navigation | How many top-level destinations, and how are they revealed? |
| Responsive transformation | What changes between breakpoints beyond width? |
| Micro-interactions | Which feedback moments exist, and which are missing? |
| Brand expression | Which three details could only belong to this brand? |

Never reproduce a studio's layout, palette, type pairing, or motion signature. Extract the principle, then design something original for this project. If a reader could name the reference from your output, start over.

## 3. Choose the register before designing anything

Two registers. The assignment decides; the assignment never gets both by default.

| | Expressive (marketing, launch, editorial, portfolio, campaign) | Utility (banking, recruiting, medical, enterprise, admin, mobile tools) |
|---|---|---|
| Goal | Feel, remember, share | Finish the task fast and correctly |
| Layout | Unconventional grids, horizontal chapters, oversized type allowed | Familiar structure, predictable controls, dense but readable |
| Motion | Scroll choreography, cinematic transitions, WebGL and 3D when they carry the story | Feedback and orientation only; 150 to 300 ms; nothing decorative |
| Navigation | May be unusual if discoverable within 3 seconds | Platform-standard; zero learning cost |
| Novelty budget | One signature idea, executed completely | None unless it removes a step |
| Failure mode | Looks like a template | Looks like a marketing site pretending to be software |

Mixed products (a SaaS with a marketing site) get one register per surface, with shared brand foundations. Say which register each surface is in, in the decision record.

**Innovation must have a reason.** Write the reason next to the idea. If the reason is "it looks impressive," delete the idea.

## 4. Generic-AI anti-patterns (hard refusals)

Any of these without a written justification is a defect, not a style:

- gradients as default surface treatment; glow or blur as decoration
- every element inside a card; cards inside cards; giant radii on everything
- glassmorphism on content surfaces
- the purple-to-blue SaaS palette; a lone acid accent on near-black
- dashboards with charts that answer no question
- pills and chips for plain labels
- icons that add no meaning (an icon beside every heading)
- hero sections that fill a viewport and say nothing
- whitespace used to hide the absence of hierarchy
- the same layout for a hospital, a bank, and a skate brand
- Inter or Space Grotesk as the unexamined default; emoji as section markers
- everything centred

Replacement rule: hierarchy from typography and spacing first; containers only where an object is genuinely separate; colour for meaning before decoration.

## 5. Typography is the primary system

Set the type before the colour. A page whose hierarchy survives in one colour is correctly structured.

- Scale: choose 5 to 7 steps with a stated ratio (1.2 to 1.333 for product, larger for editorial); name them by role (display, h1, h2, body, label, caption), never by pixel.
- Measure: 45 to 75 characters for body copy; tables and labels are exempt.
- Line height: 1.4 to 1.6 body; 1.05 to 1.2 display; tighter tracking as size grows.
- Numbers: `font-variant-numeric: tabular-nums` (and monospaced digits on iOS and Android) wherever digits align in columns.
- Variable fonts where weight axes are actually used; otherwise ship 2 to 3 static weights.
- Fallback stack declared for every face; test the fallback rendering once.
- Localisation: allow 30 to 40 percent text expansion (German, Finnish) and check CJK line height and fallback.
- Dynamic Type (Apple), font scale (Android), and browser zoom to 200 percent must not break layout; that is a layout constraint, not an accessibility afterthought.

## 6. Motion has a specification or it does not ship

Motion exists for orientation, feedback, hierarchy, continuity, state change, storytelling, and (in the expressive register only) delight. For every motion moment record:

```
MOTION   <name>            e.g. sheet-present
TRIGGER  <user or system event>
DURATION <ms>              utility: 150-300; expressive: up to 800; never above 1200 for anything blocking
EASING   <curve or physics> e.g. spring(damping 0.85) | cubic-bezier(0.2, 0, 0, 1)
ELEMENTS <what moves, what stays still>
REDUCED  <behaviour under prefers-reduced-motion / Reduce Motion>: cross-fade or instant, never "same"
```

Shared-element transitions where the user follows one object between screens; entrance and exit choreography for lists (stagger 20 to 40 ms, cap at 8 items); drag, swipe, reorder with real physics; scroll-linked effects only in the expressive register and only when they reveal, never when they delay.

## 7. Content is part of the design

Never design with lorem ipsum when real or realistic content exists. Realistic content finds the defects. Before calling a screen done, run it with: a 42-character name and a 3-character name; a 7-digit currency figure and a zero; a missing avatar; a status you did not plan for; two paragraphs where you expected one line; zero, one, and 400 records.
