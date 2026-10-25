---
description: 'T85 code-generator eval (scaffold): nextjs-feature-scaffold on a Next 16 + Zod 4 fixture. Grades Next 16 / Cure rules an unaided scaffold often gets wrong: params typed as a Promise, auth and Zod validation inside the Server Action, no deprecated error.flatten(), and loading/error boundaries for the route.'
tags: [nextjs-feature-scaffold]
max_turns: 50
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
runs: 3
---

Add a notes feature to this app. I need a page at src/app/projects/[id]/notes/page.tsx that lists a project's notes, and a form on it to add a note, with the mutation in src/lib/notes/actions.ts. Use the helpers in src/lib/db.ts and src/lib/auth.ts. Only the project's owner may add notes, and a note body is 1 to 2000 characters.
