#!/usr/bin/env bash
# Fixture scaffold (runs only under --scaffold). Ported verbatim from
# evals/tasks/t13-a11y-fixture/task.json 'fixtures'.
set -euo pipefail
cat > index.html <<'__FIXTURE_EOF__'
<html><body><img src=logo.png><form><input type=text placeholder=Email><button><i class=icon-go></i></button></form><div onclick=go() style="color:#9a9a9a;background:#fff">Continue</div></body></html>
__FIXTURE_EOF__
