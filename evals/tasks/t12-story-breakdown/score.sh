#!/bin/sh
# exit 0 = pass, 1 = fail. $1 = workdir after the run.
cd "$1" || exit 1
f=docs/epics/live-box-score.md; [ -f "$f" ] && [ $(grep -c "Given" "$f") -ge 4 ] && grep -qiE "points?" "$f"
