---
name: engagement-automation
description: "Choose and configure the right Claude Code recurring-execution mechanism — /loop, cloud routines, scheduled tasks, CI cron, or hooks — with Cure guardrails for unattended runs"
when_to_use: "Use when putting any recurring engagement work on autopilot: maintenance loops, weekly audits, monthly reports, webhook-triggered reviews. NOT for product-AI workflow patterns (agent-workflow-designer) or one-off background tasks."
argument-hint: "[task-to-automate]"
---

# Engagement Automation

Pick the right recurring-execution mechanism before wiring anything. Claude Code has five, and most automation failures come from using the wrong one: a session loop for work that must survive laptop sleep, a cloud routine for something CI already does deterministically, or unattended write-access nobody scoped.

This skill covers **harness-level** automation — Claude Code running Cure's skills on a schedule or trigger. For designing the AI workflow *inside* a product, use `/agent-workflow-designer`.

## Step 1: Classify the Mechanism

Five mechanisms. Pick exactly one per task.

| Mechanism | Runs where | Trigger | Survives laptop close? | Best for |
|-----------|-----------|---------|------------------------|----------|
| **`/loop` (fixed interval)** | Your session | Timer (`/loop 30m …`) | No | Poll-and-react within a working session: babysit CI, watch a deploy |
| **`/loop` (self-paced)** | Your session | Model picks its own cadence | No | Goal-driven iteration with a stop condition ("keep fixing until tests green") |
| **Cloud routine (`/schedule`)** | Anthropic infra | Cron, API call, or GitHub webhook | Yes | Weekly audits, monthly reports, PR-triggered reviews — no machine required |
| **CI cron (GitHub Actions)** | CI runner | Cron | Yes | Deterministic checks that need no LLM judgment (lint, license scan, `npm audit`) |
| **Hook** | Your session | Harness event (Stop, PreToolUse, ConfigChange…) | n/a | Enforcement at the moment of action, not on a clock |

Decision tree — first match wins:

```
Is it deterministic (no LLM judgment needed)?
├── Yes → CI cron. Stop. Don't spend tokens on what a shell script does.
└── No
   Is it reacting to a harness event (a tool call, a turn ending, a config change)?
   ├── Yes → hook
   └── No
      Must it run when no one is at the machine?
      ├── Yes → cloud routine
      └── No
         Is there a checkable goal it iterates toward?
         ├── Yes → /loop self-paced (model stops itself when done)
         └── No  → /loop fixed interval
```

## Step 2: Gather Context

1. **Cadence** — how often, and what happens if a run is missed? (Missed-run-tolerant → cron/routine. Must-react-fast → loop in session.)
2. **Write surface** — does the automated run only read and report, or does it change things? Everything write-capable needs the guardrails in Step 4.
3. **Token budget** — cost per run × runs per month. A weekly deep audit at ~200k tokens is fine; the same audit hourly is not.
4. **Failure visibility** — who notices when it silently stops? Routines need a delivery channel (issue, PR comment, email); loops die with the session.
5. **Trigger source** — clock, GitHub event, or external system (API-triggered routine)?

## Step 3: Configure the Chosen Mechanism

### /loop — session-scoped

```
/loop 30m /cure-product-engineering:burn-rate-tracker     # fixed interval
/loop keep the test suite green until I say stop          # self-paced, goal-driven
/loop                                                     # bare: runs the project maintenance loop
```

- Bare `/loop` uses `.claude/loop.md` if present (Cure projects get a standard one vendored at install — deps, lint drift, TODO decay, coverage regression).
- Recurring loops expire after **7 days**; re-arm with `--resume` or a fresh `/loop`.
- Scheduled fires only run skills Claude may auto-invoke: **never** set `disable-model-invocation: true` on a skill meant to be looped. To keep a loopable skill out of the `/` menu, use `user-invocable: false` instead.

### Cloud routine — /schedule

```
/schedule weekly dependency + security audit, Mondays 07:00, report as GitHub issue
```

- Triggers: cron schedule, authenticated API POST, or GitHub webhook (PR opened, release published).
- Runs on Anthropic infrastructure with **no local permission prompts** — treat every routine as unattended (Step 4 applies in full).
- Always set the per-routine token limit and daily run cap. No exceptions.
- Interactively-authenticated MCP servers are absent in headless runs — don't build a routine around one.
- See `docs/AUTOMATION.md` in the plugin repo for copy-paste recipes.

### CI cron

If the check is expressible as a shell command with a pass/fail exit code, it belongs in `.github/workflows/`, not in an LLM loop. Use `/ci-cd-pipeline` to scaffold it.

### Hook

If the real requirement is "every time X happens, do Y", that's a hook, not a schedule. See `hooks/hooks.json` in the plugin for the Cure defaults (Stop quality gate, skill security guard, ConfigChange audit).

## Step 4: Unattended-Run Guardrails (Cure policy)

Anything that runs without a human watching:

1. **Read-only by default.** Unattended runs report; humans apply. The never-unattended list — production deploys, database migrations, dependency upgrades that auto-merge, anything touching secrets or billing — is absolute.
2. **Budget caps are mandatory.** Per-run token limit + daily run cap on every routine. A silently-degraded routine that retries hourly is a four-figure surprise.
3. **Deliver somewhere durable.** Every run ends by writing its result to an issue, PR comment, or report file. A routine whose output only lives in a session transcript doesn't exist.
4. **Stop conditions, not vibes.** Self-paced loops state the goal AND the give-up condition ("stop when tests pass or after 5 attempts; report either way").
5. **Verify liveness monthly.** Loops expire in 7 days; routines fail silently when auth or webhooks rot. Put a "check the automations" line in the engagement's recurring ops.

## Step 5: Output

Produce an **Automation Plan** for each task:

```
AUTOMATION PLAN — [task]
Mechanism:    [loop-fixed | loop-self-paced | routine | ci-cron | hook]
Trigger:      [interval / cron / event]
Invocation:   [exact /loop or /schedule command, or workflow file path]
Write access: [none | scoped to X — justification]
Budget:       [tokens per run, runs per day cap]
Delivery:     [issue / PR comment / report file path]
Stop/expiry:  [goal + give-up condition, or expiry re-arm plan]
Owner:        [who checks liveness, cadence]
```

Cross-references: `/agent-workflow-designer` for product-AI workflow patterns, `/ci-cd-pipeline` for CI cron scaffolds, `/incident-response` for what to do when an automation pages you. Skills with a documented recurring shape carry a "Recurring Mode" section (finops, burn-rate-tracker, investor-reporting, security-review, and others).
