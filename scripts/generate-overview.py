#!/usr/bin/env python3
"""Generate docs/OVERVIEW.md — single internal-only reference for what this plugin actually does.

Reads frontmatter from skills, agents, personas, output-styles, rules, plus the JSON
config files (hooks, mcp, lsp, plugin manifest) and emits one deterministic markdown
file. Stdlib only — no PyYAML, no pip.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path


# --------------------------------------------------------------------------- #
# Frontmatter parser
# --------------------------------------------------------------------------- #

FRONTMATTER_RE = re.compile(
    r"\A---\s*\n(.*?)\n---\s*(?:\n|$)",
    re.DOTALL,
)


def parse_frontmatter(text: str) -> dict:
    """Extract a YAML-ish frontmatter block from the top of a markdown file.

    Handles the subset we actually use: scalars, single-line lists `[a, b]`,
    multi-line indented lists (`- item`), single/double-quoted strings, and
    nested mapping is NOT supported (we don't use it). Returns {} when no
    frontmatter is found.
    """
    if not text:
        return {}
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}
    block = match.group(1)
    return _parse_yaml_block(block)


def _parse_yaml_block(block: str) -> dict:
    out: dict = {}
    lines = block.splitlines()
    i = 0
    n = len(lines)
    while i < n:
        raw = lines[i]
        # Strip comments (only when '#' starts a token outside of quotes — keep simple).
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        # Top-level key requires no leading whitespace.
        if line[0] in (" ", "\t"):
            i += 1
            continue
        if ":" not in line:
            i += 1
            continue
        key, _, rest = line.partition(":")
        key = key.strip()
        rest = rest.strip()
        if rest == "":
            # Possible multi-line list following with `-` items.
            items: list[str] = []
            j = i + 1
            while j < n:
                sub = lines[j]
                if not sub.strip():
                    j += 1
                    continue
                if sub[0] not in (" ", "\t"):
                    break
                stripped = sub.strip()
                if stripped.startswith("- "):
                    items.append(_strip_quotes(stripped[2:].strip()))
                    j += 1
                else:
                    break
            out[key] = items
            i = j
            continue
        # Inline list `[a, b, "c"]`
        if rest.startswith("[") and rest.endswith("]"):
            inner = rest[1:-1].strip()
            if not inner:
                out[key] = []
            else:
                out[key] = [_strip_quotes(p.strip()) for p in _split_csv(inner)]
            i += 1
            continue
        out[key] = _strip_quotes(rest)
        i += 1
    return out


def _strip_quotes(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1]
    return value


def _split_csv(s: str) -> list[str]:
    # Split on commas that are not inside quotes.
    parts: list[str] = []
    buf = ""
    quote = None
    for ch in s:
        if quote:
            buf += ch
            if ch == quote:
                quote = None
            continue
        if ch in ("'", '"'):
            quote = ch
            buf += ch
            continue
        if ch == ",":
            parts.append(buf)
            buf = ""
            continue
        buf += ch
    if buf:
        parts.append(buf)
    return parts


# --------------------------------------------------------------------------- #
# Discovery
# --------------------------------------------------------------------------- #

def safe_read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        warn(f"could not read {path}: {exc}")
        return ""


def warn(msg: str) -> None:
    print(f"[generate-overview] WARN: {msg}", file=sys.stderr)


def collect_skills(repo: Path) -> list[dict]:
    """Find SKILL.md files under skills/ and read frontmatter.

    Supports both flat `skills/{name}/SKILL.md` and nested `skills/{domain}/{name}/SKILL.md`
    so the generator survives the T1 reorg.
    """
    skills_dir = repo / "skills"
    if not skills_dir.is_dir():
        warn(f"skills/ not found at {skills_dir}")
        return []
    found: list[dict] = []
    for skill_md in sorted(skills_dir.rglob("SKILL.md")):
        text = safe_read(skill_md)
        fm = parse_frontmatter(text)
        rel = skill_md.relative_to(repo)
        # Domain inferred from path if nested (skills/<domain>/<name>/SKILL.md),
        # otherwise from the skill name (heuristic below).
        parts = skill_md.relative_to(skills_dir).parts
        if len(parts) >= 3:
            path_domain = parts[0]
        else:
            path_domain = None
        name = fm.get("name") or (parts[-2] if len(parts) >= 2 else skill_md.parent.name)
        found.append(
            {
                "name": name,
                "description": fm.get("description", ""),
                "argument_hint": fm.get("argument-hint", ""),
                "allowed_tools": fm.get("allowed-tools", []),
                "disable_model_invocation": fm.get("disable-model-invocation", ""),
                "when_to_use": fm.get("when_to_use", ""),
                "path": str(rel),
                "path_domain": path_domain,
            }
        )
    return found


def collect_agents(repo: Path) -> list[dict]:
    agents_dir = repo / "agents"
    if not agents_dir.is_dir():
        warn(f"agents/ not found at {agents_dir}")
        return []
    found: list[dict] = []
    for md in sorted(agents_dir.glob("*.md")):
        text = safe_read(md)
        fm = parse_frontmatter(text)
        found.append(
            {
                "name": fm.get("name") or md.stem,
                "description": fm.get("description", ""),
                "tools": fm.get("tools", ""),
                "model": fm.get("model", ""),
                "skills": fm.get("skills", ""),
                "path": str(md.relative_to(repo)),
            }
        )
    return found


def collect_personas(repo: Path) -> list[dict]:
    personas_dir = repo / "personas"
    if not personas_dir.is_dir():
        return []
    found: list[dict] = []
    for md in sorted(personas_dir.glob("*.md")):
        text = safe_read(md)
        fm = parse_frontmatter(text)
        skill_count = _count_skill_refs(text)
        found.append(
            {
                "name": fm.get("name") or md.stem,
                "description": fm.get("description", ""),
                "type": fm.get("type", ""),
                "skill_refs": skill_count,
                "path": str(md.relative_to(repo)),
            }
        )
    return found


def _count_skill_refs(text: str) -> int:
    """Count distinct skill names referenced in a `## Skill Loadout` section.

    Heuristic: matches bolded or backticked tokens after bullet `-` markers
    that look like skill slugs (kebab-case, no spaces).
    """
    section = re.search(
        r"##\s*Skill Loadout\s*\n(.*?)(?=\n##\s|\Z)",
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )
    if not section:
        return 0
    body = section.group(1)
    # Pull tokens that look like kebab-case skill names.
    candidates = re.findall(r"[a-z][a-z0-9]+(?:-[a-z0-9]+)+", body)
    return len(set(candidates))


def collect_rules(repo: Path) -> list[dict]:
    rules_dir = repo / "rules"
    if not rules_dir.is_dir():
        return []
    found: list[dict] = []
    for md in sorted(rules_dir.glob("*.md")):
        text = safe_read(md)
        fm = parse_frontmatter(text)
        # Rules variously use `globs` (string) or `paths` (list).
        globs_val = fm.get("globs") or fm.get("paths") or ""
        if isinstance(globs_val, list):
            globs = ", ".join(globs_val)
        else:
            globs = str(globs_val)
        summary = _first_meaningful_line(text)
        found.append(
            {
                "file": md.name,
                "globs": globs,
                "summary": summary,
                "path": str(md.relative_to(repo)),
            }
        )
    return found


def _first_meaningful_line(text: str) -> str:
    """Return the first non-empty, non-heading prose line after frontmatter."""
    body = re.sub(FRONTMATTER_RE, "", text, count=1)
    for raw in body.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("#"):
            continue
        if line.startswith("```"):
            continue
        return line[:120]
    return ""


def collect_output_styles(repo: Path) -> list[dict]:
    styles_dir = repo / "output-styles"
    if not styles_dir.is_dir():
        return []
    found: list[dict] = []
    for sub in sorted(p for p in styles_dir.iterdir() if p.is_dir()):
        md = sub / "output-style.md"
        if not md.is_file():
            continue
        text = safe_read(md)
        fm = parse_frontmatter(text)
        # Some output-styles have no frontmatter — fall back to first heading.
        name = fm.get("name") or sub.name
        description = fm.get("description") or _first_h1(text)
        found.append(
            {
                "name": name,
                "description": description,
                "path": str(md.relative_to(repo)),
            }
        )
    return found


def _first_h1(text: str) -> str:
    body = re.sub(FRONTMATTER_RE, "", text, count=1)
    m = re.search(r"^#\s+(.+)$", body, flags=re.MULTILINE)
    return m.group(1).strip() if m else ""


def collect_hooks(repo: Path) -> list[dict]:
    hooks_path = repo / "hooks" / "hooks.json"
    if not hooks_path.is_file():
        warn(f"hooks/hooks.json not found at {hooks_path}")
        return []
    try:
        data = json.loads(hooks_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        warn(f"could not parse hooks.json: {exc}")
        return []
    rows: list[dict] = []
    for event, entries in (data.get("hooks") or {}).items():
        for entry in entries or []:
            matcher = entry.get("matcher", "")
            for hook in entry.get("hooks") or []:
                rows.append(
                    {
                        "event": event,
                        "matcher": matcher,
                        "type": hook.get("type", ""),
                        "summary": _summarize_hook(hook),
                    }
                )
    return rows


def _summarize_hook(hook: dict) -> str:
    htype = hook.get("type")
    if htype == "command":
        cmd = hook.get("command", "") or ""
        return _truncate(cmd.split("\n", 1)[0], 110)
    if htype in ("prompt", "agent"):
        prompt = hook.get("prompt", "") or ""
        return _truncate(prompt.split("\n", 1)[0], 110)
    return ""


def _truncate(s: str, n: int) -> str:
    s = s.strip()
    return s if len(s) <= n else s[: n - 1] + "…"


def collect_mcp(repo: Path) -> list[dict]:
    path = repo / ".mcp.json"
    if not path.is_file():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        warn(f"could not parse .mcp.json: {exc}")
        return []
    rows: list[dict] = []
    for name, cfg in (data.get("mcpServers") or {}).items():
        rows.append(
            {
                "name": name,
                "type": cfg.get("type", ""),
                "transport": cfg.get("url") or cfg.get("command") or "",
                "note": cfg.get("note", ""),
            }
        )
    return rows


def collect_lsp(repo: Path) -> list[dict]:
    path = repo / ".lsp.json"
    if not path.is_file():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        warn(f"could not parse .lsp.json: {exc}")
        return []
    rows: list[dict] = []
    for name, cfg in (data.get("lspServers") or {}).items():
        exts = cfg.get("extensionToLanguage") or {}
        rows.append(
            {
                "name": name,
                "command": " ".join([cfg.get("command", "")] + list(cfg.get("args", []))).strip(),
                "extensions": ", ".join(sorted(exts.keys())) if exts else "",
            }
        )
    return rows


def collect_plugin_manifest(repo: Path) -> dict:
    path = repo / ".claude-plugin" / "plugin.json"
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        warn(f"could not parse plugin.json: {exc}")
        return {}


# --------------------------------------------------------------------------- #
# Categorization
# --------------------------------------------------------------------------- #

# Name-pattern → category. First match wins. Patterns are matched as substrings
# against the lowercased skill/agent name.
SKILL_CATEGORY_RULES: list[tuple[str, list[str]]] = [
    ("security", ["security", "compliance", "accessibility", "qsbs"]),
    ("legal", ["legal", "contract"]),
    ("business", [
        "financial", "saas-financial", "finops", "burn-rate", "investor",
        "fundraising", "engineering-cost-model", "proposal", "ops-finance",
    ]),
    ("marketing", ["marketing", "seo", "content", "campaign", "brand", "go-to-market", "growth"]),
    ("product", [
        "product", "market-research", "customer-onboarding", "design-system",
        "product-design", "product-analytics", "product-ops", "product-strategy",
        "quarterly-planning", "uat", "feature-flags", "feature-audit",
        "portfolio-registry", "technology-radar",
    ]),
    ("platform", [
        "infrastructure", "ci-cd", "ci/cd", "observability", "incident",
        "disaster-recovery", "release", "dora", "edge-computing",
        "chaos-engineering", "green-software", "gcloud",
    ]),
    ("engineering", []),  # default bucket
]

AGENT_CATEGORY_RULES: list[tuple[str, list[str]]] = [
    ("security", ["security", "accessibility", "firebase-security"]),
    ("legal", ["legal", "contract"]),
    ("business", ["financial", "investor", "ops-finance", "market-intelligence"]),
    ("marketing", ["content", "campaign", "brand", "growth"]),
    ("product", ["product", "ux", "roadmap", "competitive"]),
    ("data", ["data-analyst", "metrics-dashboard", "ab-test"]),
    ("engineering", []),
]


def categorize(name: str, rules: list[tuple[str, list[str]]]) -> str:
    lowered = name.lower()
    for category, patterns in rules:
        if not patterns:
            return category
        for pat in patterns:
            if pat in lowered:
                return category
    return "engineering"


def group_by(rows: list[dict], key_fn) -> dict:
    out: dict[str, list[dict]] = {}
    for row in rows:
        out.setdefault(key_fn(row), []).append(row)
    return {k: out[k] for k in sorted(out.keys())}


# --------------------------------------------------------------------------- #
# Markdown rendering
# --------------------------------------------------------------------------- #

def md_escape(value) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        value = ", ".join(str(v) for v in value)
    s = str(value)
    return s.replace("|", "\\|").replace("\n", " ").strip()


def render_table(headers: list[str], rows: list[list[str]]) -> str:
    if not rows:
        return "_n/a_\n"
    head = "| " + " | ".join(headers) + " |"
    sep = "| " + " | ".join("---" for _ in headers) + " |"
    body = "\n".join("| " + " | ".join(md_escape(c) for c in row) + " |" for row in rows)
    return f"{head}\n{sep}\n{body}\n"


def render_overview(
    *,
    plugin: dict,
    skills: list[dict],
    agents: list[dict],
    personas: list[dict],
    hooks: list[dict],
    rules: list[dict],
    output_styles: list[dict],
    mcp_servers: list[dict],
    lsp_servers: list[dict],
) -> str:
    parts: list[str] = []
    parts.append("# ProductEngineeringSkills — Overview\n")
    parts.append(
        "_Auto-generated. Do not edit by hand. "
        "Regenerate with `python3 scripts/generate-overview.py`._\n"
    )

    # 1. Summary
    parts.append("## 1. Summary\n")
    parts.append(
        render_table(
            ["Field", "Value"],
            [
                ["Plugin", plugin.get("name", "n/a")],
                ["Version", plugin.get("version", "n/a")],
                ["Skills", str(len(skills))],
                ["Agents", str(len(agents))],
                ["Personas", str(len(personas))],
                ["Hooks (entries)", str(len(hooks))],
                ["Rules", str(len(rules))],
                ["Output Styles", str(len(output_styles))],
                ["MCP Servers", str(len(mcp_servers))],
                ["LSP Servers", str(len(lsp_servers))],
            ],
        )
    )

    # 2. Skills (grouped)
    parts.append("\n## 2. Skills\n")
    skills_with_cat = [
        {**s, "category": s.get("path_domain") or categorize(s["name"], SKILL_CATEGORY_RULES)}
        for s in skills
    ]
    grouped = group_by(skills_with_cat, lambda r: r["category"])
    for category, items in grouped.items():
        parts.append(f"\n### {category.title()} ({len(items)})\n")
        rows = []
        for s in sorted(items, key=lambda r: r["name"]):
            tools = s.get("allowed_tools") or ""
            if isinstance(tools, list):
                tools = ", ".join(tools) if tools else ""
            rows.append([s["name"], s.get("description", ""), tools or "default"])
        parts.append(render_table(["Skill", "Description", "Allowed Tools"], rows))

    # 3. Agents (grouped)
    parts.append("\n## 3. Agents\n")
    agents_with_cat = [
        {**a, "category": categorize(a["name"], AGENT_CATEGORY_RULES)} for a in agents
    ]
    grouped_a = group_by(agents_with_cat, lambda r: r["category"])
    for category, items in grouped_a.items():
        parts.append(f"\n### {category.title()} ({len(items)})\n")
        rows = []
        for a in sorted(items, key=lambda r: r["name"]):
            rows.append([a["name"], a.get("description", ""), a.get("tools", "")])
        parts.append(render_table(["Agent", "Purpose", "Tools"], rows))

    # 4. Personas
    parts.append("\n## 4. Personas\n")
    rows = []
    for p in sorted(personas, key=lambda r: r["name"]):
        rows.append([p["name"], p.get("description", ""), str(p.get("skill_refs", 0))])
    parts.append(render_table(["Persona", "Description", "Skills referenced"], rows))

    # 5. Hooks
    parts.append("\n## 5. Hooks\n")
    rows = []
    for h in hooks:
        rows.append([h["event"], h.get("matcher", ""), h.get("type", ""), h.get("summary", "")])
    parts.append(render_table(["Event", "Matcher", "Type", "What it does"], rows))

    # 6. Rules
    parts.append("\n## 6. Rules\n")
    rows = []
    for r in sorted(rules, key=lambda x: x["file"]):
        rows.append([r["file"], r.get("globs", ""), r.get("summary", "")])
    parts.append(render_table(["Rule", "Globs", "Summary"], rows))

    # 7. Output styles
    parts.append("\n## 7. Output Styles\n")
    rows = []
    for s in sorted(output_styles, key=lambda r: r["name"]):
        rows.append([s["name"], s.get("description", "")])
    parts.append(render_table(["Style", "Description"], rows))

    # 8. MCP servers
    parts.append("\n## 8. MCP Servers\n")
    rows = []
    for m in sorted(mcp_servers, key=lambda r: r["name"]):
        rows.append([m["name"], m.get("type", ""), m.get("transport", ""), m.get("note", "")])
    parts.append(render_table(["Server", "Type", "Transport / URL / Command", "Note"], rows))

    # 9. LSP servers
    parts.append("\n## 9. LSP Servers\n")
    rows = []
    for l in sorted(lsp_servers, key=lambda r: r["name"]):
        rows.append([l["name"], l.get("extensions", ""), l.get("command", "")])
    parts.append(render_table(["Server", "Extensions", "Command"], rows))

    # 10. Footer
    parts.append("\n---\n")
    parts.append(
        "_Regenerate with `python3 scripts/generate-overview.py`._\n"
    )

    return "\n".join(parts)


# --------------------------------------------------------------------------- #
# Entrypoint
# --------------------------------------------------------------------------- #

def build(repo: Path, out: Path) -> int:
    plugin = collect_plugin_manifest(repo)
    skills = collect_skills(repo)
    agents = collect_agents(repo)
    personas = collect_personas(repo)
    hooks = collect_hooks(repo)
    rules = collect_rules(repo)
    output_styles = collect_output_styles(repo)
    mcp_servers = collect_mcp(repo)
    lsp_servers = collect_lsp(repo)

    content = render_overview(
        plugin=plugin,
        skills=skills,
        agents=agents,
        personas=personas,
        hooks=hooks,
        rules=rules,
        output_styles=output_styles,
        mcp_servers=mcp_servers,
        lsp_servers=lsp_servers,
    )

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content, encoding="utf-8")
    print(
        f"[generate-overview] wrote {out} "
        f"({len(skills)} skills, {len(agents)} agents, {len(personas)} personas, "
        f"{len(hooks)} hooks, {len(rules)} rules, {len(output_styles)} styles, "
        f"{len(mcp_servers)} mcp, {len(lsp_servers)} lsp)"
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="generate-overview",
        description=(
            "Generate docs/OVERVIEW.md — single internal reference describing "
            "every skill, agent, persona, hook, rule, output style, and MCP/LSP "
            "server in this plugin. Internal-only. Stdlib only."
        ),
    )
    parser.add_argument(
        "--out",
        default="docs/OVERVIEW.md",
        help="Output path for the generated overview (default: docs/OVERVIEW.md)",
    )
    parser.add_argument(
        "--repo-root",
        default=os.getcwd(),
        help="Repository root to scan (default: current working directory)",
    )
    parser.add_argument(
        "--smoke-test",
        action="store_true",
        help="Verify the script imports and parses arguments, then exit 0 without writing.",
    )
    args = parser.parse_args(argv)

    if args.smoke_test:
        print("[generate-overview] smoke-test ok")
        return 0

    repo = Path(args.repo_root).resolve()
    if not repo.is_dir():
        print(f"[generate-overview] ERROR: repo-root not a directory: {repo}", file=sys.stderr)
        return 2

    out = Path(args.out)
    if not out.is_absolute():
        out = repo / out
    return build(repo, out)


if __name__ == "__main__":
    sys.exit(main())
