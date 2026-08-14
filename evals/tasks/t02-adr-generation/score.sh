#!/bin/sh
# exit 0 = pass, 1 = fail. $1 = workdir after the run.
cd "$1" || exit 1
f=$(ls docs/adr/*.md 2>/dev/null | head -1); [ -n "$f" ] && grep -qi "context" "$f" && grep -qi "decision" "$f" && grep -qi "consequence" "$f"
