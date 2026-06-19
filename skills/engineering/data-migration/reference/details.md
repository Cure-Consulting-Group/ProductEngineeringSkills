# data-migration: detailed reference

> Reference material for the `data-migration` skill, split out for progressive disclosure. Loaded on demand from SKILL.md.

## Contents
- Step 8: Firestore-Specific Migrations

## Step 8: Firestore-Specific Migrations

### Collection Restructuring

```
Scenario: flattening nested subcollections into top-level collections

Before:
  users/{userId}/orders/{orderId}  (subcollection)

After:
  orders/{orderId}  (top-level, with userId field)

Migration script (Cloud Function):
  const BATCH_SIZE = 500;

  async function migrateOrders() {
    const usersSnap = await db.collection('users').get();

    for (const userDoc of usersSnap.docs) {
      const ordersSnap = await db
        .collection('users').doc(userDoc.id)
        .collection('orders').get();

      let batch = db.batch();
      let count = 0;

      for (const orderDoc of ordersSnap.docs) {
        const newRef = db.collection('orders').doc(orderDoc.id);
        batch.set(newRef, {
          ...orderDoc.data(),
          userId: userDoc.id,
          migratedAt: admin.firestore.FieldValue.serverTimestamp(),
        }, { merge: true }); // merge for idempotency

        count++;
        if (count % BATCH_SIZE === 0) {
          await batch.commit();
          batch = db.batch();
        }
      }

      if (count % BATCH_SIZE !== 0) {
        await batch.commit();
      }
    }
  }
```

### Field Type Changes

```
Scenario: converting string timestamps to Firestore Timestamps

Migration approach (expand-contract):
  Phase 1: Add new field (createdAtTs: Timestamp) alongside old field (createdAt: string)
  Phase 2: Backfill new field from old field
  Phase 3: Update application to write both, read new
  Phase 4: Drop old field in cleanup migration

Backfill script:
  async function backfillTimestamps(collectionName: string) {
    let lastDoc = null;
    let processed = 0;

    while (true) {
      let query = db.collection(collectionName)
        .where('createdAtTs', '==', null)
        .limit(500);

      if (lastDoc) {
        query = query.startAfter(lastDoc);
      }

      const snap = await query.get();
      if (snap.empty) break;

      const batch = db.batch();
      for (const doc of snap.docs) {
        const dateStr = doc.data().createdAt;
        const timestamp = admin.firestore.Timestamp.fromDate(new Date(dateStr));
        batch.update(doc.ref, { createdAtTs: timestamp });
      }
      await batch.commit();

      lastDoc = snap.docs[snap.docs.length - 1];
      processed += snap.size;
      console.log(`Processed ${processed} documents`);
    }
  }
```

### Backfill Scripts Best Practices

```
Rules for Firestore backfill scripts:
  1. Always paginate with startAfter — never load entire collection
  2. Use batched writes (max 500 operations per batch)
  3. Add a migratedAt timestamp to every modified document
  4. Support resumption: log last processed document ID
  5. Rate limit: add delays between batches if hitting Firestore write limits
  6. Dry run mode: first run should log what would change without writing
  7. Validation: count documents before and after, verify sample
  8. Idempotent: use set with merge or check-before-write patterns
  9. Run during low-traffic windows (check Firebase console for traffic patterns)
  10. Monitor Firestore usage dashboard during execution
```
