# Shared Pre-Processing (Auto-Context)

This block is the canonical auto-context preamble. Skills should reference this file
rather than duplicating the block inline.

## Base Context Gathering

Before starting any skill, gather project context silently:

- Read `PORTFOLIO.md` if it exists in the project root or parent directories for product/team context
- Run: `cat package.json 2>/dev/null || cat build.gradle.kts 2>/dev/null || cat Podfile 2>/dev/null` to detect stack
- Run: `git log --oneline -5 2>/dev/null` for recent changes
- Run: `ls src/ app/ lib/ functions/ 2>/dev/null` to understand project structure
- Use this context to tailor all output to the actual project

## Domain-Specific Extensions

Skills may append additional context-gathering steps after the base block.
Common extensions:

- **Firebase skills**: Also read `firestore.rules`, `firebase.json`
- **AI/LLM skills**: Also check for `.env` with API key patterns, read model configs
- **Analytics skills**: Also check for analytics config files, event schemas
- **Mobile skills**: Also check for `AndroidManifest.xml`, `Info.plist`
- **Compliance skills**: Also read `COMPLIANCE.md`, check for BAA/DPA documents
