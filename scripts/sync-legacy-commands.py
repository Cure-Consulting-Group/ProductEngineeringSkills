#!/usr/bin/env python3
"""
sync-legacy-commands.py — Regenerate the legacy claude-commands/ surface from
skills/ so the two can never drift.

A `claude-commands/<name>.md` file is simply a skill's body with the YAML
frontmatter removed. This tool derives every command from its SKILL.md, adds
any missing commands, and removes orphans (commands whose skill is gone).

Gemini `.skill` packages are regenerated separately by generate-gemini-skills.sh
(also derived from skills/); run that with --force on release.

--check (CI gate) exits 1 on any drift. --write regenerates. Stdlib only.
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
CMD_DIR = ROOT / "claude-commands"


def body_of(skill_md):
    text = skill_md.read_text(encoding="utf-8")
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            return parts[2].lstrip("\n")
    return text


def desired():
    """name -> command-file content, derived from each skill."""
    out = {}
    for p in sorted(SKILLS_DIR.rglob("SKILL.md")):
        out[p.parent.name] = body_of(p).rstrip() + "\n"
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--check", action="store_true", help="exit 1 if claude-commands/ drifts from skills/")
    g.add_argument("--write", action="store_true", help="regenerate claude-commands/ from skills/")
    args = ap.parse_args()

    want = desired()
    have = {p.stem: p for p in CMD_DIR.glob("*.md")} if CMD_DIR.exists() else {}

    add = [n for n in want if n not in have]
    orphan = [n for n in have if n not in want]
    changed = [n for n in want if n in have and have[n].read_text(encoding="utf-8") != want[n]]

    drift = add or orphan or changed
    if not drift:
        print(f"claude-commands/ in sync with {len(want)} skills. ✓")
        return

    if args.write:
        CMD_DIR.mkdir(exist_ok=True)
        for n in want:
            (CMD_DIR / f"{n}.md").write_text(want[n], encoding="utf-8")
        for n in orphan:
            have[n].unlink()
        print(f"Regenerated claude-commands/: +{len(add)} added, ~{len(changed)} updated, -{len(orphan)} removed.")
        if add:
            print("  added:   " + ", ".join(sorted(add)))
        if orphan:
            print("  removed: " + ", ".join(sorted(orphan)))
        return

    # --check
    print(f"DRIFT: +{len(add)} missing, ~{len(changed)} stale, -{len(orphan)} orphaned command(s).", file=sys.stderr)
    if add:
        print("  missing:  " + ", ".join(sorted(add)), file=sys.stderr)
    if orphan:
        print("  orphaned: " + ", ".join(sorted(orphan)), file=sys.stderr)
    print("Run `python3 scripts/sync-legacy-commands.py --write`.", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
