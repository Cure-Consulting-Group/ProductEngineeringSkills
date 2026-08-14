#!/bin/sh
# exit 0 = pass, 1 = fail. $1 = workdir after the run.
cd "$1" || exit 1
f=migrations/001_add_email_verified.sql; [ -f "$f" ] && grep -qi "CONCURRENTLY" "$f" && ! grep -qiE "DROP TABLE|LOCK TABLE" "$f"
