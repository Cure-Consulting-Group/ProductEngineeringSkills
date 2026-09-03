#!/usr/bin/env python3
"""lane-preflight: check that the Codex and Antigravity lanes can run before dispatching.

Checks, without spending quota:
  - codex binary present, version, logged in (`codex login status`)
  - agy binary present, Gemini and Claude/GPT pool percentages (`agy -p /usage`)
  - the target directory is under an Antigravity trusted workspace
  - a timeout binary (gtimeout or timeout) exists for wall-clock caps

Exit 0 when every requested lane is usable, 1 otherwise. Always prints JSON.
Python stdlib only.

Examples:
  python3 lane-preflight.py --dir "$PWD"
  python3 lane-preflight.py --dir ../wt/task-ro --lanes agy --min-gemini-weekly 20
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str], timeout: int = 30) -> tuple[int, str]:
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL)
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except FileNotFoundError:
        return 127, "not found"
    except subprocess.TimeoutExpired:
        return 124, "timeout"


def codex_trusted_projects() -> list[str]:
    cfg = Path.home() / ".codex" / "config.toml"
    if not cfg.exists():
        return []
    return re.findall(r'\[projects\."([^"]+)"\]\s*\n\s*trust_level\s*=\s*"trusted"', cfg.read_text(errors="ignore"))


def check_codex(target_dir: str | None = None) -> dict:
    out: dict = {"available": False, "logged_in": False, "version": None, "reasons": []}
    if target_dir:
        roots = codex_trusted_projects()
        ok, used = is_trusted(target_dir, roots)
        out["trusted"] = ok
        out["trusted_path_used"] = used
        if roots and not ok:
            out["reasons"].append(
                f"{target_dir} is not under any of the {len(roots)} Codex trusted projects; codex trusts the physical path form (e.g. /Volumes/CureVault/...), Antigravity the symlink form (~/CureVault/...). Pass -C with the physical path, or trust it via `codex` once interactively"
            )
    if not shutil.which("codex"):
        out["reasons"].append("codex binary not on PATH (install: https://learn.chatgpt.com/docs)")
        return out
    out["available"] = True
    rc, txt = run(["codex", "--version"])
    m = re.search(r"(\d+\.\d+\.\d+)", txt)
    out["version"] = m.group(1) if m else txt.strip()[:40]
    rc, txt = run(["codex", "login", "status"])
    out["logged_in"] = rc == 0 and "logged in" in txt.lower()
    if not out["logged_in"]:
        out["reasons"].append("codex not logged in: run `codex login`")
    # weekly limit percentage: Codex writes rate_limits into every session log's token_count events
    try:
        latest = None
        for f in sorted((Path.home() / ".codex" / "sessions").rglob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)[:5]:
            for line in f.read_text(errors="ignore").splitlines():
                if '"token_count"' in line and '"rate_limits"' in line:
                    latest = line
            if latest:
                break
        if latest:
            prim = (json.loads(latest).get("payload") or {}).get("rate_limits", {}).get("primary") or {}
            out["weekly_used_percent"] = prim.get("used_percent")
    except Exception:
        out["weekly_used_percent"] = None
    cfg = Path.home() / ".codex" / "config.toml"
    if cfg.exists():
        text = cfg.read_text(errors="ignore")
        if "danger-full-access" in text:
            out["reasons"].append("~/.codex/config.toml defaults to danger-full-access; lanes must pass -s explicitly (the hook enforces this)")
        if re.search(r"network_access\s*=\s*true", text):
            out["reasons"].append("~/.codex/config.toml enables network_access inside workspace-write; lanes and sandboxed VERIFY will have network")
    return out


def parse_usage(text: str) -> dict:
    pools: dict = {}
    for line in text.splitlines():
        parts = [p.strip() for p in line.split("\t")]
        if len(parts) >= 3 and parts[2].endswith("%"):
            pool, kind, pct = parts[0], parts[1], parts[2]
            key = "gemini" if pool.lower().startswith("gemini") else "claude_gpt"
            window = "weekly" if "weekly" in kind.lower() else "five_hour"
            try:
                pools.setdefault(key, {})[window] = int(pct.rstrip("%"))
            except ValueError:
                pass
            if len(parts) >= 4:
                pools[key][window + "_reset"] = parts[3]
    return pools


def trusted_workspaces() -> list[str]:
    p = Path.home() / ".gemini" / "antigravity-cli" / "settings.json"
    try:
        return list(json.loads(p.read_text()).get("trustedWorkspaces", []))
    except Exception:
        return []


def is_trusted(target: str, roots: list[str]) -> tuple[bool, str]:
    real = os.path.realpath(target)
    candidates = {target, real, os.path.abspath(target)}
    for root in roots:
        for c in candidates:
            if c == root or c.startswith(root.rstrip("/") + "/"):
                return True, c
    return False, real


def check_agy(target_dir: str | None, min_weekly: int) -> dict:
    out: dict = {"available": False, "pools": {}, "trusted": None, "reasons": []}
    if not shutil.which("agy"):
        out["reasons"].append("agy binary not on PATH (see https://antigravity.google/cli for the install steps)")
        return out
    out["available"] = True
    rc, txt = run(["agy", "-p", "/usage", "--output-format", "json"], timeout=60)
    try:
        resp = json.loads(txt.strip().splitlines()[-1]).get("response", "")
    except Exception:
        resp = txt
    if "not logged" in resp.lower() or rc != 0 and not resp:
        out["reasons"].append("agy not logged in: run `agy` once interactively to sign in")
    out["pools"] = parse_usage(resp)
    gem = out["pools"].get("gemini", {})
    if gem and gem.get("weekly", 100) < min_weekly:
        out["reasons"].append(f"Gemini weekly pool at {gem['weekly']}% (< {min_weekly}%); skip the Antigravity lane until reset {gem.get('weekly_reset', '')}")
    if target_dir:
        roots = trusted_workspaces()
        ok, used = is_trusted(target_dir, roots)
        out["trusted"] = ok
        out["trusted_path_used"] = used
        if not ok:
            out["reasons"].append(
                f"{target_dir} is not under any of the {len(roots)} Antigravity trusted workspaces; pass the trusted form of the path (e.g. ~/CureVault/... not /Volumes/CureVault/...) or add it in ~/.gemini/antigravity-cli/settings.json"
            )
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dir", help="worktree or repo path the lane will run against")
    ap.add_argument("--lanes", default="codex,agy", help="comma list of lanes to check: codex, agy (default both)")
    ap.add_argument("--min-gemini-weekly", type=int, default=15, help="skip agy below this weekly percent remaining (default 15)")
    ap.add_argument("--json", action="store_true", help="JSON output (always on; flag kept for convention)")
    args = ap.parse_args()

    lanes = {l.strip() for l in args.lanes.split(",") if l.strip()}
    result: dict = {"status": "ok", "reasons": []}
    t = shutil.which("gtimeout") or shutil.which("timeout")
    result["timeout_bin"] = t
    if not t:
        result["reasons"].append("no gtimeout/timeout binary; codex lanes run uncapped (brew install coreutils)")

    if "codex" in lanes:
        result["codex"] = check_codex(args.dir)
        if not (result["codex"]["available"] and result["codex"]["logged_in"]):
            result["status"] = "unavailable"
        result["reasons"] += [f"codex: {r}" for r in result["codex"]["reasons"]]
    if "agy" in lanes:
        result["agy"] = check_agy(args.dir, args.min_gemini_weekly)
        hard = [r for r in result["agy"]["reasons"] if "not on PATH" in r or "not logged" in r or "not under" in r or "skip the Antigravity" in r]
        if hard:
            result["status"] = "unavailable"
        result["reasons"] += [f"agy: {r}" for r in result["agy"]["reasons"]]

    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
