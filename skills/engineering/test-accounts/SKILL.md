---
name: test-accounts
description: "QA test accounts: personas, receivable QA emails, seed/reset scripts, env-guarded credentials. Use when setting up test users, seed data, QA email addresses, or test-account teardown."
when_to_use: "NOT for test strategy or coverage (use testing-strategy), E2E tests (use e2e-testing), or production secrets (use env-secrets-manager)."
argument-hint: "[project-or-feature]"
metadata:
  verified: 2026-09-23
---

# Test Accounts

Every environment starts from a known, reproducible test state: named personas, addresses that really receive mail, idempotent seed and teardown scripts, and guards that make it impossible to run any of it against production. Synthetic data only — real user data or PII in a test account is a compliance incident, not a shortcut.

**Done when:** each persona the project needs can be created, used, and deleted in every non-prod environment by one idempotent command; teardown cascades across auth, database, Stripe, storage, and analytics; and every script refuses to run against production.

## Pre-Processing (Auto-Context)

Context — run these read-only commands first; skip any that fail or aren't permitted (they only tailor the output):

- Existing seed/fixture code: `grep -rlE "seed|fixture|factory|faker" scripts tests src functions 2>/dev/null | grep -v node_modules | head -10 || echo "(none)"`
- Auth/DB/payments in use: `grep -hoE '"(firebase-admin|firebase|@supabase/supabase-js|pg|prisma|stripe|@faker-js/faker)"' package.json functions/package.json 2>/dev/null | sort -u | head -10 || echo "(no package.json)"`

## Step 1: Classify the Need

| Need | Output |
|------|--------|
| Greenfield setup | Persona set, seed + reset scripts, env guard, credential template |
| New feature test data | Incremental seed extension (+ personas if needed) |
| Environment migration | Seed adapted to the new environment, idempotency re-checked |
| Compliance-safe data (HIPAA/COPPA/PCI/GDPR) | Synthetic generators with `_testData` flags |
| CI isolation | Per-run unique accounts + teardown hook |
| Advice / review of existing setup | Findings with severity; no generated files |

## Step 2: Gather Context

Confirm: platforms; auth provider (Firebase Auth, Auth0, Supabase, custom); database; payment provider (Stripe, RevenueCat, none); compliance flags; existing seed scripts and where they live; which environments need test data.

## Email Address Strategy (Decide Before Personas)

Every persona below needs an address that can actually **receive** mail — verification links,
password resets, magic links, receipts. Pick the strategy first; personas inherit it.

| Context | Strategy | Why |
|---|---|---|
| Shared QA / staging, humans clicking | **Catch-all on a dedicated non-prod domain** | Default. Zero provisioning, real unique addresses, wipe by dropping the mailbox |
| CI / automated E2E | **Programmatic inbox API** (Mailosaur, MailSlurp, Testmail) | Only option that can read a verification code back into a test |
| Local dev / emulator | **Local SMTP sink** (Mailpit, MailHog, Firebase Auth emulator) | No real mail leaves the machine |
| One-off manual check | Plus-addressing on an existing inbox | Acceptable for a throwaway; never as the project standard |

### Don't standardize on plus-addressing

`user+tag@domain` is real (RFC 5233 subaddressing, works on Google Workspace, M365, Fastmail,
Proton, iCloud) and it is the wrong default:

```
- Many signup forms reject "+" outright, so the strategy fails exactly where you need it.
- If the app dedupes users on a normalized email, every "+" variant collides into ONE account.
  Stripe and several vendors normalize too — silent cross-test contamination.
- It is not isolation. All mail lands in one human's inbox, so whoever reads that inbox can
  reset the password of every QA account. That inbox becomes a credential.
- "+" is trivially stripped, so it is not a reliable tenancy or routing signal either.
```

### Default: catch-all on a dedicated non-production domain

```
qa.<project>.dev          <- own it; never a subdomain of the production domain
*@qa.<project>.dev        <- catch-all; anything@ works with zero provisioning
```

Never hang QA accounts off the production domain: it risks sender reputation, and a QA
address that leaks into a real marketing list is a support incident.

### Address naming is the audit trail

```
qa-<project>-<persona>-<yyyymmdd>@qa.<project>.dev
  e.g. qa-acme-owner-20260909@qa.acme.dev
```

Deterministic and self-identifying: an orphan tells you what created it and when, so teardown
never has to guess. Encode nothing secret — these addresses appear in logs.

### Deletion must cascade

Creating accounts is easy; the leak is always deletion. One test account is a row in **five**
systems, and deleting only the auth user orphans the rest:

```
auth user -> database rows -> Stripe customer -> storage objects -> analytics identity
```

Orphaned Stripe customers are the classic offender: they survive, they accumulate, and on a
metered plan they cost money. Delete in dependency order, and make teardown idempotent so a
half-finished run can be re-run safely.

**Cure constraint — no scheduled reaper.** Org policy (2026-08-08) is no cron jobs anywhere,
which rules out the nightly-cleanup design every external example reaches for. Reap on demand
(`npm run qa:reap`) or off an existing event trigger. Deletion still runs behind the same
environment guard as the seed scripts — never pattern-match-delete against production.

Read [reference/email-accounts.md](reference/email-accounts.md) when writing the address generator,
E2E inbox polling, or the cascading teardown script.

## Step 3: Test User Personas

### Standard Persona Set

Every project starts with these 8 personas. Add project-specific personas as needed. Addresses follow the
strategy above: `qa-{project}-<persona>-{yyyymmdd}@qa.{project}.dev`, generated by `qaEmail()` — never plus-addressed.

| Persona | Display Name | Email (`qaEmail(project, …)`) | Auth Method | Subscription | Data Volume | Special Conditions |
|---------|-------------|---------------|-------------|-------------|-------------|-------------------|
| Free User | Alex Free | `qa-{project}-free-{yyyymmdd}@qa.{project}.dev` | Email/password | Free tier | Moderate (20-50 items) | Has completed onboarding |
| Premium User | Jordan Premium | `qa-{project}-premium-{yyyymmdd}@qa.{project}.dev` | Email/password | Premium monthly | Moderate (50-100 items) | Active subscription, all features unlocked |
| Admin | Sam Admin | `qa-{project}-admin-{yyyymmdd}@qa.{project}.dev` | Email/password | N/A (staff) | Full access | Admin role, all permissions |
| New User (Empty State) | Riley New | `qa-{project}-new-{yyyymmdd}@qa.{project}.dev` | Email/password | None | Zero items | Just signed up, no onboarding completed |
| Power User | Morgan Power | `qa-{project}-power-{yyyymmdd}@qa.{project}.dev` | Google OAuth | Premium annual | Large (500+ items) | Heavy usage, many connections, large history |
| Expired Subscription | Casey Expired | `qa-{project}-expired-{yyyymmdd}@qa.{project}.dev` | Email/password | Expired premium | Moderate (50-100 items) | Subscription lapsed 7 days ago, grace period |
| Banned/Suspended | Jamie Banned | `qa-{project}-banned-{yyyymmdd}@qa.{project}.dev` | Email/password | Was premium | Moderate | Account suspended, should see restriction UI |
| Multi-Device | Taylor Multi | `qa-{project}-multi-{yyyymmdd}@qa.{project}.dev` | Email/password | Premium | Moderate | Logged in on 3 devices, sync conflict scenarios |

### Persona passwords

Staging and dev accounts are reachable from the internet, so their passwords must not be guessable from the persona name. Generate a random password per persona per environment (`crypto.randomBytes(18).toString('base64url')`), store it in the environment's secret store (`QA_PASSWORD_<PERSONA>` in Secret Manager / GitHub Secrets / the team vault), and have seed scripts and E2E tests read it from there. A fixed, documented password is acceptable only against the local emulator.

### Platform-specific auth

- **Firebase Auth:** create users with the Admin SDK; use the Auth emulator locally; register fictional test phone numbers (e.g. `+1 650-555-1234` → code `123456`) in the console for SMS flows.
- **Sign in with Apple / StoreKit:** sandbox Apple accounts in App Store Connect on the catch-all domain (`qa-{project}-apple-{yyyymmdd}@qa.{project}.dev`); StoreKit configuration files for local purchase tests.
- **OAuth (Google/GitHub):** add QA accounts to the Google Cloud test-user list; use a dedicated GitHub org with bot accounts. Never personal accounts in automation.
- **Magic links:** `qaEmail(project, "magic")`, read back through the inbox API (CI) or Mailpit (local).

## Step 4: Seed and Reset Scripts

Principles: idempotent (safe to re-run), environment-guarded (allow-list of project IDs / database names, abort otherwise), deterministic (`faker.seed(42)`), relational, and reversible (every seed has a teardown). Seed scripts, reset scripts, and the env guard live in version control.

Read [reference/details.md](reference/details.md) when generating scripts: it has the Firestore, PostgreSQL, emulator, and staging seed scripts, the paginated reset script, and prefix batch-delete. Read [reference/email-accounts.md](reference/email-accounts.md) for `qaEmail()`, E2E inbox polling, and the cascading teardown.

Gotchas the scripts must handle:
- `auth.listUsers()` returns at most 1,000 users per page — loop on `pageToken` or teardown silently misses accounts.
- Firestore batches cap at 500 writes; use `BulkWriter` for bulk deletes.
- Emulators reset with `DELETE http://localhost:8080/emulator/v1/projects/{id}/databases/(default)/documents` and `DELETE http://localhost:9099/emulator/v1/projects/{id}/accounts` between suites.
- E2E runs get a unique account per run (`qaEmail(project, 'e2e', { unique: true })`); never share accounts across parallel runs.

## Step 5: Stripe Test Data

Test cards, webhook handling, and API-version gotchas are owned by the `stripe-integration` skill. Test-account specifics:

- Guard every Stripe call: abort unless the key starts with `sk_test_` or `rk_test_`. Live keys must be unreachable from seed or teardown.
- Test clocks: up to 3 customers per clock and 3 subscriptions per customer; clocks auto-delete 30 days after creation, but delete them in teardown so runs stay clean. Advance at most two billing intervals per call.
- List endpoints omit test-clock objects unless you filter by clock or customer — teardown must query by clock ID.
- Test-mode Stripe customers accumulate; delete them in the cascading teardown by QA email.

## Step 6: Credentials per Environment

| Environment | Firebase | Stripe | Auth | Analytics |
|-------------|----------|--------|------|-----------|
| Local | Emulator | `sk_test_` in `.env.local` | Emulator | Disabled |
| Dev / Staging | Per-env service account | `sk_test_` in Secret Manager | Per-env project | Debug mode |
| Production | Prod service account | `sk_live_` in Secret Manager | Prod | Enabled — no test accounts |

Commit only `.env.example` (placeholders plus `QA_PROJECT`, `QA_EMAIL_DOMAIN`); `.env*` otherwise gitignored. CI uses test keys only and never echoes secrets. Rotation, secret-manager setup, and leak scanning belong to the `env-secrets-manager` skill.

## Step 7: Compliance-Safe Test Data

All synthetic records carry `_testData: true` and `TEST-` prefixed identifiers. HIPAA: synthetic PHI with SSA-invalid SSNs (000/666/9xx areas). COPPA: minor + guardian pairs through the consent lifecycle. PCI: Stripe test cards only; card data never touches your servers. GDPR: a deletion-verification check per user. Read the "Step 8: Compliance-Safe Test Data" section of [reference/details.md](reference/details.md) when a compliance flag from Step 2 applies.

## Code/Artifact Generation

Applies when Step 1 calls for building. Grep for existing seed/fixture/factory code and extend it. Typical set (only what the classification needs):

1. `scripts/seed-test-data.ts` (or `seed.sql`) — idempotent, guarded, all personas
2. `scripts/reset-test-data.ts` + `qa:reap` npm script — cascading, paginated teardown
3. `src/utils/env-guard.ts` — refuses production
4. `tests/support/qa-email.ts` and `tests/factories/user-factory.ts`
5. `.env.example`

## Related Skills

`testing-strategy` (pyramid, coverage), `e2e-testing` (tests that use these accounts), `stripe-integration` (payments), `firebase-architect` (emulator, rules), `env-secrets-manager` (secrets), `security-review`.
