---
name: e2e-testing
description: "Generate end-to-end test suites with page objects, CI integration, visual regression, and cross-platform test strategies"
argument-hint: "[feature-or-flow]"
---

# E2E Testing

End-to-end test suites that prove your app works for real users. Page Object Model is mandatory. Every test runs independently. Flaky tests are bugs, not "just E2E things."

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

### Web (Playwright — Default)

Playwright is the default for web E2E. Cypress only if the team already uses it.

**Config template (playwright.config.ts):**
```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e/tests',
  timeout: 30_000,
  retries: process.env.CI ? 1 : 0,
  workers: process.env.CI ? 4 : undefined,
  reporter: process.env.CI
    ? [['html', { open: 'never' }], ['github']]
    : [['html', { open: 'on-failure' }]],

  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    screenshot: 'only-on-failure',
    video: 'on-first-retry',
    trace: 'on-first-retry',
  },

  projects: [
    // Auth setup — runs once, saves state for all tests
    { name: 'setup', testMatch: /.*\.setup\.ts/, teardown: 'teardown' },
    { name: 'teardown', testMatch: /.*\.teardown\.ts/ },

    // Desktop browsers
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'], storageState: 'e2e/.auth/user.json' },
      dependencies: ['setup'],
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'], storageState: 'e2e/.auth/user.json' },
      dependencies: ['setup'],
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'], storageState: 'e2e/.auth/user.json' },
      dependencies: ['setup'],
    },

    // Responsive viewports
    {
      name: 'mobile-chrome',
      use: { ...devices['Pixel 5'], storageState: 'e2e/.auth/user.json' },
      dependencies: ['setup'],
    },
    {
      name: 'mobile-safari',
      use: { ...devices['iPhone 13'], storageState: 'e2e/.auth/user.json' },
      dependencies: ['setup'],
    },
  ],
});
```

**Auth state reuse (storageState):**
```typescript
// e2e/fixtures/auth.fixture.ts — runs once, caches login state
import { test as setup } from '@playwright/test';

setup('authenticate', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill(process.env.TEST_USER_EMAIL!);
  await page.getByLabel('Password').fill(process.env.TEST_USER_PASSWORD!);
  await page.getByRole('button', { name: 'Sign in' }).click();
  await page.waitForURL('/dashboard');
  await page.context().storageState({ path: 'e2e/.auth/user.json' });
});
```

**Network mocking for external services:**
```typescript
// Mock Stripe checkout — never hit real Stripe in E2E
await page.route('**/api/create-checkout-session', (route) =>
  route.fulfill({
    status: 200,
    body: JSON.stringify({ url: '/checkout/success?session_id=test_123' }),
  })
);

// Mock analytics — prevent noise
await page.route('**/*.google-analytics.com/**', (route) => route.abort());
await page.route('**/api.mixpanel.com/**', (route) => route.abort());
```

**Accessibility assertions in every page object:**
```typescript
import AxeBuilder from '@axe-core/playwright';

// Add to BasePage or use as a shared assertion
async assertAccessible() {
  const results = await new AxeBuilder({ page: this.page })
    .withTags(['wcag2a', 'wcag2aa'])
    .analyze();
  expect(results.violations).toEqual([]);
}
```

**Responsive testing viewports:**
```
Desktop:  1280 x 720  — default
Tablet:   768 x 1024  — iPad portrait
Mobile:   375 x 667   — iPhone SE
```

**Parallel execution with sharding:**
```yaml
# In CI, shard across machines
strategy:
  matrix:
    shard: [1/4, 2/4, 3/4, 4/4]
steps:
  - run: npx playwright test --shard=${{ matrix.shard }}
```

### Android (Espresso + Compose Testing)

**ComposeTestRule setup with Hilt injection:**
```kotlin
@HiltAndroidTest
@RunWith(AndroidJUnit4::class)
class AuthFlowTest {

    @get:Rule(order = 0)
    val hiltRule = HiltAndroidRule(this)

    @get:Rule(order = 1)
    val composeRule = createAndroidComposeRule<MainActivity>()

    @Before
    fun setup() {
        hiltRule.inject()
    }

    @Test
    fun login_validCredentials_navigatesToHome() {
        LoginRobot(composeRule)
            .enterEmail("test@example.com")
            .enterPassword("password123")
            .tapLogin()
            .assertHomeScreenVisible()
    }
}
```

**Robot pattern (action methods return Robot, assertion methods return nothing):**
```kotlin
class LoginRobot(private val composeRule: ComposeContentTestRule) {

    fun enterEmail(email: String): LoginRobot {
        composeRule.onNodeWithTag("email_field").performTextInput(email)
        return this
    }

    fun enterPassword(password: String): LoginRobot {
        composeRule.onNodeWithTag("password_field").performTextInput(password)
        return this
    }

    fun tapLogin(): HomeRobot {
        composeRule.onNodeWithTag("login_button").performClick()
        composeRule.waitForIdle()
        return HomeRobot(composeRule)
    }

    // Assertion methods return nothing
    fun assertErrorVisible(message: String) {
        composeRule.onNodeWithText(message).assertIsDisplayed()
    }
}
```

**IdlingResource for async operations:**
```kotlin
// Register before tests that trigger async work
IdlingRegistry.getInstance().register(OkHttp3IdlingResource.create("OkHttp", okHttpClient))

// Unregister in @After
IdlingRegistry.getInstance().unregister(idlingResource)
```

**Test orchestrator for isolated runs:**
```groovy
// build.gradle.kts
android {
    testOptions {
        execution = "ANDROIDX_TEST_ORCHESTRATOR"
    }
}
dependencies {
    androidTestUtil("androidx.test:orchestrator:1.5.0")
}
```

**Screenshot testing with Paparazzi or Roborazzi:**
```kotlin
// Paparazzi — JVM-based, no emulator needed
@get:Rule
val paparazzi = Paparazzi(
    deviceConfig = DeviceConfig.PIXEL_5,
    theme = "android:Theme.Material3.DayNight",
)

@Test
fun loginScreen_default() {
    paparazzi.snapshot { LoginScreen(state = LoginState.Initial) }
}
```

**Firebase Test Lab integration:**
```yaml
# In CI, run on real devices
- run: gcloud firebase test android run
    --type instrumentation
    --app app/build/outputs/apk/debug/app-debug.apk
    --test app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk
    --device model=Pixel6,version=33
    --device model=Pixel4,version=30
    --results-bucket=${{ vars.GCS_BUCKET }}
```

### iOS (XCUITest)

**XCUIApplication launch arguments for test configuration:**
```swift
class AuthFlowTests: XCTestCase {
    let app = XCUIApplication()

    override func setUp() {
        super.setUp()
        continueAfterFailure = false
        app.launchArguments = [
            "--uitesting",
            "--reset-state",
            "--disable-animations",
        ]
        app.launchEnvironment = [
            "API_BASE_URL": "https://staging-api.example.com",
            "TEST_USER_EMAIL": "test@example.com",
        ]
        app.launch()
    }
}
```

**Page object with XCUIElement queries (accessibilityIdentifier first):**
```swift
class LoginPage: BasePage {

    private var emailField: XCUIElement {
        app.textFields["login_email_field"]  // accessibilityIdentifier
    }
    private var passwordField: XCUIElement {
        app.secureTextFields["login_password_field"]
    }
    private var loginButton: XCUIElement {
        app.buttons["login_submit_button"]
    }

    @discardableResult
    func enterEmail(_ email: String) -> LoginPage {
        emailField.tap()
        emailField.typeText(email)
        return self
    }

    @discardableResult
    func enterPassword(_ password: String) -> LoginPage {
        passwordField.tap()
        passwordField.typeText(password)
        return self
    }

    func tapLogin() -> HomePage {
        loginButton.tap()
        return HomePage(app: app)
    }

    func assertErrorVisible(_ message: String) {
        let error = app.staticTexts[message]
        XCTAssertTrue(error.waitForExistence(timeout: 5))
    }
}
```

**Network stubbing with URLProtocol:**
```swift
// Register a custom URLProtocol subclass that intercepts requests
// and returns predefined responses. Configure via launch arguments
// or a shared test server running locally.
```

**Snapshot testing with swift-snapshot-testing:**
```swift
import SnapshotTesting

func test_loginScreen_default() {
    let view = LoginView(viewModel: .preview)
    assertSnapshot(of: view, as: .image(layout: .device(config: .iPhone13)))
}
```

**CI execution with Fastlane:**
```ruby
# Fastfile
lane :e2e do
  scan(
    scheme: "AppUITests",
    devices: ["iPhone 15"],
    result_bundle: true,
    output_directory: "./test-results",
    clean: true
  )
end
```

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

## Step 6: Visual Regression

### Snapshot Baseline Management

```
Store baselines in the repo (e2e/__snapshots__/ or equivalent).
Advantages: versioned with code, diff in PR, no external dependency.

For large teams or many screenshots, consider external services:
  - Percy (BrowserStack)
  - Chromatic (Storybook)
  - Applitools
```

### Threshold Configuration

```
Pixel diff tolerance:
  - Default: 0.1% (catches real changes, ignores anti-aliasing)
  - Text-heavy screens: 0.5% (font rendering varies slightly)
  - Animation-present screens: skip or use a specific frame

Never set tolerance above 1% — at that point you're not catching regressions.
```

### Platform-Specific Tools

| Platform | Tool | Approach |
|----------|------|----------|
| Web | Playwright `toHaveScreenshot()` | Built-in, per-browser baselines |
| Android | Paparazzi (JVM, no device) | Compose/View rendering to PNG |
| Android | Roborazzi (Robolectric-based) | Screenshot + Compose preview |
| iOS | swift-snapshot-testing | View/controller snapshot to PNG |

### CI Integration for Visual Regression

```yaml
# Playwright visual regression in CI
- run: npx playwright test --update-snapshots  # Only in dedicated "update baseline" workflow
- run: npx playwright test                      # Normal run — fails on diff

# On failure, upload comparison artifacts
- uses: actions/upload-artifact@v4
  if: failure()
  with:
    name: visual-diffs
    path: e2e/test-results/
```

### Update Workflow

```
When visual changes are intentional:
  1. Run tests locally to see diffs
  2. Review diffs — confirm they match the design
  3. Run: npx playwright test --update-snapshots (or platform equivalent)
  4. Commit updated baselines with message: "chore: update visual baselines for [feature]"
  5. PR reviewers verify the baseline images in the diff
```

## Step 7: CI Integration

### GitHub Actions Workflow Template

```yaml
name: E2E Tests
on:
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 6 * * *'  # Nightly at 6 AM UTC
  workflow_dispatch:       # Manual trigger

env:
  BASE_URL: ${{ vars.STAGING_URL }}
  TEST_USER_EMAIL: ${{ secrets.E2E_TEST_USER_EMAIL }}
  TEST_USER_PASSWORD: ${{ secrets.E2E_TEST_USER_PASSWORD }}

jobs:
  e2e:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    strategy:
      fail-fast: false
      matrix:
        shard: [1/4, 2/4, 3/4, 4/4]

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: 'npm' }
      - run: npm ci
      - run: npx playwright install --with-deps

      - name: Run E2E tests
        run: npx playwright test --shard=${{ matrix.shard }}

      - name: Upload test artifacts on failure
        uses: actions/upload-artifact@v4
        if: failure()
        with:
          name: e2e-artifacts-${{ matrix.shard }}
          path: |
            e2e/test-results/
            playwright-report/
          retention-days: 7

      - name: Upload HTML report
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: playwright-report-${{ matrix.shard }}
          path: playwright-report/
          retention-days: 14
```

### Execution Strategy

```
PR to main:        Run smoke tests (tagged @smoke) — fast feedback
Nightly:           Run full suite — all browsers, all journeys
Pre-release:       Run full suite + visual regression + performance E2E
Manual trigger:    Run specific test file or tag via workflow_dispatch input
```

### Retry Policy

```
Retries: 1 in CI, 0 locally
  - If a test fails on retry, it is a real failure — investigate
  - If a test only passes on retry, it is flaky — fix it (see Step 8)
  - Never set retries > 1 — that hides flakiness
```

### Artifact Upload

```
On failure, always upload:
  - Screenshots (every failed assertion gets one)
  - Videos (recorded on first retry)
  - Traces (Playwright trace viewer — shows every network request, DOM snapshot)
  - Logs (console output, network errors)
```

### Performance Budgets in E2E

```typescript
// Assert performance in E2E tests
test('home page loads within budget', async ({ page }) => {
  await page.goto('/');

  const timing = await page.evaluate(() => {
    const nav = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
    return {
      domContentLoaded: nav.domContentLoadedEventEnd - nav.startTime,
      load: nav.loadEventEnd - nav.startTime,
    };
  });

  expect(timing.domContentLoaded).toBeLessThan(2000); // < 2s
  expect(timing.load).toBeLessThan(3000);              // < 3s
});

test('button interaction is responsive', async ({ page }) => {
  const start = Date.now();
  await page.getByRole('button', { name: 'Submit' }).click();
  await page.waitForResponse('**/api/submit');
  const duration = Date.now() - start;

  expect(duration).toBeLessThan(100); // < 100ms to respond
});
```

### Slack/Webhook Notification

```yaml
# Add to nightly workflow, after test job
notify:
  needs: e2e
  if: failure()
  runs-on: ubuntu-latest
  steps:
    - uses: slackapi/slack-github-action@v1
      with:
        payload: |
          {
            "text": "E2E nightly suite failed. <${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}|View run>"
          }
      env:
        SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

## Step 8: Flaky Test Management

### Detection

```
Track pass rate over the last 20 runs per test:
  - 100% pass rate = stable
  - 95-99% pass rate = warning — investigate soon
  - < 95% pass rate = flaky — quarantine immediately

Use Playwright's built-in last-run tracking or build a simple dashboard
from CI artifacts (test-results.json).
```

### Quarantine

```
Quarantined tests:
  - Mark with @Skip (Playwright: test.skip()) or @Ignore (JUnit)
  - Always include a linked ticket: test.skip('Flaky: JIRA-1234')
  - Maximum 5 quarantined tests at any time — if you hit 5, stop adding
    features and fix flaky tests
  - Review quarantine list weekly in standup
```

### Root Causes Checklist

| Symptom | Root Cause | Fix |
|---------|-----------|-----|
| Test sometimes times out | Missing explicit wait | Add `waitFor()` for the specific element/condition |
| Test fails when run with others but passes alone | State leakage between tests | Isolate test data, reset state in beforeEach |
| Test fails on CI but passes locally | Animation or transition timing | Disable animations in test config |
| Test fails intermittently on network calls | Real network dependency | Mock the external service |
| Test fails on specific browser/device | Platform-specific rendering | Add platform-specific assertion or skip |
| Element not found intermittently | Race condition in rendering | Wait for specific condition, not arbitrary sleep |

### Zero Tolerance Policy

```
Flaky tests are bugs. Treat them with the same urgency as production bugs.

Never:
  - Increase retry count to make flaky tests pass
  - Add arbitrary sleep() calls instead of proper waits
  - Blame "CI environment" without investigating
  - Leave quarantined tests for more than one sprint

Always:
  - Investigate root cause using trace/video artifacts
  - Fix the test or fix the app (sometimes the app has a race condition)
  - Add the fix to the root causes checklist for the team
```

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

---

**Related skills:** /testing-strategy, /ci-cd-pipeline, /accessibility-audit, /performance-review, /uat
