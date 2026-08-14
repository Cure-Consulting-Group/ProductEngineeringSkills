#!/bin/sh
# exit 0 = pass, 1 = fail. $1 = workdir after the run.
cd "$1" || exit 1
[ -f CHANGELOG.md ] && grep -q "3.0.0" CHANGELOG.md && grep -qi "breaking" CHANGELOG.md && grep -qi "photo" CHANGELOG.md
