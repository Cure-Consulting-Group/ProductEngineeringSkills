---
type: regex
pattern: '^(?=[\s\S]*.use server.)(?=[\s\S]*getSession\(\))(?=[\s\S]*ownerId)(?=[\s\S]*safeParse\()'
target: { source: file, path: 'src/lib/notes/actions.ts' }
---
