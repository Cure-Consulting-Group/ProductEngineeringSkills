---
type: regex
pattern: '^(?=[\s\S]*dry-?run)(?=[\s\S]*(?:resume|checkpoint))'
flags: i
target: { source: file, path: 'scripts/backfill-order-status.ts' }
---
