---
description: 'T85 risk eval (gates T79): engagement-automation across Claude Code, Codex, and Antigravity. Must give Claude a routine for the unattended weekly job and /loop for the in-session check, Antigravity /schedule plus persistent sidecar Automations, and Codex app Automations (or codex cloud exec), and must never claim Codex or Antigravity lack scheduling. Expected to fail on the with-arm until T79 corrects engagement-automation:16.'
tags: [engagement-automation]
max_turns: 20
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill]
runs: 3
---

We run client engagements in Claude Code, Codex, and Antigravity, depending on whose credits are left that week. I want two things automated: (1) a dependency and security audit every Monday at 7am that runs even when my laptop is closed, and (2) a CI status check every 30 minutes while I'm working this afternoon. What's the right mechanism for each in each of the three runtimes, and what guardrails do I need?
