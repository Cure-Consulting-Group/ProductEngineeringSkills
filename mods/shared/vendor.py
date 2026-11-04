#!/usr/bin/env python3
"""Copy mods/shared/*.ts into the mods that use them (stdlib only).

A mod is installed as its own folder, so it cannot import from mods/shared/.
This script vendors each shared file into <mod>/hooks/shared/<file> with a
generated header. --check exits 1 when a copy differs from its source (CI).

usage: python3 mods/shared/vendor.py [--check] [--json]
"""
import argparse
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
MODS = HERE.parent
CONSUMERS = {
    'rules.ts': ['cure-policy-guard', 'cure-rules-band'],
    'git.ts': ['cure-lane-board', 'cure-lane-verifier'],
}


def header(name: str) -> str:
    return f'// GENERATED from mods/shared/{name} by mods/shared/vendor.py. Do not edit: edit the source and re-run.\n'


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--check', action='store_true', help='fail when a vendored copy differs from its source')
    ap.add_argument('--json', action='store_true', help='print the result as JSON')
    args = ap.parse_args()
    drift, written = [], []
    for name, mods in CONSUMERS.items():
        want = header(name) + (HERE / name).read_text()
        for mod in mods:
            dest = MODS / mod / 'hooks' / 'shared' / name
            have = dest.read_text() if dest.exists() else None
            if have == want:
                continue
            if args.check:
                drift.append(str(dest.relative_to(MODS.parent)))
            else:
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(want)
                written.append(str(dest.relative_to(MODS.parent)))
    if args.json:
        print(json.dumps({'drift': drift, 'written': written}))
    else:
        for p in drift:
            print(f'out of date: {p} (run python3 mods/shared/vendor.py)')
        for p in written:
            print(f'wrote {p}')
    return 1 if drift else 0


if __name__ == '__main__':
    sys.exit(main())
