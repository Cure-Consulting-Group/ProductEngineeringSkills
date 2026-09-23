---
description: 'Ported golden task (release-management skill; release-coordinator agent). Result gate mirrors evals/tasks/t15-release-notes/score.sh.'
tags: [ported, release-management]
max_turns: 40
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
runs: 3
---

COMMITS.txt has the git log since v2.3.1. Work out what the next version number should be under semver and write CHANGELOG.md for that release: version heading, features and fixes grouped, and any breaking changes called out.
