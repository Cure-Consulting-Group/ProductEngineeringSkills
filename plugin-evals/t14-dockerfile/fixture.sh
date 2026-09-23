#!/usr/bin/env bash
# Fixture scaffold (runs only under --scaffold). Ported verbatim from
# evals/tasks/t14-dockerfile/task.json 'fixtures'.
set -euo pipefail
cat > package.json <<'__FIXTURE_EOF__'
{
  "name": "api", "main": "server.js", "dependencies": {"express": "^4"}
}
__FIXTURE_EOF__
