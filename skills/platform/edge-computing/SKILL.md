---
name: edge-computing
description: "Designs CDN caching, invalidation, and Next.js proxy routing on Vercel/Firebase. Use when cutting TTFB, setting Cache-Control, geo-routing, edge auth, or rate limits."
when_to_use: "NOT for a full performance audit (use performance-review) or building a Next.js feature (use nextjs-feature-scaffold)."
argument-hint: "[use-case-or-platform]"
metadata:
  verified: 2026-09-23
---

# Edge Computing

Caching and request-time logic in front of Cure's origins (Next.js on Vercel or Firebase App
Hosting, Firebase Hosting + Cloud Run/Functions). **Done when** each route has a caching decision
(static / ISR / stale-while-revalidate / no-store) with a named invalidation path, request-time logic
lives in `proxy.ts` only where it must run before render, and TTFB and cache-hit targets are stated.
Deliver the requested pieces; don't refactor unrelated routes.

When the Vercel plugin skills are installed, defer to them for platform detail: routing-middleware
for Routing Middleware, cdn-caching for cache debugging, vercel-firewall for WAF and rate-limit rules.

## Pre-Processing (Auto-Context)

Context — run these read-only commands first; skip any that fail or aren't permitted (they only tailor the output):

- Next.js version: `(grep -E '"next"|"@vercel/functions"|"@upstash/' package.json 2>/dev/null || echo "(no Next.js)") | head -5`
- Proxy/middleware file: `(ls proxy.ts src/proxy.ts middleware.ts src/middleware.ts 2>/dev/null || echo "(none)") | head -4`
- Hosting config: `(ls vercel.json vercel.ts firebase.json apphosting.yaml 2>/dev/null || echo "(none)") | head -4`

## Step 1: Classify

| Type | Output |
|---|---|
| Caching strategy | Per-route cache table, headers, invalidation path |
| Request-time routing (geo, A/B, rewrites) | `proxy.ts` logic + matcher |
| Edge auth / rate limiting | Optimistic auth check in proxy, rate-limit rule |
| Global distribution / data residency | Region choice for functions and data, routing config |
| Review of an existing setup | Findings with severity (stale APIs, uncacheable routes, low hit ratio) — no new files |

## Step 2: Gather Context

Ask only what the repo doesn't show: TTFB target and where users are, data-residency constraints
(GDPR, client contracts), share of personalized vs cacheable content, CMS or webhook that changes
content.

## Step 3: Current Platform Facts (verified 2026-09-23)

- **Next.js 16 renamed `middleware.ts` → `proxy.ts`** (export `proxy`); proxy runs on the Node.js
  runtime and `runtime` config is not allowed there. Migrate with
  `npx @next/codemod@canary middleware-to-proxy .`. Next 16.3 no longer supports
  `runtime = 'edge'` on routes or pages.
- **Vercel recommends Node.js over the Edge runtime**; both run on Fluid compute. Don't design new
  work around edge isolates — "edge" now means *the CDN and request-time logic*, not a runtime.
- **Geo and IP**: `request.geo` / `request.ip` were removed in Next 15. On Vercel use
  `geolocation(request)` and `ipAddress(request)` from `@vercel/functions`; elsewhere read the
  provider's headers.
- **Vercel KV is retired** — use Upstash Redis (or another store) from the Vercel Marketplace.
  **Edge Config** remains for low-latency, read-mostly flags and redirects.
- **`revalidateTag(tag, profile)`** — the one-argument form is deprecated. Use `'max'`
  (stale-while-revalidate) by default, `updateTag(tag)` inside Server Actions for read-your-writes,
  and `{ expire: 0 }` from webhooks that need data gone immediately.
- **Firebase Hosting** rewrites to Cloud Run with `"run": { "serviceId": …, "region": … }` (v2
  functions are Cloud Run services). Firebase Dynamic Links shut down in August 2025 — remove any
  `dynamicLinks` keys.

## Step 4: Caching (the main lever)

| Content | Cache-Control | Invalidation |
|---|---|---|
| Hashed JS/CSS/fonts/images | `public, max-age=31536000, immutable` | New filename per build |
| Unhashed images | `public, max-age=86400, stale-while-revalidate=3600` | TTL |
| Marketing / blog / docs pages | ISR or `'use cache'` + `cacheTag` | `revalidateTag(tag, 'max')` from the CMS webhook |
| Listings, feeds, search | `public, s-maxage=60, stale-while-revalidate=300` | TTL |
| HTML shell (non-ISR) | `public, max-age=0, must-revalidate` | Deploy |
| Personalized or authenticated responses | `private, no-store` | — |

Gotchas that cost hit ratio: a `Set-Cookie` on a cacheable response, `Vary` on high-cardinality
headers, unnormalized query strings, and per-user data rendered into shared pages. Never cache
anything with money, inventory, or permissions in it at the CDN.

Revalidation webhook (Route Handler): verify a shared secret with a constant-time compare, then
`revalidateTag(tag, 'max')` or `revalidatePath(path)`.

## Step 5: Request-Time Logic (`proxy.ts`)

Keep proxy thin: redirects, rewrites, headers, cookie-based routing. Always set a `matcher` that
excludes `_next/static`, `_next/image`, and public assets. Proxy is an optimistic gate, not the
authorization layer — verify auth again in every Server Function and Route Handler (a matcher change
can silently drop coverage).

```typescript
// proxy.ts — geo header + stable A/B bucket (Vercel)
import { NextResponse, type NextRequest } from "next/server";
import { geolocation } from "@vercel/functions";

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|webp)$).*)"],
};

async function bucket(id: string): Promise<"control" | "variant-a"> {
  const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(`checkout:${id}`));
  return new Uint8Array(digest)[0] < 128 ? "control" : "variant-a"; // deterministic 50/50
}

export async function proxy(request: NextRequest) {
  const visitorId = request.cookies.get("vid")?.value ?? crypto.randomUUID();
  const variant = await bucket(visitorId);
  const res =
    request.nextUrl.pathname === "/checkout" && variant === "variant-a"
      ? NextResponse.rewrite(new URL("/checkout-v2", request.url))
      : NextResponse.next();
  res.headers.set("x-user-country", geolocation(request).country ?? "US");
  if (!request.cookies.has("vid")) {
    res.cookies.set("vid", visitorId, { path: "/", maxAge: 60 * 60 * 24 * 30, httpOnly: true, sameSite: "lax" });
  }
  return res;
}
```

For experiments with analysis, route assignment through the `feature-flags` skill (Flags SDK or
Remote Config) rather than hand-rolled buckets; this snippet is for simple rewrites.

**Rate limiting.** On Vercel, prefer Firewall rate-limit rules (no code, enforced before your
function). For per-user or per-key limits in code, use `@upstash/ratelimit`:

```typescript
import { Ratelimit } from "@upstash/ratelimit";
import { Redis } from "@upstash/redis";
import { ipAddress } from "@vercel/functions";

const limiter = new Ratelimit({ redis: Redis.fromEnv(), limiter: Ratelimit.slidingWindow(100, "60 s") });
// inside proxy, for /api paths:
const { success } = await limiter.limit(ipAddress(request) ?? "anonymous");
if (!success) return new Response("Too Many Requests", { status: 429, headers: { "Retry-After": "60" } });
```

**Geo / residency.** Geo-routing is fine for localization; it does not satisfy data residency.
Residency is decided by where functions run (Vercel function region, Cloud Run region) and where
data lives (Firestore location is fixed at creation).

## Step 6: Data Near Users

| Store | Consistency | Use for | Never for |
|---|---|---|---|
| Vercel Edge Config | Read-mostly, fast global reads | Flags, redirects, allowlists | Frequent writes |
| Upstash Redis (Marketplace) | Eventual across regions | Rate limits, sessions, counters | Data of record |
| Firestore / Cloud SQL | Strong | Everything of record | Per-request hot counters (contention) |

Always code a fallback for a KV outage (fail open for flags, fail closed for rate limits on auth
endpoints).

## Step 7: Targets and Measurement

Cure defaults: TTFB p75 < 100 ms same-continent, < 200 ms cross-continent; cache hit ratio > 90%
for static assets, > 60% for cacheable dynamic routes. Measure with Vercel Speed Insights /
Observability (`x-vercel-cache`: HIT, MISS, STALE, REVALIDATED), Cloud CDN logs for Firebase, and a
multi-region synthetic check (Checkly or WebPageTest). If TTFB misses: check cache status first,
then cache keys (Vary, cookies, query), then function region vs data region.

## Output

Per-route cache table, proxy logic (if any), invalidation paths, region choices, targets, and
findings with severity for anything stale or uncacheable. Match length to the need; no filler.

## Code/Artifact Generation

Applies only when Step 1 classified the request as a build (not a review or question):

| Classification | Write |
|---|---|
| Caching strategy | Headers in `next.config.ts` / `vercel.json` / `firebase.json`; revalidation Route Handler |
| Request-time routing, edge auth | `proxy.ts` (migrate an existing `middleware.ts` with the codemod first) |
| Rate limiting | Firewall rule description, or the `@upstash/ratelimit` block in `proxy.ts` |
| Global distribution | Region config (function regions, Firestore location decision record) |

## Cross-References

- `performance-review` — full performance audit, Core Web Vitals
- `nextjs-feature-scaffold` — building the routes themselves
- `infrastructure-scaffold` — origin configs
- `security-review` — WAF, auth, headers
- `feature-flags` — experiment assignment and analysis
