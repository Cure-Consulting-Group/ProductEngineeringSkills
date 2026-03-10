---
paths:
  - "**/functions/**"
  - "**/firestore*"
  - "**/*.rules"
  - "**/firebase.json"
---

# Firebase Development Standards

- Cloud Functions v2 (onCall, onRequest, scheduled, Firestore triggers)
- TypeScript for all Cloud Functions — no JavaScript
- Firestore security rules must match every access pattern — deny by default
- Never use Firebase Admin SDK on the client
- Typed Firestore collections with converter functions
- Subcollection pattern for related data — avoid deep nesting (max 2 levels)
- Use batched writes and transactions for multi-document updates
- Cloud Functions error handling: return typed HttpsError with codes
- Emulator suite for local development — never test against production
- Firestore indexes defined in firestore.indexes.json — no runtime index creation
