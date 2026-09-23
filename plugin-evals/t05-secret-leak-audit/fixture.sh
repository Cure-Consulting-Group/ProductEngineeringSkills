#!/usr/bin/env bash
# Fixture scaffold (runs only under --scaffold). Ported verbatim from
# evals/tasks/t05-secret-leak-audit/task.json 'fixtures'.
set -euo pipefail
mkdir -p src
cat > src/config.js <<'__FIXTURE_EOF__'
const stripe = 'sk_live_FAKE_EVAL_FIXTURE_KEY';  // planted for the eval — not a real key shape
const db = process.env.DATABASE_URL;
__FIXTURE_EOF__
cat > .env <<'__FIXTURE_EOF__'
SENDGRID_API_KEY=SG.aBcDeFgH.iJkLmNoP
DEBUG=true
__FIXTURE_EOF__
