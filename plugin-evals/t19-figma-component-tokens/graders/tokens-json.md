---
type: regex
pattern: '^\s*\{(?=[\s\S]*(?:light|dark|color))(?=[\s\S]*(?:space|spacing|dimension))'
flags: i
target: { source: file, path: 'tokens.json' }
---
