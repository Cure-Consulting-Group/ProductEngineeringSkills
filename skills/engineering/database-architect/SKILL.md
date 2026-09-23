---
name: database-architect
description: "Designs schemas, indexes, and query plans for Firestore, PostgreSQL, SQLite/Room. Use when choosing a database, modeling data, adding indexes, or fixing slow queries."
when_to_use: "NOT for moving or backfilling existing data (use data-migration), Firestore rules and Functions (use firebase-architect), or local sync and conflict handling (use offline-first)."
argument-hint: "[database-or-feature]"
metadata:
  verified: 2026-09-23
---

# Database Architect

**Outcome:** a data design the team can implement — engine choice with the reason, schema (ER diagram or collection tree), access-pattern → index table, and versioned migration files with a down path. Done when every listed access pattern maps to an index or a justified scan, and every schema change is reversible or has a documented manual reversal. For query tuning, done = before/after `EXPLAIN` (or Firestore query explain) showing the change.

## Pre-Processing (Auto-Context)

Context (pre-filled in Claude Code; in other runtimes run these commands first):

- Schema files: !`find . -maxdepth 4 -path "*/node_modules" -prune -o \( -name "*.sql" -o -name "schema.prisma" -o -name "firestore.indexes.json" -o -name "*Entity.kt" \) -print 2>/dev/null | head -8 || echo "(none)"`
- Stack manifest: !`head -25 package.json 2>/dev/null || head -25 build.gradle.kts 2>/dev/null || echo "(none detected)"`

## Step 1: Classify

| Request | Output |
|---|---|
| Engine selection | Decision with the deciding access patterns and the rejected option's failure mode |
| Schema design | ER diagram / collection tree + field types + access-pattern table |
| Indexing | Index table: query → index → justification |
| Slow query | Plan analysis + rewrite or index, before/after numbers |
| Schema migration | Versioned up/down files (data movement → `data-migration`) |
| Review of an existing design | Findings with severity; no files |

## Step 2: Gather Context

Ask only what the repo doesn't show: top 5 access patterns (who reads what, how often, sorted how), volume now and in 12 months, write hot spots, consistency needs (money, inventory → strong), hosting constraints, and residency/HIPAA needs.

## Step 3: Engine Choice (Cure defaults)

- **Firestore** is the default for Cure mobile/web apps: real-time listeners, offline cache, no servers. Choose **PostgreSQL** (Cloud SQL, or Supabase when the client already uses it) when you need joins across many entities, ad-hoc reporting, multi-row transactions over large sets, or strict relational integrity — typically billing ledgers and back-office analytics. Many Cure products run both: Firestore for app state, PostgreSQL/BigQuery for reporting via export.
- **Room / SQLite / SwiftData** only for on-device storage; sync design belongs to `offline-first`.
- **Redis (Memorystore)** only as cache, rate-limit store, or ephemeral queue — never the system of record.

Firestore limits that decide designs (verified 2026-09-23, firebase.google.com/docs/firestore/quotas): 1 MiB per document; ~1 sustained write/sec per document (shard counters); new collections ramp from 500 ops/sec, +50% every 5 min (500/50/5); `in`/`array-contains-any` take up to 30 values; server aggregations are `count()`, `sum()`, `average()` only — anything else is a precomputed field; up to 100 databases per project (named databases for tenant or residency isolation).

## Step 4: Schema Rules

**Firestore**
- Model from queries backwards: one query should need one collection read. Denormalize read-mostly data; list every copy of a denormalized field in the design and name the Function that keeps it in sync.
- Subcollection when children are unbounded (>~1k), need independent queries, or have different access rules; array only for small bounded sets.
- IDs: Auth UID for user docs, auto-ID for entities, slug for known-key lookups. Avoid monotonically increasing IDs or timestamp-prefixed IDs on high-write collections — they create hotspots; put the time in a field and index it.
- Every document has `createdAt`/`updatedAt` server timestamps and a `schemaVersion` integer once the collection has migrated once.

**PostgreSQL**
- 3NF by default; denormalize only with a measured reason. `snake_case`, plural tables, `_id` FKs, `timestamptz` everywhere, `bigint` or UUIDv7 keys (time-ordered, index-friendly).
- `JSONB` for truly open attributes only; if you filter on a key, promote it to a column or add a GIN/expression index.
- Prefer `CHECK` constraints or lookup tables over `ENUM` types for values that will change (enum value removal is painful).
- Partition by range (time) or list (tenant) above ~100M rows or when you need cheap retention drops.

**Room (Android)** — explicit `Migration(from, to)` for every version bump, `exportSchema = true` with schemas committed so `MigrationTestHelper` can test them; never `fallbackToDestructiveMigration()` in release builds (it wipes user data).

## Step 5: Indexes

- Composite order: equality columns, then range, then sort. `(a, b, c)` serves `a`, `a,b`, `a,b,c` — not `b,c`.
- PostgreSQL: covering indexes with `INCLUDE`; partial indexes for hot subsets (`WHERE status = 'active'`); `CREATE INDEX CONCURRENTLY` on live tables (not inside a transaction). Find unused indexes with `pg_stat_user_indexes`, slow queries with `pg_stat_statements`.
- Firestore: single-field indexes are automatic; composite indexes live in `firestore.indexes.json` and must be committed, not clicked in the console. Add single-field exemptions for large strings, arrays, and maps you never query (saves write cost and avoids the index-entry limit); exempt monotonically increasing fields on high-write collections from ascending indexes to avoid hotspots.

## Step 6: Query Fixes

- **N+1:** Firestore `getAll(...refs)` in chunks or an `in` query (≤30); SQL `JOIN` or `= ANY(:ids)`; Room `@Transaction` + `@Relation`.
- **Pagination:** cursor/keyset (`startAfter(lastDoc)`; `WHERE (created_at, id) < (:lastCreatedAt, :lastId) ORDER BY created_at DESC, id DESC LIMIT 20`). `OFFSET` only for admin views under ~100k rows.
- **PostgreSQL diagnosis:** `EXPLAIN (ANALYZE, BUFFERS)`; look for seq scans on large tables, row-estimate misses of 10×+ (run `ANALYZE`, consider extended statistics), and sorts spilling to disk. Pool connections (PgBouncer or the Cloud SQL connector) — serverless functions exhaust connections fast.
- **Firestore diagnosis:** Query Explain (`explain({ analyze: true })`) shows index use and read counts; a query reading far more documents than it returns needs a better index or a restructured collection.

## Step 7: Schema Migrations

- Versioned, immutable files: Flyway `V{NNN}__{desc}.sql` with a matching `U{NNN}__{desc}.sql` undo file. Undo migrations are a Flyway paid-edition feature; on Community edition write the reverse as a new forward `V` migration and keep it tested. Liquibase rollback blocks are the alternative.
- Destructive changes use expand-contract (add → dual-write → backfill → switch reads → drop later). Column drops ship at least one release after the code stops reading them.
- `ALTER TABLE` that rewrites the table or takes `ACCESS EXCLUSIVE` on a large table needs a plan: `lock_timeout`, `NOT VALID` constraints validated separately, concurrent index builds.
- Anything that moves or backfills existing data → `data-migration`. Backups, PITR, and cross-region failover → `disaster-recovery`.

Template:

```sql
-- V042__add_orders_status_idx.sql  (undo: U042__add_orders_status_idx.sql)
SET lock_timeout = '5s';
CREATE INDEX CONCURRENTLY IF NOT EXISTS orders_status_created_idx
  ON orders (status, created_at DESC);
```

`CONCURRENTLY` cannot run inside a transaction: keep it alone in its own migration and, in Flyway, mark that script non-transactional (script config `executeInTransaction=false`) if your version doesn't detect it.

## Code/Artifact Generation

Applies only when Step 1 calls for building a schema, index set, or migration (not reviews, selection questions, or diagnosis-only requests). Read existing schema files first and match their tool and naming.

Produce only what the stack uses: SQL migrations (up + undo/reverse), `firestore.indexes.json` entries, Room `@Entity` + `Migration`, SwiftData `@Model`, or `schema.prisma` if Prisma is present. Deliver the requested schema; don't refactor repositories or add unrequested layers.

Match length to the need; no filler sections or restated summaries.

## Current Defaults (verified 2026-09-23)

| Component | Default | Source |
|---|---|---|
| Firebase Android | BoM 34.x (34.19.0 on 2026-09-09); no `-ktx` artifacts since BoM 34.0.0 | firebase.google.com/support/release-notes/android |
| PostgreSQL | 18 for new projects (17 acceptable where the host lags); 14 reaches EOL 2026-11-12 | postgresql.org/support/versioning |
| Room | 2.8.x with KSP (requires Kotlin 2.x + KSP2) | developer.android.com/jetpack/androidx/releases/room |
| Flyway | Current major 13.x; undo requires a paid edition | documentation.red-gate.com (Flyway release notes) |
| Redis | Managed Memorystore; confirm engine (Redis vs Valkey) and version with the client's GCP project before use | — |

## Related skills

- `data-migration` — backfills, ETL, cutover, rollback of existing data.
- `firebase-architect` — Firestore security rules, Functions, App Check.
- `offline-first` — Room/SwiftData sync and conflict resolution.
- `disaster-recovery` — backups, PITR, failover.
- `migration-validator` agent — review of a specific migration file.
