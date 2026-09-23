---
type: regex
pattern: '^(?=[\s\S]*pull_request)(?=[\s\S]*actions/checkout@)(?=[\s\S]*[Cc][Aa][Cc][Hh][Ee])'
target: { source: file, path: '.github/workflows/test.yml' }
---
