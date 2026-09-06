# UX Architecture: the model, navigation, scrolling, states, wireframes

Nothing visual starts until this file's questions are answered for the assignment. Scale the depth to the project: a single component needs the state matrix and nothing else; a product needs all of it.

## 1. The ten questions

1. Who is using this, and in what situation (device, posture, attention, frequency)?
2. What are they trying to accomplish, in their words?
3. What information do they need to decide or act?
4. What single action has the highest priority on this screen?
5. What must they see first?
6. What is secondary?
7. What stays hidden until needed (progressive disclosure)?
8. Which navigation model fits (see section 2)?
9. What happens next, and how do they know it worked?
10. What happens when it fails, and how do they recover?

Write the answers down. They become the first section of the deliverable and the source of every decision record.

## 2. The model chain

For any product larger than a screen, build and keep this chain:

```
User -> Goal -> Flow -> Screen -> Component -> Action -> State -> Outcome
```

Deliverables that make it concrete: a screen inventory (id, name, purpose, entry points, exits), a navigation model, a sitemap or information architecture, user flows for the top 3 to 5 goals, and a state matrix per meaningful screen. `wireframe.py` renders the screen inventory and flows from one JSON file.

### Navigation model selection

| Destinations | Frequency of cross-navigation | Model |
|---|---|---|
| 2 to 5 top-level, all used often | high | tabs (iOS), navigation bar (Android), top nav or compact sidebar (web) |
| 5 to 9 work areas | high | sidebar (web, iPad, Android tablet rail or pane) |
| many areas, used rarely | low | drawer or menu; search as primary navigation |
| linear task | n/a | stepper or full-screen flow with explicit progress |
| single object with facets | medium | segmented control or tabs inside the object |

A hamburger menu on a product with fewer than five destinations is a defect. A bottom tab bar with more than five is a defect.

## 3. Scrolling and viewport: design the behaviour

For every screen answer, in writing: what scrolls, what stays fixed, what becomes sticky, what collapses, what disappears, what changes once scrolling starts, and where the user learns that more content exists.

Rules:
- Vertical scrolling for long-form content; no nested same-direction scrolling unless a container is a genuinely independent region (a chat pane beside a document).
- Horizontal scrolling only for peer content (carousels, media, categories), with a visible affordance (peeking item, fade, or dots). Never horizontal scroll for primary controls.
- Sticky calls to action only when persistent access materially shortens the task (checkout, compose, save in a long form). Otherwise the action lives at the natural end.
- Headers collapse when viewport space is worth more than context; keep title or breadcrumb visible during multi-step work.
- Keyboard appearance on mobile reduces the viewport by roughly 40 percent: the focused field and its primary action stay visible.
- Safe areas: the home indicator, Dynamic Island, notches and display cutouts, and Android system bars are part of the layout, not overlays to work around later.
- Sheets and modals with overflowing content scroll inside the sheet, with the primary action fixed at the bottom and a visible top edge.
- Scroll restoration on back navigation; pull-to-refresh on feeds and lists where the platform expects it (iOS and Android lists; never on web forms).
- Pagination when the user needs to locate and return to a position (tables, search results); infinite scroll only for consumption feeds, and then with a footer route to the end.

## 4. Design every state

Meaningful components and screens ship with a state matrix. Omit a state only by writing "n/a" with a reason.

Component states: default, hover (pointer only), focused (visible ring, 3:1 contrast), pressed, selected, disabled, loading, skeleton, empty, success, warning, error, offline, no permission, partially populated, first-time user, returning user, long content, short content, missing image, invalid input, destructive confirmation.

Data states: zero records, one record, hundreds of records, extremely long names, missing values, stale data (show age), failed request (retry path), partial load.

Empty and error states are designed screens with a next step, not a grey icon and "No data."

## 5. Wireframe fidelity

| Fidelity | Shows | Hides | Use when |
|---|---|---|---|
| Low | structure, hierarchy, flows, content placement, navigation, primary interactions | colour, type choice, imagery | architecture decisions; stakeholder alignment on scope |
| Mid | real component structure, meaningful labels, spacing, states, interaction notes | final visual language | usability of the flow; engineering estimation |
| High | final typography, colour, imagery, components, motion notes, all states, platform conventions | nothing | build-ready hand-off |

Wireframes never travel alone. Attach, as the project warrants: sitemap, information architecture, user flows, screen inventory, navigation model, screen relationships, annotations, and edge cases. `wireframe.py` produces low and mid fidelity SVGs plus a flow diagram from one spec; high fidelity is authored as HTML (web), or as platform-specific specs, with the state matrix attached.

## 6. Responsive transformation is written, not implied

For every major layout, state the rule per size class. Example for a work tool:

```
Desktop (>= 1200)  persistent sidebar (240), multi-column content, expanded data tables, hover affordances
Tablet  (768-1199) collapsible sidebar or rail (72), two columns, secondary information demoted to detail view
Mobile  (< 768)    single column, top-level navigation as tabs, tables become list rows with the 2-3 decisive fields,
                   filters move into a sheet, bulk actions into a selection mode
```

"Make it responsive" is not a specification. A desktop page scaled down is not a mobile design.

## 7. Data-dense products

Dashboards, analytics, recruiting, finance, SaaS, CRM, operations, admin. Density is not the enemy; undifferentiated density is.

- Table when the user compares rows across the same fields; list when each row is an object with one decisive field; cards only when the image or shape of the object matters.
- Master-detail for object-centred work; side panel for quick edits that must not lose the list context; full page for anything with more than roughly 8 fields.
- Filters and facets left or top, persistent on desktop, in a sheet on mobile; sort visible in the header; search is a first-class citizen above 50 rows.
- Bulk actions appear on selection, in a bar that replaces the header, never as a permanent toolbar.
- Charts answer a stated question; every chart carries that question as its title. See the `dataviz` skill for mark specs.
- One number per tile only when the number is the point; otherwise put it in the table.

## 8. Decision record

Record decisions whose reasoning changes implementation or UX. Skip the obvious.

```
Decision: Bottom navigation on mobile
Reason:   Four persistent top-level destinations used throughout the session; discoverable without a gesture.

Decision: Horizontal carousel for "similar roles"
Reason:   Items are peer content, discovery is desirable, and the vertical hierarchy must stay uninterrupted.

Decision: Sidebar on desktop
Reason:   Seven persistent work areas and frequent cross-navigation.
```

## 9. Implementation awareness

Design intentionally about cost. Flag, in the hand-off, anything that requires WebGL or shaders, custom gesture engines, complex canvas rendering, advanced animation frameworks, or custom graphics pipelines, with an alternative that costs a tenth as much. Map components to the target stack (SwiftUI or UIKit, Jetpack Compose or Views, React or Next.js and CSS) so an engineer can estimate from the design. Engineering cost never dictates the concept; it informs the choice of how far to push it.

## 10. Deliverables scale with the assignment

| Assignment | Minimum set | Full set |
|---|---|---|
| Single component | anatomy, states, tokens used | plus variants, platform differences, motion |
| One screen | ten questions (short), scroll model, state matrix, the screen | plus responsive rules, decision record |
| Flow or feature | flows, screen inventory, wireframes, states | plus high fidelity, prototype notes, hand-off |
| Product | IA, navigation model, flows, inventory, wireframes, system foundations, states, hand-off | plus tokens, component library, motion spec, asset families |
| Brand | strategy, logo system, type, palette, guidelines, brand critique | plus imagery and illustration direction, motion identity, asset library, review panel |
| Design system | foundations, tokens, core components with states | plus platform variants, usage guidance, governance (see `design-system`) |

Do not bury a small request under documentation. Do not ship a product without its architecture.
