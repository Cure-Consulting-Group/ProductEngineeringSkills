#!/usr/bin/env python3
"""lane-report: turn a lane's worktree into the report contract, with the empty-diff rule enforced.

Reads the worktree, computes the diff stat, re-runs the VERIFY command(s) itself,
and prints the report. This is the guarantee layer: an empty diff is `refused`
no matter what the lane's final message says.

Exit codes: 0 complete, 2 partial (verify failed), 3 refused (empty diff),
4 timeout/unavailable passed via --status-hint. Python stdlib only.

Examples:
  python3 lane-report.py --worktree ../wt/task --lane "gpt-5.6-luna @ high" \
      --verify "npm test" --final /tmp/lane-final.txt --objective "Add rules tests"
  python3 lane-report.py --worktree ../wt/task --lane "gpt-5.6-sol @ max" --status-hint timeout --json
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def sh(cmd: str | list[str], cwd: str, timeout: int, shell: bool = False) -> tuple[int, str]:
    try:
        p = subprocess.run(cmd, cwd=cwd, shell=shell, capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL)
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except subprocess.TimeoutExpired:
        return 124, f"timeout after {timeout}s"
    except FileNotFoundError as e:
        return 127, str(e)


def tail(text: str, n: int) -> str:
    lines = text.rstrip().splitlines()
    return "\n".join(lines[-n:])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--worktree", required=True, help="path the lane ran against")
    ap.add_argument("--lane", required=True, help='as executed, e.g. "gpt-5.6-luna @ high" or "gemini-3.8-flash-high"')
    ap.add_argument("--objective", default="", help="one-line objective from the spec")
    ap.add_argument("--verify", action="append", default=[], help="VERIFY command to re-run (repeatable)")
    ap.add_argument("--verify-timeout", type=int, default=600, help="seconds per verify command (default 600)")
    ap.add_argument("--final", help="file holding the lane's final message")
    ap.add_argument("--status-hint", choices=["timeout", "unavailable"], help="override when the wrapper already knows the lane failed")
    ap.add_argument("--tail", type=int, default=40, help="lines of verify output to keep (default 40)")
    ap.add_argument("--json", action="store_true", help="emit JSON instead of the text contract")
    args = ap.parse_args()

    wt = str(Path(args.worktree).resolve())
    rc, stat = sh(["git", "diff", "--stat", "HEAD"], wt, 60)
    rc2, porcelain = sh(["git", "status", "--porcelain"], wt, 60)
    changed = bool(porcelain.strip())
    lane_said = ""
    if args.final and Path(args.final).exists():
        lane_said = tail(Path(args.final).read_text(errors="ignore"), 3).strip()

    gaps: list[str] = []
    verified: list[dict] = []
    if args.status_hint:
        status = args.status_hint
        gaps.append(f"wrapper reported {status}")
    elif not changed:
        status = "refused"
        gaps.append("empty diff with clean exit: treat as refusal, not success; check AGENTS.md pins and the spec preamble")
    else:
        status = "complete"
        for cmd in args.verify:
            vrc, out = sh(cmd, wt, args.verify_timeout, shell=True)
            verified.append({"command": cmd, "exit": vrc, "output_tail": tail(out, args.tail)})
            if vrc != 0:
                status = "partial"
        if not args.verify:
            gaps.append("no VERIFY command supplied; the report carries no evidence")
            status = "partial"
    if lane_said and changed and ("no changes" in lane_said.lower() or "did not modify" in lane_said.lower()):
        gaps.append("lane's final message disagrees with the diff")

    report = {
        "LANE": args.lane,
        "STATUS": status,
        "OBJECTIVE": args.objective,
        "CHANGES": stat.strip() or "(none)",
        "UNTRACKED": [l[3:] for l in porcelain.splitlines() if l.startswith("??")],
        "VERIFIED": verified,
        "LANE_SAID": lane_said or "(no final message captured)",
        "GAPS": gaps,
    }
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"LANE       {report['LANE']}")
        print(f"STATUS     {report['STATUS']}")
        print(f"OBJECTIVE  {report['OBJECTIVE']}")
        print("CHANGES")
        print("  " + report["CHANGES"].replace("\n", "\n  "))
        if report["UNTRACKED"]:
            print("  untracked: " + ", ".join(report["UNTRACKED"]))
        print("VERIFIED")
        if not verified:
            print("  (not run)")
        for v in verified:
            print(f"  $ {v['command']}  -> exit {v['exit']}")
            print("  " + v["output_tail"].replace("\n", "\n  "))
        print(f"LANE SAID  {report['LANE_SAID']}")
        print("GAPS       " + ("; ".join(gaps) if gaps else "none"))
    return {"complete": 0, "partial": 2, "refused": 3}.get(status, 4)


if __name__ == "__main__":
    sys.exit(main())
