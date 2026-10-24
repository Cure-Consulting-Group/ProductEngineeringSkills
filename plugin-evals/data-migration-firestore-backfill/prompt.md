---
description: 'T85 risk eval: data-migration Firestore backfill on a live 4M-doc collection. Grades the Cure Firestore rules an unaided script usually breaks: BulkWriter, pagination by document ID (a where-null query misses missing fields), and a dry-run plus resumable checkpoint.'
tags: [data-migration]
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
runs: 3
---

Our Firestore `orders` collection has about 4 million documents and we've added a `status` field (see src/types/order.ts) that none of the existing documents have. It should be "cancelled" if cancelledAt is set, "fulfilled" if fulfilledAt is set, otherwise "open". The app keeps writing orders the whole time. Write the backfill script at scripts/backfill-order-status.ts using the Admin SDK.
