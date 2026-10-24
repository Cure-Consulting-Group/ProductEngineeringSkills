# Engagement Automation

Pick the right recurring-execution mechanism before wiring anything. Claude Code has six, and most automation failures come from using the wrong one: a session loop for work that must survive laptop sleep, a cloud routine for something CI already does deterministically, or unattended write-access nobody scoped.

This skill covers **harness-level** automation — Claude Code running Cure's skills on a schedule or trigger. For designing the AI workflow *inside* a product, use the `agent-workflow-designer` skill.

**Done** when each task has one Automation Plan (Step 5) with an exact invocation, a budget cap, a durable delivery target, and a liveness owner.

**Other runtimes** (checked 2026-10-24; these change monthly, so confirm before use):
- **Antigravity (agy)** has `/schedule`: one-shot timers and recurring five-field cron. They are
  conversation-scoped ("timers and schedules belong to the conversation that created them"), so
  they stop with that conversation, like `/loop`. For persistent schedules use an Automation: a
  sidecar whose `sidecar.json` sets `"builtin": "schedule"` with a cron expression and a command,
  under `~/.gemini/config/sidecars/<id>/`. It survives restarts and starts a fresh agent
  conversation on each run. Sources: antigravity.google/docs/commands/schedule,
  antigravity.google/docs/sidecars.
- **Codex** Automations (scheduled tasks) run in the ChatGPT desktop app (locally, while the app is
  open) or on the web (no local folders). "Codex CLI doesn't provide the Scheduled management
  interface" (learn.chatgpt.com/docs/automations). Headless options for CI cron or a system
  scheduler: `codex exec …` (stable), or `codex cloud exec` to submit a Codex Cloud task
  (experimental in codex-cli 0.163.0).
- Both can load plugin hooks, but Cure's `hooks/hooks.json` assumes Claude Code's environment —
  don't reuse it there. Background: `docs/evaluations/2026-09-23/platform-facts.md` in the plugin repo.

## Step 1: Classify the Mechanism

Six mechanisms. Pick exactly one per task.

| Mechanism | Runs where | Trigger | Survives laptop close? | Best for |
|-----------|-----------|---------|------------------------|----------|
| **`/loop` (fixed interval)** | Your session | Timer (`/loop 30m …`) | No | Poll-and-react within a working session: babysit CI, watch a deploy |
| **`/loop` (self-paced)** | Your session | Model picks its own cadence | No | Goal-driven iteration with a stop condition ("keep fixing until tests green") |
| **Cloud routine (`/schedule`)** | Anthropic infra (fresh clone) | Cron (≥1h), API call, or GitHub webhook | Yes | Weekly audits, monthly reports, PR-triggered reviews — no machine required |
| **Desktop scheduled task** | Your machine, Claude Desktop app | Hourly/daily/weekly or custom cron | No: runs only while the app is open and the machine awake; one catch-up run on wake | Recurring work that needs local files, tools, or MCP config files |
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
      ├── Yes → needs local files or tools, and the machine stays on?
      │        ├── Yes → Desktop scheduled task
      │        └── No  → cloud routine
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
/loop 10m check this PR's CI and summarize new review comments   # fixed interval
/loop keep the test suite green until I say stop                  # self-paced, goal-driven
/loop                                                             # bare: runs the project maintenance loop
```

- Bare `/loop` uses `.claude/loop.md` if present (Cure projects get a standard one vendored at install — deps, lint drift, TODO decay, coverage regression).
- Use `/loop` for minutes-to-hours polling. Monthly or weekly work (a burn-rate review, a
  dependency audit) belongs in a cloud routine or Desktop scheduled task, not a session loop.
- Recurring loops expire after **7 days**: they fire once more, then delete themselves. To keep
  one going, cancel and recreate it before then, or move it to a Desktop or cloud task.
- `claude --resume` / `--continue` restores fixed-interval tasks that haven't expired (no catch-up
  for missed runs). It does not restore a self-paced `/loop` or an expired task: run `/loop` again.
  Source: code.claude.com/docs/en/scheduled-tasks (Limitations), checked 2026-10-24.
- Scheduled fires only run skills Claude may auto-invoke: **never** set `disable-model-invocation: true` on a skill meant to be looped. To keep a loopable skill out of the `/` menu, use `user-invocable: false` instead.

### Cloud routine — /schedule

```
/schedule weekly dependency + security audit, Mondays 07:00, report as GitHub issue
```

- Triggers: cron schedule, authenticated API POST, or GitHub webhook (PR opened, release published).
- Runs on Anthropic infrastructure with **no local permission prompts** — treat every routine as unattended (Step 4 applies in full).
- Always set the per-routine token limit and daily run cap — an uncapped routine that retries is an open-ended bill.
- Interactively-authenticated MCP servers are absent in headless runs — don't build a routine around one.
- See `docs/AUTOMATION.md` in the plugin repo for copy-paste recipes.

### Desktop scheduled task

In Claude Desktop's **Code** tab → **Scheduled** → **New task**, with **Only on this computer** on
and a local folder picked; or ask any Desktop session ("run the dependency audit every weekday at
9am"). Each run starts a fresh session; the prompt lives at `~/.claude/scheduled-tasks/<name>/SKILL.md`.

- Runs only while the app is open and the machine awake; a missed run gets one catch-up run on
  wake, so put a time guard in the prompt when timing matters.
- Permission mode is set per task. In Manual mode an unapproved tool stalls the run until someone
  answers — do a **Run now** first and always-allow what it needs.
- Turn on **Worktree** in the Edit form so a run doesn't act on uncommitted changes.
- Source: code.claude.com/docs/en/desktop-scheduled-tasks, checked 2026-10-24.

### CI cron

If the check is expressible as a shell command with a pass/fail exit code, it belongs in `.github/workflows/`, not in an LLM loop. Use the `ci-cd-pipeline` skill to scaffold it.

### Hook

If the real requirement is "every time X happens, do Y", that's a hook, not a schedule. See `hooks/hooks.json` in the plugin for the Cure defaults (Stop quality gate, skill security guard, ConfigChange audit).

## Step 4: Unattended-Run Guardrails (Cure policy)

Anything that runs without a human watching:

1. **Read-only by default.** Unattended runs report; humans apply. The never-unattended list — production deploys, database migrations, dependency upgrades that auto-merge, anything touching secrets or billing — stays human-run, because a wrong unattended change there is irreversible or costly before anyone sees it.
2. **Budget caps are mandatory.** Per-run token limit + daily run cap on every routine. A silently-degraded routine that retries hourly is a four-figure surprise.
3. **Deliver somewhere durable.** Every run ends by writing its result to an issue, PR comment, or report file. A routine whose output only lives in a session transcript doesn't exist.
4. **Stop conditions, not vibes.** Self-paced loops state the goal AND the give-up condition ("stop when tests pass or after 5 attempts; report either way").
5. **Non-blocking iterations, always.** Every loop iteration terminates: non-interactive commands only, no watch mode or dev servers, no prompts, hard timeouts on anything slow. One blocked iteration silently kills the whole automation.
6. **Turn ends are reports, not completion.** Opus 5.5 ends turns on progress updates; an unattended run that treats one as "done" stops partway. Give the run a checklist and the early-stop instruction from `docs/AUTOMATION.md`; continue a run that ends with open items and no named blocker at most 2–3 times, then stop for review.
7. **Verify liveness monthly.** Loops expire in 7 days; routines fail silently when auth or webhooks rot. Put a "check the automations" line in the engagement's recurring ops.

## Step 5: Output

Produce an **Automation Plan** for each task:

```
AUTOMATION PLAN — [task]
Mechanism:    [loop-fixed | loop-self-paced | routine | desktop-task | ci-cron | hook]
Trigger:      [interval / cron / event]
Invocation:   [exact /loop or /schedule command, Desktop task name, or workflow file path]
Write access: [none | scoped to X — justification]
Budget:       [tokens per run, runs per day cap]
Delivery:     [issue / PR comment / report file path]
Stop/expiry:  [goal + give-up condition, or expiry re-arm plan]
Owner:        [who checks liveness, cadence]
```

Cross-references: `agent-workflow-designer` for product-AI workflow patterns, `ci-cd-pipeline` for CI cron scaffolds, `incident-response` for what to do when an automation pages you. Skills with a documented recurring shape carry a "Recurring Mode" section (finops, burn-rate-tracker, investor-reporting, security-review, and others).
