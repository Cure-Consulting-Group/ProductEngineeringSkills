# CI/CD Pipeline

Continuous integration and deployment pipelines for mobile (Android/iOS), web (Next.js), and backend (Firebase). GitHub Actions first. Every project ships with automated build, test, and deploy from day one.

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

## Step 8: Monitoring Post-Deploy

After every production deploy, verify:
- [ ] App loads without errors (smoke test URL)
- [ ] Firebase Functions logs clean (no cold start errors)
- [ ] Crash reporting baseline unchanged (Firebase Crashlytics)
- [ ] Key user flows work (manual or E2E)
- [ ] No new error spikes in first 15 minutes
