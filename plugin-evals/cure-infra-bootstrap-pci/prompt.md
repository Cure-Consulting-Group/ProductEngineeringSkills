---
description: 'T85 risk eval: cure-infra-bootstrap. An unaided model cannot know the Cure manifest CLI; the skill must produce the claude-bootstrap init command with --dry-run first, the --pci and --gdpr flags, note that PCI forces vendored install mode, and finish with doctor.'
tags: [cure-infra-bootstrap]
max_turns: 20
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill]
runs: 3
---

Set up our standard Cure agent infrastructure in this repo: the managed CLAUDE.md, STATE.md, and the .claude/ folder with the right skills and rules for this stack. We take card payments through Stripe and we have EU customers. Don't write anything yet. Give me the exact commands you would run and what each one will change.
