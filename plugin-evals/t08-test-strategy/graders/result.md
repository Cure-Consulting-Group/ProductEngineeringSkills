---
type: regex
pattern: '^(?=[\s\S]*(?:vitest|jest))(?=[\s\S]*(?:playwright|cypress))(?=[\s\S]*[0-9]+ ?%)'
flags: i
target: { source: file, path: 'TESTING.md' }
---
