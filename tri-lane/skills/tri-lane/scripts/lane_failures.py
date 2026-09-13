#!/usr/bin/env python3
"""lane_failures: a failure is a result. Classify every non-complete run into a fixed taxonomy so reliability
can be measured next to pass rate, and decide whether a retry is allowed.

Classes (whose fault -> policy):
  infra    our environment (disk, untrusted path, sandbox denied a needed write, network)  -> fix, retry once, never charge the model
  harness  our wrapper (schema rejected, stdin never fed, cap too small for the size)       -> fix, retry once, never charge the model
  quota    our budget (rate limit, pool drained)                                             -> wait, retry once
  model    the lane (refused, silent no-op, wrong answer, stalled with no progress)          -> never auto-retry; score 0 and rework
  fixture  the benchmark (grader wording, unspecified assertion)                             -> fix the grader, regrade kept runs

Causes (Wave 4, T46) refine a class so the remedy can be sized before it is built:
  cache-miss, sandbox-denied, service-unavailable, build-timeout, test-failure, scope-violation,
  empty-diff, deletion-only, stall, refused-by-instruction, schema, quota
`classify_run(run_dir)` classifies a production run from what the run dir holds (report.json, verify.jsonl,
stderr.log, final.md); `lane-eval.py classify --production` walks every run dir and appends to failures.jsonl.

Also usable standalone:  python3 lane_failures.py '<json row>'   |   python3 lane_failures.py --run <run_dir>
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


CAUSES = [
    # (class, cause, regex) over report gaps + verify stderr/stdout tails + stderr.log + final.md
    ("infra", "cache-miss", r"ENOTCACHED|No cached version|not found in (the )?cache|offline mode|--offline|Could not resolve all (files|dependencies)|Unable to resolve package|Cannot download|dependency resolution failed|Package\.resolved.*(missing|mismatch)"),
    ("infra", "sandbox-denied", r"Operation not permitted|Read-only file system|EACCES|permission denied|EPERM|sandbox.*denied"),
    ("infra", "service-unavailable", r"CoreSimulator|Simulator.*(unavailable|disconnect|not found|failed to boot)|Unable to boot|ECONNREFUSED|could not connect|connection refused|emulator.*not (running|found)|Firestore emulator|xcodebuild: error: Unable to find a destination"),
    ("harness", "schema", r"invalid_json_schema|Invalid schema for response_format"),
    ("quota", "quota", r"rate.?limit|\b429\b|usage limit|insufficient_quota|weekly limit|too many requests"),
    ("harness", "refused-by-instruction", r"(cannot|can't|will not|won't|unable to) (proceed|run|continue|make (any )?edits).*(instruction|AGENTS\.md|orchestration|sandbox)|Blocked by the sandbox"),
    ("model", "test-failure", r"\b[1-9]\d* (failed|failing)\b|AssertionError|(?m:^\s*FAIL\b)|✗|error TS\d+|BUILD FAILED|Test Suite '.*' failed|\*\* TEST FAILED \*\*|npm ERR! Test failed"),
]


def classify_run(run_dir) -> dict:
    """Classify a production run dir. Returns {task, state, failure_class, cause, reason, evidence, status, retryable}.
    Complete runs return state complete and no cause."""
    import os
    from pathlib import Path
    rd = Path(run_dir)
    def read(name, n=6000):
        try:
            return rd.joinpath(name).read_text(errors="ignore")[-n:]
        except OSError:
            return ""
    rep = {}
    try:
        rep = json.loads(rd.joinpath("report.json").read_text())
    except Exception:
        pass
    verify = []
    for line in read("verify.jsonl", 200000).splitlines():
        try:
            verify.append(json.loads(line))
        except Exception:
            pass
    vtext = ""
    for v in verify[-3:]:
        for k in ("stderr_path", "stdout_path"):
            pth = v.get(k)
            if pth and os.path.exists(pth):
                try:
                    vtext += "\n" + Path(pth).read_text(errors="ignore")[-4000:]
                except OSError:
                    pass
    status = rep.get("STATUS")
    gaps = " ".join(rep.get("GAPS") or [])
    text = " ".join([gaps, vtext, read("stderr.log"), read("final.md", 3000), read("agy.stderr", 2000)])
    out = {"task": rd.name, "status": status, "state": None, "failure_class": None, "cause": None, "reason": None, "retryable": False, "evidence": None,
           "evidence_grade": "report" if rep else "signature-only"}  # pre-1.10.0 runs have no report.json: classified from prose signatures, noisier
    timed_out = any(v.get("timed_out") for v in verify) or "wall-clock" in gaps
    if status == "complete" and not any(v.get("exit") not in (0, None) for v in verify):
        out.update(state="complete")
        return out
    if rep and rep.get("OUT_OF_SCOPE") or rep.get("EXEC_CONFIG_TOUCHED"):
        out.update(state="partial", failure_class="model", cause="scope-violation", reason="lane touched files outside FILES or executable config", retryable=False)
        return out
    if "deletion-only" in gaps:
        out.update(state="refused", failure_class="model", cause="deletion-only", reason="deleted what it was asked to modify", retryable=False)
        return out
    if status == "refused" and "empty diff" in gaps:
        out.update(state="refused", failure_class="model", cause="empty-diff", reason="empty diff with clean exit", retryable=False)
        return out
    for cls, cause, rx in CAUSES:
        m = re.search(rx, text, re.I)
        if m:
            out.update(state="error" if cls != "model" else "failed", failure_class=cls, cause=cause, reason=cause.replace("-", " "),
                       retryable=cls in RETRYABLE, evidence=text[max(0, m.start() - 80): m.end() + 80].replace("\n", " ").strip())
            return out
    if timed_out:
        changed = bool(rep.get("TOUCHED"))
        out.update(state="timeout", failure_class="harness" if changed else "model", cause="build-timeout", reason="VERIFY or lane hit its cap", retryable=changed)
        return out
    if re.search(r"\bstall(ed|ing)?\b|no progress for \d+|heartbeat.*killed", text, re.I):
        out.update(state="stalled", failure_class="model", cause="stall", reason="no progress; killed", retryable=False)
        return out
    if status in ("partial", "timeout", "unavailable", "refused"):
        out.update(state=status, failure_class="model" if status in ("partial", "refused") else "harness", cause=None, reason=f"report status {status}, no signature matched", retryable=status in ("timeout", "unavailable"))
        return out
    if not rep:
        out.update(state="unclassified", reason="no report.json (pre-1.10.0 run)")
        return out
    out.update(state="unclassified", reason="no signature matched")
    return out


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
    if len(sys.argv) > 2 and sys.argv[1] == "--run":
        print(json.dumps(classify_run(sys.argv[2]), indent=2))
    else:
        print(json.dumps(classify(json.loads(sys.argv[1])), indent=2))
