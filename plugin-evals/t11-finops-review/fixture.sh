#!/usr/bin/env bash
# Fixture scaffold (runs only under --scaffold). Ported verbatim from
# evals/tasks/t11-finops-review/task.json 'fixtures'.
set -euo pipefail
mkdir -p functions
cat > functions/index.js <<'__FIXTURE_EOF__'
const {onRequest} = require('firebase-functions/v2/https');
exports.ping = onRequest({memory: '8GiB', minInstances: 25, timeoutSeconds: 540}, (req,res)=>res.send('pong'));
__FIXTURE_EOF__
