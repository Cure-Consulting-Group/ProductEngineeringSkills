#!/bin/sh
# exit 0 = pass, 1 = fail. $1 = workdir after the run.
cd "$1" || exit 1
[ -f RUNBOOK.md ] && grep -qE "^ *[0-9]+\." RUNBOOK.md && grep -qi "escalat" RUNBOOK.md && grep -q '`' RUNBOOK.md
