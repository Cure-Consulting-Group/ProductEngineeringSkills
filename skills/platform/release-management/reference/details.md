# release-management: detailed reference

> Reference material for the `release-management` skill, split out for progressive disclosure. Loaded on demand from SKILL.md.

## Contents
- Step 5: App Store Optimization (ASO)
- Step 8: Fastlane / CI Automation

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
