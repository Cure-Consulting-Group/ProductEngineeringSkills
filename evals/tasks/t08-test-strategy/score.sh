#!/bin/sh
# exit 0 = pass, 1 = fail. $1 = workdir after the run.
cd "$1" || exit 1
[ -f TESTING.md ] && grep -qiE "vitest|jest" TESTING.md && grep -qiE "playwright|cypress" TESTING.md && grep -qE "[0-9]+ ?%" TESTING.md
