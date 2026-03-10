# ProductEngineeringSkills — Cure Consulting Group

This is the central skill library for all Cure Consulting Group projects. It is distributed as a Claude Code plugin.

## What This Repo Is

A **Claude Code plugin** containing 24 production-grade skills, 2 custom agents, hooks for enforcement, and path-specific rules. Other projects install this plugin to get consistent standards.

## Repository Structure

```
.claude-plugin/plugin.json    — Plugin manifest (name, version, metadata)
skills/*/SKILL.md             — 24 skills with frontmatter (new format)
agents/*.md                   — Custom subagent definitions
hooks/hooks.json              — Automated enforcement hooks
rules/*.md                    — Path-specific coding standards
settings.json                 — Default permission rules
claude-commands/*.md           — Legacy command format (backwards compat)
gemini skills/*.skill          — Google Gemini skill packages
```

## Development Rules

- When adding a new skill, create it in `skills/{name}/SKILL.md` with proper YAML frontmatter
- Every skill must have: `name`, `description`, and `argument-hint` in frontmatter
- Read-only skills (audits, analysis) should set `allowed-tools: ["Read", "Grep", "Glob"]`
- Destructive or sensitive skills should set `disable-model-invocation: true`
- Keep the legacy `claude-commands/` format in sync for backwards compatibility
- Create both Claude and Gemini versions of each skill
- Follow the existing format: Step 1 (Classify), Step 2 (Gather Context), Step 3+ (Framework/Output)

## Versioning

Bump the version in `.claude-plugin/plugin.json` when making changes:
- Patch (2.0.x): Fix typos, clarify wording
- Minor (2.x.0): Add new skills, add hooks, add rules
- Major (x.0.0): Breaking changes to skill interfaces or structure

@README.md
