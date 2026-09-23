# feature-flags: detailed reference

> Read when writing the flag provider for a specific platform (Step 4 of the `feature-flags` skill).

## Contents
- Step 4: Platform Implementation Patterns

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

### Web (Next.js + Firebase Remote Config server templates or Vercel Edge Config)

```typescript
// Server-side flag evaluation (Server Component or route handler) avoids a flash of content.

// Option 1: Firebase Remote Config server templates (Admin SDK; the client
// `firebase/remote-config` package is browser-only and does not run on the server)
import { getRemoteConfig } from 'firebase-admin/remote-config';

export async function getFlags(userId: string): Promise<Record<string, boolean>> {
  const template = await getRemoteConfig().getServerTemplate({
    defaultConfig: { release_new_onboarding_flow: false, ops_kill_switch_video_upload: false },
  }); // cache the template (e.g. refresh every 60s) rather than fetching per request
  const config = template.evaluate({ randomizationId: userId }); // stable % bucketing
  return {
    newOnboarding: config.getBoolean('release_new_onboarding_flow'),
    killSwitchVideoUpload: config.getBoolean('ops_kill_switch_video_upload'),
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
  const flags = await getFlags(await currentUserId()); // your auth helper
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
