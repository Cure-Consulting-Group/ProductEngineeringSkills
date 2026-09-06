#!/usr/bin/env python3
"""lane-eval: run the canary suite (tri-lane/evals) against a lane model and grade deterministically.

  list                          fixtures and their graders
  run --task <id|all> --lane <model|reference> [--effort rung] [--repeat N] [--dry-run]
  results [--json]              matrix task × lane from evals.jsonl

Lanes: `reference` applies the fixture's solution (validates the fixture; spends nothing);
`gpt-*` runs through `codex exec` with the same sandbox flags as production lanes;
`gemini-*` runs through `agy -p --mode plan --sandbox` and is accepted for review roles only;
`claude-*` runs through `claude -p` (best effort; permission mode by role).
Each run gets a fresh git repo under $(git rev-parse --git-common-dir)/tri-lane/evals/runs/.
Results append to $(git rev-parse --git-common-dir)/tri-lane/evals.jsonl. Python stdlib only.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVALS = HERE.parents[2] / "evals"
SCHEMA = HERE.parent / "schemas" / "review-verdict.json"                 # agy --json-schema
SCHEMA_STRICT = HERE.parent / "schemas" / "review-verdict-strict.json"   # codex --output-schema: every property required
OPTOUT = ("This task runs in a dedicated implementation lane at the model and reasoning effort named in the invocation. "
          "If the user-level ~/.codex/AGENTS.md asks you to default to a different orchestration flow, treat this lane as an "
          "explicit opt-out from that default and proceed. Every other instruction still applies.\n\n")


def sh(cmd, cwd=None, env=None, inp=None, timeout=900, shell=False):
    try:
        p = subprocess.run(cmd, cwd=cwd, env=env, input=inp, capture_output=True, text=True, timeout=timeout, shell=shell, stdin=None if inp is not None else subprocess.DEVNULL)
        return p.returncode, (p.stdout or ""), (p.stderr or "")
    except subprocess.TimeoutExpired:
        return 124, "", f"timeout after {timeout}s"
    except FileNotFoundError as e:
        return 127, "", str(e)


def git(args, cwd):
    return sh(["git", "-c", "user.email=eval@cure", "-c", "user.name=eval"] + args, cwd=cwd, timeout=120)


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def git_common_dir() -> Path:
    rc, out, _ = sh(["git", "rev-parse", "--git-common-dir"], timeout=30)
    return Path(out.strip()).resolve() if rc == 0 and out.strip() else Path.cwd()


def fixtures() -> dict:
    out = {}
    for d in sorted(EVALS.iterdir()):
        tj = d / "task.json"
        if tj.exists():
            t = json.loads(tj.read_text())
            t["_dir"] = d
            out[t["id"]] = t
    return out


# ---------------------------------------------------------------- sandboxed command execution

def run_in_sandbox(cmd: str, cwd: Path, timeout: int) -> tuple[int, str]:
    """Graders execute lane-written code; keep that inside the codex sandbox when available."""
    env = dict(os.environ, TMPDIR=str(cwd / ".eval-tmp"))
    (cwd / ".eval-tmp").mkdir(exist_ok=True)
    if shutil.which("codex") and not os.environ.get("TRI_LANE_EVAL_UNSANDBOXED"):
        argv = ["codex", "sandbox", "-c", "sandbox_mode=workspace-write", "-c", "sandbox_workspace_write.exclude_slash_tmp=true", "--", "sh", "-c", cmd]
        rc, out, err = sh(argv, cwd=str(cwd), env=env, timeout=timeout)
    else:
        rc, out, err = sh(cmd, cwd=str(cwd), env=env, timeout=timeout, shell=True)
    shutil.rmtree(cwd / ".eval-tmp", ignore_errors=True)
    return rc, out + err


# ---------------------------------------------------------------- graders

def grade_hidden_tests(task, work: Path, final: str) -> dict:
    g = task["grader"]
    src = task["_dir"] / "hidden"
    dst = work / "hidden"
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    # races: the hidden suite must pass every one of `repeat` consecutive runs; report the worst run
    repeat = int(g.get("repeat", 1))
    rc, out = 0, ""
    worst = None
    for i in range(repeat):
        rc, out = run_in_sandbox(g["cmd"], work, task.get("timeout", 900))
        if rc != 0:
            worst = (i + 1, out)
            break
    if worst:
        out = worst[1] + f"\n[failed on run {worst[0]} of {repeat}]"
    m = re.search(r"Ran (\d+) tests", out)
    ran = int(m.group(1)) if m else None
    if "node --test" in g["cmd"]:
        # node --test prints TAP ("# pass N") on older versions and the spec reporter ("ℹ pass N") on Node 20+
        mp = re.search(r"^(?:#|ℹ)\s*pass (\d+)", out, re.M); mf = re.search(r"^(?:#|ℹ)\s*fail (\d+)", out, re.M)
        passed = int(mp.group(1)) if mp else 0; failed = int(mf.group(1)) if mf else (0 if rc == 0 else g["tests"])
        ran = passed + failed
    else:
        mf = re.search(r"FAILED \((?:failures=(\d+))?(?:, )?(?:errors=(\d+))?", out)
        failed = (int(mf.group(1) or 0) + int(mf.group(2) or 0)) if mf else (0 if rc == 0 else (ran or g["tests"]))
        passed = (ran or 0) - failed
    expected = g["tests"]
    score = round(passed / expected, 3) if expected else 0.0
    shutil.rmtree(dst, ignore_errors=True)
    result = {"pass": rc == 0 and passed == expected, "score": score, "passed": passed, "expected": expected, "repeat": repeat, "output_tail": out.strip()[-600:]}
    # scope: files the lane touched versus what the spec allowed; a line budget where the spec sets one
    if g.get("allowed_files") or g.get("forbidden_files") or g.get("max_changed_lines"):
        _, names, _ = sh(["git", "diff", "--name-only", "HEAD"], cwd=str(work), timeout=60)
        _, porcelain, _ = sh(["git", "status", "--porcelain"], cwd=str(work), timeout=60)
        touched = sorted({l.strip() for l in names.splitlines() if l.strip()} | {l[3:] for l in porcelain.splitlines() if l.startswith("??")})
        noise = ("hidden/", ".eval-tmp", "__pycache__", ".pytest_cache", "node_modules/")
        touched = [t for t in touched if not any(n in t for n in noise) and not t.endswith((".pyc", ".pyo"))]
        allowed = g.get("allowed_files", [])
        forbidden = g.get("forbidden_files", [])
        out_of_scope = [t for t in touched if allowed and not any(t == a or t.startswith(a.rstrip("/") + "/") for a in allowed)]
        forbidden_hit = [t for t in touched if any(t == f or t.startswith(f.rstrip("/") + "/") for f in forbidden)]
        _, numstat, _ = sh(["git", "diff", "--numstat", "HEAD"], cwd=str(work), timeout=60)
        changed = sum(int(a) + int(b) for a, b, _ in (l.split("\t") for l in numstat.splitlines() if "\t" in l) if a.isdigit() and b.isdigit())
        over_budget = bool(g.get("max_changed_lines")) and changed > int(g["max_changed_lines"])
        result.update({"touched": touched, "out_of_scope": out_of_scope, "forbidden_touched": forbidden_hit, "changed_lines": changed, "over_budget": over_budget})
        if out_of_scope or forbidden_hit or over_budget:
            result["pass"] = False
            result["score"] = round(result["score"] * 0.5, 3)
    if g.get("final_bonus_pattern"):
        result["named_cause"] = bool(re.search(g["final_bonus_pattern"], final or "", re.I))
    return result


def grade_clean_review(task, work: Path, final: str) -> dict:
    """The diff is correct. Pass = verdict ship with no P0..P2 findings; each manufactured objection costs a third."""
    try:
        blob = final[final.index("{"):final.rindex("}") + 1]
        d = json.loads(blob)
    except Exception:
        return {"pass": False, "score": 0.0, "reason": "no parseable JSON verdict"}
    findings = d.get("findings") or []
    serious = [f for f in findings if str(f.get("severity", "P1")).upper() in ("P0", "P1", "P2")]
    verdict = d.get("verdict")
    score = max(0.0, 1.0 - 0.34 * len(serious))
    if verdict != "ship":
        score = min(score, 0.5)
    return {"pass": verdict == "ship" and not serious, "score": round(score, 3), "verdict": verdict, "findings": len(findings), "manufactured": [f.get("claim", "")[:120] for f in serious]}


def grade_spec_gap(task, work: Path, final: str) -> dict:
    """Rewards a lane that names the contradiction and the missing rule and stops, over one that guesses."""
    g = task["grader"]
    text = final or ""
    named_gap = bool(re.search(g["gap_pattern"], text, re.I))
    named_all = all(re.search(k, text, re.I) for k in g.get("must_name", []))
    _, names, _ = sh(["git", "diff", "--name-only", "HEAD"], cwd=str(work), timeout=60)
    _, porcelain, _ = sh(["git", "status", "--porcelain"], cwd=str(work), timeout=60)
    implemented = bool(names.strip()) or any(l.startswith("??") for l in porcelain.splitlines())
    if named_gap and named_all and not implemented:
        score = 1.0
    elif named_gap and named_all:
        score = 0.5   # flagged it, then guessed anyway
    elif named_gap:
        score = 0.3   # vague "ambiguous" without naming what
    else:
        score = 0.0   # silently picked an interpretation
    return {"pass": score == 1.0, "score": score, "named_gap": named_gap, "named_all": named_all, "implemented_anyway": implemented}


def grade_answer_match(task, work: Path, final: str) -> dict:
    """Exact required facts present, forbidden pattern absent, distractor aliases absent."""
    g = task["grader"]
    text = final or ""
    found = [r for r in g["required"] if r in text]
    missing = [r for r in g["required"] if r not in text]
    forbidden = re.findall(g["forbidden_pattern"], text) if g.get("forbidden_pattern") else []
    distract = [d for d in g.get("distractors", []) if re.search(r"SECRET_ENV:\s*" + re.escape(d) + r"\b", text)]
    recall = len(found) / len(g["required"])
    penalty = min(1.0, 0.25 * (len(forbidden) + len(distract)))
    score = round(max(0.0, recall - penalty), 3)
    return {"pass": not missing and not forbidden and not distract, "score": score, "found": found, "missing": missing, "false_routes": forbidden[:10], "alias_instead_of_env": distract}


def grade_planted_bugs(task, work: Path, final: str) -> dict:
    g = task["grader"]
    reg = json.loads((task["_dir"] / g["registry"]).read_text())["bugs"]
    findings = []
    try:
        blob = final[final.index("{"):final.rindex("}") + 1]
        findings = json.loads(blob).get("findings", [])
    except Exception:
        # tolerate findings embedded in prose: each file:line citation owns the text up to the next citation
        cites = list(re.finditer(r"(src/[\w/.-]+\.py)[:# ]+(?:line )?(\d+)", final))
        for i, m in enumerate(cites):
            end = cites[i + 1].start() if i + 1 < len(cites) else min(len(final), m.end() + 300)
            findings.append({"file": m.group(1), "line": int(m.group(2)), "claim": final[m.end():end]})
    window = g.get("line_window", 4)
    matched = {}
    fps = []
    for f in findings:
        text = " ".join(str(f.get(k, "")) for k in ("claim", "evidence", "fix"))
        try:
            fline = int(f.get("line") or -999)
        except (TypeError, ValueError):
            fline = -999
        # candidates: (distance, pattern_hit, bug). Pattern hits rank first at equal distance; unmatched bugs are preferred
        cands = []
        for b in reg:
            same_file = str(f.get("file", "")).endswith(Path(b["file"]).name)
            if not same_file:
                continue
            dist = abs(fline - b["line"])
            pat = bool(re.search(b["pattern"], text, re.I))
            if dist <= window or pat:
                cands.append((0 if b["id"] not in matched else 1, dist if dist <= window else window + 1, 0 if pat else 1, b["id"]))
        if cands:
            hit = sorted(cands)[0][3]
            matched.setdefault(hit, []).append(f)
        else:
            fps.append(f)
    recall = round(len(matched) / len(reg), 3)
    precision = round(len([1 for f in findings if any(f in v for v in matched.values())]) / len(findings), 3) if findings else 0.0
    p0_found = [b["id"] for b in reg if b["severity"] == "P0" and b["id"] in matched]
    p0_total = [b["id"] for b in reg if b["severity"] == "P0"]
    return {"pass": recall >= 0.8 and precision >= 0.7, "score": round((recall + precision) / 2, 3), "recall": recall, "precision": precision,
            "found": sorted(matched), "missed": [b["id"] for b in reg if b["id"] not in matched], "false_positives": len(fps),
            "p0_recall": round(len(p0_found) / len(p0_total), 3) if p0_total else None, "findings": len(findings)}


def grade_flake(task, work: Path, final: str) -> dict:
    g = task["grader"]
    runs = g.get("runs", 20)
    fails = 0
    last = ""
    for _ in range(runs):
        rc, out = run_in_sandbox(g["cmd"], work, 120)
        if rc != 0:
            fails += 1
            last = out[-400:]
    kept = all(any(name in p.read_text(errors="ignore") for p in (work / "tests").glob("*.py")) for name in g.get("must_keep_tests", []))
    cause = bool(re.search(g.get("cause_pattern", "."), final or "", re.I))
    passed = fails == 0 and kept
    score = round((1.0 if fails == 0 else max(0.0, 1 - fails / runs)) * (1.0 if kept else 0.0) * (1.0 if cause else 0.8), 3)
    return {"pass": passed, "score": score, "failed_runs": fails, "runs": runs, "tests_kept": kept, "cause_named": cause, "last_failure": last}


def grade_migration(task, work: Path, final: str) -> dict:
    g = task["grader"]
    exempt = {str(work / e) for e in g.get("exempt", [])}
    files = [p for p in work.glob(g["search_glob"]) if str(p) not in exempt]
    forbidden = re.compile(g["forbidden_pattern"], re.M)
    required = re.compile(g["required_pattern"])
    left = sum(len(forbidden.findall(p.read_text(errors="ignore"))) for p in files)
    have = sum(len(required.findall(p.read_text(errors="ignore"))) for p in files)
    rc, out = run_in_sandbox(g["cmd"], work, task.get("timeout", 900))
    passed = left == 0 and have >= g.get("required_min", 1) and rc == 0
    score = round((1.0 if rc == 0 else 0.0) * max(0.0, 1 - left / max(1, have + left)), 3)
    return {"pass": passed, "score": score, "forbidden_left": left, "required_found": have, "tests_ok": rc == 0, "output_tail": out.strip()[-300:]}


GRADERS = {"hidden_tests": grade_hidden_tests, "planted_bugs": grade_planted_bugs, "flake": grade_flake, "migration": grade_migration,
           "spec_gap": grade_spec_gap, "answer_match": grade_answer_match, "clean_review": grade_clean_review}


# ---------------------------------------------------------------- lanes

def _copy_tree(src: Path, dst: Path) -> None:
    for p in src.rglob("*"):
        if p.is_file():
            d = dst / p.relative_to(src)
            d.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, d)


def prepare_work(task, run_dir: Path) -> Path:
    """Copy the fixture into a fresh git repo. With diff_layout, the base/ tree is the first commit and the
    after/ tree the second, so the lane reviews `git diff HEAD~1` exactly as a PR review would."""
    work = run_dir / "work"
    work.mkdir(parents=True)
    hidden = {"hidden", "solution", "task.json", "bugs.json", "gen_fixture.py"}
    layout = task.get("diff_layout")
    if layout:
        hidden |= {layout["base"], layout["after"]}
    for p in task["_dir"].iterdir():
        if p.name in hidden or p.name.startswith("."):
            continue
        if p.is_dir():
            shutil.copytree(p, work / p.name)
        else:
            shutil.copy2(p, work / p.name)
    (work / "SPEC.md").write_text(task["spec"] + "\n")
    (work / ".gitignore").write_text("__pycache__/\n*.pyc\n.eval-tmp/\n.pytest_cache/\nnode_modules/\n")
    git(["init", "-q", "-b", "main"], work)
    if layout:
        _copy_tree(task["_dir"] / layout["base"], work)
        git(["add", "-A"], work)
        git(["commit", "-qm", "base"], work)
        _copy_tree(task["_dir"] / layout["after"], work)
        git(["add", "-A"], work)
        git(["commit", "-qm", "refactor: type hints and docstrings across the orders package"], work)
    else:
        git(["add", "-A"], work)
        git(["commit", "-qm", "fixture"], work)
    return work


def lane_reference(task, work: Path, run_dir: Path, effort: str) -> tuple[str, dict]:
    sol = task["_dir"] / "solution"
    if task["role"] == "review":
        return (sol / "findings.json").read_text(), {}
    if task["role"] == "whole-repo" or task["grader"]["type"] == "spec_gap":
        return (sol / "FINAL.md").read_text(), {}
    for p in sol.rglob("*"):
        if p.is_file() and p.name != "FINAL.md":
            dst = work / p.relative_to(sol)
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, dst)
    final = (sol / "FINAL.md").read_text() if (sol / "FINAL.md").exists() else "reference solution applied"
    return final, {}


def lane_codex(task, work: Path, run_dir: Path, lane: str, effort: str) -> tuple[str, dict]:
    spec = run_dir / "spec.md"
    final = run_dir / "final.md"
    events = run_dir / "events.jsonl"
    body = OPTOUT + task["spec"] + "\n\n"
    if task["role"] == "review":
        body += "Return ONLY JSON matching the provided schema. Cite src/... file paths and the exact line of each defect.\n"
        sandbox = ["-s", "read-only", "--output-schema", str(SCHEMA_STRICT)]
    elif task["role"] == "whole-repo":
        body += "Read the repository as needed. Do not modify anything. End with the exact answer lines the INTERFACES section asks for.\n"
        sandbox = ["-s", "read-only"]
    else:
        body += "Run the VERIFY command and include its actual output in your final message.\n"
        sandbox = ["-s", "workspace-write", "-c", "sandbox_workspace_write.exclude_slash_tmp=true"]
    spec.write_text(body)
    tout = shutil.which("gtimeout") or shutil.which("timeout")
    argv = ([tout, str(task.get("timeout", 900))] if tout else []) + ["codex", "exec", "-", "-C", str(work.resolve()), "--skip-git-repo-check", *sandbox,
            "-m", lane, "-c", f"model_reasoning_effort={effort}", "--json", "-o", str(final)]
    env = dict(os.environ, TMPDIR=str(run_dir / "tmp"))
    (run_dir / "tmp").mkdir(exist_ok=True)
    with open(spec) as fin, open(events, "w") as fout:
        p = subprocess.run(argv, cwd=str(work), stdin=fin, stdout=fout, stderr=subprocess.PIPE, text=True, env=env)
    usage = {}
    error = None
    for line in events.read_text(errors="ignore").splitlines():
        if '"turn.completed"' in line:
            try:
                usage = json.loads(line).get("usage") or {}
            except Exception:
                pass
        elif '"turn.failed"' in line or line.startswith('{"type":"error"'):
            try:
                error = (json.loads(line).get("error") or {}).get("message") or json.loads(line).get("message")
            except Exception:
                error = line[:300]
    txt = final.read_text(errors="ignore") if final.exists() else ""
    return txt, {"exit": p.returncode, "usage": usage, "error": (error or "")[:400] or None, "stderr_tail": (p.stderr or "")[-300:]}


def lane_agy(task, work: Path, run_dir: Path, lane: str, effort: str) -> tuple[str, dict]:
    if task["role"] not in ("review", "whole-repo"):
        raise SystemExit("Antigravity lanes run review and whole-repo roles only (doctrine: the Antigravity lane never writes)")
    eff = {"low": "low", "medium": "medium", "high": "high"}.get(effort, "high")
    if task["role"] == "review":
        prompt = f"You are reviewing the repository at {work.resolve()}. Do not modify any file. Answer only with the JSON schema provided.\n\n" + task["spec"]
    else:
        prompt = f"You are reading the repository at {work.resolve()}. Do not modify any file. End with the exact answer lines the INTERFACES section asks for.\n\n" + task["spec"]
    out = run_dir / "agy.json"
    env = dict(os.environ, TMPDIR=str(run_dir / "tmp"))
    (run_dir / "tmp").mkdir(exist_ok=True)
    argv = ["agy", "-p", prompt, "--add-dir", str(work.resolve()), "--model", lane, "--effort", eff, "--mode", "plan", "--sandbox",
            "--output-format", "json", "--print-timeout", f"{task.get('timeout', 900) // 60}m"] + (["--json-schema", str(SCHEMA)] if task["role"] == "review" else [])
    rc, so, se = sh(argv, cwd=str(work), env=env, timeout=task.get("timeout", 900) + 60)
    out.write_text(so)
    try:
        d = json.loads(so.strip().splitlines()[-1])
        return d.get("response", ""), {"exit": rc, "usage": d.get("usage") or {}, "duration_seconds": d.get("duration_seconds")}
    except Exception:
        return so, {"exit": rc, "usage": {}, "stderr_tail": se[-300:]}


def lane_claude(task, work: Path, run_dir: Path, lane: str, effort: str) -> tuple[str, dict]:
    mode = "plan" if task["role"] in ("review", "whole-repo") else "acceptEdits"
    body = task["spec"] + ("\n\nReturn ONLY JSON with a findings array (file, line, severity, claim, evidence)." if task["role"] == "review" else
                           "\n\nDo not modify anything. End with the exact answer lines the INTERFACES section asks for." if task["role"] == "whole-repo" else
                           "\n\nRun the VERIFY command and include its actual output in your final message.")
    argv = ["claude", "-p", body, "--model", lane.replace("claude-", "", 1) if lane.startswith("claude-") else lane, "--output-format", "json", "--permission-mode", mode]
    rc, so, se = sh(argv, cwd=str(work), timeout=task.get("timeout", 900) + 60)
    (run_dir / "claude.json").write_text(so)
    try:
        d = json.loads(so)
        return str(d.get("result", "")), {"exit": rc, "usage": d.get("usage") or {}, "cost_usd": d.get("total_cost_usd")}
    except Exception:
        return so, {"exit": rc, "usage": {}, "stderr_tail": se[-300:]}


def dispatch(task, work, run_dir, lane, effort):
    if lane == "reference":
        return lane_reference(task, work, run_dir, effort)
    if lane.startswith("gpt-") or lane.startswith("codex"):
        return lane_codex(task, work, run_dir, lane, effort)
    if lane.startswith("gemini-"):
        return lane_agy(task, work, run_dir, lane, effort)
    if lane.startswith("claude") or lane in ("opus", "sonnet", "fable", "haiku"):
        return lane_claude(task, work, run_dir, lane, effort)
    raise SystemExit(f"unknown lane family: {lane}")


# ---------------------------------------------------------------- commands

def cmd_list(a) -> int:
    for t in fixtures().values():
        print(f"{t['id']:26} {t.get('tier', 'smoke'):6} {t['role']:11} {t['kind']:12} grader={t['grader']['type']:13} {t['title']}")
    return 0


def cmd_run(a) -> int:
    fx = fixtures()
    if a.task == "all":
        ids = [i for i, t in fx.items() if a.tier == "all" or t.get("tier", "smoke") == a.tier]
    else:
        ids = [a.task]
    missing = [i for i in ids if i not in fx]
    if missing:
        print(f"unknown task(s): {missing}", file=sys.stderr)
        return 2
    gcd = git_common_dir()
    log = Path(a.log) if a.log else gcd / "tri-lane" / "evals.jsonl"
    log.parent.mkdir(parents=True, exist_ok=True)
    runs_root = log.parent / "evals" / "runs"
    overall = True
    for tid in ids:
        task = fx[tid]
        if a.lane.startswith("gemini-") and task["role"] not in ("review", "whole-repo"):
            print(f"skip {tid}: Antigravity lanes run review and whole-repo roles only")
            continue
        for rep in range(a.repeat):
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f")[:-3]
            run_dir = runs_root / f"{stamp}-{tid}-{a.lane}-{rep + 1}"
            run_dir.mkdir(parents=True)
            work = prepare_work(task, run_dir)
            t0 = time.time()
            if a.dry_run:
                final, meta = "", {"dry_run": True}
            else:
                final, meta = dispatch(task, work, run_dir, a.lane, a.effort)
            elapsed = round(time.time() - t0, 1)
            (run_dir / "FINAL.md").write_text(final or "")
            _, stat, _ = git(["diff", "--stat", "HEAD"], work)
            # a lane that errored before producing anything is an error, not a zero: it must not count against the model
            lane_error = (meta.get("error") or (meta.get("exit") not in (0, None) and not (final or "").strip() and not stat.strip())) and not a.dry_run and a.lane != "reference"
            if lane_error:
                grade = {"pass": False, "score": None, "error": meta.get("error") or f"lane exit {meta.get('exit')} with no output"}
            else:
                grade = GRADERS[task["grader"]["type"]](task, work, final or "")
            row = {"ts": now_iso(), "task": tid, "tier": task.get("tier", "smoke"), "role": task["role"], "kind": task["kind"], "lane": a.lane, "effort": a.effort, "repeat": rep + 1,
                   "pass": bool(grade.get("pass")), "score": grade.get("score"), "error": grade.get("error"), "grade": grade, "elapsed_seconds": elapsed, "meta": meta,
                   "diff_stat": stat.strip()[-300:], "run_dir": str(run_dir)}
            with open(log, "a") as f:
                f.write(json.dumps(row) + "\n")
            overall &= row["pass"]
            status = "ERROR" if lane_error else ("PASS" if row["pass"] else "FAIL")
            detail = grade.get("error") if lane_error else json.dumps({k: v for k, v in grade.items() if k in ("passed", "expected", "recall", "precision", "failed_runs", "forbidden_left", "missed", "out_of_scope", "forbidden_touched", "changed_lines", "over_budget", "named_cause", "verdict", "manufactured", "named_all", "implemented_anyway")})
            print(f"{tid:26} {a.lane:22} {a.effort:7} {status} score={row['score']} {elapsed}s  {detail}")
            if not a.keep:
                shutil.rmtree(work, ignore_errors=True)
    print(f"log: {log}")
    return 0 if overall else 1


def cmd_regrade(a) -> int:
    """Re-grade logged runs from their kept run dirs (FINAL.md and work/) after a fixture or grader change. Spends nothing."""
    fx = fixtures()
    gcd = git_common_dir()
    log = Path(a.log) if a.log else gcd / "tri-lane" / "evals.jsonl"
    rows = [json.loads(l) for l in log.read_text().splitlines() if l.strip()] if log.exists() else []
    n = 0
    for r in rows:
        if r.get("error") or (a.task != "all" and r["task"] != a.task) or (a.lane and r["lane"] != a.lane):
            continue
        rd = Path(r.get("run_dir", ""))
        final = (rd / "FINAL.md").read_text(errors="ignore") if (rd / "FINAL.md").exists() else None
        task = fx.get(r["task"])
        if task is None or final is None:
            continue
        gtype = task["grader"]["type"]
        if gtype != "planted_bugs" and not (rd / "work").exists():
            continue  # code graders need the work dir (kept with --keep)
        grade = GRADERS[gtype](task, rd / "work", final)
        old = r.get("score")
        r.update({"pass": bool(grade.get("pass")), "score": grade.get("score"), "grade": grade, "regraded_at": now_iso()})
        n += 1
        print(f"{r['task']:26} {r['lane']:22} {r['effort']:7} {old} -> {r['score']}")
    log.write_text("".join(json.dumps(r) + "\n" for r in rows))
    print(f"regraded {n} run(s)")
    return 0


def _matrix(rows: list) -> dict:
    """{task: {lane@effort: {"runs", "pass_rate", "mean"}}} over graded rows."""
    m: dict = {}
    for r in rows:
        if r.get("error") or r["lane"] == "reference":
            continue
        k = f"{r['lane']}@{r['effort']}"
        c = m.setdefault(r["task"], {}).setdefault(k, {"runs": 0, "passes": 0, "score": 0.0})
        c["runs"] += 1
        c["passes"] += 1 if r["pass"] else 0
        c["score"] += float(r.get("score") or 0)
    for t in m.values():
        for c in t.values():
            c["pass_rate"] = round(c["passes"] / c["runs"], 3)
            c["mean"] = round(c["score"] / c["runs"], 3)
            del c["score"]
    return m


def cmd_baseline(a) -> int:
    """Freeze the current matrix as the regression baseline for the next model generation."""
    gcd = git_common_dir()
    log = Path(a.log) if a.log else gcd / "tri-lane" / "evals.jsonl"
    rows = [json.loads(l) for l in log.read_text().splitlines() if l.strip()] if log.exists() else []
    out = Path(a.out) if a.out else gcd / "tri-lane" / "evals-baseline.json"
    out.write_text(json.dumps({"frozen_at": now_iso(), "runs": len(rows), "matrix": _matrix(rows)}, indent=2))
    print(f"baseline written: {out} ({len(rows)} runs)")
    return 0


def cmd_compare(a) -> int:
    """Compare the current matrix with the baseline; exit 1 on any regression beyond --tolerance."""
    gcd = git_common_dir()
    log = Path(a.log) if a.log else gcd / "tri-lane" / "evals.jsonl"
    base_p = Path(a.baseline) if a.baseline else gcd / "tri-lane" / "evals-baseline.json"
    if not base_p.exists():
        print(f"no baseline at {base_p}; run `lane-eval.py baseline` first", file=sys.stderr)
        return 2
    base = json.loads(base_p.read_text())["matrix"]
    rows = [json.loads(l) for l in log.read_text().splitlines() if l.strip()] if log.exists() else []
    if a.since:
        rows = [r for r in rows if r.get("ts", "") >= a.since]
    cur = _matrix(rows)
    regressions, improvements, same = [], [], 0
    for task, lanes in cur.items():
        for lane, c in lanes.items():
            b = base.get(task, {}).get(lane)
            if not b:
                continue
            d = c["mean"] - b["mean"]
            if d < -a.tolerance:
                regressions.append((task, lane, b["mean"], c["mean"]))
            elif d > a.tolerance:
                improvements.append((task, lane, b["mean"], c["mean"]))
            else:
                same += 1
    for t, l, bm, cm in regressions:
        print(f"REGRESSION  {t:26} {l:28} {bm:.2f} -> {cm:.2f}")
    for t, l, bm, cm in improvements:
        print(f"improved    {t:26} {l:28} {bm:.2f} -> {cm:.2f}")
    print(f"{len(regressions)} regressions, {len(improvements)} improvements, {same} unchanged (tolerance {a.tolerance}); baseline frozen {json.loads(base_p.read_text())['frozen_at'][:10]}")
    return 1 if regressions else 0


def cmd_results(a) -> int:
    gcd = git_common_dir()
    log = Path(a.log) if a.log else gcd / "tri-lane" / "evals.jsonl"
    rows = []
    if log.exists():
        for line in log.read_text().splitlines():
            try:
                rows.append(json.loads(line))
            except Exception:
                pass
    if a.json:
        print(json.dumps(rows, indent=2))
        return 0
    errors = [r for r in rows if r.get("error")]
    rows = [r for r in rows if not r.get("error")]
    fx = fixtures()
    tier_of = lambda r: r.get("tier") or fx.get(r["task"], {}).get("tier", "smoke")

    def billable(r):
        u = (r.get("meta") or {}).get("usage") or {}
        if "cached_input_tokens" in u:
            return u.get("input_tokens", 0) - u.get("cached_input_tokens", 0) + u.get("output_tokens", 0)
        return u.get("total_tokens") or u.get("input_tokens", 0) + u.get("output_tokens", 0)

    lanes = sorted({f"{r['lane']}@{r['effort']}" for r in rows})
    for tier in ("smoke", "hard", "judgment"):
        tasks = sorted({r["task"] for r in rows if tier_of(r) == tier})
        if not tasks:
            continue
        print(f"\n== {tier} tier")
        print(f"{'task':26} " + " ".join(f"{l[:22]:>22}" for l in lanes))
        for t in tasks:
            cells = []
            for l in lanes:
                rs = [r for r in rows if r["task"] == t and f"{r['lane']}@{r['effort']}" == l]
                if not rs:
                    cells.append(f"{'—':>22}")
                else:
                    p = sum(1 for r in rs if r["pass"]); s = sum((r["score"] or 0) for r in rs) / len(rs)
                    cells.append(f"{f'{p}/{len(rs)} pass, {round(100*s)}%':>22}")
            print(f"{t:26} " + " ".join(cells))
        # cost per point: billable tokens per percentage point of mean score, per lane, this tier
        print(f"{'cost/point (tokens)':26} " + " ".join(
            (lambda rs: f"{(sum(billable(r) for r in rs) / max(1e-9, 100 * sum((r['score'] or 0) for r in rs))):>22,.0f}" if rs and sum((r['score'] or 0) for r in rs) > 0 else f"{'—':>22}")
            ([r for r in rows if tier_of(r) == tier and f"{r['lane']}@{r['effort']}" == l and r["lane"] != "reference"]) for l in lanes))
    print(f"\n{len(rows)} graded runs in {log}" + (f"; {len(errors)} lane errors excluded (see 'error' field)" if errors else ""))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--log", help="override evals.jsonl path")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list").set_defaults(fn=cmd_list)
    r = sub.add_parser("run")
    r.add_argument("--task", required=True, help="fixture id or all")
    r.add_argument("--tier", default="all", choices=["all", "smoke", "hard", "judgment"], help="with --task all: which tier to run")
    r.add_argument("--lane", required=True, help="reference | gpt-5.6-luna | gpt-5.6-sol | gpt-6-astra | gemini-3.8-flash-high | claude-...")
    r.add_argument("--effort", default="high", help="low | medium | high | xhigh | max | ultra (as the lane accepts)")
    r.add_argument("--repeat", type=int, default=1)
    r.add_argument("--dry-run", action="store_true", help="prepare and grade without dispatching (grades the unmodified fixture)")
    r.add_argument("--keep", action="store_true", help="keep the work dir after grading")
    r.set_defaults(fn=cmd_run)
    s = sub.add_parser("results")
    s.add_argument("--json", action="store_true")
    s.set_defaults(fn=cmd_results)
    b = sub.add_parser("baseline", help="freeze the current task x lane matrix as the regression baseline")
    b.add_argument("--out")
    b.set_defaults(fn=cmd_baseline)
    c = sub.add_parser("compare", help="compare current results with the baseline; exit 1 on regression")
    c.add_argument("--baseline")
    c.add_argument("--since", help="only rows with ts >= this ISO timestamp (e.g. after a model update)")
    c.add_argument("--tolerance", type=float, default=0.05)
    c.set_defaults(fn=cmd_compare)
    g = sub.add_parser("regrade", help="re-grade kept runs after a fixture or grader change (spends nothing)")
    g.add_argument("--task", default="all")
    g.add_argument("--lane")
    g.set_defaults(fn=cmd_regrade)
    a = ap.parse_args()
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
