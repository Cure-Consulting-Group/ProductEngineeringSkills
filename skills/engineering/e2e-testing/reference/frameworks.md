# E2E Frameworks & Platform Patterns

> Read when writing the config or first tests for a platform in the `e2e-testing` skill.
> Retry counts come from the `testing-strategy` skill; the configs below read them from env.

## Web (Playwright — default)

**Config (`playwright.config.ts`):**
```typescript
import { defineConfig, devices } from '@playwright/test';

const auth = { storageState: 'e2e/.auth/user.json' };

export default defineConfig({
  testDir: './e2e',
  timeout: 30_000,
  retries: Number(process.env.E2E_RETRIES ?? 0), // value per testing-strategy flake policy
  workers: process.env.CI ? 4 : undefined,
  reporter: process.env.CI ? [['html', { open: 'never' }], ['github']] : [['html', { open: 'on-failure' }]],
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    trace: 'retain-on-failure', // works with or without retries
  },
  projects: [
    { name: 'setup', testMatch: /fixtures\/.*\.setup\.ts/ },
    { name: 'chromium', testMatch: /tests\/.*\.spec\.ts/, use: { ...devices['Desktop Chrome'], ...auth }, dependencies: ['setup'] },
    { name: 'firefox', testMatch: /tests\/.*\.spec\.ts/, use: { ...devices['Desktop Firefox'], ...auth }, dependencies: ['setup'] },
    { name: 'webkit', testMatch: /tests\/.*\.spec\.ts/, use: { ...devices['Desktop Safari'], ...auth }, dependencies: ['setup'] },
    { name: 'mobile-chrome', testMatch: /tests\/.*\.spec\.ts/, use: { ...devices['Pixel 5'], ...auth }, dependencies: ['setup'] },
    { name: 'mobile-safari', testMatch: /tests\/.*\.spec\.ts/, use: { ...devices['iPhone 13'], ...auth }, dependencies: ['setup'] },
  ],
});
```
Add `e2e/.auth/` to `.gitignore` — it holds live session cookies.

**Auth state reuse (`e2e/fixtures/auth.setup.ts`):**
```typescript
import { test as setup, expect } from '@playwright/test';

setup('authenticate', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill(process.env.TEST_USER_EMAIL!);
  await page.getByLabel('Password').fill(process.env.TEST_USER_PASSWORD!);
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page).toHaveURL('/dashboard');
  await page.context().storageState({ path: 'e2e/.auth/user.json' });
});
```

**Page object + test (assertions in the test):**
```typescript
// e2e/pages/LoginPage.ts
export class LoginPage {
  constructor(private page: Page) {}
  async goto() { await this.page.goto('/login'); }
  async signIn(email: string, password: string) {
    await this.page.getByLabel('Email').fill(email);
    await this.page.getByLabel('Password').fill(password);
    await this.page.getByRole('button', { name: 'Sign in' }).click();
    return new HomePage(this.page);
  }
  error() { return this.page.getByRole('alert'); }
}

// e2e/tests/auth.spec.ts
test('auth_login_invalidCredentials', async ({ page }) => {
  const login = new LoginPage(page);
  await login.goto();
  await login.signIn('nobody@example.com', 'wrong');
  await expect(login.error()).toContainText('Invalid');
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

**Accessibility check (call from tests on key screens; WCAG level per `accessibility-audit`):**
```typescript
import AxeBuilder from '@axe-core/playwright';

// e2e/helpers/axe.ts
export async function expectAccessible(page: Page) {
  const results = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa'])
    .analyze();
  expect(results.violations).toEqual([]);
}
```

## Android (Compose testing + Espresso)

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
```kotlin
// build.gradle.kts
android {
    testOptions {
        execution = "ANDROIDX_TEST_ORCHESTRATOR"
    }
}
dependencies {
    androidTestUtil("androidx.test:orchestrator:<current>") // confirm current androidx.test release before use
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
    --device model=<model>,version=<api>   # pick from: gcloud firebase test android models list
    --device model=<model>,version=<api>   # cover min SDK and target SDK
    --results-bucket=${{ vars.GCS_BUCKET }}
```

## iOS (XCUITest)

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
