# Cure mods for Claude Code

Nine [Claude Code mods](https://code.claude.com/docs/en/plugins/mods/overview.md), published in the `cure` marketplace (this repository) beside the skill library. Each is its own plugin, so you install only the ones you want.

| Mod | What it does | Where the rule came from | Tests |
|---|---|---|---|
| `cure-policy-guard` | Refuses a tool call that breaks a written house rule, unless you override. File writes: no cron, Vertex-only Gemini in PHI repos, no new AI vendor in minors' repos, no hard-coded credentials, no building another machine's state rows. Bash and WebFetch: no request to a consumer AI API from a PHI or minors' repo. Every override is recorded; `/policy-guard` lists them. | Org no-cron policy (2026-08-08); Level5 `BAA_INVENTORY.md`; minors' data in TIR / SPEDTECH / LearnLift; a hardcoded Gemini key; DistrictZero `state-targets.md` | 30 |
| `cure-lane-verifier` | When a subagent or tri-lane lane reports back, attaches git's account of the branches and worktrees the report names. A "complete" with an empty branch is flagged `EMPTY COMPLETION`. | Memory rule *verify lane output by mutation*: a lane reported 42 passing tests with an empty diff | 14 |
| `cure-spend-band` | Today's GitHub Actions spend beside the spinner and a dismissible warning when the month is on pace to exceed the plan's included usage. `/spend` gives the detail. | The September 2026 Actions overage ($264) | 19 |
| `cure-cache-band` | How long the prompt cache has left, the session's hit rate and misses, and what a cold next message re-caches. `/cache` gives the detail and the session's cost. | A cold cache re-bills the whole context at the write rate | 20 |
| `cure-image-viewer` | Draws the images you sent above the prompt until the turn that carried them ends. | Terminal UI graphics | 14 |
| `cure-cite-check` | Checks `file:line` citations in Claude's answers against the session's repositories and toasts the stale ones. Never edits the answer. `/cite-check`. | Memory rule *verify before asserting architecture* | 23 |
| `cure-agent-budget` | Caps how many subagents one session runs at once, tracked by agent id. Optional research routing to a model alias, off by default. `/agents-budget`. | Runaway subagent fan-out | 14 |
| `cure-rules-band` | The house rules of the repository the session is in, above the prompt; nothing for a repo with none. `/rules`. | Cross-repo context switching | 10 |
| `cure-lane-board` | Tri-lane worktrees, branches, commits ahead, dirty files and pull requests. `/lanes`. | Multi-vendor work across worktrees | 16 |

Retired in Wave 7 (T73): `cure-llm-ledger`, `cure-secret-scrub`, `cure-ci-preview` and `cure-handoff` were dropped (`token-ledger` and `secret-redactor` in `vetted-mods` cover the first two); `cure-egress-guard` and `cure-claim-guard` are now rules in `cure-policy-guard`. If you installed them, run `scripts/uninstall-all-mods.sh --retired`. [PLAN.md](PLAN.md) has the reasons.

## Install

Mods need **Claude Code 2.1.287 or later** (`claude --version`); the `userConfig` pickers need 2.1.271 or later.

Install every mod the marketplace lists (the script reads `.claude-plugin/marketplace.json`, shows each error and exits non-zero if any install fails):

```sh
scripts/install-all-mods.sh            # user scope; or: project | local
```

Or one at a time:

```sh
/plugin marketplace add Cure-Consulting-Group/ProductEngineeringSkills
/plugin install cure-policy-guard@cure
```

`scripts/uninstall-all-mods.sh [--retired] [scope]` removes them the same way.

## Update

```
/plugin marketplace update cure
/plugin update cure-cache-band@cure
```

With auto-update on for the `cure` marketplace, merged changes arrive at the next session start. A mod's new code is picked up when its `version` in `.claude-plugin/plugin.json` changes: bump it in the same commit as the change.

Mods are not sandboxed, so auto-update means a merge to `main` here runs on every machine that installed them. Review a mod PR as you would a change to a hook.

To turn one off, use `/plugin` → Installed. To run a session with no mods at all, use `claude --safe-mode`.

## What they touch

Mods run with your user's access. These nine:
- read files;
- run `git` (always as `git -C <dir>`), `gh` (spend band and lane board), `hostname` (policy guard, only for a state-claim check), and `id -u` and `file` (image viewer);
- make no network calls of their own beyond `gh`;
- never write outside Claude Code's own plugin store.

Per Bash call, the mods add no subprocess: policy-guard checks the command's text for an AI vendor host before it looks anything up, and cite-check only records the paths a command names. Drawing a band never spawns a process.

## Settings

Each mod's options are `userConfig` rows in `/plugin` → the mod → Configure (stored under `pluginConfigs`):

| Mod | Options |
|---|---|
| `cure-policy-guard` | `askTimeoutSeconds` (60): the override question refuses after this long, so unattended sessions and /loop never stall |
| `cure-agent-budget` | `maxConcurrent` (8, 0 = off); `routeResearchTo` (`off` \| `sonnet` \| `haiku`, default `off`) |
| `cure-cite-check` | `noteToClaude` (off): also tell Claude about stale citations on its next turn |
| `cure-spend-band` | `org`, `allowanceUsd` (300), `paceWarning` (on). `CURE_SPEND_ORG` / `CURE_SPEND_ALLOWANCE` override |
| `cure-cache-band` | `ttl` (`auto` \| `5m` \| `1h`). `CURE_CACHE_TTL` overrides |
| `cure-image-viewer` | `imageDir` (empty: guess). `CURE_IMAGE_DIR` overrides |

## The mods in detail

### cure-policy-guard

It inspects Claude's `Write`, `Edit`, `MultiEdit` and `NotebookEdit` calls, and only the text each call **adds** (an edit that removes a violation goes through), plus `Bash` and `WebFetch` calls.

| Rule | Fires when |
|---|---|
| `no-cron` | A `schedule:` trigger is added to `.github/workflows/*.yml` |
| `level5-vertex-only` | In a PHI repo (Level5): `@google/generative-ai`, `generativelanguage.googleapis.com` or `GEMINI_API_KEY` |
| `minors-new-ai-vendor` | In a minors' repo: an import of an AI vendor SDK that the nearest `package.json` doesn't already list |
| `hardcoded-secret` | A Google, Anthropic, OpenAI, GitHub or Stripe key, or a private key, in any file except `.env*` |
| `state-claim` | In DistrictZero: a `scripts/build-<st>-*` write for a state that `.agents/state-targets.md` (read from the file's own repo) gives to another machine. Host names match exactly, without the domain |
| `ai-egress` | A Bash command or WebFetch URL that names a consumer AI API host (matched as a whole host name) from a PHI or minors' repo. The repo is the one a leading `cd <dir>` or `git -C <dir>` names, else the session's |

The repos and patterns are one table, `mods/shared/rules.ts`, which the rules band displays too. Mods install one folder each, so `mods/shared/vendor.py` copies it into each consumer; edit the source and re-run it.

How it decides what happens:
- **Interactive session:** you're asked "Refuse it / Allow this once (logged)".
- **Nobody answers within `askTimeoutSeconds`**, nobody can be asked (`-p`, headless agents), or the question is dismissed: the call is refused, and Claude is told the rule and its source.
- **The guard itself fails** before deciding: the call is refused (fail closed).

Known gap: a file written through `Bash` (`cat >`, `sed -i`) is not inspected for the file rules. CI and the org scanners remain the backstop.

### cure-agent-budget

Counts the subagents this session started (`agent.spawn`) and has not seen finish (their `turn.complete`), reconciled against `$.agent.list()`, in session state. A new session starts at 0; the 0.1.0 machine-wide count is deleted at session start. Workflow agents and teammates are not counted. With `routeResearchTo` set, a research-shaped subagent that names no model, under an Opus session, runs on that alias; "use opus" in the prompt opts out.

### cure-cite-check

After each main-loop answer it extracts `path:line` and `path#Lnn` citations (never `host.tld:port`, URLs or versions) and resolves each against the session root, its git toplevel, the repositories the session touched (files it read or edited, folders its commands named) and the toplevel's tracked files. A citation is flagged when its line is past the end of the file, or when its file is missing although its folder exists in the session's repos. Anything else it cannot find is counted as unverified, not flagged, because it may live in a repository the session never touched. Line counts are cached by mtime, so an unchanged file is read once. Measured on this repo's last 50 answers: 0 false flags in 96 citations (0.1.0: 89 of 91 flags false).

### cure-rules-band

Shows `rules ● <repo> · <rules>` for a repo in the shared table, or the rules in that repo's `.cure/rules.json`. A worktree reads as its main repo. `/rules hide` dismisses it for the session.

### cure-lane-board

`/lanes` lists `lane/*` branches with their worktrees, commits ahead of `origin/HEAD`, dirty files and open PRs (with merge-queue position). All git calls run against the session root, in two parallel rounds.

### cure-lane-verifier

Where it reads reports:
- **Foreground `Agent` results:** the note rides as model-only `context` after the result.
- **Background hand-backs:** engine attachments and peer messages carrying a hand-back marker get the note appended.

What it extracts from a report:
- absolute paths;
- `lane/<task>` names;
- "branch \`x\`" mentions.

What git reports for each target, read-only:
- commits ahead of `origin/HEAD`;
- `diff --shortstat`;
- uncommitted files.

**The alarm:** a completion claim plus a named branch with nothing on it. An empty named branch raises the alarm even if a named checkout is dirty with unrelated work; this case was found during the live test.

Limits:
- Branch names are looked up in the session's repository only.
- Report parsing is pattern-based.
- If git can't answer, the target says "could not verify". That's never treated as empty.

### cure-spend-band

How it gets the numbers:
- **Source:** `gh api organizations/{org}/settings/billing/usage` through your logged-in `gh`. One fetch serves the machine: the month is kept in the mod's store with its `fetchedAt`, and a session fetches only when that copy is over 15 minutes old (`/spend` wants one under a minute old). The call times out at 25 s. No token is stored.
- **Settings:** `org` and `allowanceUsd` (see Settings above). `/spend dismiss` hides the pace warning until the month ends; `/spend show` brings it back.

How to read the numbers:
- **The projection** is month to date plus the last three full days' average for the rest of the month. Before the first full day it falls back to month-to-date pace.
- **"Billed so far"** is what GitHub actually charges, all products and seats included. The Actions figures are gross, before included usage.
- **If a refresh fails,** `/spend` says so under the last good numbers.

### cure-cache-band

```
cache ● 1h ████████████████ 59m left · hit 76% · misses 0
cache ● 5m ███░░░░░░░░░░░░░ 53s left · hit 36% · misses 1
cache ○ cold · next message re-caches 82k tokens
```

Green while warm, amber under a quarter of the TTL, red once cold.

What is measured and what is assumed:
- **Measured:** hit rate, misses and token counts come from the usage each model response reports. Nothing is fetched.
- **Assumed:** the TTL. The API does not report it per response, so the mod takes `1h` on a subscription inside its limits and `5m` on an API key or once a limit window is exhausted. Set the `ttl` option (or `CURE_CACHE_TTL`) to `5m` or `1h` when that is wrong; `/cache` says which was used.
- **Cost:** `/cache` shows the session's cost as the engine reports it (`$.session.usage().cost`). The mod keeps no price table.

Definitions:
- **Hit rate** is tokens read from the cache over all prompt tokens this session.
- **A miss** is a request that read less than half of the prefix the request before it left in the cache: an expiry, a model switch, a compaction or an edited prefix.
- **Main conversation only:** a subagent keeps a cache of its own and is not counted.

Limit: after a resume the band shows nothing until the first response, because it cannot know when the cache was last touched.

### cure-image-viewer

It shows the images of the prompt you just sent and keeps them up until that turn ends. At most four (one, with a count, when the band is narrower than 100 columns), each at most 10 rows by 40 columns, in the picture's own aspect.

Why not while you are still typing: Claude Code saves a pasted image when the prompt is submitted, not when it is pasted, so a draft's image is not on disk to draw.

Where the pictures come from:
- The plugin API gives a pasted image's kind, never its bytes. The mod reads the copy Claude Code saves at `<tmp>/claude-<uid>/<project>/<session>/images/<N>.png`.
- That layout is this build's (2.1.289), not a documented contract. If a sent image's file is not there the row says `[Image #N] not found on disk`. Set the `imageDir` option (or `CURE_IMAGE_DIR`) to point it elsewhere. The pictures' bytes are dropped when the turn ends.

What draws the picture:
- The terminal, through the kitty graphics protocol. The mod sends the PNG's bytes inline, not a file path for the terminal to open. Tested in Warp 0.2026.09.30 on 2026-10-07 with a script outside Claude Code: inline bytes drew, a file path drew nothing.
- An image over 2 MiB cannot be sent inline and is captioned with its size instead. Large retina screenshots can exceed that.
- On a surface with no image element (the desktop app), each image is a caption with its pixel size.

Pasting a file copied in Finder gives Claude the file's icon, not its contents. Copy from Preview, or drag the file in.

## Verification

### Wave 7 (2026-10-24, Claude Code 2.1.306)

`python3 mods/check.py` is the gate (CI runs it): 9 mods, every one green on `claude plugin test` and `claude plugin validate --strict`, 160 tests; marketplace and mod folders match; `mods/shared/` copies current; no retired model ID under `mods/` or `design/`.

Each defect fixed in Wave 7 has a test that fails on the old code, among them: a stuck machine-wide agent count cleared at session start; a session restart at 0 running; an "audit" Agent call not rewritten to another model; cite-check resolving against the toplevel and never editing the answer; `host.tld:port` not read as a citation; a 60 s ask timeout; one git call per folder; spend-band's one fetch per machine.

Not yet confirmed live: the ask timeout against the real hook budget (the kit confirms the race; the docs say a wait inside a `$` call does not count against the 10 s limit), and five parallel "audit" agents on the session model in a real session.

### 2026-10-05 (Claude Code 2.1.289)

**Validation:** `claude plugin validate` passes for each mod and for the marketplace.

**Tests:** `claude plugin test <mod>` ran 42 tests across these three mods then (current counts are in the table at the top):

| Mod | Tests |
|---|---|
| Guard | 17 |
| Lane verifier | 14 |
| Spend band | 11 |

Each suite covers the pure rules and arithmetic, plus the hook end to end with stubbed git, `gh`, the store, the clock and the question dialog.

**Mutation testing:** 19 deliberate breakages, all caught.
- **Guard:** rule regexes, exemptions, override logic, failing open, Edit coverage.
- **Lane verifier:** the alarm logic, a dropped note, the background path, a reversed commit count.
- **Spend band:** the product filter, the projection, the warning threshold, the requested month, timer start and cancel.

Two survived the first pass:
- **Edit coverage:** the guard had no end-to-end test of `Edit`, so a test was added.
- **Hand-back detection:** the mutation was badly built and still matched, so it was rebuilt; the rebuilt one is caught.

**Live runs** in a real 2.1.289 session:
- **Guard:** refused a cron workflow and the file was not created.
- **`/spend`:** returned live numbers.
- **Lane verifier:** flagged an echoed "complete" on an empty `lane/` branch.

**Bugs found by the live runs and fixed:**
- The timer handle is `{ cancel }`, not a function.
- The empty-branch case above.

Run the tests:

```sh
for m in cure-policy-guard cure-lane-verifier cure-spend-band; do claude plugin test mods/$m; done
```

### 2026-10-07 (Claude Code 2.1.289)

| Mod | Tests |
|---|---|
| Cache band | 18 |
| Image viewer | 12 |

Both pass `claude plugin validate` and type-check. Each suite covers the pure arithmetic plus the hooks end to end with a stubbed clock, model response, file listing and `file`.

**Mutation testing:** 12 deliberate breakages. Three survived the first pass:
- **Cache band, first-request guard:** the guard was redundant and was removed.
- **Cache band, survey:** no test mounted the band under a survey, so one was added.
- **Image viewer, id prefix:** image 1 matched `10.png`; a test was added.

One still survives: removing the image viewer's check for a surface with no `Image` element does not fail its test.

**Image viewer 0.3.0 (2026-10-07):** switched from a file path to inline bytes after the Warp test above; four mutations of that change were each caught. Established since 0.1.0: a pasted image's file exists only after submit.

**Not yet confirmed live:** whether Claude Code sends images to Warp at all. The Warp test proved the terminal can draw them, not that the engine will ask it to. The cache band has loaded in a session but its figures have not been checked against a known cache state.

```sh
for m in cure-cache-band cure-image-viewer; do claude plugin test mods/$m; done
```

What to build next: [IDEAS.md](IDEAS.md).
