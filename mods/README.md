# Cure mods for Claude Code

Five [Claude Code mods](https://code.claude.com/docs/en/plugins/mods/overview.md), published in the `cure` marketplace (this repository) beside the skill library. Each is its own plugin, so you install only the ones you want. The first three each turn a rule or lesson the portfolio already has in writing into a check that runs. The last two are displays.

| Mod | What it does | Where the rule came from |
|---|---|---|
| `cure-policy-guard` | Refuses a file write that breaks a written house rule, unless you override. Every override is recorded; `/policy-guard` lists them. | Org no-cron policy (2026-08-08); Level5 `BAA_INVENTORY.md`; minors' data in TIR / SPEDTECH / LearnLift; the hard-coded Gemini key found in TIR scripts |
| `cure-lane-verifier` | When a subagent or tri-lane lane reports back, attaches git's account of the branches and worktrees the report names. A "complete" with an empty branch is flagged `EMPTY COMPLETION`. | Memory rule *verify lane output by mutation*: a lane reported 42 passing tests with an empty diff |
| `cure-spend-band` | Shows today's GitHub Actions spend beside the spinner and a warning under the prompt when the month is on pace to exceed the plan's included usage. `/spend` gives the detail. | The September 2026 Actions overage ($264) |
| `cure-cache-band` | Shows above the prompt how long the prompt cache has left, the session's hit rate and misses, and, once it lapses, how many tokens the next message re-caches. `/cache` gives the detail. | A cold cache re-bills the whole context at the write rate |
| `cure-image-viewer` | Draws the images you paste above the prompt, from the draft until the turn that sent them ends. | — |

## Install

Mods need **Claude Code 2.1.287 or later** (`claude --version`). This machine had 2.1.285 on 2026-10-05:

```sh
brew upgrade --cask claude-code@latest
```

Try one without installing (it hot-reloads when you save a file):

```sh
claude --plugin-dir mods/cure-policy-guard   # from a checkout of this repository
```

Install for every session. The marketplace is the one the skill library already uses:

```
/plugin marketplace add Cure-Consulting-Group/ProductEngineeringSkills
/plugin install cure-policy-guard@cure
/plugin install cure-lane-verifier@cure
/plugin install cure-spend-band@cure
/plugin install cure-cache-band@cure
/plugin install cure-image-viewer@cure
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

It shows the images the draft names (`[Image #1]`), then keeps the submitted ones up until that turn ends. At most four, each at most 10 rows by 40 columns, in the picture's own aspect.

Where the pictures come from:
- The plugin API gives a pasted image's kind, never its bytes. The mod reads the copy Claude Code saves at `<tmp>/claude-<uid>/<project>/<session>/images/<N>.png`.
- That layout is this build's (2.1.289), not a documented contract. If a file is not there the row says `[Image #N] not found on disk`. Set `CURE_IMAGE_DIR` to point it elsewhere.

What draws the picture:
- The terminal, through the kitty graphics protocol (kitty, Ghostty). Elsewhere, and on the desktop surface, each image is a caption with its pixel size.

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
| Image viewer | 10 |

Both pass `claude plugin validate` and type-check. Each suite covers the pure arithmetic plus the hooks end to end with a stubbed clock, model response, file listing and `file`.

**Mutation testing:** 12 deliberate breakages. Three survived the first pass:
- **Cache band, first-request guard:** the guard was redundant and was removed.
- **Cache band, survey:** no test mounted the band under a survey, so one was added.
- **Image viewer, id prefix:** image 1 matched `10.png`; a test was added.

One still survives: removing the image viewer's check for a surface with no `Image` element does not fail its test.

**Not yet run live:** neither mod has been exercised in a real session as of this commit. Unverified: whether a pasted image's file exists before the prompt is submitted, and whether Warp draws the picture.

```sh
for m in cure-cache-band cure-image-viewer; do claude plugin test mods/$m; done
```

What to build next: [IDEAS.md](IDEAS.md).
