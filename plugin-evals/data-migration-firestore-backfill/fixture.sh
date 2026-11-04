#!/usr/bin/env bash
# Fixture scaffold (runs only under --scaffold). A Firebase Admin project whose `orders`
# collection (~4M docs) needs a derived `status` field backfilled while the app keeps writing.
set -euo pipefail
mkdir -p src/types scripts
cat > package.json <<'__FIXTURE_EOF__'
{
  "name": "shop-backend",
  "private": true,
  "type": "module",
  "scripts": { "backfill": "tsx scripts/backfill-order-status.ts" },
  "dependencies": { "firebase-admin": "13.5.0" },
  "devDependencies": { "tsx": "4.20.6", "typescript": "5.9.3" }
}
__FIXTURE_EOF__
cat > src/types/order.ts <<'__FIXTURE_EOF__'
import type { Timestamp } from 'firebase-admin/firestore';

// Existing shape. `status` is new and missing on every existing document.
export interface Order {
  customerId: string;
  totalCents: number;
  createdAt: Timestamp;
  fulfilledAt?: Timestamp | null;
  cancelledAt?: Timestamp | null;
  status?: 'open' | 'fulfilled' | 'cancelled';
}
__FIXTURE_EOF__
cat > firebase.json <<'__FIXTURE_EOF__'
{ "firestore": { "rules": "firestore.rules", "indexes": "firestore.indexes.json" } }
__FIXTURE_EOF__
