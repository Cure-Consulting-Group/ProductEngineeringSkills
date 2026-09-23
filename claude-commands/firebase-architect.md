# Firebase Architect

**Outcome:** a Firebase feature design that is secure by default and keeps Firebase out of the domain layer — collection tree, document shapes, access-pattern → index table, security rules with emulator tests, and any server logic as Functions v2. Done when every collection the clients touch has a rule and a rules test, every query has an index, and no domain or presentation code imports a Firebase type. Path rules in `rules/firebase.md` (Claude Code) carry the same standards for code edits.

## Pre-Processing (Auto-Context)

Context (pre-filled in Claude Code; in other runtimes run these commands first):

- Firebase files: !`ls firebase.json firestore.rules storage.rules firestore.indexes.json 2>/dev/null || echo "(none)"`
- Databases and functions config: !`grep -nE '"(database|source|runtime)"' firebase.json 2>/dev/null | head -8 || echo "(no firebase.json)"`
- Functions runtime: !`grep -nE '"(node|firebase-functions|firebase-admin)"' functions/package.json 2>/dev/null | head -4 || echo "(no functions/)"`

## Step 1: Classify

| Request | Output |
|---|---|
| Data model | Collection tree + document shapes + access-pattern/index table + rules |
| Security rules | `firestore.rules` changes + rules unit tests |
| Server logic | Functions v2 trigger or callable + idempotency plan |
| Client data layer | DTO + data source + repository impl (Android/iOS/web) |
| Full feature | All of the above, scoped to the feature |
| Review or question | Findings with severity, or an answer; no files |

## Step 2: Gather Context

Confirm: feature and collections (new or existing), who reads/writes what (owner, org member, admin, public), offline needs (then pair with `offline-first`), scale, and whether a named database is in use.

## Step 3: Data Model Rules

- **Clean Architecture boundary:** no `FirebaseFirestore`, `DocumentReference`, `Timestamp`, or `DocumentSnapshot` above the data layer. DTOs map to domain models in the repository; listeners become `Flow` via `callbackFlow` (Android) or `AsyncStream` (iOS); writes return `Result`.
- **IDs:** `users/{uid}` uses the Auth UID; entities use auto-IDs; slugs only for known-key lookups. No sequential or date-prefixed IDs on high-write collections (index hotspots) — store the time in a field.
- **Shape:** subcollection for unbounded or separately secured children; arrays only for small bounded sets; 1 MiB doc cap; ~1 sustained write/sec per document, so shard counters.
- **Timestamps:** `createdAt`/`updatedAt` set with `FieldValue.serverTimestamp()` (`import { FieldValue } from 'firebase-admin/firestore'` on the server; `serverTimestamp()` from `firebase/firestore` on web). Rules enforce `request.resource.data.updatedAt == request.time`.
- **Denormalized copies** are listed in the design with the Function that maintains each one.
- **Named databases** (up to 100 per project) for residency or hard tenant isolation only; each has its own rules, indexes, and `firebase.json` entry, and triggers must pass `database: '<id>'`.

## Step 4: Security Rules Patterns

Deny by default; every `match` is explicit. Patterns Cure uses:

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    function signedIn() { return request.auth != null; }
    function isOwner(uid) { return signedIn() && request.auth.uid == uid; }
    function hasRole(role) { return signedIn() && request.auth.token.role == role; } // custom claim, set server-side
    function onlyChanges(keys) { return request.resource.data.diff(resource.data).affectedKeys().hasOnly(keys); }

    match /users/{uid} {
      allow read: if isOwner(uid) || hasRole('admin');
      allow create: if isOwner(uid)
        && request.resource.data.keys().hasOnly(['displayName', 'createdAt', 'updatedAt'])
        && request.resource.data.createdAt == request.time;
      allow update: if isOwner(uid) && onlyChanges(['displayName', 'updatedAt'])
        && request.resource.data.updatedAt == request.time;
      allow delete: if false; // deletion goes through a Function that cleans up subcollections
    }
  }
}
```

- Privileged fields (`role`, `plan`, `credits`, `status`) are never client-writable; they change only via Admin SDK in Functions. Use custom claims for roles, not a client-readable `role` field.
- `list` queries must be constrained by the rule (rules are not filters): a rule `resource.data.ownerId == request.auth.uid` requires the client query to include `where('ownerId', '==', uid)`.
- Minimise `get()`/`exists()` lookups in hot rules — each is a billed read and adds latency.
- Every rule change ships with `@firebase/rules-unit-testing` tests against the emulator (allowed and denied cases). Mirror the same discipline in `storage.rules` (content type + size limits per path).

## Step 5: Cloud Functions v2

- Triggers from `firebase-functions/v2/firestore`: `onDocumentCreated`, `onDocumentUpdated`, `onDocumentDeleted`, `onDocumentWritten` (not the v1 `onCreate`/`onWrite`). HTTPS/callables from `firebase-functions/v2/https`.
- Delivery is at-least-once: make handlers idempotent (use `event.id` or a deterministic target ID) and guard against self-triggering loops when a trigger writes to the document it watches.
- Admin SDK is modular: `initializeApp()` from `firebase-admin/app`, `getFirestore()` from `firebase-admin/firestore`, `getAuth()` from `firebase-admin/auth`.
- Callables that clients invoke set `enforceAppCheck: true`; set `region` and `minInstances` explicitly for latency-sensitive paths; secrets via `defineSecret`, never plain env vars.

## Step 6: App Check

Enable App Check for Firestore, Storage, Functions, and any AI/Vertex endpoints before launch: Play Integrity (Android), App Attest with DeviceCheck fallback (iOS), reCAPTCHA Enterprise (web). Roll out in monitor mode, watch the verified-request ratio in the console, then enforce. Debug providers only in debug builds; register CI debug tokens as secrets. App Check reduces abuse; it does not replace rules.

## Code/Artifact Generation

Applies only when Step 1 calls for building (not reviews or questions). Read existing `firestore.rules`, `firestore.indexes.json`, and `firebase.json` first and extend them; never overwrite.

Produce the files the classification needs, from this set: rules + rules tests, index entries, TypeScript document types for Functions, platform DTOs (Kotlin data class / Swift `Codable`) for the platforms the repo has, and v2 triggers or callables. Deliver the requested feature; don't restructure unrelated collections or rules.

## Current Defaults (verified 2026-09-23)

| Component | Default | Source |
|---|---|---|
| Android SDK | Firebase BoM 34.x (34.19.0 on 2026-09-09); main modules only — KTX artifacts were removed from BoM 34.0.0, and their Kotlin APIs now live in the main modules | firebase.google.com/support/release-notes/android |
| Functions runtime | Node.js 22 (`"engines": {"node": "22"}`); Node 20 is deprecated on Cloud Run functions (2026-04-30) and decommissioned 2026-10-30. Node 24 is GA on Cloud Run functions but not yet listed by the Firebase docs — confirm Firebase CLI support before use | firebase.google.com/docs/functions/manage-functions; docs.cloud.google.com/functions/docs/runtime-support |
| Functions API | 2nd gen (`firebase-functions/v2/*`), TypeScript | firebase.google.com/docs/functions/firestore-events |
| Emulators | firestore 8080, auth 9099, functions 5001, storage 9199 | — |
| Rules tests | `@firebase/rules-unit-testing` + the project's test runner | — |

## Related skills

- `firebase-security-auditor` agent — audit of existing rules.
- `database-architect` — engine choice, indexes, SQL.
- `data-migration` — reshaping or backfilling existing Firestore data.
- `offline-first` — local cache, sync, conflicts.
- `security-review` — broader threat model.
