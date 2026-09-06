#!/usr/bin/env python3
"""lane_failures: a failure is a result. Classify every non-complete run into a fixed taxonomy so reliability
can be measured next to pass rate, and decide whether a retry is allowed.

Classes (whose fault -> policy):
  infra    our environment (disk, untrusted path, sandbox denied a needed write, network)  -> fix, retry once, never charge the model
  harness  our wrapper (schema rejected, stdin never fed, cap too small for the size)       -> fix, retry once, never charge the model
  quota    our budget (rate limit, pool drained)                                             -> wait, retry once
  model    the lane (refused, silent no-op, wrong answer, stalled with no progress)          -> never auto-retry; score 0 and rework
  fixture  the benchmark (grader wording, unspecified assertion)                             -> fix the grader, regrade kept runs

Also usable standalone:  python3 lane_failures.py '<json row>'
"""
from __future__ import annotations

import json
import re
import sys

RETRYABLE = {"infra", "harness", "quota"}

SIGNATURES = [
    # (class, reason, regex over error text + stderr + events tail + final)
    ("harness", "output schema rejected", r"invalid_json_schema|Invalid schema for response_format"),
    ("harness", "stdin never fed", r"Reading additional input from stdin"),
    ("harness", "unsupported effort for model", r"reasoning effort.*(not supported|unsupported|invalid)|ultra.*not (supported|available)"),
    ("quota", "rate limit or pool drained", r"rate.?limit|429|usage limit|quota|too many requests|insufficient_quota|weekly limit"),
    ("infra", "disk full", r"ENOSPC|No space left on device"),
    ("infra", "untrusted path", r"confirm the path|not a trusted|trusted (directory|workspace)|which repository"),
    ("infra", "sandbox denied a required write", r"Operation not permitted|Read-only file system|EACCES|permission denied"),
    ("infra", "network blocked in sandbox", r"Could not resolve host|Network is unreachable|ConnectionError|getaddrinfo|Temporary failure in name resolution"),
    ("harness", "codex declined per instruction file", r"(cannot|can't|will not|won't) (proceed|run|continue).*(instruction|AGENTS\.md|orchestration)"),
]


def classify(row: dict) -> dict:
    """Return {"state", "failure_class", "reason", "retryable"} for a run row (or partial row)."""
    meta = row.get("meta") or {}
    grade = row.get("grade") or {}
    text = " ".join(str(x) for x in (meta.get("error"), meta.get("stderr_tail"), meta.get("events_tail"), row.get("final_tail")) if x)
    passed = bool(row.get("pass"))
    exit_code = meta.get("exit")
    stalled = bool(meta.get("stalled"))
    changed = bool(row.get("diff_stat")) or bool(grade.get("touched"))

    if passed:
        return {"state": "complete", "failure_class": None, "reason": None, "retryable": False}
    for cls, reason, rx in SIGNATURES:
        if re.search(rx, text, re.I):
            return {"state": "error", "failure_class": cls, "reason": reason, "retryable": cls in RETRYABLE}
    if stalled:
        return {"state": "stalled", "failure_class": "model", "reason": f"no progress for {meta.get('stall_seconds', '?')}s; killed", "retryable": False}
    if exit_code == 124:
        return {"state": "timeout", "failure_class": "harness" if changed else "model", "reason": "hit the wall-clock cap" + (" with a diff (cap too small for the task size)" if changed else " with no diff"), "retryable": changed}
    if exit_code not in (0, None) and not changed and not (row.get("final_tail") or "").strip():
        return {"state": "error", "failure_class": "harness", "reason": f"lane exit {exit_code} with no output", "retryable": True}
    if grade.get("score") is None:
        return {"state": "error", "failure_class": "harness", "reason": row.get("error") or "no grade produced", "retryable": True}
    if grade.get("implemented_anyway") is False and grade.get("named_gap"):
        return {"state": "failed", "failure_class": "model", "reason": "named a spec gap but not all of them", "retryable": False}
    if not changed and row.get("role") == "implement":
        return {"state": "refused", "failure_class": "model", "reason": "no diff produced", "retryable": False}
    return {"state": "failed", "failure_class": "model", "reason": "graded below pass", "retryable": False}


if __name__ == "__main__":
    print(json.dumps(classify(json.loads(sys.argv[1])), indent=2))
