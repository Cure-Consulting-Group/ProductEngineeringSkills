#!/usr/bin/env bash
# Fixture scaffold (runs only under --scaffold). Ported verbatim from
# evals/tasks/t16-substitution-integrity/task.json 'fixtures'.
set -euo pipefail
mkdir -p .claude/skills/subst-fixture
cat > .claude/skills/subst-fixture/SKILL.md <<'__FIXTURE_EOF__'
---
name: subst-fixture
description: "Delivery-integrity fixture — asserts literal dollars survive skill loading"
argument-hint: "[words]"
---

Write a file named DELIVERED.txt whose entire content is EXACTLY the following three lines, character-for-character:

PRICE=\$0.15
SHELL=\$1
CAP=\$2,000
__FIXTURE_EOF__
