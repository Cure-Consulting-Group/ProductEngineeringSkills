# E2E CI, Visual Regression, Performance & Flakes

> Read when setting up the E2E CI job, visual baselines, performance assertions, or diagnosing a
> flaky test in the `e2e-testing` skill. Retry counts and quarantine limits are owned by the
> `testing-strategy` skill — this file covers mechanics only.

## Visual Regression

Baselines live in the repo (versioned with the code, diffed in the PR). Use a hosted service
(Percy, Chromatic, Applitools) only when screenshot volume makes the repo unwieldy.

| Platform | Tool |
|----------|------|
| Web | Playwright `toHaveScreenshot()` — per-browser, per-OS baselines |
| Android | Paparazzi (JVM, no device) or Roborazzi (Robolectric) |
| iOS | swift-snapshot-testing |

Tolerance: start at `maxDiffPixelRatio: 0.001`; text-heavy screens up to 0.005; never above 0.01
— past that you stop catching regressions. Freeze animations and mask dynamic content (dates,
avatars) instead of raising tolerance.

Baselines render differently per OS: generate them in the same container/OS image CI uses (e.g. the
official Playwright Docker image), never from a developer's Mac. Regenerate only in a dedicated
workflow (`npx playwright test --update-snapshots`), commit as
`chore: update visual baselines for <feature>`, and review the images in the PR diff.

## CI Job (GitHub Actions)

```yaml
name: E2E
on:
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 6 * * *'   # nightly full suite
  workflow_dispatch:

jobs:
  e2e:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    strategy:
      fail-fast: false
      matrix:
        shard: [1/4, 2/4, 3/4, 4/4]
    env:
      BASE_URL: ${{ vars.STAGING_URL }}
      TEST_USER_EMAIL: ${{ secrets.E2E_TEST_USER_EMAIL }}
      TEST_USER_PASSWORD: ${{ secrets.E2E_TEST_USER_PASSWORD }}
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-node@v7
        with: { node-version: 24, cache: 'npm' }   # Node 24 = active LTS; 20 is EOL
      - run: npm ci
      - run: npx playwright install --with-deps
      - run: npx playwright test --shard=${{ matrix.shard }} ${{ github.event_name == 'pull_request' && '--grep @smoke' || '' }}
      - uses: actions/upload-artifact@v7
        if: failure()
        with:
          name: e2e-artifacts-${{ strategy.job-index }}
          path: |
            test-results/
            playwright-report/
          retention-days: 7
```

Action majors verified 2026-09-23 (checkout, setup-node, upload-artifact all at v7); pin to a
commit SHA if the repo's CI rules require it (see the `ci-cd-pipeline` skill). For failure
notifications, use the team's chat webhook action — confirm its current major and inputs before use.

Cadence: PR → `@smoke`; nightly → full suite, all browsers; pre-release → full + visual +
performance; manual → specific file or tag.

Artifacts on failure: screenshot, trace (open with `npx playwright show-trace`), video, console
and network logs. Link them in the PR.

## Performance in E2E

Lab numbers from CI runners are noisy; use E2E perf assertions as smoke alarms with generous
budgets, and take real Core Web Vitals (LCP, CLS, INP) from field data (RUM/CrUX) — the
`performance-review` skill owns budgets.

```typescript
test('home renders within budget', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('main')).toBeVisible();
  const lcp = await page.evaluate(() => new Promise<number>((resolve) => {
    new PerformanceObserver((list) => {
      const entries = list.getEntries();
      resolve(entries[entries.length - 1].startTime);
    }).observe({ type: 'largest-contentful-paint', buffered: true });
  }));
  expect(lcp).toBeLessThan(2500);
});
```

For interaction latency, load the `web-vitals` library's `onINP` in the page, script the
interactions, and read the reported value on `visibilitychange` — don't time `click()` +
`waitForResponse()` with `Date.now()`, which measures the network, not responsiveness.

## Flaky Tests

Detection: track per-test pass rate over the last 20 runs from the CI JSON reporter; a test that
passes only on retry is flaky by definition.

Root causes:

| Symptom | Cause | Fix |
|---------|-------|-----|
| Intermittent timeout | Waiting on the wrong thing | Wait on a specific element/URL/response; no sleeps, no `networkidle` |
| Fails with others, passes alone | State leakage | Unique data per test; reset in `beforeEach` |
| Fails on CI only | Animations, slower CPU, OS fonts | Disable animations; baselines from the CI image |
| Intermittent on network calls | Real third-party dependency | Mock it with `page.route` |
| One browser/device only | Platform rendering or timing | Fix the app or scope the test; don't skip silently |
| Element intermittently missing | Race in the app itself | Fix the app — sometimes the test is right |

Quarantine mechanics: `test.fixme()` (Playwright) / `@Ignore` (JUnit) with a linked ticket in the
reason string, reviewed weekly. How many may be quarantined and for how long:
`testing-strategy`.
