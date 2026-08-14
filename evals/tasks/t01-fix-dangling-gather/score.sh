#!/bin/sh
# exit 0 = pass, 1 = fail. $1 = workdir after the run.
cd "$1" || exit 1
awk '/Additionally gather/{f=1;next} f&&NF{exit !(/^[-*]/)}' BROKEN_SKILL.md && grep -q "Full-cycle software" BROKEN_SKILL.md
