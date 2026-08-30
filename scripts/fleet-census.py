#!/usr/bin/env python3
"""fleet-census.py — Consuming-project census + manifest tool (T31).

Answers, per project: how is the library installed, which version, has the
vendored copy drifted, what local skills exist, and is there a double-install
risk (vendored tree AND plugin instructions in CLAUDE.md).

Manifest: .claude/cure-manifest.json
  {
    "library": "cure-product-engineering",
    "version":  "<library version at install>",
    "mode":     "plugin" | "vendored" | "hybrid" | "none",
    "channel":  "stable" | "next",
    "installed": "<ISO date>",
    "local_skills": ["..."]        # project-owned, never flagged as drift
  }

Usage:
  python3 scripts/fleet-census.py --projects-dir ~/Documents/Cure-Consulting-Group
  python3 scripts/fleet-census.py --projects-dir DIR --json
  python3 scripts/fleet-census.py --write-manifest PROJ --mode plugin --channel next

Stdlib only. Exit 1 (census mode) if any drift/double-install found.
"""

import argparse
import hashlib
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGIN = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text())
LIB_VERSION = PLUGIN["version"]

SKIP_DIRS = {"ProductEngineeringSkills", "docs", "tools"}

PLUGIN_CACHE = Path.home() / ".claude" / "plugins" / "cache" / "cure" / "cure-product-engineering"
FLEET_CACHE = Path.home() / ".cure" / "telemetry" / "fleet-last.json"


def installed_plugin_version():
    """Highest version present in the local plugin cache — the version Claude
    Code actually SERVES. None if the plugin isn't installed on this machine."""
    if not PLUGIN_CACHE.exists():
        return None
    def key(v):
        try:
            return tuple(int(x) for x in v.split("."))
        except ValueError:
            return (0,)
    versions = [d.name for d in PLUGIN_CACHE.iterdir() if d.is_dir()]
    return max(versions, key=key) if versions else None


def library_skills():
    return {p.parent.name: p for p in (ROOT / "skills").rglob("SKILL.md")}


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def census_project(proj, lib):
    claude = proj / ".claude"
    manifest_path = claude / "cure-manifest.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else None

    vend_dir = claude / "skills"
    vendored, drifted, local = [], [], []
    if vend_dir.exists():
        for d in sorted(vend_dir.iterdir()):
            sm = d / "SKILL.md"
            if not sm.exists():
                continue
            if d.name in lib:
                vendored.append(d.name)
                if sha(sm) != sha(lib[d.name]):
                    drifted.append(d.name)
            else:
                local.append(d.name)

    claude_md = proj / "CLAUDE.md"
    mentions_plugin = claude_md.exists() and "plugin install" in claude_md.read_text(errors="replace")
    double_install = bool(vendored) and mentions_plugin

    mode = manifest["mode"] if manifest else ("vendored" if vendored else ("plugin" if mentions_plugin else "none"))
    return {
        "project": proj.name,
        "mode": mode,
        "manifest": bool(manifest),
        "manifest_version": manifest.get("version") if manifest else None,
        "channel": manifest.get("channel", "stable") if manifest else "stable",
        "current_library": LIB_VERSION,
        "vendored_count": len(vendored),
        "drifted_count": len(drifted),
        "drifted": drifted[:10],
        "local_skills": local,
        "double_install": double_install,
    }


def write_manifest(proj, mode, channel, lib):
    claude = proj / ".claude"
    claude.mkdir(exist_ok=True)
    vend_dir = claude / "skills"
    local = []
    if vend_dir.exists():
        local = sorted(d.name for d in vend_dir.iterdir()
                       if (d / "SKILL.md").exists() and d.name not in lib)
    # Record FACT, not intent: the version is what the plugin cache actually
    # serves, never the library checkout's HEAD. A manifest that records
    # aspiration poisons every canary run that trusts it (learned 2026-08-14:
    # first canary hard-stopped on exactly this mismatch).
    installed_v = installed_plugin_version()
    manifest = {
        "library": "cure-product-engineering",
        "version": installed_v or LIB_VERSION,
        "version_source": "plugin-cache" if installed_v else "library-checkout (UNVERIFIED — plugin not in cache)",
        "mode": mode,
        "channel": channel,
        "installed": date.today().isoformat(),
        "local_skills": local,
    }
    (claude / "cure-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--projects-dir", type=Path, help="directory of project checkouts")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--write-manifest", type=Path, metavar="PROJ", help="write cure-manifest.json into PROJ")
    ap.add_argument("--mode", choices=["plugin", "vendored", "hybrid", "none"], default="plugin")
    ap.add_argument("--channel", choices=["stable", "next"], default="stable")
    args = ap.parse_args()

    lib = library_skills()

    if args.write_manifest:
        m = write_manifest(args.write_manifest.expanduser().resolve(), args.mode, args.channel, lib)
        print(json.dumps(m, indent=2))
        return 0

    if not args.projects_dir:
        print("need --projects-dir or --write-manifest"); return 2
    base = args.projects_dir.expanduser().resolve()
    rows = [census_project(p, lib) for p in sorted(base.iterdir())
            if p.is_dir() and p.name not in SKIP_DIRS and (p / ".git").exists()
            and ((p / ".claude").exists() or (p / "CLAUDE.md").exists())]

    problems = [r for r in rows if r["drifted_count"] or r["double_install"]
                or (r["manifest"] and r["manifest_version"] != LIB_VERSION)]

    # SCORECARD's Fleet row reads this cache. Nothing wrote it, so the row was
    # frozen at whatever ran last (v7.4.4, 2026-08-14) and silently survived
    # every census since — a metric that cannot move is worse than "no data".
    try:
        FLEET_CACHE.parent.mkdir(parents=True, exist_ok=True)
        FLEET_CACHE.write_text(json.dumps(
            {"library_version": LIB_VERSION, "projects": rows,
             "problems": len(problems)}, indent=2) + "\n")
    except OSError:
        pass  # never fail a census over its own cache

    if args.json:
        print(json.dumps({"library_version": LIB_VERSION, "projects": rows,
                          "problems": len(problems)}, indent=2))
    else:
        inst = installed_plugin_version()
        print(f"library checkout v{LIB_VERSION} | plugin cache serves v{inst or 'NOT INSTALLED'}\n")
        print(f"{'project':<28}{'mode':<10}{'chan':<7}{'manifest':<10}{'vendored':<10}{'drift':<7}{'local':<7}{'2x-install'}")
        for r in rows:
            print(f"{r['project']:<28}{r['mode']:<10}{r['channel']:<7}"
                  f"{(r['manifest_version'] or '—'):<10}{r['vendored_count']:<10}"
                  f"{r['drifted_count']:<7}{len(r['local_skills']):<7}"
                  f"{'⚠️ YES' if r['double_install'] else 'no'}")
        if problems:
            print(f"\n❌ {len(problems)} project(s) with drift/double-install/version-lag")
    return 1 if problems else 0


if __name__ == "__main__":
    main()
