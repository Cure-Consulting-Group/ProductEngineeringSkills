---
description: 'Routing (T53): natural phrasing must reach stripe-integration from its description alone.'
tags: [routing, stripe-integration]
max_turns: 15
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill]
runs: 3
---

We're adding monthly subscriptions to our Expo app, backend is Firebase. Walk me through the webhook side: which events to handle and how subscription status ends up in Firestore so the app can gate features.
