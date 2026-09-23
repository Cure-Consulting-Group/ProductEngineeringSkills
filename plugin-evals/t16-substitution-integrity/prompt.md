---
description: 'Guards the \$N substitution bug (statledger canary F-1): a skill body with escaped dollars must deliver PRICE=$0.15 / SHELL=$1 / CAP=$2,000 verbatim, never the invocation args. The fixture is slash-invoked (no Skill tool call), so the process grader is a Write of DELIVERED.txt. The no-plugin arm loads no skills at all, so W/OUT is 0 by construction — read WITH only.'
tags: [finops, ported, substitution]
max_turns: 40
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
runs: 3
---

/subst-fixture alpha beta gamma
