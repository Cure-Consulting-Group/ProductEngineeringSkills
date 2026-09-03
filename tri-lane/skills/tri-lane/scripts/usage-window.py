#!/usr/bin/env python3
"""usage-window: sum Claude Code and Codex token usage between two timestamps, from their local logs.

Claude: every assistant message in ~/.claude/projects/<project-slug>/**/*.jsonl carries
`message.usage` (input, cache_creation, cache_read, output, thinking). Subagent transcripts
live under <session>/subagents/ and are included.
Codex: ~/.codex/sessions/**/*.jsonl carries cumulative `token_count` events per session,
plus the account's weekly rate-limit percentage.

Works for any arm of a benchmark, including the manual three-terminal flow, because it
reads logs rather than instrumenting commands. Python stdlib only.

Examples:
  python3 usage-window.py --since 2026-09-03T14:00:00Z
  python3 usage-window.py --since 2026-09-03T14:00:00Z --until 2026-09-03T15:30:00Z --project ~/CureVault/projects/Vendly
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


def parse_ts(s: str) -> datetime:
    s = s.strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    d = datetime.fromisoformat(s)
    if d.tzinfo is None:
        d = d.replace(tzinfo=timezone.utc)
    return d.astimezone(timezone.utc)


def project_slug(path: str) -> str:
    return re.sub(r"[^A-Za-z0-9]", "-", str(Path(path).resolve()))


def claude_usage(project: str, since: datetime, until: datetime) -> dict:
    home = Path.home() / ".claude" / "projects"
    candidates = [home / project_slug(project)]
    # the same repo may be opened via a symlinked path; include any slug that ends with the repo name
    name = Path(project).resolve().name
    candidates += [p for p in home.glob(f"*-{name}") if p not in candidates]
    tot = {"input_tokens": 0, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0, "output_tokens": 0, "thinking_tokens": 0}
    msgs = 0
    models: dict = {}
    files = 0
    for root in candidates:
        if not root.exists():
            continue
        for f in root.rglob("*.jsonl"):
            try:
                if datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc) < since:
                    continue
            except OSError:
                continue
            files += 1
            with open(f, errors="ignore") as fh:
                for line in fh:
                    if '"usage"' not in line:
                        continue
                    try:
                        d = json.loads(line)
                    except Exception:
                        continue
                    if d.get("type") != "assistant":
                        continue
                    ts = d.get("timestamp")
                    if not ts:
                        continue
                    try:
                        t = parse_ts(ts)
                    except Exception:
                        continue
                    if not (since <= t <= until):
                        continue
                    u = (d.get("message") or {}).get("usage") or {}
                    msgs += 1
                    for k in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens", "output_tokens"):
                        tot[k] += int(u.get(k) or 0)
                    tot["thinking_tokens"] += int(((u.get("output_tokens_details") or {}).get("thinking_tokens")) or 0)
                    m = (d.get("message") or {}).get("model") or "unknown"
                    models[m] = models.get(m, 0) + int(u.get("output_tokens") or 0)
    tot["billable_tokens"] = tot["input_tokens"] + tot["cache_creation_input_tokens"] + tot["output_tokens"]
    tot["messages"] = msgs
    tot["files_scanned"] = files
    tot["output_tokens_by_model"] = models
    return tot


def codex_usage(since: datetime, until: datetime) -> dict:
    root = Path.home() / ".codex" / "sessions"
    keys = ("input_tokens", "cached_input_tokens", "cache_write_input_tokens", "output_tokens", "reasoning_output_tokens", "total_tokens")
    tot = {k: 0 for k in keys}
    sessions = 0
    latest_rl = None
    latest_rl_ts = None
    if not root.exists():
        return {**tot, "sessions": 0, "weekly_used_percent": None}
    for f in root.rglob("*.jsonl"):
        try:
            if datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc) < since:
                # still useful for the latest rate limit if nothing newer exists; skip for speed
                continue
        except OSError:
            continue
        before = None
        last_in = None
        with open(f, errors="ignore") as fh:
            for line in fh:
                if '"token_count"' not in line:
                    continue
                try:
                    d = json.loads(line)
                except Exception:
                    continue
                ts = d.get("timestamp")
                info = ((d.get("payload") or {}).get("info")) or {}
                usage = info.get("total_token_usage") or {}
                rl = (d.get("payload") or {}).get("rate_limits") or {}
                if not ts or not usage:
                    continue
                try:
                    t = parse_ts(ts)
                except Exception:
                    continue
                if rl.get("primary") and (latest_rl_ts is None or t > latest_rl_ts):
                    latest_rl, latest_rl_ts = rl["primary"], t
                if t < since:
                    before = usage
                elif t <= until:
                    last_in = usage
        if last_in:
            sessions += 1
            for k in keys:
                tot[k] += int(last_in.get(k) or 0) - int((before or {}).get(k) or 0)
    out = {**tot, "sessions": sessions}
    out["billable_tokens"] = tot["input_tokens"] - tot["cached_input_tokens"] + tot["output_tokens"]
    out["weekly_used_percent"] = latest_rl.get("used_percent") if latest_rl else None
    out["weekly_resets_at"] = datetime.fromtimestamp(latest_rl["resets_at"], tz=timezone.utc).isoformat() if latest_rl and latest_rl.get("resets_at") else None
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--since", required=True, help="ISO timestamp (UTC if no offset)")
    ap.add_argument("--until", help="ISO timestamp; default now")
    ap.add_argument("--project", default=os.getcwd(), help="repo path whose Claude sessions to count (default cwd)")
    ap.add_argument("--json", action="store_true", help="JSON output (always on)")
    args = ap.parse_args()
    since = parse_ts(args.since)
    until = parse_ts(args.until) if args.until else datetime.now(timezone.utc)
    out = {
        "since": since.isoformat(),
        "until": until.isoformat(),
        "project": str(Path(args.project).resolve()),
        "claude": claude_usage(args.project, since, until),
        "codex": codex_usage(since, until),
    }
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
