#!/usr/bin/env python3
"""
sync-metadata.py — Single source of truth for library counts and version.

The library's counts (skills, agents, personas, rules, output-styles) and its
version are repeated across many docs and configs. They drift. This tool
derives the truth ONCE from the filesystem + .claude-plugin/plugin.json and
either verifies (--check, for CI) or rewrites (--write) the hardcoded values.

Truth sources:
  - version  : .claude-plugin/plugin.json  ["version"]   (authoritative)
  - counts   : the filesystem              (skills/, agents/, ...)

Stdlib only. --help / --check / --write / --json.
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def truth():
    plugin = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text())
    version = plugin["version"]
    skills = sorted((ROOT / "skills").rglob("SKILL.md"))
    by_domain = {}
    for p in skills:
        dom = p.relative_to(ROOT / "skills").parts[0]
        by_domain[dom] = by_domain.get(dom, 0) + 1
    return {
        "version": version,
        "skills": len(skills),
        "agents": len(list((ROOT / "agents").glob("*.md"))),
        "personas": len(list((ROOT / "personas").glob("*.md"))),
        "rules": len(list((ROOT / "rules").glob("*.md"))),
        "output_styles": len([d for d in (ROOT / "output-styles").iterdir() if d.is_dir()]),
        "domains": dict(sorted(by_domain.items())),
    }


def build_rules(t):
    """List of (path, compiled_regex, replacement, label). Idempotent.

    Two tiers to avoid clobbering legitimate sub-counts:
      - CONFIG files: a count always means the library total → blanket replace.
      - PROSE files: only replace explicit total-count IDIOMS, never bare
        "N skills" (which may be a domain sub-count like "engineering (39)").
    """
    v = t["version"]
    sk, ag, pe = t["skills"], t["agents"], t["personas"]
    rules = []

    # --- Version: plugin-version mentions only (parenthetical or trailing) ---
    for rel in ["hooks/hooks.json", "CLAUDE.md", "README.md", ".claude-plugin/marketplace.json"]:
        rules.append((rel, re.compile(r"\(v\d+\.\d+\.\d+\)"), f"(v{v})", "version (parenthetical)"))
        rules.append((rel, re.compile(r"\bv\d+\.\d+\.\d+\b(?=\s*[\)\.—,])"), f"v{v}", "version token"))

    # --- CONFIG files: count = total, safe to blanket-replace ---
    for rel in ["hooks/hooks.json", ".claude-plugin/marketplace.json",
                ".claude-plugin/plugin.json", "package.json"]:
        rules.append((rel, re.compile(r"\b\d+(?=\s+(?:production-grade\s+)?skills\b)"), str(sk), "skill count"))
        rules.append((rel, re.compile(r"\b\d+(?=\s+(?:custom\s+)?agents\b)"), str(ag), "agent count"))
        rules.append((rel, re.compile(r"\b\d+(?=\s+personas\b)"), str(pe), "persona count"))

    # --- PROSE files: total-count idioms only (never bare "N skills") ---
    for rel in ["CLAUDE.md", "README.md", "docs/OVERVIEW.md"]:
        # "75 production-grade skills", "80 skills (domain-organized)", "library — 80 skills"
        rules.append((rel, re.compile(r"\b\d+(?=\s+production-grade\s+skills\b)"), str(sk), "total skills idiom"))
        rules.append((rel, re.compile(r"\b\d+(?=\s+skills\s+\(domain-organized\))"), str(sk), "total skills idiom"))
        rules.append((rel, re.compile(r"\b\d+(?=\s+skills\s+\(organized into)"), str(sk), "total skills idiom"))
        rules.append((rel, re.compile(r"(?<=library — )\d+(?=\s+skills)"), str(sk), "total skills idiom"))
        rules.append((rel, re.compile(r"(?<=library - )\d+(?=\s+skills)"), str(sk), "total skills idiom"))
        # "39 custom agents", "39 specialized subagents", "39 agents," in inventory lines
        rules.append((rel, re.compile(r"\b\d+(?=\s+custom\s+agents\b)"), str(ag), "total agents idiom"))
        rules.append((rel, re.compile(r"\b\d+(?=\s+specialized\s+subagents\b)"), str(ag), "total agents idiom"))

    return rules


def apply_rules(t, write):
    rules = build_rules(t)
    changes = {}
    for rel, pat, repl, label in rules:
        path = ROOT / rel
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        new = pat.sub(repl, text)
        if new != text:
            changes.setdefault(rel, []).append(label)
            if write:
                path.write_text(new, encoding="utf-8")
    return changes


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--check", action="store_true", help="exit 1 if any file drifts from truth (CI gate)")
    g.add_argument("--write", action="store_true", help="rewrite hardcoded counts/version to match truth")
    ap.add_argument("--json", action="store_true", help="print the computed truth as JSON")
    args = ap.parse_args()

    t = truth()
    if args.json:
        print(json.dumps(t, indent=2)); return

    print(f"Truth: v{t['version']} | {t['skills']} skills | {t['agents']} agents | "
          f"{t['personas']} personas | {t['rules']} rules | {t['output_styles']} output-styles")
    print(f"Domains: " + ", ".join(f"{k} ({v})" for k, v in t['domains'].items()))

    changes = apply_rules(t, write=args.write)
    if not changes:
        print("\nAll metadata in sync. ✓")
        return
    verb = "Rewrote" if args.write else "DRIFT in"
    print(f"\n{verb}:")
    for rel, labels in changes.items():
        print(f"  {rel}: {', '.join(sorted(set(labels)))}")
    if args.check:
        print("\nFAIL: metadata drift. Run `python3 scripts/sync-metadata.py --write`.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
