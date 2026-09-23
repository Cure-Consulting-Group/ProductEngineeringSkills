---
type: regex
pattern: '^(?=[\s\S]*empty)(?=[\s\S]*loading)(?=[\s\S]*error)(?=[\s\S]*offline)(?=[\s\S]*long)'
flags: i
target: { source: file, path: 'design/states.md' }
---
