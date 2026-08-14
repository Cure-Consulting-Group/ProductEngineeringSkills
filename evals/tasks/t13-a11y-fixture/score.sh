#!/bin/sh
# exit 0 = pass, 1 = fail. $1 = workdir after the run.
cd "$1" || exit 1
[ -f A11Y.md ] && grep -qi "alt" A11Y.md && grep -qi "label" A11Y.md && grep -qi "contrast" A11Y.md
