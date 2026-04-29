# Skill Scripts Convention

Skills are prompts. Some skills also ship executable tooling. This doc defines the contract for those scripts so they stay portable, testable, and free of hidden dependencies.

## Where scripts live

Every script bundled with a skill lives at:

```
skills/{skill-name}/scripts/{verb_noun}.py
```

One script per concern. A skill with three scripts has three files in the same `scripts/` directory. There is no `lib/` shared module — duplicate small helpers across scripts before introducing shared code. Skill scripts are leaf utilities, not a framework.

## Stdlib-only rule

Scripts MUST use only the Python 3.9+ standard library. No `pip install`, no `requirements.txt`, no virtualenv. Allowed modules include (non-exhaustive):

- `argparse`, `json`, `csv`, `math`, `statistics`, `datetime`, `pathlib`
- `subprocess`, `urllib.request`, `urllib.error`, `re`, `html.parser`
- `dataclasses`, `enum`, `typing`, `sys`, `os`, `io`

Why:

1. **Portability.** Scripts run on any client laptop or CI runner with `python3` already installed. No environment setup.
2. **Plugin trust.** This repo is distributed as a Claude Code plugin. Pulling pip dependencies into client environments is a supply-chain risk we will not take on.
3. **Skill stability.** A skill that worked last month should still work this month. Stdlib is a stable target. PyPI is not.

If you find yourself wanting `requests`, use `urllib.request`. If you want `pandas`, you are probably solving the wrong problem in a script — push the analysis to the model and keep the script narrow.

## Required interface

Every script must support:

- `python3 path/to/script.py --help` — prints `argparse` usage; exits 0.
- `python3 path/to/script.py --json` — emits machine-readable JSON to stdout. Default human output is fine when `--json` is omitted.
- Clear `error: ...` messages on stderr for bad input. **No stack traces leak to the user.** Catch `OSError`, `ValueError`, `subprocess.CalledProcessError`, `urllib.error.URLError`, etc., and turn them into one-line errors.
- A module docstring at the top: one-line purpose, then a short `Usage:` block with at least one example invocation.
- `argparse.ArgumentParser(description=...)` and per-argument `help=` strings.
- Exit codes: `0` on success, `1` on findings/failure-with-output, `2` on bad input or missing files.

Soft limits:

- Stay under ~250 lines per script. If you need more, the script is doing two things — split it.
- One responsibility per script. A skill with three responsibilities ships three scripts.

## Naming

- `snake_case` filename, `.py` extension.
- `verb_noun.py` — the script does something to something. Examples: `deployment_frequency.py`, `runway_calculator.py`, `wcag_check.py`, `cost_estimator.py`.
- Avoid generic names like `main.py`, `run.py`, `tool.py`.
- The script name and the SKILL.md "## Scripts" entry must match.

## Testing

Smoke test for every script: it must run with `--help` and exit 0. The repo ships a runner:

```bash
scripts/verify-skill-scripts.sh
```

That script walks `skills/*/*/scripts/*.py` (domain-nested layout), runs `--help` on each, and fails if any exit non-zero, emit a stack trace, or omit a `usage:` line. Run it locally before opening a PR; CI runs it on every push.

For richer testing, write a few example invocations in the docstring and verify them by hand. Skill scripts are small enough that an integration-test-by-eye is reasonable.

## When to add a script vs. keep the skill pure-prompt

Add a script when:

- The skill produces a number that should be reproducible (DORA metrics, runway months, LTV:CAC).
- The skill parses a structured input (CSV, JSON, git log) and emits a structured output.
- The same calculation is requested every engagement and should not depend on model arithmetic.
- The check is mechanical and deterministic (static accessibility checks, file structure validation).

Keep the skill pure-prompt when:

- The output is judgment, narrative, or a framework (PRD, RFC, code review).
- The "input" is an unstructured codebase the model is better at reasoning about than a regex.
- The work requires synthesis across many sources — the script would just stub-call the model.
- Adding a script would require non-stdlib dependencies.

A skill can do both: prompt drives the analysis, script handles the math. SKILL.md should reference the script in a `## Scripts` section with one-line purpose and example invocation, so the model knows it exists and can call it via Bash.

## SKILL.md reference pattern

Append a section near the end of SKILL.md:

```markdown
## Scripts

This skill bundles the following stdlib-only scripts under `scripts/`:

- `scripts/foo_calculator.py` — One-line purpose.
  ```bash
  python3 skills/{skill-name}/scripts/foo_calculator.py --arg value --json
  ```
```

Keep it terse. The script's `--help` is the source of truth for arguments.
