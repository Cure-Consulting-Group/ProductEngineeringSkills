#!/bin/sh
# exit 0 = pass, 1 = fail. $1 = workdir after the run.
cd "$1" || exit 1
[ -f openapi.yaml ] && grep -qE "openapi: .?3" openapi.yaml && grep -q "/v1/teams" openapi.yaml && grep -qi "bearer" openapi.yaml
