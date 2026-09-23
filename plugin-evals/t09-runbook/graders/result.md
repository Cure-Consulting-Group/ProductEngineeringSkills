---
type: regex
pattern: '^(?=[\s\S]*(?:^|\n) *[0-9]+\.)(?=[\s\S]*escalat)(?=[\s\S]*`)'
flags: i
target: { source: file, path: 'RUNBOOK.md' }
---
