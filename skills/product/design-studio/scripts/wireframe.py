#!/usr/bin/env python3
"""
wireframe.py
Render low- or mid-fidelity wireframes, a flow diagram, and a screen inventory from one JSON spec.
Standard library only; output is plain SVG and Markdown.

Usage:
    python3 wireframe.py --example > spec.json          # starter spec to edit
    python3 wireframe.py --spec spec.json --out design/wireframes [--fidelity low|mid] [--json]

Spec shape (see --example): product, platform (ios|android|tablet|web), fidelity, nav_items[], screens[], flows[].
nav_items (top-level or per screen) label the tab bar, sidebar, or top bar. Stale screen SVGs in --out are removed.
Each screen: id, name, purpose, nav (tabs|sidebar|topbar|none), primary_action, regions[], notes[].
Each region: type (header|hero|text|list|card|form|table|chart|image|tabs|toolbar|cta|sheet),
             label, optional rows, height, fixed (true = stays put), sticky (true = sticks on scroll).
Fixed regions render in the chrome; the rest stack in a scrolling area and the scroll model is
written into inventory.md, which is the source for the scrolling section of the deliverable.
"""

import argparse
import json
import os
import sys
from typing import Any, Dict, List, Tuple

FRAMES = {"ios": (393, 852), "android": (412, 915), "tablet": (834, 1194), "web": (1440, 900)}
DEFAULT_HEIGHT = {"header": 56, "hero": 220, "text": 72, "list": 64, "card": 120, "form": 68, "table": 40,
                  "chart": 200, "image": 180, "tabs": 44, "toolbar": 48, "cta": 56, "sheet": 260}
INK, MUTE, FILL, ACCENT = "#111827", "#6B7280", "#F3F4F6", "#2563EB"

EXAMPLE: Dict[str, Any] = {
    "product": "Dispatch",
    "platform": "android",
    "fidelity": "mid",
    "nav_items": ["Today", "Jobs", "Map", "Inbox"],
    "screens": [
        {"id": "today", "name": "Today", "purpose": "See the day's route and what is late", "nav": "tabs",
         "primary_action": "Start next job",
         "regions": [
             {"type": "header", "label": "Today", "fixed": True},
             {"type": "card", "label": "Next job: address, window, status"},
             {"type": "tabs", "label": "Route / Late / Done", "sticky": True},
             {"type": "list", "label": "Job row: customer, window, distance", "rows": 6},
             {"type": "cta", "label": "Start next job", "fixed": True}],
         "notes": ["Empty: no jobs today -> 'Pick up unassigned' path", "Error: sync failed -> banner with retry, cached route stays", "Long: 42-char customer name wraps to two lines"]},
        {"id": "job", "name": "Job", "purpose": "Do the job and close it", "nav": "none",
         "primary_action": "Mark complete",
         "regions": [
             {"type": "header", "label": "< Back   Job", "fixed": True},
             {"type": "hero", "label": "Customer, address, window"},
             {"type": "text", "label": "Notes from dispatcher (2-4 lines)"},
             {"type": "form", "label": "Parts used, time, signature", "rows": 3},
             {"type": "toolbar", "label": "Call / Navigate / Complete", "fixed": True}],
         "notes": ["Offline: form saves locally, badge shows 'will sync'"]}
    ],
    "flows": [{"from": "today", "to": "job", "label": "tap row"}, {"from": "job", "to": "today", "label": "complete / back"}]
}


def esc(s: str) -> str:
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def text(x: float, y: float, s: str, size: int = 12, fill: str = INK, anchor: str = "start", weight: str = "normal") -> str:
    return f'<text x="{x}" y="{y}" font-family="-apple-system, Helvetica, Arial, sans-serif" font-size="{size}" fill="{fill}" text-anchor="{anchor}" font-weight="{weight}">{esc(s)}</text>'


def box(x: float, y: float, w: float, h: float, fill: str = "white", stroke: str = INK, dash: str = "", rx: int = 4) -> str:
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="1.2"{d}/>'


def placeholder_image(x: float, y: float, w: float, h: float) -> str:
    return box(x, y, w, h, FILL, MUTE) + f'<line x1="{x}" y1="{y}" x2="{x+w}" y2="{y+h}" stroke="{MUTE}"/><line x1="{x+w}" y1="{y}" x2="{x}" y2="{y+h}" stroke="{MUTE}"/>'


def region_svg(r: Dict[str, Any], x: float, y: float, w: float, fidelity: str) -> Tuple[str, float]:
    t = r.get("type", "text")
    rows = int(r.get("rows", 1))
    h = float(r.get("height") or DEFAULT_HEIGHT.get(t, 72) * (rows if t in ("list", "table", "form") else 1))
    label = r.get("label", t)
    parts: List[str] = []
    if fidelity == "low" or t in ("text", "sheet"):
        parts.append(box(x, y, w, h, FILL if t != "cta" else ACCENT, MUTE if t != "cta" else ACCENT))
        parts.append(text(x + 10, y + 20, f"{t.upper()}: {label}", 11, "white" if t == "cta" else MUTE))
        return "".join(parts), h
    if t in ("header", "toolbar", "tabs"):
        parts.append(box(x, y, w, h, "white", MUTE, rx=0))
        segs = [s.strip() for s in str(label).split("|")] if "|" in str(label) else [label]
        seg_w = w / len(segs)
        for i, s in enumerate(segs):
            parts.append(text(x + seg_w * i + seg_w / 2, y + h / 2 + 4, s, 12, INK if i == 0 else MUTE, "middle", "600" if t == "header" else "normal"))
            if t == "tabs" and i == 0:
                parts.append(f'<line x1="{x+8}" y1="{y+h-2}" x2="{x+seg_w-8}" y2="{y+h-2}" stroke="{ACCENT}" stroke-width="2"/>')
    elif t == "hero":
        parts.append(placeholder_image(x + 12, y + 12, 72, 72))
        parts.append(text(x + 96, y + 36, label, 16, INK, weight="600"))
        parts.append(box(x + 96, y + 48, w - 120, 10, FILL, FILL))
        parts.append(box(x + 96, y + 64, (w - 120) * 0.6, 10, FILL, FILL))
    elif t == "list":
        rh = h / rows
        for i in range(rows):
            yy = y + rh * i
            parts.append(f'<circle cx="{x+28}" cy="{yy+rh/2}" r="14" fill="{FILL}" stroke="{MUTE}"/>')
            parts.append(box(x + 52, yy + rh / 2 - 14, (w - 100) * (0.55 if i % 2 else 0.7), 10, INK, INK))
            parts.append(box(x + 52, yy + rh / 2 + 2, (w - 100) * 0.4, 8, FILL, FILL))
            parts.append(text(x + w - 12, yy + rh / 2 + 4, "›", 16, MUTE, "end"))
            parts.append(f'<line x1="{x+52}" y1="{yy+rh}" x2="{x+w}" y2="{yy+rh}" stroke="{FILL}"/>')
        parts.append(text(x + 12, y + h - 6, label, 9, MUTE))
    elif t == "table":
        rh = h / rows
        cols = 4 if w > 500 else 3
        cw = w / cols
        for i in range(rows):
            yy = y + rh * i
            parts.append(box(x, yy, w, rh, FILL if i == 0 else "white", MUTE, rx=0))
            for c in range(cols):
                parts.append(box(x + cw * c + 10, yy + rh / 2 - 5, cw * 0.6, 8, INK if i == 0 else FILL, INK if i == 0 else FILL))
        parts.append(text(x + 4, y - 4, label, 9, MUTE))
    elif t == "form":
        fh = h / rows
        for i in range(rows):
            yy = y + fh * i
            parts.append(text(x + 4, yy + 14, f"Label {i+1}", 10, MUTE))
            parts.append(box(x, yy + 20, w, fh - 30, "white", MUTE))
        parts.append(text(x + 4, y + h - 2, label, 9, MUTE))
    elif t == "card":
        parts.append(box(x, y, w, h, "white", MUTE, rx=8))
        parts.append(text(x + 14, y + 26, label, 13, INK, weight="600"))
        parts.append(box(x + 14, y + 40, w * 0.6, 10, FILL, FILL))
        parts.append(box(x + 14, y + 56, w * 0.4, 10, FILL, FILL))
    elif t == "chart":
        parts.append(box(x, y, w, h, "white", MUTE))
        parts.append(text(x + 10, y + 18, label, 11, INK, weight="600"))
        pts = " ".join(f"{x + 16 + (w - 32) * i / 7},{y + h - 16 - (h - 50) * v}" for i, v in enumerate([0.3, 0.5, 0.4, 0.7, 0.6, 0.85, 0.75, 0.9]))
        parts.append(f'<polyline points="{pts}" fill="none" stroke="{ACCENT}" stroke-width="2"/>')
    elif t == "image":
        parts.append(placeholder_image(x, y, w, h))
        parts.append(text(x + w / 2, y + h / 2 + 4, label, 11, MUTE, "middle"))
    elif t == "cta":
        parts.append(box(x + 12, y + 8, w - 24, h - 16, ACCENT, ACCENT, rx=10))
        parts.append(text(x + w / 2, y + h / 2 + 5, label, 14, "white", "middle", "600"))
    else:
        parts.append(box(x, y, w, h, FILL, MUTE))
        parts.append(text(x + 10, y + 20, label, 11, MUTE))
    return "".join(parts), h


def render_screen(screen: Dict[str, Any], platform: str, fidelity: str, nav_items: List[str]) -> Tuple[str, Dict[str, Any]]:
    fw, fh = FRAMES.get(platform, FRAMES["web"])
    nav_items = screen.get("nav_items") or nav_items
    nav = screen.get("nav", "none")
    margin = 16 if platform != "web" else 24
    parts: List[str] = [box(0, 0, fw, fh, "white", INK, rx=0)]
    x, w = margin, fw - 2 * margin
    top, bottom = 0.0, 0.0
    if platform in ("ios", "android"):
        top = 47 if platform == "ios" else 24  # status bar / cutout region
        parts.append(box(0, 0, fw, top, FILL, FILL, rx=0))
        parts.append(text(fw / 2, top - 8, "safe area", 9, MUTE, "middle"))
        if nav == "tabs":
            bar = 83 if platform == "ios" else 80
            bottom = bar
            parts.append(box(0, fh - bar, fw, bar, FILL, MUTE, rx=0))
            tabs = (nav_items or ["Home", "Search", "Inbox", "Profile"])[:5]
            for i, lbl in enumerate(tabs):
                cx = fw / (2 * len(tabs)) + fw / len(tabs) * i
                parts.append(f'<circle cx="{cx}" cy="{fh-bar+22}" r="10" fill="{ACCENT if i == 0 else MUTE}"/>')
                parts.append(text(cx, fh - bar + 46, lbl, 10, ACCENT if i == 0 else MUTE, "middle"))
            parts.append(text(fw / 2, fh - 10, "tab bar (fixed)" if platform == "ios" else "navigation bar (fixed)", 9, MUTE, "middle"))
    elif nav == "sidebar":
        sw = 240 if platform == "web" else 200
        parts.append(box(0, 0, sw, fh, FILL, MUTE, rx=0))
        for i, lbl in enumerate((nav_items or ["Overview", "Work", "People", "Reports", "Settings"])[:12]):
            parts.append(text(20, 60 + 36 * i, lbl, 13, ACCENT if i == 0 else INK, weight="600" if i == 0 else "normal"))
        parts.append(text(sw / 2, fh - 12, "sidebar (persistent)", 9, MUTE, "middle"))
        x, w = sw + margin, fw - sw - 2 * margin
    elif nav == "topbar":
        parts.append(box(0, 0, fw, 64, "white", MUTE, rx=0))
        for i, lbl in enumerate((nav_items or ["Product", "Pricing", "Docs", "Company"])[:6]):
            parts.append(text(200 + 110 * i, 38, lbl, 13, INK))
        parts.append(text(fw - margin, 38, "Sign in   [Get started]", 13, ACCENT, "end"))
        top = 64
    fixed_top = [r for r in screen.get("regions", []) if r.get("fixed") and r.get("type") in ("header", "tabs")]
    fixed_bottom = [r for r in screen.get("regions", []) if r.get("fixed") and r.get("type") not in ("header", "tabs")]
    scrolling = [r for r in screen.get("regions", []) if not r.get("fixed")]
    y = top
    for r in fixed_top:
        svg, h = region_svg(r, x, y, w, fidelity)
        parts.append(svg + text(x + w, y + 10, "FIXED", 8, ACCENT, "end"))
        y += h + 4
    yb = fh - bottom
    for r in reversed(fixed_bottom):
        _, h = region_svg(r, x, 0, w, fidelity)
        yb -= h + 4
        svg, _ = region_svg(r, x, yb, w, fidelity)
        parts.append(svg + text(x + w, yb + 10, "FIXED", 8, ACCENT, "end"))
    scroll_top, scroll_bottom = y, yb
    parts.append(f'<rect x="{x-6}" y="{scroll_top}" width="{w+12}" height="{max(scroll_bottom-scroll_top, 0)}" fill="none" stroke="{ACCENT}" stroke-dasharray="4 4" opacity="0.6"/>')
    parts.append(text(x + w + 6, scroll_top + 12, "scrolls ↓", 8, ACCENT, "end"))
    y = scroll_top + 8
    overflow = 0.0
    for r in scrolling:
        svg, h = region_svg(r, x, y, w, fidelity)
        if y + h > scroll_bottom:
            overflow += h + 8
        parts.append(svg + (text(x + w, y + 10, "STICKY", 8, ACCENT, "end") if r.get("sticky") else ""))
        y += h + 8
    if overflow:
        parts.append(text(x + w / 2, scroll_bottom - 6, f"… {int(overflow)} px more below the fold", 9, ACCENT, "middle"))
    title = f'{screen.get("name", screen["id"])}  ·  {platform}  ·  {fidelity}-fi'
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-10 -30 {fw+20} {fh+40}" width="{fw+20}" height="{fh+40}" role="img" aria-label="{esc(title)}">'
           f'{text(0, -10, title, 13, INK, weight="600")}{"".join(parts)}</svg>')
    model = {"id": screen["id"], "name": screen.get("name", screen["id"]), "purpose": screen.get("purpose", ""), "nav": nav,
             "primary_action": screen.get("primary_action", ""),
             "fixed": [r.get("label", r["type"]) for r in fixed_top + fixed_bottom],
             "sticky": [r.get("label", r["type"]) for r in scrolling if r.get("sticky")],
             "scrolls": [r.get("label", r["type"]) for r in scrolling if not r.get("sticky")],
             "below_fold_px": int(overflow), "notes": screen.get("notes", [])}
    return svg, model


def render_flow(spec: Dict[str, Any]) -> str:
    screens = spec.get("screens", [])
    cols = max(1, min(4, len(screens)))
    bw, bh, gx, gy = 200, 90, 80, 70
    pos = {s["id"]: ((i % cols) * (bw + gx) + 20, (i // cols) * (bh + gy) + 40) for i, s in enumerate(screens)}
    W = cols * (bw + gx) + 40
    H = ((len(screens) - 1) // cols + 1) * (bh + gy) + 60
    parts = ['<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#111827"/></marker></defs>']
    for s in screens:
        x, y = pos[s["id"]]
        parts.append(box(x, y, bw, bh, "white", INK, rx=6))
        parts.append(text(x + 12, y + 24, s.get("name", s["id"]), 13, INK, weight="600"))
        parts.append(text(x + 12, y + 44, s.get("purpose", "")[:34], 10, MUTE))
        parts.append(text(x + 12, y + 64, f"→ {s.get('primary_action', '')}"[:34], 10, ACCENT))
    for i, f in enumerate(spec.get("flows", [])):
        if f["from"] not in pos or f["to"] not in pos:
            continue
        (x1, y1), (x2, y2) = pos[f["from"]], pos[f["to"]]
        sx, sy = x1 + bw, y1 + bh / 2 + (8 if i % 2 else -8)
        ex, ey = x2, y2 + bh / 2 + (8 if i % 2 else -8)
        if x2 < x1:
            sx, ex = x1, x2 + bw
        parts.append(f'<line x1="{sx}" y1="{sy}" x2="{ex}" y2="{ey}" stroke="{INK}" stroke-width="1.2" marker-end="url(#arrow)"/>')
        parts.append(text((sx + ex) / 2, (sy + ey) / 2 - 6, f.get("label", ""), 10, MUTE, "middle"))
    title = f'{spec.get("product", "Product")} — flows'
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{esc(title)}">{text(20, 24, title, 14, INK, weight="600")}{"".join(parts)}</svg>'


def main() -> None:
    parser = argparse.ArgumentParser(description="Wireframes, flow diagram, and screen inventory from a JSON spec (SVG + Markdown, stdlib only)")
    parser.add_argument("--spec", help="Path to the spec JSON")
    parser.add_argument("--out", default="design/wireframes", help="Output directory")
    parser.add_argument("--fidelity", choices=["low", "mid"], help="Override the spec's fidelity")
    parser.add_argument("--example", action="store_true", help="Print an example spec and exit")
    parser.add_argument("--json", action="store_true", help="Print the screen models as JSON")
    args = parser.parse_args()

    if args.example:
        print(json.dumps(EXAMPLE, indent=2))
        return
    if not args.spec:
        parser.error("--spec is required (or --example)")
    with open(args.spec, "r", encoding="utf-8") as f:
        spec = json.load(f)
    platform = spec.get("platform", "web")
    fidelity = args.fidelity or spec.get("fidelity", "low")
    if platform not in FRAMES:
        print(f"❌ platform must be one of {', '.join(FRAMES)}", file=sys.stderr)
        sys.exit(1)
    screens_dir = os.path.join(args.out, "screens")
    os.makedirs(screens_dir, exist_ok=True)
    wanted = {f"{s['id']}.svg" for s in spec.get("screens", [])}
    for stale in os.listdir(screens_dir):
        if stale.endswith(".svg") and stale not in wanted:
            os.remove(os.path.join(screens_dir, stale))
            print(f"  removed stale {stale}")
    models = []
    for s in spec.get("screens", []):
        svg, model = render_screen(s, platform, fidelity, spec.get("nav_items") or [])
        with open(os.path.join(screens_dir, f"{s['id']}.svg"), "w", encoding="utf-8") as f:
            f.write(svg)
        models.append(model)
    with open(os.path.join(args.out, "flow.svg"), "w", encoding="utf-8") as f:
        f.write(render_flow(spec))
    lines = [f"# {spec.get('product', 'Product')} — screen inventory ({platform}, {fidelity}-fi)", "",
             "| Screen | Purpose | Nav | Primary action | Fixed | Sticky | Scrolls | Below fold |", "|---|---|---|---|---|---|---|---|"]
    cell = lambda v: str(v).replace("|", "/")
    for m in models:
        lines.append(f"| {cell(m['name'])} | {cell(m['purpose'])} | {m['nav']} | {cell(m['primary_action'])} | {cell('; '.join(m['fixed']) or '—')} | {cell('; '.join(m['sticky']) or '—')} | {cell('; '.join(m['scrolls']) or '—')} | {m['below_fold_px']} px |")
    lines += ["", "## Notes and states", ""]
    for m in models:
        for n in m["notes"]:
            lines.append(f"- **{m['name']}**: {n}")
    with open(os.path.join(args.out, "inventory.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    if args.json:
        print(json.dumps({"out": args.out, "screens": models}, indent=2))
    else:
        print(f"✓ {len(models)} screens -> {screens_dir}/, flow.svg, inventory.md in {args.out}")


if __name__ == "__main__":
    main()
