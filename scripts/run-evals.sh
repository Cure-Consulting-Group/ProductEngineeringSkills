#!/bin/sh
# Thin wrapper — BACKLOG T30 names run-evals.sh; the implementation is Python
# per docs/SCRIPTS_CONVENTION.md. All args pass through.
exec python3 "$(dirname "$0")/run-evals.py" "$@"
