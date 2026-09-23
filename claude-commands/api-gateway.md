# API Gateway

**Outcome:** a gateway or BFF design the team can deploy — chosen pattern with the reason, the middleware pipeline in order, the aggregation endpoints each client needs, and (for GraphQL) the subgraph ownership map. Done when every client call path is traced from device to service and every cross-cutting concern has exactly one home. Contract policy (error format, rate-limit defaults, versioning, deprecation headers) is owned by `api-architect`; the gateway enforces it and does not redefine it.

## Pre-Processing (Auto-Context)

Context (pre-filled in Claude Code; in other runtimes run these commands first):

- Stack manifest: !`head -30 package.json 2>/dev/null || echo "(no package.json)"`
- Gateway/BFF code: !`find . -maxdepth 4 -path "*/node_modules" -prune -o \( -iname "*gateway*" -o -iname "*bff*" -o -name "supergraph*.yaml" -o -name "router.yaml" \) -print 2>/dev/null | head -5 || echo "(none)"`

## Step 1: Classify

| Need | Output |
|------|--------|
| First gateway for a product | Pattern choice + middleware pipeline + routing table |
| Mobile or web BFF | Aggregation endpoints + payload contracts per client |
| GraphQL across teams | Subgraph map + entity keys + router config |
| Auth or rate-limit enforcement | Middleware design applying `api-architect`'s policy |
| Review of an existing gateway | Findings with severity; no files |

## Step 2: Gather Context

Ask only what the repo doesn't answer: number of backend services and their protocols, client platforms, auth provider, peak RPS and burstiness, p99 latency target, and how many teams own backends (drives BFF vs single gateway and federation vs one schema).

## Step 3: Choose the Pattern

| Pattern | Choose when | Cure implementation |
|---|---|---|
| Single gateway (start here) | <10 engineers, 1–3 services, similar client needs | Cloud Run service (Express/Fastify) routing by path prefix |
| BFF per client | Clients need different shapes; mobile needs aggregated, small payloads | Web: Next.js Server Components / route handlers are the BFF. Mobile: Cloud Run service. Partners: separate service with API-key management |
| Service mesh sidecar | 10+ services, a platform team, mTLS between services | Envoy/Istio — overkill for nearly every Cure engagement |
| Managed API management | Enterprise partner programs needing a portal and key analytics | Apigee or Kong |
| Edge gateway | Global latency-sensitive auth/routing checks | See `edge-computing` |

Cold-start behaviour varies by runtime, region, bundle size, and min-instances; measure it for the actual service rather than quoting a figure. For latency-sensitive Cloud Run gateways set `min-instances ≥ 1`.

## Step 4: BFF Rules

- **Aggregate per screen.** One call per mobile screen (`GET /mobile/v1/home`) that fans out server-side with `Promise.all` and per-upstream timeouts; a slow optional section degrades to `null` instead of failing the screen.
- **Trim fields,** don't transform semantics. Return only what the client renders; keep raw, cacheable values — ISO timestamps, integer money with currency, image URLs with size variants (`w=` params or @2x/@3x). Relative time ("2 hours ago"), currency formatting, and layout units are formatted on the device in the user's locale; server-formatted strings break caching and i18n.
- **Page small** (20 items) with cursors per `api-architect`.
- **Web BFF:** Next.js Server Components fetch in parallel and stream with Suspense; there is no separate BFF deployment. Put auth checks in the data layer, not only in `proxy.ts`/middleware (CVE-2025-29927 bypassed middleware-only auth).
- **Shared code** (token verification, logging, error mapping, health checks) lives in one internal package used by every BFF; BFFs contain aggregation only, never business rules.

## Step 5: Middleware Pipeline (in this order)

1. **Request ID** — accept or mint `X-Request-Id`; propagate downstream and into logs and trace context.
2. **CORS** — explicit origin allowlist; never `*` with credentials; cache preflights (`Access-Control-Max-Age: 86400`).
3. **Body limits and content type** — 1 MB default, raised per route; reject unexpected `Content-Type` before parsing.
4. **Authentication** — Firebase: `getAuth().verifyIdToken()` from `firebase-admin/auth`. JWT: verify signature, `exp`, `iss`, `aud`; asymmetric algorithms for tokens verified outside the issuer. API keys: hashed lookup, per-key scopes. Pass a verified user context downstream; services never re-trust raw client headers.
5. **Rate limiting** — enforce `api-architect`'s class table (per IP, per user/key, per route). Sliding-window counters in Redis/Memorystore for multi-instance gateways; an in-memory limiter is wrong as soon as there is more than one instance. Respond per `api-architect` (429 + `Retry-After`).
6. **Validation** — schema-validate (Zod or the OpenAPI schema) before the handler; errors in Problem Details format.
7. **Proxy/aggregate** — per-upstream timeout, retry only idempotent calls, circuit-break on repeated failure.
8. **Access log** — one structured line per request: `requestId, method, route template, status, durationMs, userId, client version, upstream, upstreamMs, cacheHit`. Never log tokens, passwords, or PII bodies. Dashboards, SLOs, and alert thresholds come from `observability`.

## Step 6: GraphQL Federation

- **One schema until two teams collide.** A single GraphQL server (Yoga, Apollo Server) for one team; federation when multiple teams own parts of the graph.
- **Subgraph = bounded context** (users, catalog, orders). Shared entities declare `@key(fields: "id")` in the owning subgraph; other subgraphs contribute fields to the entity, never duplicate its core fields.
- **Router:** Apollo Router (Federation v2) is the default; composition is checked in CI so a subgraph change that breaks the supergraph fails before deploy.
- **Every resolver that hits a store or service uses DataLoader** (batch + per-request cache) — N+1 is the most common federation performance bug.
- **Limits at the router:** max depth 10, a cost budget per operation, persisted queries for first-party apps (reject arbitrary operations from mobile clients in production).

## Code/Artifact Generation

Applies only when Step 1 calls for building a gateway or BFF (not reviews or questions). Read existing gateway code first and extend it.

- Middleware modules for the pipeline in Step 5 (e.g. `src/gateway/middleware/`), a Redis-backed limiter, and a health endpoint that checks upstream reachability.
- For federation: `supergraph.yaml` / router config and one example entity per subgraph.

Deliver what was asked; don't add monitoring stacks or refactor services behind the gateway.

## Related skills

- `api-architect` — contract, errors, rate-limit numbers, versioning.
- `observability` — gateway dashboards, SLOs, alerting.
- `edge-computing` — edge middleware and CDN layers.
- `security-review` — auth and key-handling audit.
- `infrastructure-scaffold` — deploying the gateway service.
