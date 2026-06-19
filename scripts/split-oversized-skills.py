#!/usr/bin/env python3
"""
split-oversized-skills.py — Bring SKILL.md bodies under the 500-line limit via
progressive disclosure, content-preserving.

For each oversized skill, the largest *reference-type* H2 sections are MOVED
(not rewritten) into a sibling `reference/details.md` (one level deep, with a
table of contents), and replaced in SKILL.md by a one-line pointer. Core
sections (intro/pre-processing and the code-generation/output block) are never
moved, so the skill's workflow and deliverables stay inline.

--list shows what would move. --apply performs it. --check fails if any skill
body still exceeds the limit (CI gate). Stdlib only. Reversible via git.
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
LIMIT = 500
# Sections that must stay inline (core to running the skill / its output).
KEEP_INLINE = re.compile(r"code generation|output format|required output|"
                         r"deliverable|pre-processing|classify", re.I)


def sections(body_lines):
    """Return list of (start, end, title) for each top-level ## section."""
    heads = [i for i, l in enumerate(body_lines) if re.match(r"^##[^#]", l)]
    secs = []
    for j, h in enumerate(heads):
        end = heads[j + 1] if j + 1 < len(heads) else len(body_lines)
        title = body_lines[h].lstrip("#").strip()
        secs.append((h, end, title))
    return secs


def plan(path):
    text = path.read_text(encoding="utf-8")
    fm, body = "", text
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            fm, body = parts[1], parts[2]
    body_lines = body.splitlines(keepends=True)
    total = len(body_lines)
    if total <= LIMIT:
        return None
    secs = sections(body_lines)
    # Candidates: skip the first section; never move core/output sections.
    cand = [(s, e, t) for (s, e, t) in secs[1:] if not KEEP_INLINE.search(t)]
    cand.sort(key=lambda x: (x[1] - x[0]), reverse=True)
    chosen, projected = [], total
    for s, e, t in cand:
        if projected <= LIMIT:
            break
        chosen.append((s, e, t))
        projected -= (e - s) - 3  # section replaced by ~3-line pointer
    chosen.sort()  # restore document order
    return {"fm": fm, "body_lines": body_lines, "total": total,
            "projected": projected, "chosen": chosen}


def apply(path, p):
    refdir = path.parent / "reference"
    refdir.mkdir(exist_ok=True)
    body_lines = p["body_lines"]
    name = path.parent.name

    # Build the reference file from chosen sections (in order).
    blocks, toc = [], []
    for s, e, t in p["chosen"]:
        toc.append(f"- {t}")
        blocks.append("".join(body_lines[s:e]).rstrip() + "\n")
    ref = (f"# {name}: detailed reference\n\n"
           f"> Reference material for the `{name}` skill, split out for "
           f"progressive disclosure. Loaded on demand from SKILL.md.\n\n"
           f"## Contents\n" + "\n".join(toc) + "\n\n" + "\n".join(blocks))
    (refdir / "details.md").write_text(ref, encoding="utf-8")

    # Replace chosen sections in the body with pointers (high index first).
    for s, e, t in sorted(p["chosen"], reverse=True):
        ptr = [f"## {t}\n", "\n",
               f"See [reference/details.md](reference/details.md) "
               f"(section “{t}”) for full detail.\n", "\n"]
        body_lines[s:e] = ptr

    new_body = "".join(body_lines)
    out = f"---{p['fm']}---{new_body}" if p["fm"] else new_body
    path.write_text(out, encoding="utf-8")
    return len("".join(body_lines).splitlines())


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--list", action="store_true")
    g.add_argument("--apply", action="store_true")
    g.add_argument("--check", action="store_true", help="exit 1 if any body > limit")
    args = ap.parse_args()

    over = []
    for path in sorted(SKILLS_DIR.rglob("SKILL.md")):
        p = plan(path)
        if p:
            over.append((path, p))

    if args.check:
        if over:
            print(f"FAIL: {len(over)} skill bodies exceed {LIMIT} lines.", file=sys.stderr)
            for path, p in over:
                print(f"  {path.parent.name}: {p['total']}", file=sys.stderr)
            sys.exit(1)
        print(f"All skill bodies within {LIMIT} lines. ✓")
        return

    if not over:
        print(f"All skill bodies within {LIMIT} lines. ✓")
        return

    for path, p in over:
        n = len(p["chosen"])
        moved = sum((e - s) for s, e, _ in p["chosen"])
        msg = f"{path.parent.name}: {p['total']} -> ~{p['projected']} lines (move {n} sections, {moved} lines)"
        if p["projected"] > LIMIT:
            msg += "  [still over — only non-core sections moved]"
        if args.apply:
            actual = apply(path, p)
            msg = f"{path.parent.name}: {p['total']} -> {actual} lines ({n} sections -> reference/details.md)"
        print("  " + msg)
    print(f"\n{'Applied' if args.apply else 'Would move'} splits for {len(over)} skills.")


if __name__ == "__main__":
    main()
