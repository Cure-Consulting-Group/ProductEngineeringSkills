#!/bin/sh
# exit 0 = pass, 1 = fail. $1 = workdir after the run.
cd "$1" || exit 1
[ -f firestore.rules ] && grep -q "request.auth" firestore.rules && grep -qE "request\.auth\.uid ?== ?[a-zA-Z]+" firestore.rules
