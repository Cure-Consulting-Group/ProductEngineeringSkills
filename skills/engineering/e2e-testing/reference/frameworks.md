# E2E Frameworks & Platform Patterns

> Reference for the `e2e-testing` skill. Platform-specific framework choices and patterns (web, Android, iOS, backend).

## Contents
- Step 4: Platform-Specific Frameworks and Patterns

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
