# Prompt Coach — coach, don't block

A `UserPromptSubmit` hook that **never blocks your work**. When a prompt is vague,
ambiguous, or missing details that would weaken the result, it injects a short
coaching note plus a **restructured version of your prompt** — so you learn to
phrase requests better *while* the work proceeds. Clear prompts (and operational
commands like `/login`, greetings, and follow-ups) pass through silently.

## Why this exists

The official `hookify` plugin (and hand-rolled prompt validators) gate prompts
with `action: block` — a hard stop that rejects input it judges "not actionable"
and teaches you nothing. That false-positives on legitimate short commands and
breaks flow. The Cure standard is the opposite: **a weak prompt is a teaching
moment, not an error.** Coach and continue; never deny.

## Install (opt-in, per machine or per project)

Add to `~/.claude/settings.json` (all projects) or a project's
`.claude/settings.json` (just that repo):

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "prompt",
            "model": "claude-haiku-4-5",
            "prompt": "You are a prompt coach for Cure Consulting Group. The user just submitted a prompt to a Claude Code agent. You must NEVER block, deny, or stop it — the user's work ALWAYS proceeds regardless of your output. Your only job is to help the user phrase better requests over time.\n\nDecide if the prompt is already good enough. Treat as GOOD (output nothing) when it is: a slash command (e.g. /login, /commit), a short operational command, a greeting, a one-word confirmation, a direct follow-up to the current work, or any request that clearly names an action and its target. Bias strongly toward GOOD — only coach when phrasing would genuinely produce a worse result.\n\nIf the prompt is genuinely vague (no clear action, no target, or missing detail that would change the outcome), produce: (1) one sentence on what is unclear, and (2) a restructured version that names the concrete action, the target/scope, and any success criteria — inferring sensibly from context. Keep it under 80 words. Do not actually perform the task here.\n\nRespond ONLY with JSON. If good: {\"hookSpecificOutput\":{\"hookEventName\":\"UserPromptSubmit\",\"additionalContext\":\"\"}}. If coaching: {\"hookSpecificOutput\":{\"hookEventName\":\"UserPromptSubmit\",\"additionalContext\":\"PROMPT COACH (non-blocking — proceeding anyway):\\nUnclear: <one sentence>.\\nTry next time: \\\"<restructured prompt>\\\"\"}}"
          }
        ]
      }
    ]
  }
}
```

The key safety property: there is **no blocking path** in the prompt — it can only
emit `additionalContext` (advice) or nothing. The agent always runs your request.

## Replacing a hookify blocking rule

If a project has a blocking prompt rule, find and relax it:

```bash
# from the project root where the block fires:
ls .claude/hookify.*.local.md
```

In the offending file's frontmatter, change `action: block` to `action: warn`
(shows guidance, lets the work proceed) or `enabled: false` to disable it. Then
add the prompt-coach hook above for the constructive version.

## Principle

> A hook that rejects without teaching just trains people to fight the tool.
> Hooks should lower the floor (catch real danger) and raise the ceiling (coach
> toward better prompts) — never stand in the doorway.
