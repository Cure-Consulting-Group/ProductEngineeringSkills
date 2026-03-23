# Cure Consulting Group — Product Engineering Standards

Use these standards for ALL engineering work. This is the condensed version of our 63-skill library.

## Tech Stack Defaults

| Layer | Default |
|-------|---------|
| Android | Kotlin, Jetpack Compose, Hilt, MVI, Clean Architecture |
| iOS | Swift, SwiftUI, MVVM, structured concurrency |
| Web | Next.js, TypeScript, Tailwind CSS, App Router |
| Backend | Firebase (Firestore, Cloud Functions v2, Auth) |
| API | REST (OpenAPI 3.0), GraphQL where appropriate |
| Payments | Stripe (Android SDK + server-side via Firebase Functions) |
| AI | OpenAI, Gemini, Claude — production integrations with guardrails |
| CI/CD | GitHub Actions, Firebase Deploy, Fastlane (mobile) |
| Testing | JUnit5/MockK (Android), XCTest (iOS), Vitest/Playwright (Web) |
| Design | 8pt grid, WCAG AA minimum, platform-native patterns |

## Architecture Standards

### Android (Kotlin)
- Clean Architecture: data/domain/presentation layers
- MVI pattern with sealed class UiState, UiEvent, SideEffect
- Jetpack Compose for all UI (no XML layouts)
- Hilt for dependency injection
- Kotlin Coroutines + Flow for async
- Room for local DB, Retrofit for networking

### iOS (Swift)
- MVVM or TCA (The Composable Architecture)
- SwiftUI for all new UI
- Structured concurrency (async/await, TaskGroup)
- Swift Package Manager for dependencies
- Combine for reactive streams where needed

### Web (Next.js/TypeScript)
- App Router with Server Components by default
- Client Components only when needed ('use client')
- Tailwind CSS for styling (no CSS modules)
- Server Actions for mutations
- Zod for validation, React Hook Form for forms

### Firebase
- Cloud Functions v2 (onRequest, onCall, onDocumentWritten)
- Typed Firestore collections with converter patterns
- Security rules: deny by default, validate all writes
- Composite indexes in firestore.indexes.json

### API Design
- RESTful with OpenAPI 3.0 spec
- Consistent error format: `{ error: { code, message, details } }`
- Pagination on all list endpoints
- Rate limiting with X-RateLimit headers
- API versioning via URL path (/v1/, /v2/)

## Quality Standards

### Security (OWASP)
- No hardcoded secrets — use environment variables
- Input validation at all boundaries
- Parameterized queries (no SQL injection)
- CSRF protection on all forms
- Content Security Policy headers
- Auth: JWT with short expiry + refresh tokens

### Testing
- Unit tests: 80%+ coverage on business logic
- Integration tests: API endpoints, database operations
- E2E tests: Critical user flows (Playwright/Detox/XCUITest)
- No disabled tests in CI
- Test accounts with seed data scripts

### Accessibility (WCAG 2.2 AA)
- Semantic HTML (landmarks, headings hierarchy)
- All images have alt text
- 4.5:1 contrast ratio for text
- 44x44px minimum touch targets
- Keyboard navigable, screen reader compatible
- `prefers-reduced-motion` respected

### Performance
- Core Web Vitals: LCP <2.5s, FID <100ms, CLS <0.1
- Bundle size budgets enforced in CI
- Image optimization (WebP/AVIF, lazy loading)
- Database queries indexed, no N+1

### Compliance & Regulatory
- HIPAA: encrypt PHI at rest and in transit, audit trails, BAAs with vendors
- GDPR: consent management, data subject rights (export/delete), DPA
- PCI DSS: tokenize card data (Stripe handles this), no raw card numbers in logs
- COPPA: parental consent flows, data minimization for under-13 users
- Compliance requirements override convenience — scope decisions favor compliance over ergonomics

### Observability
- Structured logging (JSON) with correlation IDs across services
- Distributed tracing (OpenTelemetry) for cross-service requests
- SLO/SLI definitions for critical user flows
- Alerting: PagerDuty/Opsgenie for SEV1-2, Slack for SEV3-4
- Dashboards: latency p50/p95/p99, error rate, saturation

### Feature Flags & Progressive Rollout
- All new features behind flags (LaunchDarkly, Firebase Remote Config, or Statsig)
- Progressive rollout: 1% → 10% → 50% → 100% with monitoring at each stage
- Kill switches for instant rollback without deployment
- A/B testing framework tied to analytics events

### Analytics
- Event taxonomy: noun_verb format (e.g., `button_clicked`, `screen_viewed`)
- Tracking plan documented before implementation
- Funnels for critical conversion paths
- Dashboard per feature with adoption and engagement metrics

## Process Standards

### SDLC Artifacts
Every feature needs: PRD → ADR (if architectural) → Epic → Stories → Implementation → Tests → Deploy → Audit

### Git Workflow
- Feature branches from main
- PR requires: tests pass, code review, no security warnings
- Conventional commits: feat:, fix:, chore:, docs:
- Squash merge to main

### Deployment
- Staging → Production (no direct-to-prod)
- Feature flags for progressive rollout
- Rollback plan documented before deploy
- Post-deploy smoke tests

### Incident Response
- Severity levels: SEV1 (outage) → SEV4 (cosmetic)
- SEV1/SEV2: immediate response, war room, status page update
- Post-mortem within 48 hours, blameless format
- Action items tracked to completion

## Skill Quick Reference

When asked to perform these tasks, apply the corresponding framework:

| Task | Framework |
|------|-----------|
| New feature | SDLC skill → PRD + ADR + Stories + Implementation |
| Code review | Security (OWASP) + Quality + Testing coverage |
| Architecture decision | ADR format: Context → Decision → Consequences |
| Cost estimate | Engineering Cost Model: team size × duration × infra |
| Performance audit | Core Web Vitals + bundle analysis + query optimization |
| Security review | OWASP Top 10 checklist + auth + data + API |
| Database design | Schema + indexes + migrations + security rules |
| API design | OpenAPI 3.0 spec + error handling + versioning |
| Testing strategy | Pyramid: unit (70%) → integration (20%) → E2E (10%) |
| Incident response | Classify severity → Mitigate → Communicate → Post-mortem |
| Release | Version bump → Changelog → Staged rollout → Monitor |

## Consulting Operations

### Client Communication
- Weekly sprint demos with recorded walkthrough
- Stakeholder updates: what shipped, what's next, blockers
- Risk escalation: flag early, propose solutions

### Handoff
- Runbook with all operational procedures
- Architecture diagrams (C4 model)
- Credential transfer via 1Password vault
- 30-day warranty support period
