---
paths:
  - "**/functions/**"
  - "**/firestore*"
  - "**/*.rules"
  - "**/firebase.json"
---

# Firebase Development Standards

- Cloud Functions v2 (onCall, onRequest, scheduled, Firestore triggers) on the Node.js 22 runtime (`"engines": {"node": "22"}`); Node 20 is decommissioned 2026-10-30
- TypeScript for all Cloud Functions — no JavaScript
- Firestore security rules cover every access pattern — deny by default
- App Check enforced for Firestore, Storage and Functions before launch (monitor mode first); it reduces abuse but never replaces rules
- Never use the Firebase Admin SDK on the client
- Typed Firestore collections with converter functions
- Subcollections for related data — avoid deep nesting (max 2 levels)
- Batched writes and transactions for multi-document updates
- Cloud Functions errors: throw typed `HttpsError` with codes
- Emulator suite for local development — never test against production
- Indexes defined in `firestore.indexes.json` — no runtime index creation

Verified 2026-10-24 against `firebase-architect` (its runtime facts verified 2026-09-23 from firebase.google.com and docs.cloud.google.com; recheck Node 24 support before upgrading).
