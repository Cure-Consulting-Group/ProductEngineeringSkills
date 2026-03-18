---
name: firebase-architect
description: "Design Firestore schemas, security rules, Cloud Functions, and data layer architecture"
argument-hint: "[feature-or-collection]"
---

# Firebase Architect

Generates production-grade Firebase architecture. Every output is security-first, offline-aware, and Clean Architecture compliant (Firebase never leaks into domain layer).

## Pre-Processing (Auto-Context)

Before starting, gather project context silently:
- Read `PORTFOLIO.md` if it exists in the project root or parent directories for product/team context
- Run: `cat package.json 2>/dev/null || cat build.gradle.kts 2>/dev/null || cat Podfile 2>/dev/null` to detect stack
- Run: `git log --oneline -5 2>/dev/null` for recent changes
- Run: `ls src/ app/ lib/ functions/ 2>/dev/null` to understand project structure
- Use this context to tailor all output to the actual project

## Core Principle: Firebase in Clean Architecture

```
Presentation Layer  →  ViewModel / StateFlow
Domain Layer        →  UseCases + Repository INTERFACES only (no Firebase imports)
Data Layer          →  FirestoreDataSource, FirebaseAuthDataSource, DTO models
                        ↓
                    Firebase SDK (Firestore, Auth, Functions, Storage)
```

**Hard rules:**
- No `FirebaseFirestore` or `DocumentReference` in domain or presentation layers
- DTOs live in data layer; map to/from domain models at the repository boundary
- All Firestore listeners converted to `Flow` via `callbackFlow`
- All writes use structured error handling (`Result<T>` / `sealed class`)

## Step 1: Classify the Request

| Request | Primary Output | Action |
|---------|---------------|--------|
| Data modeling / schema | Collection design + security rules | Design schema |
| Security rules | Rules file + test spec | Write rules |
| Cloud Function | TypeScript function scaffold | Scaffold function |
| Auth flow | Auth architecture + rules | Design auth |
| Android integration | Repository + DataSource + DTO scaffold | Scaffold data layer |
| Full feature | All of the above | Generate everything |

## Step 2: Gather Context

Before generating, confirm:
1. **Feature name** — e.g., "Subscription Management"
2. **Collections involved** — new or existing?
3. **Auth model** — Firebase Auth UID as primary key? (default: yes)
4. **Access patterns** — who reads what? (user reads own data, admin reads all, etc.)
5. **Offline requirement** — does this feature need to work offline?
6. **Scale expectation** — hundreds / thousands / millions of documents?

## Step 3: Firestore Design Principles (Always Apply)

### Collection Structure Rules
- **Root collection** for entities queried across users (admin dashboards, analytics)
- **Subcollection** for entities owned by a single parent document (user's orders, posts)
- **Denormalize aggressively** — Firestore is not relational; duplicate data to avoid joins
- **Max document size**: 1MB. Arrays > 10k items → subcollection
- **Avoid deeply nested subcollections** (max 2 levels deep in practice)

### Document ID Rules
```
users/{uid}                    ← Firebase Auth UID always
users/{uid}/subscriptions/{id} ← Auto-generated Firestore ID
products/{slug}                ← Human-readable slug when queried by known key
events/{YYYY-MM-DD}_{id}      ← Date-prefixed for time-series queries
```

### Timestamp Rules
- All documents include `createdAt: Timestamp` and `updatedAt: Timestamp`
- Use `FieldValue.serverTimestamp()` on write — never client-side Date
- Index `createdAt` and `updatedAt` on any collection with list/sort queries

## Step 4: Output Format

For schema designs, always output:
1. **Collection hierarchy diagram** (ASCII tree)
2. **Document shape** (TypeScript interface + Kotlin data class)
3. **Access patterns table** (query → index requirement)
4. **Security rules** (scoped to this feature)
5. **Android Data Layer scaffold** (DTO + Repository impl stub)
6. **Cloud Functions** (if writes need server-side logic)

## Code Generation (Required)

You MUST generate actual Firebase files using Write:

1. **Security Rules**: `firestore.rules` — deny-by-default with per-collection rules, field validation, auth checks
2. **Indexes**: `firestore.indexes.json` — composite indexes for all planned queries
3. **Data Models** (TypeScript): `functions/src/models/{collection}.ts` — typed interfaces matching schema
4. **Data Models** (Kotlin): `data/model/{Collection}.kt` — Firestore-compatible data classes
5. **Data Models** (Swift): `Models/{Collection}.swift` — Codable structs
6. **Cloud Function triggers**: `functions/src/triggers/{collection}.ts` — onCreate/onUpdate/onDelete handlers
7. **Storage Rules**: `storage.rules` — file type and size validation
8. **Firebase config**: `firebase.json` — hosting, functions, firestore, storage config

Before generating, Read existing `firestore.rules` and `firebase.json` if they exist. Extend rather than replace.

Use Grep to find all Firestore references in client code: `collection(|doc(|getFirestore` to ensure all collections have rules.

## Tech Stack Defaults

```yaml
firebase_sdk_android: firebase-bom:33.x
firestore_android: ktx, offline persistence enabled
auth: Firebase Auth (email, Google Sign-In)
functions: TypeScript, Node 20, Cloud Functions v2
emulator: firestore:8080, auth:9099, functions:5001, storage:9199
rules_testing: @firebase/rules-unit-testing + Jest
android_coroutines: kotlinx-coroutines-play-services for Task → suspend
```
