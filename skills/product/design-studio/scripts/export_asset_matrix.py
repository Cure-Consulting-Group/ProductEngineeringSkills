#!/usr/bin/env python3
"""
export_asset_matrix.py
Production asset export from one master SVG. Standard library only; rendering is delegated to whatever
SVG renderer the machine has, tried in this order:

  rsvg-convert  |  inkscape  |  magick (ImageMagick 7)  |  Google Chrome / Chromium headless  |  qlmanage (macOS)

The first four keep transparency. qlmanage flattens alpha to white, so with it only opaque outputs are
produced and every transparent asset is reported as a failure instead of shipped as a white box.
Every transparent output is verified by reading its corner pixel after rendering.

Outputs:
  web      favicon 16/32/48 (+ favicon.ico), apple-touch-icon 180, android-chrome 192/512, maskable 512,
           avatar 400, OpenGraph 1200x630, Twitter/X header 1500x500, brand_guidelines.html
  ios      AppIcon.appiconset: 1024 master and the device sizes (opaque, square corners; the system masks)
  android  adaptive foreground (108 dp canvas, mark inside the 66 dp safe zone, transparent), background layer,
           legacy launcher mdpi..xxxhdpi, Play Store icon 512 and feature graphic 1024x500
Monochrome and notification glyphs are authored separately as single-colour SVGs (see references/brand-identity.md).

Usage:
    python3 export_asset_matrix.py --svg master_logo.svg --output-dir dist/brand_assets --brand-name "Brand"
    python3 export_asset_matrix.py --svg master_logo.svg --platforms web,ios,android --icon-bg 0F172A
"""

import argparse
import base64
import html
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
import zlib
from typing import Optional, Tuple

SVG_NS = "http://www.w3.org/2000/svg"
CHROME_PATHS = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/usr/bin/google-chrome", "/usr/bin/chromium", "/usr/bin/chromium-browser",
]
WEB_SPECS = [  # (name, w, h, mark, transparent)
    ("favicon-16x16.png", 16, 16, 16, True), ("favicon-32x32.png", 32, 32, 32, True), ("favicon-48x48.png", 48, 48, 48, True),
    ("apple-touch-icon.png", 180, 180, 140, False), ("android-chrome-192x192.png", 192, 192, 192, True),
    ("android-chrome-512x512.png", 512, 512, 512, True), ("maskable-icon-512x512.png", 512, 512, 400, False),
    ("avatar-400x400.png", 400, 400, 280, False), ("opengraph-1200x630.png", 1200, 630, 300, False),
    ("twitter-header-1500x500.png", 1500, 500, 260, False),
]
IOS_SIZES = [40, 58, 60, 76, 80, 87, 120, 152, 167, 180]
ANDROID_LEGACY = {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}
ADAPTIVE_CANVAS, ADAPTIVE_SAFE = 432, 264  # 108 dp and 66 dp at 4x


# ---------------------------------------------------------------- renderers
def find_renderer() -> Tuple[str, str]:
    for name in ("rsvg-convert", "inkscape", "magick"):
        path = shutil.which(name)
        if path:
            return name, path
    for path in CHROME_PATHS:
        if os.path.exists(path):
            return "chrome", path
    for name in ("google-chrome", "chromium", "chromium-browser"):
        path = shutil.which(name)
        if path:
            return "chrome", path
    if shutil.which("qlmanage"):
        return "qlmanage", "qlmanage"
    return "", ""


def run(cmd, timeout=120) -> bool:
    try:
        return subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=timeout, check=False).returncode == 0
    except (subprocess.TimeoutExpired, OSError):
        return False


def render(svg_path: str, out_png: str, w: int, h: int, renderer: Tuple[str, str]) -> bool:
    name, exe = renderer
    out_dir = os.path.dirname(os.path.abspath(out_png))
    if name == "rsvg-convert":
        return run([exe, "-w", str(w), "-h", str(h), "-o", out_png, svg_path]) and os.path.exists(out_png)
    if name == "inkscape":
        return run([exe, svg_path, "--export-type=png", f"--export-width={w}", f"--export-height={h}", f"--export-filename={out_png}"]) and os.path.exists(out_png)
    if name == "magick":
        return run([exe, "-background", "none", "-density", "384", svg_path, "-resize", f"{w}x{h}!", out_png]) and os.path.exists(out_png)
    if name == "chrome":
        with open(svg_path, "r", encoding="utf-8") as f:
            svg = f.read()
        page = os.path.join(out_dir, f".{os.path.basename(out_png)}.html")
        with open(page, "w", encoding="utf-8") as f:
            f.write(f'<!doctype html><html><head><meta charset="utf-8"><style>html,body{{margin:0;background:transparent;overflow:hidden}}svg{{display:block}}</style></head><body>{svg}</body></html>')
        ok = run([exe, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run", "--default-background-color=00000000",
                  f"--window-size={w},{h}", f"--screenshot={os.path.abspath(out_png)}", "file://" + os.path.abspath(page)], timeout=180)
        os.remove(page)
        return ok and os.path.exists(out_png)
    if name == "qlmanage":
        run([exe, "-t", "-s", str(max(w, h)), "-o", out_dir, svg_path])
        produced = os.path.join(out_dir, os.path.basename(svg_path) + ".png")
        if not os.path.exists(produced):
            return False
        os.replace(produced, out_png)
        pw, ph = png_size(out_png)
        if (pw, ph) != (w, h):  # Quick Look letterboxes; crop to the canvas, never squash
            run(["sips", "-c", str(h), str(w), out_png])
        return True
    return False


# ---------------------------------------------------------------- png helpers
def png_size(path: str) -> Tuple[int, int]:
    with open(path, "rb") as f:
        head = f.read(24)
    return struct.unpack(">II", head[16:24]) if head[:8] == b"\x89PNG\r\n\x1a\n" else (0, 0)


def corner_alpha(path: str) -> Optional[int]:
    """Alpha of the top-left pixel (stdlib PNG decode of the first scanline); None if not RGBA."""
    with open(path, "rb") as f:
        data = f.read()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    pos, idat, colour_type = 8, b"", 0
    while pos < len(data):
        length = struct.unpack(">I", data[pos:pos + 4])[0]
        tag, body = data[pos + 4:pos + 8], data[pos + 8:pos + 8 + length]
        pos += 12 + length
        if tag == b"IHDR":
            colour_type = body[9]
        elif tag == b"IDAT":
            idat += body
        elif tag == b"IEND":
            break
    if colour_type != 6:
        return None  # no alpha channel at all: treated as opaque by callers
    try:
        raw = zlib.decompressobj().decompress(idat, 8)  # filter byte + first pixel is enough
    except zlib.error:
        return None
    return raw[4] if len(raw) >= 5 else None  # filters on the first pixel of the first row are identity


def write_ico(png_paths, ico_path: str) -> None:
    images = []
    for path in png_paths:
        with open(path, "rb") as f:
            data = f.read()
        w, h = struct.unpack(">II", data[16:24])
        images.append((w, h, data))
    header = struct.pack("<HHH", 0, 1, len(images))
    offset = 6 + 16 * len(images)
    entries, blobs = [], []
    for w, h, data in images:
        entries.append(struct.pack("<BBBBHHII", w if w < 256 else 0, h if h < 256 else 0, 0, 0, 1, 32, len(data), offset))
        blobs.append(data)
        offset += len(data)
    with open(ico_path, "wb") as f:
        f.write(header + b"".join(entries) + b"".join(blobs))


# ---------------------------------------------------------------- composition
class Exporter:
    def __init__(self, master_svg: str, renderer: Tuple[str, str]):
        self.master = master_svg
        self.renderer = renderer
        ET.register_namespace("", SVG_NS)
        ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")
        self.root = ET.parse(master_svg).getroot()
        self.view_box = self.root.get("viewBox") or f"0 0 {self.root.get('width', '512').rstrip('px')} {self.root.get('height', '512').rstrip('px')}"
        self.failures = 0

    def compose(self, out_png: str, w: int, h: int, mark: int, bg: str = "", transparent: bool = False, label: str = "") -> bool:
        """Master centred at `mark` px on a w x h canvas: solid `bg` hex, or transparent."""
        outer = ET.Element(f"{{{SVG_NS}}}svg", {"viewBox": f"0 0 {w} {h}", "width": str(w), "height": str(h)})
        if bg and not transparent:
            ET.SubElement(outer, f"{{{SVG_NS}}}rect", {"width": str(w), "height": str(h), "fill": f"#{bg}"})
        if mark > 0:
            inner = ET.SubElement(outer, f"{{{SVG_NS}}}svg", {"x": str((w - mark) // 2), "y": str((h - mark) // 2), "width": str(mark), "height": str(mark),
                                                             "viewBox": self.view_box, "preserveAspectRatio": "xMidYMid meet"})
            for child in list(self.root):
                inner.append(child)
        os.makedirs(os.path.dirname(os.path.abspath(out_png)), exist_ok=True)
        with tempfile.TemporaryDirectory(dir=os.path.dirname(os.path.abspath(out_png))) as tmp:
            wrapper = os.path.join(tmp, "wrapper.svg")
            ET.ElementTree(outer).write(wrapper, encoding="utf-8", xml_declaration=True)
            ok = render(wrapper, out_png, w, h, self.renderer)
        reason = ""
        if ok and transparent:
            alpha = corner_alpha(out_png)
            if alpha is None or alpha == 255:
                ok, reason = False, "renderer flattened transparency (install rsvg-convert or Google Chrome)"
                os.remove(out_png)
        if ok and png_size(out_png) != (w, h):
            ok, reason = False, f"rendered {png_size(out_png)} instead of {(w, h)}"
        self.failures += 0 if ok else 1
        print(f"  {'✓' if ok else '✗'} {label or os.path.relpath(out_png)}{' — ' + reason if reason else ''}")
        return ok


def build_brand_guide_html(brand_name: str, svg_content: str, out_path: str) -> None:
    """Standalone HTML brand book. The SVG is embedded as an image so any script inside it stays inert."""
    safe_name = html.escape(brand_name, quote=True)
    logo_img = f'<img src="data:image/svg+xml;base64,{base64.b64encode(svg_content.encode("utf-8")).decode("ascii")}" alt="{safe_name} logomark">'
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{safe_name} — Brand Identity Guidelines</title>
    <style>
        :root {{ --bg: #090D16; --surface: #131A29; --border: #232E45; --text-primary: #F8FAFC; --text-muted: #94A3B8; --primary: #4F46E5; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: var(--bg); color: var(--text-primary); margin: 0; padding: 40px 20px; }}
        .container {{ max-width: 960px; margin: 0 auto; }}
        header {{ border-bottom: 1px solid var(--border); padding-bottom: 24px; margin-bottom: 40px; }}
        h1 {{ font-size: 2.2rem; margin: 0 0 8px 0; font-weight: 700; }}
        .badge {{ background: var(--primary); padding: 4px 10px; border-radius: 999px; font-size: 0.8rem; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 24px; margin-bottom: 40px; }}
        .card {{ background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 24px; text-align: center; }}
        .logo-preview {{ max-width: 180px; height: 180px; margin: 0 auto 16px auto; display: flex; align-items: center; justify-content: center; }}
        .logo-preview img {{ max-width: 100%; max-height: 100%; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <span class="badge">Production Brand Specification</span>
            <h1>{safe_name}</h1>
            <p style="color: var(--text-muted);">Visual Identity System &amp; Asset Manifest</p>
        </header>
        <div class="grid">
            <div class="card">
                <h3>Primary Logomark</h3>
                <div class="logo-preview">{logo_img}</div>
                <p style="color: var(--text-muted); font-size: 0.85rem;">Master Vector (SVG)</p>
            </div>
            <div class="card" style="background: #ffffff; color: #111;">
                <h3 style="color: #111;">Monochrome Contrast</h3>
                <div class="logo-preview" style="filter: grayscale(100%) contrast(200%);">{logo_img}</div>
                <p style="color: #666; font-size: 0.85rem;">1-Bit Light Background</p>
            </div>
        </div>
    </div>
</body>
</html>
"""
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(page)


# ---------------------------------------------------------------- main
def main() -> None:
    parser = argparse.ArgumentParser(description="Export favicons, app icons, social cards, and a brand book from a master SVG (stdlib; uses the SVG renderer on the machine)")
    parser.add_argument("--svg", required=True, help="Path to the master logo SVG")
    parser.add_argument("--output-dir", default="dist/brand_assets", help="Target output directory")
    parser.add_argument("--brand-name", default="Brand Identity", help="Brand name for the brand book")
    parser.add_argument("--platforms", default="web", help="Comma list of web,ios,android (default web)")
    parser.add_argument("--icon-bg", default="0F172A", help="Hex (no #) background for opaque app icons and social cards")
    args = parser.parse_args()

    if not os.path.exists(args.svg):
        print(f"❌ Error: SVG file '{args.svg}' not found.")
        sys.exit(1)
    platforms = {p.strip() for p in args.platforms.split(",") if p.strip()}
    unknown = platforms - {"web", "ios", "android"}
    if unknown:
        print(f"❌ Error: unknown platform(s) {', '.join(sorted(unknown))}; use web, ios, android")
        sys.exit(1)
    renderer = find_renderer()
    if not renderer[0]:
        print("❌ Error: no SVG renderer found. Install rsvg-convert (librsvg), Inkscape, ImageMagick, or Google Chrome.")
        sys.exit(2)
    print(f"🎨 Rendering {args.svg} with {renderer[0]}" + (" (opaque outputs only: Quick Look flattens transparency)" if renderer[0] == "qlmanage" else ""))
    try:
        ex = Exporter(args.svg, renderer)
    except ET.ParseError as err:
        print(f"❌ Error: the SVG is not well-formed XML ({err}).")
        sys.exit(1)
    os.makedirs(args.output_dir, exist_ok=True)
    bg = args.icon_bg

    if "ios" in platforms:
        ios_dir = os.path.join(args.output_dir, "ios", "AppIcon.appiconset")
        ex.compose(os.path.join(ios_dir, "icon-1024.png"), 1024, 1024, 800, bg, label="ios/AppIcon.appiconset/icon-1024.png (opaque, square corners; system applies the mask)")
        for size in IOS_SIZES:
            ex.compose(os.path.join(ios_dir, f"icon-{size}.png"), size, size, int(size * 0.78), bg, label=f"ios/AppIcon.appiconset/icon-{size}.png")
    if "android" in platforms:
        base = os.path.join(args.output_dir, "android")
        ex.compose(os.path.join(base, "mipmap-xxxhdpi", "ic_launcher_foreground.png"), ADAPTIVE_CANVAS, ADAPTIVE_CANVAS, ADAPTIVE_SAFE, transparent=True,
                   label="android/mipmap-xxxhdpi/ic_launcher_foreground.png (108 dp canvas, mark within 66 dp safe zone, transparent)")
        ex.compose(os.path.join(base, "mipmap-xxxhdpi", "ic_launcher_background.png"), ADAPTIVE_CANVAS, ADAPTIVE_CANVAS, 0, bg, label=f"android/mipmap-xxxhdpi/ic_launcher_background.png (solid #{bg})")
        for density, size in ANDROID_LEGACY.items():
            ex.compose(os.path.join(base, f"mipmap-{density}", "ic_launcher.png"), size, size, int(size * 0.72), bg, label=f"android/mipmap-{density}/ic_launcher.png ({size}px)")
        ex.compose(os.path.join(base, "play-store", "icon-512.png"), 512, 512, 400, bg, label="android/play-store/icon-512.png")
        ex.compose(os.path.join(base, "play-store", "feature-graphic-1024x500.png"), 1024, 500, 300, bg, label="android/play-store/feature-graphic-1024x500.png")
        print("  ℹ ic_launcher_monochrome (432 px alpha glyph) and the 24 dp notification icon are authored as single-colour SVGs; see references/brand-identity.md §5")
    if "web" in platforms:
        favicon_pngs = []
        for name, w, h, mark, transparent in WEB_SPECS:
            out_file = os.path.join(args.output_dir, name)
            if ex.compose(out_file, w, h, mark, bg, transparent=transparent, label=f"{name} ({w}x{h})") and w in (16, 32, 48):
                favicon_pngs.append(out_file)
        if favicon_pngs:
            write_ico(favicon_pngs, os.path.join(args.output_dir, "favicon.ico"))
            print("  ✓ favicon.ico (multi-resolution bundle)")
        with open(args.svg, "r", encoding="utf-8") as f:
            svg_content = f.read()
        build_brand_guide_html(args.brand_name, svg_content, os.path.join(args.output_dir, "brand_guidelines.html"))
        print("  ✓ brand_guidelines.html (standalone brand book)")

    if ex.failures:
        print(f"\n⚠ {ex.failures} asset(s) failed; nothing was written for them. Fix the renderer and re-run.")
        sys.exit(3)
    print(f"\n🎉 Assets compiled to '{args.output_dir}'")


if __name__ == "__main__":
    main()
