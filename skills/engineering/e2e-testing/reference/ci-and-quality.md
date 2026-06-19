# E2E CI, Visual Regression & Flake Management

> Reference for the `e2e-testing` skill. CI integration, visual regression, and flaky-test handling.

## Contents
- Step 6: Visual Regression
- Step 7: CI Integration
- Step 8: Flaky Test Management

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
