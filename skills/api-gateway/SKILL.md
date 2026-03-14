---
name: api-gateway
description: "Design API gateway and BFF layers — rate limiting, request transformation, auth middleware, GraphQL federation, and mobile-optimized backends"
argument-hint: "[api-or-project]"
---

# API Gateway

Design the layer between your clients and your services. A well-designed gateway simplifies clients, enforces security, and enables independent backend evolution.

## Step 1: Classify the Gateway Need

| Need | Output |
|------|--------|
| API gateway setup | Gateway architecture + routing config + middleware stack |
| BFF pattern | Per-client backend with aggregation and transformation |
| GraphQL gateway | Federated schema + subgraph design + performance config |
| Rate limiting | Rate limit strategy + implementation per tier |
| API versioning | Versioning strategy + migration plan + deprecation policy |
| Auth middleware | Authentication + authorization middleware pipeline |

## Step 2: Gather Context

1. **Backend services** — how many services? REST, gRPC, GraphQL? Monolith or microservices?
2. **Client platforms** — mobile (iOS/Android), web (SPA/SSR), third-party API consumers?
3. **Auth mechanism** — Firebase Auth, Auth0, custom JWT, API keys, OAuth2?
4. **Traffic volume** — requests/second (current and projected), burst patterns?
5. **Latency requirements** — p99 target? Real-time features? Mobile on 3G?
6. **Team size** — separate frontend/backend teams? Multiple backend teams?

## Step 3: Gateway Architecture

```
Choose the pattern that matches your team and product:

SINGLE GATEWAY (start here)
  All clients → one gateway → backend services

  When to use:
    - Small team (<10 engineers)
    - 1-3 backend services
    - Uniform client needs

  Implementation:
    - Cloud Run / Cloud Functions as gateway layer
    - Express or Fastify with middleware pipeline
    - Route by path prefix: /api/v1/users → user-service
    - Apply auth, rate limiting, logging at gateway

  Pros: simple, one place for cross-cutting concerns
  Cons: becomes bottleneck as team/services grow

BFF — BACKEND FOR FRONTEND (recommended at scale)
  Mobile app → Mobile BFF → backend services
  Web app    → Web BFF    → backend services
  Partners   → Partner API → backend services

  When to use:
    - Different clients need different data shapes
    - Mobile needs aggregated, minimal payloads
    - Web uses SSR with different data requirements
    - Third-party API has different auth/rate limits

  Implementation:
    - Mobile BFF: Cloud Run (lightweight, fast cold start)
    - Web BFF: Next.js API routes or server components (colocated with frontend)
    - Partner API: separate service with API key management

  Pros: each client gets optimal API, teams work independently
  Cons: code duplication across BFFs (mitigate with shared libraries)

SIDECAR PROXY (service mesh)
  Each service → sidecar (Envoy/Istio) → handles routing, auth, observability

  When to use:
    - Many services (10+) with service-to-service communication
    - Platform team managing infrastructure for multiple product teams
    - Need mTLS between services

  Overkill for: most projects. Don't adopt unless you have a platform team.

Technology selection:
  | Option | Best For | Cold Start | Cost |
  |--------|----------|-----------|------|
  | Cloud Run + Express | BFF, lightweight gateway | ~200ms | Per-request |
  | Next.js API routes | Web BFF (colocated) | N/A (server) | Included |
  | Firebase Cloud Functions | Simple gateway | ~500ms | Per-invocation |
  | Kong / Apigee | Enterprise API management | N/A | License |
  | Cloudflare Workers | Edge gateway, <50ms latency | ~0ms | Per-request |

Cure default: Cloud Run for dedicated gateways, Next.js API routes for web BFF.
```

## Step 4: BFF — Backend for Frontend

```
Mobile BFF — optimize for constrained devices:

  Aggregate calls:
    Instead of: client makes 5 API calls to render home screen
    Do: client makes 1 call to /mobile/home, BFF aggregates internally

    // Mobile BFF endpoint
    GET /mobile/v1/home
    Response: {
      user: { name, avatar_url, plan },
      feed: [ top 10 items, pre-formatted ],
      notifications: { unread_count },
      feature_flags: { ... }
    }

  Reduce payload size:
    - Strip fields mobile doesn't use (backend returns 40 fields, mobile needs 8)
    - Compress images to mobile-appropriate dimensions
    - Use pagination with small page sizes (20 items, not 100)
    - Return pre-computed display strings ("2 hours ago" not ISO timestamp)

  Platform-specific transformations:
    - iOS: return image URLs with @2x/@3x variants
    - Android: return dimension values in dp
    - Both: format currencies, dates in device locale

Web BFF — optimize for SSR and streaming:

  Next.js Server Components as BFF (recommended for web):
    // app/dashboard/page.tsx — this IS your BFF
    export default async function Dashboard() {
      const [user, stats, feed] = await Promise.all([
        fetchUser(),       // calls user-service
        fetchStats(),      // calls analytics-service
        fetchFeed(),       // calls content-service
      ]);
      return <DashboardView user={user} stats={stats} feed={feed} />;
    }

  Benefits:
    - No separate BFF deployment — server components are the BFF
    - Streaming: components render as data arrives (Suspense boundaries)
    - Colocated: data fetching lives next to the component that uses it
    - Type-safe: shared types between fetch functions and components

Shared logic extraction:
  Create a shared package for logic common to all BFFs:
    @cure/gateway-core
      ├── auth/          — JWT validation, token refresh
      ├── logging/       — structured request/response logging
      ├── errors/        — error transformation (internal → client-safe)
      ├── cache/         — caching strategies (Redis, in-memory)
      └── health/        — health check endpoints
```

## Step 5: Security Middleware

```
Apply middleware in this order — fail fast on security:

1. REQUEST ID
   Generate unique request ID (X-Request-ID header)
   Propagate to all downstream services for tracing

2. CORS
   Strict origin allowlist — never use Access-Control-Allow-Origin: *
   Credential handling: only allow with specific origins
   Preflight caching: Access-Control-Max-Age: 86400 (24 hours)

   const corsConfig = {
     origin: ['https://app.example.com', 'https://staging.example.com'],
     credentials: true,
     methods: ['GET', 'POST', 'PUT', 'DELETE'],
     allowedHeaders: ['Content-Type', 'Authorization'],
     maxAge: 86400,
   };

3. AUTH VERIFICATION
   JWT validation:
     - Verify signature (RS256, not HS256 for public clients)
     - Check expiration (reject expired tokens, no grace period)
     - Validate issuer and audience claims
     - Extract user context for downstream services

   API key management:
     - Hash keys in storage (never store plaintext)
     - Prefix keys for identification: sk_live_xxx, sk_test_xxx
     - Rotate keys with overlap period (old key valid for 24h after rotation)
     - Rate limit per key, not just per IP

   Firebase Auth verification:
     import { getAuth } from 'firebase-admin/auth';
     const decodedToken = await getAuth().verifyIdToken(idToken);

4. RATE LIMITING
   Strategy by tier:
     Anonymous:      10 req/min per IP (strict)
     Authenticated:  100 req/min per user (standard)
     Premium:        1000 req/min per user (elevated)
     Internal:       no limit (service-to-service with mTLS)

   Algorithm: sliding window (recommended)
     - More fair than fixed window (no burst at window boundary)
     - Implementation: Redis sorted set with timestamp scores
     - Include rate limit headers in response:
       X-RateLimit-Limit: 100
       X-RateLimit-Remaining: 87
       X-RateLimit-Reset: 1679012345

   Per-endpoint limits (layer on top of per-user):
     POST /api/auth/login:   5/min (brute force protection)
     POST /api/upload:       10/min (resource-intensive)
     GET  /api/search:       30/min (expensive queries)
     GET  /api/feed:         120/min (high-frequency, low-cost)

5. REQUEST VALIDATION
   Schema validation (use Zod or Joi):
     - Validate request body against schema before handler
     - Reject with 400 + specific validation errors
     - Payload size limit: 1MB default, increase per-endpoint if needed
     - Content-Type enforcement: reject unexpected content types

6. LOGGING
   Structured request log (every request):
     { request_id, method, path, status, duration_ms, user_id, ip }
   Never log: request bodies with PII, auth tokens, passwords
   Log separately: 4xx errors (client issues), 5xx errors (our issues)
```

## Step 6: GraphQL Federation

```
Use federation when multiple teams own different parts of the graph.

Schema stitching vs federation:
  Stitching: gateway merges schemas (simple, centralized control)
  Federation: each service owns its subgraph (decentralized, scales with teams)

  Use stitching for: <5 services, one team, simple composition
  Use federation for: 5+ services, multiple teams, shared entities

Subgraph design:
  Each subgraph = one bounded context:
    users-subgraph:    User, Profile, Authentication
    products-subgraph: Product, Category, Inventory
    orders-subgraph:   Order, Payment, Shipping

  Shared types (entity references):
    // users-subgraph
    type User @key(fields: "id") {
      id: ID!
      name: String!
      email: String!
    }

    // orders-subgraph
    type User @key(fields: "id") {
      id: ID!
      orders: [Order!]!   // extends User with orders
    }

Performance with DataLoader:
  Every resolver that fetches from a service MUST use DataLoader:
    - Batches multiple individual fetches into one bulk request
    - Per-request cache prevents duplicate fetches within one query
    - Without DataLoader: N+1 queries kill performance at scale

  const userLoader = new DataLoader(async (ids) => {
    const users = await userService.getByIds(ids);
    return ids.map(id => users.find(u => u.id === id));
  });

Query complexity limits:
  - Assign cost to each field (1 for scalars, 10 for lists, 5 for relations)
  - Reject queries exceeding max complexity (e.g., 1000)
  - Prevents: deeply nested queries, denial-of-service via expensive queries
  - Depth limit: max 10 levels of nesting

Gateway implementation:
  Apollo Router (recommended for federation v2):
    - Rust-based, high-performance query planner
    - Supports @defer for streaming partial responses
    - Built-in telemetry (OpenTelemetry compatible)

  Alternatives:
    - Mercurius (Fastify) for stitching
    - Yoga + Envelop for custom gateway
    - Hasura for database-to-GraphQL with federation support
```

## Step 7: Monitoring and Analytics

```
Gateway is the single best place to observe all API traffic.

Request logging (structured, every request):
  {
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "req_abc123",
    "method": "GET",
    "path": "/api/v1/users/456",
    "status": 200,
    "duration_ms": 45,
    "user_id": "user_789",
    "client": "mobile-ios/3.2.1",
    "rate_limit_remaining": 87,
    "upstream_service": "user-service",
    "upstream_duration_ms": 32,
    "cache_hit": false
  }

Latency tracking:
  Track percentiles, not averages:
    p50: typical user experience
    p95: degraded experience (1 in 20 requests)
    p99: worst case (investigate if > 2x p50)

  Set alerts:
    p50 > 200ms: investigate
    p95 > 500ms: action required
    p99 > 1000ms: incident

  Track per-endpoint latency — aggregate latency hides problems.

Error rate monitoring:
  4xx rate: client errors (bad requests, auth failures)
    - Spike in 401s = auth issue, token expiry problem
    - Spike in 429s = rate limit too aggressive, or a client is abusing
    - Spike in 400s = client bug, or API contract changed

  5xx rate: server errors (our fault)
    - Target: <0.1% of all requests
    - Alert at: >0.5% sustained for 5 minutes
    - Page at: >1% sustained for 2 minutes

Usage analytics per consumer:
  Track per API key / client app:
    - Total requests per day/week/month
    - Top endpoints by volume
    - Error rate per consumer
    - Latency per consumer

  Use for:
    - Identifying heavy consumers for optimization
    - Deprecation planning (who uses old endpoints?)
    - Capacity planning (growth trends)
    - Client support (reproduce issues with their traffic pattern)

Dashboard (build in Grafana, Datadog, or Cloud Monitoring):
  Row 1: Total RPS, error rate, p50/p95/p99 latency
  Row 2: Per-endpoint breakdown (top 10 by volume)
  Row 3: Per-consumer breakdown (top 10 by volume)
  Row 4: Rate limiting (rejections/min, top rejected consumers)
  Row 5: Upstream health (per-service latency and error rate)
```

## Cross-References

- `/api-architect` — REST and GraphQL API design that the gateway routes to
- `/infrastructure-scaffold` — cloud infrastructure for deploying gateway services
- `/security-review` — comprehensive security audit including gateway layer
- `/performance-review` — load testing and latency optimization for gateway
- `/firebase-architect` — Firebase Auth integration and Cloud Functions as backend
- `/observability` — monitoring and alerting for gateway health
