#!/usr/bin/env bash
# Fixture scaffold (runs only under --scaffold). Ported verbatim from
# evals/tasks/t01-fix-dangling-gather/task.json 'fixtures'.
set -euo pipefail
cat > BROKEN_SKILL.md <<'__FIXTURE_EOF__'
# SDLC Artifact Generator

## Pre-Processing (Auto-Context)

- Portfolio: check PORTFOLIO.md

Use this context to tailor all output.

Additionally gather (domain-specific):
Full-cycle software development lifecycle artifact generation for technical product teams.

## Step 1
Determine what the user needs.
__FIXTURE_EOF__
