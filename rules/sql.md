---
paths:
  - "**/*.sql"
  - "**/migrations/**"
---

# SQL Standards — Cure Consulting Group

When editing SQL files or migrations, follow these standards:

## Naming Conventions
- Tables: `snake_case`, plural (`users`, `order_items`)
- Columns: `snake_case`, singular (`first_name`, `created_at`)
- Indexes: `idx_{table}_{columns}` (`idx_users_email`)
- Constraints: `fk_{table}_{ref_table}`, `chk_{table}_{column}`, `uq_{table}_{column}`
- Migrations: `{timestamp}_{description}.sql` (`20261024120000_add_users_table.sql`)

## Migration Safety
- Every migration is reversible — UP and DOWN sections
- Never drop columns or tables in the same release as the code change — expand, migrate, then contract
- Add columns as nullable or with a constant DEFAULT; for NOT NULL on a populated table use `CHECK (...) NOT VALID` → `VALIDATE CONSTRAINT` → `SET NOT NULL`
- `CREATE INDEX CONCURRENTLY` (PostgreSQL) — it cannot run inside a transaction block
- `SET lock_timeout = '5s'` at the top of DDL migrations so a blocked lock fails fast instead of queueing traffic
- Test migrations against a copy of production data before deploying

## Schema Design
- Every table has: `id` (primary key), `created_at` and `updated_at` (`timestamptz`)
- Primary keys: `bigint GENERATED ALWAYS AS IDENTITY`, or UUIDv7 when IDs are exposed or generated outside the database (`uuidv7()` is built in from PostgreSQL 18; generate in the app on older versions). Not `serial`/`bigserial`, not random UUIDv4 for B-tree keys
- PostgreSQL 18 for new projects
- Foreign keys always state an ON DELETE policy (CASCADE, SET NULL or RESTRICT)
- `timestamptz`, never `timestamp`
- `text`, not `varchar(n)`, unless there is a real length constraint (enforce it with a CHECK)

## Query Standards
- Parameterized queries only — never string concatenation for values
- Explicit column lists in INSERT
- Explicit JOIN syntax — never comma-separated FROM tables
- Index every foreign key column and the columns used in WHERE/ORDER BY
- LIMIT every user-facing query; cursor (keyset) pagination over OFFSET for large tables

Verified 2026-10-24: `uuidv7()` documented for PostgreSQL 18 (postgresql.org/docs/current/functions-uuid.html, 18.6). Matches `database-architect`.
