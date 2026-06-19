# test-accounts: detailed reference

> Reference material for the `test-accounts` skill, split out for progressive disclosure. Loaded on demand from SKILL.md.

## Contents
- Step 4: Seed Data Scripts
- Step 8: Compliance-Safe Test Data

## Step 4: Seed Data Scripts

### Design Principles

```
1. IDEMPOTENT    — safe to run multiple times, same result
2. ENVIRONMENT-AWARE — checks which environment before executing
3. DETERMINISTIC — same seed produces same data (use fixed seeds for faker)
4. RELATIONAL    — entities reference each other correctly
5. REVERSIBLE    — every seed has a corresponding teardown
```

### Firebase/Firestore Seed Script (TypeScript)

```typescript
// scripts/seed-firestore.ts
import { initializeApp, cert } from 'firebase-admin/app';
import { getFirestore, Timestamp } from 'firebase-admin/firestore';
import { getAuth } from 'firebase-admin/auth';

const ALLOWED_PROJECTS = ['my-app-dev', 'my-app-staging'];

async function assertEnvironment() {
  const projectId = process.env.GCLOUD_PROJECT || process.env.FIREBASE_PROJECT_ID;
  if (!projectId || !ALLOWED_PROJECTS.includes(projectId)) {
    throw new Error(
      `ABORT: Seed script refused to run against project "${projectId}". ` +
      `Allowed: ${ALLOWED_PROJECTS.join(', ')}`
    );
  }
}

const PERSONAS = {
  free:    { email: 'test+free@example.com',    displayName: 'Alex Free',      role: 'user',  tier: 'free' },
  premium: { email: 'test+premium@example.com', displayName: 'Jordan Premium', role: 'user',  tier: 'premium' },
  admin:   { email: 'test+admin@example.com',   displayName: 'Sam Admin',      role: 'admin', tier: 'staff' },
  new:     { email: 'test+new@example.com',     displayName: 'Riley New',      role: 'user',  tier: 'free' },
  power:   { email: 'test+power@example.com',   displayName: 'Morgan Power',   role: 'user',  tier: 'premium' },
  expired: { email: 'test+expired@example.com', displayName: 'Casey Expired',  role: 'user',  tier: 'expired' },
  banned:  { email: 'test+banned@example.com',  displayName: 'Jamie Banned',   role: 'user',  tier: 'suspended' },
  multi:   { email: 'test+multi@example.com',   displayName: 'Taylor Multi',   role: 'user',  tier: 'premium' },
};

async function seedUsers(auth: any, db: FirebaseFirestore.Firestore) {
  for (const [key, persona] of Object.entries(PERSONAS)) {
    // Idempotent: delete if exists, then create
    try { await auth.getUserByEmail(persona.email).then((u: any) => auth.deleteUser(u.uid)); } catch {}

    const user = await auth.createUser({
      email: persona.email,
      password: `TestPass123!${key}`,
      displayName: persona.displayName,
      emailVerified: true,
    });

    await db.doc(`users/${user.uid}`).set({
      email: persona.email,
      displayName: persona.displayName,
      role: persona.role,
      tier: persona.tier,
      createdAt: Timestamp.now(),
      updatedAt: Timestamp.now(),
    });

    // Set custom claims for role-based access
    if (persona.role === 'admin') {
      await auth.setCustomUserClaims(user.uid, { admin: true });
    }

    console.log(`  Seeded: ${persona.displayName} (${persona.email}) → ${user.uid}`);
  }
}

async function main() {
  await assertEnvironment();
  const app = initializeApp();
  const db = getFirestore(app);
  const auth = getAuth(app);

  console.log('Seeding users...');
  await seedUsers(auth, db);

  // Add feature-specific seed data here:
  // await seedProducts(db);
  // await seedOrders(db, userIds);
  // await seedSubscriptions(db, userIds);

  console.log('Seed complete.');
}

main().catch(console.error);
```

### PostgreSQL Seed Script (SQL)

```sql
-- scripts/seed.sql
-- IDEMPOTENT: Uses ON CONFLICT DO UPDATE

BEGIN;

-- Guard: only run against dev/staging
DO $$
BEGIN
  IF current_database() NOT IN ('myapp_dev', 'myapp_staging', 'myapp_test') THEN
    RAISE EXCEPTION 'ABORT: Seed script refused to run against database %', current_database();
  END IF;
END $$;

-- Personas
INSERT INTO users (id, email, display_name, role, tier, created_at, updated_at)
VALUES
  ('00000000-0000-0000-0000-000000000001', 'test+free@example.com',    'Alex Free',      'user',  'free',      NOW(), NOW()),
  ('00000000-0000-0000-0000-000000000002', 'test+premium@example.com', 'Jordan Premium', 'user',  'premium',   NOW(), NOW()),
  ('00000000-0000-0000-0000-000000000003', 'test+admin@example.com',   'Sam Admin',      'admin', 'staff',     NOW(), NOW()),
  ('00000000-0000-0000-0000-000000000004', 'test+new@example.com',     'Riley New',      'user',  'free',      NOW(), NOW()),
  ('00000000-0000-0000-0000-000000000005', 'test+power@example.com',   'Morgan Power',   'user',  'premium',   NOW(), NOW()),
  ('00000000-0000-0000-0000-000000000006', 'test+expired@example.com', 'Casey Expired',  'user',  'expired',   NOW(), NOW()),
  ('00000000-0000-0000-0000-000000000007', 'test+banned@example.com',  'Jamie Banned',   'user',  'suspended', NOW(), NOW()),
  ('00000000-0000-0000-0000-000000000008', 'test+multi@example.com',   'Taylor Multi',   'user',  'premium',   NOW(), NOW())
ON CONFLICT (id) DO UPDATE SET
  email = EXCLUDED.email,
  display_name = EXCLUDED.display_name,
  role = EXCLUDED.role,
  tier = EXCLUDED.tier,
  updated_at = NOW();

-- Feature-specific seed data goes here:
-- INSERT INTO products (...) VALUES (...) ON CONFLICT DO UPDATE ...;
-- INSERT INTO orders (...) VALUES (...) ON CONFLICT DO UPDATE ...;

COMMIT;
```

### Local Development Seed (Emulator)

```typescript
// scripts/seed-emulator.ts
// Runs against Firebase Emulator — no environment guard needed

import { initializeApp } from 'firebase-admin/app';
import { getFirestore } from 'firebase-admin/firestore';
import { getAuth } from 'firebase-admin/auth';

process.env.FIRESTORE_EMULATOR_HOST = 'localhost:8080';
process.env.FIREBASE_AUTH_EMULATOR_HOST = 'localhost:9099';

// Reuse the same persona definitions and seed functions
// from seed-firestore.ts — the emulator accepts the same API calls.

// Add: bulk fake data for load testing (use faker with fixed seed)
import { faker } from '@faker-js/faker';
faker.seed(42); // Deterministic — same data every run

async function seedBulkData(db: FirebaseFirestore.Firestore, userId: string, count: number) {
  const batch = db.batch();
  for (let i = 0; i < count; i++) {
    const ref = db.collection(`users/${userId}/items`).doc(`item-${i}`);
    batch.set(ref, {
      title: faker.commerce.productName(),
      description: faker.commerce.productDescription(),
      price: parseFloat(faker.commerce.price()),
      createdAt: faker.date.past(),
    });
  }
  await batch.commit();
}
```

### Staging Seed (Idempotent, Safe to Re-Run)

```bash
#!/bin/bash
# scripts/seed-staging.sh

set -euo pipefail

PROJECT="my-app-staging"
CURRENT=$(gcloud config get-value project 2>/dev/null)

if [ "$CURRENT" != "$PROJECT" ]; then
  echo "ERROR: Expected project $PROJECT, got $CURRENT"
  echo "Run: gcloud config set project $PROJECT"
  exit 1
fi

echo "Seeding staging ($PROJECT)..."
npx ts-node scripts/seed-firestore.ts
echo "Done."
```

## Step 8: Compliance-Safe Test Data

### HIPAA: Synthetic PHI

```typescript
// NEVER use real patient data. Generate synthetic PHI clearly marked as test data.
import { faker } from '@faker-js/faker';
faker.seed(42);

function generateSyntheticPatient() {
  return {
    id: `TEST-PATIENT-${faker.string.uuid()}`,
    firstName: faker.person.firstName(),
    lastName: faker.person.lastName(),
    dateOfBirth: faker.date.birthdate({ min: 18, max: 90, mode: 'age' }),
    ssn: `000-${faker.string.numeric(2)}-${faker.string.numeric(4)}`, // SSA reserved 000 prefix for test
    diagnosis: faker.helpers.arrayElement([
      'TEST-DX-Hypertension',
      'TEST-DX-Type2Diabetes',
      'TEST-DX-Asthma',
    ]),
    mrn: `TEST-MRN-${faker.string.numeric(8)}`,
    _testData: true, // Always flag synthetic records
    _generatedAt: new Date().toISOString(),
  };
}

// All synthetic PHI must:
// 1. Use TEST- prefix on identifiers
// 2. Use SSA-reserved SSN ranges (000-xx-xxxx, 666-xx-xxxx, 9xx-xx-xxxx)
// 3. Set _testData: true flag
// 4. Never be derived from real patient records
```

### COPPA: Minor + Guardian Test Pairs

```typescript
function generateCOPPATestPair() {
  return {
    minor: {
      email: `test+minor-${faker.string.nanoid(6)}@example.com`,
      displayName: faker.person.firstName() + ' (Minor)',
      dateOfBirth: faker.date.birthdate({ min: 8, max: 12, mode: 'age' }),
      parentalConsentGiven: false, // Start without consent
      parentalConsentDate: null,
      _testData: true,
    },
    guardian: {
      email: `test+guardian-${faker.string.nanoid(6)}@example.com`,
      displayName: faker.person.firstName() + ' (Guardian)',
      dateOfBirth: faker.date.birthdate({ min: 30, max: 50, mode: 'age' }),
      linkedMinors: [], // Populated after consent flow
      _testData: true,
    },
  };
}

// Test scenarios for COPPA:
// 1. Minor signs up → consent required → guardian notified
// 2. Guardian grants consent → minor account activated
// 3. Guardian revokes consent → minor account deactivated + data deleted
// 4. Minor ages out (turns 13) → parental controls removed
```

### PCI: Payment Card Testing

```
Hard rule: NEVER store, log, or transmit real card numbers anywhere.

In test environments:
  - Use ONLY Stripe test card numbers (see Step 5 table above)
  - Stripe test mode guarantees no real charges occur
  - Card data never touches your servers — Stripe.js / PaymentSheet handles it
  - PCI compliance = "let Stripe handle it" for SAQ-A merchants

Prohibited in ALL environments:
  - Logging card numbers (even masked)
  - Storing card numbers in your database
  - Passing card numbers through your API (use Stripe tokens/PaymentMethods)
  - Screenshots or screen recordings containing card entry fields with real data
```

### GDPR: Data Deletion Verification

```typescript
// Verify that "right to deletion" actually works for test accounts

async function verifyGDPRDeletion(userId: string) {
  const db = getFirestore();

  // Collections that must be purged on deletion
  const collectionsToCheck = [
    `users/${userId}`,
    `users/${userId}/orders`,
    `users/${userId}/preferences`,
    `users/${userId}/sessions`,
    `analytics_events`, // Check for userId references
  ];

  const results: { collection: string; found: boolean; count: number }[] = [];

  // Check direct documents
  for (const path of collectionsToCheck) {
    if (path.includes('/')) {
      const doc = await db.doc(path).get();
      results.push({ collection: path, found: doc.exists, count: doc.exists ? 1 : 0 });
    }
  }

  // Check analytics events for userId references
  const analyticsSnapshot = await db.collection('analytics_events')
    .where('userId', '==', userId)
    .limit(1)
    .get();
  results.push({
    collection: 'analytics_events (userId refs)',
    found: !analyticsSnapshot.empty,
    count: analyticsSnapshot.size,
  });

  // Report
  const failures = results.filter(r => r.found);
  if (failures.length > 0) {
    console.error('GDPR DELETION INCOMPLETE:');
    failures.forEach(f => console.error(`  ${f.collection}: ${f.count} records remain`));
    throw new Error('GDPR deletion verification failed');
  }

  console.log(`GDPR deletion verified: no data found for user ${userId}`);
}
```
