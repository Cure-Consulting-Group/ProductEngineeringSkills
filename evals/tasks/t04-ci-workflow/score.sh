#!/bin/sh
# exit 0 = pass, 1 = fail. $1 = workdir after the run.
cd "$1" || exit 1
f=.github/workflows/test.yml; [ -f "$f" ] && grep -q "pull_request" "$f" && grep -q "actions/checkout@" "$f" && grep -qi "cache" "$f"
