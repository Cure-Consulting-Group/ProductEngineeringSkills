---
type: regex
pattern: '^(?=[\s\S]*minInstances)(?=[\s\S]*(?:memory|8GiB))'
flags: i
target: { source: file, path: 'COSTS.md' }
---
