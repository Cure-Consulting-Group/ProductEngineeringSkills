# E2E Testing

End-to-end test suites that prove your app works for real users. Page Object Model is mandatory. Every test runs independently. Flaky tests are bugs, not "just E2E things."

## Pre-Processing (Auto-Context)

Project context, gathered before the skill runs. Values are injected inline below; in an environment that does not execute them (e.g. Gemini), run the shown commands instead.

- Portfolio: !`sed -n '1,40p' PORTFOLIO.md 2>/dev/null || echo "(no PORTFOLIO.md)"`
- Stack manifest: !`head -40 package.json 2>/dev/null || head -40 build.gradle.kts 2>/dev/null || head -20 Podfile 2>/dev/null || echo "(none detected)"`
- Recent commits: !`git log --oneline -5 2>/dev/null || echo "(not a git repo)"`
- Layout: !`ls src/ app/ lib/ functions/ 2>/dev/null | head -25`

Use this context to tailor all output to the actual project.

## Step 1: Classify the E2E Need

| Type | When to Use | Scope |
|------|------------|-------|
| **Critical User Journey** | Always — these exist from day one | Sign up, core loop, payments, settings |
| **Regression Suite** | After major refactor or migration | Full flow coverage of changed areas |
| **Smoke Test Suite** | Post-deploy verification | 5-10 tests, < 2 minutes, critical paths only |
| **Visual Regression** | UI-heavy apps, design system changes | Screenshot comparison against baselines |
| **Performance E2E** | User-facing latency matters | Page load, interaction timing, LCP/FID |

Determine which type(s) apply. Most projects need Critical User Journeys + Smoke Tests at minimum.

## Step 2: Gather Context

Before generating anything, determine:

1. **Platform** — Web, Android, iOS, or cross-platform?
2. **Framework** — Next.js, Compose, SwiftUI, React Native, Flutter?
3. **CI provider** — GitHub Actions, CircleCI, Xcode Cloud, Bitrise?
4. **Test environment** — Staging URL? Emulator? Physical devices?
5. **Existing E2E coverage** — Starting from zero or extending existing suite?
6. **Auth flow type** — Email/password, OAuth, magic link, SSO?
7. **External services** — Stripe, analytics, push notifications?

## Step 3: Test Architecture

### Page Object Model (POM) — Mandatory

Every E2E suite uses POM. No exceptions. Raw selectors in test files are a code smell.

```
Page Object rules:
  1. One class per screen/page
  2. Actions return the next page object (for chaining)
  3. Assertions live in the page object, not the test
  4. Selectors are private — tests never see CSS/XPath/accessibility IDs directly
  5. Base page class handles common actions (wait, tap, type, scroll, assertVisible)
```

### File Structure by Platform

**Web:**
```
e2e/
├── pages/              # Page objects (LoginPage, HomePage, SettingsPage)
│   ├── BasePage.ts     # Common actions: goto, waitForLoad, screenshot
│   ├── LoginPage.ts
│   ├── HomePage.ts
│   └── SettingsPage.ts
├── tests/              # Test files grouped by journey
│   ├── auth.spec.ts
│   ├── onboarding.spec.ts
│   └── payments.spec.ts
├── fixtures/           # Test data factories, auth state, custom fixtures
│   ├── auth.fixture.ts
│   └── test-data.ts
└── helpers/            # Utilities: network mocks, date helpers, assertions
    ├── mock-stripe.ts
    └── accessibility.ts
```

**Android:**
```
app/src/androidTest/
├── pages/              # Page objects using Compose semantics or Espresso matchers
│   ├── BasePage.kt
│   ├── LoginPage.kt
│   └── HomePage.kt
├── tests/              # Test classes grouped by journey
│   ├── AuthFlowTest.kt
│   └── PaymentFlowTest.kt
├── robots/             # Robot pattern (alternative to POM for Android)
│   ├── LoginRobot.kt
│   └── HomeRobot.kt
└── helpers/            # IdlingResources, test rules, data builders
    ├── ComposeTestHelper.kt
    └── TestDataFactory.kt
```

**iOS:**
```
UITests/
├── Pages/              # Page objects using XCUIElement queries
│   ├── BasePage.swift
│   ├── LoginPage.swift
│   └── HomePage.swift
├── Tests/              # Test cases grouped by journey
│   ├── AuthFlowTests.swift
│   └── PaymentFlowTests.swift
└── Helpers/            # Launch arguments, network stubs, extensions
    ├── XCUIElementExtensions.swift
    └── TestEnvironment.swift
```

### Base Page Class Pattern

```typescript
// Web (Playwright) — BasePage.ts
export abstract class BasePage {
  constructor(protected page: Page) {}

  async waitForLoad() {
    await this.page.waitForLoadState('networkidle');
  }

  async tap(locator: Locator) {
    await locator.waitFor({ state: 'visible' });
    await locator.click();
  }

  async type(locator: Locator, text: string) {
    await locator.fill(text);
  }

  async scrollTo(locator: Locator) {
    await locator.scrollIntoViewIfNeeded();
  }

  async assertVisible(locator: Locator) {
    await expect(locator).toBeVisible();
  }

  async assertNotVisible(locator: Locator) {
    await expect(locator).not.toBeVisible();
  }
}
```

```kotlin
// Android — BasePage.kt
abstract class BasePage(
    protected val composeRule: ComposeContentTestRule
) {
    fun waitForIdle() {
        composeRule.waitForIdle()
    }

    fun assertVisible(testTag: String) {
        composeRule.onNodeWithTag(testTag).assertIsDisplayed()
    }

    fun tap(testTag: String) {
        composeRule.onNodeWithTag(testTag).performClick()
    }

    fun type(testTag: String, text: String) {
        composeRule.onNodeWithTag(testTag).performTextInput(text)
    }

    fun scrollTo(testTag: String) {
        composeRule.onNodeWithTag(testTag).performScrollTo()
    }
}
```

```swift
// iOS — BasePage.swift
class BasePage {
    let app: XCUIApplication

    init(app: XCUIApplication) {
        self.app = app
    }

    func waitForElement(_ identifier: String, timeout: TimeInterval = 5) -> XCUIElement {
        let element = app.descendants(matching: .any)[identifier]
        XCTAssertTrue(element.waitForExistence(timeout: timeout),
                      "\(identifier) did not appear within \(timeout)s")
        return element
    }

    func tap(_ identifier: String) {
        waitForElement(identifier).tap()
    }

    func type(_ identifier: String, text: String) {
        let element = waitForElement(identifier)
        element.tap()
        element.typeText(text)
    }

    func assertVisible(_ identifier: String) {
        XCTAssertTrue(waitForElement(identifier).exists)
    }
}
```

### Test Data Isolation

```
Rules:
  1. Each test creates its own state — unique user, unique data
  2. Tests clean up after themselves (delete created users/data in afterEach)
  3. Never share state between tests — no "test user 1" used by 5 tests
  4. Use factories: createTestUser(), createTestOrder() with random suffixes
  5. For auth, generate unique emails: `test+${uuid}@example.com`
```

See /testing-strategy for test data builder patterns.

### No Test-to-Test Dependencies

```
Every test runs independently. This means:
  - No test relies on another test having run first
  - No shared mutable state between tests
  - Test order is randomized — if order matters, your tests are broken
  - Each test starts from a known state (fresh login, empty cart, clean DB)
```

## Step 4: Platform-Specific Frameworks and Patterns

See [reference/frameworks.md](reference/frameworks.md) for per-platform framework choices and patterns (Playwright/Cypress web, Espresso/Compose Android, XCUITest iOS, API/contract backend).

## Step 5: Critical User Journeys

Every app should have E2E tests for these journeys. Adapt to your app's specifics.

### Authentication
```
Test: auth_signUp_fullFlow
  1. Navigate to sign up
  2. Enter valid email + password
  3. Submit → verify confirmation screen
  4. (If email verification) Check for verification prompt
  5. Login with new credentials
  6. Assert: landed on home/dashboard

Test: auth_login_validCredentials
  1. Navigate to login
  2. Enter valid email + password
  3. Submit → assert home screen

Test: auth_login_invalidCredentials
  1. Enter wrong password
  2. Assert: error message visible, not logged in

Test: auth_logout
  1. Login → navigate to settings
  2. Tap logout
  3. Assert: redirected to login, auth state cleared

Test: auth_forgotPassword
  1. Navigate to forgot password
  2. Enter email → submit
  3. Assert: confirmation message shown
```

### Onboarding
```
Test: onboarding_firstLaunch_completesSetup
  1. Fresh install / cleared state
  2. Step through onboarding screens
  3. Complete profile setup
  4. Assert: landed on home with correct profile data
```

### Core Loop
```
Test: core_[primaryAction]_fullFlow
  This varies per app. Examples:
  - Social app: create post → appears in feed → receives interaction
  - E-commerce: search → add to cart → checkout
  - SaaS: create project → invite member → collaborate
  - Fitness: start workout → log exercises → view summary
```

### Payments (if Stripe)
```
Test: payment_subscribe_fullFlow
  1. Login → navigate to pricing
  2. Select a plan
  3. Enter test card (4242 4242 4242 4242)
  4. Confirm payment
  5. Assert: subscription active, premium features unlocked

Test: payment_subscribe_declinedCard
  1. Enter declined test card (4000 0000 0000 0002)
  2. Assert: error message, no subscription created
```

### Settings
```
Test: settings_updateProfile
  1. Navigate to settings
  2. Change display name
  3. Save → assert: updated name reflected

Test: settings_changePassword
  1. Enter current password + new password
  2. Save → logout → login with new password
  3. Assert: login successful

Test: settings_deleteAccount
  1. Navigate to account deletion
  2. Confirm deletion
  3. Assert: logged out, cannot login again
```

### Error Recovery
```
Test: error_networkFailure_retrySucceeds
  1. Trigger action with network intercepted/blocked
  2. Assert: error state shown with retry option
  3. Restore network → tap retry
  4. Assert: action completes successfully
```

### Deep Links
```
Test: deepLink_navigatesToCorrectScreen
  1. Open app via deep link URL
  2. Assert: correct screen displayed with correct data
  3. Assert: back navigation works as expected
```

## Steps 6–8: Visual Regression, CI Integration & Flake Management

See [reference/ci-and-quality.md](reference/ci-and-quality.md) for visual regression, CI pipeline integration, and flaky-test management.

## Step 9: Test Reporting

### HTML Report Generation

| Platform | Tool | Output |
|----------|------|--------|
| Web (Playwright) | Built-in HTML reporter | `playwright-report/index.html` |
| Android | Allure | `build/reports/allure-report/` |
| iOS | XCResult + xcresulttool | `.xcresult` bundle |
| All | Allure (cross-platform) | Unified dashboard |

### Test Run Summary

```
Every CI run produces a summary:
  Total:    142
  Passed:   138
  Failed:   2
  Skipped:  2 (quarantined)
  Duration: 4m 32s

Failed tests are listed with one-line reason.
```

### Failed Test Details

```
For every failed test, capture:
  1. Screenshot at moment of failure
  2. Video of the full test run (on first retry)
  3. Stack trace with page object step highlighted
  4. Network requests/responses during the test
  5. Console logs and errors
  6. Browser/device info

All artifacts uploaded as CI artifacts, linked in PR comment.
```

### Trend Dashboard

```
Track over time (weekly review):
  - Overall pass rate (target: > 99%)
  - Most-failed tests (top 5 — fix these first)
  - Slowest tests (top 5 — optimize or split these)
  - Test count growth (are we adding coverage?)
  - Flaky test count (trending down = good)

Use Allure trend reports or build a simple dashboard from CI data.
```

## Code Generation (Required)

You MUST generate actual test files using the Write tool:

1. **Config**: `playwright.config.ts` or `maestro/` config based on platform
2. **Page Objects**: `tests/pages/{Feature}Page.ts` with locators and actions
3. **Test Suites**: `tests/{feature}.spec.ts` with describe/it blocks for happy + error paths
4. **Fixtures**: `tests/fixtures/{feature}.fixtures.ts` with test data
5. **CI Integration**: `.github/workflows/e2e.yml` for running E2E tests

Before generating, use Glob to find existing test patterns (`**/*.spec.ts`, `**/*.test.ts`, `**/pages/*.ts`) and match conventions.

---

**Related skills:** /testing-strategy, /ci-cd-pipeline, /accessibility-audit, /performance-review, /uat

## Verification Contract (Cure standard)

A change is "done" when the affected flow has been exercised end-to-end and the
behavior observed — not when unit tests pass. Green tests on a broken flow is
the classic false-done. Before reporting success: run the real entry point
(app, endpoint, CLI, screen), drive the changed path with realistic input, and
state what you observed. If the flow cannot be exercised, say so explicitly
instead of substituting test results.
