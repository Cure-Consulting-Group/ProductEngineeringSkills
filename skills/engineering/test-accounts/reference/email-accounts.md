# test-accounts: QA email address provisioning

Deep reference for the "Email Address Strategy" section of `SKILL.md`. Covers address
generation, reading mail back in automated tests, and cascading teardown.

## Contents

- Address generator (shared by seeders and tests)
- Reading verification mail in E2E
- Local sink for development
- Cascading teardown
- Provider notes

---

## Address generator

One generator, imported by both the seeder and the test suite, so an address is never
hand-typed twice and teardown can recognise its own output.

```ts
// tests/support/qa-email.ts
const QA_DOMAIN = process.env.QA_EMAIL_DOMAIN ?? "qa.example.dev";
const PREFIX = "qa";

/** qa-<project>-<persona>-<yyyymmdd>[-<nonce>]@<qa domain> */
export function qaEmail(project: string, persona: string, opts: { unique?: boolean } = {}) {
  const day = new Date().toISOString().slice(0, 10).replace(/-/g, "");
  const nonce = opts.unique ? `-${Math.random().toString(36).slice(2, 8)}` : "";
  return `${PREFIX}-${slug(project)}-${slug(persona)}-${day}${nonce}@${QA_DOMAIN}`;
}

/** True only for addresses this project generated — teardown's safety predicate. */
export function isQaEmail(address: string) {
  return address.endsWith(`@${QA_DOMAIN}`) && address.startsWith(`${PREFIX}-`);
}

const slug = (s: string) => s.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
```

Use `unique: true` for anything running concurrently (CI shards, parallel E2E workers).
A fixed daily address is fine for a seeded persona a human logs into; it is a race for
tests running in parallel.

---

## Reading verification mail in E2E

This is the capability plus-addressing cannot provide: a test needs to *read* the message.
Any provider exposing an inbox API works; the shape is the same.

```ts
// tests/e2e/signup.spec.ts
import MailosaurClient from "mailosaur";
const mailbox = new MailosaurClient(process.env.MAILOSAUR_API_KEY!);
const SERVER = process.env.MAILOSAUR_SERVER_ID!;

test("new user completes email verification", async ({ page }) => {
  const address = qaEmail("vendly", "owner", { unique: true });

  await signUp(page, address);

  // Poll the inbox, scoped to THIS address — never "latest message in the server",
  // which cross-talks the moment a second test runs concurrently.
  const message = await mailbox.messages.get(
    SERVER,
    { sentTo: address },
    { timeout: 30_000 },
  );

  const link = message.html?.links?.find((l) => l.href?.includes("/verify"));
  expect(link?.href).toBeDefined();
  await page.goto(link!.href!);
  await expect(page.getByText("Email verified")).toBeVisible();
});
```

Rules that prevent flake:

- Always filter by `sentTo: address`. "Most recent message" is a race under parallelism.
- Give the poll a real timeout (20–30s). Verification mail is genuinely slow sometimes.
- Assert on a *link or code*, not on body copy — marketing edits should not break tests.
- Delete the message after asserting if the provider bills per stored message.

---

## Local sink for development

No external dependency, no real mail, no account to provision:

```yaml
# docker-compose.dev.yml
services:
  mailpit:
    image: axllent/mailpit
    ports:
      - "1025:1025"   # SMTP — point the app's mailer here
      - "8025:8025"   # web UI
```

Point `SMTP_HOST=localhost` / `SMTP_PORT=1025` in `.env.development`. The Firebase Auth
emulator is equivalent for auth flows: it prints the verification link to its own log
instead of sending, which is enough for local work and needs no SMTP at all.

---

## Cascading teardown

The failure mode is always a partial delete. Order matters, and every step must tolerate
"already gone" so a re-run after a crash converges.

```ts
// scripts/reap-qa-accounts.ts
import { assertNotProduction } from "../src/utils/env-guard";
import { isQaEmail } from "../tests/support/qa-email";

export async function reapQaAccount(email: string) {
  assertNotProduction();                       // same guard as the seed scripts
  if (!isQaEmail(email)) {
    throw new Error(`refusing to delete non-QA address: ${email}`);
  }

  const user = await auth.getUserByEmail(email).catch(() => null);

  // Dependency order: anything referencing the user goes before the user itself.
  await deleteAnalyticsIdentity(email).catch(ignoreMissing);
  await deleteStorageObjects(`users/${user?.uid}/`).catch(ignoreMissing);
  await deleteStripeCustomerByEmail(email).catch(ignoreMissing);
  await deleteDatabaseRows(user?.uid).catch(ignoreMissing);
  if (user) await auth.deleteUser(user.uid).catch(ignoreMissing);

  return { email, deleted: true };
}

const ignoreMissing = (e: unknown) => {
  if (isNotFound(e)) return;
  throw e;
};
```

Two guards, both load-bearing:

- `assertNotProduction()` — the environment guard this skill already generates.
- `isQaEmail()` — a positive allow-list. Deleting by "looks like a test account" is how
  a real customer eventually gets reaped.

**Stripe specifically:** customers are the resource that silently accumulates. Search by
email and delete in test mode; live-mode customers must never be reachable from this script
(separate keys, enforced by the env guard). Test clocks cap at 3 active per account — delete
them in the same pass or subscription tests start failing on an unrelated PR.

**Invocation — no cron.** Cure org policy (2026-08-08) forbids scheduled jobs, so expose
teardown as an explicit target and call it from the places that already run:

```json
{ "scripts": { "qa:reap": "tsx scripts/reap-qa-accounts.ts" } }
```

Call it in an E2E `afterAll` for addresses that test created, and run `qa:reap --older-than 30d`
by hand when cleaning house. An accumulating estate is visible in the address dates, which is
why the naming convention encodes them.

---

## Provider notes

| Provider | Catch-all | Inbox API | Notes |
|---|---|---|---|
| Google Workspace | Yes (routing rule) | No | Catch-all is a routing setting, not a mailbox; needs a real destination |
| Fastmail | Yes | No | Simple catch-all + masked addresses |
| Cloudflare Email Routing | Yes | No | Free catch-all → forward; good for a cheap `qa.<project>.dev` |
| Mailosaur | n/a | Yes | Per-server addresses, HTML link extraction built in |
| MailSlurp | n/a | Yes | Creates disposable inboxes on demand |
| Testmail.app | n/a | Yes | Namespace + tag addressing, GraphQL API |
| Mailpit / MailHog | n/a | Local only | Development sink; never reachable from CI |

Choosing: a catch-all domain and an inbox-API provider are complements, not alternatives.
The domain serves humans on staging; the API serves CI. Most projects need both.
