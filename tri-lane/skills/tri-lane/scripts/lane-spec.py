#!/usr/bin/env python3
"""lane-spec: check the substance of a six-part spec before dispatch (Wave 4, T50).

Not a hook. The implementer runs it in step 3; hard failures return STATUS refused, warnings go to GAPS.
Checks:
  sections   all seven headers present (LANE, REASONING, OBJECTIVE, FILES, INTERFACES, CONSTRAINTS, VERIFY)
  lane       LANE is luna | sol | flash | pro
  rung       REASONING is legal for the lane (Luna has no ultra; agy has low|medium|high)
  files      every FILES path exists in the worktree or its parent directory does; bare directories warn
  verify     VERIFY is non-empty; a pipe through grep/tail/head or an `||` fallback warns (exit status may be masked)
  constraints CONSTRAINTS non-empty
Exit 0 = ok (warnings allowed), 2 = hard failure. --json for machine use. Python stdlib only.

  python3 lane-spec.py check "$SPEC" --worktree "$WT"
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HEADERS = ("LANE", "REASONING", "OBJECTIVE", "FILES", "INTERFACES", "CONSTRAINTS", "VERIFY")
LANES = {"luna": {"low", "medium", "high", "xhigh", "max"}, "sol": {"low", "medium", "high", "xhigh", "max", "ultra"},
         "flash": {"low", "medium", "high"}, "pro": {"low", "medium", "high"}}
FILTER_RX = re.compile(r"\|\s*(grep|tail|head|sed|awk|cut|sort|uniq|wc)\b|\|\|")
HEADER_RX = re.compile(r"^\s*(#+\s*)?\**(LANE|REASONING|OBJECTIVE|FILES|INTERFACES|CONSTRAINTS|VERIFY)\**\s*[:\-—]?\s*(.*)$")


def parse(text: str) -> dict:
    """{header: [lines]} with the header's own trailing text as the first line."""
    out: dict = {}
    cur = None
    for line in text.splitlines():
        m = HEADER_RX.match(line)
        if m:
            cur = m.group(2)
            out.setdefault(cur, [])
            if m.group(3).strip():
                out[cur].append(m.group(3).strip())
            continue
        if cur:
            out[cur].append(line)
    return out


def files_from(lines: list) -> list:
    paths = []
    for l in lines:
        s = l.strip().lstrip("-*• ").strip()
        if not s or s.startswith(("(", "#")):
            continue
        s = s.split("(")[0].split("—")[0].split(" - ")[0].strip().strip("`").strip()
        if s and " " not in s and "/" in s or s.endswith((".py", ".ts", ".tsx", ".js", ".swift", ".kt", ".rules", ".md", ".json", ".yml", ".yaml", ".sql")):
            paths.append(s.rstrip(","))
    return paths


def check(text: str, worktree: str | None) -> dict:
    sec = parse(text)
    errors, warnings = [], []
    missing = [h for h in HEADERS if h not in sec]
    if missing:
        errors.append(f"missing sections: {', '.join(missing)}")
    lane = (sec.get("LANE") or [""])[0].split()[0].lower() if sec.get("LANE") and sec["LANE"][0].strip() else ""
    rung = (sec.get("REASONING") or [""])[0].split()[0].lower() if sec.get("REASONING") and sec["REASONING"][0].strip() else ""
    if lane and lane not in LANES:
        errors.append(f"LANE {lane!r} is not luna | sol | flash | pro")
    if lane in LANES and rung and rung not in LANES[lane]:
        errors.append(f"REASONING {rung!r} is not legal for {lane} (allowed: {', '.join(sorted(LANES[lane]))})")
    if "LANE" in sec and not lane:
        errors.append("LANE is empty")
    if "REASONING" in sec and not rung:
        errors.append("REASONING is empty")
    paths = files_from(sec.get("FILES") or [])
    if "FILES" in sec and not paths:
        errors.append("FILES names no paths")
    if worktree:
        wt = Path(worktree)
        for p in paths:
            q = wt / p
            if p.endswith("/") or q.is_dir():
                warnings.append(f"FILES entry {p!r} is a directory: the lane may touch anything under it")
            elif not q.exists() and not q.parent.exists():
                errors.append(f"FILES entry {p!r} does not exist and neither does its directory")
    else:
        for p in paths:
            if p.endswith("/"):
                warnings.append(f"FILES entry {p!r} is a directory: the lane may touch anything under it")
    verify = " ".join(l.strip() for l in (sec.get("VERIFY") or []) if l.strip()).strip("` ")
    if "VERIFY" in sec and not verify:
        errors.append("VERIFY is empty: the report would carry no evidence")
    if verify and FILTER_RX.search(verify):
        warnings.append("VERIFY is piped through a filter or an || fallback; its exit status may be masked (s2-flow-fix hid an xcodebuild failure behind grep)")
    if "CONSTRAINTS" in sec and not any(l.strip() for l in sec["CONSTRAINTS"]):
        warnings.append("CONSTRAINTS is empty: name the project laws that apply, or say 'none'")
    if "OBJECTIVE" in sec and len(" ".join(sec["OBJECTIVE"]).split()) < 6:
        warnings.append("OBJECTIVE is under six words")
    return {"ok": not errors, "errors": errors, "warnings": warnings, "lane": lane, "reasoning": rung, "files": paths, "verify": verify}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check")
    c.add_argument("spec", help="path to the spec file")
    c.add_argument("--worktree", help="resolve FILES against this checkout")
    c.add_argument("--json", action="store_true")
    a = ap.parse_args()
    text = Path(a.spec).read_text(errors="ignore")
    r = check(text, a.worktree)
    if a.json:
        print(json.dumps(r, indent=2))
    else:
        print(("ok" if r["ok"] else "REFUSED") + f"  lane={r['lane'] or '?'} rung={r['reasoning'] or '?'} files={len(r['files'])} verify={r['verify'][:60]!r}")
        for e in r["errors"]:
            print("  error:   " + e)
        for w in r["warnings"]:
            print("  warning: " + w)
    return 0 if r["ok"] else 2


if __name__ == "__main__":
    sys.exit(main())
