#!/usr/bin/env python3
"""Zero-model smoke test: does Antigravity (agy) list every skill and agent in the export?

Builds the flat plugin with scripts/export-antigravity.py (unless --plugin-dir is given), drops it
into a throwaway git workspace as `.agents/plugins/cure/`, and runs the two free slash commands
`agy -p "/skills"` and `agy -p "/agents"` with `--add-dir <workspace>` (headless agy has no
workspace without it). No model turn is spent. The plugin is not installed globally, but `agy` runs with your real HOME and may write its own session/log files under ~/.gemini.

Asserts: every exported skill appears as `cure:<name>`, every exported persona appears in
/agents. Skips cleanly (exit 0, status "skipped") when agy is not installed or not signed in,
which is the normal state on CI runners.

Usage:
  python3 scripts/antigravity-smoke.py
  python3 scripts/antigravity-smoke.py --json
  python3 scripts/antigravity-smoke.py --plugin-dir dist/antigravity/cure --keep

Exit codes: 0 pass or skipped, 1 skills/agents missing, 2 export failed or agy errored.
"""
import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def agy_slash(cmd: str, ws: Path) -> dict:
    # --mode plan --sandbox keep the cure-tri-lane guard hook satisfied; slash commands spend no model turn.
    argv = ["agy", "-p", cmd, "--add-dir", str(ws), "--mode", "plan", "--sandbox", "--output-format", "json"]
    p = subprocess.run(argv, cwd=str(ws), capture_output=True, text=True, timeout=180)
    lines = [l for l in p.stdout.splitlines() if l.strip().startswith("{")]
    if not lines:
        return {"status": "ERROR", "error": (p.stderr or p.stdout).strip()[-300:], "response": ""}
    return json.loads(lines[-1])


def main() -> int:
    ap = argparse.ArgumentParser(description="Zero-model Antigravity listing smoke test for the exported plugin.")
    ap.add_argument("--plugin-dir", help="use an existing export instead of building one")
    ap.add_argument("--keep", action="store_true", help="keep the throwaway workspace and print its path")
    ap.add_argument("--json", action="store_true", help="machine-readable result on stdout")
    a = ap.parse_args()
    result = {"status": "skipped", "reason": ""}

    def done(code: int) -> int:
        if a.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"antigravity smoke: {result['status']}" + (f" ({result['reason']})" if result.get("reason") else ""))
            for k in ("skills_expected", "skills_listed", "missing_skills", "agents_listed", "missing_agents", "agy_version"):
                if k in result:
                    print(f"  {k}: {result[k]}")
        return code

    if not shutil.which("agy"):
        result["reason"] = "agy not on PATH"
        return done(0)
    tmp = Path(tempfile.mkdtemp(prefix="agy-smoke-"))
    try:
        if a.plugin_dir:
            plugin = Path(a.plugin_dir).resolve()
        else:
            plugin = tmp / "export" / "cure"
            p = subprocess.run([sys.executable, str(REPO / "scripts" / "export-antigravity.py"), "--out", str(plugin), "--json"],
                               capture_output=True, text=True, timeout=300)
            if p.returncode != 0:
                result.update(status="error", reason="export failed: " + p.stderr.strip()[-300:])
                return done(2)
        ws = tmp / "ws"
        (ws / ".agents" / "plugins").mkdir(parents=True)
        shutil.copytree(plugin, ws / ".agents" / "plugins" / "cure")
        subprocess.run(["git", "init", "-q", str(ws)], check=True, timeout=30)
        result["agy_version"] = subprocess.run(["agy", "--version"], capture_output=True, text=True, timeout=30).stdout.strip()
        sk = agy_slash("/skills", ws)
        if sk.get("status") != "SUCCESS":
            err = str(sk.get("error", ""))
            if "auth" in err.lower():
                result["reason"] = "agy not signed in"
                return done(0)
            result.update(status="error", reason="agy /skills: " + err)
            return done(2)
        listed = {l.split("\t")[0] for l in sk.get("response", "").splitlines() if l.strip()}
        expected = sorted(d.name for d in (plugin / "skills").iterdir() if (d / "SKILL.md").exists())
        missing = [n for n in expected if f"cure:{n}" not in listed]
        ag = agy_slash("/agents", ws)
        agents = {l.strip() for l in ag.get("response", "").splitlines() if l.strip()}
        want_agents = sorted(d.name for d in (plugin / "agents").iterdir()) if (plugin / "agents").is_dir() else []
        missing_agents = [n for n in want_agents if n not in agents]
        result.update(status="pass" if not missing and not missing_agents else "fail",
                      skills_expected=len(expected), skills_listed=len(expected) - len(missing), missing_skills=missing,
                      agents_listed=len(want_agents) - len(missing_agents), missing_agents=missing_agents,
                      model_turns=sk.get("num_turns", 0) + ag.get("num_turns", 0))
        if a.keep:
            result["workspace"] = str(ws)
        return done(0 if result["status"] == "pass" else 1)
    except (OSError, ValueError, subprocess.SubprocessError) as e:
        result.update(status="error", reason=str(e)[:300])
        return done(2)
    finally:
        if not a.keep:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
