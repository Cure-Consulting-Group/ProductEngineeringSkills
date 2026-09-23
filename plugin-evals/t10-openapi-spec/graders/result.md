---
type: regex
pattern: '^(?=[\s\S]*openapi: .?3)(?=[\s\S]*/v1/teams)(?=[\s\S]*bearer)'
flags: i
target: { source: file, path: 'openapi.yaml' }
---
