# Cure mods for Claude Code

Fifteen [Claude Code mods](https://code.claude.com/docs/en/plugins/mods/overview.md), published in the `cure` marketplace (this repository) beside the skill library. Each is its own plugin, so you install only the ones you want.

| Mod | What it does | Where the rule came from | Tests |
|---|---|---|---|
| `cure-policy-guard` | Refuses a file write that breaks a written house rule, unless you override. Every override is recorded; `/policy-guard` lists them. | Org no-cron policy (2026-08-08); Level5 `BAA_INVENTORY.md`; minors' data in TIR / SPEDTECH / LearnLift; hardcoded Gemini key | 17 |
| `cure-lane-verifier` | When a subagent or tri-lane lane reports back, attaches git's account of the branches and worktrees the report names. A "complete" with an empty branch is flagged `EMPTY COMPLETION`. | Memory rule *verify lane output by mutation*: a lane reported 42 passing tests with an empty diff | 14 |
| `cure-spend-band` | Shows today's GitHub Actions spend beside the spinner and a warning under the prompt when the month is on pace to exceed the plan's included usage. `/spend` gives the detail. | The September 2026 Actions overage ($264) | 14 |
| `cure-cache-band` | Shows above the prompt how long the prompt cache has left, the session's hit rate and misses, and, once it lapses, how many tokens the next message re-caches. `/cache` gives the detail. | A cold cache re-bills the whole context at the write rate | 18 |
| `cure-image-viewer` | Draws the images you paste above the prompt, from the draft until the turn that sent them ends. | Terminal UI graphics | 10 |
| `cure-secret-scrub` | Redacts API keys, tokens, and private keys from Read, Grep, and Bash outputs before they enter model context. `/secret-scrub` lists stats. | Leaked credentials in session exploration across 34 repos | 16 |
| `cure-llm-ledger` | Per-turn token and dollar cost ledger attributed by repo, branch, and model. Appends atomic JSONL records; `/ledger` gives session breakdown. | Anthropic spend absent from `v_billing_unified` | 8 |
| `cure-cite-check` | Verifies `file:line` code citations in assistant answers against disk, flagging missing files and out-of-range lines. Adds `/cite-check`. | Memory rule *verify before asserting architecture*: stale file:line citations | 10 |
| `cure-claim-guard` | Enforces multi-machine state file ownership rules in shared repos (DistrictZero `state-targets.md`), blocking cross-machine collisions. Adds `/claims`. | DistrictZero CLAUDE.md multi-machine coordination | 11 |
| `cure-ci-preview` | Pre-push GitHub Actions runner time and cost estimator. Warns when commits mix doc notes with code. Adds `/ci-preview`. | Costly matrix builds and lost docs-only skip optimization | 9 |
| `cure-agent-budget` | Enforces subagent concurrency caps and automatically down-routes read-only research subagents from Opus to Sonnet. Adds `/agents-budget`. | Runaway subagent fan-out token costs | 9 |
| `cure-egress-guard` | Blocks unauthorized outbound data transmission to external AI vendor endpoints in sensitive repos (PHI, minors). Adds `/egress-guard`. | Level5 PHI and student data privacy guardrails | 10 |
| `cure-rules-band` | Displays repository house rules and legal/architectural constraints in a HUD banner above the prompt. Adds `/rules`. | Cross-repo context switching and forgotten house rules | 7 |
| `cure-handoff` | Drafts structured `STATE.md` handoff blocks from git commits, branch status, and working tree diffs. Adds `/handoff`. | Manual STATE.md handoff drift | 3 |
| `cure-lane-board` | Multi-lane dashboard for tri-lane worktrees, branches, live commits, and defect window status. Adds `/lanes`. | Multi-vendor orchestration tracking across worktrees | 5 |

## Install

Mods need **Claude Code 2.1.287 or later** (`claude --version`).

Install for every session:

```sh
/plugin marketplace add Cure-Consulting-Group/ProductEngineeringSkills
/plugin install cure-policy-guard@cure
/plugin install cure-lane-verifier@cure
/plugin install cure-spend-band@cure
/plugin install cure-cache-band@cure
/plugin install cure-image-viewer@cure
/plugin install cure-secret-scrub@cure
/plugin install cure-llm-ledger@cure
/plugin install cure-cite-check@cure
/plugin install cure-claim-guard@cure
/plugin install cure-ci-preview@cure
/plugin install cure-agent-budget@cure
/plugin install cure-egress-guard@cure
/plugin install cure-rules-band@cure
/plugin install cure-handoff@cure
/plugin install cure-lane-board@cure
```

## Update

```
/plugin marketplace update cure
/plugin update cure-cache-band@cure
```

With auto-update on for the `cure` marketplace, merged changes arrive at the next session start. A mod's new code is picked up when its `version` in `.claude-plugin/plugin.json` changes: bump it in the same commit as the change.

Mods are not sandboxed, so auto-update means a merge to `main` here runs on every machine that installed them. Review a mod PR as you would a change to a hook.

To turn one off, use `/plugin` → Installed. To run a session with no mods at all, use `claude --safe-mode`.

Mods are not sandboxed: they run with your user's access. These five:
- read files;
- run `git`, plus `gh api` (spend band only) and `id -u` and `file` (image viewer only);
- make no network calls of their own beyond `gh`;
- never write outside Claude Code's own plugin store.

## The mods in detail

### cure-policy-guard

It inspects Claude's `Write`, `Edit`, `MultiEdit` and `NotebookEdit` calls, and only the text each call **adds**: an edit that removes a violation goes through.

| Rule | Fires when |
|---|---|
| `no-cron` | A `schedule:` trigger is added to `.github/workflows/*.yml` |
| `level5-vertex-only` | In Level5: `@google/generative-ai`, `generativelanguage.googleapis.com` or `GEMINI_API_KEY` |
| `minors-new-ai-vendor` | In initiated-recruiting(-nil), SPEDTECH, LearnLift or iep-and-thrive: an import of an AI vendor SDK that the nearest `package.json` doesn't already list |
| `hardcoded-secret` | A Google, Anthropic, OpenAI, GitHub or Stripe key, or a private key, in any file except `.env*` |

How it decides what happens:
- **Interactive session:** you're asked "Refuse the write / Allow this once (logged)".
- **Nobody to ask** (`-p`, headless agents) or the question is dismissed: the write is refused, and Claude is told the rule and its source.

Known gap: a file written through `Bash` (`cat >`, `sed -i`) is not inspected. CI and the org scanners remain the backstop.

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
- **Source:** `gh api organizations/{org}/settings/billing/usage` through your logged-in `gh`, every 15 minutes and on `/spend`. No token is stored.
- **Settings:** `CURE_SPEND_ORG` (default `Cure-Consulting-Group`) and `CURE_SPEND_ALLOWANCE` (default `300`, in USD).

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
- **Assumed:** the TTL. The API does not report it per response, so the mod takes `1h` on a subscription inside its limits and `5m` on an API key or once a limit window is exhausted. Set `CURE_CACHE_TTL=5m` or `1h` when that is wrong; `/cache` says which was used.

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
- That layout is this build's (2.1.289), not a documented contract. If a sent image's file is not there the row says `[Image #N] not found on disk`. Set `CURE_IMAGE_DIR` to point it elsewhere.

What draws the picture:
- The terminal, through the kitty graphics protocol. The mod sends the PNG's bytes inline, not a file path for the terminal to open. Tested in Warp 0.2026.09.30 on 2026-10-07 with a script outside Claude Code: inline bytes drew, a file path drew nothing.
- An image over 2 MiB cannot be sent inline and is captioned with its size instead. Large retina screenshots can exceed that.
- On a surface with no image element (the desktop app), each image is a caption with its pixel size.

Pasting a file copied in Finder gives Claude the file's icon, not its contents. Copy from Preview, or drag the file in.

## Verification (2026-10-05, Claude Code 2.1.289)

**Validation:** `claude plugin validate` passes for each mod and for the marketplace.

**Tests:** `claude plugin test <mod>` runs 42 tests:

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

### Added 2026-10-07 (Claude Code 2.1.289)

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
