---
name: data-migration
description: "Plans and runs data migrations: ETL, backfills, dual-write, zero-downtime cutover, rollback. Use when moving or reshaping existing data across databases, Firestore, or legacy systems."
when_to_use: "NOT for schema, index, or engine selection (use database-architect) or checking a single migration file (migration-validator agent)."
argument-hint: "[source-to-target]"
metadata:
  verified: 2026-09-23
---

# Data Migration

**Outcome:** a migration plan an engineer can execute and reverse — strategy with the reason, field mapping, idempotent scripts, validation gates (before/during/after), a rollback path with a tested restore, and the cutover sequence. Done when every source field has a mapping or an explicit skip, the rollback has been rehearsed on a copy, and the go/no-go checks are numeric.

**Invariants** (these protect client data, which is irreversible to lose):
- A restore from the pre-migration backup is tested before the forward run.
- Every script is idempotent and resumable from a checkpoint — migrations get interrupted.
- Production data never lands in dev/staging without anonymization.
- Scheduled downtime needs explicit client sign-off; zero-downtime is the default target.

## Pre-Processing (Auto-Context)

Context (pre-filled in Claude Code; in other runtimes run these commands first):

- Existing migrations: !`find . -maxdepth 4 -path "*/node_modules" -prune -o -type d -name "migrations" -print 2>/dev/null | head -3 || echo "(none)"`
- Firebase config: !`ls firebase.json firestore.rules firestore.indexes.json 2>/dev/null || echo "(no Firebase config)"`
- Stack manifest: !`head -25 package.json 2>/dev/null || echo "(no package.json)"`

## Step 1: Classify

| Type | Example | Default strategy |
|---|---|---|
| In-place reshape | Rename/split fields, flatten subcollections, change types | Expand-contract with backfill |
| Same engine, new home | Cloud SQL instance move, project split | Replication (logical/PITR export) + cutover |
| Engine switch | MongoDB → Firestore, MySQL → PostgreSQL | Bulk load + CDC catch-up + flagged cutover |
| Legacy integration | CSV/SFTP drops, SOAP, mainframe extracts | Staged ETL with quarantine table |
| Review of a plan | — | Findings with severity against the invariants; no files |

Strategy choice in one line: under ~1M records with an agreed window → big bang; otherwise bulk + CDC; long-lived legacy replacement → strangler (per-feature dual-read/dual-write). The model knows these patterns; the plan must state *which* and *why*.

## Step 2: Gather Context

Ask only what isn't discoverable: source and target engines and versions, volume (records, GB, largest table/collection), write rate during migration, downtime tolerance, PII/PHI/PCI and residency constraints, every reader/writer of the data (including mobile app versions still in the field), hard deadline, and last verified backup.

## Step 3: Mapping and Idempotency

Produce a mapping table: source field → target field → transform → null default. Every source field appears, including `SKIP` rows with a reason (e.g. SSNs not needed).

- **Deterministic target IDs** derived from the source primary key only (`hash(sourceTable + ":" + sourcePk)` or the source key itself). Never include a migration version or timestamp in the ID — a re-run under a new version would duplicate every record.
- **Writes are upserts:** `INSERT … ON CONFLICT DO UPDATE` in SQL; `set(…, { merge: true })` in Firestore.
- **Checkpoint** the last processed key after each chunk; the script accepts `--resume-from` and `--dry-run` (logs what would change, writes nothing). Dry run first, always.
- **Dead-letter** failed records with the error category (data quality / network / quota / permission); never skip silently. Halt when the error rate exceeds 1% of a chunk.
- Record `migratedAt` and `migrationId` as fields (not in the ID) so you can find and reverse touched rows.

## Step 4: Firestore Migrations (Cure's most common case)

- **Bulk writes use `BulkWriter`** (`db.bulkWriter()` in the Admin SDK): it batches, retries transient errors, and throttles to the 500/50/5 ramp automatically. Use batched writes only when a group of writes must be atomic; batches are bounded by the 10 MiB request size and 500 field transforms (the old 500-writes-per-batch cap no longer appears in the quotas page — confirm before relying on larger batches).
- **Paginate by document ID**, not by a query on the field you're backfilling: `orderBy(FieldPath.documentId()).startAfter(lastId).limit(500)`. A `where('newField', '==', null)` query does **not** match documents where the field is missing, so a backfill driven by it silently skips every unmigrated document. Check the field in code.
- **Expand-contract for type or shape changes:** add the new field → app writes both → backfill → app reads new → stop writing old → cleanup migration drops old. Mobile clients lag: don't drop the old field until the minimum supported app version reads the new one (check the Remote Config force-update floor).
- **CDC with Functions v2:** `onDocumentWritten` from `firebase-functions/v2/firestore`. Delivery is at-least-once and unordered — handlers must be idempotent and compare `event.data.after.updateTime` (or a version field) before overwriting the target. A write that doesn't change data fires no event.
- **Hot documents:** a single document sustains about 1 write/sec; counters or aggregates touched by the backfill need sharding or a post-pass.
- **Security rules** must accept both old and new shapes during the transition, or clients on the old shape start failing writes mid-migration.
- **Backups:** `gcloud firestore export` is *not* a point-in-time snapshot (it may include writes made while it ran). For a consistent pre-migration copy use PITR (7-day window, export with a snapshot time) or a scheduled backup. `gcloud firestore import` overwrites documents with the same ID.

Read the Firestore scripts reference (`reference/details.md`) when you need a full backfill or subcollection-flattening script to adapt.

## Step 5: SQL and Legacy Gotchas

- **PostgreSQL logical replication** needs `wal_level = logical` (restart required; on Cloud SQL set the `cloudsql.logical_decoding` flag instead of `ALTER SYSTEM`). Tables need a primary key or `REPLICA IDENTITY`; sequences and DDL are not replicated — reset sequences on the target before cutover.
- Bulk load with `COPY` (or `\copy` from a client), then create secondary indexes and constraints after the load.
- Backfills on large tables: chunk by primary-key range (1k–5k rows), commit per chunk, and watch replication lag and lock waits; never one giant `UPDATE`.
- Legacy files: stream-parse (never load whole files), verify header row counts and checksums, normalise encoding to UTF-8 up front, land raw rows in a quarantine/staging table before transforming.

## Step 6: Validation Gates

| Gate | Checks | Pass threshold |
|---|---|---|
| Pre | Null %, type drift, orphaned FKs, duplicate business keys, max field lengths vs target | All mapped fields satisfiable; anomalies listed with owner |
| During | Extracted vs loaded counts per chunk, error rate, throughput, CDC lag | Errors <0.1% (halt at 1%); lag <5 s steady |
| Post | Counts per table/collection, checksums on critical columns, 1% or 1,000-record sample (whichever larger), business-rule checks, smoke tests of critical flows | Counts match or delta explained; zero checksum mismatches on money fields |

## Step 7: Cutover and Rollback

Flag-controlled sequence (flags from `feature-flags`): dual-write on → validate → reads shift 10% → 50% → 100% → target-only writes → hold → decommission. Rollback at any step before target-only writes = flags off (source stayed authoritative). After target-only writes, rollback = restore the pre-migration backup plus replay of the dead-letter/CDC log — state that RPO explicitly.

Roll back when: target write errors >1%, divergence found by the consistency check, p95 latency >2× the pre-migration baseline, or any money-field checksum mismatch. Keep the source read-only for at least 7 days after cutover.

Report: type, strategy, record counts, duration, downtime, error rate, rollback rehearsed (yes/no), gate results. Match length to the need; no filler sections.

## Code/Artifact Generation

Applies only when Step 1 calls for executing a migration (not reviews or planning questions). Read existing migrations first and match their format and language.

- The migration script with `--dry-run`, `--resume-from`, checkpointing, and dead-lettering.
- A validation script implementing the Step 6 gates.
- A backup/restore script for the target (Firestore PITR export or `pg_dump --format=custom`).

Don't add CI workflows or refactor application code unless asked.

## Related skills

- `database-architect` — target schema, indexes, engine choice.
- `firebase-architect` — Firestore rules and data model for the target shape.
- `feature-flags` — the cutover flags.
- `disaster-recovery` — backup policy beyond this migration.
- `migration-validator` agent — review of individual migration files.
