# Product Design

**Lane.** This is the lightweight lane: one screen or component spec, or a guideline review of UI that
already exists. Anything larger — a new product or flow, brand, design system, tokens, production
assets — belongs to design-studio, the library's default design skill. If the request grows past one
screen or needs new tokens, say so and hand off rather than expanding here.

**Outcome:** an implementation-ready spec (or review findings) a developer can build from without a
designer in the room. Done when every state is specified and every a11y requirement is testable.
Match length to the need; no filler sections or restated summaries.

## Pre-Processing (Auto-Context)

Context (pre-filled in Claude Code; in other runtimes run these commands first):

- Design files: !`ls DESIGN.md design/DESIGN.md design/tokens.json tokens.json 2>/dev/null | head -4 | grep . || echo "(no DESIGN.md or tokens)"`
- Platforms present: !`ls package.json build.gradle.kts Podfile Package.swift 2>/dev/null | head -4 | grep . || echo "(none detected)"`

Use existing tokens and component names from the listed files; never invent a parallel token set.

## Step 1: Classify

| Request | Deliver |
|---|---|
| Component spec | Step 3 component spec |
| Screen spec | Step 3 screen spec |
| Review / audit of existing UI | Findings: every issue with severity, guideline cited, fix |
| Anything larger (flow, product, brand, system, tokens) | Hand off to design-studio |

## Step 2: Gather Context

Platform(s), the screen or component, existing tokens/components, brand constraints, and the handoff
target (SwiftUI / Compose / web). Ask only for what is missing.

Platform choice: native iOS → HIG only; native Android → M3 only; React Native / Flutter →
platform-adaptive (HIG on iOS, M3 on Android); web, PWA, Capacitor/Ionic → web patterns, no imitation
of native chrome. For platform detail invoke ios-design-expert, android-design-expert, or
web-design-expert.

## Step 3: Spec Contents

**Component spec:** anatomy (named parts); states (default, pressed/hover, focused, disabled, loading,
error); variants and sizes; spacing using existing tokens; a11y (role, accessible name, keyboard and
focus behavior); motion (entry, exit, state change, reduced-motion fallback); token names for handoff;
Figma variant property names if a Figma library exists.

**Screen spec:** regions and components; every state (skeleton, empty, success, error, partial);
navigation (entry, exit, back behavior); responsive / size-class behavior; screen-reader reading order.

## Step 4: Accessibility Floor (WCAG 2.2 AA)

- Contrast: text 4.5:1, large text (≥18pt, or ≥14pt bold) 3:1, focus indicators and UI parts 3:1.
- Targets: iOS 44×44pt, Android 48×48dp. Web: 24×24 CSS px is the AA minimum (2.5.8); Cure's default is 44×44px (the AAA 2.5.5 size) for primary actions.
- Honor reduced motion; never use color alone to convey meaning; every interactive element has an accessible name.

For a full WCAG audit, use accessibility-audit.

## Step 5: Artifact Generation

Applies only when the user asks for a file. Write the spec to `docs/design/{screen-or-component}.md`
(review findings to `docs/design/{name}-review.md`). One file; don't generate token or inventory docs —
those are design-studio outputs.
