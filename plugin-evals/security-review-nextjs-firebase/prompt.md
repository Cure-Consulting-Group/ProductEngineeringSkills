---
description: 'T85 risk eval: security-review on a Next 16 + Firebase + Stripe fixture. Grades Cure-specific calls an unaided review tends to miss: OWASP 2025 (not 2021) IDs, the Server Action IDOR, the AIza web key treated as a public identifier, and X-XSS-Protection flagged for removal.'
tags: [security-review]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill]
runs: 3
---

We launch this app to customers next week. Users sign in with Firebase, edit their profile (including their home address), and upgrade to Pro through Stripe Checkout. Please look through the repo for security problems before we go live and tell me what has to be fixed first.
