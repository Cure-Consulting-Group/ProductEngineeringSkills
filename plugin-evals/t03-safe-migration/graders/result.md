---
type: regex
pattern: '^(?=[\s\S]*CONCURRENTLY)(?![\s\S]*(?:DROP TABLE|LOCK TABLE))'
flags: i
target: { source: file, path: 'migrations/001_add_email_verified.sql' }
---
