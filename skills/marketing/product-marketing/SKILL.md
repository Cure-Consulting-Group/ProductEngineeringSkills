---
name: product-marketing
description: "Writes platform-native social content for portfolio brands. Use when creating Reels, Shorts, LinkedIn or X posts, a campaign, a message house, or brand-voice copy."
when_to_use: "NOT for SEO (seo-content-engine), launch strategy (go-to-market), engineering posts (technical-blog-writer), or Instagram API setup."
argument-hint: "[product-name] [platform-or-campaign]"
metadata:
  verified: 2026-09-23
---

# Product Marketing

**Outcome:** a ready-to-post content package (or campaign) for one product, in that product's voice,
built for the platform it lives on: hook, copy, one CTA, hashtags, and visual/audio direction a
designer can execute. Done when every piece passes the Step 6 checklist. Match length to the need; no
filler sections or restated summaries.

Every run is scoped to one product. Multi-market products get localized variants per market.

## Pre-Processing (Auto-Context)

Context — run these read-only commands first; skip any that fail or aren't permitted (they only tailor the output):

- Portfolio products: `grep -m6 -E '^#{2,3} ' PORTFOLIO.md 2>/dev/null || echo "(no PORTFOLIO.md)"`
- Market research: `ls docs/market-research.md docs/icp.md docs/gtm-plan.md 2>/dev/null | grep . || echo "(none)"`

If research docs exist, pull ICP pains, trigger events, differentiation, and channel choices from them
before writing. With no ICP research, say so and suggest the market-research skill.

## Step 1: Classify

| Request | Output |
|---|---|
| Content package (one or several platforms) | One Step 5 package per platform |
| Campaign | Sequence table + a package per piece |
| Brand foundation | Message house + voice guide |
| Copy (ads, landing, email) | Copy with 2–3 variants |
| Content calendar | Weekly/monthly themes and slots |
| Press | Release + media-kit outline |

## Step 2: Identify the Product

Read `reference/brands.md` for the product's section (Vendly, Autograph, The Initiated,
TwntyHoops, Cure Consulting Group): ICP, tone, languages, core message, differentiators, visual
direction. For a product not in the
registry, gather the same fields first.

## Step 3: Platform Rules (verified 2026-09-23 — platforms change these often)

Hard limits are facts; the rest are Cure starting points to test against the account's own analytics.

| Platform | Hard limits | Cure defaults |
|---|---|---|
| Instagram Reels | 9:16; up to 3 min recorded in-app (longer uploads rolling out); **max 5 hashtags per post** (Instagram, Dec 2025) | Hook in the first 1.5s with text overlay (most watch muted); 15–60s; 3–5 targeted hashtags in the caption; CTA in the caption, not burned into video |
| Instagram feed / carousel | Up to 20 carousel slides; caption 2,200 chars; 5 hashtags | 1080×1350 portrait; slide 1 is the hook, one idea per slide, CTA on the last; alt text on every image |
| YouTube Shorts | Vertical or square, **up to 3 minutes** (since 2024-10-15); description links aren't clickable | Hook in 3s; 30–60s unless the story needs more; channel CTA ("watch the full video"); upload natively, never share IG links |
| YouTube long-form | Title ≤100 chars (~60 visible) | 8–12 min; benefit-first title; first two description lines are the hook; ≥4 chapters; thumbnail 3–5 words, readable on mobile |
| LinkedIn | Post 3,000 chars | ~1,300 chars; hook → insight → takeaway → question; document carousels for tactics; 3–5 hashtags; 2–3 posts/week; no engagement bait |
| X | 280 chars per post (longer for Premium accounts) | Hook post stands alone; threads numbered; link in a reply, not the first post; 0–2 hashtags; one image or video |

Carousel slide count and Reels upload length have changed several times — confirm in-app before a
campaign that depends on them.

## Step 4: Message House and Copy Rules

Before copy for a new product or campaign, fill the message house: brand promise (roof) → three
benefit pillars with two proof points each → foundation of ICP pain, trigger event, and reason to
believe. Registry products already have the core message; build pillars from it.

Copy rules that matter most: outcome before feature; the customer's own words; specifics over
superlatives ("47% faster", not "blazing fast"); one CTA per piece, action verb + outcome ("Start
finding players", not "Sign up"); email subject lines under 50 chars, A/B tested on launches. Don't
name competitors in public copy.

**Localization (Vendly and other multi-market brands):** localize, never translate. DR, Mexican, and
Colombian Spanish differ — use regional idiom; Brazil gets native Portuguese; US Latino English may
code-switch where it's authentic. Currency, payment rails (PIX, CoDi, Nequi), and cultural references
must be right for the market.

## Step 5: Content Package Format

```markdown
## Content Package: [Product] — [Platform] — [Reel | Carousel | Short | Long-form | Post | Thread]
Objective: [awareness | conversion | engagement | education] · ICP: [segment] · Language: [+ regional variant]

### Hook
### Copy
### CTA
### Hashtags (within the platform limit)
### Visual direction — shot type, exact overlay text, b-roll, color/mood, thumbnail (YouTube)
### Audio direction (video) — music/original audio, VO script
### Market variants (multi-market only; localized)
```

Campaigns add a brief (objective, duration, platforms, ICP, core message, key CTA) and a sequence table
(day, platform, type, hook summary, objective) above the packages.

## Step 6: Checklist

- [ ] ICP's voice, not the product team's; every claim specific and provable
- [ ] One message and one CTA per piece
- [ ] Within Step 3 hard limits (length, hashtags, format)
- [ ] Visual direction specific enough to shoot or design without a follow-up
- [ ] Variants localized; alt text noted for images
- [ ] The hook would stop your own scroll

Related: go-to-market (the strategy content serves), seo-content-engine (web and YouTube search),
analytics-implementation (content performance tracking).
