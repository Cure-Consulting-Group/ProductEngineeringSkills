# CI/CD Pipeline

GitHub Actions pipelines for Cure projects: web (Next.js), Android, iOS, and Firebase backends.
**Done when** the repo has CI on every PR (lint, type-check, test, build), staging deploys on merge to
`main`, production deploys behind an environment approval, keyless GCP auth, and a written rollback
path per platform. Deliver the requested workflows; don't refactor app code or add unrequested jobs.

## Pre-Processing (Auto-Context)

Context (pre-filled in Claude Code; in other runtimes run these commands first):

- Existing workflows: !`(ls .github/workflows/ 2>/dev/null || echo "(none)") | head -15`
- Scripts: !`(grep -A15 '"scripts"' package.json 2>/dev/null || echo "(no package.json)") | head -16`
- Platforms: !`(ls -d android ios functions app apps firebase.json apphosting.yaml vercel.json 2>/dev/null || echo "(none detected)") | head -10`

Read any existing workflow before writing a new one — adapt, don't duplicate.

## Step 1: Classify

| Request | Output |
|---|---|
| New pipeline (greenfield) | `ci.yml` + `deploy.yml` (+ `release.yml` for mobile) |
| Add a platform/job to an existing pipeline | Edit the existing workflow |
| Review/harden an existing pipeline | Findings list (pins, permissions, secrets, gates) — no new files |
| Question (how do I…) | Answer with the relevant snippet |

| Project | Pipeline |
|---|---|
| Next.js on Firebase **App Hosting** (Cure default for Firebase + Next) | CI in Actions; App Hosting builds and rolls out on push to its live branch — don't duplicate the build |
| Next.js on Vercel | CI in Actions; Vercel Git integration deploys previews and production |
| Static site on Firebase Hosting | Build → deploy with firebase-tools |
| Android | Lint → unit test → assemble → App Distribution (testers) / Play (via release-management) |
| iOS | Test → archive → TestFlight via Fastlane |
| Cloud Functions | Lint → test → `firebase deploy --only functions` |
| Monorepo | Path-filtered jobs, shared test gate |

## Step 2: Gather Context

Ask only for what the repo doesn't answer: platforms, hosting, environments (dev/staging/prod),
required secrets (App Store Connect, Play, Stripe), and test runners.

## Step 3: Cure Pipeline Policy

- **Branching and release policy is owned by the `release-management` skill** — link to it, don't
  restate it. The CI view of it: PRs → CI + preview; merge to `main` → auto-deploy **staging**;
  **production** deploys only from a release tag or `release/*` branch through a GitHub Environment
  with required reviewers. `main` never auto-deploys production.
- Follow `rules/cicd.md`: actions pinned by full commit SHA (tag in a trailing comment), a
  `permissions:` block on every workflow, `concurrency` groups, `timeout-minutes` on every job.
- **Keyless GCP auth.** Use Workload Identity Federation via `google-github-actions/auth` with
  **service-account impersonation** (`service_account:` input), then run `firebase-tools` directly.
  Gotchas: direct WIF (no impersonation) is not supported by the Firebase Admin SDK and its tokens
  expire in 5 minutes; `FirebaseExtended/action-hosting-deploy` still requires a JSON key, so skip it
  for keyless deploys. Long-lived `FIREBASE_SERVICE_ACCOUNT` JSON keys are legacy — migrate them.
- Node: 24 (Active LTS) for new projects; 22 is maintenance LTS until 2027-04-30; 20 is EOL
  (2026-04-30). Match the `engines` field and the Cloud Functions runtime.
- Runners: `ubuntu-24.04`, `macos-26` (pin the version, not `-latest`, for reproducible Xcode).

## Step 4: Templates

Pins below were current on 2026-09-23 (checkout v7.0.1, setup-node v7.0.0, setup-java v6.0.1,
gradle/actions v6.3.0, setup-ruby v1.326.0, auth v3.0.0, firebase-tools 15.x). Refresh SHAs with
`gh api repos/<owner>/<action>/commits/<tag> --jq .sha` when writing new files.

### CI (every PR, web/functions)
```yaml
name: CI
on: { pull_request: {}, push: { branches: [main] } }
permissions: { contents: read }
concurrency: { group: ci-${{ github.ref }}, cancel-in-progress: true }
jobs:
  ci:
    runs-on: ubuntu-24.04
    timeout-minutes: 20
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
      - uses: actions/setup-node@820762786026740c76f36085b0efc47a31fe5020 # v7.0.0
        with: { node-version: 24, cache: npm }
      - run: npm ci
      - run: npm run lint && npx tsc --noEmit
      - run: npm test -- --ci
      - run: npm run build
```

### Deploy Firebase (keyless) — staging on `main`, production on tag with approval
```yaml
name: Deploy
on: { push: { branches: [main], tags: ['v*'] } }
permissions: { contents: read, id-token: write }
jobs:
  deploy:
    runs-on: ubuntu-24.04
    timeout-minutes: 20
    environment: ${{ startsWith(github.ref, 'refs/tags/') && 'production' || 'staging' }}
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
      - uses: actions/setup-node@820762786026740c76f36085b0efc47a31fe5020 # v7.0.0
        with: { node-version: 24, cache: npm }
      - run: npm ci && npm run build
      - uses: google-github-actions/auth@7c6bc770dae815cd3e89ee6cdf493a5fab2cc093 # v3.0.0
        with:
          workload_identity_provider: ${{ vars.GCP_WIF_PROVIDER }}
          service_account: ${{ vars.GCP_DEPLOY_SA }}
      - run: npx firebase-tools@15 deploy --only hosting,functions --project ${{ vars.FIREBASE_PROJECT_ID }} --non-interactive
```
The `production` environment carries required reviewers; `vars.*` are per-environment.

### Android
```yaml
      - uses: actions/setup-java@de7274f081f381c8f8158605e0321c36c376e2e6 # v6.0.1
        with: { distribution: temurin, java-version: 17 }
      - uses: gradle/actions/setup-gradle@9c971963bec38e04b3d30dcc455b5382be2fdbfb # v6.3.0
      - run: ./gradlew ktlintCheck testDebugUnitTest assembleRelease
      # testers build, after the auth step above:
      - run: npx firebase-tools@15 appdistribution:distribute app/build/outputs/apk/release/app-release.apk --app ${{ vars.FIREBASE_APP_ID_ANDROID }} --groups internal-testers
```

### iOS (Fastlane → TestFlight), on `macos-26`
```yaml
      - uses: ruby/setup-ruby@762794c140bbeda0f1224786aa33b4b46783a6c1 # v1.326.0
        with: { bundler-cache: true }   # reads .ruby-version
      - run: bundle exec fastlane test
      - if: startsWith(github.ref, 'refs/tags/')
        run: bundle exec fastlane beta
        env:
          APP_STORE_CONNECT_API_KEY: ${{ secrets.ASC_API_KEY }}
          MATCH_PASSWORD: ${{ secrets.MATCH_PASSWORD }}
```

## Step 5: Secrets and Gates

- Secrets only for what has no keyless path: `ASC_API_KEY`, `MATCH_PASSWORD`, Android keystore +
  password, Play service-account JSON (whether Fastlane `supply` can upload keylessly: confirm before use).
  Non-secrets (project IDs, WIF provider, SA email) go in environment `vars`.
- Required checks on `main`: lint, type-check, unit tests, build, one approving review. Coverage
  thresholds come from the `testing-strategy` skill; don't restate them here.
- Recommended: E2E (see `e2e-testing`), bundle-size delta, secret scanning and SAST (see
  `security-review`), Dependabot.

## Step 6: Rollback per Platform

| Platform | Rollback |
|---|---|
| Firebase Hosting | `firebase hosting:clone SITE_ID@PREVIOUS_VERSION_ID SITE_ID:live` (or console → Release history → Roll back) |
| App Hosting | Console → Rollouts → "Roll back to this build"; CLI: `firebase apphosting:rollouts:create BACKEND_ID --git_commit <good-sha>` |
| Cloud Functions | `git revert` the change and let the pipeline redeploy |
| Vercel | Instant Rollback / promote the previous deployment |
| Android (Play) | Halt the staged rollout; a fix needs a new build with a higher versionCode (Play won't re-serve an older one) |
| iOS (App Store) | Pause phased release, then ship a fix with a higher build number (request expedited review if needed). TestFlight has no rollback — expiring a build doesn't restore production. |

Never force-push `main`; revert and roll forward.

## Code/Artifact Generation

Applies only when Step 1 classified the request as a new pipeline or an addition to one. Write:

- New pipeline → `.github/workflows/ci.yml` and `.github/workflows/deploy.yml`; mobile projects also
  get `.github/workflows/release.yml` (tag-triggered store build).
- Addition → edit the existing workflow file in place.

Review and question requests get findings or an answer, not files. After deploys, the smoke check is
part of the deploy job (health URL, Crashlytics/Sentry baseline) — see the `observability` skill.

## Cross-References

- `infrastructure-scaffold` — Firebase/GCP/Vercel/Docker configs the pipeline deploys
- `release-management` — branching, versioning, staged rollouts, store submission
- `testing-strategy` — test commands and coverage thresholds
- `security-review` — secret scanning and SAST steps
- `e2e-testing` — E2E sharding in CI
