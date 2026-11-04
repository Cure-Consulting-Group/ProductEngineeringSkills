---
description: 'Routing (T81 single owner): Firestore data modeling belongs to firebase-architect, not database-architect.'
tags: [firebase-architect, routing]
max_turns: 15
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill]
runs: 3
---

How should I structure Firestore for a group chat app? Each user needs a list of their chats sorted by the latest message, an unread count per chat, and paginated message history. Writes come straight from the iOS and Android clients.
