---
name: offline-first
description: "Architect offline-first mobile apps — local storage, sync strategies, conflict resolution, optimistic UI, and background sync patterns"
argument-hint: "[feature-or-project]"
---

# Offline-First Architecture

Architects production-grade offline-first applications across Android, iOS, and web. Every output enforces local-first data persistence, deterministic sync, explicit conflict resolution, and seamless UX regardless of connectivity. If your app breaks without internet, it is not ready for production.

## Pre-Processing (Auto-Context)

Before starting, gather project context silently:
- Read `PORTFOLIO.md` if it exists in the project root or parent directories for product/team context
- Run: `cat package.json 2>/dev/null || cat build.gradle.kts 2>/dev/null || cat Podfile 2>/dev/null` to detect stack
- Run: `git log --oneline -5 2>/dev/null` for recent changes
- Run: `ls src/ app/ lib/ functions/ 2>/dev/null` to understand project structure
- Use this context to tailor all output to the actual project

## Core Principle: The Network is a Lie

```
Offline-first     →  App works fully without network; syncs when connectivity returns
Cache-first       →  App shows cached data immediately, refreshes in background
Graceful degrade  →  Core features work offline, advanced features require network
Sync-critical     →  Data must be consistent across devices with conflict resolution
```

**Hard rules:**
- The app must launch and show meaningful content with zero network connectivity
- All write operations are persisted locally FIRST, then synced to the server
- Every sync operation is idempotent — replaying the same operation produces the same result
- Conflict resolution strategy is defined per entity at design time — never at runtime panic
- Users always see their own local changes immediately (optimistic UI is default)
- Network status is never shown as a blocking error — show a subtle indicator and continue
- Data integrity is non-negotiable: local data must never be silently dropped or corrupted during sync

## Step 1: Classify the Offline Need

| Request | Primary Output | Action |
|---------|---------------|--------|
| Full offline-first | Local DB + sync engine + conflict resolution | Architect full stack |
| Graceful degradation | Caching layer + offline fallbacks | Add offline resilience |
| Cache-first reads | Cache strategy + background refresh | Implement caching |
| Sync-critical data | Sync queue + conflict resolution + idempotency | Design sync system |
| Background sync | Platform-specific background task setup | Configure background sync |
| Offline audit | Connectivity failure analysis + gap report | Audit existing app |

## Step 2: Gather Context

Before generating, confirm:
1. **Platforms** — Android, iOS, web, or all three?
2. **Data model complexity** — how many entity types? Relationships? Nested data?
3. **Conflict likelihood** — single-user device data (low), shared/collaborative data (high)?
4. **Connectivity patterns** — always-on WiFi, intermittent mobile, field work with no signal?
5. **Data volume** — how much data needs to be available offline? (KB, MB, GB)
6. **Sync frequency** — real-time, periodic, manual, or on-reconnect?
7. **Current backend** — Firestore (has built-in offline), REST API, GraphQL?
8. **Compliance** — any data that must NOT be stored locally? (PII restrictions, HIPAA)

## Step 3: Local Storage Strategy

### Android

| Storage Type | Use For | Technology | Max Size |
|-------------|---------|------------|----------|
| Structured data | Entities, relationships, queries | Room (SQLite) | Device storage |
| Preferences | Settings, flags, simple key-value | DataStore (Proto/Preferences) | ~1MB practical |
| Files/media | Images, documents, cached assets | File storage + coil disk cache | Device storage |
| Sync queue | Pending operations | Room table | Device storage |

```kotlin
// Room entity with sync metadata
@Entity(tableName = "orders")
data class OrderEntity(
    @PrimaryKey val id: String,
    val customerId: String,
    val status: String,
    val total: Double,
    val updatedAt: Long,
    // Sync metadata
    val syncStatus: SyncStatus,  // SYNCED, PENDING, CONFLICT, FAILED
    val localVersion: Int,
    val serverVersion: Int,
    val lastSyncedAt: Long?
)

enum class SyncStatus { SYNCED, PENDING, CONFLICT, FAILED }
```

### iOS

| Storage Type | Use For | Technology | Max Size |
|-------------|---------|------------|----------|
| Structured data | Entities, relationships, queries | SwiftData / Core Data | Device storage |
| Preferences | Settings, flags, simple key-value | UserDefaults | ~1MB practical |
| Files/media | Images, documents, cached assets | FileManager + URLCache | Device storage |
| Sync queue | Pending operations | SwiftData table | Device storage |

```swift
// SwiftData model with sync metadata
@Model
class Order {
    @Attribute(.unique) var id: String
    var customerId: String
    var status: String
    var total: Double
    var updatedAt: Date
    // Sync metadata
    var syncStatus: SyncStatus
    var localVersion: Int
    var serverVersion: Int
    var lastSyncedAt: Date?
}

enum SyncStatus: String, Codable {
    case synced, pending, conflict, failed
}
```

### Web

| Storage Type | Use For | Technology | Max Size |
|-------------|---------|------------|----------|
| Structured data | Entities, queries | IndexedDB (via Dexie.js or idb) | ~50MB-unlimited (with permission) |
| Preferences | Settings, tokens | localStorage | 5-10MB |
| Cached assets | Pages, images, API responses | Cache API (Service Worker) | Browser-managed |
| Sync queue | Pending operations | IndexedDB table | Browser-managed |

### Firestore Offline Persistence

- Firestore has built-in offline persistence — enable it and get offline reads/writes for free
- **Android:** `FirebaseFirestore.getInstance().firestoreSettings = firestoreSettings { isPersistenceEnabled = true }`
- **iOS:** persistence is enabled by default
- **Web:** `enableIndexedDbPersistence(db)` or `enableMultiTabIndexedDbPersistence(db)` for multi-tab
- **Limitations:** cache size defaults to 100MB (configurable), no offline query indexing, listener-based reads only (no cold cache queries without prior listener)
- **When Firestore offline is NOT enough:** complex local queries, custom conflict resolution, offline write queues with retry logic, local-only data

## Step 4: Sync Architecture

### Sync Strategy Selection

| Strategy | Best For | Complexity | Data Loss Risk |
|----------|----------|-----------|----------------|
| Last-write-wins (LWW) | User settings, preferences, non-collaborative data | Low | Medium (silent overwrite) |
| Server-wins | Read-heavy data, admin-controlled content | Low | Low |
| Client-wins | Offline-heavy workflows, field data collection | Low | Medium |
| Field-level merge | Forms, profiles, entities with independent fields | Medium | Low |
| Operational transform | Real-time collaborative editing (docs, whiteboards) | Very high | Very low |
| CRDT | Distributed counters, sets, collaborative data | High | Very low |

**Default recommendation:** Field-level merge for most business applications. Use LWW only for truly independent per-user data.

### Conflict Resolution Patterns

**Field-Level Merge:**
```
Server version:  { name: "Alice",  email: "alice@old.com", phone: "555-1234" }
Client version:  { name: "Alice",  email: "alice@new.com", phone: "555-1234" }
                                    ↑ client changed email
Server update:   { name: "Alice",  email: "alice@old.com", phone: "555-9999" }
                                                            ↑ server changed phone

Merged result:   { name: "Alice",  email: "alice@new.com", phone: "555-9999" }
                                    ↑ client wins email     ↑ server wins phone
```

- Track which fields the client modified (dirty field set)
- On sync: only push dirty fields, accept server values for non-dirty fields
- If both client and server modified the same field → escalate to conflict UI or apply priority rule

**Manual Conflict Resolution UI:**
- Show both versions side-by-side with diff highlighting
- Let user pick per-field or accept one version entirely
- Required for collaborative data where automated merge is insufficient
- Store conflict state in local DB — don't block the user; let them resolve later

### Sync Queue Design

```
sync_queue table:
  id: auto-increment
  entityType: string           ← "order", "profile", etc.
  entityId: string             ← remote entity ID
  operation: "CREATE" | "UPDATE" | "DELETE"
  payload: JSON                ← serialized entity or delta
  dirtyFields: string[]        ← for field-level merge
  createdAt: timestamp
  retryCount: int
  maxRetries: int (default 5)
  nextRetryAt: timestamp       ← exponential backoff
  status: "PENDING" | "IN_PROGRESS" | "FAILED" | "COMPLETED"
```

- Process queue FIFO within each entity, parallel across entities
- Idempotency key: `{entityType}:{entityId}:{operation}:{contentHash}`
- On conflict (HTTP 409): mark entity as CONFLICT, surface in UI
- On permanent failure (HTTP 4xx except 409): mark as FAILED, alert user
- On transient failure (HTTP 5xx, timeout): retry with exponential backoff (1s, 2s, 4s, 8s, 16s, cap at 5min)

### Delta Sync vs Full Sync

- **Delta sync (preferred):** only transmit changes since last sync timestamp
  - Server endpoint: `GET /entities?updatedAfter={lastSyncTimestamp}`
  - Requires server to never hard-delete — use soft delete with `deletedAt` timestamp
  - Client stores `lastSyncTimestamp` per entity type
- **Full sync (fallback):** download entire dataset
  - Use when: first launch, sync timestamp is too old (>30 days), data integrity check fails
  - Paginate: never download unbounded result sets
  - Trigger automatically if delta sync returns inconsistent data

## Step 5: Optimistic UI Patterns

### Immediate Local Feedback

```kotlin
// Android — ViewModel pattern
fun placeOrder(order: Order) {
    viewModelScope.launch {
        // 1. Save locally with PENDING status
        val localOrder = order.copy(syncStatus = SyncStatus.PENDING)
        localRepository.save(localOrder)
        // UI updates immediately via Room Flow

        // 2. Enqueue sync operation
        syncQueue.enqueue(SyncOperation.Create("order", localOrder))

        // 3. Sync engine processes queue when online
        // On success: update syncStatus to SYNCED
        // On failure: update syncStatus to FAILED, show retry option
    }
}
```

### Pending State Indicators

- Subtle sync icon on items with `PENDING` status (small cloud with arrow)
- Do NOT block user interaction while sync is pending
- Show "Syncing..." in a non-intrusive status bar, not a modal
- Items with `FAILED` status show a retry button — tapping retries immediately

### Rollback on Failure

- If server rejects a create: remove from local DB, show "Could not save — please try again" toast
- If server rejects an update: revert to last synced version, show diff of what was lost
- If server rejects a delete: restore the item locally, show "Could not delete" message
- Never silently discard user data — always inform and offer recovery

### Error Recovery UX

| Scenario | User Experience |
|----------|----------------|
| Offline, user creates item | Item saved locally, shown with sync-pending icon |
| Comes online, sync succeeds | Sync icon disappears, item fully saved |
| Comes online, sync conflicts | Badge on item, tap to resolve conflict |
| Comes online, sync fails (server error) | Retry icon, automatic retry with backoff |
| Comes online, sync fails (validation) | Error message, edit form reopens with issues highlighted |

## Step 6: Background Sync

### Android (WorkManager)

```kotlin
// Periodic background sync
val syncWork = PeriodicWorkRequestBuilder<SyncWorker>(
    repeatInterval = 15, repeatIntervalTimeUnit = TimeUnit.MINUTES
).setConstraints(
    Constraints.Builder()
        .setRequiredNetworkType(NetworkType.CONNECTED)
        .setRequiresBatteryNotLow(true)
        .build()
).setBackoffCriteria(
    BackoffPolicy.EXPONENTIAL, 30, TimeUnit.SECONDS
).build()

WorkManager.getInstance(context).enqueueUniquePeriodicWork(
    "periodic_sync", ExistingPeriodicWorkPolicy.KEEP, syncWork
)
```

- Use `PeriodicWorkRequest` for regular sync (min 15-minute interval)
- Use `OneTimeWorkRequest` for immediate sync on connectivity change
- Chain workers: `uploadPendingChanges` → `downloadServerChanges` → `resolveConflicts`
- Use `Foreground Service` only for large uploads/downloads that take >10 minutes

### iOS (BGTaskScheduler)

```swift
// Register background task
BGTaskScheduler.shared.register(
    forTaskWithIdentifier: "com.app.sync",
    using: nil
) { task in
    handleBackgroundSync(task: task as! BGAppRefreshTask)
}

// Schedule
let request = BGAppRefreshTaskRequest(identifier: "com.app.sync")
request.earliestBeginDate = Date(timeIntervalSinceNow: 15 * 60)
try BGTaskScheduler.shared.submit(request)
```

- `BGAppRefreshTask` for lightweight sync (30s execution window)
- `BGProcessingTask` for heavy sync (minutes, requires power + WiFi)
- Silent push notifications can trigger immediate background fetch
- iOS aggressively throttles background tasks — design for infrequent execution

### Web (Service Worker + Background Sync API)

```javascript
// Register sync event
navigator.serviceWorker.ready.then(registration => {
    return registration.sync.register('sync-pending-changes');
});

// Service worker handles sync
self.addEventListener('sync', event => {
    if (event.tag === 'sync-pending-changes') {
        event.waitUntil(processPendingSyncQueue());
    }
});
```

- Background Sync API fires when connectivity is restored — even if page is closed
- Periodic Background Sync (`periodicSync`) requires site to be installed as PWA
- Fallback: sync on page load if Background Sync is not supported

## Step 7: Network State Management

### Connectivity Detection

```kotlin
// Android — ConnectivityManager with Flow
class NetworkMonitor @Inject constructor(
    context: Context
) {
    val isOnline: Flow<Boolean> = callbackFlow {
        val connectivityManager = context.getSystemService<ConnectivityManager>()
        val callback = object : ConnectivityManager.NetworkCallback() {
            override fun onAvailable(network: Network) { trySend(true) }
            override fun onLost(network: Network) { trySend(false) }
        }
        connectivityManager?.registerDefaultNetworkCallback(callback)
        awaitClose { connectivityManager?.unregisterNetworkCallback(callback) }
    }.distinctUntilChanged()
}
```

- **Android:** `ConnectivityManager.NetworkCallback` — reactive, battery-efficient
- **iOS:** `NWPathMonitor` — observe `currentPath.status`
- **Web:** `navigator.onLine` + `online`/`offline` events (unreliable) — verify with actual fetch

### Bandwidth-Aware Behavior

| Bandwidth | Behavior |
|-----------|----------|
| High (WiFi) | Full sync, download images at full resolution, prefetch next pages |
| Medium (4G/5G) | Normal sync, compressed images, no prefetch |
| Low (3G/Edge) | Essential sync only, thumbnail images, pagination reduced |
| None (offline) | Local data only, queue all writes, show offline indicator |

- **Android:** check `NetworkCapabilities.NET_CAPABILITY_NOT_METERED` for WiFi detection
- **iOS:** check `NWPath.isExpensive` and `NWPath.isConstrained`
- Respect user's data saver settings — reduce sync frequency on metered connections

### Airplane Mode and Edge Cases

- Airplane mode with WiFi: treat as connected (hotel WiFi, airplane WiFi)
- Captive portal: `ConnectivityManager` may report connected but HTTP requests fail — detect via connectivity check endpoint
- VPN: may cause connectivity callbacks to fire repeatedly — debounce with 1s delay
- Server maintenance: distinguish between no-network and server-down (different UI treatment)

## Step 8: Testing Offline Scenarios

### Network Condition Simulation

- **Android:** use `ConnectivityManager` mock in tests; for manual testing, use Android Emulator's network settings or Charles Proxy throttling
- **iOS:** use Network Link Conditioner (Xcode Additional Tools) for realistic network profiles
- **Web:** Chrome DevTools → Network → Offline / throttling profiles
- **CI:** intercept HTTP layer in tests, simulate offline/slow/error responses

### Test Scenarios (Minimum Coverage)

| Scenario | Expected Behavior |
|----------|-------------------|
| App launch while offline | Shows cached data, no crash, no blocking spinner |
| Create item while offline | Saved locally, shown immediately, sync icon visible |
| Edit item while offline | Local update applied, sync queued |
| Delete item while offline | Removed from UI, soft-deleted locally, sync queued |
| Go online after offline edits | Sync queue processes, all changes uploaded |
| Conflict during sync | Conflict UI shown, user can resolve |
| Server rejects sync operation | Error shown, user can retry or discard |
| Kill app while offline, reopen | Pending operations survive, queue intact |
| Background sync fires | Queue processed without user interaction |
| Token expired during sync | Auth refresh triggered, sync retries automatically |

### Data Integrity Verification

- After sync, verify local data matches server data (checksum or version comparison)
- Periodic full-sync reconciliation (e.g., weekly) to catch drift
- Log and alert on data inconsistencies — never silently accept mismatched state
- Write integration tests that simulate multi-device sync scenarios

### Sync Conflict Reproduction

- Automated test: modify same entity on two "devices" (two test instances) while offline, bring both online
- Verify conflict detection fires and resolution produces expected result
- Test all configured conflict strategies (LWW, field-merge, manual)
- Verify no data loss in any conflict scenario — compare pre-conflict and post-resolution data

## Step 9: Output Templates

For every offline-first architecture, deliver:

1. **Storage layer diagram** — local DB schema with sync metadata fields
2. **Sync architecture diagram** — flow from local write → queue → sync → server → reconcile
3. **Conflict resolution matrix** — per-entity strategy with field-level rules
4. **Background sync configuration** — platform-specific WorkManager/BGTask/ServiceWorker setup
5. **Offline test plan** — scenario table with expected behaviors

### Sync Status Dashboard Template
```
| Entity | Local Count | Server Count | Pending | Conflicts | Last Sync |
|--------|------------|--------------|---------|-----------|-----------|
| Orders | 142 | 140 | 2 | 0 | 2 min ago |
| Products | 89 | 89 | 0 | 0 | 5 min ago |
| Messages | 1,203 | 1,198 | 3 | 2 | 1 min ago |
```

### Conflict Resolution Matrix Template
```
| Entity | Field | Strategy | Priority | Notes |
|--------|-------|----------|----------|-------|
| Order | status | Server wins | — | Server is authoritative for status |
| Order | notes | Field merge | Client | User's notes take priority |
| Profile | email | Server wins | — | Email verified server-side |
| Profile | displayName | LWW | — | Non-critical, last write wins |
| Message | content | Client wins | — | User authored the content |
```

## Tech Stack Defaults

```yaml
android:
  local_db: Room 2.6.x (SQLite)
  preferences: DataStore (Preferences or Proto)
  sync: WorkManager 2.9.x
  network_monitor: ConnectivityManager + Flow
  image_cache: Coil 2.x with disk cache
ios:
  local_db: SwiftData (iOS 17+) or Core Data
  preferences: UserDefaults
  sync: BGTaskScheduler + URLSession background tasks
  network_monitor: NWPathMonitor
  image_cache: URLCache + AsyncImage
web:
  local_db: IndexedDB via Dexie.js 4.x or idb
  sync: Background Sync API + Service Worker
  cache: Cache API for assets, stale-while-revalidate for API
  network_monitor: navigator.onLine + periodic health check
firestore:
  offline: enableIndexedDbPersistence (web), default on (mobile)
  cache_size: 100MB default, increase for data-heavy apps
  listeners: onSnapshot for real-time, getDoc for one-shot cached reads
conflict_resolution:
  default: field-level merge
  fallback: manual resolution UI
  collaborative: evaluate CRDT (Yjs, Automerge) for real-time co-editing
```

## Code Generation (Required)

Generate offline-first infrastructure using Write:

1. **Sync queue** (Android): `data/sync/SyncQueue.kt` — Room-backed operation queue with WorkManager
2. **Sync queue** (iOS): `Data/Sync/SyncQueue.swift` — SwiftData-backed queue with BGTaskScheduler
3. **Sync queue** (Web): `src/sync/sync-queue.ts` — IndexedDB-backed queue with service worker
4. **Conflict resolver**: `src/sync/conflict-resolver.ts` — last-write-wins or custom merge strategy
5. **Network monitor**: `src/sync/network-monitor.ts` — connectivity detection and queue drain trigger
6. **Optimistic UI helper**: `src/sync/optimistic.ts` — temporary ID management and rollback

Before generating, Grep for existing offline/sync code and detect which data layer is in use (Room, SwiftData, IndexedDB).

## Cross-References

- `/database-architect` — schema design for local storage and sync metadata tables
- `/firebase-architect` — Firestore offline persistence configuration and security rules
- `/testing-strategy` — offline test scenarios in the testing pyramid
- `/performance-review` — sync performance budgets and battery impact monitoring
- `/notification-architect` — silent push notifications to trigger background sync
- `/i18n` — offline-available localized strings
