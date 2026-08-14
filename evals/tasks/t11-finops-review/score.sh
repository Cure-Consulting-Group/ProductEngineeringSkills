#!/bin/sh
# exit 0 = pass, 1 = fail. $1 = workdir after the run.
cd "$1" || exit 1
[ -f COSTS.md ] && grep -qi "minInstances" COSTS.md && grep -qiE "memory|8GiB" COSTS.md
