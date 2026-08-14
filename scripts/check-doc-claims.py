#!/usr/bin/env python3
"""check-doc-claims.py — Narrative drift detection for prose docs (T34).

The structured checks (sync-metadata, audit-library) verify counts and
frontmatter. This tool verifies the *prose*: every repo-relative file path a
top-level doc references must exist on disk. Catches the EVALUATION.md class
of drift — a doc confidently pointing at (or describing) a file that was
deleted or renamed, which no count check can see.

Checked docs: README.md, CLAUDE.md, GEMINI.md, AGENT-GUIDE.md, docs/*.md.
Checked claims:
  1. Markdown links to local .md/.py/.sh/.json files -> target must exist.
  2. Backtick-quoted repo paths (`scripts/x.py`, `docs/X.md`, dir trees) -> must exist.

Stdlib only. Exit 0 = clean, 1 = drift found.

Usage:
  python3 scripts/check-doc-claims.py            # human output
  python3 scripts/check-doc-claims.py --json     # machine output
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DOCS = sorted(
    [p for p in [ROOT / n for n in ("README.md", "CLAUDE.md", "GEMINI.md", "AGENT-GUIDE.md")] if p.exists()]
    + sorted((ROOT / "docs").glob("*.md"))
)

# Repo-relative path shapes we treat as verifiable claims.
PATH_RE = re.compile(
    r"`([A-Za-z0-9_./ -]+\.(?:md|py|sh|json|yml|yaml))`"  # backticked file
    r"|\]\(((?!https?://|#)[^)]+\.md)\)"                   # local md link
)

# Paths that are templates/examples, not claims about this repo.
IGNORE_RE = re.compile(
    r"[{<*]"                       # globs/placeholders: {name}, <path>, *
    r"|^(dist|node_modules|~)/"    # generated or external
    r"|^(\.claude|\.agents|\.gemini)/"  # consuming-project conventions, not this repo
    r"|^(path|your|my|some|target|workspace)[-_/]"  # obvious examples
    r"|foo|bar[._/]|baz"           # placeholder names
    r"|\.example$"
)


def check():
    findings = []
    for doc in DOCS:
        text = doc.read_text(encoding="utf-8", errors="replace")
        in_code = False
        for lineno, line in enumerate(text.splitlines(), 1):
            if line.strip().startswith("```"):
                in_code = not in_code
                continue
            for m in PATH_RE.finditer(line):
                raw = (m.group(1) or m.group(2)).strip()
                # command strings like `python3 scripts/x.py` -> keep the path token
                if " " in raw:
                    raw = raw.split()[-1]
                # bare filenames (no '/') usually describe files in OTHER
                # repos (a consuming project's CLAUDE.md, AGENTS.md, ...);
                # only repo-relative paths are verifiable claims here.
                if "/" not in raw or IGNORE_RE.search(raw):
                    continue
                # resolve relative to repo root, then to the doc's dir
                if not ((ROOT / raw).exists() or (doc.parent / raw).exists()):
                    findings.append({
                        "doc": str(doc.relative_to(ROOT)),
                        "line": lineno,
                        "claim": raw,
                    })
    return findings


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()

    findings = check()
    if args.json:
        print(json.dumps({"drift": findings, "count": len(findings)}, indent=2))
    else:
        if findings:
            print(f"❌ {len(findings)} dead doc reference(s):")
            for f in findings:
                print(f"  {f['doc']}:{f['line']}  ->  {f['claim']}")
        else:
            print(f"✅ doc claims clean across {len(DOCS)} docs")
    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
