# performance-review: Cure optimization playbook

> Read this at Step 5 when choosing fixes. It lists stack-specific levers and gotchas Cure has hit, not generic advice. Each item names the metric it moves.

## Web (Next.js App Router)

- **LCP**: the LCP image gets `next/image` with `priority` (or `fetchPriority="high"`) and explicit `sizes`; never lazy-load it. Hero images as AVIF/WebP, ≤200 KB.
- **LCP/TTFB**: static or cached rendering by default; in Next 16 opt dynamic routes into caching with Cache Components (`'use cache'`, `cacheLife`, `cacheTag`) rather than making whole pages dynamic. A single `cookies()`/`headers()` read in a shared layout makes every child route dynamic — move it down the tree or behind Suspense.
- **INP**: long tasks >50 ms on input; break up with `startTransition`, `scheduler.yield()` where supported, and moving work off the main thread. Third-party tags (chat widgets, tag managers) are the usual culprit — load with `next/script` `strategy="lazyOnload"` or behind interaction.
- **CLS**: reserve space for images, embeds, ads, and cookie banners; `next/font` to avoid font-swap shift.
- **Bundle**: barrel files (`index.ts` re-exporting a library) defeat tree-shaking — use `optimizePackageImports` or direct imports; `lodash` → per-function imports or native; date libraries → `Intl`/`date-fns` per-function.
- **Caching headers**: hashed static assets `max-age=31536000, immutable`; public API responses `s-maxage` + `stale-while-revalidate` at the CDN.

## Mobile

- **Startup (Android)**: Baseline Profiles (and Startup Profiles) cut cold start materially — generate with Macrobenchmark; defer SDK init (analytics, crash, ads) until after first frame via App Startup lazy initializers; no disk or network on the main thread (StrictMode in debug).
- **Startup (iOS)**: fewer dynamic frameworks (static linking / mergeable libraries), no work in `+load` or static initializers, defer SDK init until after first frame; measure with Instruments App Launch.
- **Scrolling**: Compose — stable keys in `LazyColumn`, avoid unstable lambdas/collections causing recomposition (check with Layout Inspector recomposition counts). SwiftUI — stable `id`s, avoid heavy work in `body`, prefer `List`/`LazyVStack` over `VStack` for long content.
- **Images**: decode at display size (Coil `size()`, `UIImage` downsampling via ImageIO); disk cache sized to the feed, not unbounded.
- **Size**: Android App Bundle + R8 full mode + resource shrinking; iOS asset catalogs with app thinning, on-demand resources for large packs.

## Backend

- **Queries**: `EXPLAIN (ANALYZE, BUFFERS)` anything >50 ms at p95; index WHERE + ORDER BY together; keyset pagination instead of OFFSET beyond page ~10.
- **Connections**: serverless + Postgres needs a pooler (PgBouncer transaction mode, or the provider's pooled endpoint); per-instance pools of 1–5, not 20.
- **Cold starts**: min instances ≥1 for auth, payments, and webhooks; lazy-import heavy libraries; keep the deploy package small; Cloud Run for sustained traffic over per-invocation functions.
- **Caching**: cache computed results, not raw rows; event-driven invalidation where the write path is known; watch hit rate (<70% means the key or TTL is wrong).

## Firestore

- Reads are billed per document: cap list queries with `.limit()`, paginate with cursors, denormalize the fields a list screen needs into the list document.
- Sustained writes to a single document are limited to about 1 per second — use distributed counters or aggregation queries (`count()`, `sum()`, `average()`) instead of hot counter documents.
- Offline cache: web `persistentLocalCache`, Android `PersistentCacheSettings` (the older `enableIndexedDbPersistence` / `isPersistenceEnabled` APIs are deprecated); see the `offline-first` skill.
- Bulk server-side writes: `BulkWriter`, not loops of 500-op batches.
- Remove unused composite indexes; each one costs write latency and storage.
