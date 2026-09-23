---
type: regex
pattern: '^(?=(?:[\s\S]*?(?:^|\n)(?:\*\*|#+ |- )?Decision:){3})(?=[\s\S]*Reason:)'
target: { source: file, path: 'design/decisions.md' }
---
