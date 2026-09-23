#!/usr/bin/env python3
"""
codex-smoke.py — zero-model Codex install smoke test for the Cure skill library.

Installs the plugin from this checkout into a THROWAWAY CODEX_HOME (never
~/.codex), renders the model-visible prompt with `codex debug prompt-input`
(no model call, no auth needed), and asserts:

  1. every skill in skills/**/SKILL.md is listed as cure-product-engineering:<name>,
     except skills whose agents/openai.yaml sets allow_implicit_invocation: false;
  2. those hidden skills are absent from the listing (Codex's equivalent of
     Claude's disable-model-invocation — see scripts/sync-metadata.py);
  3. nothing is silently dropped (Codex 0.155 drops a skill with invalid YAML
     frontmatter without any warning);
  4. .codex-plugin/plugin.json fences off hooks/hooks.json with an inline hooks
     object. An empty array does NOT fence (MEASURED on 0.155.0: Codex treats
     `"hooks": []` as undefined and falls back to hooks/hooks.json).

Exit 0 = pass, 1 = assertion failure, 2 = codex/tooling error.
Exits 0 with a SKIP message when `codex` is not on PATH (CI runners).

Stdlib only. Usage:
  python3 scripts/codex-smoke.py            # human output
  python3 scripts/codex-smoke.py --json     # machine output
  python3 scripts/codex-smoke.py --keep     # keep the temp CODEX_HOME for inspection
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGIN = "cure-product-engineering"
MARKETPLACE = "cure"
NAME = re.compile(r"^name:\s*['\"]?([^'\"\n]+?)['\"]?\s*$", re.M)
NO_IMPLICIT = re.compile(r"allow_implicit_invocation:\s*false\b")


def expected_skills(root):
    listed, hidden, unnamed = set(), set(), []
    for skill in sorted((root / "skills").rglob("SKILL.md")):
        text = skill.read_text(encoding="utf-8", errors="replace")
        fm = text[3:text.find("\n---", 3)] if text.startswith("---") else ""
        m = NAME.search(fm)
        if not m:
            unnamed.append(str(skill.relative_to(root)))
            continue
        sidecar = skill.parent / "agents" / "openai.yaml"
        if sidecar.exists() and NO_IMPLICIT.search(sidecar.read_text(encoding="utf-8")):
            hidden.add(m.group(1))
        else:
            listed.add(m.group(1))
    return listed, hidden, unnamed


def hooks_fenced(root):
    manifest = root / ".codex-plugin" / "plugin.json"
    if not manifest.exists():
        return False, ".codex-plugin/plugin.json missing"
    hooks = json.loads(manifest.read_text(encoding="utf-8")).get("hooks", None)
    if hooks is None:
        return False, "no `hooks` key: Codex auto-loads hooks/hooks.json (Claude-only hooks)"
    if hooks == [] or hooks == "":
        return False, "`hooks` is empty: Codex treats it as undefined and loads hooks/hooks.json"
    return True, f"hooks = {json.dumps(hooks)}"


def run(cmd, env, cwd, timeout=180):
    return subprocess.run(cmd, env=env, cwd=cwd, capture_output=True, text=True, timeout=timeout)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", action="store_true", help="print a JSON report")
    ap.add_argument("--keep", action="store_true", help="keep the temporary CODEX_HOME and print its path")
    ap.add_argument("--codex", default="codex", help="codex binary (default: codex on PATH)")
    args = ap.parse_args()

    codex = shutil.which(args.codex)
    if not codex:
        msg = "SKIP: codex CLI not installed; Codex smoke test not run."
        print(json.dumps({"status": "skip", "reason": msg}) if args.json else msg)
        return 0

    report = {"status": "fail", "codex": None, "listed": 0, "expected": 0,
              "dropped": [], "unexpected": [], "hidden_leaked": [], "hooks": None, "errors": []}
    listed_want, hidden, unnamed = expected_skills(ROOT)
    report["expected"] = len(listed_want)
    report["hidden"] = sorted(hidden)
    if unnamed:
        report["errors"].append(f"SKILL.md without a frontmatter name: {unnamed}")

    fenced, why = hooks_fenced(ROOT)
    report["hooks"] = why
    if not fenced:
        report["errors"].append(f"hooks not fenced: {why}")

    home = Path(tempfile.mkdtemp(prefix="cure-codex-home-"))
    work = Path(tempfile.mkdtemp(prefix="cure-codex-cwd-"))
    env = dict(os.environ, CODEX_HOME=str(home))
    rc = 1
    try:
        report["codex"] = run([codex, "--version"], env, work).stdout.strip()
        steps = [
            [codex, "plugin", "marketplace", "add", str(ROOT)],
            [codex, "plugin", "add", f"{PLUGIN}@{MARKETPLACE}"],
        ]
        for cmd in steps:
            r = run(cmd, env, work)
            if r.returncode != 0:
                report["errors"].append(f"`{' '.join(cmd[1:])}` failed: {(r.stderr or r.stdout).strip()[:400]}")
                rc = 2
                raise RuntimeError
        r = run([codex, "debug", "prompt-input"], env, work)
        if r.returncode != 0:
            report["errors"].append(f"`debug prompt-input` failed: {r.stderr.strip()[:400]}")
            rc = 2
            raise RuntimeError
        items = json.loads(r.stdout)
        text = "\n".join(c.get("text", "") for it in items for c in it.get("content", []) if isinstance(c, dict))
        got = set(re.findall(rf"^- {re.escape(PLUGIN)}:([a-z0-9-]+):", text, re.M))
        report["listed"] = len(got)
        report["dropped"] = sorted(listed_want - got)
        report["unexpected"] = sorted(got - listed_want - hidden)
        report["hidden_leaked"] = sorted(got & hidden)
        ok = not (report["dropped"] or report["unexpected"] or report["hidden_leaked"] or report["errors"])
        report["status"] = "pass" if ok else "fail"
        rc = 0 if ok else 1
    except RuntimeError:
        pass
    except (subprocess.TimeoutExpired, json.JSONDecodeError) as e:
        report["errors"].append(f"{type(e).__name__}: {e}")
        rc = 2
    finally:
        shutil.rmtree(work, ignore_errors=True)
        if args.keep:
            report["codex_home"] = str(home)
        else:
            shutil.rmtree(home, ignore_errors=True)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"{report['codex']}: {report['listed']} listed / {report['expected']} expected "
              f"(+{len(hidden)} hidden by agents/openai.yaml: {', '.join(sorted(hidden)) or 'none'})")
        print(f"hooks: {report['hooks']}")
        for key in ("dropped", "unexpected", "hidden_leaked"):
            if report[key]:
                print(f"  {key}: {', '.join(report[key])}")
        for e in report["errors"]:
            print(f"  error: {e}")
        if args.keep:
            print(f"CODEX_HOME kept at {home}")
        print("PASS" if rc == 0 else "FAIL")
    return rc


if __name__ == "__main__":
    sys.exit(main())
