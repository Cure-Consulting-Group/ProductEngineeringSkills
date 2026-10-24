---
description: 'Routing (T81): natural pre-launch phrasing must reach security-review from its rewritten description.'
tags: [security-review, routing]
max_turns: 15
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill]
runs: 3
---

We're launching our Next.js and Firebase app next week. We just added email login, and users can now upload a profile photo and save their home address. Can you check this for vulnerabilities before we go live? Here's the new code:

```ts
// app/profile/actions.ts
'use server'
import { db } from '@/lib/firebase-admin'
export async function saveAddress(userId: string, address: string) {
  await db.collection('users').doc(userId).update({ address })
}
```

```
// storage.rules
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    match /avatars/{userId}/{file} {
      allow read, write: if request.auth != null;
    }
  }
}
```
