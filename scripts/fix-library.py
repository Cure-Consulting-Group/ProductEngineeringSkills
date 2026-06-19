#!/usr/bin/env python3
"""
fix-library.py — Systemic, idempotent auto-fixes for skills and agents,
bringing the library into line with the official Anthropic spec.

Skill fixes:
  - Remove inert `version:` / `compatibility:` frontmatter (not read by harness).
  - Add a sensible `argument-hint:` where missing.

Agent fixes:
  - Drop preload `skills:` references to skills that don't exist (broken refs).
  - Right-size `skills:` preloads: keep author-ordered prefix while cumulative
    body stays <= MAX_PRELOAD_LINES and count <= MAX_PRELOAD_SKILLS; the rest
    remain invocable on demand via the Skill tool (per Anthropic guidance).

Run with --dry-run to preview, --apply to write. Re-running is a no-op.
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
AGENTS_DIR = ROOT / "agents"

MAX_PRELOAD_LINES = 1500
MAX_PRELOAD_SKILLS = 4

# Sensible argument-hints for the handful of skills missing one.
ARG_HINT_DEFAULTS = {
    "technical-blog-writer": "[topic-or-title]",
    "equity-research": "[company-or-ticker]",
    "comps-analysis": "[company-or-sector]",
    "merger-modeling": "[acquirer-and-target]",
    "dcf-modeling": "[company-or-ticker]",
}
ARG_HINT_FALLBACK = "[input]"


def skill_index():
    """name/dirname -> body line count."""
    idx = {}
    for p in SKILLS_DIR.rglob("SKILL.md"):
        txt = p.read_text(encoding="utf-8", errors="replace")
        body = txt.split("---", 2)[2] if txt.startswith("---") else txt
        lines = len(body.splitlines())
        m = re.search(r"^name:\s*(.+)$", txt, re.M)
        if m:
            idx[m.group(1).strip().strip('"').strip("'")] = lines
        idx[p.parent.name] = lines
    return idx


def split_fm(text):
    if not text.startswith("---"):
        return None, None, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None, None, text
    return parts[1], parts[2], text


def fix_skill(path, changes):
    text = path.read_text(encoding="utf-8")
    fm, body, _ = split_fm(text)
    if fm is None:
        return text, False
    lines = fm.splitlines()
    out, touched = [], False

    for ln in lines:
        if re.match(r"^\s*(version|compatibility)\s*:", ln):
            changes.append(f"{path.parent.name}: drop `{ln.split(':')[0].strip()}`")
            touched = True
            continue
        out.append(ln)

    has_hint = any(re.match(r"^\s*argument-hint\s*:", l) for l in out)
    if not has_hint:
        hint = ARG_HINT_DEFAULTS.get(path.parent.name, ARG_HINT_FALLBACK)
        # insert after description (or when_to_use if present), else end
        insert_at = len(out)
        for i, l in enumerate(out):
            if re.match(r"^\s*(when_to_use|description)\s*:", l):
                insert_at = i + 1
        out.insert(insert_at, f'argument-hint: "{hint}"')
        changes.append(f"{path.parent.name}: add argument-hint {hint}")
        touched = True

    if not touched:
        return text, False
    return rebuild(out, body), True


def rebuild(fm_lines, body):
    """Reassemble frontmatter + body without leading/trailing blank lines."""
    while fm_lines and fm_lines[0].strip() == "":
        fm_lines.pop(0)
    while fm_lines and fm_lines[-1].strip() == "":
        fm_lines.pop()
    return "---\n" + "\n".join(fm_lines) + "\n---" + body


def fix_agent(path, idx, changes):
    text = path.read_text(encoding="utf-8")
    fm, body, _ = split_fm(text)
    if fm is None:
        return text, False
    lines = fm.splitlines()
    out, touched = [], False

    for ln in lines:
        m = re.match(r"^(\s*skills\s*:\s*)(.+)$", ln)
        if not m:
            out.append(ln)
            continue
        prefix, raw = m.group(1), m.group(2)
        refs = [s.strip() for s in raw.split(",") if s.strip()]
        kept, cum, dropped_missing, dropped_size = [], 0, [], []
        for r in refs:
            if r not in idx:
                dropped_missing.append(r)
                continue
            if len(kept) >= MAX_PRELOAD_SKILLS or cum + idx[r] > MAX_PRELOAD_LINES:
                dropped_size.append(r)
                continue
            kept.append(r)
            cum += idx[r]
        if dropped_missing:
            changes.append(f"{path.stem}: drop broken preload refs {dropped_missing}")
            touched = True
        if dropped_size:
            changes.append(f"{path.stem}: right-size preload, defer {dropped_size} to on-demand (kept {cum} lines)")
            touched = True
        if kept != refs:
            out.append(f"{prefix}{', '.join(kept)}")
        else:
            out.append(ln)

    if not touched:
        return text, False
    return rebuild(out, body), True


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true", help="preview changes")
    g.add_argument("--apply", action="store_true", help="write changes")
    g.add_argument("--check", action="store_true", help="exit 1 if any fix is pending (CI gate)")
    args = ap.parse_args()

    idx = skill_index()
    changes = []

    for p in sorted(SKILLS_DIR.rglob("SKILL.md")):
        new, touched = fix_skill(p, changes)
        if touched and args.apply:
            p.write_text(new, encoding="utf-8")

    for p in sorted(AGENTS_DIR.glob("*.md")):
        new, touched = fix_agent(p, idx, changes)
        if touched and args.apply:
            p.write_text(new, encoding="utf-8")

    if not changes:
        print("Nothing to fix — library already compliant. ✓")
        return
    verb = "APPLIED" if args.apply else "PENDING"
    print(f"{verb} {len(changes)} fixes:\n")
    for c in changes:
        print(f"  - {c}")
    if args.dry_run:
        print("\nRe-run with --apply to write.")
    if args.check:
        print(f"\nFAIL: {len(changes)} compliance fixes pending. Run `python3 scripts/fix-library.py --apply`.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
