#!/usr/bin/env python3
"""
contrast_check.py
WCAG 2.2 contrast ratios for a palette. Standard library only.

Checks explicit pairs, or the pairs the studio's token convention implies in a W3C tokens file:
  text.<role> (not disabled/inverse)  on every surface.<role> (not inverse)      4.5:1
  text.inverse                        on surface.inverse                          4.5:1
  <group>.on-<x>                      on <group>.<x> (e.g. brand.on-primary)      4.5:1
  <group>.on-colour / on              on the group's non-"on", non-subtle colours 4.5:1
  <group>.text                        on <group>.subtle (status groups)            4.5:1
  border.focus and border.strong      on every surface.<role>                    3:1 (UI)
Values under $extensions.modes are checked per mode (light, dark, ...) as well as the base value.

Usage:
    python3 contrast_check.py --pairs "#111827:#FFFFFF,#94A3B8:#090D16"
    python3 contrast_check.py --tokens tokens.json [--json]

Thresholds: AA text 4.5:1, AA large text and UI components 3:1, AAA text 7:1.
Exit 1 when any checked pair fails AA for body text (or 3:1 for pairs tagged as UI).
"""

import argparse
import json
import re
import sys
from typing import Any, Dict, List, Tuple

HEX = re.compile(r"^#?([0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")


def parse_hex(value: str) -> Tuple[float, float, float]:
    m = HEX.match(value.strip())
    if not m:
        raise ValueError(f"not a hex colour: {value}")
    h = m.group(1)
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))  # type: ignore[return-value]


def luminance(rgb: Tuple[float, float, float]) -> float:
    def channel(c: float) -> float:
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (channel(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(fg: str, bg: str) -> float:
    l1, l2 = luminance(parse_hex(fg)), luminance(parse_hex(bg))
    hi, lo = max(l1, l2), min(l1, l2)
    return round((hi + 0.05) / (lo + 0.05), 2)


def flatten(tokens: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for key, val in tokens.items():
        if key.startswith("$"):
            continue
        path = f"{prefix}.{key}" if prefix else key
        if isinstance(val, dict) and ("$value" in val or "value" in val):
            out[path] = val.get("$value", val.get("value"))
        elif isinstance(val, dict):
            out.update(flatten(val, path))
    return out


def resolve(value: Any, table: Dict[str, Any], depth: int = 0) -> Any:
    if isinstance(value, str) and value.startswith("{") and value.endswith("}") and depth < 10:
        return resolve(table.get(value[1:-1]), table, depth + 1)
    return value


def flatten_full(tokens: Dict[str, Any], prefix: str = "") -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for key, val in tokens.items():
        if key.startswith("$"):
            continue
        path = f"{prefix}.{key}" if prefix else key
        if isinstance(val, dict) and ("$value" in val or "value" in val):
            out[path] = val
        elif isinstance(val, dict):
            out.update(flatten_full(val, path))
    return out


def colour_tables(path: str) -> Dict[str, Dict[str, str]]:
    """{mode: {token_path: hex}} with 'base' always present; mode values fall back to the base value."""
    with open(path, "r", encoding="utf-8") as f:
        full = flatten_full(json.load(f))
    base_vals = {k: v.get("$value", v.get("value")) for k, v in full.items()}
    modes = set()
    for v in full.values():
        modes.update(((v.get("$extensions") or {}).get("modes") or {}).keys())
    tables: Dict[str, Dict[str, str]] = {}
    for mode in ["base"] + sorted(modes):
        vals = dict(base_vals)
        if mode != "base":
            for k, v in full.items():
                mv = ((v.get("$extensions") or {}).get("modes") or {}).get(mode)
                if mv is not None:
                    vals[k] = mv
        resolved = {k: resolve(v, vals) for k, v in vals.items()}
        tables[mode] = {k: str(v) for k, v in resolved.items() if isinstance(v, str) and HEX.match(v)}
    return tables


def pairs_from_tokens(path: str) -> List[Tuple[str, str, str, str, str]]:
    pairs: List[Tuple[str, str, str, str, str]] = []
    for mode, colours in colour_tables(path).items():
        tag = "" if mode == "base" else f" [{mode}]"
        last = lambda k: k.split(".")[-1]
        texts = {k: v for k, v in colours.items() if ".text." in k and last(k) not in ("disabled", "inverse")}
        surfaces = {k: v for k, v in colours.items() if ".surface." in k and last(k) != "inverse"}
        for tk, tv in texts.items():
            for sk, sv in surfaces.items():
                pairs.append((tk + tag, tv, sk + tag, sv, "text"))
        inv_text = [k for k in colours if ".text.inverse" in k]
        inv_surf = [k for k in colours if ".surface.inverse" in k]
        for tk in inv_text:
            for sk in inv_surf:
                pairs.append((tk + tag, colours[tk], sk + tag, colours[sk], "text"))
        for k, v in colours.items():
            name = last(k)
            if not name.startswith("on"):
                continue
            group = k.rsplit(".", 1)[0]
            siblings = {last(s): s for s in colours if s.rsplit(".", 1)[0] == group and not last(s).startswith("on")}
            if name.startswith("on-") and name[3:] in siblings:
                targets = [siblings[name[3:]]]
            else:
                targets = [s for n, s in siblings.items() if n not in ("subtle", "surface", "disabled")]
            for sk in targets:
                pairs.append((k + tag, v, sk + tag, colours[sk], "text"))
        for k, v in colours.items():
            if last(k) == "text" and ".text." not in k:
                subtle = k.rsplit(".", 1)[0] + ".subtle"
                if subtle in colours:
                    pairs.append((k + tag, v, subtle + tag, colours[subtle], "text"))
        for k, v in colours.items():
            if ".border." in k and last(k) in ("focus", "strong"):
                for sk, sv in surfaces.items():
                    pairs.append((k + tag, v, sk + tag, sv, "ui"))
    return pairs


def main() -> None:
    parser = argparse.ArgumentParser(description="WCAG 2.2 contrast check for palette pairs or a W3C tokens file")
    parser.add_argument("--pairs", help='Comma-separated "fg:bg" hex pairs, e.g. "#111:#fff,#888:#000"')
    parser.add_argument("--tokens", help="W3C design tokens JSON; pairs by the studio convention, per mode")
    parser.add_argument("--ui", action="store_true", help="Treat --pairs as UI/large-text pairs (3:1 threshold)")
    parser.add_argument("--json", action="store_true", help="Machine-readable output")
    args = parser.parse_args()

    rows: List[Dict[str, Any]] = []
    if args.pairs:
        for item in args.pairs.split(","):
            fg, bg = item.split(":")
            rows.append({"fg": fg.strip(), "bg": bg.strip(), "fg_name": fg.strip(), "bg_name": bg.strip(), "kind": "ui" if args.ui else "text"})
    if args.tokens:
        for tk, tv, sk, sv, kind in pairs_from_tokens(args.tokens):
            rows.append({"fg": tv, "bg": sv, "fg_name": tk, "bg_name": sk, "kind": kind})
    if not rows:
        parser.error("give --pairs or --tokens (no text/surface tokens found)")

    failures = 0
    for r in rows:
        ratio = contrast(r["fg"], r["bg"])
        r["ratio"] = ratio
        r["aa_text"] = ratio >= 4.5
        r["aa_large_ui"] = ratio >= 3.0
        r["aaa_text"] = ratio >= 7.0
        r["pass"] = r["aa_large_ui"] if r["kind"] == "ui" else r["aa_text"]
        failures += 0 if r["pass"] else 1

    if args.json:
        print(json.dumps({"pairs": rows, "failures": failures}, indent=2))
    else:
        print(f"{'foreground':40} {'background':40} {'ratio':>6}  AA  AA-lg/UI  AAA")
        for r in rows:
            print(f"{r['fg_name'][:40]:40} {r['bg_name'][:40]:40} {r['ratio']:>6}  {'✓' if r['aa_text'] else '✗'}   {'✓' if r['aa_large_ui'] else '✗'}       {'✓' if r['aaa_text'] else '✗'}"
                  + ("" if r["pass"] else "   <-- FAIL"))
        print(f"\n{len(rows) - failures}/{len(rows)} pairs pass their threshold")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
