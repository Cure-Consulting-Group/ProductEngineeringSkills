# Cross-Platform Setup Guide

How to get Cure Consulting Group's engineering standards on every Claude platform.

## Platform Capabilities

| Capability | Claude Code CLI | Claude Desktop | claude.ai (Browser) |
|-----------|----------------|---------------|---------------------|
| 63 Skills | Yes | No | No |
| 9 Agents | Yes | No | No |
| 12 Hook Events | Yes | No | No |
| 11 Path Rules | Yes | No | No |
| 9 Output Styles | Yes | No | No |
| MCP Servers | Yes (all) | Yes (all) | Partial (remote only) |
| LSP Servers | Yes | No | No |
| Custom Instructions | N/A | N/A | Yes |
| Project Knowledge | N/A | Yes (via Projects) | Yes (via Projects) |

> **Note:** claude.ai only supports remote MCP servers (GitHub, Sentry). Stdio-based servers (Firestore, PostgreSQL) require Claude Code CLI or Claude Desktop.

## 1. Claude Code CLI (Full Power)

Already installed. All 64 skills, 9 agents, hooks, rules, and output styles are active.

```bash
# Verify
ls -la ~/.claude/plugins/ProductEngineeringSkills
cat ~/.claude/settings.json
```

## 2. Claude Desktop App

### MCP Servers

If you ran `setup.sh`, the GitHub, Sentry, Firestore, and PostgreSQL MCP servers were added automatically. Otherwise, manually add them to your Claude Desktop config:

| OS | Config Path |
|----|------------|
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |
| Linux | `~/.config/Claude/claude_desktop_config.json` |

Copy the server entries from `.mcp.json` in this repo into your config file. Restart Claude Desktop to pick up the changes.

### Project Knowledge

For project-specific work in Claude Desktop:
1. Create a new Project in Claude Desktop
2. Add `claude-project-knowledge.md` as project knowledge
3. Claude Desktop will use these standards for all conversations in that project

## 3. claude.ai (Browser)

### Custom Instructions (Global)

1. Go to claude.ai → Settings → Profile → Custom Instructions
2. Copy the content from `claude-custom-instructions.md` (the section after "copy below this line")
3. Save — these apply to ALL conversations

### Project Knowledge (Per-Project)

1. Create a new Project at claude.ai
2. Click "Add content" → Upload `claude-project-knowledge.md`
3. All conversations in that project will follow Cure standards

### MCP Servers (Remote Only)

claude.ai only supports remote HTTP-based MCP servers:
- **GitHub MCP**: Connect via the GitHub integration
- **Sentry MCP**: Connect via the Sentry integration
- **Firestore/PostgreSQL**: Not available — these are stdio servers that require a local process. Use Claude Code CLI or Claude Desktop for database access.

## 4. Environment Variables

MCP servers require credentials. Set these in your shell profile (`~/.zshrc` or `~/.bashrc`):

```bash
# GitHub MCP — needed by: Claude Code CLI, Claude Desktop
export GITHUB_TOKEN="ghp_..."

# Sentry MCP — needed by: Claude Code CLI, Claude Desktop
export SENTRY_AUTH_TOKEN="sntrys_..."

# Firestore MCP — needed by: Claude Code CLI, Claude Desktop
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
export FIREBASE_PROJECT_ID="your-project-id"

# PostgreSQL MCP — needed by: Claude Code CLI, Claude Desktop
export DATABASE_URL="postgresql://user:pass@host:5432/db"
```

## Summary

| Platform | What You Get |
|----------|-------------|
| **Claude Code CLI** | Everything — 64 skills, 9 agents, hooks, rules, MCP, LSP |
| **Claude Desktop** | MCP servers (all 4) + project knowledge |
| **claude.ai** | Custom instructions (global) + project knowledge + remote MCP (GitHub, Sentry only) |

The full plugin system is Claude Code CLI exclusive. For Claude Desktop and claude.ai, you get our standards as knowledge context and MCP server access for tooling.
