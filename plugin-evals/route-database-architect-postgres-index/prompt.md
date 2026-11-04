---
description: 'Routing (T81): a PostgreSQL index and slow-query question reaches database-architect, not firebase-architect.'
tags: [database-architect, routing]
max_turns: 15
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill]
runs: 3
---

Our Postgres query for a customer's recent orders now takes 3 to 4 seconds because the orders table has 40M rows: SELECT * FROM orders WHERE customer_id = :customer_id AND status <> 'cancelled' ORDER BY created_at DESC LIMIT 20. What index should we add, and how do we add it in production without locking the table?
