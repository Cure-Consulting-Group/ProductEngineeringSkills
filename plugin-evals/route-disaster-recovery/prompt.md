---
description: 'Routing (T53): natural phrasing must reach disaster-recovery from its description alone.'
tags: [disaster-recovery, routing]
max_turns: 15
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill]
runs: 3
---

What happens if all of us-central1 goes down? We run Cloud Run, Firestore, and Cloud SQL there. I need recovery targets and a failover drill we can actually run.
