---
name: feature-audit
description: "Run a 5-phase post-completion audit with scored gap report and test scaffolds"
argument-hint: "[feature-name]"
allowed-tools: ["Read", "Grep", "Glob"]
context: fork
---

# Feature Audit

Multi-phase audit that runs after every feature completion across Android, iOS, Firebase, and Web. Produces a scored gap report with actionable fixes and missing test scaffolds.

## Pre-Processing (Auto-Context)

Before starting, gather project context silently:
- Read `PORTFOLIO.md` if it exists in the project root or parent directories for product/team context
- Run: `cat package.json 2>/dev/null || cat build.gradle.kts 2>/dev/null || cat Podfile 2>/dev/null` to detect stack
- Run: `git log --oneline -5 2>/dev/null` for recent changes
- Run: `ls src/ app/ lib/ functions/ 2>/dev/null` to understand project structure
- Use this context to tailor all output to the actual project

## Automated Scanning (Before Manual Review)

Before applying the audit framework, scan the codebase:

1. **File Discovery**: Use Glob to find all feature-related files:
   - `**/{feature}/**/*.kt` `**/{feature}/**/*.swift` `**/{feature}/**/*.tsx`
2. **Error Handling Check**: Use Grep to scan for patterns:
   - Missing: `catch|throw|Result` in feature code (error handling gaps)
   - Present: `try { } catch { }` with empty catch blocks (swallowed errors)
   - Missing: `sealed class.*Error|enum.*Error` (no error type hierarchy)
3. **Test Coverage Check**: Use Glob to compare:
   - Source files: `**/{feature}/**/*.kt` count
   - Test files: `**/{feature}/**/*Test.kt` count
   - Flag if test count < source count
4. **Security Scan**: Use Grep to find:
   - Hardcoded strings matching API key patterns: `sk-|pk_|ghp_|AIza|AKIA`
   - Raw SQL or unparameterized queries
   - Missing input validation on public functions

Report findings before proceeding to the framework phases.

## When to Run

1. **Post-Completion** — After any feature is marked done, merged, or declared "ready to ship"
2. **Explicit Request** — When asked for a feature audit, code audit, gap analysis, or test coverage check

Execute all 5 phases in order. Do not skip phases. Do not summarize — audit.

## Required Inputs

| Input | Required | Notes |
|---|---|---|
| Feature name | Yes | Short identifier |
| Feature description | Yes | 1-2 sentences |
| Android files/modules | Yes if Android | Screens, ViewModels, Repositories |
| iOS files/modules | Yes if iOS | TCA Features, Views, Clients |
| Firebase collections/functions | Yes if Firebase used | Firestore paths, callable names |
| Known concerns | Optional | Any suspected gaps |

If any required input is missing, ask for it before proceeding.

## Phase 1: Feature Boundary Mapping

Map the complete surface area:

- Every **entry point**: UI trigger, deep link, push notification, Universal Link, background job
- Every **exit point**: success state, error state, navigation destination, callback
- Complete **data flow**: input → transform → output → persistence
- All **external dependencies**: APIs, Firebase collections, Stripe endpoints, 3rd-party SDKs
- Any dependency with **no fallback or error handling** → flag immediately
- iOS TCA: map the full `Action → Reducer → Effect` chain
- Android: map `UiEvent → ViewModel → Repository → DataSource` chain

## Phase 2: Logic Gap Detection

### Universal Checks
- State assumed but never validated (null/nil checks, empty states, auth state)
- Business rules implemented inconsistently across layers
- Hardcoded values, magic numbers, strings that should be constants or remote config
- Firebase reads/writes with no security rule coverage (note collection path)
- Race conditions or missing debounce/throttle on user-triggered events

### Android-Specific
- Async operations missing:
  - Error handling (`try/catch`, `.catch{}`, sealed `Result` wrapper)
  - Loading/in-progress state management
  - Cancellation handling (`viewModelScope`, `lifecycleScope`)

### iOS TCA-Specific
- Effects missing:
  - Error mapping (`TaskResult`, `.run { }` failure path)
  - Cancellation (`Effect.cancel(id:)`, `.cancellable(id:)`)
- State mutation happening outside a Reducer
- Effects fired outside a store
- Actions dispatched but not handled (silent `.none` returns on meaningful actions)

### Firebase/Backend
- Security rules missing for any collection read/written by this feature
- Cloud Functions with no error response handling
- Firestore writes without optimistic locking or transaction where needed

## Phase 3: Integration & Wiring Validation

Validate end-to-end wiring across all layers:

**Android**: Hilt chain complete, StateFlow → Composable connected, navigation graph wired, lifecycle-aware Firebase listeners

**iOS TCA**: Store scoping correct, `DependencyValues` injection complete, all Actions handled, state-driven navigation, `testValue` defined for all live Dependencies

**Firebase**: Firestore schema matches both clients, Functions deployed to correct env, Auth UID scoped correctly, security rules consistent

**Stripe**: PaymentIntent lifecycle complete, webhooks idempotent, Customer/PaymentMethod associations correct in both Stripe and Firestore

## Phase 4: Test Coverage Audit

Rate each item: ✅ Covered | ⚠️ Partial | ❌ Missing

**Android**: ViewModel with MockK/FakeRepository, Repository with fake data source, Hilt test modules, ComposeTestRule UI tests, navigation tests

**iOS TCA**: `TestStore` for ALL Reducer tests, every `Action` asserts exact `State` mutation, every `Effect` awaited and resulting `Action` asserted, `withDependencies {}` overrides, exhaustivity mode, cancellation tested

**Firebase/Backend**: Firestore rules via Emulator Suite, Firebase Functions unit tests, end-to-end happy path

**Web**: Component unit tests, integration tests, E2E tests for critical paths

## Phase 5: Audit Report Output

```
═══════════════════════════════════════════════════════
FEATURE AUDIT REPORT
Feature: [NAME]
Date: [TODAY]
═══════════════════════════════════════════════════════

SUMMARY SCORECARD
┌─────────────────────────┬─────────┬───────────┬─────────┬────────┬────────┐
│ Category                │ Android │ iOS (TCA) │ Backend │ Score  │ Status │
├─────────────────────────┼─────────┼───────────┼─────────┼────────┼────────┤
│ Feature Boundary        │  X/10   │   X/10    │  X/10   │  X/30  │ 🟢🟡🔴│
│ Logic Gap Detection     │  X/10   │   X/10    │  X/10   │  X/30  │ 🟢🟡🔴│
│ Integration Wiring      │  X/10   │   X/10    │  X/10   │  X/30  │ 🟢🟡🔴│
│ Test Coverage           │  X/10   │   X/10    │  X/10   │  X/30  │ 🟢🟡🔴│
├─────────────────────────┼─────────┼───────────┼─────────┼────────┼────────┤
│ OVERALL                 │         │           │         │ X/120  │        │
└─────────────────────────┴─────────┴───────────┴─────────┴────────┴────────┘

Scoring: 🟢 >= 80% | 🟡 60-79% | 🔴 < 60%

CRITICAL GAPS (block ship — fix before merge)
1. [Platform] — [Gap] — [File/Layer] — [Fix]

HIGH PRIORITY GAPS (fix in next sprint)
1. [Platform] — [Gap] — [File/Layer] — [Fix]

MISSING TESTS
1. [Platform] — [Test description] — [Test type]
   Scaffold: [Minimal code stub for the missing test]

WIRING ISSUES
1. [Platform] — [Issue] — [From layer → To layer] — [Fix]

CROSS-PLATFORM CONSISTENCY ISSUES
1. [Behavior or data contract that differs between Android and iOS] — [Risk] — [Fix]

RECOMMENDATIONS
- [Architectural or process improvement]

NEXT ACTIONS CHECKLIST
[ ] Fix all CRITICAL gaps before next PR/merge
[ ] Schedule HIGH PRIORITY gaps for next sprint
[ ] Add all MISSING TESTS to backlog with ticket references
[ ] Resolve WIRING ISSUES before QA handoff
[ ] Address CROSS-PLATFORM issues before dual-platform release
═══════════════════════════════════════════════════════
```
