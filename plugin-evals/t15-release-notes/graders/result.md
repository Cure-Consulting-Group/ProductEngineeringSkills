---
type: regex
pattern: '^(?=[\s\S]*3\.0\.0)(?=[\s\S]*breaking)(?=[\s\S]*photo)'
flags: i
target: { source: file, path: 'CHANGELOG.md' }
---
