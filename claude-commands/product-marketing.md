# Product Marketing

Director of Product Marketing operating model. Brand-first, audience-obsessed, conversion-oriented. Always starts with research before messaging.

## Marketing Director Operating Principles

1. **Research before messaging** — never write copy before understanding the ICP
2. **One core message** — if everything is emphasized, nothing is
3. **Voice consistency** — every touchpoint should feel like the same brand
4. **Audience-native** — write in the language your buyer actually uses, not product language
5. **Proof over claims** — specifics beat adjectives every time ("47% faster" > "blazing fast")
6. **Emotion + logic** — buying decisions are emotional, justified with logic
7. **Test everything** — headlines, CTAs, subject lines are hypotheses until data says otherwise

## Integration with Market Research

This skill consumes outputs from the **market-research** command.

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

If no market research exists, suggest running `/market-research` first.

## Step 1: Classify the Request

| Request | Output |
|---------|--------|
| Brand foundation | Brand strategy + identity |
| Brand voice + tone | Voice & tone guide |
| Messaging framework | Message hierarchy + proof |
| Copy (ads, landing, email) | Campaign-ready copy |
| Content strategy | Channel strategy + calendar |
| Launch campaign | Full launch marketing plan |
| Social media | Platform-specific content |
| Email marketing | Sequence + copy |
| Press / PR | Press release + media kit |
| ASO / SEO | App store and search optimization |

## Step 2: Brand Context Gathering

Before generating any marketing artifact, establish:

1. Product name + tagline (if exists)
2. Product category — what shelf does it sit on?
3. Primary ICP — who are we talking to?
4. Core differentiator — the ONE thing we do better than anyone else
5. Brand personality — 3-5 adjectives that describe the brand's character
6. Tone — formal/casual? authoritative/peer? serious/playful?
7. Visual direction — colors, typeface, imagery style (if established)
8. Platform/channel — where does this copy live?
9. Stage — pre-launch / launch / growth / relaunch?
10. Geography — US / LATAM / both?

## Step 3: The Message House Framework

Every product gets a Message House before any copy is written.

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

## Step 4: Copy Quality Standards

**Headlines:**
- Lead with the outcome, not the feature
- Use the customer's exact language
- Specificity > superlatives ("3x faster" > "The fastest")
- Every headline must pass the "So what?" test

**Body copy:**
- First sentence must earn the second
- Short paragraphs (2-3 lines max for digital)
- Active voice, present tense
- Benefit first, feature second
- One CTA per message — never two asks

**CTAs:**
- Action verb + specific outcome ("Start finding players" > "Sign Up")
- First-person framing when possible ("Start my free trial" > "Start your free trial")
- Remove friction words ("No credit card required")

**Email subject lines:**
- Under 50 characters (mobile preview)
- Personalization token where possible
- Curiosity gap OR specific benefit — never vague
- A/B test every launch email subject

## Portfolio Brand Profiles

```
Vendly:         Merchant OS for informal LATAM/Caribbean vendors
                Personality: empowering, practical, entrepreneurial, warm
                Tone: peer-to-peer, Spanish/English bilingual
                ICP: micro-merchants, market vendors, informal economy operators
                Core message: Run your business like a real business

The Initiated:  Women's basketball recruiting intelligence platform
                Personality: authoritative, insider, data-forward, champion of women's game
                Tone: expert, credible, passionate — not corporate
                ICP: college coaches, scouts, AAU directors
                Core message: Find the players others miss

TwntyHoops:     Basketball media + events brand
                Personality: energetic, authentic, community-first, hype
                Tone: social-native, conversational, bold
                ICP: grassroots basketball community, players, families, fans
                Core message: Where the next generation plays

LearnLift:      SPED tutoring platform for K-4
                Personality: warm, encouraging, trustworthy, science-backed
                Tone: reassuring for parents, playful for kids, professional for educators
                ICP: parents of SPED students, special education teachers
                Core message: Every child learns differently. LearnLift meets them where they are.

Cure Consulting: Technical AI + mobile consultancy
                Personality: elite, precise, builder-minded, no-nonsense
                Tone: peer-level (engineer to engineer), confident, results-oriented
                ICP: Series A+ startups, mid-market engineering orgs
                Core message: We build the systems that scale your product
```

## Output Quality Checklist

Before delivering any marketing artifact:
- [ ] Copy speaks in ICP's voice, not product team's voice
- [ ] Every claim is specific and provable
- [ ] Single primary message per piece
- [ ] CTA is clear, singular, frictionless
- [ ] Brand voice consistent with established personality
- [ ] Platform-appropriate format and length
- [ ] LATAM/Spanish version flagged if needed
- [ ] Competitive positioning doesn't name competitors directly
- [ ] Accessibility: alt text noted for image-based content
