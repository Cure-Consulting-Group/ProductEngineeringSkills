# Product Engineering Skills

The complete skill library that Cure Consulting Group uses to build apps, platforms, and products. These skills encode our standards, frameworks, and processes — so every project ships with the same level of rigor.

## How It's Organized

```
ProductEngineeringSkills/
├── claude-commands/      # Claude Code custom commands (.md)
├── gemini skills/        # Google Gemini skills (.skill ZIP)
└── README.md
```

## Skill Inventory

### Product & Strategy
| Skill | What It Does |
|-------|-------------|
| **product-manager** | OKRs, roadmaps, RICE prioritization, feature briefs, north star metrics |
| **product-design** | Apple HIG, Material Design 3, Web design specs, tokens, accessibility-first |
| **market-research** | TAM/SAM/SOM, competitive analysis, ICP definition, pricing research |
| **go-to-market** | GTM plans, launch strategy, channel selection, growth playbooks |
| **product-marketing** | Brand strategy, messaging frameworks, copy, campaigns, portfolio brand profiles |

### Engineering & Architecture
| Skill | What It Does |
|-------|-------------|
| **sdlc** | PRDs, ADRs, RFCs, Epics, Stories, Task specs, test specs — full SDLC artifacts |
| **android-feature-scaffold** | Clean Architecture Android scaffolding (MVI, Compose, Hilt, Kotlin) |
| **ios-architect** | Swift/SwiftUI Clean Architecture, MVVM, structured concurrency |
| **firebase-architect** | Firestore schema design, security rules, Cloud Functions, data layer |
| **stripe-integration** | Stripe payments + subscriptions via Firebase Cloud Functions, webhook handling |

### Operations & Legal
| Skill | What It Does |
|-------|-------------|
| **project-manager** | Sprint planning, RACI, risk registers, retrospectives, velocity tracking |
| **legal-doc-scaffold** | Terms of Service, Privacy Policy, SOW, NDA scaffolds (with attorney disclaimer) |

## Using with Claude Code

Copy the `claude-commands/` files into your project's `.claude/commands/` directory:

```bash
cp claude-commands/*.md /path/to/your/project/.claude/commands/
```

Then use them as slash commands:
```
/sdlc — Generate SDLC artifacts
/android-feature-scaffold — Scaffold an Android feature module
/product-manager — Run PM frameworks
```

## Using with Google Gemini

Import the `.skill` files from `gemini skills/` into your Gemini workspace. Each `.skill` file is a ZIP archive containing:
- `SKILL.md` — The main skill definition
- `references/` — Supporting documents and templates

## Tech Stack Defaults

These skills assume the following stack (override per-project as needed):

| Layer | Default |
|-------|---------|
| Android | Kotlin, Jetpack Compose, Hilt, MVI, Clean Architecture |
| iOS | Swift, SwiftUI, MVVM, structured concurrency |
| Web | Next.js, TypeScript, Tailwind CSS |
| Backend | Firebase (Firestore, Cloud Functions v2, Auth) |
| Payments | Stripe (Android SDK + server-side via Firebase Functions) |
| AI | Vertex AI, Gemini, OpenAI — production integrations |
| Design | 8pt grid, WCAG AA minimum, platform-native patterns |

## Contributing

When adding a new skill:
1. Create both a Claude command (`.md`) and Gemini skill (`.skill`) version
2. Follow the existing format: Step 1 (Classify), Step 2 (Gather Context), Step 3+ (Framework/Output)
3. Include opinionated defaults — these are standards, not suggestions
4. Cross-reference related skills where relevant
