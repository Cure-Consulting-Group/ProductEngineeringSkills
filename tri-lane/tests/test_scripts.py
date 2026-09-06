"""Unit tests for the cure-tri-lane scripts. Stdlib unittest only; no network, no quota.

Run:  python3 -m unittest discover -s tri-lane/tests -v
Every test that needs git builds a throwaway repo under a temp dir. Tests that need the codex
binary are skipped when it is absent (CI), so the sandbox itself is covered by lane-selftest.py
on a developer machine, not here.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "tri-lane" / "scripts"
HOOK = ROOT / "hooks" / "guard-lane-command.py"
PY = sys.executable
ENV = dict(os.environ, TRI_LANE_NO_POOLS="1")


def run(args, cwd=None, inp=None, env=ENV, timeout=120):
    p = subprocess.run([PY] + [str(a) for a in args], cwd=cwd, input=inp, capture_output=True, text=True, env=env, timeout=timeout)
    return p.returncode, p.stdout, p.stderr


def git(args, cwd):
    return subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t"] + args, cwd=cwd, capture_output=True, text=True)


def temp_repo():
    d = Path(tempfile.mkdtemp(prefix="tri-lane-test-"))
    repo = d / "repo"
    repo.mkdir()
    git(["init", "-q", "-b", "main"], repo)
    (repo / "README.md").write_text("hello\n")
    git(["add", "-A"], repo)
    git(["commit", "-qm", "init"], repo)
    return d, repo


class GuardHook(unittest.TestCase):
    CASES = [
        ("block", 'codex exec - -m gpt-5.6-luna < spec.txt'),
        ("pass", 'codex exec - -C ../wt/x -s workspace-write -m gpt-5.6-luna < spec.txt'),
        ("pass", 'codex exec review --base dev -o out.txt'),
        ("block", 'codex exec review --base dev -s danger-full-access'),
        ("block", 'codex exec -s read-only --dangerously-bypass-approvals-and-sandbox "x"'),
        ("block", 'codex exec - -s workspace-write --yolo < s'),
        ("block", 'codex -m gpt-5.6-luna exec - < spec'),
        ("pass", 'codex -m gpt-5.6-luna exec - -s read-only < spec'),
        ("block", 'agy -p "review this" --mode plan --output-format json'),
        ("block", 'agy -p "review this" --sandbox --output-format json'),
        ("pass", 'agy -p "review this" --mode plan --sandbox --output-format json'),
        ("pass", 'agy -p "/usage" --output-format json'),
        ("block", 'agy -p "fix it" --sandbox --mode accept-edits'),
        ("block", 'agy -p "fix it" --sandbox --mode plan -y'),
        ("block", 'agy -p "fix it" --sandbox --mode plan --approval-mode yolo'),
        ("pass", 'git status && ls -la'),
        ("block", 'git diff | codex exec - -m gpt-5.6-sol'),
        ("pass", 'echo "codex exec is a command" '),
        ("pass", 'gtimeout 600 codex exec - -C "$WT" -s workspace-write --skip-git-repo-check -m gpt-5.6-luna --json -o "$F" < "$S"'),
        ("block", 'cat > spec.txt <<EOF\nCONSTRAINTS run with -s workspace-write\nEOF\ncodex exec - -m gpt-5.6-luna < spec.txt'),
        ("block", 'codex exec review --base dev\ncodex exec - -m gpt-5.6-luna < s'),
        ("block", 'codex exec - -m gpt-5.6-luna < s # -s workspace-write'),
        ("pass", 'grep -r "agy -p" docs/'),
        ("pass", 'TMPDIR="$RUN/tmp" agy -p "$(cat "$SPEC")" --add-dir "$WT_RO" --model gemini-3.8-flash-high --effort high --mode plan --sandbox --json-schema x --output-format json --print-timeout 15m > "$OUT"'),
        ("block", 'T=gtimeout; $T 600 codex exec - -m gpt-5.6-luna < s || CODEX_HOME=/x /Users/me/.local/bin/codex exec "hi"'),
    ]

    def test_matrix(self):
        for want, cmd in self.CASES:
            rc, _, err = run([HOOK], inp=json.dumps({"tool_input": {"command": cmd}}))
            got = "block" if rc == 2 else "pass"
            self.assertEqual(got, want, f"{cmd!r}: {err.strip()}")

    def test_fails_open_on_garbage(self):
        rc, _, _ = run([HOOK], inp="not json")
        self.assertEqual(rc, 0)


class Toolchains(unittest.TestCase):
    def test_detects_markers_and_resolves_physical_paths(self):
        sys.path.insert(0, str(SCRIPTS))
        from lane_toolchains import detect, writable_roots
        d = Path(tempfile.mkdtemp())
        (d / "gradlew").write_text("")
        (d / "package.json").write_text("{}")
        names = [t["toolchain"] for t in detect(d)]
        self.assertIn("gradle", names)
        self.assertIn("node", names)
        for p in writable_roots(d):
            self.assertEqual(p, str(Path(p).resolve()), "writable roots must be physical paths")
        shutil.rmtree(d)


class Route(unittest.TestCase):
    def s(self, *args):
        rc, out, err = run([SCRIPTS / "lane-route.py", "suggest", *args])
        self.assertEqual(rc, 0, err)
        return json.loads(out)

    def test_routine_goes_to_luna(self):
        r = self.s("--role", "implement", "--kind", "impl")
        self.assertEqual(r["lane"], "gpt-5.6-luna")
        self.assertEqual(r["effort"], "medium")

    def test_risk_goes_to_sol_max(self):
        r = self.s("--role", "implement", "--kind", "android", "--risk", "payments")
        self.assertEqual((r["lane"], r["effort"]), ("gpt-5.6-sol", "max"))

    def test_terminal_work_suggests_astra_in_shadow(self):
        r = self.s("--role", "implement", "--kind", "ci")
        self.assertEqual(r["lane"], "gpt-6-astra")
        self.assertTrue(r["shadow"])

    def test_escalation_on_attempts(self):
        self.assertEqual(self.s("--role", "implement", "--kind", "impl", "--attempt", "2")["effort"], "xhigh")
        self.assertEqual(self.s("--role", "implement", "--kind", "impl", "--attempt", "3")["effort"], "ultra")

    def test_reviews_and_system(self):
        self.assertEqual(self.s("--role", "review", "--kind", "impl")["lane"], "gpt-5.6-sol")
        self.assertEqual(self.s("--role", "review", "--kind", "impl", "--risk", "payments")["lane"], "gpt-6-astra")
        self.assertEqual(self.s("--role", "system-review")["lane"], "gemini-3.8-flash-high")
        self.assertEqual(self.s("--role", "whole-repo")["lane"], "gemini-3.1-pro-high")

    def test_table_has_dates_and_sources(self):
        t = json.loads((ROOT / "skills" / "tri-lane" / "models.json").read_text())
        self.assertRegex(t["updated"], r"^\d{4}-\d{2}-\d{2}$")
        self.assertTrue(all(r.get("basis") for r in t["rules"]))


class Report(unittest.TestCase):
    def setUp(self):
        self.d, self.repo = temp_repo()
        self.wt = self.d / "wt"
        git(["worktree", "add", "--detach", "-q", str(self.wt), "HEAD"], self.repo)

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def report(self, *args):
        rc, out, err = run([SCRIPTS / "lane-report.py", "--worktree", self.wt, "--lane", "x", "--json", *args], cwd=self.repo)
        try:
            return rc, json.loads(out)
        except Exception:
            self.fail(f"no JSON: rc={rc} out={out[-300:]} err={err[-300:]}")

    def test_empty_diff_is_refused(self):
        rc, d = self.report()
        self.assertEqual((rc, d["STATUS"]), (3, "refused"))

    def test_main_checkout_refused(self):
        rc, out, err = run([SCRIPTS / "lane-report.py", "--worktree", self.repo, "--lane", "x"], cwd=self.repo)
        self.assertEqual(rc, 4)

    def test_out_of_scope_and_exec_config_block_verify(self):
        (self.wt / "README.md").write_text("x\n")
        (self.wt / "package.json").write_text("{}\n")
        rc, d = self.report("--files", "README.md", "--verify", "echo no", "--unsandboxed-verify")
        self.assertEqual(d["STATUS"], "partial")
        self.assertEqual(d["VERIFIED"], [])
        self.assertIn("package.json", d["EXEC_CONFIG_TOUCHED"])

    def test_base_counts_committed_work_and_runs_verify(self):
        (self.wt / "README.md").write_text("changed\n")
        git(["add", "-A"], self.wt); git(["commit", "-qm", "lane"], self.wt)
        rc, d = self.report("--base", "main", "--files", "README.md", "--verify", "echo ok", "--unsandboxed-verify")
        self.assertEqual((rc, d["STATUS"], d["BASE"]), (0, "complete", "main"))
        self.assertIn("ok", d["VERIFIED"][0]["output_tail"])

    def test_timeout_with_diff_is_still_evaluated(self):
        (self.wt / "README.md").write_text("changed\n")
        rc, d = self.report("--files", "README.md", "--verify", "true", "--unsandboxed-verify", "--status-hint", "timeout")
        self.assertEqual(d["STATUS"], "complete")
        self.assertTrue(any("wall-clock" in g for g in d["GAPS"]))

    def test_gradle_commands_get_no_daemon_offline(self):
        sys.path.insert(0, str(SCRIPTS))
        import importlib.util
        spec = importlib.util.spec_from_file_location("lr", SCRIPTS / "lane-report.py")
        lr = importlib.util.module_from_spec(spec); spec.loader.exec_module(lr)
        self.assertEqual(lr.gradle_safe("./gradlew test"), "./gradlew --no-daemon --offline test")
        self.assertEqual(lr.gradle_safe("cd app && gradle build"), "cd app && gradle --no-daemon --offline build")
        self.assertEqual(lr.gradle_safe("./gradlew --no-daemon test"), "./gradlew --no-daemon test")
        self.assertEqual(lr.gradle_safe("npm test"), "npm test")


class Worktree(unittest.TestCase):
    def setUp(self):
        self.d, self.repo = temp_repo()

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def lw(self, *args):
        return run([SCRIPTS / "lane-worktree.py", *args], cwd=self.repo)

    def test_lock_refuses_removal_then_salvages(self):
        rc, out, err = self.lw("add", "--task", "t", "--base", "main")
        self.assertEqual(rc, 0, err)
        wt = Path(json.loads(out)["worktree"])
        self.assertTrue(wt.exists())
        sleeper = subprocess.Popen(["sleep", "30"])
        try:
            self.lw("lock", "--task", "t", "--pid", str(sleeper.pid))
            self.assertEqual(self.lw("status", "--task", "t")[0], 3)
            self.assertEqual(self.lw("remove", "--task", "t", "--base", "main")[0], 3)
            self.assertTrue(wt.exists())
        finally:
            sleeper.kill(); sleeper.wait()
        self.lw("unlock", "--task", "t")
        (wt / "NEW.txt").write_text("salvage\n")
        rc, out, err = self.lw("remove", "--task", "t", "--base", "main", "--no-push")
        self.assertEqual(rc, 0, err)
        self.assertFalse(wt.exists())
        branches = git(["branch", "--list", "lane/t-salvage"], self.repo).stdout
        self.assertIn("lane/t-salvage", branches)

    def test_ro_twin_is_detached_and_unwritable(self):
        self.lw("add", "--task", "t", "--base", "main")
        rc, out, err = self.lw("add", "--task", "t", "--ro", "--base", "lane/t")
        self.assertEqual(rc, 0, err)
        ro = Path(json.loads(out)["worktree"])
        self.assertTrue(ro.exists())
        self.assertFalse(os.access(ro / "README.md", os.W_OK))
        self.assertEqual(self.lw("remove", "--task", "t", "--ro")[0], 0)


class Log(unittest.TestCase):
    def setUp(self):
        self.d, self.repo = temp_repo()
        self.log = self.d / "bench.jsonl"

    def tearDown(self):
        shutil.rmtree(self.d, ignore_errors=True)

    def ll(self, *args):
        return run([SCRIPTS / "lane-log.py", "--log", self.log, *args], cwd=self.repo)

    def test_start_end_records_model_and_autodiscovers_run_files(self):
        rc, out, err = self.ll("start", "--task", "x", "--arm", "tri-lane", "--kind", "impl", "--model", "claude-test", "--effort", "high")
        self.assertEqual(rc, 0, err)
        rd = self.d / "run" / "x"
        rd.mkdir(parents=True)
        (rd / "events.jsonl").write_text(json.dumps({"type": "turn.completed", "usage": {"input_tokens": 100, "cached_input_tokens": 40, "output_tokens": 10, "total_tokens": 110}}) + "\n")
        (rd / "agy.json").write_text(json.dumps({"usage": {"input_tokens": 5, "output_tokens": 1, "thinking_tokens": 0, "cache_read_tokens": 0, "total_tokens": 6}, "duration_seconds": 1}))
        (rd / "route-suggestion.json").write_text(json.dumps({"lane": "gpt-5.6-luna", "effort": "medium", "rule": "impl-routine"}))
        rc, out, err = self.ll("end", "--task", "x", "--route", "delegate", "--lane", "gpt-5.6-luna @ medium", "--status", "complete")
        self.assertEqual(rc, 0, err)
        row = json.loads(self.log.read_text().splitlines()[-1])
        self.assertEqual((row["model"], row["effort"]), ("claude-test", "high"))
        self.assertEqual(row["codex_lane"]["billable_tokens"], 70)
        self.assertEqual(row["agy"]["total_tokens"], 6)
        self.assertTrue(row["suggestion_followed"])

    def test_due_and_update(self):
        self.ll("start", "--task", "y", "--arm", "manual", "--model", "m", "--effort", "e")
        self.ll("end", "--task", "y", "--route", "manual", "--status", "complete")
        rc, out, _ = self.ll("due", "--within", "8", "--json")
        self.assertEqual(json.loads(out)[0]["task"], "y")
        self.ll("update", "--task", "y", "--escaped-defects", "0")
        rc, out, _ = self.ll("due", "--within", "8", "--json")
        self.assertEqual(json.loads(out), [])

    def test_report_blocks_on_model_freeze_and_windows(self):
        self.ll("start", "--task", "a", "--arm", "manual", "--model", "m1", "--effort", "e")
        self.ll("end", "--task", "a", "--route", "manual", "--status", "complete")
        self.ll("start", "--task", "b", "--arm", "tri-lane", "--model", "m2", "--effort", "e")
        self.ll("end", "--task", "b", "--route", "audit", "--status", "complete")
        rc, out, err = run([SCRIPTS / "benchmark-report.py", "--log", self.log, "--json"], cwd=self.repo)
        d = json.loads(out)
        self.assertFalse(d["decision"]["checks"]["model_frozen"]["pass"])
        self.assertFalse(d["decision"]["checks"]["defect_windows_closed"]["pass"])
        self.assertTrue(d["decision"]["verdict"].startswith("keep measuring"))


class Dashboard(unittest.TestCase):
    def test_renders_from_log_and_from_nothing(self):
        d = Path(tempfile.mkdtemp())
        log = d / "b.jsonl"
        row = {"task": "t", "arm": "tri-lane", "kind": "impl", "started_at": "2026-09-01T00:00:00+00:00", "ended_at": "2026-09-01T01:00:00+00:00", "elapsed_seconds": 3600,
               "claude": {"billable_tokens": 1000, "cache_read_input_tokens": 5000, "messages": 3}, "codex_lane": {"billable_tokens": 200}, "agy": {"total_tokens": 50},
               "findings": {"codex": {"confirmed": 2, "disputed": 0, "unverified": 1}}, "advisor": "ship", "rework": 0, "escaped_defects": 0, "pool_deltas": {"codex_weekly": 2.0}}
        log.write_text(json.dumps(row) + "\n")
        out = d / "dash.html"
        rc, so, se = run([SCRIPTS / "benchmark-dashboard.py", "--log", log, "--out", out])
        self.assertEqual(rc, 0, se)
        html = out.read_text()
        self.assertIn("<title>Tri-Lane Benchmark</title>", html)
        self.assertNotIn("__DATA__", html)
        self.assertIn('"task": "t"', html)
        rc, so, se = run([SCRIPTS / "benchmark-dashboard.py", "--log", d / "missing.jsonl", "--out", d / "empty.html"])
        self.assertEqual(rc, 0, se)
        self.assertIn("no tasks logged", (d / "empty.html").read_text())
        shutil.rmtree(d)


class Canary(unittest.TestCase):
    """The reference solution must score 100% on every fixture: this validates fixtures and graders together."""

    def test_reference_passes_every_fixture(self):
        d = Path(tempfile.mkdtemp())
        env = dict(ENV, TRI_LANE_EVAL_UNSANDBOXED="1")  # CI has no codex; the sandbox is covered by lane-selftest locally
        rc, out, err = run([SCRIPTS / "lane-eval.py", "--log", d / "evals.jsonl", "run", "--task", "all", "--lane", "reference"], env=env, timeout=600)
        self.assertEqual(rc, 0, out + err)
        rows = [json.loads(l) for l in (d / "evals.jsonl").read_text().splitlines()]
        self.assertEqual(len(rows), 11)
        self.assertEqual(sum(1 for r in rows if r["tier"] == "hard"), 5)
        for r in rows:
            self.assertTrue(r["pass"], f"{r['task']}: {r['grade']}")
            self.assertEqual(r["score"], 1.0, f"{r['task']}: {r['grade']}")
        shutil.rmtree(d)

    def test_unmodified_fixture_fails(self):
        d = Path(tempfile.mkdtemp())
        env = dict(ENV, TRI_LANE_EVAL_UNSANDBOXED="1")
        rc, out, err = run([SCRIPTS / "lane-eval.py", "--log", d / "evals.jsonl", "run", "--task", "impl-spec-service", "--lane", "reference", "--dry-run"], env=env, timeout=300)
        self.assertEqual(rc, 1)
        shutil.rmtree(d)

    def test_hard_tier_fixtures_fail_unmodified(self):
        d = Path(tempfile.mkdtemp())
        env = dict(ENV, TRI_LANE_EVAL_UNSANDBOXED="1")
        for t in ("cross-module-invariant", "concurrency-race", "needle-in-diff-review", "whole-repo-read", "underspecified-spec"):
            rc, out, err = run([SCRIPTS / "lane-eval.py", "--log", d / "e.jsonl", "run", "--task", t, "--lane", "reference", "--dry-run"], env=env, timeout=600)
            self.assertEqual(rc, 1, f"{t} should fail unmodified: {out[-300:]}")
        shutil.rmtree(d)

    def test_spec_gap_and_answer_graders(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("le", SCRIPTS / "lane-eval.py")
        le = importlib.util.module_from_spec(spec); spec.loader.exec_module(le)
        d, repo = temp_repo()
        fx = le.fixtures()
        gap = fx["underspecified-spec"]
        self.assertEqual(le.grade_spec_gap(gap, repo, "The spec is contradictory about negative qty and the rounding rule is unspecified; stopping.")["score"], 1.0)
        self.assertEqual(le.grade_spec_gap(gap, repo, "Implemented it, tests pass.")["score"], 0.0)
        (repo / "x.py").write_text("x")
        self.assertEqual(le.grade_spec_gap(gap, repo, "contradiction on negative qty and rounding unspecified, but I implemented ValueError")["score"], 0.5)
        wr = fx["whole-repo-read"]
        good = "UNAUTHENTICATED: /admin/export, /orders/bulk-delete, /users/impersonate\nSECRET_ENV: ORDERS_WEBHOOK_HMAC_KEY"
        self.assertTrue(le.grade_answer_match(wr, repo, good)["pass"])
        bad = "UNAUTHENTICATED: /admin/export, /api/v1/resource7\nSECRET_ENV: signing_secret"
        g = le.grade_answer_match(wr, repo, bad)
        self.assertFalse(g["pass"]); self.assertEqual(g["alias_instead_of_env"], ["signing_secret"]); self.assertEqual(len(g["false_routes"]), 1)
        shutil.rmtree(d)

    def test_planted_bug_grader_handles_prose_and_neighbours(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("le", SCRIPTS / "lane-eval.py")
        le = importlib.util.module_from_spec(spec); spec.loader.exec_module(le)
        task = le.fixtures()["review-planted-bugs"]
        prose = "src/capture.py:84 the sale already has an intent check locks the cashier out. src/capture.py line 86 logs the token. src/capture.py:200 unrelated nit."
        g = le.grade_planted_bugs(task, Path("."), prose)
        self.assertIn("B04-dead-intent-lockout", g["found"])
        self.assertIn("B03-token-in-logs", g["found"])
        self.assertEqual(g["false_positives"], 1)


if __name__ == "__main__":
    unittest.main()
