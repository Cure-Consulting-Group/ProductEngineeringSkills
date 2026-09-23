---
name: api-architect
description: "Designs REST/GraphQL API contracts: errors, auth, rate limits, versioning, OpenAPI. Use when designing endpoints or an API's error, auth, or deprecation policy."
when_to_use: "NOT for gateway/BFF layers (use api-gateway) or validating an existing API against its spec (api-validator agent)."
argument-hint: "[api-name]"
metadata:
  verified: 2026-09-23
---

# API Architect

**Outcome:** an API contract a client team can build against — an OpenAPI 3.1 document (or GraphQL SDL) plus a short decisions table (auth, errors, pagination, limits, versioning). Done when every endpoint has request/response schemas, an error type, an auth requirement, and a rate-limit class. This skill owns Cure's API policy: rate-limit defaults, error format, versioning and deprecation, and the OpenAPI version. `api-gateway` and other skills link here instead of restating it.

## Pre-Processing (Auto-Context)

Context (pre-filled in Claude Code; in other runtimes run these commands first):

- Existing specs: !`find . -maxdepth 4 \( -name "openapi*.y*ml" -o -name "openapi*.json" -o -name "*.graphql" \) -not -path "*/node_modules/*" 2>/dev/null | head -5 || echo "(none)"`
- Route files: !`find . -maxdepth 5 -path "*/node_modules" -prune -o \( -path "*/api/*" -o -path "*/routes/*" \) -type f -print 2>/dev/null | head -5 || echo "(none)"`

## Step 1: Classify

| Need | Pattern | Output |
|------|---------|--------|
| CRUD over resources | REST | OpenAPI 3.1 + decisions table |
| Many clients, varied read shapes | GraphQL | SDL + complexity/depth limits |
| Server push | SSE (one-way) or WebSocket (two-way) | Event schema + reconnect/resume rules |
| Webhook receiver | HTTP POST | Signature check, idempotency, 2xx-fast + async processing |
| Public developer API | REST + API keys | Everything above + key lifecycle + published deprecation policy |
| Review of an existing design | — | Findings against the conventions below, with severity; no files |

## Step 2: Gather Context

Ask only what the repo doesn't answer: consumers (own mobile/web, partners, public), auth model, core entities, expected peak RPS, and whether old mobile app versions must keep working (they usually must — this drives versioning).

## Step 3: Cure Contract Conventions

These are decisions, not options. Deviate only with a stated reason.

- **Paths:** plural kebab-case resources, `/v1/payment-methods/{id}`; nest at most one level (`/v1/users/{id}/orders`). Actions that aren't CRUD use a sub-resource verb: `POST /v1/orders/{id}/cancel`.
- **Casing:** camelCase for every JSON field *and* query parameter (`perPage`, `createdAfter`, `sort=-createdAt`). One convention across body and query.
- **Timestamps:** RFC 3339 UTC strings (`2026-01-15T10:30:00Z`). Money: integer minor units + ISO 4217 currency (`{ "amount": 1999, "currency": "USD" }`), never floats.
- **Envelope:** `{ "data": … }`; lists add `"pagination": { "nextCursor": "…", "hasMore": true }`. Cursor pagination by default (`?cursor=…&limit=20`, max 100); offset only for admin UIs under ~100k rows.
- **Idempotency:** any POST that moves money or sends messages accepts an `Idempotency-Key` header; store key + response for 24 h and replay on retry.
- **Request ID:** every response carries `X-Request-Id`; propagate it downstream and include it in error bodies.

## Step 4: Errors — RFC 9457 Problem Details

All errors are `application/problem+json` (RFC 9457, which obsoletes RFC 7807). Standard members plus Cure extension members `code`, `requestId`, and `errors[]` for validation:

```json
{
  "type": "https://api.example.com/problems/validation-error",
  "title": "Validation failed",
  "status": 400,
  "detail": "2 fields are invalid",
  "code": "VALIDATION_ERROR",
  "requestId": "req_7Hk2",
  "errors": [{ "field": "email", "message": "must be a valid email address" }]
}
```

| `code` | Status | Notes |
|---|---|---|
| `VALIDATION_ERROR` | 400 / 422 | Field-level `errors[]` required |
| `AUTHENTICATION_ERROR` | 401 | Missing, expired, or revoked token |
| `FORBIDDEN` | 403 | Authenticated but not allowed; don't reveal whether the resource exists if that leaks data (use 404) |
| `NOT_FOUND` | 404 | |
| `CONFLICT` | 409 | Duplicate or state conflict; also idempotency-key reuse with a different body |
| `RATE_LIMITED` | 429 | Always with `Retry-After` |
| `INTERNAL_ERROR` | 500 | Generic `detail`; never stack traces, SQL, or file paths — log those server-side keyed by `requestId` |

Clients switch on `code`, never on `detail` text.

## Step 5: Authentication

- **Firebase Auth (Cure default for own apps):** client sends the ID token as `Authorization: Bearer …`; server verifies with the modular Admin SDK — `import { getAuth } from 'firebase-admin/auth'; await getAuth().verifyIdToken(token, true)`. Pass `checkRevoked: true` on sensitive routes (payments, account changes); it costs an extra lookup.
- **Custom JWT:** access token 15–60 min, refresh token rotated on every use with reuse detection (a reused refresh token revokes the family). Asymmetric signing (RS256/ES256) when anything other than the issuer verifies.
- **API keys (partners/public):** `X-API-Key` header, never the URL. Prefix by environment (`sk_live_`, `sk_test_`), store only a hash, scope per key, allow two active keys during rotation.

## Step 6: Rate Limits (canonical defaults)

| Class | Limit | Key |
|---|---|---|
| Anonymous | 20 req/min | IP |
| Authenticated | 100 req/min | user or API key |
| Writes | 30 req/min | user |
| Auth endpoints (login, OTP, password reset) | 5 req/min | IP **and** account |
| Expensive (search, upload, export) | 10–30 req/min | user |
| Webhook receivers | 1,000 req/min | source (Stripe and similar send bursts) |
| Service-to-service | none at the edge | mTLS / service identity |

Paid tiers may raise the authenticated limit; record the tier table in the decisions table. Over the limit: `429` + `Retry-After` (seconds). Quota headers: the IETF `RateLimit` / `RateLimit-Policy` fields (e.g. `RateLimit-Policy: "default";q=100;w=60`, `RateLimit: "default";r=42;t=30`) are still an Internet-Draft (draft-ietf-httpapi-ratelimit-headers-11, May 2026) and the syntax has changed between drafts — confirm before use, and keep legacy `X-RateLimit-Limit/Remaining/Reset` only where existing clients already parse them.

## Step 7: Versioning and Deprecation

- Major version in the URL (`/v1`); start at v1. Additive changes (new fields, endpoints, enum values clients were told to tolerate) stay in the version; removals, renames, type or semantics changes need a new major.
- Support N-1 for at least 6 months after the successor ships — longer when old mobile builds can't be forced to update. Pair every sunset with a Remote Config force-update gate in the apps.
- Announce with headers on every response from the deprecated surface: `Deprecation: @1767225600` (RFC 9745, a Structured Field date) plus `Sunset: Thu, 01 Jul 2027 00:00:00 GMT` (RFC 8594) and `Link: <https://…/migration>; rel="deprecation"`. The Sunset date must not be earlier than the Deprecation date.
- Log usage per client version on deprecated endpoints so you know who is still calling before you turn it off.

## Step 8: Spec and GraphQL Rules

- **OpenAPI 3.1** is the Cure default: schemas are JSON Schema 2020-12, so nullable is `type: [string, "null"]` (the 3.0 `nullable: true` keyword is gone). OAS 3.2.0 was released in September 2025; adopt it only once the project's generator, validator, and docs renderer support it — confirm before use.
- Every operation has an `operationId`, a `security` requirement (or explicit `security: []`), and a `default` response referencing the Problem Details schema.
- **GraphQL:** DataLoader on every resolver that fetches from a store; query depth ≤10 and a cost limit enforced before execution; errors use `extensions.code` with the same codes as the REST table. Federation and gateway composition belong to `api-gateway`.

## Code/Artifact Generation

Applies only when Step 1 calls for building a new or revised contract (not reviews or questions). Read existing specs and routes first and extend them rather than replacing.

1. `docs/openapi.yaml` — OpenAPI 3.1 with schemas, security schemes, and the Problem Details component.
2. Error types for the server's language (e.g. `src/types/problem.ts`) matching Step 4.
3. A typed client only if the project has no generator already; prefer generating it from the spec.

Deliver the requested artifact; don't refactor route handlers or add unrequested files.

## Related skills

- `api-gateway` — BFF, gateway middleware order, and GraphQL federation; enforces the limits above.
- `api-validator` agent — checks an implementation against the spec.
- `security-review` — threat modelling of the auth and key design.
