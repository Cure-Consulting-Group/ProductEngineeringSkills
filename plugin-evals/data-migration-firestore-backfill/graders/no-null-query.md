---
type: regex
pattern: 'where\(\s*.status.\s*,\s*.==.\s*,\s*null'
match: not_contains
target: { source: file, path: 'scripts/backfill-order-status.ts' }
---
