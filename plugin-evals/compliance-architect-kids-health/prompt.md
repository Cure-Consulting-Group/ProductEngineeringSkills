---
description: 'T85 risk eval: compliance-architect on a kids + health app (HIPAA and COPPA at once). Grades vendor and rule facts the skill carries and an unaided answer usually misses: Identity Platform instead of Firebase Auth for PHI, SendGrid not HIPAA-eligible, the 2025 COPPA amendments, and an audit trail outside Firestore.'
tags: [compliance-architect]
max_turns: 20
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill]
runs: 3
---

We're building a pediatric asthma tracker. Kids aged 8 to 14 log symptoms and inhaler use on a phone; their parents and the child's pulmonology clinic see the data. The clinic is our customer and will sign a BAA with us. Current stack: Firebase Auth, Firestore, Cloud Functions, GA4 and Crashlytics, SendGrid for reminder emails, and Stripe for the parent subscription. US users only for now. What do we have to change in the architecture before launch?
