#!/usr/bin/env python3
"""Release gate for the Cure mods (stdlib only).

Checks, in order:
  1. every mods/<name>/ has a plugin.json, and the marketplace lists exactly those mods
  2. mods/shared/ copies are current (mods/shared/vendor.py --check)
  3. no retired model ID appears under mods/ or design/ (a line may opt out with
     the marker `retired-id-ok`)
  4. `claude plugin test` and `claude plugin validate --strict` pass for each mod
     (skipped with --no-claude, or when `claude` is not on PATH and --require-claude is unset)

Exits 1 on any failure. --json prints a machine-readable report.

usage: python3 mods/check.py [--no-claude] [--require-claude] [--json] [--max-mods N]
"""
import argparse
import json
import pathlib
import re
import shutil
import subprocess
import sys

MODS = pathlib.Path(__file__).resolve().parent
ROOT = MODS.parent
RETIRED_ID = re.compile(
    r'\b(?:claude-instant[\w.-]*|claude-2[\w.-]*|claude-3[\w.-]*|claude-(?:sonnet|opus|haiku)-4[\w.-]*'
    r'|gpt-3\.5[\w.-]*|gpt-4o[\w.-]*|gpt-4-turbo[\w.-]*|gpt-4\b|gemini-1\.\d[\w.-]*|gemini-2\.\d[\w.-]*)'
)
SCAN_SUFFIXES = {'.ts', '.tsx', '.js', '.json', '.md', '.html', '.py', '.sh', '.yml', '.yaml', '.txt'}


def mod_dirs():
    return sorted(p for p in MODS.iterdir() if (p / '.claude-plugin' / 'plugin.json').exists())


def check_marketplace(mods):
    market = json.loads((ROOT / '.claude-plugin' / 'marketplace.json').read_text())
    listed = {p['name']: p['source'] for p in market['plugins'] if str(p.get('source', '')).startswith('./mods/')}
    problems = []
    on_disk = {m.name for m in mods}
    for name in sorted(on_disk - set(listed)):
        problems.append(f'mods/{name} is not in .claude-plugin/marketplace.json')
    for name, src in sorted(listed.items()):
        if src != f'./mods/{name}' or name not in on_disk:
            problems.append(f'marketplace entry {name} -> {src} has no matching mods/ folder')
    return problems


def check_vendor():
    r = subprocess.run([sys.executable, str(MODS / 'shared' / 'vendor.py'), '--check'], capture_output=True, text=True)
    return [] if r.returncode == 0 else [line for line in r.stdout.splitlines() if line] or ['vendor.py --check failed']


def check_retired_ids():
    hits = []
    for base in (MODS, ROOT / 'design'):
        if not base.exists():
            continue
        for path in sorted(base.rglob('*')):
            if not path.is_file() or path.suffix not in SCAN_SUFFIXES or '/.claude-plugin/types/' in str(path):
                continue
            for n, line in enumerate(path.read_text(errors='replace').splitlines(), 1):
                if 'retired-id-ok' in line or path == pathlib.Path(__file__).resolve():
                    continue
                for m in RETIRED_ID.finditer(line):
                    hits.append(f'{path.relative_to(ROOT)}:{n}: retired model id {m.group(0)}')
    return hits


def run_claude(mods):
    results, problems = {}, []
    for mod in mods:
        rel = str(mod.relative_to(ROOT))
        test = subprocess.run(['claude', 'plugin', 'test', rel], cwd=ROOT, capture_output=True, text=True)
        val = subprocess.run(['claude', 'plugin', 'validate', '--strict', rel], cwd=ROOT, capture_output=True, text=True)
        out = test.stdout + test.stderr
        passed = re.search(r'(\d+) pass', out)
        failed = re.search(r'(\d+) fail', out)
        results[mod.name] = {
            'tests_pass': int(passed.group(1)) if passed else 0,
            'tests_fail': int(failed.group(1)) if failed else 0,
            'test_exit': test.returncode,
            'validate_exit': val.returncode,
        }
        if test.returncode != 0:
            problems.append(f'{rel}: claude plugin test failed\n' + out[-2000:])
        if val.returncode != 0:
            problems.append(f'{rel}: claude plugin validate --strict failed\n' + (val.stdout + val.stderr)[-2000:])
    return results, problems


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--no-claude', action='store_true', help='skip claude plugin test / validate')
    ap.add_argument('--require-claude', action='store_true', help='fail when claude is not on PATH')
    ap.add_argument('--max-mods', type=int, default=10, help='fail above this many mods (T73: 10)')
    ap.add_argument('--json', action='store_true', help='print a JSON report')
    args = ap.parse_args()

    mods = mod_dirs()
    problems = []
    if len(mods) > args.max_mods:
        problems.append(f'{len(mods)} mods, over the cap of {args.max_mods}')
    problems += check_marketplace(mods)
    problems += check_vendor()
    problems += check_retired_ids()
    results = {}
    has_claude = shutil.which('claude') is not None
    if args.require_claude and not has_claude:
        problems.append('claude is not on PATH (--require-claude)')
    if not args.no_claude and has_claude:
        results, more = run_claude(mods)
        problems += more

    report = {
        'mods': [m.name for m in mods],
        'count': len(mods),
        'tests': results,
        'tests_total': sum(r['tests_pass'] for r in results.values()),
        'problems': problems,
    }
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f'{len(mods)} mods: {", ".join(report["mods"])}')
        for name, r in results.items():
            print(f'  {name}: {r["tests_pass"]} pass, {r["tests_fail"]} fail, validate {"ok" if r["validate_exit"] == 0 else "FAILED"}')
        if results:
            print(f'  {report["tests_total"]} tests in all')
        for p in problems:
            print(f'FAIL {p}')
        print('ok' if not problems else f'{len(problems)} problem(s)')
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
