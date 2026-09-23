#!/usr/bin/env bash
# Fixture scaffold (runs only under --scaffold). Ported verbatim from
# evals/tasks/t15-release-notes/task.json 'fixtures'.
set -euo pipefail
cat > COMMITS.txt <<'__FIXTURE_EOF__'
feat!: drop support for legacy /v0 endpoints
feat: add player photo uploads
fix: box score double-count on overtime
chore: bump deps
__FIXTURE_EOF__
