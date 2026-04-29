---
name: edge-computing
version: "1.0.0"
description: "Architect edge computing solutions — edge functions, CDN strategies, cache invalidation, edge middleware, and global latency optimization"
when_to_use: "Use when architecting edge functions, CDN strategies, cache invalidation, or edge middleware for latency-sensitive apps."
argument-hint: "[use-case-or-platform]"
---

# Edge Computing

Edge architecture framework for low-latency, globally distributed applications. Use when optimizing TTFB, implementing edge middleware, designing caching strategies, or distributing compute closer to users. Covers Vercel Edge Functions, Cloudflare Workers, Next.js middleware, and Firebase Hosting.

## Pre-Processing (Auto-Context)

Before starting, gather project context silently:
- Read `PORTFOLIO.md` if it exists in the project root or parent directories for product/team context
- Run: `cat package.json 2>/dev/null || cat build.gradle.kts 2>/dev/null || cat Podfile 2>/dev/null` to detect stack
- Run: `git log --oneline -5 2>/dev/null` for recent changes
- Run: `ls src/ app/ lib/ functions/ 2>/dev/null` to understand project structure
- Use this context to tailor all output to the actual project

## Step 1: Classify the Edge Need

| Type | When to Use | Output |
|------|------------|--------|
| Edge Rendering | SSR at the edge for global low-latency pages | Edge function config, ISR/streaming setup |
| API Edge Proxy | Auth, rate limiting, routing before hitting origin | Edge middleware with request transformation |
| Edge Caching | Static and dynamic content caching strategy | Cache rules, invalidation strategy, hit ratio targets |
| Edge Auth | Token verification at edge to avoid origin round-trips | JWT validation middleware, session handling |
| Global Distribution | Multi-region deployment for latency-sensitive apps | Region selection, data replication, routing config |

## Step 2: Gather Context

1. **Framework** -- Next.js (App Router or Pages), Remix, Astro, plain functions?
2. **CDN/Edge provider** -- Vercel, Cloudflare, Firebase Hosting, AWS CloudFront?
3. **Latency requirements** -- what is the TTFB target? (< 100ms global? < 50ms for primary region?)
4. **Geographic distribution** -- where are your users? Single region, multi-region, or truly global?
5. **Data residency** -- GDPR, data sovereignty, or compliance requirements for where data is processed?
6. **Dynamic vs. static ratio** -- what percentage of your content is personalized vs. cacheable?

## Step 3: Edge Function Patterns

### Vercel Edge Functions
```typescript
// app/api/edge-example/route.ts
// Runs on Vercel's Edge Network — V8 isolates, not Node.js
export const runtime = "edge";
export const preferredRegion = ["iad1", "cdg1", "hnd1"]; // US, EU, Asia

export async function GET(request: Request) {
  const country = request.headers.get("x-vercel-ip-country") || "US";
  const city = request.headers.get("x-vercel-ip-city") || "Unknown";

  // Edge functions are limited: no Node.js APIs, no fs, limited npm packages
  // Use for: routing, auth, personalization, A/B testing
  // Do NOT use for: heavy computation, database writes, file processing

  return new Response(JSON.stringify({ country, city }), {
    headers: { "Content-Type": "application/json" },
  });
}
```

### Cloudflare Workers
```typescript
// worker.ts — runs on Cloudflare's global network (300+ locations)
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);

    // Route to different origins based on path
    if (url.pathname.startsWith("/api")) {
      return fetch(`${env.API_ORIGIN}${url.pathname}`, request);
    }

    // Serve static assets from R2
    if (url.pathname.startsWith("/assets")) {
      const object = await env.ASSETS_BUCKET.get(url.pathname.slice(8));
      if (!object) return new Response("Not found", { status: 404 });
      return new Response(object.body, {
        headers: { "Cache-Control": "public, max-age=31536000, immutable" },
      });
    }

    // Default: proxy to origin
    return fetch(request);
  },
};
```

### Next.js Middleware (Edge Runtime)
```typescript
// middleware.ts — runs before every matched request
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export const config = {
  matcher: [
    // Match all paths except static files and _next
    "/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)",
  ],
};

export function middleware(request: NextRequest) {
  const response = NextResponse.next();

  // Geolocation routing
  const country = request.geo?.country || "US";
  response.headers.set("x-user-country", country);

  // Security headers (applied at edge, before origin)
  response.headers.set("X-Frame-Options", "DENY");
  response.headers.set("X-Content-Type-Options", "nosniff");
  response.headers.set("Referrer-Policy", "strict-origin-when-cross-origin");

  return response;
}
```

### Firebase Hosting Rewrites (Edge-Level Routing)
```json
{
  "hosting": {
    "rewrites": [
      { "source": "/api/**", "function": "api" },
      { "source": "/app/**", "destination": "/app/index.html" },
      {
        "source": "/blog/**",
        "dynamicLinks": false,
        "function": { "functionId": "blogSSR", "region": "us-central1" }
      }
    ],
    "headers": [
      {
        "source": "**/*.@(js|css)",
        "headers": [{ "key": "Cache-Control", "value": "public, max-age=31536000, immutable" }]
      },
      {
        "source": "/api/**",
        "headers": [{ "key": "Cache-Control", "value": "no-store" }]
      }
    ]
  }
}
```

## Step 4: Caching Strategy

### Cache Hierarchy
```
Request → Edge Cache (CDN PoP) → Origin Shield → Origin Server → Database

Layer             TTL              Use For
──────────────────────────────────────────────────────────────
Browser cache     varies           Static assets, user-specific data
Edge cache        60s - 1 year     Pages, API responses, images
Origin shield     same as edge     Single origin cache before server
Application       varies           In-memory, Redis, KV store
Database          N/A              Source of truth
```

### Static Asset Caching
```
Asset Type          Cache-Control Header                        Rationale
──────────────────────────────────────────────────────────────────────────────
JS/CSS (hashed)     public, max-age=31536000, immutable         Content-hash in filename = safe to cache forever
Images (hashed)     public, max-age=31536000, immutable         Same — fingerprinted filenames
Images (unhashed)   public, max-age=86400, stale-while-revalidate=3600   May change, 1 day cache
Fonts               public, max-age=31536000, immutable         Fonts never change per version
HTML pages          public, max-age=0, must-revalidate          Always check for fresh version
API responses       no-store                                     Dynamic, personalized — do not cache
```

### ISR (Incremental Static Regeneration)
```typescript
// app/blog/[slug]/page.tsx — Next.js ISR
export const revalidate = 3600; // Revalidate every hour

export async function generateStaticParams() {
  const posts = await getPosts();
  return posts.map((post) => ({ slug: post.slug }));
}

// How ISR works at the edge:
// 1. First request: serve static page from edge cache
// 2. After revalidate period: serve stale, trigger background regeneration
// 3. Next request: serve freshly regenerated page
// 4. Result: always fast (cached), eventually fresh

// Use for: blog posts, product pages, marketing pages, docs
// Do NOT use for: dashboards, real-time data, user-specific content
```

### Stale-While-Revalidate Pattern
```
Cache-Control: public, s-maxage=60, stale-while-revalidate=300

Behavior:
  0-60s:    Serve from cache (fresh)
  60-360s:  Serve stale from cache, revalidate in background
  >360s:    Cache expired, fetch from origin (slow for this one request)

This is the single most impactful caching pattern for dynamic content.
Use it for: product listings, search results, feeds, dashboards with acceptable staleness.
```

### Cache Invalidation Strategies
```
Strategy              When to Use                     How
──────────────────────────────────────────────────────────────────
Time-based (TTL)      Predictable freshness needs     Cache-Control max-age
On-demand purge       Content updates (CMS publish)   Purge API call from webhook
Tag-based             Related content groups           Cache tags + purge by tag
Path-based            Specific URL updates             Purge by URL pattern
Stale-while-reval.    Acceptable staleness             s-maxage + stale-while-revalidate

// Next.js on-demand revalidation
// app/api/revalidate/route.ts
import { revalidatePath, revalidateTag } from "next/cache";

export async function POST(request: Request) {
  const { path, tag, secret } = await request.json();
  if (secret !== process.env.REVALIDATION_SECRET) {
    return new Response("Unauthorized", { status: 401 });
  }
  if (tag) revalidateTag(tag);
  if (path) revalidatePath(path);
  return new Response("Revalidated");
}

// Call from CMS webhook:
// POST /api/revalidate { "tag": "blog-posts", "secret": "xxx" }
```

## Step 5: Edge Middleware Patterns

### Auth Verification at Edge
```typescript
// middleware.ts — verify JWT at edge, avoid origin round-trip for unauthorized requests
import { jwtVerify } from "jose";

const PUBLIC_PATHS = ["/", "/login", "/signup", "/api/auth"];

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Skip auth for public paths
  if (PUBLIC_PATHS.some((p) => pathname.startsWith(p))) {
    return NextResponse.next();
  }

  const token = request.cookies.get("session")?.value;
  if (!token) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  try {
    // Verify JWT at edge — no origin round-trip needed
    const secret = new TextEncoder().encode(process.env.JWT_SECRET);
    const { payload } = await jwtVerify(token, secret);
    const response = NextResponse.next();
    response.headers.set("x-user-id", payload.sub as string);
    return response;
  } catch {
    return NextResponse.redirect(new URL("/login", request.url));
  }
}
```

### Geolocation Routing
```typescript
// Route users to region-appropriate content or services
export function middleware(request: NextRequest) {
  const country = request.geo?.country || "US";
  const url = request.nextUrl.clone();

  // Compliance: redirect EU users to EU-hosted version
  const EU_COUNTRIES = ["DE", "FR", "IT", "ES", "NL", "BE", "AT", "SE", "PL"];
  if (EU_COUNTRIES.includes(country) && !url.pathname.startsWith("/eu")) {
    url.pathname = `/eu${url.pathname}`;
    return NextResponse.rewrite(url);
  }

  // Localization: set default language based on region
  const response = NextResponse.next();
  response.cookies.set("preferred-region", country, { path: "/" });
  return response;
}
```

### A/B Testing at Edge
```typescript
// Assign experiment variants at edge — zero client-side flicker
export function middleware(request: NextRequest) {
  const response = NextResponse.next();

  // Check for existing assignment
  let variant = request.cookies.get("experiment-checkout")?.value;

  if (!variant) {
    // Assign variant based on hash of user identifier
    variant = Math.random() < 0.5 ? "control" : "variant-a";
    response.cookies.set("experiment-checkout", variant, {
      path: "/",
      maxAge: 60 * 60 * 24 * 30, // 30 days
    });
  }

  // Rewrite to variant-specific page
  if (request.nextUrl.pathname === "/checkout" && variant === "variant-a") {
    return NextResponse.rewrite(new URL("/checkout-v2", request.url), {
      headers: response.headers,
    });
  }

  return response;
}
```

### Rate Limiting at Edge
```typescript
// Basic edge rate limiting using KV store
export async function middleware(request: NextRequest) {
  if (!request.nextUrl.pathname.startsWith("/api")) {
    return NextResponse.next();
  }

  const ip = request.ip || request.headers.get("x-forwarded-for") || "unknown";
  const key = `rate-limit:${ip}`;

  // In production, use Vercel KV, Cloudflare KV, or Upstash Redis
  // Edge-compatible KV stores only — no Node.js Redis clients
  const current = await kv.incr(key);
  if (current === 1) await kv.expire(key, 60); // 60-second window

  if (current > 100) { // 100 requests per minute
    return new Response("Too Many Requests", {
      status: 429,
      headers: { "Retry-After": "60" },
    });
  }

  return NextResponse.next();
}
```

## Step 6: Data at the Edge

### Edge KV Stores
```
Store                 Provider      Consistency    Use For
──────────────────────────────────────────────────────────────────
Vercel KV             Vercel        Eventual       Session data, rate limits, feature flags
Cloudflare KV         Cloudflare    Eventual       Config, A/B assignments, cached responses
Upstash Redis         Multi-CDN     Eventual       Rate limiting, session, real-time counters
Vercel Edge Config    Vercel        Strong-ish     Feature flags, redirects (< 1s propagation)
Cloudflare D1         Cloudflare    Strong         SQLite at edge — small datasets, read-heavy

Rules:
  - Edge KV is eventually consistent — do NOT use for financial transactions
  - Use for: sessions, feature flags, cached queries, rate limits
  - Do NOT use for: user data of record, payment state, inventory counts
  - Always have a fallback for KV unavailability
```

### Cache Warming
```
Problem: first user in each region gets a cold cache (slow).
Solution: warm caches proactively after deploys or content updates.

# Warm cache for critical pages after deploy
curl -s https://example.com/ > /dev/null &
curl -s https://example.com/pricing > /dev/null &
curl -s https://example.com/blog > /dev/null &
wait

# Warm from multiple regions using synthetic monitoring
# Use: Checkly, Datadog Synthetics, or custom GitHub Action
# Hit critical pages from each target region post-deploy
```

### Consistency Tradeoffs
```
Requirement                    Edge Strategy
──────────────────────────────────────────────────────────────────
Strong consistency needed      Do NOT use edge caching — hit origin
Read-heavy, stale OK           Edge cache with stale-while-revalidate
Write-after-read               Bypass edge cache for authenticated writes
Real-time collaboration        WebSocket to origin, not edge
User-specific data             No edge cache, or cache per-user with Vary header
Public content                 Aggressive edge caching, on-demand purge
```

## Step 7: Performance Measurement

### TTFB by Region
```
Target TTFB (Time to First Byte):
  Primary region:   < 50ms
  Same continent:   < 100ms
  Cross-continent:  < 200ms
  Global worst:     < 500ms

Measure with:
  - Vercel Analytics (built-in, per-route, per-region)
  - Cloudflare Analytics (per-PoP performance)
  - WebPageTest (multi-region, waterfall analysis)
  - Checkly / Datadog Synthetics (continuous monitoring from global locations)

If TTFB > target:
  1. Check if response is cached at edge (x-vercel-cache: HIT vs MISS)
  2. If MISS: check cache rules, TTL, Vary headers
  3. If HIT but slow: check edge function execution time
  4. If no edge: consider adding edge caching or moving compute to edge
```

### Cache Hit Ratio
```
Target: > 90% cache hit ratio for static assets, > 60% for dynamic content

Measure:
  - x-vercel-cache header: HIT, MISS, STALE, REVALIDATED
  - Cloudflare Analytics → Caching tab → cache hit ratio
  - Custom logging: log cache status on every response

If hit ratio is low:
  1. Check Vary headers (too many = low cache hits)
  2. Check TTLs (too short = frequent misses)
  3. Check query parameters (each unique URL = separate cache entry)
  4. Consider normalizing URLs before caching
  5. Remove unnecessary cookies from cached responses
```

### Edge vs. Origin Comparison
```
Metric              Edge        Origin      Impact
──────────────────────────────────────────────────────────────
TTFB (same region)  20-50ms     100-300ms   2-6x faster
TTFB (cross-cont.)  50-100ms    300-800ms   3-8x faster
Throughput           CDN limit   Server cap  10-100x higher
Cost per request     ~$0.00001  ~$0.0001    10x cheaper
Cold start           < 5ms      50-500ms    10-100x faster
Max execution        30s        300s        Origin for long tasks
Node.js APIs         No         Yes         Origin for fs, streams
Database access      KV only    Full        Origin for writes
```

## Step 8: Output

```
EDGE COMPUTING ARCHITECTURE
System: [NAME]
Date: [TODAY]
Prepared by: [NAME]

EDGE SUMMARY
┌──────────────────────────┬────────────────────────────────────┐
│ Field                    │ Value                              │
├──────────────────────────┼────────────────────────────────────┤
│ Edge Provider            │ [Vercel / Cloudflare / Firebase]   │
│ Edge Functions           │ [Count, purpose]                   │
│ Cache Strategy           │ [ISR / SWR / static / none]        │
│ Target TTFB              │ [Xms per region]                   │
│ Cache Hit Ratio Target   │ [X%]                               │
│ Data at Edge             │ [KV store, purpose]                │
│ Regions                  │ [Primary + replicas]               │
└──────────────────────────┴────────────────────────────────────┘

DELIVERABLES GENERATED:
  - [ ] Edge function configurations per route
  - [ ] Caching strategy with TTL and invalidation rules
  - [ ] Edge middleware (auth, geo-routing, A/B, rate limiting)
  - [ ] Cache-Control headers for all asset types
  - [ ] Cache invalidation webhook integration
  - [ ] Data-at-edge strategy (KV store selection, consistency model)
  - [ ] Performance targets (TTFB by region, cache hit ratio)
  - [ ] Cache warming automation post-deploy
  - [ ] Monitoring and alerting for edge performance

RELATED SKILLS:
  - /infrastructure-scaffold — origin infrastructure configs
  - /performance-review — full performance audit including edge
  - /nextjs-feature-scaffold — Next.js-specific edge patterns
  - /security-review — edge security (auth, rate limiting, WAF)
```

## Code Generation (Required)

Generate edge infrastructure using Write:

1. **Edge middleware**: `src/middleware.ts` — Next.js middleware for geo-routing, A/B testing, auth
2. **Edge function**: `functions/edge/handler.ts` — Cloudflare Worker or Vercel Edge Function template
3. **Cache config**: `vercel.json` or `_headers` — CDN cache rules with stale-while-revalidate
4. **Cache invalidation**: `scripts/purge-cache.sh` — CDN cache purge script
