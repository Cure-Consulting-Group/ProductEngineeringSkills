#!/usr/bin/env python3
"""
design_review_panel.py
Three-perspective design review: Creative Director, Product/UX Director, Design Systems/Production Director.
Builds one prompt per perspective from a brief and the artefacts (files under --out are excluded; SVG bodies
are listed by path unless --include-svg), and optionally runs them on the
CLIs found on PATH (claude, codex, gemini), one perspective per model family. Standard library only.

Usage:
    python3 design_review_panel.py --brief brief.md --artifacts "design/**/*.md" "design/**/*.json" "design/**/*.html" --out design/review --emit
    python3 design_review_panel.py --brief brief.md --artifacts ... --out review/ --run [--backends claude,codex,gemini] [--timeout 600]

--emit writes review/prompts/<perspective>.md for use with subagents or tri-lane lanes.
--run also writes review/results/<perspective>.md and review/synthesis.md (a template you fill in).
Reviews are read-only: every backend is invoked in its read-only or plan mode, with the artefacts inlined.
"""

import argparse
import glob
import json
import os
import shutil
import subprocess
import sys
from typing import Dict, List

PERSPECTIVES: Dict[str, Dict[str, str]] = {
    "creative-director": {
        "title": "Creative Director",
        "owns": "concept, originality, brand, art direction, visual storytelling, emotional resonance",
        "asks": "Is there one idea? Could another product look identical? What is memorable? Where is it generic? Does the register (expressive vs utility) fit the assignment?",
    },
    "ux-director": {
        "title": "Product / UX Director",
        "owns": "hierarchy, flows, usability, platform conventions, interaction, accessibility, responsive behaviour, scrolling model, states",
        "asks": "Is the primary action obvious in two seconds? Does it feel native on each platform? What breaks at 200 percent text or 320 px? Which state (empty, error, loading, offline, long content) is missing? Where is the user lost?",
    },
    "systems-director": {
        "title": "Design Systems / Production Director",
        "owns": "components, tokens, consistency, states, scalability, implementation cost, asset completeness",
        "asks": "Which values are not tokens? Which components lack a full state matrix? What costs more to build than it returns, and what is the cheaper equivalent? Which production assets are missing? Where do platforms drift from the shared brand without a reason?",
    },
}
CONTRACT = """
Return under 400 words, in this exact structure:
KEEP      three strengths, one line each
DEFECTS   the five most important defects, ranked, each with the artefact and line or element it refers to
DISSENT   one change you would make that the other perspectives will probably dislike, and why
VERDICT   ship | fix-first | rethink, with one sentence
Do not restate the brief. Do not propose a redesign. Judge what is in front of you against the standard:
could this plausibly have shipped from a top-tier product design team or an award-winning studio?
"""
MAX_BYTES = 120_000


def read_artifacts(patterns: List[str], out_dir: str, include_svg: bool) -> str:
    chunks, total = [], 0
    out_abs = os.path.abspath(out_dir)
    skipped_svg: List[str] = []
    for pat in patterns:
        for path in sorted(glob.glob(pat, recursive=True)):
            if not os.path.isfile(path) or os.path.abspath(path).startswith(out_abs + os.sep):
                continue
            if path.lower().endswith(".svg") and not include_svg:
                skipped_svg.append(path)
                continue
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                body = f.read()
            if total + len(body) > MAX_BYTES:
                body = body[: max(0, MAX_BYTES - total)] + "\n[truncated]"
            total += len(body)
            chunks.append(f"\n===== {path} =====\n{body}")
            if total >= MAX_BYTES:
                break
    if skipped_svg:
        chunks.append("\n===== SVG artefacts (bodies omitted; judge them from inventory.md and the specs; pass --include-svg to inline) =====\n" + "\n".join(skipped_svg))
    return "".join(chunks)


def build_prompt(key: str, brief: str, artifacts: str) -> str:
    p = PERSPECTIVES[key]
    return (f"You are the {p['title']} on a design review panel. You own: {p['owns']}.\n"
            f"You ask: {p['asks']}\n\nBRIEF\n{brief}\n\nARTEFACTS{artifacts}\n{CONTRACT}")


def backend_cmd(backend: str, prompt_path: str) -> List[str]:
    if backend == "claude":
        return ["claude", "-p", f"Read the review request in {prompt_path} and answer it.", "--permission-mode", "plan"]
    if backend == "codex":
        return ["codex", "exec", "-s", "read-only", f"Read the review request in {prompt_path} and answer it."]
    if backend == "gemini":
        return ["gemini", "-p", f"Read the review request in {prompt_path} and answer it."]
    raise ValueError(backend)


def main() -> None:
    parser = argparse.ArgumentParser(description="Three-perspective design review panel (prompts, optional CLI execution)")
    parser.add_argument("--brief", required=True, help="Markdown brief: goal, audience, register, platforms, constraints")
    parser.add_argument("--artifacts", nargs="*", default=[], help="Files or globs to review (md, svg, html, json)")
    parser.add_argument("--out", default="review", help="Output directory")
    parser.add_argument("--emit", action="store_true", help="Write the three prompts")
    parser.add_argument("--run", action="store_true", help="Run the prompts on available CLIs")
    parser.add_argument("--backends", default="claude,codex,gemini", help="Preferred backend per perspective, in order")
    parser.add_argument("--timeout", type=int, default=600, help="Seconds per review")
    parser.add_argument("--include-svg", action="store_true", help="Inline SVG bodies (large); by default only their paths are listed")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not (args.emit or args.run):
        parser.error("pass --emit and/or --run")

    with open(args.brief, "r", encoding="utf-8") as f:
        brief = f.read()
    artifacts = read_artifacts(args.artifacts, args.out, args.include_svg)
    prompts_dir = os.path.join(args.out, "prompts")
    os.makedirs(prompts_dir, exist_ok=True)
    prompt_paths = {}
    for key in PERSPECTIVES:
        path = os.path.join(prompts_dir, f"{key}.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(build_prompt(key, brief, artifacts))
        prompt_paths[key] = path
    summary: Dict[str, Dict[str, str]] = {k: {"prompt": v} for k, v in prompt_paths.items()}

    if args.run:
        preferred = [b for b in args.backends.split(",") if b]
        available = [b for b in preferred if shutil.which(b)]
        if not available:
            print("❌ none of the backends are on PATH; use --emit and run the prompts with subagents", file=sys.stderr)
            sys.exit(2)
        results_dir = os.path.join(args.out, "results")
        os.makedirs(results_dir, exist_ok=True)
        for i, key in enumerate(PERSPECTIVES):
            backend = available[i % len(available)]
            out_path = os.path.join(results_dir, f"{key}.md")
            print(f"▶ {PERSPECTIVES[key]['title']} on {backend} ...", flush=True)
            try:
                res = subprocess.run(backend_cmd(backend, os.path.abspath(prompt_paths[key])), capture_output=True, text=True, timeout=args.timeout, check=False)
                body = res.stdout.strip() or f"(no output; stderr: {res.stderr.strip()[:2000]})"
                status = "ok" if res.returncode == 0 and res.stdout.strip() else f"exit {res.returncode}"
            except subprocess.TimeoutExpired:
                body, status = "(timed out)", "timeout"
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(f"# {PERSPECTIVES[key]['title']} ({backend}, {status})\n\n{body}\n")
            summary[key].update({"backend": backend, "status": status, "result": out_path})
        synthesis = os.path.join(args.out, "synthesis.md")
        if not os.path.exists(synthesis):
            with open(synthesis, "w", encoding="utf-8") as f:
                f.write("# Panel synthesis\n\nLabel every defect, decide conflicts by register and the ten questions, fold the strongest ideas into one direction.\n\n"
                        "| # | Perspective | Finding | Label (Confirmed/Disputed/Unverified) | Action |\n|---|---|---|---|---|\n\n## Conflicts and decisions\n\n## Direction\n")
            summary["synthesis"] = {"path": synthesis}
    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        for k, v in summary.items():
            print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
