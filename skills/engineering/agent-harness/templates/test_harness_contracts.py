"""Harness contracts: the Controls table in AGENTS.md, as code.

Each test enforces one rule an agent is likely to break because it has only read about it.
Failure messages state the rule and the fix, because the reader is usually an agent that has
never seen this file. Put it in a CI job that runs on every PR.

Template from the cure-product-engineering `agent-harness` skill. The first three tests apply to
any repo; replace the last with the repo's own top rules, and mutation-check each one.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # adjust if this file is not one level below the root
PATH_ROOTS = ("services/", "scripts/", "docs/", "terraform/", ".claude/", ".github/")


def _git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)


def _tracked(*paths: str) -> list[str]:
    return [p for p in _git("ls-files", "--", *paths).stdout.splitlines() if p]


def test_agent_docs_name_only_paths_that_exist() -> None:
    missing = []
    for doc in ("AGENTS.md", "CLAUDE.md"):
        if not (ROOT / doc).exists():
            continue
        for span in re.findall(r"`([^`\n]+)`", (ROOT / doc).read_text()):
            for token in re.split(r"[\s=]+", span):
                token = token.strip("\"'(").rstrip("\"'),;:.")
                if not token.startswith(PATH_ROOTS) or re.search(r"[*?<>{}…]", token):
                    continue
                if _git("check-ignore", "-q", "--no-index", token).returncode == 0:
                    continue  # machine-local paths are named on purpose
                if not (ROOT / token).exists():
                    missing.append(f"{doc}: `{token}`")
    assert not missing, "Agent docs name paths that do not exist. Fix the path or drop the claim:\n  " + "\n  ".join(missing)


def test_no_scheduled_workflows() -> None:
    offenders = []
    for wf in sorted((ROOT / ".github" / "workflows").glob("*.y*ml")):
        for i, line in enumerate(wf.read_text().splitlines(), 1):
            if re.match(r"^\s*schedule\s*:", line) or re.match(r"^\s*-?\s*cron\s*:", line):
                offenders.append(f"{wf.name}:{i}")
    assert not offenders, (
        "Scheduled workflow trigger (org policy 2026-08-08). Trigger on push, pull_request or "
        "workflow_dispatch:\n  " + "\n  ".join(offenders)
    )


def test_cure_library_is_a_plugin_not_vendored() -> None:
    vendored = _tracked(".claude/agents", ".claude/commands", ".claude/output-styles", ".claude/personas", ".claude/hooks/hooks.json")
    assert not vendored, "Vendored Cure library files are tracked. Delete them; the plugin provides them:\n  " + "\n  ".join(vendored[:10])


# Replace with the repo's own rules. Proven examples:
# - every custom metric emitted or alerted on is registered in docs/METRICS.md
# - views select explicit columns, never bare SELECT *
# - Terraform's ignore_changes covers image only, so env stays Terraform-owned
# - a table's Terraform schema matches the dataclass that writes it
