---
globs: "**/*.sql,**/migrations/**"
---

# SQL Standards — Cure Consulting Group

When editing SQL files or migrations, follow these standards:

## Naming Conventions
- Tables: `snake_case`, plural (`users`, `order_items`)
- Columns: `snake_case`, singular (`first_name`, `created_at`)
- Indexes: `idx_{table}_{columns}` (`idx_users_email`)
- Constraints: `fk_{table}_{ref_table}`, `chk_{table}_{column}`, `uq_{table}_{column}`
- Migrations: `{timestamp}_{description}.sql` (`20240315120000_add_users_table.sql`)

## Migration Safety
- Every migration must be reversible — include both UP and DOWN sections
- Never drop columns or tables in the same release as code changes — use 2-step process
- Add columns as nullable or with DEFAULT — never add NOT NULL without DEFAULT on existing tables
- Use `CREATE INDEX CONCURRENTLY` (PostgreSQL) to avoid table locks
- Test migrations against a copy of production data before deploying

## Schema Design
- Every table has: `id` (primary key), `created_at` (timestamptz), `updated_at` (timestamptz)
- Use `uuid` or `bigserial` for primary keys — never `serial` (32-bit overflow risk)
- Foreign keys always have ON DELETE policy (CASCADE, SET NULL, or RESTRICT — never leave default)
- Use `timestamptz` not `timestamp` — always store timezone-aware timestamps
- Use `text` not `varchar` unless you have a specific length constraint

## Query Standards
- Always use parameterized queries — never string concatenation for values
- Include explicit column lists in INSERT — never `INSERT INTO table VALUES (...)`
- Use explicit JOIN syntax — never comma-separated FROM tables
- Index all foreign key columns and columns used in WHERE/ORDER BY
- LIMIT all user-facing queries — no unbounded SELECTs
