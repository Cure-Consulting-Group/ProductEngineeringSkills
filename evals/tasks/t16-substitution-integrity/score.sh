#!/bin/sh
# exit 0 = pass, 1 = fail. $1 = workdir after the run.
cd "$1" || exit 1
[ -f DELIVERED.txt ] && grep -q 'PRICE=\$0\.15' DELIVERED.txt && grep -q 'SHELL=\$1' DELIVERED.txt && grep -q 'CAP=\$2,000' DELIVERED.txt && ! grep -qE 'alpha|beta' DELIVERED.txt
