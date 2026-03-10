---
name: database-architect
description: "Design database schemas, plan migrations, optimize queries, define indexing strategies for Firestore, PostgreSQL, and SQLite"
argument-hint: "[database-or-feature]"
---

# Database Architect

Designs production-grade database schemas, migration plans, indexing strategies, and query optimizations across Firestore, PostgreSQL, SQLite/Room, and Redis. Every recommendation considers data volume, access patterns, consistency requirements, and Cure Consulting Group's Firebase-first but multi-database approach.

## Core Principle: Right Database for the Right Job

```
Firestore       →  Real-time sync, mobile-first, denormalized documents
PostgreSQL      →  Relational data, complex queries, ACID transactions
SQLite/Room     →  Local mobile storage, offline-first, structured cache
Redis           →  Caching layer, session storage, rate limiting, pub/sub
```

**Hard rules:**
- Default to Firestore unless the use case explicitly requires relational queries or local-only storage
- Never store secrets, API keys, or PII in unencrypted local databases
- All schemas must include `createdAt` and `updatedAt` timestamps
- All migrations must be reversible or have a documented rollback plan
- Database access goes through repository interfaces — no direct SDK usage in domain or presentation layers

## Step 1: Classify the Database Need

| Request | Primary Output | Action |
|---------|---------------|--------|
| Schema design | Collection/table structure + relationships | Design schema |
| Migration planning | Versioned migration scripts + rollback plan | Plan migration |
| Query optimization | EXPLAIN analysis + rewrite recommendations | Optimize queries |
| Indexing strategy | Index definitions + maintenance plan | Define indexes |
| Database selection | Comparison matrix + recommendation | Evaluate databases |
| Full data layer | All of the above | Generate everything |

## Step 2: Gather Context

Before generating, confirm:
1. **Feature name** — e.g., "Order Management", "User Profiles"
2. **Current database** — existing database(s) in use, or greenfield?
3. **Data volume** — hundreds / thousands / millions / billions of records?
4. **Access patterns** — read-heavy, write-heavy, or balanced? Real-time needs?
5. **Consistency requirements** — eventual consistency acceptable, or strong consistency required?
6. **Hosting environment** — Firebase/GCP, AWS, self-hosted, mobile-local?
7. **Existing schema** — any current tables/collections to integrate with?
8. **Compliance needs** — GDPR, HIPAA, data residency requirements?

## Step 3: Database Selection Guide

### Firestore
- **Best for:** real-time sync, mobile-first apps, denormalized data, serverless backends
- **Sweet spot:** <10M documents per collection, fan-out read patterns
- **Strengths:** automatic scaling, offline persistence, real-time listeners, zero server management
- **Limitations:** no cross-document joins, limited aggregation, 1MB document size limit, 500 writes/sec per document
- **Choose when:** the app needs real-time updates, mobile offline support, or rapid prototyping

### PostgreSQL
- **Best for:** relational data, complex queries, ACID transactions, reporting/analytics
- **Sweet spot:** structured data with relationships, complex WHERE/JOIN/GROUP BY queries
- **Strengths:** full SQL, ACID compliance, rich indexing (B-tree, GIN, GiST), JSONB for semi-structured data, mature ecosystem
- **Limitations:** requires server management (unless using managed services), manual scaling, no built-in real-time sync
- **Choose when:** data is inherently relational, complex queries are needed, or strong consistency is non-negotiable

### SQLite / Room
- **Best for:** local mobile storage, offline-first apps, structured local cache
- **Sweet spot:** local data persistence on Android/iOS, sync queues, app configuration
- **Strengths:** zero network latency, works offline, full SQL locally, Room provides compile-time query verification
- **Limitations:** single-writer, no built-in sync, local to device only
- **Choose when:** the app needs structured local storage, offline-first behavior, or a sync outbox pattern

### Redis
- **Best for:** caching layer, session storage, rate limiting, pub/sub messaging
- **Sweet spot:** high-frequency reads, TTL-based expiration, real-time counters
- **Strengths:** sub-millisecond latency, built-in data structures (sets, sorted sets, streams), pub/sub, TTL
- **Limitations:** in-memory (limited by RAM), not a primary data store, data loss risk without persistence config
- **Choose when:** you need a caching layer, rate limiter, session store, or real-time leaderboard

## Step 4: Schema Design Patterns

### Firestore Document Modeling
- **Document modeling:** one document per logical entity; embed related data when read together
- **Subcollection strategy:** use subcollections when child entities exceed 10k items, need independent queries, or have different access control
- **Denormalization rules:** duplicate data that is read frequently but written rarely; accept write complexity for read performance
- **Reference patterns:** store document path strings for cross-collection references; resolve at read time
- **Fan-out writes:** when denormalized data changes, use Cloud Functions or batched writes to update all copies
- **Document ID conventions:** Auth UID for user docs, auto-ID for most entities, slug for human-readable lookups, date-prefixed for time-series

### PostgreSQL Schema Design
- **Normalization:** default to 3NF; denormalize only with measured performance justification
- **Junction tables:** for all many-to-many relationships; include `created_at` and metadata columns
- **JSON columns:** use `JSONB` for truly dynamic/schemaless attributes; never for data that needs indexing or joins
- **ENUMs:** use PostgreSQL `CREATE TYPE ... AS ENUM` for fixed-value columns; prefer check constraints for values that may change
- **Partitioning:** partition tables >100M rows by range (date) or list (tenant); use declarative partitioning
- **Naming conventions:** `snake_case` for all identifiers, plural table names, `_id` suffix for foreign keys

### SQLite / Room
- **Entity relationships:** use `@Relation` and `@Embedded` annotations; define `ForeignKey` constraints explicitly
- **Type converters:** create `@TypeConverter` for dates, enums, and complex types; register globally in the database class
- **Migration path:** define `Migration(fromVersion, toVersion)` for every schema change; never use `fallbackToDestructiveMigration()` in production
- **Embedded vs referenced:** embed value objects (address, coordinates); reference entities with foreign keys

## Step 5: Migration Planning

### Versioned Migrations
- Every schema change gets a numbered migration file (e.g., `V001__create_users_table.sql`)
- Migrations are immutable once deployed — never edit a released migration
- Use a migration tool: Flyway or Liquibase for PostgreSQL, Room `Migration` objects for SQLite, Firestore migration scripts as Cloud Functions

### Rollback Strategy
- Every migration must have a corresponding rollback script or a documented manual reversal procedure
- For additive changes (new column, new table): rollback = drop the addition
- For destructive changes (drop column, rename): copy data first, keep old column during transition period, drop in a later migration
- Test rollback scripts in staging before deploying the forward migration to production

### Zero-Downtime Migration Patterns
1. **Expand-Contract pattern:** add new column → backfill → update app to write both → update app to read new → drop old column
2. **Dual-write period:** write to both old and new schemas during transition
3. **Shadow tables:** create new table structure, sync data, swap references atomically
4. **Feature flags:** gate new schema reads behind feature flags; roll back by disabling the flag

### Data Backfill Scripts
- Write idempotent backfill scripts that can be re-run safely
- Process in batches (1000–5000 rows per batch) to avoid locking and memory issues
- Log progress and support resumption from the last processed ID
- Run backfills during low-traffic windows; monitor database load during execution

### Testing Migrations
- Test every migration against a snapshot of production data (anonymized if necessary)
- Verify both forward migration and rollback
- Measure migration execution time on production-scale data
- Include migration tests in CI pipeline

## Step 6: Indexing Strategy

### General Principles
- Index columns that appear in `WHERE`, `JOIN`, `ORDER BY`, and `GROUP BY` clauses
- Avoid over-indexing — each index slows writes and consumes storage
- Review and drop unused indexes quarterly

### Composite Indexes
- Column order matters: place equality conditions first, then range conditions, then sort columns
- A composite index on `(a, b, c)` supports queries on `(a)`, `(a, b)`, and `(a, b, c)` but not `(b, c)` alone

### Covering Indexes
- Include all columns needed by a query in the index to enable index-only scans
- PostgreSQL: use `INCLUDE` clause for non-key columns in the index

### Firestore Indexes
- **Automatic indexes:** Firestore auto-indexes every field; no action needed for single-field queries
- **Composite indexes:** required for queries with multiple `where` clauses or `where` + `orderBy` on different fields; define in `firestore.indexes.json`
- **Exempt fields:** exempt large string/array fields from automatic indexing to save costs

### PostgreSQL EXPLAIN ANALYZE
- Run `EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)` on every slow query
- Look for: sequential scans on large tables, nested loop joins on large sets, high buffer reads
- Target: all frequent queries should use index scans or bitmap index scans
- Monitor with `pg_stat_user_indexes` for unused indexes and `pg_stat_statements` for slow queries

### Index Maintenance
- Schedule `REINDEX` or `pg_repack` for heavily updated tables
- Monitor index bloat with `pgstattuple` extension
- For Firestore, review composite index usage in the Firebase console and remove unused indexes

## Step 7: Query Optimization

### N+1 Detection
- Identify loops that issue one query per iteration — replace with batch reads or joins
- Firestore: use `whereIn` (max 30 values) or `getAll()` for batch document fetches
- PostgreSQL: use `JOIN` or `WHERE IN` subqueries; use `EXISTS` over `IN` for large subquery results
- Room: use `@Transaction` with `@Relation` to load parent + children in one call

### Batch Reads
- Firestore: batch reads with `getAll()` (max 500 documents); for larger sets, paginate
- PostgreSQL: use `ANY(ARRAY[...])` for parameterized batch lookups; limit batch size to 1000

### Pagination Patterns
- **Cursor-based (preferred):** use `startAfter(lastDocument)` in Firestore, `WHERE id > :lastId ORDER BY id LIMIT :pageSize` in SQL; stable under concurrent writes
- **Offset-based (use sparingly):** `OFFSET` + `LIMIT` in SQL; degrades on large offsets; acceptable for admin/backoffice UIs with <100k rows

### Denormalization Trade-offs
- Denormalize when read frequency is 10x+ write frequency for the same data
- Track all locations of denormalized data in documentation
- Use Cloud Functions (Firestore) or database triggers (PostgreSQL) to keep copies in sync
- Monitor for data drift — schedule periodic consistency checks

### Read Replicas
- Route read-heavy analytics and reporting queries to read replicas
- Accept replication lag (typically <1s for PostgreSQL streaming replication)
- Never route writes to read replicas
- Use connection pooling (PgBouncer) to manage replica connections efficiently

## Step 8: Backup & Disaster Recovery

### Automated Backups
- **Firestore:** enable daily automated exports to Cloud Storage; use `gcloud firestore export`
- **PostgreSQL:** configure continuous WAL archiving + daily `pg_dump` base backups; retain 30 days minimum
- **SQLite/Room:** back up database file on app update and before migrations; sync to cloud storage for critical data
- **Redis:** enable RDB snapshots + AOF persistence; schedule `BGSAVE` during low-traffic periods

### Point-in-Time Recovery
- **PostgreSQL:** configure WAL archiving for PITR; test recovery to a specific timestamp quarterly
- **Firestore:** use timestamped exports; restore by importing a specific export
- Document Recovery Time Objective (RTO) and Recovery Point Objective (RPO) for each database

### Export Strategies
- Maintain automated export pipelines to BigQuery or data warehouse for analytics
- Export anonymized datasets for development and testing environments
- Version export scripts alongside migration scripts

### Cross-Region Replication
- **Firestore:** use multi-region locations (`nam5`, `eur3`) for automatic cross-region replication
- **PostgreSQL:** configure streaming replication to a secondary region; automate failover with Patroni or Cloud SQL HA
- **Redis:** use Redis Sentinel or Redis Cluster for cross-region replication and automatic failover
- Test failover procedures quarterly; document runbooks for manual failover

## Step 9: Output Templates

For every database architecture recommendation, deliver:

1. **Schema diagram** — ASCII or Mermaid ER diagram showing entities, relationships, and cardinality
2. **Migration script** — versioned, idempotent SQL/script with rollback counterpart
3. **Index recommendations** — table of recommended indexes with justification and expected query improvement
4. **Performance report** — baseline metrics, identified bottlenecks, optimization results with before/after EXPLAIN output

### Schema Diagram Format
```
[Collection/Table] ──── 1:N ────→ [Collection/Table]
       │
       └──── 1:1 ────→ [Collection/Table]
```

### Migration Script Template
```sql
-- Migration: V{NNN}__{description}.sql
-- Author: {name}
-- Date: {date}
-- Description: {what and why}

BEGIN;

-- Forward migration
{SQL statements}

-- Verification
{SELECT count or validation query}

COMMIT;

-- Rollback: V{NNN}__rollback__{description}.sql
```

### Index Recommendation Table
```
| Table/Collection | Index Name | Columns | Type | Justification |
|-----------------|------------|---------|------|---------------|
| | | | | |
```

### Performance Report Template
```
## Query: {description}
- Before: {execution time, scan type}
- After: {execution time, scan type}
- Improvement: {percentage}
- Changes applied: {index added, query rewritten, etc.}
```

## Tech Stack Defaults

```yaml
firestore: Firebase BOM 33.x, offline persistence enabled
postgresql: PostgreSQL 16, managed via Cloud SQL or Supabase
sqlite_android: Room 2.6.x, KSP annotation processing
redis: Redis 7.x, managed via Memorystore or Upstash
migration_tools:
  postgresql: Flyway 10.x or Liquibase 4.x
  sqlite: Room auto-migration + manual Migration objects
  firestore: Custom Cloud Functions for data migrations
monitoring:
  postgresql: pg_stat_statements, pgBadger, Cloud SQL Insights
  firestore: Firebase Console, Cloud Monitoring
  redis: Redis INFO, Slowlog
```
