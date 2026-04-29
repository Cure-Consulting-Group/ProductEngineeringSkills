---
name: data-migration
version: "1.0.0"
description: "Plan and execute data migrations — ETL pipelines, zero-downtime cutover, validation, rollback strategies, and legacy system integration"
when_to_use: "Use when planning ETL pipelines, zero-downtime data migrations, or legacy system cutover. NOT for schema design (use database-architect)."
argument-hint: "[source-to-target]"
---

# Data Migration

## Pre-Processing (Auto-Context)

Before starting, gather project context silently:
- Read `PORTFOLIO.md` if it exists in the project root or parent directories for product/team context
- Run: `cat package.json 2>/dev/null || cat build.gradle.kts 2>/dev/null || cat Podfile 2>/dev/null` to detect stack
- Run: `git log --oneline -5 2>/dev/null` for recent changes
- Run: `ls src/ app/ lib/ functions/ 2>/dev/null` to understand project structure
- Use this context to tailor all output to the actual project

Plans and executes production-grade data migrations across databases, cloud platforms, and legacy systems. Covers ETL pipeline design, zero-downtime cutover patterns, validation frameworks, rollback strategies, and Firestore-specific migration tooling. Every migration is reversible, validated, and monitored.

**Hard rules:**
- Every migration has a rollback plan — tested before the forward migration runs
- Data validation runs before, during, and after migration — not just after
- Zero-downtime is the default target; scheduled downtime requires executive approval
- Idempotent operations only — every script must be safe to re-run
- Production data is never used in development without anonymization
- Migration scripts live in version control alongside application code

## Step 1: Classify the Migration Type

| Type | Characteristics | Typical Duration | Risk Level |
|------|----------------|-----------------|------------|
| Schema Evolution | Same database, structural changes (add/rename/drop columns) | Minutes–hours | Low–Medium |
| Database-to-Database | Same engine, different instance (e.g., dev → prod restore) | Hours | Medium |
| Platform Switch | Different engines (MySQL → PostgreSQL, MongoDB → Firestore) | Days–weeks | High |
| Cloud Migration | On-premise → cloud or cloud → cloud | Weeks–months | High |
| Legacy System Integration | Mainframe, CSV exports, SOAP APIs → modern stack | Weeks–months | Very High |
| Firestore Restructuring | Collection/document model changes within Firestore | Hours–days | Medium–High |

## Step 2: Gather Context

Before planning, confirm:

1. **Source system** — database engine, version, hosting, schema, data volume (rows/documents, GB/TB)?
2. **Target system** — database engine, version, hosting, desired schema?
3. **Data volume** — total records, total size, largest table/collection, growth rate?
4. **Downtime tolerance** — zero-downtime required, or maintenance window available (duration)?
5. **Compliance constraints** — does data include PII, PHI, PCI data? Cross-border transfer restrictions?
6. **Dependencies** — what applications read/write this data? Can they be paused or dual-configured?
7. **Timeline** — hard deadline (e.g., vendor contract end), or flexible?
8. **Current backup state** — last backup timestamp, backup verification status, restore tested?
9. **Rollback requirements** — how quickly must we be able to revert? What data loss is acceptable?

## Step 3: Migration Strategy Selection

### Big Bang Migration

```
When to use:
  - Small datasets (<1M records)
  - Short maintenance window available (< 4 hours)
  - Simple schema mapping (1:1 field correspondence)
  - Non-critical system or acceptable downtime

Process:
  1. Announce maintenance window
  2. Stop all writes to source
  3. Run full export from source
  4. Transform data
  5. Load into target
  6. Validate (row counts, checksums, spot checks)
  7. Switch application to target
  8. Monitor for 1 hour
  9. Decommission source after 7-day hold

Rollback: switch application back to source (source is read-only during hold period)
Risk: all-or-nothing — failure means full rollback
```

### Trickle Migration (Change Data Capture)

```
When to use:
  - Large datasets (>1M records)
  - Zero-downtime required
  - Source system supports CDC (PostgreSQL WAL, MySQL binlog, Firestore listeners)

Process:
  1. Set up CDC pipeline (Debezium, Firestore onSnapshot, PostgreSQL logical replication)
  2. Run initial bulk load of historical data
  3. CDC catches up on changes made during bulk load
  4. Validate source-target consistency
  5. Switch reads to target (behind feature flag)
  6. Switch writes to target
  7. Decommission CDC pipeline after 7-day monitoring period

Rollback: reverse CDC direction or switch reads/writes back to source
Risk: CDC lag can cause temporary inconsistency; monitor lag continuously
```

### Blue-Green Migration

```
When to use:
  - Critical systems where cutover must be instant
  - Both source and target can run simultaneously
  - Application supports database connection switching

Process:
  1. Stand up target (green) alongside source (blue)
  2. Sync data from blue → green (initial + ongoing CDC)
  3. Run validation suite against green
  4. Switch traffic to green (DNS, connection string, feature flag)
  5. Monitor green for anomalies
  6. Keep blue running for 7 days as fallback
  7. Decommission blue

Rollback: switch traffic back to blue (instant)
Risk: cost of running two systems simultaneously; data sync complexity
```

### Strangler Fig Migration

```
When to use:
  - Legacy system replacement over months
  - Gradual feature-by-feature migration
  - Cannot afford big-bang risk

Process:
  1. Identify migration order (lowest risk features first)
  2. For each feature:
     a. Build new data model in target
     b. Implement dual-read (read from target, fallback to source)
     c. Implement dual-write (write to both)
     d. Migrate historical data for this feature
     e. Validate feature data in target
     f. Switch to target-only reads
     g. Stop writing to source for this feature
  3. Repeat until all features migrated
  4. Decommission source

Rollback: per-feature rollback by reverting to dual-read/source-only
Risk: long duration increases complexity; dual-write bugs can cause divergence
```

## Step 4: ETL Pipeline Design

### Extract Patterns

```
Firestore:
  - Full export: gcloud firestore export gs://bucket/path
  - Streaming: onSnapshot listeners for real-time CDC
  - Batch read: getAll() with pagination (500 docs per batch)
  - BigQuery export: scheduled export via Data Transfer Service

PostgreSQL:
  - Full dump: pg_dump --format=custom --compress=9
  - Logical replication: CREATE PUBLICATION / CREATE SUBSCRIPTION
  - COPY command: COPY table TO STDOUT WITH CSV HEADER
  - CDC: Debezium connector reading WAL

Legacy systems:
  - CSV/Excel: parse with streaming reader (not full-file load into memory)
  - SOAP API: paginated requests with exponential backoff
  - FTP drops: scheduled pickup with file validation (checksum, row count header)
  - Direct database: read-only replica connection with query timeout
```

### Transform Rules

```
Mapping document template:
┌─────────────────────┬──────────────────────┬──────────────────────────┐
│ Source Field         │ Target Field         │ Transformation           │
├─────────────────────┼──────────────────────┼──────────────────────────┤
│ user.first_name     │ users.displayName    │ CONCAT(first, ' ', last) │
│ user.created_date   │ users.createdAt      │ PARSE_DATE('MM/dd/yyyy') │
│ order.total_cents   │ orders.totalAmount   │ DIVIDE by 100, DECIMAL   │
│ user.status = 'A'   │ users.isActive       │ MAP('A'→true, else false)│
│ (no equivalent)     │ users.migratedAt     │ CURRENT_TIMESTAMP        │
│ user.ssn            │ (do not migrate)     │ SKIP — not needed        │
└─────────────────────┴──────────────────────┴──────────────────────────┘

Transformation rules:
  - NULL handling: define explicit default for every nullable source field
  - Type coercion: document every type change (string→number, date format changes)
  - Encoding: normalize to UTF-8; detect and convert from source encoding
  - Deduplication: define merge strategy for duplicate source records
  - Derived fields: document calculation formulas for computed fields
  - Anonymization: PII fields that should not migrate to non-production targets
```

### Load Strategies

```
Batch loading:
  - Firestore: batched writes (max 500 ops per batch), with retry and exponential backoff
  - PostgreSQL: COPY command for bulk inserts (10-100x faster than INSERT)
  - Batch size: 1000–5000 records; tune based on target system capacity

Streaming loading:
  - Process source changes in near-real-time
  - Buffer writes to reduce target system load (batch micro-writes)
  - Monitor lag between source event and target write

Idempotency rules:
  - Use deterministic IDs (hash of source primary key + migration version)
  - Use UPSERT / ON CONFLICT for SQL targets
  - Use set() with merge for Firestore targets
  - Log every record processed; support resumption from last checkpoint
```

## Step 5: Data Validation Framework

### Pre-Migration Validation

```
Before starting:
  1. Source data quality audit:
     - [ ] NULL percentage per column (flag >10% unexpected NULLs)
     - [ ] Data type consistency (strings in numeric columns, invalid dates)
     - [ ] Referential integrity (orphaned foreign keys)
     - [ ] Duplicate detection (primary key uniqueness, business key uniqueness)
     - [ ] Value range validation (negative ages, future dates, impossible amounts)

  2. Schema compatibility check:
     - [ ] All source fields have a target mapping or explicit skip justification
     - [ ] Target schema can accommodate maximum source field lengths
     - [ ] Target constraints (NOT NULL, UNIQUE, CHECK) are satisfiable by source data
     - [ ] Character encoding is compatible
```

### During-Migration Validation

```
Real-time monitoring:
  - Record count: source extracted vs. target loaded (should match or have documented delta)
  - Error rate: failures per batch (alert if >0.1%)
  - Throughput: records/second (alert if drops below baseline by >50%)
  - Lag: time between source change and target write (for CDC migrations)
  - Checkpointing: last successfully processed record ID (for resumption)

Error handling:
  - Dead letter queue for failed records (do not skip silently)
  - Categorize errors: data quality, network, capacity, permission
  - Auto-retry transient errors (network, rate limit) with exponential backoff
  - Halt migration if error rate exceeds threshold (configurable, default 1%)
```

### Post-Migration Validation

```
Completeness checks:
  - [ ] Row/document count matches (source vs. target, per table/collection)
  - [ ] Checksum comparison on critical columns (SUM, HASH of concatenated values)
  - [ ] Null count comparison per column

Accuracy checks:
  - [ ] Random sample validation (1% or 1000 records, whichever is larger)
  - [ ] Business rule validation (calculated fields produce correct results)
  - [ ] Referential integrity in target (no orphaned foreign keys)
  - [ ] Date/time values preserved correctly (timezone handling)

Functional checks:
  - [ ] Application smoke tests pass against target database
  - [ ] Critical user flows work end-to-end
  - [ ] Reporting queries produce same results against target
  - [ ] Search/filter functionality returns expected results
```

## Step 6: Rollback Plan

### Point-in-Time Recovery

```
Before migration:
  1. Take a labeled backup of the target database
     - PostgreSQL: pg_dump with timestamp label
     - Firestore: gcloud firestore export with date prefix
     - Room/SQLite: copy database file before migration object runs

  2. Record the pre-migration state:
     - Row counts per table/collection
     - Schema version identifier
     - Application version deployed
     - Feature flag states

Rollback execution:
  1. Stop writes to target
  2. Restore from pre-migration backup
  3. Revert application to previous version (or toggle feature flag)
  4. Verify restored state matches pre-migration records
  5. Resume normal operations
  6. Conduct post-mortem on migration failure

Recovery Time Objective (RTO): document and test — target <30 minutes for critical systems
Recovery Point Objective (RPO): zero data loss during rollback (backup is pre-migration state)
```

### Dual-Write Rollback

```
During dual-write period:
  - Both source and target receive all writes
  - Reads default to source (target is warming up)
  - Validation runs continuously comparing source and target

Rollback trigger conditions:
  - Error rate >1% on target writes
  - Data divergence detected between source and target
  - Application latency increases >50% due to dual-write overhead
  - Target system instability (connection failures, timeouts)

Rollback steps:
  1. Disable dual-write (stop writing to target)
  2. Revert read path to source-only
  3. Target becomes stale but source is authoritative
  4. No data loss — source was always receiving all writes
```

### Feature Flag Cutover

```
Migration phases controlled by feature flags:
  FF: migration_read_from_target   (default: false)
  FF: migration_write_to_target    (default: false)
  FF: migration_dual_write         (default: false)

Rollout sequence:
  Phase 1: migration_dual_write = true          (write to both)
  Phase 2: migration_read_from_target = true     (read from target, write to both)
  Phase 3: migration_write_to_target = true      (write to target only)
  Phase 4: Remove flags, decommission source

Rollback: set all flags to false → instant revert to source-only
```

## Step 7: Zero-Downtime Patterns

### Dual-Write Architecture

```
Application Layer:
  ┌─────────────┐
  │  App Server  │
  │  / Client    │
  └──────┬───────┘
         │ write
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌────────┐
│ Source  │ │ Target │
│   DB   │ │   DB   │
└────────┘ └────────┘

Implementation:
  - Write to source first (authoritative)
  - Write to target second (async or sync depending on consistency needs)
  - If target write fails: log to retry queue, do NOT fail the user request
  - Read from source until validation confirms target consistency
  - Gradual read traffic shift: 0% → 10% → 50% → 100% target
```

### Change Data Capture Pipeline

```
┌────────┐    ┌─────────┐    ┌───────────┐    ┌────────┐
│ Source  │───▶│   CDC   │───▶│ Transform │───▶│ Target │
│   DB   │    │ (Debezium│    │  Service  │    │   DB   │
└────────┘    │  / WAL)  │    └───────────┘    └────────┘
              └─────────┘
                  │
                  ▼
           ┌────────────┐
           │ Dead Letter │
           │   Queue     │
           └────────────┘

PostgreSQL CDC setup:
  ALTER SYSTEM SET wal_level = logical;
  CREATE PUBLICATION migration_pub FOR TABLE users, orders, products;
  -- On target:
  CREATE SUBSCRIPTION migration_sub
    CONNECTION 'host=source dbname=app'
    PUBLICATION migration_pub;

Firestore CDC:
  // Cloud Function triggered on document changes
  exports.syncToTarget = functions.firestore
    .document('{collection}/{docId}')
    .onWrite(async (change, context) => {
      // Transform and write to target
    });
```

## Step 8: Firestore-Specific Migrations

### Collection Restructuring

```
Scenario: flattening nested subcollections into top-level collections

Before:
  users/{userId}/orders/{orderId}  (subcollection)

After:
  orders/{orderId}  (top-level, with userId field)

Migration script (Cloud Function):
  const BATCH_SIZE = 500;

  async function migrateOrders() {
    const usersSnap = await db.collection('users').get();

    for (const userDoc of usersSnap.docs) {
      const ordersSnap = await db
        .collection('users').doc(userDoc.id)
        .collection('orders').get();

      let batch = db.batch();
      let count = 0;

      for (const orderDoc of ordersSnap.docs) {
        const newRef = db.collection('orders').doc(orderDoc.id);
        batch.set(newRef, {
          ...orderDoc.data(),
          userId: userDoc.id,
          migratedAt: admin.firestore.FieldValue.serverTimestamp(),
        }, { merge: true }); // merge for idempotency

        count++;
        if (count % BATCH_SIZE === 0) {
          await batch.commit();
          batch = db.batch();
        }
      }

      if (count % BATCH_SIZE !== 0) {
        await batch.commit();
      }
    }
  }
```

### Field Type Changes

```
Scenario: converting string timestamps to Firestore Timestamps

Migration approach (expand-contract):
  Phase 1: Add new field (createdAtTs: Timestamp) alongside old field (createdAt: string)
  Phase 2: Backfill new field from old field
  Phase 3: Update application to write both, read new
  Phase 4: Drop old field in cleanup migration

Backfill script:
  async function backfillTimestamps(collectionName: string) {
    let lastDoc = null;
    let processed = 0;

    while (true) {
      let query = db.collection(collectionName)
        .where('createdAtTs', '==', null)
        .limit(500);

      if (lastDoc) {
        query = query.startAfter(lastDoc);
      }

      const snap = await query.get();
      if (snap.empty) break;

      const batch = db.batch();
      for (const doc of snap.docs) {
        const dateStr = doc.data().createdAt;
        const timestamp = admin.firestore.Timestamp.fromDate(new Date(dateStr));
        batch.update(doc.ref, { createdAtTs: timestamp });
      }
      await batch.commit();

      lastDoc = snap.docs[snap.docs.length - 1];
      processed += snap.size;
      console.log(`Processed ${processed} documents`);
    }
  }
```

### Backfill Scripts Best Practices

```
Rules for Firestore backfill scripts:
  1. Always paginate with startAfter — never load entire collection
  2. Use batched writes (max 500 operations per batch)
  3. Add a migratedAt timestamp to every modified document
  4. Support resumption: log last processed document ID
  5. Rate limit: add delays between batches if hitting Firestore write limits
  6. Dry run mode: first run should log what would change without writing
  7. Validation: count documents before and after, verify sample
  8. Idempotent: use set with merge or check-before-write patterns
  9. Run during low-traffic windows (check Firebase console for traffic patterns)
  10. Monitor Firestore usage dashboard during execution
```

## Step 9: Post-Migration Verification and Monitoring

### Verification Checklist

```
Immediately after cutover:
  - [ ] Row/document counts match expected values
  - [ ] Application health checks passing
  - [ ] Error rate at or below pre-migration baseline
  - [ ] Latency at or below pre-migration baseline
  - [ ] All critical user flows tested manually
  - [ ] Search and filter results verified
  - [ ] Reporting queries producing correct output

24 hours after cutover:
  - [ ] No data drift detected (scheduled consistency checks)
  - [ ] Backup of target database confirmed
  - [ ] No increase in support tickets or error reports
  - [ ] CDC pipeline (if used) lag is consistently <5 seconds

7 days after cutover:
  - [ ] Source system decommission decision made
  - [ ] Migration scripts archived in version control
  - [ ] Documentation updated (architecture diagrams, runbooks)
  - [ ] Lessons learned captured
```

### Monitoring Dashboard

```
Metrics to watch post-migration:
  - Query latency (p50, p95, p99) — compare to pre-migration baseline
  - Error rate per endpoint — compare to pre-migration baseline
  - Database CPU/memory/IOPS — watch for capacity issues
  - Connection pool utilization — watch for exhaustion
  - Replication lag (if applicable) — alert if >10 seconds
  - Firestore read/write/delete counts — watch for unexpected spikes
  - Application-level health checks — all green

Alert thresholds:
  - Latency p95 >2x pre-migration baseline → page on-call
  - Error rate >1% → page on-call
  - Replication lag >30 seconds → alert migration team
  - Database CPU >80% sustained → alert infrastructure team
```

### Migration Report Output

```
DATA MIGRATION REPORT
Migration: [SOURCE] → [TARGET]
Date: [TODAY]
Engineer: [NAME]

MIGRATION SUMMARY
┌──────────────────────┬────────────────────────────────────┐
│ Field                │ Value                              │
├──────────────────────┼────────────────────────────────────┤
│ Migration Type       │ [From Step 1 classification]       │
│ Strategy             │ [From Step 3 selection]            │
│ Total Records        │ [count]                            │
│ Duration             │ [HH:MM]                            │
│ Downtime             │ [HH:MM or "zero"]                  │
│ Error Rate           │ [percentage]                       │
│ Rollback Tested      │ [Yes/No]                           │
│ Validation Passed    │ [Yes/No — with details]            │
└──────────────────────┴────────────────────────────────────┘

DELIVERABLES GENERATED:
  - [ ] Migration strategy document
  - [ ] ETL pipeline (extract, transform, load scripts)
  - [ ] Field mapping document
  - [ ] Validation framework (pre, during, post checks)
  - [ ] Rollback plan (tested)
  - [ ] Monitoring dashboard configured
  - [ ] Post-migration verification completed

CROSS-REFERENCES:
  - /database-architect — for schema design and indexing strategy
  - /firebase-architect — for Firestore-specific patterns and security rules
  - /infrastructure-scaffold — for cloud infrastructure provisioning
  - /incident-response — for migration failure runbook
```

## Code Generation (Required)

Generate migration infrastructure using Write:

1. **Migration script template**: `migrations/{timestamp}_{name}.ts` with up/down functions
2. **Validation script**: `scripts/validate-migration.ts` — pre/post migration data integrity checks
3. **Rollback script**: `scripts/rollback-migration.ts` — reverses last applied migration
4. **Firestore backup**: `scripts/backup-before-migration.sh` — snapshot before migration
5. **CI workflow**: `.github/workflows/migration-test.yml` — runs migration against test DB

Before generating, Glob for existing migrations (`**/migrations/**`) and Read them to match format.
