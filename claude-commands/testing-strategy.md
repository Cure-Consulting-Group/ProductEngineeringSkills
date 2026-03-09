# Testing Strategy

Defines testing standards, pyramid ratios, and patterns for every platform. Write tests that catch real bugs, not tests that test the framework.

## Testing Pyramid (Default Ratios)

```
        ╱ E2E ╲          5%  — Critical user journeys only
       ╱ Integ ╲        20%  — Cross-layer wiring, API contracts
      ╱  Unit   ╲       75%  — Business logic, pure functions, state
```

## Step 1: Classify What Needs Testing

| Layer | What to Test | What NOT to Test |
|-------|-------------|-----------------|
| Domain/Business Logic | Use cases, validation, state machines, calculations | Framework internals, third-party library behavior |
| Data/Repository | API mapping, caching logic, error transformation | Raw HTTP client behavior, Firebase SDK internals |
| Presentation/UI | User interactions, state rendering, navigation | Pixel-perfect layout, animation timing |
| Integration | Cross-layer data flow, auth gates, payment flows | Already-covered unit scenarios |
| E2E | Sign up, purchase, core feature loop | Every permutation — only critical paths |

## Step 2: Platform Standards

### Android (Kotlin)
```
Runner:      JUnit 5
Mocking:     MockK
Assertions:  Truth / Kotest matchers
Coroutines:  Turbine (Flow testing), TestDispatcher
UI:          ComposeTestRule, Espresso (legacy views)
Coverage:    JaCoCo, minimum 70% on business logic

Naming: `fun methodName_condition_expectedResult()`
  Example: `fun login_invalidEmail_showsError()`

File structure:
  src/test/          — unit tests (JVM, no Android framework)
  src/androidTest/   — instrumented tests (Compose UI, Espresso)
```

### iOS (Swift)
```
Runner:      XCTest / Swift Testing (@Test macro)
Mocking:     Protocol-based fakes (no mocking library needed)
TCA:         TestStore with exhaustive assertions
Async:       XCTestExpectation, async/await test functions
UI:          XCUITest for E2E, ViewInspector for SwiftUI unit
Coverage:    Xcode built-in, minimum 70% on business logic

Naming: `func test_methodName_condition_expectedResult()`
  Example: `func test_login_invalidEmail_showsError()`
```

### Next.js / React (TypeScript)
```
Runner:      Vitest
Components:  React Testing Library (@testing-library/react)
API Mocks:   MSW (Mock Service Worker)
E2E:         Playwright
Coverage:    v8/istanbul via Vitest, minimum 70% on lib/

Naming: `it('does X when Y')`
  Example: `it('shows error message when email is invalid')`

File structure:
  __tests__/[feature]/   — co-located with feature
  e2e/                   — Playwright tests at project root
```

### Firebase Cloud Functions (TypeScript)
```
Runner:      Jest or Vitest
Emulator:    Firebase Emulator Suite for integration tests
Rules:       @firebase/rules-unit-testing
Coverage:    minimum 80% on business logic functions

Test with emulator for:
  - Firestore security rules (every rule = a test)
  - Callable functions (auth context, input validation)
  - Webhook handlers (Stripe signature verification)
```

## Step 3: What Makes a Good Test

```
✅ Tests behavior, not implementation
✅ Fails when the feature is broken
✅ Passes when the feature works
✅ Readable — the test name IS the specification
✅ Fast — unit tests < 1s each
✅ Independent — no test depends on another test's state

❌ Tests framework internals (React renders, Hilt injection)
❌ Mirrors implementation (1:1 mock of every dependency)
❌ Flaky (passes sometimes, fails sometimes)
❌ Slow (>5s for a unit test)
❌ Requires manual setup (database, network, specific device)
```

## Step 4: Test Patterns

### Arrange-Act-Assert (AAA)
```
// Every test follows this structure:
// 1. ARRANGE — set up inputs, mocks, initial state
// 2. ACT     — call the function / trigger the interaction
// 3. ASSERT  — verify the output / state change
```

### Fake Over Mock
```
Prefer fakes (real implementations with controlled data) over mocks.
Fakes test behavior. Mocks test wiring.

Use mocks only when:
  - The real dependency is slow (network, database)
  - You need to verify a specific interaction (was X called with Y?)
  - The dependency has side effects (sending email, charging card)
```

### Test Data Builders
```
// Don't construct test objects inline — use builders:
fun aUser(
  id: String = "user-1",
  name: String = "Test User",
  email: String = "test@example.com",
) = User(id = id, name = name, email = email)

// Readable, reusable, easy to override one field
```

### Error Path Testing
```
Every function that can fail needs tests for:
  1. Happy path (works correctly)
  2. Invalid input (bad data)
  3. Dependency failure (network error, auth expired)
  4. Edge cases (empty list, null, boundary values)
  5. Timeout/cancellation (async operations)
```

## Step 5: Coverage Rules

```
Must cover (>= 80%):
  - Business logic / domain layer
  - State management (ViewModel, Reducer, store)
  - Data transformation (mappers, parsers, formatters)
  - Validation logic

Should cover (>= 60%):
  - Repository layer (data fetching + caching)
  - Navigation logic
  - Error handling paths

Can skip:
  - Generated code (Hilt modules, build configs)
  - Pure UI layout (test visually, not programmatically)
  - Third-party library wrappers (test your code, not theirs)
```

## Step 6: CI Integration

```yaml
# Every PR runs:
- Lint check
- Unit tests (all platforms)
- Coverage report (fail if below threshold)
- Integration tests (if touched files in data/ or api/)
- E2E tests (nightly or on release branch only — too slow for every PR)
```

## Flaky Test Policy

```
Flaky test detected?
  1. Quarantine immediately (move to @Ignore/@Skip with TODO)
  2. File a bug ticket with reproduction steps
  3. Fix within current sprint (do not let quarantine list grow)
  4. Never: retry flaky tests in CI to make them pass
```
