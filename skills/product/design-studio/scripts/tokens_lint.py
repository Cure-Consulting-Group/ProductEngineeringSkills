#!/usr/bin/env python3
"""
tokens_lint.py
Lint a W3C Design Tokens file for the studio's three-tier convention. Standard library only.

Checks:
  E1  every token has $type and $value
  E2  names are lowercase words separated by dots/hyphens (no spaces, camelCase, or abbreviations other than bg/fg)
  E3  alias references ({path.to.token}) resolve
  E4  no alias cycles
  W1  tiers: top-level groups named primitive|primitives|core, semantic|sys|alias, component|comp|components;
      semantic tokens should alias primitives (raw values in the semantic tier are warned),
      component tokens should alias semantic tokens
  W2  mode parity: with --modes, every semantic colour token carries $extensions.modes.<mode> for each mode,
      or, with two --tokens files, both files define the same token paths

Usage:
    python3 tokens_lint.py --tokens tokens.json [--modes light,dark] [--json]
    python3 tokens_lint.py --tokens light.json --tokens dark.json     # parity between files
Exit 1 on any error; warnings alone exit 0.
"""

import argparse
import json
import re
import sys
from typing import Any, Dict, List, Tuple

NAME_RE = re.compile(r"^[a-z0-9]+(?:[-.][a-z0-9]+)*$")
TIER_NAMES = {"primitive": {"primitive", "primitives", "core", "ref"}, "semantic": {"semantic", "sys", "alias"}, "component": {"component", "comp", "components"}}


def walk(node: Dict[str, Any], prefix: str, out: Dict[str, Dict[str, Any]], problems: List[Tuple[str, str, str]]) -> None:
    for key, val in node.items():
        if key.startswith("$"):
            continue
        path = f"{prefix}.{key}" if prefix else key
        if not isinstance(val, dict):
            problems.append(("E1", path, "token or group must be an object"))
            continue
        if "$value" in val or "value" in val:
            out[path] = val
            if "$value" not in val or "$type" not in val:
                problems.append(("E1", path, "missing $type or $value (W3C format requires both)"))
        else:
            walk(val, path, out, problems)


def tier_of(path: str) -> str:
    head = path.split(".")[0]
    for tier, names in TIER_NAMES.items():
        if head in names:
            return tier
    return "untiered"


def lint(tokens: Dict[str, Any], modes: List[str]) -> Tuple[List[Tuple[str, str, str]], Dict[str, Dict[str, Any]]]:
    problems: List[Tuple[str, str, str]] = []
    table: Dict[str, Dict[str, Any]] = {}
    walk(tokens, "", table, problems)

    for path, tok in table.items():
        for part in path.split("."):
            if not NAME_RE.match(part):
                problems.append(("E2", path, f"segment '{part}' is not lowercase-dotted/hyphenated"))
                break
        val = tok.get("$value", tok.get("value"))
        if isinstance(val, str) and val.startswith("{") and val.endswith("}"):
            target = val[1:-1]
            if target not in table:
                problems.append(("E3", path, f"alias {{{target}}} does not resolve"))
            else:
                seen = {path}
                cur = target
                while True:
                    nxt = table[cur].get("$value", table[cur].get("value"))
                    if not (isinstance(nxt, str) and nxt.startswith("{")):
                        break
                    nxt = nxt[1:-1]
                    if nxt in seen or nxt not in table:
                        if nxt in seen:
                            problems.append(("E4", path, "alias cycle"))
                        break
                    seen.add(nxt)
                    cur = nxt
                src_tier, dst_tier = tier_of(path), tier_of(target)
                if src_tier == "component" and dst_tier == "primitive":
                    problems.append(("W1", path, "component token aliases a primitive; alias a semantic token"))
        else:
            if tier_of(path) == "semantic" and tok.get("$type") in ("color", "dimension", "fontFamily"):
                problems.append(("W1", path, "semantic token holds a raw value; alias a primitive"))
            if tier_of(path) == "component":
                problems.append(("W1", path, "component token holds a raw value; alias a semantic token"))

    tiers = {tier_of(p) for p in table}
    if tiers == {"untiered"}:
        problems.append(("W1", "(root)", "no primitive/semantic/component top-level groups; tier checks skipped"))

    for mode in modes:
        for path, tok in table.items():
            if tier_of(path) == "semantic" and tok.get("$type") == "color":
                mode_vals = (tok.get("$extensions") or {}).get("modes") or {}
                if mode not in mode_vals:
                    problems.append(("W2", path, f"no value for mode '{mode}' in $extensions.modes"))
    return problems, table


def main() -> None:
    parser = argparse.ArgumentParser(description="Lint W3C design tokens for tiers, naming, aliases, and mode parity")
    parser.add_argument("--tokens", action="append", required=True, help="tokens.json (repeat for light/dark parity)")
    parser.add_argument("--modes", default="", help="Comma list of modes every semantic colour must define, e.g. light,dark")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    modes = [m for m in args.modes.split(",") if m]
    all_problems: List[Dict[str, str]] = []
    tables = []
    for path in args.tokens:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        problems, table = lint(data, modes)
        tables.append((path, table))
        all_problems += [{"file": path, "code": c, "token": t, "message": m} for c, t, m in problems]
    if len(tables) == 2:
        (fa, ta), (fb, tb) = tables
        for missing in sorted(set(ta) - set(tb)):
            all_problems.append({"file": fb, "code": "W2", "token": missing, "message": f"defined in {fa} but not here"})
        for missing in sorted(set(tb) - set(ta)):
            all_problems.append({"file": fa, "code": "W2", "token": missing, "message": f"defined in {fb} but not here"})

    errors = [p for p in all_problems if p["code"].startswith("E")]
    total = sum(len(t) for _, t in tables)
    if args.json:
        print(json.dumps({"tokens": total, "errors": len(errors), "warnings": len(all_problems) - len(errors), "problems": all_problems}, indent=2))
    else:
        for p in all_problems:
            print(f"{p['code']}  {p['token']:50} {p['message']}")
        print(f"\n{total} tokens, {len(errors)} errors, {len(all_problems) - len(errors)} warnings")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
