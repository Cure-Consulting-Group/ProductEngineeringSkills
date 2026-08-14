#!/usr/bin/env python3
"""run-evals.py — Golden-task eval harness for the Cure skill library (T30).

Runs the tasks in evals/tasks/ against headless agent CLIs and scores each run
with the task's deterministic score.sh gate. Two modes:

  --mode skill   Skill on/off A-B on the same backend: the "on" arm gets the
                 relevant skill(s) copied into the workdir's .claude/skills/;
                 the "off" arm runs bare. The delta is the skill's measured
                 effectiveness — the only honest answer to "does this skill
                 help".
  --mode model   Same tasks across backends (claude / gemini / codex), skills
                 on. Produces the runtime-selection matrix (T33).

Incremental gate (Ring 0):
  --changed <git-ref>   Map the diff vs <ref> to affected skills via
                        evals/index.json, run only their tasks at 1 rep,
                        exit 1 if any previously-passing task now fails
                        (compared against the newest evals/results/*.json).

Judge note: deterministic gates are the primary score. The optional rubric
judge must be a DIFFERENT model family than the candidate (self-preference
bias); the runner enforces this and skips judging when only same-family
CLIs are available.

Cost note: subscription CLIs are the execution vehicle (claude -p /
gemini -p / codex exec). Default reps=3 for sweeps, 1 for --changed.

Stdlib only. --help / --json / --dry-run.
"""

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TASKS_DIR = ROOT / "evals" / "tasks"
RESULTS_DIR = ROOT / "evals" / "results"
INDEX = ROOT / "evals" / "index.json"

# Backend command templates. {prompt} is substituted; cwd is the task workdir.
# --setting-sources project keeps user-level plugins out of the "off" arm.
BACKENDS = {
    "claude": ["claude", "-p", "{prompt}", "--permission-mode", "acceptEdits",
               "--setting-sources", "project", "--max-turns", "30"],
    "gemini": ["gemini", "-p", "{prompt}", "--yolo"],
    "codex":  ["codex", "exec", "--full-auto", "{prompt}"],
    # mock: writes nothing; exists so the harness itself can be smoke-tested.
    "mock":   ["sh", "-c", "true"],
}
FAMILY = {"claude": "anthropic", "gemini": "google", "codex": "openai", "mock": "mock"}
TIMEOUT_S = 600


def load_tasks(only=None):
    tasks = []
    for d in sorted(TASKS_DIR.iterdir()):
        tj = d / "task.json"
        if tj.exists():
            t = json.loads(tj.read_text())
            t["_dir"] = d
            if only is None or t["id"] in only:
                tasks.append(t)
    return tasks


def find_skill_dir(name):
    hits = list((ROOT / "skills").glob(f"*/{name}"))
    return hits[0] if hits else None


def setup_workdir(task, skills_on):
    wd = Path(tempfile.mkdtemp(prefix=f"eval-{task['id']}-"))
    for rel, content in task.get("fixtures", {}).items():
        p = wd / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
    subprocess.run(["git", "init", "-q"], cwd=wd, capture_output=True)
    if skills_on:
        for s in task["skills"]:
            src = find_skill_dir(s)
            if src:
                shutil.copytree(src, wd / ".claude" / "skills" / s)
    return wd


def run_arm(task, backend, skills_on, dry):
    label = f"{task['id']} [{backend}|skill={'on' if skills_on else 'off'}]"
    if dry:
        print(f"  would run: {label}")
        return None
    wd = setup_workdir(task, skills_on)
    cmd = [a.replace("{prompt}", task["prompt"]) for a in BACKENDS[backend]]
    t0 = time.time()
    try:
        r = subprocess.run(cmd, cwd=wd, capture_output=True, text=True, timeout=TIMEOUT_S)
        agent_ok = r.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        agent_ok = False
        r = None
    elapsed = round(time.time() - t0, 1)
    gate = subprocess.run(["sh", str(task["_dir"] / "score.sh"), str(wd)],
                          capture_output=True, text=True)
    passed = gate.returncode == 0
    # diff hygiene: files created beyond fixtures
    n_files = sum(1 for p in wd.rglob("*")
                  if p.is_file() and ".git" not in p.parts and ".claude" not in p.parts)
    shutil.rmtree(wd, ignore_errors=True)
    print(f"  {'PASS' if passed else 'FAIL'}  {label}  {elapsed}s")
    return {"task": task["id"], "backend": backend, "skill": skills_on,
            "pass": passed, "agent_exit_ok": agent_ok, "seconds": elapsed,
            "files_written": n_files}


def wilson(p, n, z=1.96):
    """Wilson score interval — honest about small n, never leaves [0,1]."""
    if n == 0:
        return (0.0, 1.0)
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / denom
    return (round(max(0, center - half), 3), round(min(1, center + half), 3))


def summarize(runs):
    out = {}
    for r in runs:
        if r is None:
            continue
        key = (r["task"], r["backend"], r["skill"])
        out.setdefault(key, []).append(r["pass"])
    result = {}
    for (t, b, s), v in out.items():
        p, n = sum(v) / len(v), len(v)
        result[f"{t}|{b}|{'on' if s else 'off'}"] = {
            "pass_rate": p, "n": n, "ci95": wilson(p, n),
            # flaky = mixed outcomes across reps: neither trustworthy pass nor clean fail
            "flaky": 0 < p < 1,
        }
    return result


def write_results(mode, runs, summary):
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M")
    out = {"mode": mode, "stamp": stamp, "summary": summary, "runs": [r for r in runs if r]}
    path = RESULTS_DIR / f"{stamp}-{mode}.json"
    path.write_text(json.dumps(out, indent=2) + "\n")
    regen_results_md()
    return path


def latest_results():
    files = sorted(RESULTS_DIR.glob("*.json")) if RESULTS_DIR.exists() else []
    return json.loads(files[-1].read_text()) if files else None


def skill_deltas(results):
    """on-vs-off pass-rate delta per skill, from a skill-mode results dict."""
    if not results or results.get("mode") != "skill":
        return {}
    by_task = {}
    for k, v in results["summary"].items():
        task, backend, arm = k.split("|")
        d = by_task.setdefault(task, {})
        d[arm] = v["pass_rate"]
        d["n_min"] = min(d.get("n_min", 999), v.get("n", 0))
    idx = json.loads(INDEX.read_text())["skill_to_tasks"]
    deltas = {}
    for skill, tids in idx.items():
        pairs = [(by_task[t]["on"], by_task[t]["off"]) for t in tids
                 if t in by_task and "on" in by_task[t] and "off" in by_task[t]
                 and by_task[t].get("n_min", 3) >= 3]
        if pairs:
            deltas[skill] = round(sum(on - off for on, off in pairs) / len(pairs), 3)
    return deltas


def regen_results_md():
    res = latest_results()
    md = ["# Eval Results (generated — do not edit)", ""]
    if not res:
        md.append("_No results yet. Run `python3 scripts/run-evals.py --mode skill`._")
    else:
        md += [f"Latest sweep: `{res['stamp']}` mode=`{res['mode']}`", "",
               "| key (task\\|backend\\|arm) | pass rate | n | 95% CI | flaky |", "|---|---|---|---|---|"]
        for k, v in sorted(res["summary"].items()):
            ci = v.get("ci95", ("—", "—"))
            md.append(f"| {k} | {v['pass_rate']:.0%} | {v['n']} | [{ci[0]}, {ci[1]}] | {'⚠️' if v.get('flaky') else ''} |")
        md += ["", "_Deltas require n≥3 per arm; single-rep results are directional only (t07, 2026-08-14)._"]
        d = skill_deltas(res)
        if d:
            md += ["", "## Skill on/off deltas", "", "| skill | Δ pass rate |", "|---|---|"]
            for s, dv in sorted(d.items(), key=lambda x: -x[1]):
                md.append(f"| {s} | {dv:+.0%} |")
    (ROOT / "evals" / "RESULTS.md").write_text("\n".join(md) + "\n")


def changed_skills(ref):
    diff = subprocess.run(["git", "diff", "--name-only", ref], cwd=ROOT,
                          capture_output=True, text=True).stdout.splitlines()
    skills = set()
    for f in diff:
        parts = Path(f).parts
        if len(parts) >= 3 and parts[0] == "skills":
            skills.add(parts[2])
    return skills


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--mode", choices=["skill", "model"], default="skill")
    ap.add_argument("--backends", default="claude", help="comma list for --mode model")
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--tasks", help="comma list of task ids to run")
    ap.add_argument("--changed", metavar="REF", help="Ring-0 gate: eval only skills changed vs REF")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    only = set(args.tasks.split(",")) if args.tasks else None
    reps = args.reps

    if args.changed:
        skills = changed_skills(args.changed)
        idx = json.loads(INDEX.read_text())["skill_to_tasks"]
        only = {t for s in skills for t in idx.get(s, [])}
        reps = 1
        if not only:
            print("Ring 0: no eval-covered skills changed — pass.")
            return 0

    tasks = load_tasks(only)
    if not tasks:
        print("No tasks matched."); return 1
    backends = args.backends.split(",") if args.mode == "model" else ["claude"]
    for b in backends:
        if b not in BACKENDS:
            print(f"unknown backend {b}"); return 1

    print(f"mode={args.mode} tasks={len(tasks)} reps={reps} backends={backends}")
    runs = []
    for task in tasks:
        for b in backends:
            arms = [True, False] if args.mode == "skill" else [True]
            for skills_on in arms:
                for _ in range(reps):
                    runs.append(run_arm(task, b, skills_on, args.dry_run))
    if args.dry_run:
        return 0

    summary = summarize(runs)
    path = write_results(args.mode, runs, summary)
    print(f"\nresults -> {path.relative_to(ROOT)}")

    if args.changed:
        prev = None
        files = sorted(RESULTS_DIR.glob("*.json"))
        if len(files) >= 2:
            prev = json.loads(files[-2].read_text())
        if prev:
            regressed = [k for k, v in summary.items()
                         if k in prev["summary"]
                         and prev["summary"][k]["pass_rate"] > 0 and v["pass_rate"] == 0]
            if regressed:
                print(f"❌ Ring 0 regression: {regressed}"); return 1
        print("✅ Ring 0: no regression.")

    if args.json:
        print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
