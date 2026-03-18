# Feature Flags

Designs and implements feature flag systems for progressive rollouts, A/B experimentation, operational kill switches, and permission-based access control. Covers Firebase Remote Config, LaunchDarkly, and custom implementations across Android, iOS, and web. Every flag has a lifecycle, an owner, and a cleanup date.

## Pre-Processing (Auto-Context)

Before starting, gather project context silently:
- Read `PORTFOLIO.md` if it exists in the project root or parent directories for product/team context
- Run: `cat package.json 2>/dev/null || cat build.gradle.kts 2>/dev/null || cat Podfile 2>/dev/null` to detect stack
- Run: `git log --oneline -5 2>/dev/null` for recent changes
- Run: `ls src/ app/ lib/ functions/ 2>/dev/null` to understand project structure
- Use this context to tailor all output to the actual project

**Hard rules:**
- Every feature flag has an owner, a creation date, and a maximum lifespan
- Flags older than 90 days without renewal are tech debt — schedule cleanup
- Kill switches must work without a deploy (server-side evaluation)
- A/B tests require a hypothesis, success metric, and minimum sample size BEFORE launch
- Default values must be safe — if the flag service is unreachable, the app must still work
- Never nest feature flags more than 2 levels deep — complexity kills debuggability

## Step 1: Classify the Flag Type

| Flag Type | Purpose | Lifespan | Example |
|-----------|---------|----------|---------|
| Release Toggle | Gate incomplete features during development | Days–weeks (remove after launch) | `show_new_checkout_flow` |
| Experiment / A/B | Test hypotheses with controlled rollout | 2–6 weeks (remove after analysis) | `experiment_pricing_page_v2` |
| Ops Toggle / Kill Switch | Disable features during incidents without deploy | Permanent (always present) | `kill_switch_video_upload` |
| Permission Toggle | Enable features for specific user segments | Long-lived (tied to entitlements) | `enable_premium_analytics` |

## Step 2: Gather Context

Before implementing, confirm:

1. **Feature name** — what is being flagged and why?
2. **Platform(s)** — Android, iOS, web, backend (Cloud Functions), or all?
3. **Flag provider** — Firebase Remote Config, LaunchDarkly, Statsig, Flagsmith, or custom?
4. **User segmentation** — do you need targeting by user ID, geography, app version, subscription tier, or percentage rollout?
5. **Analytics integration** — what metrics define success? Is an A/B test required?
6. **Rollback needs** — how quickly must you be able to disable this feature? Seconds (kill switch) or minutes (config update)?
7. **Dependencies** — does this flag interact with other flags or feature configurations?

## Step 3: Flag Architecture

### Naming Conventions

```
Pattern: {type}_{feature}_{variant}

Types:
  release_    — release toggle (temporary)
  exp_        — experiment / A/B test (temporary)
  ops_        — operational toggle / kill switch (permanent)
  perm_       — permission toggle (long-lived)

Examples:
  release_new_onboarding_flow
  exp_checkout_single_page
  ops_kill_switch_image_processing
  perm_premium_export_csv

Rules:
  - snake_case always
  - Maximum 50 characters
  - No version numbers in flag names (use variants instead)
  - Prefix makes flag type instantly recognizable in dashboards
```

### Flag Lifecycle

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│ PROPOSED │────▶│ CREATED  │────▶│  ACTIVE  │────▶│ COMPLETE │────▶│ ARCHIVED │
└──────────┘     └──────────┘     └──────────┘     └──────────┘     └──────────┘
                      │                │                │
                      │                │                ▼
                      │                │          ┌──────────┐
                      │                └─────────▶│ CLEANUP  │
                      │                           └──────────┘
                      ▼
                 ┌──────────┐
                 │ REJECTED │
                 └──────────┘

State definitions:
  PROPOSED:  PR/ticket created requesting the flag
  CREATED:   Flag exists in provider with default value (off)
  ACTIVE:    Flag is being used for rollout or experiment
  COMPLETE:  Rollout is 100% or experiment concluded — flag value is decided
  CLEANUP:   Code removal PR created — removing flag checks from codebase
  ARCHIVED:  Flag deleted from provider, code cleaned up
  REJECTED:  Flag proposal denied (not needed, wrong approach)
```

### Flag Ownership Registry

```
Maintain a flag registry (Notion, Google Sheet, or YAML in repo):

flags:
  - name: release_new_onboarding_flow
    type: release
    owner: "@jane"
    created: 2026-01-15
    max_age: 2026-03-15      # 60 days max for release toggles
    status: active
    description: "New user onboarding with personalization quiz"
    platforms: [android, ios, web]
    jira: PROJ-1234
    cleanup_pr: null          # filled when cleanup starts

  - name: ops_kill_switch_video_upload
    type: ops
    owner: "@platform-team"
    created: 2025-06-01
    max_age: permanent
    status: active
    description: "Emergency disable for video upload pipeline"
    platforms: [android, ios, web, backend]
    jira: PROJ-800
    cleanup_pr: null          # never — permanent flag
```

## Step 4: Platform Implementation Patterns

### Android (Firebase Remote Config)

```kotlin
// Flag provider abstraction — never call Remote Config directly in features
interface FeatureFlagProvider {
    fun isEnabled(flag: String): Boolean
    fun getString(flag: String): String
    fun getInt(flag: String): Int
    suspend fun refresh()
}

class FirebaseFeatureFlagProvider @Inject constructor(
    private val remoteConfig: FirebaseRemoteConfig
) : FeatureFlagProvider {

    init {
        val configSettings = remoteConfigSettings {
            minimumFetchIntervalInSeconds = if (BuildConfig.DEBUG) 0 else 3600
        }
        remoteConfig.setConfigSettingsAsync(configSettings)
        remoteConfig.setDefaultsAsync(R.xml.remote_config_defaults)
    }

    override fun isEnabled(flag: String): Boolean =
        remoteConfig.getBoolean(flag)

    override fun getString(flag: String): String =
        remoteConfig.getString(flag)

    override fun getInt(flag: String): Int =
        remoteConfig.getLong(flag).toInt()

    override suspend fun refresh() {
        remoteConfig.fetchAndActivate().await()
    }
}

// Usage in ViewModel — clean, testable
class OnboardingViewModel @Inject constructor(
    private val flags: FeatureFlagProvider
) : ViewModel() {

    val showNewOnboarding: Boolean
        get() = flags.isEnabled("release_new_onboarding_flow")
}

// Local defaults: res/xml/remote_config_defaults.xml
// EVERY flag must have a safe default (feature OFF for release toggles)
<?xml version="1.0" encoding="utf-8"?>
<defaultsMap>
    <entry>
        <key>release_new_onboarding_flow</key>
        <value>false</value>
    </entry>
    <entry>
        <key>ops_kill_switch_video_upload</key>
        <value>false</value>  <!-- false = feature is ON (kill switch not triggered) -->
    </entry>
</defaultsMap>
```

### iOS (Firebase Remote Config)

```swift
// Protocol-based abstraction for testability
protocol FeatureFlagProvider {
    func isEnabled(_ flag: String) -> Bool
    func string(for flag: String) -> String
    func refresh() async throws
}

final class FirebaseFeatureFlagProvider: FeatureFlagProvider {
    private let remoteConfig = RemoteConfig.remoteConfig()

    init() {
        let settings = RemoteConfigSettings()
        #if DEBUG
        settings.minimumFetchInterval = 0
        #else
        settings.minimumFetchInterval = 3600
        #endif
        remoteConfig.configSettings = settings
        remoteConfig.setDefaults(fromPlist: "RemoteConfigDefaults")
    }

    func isEnabled(_ flag: String) -> Bool {
        remoteConfig.configValue(forKey: flag).boolValue
    }

    func string(for flag: String) -> String {
        remoteConfig.configValue(forKey: flag).stringValue ?? ""
    }

    func refresh() async throws {
        let status = try await remoteConfig.fetchAndActivate()
        if status == .error {
            throw FeatureFlagError.refreshFailed
        }
    }
}

// Usage in SwiftUI
struct OnboardingView: View {
    @EnvironmentObject var flags: FeatureFlagProvider

    var body: some View {
        if flags.isEnabled("release_new_onboarding_flow") {
            NewOnboardingView()
        } else {
            LegacyOnboardingView()
        }
    }
}
```

### Web (Next.js + Edge Config or Firebase Remote Config)

```typescript
// Server-side flag evaluation (Next.js middleware or server component)
// Prefer server-side evaluation to avoid flash of content

// Option 1: Firebase Remote Config (server-side)
import { initializeServerApp } from 'firebase/app';
import { getRemoteConfig, fetchAndActivate, getValue } from 'firebase/remote-config';

export async function getFlags(): Promise<Record<string, boolean>> {
  const rc = getRemoteConfig(app);
  await fetchAndActivate(rc);
  return {
    newOnboarding: getValue(rc, 'release_new_onboarding_flow').asBoolean(),
    killSwitchVideoUpload: getValue(rc, 'ops_kill_switch_video_upload').asBoolean(),
  };
}

// Option 2: Vercel Edge Config (fastest for web)
import { get } from '@vercel/edge-config';

export async function getFlag(flag: string): Promise<boolean> {
  return (await get<boolean>(flag)) ?? false; // default to false if unreachable
}

// Client-side hydration — pass flags from server to client
// In layout.tsx:
export default async function RootLayout({ children }: { children: React.ReactNode }) {
  const flags = await getFlags();
  return (
    <html>
      <body>
        <FeatureFlagProvider flags={flags}>
          {children}
        </FeatureFlagProvider>
      </body>
    </html>
  );
}

// React context for client components
'use client';
const FeatureFlagContext = createContext<Record<string, boolean>>({});

export function useFlag(flag: string): boolean {
  const flags = useContext(FeatureFlagContext);
  return flags[flag] ?? false;
}
```

## Step 5: A/B Testing Framework

### Experiment Design Template

```
EXPERIMENT: [Name]
Hypothesis:    [If we {change}, then {metric} will {improve/decrease} by {amount}]
               Example: "If we show a single-page checkout instead of multi-step,
               then conversion rate will increase by 15%"

Primary metric:   [One metric that defines success — e.g., checkout conversion rate]
Secondary metrics: [Supporting metrics — e.g., average order value, time to complete]
Guardrail metrics: [Metrics that must NOT degrade — e.g., error rate, refund rate]

Variants:
  - Control (A): current experience [50% of traffic]
  - Treatment (B): new experience [50% of traffic]
  - (Optional) Treatment (C): alternate new experience [33% each if 3-way]

Targeting:
  - User segment: [all users / new users / premium tier / geography]
  - Exclusions: [internal users, test accounts, users in other experiments]

Sample size calculation:
  Baseline conversion: [current rate, e.g., 3.2%]
  Minimum detectable effect: [e.g., 15% relative lift = 3.68% target]
  Statistical significance: 95% (alpha = 0.05)
  Statistical power: 80% (beta = 0.20)
  Required sample per variant: [calculate — e.g., ~15,000 users per variant]
  Estimated duration: [based on daily traffic — e.g., 14 days at 2000 users/day]

Decision rules:
  - If primary metric improves with p < 0.05 and no guardrail regressions → ship Treatment
  - If no significant difference after 2x estimated duration → ship Control (cheaper)
  - If guardrail metric regresses significantly → stop experiment immediately
```

### Analytics Integration

```
Firebase Analytics event tagging:
  // On flag evaluation, log the variant assignment
  analytics.logEvent('experiment_assigned', {
    experiment_name: 'exp_checkout_single_page',
    variant: 'treatment_b',
    user_id: userId,
    timestamp: serverTimestamp,
  });

  // On conversion event, include experiment context
  analytics.logEvent('purchase_complete', {
    experiment_name: 'exp_checkout_single_page',
    variant: 'treatment_b',
    order_value: 49.99,
  });

BigQuery analysis query:
  SELECT
    variant,
    COUNT(DISTINCT user_id) AS users,
    COUNTIF(event_name = 'purchase_complete') AS conversions,
    COUNTIF(event_name = 'purchase_complete') / COUNT(DISTINCT user_id) AS conversion_rate
  FROM analytics_events
  WHERE experiment_name = 'exp_checkout_single_page'
    AND event_date BETWEEN '2026-03-01' AND '2026-03-14'
  GROUP BY variant;
```

## Step 6: Progressive Rollout Strategy

### Standard Rollout Stages

```
Stage 1: Internal (dogfood)
  Audience:  Internal team only (whitelist by user ID)
  Duration:  2-5 days
  Criteria:  No crashes, no critical bugs, team approval
  Rollback:  Instant — disable flag

Stage 2: Canary (1%)
  Audience:  1% of production users (random)
  Duration:  1-3 days
  Criteria:  Error rate stable, no crash spike, latency unchanged
  Rollback:  Instant — disable flag
  Monitoring: Crashlytics, error rate, latency p95

Stage 3: Early Adopters (10%)
  Audience:  10% of production users
  Duration:  3-5 days
  Criteria:  All Stage 2 criteria + user feedback neutral/positive
  Rollback:  Instant — disable flag
  Monitoring: All Stage 2 + support ticket volume, NPS if available

Stage 4: Half Rollout (50%)
  Audience:  50% of production users
  Duration:  3-7 days
  Criteria:  All Stage 3 criteria + A/B metrics positive (if experiment)
  Rollback:  Disable flag — 50% of users revert

Stage 5: Full Rollout (100%)
  Audience:  All users
  Duration:  7 days observation
  Criteria:  All metrics stable at 100%
  Action:    Schedule flag cleanup — the feature is now permanent

Automatic rollback triggers (at any stage):
  - Crash rate increases >0.5% above baseline
  - Error rate increases >1% above baseline
  - Latency p95 increases >50% above baseline
  - Manual kill switch activated by on-call
```

### Firebase Remote Config Rollout Configuration

```
// Firebase Remote Config conditions (in Firebase Console):
Condition: "Canary 1%"
  → User in random percentile: 0-1%

Condition: "Early Adopters 10%"
  → User in random percentile: 0-10%

Condition: "Half Rollout 50%"
  → User in random percentile: 0-50%

Condition: "Internal Team"
  → User ID in: ["uid1", "uid2", "uid3"]
  → OR: App version contains "debug"

// Parameter value:
release_new_onboarding_flow:
  Default: false
  Internal Team: true
  Canary 1%: true
  Early Adopters 10%: true
  Half Rollout 50%: true
```

## Step 7: Flag Hygiene

### Maximum Flag Age by Type

```
┌──────────────────┬─────────────┬──────────────────────────────────┐
│ Flag Type        │ Max Age     │ Action at Expiry                 │
├──────────────────┼─────────────┼──────────────────────────────────┤
│ Release Toggle   │ 60 days     │ Must be at 100% or removed       │
│ Experiment       │ 45 days     │ Must have conclusion and cleanup  │
│ Ops / Kill Switch│ Permanent   │ Annual review for relevance       │
│ Permission Toggle│ 1 year      │ Annual review, re-justify         │
└──────────────────┴─────────────┴──────────────────────────────────┘
```

### Dead Flag Detection

```
Automated detection (run weekly in CI):

1. Scan codebase for flag references:
   grep -rn "isEnabled\|getFlag\|useFlag\|remote_config" --include="*.kt" --include="*.swift" --include="*.ts" --include="*.tsx"

2. Compare against flag registry:
   - Flag in code but NOT in registry → undocumented flag (violation)
   - Flag in registry but NOT in code → dead flag (schedule deletion)
   - Flag in registry past max_age → overdue cleanup (create ticket)

3. Generate dead flag report:
   DEAD FLAG REPORT — [DATE]
   ┌──────────────────────────────┬────────┬────────────┬──────────┐
   │ Flag Name                    │ Type   │ Created    │ Age      │
   ├──────────────────────────────┼────────┼────────────┼──────────┤
   │ release_old_payment_flow     │ release│ 2025-11-01 │ 134 days │
   │ exp_homepage_layout_v2       │ exp    │ 2025-12-15 │ 89 days  │
   └──────────────────────────────┴────────┴────────────┴──────────┘
   ACTION: Create cleanup PRs for the above flags.
```

### Tech Debt Cleanup Process

```
Cleanup PR checklist:
  - [ ] Remove all flag evaluation code (if/else branches)
  - [ ] Keep the winning code path; delete the losing path
  - [ ] Remove flag from local defaults (XML, plist, JSON)
  - [ ] Remove flag from provider (Firebase Console, LaunchDarkly)
  - [ ] Remove flag from registry
  - [ ] Update tests (remove flag-specific test variants)
  - [ ] Verify no other flags depend on the removed flag

Cleanup sprint: dedicate 10% of each sprint to flag cleanup (non-negotiable)
```

## Step 8: CI/CD Integration

### Flag-Aware Deployments

```
GitHub Actions workflow addition:

- name: Flag status check
  run: |
    # List all active flags and their rollout percentages
    echo "## Active Feature Flags" >> $GITHUB_STEP_SUMMARY
    echo "| Flag | Type | Rollout | Owner |" >> $GITHUB_STEP_SUMMARY
    echo "|------|------|---------|-------|" >> $GITHUB_STEP_SUMMARY
    # Parse flag registry and output table
    yq '.flags[] | select(.status == "active") |
      "| " + .name + " | " + .type + " | " + (.rollout // "N/A") + " | " + .owner + " |"' \
      flags.yml >> $GITHUB_STEP_SUMMARY

- name: Dead flag check
  run: |
    # Fail CI if any flags exceed max age
    OVERDUE=$(yq '.flags[] | select(.status == "active" and .max_age != "permanent") |
      select(.max_age < now | strftime("%Y-%m-%d"))' flags.yml)
    if [ -n "$OVERDUE" ]; then
      echo "::error::Overdue feature flags detected. Create cleanup PRs."
      echo "$OVERDUE"
      exit 1
    fi
```

### PR Description Flag Annotation

```
PR template addition (add to .github/pull_request_template.md):

## Feature Flags
<!-- If this PR adds, modifies, or removes a feature flag, fill in below -->

| Action | Flag Name | Type | Owner | Cleanup Date |
|--------|-----------|------|-------|--------------|
| Added/Modified/Removed | `flag_name` | release/exp/ops/perm | @owner | YYYY-MM-DD |

**Rollout plan:** [Link to rollout plan or describe stages]
```

### Automated Flag Cleanup Reminders

```
GitHub Action (scheduled weekly):

name: Feature Flag Hygiene Check
on:
  schedule:
    - cron: '0 9 * * 1'  # Every Monday at 9 AM

jobs:
  flag-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Check flag age
        run: |
          # Parse flags.yml, find overdue flags, create issues
          # Post summary to Slack #engineering channel
```

### Feature Flag Report Output

```
FEATURE FLAG REPORT
Application: [NAME]
Date: [TODAY]
Engineer: [NAME]

FLAG INVENTORY
┌──────────────────────┬────────┬────────────────┬──────────────┐
│ Flag Name            │ Type   │ Status         │ Cleanup Date │
├──────────────────────┼────────┼────────────────┼──────────────┤
│ [flag_name]          │ [type] │ [rollout %]    │ [date]       │
└──────────────────────┴────────┴────────────────┴──────────────┘

DELIVERABLES GENERATED:
  - [ ] Flag architecture (naming, lifecycle, ownership)
  - [ ] Platform implementations (Android, iOS, Web)
  - [ ] A/B test design (hypothesis, metrics, sample size)
  - [ ] Progressive rollout plan (stages, criteria, triggers)
  - [ ] Flag hygiene automation (dead flag detection, CI checks)
  - [ ] Cleanup process documented

CROSS-REFERENCES:
  - /release-management — for coordinating flag rollouts with app releases
  - /analytics-implementation — for experiment event tracking and analysis
  - /ci-cd-pipeline — for flag-aware deployment workflows
  - /testing-strategy — for testing both flag states
```

## Automated Flag Discovery

Before defining flag strategy, scan existing codebase:

1. **Find existing flags**: Grep for flag patterns:
   - `isEnabled|getFlag|useFeatureFlag|remoteConfig|LaunchDarkly|Unleash|getBoolean`
2. **Find dead flags**: Grep for flags that exist in config but have no code references
3. **Find hardcoded toggles**: Grep for `if (true)` or `if (false)` or `#if DEBUG` blocks that should be flags

## Code Generation (Required)

Generate flag infrastructure using Write:

1. **Flag registry**: `config/feature-flags.yml` with all flags, owners, and expiry dates
2. **Dead flag detector**: `scripts/check-dead-flags.sh` that cross-references registry with codebase
3. **CI check**: `.github/workflows/flag-hygiene.yml` that runs dead flag detection on PR
