# offline-first: platform code samples

Read this file when generating or reviewing platform code for the offline-first skill. SKILL.md holds the decisions; this holds the sample implementations. Versions are in SKILL.md "Tech Stack Defaults".

## Contents
- Sync metadata on local entities (Room, SwiftData)
- Firestore persistence setup (web, Android, iOS)
- Optimistic write (Android ViewModel)
- Background sync (WorkManager, BGTaskScheduler, Service Worker)
- Connectivity monitor (Android)

## Sync metadata on local entities

### Android (Room)
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

### iOS (SwiftData)
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

## Firestore persistence setup

```typescript
// Web (modular SDK) — memory cache is the default; opt in to IndexedDB persistence
import { initializeFirestore, persistentLocalCache, persistentMultipleTabManager } from 'firebase/firestore';
const db = initializeFirestore(app, {
  localCache: persistentLocalCache({ tabManager: persistentMultipleTabManager() }),
});
// Cold cache read without a prior listener:
import { getDocsFromCache, query, collection } from 'firebase/firestore';
const cached = await getDocsFromCache(query(collection(db, 'orders')));
```

```kotlin
// Android — persistent disk cache is the default; set size explicitly when needed
firestore.firestoreSettings = firestoreSettings {
    setLocalCacheSettings(persistentCacheSettings { setSizeBytes(200L * 1024 * 1024) })
}
// Cache-only read: collectionRef.get(Source.CACHE)
```

iOS: persistence is on by default; configure with `PersistentCacheSettings(sizeBytes:)` on `FirestoreSettings.cacheSettings`.

## Optimistic write (Android ViewModel)
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

## Background sync

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

### Web (Service Worker + Background Sync API, Chromium only)
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

Feature-detect `'sync' in ServiceWorkerRegistration.prototype`; otherwise drain the queue on page load, on the `online` event, and on `visibilitychange`.

## Connectivity monitor (Android)
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
