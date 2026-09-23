---
type: regex
pattern: '^\s*\{(?=[\s\S]*\"(?:color|colors|colour)\")(?=[\s\S]*\"(?:spacing|space|dimensions?)\")'
flags: i
target: { source: file, path: 'tokens.json' }
---
