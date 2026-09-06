#!/usr/bin/env python3
"""
figma_sync.py
Synchronizes design tokens and brand assets with Figma via the Figma REST API.

Features:
- Parses W3C / DTCG Design Tokens (JSON format).
- Converts HEX / HSL colors into Figma 0.0 - 1.0 RGBA space.
- Creates a Figma variable collection with one mode per $extensions.modes key (light, dark, ...); aliases resolved.
- Supports dry-run validation mode for offline testing.

Usage:
    python3 figma_sync.py --tokens-file tokens.json                     # validate only (default)
    FIGMA_TOKEN=... FIGMA_FILE_KEY=... python3 figma_sync.py --tokens-file tokens.json --apply

The token is read only from the FIGMA_TOKEN environment variable; it is never accepted on the command line.
"""

import argparse
import json
import os
import re
import sys
import urllib.request
import urllib.error
from typing import Dict, Any, List, Tuple


def hex_to_figma_rgba(hex_code: str) -> Dict[str, float]:
    """Convert #RRGGBB or #RRGGBBAA into Figma's 0-1 float RGB dictionary."""
    clean_hex = hex_code.lstrip("#")
    if len(clean_hex) == 3:
        clean_hex = "".join([c * 2 for c in clean_hex])
    
    r = int(clean_hex[0:2], 16) / 255.0
    g = int(clean_hex[2:4], 16) / 255.0
    b = int(clean_hex[4:6], 16) / 255.0
    a = 1.0
    if len(clean_hex) == 8:
        a = int(clean_hex[6:8], 16) / 255.0
    return {"r": round(r, 4), "g": round(g, 4), "b": round(b, 4), "a": round(a, 4)}


def parse_tokens(tokens_dict: Dict[str, Any], prefix: str = "") -> List[Tuple[str, str, Any, Dict[str, Any]]]:
    """
    Recursively extract token definitions from W3C DTCG formatted json.
    Returns a list of (token_path, token_type, value, modes) where modes comes from $extensions.modes.
    """
    extracted = []
    for key, val in tokens_dict.items():
        if key.startswith("$"):
            continue
        current_path = f"{prefix}/{key}" if prefix else key
        if isinstance(val, dict):
            if "$value" in val or "value" in val:
                token_val = val.get("$value", val.get("value"))
                token_type = val.get("$type", val.get("type", "unknown"))
                modes = (val.get("$extensions") or {}).get("modes") or {}
                extracted.append((current_path, token_type, token_val, modes))
            else:
                extracted.extend(parse_tokens(val, current_path))
    return extracted


def resolve_aliases(tokens: List[Tuple[str, str, Any, Dict[str, Any]]]) -> List[Tuple[str, str, Any, Dict[str, Any]]]:
    """Replace {dotted.path} aliases (in values and mode values) with the referenced token's value."""
    table = {path.replace("/", "."): val for path, _, val, _ in tokens}

    def deref(v: Any, depth: int = 0) -> Any:
        while isinstance(v, str) and v.startswith("{") and v.endswith("}") and depth < 10:
            v = table.get(v[1:-1], v)
            depth += 1
            if isinstance(v, str) and v.startswith("{") and v[1:-1] not in table:
                raise ValueError(f"alias {v} does not resolve")
        return v

    return [(path, t, deref(val), {m: deref(mv) for m, mv in modes.items()}) for path, t, val, modes in tokens]


def to_figma_value(token_type: str, val: Any) -> Tuple[str, Any]:
    if token_type in ["color", "colour"] or (isinstance(val, str) and val.startswith("#")):
        return "COLOR", hex_to_figma_rgba(str(val))
    if token_type in ["number", "dimension", "spacing", "radius", "duration"] or isinstance(val, (int, float)):
        try:
            if isinstance(val, str):
                for unit in ("px", "ms", "rem"):
                    if val.endswith(unit):
                        return "FLOAT", float(val[: -len(unit)])
            return "FLOAT", float(val)
        except ValueError:
            return "STRING", str(val)
    return "STRING", str(val)


def build_figma_variable_payload(tokens: List[Tuple[str, str, Any, Dict[str, Any]]], collection_name: str = "Brand Design System") -> Dict[str, Any]:
    """Build the Figma Variables REST API payload: one collection, one mode per $extensions.modes key (or 'Default')."""
    temp_collection_id = "temp_collection_brand"
    mode_names: List[str] = []
    for _, _, _, modes in tokens:
        for m in modes:
            if m not in mode_names:
                mode_names.append(m)
    if not mode_names:
        mode_names = ["Default"]
    mode_ids = {m: f"temp_mode_{i}" for i, m in enumerate(mode_names)}

    variable_collections = [{"action": "CREATE", "id": temp_collection_id, "name": collection_name, "initialModeId": mode_ids[mode_names[0]]}]
    variable_modes = [{"action": "UPDATE", "id": mode_ids[mode_names[0]], "name": mode_names[0].title(), "variableCollectionId": temp_collection_id}]
    variable_modes += [{"action": "CREATE", "id": mode_ids[m], "name": m.title(), "variableCollectionId": temp_collection_id} for m in mode_names[1:]]

    variables = []
    variable_mode_values = []
    for idx, (path, token_type, val, modes) in enumerate(tokens):
        temp_var_id = f"temp_var_{idx}"
        resolved_type, base_value = to_figma_value(token_type, val)
        variables.append({"action": "CREATE", "id": temp_var_id, "name": path, "variableCollectionId": temp_collection_id, "resolvedType": resolved_type})
        for m in mode_names:
            mv = modes.get(m, val)
            _, figma_value = to_figma_value(token_type, mv)
            variable_mode_values.append({"variableId": temp_var_id, "modeId": mode_ids[m], "value": figma_value})

    return {"variableCollections": variable_collections, "variableModes": variable_modes, "variables": variables, "variableModeValues": variable_mode_values}


def sync_to_figma(file_key: str, token: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Execute POST to Figma REST API variables endpoint."""
    url = f"https://api.figma.com/v1/files/{file_key}/variables"
    data = json.dumps(payload).encode("utf-8")
    
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "X-Figma-Token": token,
            "Content-Type": "application/json"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req) as response:
            res_body = response.read().decode("utf-8")
            return json.loads(res_body)
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8")
        raise RuntimeError(f"Figma API error (HTTP {e.code}): {err_msg}")


def main():
    parser = argparse.ArgumentParser(description="Sync design tokens to Figma Variables")
    parser.add_argument("--tokens-file", required=True, help="Path to tokens.json")
    parser.add_argument("--file-key", help="Target Figma file key (or FIGMA_FILE_KEY in the environment)")
    parser.add_argument("--apply", action="store_true", help="Actually POST to Figma. Without it the script only validates and prints the payload")
    parser.add_argument("--dry-run", action="store_true", help="Validate and print the payload without calling the API (the default; kept for compatibility)")
    args = parser.parse_args()

    if not os.path.exists(args.tokens_file):
        print(f"❌ Error: Tokens file '{args.tokens_file}' does not exist.")
        sys.exit(1)

    with open(args.tokens_file, "r", encoding="utf-8") as f:
        tokens_raw = json.load(f)

    try:
        flat_tokens = resolve_aliases(parse_tokens(tokens_raw))
    except ValueError as err:
        print(f"❌ Error: {err}")
        sys.exit(1)
    print(f"📦 Loaded {len(flat_tokens)} tokens from {args.tokens_file}")

    payload = build_figma_variable_payload(flat_tokens)

    if args.dry_run or not args.apply:
        print("\n🧪 DRY RUN: generated Figma REST API payload (pass --apply to publish):")
        print(json.dumps(payload, indent=2))
        print("\n✅ Dry run complete. Token schemas validated successfully.")
        return

    figma_token = os.environ.get("FIGMA_TOKEN")
    file_key = args.file_key or os.environ.get("FIGMA_FILE_KEY")

    if not figma_token or not file_key:
        print("❌ Error: set FIGMA_TOKEN in the environment and pass --file-key (or FIGMA_FILE_KEY).")
        print("Tip: run without --apply to validate locally without calling Figma.")
        sys.exit(1)
    if not re.fullmatch(r"[A-Za-z0-9]{10,64}", file_key):
        print("❌ Error: the Figma file key must be 10-64 alphanumeric characters (copy it from the file URL).")
        sys.exit(1)
    print("Note: each --apply run creates a new variable collection; delete the previous one in Figma before re-publishing.")

    print(f"🌐 Publishing tokens to Figma File: {file_key}...")
    result = sync_to_figma(file_key, figma_token, payload)
    print("🎉 Successfully published to Figma Variables!")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
