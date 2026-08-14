#!/bin/sh
# exit 0 = pass, 1 = fail. $1 = workdir after the run.
cd "$1" || exit 1
[ -f Dockerfile ] && [ $(grep -c "^FROM" Dockerfile) -ge 2 ] && grep -qE "^USER [a-z]" Dockerfile && ! grep -qE "^USER root" Dockerfile
