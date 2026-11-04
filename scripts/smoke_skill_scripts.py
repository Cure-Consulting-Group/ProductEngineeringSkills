#!/usr/bin/env python3
"""Run every bundled skill script past --help, using the `Smoke:` line in its docstring (T88).

Each script under skills/*/*/scripts/*.py declares, in its module docstring, one of:

    Smoke: <arguments>                 run the script with these arguments
    Smoke: none (<reason>)             no safe offline invocation exists; the reason is required
    Smoke-exits: 0,2  (<why>)          optional; exit codes that count as a pass (default 0,1)

Path placeholders in the arguments (the one convention for every script):

    {skill}     the skill's folder              skills/<domain>/<name>
    {fixtures}  the script's fixtures folder    skills/<domain>/<name>/scripts/fixtures
    {tmp}       a fresh temporary folder, removed afterwards
    {repo}      the repository root

A run passes when it exits with an allowed code within the timeout, prints no Python traceback,
and, when the arguments include --json, prints valid JSON on stdout. Exit 1 is a findings result
by the scripts convention (docs/SCRIPTS_CONVENTION.md) and passes by default.

Usage:
    python3 scripts/smoke_skill_scripts.py            # every script
    python3 scripts/smoke_skill_scripts.py --json     # machine-readable results
    python3 scripts/smoke_skill_scripts.py --only wcag_check.py

Exit: 0 all pass, 1 any failure, 2 bad input.
"""
import argparse
import ast
import json
import os
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def declared(path: Path):
    """(args | None for 'none', reason, allowed exit codes) from the docstring, or an error string."""
    try:
        doc = ast.get_docstring(ast.parse(path.read_text(encoding="utf-8"))) or ""
    except (OSError, SyntaxError) as err:
        return f"cannot parse: {err}"
    smoke = [line[len("Smoke:"):].strip() for line in doc.splitlines() if line.startswith("Smoke:")]
    exits = [line[len("Smoke-exits:"):].strip() for line in doc.splitlines() if line.startswith("Smoke-exits:")]
    if len(smoke) != 1:
        return "no `Smoke:` line in the module docstring" if not smoke else "more than one `Smoke:` line"
    allowed = {0, 1}
    if exits:
        try:
            allowed = {int(x) for x in exits[0].split()[0].split(",")}
        except ValueError:
            return f"unreadable Smoke-exits: {exits[0]}"
    if smoke[0].startswith("none"):
        reason = smoke[0][4:].strip(" ()")
        return (None, reason, allowed) if reason else "`Smoke: none` needs a reason in parentheses"
    return smoke[0], "", allowed


def run_one(path: Path, timeout: int) -> dict:
    rel = str(path.relative_to(REPO))
    d = declared(path)
    if isinstance(d, str):
        return {"script": rel, "status": "fail", "detail": d}
    args, reason, allowed = d
    if args is None:
        return {"script": rel, "status": "declared-none", "detail": reason}
    with tempfile.TemporaryDirectory(prefix="cure-smoke-") as tmp:
        subs = {"{skill}": str(path.parent.parent), "{fixtures}": str(path.parent / "fixtures"), "{tmp}": tmp, "{repo}": str(REPO)}
        argv = []
        for tok in shlex.split(args):
            for k, v in subs.items():
                tok = tok.replace(k, v)
            argv.append(tok)
        try:
            p = subprocess.run([sys.executable, str(path), *argv], cwd=REPO, capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            return {"script": rel, "status": "fail", "detail": f"timed out after {timeout}s", "args": args}
    problems = []
    if p.returncode not in allowed:
        problems.append(f"exit {p.returncode} (allowed {','.join(map(str, sorted(allowed)))})")
    if "Traceback (most recent call last)" in p.stdout + p.stderr:
        problems.append("traceback")
    if "--json" in argv:
        try:
            json.loads(p.stdout)
        except ValueError:
            problems.append("--json output is not valid JSON")
    detail = "; ".join(problems) or f"exit {p.returncode}"
    if problems:
        tail = (p.stderr or p.stdout).strip().splitlines()[-3:]
        detail += (" | " + " / ".join(tail)) if tail else ""
    return {"script": rel, "status": "fail" if problems else "pass", "detail": detail, "args": args}


def main() -> int:
    ap = argparse.ArgumentParser(description="Run each skill script with its declared Smoke: arguments.")
    ap.add_argument("--json", action="store_true", help="print results as JSON")
    ap.add_argument("--only", help="run only scripts whose file name matches this")
    ap.add_argument("--timeout", type=int, default=90, help="seconds per script (default 90)")
    a = ap.parse_args()
    scripts = sorted(REPO.glob("skills/*/*/scripts/*.py"))
    if a.only:
        scripts = [s for s in scripts if s.name == a.only]
        if not scripts:
            print(f"error: no script named {a.only}", file=sys.stderr)
            return 2
    results = [run_one(s, a.timeout) for s in scripts]
    failed = [r for r in results if r["status"] == "fail"]
    if a.json:
        print(json.dumps({"results": results, "failed": len(failed)}, indent=2))
    else:
        for r in results:
            mark = {"pass": "ok   ", "declared-none": "none ", "fail": "FAIL "}[r["status"]]
            print(f"{mark} {r['script']}  {r['detail']}")
        ran = sum(r["status"] == "pass" for r in results)
        none = sum(r["status"] == "declared-none" for r in results)
        print(f"\nsmoke: {ran} passed, {len(failed)} failed, {none} declared none (of {len(results)})")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
