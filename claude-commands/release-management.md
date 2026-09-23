# Release Management

Outcome: a release plan (or executed release artifacts) for Android, iOS, and/or web in which
every step is staged, monitored, and reversible. Done when the version numbers, the rollout
schedule with halt thresholds, the rollback path per platform, and the release notes exist.
Match length to the need; no filler sections.

This skill owns the **Cure branch and release policy**; `ci-cd-pipeline` and
`infrastructure-scaffold` implement it and link here rather than restating it.

## Branch and release policy (Cure standard)

- `main` is always releasable and auto-deploys to **staging** on merge.
- **Production** deploys only from a version tag (`vX.Y.Z`) cut from `main` — or from a
  `release/X.Y` branch when a release needs stabilization or a hotfix on an older line — and
  runs in a CI `production` environment with manual approval.
- Mobile production is always a staged rollout; never 100% on day one.
- Every release names its rollback path before it ships (flag kill switch, rollout halt, or
  roll-forward hotfix).

## Pre-Processing (Auto-Context)

Context (pre-filled in Claude Code; in other runtimes run these commands first):

- Recent tags: !`git tag --sort=-creatordate 2>/dev/null | head -5 || echo "(no tags)"`
- Commits since last tag: !`git log --oneline "$(git describe --tags --abbrev=0 2>/dev/null)..HEAD" 2>/dev/null | head -15 || echo "(none)"`
- Versions: !`grep -hE "versionName|versionCode|MARKETING_VERSION|\"version\":" app/build.gradle.kts package.json *.xcodeproj/project.pbxproj 2>/dev/null | sort -u | head -6 || echo "(not found)"`
- Release tooling: !`ls fastlane/Fastfile release-please-config.json .changeset .github/workflows/release*.yml 2>/dev/null || echo "(none)"`

## Step 1: Classify the Release

| Type | Bump | Rollout | Sign-off |
|------|------|---------|----------|
| Major | X.0.0 | Internal → Beta → 1% → 10% → 50% → 100% | Full QA + stakeholder |
| Minor | x.Y.0 | Internal → Beta → 5% → 25% → 100% | QA + team lead |
| Patch | x.y.Z | Internal → 10% → 50% → 100% | QA |
| Hotfix | x.y.Z | Internal → 25% → 100% (accelerated) | Engineering lead |
| Beta / TestFlight | x.y.z-beta.N | Internal + opt-in testers | None external |

Also note whether the request is a **plan/checklist**, **automation setup**, or **rollback now** —
it decides what Code/Artifact Generation produces.

## Step 2: Gather Context

Ask only for what the auto-context didn't answer: platforms and channels (Play tracks,
TestFlight, Vercel, Firebase Hosting), current production version per platform, flags tied to
this release, accepted known issues, privacy-policy or data-safety changes, and new strings
awaiting translation.

## Step 3: Versioning

- SemVer for the user-visible version; pre-releases `1.2.0-beta.1`, `1.2.0-rc.1`.
- **Android** `versionCode` = `MAJOR*10000 + MINOR*100 + PATCH` (2.5.3 → 20503). It must strictly
  increase on every upload, so leave headroom: a rollback build of 2.5.2 code ships as 2.5.4
  (20504), never as 20502.
- **iOS** build number = CI build number (ever-incrementing) — avoids duplicate-build rejections.
- **Web**: tag `vX.Y.Z`; deploy label `X.Y.Z-<shortsha>`.

## Step 4: Release Checklist (gotchas only — the model knows the generic list)

**Android:** archive the R8 mapping file; include a baseline profile; update the Data safety form
when data collection changed; the base module's compressed per-device download must stay under
Play's 200 MB cap (move extras to Play Feature/Asset Delivery). Rollout: 1% day 0 → 5% day 1
(if crash < 1%, ANR < 0.5%) → 10% day 2 → 25% day 3 → 50% day 5 → 100% day 7.

**iOS:** archive dSYMs; external TestFlight groups need beta review (allow 1–2 days); update
privacy nutrition labels; add review notes with a test account. Phased release is fixed at 7
days (1/2/5/10/20/50/100%) and only affects automatic updates — manual updaters get it at once.

**Web:** E2E against the preview deployment; Lighthouse Performance > 90, Accessibility > 95;
production env vars verified; promote the reviewed preview rather than rebuilding.

## Step 5: Rollback Paths

| Platform | Fastest | Full rollback |
|---|---|---|
| Android | Remote-config kill switch; halt staged rollout in Play Console (stops new installs) | Play will not re-promote an older build: rebuild the last good code with a **higher** `versionCode` and roll it out, or roll forward with a fix |
| iOS | Kill switch; pause phased release | Approved versions can't be pulled — submit a fix and request expedited review |
| Vercel | Instant rollback to the previous production deployment | Same |
| Firebase Hosting | Console → Release history → Roll back | `firebase hosting:clone SITE_ID@VERSION_ID SITE_ID:live` |

Decision matrix: crash rate > 2× baseline → halt and investigate; > 5× or any data loss/corruption
→ roll back now; ANR > 0.47% → halt; API error rate up > 1 pt → halt; revenue down > 10% vs
forecast → halt; rating down > 0.3 stars → PM decides; security vulnerability → hotfix or roll back.

## Step 6: Changelogs and Release Notes

Two outputs, deliberately different:
- **Developer changelog** (`CHANGELOG.md`, GitHub release) — generated from Conventional Commits
  by release-please (or Changesets in JS monorepos). Don't hand-edit it; fix the commit messages.
  (standard-version is deprecated.)
- **User-facing release notes** (store "What's new") — a human curates these from the `feat`/`fix`
  entries in plain language. Limits: Play 500 characters per locale, App Store 4,000.

## Step 7: Release Monitoring

- Android vitals bad-behavior thresholds: user-perceived crash rate 1.09%, ANR 0.47%. Cure
  targets: crash < 0.5%, ANR < 0.2%.
- iOS: crash rate < 1% of sessions (target < 0.3%); watch hangs, terminations, disk writes.
- Web: JS error rate < 0.1% of page loads; Core Web Vitals LCP < 2.5 s, INP < 200 ms, CLS < 0.1.
- Alerts: crash > 2× baseline after rollout start → page on-call; > 3× → auto-halt; rating
  drop > 0.2 stars in 48 h → product team.

## Step 8: ASO and Fastlane

Read [reference/details.md](reference/details.md) when the request covers store listing
optimization (section "Step 5: App Store Optimization") or release automation — Fastlane lanes
and the tag-triggered GitHub Actions release workflow (section "Step 8: Fastlane / CI Automation").

## Code/Artifact Generation

Applies only when Step 1 identified **automation setup**. A plan/checklist request gets the plan;
a **rollback now** request gets the Step 5 commands for the affected platform, nothing else.
Check existing release config and `git tag --list` first, then write only what's missing:

| File | When |
|---|---|
| `fastlane/Fastfile` (beta + production lanes) | Mobile |
| `release-please-config.json` + workflow, or `.changeset/` | No changelog automation yet |
| `.github/workflows/release.yml` (tag-triggered, `production` environment approval) | No release workflow yet |
| `scripts/bump-version.sh` | Version codes computed by hand today |

## Cross-References

`ci-cd-pipeline` (workflow implementation), `feature-flags` (kill switches), `observability`
(rollout dashboards and alerts), `incident-response` (when a release causes an incident).
