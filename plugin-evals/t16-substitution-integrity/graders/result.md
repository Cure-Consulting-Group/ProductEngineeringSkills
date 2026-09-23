---
type: regex
pattern: '^(?=[\s\S]*PRICE=\$0\.15)(?=[\s\S]*SHELL=\$1)(?=[\s\S]*CAP=\$2,000)(?![\s\S]*(?:alpha|beta))'
target: { source: file, path: 'DELIVERED.txt' }
---
