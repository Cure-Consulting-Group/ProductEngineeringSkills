# Release Management

Manages the full release lifecycle for Android, iOS, and web applications. Covers versioning strategy, release checklists, staged rollouts, App Store Optimization (ASO), changelog generation, release monitoring, and Fastlane/CI automation. Every release is staged, monitored, and reversible.

**Hard rules:**
- Never ship to 100% on day one — staged rollouts are mandatory for mobile
- Every release has a rollback plan (feature flags, staged rollout halt, or hotfix path)
- Crash rate must be below threshold before advancing rollout percentage
- Changelog is generated from conventional commits — no manual writing
- Release branches are cut, never released directly from main
- App store metadata (screenshots, descriptions) is version-controlled

## Pre-Processing (Auto-Context)

Project context, gathered before the skill runs. Values are injected inline below; in an environment that does not execute them (e.g. Gemini), run the shown commands instead.

- Portfolio: !`sed -n '1,40p' PORTFOLIO.md 2>/dev/null || echo "(no PORTFOLIO.md)"`
- Stack manifest: !`head -40 package.json 2>/dev/null || head -40 build.gradle.kts 2>/dev/null || head -20 Podfile 2>/dev/null || echo "(none detected)"`
- Recent commits: !`git log --oneline -5 2>/dev/null || echo "(not a git repo)"`
- Layout: !`ls src/ app/ lib/ functions/ 2>/dev/null | head -25`

Use this context to tailor all output to the actual project.

## Step 1: Classify the Release Type

| Type | Trigger | Version Bump | Rollout Strategy | Review Required |
|------|---------|-------------|-----------------|-----------------|
| Major | Breaking changes, redesign, platform update | X.0.0 | Internal → Beta → 1% → 10% → 50% → 100% | Full QA + stakeholder sign-off |
| Minor | New features, non-breaking enhancements | x.Y.0 | Internal → Beta → 5% → 25% → 100% | QA + team lead sign-off |
| Patch | Bug fixes, performance improvements | x.y.Z | Internal → 10% → 50% → 100% | QA sign-off |
| Hotfix | Critical production bug, security fix | x.y.Z | Internal → 25% → 100% (accelerated) | Engineering lead sign-off |
| Beta / TestFlight | Pre-release testing | x.y.z-beta.N | Internal testers + opt-in users | No external review needed |

## Step 2: Gather Context

Before releasing, confirm:

1. **Platform(s)** — Android (Play Store), iOS (App Store), web (Vercel/Firebase Hosting), or multi-platform?
2. **Current version** — what is the current production version on each platform?
3. **Release cadence** — weekly, biweekly, monthly, or ad-hoc?
4. **Distribution channels** — Play Store tracks (internal/closed/open/production), TestFlight, App Store, Vercel, Firebase Hosting?
5. **Feature flags** — any flags that should be toggled with this release?
6. **Known issues** — any known bugs shipping in this version (documented and accepted)?
7. **Compliance** — any privacy policy or terms changes required with this version?
8. **Localization** — new strings added? Translations complete for all supported locales?

## Step 3: Versioning Strategy

### Semantic Versioning (SemVer)

```
Format: MAJOR.MINOR.PATCH

MAJOR:  Breaking changes to user-facing behavior or API contracts
        Examples: complete UI redesign, removed features, auth system change
MINOR:  New features, non-breaking enhancements
        Examples: new screen, new settings option, new API endpoint
PATCH:  Bug fixes, performance improvements, copy changes
        Examples: crash fix, typo correction, loading speed improvement

Pre-release:  1.2.0-beta.1, 1.2.0-rc.1
Build meta:   1.2.0+build.456 (informational only, no precedence)
```

### Android Version Mapping

```
versionName: "2.5.3"              // User-visible version (SemVer)
versionCode: 20503                // Play Store integer (must always increase)

Version code formula:
  MAJOR * 10000 + MINOR * 100 + PATCH
  2.5.3  → 20503
  2.5.4  → 20504
  2.6.0  → 20600
  3.0.0  → 30000

For multi-ABI builds, add ABI offset:
  arm64-v8a:  versionCode + 0
  armeabi-v7a: versionCode + 1
  x86_64:     versionCode + 2

// build.gradle.kts
android {
    defaultConfig {
        versionName = "2.5.3"
        versionCode = 20503
    }
}
```

### iOS Version Mapping

```
CFBundleShortVersionString: "2.5.3"   // User-visible version (SemVer)
CFBundleVersion: "1"                   // Build number (reset per version or ever-incrementing)

Strategy A: Reset build number per version (simpler)
  2.5.3 (1), 2.5.3 (2) — for TestFlight iterations
  2.5.4 (1) — reset on version bump

Strategy B: Ever-incrementing build number (CI-friendly)
  2.5.3 (456), 2.5.3 (457), 2.5.4 (458)
  Build number = CI build number (always unique)

Recommendation: Strategy B — avoids accidental duplicate build numbers
```

### Web Versioning

```
package.json version: "2.5.3"
Git tag: v2.5.3
Deploy label: deploy-2.5.3-abc1234 (version + short SHA)

Vercel: automatic preview deployments per PR, promote to production
Firebase Hosting: firebase deploy --only hosting (version in channel)
```

## Step 4: Release Checklist

### Android Release Checklist

```
Pre-Release:
  - [ ] Version bumped (versionName + versionCode) in build.gradle.kts
  - [ ] All features complete and merged to release branch
  - [ ] Feature flags configured for this version
  - [ ] Translations complete for all supported locales
  - [ ] ProGuard/R8 mapping file archived (for crash symbolication)
  - [ ] QA sign-off on release candidate build

Build & Test:
  - [ ] Release build generated (signed with production keystore)
  - [ ] Unit tests passing (100%)
  - [ ] Instrumented tests passing on target API levels (min, target, latest)
  - [ ] Lint checks passing with zero errors
  - [ ] App size within budget (<50MB APK, <150MB AAB with on-demand modules)
  - [ ] Baseline profile included (for startup performance)

Play Store:
  - [ ] Internal testing track upload → team verification (1-2 days)
  - [ ] Closed testing track upload → beta testers (2-3 days)
  - [ ] Production track upload → staged rollout (1% start)
  - [ ] Release notes written (user-facing, per locale)
  - [ ] What's New text updated
  - [ ] Screenshots updated (if UI changed)
  - [ ] Content rating questionnaire current
  - [ ] Data safety section current

Staged Rollout (Production):
  Day 0:  1% rollout   — monitor crash rate, ANR rate, error rate
  Day 1:  5% rollout   — if crash rate <1%, ANR <0.5%
  Day 2:  10% rollout  — review user ratings and crash reports
  Day 3:  25% rollout  — confirm no regression in key metrics
  Day 5:  50% rollout  — broader monitoring
  Day 7:  100% rollout — or halt if issues detected

Rollback:
  - Halt staged rollout in Play Console (instant — stops new users)
  - If critical: promote previous version to 100%
  - Feature flag kill switch for specific features
```

### iOS Release Checklist

```
Pre-Release:
  - [ ] Version bumped (CFBundleShortVersionString + CFBundleVersion)
  - [ ] All features complete and merged to release branch
  - [ ] Feature flags configured for this version
  - [ ] Translations complete for all supported locales
  - [ ] dSYM files archived (for crash symbolication)
  - [ ] QA sign-off on TestFlight build

Build & Test:
  - [ ] Archive build generated (signed with distribution certificate)
  - [ ] Unit tests passing (100%)
  - [ ] UI tests passing on target device matrix (iPhone, iPad if universal)
  - [ ] SwiftLint/SwiftFormat passing with zero errors
  - [ ] App size within budget (check App Thinning report)
  - [ ] Memory profiling clean (no leaks in Instruments)

TestFlight:
  - [ ] Upload to App Store Connect
  - [ ] Internal testers notified (auto-distributed)
  - [ ] External TestFlight group updated (requires beta review)
  - [ ] Beta testing period: 5-7 days minimum
  - [ ] TestFlight crash reports reviewed

App Store Submission:
  - [ ] App Store review submission
  - [ ] What's New text written (per locale)
  - [ ] Screenshots updated (if UI changed, all device sizes)
  - [ ] App preview video updated (if applicable)
  - [ ] Privacy nutrition labels current
  - [ ] In-app purchases / subscriptions configured
  - [ ] Review notes for Apple (explain new features, provide test account)

Phased Release:
  Day 1:  1% of users
  Day 2:  2% of users
  Day 3:  5% of users
  Day 4:  10% of users
  Day 5:  20% of users
  Day 6:  50% of users
  Day 7:  100% of users

  Note: Apple's phased release only applies to auto-updates.
  Users who manually update will get the new version immediately.

Rollback:
  - Pause phased release (stops auto-updates)
  - Cannot remove a version once approved — must submit a new version
  - Expedited review available for critical fixes (use sparingly)
  - Feature flag kill switch is the fastest rollback
```

### Web Release Checklist

```
Pre-Release:
  - [ ] Version bumped in package.json
  - [ ] All features complete and merged to release branch
  - [ ] Feature flags configured
  - [ ] Translations complete
  - [ ] Environment variables verified for production

Build & Test:
  - [ ] Production build succeeds (next build)
  - [ ] Unit tests passing (Vitest)
  - [ ] E2E tests passing (Playwright against preview deployment)
  - [ ] Lighthouse score within budget (Performance >90, Accessibility >95)
  - [ ] Bundle size within budget (check with next/bundle-analyzer)
  - [ ] No TypeScript errors

Deployment:
  Vercel:
    - [ ] Preview deployment reviewed and approved
    - [ ] Promote preview → production
    - [ ] Verify production URL loads correctly
    - [ ] CDN cache invalidated for changed assets

  Firebase Hosting:
    - [ ] firebase deploy --only hosting
    - [ ] Verify live site
    - [ ] Previous version available for instant rollback

Rollback:
  - Vercel: instant rollback to previous deployment
  - Firebase Hosting: firebase hosting:clone PREVIOUS_VERSION live
  - Feature flag kill switch for specific features
```

## Step 5: App Store Optimization (ASO)

See [reference/details.md](reference/details.md) (section “Step 5: App Store Optimization (ASO)”) for full detail.

## Step 6: Changelog Generation

### Conventional Commits

```
Commit format:
  type(scope): description

  [optional body]

  [optional footer: BREAKING CHANGE, Closes #123]

Types:
  feat:     New feature (→ MINOR bump)
  fix:      Bug fix (→ PATCH bump)
  perf:     Performance improvement (→ PATCH bump)
  docs:     Documentation only
  style:    Code style (formatting, no logic change)
  refactor: Code change that neither fixes nor adds
  test:     Adding or correcting tests
  chore:    Build process, dependencies, CI changes
  ci:       CI configuration changes

Breaking changes:
  feat!: remove legacy auth flow           (→ MAJOR bump)
  feat(auth): new login screen

  BREAKING CHANGE: Legacy email/password login has been removed.
  Users must re-authenticate with the new OAuth flow.
```

### Automated Changelog Generation

```
User-facing changelog (for app stores):
  - Include only feat and fix commits
  - Group by category: "New Features", "Bug Fixes", "Performance"
  - Write in user-friendly language (not technical commit messages)
  - Maximum 500 characters for Play Store "What's New"
  - Maximum 4000 characters for App Store "What's New"

Developer changelog (for GitHub releases):
  - Include all commit types
  - Group by type
  - Include PR links and contributor attribution
  - Auto-generated via release-please or standard-version

Template (user-facing):
  What's New in v2.5.3:

  New Features
  - Redesigned profile page with customizable themes
  - Added export to PDF for reports

  Improvements
  - Faster app startup (30% improvement)
  - Smoother scrolling in long lists

  Bug Fixes
  - Fixed crash when opening notifications on Android 14
  - Fixed incorrect total on order summary page
```

## Step 7: Release Monitoring

### Crash Rate Thresholds

```
Android (Play Console vitals):
  - User-perceived crash rate: <1.09% (Play Console bad behavior threshold)
  - User-perceived ANR rate: <0.47% (Play Console bad behavior threshold)
  - Target: crash rate <0.5%, ANR rate <0.2%

iOS (Xcode Organizer / App Store Connect):
  - Crash rate: <1% of sessions
  - Target: crash rate <0.3%
  - Monitor: terminations, disk writes, hangs

Web:
  - JavaScript error rate: <0.1% of page loads
  - Core Web Vitals: LCP <2.5s, FID <100ms, CLS <0.1
  - Target: zero unhandled promise rejections in production

Alerting:
  - Crash rate >2x baseline after rollout start → page on-call
  - Crash rate >3x baseline → halt rollout automatically
  - New crash cluster (>100 occurrences in 1 hour) → alert release owner
```

### Review Sentiment Monitoring

```
Monitor after each release:
  - Play Store rating trend (7-day moving average)
  - App Store rating trend
  - New 1-star reviews mentioning recent changes
  - Support ticket volume (compare to pre-release baseline)

Automated alerts:
  - Average rating drops >0.2 stars in 48 hours → alert product team
  - 1-star review spike (>3x normal) → alert release owner
  - "crash", "broken", "update" keyword spike in reviews → alert engineering

Tools:
  - AppFollow or AppBot for review monitoring
  - Play Console "Ratings and reviews" dashboard
  - App Store Connect "Ratings and Reviews"
```

### Rollback Decision Matrix

```
┌──────────────────────┬──────────────────┬──────────────────────────────┐
│ Signal               │ Threshold        │ Action                       │
├──────────────────────┼──────────────────┼──────────────────────────────┤
│ Crash rate           │ >2x baseline     │ Halt rollout, investigate    │
│ Crash rate           │ >5x baseline     │ Rollback immediately         │
│ ANR rate (Android)   │ >0.47%           │ Halt rollout, investigate    │
│ Error rate (API)     │ >1% increase     │ Halt rollout, investigate    │
│ Revenue drop         │ >10% vs forecast │ Halt rollout, investigate    │
│ Rating drop          │ >0.3 stars       │ Alert PM, consider halt      │
│ Security vulnerability│ Any severity    │ Hotfix or rollback           │
│ Data loss / corruption│ Any occurrence  │ Rollback immediately         │
└──────────────────────┴──────────────────┴──────────────────────────────┘
```

## Step 8: Fastlane / CI Automation

See [reference/details.md](reference/details.md) (section “Step 8: Fastlane / CI Automation”) for full detail.

## Code Generation (Required)

Generate actual release automation files using Write:

1. **Fastlane** (if mobile): `fastlane/Fastfile` with lanes for beta and production
2. **Changelog**: `CHANGELOG.md` with Keep a Changelog format, populated from git log
3. **Version bump script**: `scripts/bump-version.sh` for semantic versioning
4. **Release workflow**: `.github/workflows/release.yml` with approval gates
5. **Rollback script**: `scripts/rollback.sh` that reverts to previous tagged version

Before generating, use Glob to find existing release configs and Grep git tags (`git tag --list`) to understand versioning history.
