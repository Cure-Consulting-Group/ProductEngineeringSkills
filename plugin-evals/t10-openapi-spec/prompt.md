---
description: 'Ported golden task (api-architect skill; api-specification output style). Result gate mirrors evals/tasks/t10-openapi-spec/score.sh.'
tags: [api-architect, ported]
max_turns: 40
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
runs: 3
---

Write openapi.yaml (OpenAPI 3.x) for our roster service: GET /v1/teams/{teamId}/players as a paginated list and POST /v1/teams/{teamId}/players. Bearer JWT auth; include the error responses.
