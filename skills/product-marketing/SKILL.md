---
name: product-marketing
description: "Product voice and content marketing expert — generates platform-native content packages across Instagram, YouTube, LinkedIn, and X/Twitter for portfolio brands"
argument-hint: "[product-name] [platform-or-campaign]"
---

# Product Marketing

Product voice and content marketing engine. Generates platform-native content packages rooted in each product's ICP, tone of voice, and target demographic — not generic marketing copy.

**Every invocation is scoped to a single product.** Multi-language/multi-market products produce market-specific variants in the appropriate language.

## Pre-Processing (Auto-Context)

Before starting, gather project context silently:
- Read `PORTFOLIO.md` if it exists in the project root or parent directories for product/team context
- Run: `cat package.json 2>/dev/null || cat build.gradle.kts 2>/dev/null || cat Podfile 2>/dev/null` to detect stack
- Run: `git log --oneline -5 2>/dev/null` for recent changes
- Use this context to identify the product, its ICP, and target platforms

## Operating Principles

1. **Product-first, demographics-driven** — every piece of content is rooted in the specific product's ICP, not generic best practices
2. **Research before messaging** — never write copy before understanding the ICP. If no market research exists, suggest running `/market-research` first
3. **One core message** — if everything is emphasized, nothing is
4. **Audience-native voice** — write in the language your buyer actually uses, not product language
5. **Proof over claims** — specifics beat adjectives ("47% faster" > "blazing fast")
6. **Platform-native** — every piece is built for the platform it lives on, not repurposed from another
7. **Full package per run** — every invocation outputs hook, caption/copy, CTA, hashtags, and visual direction

## Integration with Market Research

This skill consumes outputs from the **market-research** skill.

When market research exists, extract before generating:
```
From market research:
  → ICP definition → drives persona narratives and copy voice
  → Competitive differentiation → drives positioning and messaging
  → ICP pain points → drives headline hooks and benefit framing
  → ICP trigger events → drives campaign timing and channel selection
  → Pricing analysis → drives value proposition framing
  → GTM channels → drives channel strategy and content format
```

---

## Step 1: Classify the Request

| Request | Output |
|---------|--------|
| Content package (single platform) | Full content package for one platform |
| Content package (multi-platform) | Platform-native packages for each requested platform |
| Campaign (launch / awareness / conversion) | Multi-platform campaign with sequencing and cadence |
| Brand foundation | Message House + voice guide + brand strategy |
| Copy (ads, landing, email) | Campaign-ready copy with variants |
| Content calendar | Weekly/monthly content plan with themes |
| Press / PR | Press release + media kit |
| ASO / SEO | App store and search optimization |

## Step 2: Identify the Product

Match the user's request to a product in the registry. If the product is not listed, gather the equivalent context before generating.

---

## Product Registry

### Vendly
```
What:               Merchant OS for informal vendors and small business operators
Markets:            Dominican Republic, Colombia, Mexico, Brazil, US Latino diaspora
ICP:                Street vendors, market stall operators, small shop owners
                    Aged 25–45, low to moderate tech literacy, mobile-first
Tone:               Warm, empowering, community-rooted. Speaks to dignity of the hustle.
                    Never condescending. Never startup-bro.
Languages:          Spanish (DR/Colombia/Mexico variants), Portuguese (Brazil),
                    English (US Latino)
Core message:       Run your business like a real business
Key differentiators: Built for the informal economy, QR-native payments
                    (PIX, CoDi, Nequi), no bank account required
Personality:        Empowering, practical, entrepreneurial, warm
Visual direction:   Warm tones, real vendors in real markets, mobile screens
                    in-context, no stock photography. Latinx street markets,
                    colmados, ferias, mercados.
```

### Autograph
```
What:               AI medical scribe platform for physicians
ICP:                Attending physicians, hospitalists, outpatient PCPs
                    Aged 30–55, time-starved, EHR-fatigued
Tone:               Clinical credibility, clean, efficient. Peer-to-peer.
                    Not startup-bro. Not consumer tech.
Language:           English only
Core message:       Your AI scribe. Documentation, done.
Key differentiators: Real-time ambient documentation, reduces charting time,
                    built by people who understand clinical workflow
Personality:        Precise, trustworthy, clinical, efficient
Visual direction:   Clean white/blue palette, physician in workflow (not
                    posing), subtle tech overlay. No stock stethoscopes.
                    Show the screen, show the note, show the saved time.
```

### The Initiated
```
What:               NCAA-approved women's basketball recruiting intelligence
                    platform + scouting service
ICP (B2B):          D1/D2/D3 college coaches, club program directors
ICP (B2C):          Elite HS athletes (classes 2026–2031) and their parents
Tone:               Authoritative scouting voice. Data-driven but with culture.
                    Respects the grind of the female athlete.
Language:           English only
Core message:       Find the players others miss.
Key differentiators: NCAA-approved, coach-facing intelligence tools, athlete
                    exposure infrastructure, event access
Personality:        Authoritative, insider, data-forward, champion of women's game
Visual direction:   Game action, scouting film stills, data overlays on
                    player footage. Purple/gold brand palette. Show the work
                    — film sessions, coaching huddles, athlete highlight clips.
```

### Antigravity
```
What:               AI agent orchestration framework for developers
ICP:                Senior engineers, technical founders, AI-native dev teams
Tone:               Technical, direct, no fluff. Builder-to-builder.
                    Respects engineering rigor.
Language:           English only
Core message:       Ship with agents. Not prompts.
Key differentiators: Skill-based architecture, multi-agent coordination,
                    production-grade patterns, VS Code-native
Personality:        Elite, precise, builder-minded, no-nonsense
Visual direction:   Dark mode UI, code snippets, terminal output, architecture
                    diagrams. No stock illustrations. Show the tool in use.
```

### TwntyHoops
```
What:               Basketball media and events brand
ICP:                Hoopers, basketball culture fans, event attendees,
                    sneakerheads aged 16–30
Tone:               Culture-forward, hype but authentic. Hip-hop adjacent.
                    Not corporate. AAVE-aware, culture-aware.
Language:           English (AAVE-aware, culture-aware)
Core message:       Where the next generation plays.
Key differentiators: Grassroots credibility, event access, media coverage
                    of underexposed talent
Personality:        Energetic, authentic, community-first, bold
Visual direction:   Game highlights, crowd energy, sneaker details, court
                    textures. High contrast, bold typography. Show the
                    culture — not just the game.
```

### Cure Consulting Group
```
What:               Technical AI + mobile consultancy
ICP:                Series A+ startups, mid-market engineering orgs,
                    CTOs and VPs of Engineering
Tone:               Peer-level (engineer to engineer), confident,
                    results-oriented. Not salesy.
Language:           English only
Core message:       We build the systems that scale your product.
Key differentiators: Full-stack product engineering (Android/iOS/Web/Firebase),
                    AI integration, 58-skill standardized delivery framework
Personality:        Elite, precise, builder-minded, no-nonsense
Visual direction:   Clean, minimal. Code-in-context, architecture diagrams,
                    product screenshots. Dark backgrounds, monospace type.
```

---

## Step 3: Platform Specifications

Every piece of content must follow these platform rules. Do not deviate.

### Instagram Reels
```
Format:             Vertical video (9:16)
Duration:           7–15 seconds optimal, 30s max
Hook:               Must land in first 1.5 seconds — text overlay + motion
Text overlay:       Critical — 60%+ of viewers watch without sound
Caption:            125 chars above fold, full CTA below fold
Hashtags:           15–20, mix of broad + niche, in first comment (not caption)
CTA:                In caption, never in video (IG punishes video CTAs)
Music/audio:        Trending audio when relevant, original audio for authority
```

### Instagram Static / Carousel
```
Format:             1080×1080 (square) or 1080×1350 (portrait, preferred)
Carousel:           Up to 10 slides. First slide = stop-the-scroll hook
                    Optimized for saves, not just likes
Design rules:       Bold headline on slide 1, one idea per slide,
                    CTA on last slide, consistent brand typography
Caption:            Long-form okay (up to 2200 chars), storytelling format
Hashtags:           15–20, first comment
Alt text:           Required for every image — describe content, not brand
```

### YouTube Long-form
```
Duration:           8–12 minutes sweet spot (watch time algorithm)
Title:              SEO-optimized, benefit-first, under 60 chars
                    Format: "[Outcome] — [How/What] | [Brand]"
Description:        First 2 lines = hook (visible before "Show more")
                    Include chapters with timestamps
                    Keywords naturally placed, not stuffed
Thumbnail:          Text overlay (3–5 words max), face when possible,
                    high contrast, readable at mobile size
Chapters:           Required. Minimum 4 chapters with descriptive names.
Tags:               10–15 relevant tags
End screen:         Subscribe + next video prompt in last 20 seconds
```

### YouTube Shorts
```
Format:             Vertical (9:16), under 60 seconds
Hook:               First 3 seconds must stop the scroll
Text overlay:       Critical — same as Reels logic
No external links:  Description links don't work on Shorts
CTA:                "Follow for more" or "Watch the full video" (channel CTA)
Cross-post:         Can repurpose Reels if aspect ratio matches
                    Re-upload natively — don't share IG links
```

### LinkedIn
```
Tone:               B2B, professional but not corporate. Storytelling > features.
Format:             Text post (1300 char ideal, 3000 max)
                    Document/PDF carousel for tactical content
                    Video: square or vertical, 1–3 min
Structure:          Hook line → story/insight → takeaway → engagement question
Hashtags:           3–5 maximum. No hashtag walls. Relevant only.
Posting cadence:    2–3x per week max. Quality > quantity.
Engagement:         End with a question. Reply to every comment within 2 hours.
Do NOT:             Use engagement bait ("Agree?"), emoji spam, or
                    repost IG content without reformatting
```

### X / Twitter
```
Format:             280 chars per tweet, threads for depth
Hook tweet:         Carries all the weight — must stop the scroll alone
Thread structure:   Hook → context → proof points → CTA
                    Number tweets (1/7, 2/7...) for threads
Links:              Never in the first tweet (kills reach). Link in reply
                    or final tweet.
Hashtags:           0–2 maximum. Only if genuinely trending/relevant.
Visuals:            Single image or video boosts reach. No multi-image
                    unless gallery format adds value.
Tone:               Sharp, direct, quotable. Slightly more casual than LinkedIn.
                    Product-specific tone still applies.
```

---

## Step 4: The Message House

Every product gets a Message House before any copy is written. If generating content for a product already in the registry, the Message House is pre-built.

```
┌─────────────────────────────────────────────┐
│           BRAND PROMISE (Roof)              │
│   The single most important thing we stand  │
│   for. Emotional. Memorable. Defensible.    │
└─────────────────────────────────────────────┘
         │              │              │
┌────────┴───┐  ┌───────┴────┐  ┌─────┴──────┐
│  PILLAR 1  │  │  PILLAR 2  │  │  PILLAR 3  │
│ (Benefit)  │  │ (Benefit)  │  │ (Benefit)  │
│            │  │            │  │            │
│ Proof pt 1 │  │ Proof pt 1 │  │ Proof pt 1 │
│ Proof pt 2 │  │ Proof pt 2 │  │ Proof pt 2 │
└────────────┘  └────────────┘  └────────────┘
┌─────────────────────────────────────────────┐
│              FOUNDATION                     │
│  ICP pain point + trigger event + RTB       │
│  (Reason To Believe — credibility anchor)   │
└─────────────────────────────────────────────┘
```

---

## Step 5: Copy Quality Standards

**Headlines / Hooks:**
- Lead with the outcome, not the feature
- Use the customer's exact language
- Specificity > superlatives ("3x faster" > "The fastest")
- Every headline must pass the "So what?" test
- For video: the hook IS the first 1.5–3 seconds. Text + motion + audio.

**Body copy / Captions:**
- First sentence must earn the second
- Short paragraphs (2-3 lines max for digital)
- Active voice, present tense
- Benefit first, feature second
- One CTA per message — never two asks
- Platform-appropriate length (don't write a LinkedIn essay for X)

**CTAs:**
- Action verb + specific outcome ("Start finding players" > "Sign Up")
- First-person framing when possible ("Start my free trial" > "Start your free trial")
- Remove friction words ("No credit card required")
- Platform-appropriate (IG: "Link in bio", LinkedIn: "DM me", X: "Reply with...")

**Email subject lines:**
- Under 50 characters (mobile preview)
- Personalization token where possible
- Curiosity gap OR specific benefit — never vague
- A/B test every launch email subject

---

## Step 6: Generate Content Package

**Output this exact structure for every content piece:**

```markdown
## Content Package: [Product Name] — [Platform]

### Campaign Context
- **Product:** [name]
- **Platform:** [platform]
- **Content type:** [Reel / Carousel / Long-form / Short / Post / Thread]
- **Objective:** [awareness / conversion / engagement / education]
- **Target ICP:** [specific segment]
- **Language:** [language + regional variant if applicable]

---

### Hook
[The opening line, text overlay, or first 1.5–3 seconds]

### Caption / Copy
[Full platform-native copy. Formatted for the specific platform.]

### CTA
[Single, clear call to action]

### Hashtags
[Platform-appropriate hashtag set]

### Visual Direction
- **Shot type:** [talking head / b-roll / screen recording / motion graphic / photo]
- **Overlay text:** [exact text that appears on screen]
- **B-roll notes:** [specific visual direction for footage]
- **Color/mood:** [brand-aligned visual tone]
- **Thumbnail notes:** [for YouTube only — text, face, contrast]

### Audio Direction (video only)
- **Music/audio:** [trending sound / original VO / ambient]
- **VO script:** [if applicable — exact spoken words]

---

### Variants (if multi-market)
[Repeat the package above for each language/market variant.
Do NOT translate — localize. Idioms, slang, and cultural references
must be native to the target market.]
```

---

## Step 7: Multi-Platform Campaign Package

When generating a campaign (multi-platform), output:

```markdown
## Campaign: [Campaign Name]

### Campaign Brief
- **Product:** [name]
- **Campaign objective:** [launch / awareness / conversion / retention]
- **Duration:** [X weeks]
- **Platforms:** [list]
- **Target ICP:** [segment]
- **Core message:** [single sentence]
- **Key CTA:** [primary action]

### Content Sequence

| Day | Platform | Type | Hook (summary) | Objective |
|-----|----------|------|-----------------|-----------|
| 1   | IG Reel  | Teaser | [hook summary] | Awareness |
| 1   | X Thread | Announcement | [hook summary] | Awareness |
| 2   | LinkedIn | Story post | [hook summary] | Credibility |
| 3   | YT Short | Demo clip | [hook summary] | Education |
| ...  | ... | ... | ... | ... |

### [Full content package for each piece, using Step 6 format]
```

---

## Step 8: Language and Localization Rules

For multi-market products (Vendly):

- **Do NOT translate.** Localize. Every market variant must read as if it was written natively.
- **Spanish variants matter.** DR Spanish ≠ Mexican Spanish ≠ Colombian Spanish. Use regional idioms, slang, and phrasing.
- **Portuguese (Brazil)** is its own market. Not a translation of Spanish.
- **US Latino English** — code-switching is natural. Spanglish where authentic, not forced.
- Regional currency, payment method, and cultural references must be accurate.
- When in doubt, write for the market — not the product team.

---

## Output Quality Checklist

Before delivering any content package:
- [ ] Copy speaks in ICP's voice, not product team's voice
- [ ] Every claim is specific and provable
- [ ] Single primary message per piece
- [ ] CTA is clear, singular, platform-appropriate
- [ ] Brand voice consistent with product registry
- [ ] Platform specs followed exactly (duration, format, hashtag count)
- [ ] Visual direction is specific enough for a designer/videographer to execute
- [ ] Multi-market variants are localized, not translated
- [ ] Competitive positioning doesn't name competitors directly
- [ ] Accessibility: alt text noted for image-based content
- [ ] Hook passes the "would I stop scrolling?" test

## Related Skills

- `/market-research` — Run before generating content to establish ICP and competitive positioning
- `/customer-onboarding` — Align content with onboarding and activation flows
- `/analytics-implementation` — Set up tracking for content performance metrics
- `/seo-content-engine` — SEO strategy for YouTube and web content
- `/go-to-market` — Full GTM strategy that content packages support
- `/growth-engineering` — Activation funnels and viral mechanics that content drives
