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


def _claude_files(project: str):
    home = Path.home() / ".claude" / "projects"
    candidates = [home / project_slug(project)]
    name = Path(project).resolve().name
    candidates += [p for p in home.glob(f"*-{name}") if p not in candidates]
    for root in candidates:
        if root.exists():
            yield from root.rglob("*.jsonl")


def _is_agent_transcript(f: Path, agent: str) -> bool:
    """A subagent transcript whose opening mentions the agent (frontmatter name or heading)."""
    if "subagents" not in f.parts and not f.name.startswith("agent-"):
        return False
    try:
        with open(f, errors="ignore") as fh:
            head = fh.read(8000)
    except OSError:
        return False
    needle = agent.lower()
    return needle in head.lower() or needle.replace("-", " ") in head.lower()


def claude_usage_multi(project: str, windows: list, agent: str | None = None) -> list:
    """One pass over the project's transcripts; returns one usage dict per (since, until) window, in order.
    A message inside several windows is counted in each (overlap is the caller's to flag). `agent` restricts
    the scan to subagent transcripts for that agent (e.g. cure-advisor) so a per-review cost can be measured."""
    tots = [{"input_tokens": 0, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0, "output_tokens": 0, "thinking_tokens": 0, "messages": 0, "files_scanned": 0} for _ in windows]
    if not windows:
        return tots
    lo = min(w[0] for w in windows)
    for f in _claude_files(project):
        try:
            if datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc) < lo:
                continue
        except OSError:
            continue
        if agent and not _is_agent_transcript(f, agent):
            continue
        touched = set()
        with open(f, errors="ignore") as fh:
            for line in fh:
                if '"usage"' not in line:
                    continue
                try:
                    d = json.loads(line)
                except Exception:
                    continue
                if d.get("type") != "assistant" or not d.get("timestamp"):
                    continue
                try:
                    t = parse_ts(d["timestamp"])
                except Exception:
                    continue
                u = (d.get("message") or {}).get("usage") or {}
                for i, (since, until) in enumerate(windows):
                    if since <= t <= until:
                        touched.add(i)
                        tt = tots[i]
                        tt["messages"] += 1
                        for k in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens", "output_tokens"):
                            tt[k] += int(u.get(k) or 0)
                        tt["thinking_tokens"] += int(((u.get("output_tokens_details") or {}).get("thinking_tokens")) or 0)
        for i in touched:
            tots[i]["files_scanned"] += 1
    for tt in tots:
        tt["billable_tokens"] = tt["input_tokens"] + tt["cache_creation_input_tokens"] + tt["output_tokens"]
    return tots


def agent_transcript_costs(project: str, agent: str, since: datetime, until: datetime) -> list:
    """Billable tokens per subagent transcript for `agent` (one number per review), for a median per-review cost."""
    out = []
    for f in _claude_files(project):
        if not _is_agent_transcript(f, agent):
            continue
        try:
            if datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc) < since:
                continue
        except OSError:
            continue
        bill, n, last = 0, 0, None
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
                u = (d.get("message") or {}).get("usage") or {}
                bill += int(u.get("input_tokens") or 0) + int(u.get("cache_creation_input_tokens") or 0) + int(u.get("output_tokens") or 0)
                n += 1
                last = d.get("timestamp") or last
        if n and last:
            try:
                if not (since <= parse_ts(last) <= until):
                    continue
            except Exception:
                pass
            out.append({"file": str(f), "billable_tokens": bill, "messages": n, "ended_at": last})
    return out


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
    ap.add_argument("--agent", help="restrict the Claude scan to subagent transcripts for this agent (e.g. cure-advisor); prints per-transcript costs too")
    ap.add_argument("--project", default=os.getcwd(), help="repo path whose Claude sessions to count (default cwd)")
    ap.add_argument("--json", action="store_true", help="JSON output (always on)")
    args = ap.parse_args()
    since = parse_ts(args.since)
    until = parse_ts(args.until) if args.until else datetime.now(timezone.utc)
    if args.agent:
        per = agent_transcript_costs(args.project, args.agent, since, until)
        bills = sorted(x["billable_tokens"] for x in per)
        out = {
            "since": since.isoformat(), "until": until.isoformat(), "project": str(Path(args.project).resolve()), "agent": args.agent,
            "claude": claude_usage_multi(args.project, [(since, until)], agent=args.agent)[0],
            "transcripts": len(per),
            "billable_median": bills[len(bills) // 2] if bills else None,
            "billable_mean": round(sum(bills) / len(bills)) if bills else None,
            "per_transcript": per,
        }
        print(json.dumps(out, indent=2))
        return 0
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
