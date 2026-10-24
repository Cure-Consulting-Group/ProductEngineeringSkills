#!/usr/bin/env python3
"""Tests for scripts/export-antigravity.py rule export (T76) and the smoke script's static rule check.

Run: python3 scripts/test_export_antigravity.py   (exit 0 = all pass). Stdlib unittest, no agy needed.
"""
import importlib.util
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent


def load(name, file):
    spec = importlib.util.spec_from_file_location(name, HERE / file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


exp = load("export_antigravity", "export-antigravity.py")
smoke = load("antigravity_smoke", "antigravity-smoke.py")


def globs_of(fm: str) -> list:
    return exp.rule_globs(fm, "test.md")


class RuleGlobParsing(unittest.TestCase):
    def test_paths_block_list(self):
        self.assertEqual(globs_of('paths:\n  - "**/*.kt"\n  - **/*.java'), ["**/*.kt", "**/*.java"])

    def test_paths_comma_string(self):
        self.assertEqual(globs_of('paths: "**/*.sql, **/migrations/**"'), ["**/*.sql", "**/migrations/**"])

    def test_legacy_scalar_globs(self):  # the T76 bug: this used to export as globs: ""
        self.assertEqual(globs_of('globs: "**/*.tf,**/*.tfvars"'), ["**/*.tf", "**/*.tfvars"])

    def test_singular_glob_and_flow_list(self):
        self.assertEqual(globs_of("glob: ['**/*.go']"), ["**/*.go"])
        self.assertEqual(globs_of('paths: ["a/**", "b/**"]'), ["a/**", "b/**"])

    def test_brace_expansion_and_dedupe(self):
        self.assertEqual(globs_of('paths:\n  - "src/**/*.{ts,tsx}"\n  - "src/**/*.ts"'),
                         ["src/**/*.ts", "src/**/*.tsx"])

    def test_union_of_keys(self):
        self.assertEqual(globs_of('paths:\n  - "a"\nglobs: "b"'), ["a", "b"])

    def test_empty_rules_fail(self):
        for fm in ('globs: ""', "paths: []", "paths:", 'paths:\n  - ""', "description: no globs at all"):
            with self.subTest(fm=fm), self.assertRaises(exp.ExportError):
                globs_of(fm)


class ExportRules(unittest.TestCase):
    def export_with(self, rules: dict):
        with tempfile.TemporaryDirectory() as td:
            fake = Path(td)
            (fake / "rules").mkdir()
            for name, text in rules.items():
                (fake / "rules" / name).write_text(text)
            orig = exp.REPO
            exp.REPO = fake
            try:
                out = fake / "out"
                out.mkdir()
                summary = exp.export_rules(out)
                return summary, {f.name: f.read_text() for f in (out / "rules").iterdir()}
            finally:
                exp.REPO = orig

    def test_planted_empty_rule_fails_export(self):
        with self.assertRaises(exp.ExportError) as cm:
            self.export_with({"ok.md": '---\npaths:\n  - "**/*.go"\n---\n# ok\n',
                              "empty.md": '---\nglobs: ""\n---\n# empty\n'})
        self.assertIn("empty.md", str(cm.exception))

    def test_emits_one_quoted_comma_separated_globs(self):
        summary, files = self.export_with({"x.md": '---\npaths:\n  - "**/*.sql"\n  - "**/migrations/**"\n---\n# x\n'})
        text = files["cure-rule-x.md"]
        self.assertIn('trigger: glob\n', text)
        self.assertIn('globs: "**/*.sql, **/migrations/**"\n', text)
        self.assertEqual(summary["rule_globs"], {"x": ["**/*.sql", "**/migrations/**"]})


class RepoRules(unittest.TestCase):
    """Library invariants: Claude Code reads only `paths`, so every rule uses it, and every rule exports."""

    def test_every_rule_uses_paths_list(self):
        for p in sorted((REPO / "rules").glob("*.md")):
            fm, _ = exp.split_frontmatter(p.read_text(encoding="utf-8"), str(p))
            with self.subTest(rule=p.name):
                self.assertRegex(fm, r"(?m)^paths:\s*$", "use a `paths:` YAML list")
                self.assertNotRegex(fm, r"(?m)^globs?:", "`globs:` is ignored by Claude Code")
                self.assertTrue(exp.rule_globs(fm, str(p)))


class SmokeStaticCheck(unittest.TestCase):
    def test_flags_empty_glob_rule(self):
        with tempfile.TemporaryDirectory() as td:
            rd = Path(td) / "rules"
            rd.mkdir()
            (rd / "cure-rule-good.md").write_text('---\ntrigger: glob\nglobs: "**/*.go"\n---\n')
            (rd / "cure-rule-bad.md").write_text('---\ntrigger: glob\nglobs: ""\n---\n')
            (rd / "cure-rule-none.md").write_text("---\ntrigger: glob\n---\n")
            (rd / "cure-style-x.md").write_text("---\ntrigger: model_decision\n---\n")
            self.assertEqual(smoke.empty_glob_rules(Path(td)), ["cure-rule-bad.md", "cure-rule-none.md"])


class FullExport(unittest.TestCase):
    def test_real_export_has_no_empty_globs(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "cure"
            p = subprocess.run([sys.executable, str(HERE / "export-antigravity.py"), "--out", str(out), "--json"],
                               capture_output=True, text=True, timeout=300)
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertEqual(smoke.empty_glob_rules(out), [])
            for f in (out / "rules").glob("cure-rule-*.md"):
                self.assertTrue(re.search(r'(?m)^globs: "[^"]+"$', f.read_text()), f.name)


if __name__ == "__main__":
    unittest.main(verbosity=2)
