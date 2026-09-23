---
type: regex
pattern: '^(?=(?:[\s\S]*?(?:^|\n)FROM){2})(?=[\s\S]*(?:^|\n)USER [a-z])(?![\s\S]*(?:^|\n)USER root)'
target: { source: file, path: 'Dockerfile' }
---
