---
type: regex
pattern: '^(?=[\s\S]*\"screens\")(?=[\s\S]*\"fixed\"\s*:\s*true)(?=[\s\S]*\"flows\")(?=[\s\S]*empty)(?=[\s\S]*error)(?=[\s\S]*long)'
flags: i
target: { source: file, path: 'design/spec.json' }
---
