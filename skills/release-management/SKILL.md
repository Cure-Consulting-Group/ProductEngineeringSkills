---
name: release-management
description: "Manage release workflows — app store submissions, staged rollouts, versioning strategy, changelogs, and ASO for Android and iOS"
argument-hint: "[platform-or-version]"
---

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

Before starting, gather project context silently:
- Read `PORTFOLIO.md` if it exists in the project root or parent directories for product/team context
- Run: `cat package.json 2>/dev/null || cat build.gradle.kts 2>/dev/null || cat Podfile 2>/dev/null` to detect stack
- Run: `git log --oneline -5 2>/dev/null` for recent changes
- Run: `ls src/ app/ lib/ functions/ 2>/dev/null` to understand project structure
- Use this context to tailor all output to the actual project

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

### Keyword Strategy

```
Research process:
  1. Seed keywords from product description and competitor analysis
  2. Use ASO tools (AppTweak, Sensor Tower, AppFollow) for volume/difficulty scores
  3. Target: high volume (>20 search score) + low difficulty (<50)
  4. Include keywords in: title, subtitle, keyword field (iOS), description (Android)

iOS keyword rules:
  - Title: 30 characters max — brand name + primary keyword
  - Subtitle: 30 characters max — secondary benefit/keyword
  - Keyword field: 100 characters — comma-separated, no spaces after commas,
    no duplicates from title/subtitle, singular forms only
  - URL: include keyword in the App Store URL if possible

Android keyword rules:
  - Title: 30 characters max — brand name + primary keyword
  - Short description: 80 characters max — key features + keywords
  - Full description: 4000 characters max — use keywords naturally (not stuffing),
    first 3 lines are most important (visible before "Read More")
  - Developer name is indexed — use brand name

Keyword refresh cadence:
  - Review keyword rankings monthly
  - Update keywords with each release (title/subtitle changes are low-risk)
  - A/B test title and short description quarterly
```

### Screenshots and Preview Videos

```
Screenshot requirements:
  Android:
    - Minimum 2, maximum 8 screenshots per device type
    - Phone: 16:9 ratio, minimum 320px, maximum 3840px on any side
    - Recommended sizes: 1080x1920 (phone), 1200x1920 (7" tablet), 1600x2560 (10" tablet)
    - First 2-3 screenshots are critical (visible in search results)

  iOS:
    - 6.7" display (iPhone 15 Pro Max): 1290x2796 — required
    - 6.5" display (iPhone 14 Plus): 1284x2778 — required
    - 5.5" display (iPhone 8 Plus): 1242x2208 — optional (older)
    - iPad Pro 12.9" (6th gen): 2048x2732 — if universal app
    - Maximum 10 screenshots per device size

Screenshot best practices:
  - Each screenshot conveys ONE feature/benefit
  - Include text overlay: short headline + feature callout
  - Use actual app UI (not mockups) — Apple rejects obvious mockups
  - Localize screenshots for top 5 markets
  - A/B test first screenshot (Google Play Experiments)

Preview video:
  - 15-30 seconds, show the 3 most compelling features
  - No audio narration needed (most users watch without sound)
  - App footage only (no lifestyle/stock footage per Apple guidelines)
  - Update video only for major releases (high production cost)
```

### Localized Listings

```
Priority locales (by market size):
  1. English (US) — default
  2. English (UK, AU, CA) — minor copy adjustments
  3. Spanish (MX/ES)
  4. Portuguese (BR)
  5. French (FR)
  6. German (DE)
  7. Japanese (JP)
  8. Korean (KR)

Localization checklist per locale:
  - [ ] App name / title (if localized brand)
  - [ ] Subtitle / short description
  - [ ] Full description
  - [ ] What's New / release notes
  - [ ] Keywords (iOS keyword field — research per locale)
  - [ ] Screenshots (localized text overlays + actual localized app UI)
  - [ ] Preview video subtitles (if applicable)

Store all listing assets in version control:
  store-assets/
  ├── android/
  │   ├── en-US/
  │   │   ├── title.txt
  │   │   ├── short-description.txt
  │   │   ├── full-description.txt
  │   │   └── changelogs/
  │   │       └── 20503.txt     # versionCode-based changelog
  │   └── es-MX/
  │       └── ...
  └── ios/
      ├── en-US/
      │   ├── name.txt
      │   ├── subtitle.txt
      │   ├── keywords.txt
      │   ├── description.txt
      │   └── whats-new.txt
      └── es-MX/
          └── ...
```

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

### Android Fastlane Configuration

```ruby
# fastlane/Fastfile (Android)

default_platform(:android)

platform :android do
  desc "Deploy to internal testing track"
  lane :internal do
    gradle(task: "clean bundleRelease")
    upload_to_play_store(
      track: "internal",
      aab: "app/build/outputs/bundle/release/app-release.aab",
      skip_upload_metadata: true,
      skip_upload_images: true,
      skip_upload_screenshots: true
    )
  end

  desc "Promote internal to production with staged rollout"
  lane :release do |options|
    rollout = options[:rollout] || "0.01"  # default 1%
    upload_to_play_store(
      track: "internal",
      track_promote_to: "production",
      rollout_percentage: rollout,
      skip_upload_metadata: false,
      skip_upload_images: false,
      skip_upload_screenshots: false
    )
  end

  desc "Increase rollout percentage"
  lane :increase_rollout do |options|
    rollout = options[:rollout]  # e.g., "0.10" for 10%
    upload_to_play_store(
      track: "production",
      rollout_percentage: rollout,
      skip_upload_aab: true,
      skip_upload_metadata: true
    )
  end

  desc "Halt rollout"
  lane :halt_rollout do
    upload_to_play_store(
      track: "production",
      rollout_percentage: "0",
      skip_upload_aab: true
    )
  end
end
```

### iOS Fastlane Configuration

```ruby
# fastlane/Fastfile (iOS)

default_platform(:ios)

platform :ios do
  desc "Upload to TestFlight"
  lane :beta do
    increment_build_number(
      build_number: ENV["CI_BUILD_NUMBER"] || latest_testflight_build_number + 1
    )
    build_app(
      scheme: "App",
      export_method: "app-store",
      output_directory: "./build"
    )
    upload_to_testflight(
      skip_waiting_for_build_processing: true,
      distribute_external: false
    )
  end

  desc "Submit to App Store with phased release"
  lane :release do
    deliver(
      submit_for_review: true,
      automatic_release: false,  # manual release after approval
      phased_release: true,      # 7-day phased rollout
      submission_information: {
        add_id_info_uses_idfa: false
      },
      force: true  # skip HTML preview
    )
  end

  desc "Upload metadata and screenshots only"
  lane :metadata do
    deliver(
      skip_binary_upload: true,
      skip_metadata: false,
      skip_screenshots: false,
      force: true
    )
  end
end
```

### GitHub Actions Release Workflow

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  android-release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: ruby/setup-ruby@v1
        with: { ruby-version: '3.2' }
      - run: bundle install
      - name: Decode keystore
        run: echo ${{ secrets.KEYSTORE_BASE64 }} | base64 -d > app/keystore.jks
      - name: Build and upload to internal track
        run: bundle exec fastlane android internal
        env:
          PLAY_STORE_JSON_KEY: ${{ secrets.PLAY_STORE_JSON_KEY }}

  ios-release:
    runs-on: macos-14
    steps:
      - uses: actions/checkout@v4
      - uses: ruby/setup-ruby@v1
        with: { ruby-version: '3.2' }
      - run: bundle install
      - name: Install certificates
        uses: apple-actions/import-codesign-certs@v2
        with:
          p12-file-base64: ${{ secrets.CERTIFICATES_P12 }}
          p12-password: ${{ secrets.CERTIFICATES_PASSWORD }}
      - name: Upload to TestFlight
        run: bundle exec fastlane ios beta
        env:
          APP_STORE_CONNECT_API_KEY_ID: ${{ secrets.ASC_KEY_ID }}
          APP_STORE_CONNECT_API_ISSUER_ID: ${{ secrets.ASC_ISSUER_ID }}

  web-release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - run: npm ci && npm run build
      - name: Deploy to Vercel
        run: vercel deploy --prod --token=${{ secrets.VERCEL_TOKEN }}
```

### Release Report Output

```
RELEASE MANAGEMENT REPORT
Application: [NAME]
Version: [X.Y.Z]
Date: [TODAY]
Release Manager: [NAME]

RELEASE SUMMARY
┌──────────────────────┬────────────────────────────────────┐
│ Field                │ Value                              │
├──────────────────────┼────────────────────────────────────┤
│ Release Type         │ [Major/Minor/Patch/Hotfix]         │
│ Platforms            │ [Android, iOS, Web]                │
│ Version              │ [X.Y.Z]                            │
│ Android versionCode  │ [NNNNN]                            │
│ iOS build number     │ [NNN]                              │
│ Features Included    │ [count]                            │
│ Bugs Fixed           │ [count]                            │
│ Rollout Status       │ [% / track]                        │
│ Crash Rate           │ [current vs baseline]              │
│ Rating Trend         │ [current vs previous version]      │
└──────────────────────┴────────────────────────────────────┘

DELIVERABLES GENERATED:
  - [ ] Version bumped across all platforms
  - [ ] Release branch cut and tagged
  - [ ] Platform-specific checklists completed
  - [ ] Staged rollout configured and monitoring active
  - [ ] ASO metadata updated (keywords, screenshots, descriptions)
  - [ ] Changelog generated (user-facing + developer)
  - [ ] Release monitoring dashboards configured
  - [ ] Fastlane / CI automation templates provided

CROSS-REFERENCES:
  - /ci-cd-pipeline — for build and deployment automation
  - /feature-flags — for coordinating flag rollouts with releases
  - /incident-response — for release rollback and hotfix procedures
  - /analytics-implementation — for tracking release impact on metrics
```

## Code Generation (Required)

Generate actual release automation files using Write:

1. **Fastlane** (if mobile): `fastlane/Fastfile` with lanes for beta and production
2. **Changelog**: `CHANGELOG.md` with Keep a Changelog format, populated from git log
3. **Version bump script**: `scripts/bump-version.sh` for semantic versioning
4. **Release workflow**: `.github/workflows/release.yml` with approval gates
5. **Rollback script**: `scripts/rollback.sh` that reverts to previous tagged version

Before generating, use Glob to find existing release configs and Grep git tags (`git tag --list`) to understand versioning history.
