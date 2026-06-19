# performance-review: detailed reference

> Reference material for the `performance-review` skill, split out for progressive disclosure. Loaded on demand from SKILL.md.

## Contents
- Step 5: Optimization Strategies

## Step 5: Optimization Strategies

### Web Optimization

```
Code splitting:
  - Route-based splitting with next/dynamic or React.lazy
  - Split vendor chunks > 50 KB into separate bundles
  - Defer below-fold component loading with Intersection Observer
  - Use barrel file elimination (avoid re-exporting entire modules)

Image optimization:
  - Serve WebP/AVIF with <picture> fallback
  - Use next/image with width/height (prevents CLS)
  - Implement responsive srcset (mobile: 640w, tablet: 1024w, desktop: 1920w)
  - Lazy load below-fold images (loading="lazy")
  - Use blur placeholder for hero images

Caching:
  - Static assets: Cache-Control max-age=31536000, immutable
  - API responses: stale-while-revalidate pattern
  - Service worker: cache-first for static, network-first for API
  - ISR (Incremental Static Regeneration): revalidate=60 for semi-static pages

Rendering:
  - SSG for marketing/content pages (build-time generation)
  - SSR for personalized/dynamic pages
  - Streaming SSR with React Suspense for progressive loading
  - Edge rendering for geo-sensitive content (Vercel Edge, Cloudflare Workers)

CDN:
  - All static assets served from CDN (Vercel, CloudFront, Cloudflare)
  - API responses cached at edge for public data (Cache-Control: s-maxage=60)
  - Purge strategy: deploy-time invalidation for static, TTL for dynamic
```

### Mobile Optimization (Android & iOS)

```
Lazy initialization:
  - Defer non-critical SDK init to after first frame
  - Use lazy properties (Kotlin: by lazy {}, Swift: lazy var)
  - Initialize analytics/crash reporting after UI is interactive
  - Background-init heavy singletons (database, image cache)

Image caching:
  - Android: Coil with disk cache (250 MB limit), memory cache (25% of heap)
  - iOS: Kingfisher with disk cache (300 MB), memory cache (100 MB)
  - Downscale images to display size before decoding
  - Prefetch next-screen images during idle time

List performance:
  - RecyclerView with DiffUtil (Android) / LazyColumn with keys (Compose)
  - UICollectionView with DiffableDataSource (iOS)
  - Pagination: 20 items per page, prefetch at 80% scroll position
  - Avoid nested scrollable containers

Threading:
  - Android: Dispatchers.IO for network/disk, Dispatchers.Default for computation
  - iOS: async/await with TaskGroup, never block MainActor
  - Image decoding on background thread (always)
  - JSON parsing off main thread for payloads > 1 KB
```

### Backend Optimization

```
Query optimization:
  - Add indexes for all WHERE/ORDER BY fields
  - Use EXPLAIN ANALYZE for queries > 50ms
  - Avoid N+1 queries: use JOINs or batch fetching
  - Paginate all list endpoints (max 100 items per page)

Connection pooling:
  - PostgreSQL: PgBouncer with transaction mode, pool size = (CPU cores * 2) + disk spindles
  - MySQL: ProxySQL for connection multiplexing
  - Close idle connections after 300s
  - Monitor pool utilization — alert at 80%

Caching layers:
  - L1: In-memory (application-level, <1ms, 100 MB limit)
  - L2: Redis/Memcached (<5ms, session data, computed results)
  - L3: CDN edge cache (<50ms, public API responses)
  - Cache invalidation: event-driven (pub/sub) over TTL when possible
  - Redis: set maxmemory-policy allkeys-lru, monitor hit rate

Denormalization:
  - Precompute aggregations for dashboard queries
  - Store derived fields (e.g., order_total) to avoid joins
  - Use materialized views for complex reporting queries
  - Rebuild strategy: async job, not in request path

Serverless cold start mitigation:
  - Minimum instances: 1-3 for critical functions (auth, payments, webhooks)
  - Keep dependencies minimal (< 50 MB deployment package)
  - Use lazy imports for heavy libraries
  - Prefer Cloud Run over Cloud Functions for sustained traffic
```

### Firebase-Specific Optimization

```
Firestore read optimization:
  - Design documents for read patterns (denormalize, don't normalize)
  - Keep documents < 10 KB for fast reads
  - Use subcollections for 1:N relationships (not arrays)
  - Limit query results: .limit(20) on all list queries
  - Use select() to fetch only needed fields

Composite indexes:
  - Create for all multi-field queries (equality + range + orderBy)
  - Monitor index usage in Firebase Console
  - Remove unused indexes (they cost write performance)

Offline persistence:
  - Enable on mobile: FirebaseFirestore.setSettings { isPersistenceEnabled = true }
  - Set cache size: 100 MB minimum for offline-first apps
  - Use source: .cache for non-critical reads
  - Implement optimistic UI updates with rollback on sync failure

Batch operations:
  - Use writeBatch() for multi-document writes (max 500 per batch)
  - Batch reads with getAll() instead of sequential gets
  - Transaction retry: max 5 attempts with exponential backoff
  - Use Firestore BulkWriter for server-side migrations
```
