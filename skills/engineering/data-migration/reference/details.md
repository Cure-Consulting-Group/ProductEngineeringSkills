# data-migration: Firestore script reference

Read this when adapting a Firestore backfill or restructuring script. Rules and gotchas live in SKILL.md Step 4; these are starting points in the modular Admin SDK (`firebase-admin/firestore`), TypeScript.

## Backfill a field (paginate by document ID, BulkWriter, resumable)

```ts
import { getFirestore, FieldPath, FieldValue, Timestamp } from 'firebase-admin/firestore';

const db = getFirestore();

export async function backfillCreatedAtTs(collection: string, opts: { dryRun: boolean; resumeFrom?: string }) {
  const writer = db.bulkWriter();
  writer.onWriteError((err) => err.failedAttempts < 5); // retry transient errors, then surface
  let lastId = opts.resumeFrom;
  let scanned = 0, changed = 0;

  while (true) {
    let q = db.collection(collection).orderBy(FieldPath.documentId()).limit(500);
    if (lastId) q = q.startAfter(lastId);
    const snap = await q.get();
    if (snap.empty) break;

    for (const doc of snap.docs) {
      const data = doc.data();
      // Check in code: where('createdAtTs','==',null) would miss docs where the field is absent.
      if (data.createdAtTs instanceof Timestamp || typeof data.createdAt !== 'string') continue;
      changed++;
      if (!opts.dryRun) {
        writer.update(doc.ref, {
          createdAtTs: Timestamp.fromDate(new Date(data.createdAt)),
          migratedAt: FieldValue.serverTimestamp(),
          migrationId: '2026-09-createdAtTs',
        });
      }
    }
    scanned += snap.size;
    lastId = snap.docs[snap.docs.length - 1].id;
    console.log(JSON.stringify({ scanned, changed, checkpoint: lastId })); // persist checkpoint
  }
  await writer.close();
}
```

## Flatten a subcollection into a top-level collection

`users/{uid}/orders/{orderId}` → `orders/{orderId}` with a `userId` field. Use a collection-group query so you don't load every user first; keep the source order ID as the target ID so re-runs upsert.

```ts
const writer = db.bulkWriter();
let last: FirebaseFirestore.QueryDocumentSnapshot | undefined;
while (true) {
  let q = db.collectionGroup('orders').orderBy(FieldPath.documentId()).limit(500);
  if (last) q = q.startAfter(last); // collection-group documentId ordering needs the snapshot or full path
  const snap = await q.get();
  if (snap.empty) break;
  for (const doc of snap.docs) {
    const userId = doc.ref.parent.parent?.id;
    if (!userId) continue; // a top-level 'orders' doc from an earlier run
    writer.set(db.collection('orders').doc(doc.id), { ...doc.data(), userId, migratedAt: FieldValue.serverTimestamp() }, { merge: true });
  }
  last = snap.docs[snap.docs.length - 1];
}
await writer.close();
```

Order-ID collisions across users are possible only if IDs were not auto-generated; check for them in the pre-migration gate before running.

## CDC to a target (Functions v2)

```ts
import { onDocumentWritten } from 'firebase-functions/v2/firestore';

export const syncOrder = onDocumentWritten('orders/{orderId}', async (event) => {
  const after = event.data?.after;
  const updateTime = after?.updateTime?.toMillis() ?? Date.now();
  // Idempotent + ordered: skip if the target already holds a newer version.
  await upsertTarget(event.params.orderId, after?.exists ? after.data() : null, updateTime);
});
```
