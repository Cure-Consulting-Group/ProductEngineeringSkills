---
name: api-architect
description: "Design REST/GraphQL APIs with versioning, auth, rate limiting, and error standards"
argument-hint: "[api-name]"
---

# API Architect

Design production REST and GraphQL APIs with versioning, authentication, error handling, and documentation. For backends beyond Firebase — Node.js, Python, Go, or any HTTP service.

## Pre-Processing (Auto-Context)

Before starting, gather project context silently:
- Read `PORTFOLIO.md` if it exists in the project root or parent directories for product/team context
- Run: `cat package.json 2>/dev/null || cat build.gradle.kts 2>/dev/null || cat Podfile 2>/dev/null` to detect stack
- Run: `git log --oneline -5 2>/dev/null` for recent changes
- Run: `ls src/ app/ lib/ functions/ 2>/dev/null` to understand project structure
- Use this context to tailor all output to the actual project

## Step 1: Classify the API Type

| Need | Pattern |
|------|---------|
| Standard CRUD | REST with resource-based routes |
| Complex queries, multiple clients | GraphQL |
| Real-time data | WebSocket or Server-Sent Events |
| Webhook receiver | HTTP POST endpoint with signature verification |
| Third-party integration | REST client with retry and circuit breaker |
| Internal microservice | REST or gRPC depending on performance needs |
| Public developer API | REST with API keys, rate limits, versioned |

## Step 2: Gather Context

1. **API purpose** — internal, partner, or public?
2. **Consumers** — mobile app, web app, third-party, or all?
3. **Auth model** — Firebase Auth, JWT, API keys, OAuth 2.0?
4. **Data model** — what entities and relationships?
5. **Scale** — expected requests per second?
6. **Versioning** — how will breaking changes be handled?

## Step 3: REST API Design Standards

### URL Structure
```
/{version}/{resource}                    GET (list), POST (create)
/{version}/{resource}/{id}               GET (read), PUT (update), DELETE
/{version}/{resource}/{id}/{sub-resource} Nested resources

Examples:
  GET    /v1/users                       List users
  POST   /v1/users                       Create user
  GET    /v1/users/123                   Get user 123
  PUT    /v1/users/123                   Update user 123
  DELETE /v1/users/123                   Delete user 123
  GET    /v1/users/123/orders            List user 123's orders

Rules:
  - Plural nouns for resources (users, not user)
  - Lowercase, hyphen-separated (payment-methods, not paymentMethods)
  - No verbs in URLs (POST /users, not POST /create-user)
  - Nest max 2 levels deep (/users/123/orders, not /users/123/orders/456/items)
```

### HTTP Methods & Status Codes
```
GET     200 (OK), 404 (Not Found)
POST    201 (Created), 400 (Bad Request), 409 (Conflict)
PUT     200 (OK), 404 (Not Found), 400 (Bad Request)
DELETE  204 (No Content), 404 (Not Found)
Any     401 (Unauthorized), 403 (Forbidden), 429 (Rate Limited), 500 (Server Error)
```

### Request/Response Format
```json
// Success response (single resource)
{
  "data": { "id": "123", "name": "Acme Corp", "createdAt": "2026-01-15T10:30:00Z" }
}

// Success response (list)
{
  "data": [{ ... }, { ... }],
  "pagination": {
    "page": 1,
    "perPage": 20,
    "total": 142,
    "hasMore": true
  }
}

// Error response
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Email is required",
    "details": [
      { "field": "email", "message": "must be a valid email address" }
    ]
  }
}
```

### Pagination (cursor-based preferred)
```
Offset-based:  ?page=2&per_page=20       (simple, but skip-count is slow on large sets)
Cursor-based:  ?cursor=abc123&limit=20    (performant, stable for real-time data)
```

### Filtering, Sorting, Search
```
Filter:  GET /v1/orders?status=active&created_after=2026-01-01
Sort:    GET /v1/orders?sort=-created_at  (- prefix = descending)
Search:  GET /v1/users?q=rashad
Fields:  GET /v1/users?fields=id,name,email  (sparse fieldsets)
```

## Step 4: Authentication Patterns

```
Firebase Auth (mobile + web):
  Client sends Firebase ID token in Authorization header
  Server verifies with admin.auth().verifyIdToken(token)

JWT (custom backend):
  Access token:  short-lived (15min-1hr), stateless
  Refresh token: long-lived (7-30 days), stored server-side
  Rotation:      new refresh token on each use, old one invalidated

API Keys (third-party / public API):
  Sent in X-API-Key header (never in URL)
  Scoped to specific permissions
  Rate limited per key
  Rotatable without downtime
```

## Step 5: Rate Limiting

```
Default limits:
  Authenticated:    100 requests/minute per user
  Unauthenticated:  20 requests/minute per IP
  Write operations:  30 requests/minute per user
  Webhook receivers: 1000 requests/minute (Stripe sends bursts)

Response headers:
  X-RateLimit-Limit: 100
  X-RateLimit-Remaining: 42
  X-RateLimit-Reset: 1710100000

429 response:
  Retry-After: 30
```

## Step 6: Versioning Strategy

```
URL versioning (default):   /v1/users, /v2/users
Header versioning:          Accept: application/vnd.api+json;version=2

Rules:
  - v1 is the first version, not v0
  - Additive changes (new fields, new endpoints) don't require new version
  - Breaking changes (removed fields, changed types) require new version
  - Support N-1 version for minimum 6 months after new version
  - Deprecation header: Sunset: Sat, 01 Jan 2027 00:00:00 GMT
```

## Step 7: API Documentation

Every API ships with OpenAPI 3.0 spec:
```yaml
openapi: 3.0.3
info:
  title: API Name
  version: 1.0.0
paths:
  /v1/resource:
    get:
      summary: List resources
      parameters: [...]
      responses:
        '200': { description: Success, content: { ... } }
```

Auto-generate docs from spec using Swagger UI or Redoc.

## Code Generation (Required)

Generate actual API specification using Write:

1. **OpenAPI spec**: `docs/openapi.yaml` — complete OpenAPI 3.1 specification with schemas, paths, security
2. **Error response types**: `src/types/errors.ts` — standardized error response types
3. **API client**: `src/api/client.ts` — type-safe API client generated from spec
4. **Postman collection**: `docs/api-collection.json` — importable Postman collection

Before generating, Glob for existing API routes (`**/api/**`, `**/routes/**`) and Read them to document current state.

## Step 8: Error Handling Standards

```
Error codes (use instead of relying on HTTP status alone):
  VALIDATION_ERROR     — 400, invalid input
  AUTHENTICATION_ERROR — 401, missing or invalid token
  FORBIDDEN            — 403, insufficient permissions
  NOT_FOUND            — 404, resource doesn't exist
  CONFLICT             — 409, duplicate or state conflict
  RATE_LIMITED         — 429, too many requests
  INTERNAL_ERROR       — 500, unexpected server error

Rules:
  - Never expose stack traces, file paths, or SQL in error responses
  - Log full error server-side, return sanitized message to client
  - Include request ID in every response for debugging: X-Request-Id
  - Validation errors include field-level details
```
