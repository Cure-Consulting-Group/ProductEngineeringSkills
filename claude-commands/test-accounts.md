# Test Accounts

Generate complete test account infrastructure: personas, seed data, Stripe test config, credential management, state reset utilities, and compliance-safe synthetic data. Every environment gets consistent, reproducible test state. NEVER use real user data or PII in test accounts.

## Pre-Processing (Auto-Context)

Project context, gathered before the skill runs. Values are injected inline below; in an environment that does not execute them (e.g. Gemini), run the shown commands instead.

- Portfolio: !`sed -n '1,40p' PORTFOLIO.md 2>/dev/null || echo "(no PORTFOLIO.md)"`
- Stack manifest: !`head -40 package.json 2>/dev/null || head -40 build.gradle.kts 2>/dev/null || head -20 Podfile 2>/dev/null || echo "(none detected)"`
- Recent commits: !`git log --oneline -5 2>/dev/null || echo "(not a git repo)"`
- Layout: !`ls src/ app/ lib/ functions/ 2>/dev/null | head -25`

Use this context to tailor all output to the actual project.

## Core Principle: Test Data Is Infrastructure

```
Test accounts are not an afterthought — they are first-class infrastructure.
Every developer, every CI run, and every QA session must start from a known, reproducible state.
Test data scripts live in version control alongside the code they support.
```

## Code Generation (Required)

Generate test infrastructure using Write:

1. **Seed script**: `scripts/seed-test-data.ts` — idempotent Firestore/PostgreSQL seeder with all personas
2. **Environment guard**: `src/utils/env-guard.ts` — prevents seed script from running in production
3. **Test user factory**: `tests/factories/user-factory.ts` — faker-based user generator
4. **Credential template**: `.env.test.example` — test environment variables
5. **Reset script**: `scripts/reset-test-data.ts` — wipes and re-seeds test environment

Before generating, Grep for existing test data patterns (`seed|fixture|factory|faker`) to match conventions.

## Step 1: Classify the Test Account Need

| Need | Primary Output | Action |
|------|---------------|--------|
| Greenfield setup | Full persona set + seed scripts + credential template | Generate everything |
| New feature test data | Incremental seed script + new personas if needed | Extend existing seed |
| Environment migration | Seed script adapted for new environment | Adapt + validate idempotency |
| Compliance-safe test data | Synthetic data generators with audit trail | Generate compliant fixtures |
| CI/CD test isolation | Per-run ephemeral accounts + teardown scripts | Generate isolation harness |

## Step 2: Gather Context

Before generating, confirm:
1. **Project name** — e.g., "Antigravity", "HealthTracker"
2. **Platforms** — Android / iOS / Web / all?
3. **Auth provider** — Firebase Auth, Auth0, Supabase Auth, custom?
4. **Database** — Firestore, PostgreSQL, SQLite, combination?
5. **Payment provider** — Stripe, RevenueCat, none?
6. **Compliance flags** — HIPAA, COPPA, PCI, GDPR, SOC 2, none?
7. **Existing seed scripts** — any current test data setup? Where does it live?
8. **Environments** — local, dev, staging, production? Which need test data?

## Step 3: Test User Personas

### Standard Persona Set

Every project starts with these 8 personas. Add project-specific personas as needed.

| Persona | Display Name | Email Pattern | Auth Method | Subscription | Data Volume | Special Conditions |
|---------|-------------|---------------|-------------|-------------|-------------|-------------------|
| Free User | Alex Free | test+free@{domain}.com | Email/password | Free tier | Moderate (20-50 items) | Has completed onboarding |
| Premium User | Jordan Premium | test+premium@{domain}.com | Email/password | Premium monthly | Moderate (50-100 items) | Active subscription, all features unlocked |
| Admin | Sam Admin | test+admin@{domain}.com | Email/password | N/A (staff) | Full access | Admin role, all permissions |
| New User (Empty State) | Riley New | test+new@{domain}.com | Email/password | None | Zero items | Just signed up, no onboarding completed |
| Power User | Morgan Power | test+power@{domain}.com | Google OAuth | Premium annual | Large (500+ items) | Heavy usage, many connections, large history |
| Expired Subscription | Casey Expired | test+expired@{domain}.com | Email/password | Expired premium | Moderate (50-100 items) | Subscription lapsed 7 days ago, grace period |
| Banned/Suspended | Jamie Banned | test+banned@{domain}.com | Email/password | Was premium | Moderate | Account suspended, should see restriction UI |
| Multi-Device | Taylor Multi | test+multi@{domain}.com | Email/password | Premium | Moderate | Logged in on 3 devices, sync conflict scenarios |

### Persona Password Convention

```
All test account passwords: TestPass123!{persona}
  - Free user:    TestPass123!free
  - Premium user: TestPass123!premium
  - Admin:        TestPass123!admin
  ... and so on.

NEVER use these passwords in production.
Assert environment before account creation.
```

### Platform-Specific Auth Accounts

#### Android (Firebase Auth)
```
- Create test users via Firebase Admin SDK
- Use Firebase Auth Emulator in local development
- Test Google Sign-In with test accounts in Google Cloud Console
- Enable test phone numbers in Firebase Console for SMS auth:
    +1 650-555-1234 → verification code: 123456
    +1 650-555-5678 → verification code: 654321
```

#### iOS (Sign in with Apple Sandbox)
```
- Create sandbox Apple IDs at appleid.apple.com (use test+apple@{domain}.com)
- Sign in with Apple sandbox returns deterministic user identifiers
- Test in-app purchase accounts via App Store Connect sandbox users
- StoreKit Testing in Xcode: use StoreKit configuration file for local testing
```

#### Web (OAuth Test Accounts)
```
- Google OAuth: use test accounts in Google Cloud Console test user list
- GitHub OAuth: create a dedicated test GitHub org with bot accounts
- Magic link: test+magic@{domain}.com — verify via Mailhog/Mailtrap in staging
- Never use personal accounts for automated testing
```

## Step 4: Seed Data Scripts

See [reference/details.md](reference/details.md) (section “Step 4: Seed Data Scripts”) for full detail.

## Step 5: Stripe Test Configuration

### Test Card Numbers

| Scenario | Card Number | CVC | Expiry |
|----------|------------|-----|--------|
| Success | 4242 4242 4242 4242 | Any 3 digits | Any future date |
| Decline (generic) | 4000 0000 0000 0002 | Any 3 digits | Any future date |
| Decline (insufficient funds) | 4000 0000 0000 9995 | Any 3 digits | Any future date |
| Requires 3D Secure | 4000 0025 0000 3155 | Any 3 digits | Any future date |
| Requires 3DS (always) | 4000 0000 0000 3220 | Any 3 digits | Any future date |
| Expired card | 4000 0000 0000 0069 | Any 3 digits | Any future date |
| Processing error | 4000 0000 0000 0119 | Any 3 digits | Any future date |
| Disputed (fraud) | 4000 0000 0000 0259 | Any 3 digits | Any future date |

### Environment Guard (Every Stripe Call)

```typescript
function assertStripeTestMode(stripe: Stripe) {
  // Stripe test keys start with sk_test_ or rk_test_
  const key = process.env.STRIPE_SECRET_KEY || '';
  if (!key.startsWith('sk_test_') && !key.startsWith('rk_test_')) {
    throw new Error(
      'ABORT: Stripe secret key is not a test key. ' +
      'Test scripts must NEVER run against live mode.'
    );
  }
}
```

### Test Webhook Events

```bash
# Trigger test webhook events locally via Stripe CLI
stripe listen --forward-to localhost:5001/my-app/us-central1/stripeWebhook

# Trigger specific events
stripe trigger payment_intent.succeeded
stripe trigger customer.subscription.created
stripe trigger customer.subscription.updated
stripe trigger customer.subscription.deleted
stripe trigger invoice.payment_failed
stripe trigger checkout.session.completed
```

### Test Clock Setup (Subscription Lifecycle Testing)

```typescript
// Test clocks let you simulate time passing for subscription testing
// IMPORTANT: Test clocks must be cleaned up — they count toward your limit

async function createTestClock(stripe: Stripe): Promise<Stripe.TestHelpers.TestClock> {
  assertStripeTestMode(stripe);
  const clock = await stripe.testHelpers.testClocks.create({
    frozen_time: Math.floor(Date.now() / 1000),
    name: `test-clock-${Date.now()}`,
  });
  return clock;
}

async function advanceTestClock(stripe: Stripe, clockId: string, days: number) {
  const advanceTo = Math.floor(Date.now() / 1000) + (days * 86400);
  await stripe.testHelpers.testClocks.advance(clockId, {
    frozen_time: advanceTo,
  });
}

// Cleanup: delete test clocks after test run
async function cleanupTestClocks(stripe: Stripe) {
  assertStripeTestMode(stripe);
  const clocks = await stripe.testHelpers.testClocks.list({ limit: 100 });
  for (const clock of clocks.data) {
    await stripe.testHelpers.testClocks.del(clock.id);
  }
}
```

### Connect Account Test Setup

```typescript
// If using Stripe Connect (marketplaces, platforms)
async function createTestConnectAccount(stripe: Stripe) {
  assertStripeTestMode(stripe);
  const account = await stripe.accounts.create({
    type: 'express',
    country: 'US',
    email: 'test+connect@example.com',
    capabilities: {
      card_payments: { requested: true },
      transfers: { requested: true },
    },
  });
  // In test mode, skip onboarding by updating the account directly
  return account;
}
```

## Step 6: Environment Credential Management

### Credential Matrix

| Environment | Firebase | Stripe | Auth | Analytics |
|-------------|----------|--------|------|-----------|
| Local (emulator) | Emulator auto-config | `sk_test_...` in `.env.local` | Emulator (no real auth) | Disabled |
| Dev | Dev project service account | `sk_test_...` in Secret Manager | Dev Firebase Auth | Debug mode |
| Staging | Staging project service account | `sk_test_...` in Secret Manager | Staging Firebase Auth | Debug mode |
| Production | Prod project service account | `sk_live_...` in Secret Manager | Prod Firebase Auth | Enabled |

### .env Template

```bash
# .env.template — commit this file (no real values)
# Copy to .env.local and fill in values. NEVER commit .env.local.

# === Environment ===
NODE_ENV=development
APP_ENV=local  # local | dev | staging | production

# === Firebase ===
FIREBASE_PROJECT_ID=my-app-dev
FIRESTORE_EMULATOR_HOST=localhost:8080
FIREBASE_AUTH_EMULATOR_HOST=localhost:9099
FIREBASE_STORAGE_EMULATOR_HOST=localhost:9199

# === Stripe (TEST keys only in this file) ===
STRIPE_PUBLISHABLE_KEY=pk_test_REPLACE_ME
STRIPE_SECRET_KEY=sk_test_REPLACE_ME
STRIPE_WEBHOOK_SECRET=whsec_REPLACE_ME

# === Auth ===
GOOGLE_CLIENT_ID=REPLACE_ME.apps.googleusercontent.com
APPLE_CLIENT_ID=com.example.app

# === Analytics (disabled locally) ===
ANALYTICS_ENABLED=false
MIXPANEL_TOKEN=test-token-not-real
```

### .gitignore Rules (Non-Negotiable)

```gitignore
# Credentials — NEVER commit
.env
.env.*
!.env.template
*.pem
*.key
service-account*.json
*-credentials.json
firebase-debug.log
```

### Secret Rotation Schedule

```
| Secret | Rotation Frequency | Owner | Stored In |
|--------|--------------------|-------|-----------|
| Stripe secret key | 90 days | Engineering lead | GCP Secret Manager |
| Stripe webhook secret | On endpoint change | Engineering lead | GCP Secret Manager |
| Firebase service account | 365 days | DevOps | GCP IAM |
| OAuth client secrets | 180 days | Engineering lead | GCP Secret Manager |
| CI/CD deploy tokens | 90 days | DevOps | GitHub Secrets |
```

### CI/CD Secrets Setup (GitHub Actions)

```yaml
# .github/workflows/test.yml
env:
  FIREBASE_PROJECT_ID: ${{ secrets.FIREBASE_PROJECT_ID_STAGING }}
  STRIPE_SECRET_KEY: ${{ secrets.STRIPE_SECRET_KEY_TEST }}
  STRIPE_WEBHOOK_SECRET: ${{ secrets.STRIPE_WEBHOOK_SECRET_TEST }}

# Setting secrets via CLI:
# gh secret set STRIPE_SECRET_KEY_TEST --body "sk_test_..."
# gh secret set FIREBASE_PROJECT_ID_STAGING --body "my-app-staging"

# NEVER use production secrets in CI. Test keys only.
# NEVER echo or log secret values in CI output.
```

## Step 7: State Reset Utilities

### Reset Script (Clear Test Data, Preserve Config)

```typescript
// scripts/reset-test-data.ts
import { initializeApp } from 'firebase-admin/app';
import { getFirestore } from 'firebase-admin/firestore';
import { getAuth } from 'firebase-admin/auth';

const TEST_EMAIL_PREFIX = 'test+';

async function resetTestUsers(auth: any) {
  const listResult = await auth.listUsers(1000);
  const testUsers = listResult.users.filter(
    (u: any) => u.email?.startsWith(TEST_EMAIL_PREFIX)
  );

  for (const user of testUsers) {
    await auth.deleteUser(user.uid);
    console.log(`  Deleted auth user: ${user.email}`);
  }
}

async function resetTestDocuments(db: FirebaseFirestore.Firestore) {
  // Delete user documents for test accounts
  const usersSnapshot = await db.collection('users')
    .where('email', '>=', TEST_EMAIL_PREFIX)
    .where('email', '<', TEST_EMAIL_PREFIX + '\uf8ff')
    .get();

  const batch = db.batch();
  usersSnapshot.docs.forEach(doc => batch.delete(doc.ref));
  await batch.commit();
  console.log(`  Deleted ${usersSnapshot.size} test user documents`);

  // Add subcollection cleanup here:
  // await deleteSubcollections(db, usersSnapshot.docs);
}

async function main() {
  // Same environment guard as seed script
  await assertEnvironment();

  const app = initializeApp();
  const db = getFirestore(app);
  const auth = getAuth(app);

  console.log('Resetting test data...');
  await resetTestUsers(auth);
  await resetTestDocuments(db);
  console.log('Reset complete. Run seed script to restore test accounts.');
}

main().catch(console.error);
```

### Per-Test Isolation Strategy

```
For unit tests:
  - Each test creates its own data via test builders — no shared state
  - Use beforeEach/afterEach for setup/teardown

For integration tests (Emulator):
  - Clear Firestore between test suites: fetch('http://localhost:8080/emulator/v1/projects/{id}/databases/(default)/documents', { method: 'DELETE' })
  - Clear Auth between test suites: fetch('http://localhost:9099/emulator/v1/projects/{id}/accounts', { method: 'DELETE' })
  - Each test file gets a clean slate

For E2E tests:
  - Seed a unique test user per test run: test+e2e-{timestamp}@example.com
  - Clean up after test completes (or on next run via prefix scan)
  - Never share test accounts across parallel E2E runs
```

### Firestore Batch Delete by Test Prefix

```typescript
async function deleteCollectionByPrefix(
  db: FirebaseFirestore.Firestore,
  collection: string,
  field: string,
  prefix: string
) {
  const snapshot = await db.collection(collection)
    .where(field, '>=', prefix)
    .where(field, '<', prefix + '\uf8ff')
    .limit(500) // Firestore batch limit
    .get();

  if (snapshot.empty) return 0;

  const batch = db.batch();
  snapshot.docs.forEach(doc => batch.delete(doc.ref));
  await batch.commit();

  // Recurse for large datasets
  if (snapshot.size === 500) {
    const more = await deleteCollectionByPrefix(db, collection, field, prefix);
    return snapshot.size + more;
  }
  return snapshot.size;
}
```

### Stripe Test Mode Cleanup

```
Stripe test mode data does NOT require cleanup — it is isolated from live.
However, these resources have limits and should be cleaned up:

  - Test Clocks: max 3 active per account — always delete after use
  - Webhook endpoints: remove stale test endpoints
  - Connected accounts: clean up periodically if using Connect

Production data is never accessible in test mode. This is a Stripe guarantee.
```

## Step 8: Compliance-Safe Test Data

See [reference/details.md](reference/details.md) (section “Step 8: Compliance-Safe Test Data”) for full detail.

## Related Skills

- `/testing-strategy` — Test pyramid, platform standards, coverage rules
- `/firebase-architect` — Firestore schema, security rules, emulator setup
- `/stripe-integration` — Payment integration, webhook handling, subscription management
- `/security-review` — OWASP checklist, auth/data security audit
- `/ci-cd-pipeline` — CI/CD setup, secrets management, deployment workflows
