---
type: regex
pattern: '^(?=[\s\S]*git worktree add)(?=[\s\S]*git worktree (?:remove|prune))(?![\s\S]*git stash)'
target: { source: file, path: 'HOTFIX.md' }
---
