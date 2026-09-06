#!/usr/bin/env python3
"""
export_asset_matrix.py
Production asset export pipeline for brand and product design. Stdlib only, macOS tools.

Given a master SVG, generates:
1. Web favicons (16x16, 32x32, 48x48, and a multi-resolution favicon.ico)
2. Mobile app icons (Apple touch icon 180x180, Android 192x192 and 512x512)
3. Social cards (OpenGraph 1200x630, Twitter 1500x500, avatar 400x400)
4. A standalone HTML brand book (brand_guidelines.html)

Rasterises with macOS `qlmanage`, resizes and pads with macOS `sips`, writes the .ico with the
standard library. Runs on macOS only; nothing is installed and nothing leaves the machine.

Usage:
    python3 export_asset_matrix.py --svg master_logo.svg --output-dir dist/brand_assets --brand-name "Brand"
"""

import argparse
import base64
import html
import os
import shutil
import struct
import subprocess
import sys

ASSET_SPECS = [
    {"name": "favicon-16x16.png", "width": 16, "height": 16, "category": "web"},
    {"name": "favicon-32x32.png", "width": 32, "height": 32, "category": "web"},
    {"name": "favicon-48x48.png", "width": 48, "height": 48, "category": "web"},
    {"name": "apple-touch-icon.png", "width": 180, "height": 180, "category": "mobile"},
    {"name": "android-chrome-192x192.png", "width": 192, "height": 192, "category": "mobile"},
    {"name": "android-chrome-512x512.png", "width": 512, "height": 512, "category": "mobile"},
    {"name": "avatar-400x400.png", "width": 400, "height": 400, "category": "social"},
    {"name": "opengraph-1200x630.png", "width": 1200, "height": 630, "category": "social"},
    {"name": "twitter-header-1500x500.png", "width": 1500, "height": 500, "category": "social"},
]
SOCIAL_BACKGROUND = "0F172A"  # slate-900, hex without '#', as sips expects


def sips(*args: str) -> bool:
    res = subprocess.run(["sips", *args], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    return res.returncode == 0


def render_svg_to_png(svg_path: str, output_png: str, size: int = 1500) -> bool:
    """Rasterise an SVG to a square PNG with macOS Quick Look (qlmanage)."""
    if not shutil.which("qlmanage"):
        return False
    out_dir = os.path.dirname(output_png) or "."
    subprocess.run(["qlmanage", "-t", "-s", str(size), "-o", out_dir, svg_path],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    rendered = os.path.join(out_dir, f"{os.path.basename(svg_path)}.png")
    if os.path.exists(rendered):
        os.replace(rendered, output_png)
        return True
    return False


def resize_square(master_png: str, out_file: str, size: int) -> bool:
    shutil.copyfile(master_png, out_file)
    return sips("-z", str(size), str(size), out_file)


def make_social_card(master_png: str, out_file: str, width: int, height: int) -> bool:
    """Mark centred on a solid background: resize the mark, then pad the canvas."""
    mark_size = min(height // 2, 240)
    shutil.copyfile(master_png, out_file)
    return (sips("-z", str(mark_size), str(mark_size), out_file)
            and sips("-p", str(height), str(width), "--padColor", SOCIAL_BACKGROUND, out_file))


def write_ico(png_paths, ico_path: str) -> None:
    """Multi-resolution .ico with PNG-encoded entries (supported by every current browser)."""
    images = []
    for path in png_paths:
        with open(path, "rb") as f:
            data = f.read()
        w, h = struct.unpack(">II", data[16:24])  # PNG IHDR width/height
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


def build_brand_guide_html(brand_name: str, svg_content: str, out_path: str) -> None:
    """Standalone HTML brand book. The SVG is embedded as an image so any script inside it stays inert."""
    safe_name = html.escape(brand_name, quote=True)
    svg_b64 = base64.b64encode(svg_content.encode("utf-8")).decode("ascii")
    logo_img = f'<img src="data:image/svg+xml;base64,{svg_b64}" alt="{safe_name} logomark">'
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


def main() -> None:
    parser = argparse.ArgumentParser(description="Export favicons, app icons, social cards, and a brand book from a master SVG (macOS, stdlib only)")
    parser.add_argument("--svg", required=True, help="Path to the master logo SVG")
    parser.add_argument("--output-dir", default="dist/brand_assets", help="Target output directory")
    parser.add_argument("--brand-name", default="Brand Identity", help="Brand name for the brand book")
    args = parser.parse_args()

    if not os.path.exists(args.svg):
        print(f"❌ Error: SVG file '{args.svg}' not found.")
        sys.exit(1)
    if not (shutil.which("qlmanage") and shutil.which("sips")):
        print("❌ Error: this exporter needs macOS (qlmanage and sips). Export the raster set from Illustrator or Figma instead.")
        sys.exit(2)

    os.makedirs(args.output_dir, exist_ok=True)
    master_png = os.path.join(args.output_dir, "master_base.png")
    print(f"🎨 Rendering master raster from: {args.svg}...")
    if not render_svg_to_png(args.svg, master_png, 1500):
        print("❌ Error: qlmanage could not rasterise the SVG (check that it is valid XML with a viewBox).")
        sys.exit(2)

    favicon_pngs = []
    for spec in ASSET_SPECS:
        out_file = os.path.join(args.output_dir, spec["name"])
        if spec["width"] == spec["height"]:
            ok = resize_square(master_png, out_file, spec["width"])
            if ok and spec["width"] in (16, 32, 48):
                favicon_pngs.append(out_file)
        else:
            ok = make_social_card(master_png, out_file, spec["width"], spec["height"])
        print(f"  {'✓' if ok else '✗'} {spec['name']} ({spec['width']}x{spec['height']})")

    if favicon_pngs:
        write_ico(favicon_pngs, os.path.join(args.output_dir, "favicon.ico"))
        print("  ✓ favicon.ico (multi-resolution bundle)")

    with open(args.svg, "r", encoding="utf-8") as f:
        svg_content = f.read()
    build_brand_guide_html(args.brand_name, svg_content, os.path.join(args.output_dir, "brand_guidelines.html"))
    print("  ✓ brand_guidelines.html (standalone brand book)")
    print(f"\n🎉 Brand asset matrix compiled to '{args.output_dir}'")


if __name__ == "__main__":
    main()
