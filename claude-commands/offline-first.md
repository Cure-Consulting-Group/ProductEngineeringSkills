# Offline-First Architecture

Local-first persistence, deterministic sync, conflict resolution decided per entity, and UX that never blocks on the network.

**Done when:** every entity in scope has a storage location, a sync strategy, and a conflict rule; the write path is local-first with an idempotent sync queue; and the offline test scenarios below have an owner. For an audit, done is a gap report with severity per finding.

## Pre-Processing (Auto-Context)

Context (pre-filled in Claude Code; in other runtimes run these commands first):

- Local data layer in use: !`grep -rlE "androidx.room|SwiftData|CoreData|dexie|idb|persistentLocalCache|enableIndexedDbPersistence|WorkManager|BGTaskScheduler" --include=*.kts --include=*.gradle --include=*.swift --include=*.ts --include=*.json . 2>/dev/null | grep -v node_modules | head -10 || echo "(none found)"`

## Invariants

These protect user data, which is why they are fixed rather than per-project choices:
- The app launches and shows meaningful content with zero connectivity.
- Writes persist locally first, then sync; every sync operation is idempotent.
- Conflict strategy is chosen per entity at design time.
- Users see their own changes immediately; offline is a subtle indicator, never a blocking error.
- Local data is never silently dropped — rejected writes are surfaced with a recovery option.

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
7. **Current backend** — Firestore (built-in offline cache), REST, GraphQL?
8. **Compliance** — any data that must NOT be stored locally? (PII restrictions, HIPAA)

## Step 3: Local Storage Strategy

| Data | Android | iOS | Web |
|------|---------|-----|-----|
| Structured entities + sync queue | Room | SwiftData (iOS 17+) / Core Data | IndexedDB via Dexie 4 or idb |
| Preferences | DataStore | UserDefaults | localStorage (small, non-secret only) |
| Files / media | Files + Coil 3 disk cache | FileManager + URLCache | Cache API (Service Worker) |

Every syncable entity carries sync metadata: `syncStatus` (SYNCED/PENDING/CONFLICT/FAILED), `localVersion`, `serverVersion`, `lastSyncedAt`. Read [reference/platform-code.md](reference/platform-code.md) when generating the entity models, persistence setup, or background workers.

### Firestore offline persistence (current APIs)

- **Web:** memory cache is the default. Opt in with `initializeFirestore(app, { localCache: persistentLocalCache({ tabManager: persistentMultipleTabManager() }) })`. `enableIndexedDbPersistence` / `enableMultiTabIndexedDbPersistence` are deprecated.
- **Android:** persistent cache is on by default; configure through `setLocalCacheSettings(PersistentCacheSettings…)` — `isPersistenceEnabled` / `setCacheSizeBytes` are deprecated.
- **iOS:** on by default; configure with `PersistentCacheSettings` on `cacheSettings`.
- Cache threshold defaults to 100 MB with LRU cleanup. Cold cache reads work without a listener via `getDocsFromCache` / `Source.CACHE`. Use `includeMetadataChanges` + `fromCache` / `hasPendingWrites` to drive sync indicators.
- **Firestore offline is not enough** when you need complex local queries, custom conflict rules (Firestore is last-write-wins per field), write queues with business-level retry, or local-only data — add Room/SwiftData/IndexedDB on top.

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

## Step 5: Optimistic UI

- Save locally with `PENDING`, enqueue the sync op, let the UI update from the local store (Room Flow, SwiftData `@Query`, Dexie `liveQuery`).
- Pending items show a small sync icon; `FAILED` items show a retry control; never a modal.
- Server rejects a create → remove locally and say so; an update → revert to last synced version and show what was lost; a delete → restore the item.
- Validation failures reopen the edit form with the server's errors.

## Step 6: Background Sync

- **Android:** WorkManager — unique periodic work (15-minute minimum) with `NetworkType.CONNECTED`, exponential backoff, plus one-time work on reconnect. Chain upload → download → resolve. Foreground service only for transfers over ~10 minutes.
- **iOS:** `BGAppRefreshTask` (~30 s budget) for light sync, `BGProcessingTask` for heavy sync; silent push can trigger a fetch but is throttled — design for infrequent execution.
- **Web:** the Background Sync API is **Chromium-only** (no Safari, no Firefox), and Periodic Background Sync requires an installed PWA. Always ship the fallback: drain the queue on load, on the `online` event, and on `visibilitychange`.

## Step 7: Network State

- Android `ConnectivityManager.NetworkCallback` (+ `NET_CAPABILITY_VALIDATED` to catch captive portals), iOS `NWPathMonitor` (`isExpensive`, `isConstrained` for data-saver), web `navigator.onLine` only as a hint — confirm with a real request.
- Debounce connectivity flaps (~1 s, VPNs fire repeatedly). Distinguish no-network from server-down in the UI.
- On metered or constrained networks: essential sync only, thumbnails, no prefetch.

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

## Step 9: Output

Deliver, scaled to the Step-1 classification: storage schema with sync metadata; sync flow (local write → queue → server → reconcile); a per-entity conflict matrix (`Entity | Field | Strategy | Notes`); background-sync configuration per platform; and the offline test plan. Match length to the need; no filler sections.

## Tech Stack Defaults (verified 2026-09-23)

```yaml
android: Room 2.8, DataStore 1.2, WorkManager 2.11, Coil 3.x
ios:     SwiftData (iOS 17+) or Core Data, BGTaskScheduler, NWPathMonitor
web:     Dexie 4.x or idb, Service Worker + Cache API, Background Sync where supported
firestore: persistentLocalCache (web), default persistent cache (mobile)
conflicts: field-level merge default; CRDT (Yjs, Automerge) for real-time co-editing
```

## Code/Artifact Generation

Applies when Step 1 calls for building. Detect the data layer first and extend existing sync code. Generate only for platforms in scope:

1. Sync queue — `data/sync/SyncQueue.kt` (Room + WorkManager), `Data/Sync/SyncQueue.swift` (SwiftData + BGTaskScheduler), or `src/sync/sync-queue.ts` (IndexedDB + service worker)
2. Conflict resolver implementing the per-entity matrix
3. Network monitor that triggers queue drain
4. Optimistic-update helper (temporary IDs, rollback)

## Cross-References

`database-architect` (local schema), `firebase-architect` (Firestore config and rules), `testing-strategy` (where offline tests sit and coverage targets), `performance-review` (battery and sync budgets), `notification-architect` (silent push triggers).
