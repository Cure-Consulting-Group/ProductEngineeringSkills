# E2E Testing

**Outcome:** E2E tests for the requested flows that run independently, pass reliably in CI, and fail
with enough artifacts (trace, screenshot, logs) to diagnose. Done when the target journeys are
covered on the classified platform(s) and the suite runs green twice in a row. Write only the tests
and config the request needs; don't refactor app code beyond adding test IDs.

Policy owned elsewhere: coverage targets, retry counts, and flake quarantine limits come from the
`testing-strategy` skill — apply its numbers, don't restate or override them here.

## Pre-Processing (Auto-Context)

Context — run these read-only commands first; skip any that fail or aren't permitted (they only tailor the output):

- E2E tooling in deps: `grep -hoE '"(@playwright/test|cypress|detox|@axe-core/playwright)"' package.json 2>/dev/null | sort -u || echo "(none in package.json)"`
- Existing E2E files: `find . -path ./node_modules -prune -o \( -name '*.spec.ts' -o -name '*UITests*' -o -path '*androidTest*' \) -print 2>/dev/null | head -10`
- Config: `ls playwright.config.* cypress.config.* 2>/dev/null || echo "(no web E2E config)"`

## Step 1: Classify the Need

| Type | When | Scope |
|------|------|-------|
| Critical user journeys | Always; exist from day one | Sign-up/login, core loop, payments, settings |
| Smoke suite | Post-deploy verification | 5–10 tests, < 2 minutes, tagged `@smoke` |
| Regression suite | After a refactor or migration | Full coverage of the changed areas |
| Visual regression | UI-heavy apps, design-system changes | Screenshot baselines |
| Performance E2E | User-facing latency matters | LCP, CLS, INP (FID was retired in 2024) |
| Flake fix | A test passes only sometimes | Root cause from trace, then fix test or app |

Most projects need critical journeys + smoke at minimum.

## Step 2: Gather Context

From the auto-context and a quick look at existing tests, establish: platform(s); framework
already in use (extend it — don't introduce a second one); CI provider; target environment
(local server, staging URL, emulator/simulator, device farm); auth type (password, OAuth, magic
link, SSO); external services to mock (Stripe, analytics, push). Ask the user only for what the
repo doesn't show.

## Step 3: Architecture

**Framework defaults:** web → Playwright (Cypress only if the team already uses it); Android →
Compose testing + Espresso with Hilt; iOS → XCUITest. Read `reference/frameworks.md` when writing
the config or first tests for a platform — it has the Playwright config, auth-state reuse,
network mocking, Hilt/Robot setup, and XCUITest page objects.

**Page objects are the Cure default** (Robot pattern is fine on Android):
- One class per screen; locators and actions live there, so a UI change is a one-file fix.
- Actions that navigate return the next page object.
- The test owns the outcome assertions (`expect(...)` for what the journey proves). A page object
  may wait for its own ready state (e.g. its heading is visible) before acting.
- Locator priority: role + accessible name → label → test ID (`data-testid`, Compose `testTag`,
  iOS `accessibilityIdentifier`) → text. Never CSS/XPath chains tied to layout.
- In Playwright, don't wrap `click`/`fill` in base-class helpers: locators and web-first assertions
  already auto-wait. Never use `waitForLoadState('networkidle')` (Playwright marks it discouraged)
  or fixed sleeps — wait on a specific element, URL, or response.

**Layout (web):**
```
e2e/
├── pages/       LoginPage.ts, HomePage.ts …
├── tests/       auth.spec.ts, payments.spec.ts … (grouped by journey)
├── fixtures/    auth.setup.ts, data factories, custom fixtures
└── helpers/     network mocks, axe helper
```
Android: `app/src/androidTest/…/{pages|robots,tests,helpers}`. iOS: `UITests/{Pages,Tests,Helpers}`.

**Isolation:** each test creates its own data through factories with unique suffixes, cleans up
after itself, and never depends on another test's state or order. Log in once per worker via
stored auth state instead of through the UI in every test. Use the `test-accounts` skill for
persona accounts and the org's email-address convention.

## Step 4: Critical Journeys

Cover these, adapted to the app (test names `area_action_expectation`):

- **Auth:** sign-up full flow; login valid; login invalid → error, not logged in; logout clears
  state; forgot password → confirmation.
- **Onboarding:** fresh state → complete setup → home shows the new profile.
- **Core loop:** the app's primary action end to end (create → appears → can be acted on).
- **Payments (Stripe test mode):** subscribe with `4242 4242 4242 4242` → active and premium
  unlocked; declined `4000 0000 0000 0002` → error, no subscription. Mock the checkout-session
  call in PR runs; hit Stripe test mode only in nightly.
- **Settings:** update profile persists; change password → re-login works; delete account → can't
  log in.
- **Error recovery:** block the network → error with retry → restore → retry succeeds.
- **Deep links:** open via URL → correct screen and data → back navigation sane.

## Step 5: Visual Regression, CI, Flakes

Read `reference/ci-and-quality.md` when setting up CI, visual baselines, performance assertions,
or diagnosing a flaky test. Key decisions:
- PR runs: `@smoke` only. Nightly: full suite, all browsers. Pre-release: full + visual + perf.
- Capture trace, screenshot, and video on failure (`retain-on-failure`), upload as CI artifacts.
- Visual baselines live in the repo and are regenerated only in a dedicated update workflow,
  reviewed in the PR diff.
- A test that passes only on retry is a flaky test — find the root cause in its trace. Retry and
  quarantine limits: `testing-strategy`.

## Step 6: Reporting

Playwright: built-in HTML report (`playwright-report/`) + `github` reporter in CI. Android and
iOS: Allure or `.xcresult`. Every CI run reports total/passed/failed/skipped/duration, with a
one-line reason per failure and artifact links in the PR.

## Code Generation

Applies when the classification calls for new or extended tests (not for a flake diagnosis or a
strategy question). First find existing patterns (`**/*.spec.ts`, `**/pages/*`, `androidTest/`,
`UITests/`) and match them. For a new web suite, write only what's missing of:

1. `playwright.config.ts` (from the frameworks reference)
2. `e2e/pages/{Screen}Page.ts`
3. `e2e/tests/{journey}.spec.ts` — happy and error paths
4. `e2e/fixtures/` — auth setup and data factories
5. `.github/workflows/e2e.yml` (from the CI reference) if no E2E job exists

Android and iOS follow the same five parts in their native layouts.

## Done Means Exercised

A flow is done when it has been driven end to end against a running build and the behaviour
observed — green unit tests on a broken flow is the classic false-done. If the flow can't be
exercised (no environment, missing credentials), say so rather than substituting other test results.

## Related Skills

`testing-strategy` (pyramid, coverage, retry and flake policy), `test-accounts`,
`ci-cd-pipeline`, `accessibility-audit`, `performance-review`, `uat`.
