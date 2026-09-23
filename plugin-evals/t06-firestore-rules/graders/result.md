---
type: regex
pattern: '^(?=[\s\S]*request\.auth)(?=[\s\S]*request\.auth\.uid ?== ?[a-zA-Z]+)'
target: { source: file, path: 'firestore.rules' }
---
