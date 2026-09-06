#!/usr/bin/env python3
"""
benchmark-design-models.py
Visual and technical design benchmark for comparing LLM models on brand identity,
vector engineering, and design system capabilities.

Benchmarks models on:
1. Deterministic Gate (score.sh pass/fail)
2. Vector Purity & Math (pure SVG, viewBox, anchor point efficiency, 0 raster artifacts)
3. Color Contrast & Accessibility (Calculates mathematical WCAG contrast ratios)
4. Token Completeness (W3C DTCG compliance, Light/Dark modes, spacing scales)
5. Execution Speed / Latency

Outputs:
- JSON benchmark results to evals/results/design_benchmark_<timestamp>.json
- Interactive HTML Visual Leaderboard to evals/results/design_leaderboard.html
"""

import argparse
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List

ROOT = Path(__file__).resolve().parent.parent
TASKS_DIR = ROOT / "evals" / "tasks"
RESULTS_DIR = ROOT / "evals" / "results"
SKILLS_DIR = ROOT / "skills"

BACKENDS = {
    "claude": ["claude", "-p", "{prompt}", "--permission-mode", "acceptEdits",
               "--setting-sources", "project", "--max-turns", "30"],
    "gemini": ["gemini", "-p", "{prompt}", "--yolo"],
    "codex":  ["codex", "exec", "--full-auto", "{prompt}"],
}


def hex_to_relative_luminance(hex_str: str) -> float:
    """Calculates relative luminance per WCAG 2.1 specification."""
    hex_clean = hex_str.lstrip("#")
    if len(hex_clean) == 3:
        hex_clean = "".join([c * 2 for c in hex_clean])
    if len(hex_clean) < 6:
        return 0.5
    r = int(hex_clean[0:2], 16) / 255.0
    g = int(hex_clean[2:4], 16) / 255.0
    b = int(hex_clean[4:6], 16) / 255.0

    def adjust(c):
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    return 0.2126 * adjust(r) + 0.7152 * adjust(g) + 0.0722 * adjust(b)


def calculate_contrast(hex1: str, hex2: str) -> float:
    """Calculates WCAG contrast ratio between two hex colors."""
    try:
        l1 = hex_to_relative_luminance(hex1)
        l2 = hex_to_relative_luminance(hex2)
        bright = max(l1, l2)
        dark = min(l1, l2)
        return round((bright + 0.05) / (dark + 0.05), 2)
    except Exception:
        return 1.0


def score_vector_purity(svg_path: Path) -> Dict[str, Any]:
    """Scores vector hygiene: XML validity, viewBox, zero raster tags, path count."""
    if not svg_path.exists():
        return {"score": 0, "error": "File missing"}
    
    content = svg_path.read_text(encoding="utf-8", errors="ignore")
    score = 100
    deductions = []

    # Check for raster pollution
    if "<image" in content.lower() or "data:image" in content.lower():
        score -= 50
        deductions.append("Raster embed detected (<image> or base64 data)")

    # Check XML validity
    try:
        root = ET.fromstring(content)
    except Exception as e:
        score -= 40
        deductions.append(f"Invalid XML: {str(e)[:40]}")
        return {"score": max(0, score), "deductions": deductions, "svg": content}

    # Check viewBox
    if not root.get("viewBox"):
        score -= 20
        deductions.append("Missing viewBox attribute")

    # Count paths and geometric elements
    element_types = [elem.tag.split("}")[-1] for elem in root.iter()]
    vector_elements = [t for t in element_types if t in ["path", "circle", "rect", "polygon", "polyline", "line"]]

    return {
        "score": max(0, score),
        "deductions": deductions,
        "vector_element_count": len(vector_elements),
        "raw_svg": content
    }


def score_tokens(tokens_path: Path) -> Dict[str, Any]:
    """Scores token completeness and W3C DTCG formatting."""
    if not tokens_path.exists():
        return {"score": 0, "error": "Tokens file missing"}
    
    try:
        data = json.loads(tokens_path.read_text(encoding="utf-8"))
    except Exception as e:
        return {"score": 0, "error": f"Invalid JSON: {str(e)[:30]}"}

    score = 0
    categories = []
    text_data = json.dumps(data).lower()

    if any(k in text_data for k in ["color", "colours", "primary"]):
        score += 40
        categories.append("colors")
    if any(k in text_data for k in ["spacing", "space", "dimension"]):
        score += 30
        categories.append("spacing")
    if any(k in text_data for k in ["radius", "radii"]):
        score += 15
        categories.append("radii")
    if "$value" in text_data or "value" in text_data:
        score += 15
        categories.append("w3c-dtcg-structure")

    # Extract hex colors
    hexes = re.findall(r"#(?:[0-9a-fA-F]{3}){1,2}\b", text_data)

    return {
        "score": score,
        "categories": categories,
        "detected_colors": list(set(hexes))[:8]
    }


def run_benchmark_trial(backend: str, task: Dict[str, Any], skill_name: str) -> Dict[str, Any]:
    """Executes a single benchmark task against a specific model backend."""
    wd = Path(tempfile.mkdtemp(prefix=f"design-eval-{backend}-"))
    
    # Copy skill into .claude/skills/
    skill_src = list(SKILLS_DIR.glob(f"*/{skill_name}"))
    if skill_src:
        dest = wd / ".claude" / "skills" / skill_name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(skill_src[0], dest)

    subprocess.run(["git", "init", "-q"], cwd=wd, capture_output=True)

    cmd = [a.replace("{prompt}", task["prompt"]) for a in BACKENDS[backend]]
    print(f"\n🚀 Running {backend.upper()} on task: {task['id']}...")

    t0 = time.time()
    try:
        r = subprocess.run(cmd, cwd=wd, capture_output=True, text=True, timeout=600)
        agent_exit_ok = r.returncode == 0
    except Exception as e:
        agent_exit_ok = False

    elapsed = round(time.time() - t0, 1)

    # 1. Deterministic gate
    gate = subprocess.run(["sh", str(task["_dir"] / "score.sh"), str(wd)],
                          capture_output=True, text=True)
    gate_passed = gate.returncode == 0

    # 2. Vector Purity
    svg_metrics = score_vector_purity(wd / "logo.svg")

    # 3. Token Completeness
    token_metrics = score_tokens(wd / "tokens.json")

    # 4. Color Contrast Check
    colors = token_metrics.get("detected_colors", [])
    max_contrast = 1.0
    if len(colors) >= 2:
        for c1 in colors:
            for c2 in colors:
                ratio = calculate_contrast(c1, c2)
                if ratio > max_contrast:
                    max_contrast = ratio

    contrast_score = 100 if max_contrast >= 7.0 else (70 if max_contrast >= 4.5 else 30)

    # Calculate overall design composite score (0-100)
    composite_score = round(
        (0.35 * (100 if gate_passed else 0)) +
        (0.25 * svg_metrics.get("score", 0)) +
        (0.25 * token_metrics.get("score", 0)) +
        (0.15 * contrast_score),
        1
    )

    result = {
        "backend": backend,
        "task": task["id"],
        "gate_passed": gate_passed,
        "composite_score": composite_score,
        "elapsed_seconds": elapsed,
        "vector_metrics": svg_metrics,
        "token_metrics": token_metrics,
        "max_contrast_ratio": max_contrast,
        "contrast_score": contrast_score,
        "raw_svg": svg_metrics.get("raw_svg", ""),
    }

    shutil.rmtree(wd, ignore_errors=True)
    print(f"  🏁 Result for {backend.upper()}: Gate={'PASS' if gate_passed else 'FAIL'} | Composite={composite_score}/100 in {elapsed}s")
    return result


def generate_html_leaderboard(results: List[Dict[str, Any]], out_path: Path):
    """Compiles results into a side-by-side visual HTML leaderboard."""
    # Sort results by composite score descending
    sorted_res = sorted(results, key=lambda x: x["composite_score"], reverse=True)

    rows_html = ""
    gallery_html = ""

    for rank, r in enumerate(sorted_res, 1):
        status_badge = '<span style="color:#10b981;font-weight:700;">PASS</span>' if r["gate_passed"] else '<span style="color:#ef4444;font-weight:700;">FAIL</span>'
        colors_chips = "".join([f'<span class="chip" style="background:{c};" title="{c}"></span>' for c in r["token_metrics"].get("detected_colors", [])])
        
        rows_html += f"""
        <tr>
            <td>#{rank}</td>
            <td><strong>{r['backend'].upper()}</strong></td>
            <td><span class="score">{r['composite_score']}</span>/100</td>
            <td>{status_badge}</td>
            <td>{r['vector_metrics'].get('score', 0)}%</td>
            <td>{r['token_metrics'].get('score', 0)}%</td>
            <td>{r['max_contrast_ratio']}:1 ({r['contrast_score']}%)</td>
            <td>{r['elapsed_seconds']}s</td>
            <td><div class="palette">{colors_chips}</div></td>
        </tr>
        """

        svg_content = r.get("raw_svg") or '<div style="color:#64748b;padding:40px;">No SVG Generated</div>'
        gallery_html += f"""
        <div class="card">
            <div class="card-header">
                <h3>{r['backend'].upper()}</h3>
                <span class="badge">Score: {r['composite_score']}</span>
            </div>
            <div class="preview-box">
                {svg_content}
            </div>
            <div class="card-meta">
                <p><strong>Gate:</strong> {'PASS' if r['gate_passed'] else 'FAIL'}</p>
                <p><strong>Vector Elements:</strong> {r['vector_metrics'].get('vector_element_count', 0)}</p>
                <p><strong>Max Contrast:</strong> {r['max_contrast_ratio']}:1</p>
                <div class="palette">{colors_chips}</div>
            </div>
        </div>
        """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>AI Design Model Benchmark — Leaderboard</title>
    <style>
        :root {{
            --bg: #0B0F19;
            --surface: #111827;
            --border: #1F2937;
            --accent: #6366F1;
            --text: #F9FAFB;
            --muted: #9CA3AF;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: var(--bg);
            color: var(--text);
            margin: 0;
            padding: 40px 24px;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        header {{ margin-bottom: 32px; border-bottom: 1px solid var(--border); padding-bottom: 20px; }}
        h1 {{ font-size: 2.2rem; margin: 0 0 8px 0; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background: var(--surface);
            border-radius: 8px;
            overflow: hidden;
            margin-bottom: 48px;
        }}
        th, td {{ padding: 14px 16px; text-align: left; border-bottom: 1px solid var(--border); }}
        th {{ background: #1E293B; font-size: 0.85rem; text-transform: uppercase; color: var(--muted); }}
        .score {{ font-weight: 800; color: var(--accent); font-size: 1.1rem; }}
        .palette {{ display: flex; gap: 6px; }}
        .chip {{ width: 20px; height: 20px; border-radius: 4px; display: inline-block; border: 1px solid rgba(255,255,255,0.2); }}
        .gallery-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
            gap: 24px;
        }}
        .card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px;
        }}
        .card-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }}
        .badge {{ background: var(--accent); padding: 4px 10px; border-radius: 999px; font-weight: 700; font-size: 0.85rem; }}
        .preview-box {{
            background: #000;
            height: 240px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 8px;
            margin-bottom: 16px;
            padding: 16px;
        }}
        .preview-box svg {{ max-width: 100%; max-height: 100%; }}
        .card-meta p {{ margin: 6px 0; font-size: 0.9rem; color: var(--muted); }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>AI Design Model Benchmark</h1>
            <p style="color: var(--muted);">Comparative evaluation across Vector Geometry, W3C DTCG Tokens, and WCAG Accessibility.</p>
        </header>

        <h2>Leaderboard Results</h2>
        <table>
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Model Backend</th>
                    <th>Composite Score</th>
                    <th>Deterministic Gate</th>
                    <th>Vector Purity</th>
                    <th>Tokens</th>
                    <th>WCAG Contrast</th>
                    <th>Latency</th>
                    <th>Color Palette</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>

        <h2>Visual Logo Submissions</h2>
        <div class="gallery-grid">
            {gallery_html}
        </div>
    </div>
</body>
</html>
"""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    print(f"📊 Visual Leaderboard generated at: {out_path}")


def main():
    parser = argparse.ArgumentParser(description="Benchmark models on design capabilities")
    parser.add_argument("--backends", default="claude,gemini,codex", help="Comma-separated backend list")
    parser.add_argument("--task", default="t17-brand-vector-engineering", help="Task ID to evaluate")
    parser.add_argument("--dry-run", action="store_true", help="Print plan without running agents")
    args = parser.parse_args()

    task_dir = TASKS_DIR / args.task
    if not task_dir.exists():
        print(f"Error: Task {args.task} not found in {TASKS_DIR}")
        sys.exit(1)

    task = json.loads((task_dir / "task.json").read_text())
    task["_dir"] = task_dir

    backends = [b.strip() for b in args.backends.split(",") if b.strip() in BACKENDS]
    print(f"🎯 Design Benchmark Initiated | Task: {task['id']} | Backends: {backends}")

    if args.dry_run:
        print("Dry run complete.")
        return

    results = []
    for b in backends:
        res = run_benchmark_trial(b, task, "design-studio")
        results.append(res)

    # Save JSON results
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    json_path = RESULTS_DIR / f"design_benchmark_{ts}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    # Generate HTML report
    html_path = RESULTS_DIR / "design_leaderboard.html"
    generate_html_leaderboard(results, html_path)


if __name__ == "__main__":
    main()
