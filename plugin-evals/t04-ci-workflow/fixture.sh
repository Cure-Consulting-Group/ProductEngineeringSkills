#!/usr/bin/env bash
# Fixture scaffold (runs only under --scaffold). Ported verbatim from
# evals/tasks/t04-ci-workflow/task.json 'fixtures'.
set -euo pipefail
cat > package.json <<'__FIXTURE_EOF__'
{
  "name": "fixture",
  "scripts": {"test": "node --test"}
}
__FIXTURE_EOF__
