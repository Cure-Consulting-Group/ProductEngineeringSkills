# Testing Strategy

**Outcome:** a testing strategy for the named project or feature — current state, the gaps that matter, per-platform stack, coverage gates, CI wiring, and flaky-test policy. Done when every layer that holds business logic has a named test type, a coverage gate, and a CI stage. Match length to the need; no filler sections or restated summaries.

This skill is the **library's source of truth for coverage thresholds and CI retry policy**. Other skills (sdlc, e2e-testing, scaffolds, rules) link here instead of restating numbers.

## Pre-Processing (Auto-Context)

Context — run these read-only commands first; skip any that fail or aren't permitted (they only tailor the output):

- Stack manifest: `head -30 package.json 2>/dev/null || head -30 build.gradle.kts 2>/dev/null || head -20 Package.swift 2>/dev/null || head -20 pyproject.toml 2>/dev/null || echo "(none detected)"`
- Coverage/test config: `ls jest.config* vitest.config* playwright.config* pytest.ini .nycrc* 2>/dev/null | head -5 || echo "(none)"`

## Step 1: Classify

| Request | Output |
|---|---|
| New project, no tests | Full strategy: stack, pyramid, gates, CI stages |
| Existing project, "what are we missing" | Current-state audit (Step 2) + ranked gap list |
| Single feature | Test list per layer for that feature; skip the project-wide sections |
| "Tests are flaky / CI is slow" | Flaky-test policy + CI stage split only |

## Step 2: Gather Current State (existing projects)

Measure before recommending:

1. **Ratio** — count source vs test files (`*Test.*`, `*Spec.*`, `*.test.*`, `*.spec.*`, `test_*.py`), excluding `node_modules`, `build`, `.next`, generated code.
2. **Frameworks** — detect from config and imports, not keyword greps: `vitest`/`jest` in the manifest, `org.junit.jupiter` / `io.mockk` in Gradle, `import Testing` / `XCTestCase`, `pytest` in pyproject. (A grep for `it(`/`test(` matches nearly every file.)
3. **Coverage config** — existing thresholds in `vitest.config*`, `jest.config*`, JaCoCo, `.nycrc*`, `pyproject` `[tool.coverage]`.
4. **Untested units** — ViewModels, use cases, reducers, repositories, Cloud Functions handlers with no matching test file.
5. **Disabled tests** — `@Disabled`, `@Ignore`, `.skip`, `xit`, `xdescribe`, `@pytest.mark.skip`. Each one is quarantine debt; count them.

Report current state first, then the strategy.

## Step 3: Pyramid (default ratios)

Unit ~75% · Integration ~20% · E2E ~5% (critical journeys only: sign-up, purchase, core loop). Test behavior, not framework internals — no tests of React rendering, Hilt injection, or SDK behavior. Integration tests own cross-layer wiring, auth gates, and payment flows; don't re-cover unit scenarios there.

## Step 4: Platform Stack (Cure defaults)

| Platform | Runner / mocking | UI / E2E | Coverage tool | Naming |
|---|---|---|---|---|
| Android (Kotlin) | JUnit 5, MockK, Turbine + `TestDispatcher` for Flows | Compose test rule; Espresso only for legacy views | JaCoCo / Kover | `login_invalidEmail_showsError()` |
| iOS (Swift) | Swift Testing (`@Test`) for new code, XCTest for existing; protocol-based fakes, no mocking library | XCUITest | Xcode coverage | `test_login_invalidEmail_showsError()` |
| Next.js / React | Vitest, React Testing Library, MSW for network | Playwright (see e2e-testing) | Vitest v8 | `it('shows error when email is invalid')` |
| Firebase Functions | Vitest or Jest against the Emulator Suite; `@firebase/rules-unit-testing` | — | Vitest v8 / Istanbul | every security rule has an allow and a deny test |
| Python | pytest, pytest-asyncio, fakes over `unittest.mock` | — | coverage.py | `test_login_invalid_email_shows_error` |

Layout: Android `src/test/` (JVM) vs `src/androidTest/` (instrumented); web tests co-located per feature, E2E in `e2e/` at the root.

Cure testing conventions the model should apply without being asked:
- **Fakes over mocks.** Mocks only for slow, side-effecting (email, charge), or interaction-verification cases.
- **Test data builders** with defaults (`aUser(email = …)`) instead of inline construction.
- **Error paths are mandatory** for anything that can fail: invalid input, dependency failure, auth expired, empty/boundary, timeout/cancellation.
- Stripe/webhook handlers are tested with a real signature over the raw body, in the emulator.

## Step 5: Coverage Gates (source of truth)

| Scope | Gate |
|---|---|
| **New or changed code in a PR** (diff coverage) | **≥80%** — CI fails below this |
| Domain/business logic, state (ViewModel/reducer/store), mappers/parsers, validation | ≥80% |
| Repositories, navigation, error-handling paths | ≥60% |
| Whole-project line coverage | Ratchet: never decreases PR over PR; no fixed number |
| Excluded | Generated code (Hilt/DI modules, build config), pure layout, third-party wrappers |

Why 80% on new code: it is the Cure standard stated in the plugin's compaction hook ("80% coverage minimum on new code") and gates the code a PR author controls. A whole-project floor punishes legacy repos and gets gamed; the ratchet plus diff gate raises coverage without that. This replaces the earlier 70%-per-platform figures, which contradicted the 80% layer rule. Implement with the tool's diff mode (e.g. `diff-cover`, Codecov/Coveralls patch status, Kover/JaCoCo with a changed-files filter).

## Step 6: CI Stages

| Trigger | Runs |
|---|---|
| Every PR | Lint + type check · unit tests (all platforms) · diff-coverage gate · integration tests when `data/`, `api/`, `functions/`, or rules changed |
| Merge to main / release branch | Full integration + E2E critical journeys |
| Nightly | Full E2E matrix, visual regression |

## Step 7: Retry and Flaky-Test Policy (source of truth)

- **Unit and integration tests: 0 retries in CI.** A retry hides a real race.
- **E2E: at most 1 retry in CI** (Playwright `retries: process.env.CI ? 1 : 0`, trace/video `on-first-retry`). A test that passes only on retry is **flaky**, reported as such, and enters quarantine — it is never counted as a clean pass. Locally, 0 retries.
- **Quarantine:** move to skip with a ticket link and owner; fix within the current sprint. The quarantine list is reviewed at every sprint boundary and must not grow two sprints running.

## Verification Contract (Cure standard)

A change is "done" when the affected flow has been exercised end-to-end and the behavior observed — not when unit tests pass. Green tests on a broken flow is the classic false-done. Run the real entry point (app, endpoint, CLI, screen), drive the changed path with realistic input, and state what you observed. If the flow cannot be exercised, say so explicitly instead of substituting test results.
