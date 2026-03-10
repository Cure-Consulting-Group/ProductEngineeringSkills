# ProductEngineeringSkills — Comprehensive Evaluation

## 1. Skills Audit

### Current State: 24 Claude Commands + 13 Gemini Skills

| Category | Skills | Coverage | Gaps |
|----------|--------|----------|------|
| **Product & Strategy** (7) | product-manager, product-design, market-research, go-to-market, product-marketing, customer-onboarding, seo-content-engine | Strong | Competitive intelligence automation, A/B test design |
| **Engineering** (8) | sdlc, android-feature-scaffold, ios-architect, nextjs-feature-scaffold, firebase-architect, api-architect, stripe-integration, ai-feature-builder | Strong | Database migration planning, infrastructure-as-code |
| **Quality & Security** (3) | feature-audit, testing-strategy, security-review | Adequate | Performance/load testing, accessibility audit |
| **Operations** (3) | project-manager, ci-cd-pipeline, analytics-implementation | Adequate | Incident response, on-call runbooks |
| **Business** (3) | engineering-cost-model, saas-financial-model, legal-doc-scaffold | Good | Investor deck scaffold, pitch preparation |

### Format Issues

All 24 skills use the **old command format** (`.claude/commands/name.md`). Claude Code now supports the **new skill format** with frontmatter metadata:

```yaml
---
name: sdlc
description: Generate SDLC artifacts (PRDs, ADRs, RFCs, Epics, Stories)
argument-hint: [feature-name]
---
```

**Impact**: Without frontmatter, skills cannot be auto-invoked by Claude, cannot restrict tools, cannot specify models, and cannot use context forking. This is leaving significant capability on the table.

### Gemini Parity Gap

Only 13 of 24 skills have Gemini equivalents. Missing:
- ai-feature-builder, api-architect, nextjs-feature-scaffold
- ci-cd-pipeline, testing-strategy, security-review
- analytics-implementation, engineering-cost-model, saas-financial-model
- customer-onboarding, seo-content-engine

---

## 2. Hooks Evaluation — What We Should Build

### Current State: No hooks exist

This is the biggest missed opportunity. Hooks can **connect skills to each other** and **enforce standards automatically**.

### Recommended Hooks

#### A. PostToolUse Hooks (Auto-enforcement)

| Hook | Trigger | What It Does |
|------|---------|--------------|
| **Auto-audit trigger** | After `Write` or `Edit` on source files | Reminds Claude to run `/feature-audit` after significant code generation |
| **Security gate** | After `Write` on auth/payment files | Runs security review checklist automatically |
| **Test reminder** | After `Edit` on any source file | Checks if corresponding test file exists, prompts if not |
| **Format enforcement** | After `Edit\|Write` | Runs project linter/formatter |

#### B. PreToolUse Hooks (Guardrails)

| Hook | Trigger | What It Does |
|------|---------|--------------|
| **Protected files** | Before `Edit` on `.env`, `*-lock.*`, CI configs | Blocks accidental edits to sensitive files |
| **Dangerous commands** | Before `Bash` with `rm -rf`, `drop table`, `force push` | Requires confirmation |
| **Production safeguard** | Before `Bash` with deploy/push to main | Blocks unless audit passed |

#### C. SessionStart Hooks (Context injection)

| Hook | Trigger | What It Does |
|------|---------|--------------|
| **Project detection** | Session start | Detects project type (Android/iOS/Web/Firebase) and loads relevant skills |
| **Standards injection** | Session start | Injects tech stack defaults and coding standards into context |
| **Git state check** | Session start | Reports branch, uncommitted changes, PR status |

#### D. Notification Hooks

| Hook | Trigger | What It Does |
|------|---------|--------------|
| **Desktop notification** | Permission prompt or idle | Alerts developer when Claude needs input |

---

## 3. Package Strategy — Plugin Architecture

### Current Distribution Model (Manual Copy)

```bash
cp claude-commands/*.md /path/to/your/project/.claude/commands/
```

**Problems:**
- No versioning — teams don't know which version they have
- No auto-updates — skills get stale across projects
- No hooks or settings travel with skills
- No dependency resolution
- Manual effort per project

### Recommended: Claude Code Plugin

Claude Code now supports **Plugins** — packaged bundles of skills, hooks, agents, MCP servers, and settings that can be installed and version-controlled.

#### Proposed Plugin Structure

```
ProductEngineeringSkills/
├── .claude-plugin/
│   └── plugin.json              # Plugin manifest
├── skills/                      # New SKILL.md format with frontmatter
│   ├── sdlc/
│   │   └── SKILL.md
│   ├── android-feature-scaffold/
│   │   └── SKILL.md
│   ├── ios-architect/
│   │   └── SKILL.md
│   ├── ... (all 24 skills)
│   └── feature-audit/
│       └── SKILL.md
├── agents/                      # Custom subagent definitions
│   ├── code-reviewer.md         # Security + quality review agent
│   └── project-bootstrapper.md  # New project setup agent
├── hooks/
│   └── hooks.json               # All hook configurations
├── settings.json                # Default permissions and settings
├── claude-commands/             # Legacy format (kept for backwards compat)
├── gemini skills/               # Gemini format
├── CLAUDE.md                    # Project instructions
├── README.md
└── EVALUATION.md                # This document
```

#### Benefits

1. **Install once, auto-update**: `claude plugin install cure-consulting/product-engineering-skills`
2. **Version pinning**: Teams can pin to a version or track latest
3. **Namespaced skills**: `/cure:sdlc`, `/cure:feature-audit` — no naming conflicts
4. **Hooks travel with skills**: Security gates, format enforcement ship automatically
5. **Settings defaults**: Permissions, model preferences included
6. **Marketplace distribution**: Publish to Claude Code marketplace for team-wide access

---

## 4. Enhancement Recommendations (from Claude Code Documentation)

### A. Add Frontmatter to All Skills

Every skill should have:
```yaml
---
name: skill-name
description: When to use this skill (enables auto-invocation)
argument-hint: [what-to-pass]
disable-model-invocation: false  # or true for destructive skills like deploy
allowed-tools: [tool-list]       # restrict where appropriate
---
```

### B. Add Custom Agents

| Agent | Purpose |
|-------|---------|
| **code-reviewer** | Read-only agent that audits code against your standards |
| **project-bootstrapper** | Sets up new projects with correct architecture and config |

### C. Add MCP Server Configurations

Ship recommended MCP servers in `.mcp.json`:
```json
{
  "mcpServers": {
    "github": { "type": "http", "url": "https://api.githubcopilot.com/mcp/" },
    "sentry": { "type": "http", "url": "https://mcp.sentry.dev/sse" }
  }
}
```

### D. Add Path-Specific Rules

Use `.claude/rules/` with path matchers:
- `rules/android.md` — loads when editing `*.kt` files
- `rules/ios.md` — loads when editing `*.swift` files
- `rules/web.md` — loads when editing `*.tsx` files
- `rules/firebase.md` — loads when editing `functions/**`

### E. Add Output Styles

Custom output formatting for different artifact types (PRDs vs code vs reports).

### F. Skills That Should Be Read-Only

Some skills should use `allowed-tools: [Read, Grep, Glob]`:
- `feature-audit` — should only read and report, not modify
- `security-review` — should only analyze, not change code
- `engineering-cost-model` — analysis only
- `saas-financial-model` — analysis only

### G. Skills That Should Fork Context

Long-running skills should use `context: fork` to avoid polluting the main conversation:
- `sdlc` — generates many artifacts
- `market-research` — extensive analysis
- `saas-financial-model` — complex modeling

### H. New Skills to Add

| Skill | Purpose |
|-------|---------|
| **incident-response** | Runbooks, severity classification, post-mortems |
| **accessibility-audit** | WCAG compliance checking, screen reader testing |
| **performance-review** | Load testing plans, performance budgets, optimization |
| **database-architect** | Schema design, migration planning, indexing strategy |
| **infrastructure-scaffold** | Terraform/Pulumi templates, cloud architecture |
| **code-review** | Systematic code review against team standards |

---

## 5. Implementation Priority

| Priority | Action | Impact |
|----------|--------|--------|
| **P0** | Restructure as plugin with `plugin.json` | Enables all other improvements |
| **P0** | Add frontmatter to all skills | Enables auto-invocation and tool restrictions |
| **P1** | Add hooks configuration | Connects skills, enforces standards |
| **P1** | Add CLAUDE.md with project rules | Context injection for all sessions |
| **P1** | Add `.claude/rules/` with path-specific rules | Platform-specific guidance |
| **P2** | Add custom agents | Specialized review and setup workflows |
| **P2** | Add MCP server configs | External tool integration |
| **P3** | Add marketplace manifest | Team-wide distribution |
| **P3** | Close Gemini parity gap | Full cross-platform coverage |
