---
name: ci-cd-pipeline
version: "1.0.0"
description: "Generate GitHub Actions workflows for build, test, deploy with environment configs and secrets management"
when_to_use: "Use when creating GitHub Actions workflows, deployment pipelines, or CI/CD configs. NOT for diagnosing CI failures (use ci-debugger agent)."
argument-hint: "[project-name]"
---

# CI/CD Pipeline

Continuous integration and deployment pipelines for mobile (Android/iOS), web (Next.js), and backend (Firebase). GitHub Actions first. Every project ships with automated build, test, and deploy from day one.

## Pre-Processing (Auto-Context)

Before starting, gather project context silently:
- Read `PORTFOLIO.md` if it exists in the project root or parent directories for product/team context
- Run: `cat package.json 2>/dev/null || cat build.gradle.kts 2>/dev/null || cat Podfile 2>/dev/null` to detect stack
- Run: `git log --oneline -5 2>/dev/null` for recent changes
- Run: `ls src/ app/ lib/ functions/ 2>/dev/null` to understand project structure
- Use this context to tailor all output to the actual project

## Step 1: Classify the Pipeline Type

| Project | Pipeline |
|---------|----------|
| Next.js + Firebase Hosting | Build → Test → Export → Deploy to Firebase |
| Next.js + Vercel | Push-to-deploy (Vercel handles CI) |
| Android app | Build → Lint → Test → Assemble → Firebase App Distribution / Play Store |
| iOS app | Build → Test → Archive → TestFlight / App Store (Fastlane) |
| Firebase Cloud Functions | Lint → Test → Deploy Functions |
| Monorepo (web + functions) | Matrix build: web and functions in parallel |
| Full stack (mobile + web + backend) | Separate workflows per platform, shared test gate |

## Step 2: Gather Context

1. **Platforms** — web, Android, iOS, backend, or combination?
2. **Hosting** — Firebase, Vercel, AWS, or other?
3. **Environments** — dev / staging / production? How many?
4. **Branch strategy** — trunk-based, GitFlow, or GitHub Flow?
5. **Secrets needed** — Firebase SA key, Play Store key, App Store Connect, Stripe keys?
6. **Test suite** — unit, integration, E2E? What runners?

## Step 3: Branch Strategy (Default: GitHub Flow)

```
main              — production, always deployable
feature/*         — feature branches, PR into main
hotfix/*          — urgent fixes, PR into main

Environments:
  PR preview       → deploy to preview URL (Vercel) or staging Firebase site
  main             → auto-deploy to production
  tags (v1.0.0)    → release builds (mobile)
```

## Step 4: Pipeline Templates

### Next.js + Firebase Hosting
```yaml
name: Deploy Web
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: 'npm' }
      - run: npm ci
      - run: npm run lint
      - run: npm run test -- --ci
      - run: npm run build
      - if: github.ref == 'refs/heads/main'
        uses: FirebaseExtended/action-hosting-deploy@v0
        with:
          repoToken: ${{ secrets.GITHUB_TOKEN }}
          firebaseServiceAccount: ${{ secrets.FIREBASE_SERVICE_ACCOUNT }}
          channelId: live
          projectId: ${{ vars.FIREBASE_PROJECT_ID }}
```

### Android (Gradle + Firebase App Distribution)
```yaml
name: Android CI
on:
  push:
    branches: [main]
  pull_request:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: temurin, java-version: 17 }
      - uses: gradle/actions/setup-gradle@v3
      - run: ./gradlew ktlintCheck
      - run: ./gradlew testDebugUnitTest
      - run: ./gradlew assembleRelease
      - if: github.ref == 'refs/heads/main'
        uses: wzieba/Firebase-Distribution-Github-Action@v1
        with:
          appId: ${{ secrets.FIREBASE_APP_ID_ANDROID }}
          serviceCredentialsFileContent: ${{ secrets.FIREBASE_SERVICE_ACCOUNT }}
          groups: internal-testers
          file: app/build/outputs/apk/release/app-release.apk
```

### iOS (Fastlane + TestFlight)
```yaml
name: iOS CI
on:
  push:
    branches: [main]
  pull_request:

jobs:
  build:
    runs-on: macos-14
    steps:
      - uses: actions/checkout@v4
      - uses: ruby/setup-ruby@v1
        with: { ruby-version: 3.2, bundler-cache: true }
      - run: bundle exec fastlane test
      - if: github.ref == 'refs/heads/main'
        run: bundle exec fastlane beta
        env:
          APP_STORE_CONNECT_API_KEY: ${{ secrets.ASC_API_KEY }}
          MATCH_PASSWORD: ${{ secrets.MATCH_PASSWORD }}
```

### Firebase Cloud Functions
```yaml
name: Deploy Functions
on:
  push:
    branches: [main]
    paths: ['functions/**']

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20, cache: 'npm', cache-dependency-path: functions/package-lock.json }
      - run: cd functions && npm ci
      - run: cd functions && npm run lint
      - run: cd functions && npm test
      - uses: w9jds/firebase-action@v13.22.1
        with:
          args: deploy --only functions
        env:
          GCP_SA_KEY: ${{ secrets.FIREBASE_SERVICE_ACCOUNT }}
          PROJECT_ID: ${{ vars.FIREBASE_PROJECT_ID }}
```

## Step 5: Environment & Secrets Management

```
GitHub Secrets (never in code):
  FIREBASE_SERVICE_ACCOUNT     — GCP service account JSON
  FIREBASE_APP_ID_ANDROID      — Firebase app ID
  ASC_API_KEY                  — App Store Connect API key (base64)
  MATCH_PASSWORD               — iOS code signing
  KEYSTORE_PASSWORD            — Android signing key
  STRIPE_SECRET_KEY            — only in Functions deploy

GitHub Variables (non-sensitive):
  FIREBASE_PROJECT_ID          — project identifier
  ENVIRONMENT                  — dev / staging / production
```

Rules:
- **Never** commit secrets, .env files, service account keys, or keystores
- Use GitHub Environment protection rules for production deploys (require approval)
- Rotate secrets quarterly

## Step 6: Quality Gates

Every PR must pass before merge:

```
Required checks:
  ✅ Lint passes (no warnings)
  ✅ Unit tests pass (100%)
  ✅ Build succeeds
  ✅ No new TypeScript errors
  ✅ Code review approved (1+ reviewer)

Recommended checks:
  ⬜ E2E tests pass
  ⬜ Bundle size delta < 10%
  ⬜ Lighthouse score >= 90
  ⬜ Security scan clean (Dependabot / Snyk)
```

## Step 7: Rollback Procedures

```
Firebase Hosting:  firebase hosting:clone SOURCE_SITE:PREVIOUS_VERSION TARGET_SITE:live
Cloud Functions:   Redeploy previous commit: git revert HEAD && git push
Android:           Firebase App Distribution → promote previous build
iOS:               TestFlight → expire current build, previous is auto-available
Vercel:            Dashboard → Deployments → Promote previous
```

Never force-push main. Always revert-and-push-forward.

## Code Generation (Required)

You MUST generate actual workflow files using the Write tool:

1. **CI workflow**: `.github/workflows/ci.yml` — lint, type-check, test, build (matrix for affected platforms)
2. **Deploy workflow**: `.github/workflows/deploy.yml` — staging auto-deploy, production with approval
3. **Release workflow**: `.github/workflows/release.yml` — version bump, changelog, tag, publish

Before generating, use Glob to find existing workflows (`.github/workflows/*.yml`) and Read them to understand current setup. Adapt, don't duplicate.

Use Grep to find test commands in package.json/build.gradle to set correct test steps.

## Cross-References

- `/infrastructure-scaffold` — for Firebase, GCP, Vercel, and Docker configs the pipeline deploys
- `/testing-strategy` — for test runner commands and coverage thresholds to enforce in CI
- `/security-review` — for secret scanning and SAST steps to add to the pipeline
- `/e2e-testing` — for E2E workflow integration and sharding patterns

## Step 8: Monitoring Post-Deploy

After every production deploy, verify:
- [ ] App loads without errors (smoke test URL)
- [ ] Firebase Functions logs clean (no cold start errors)
- [ ] Crash reporting baseline unchanged (Firebase Crashlytics)
- [ ] Key user flows work (manual or E2E)
- [ ] No new error spikes in first 15 minutes
