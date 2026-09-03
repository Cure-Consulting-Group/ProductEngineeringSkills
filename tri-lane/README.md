# cure-tri-lane

Opt-in multi-vendor orchestration for Cure Consulting Group engagements. A Claude Code session acts as architect; Codex (GPT-5.6 Luna/Sol) implements spec-determined work and audits correctness; Antigravity (Gemini 3.8 Flash) reviews systems, security rules, infra, and CI and verifies in a browser; a fresh-context Claude advisor gives the final verdict. Every lane runs in its own git worktree and returns a machine-checkable report.

This plugin is independent of `cure-product-engineering`. Installing it changes nothing for machines that do not have it; the library keeps working exactly as before.

## Install

```
claude plugin marketplace add Cure-Consulting-Group/ProductEngineeringSkills   # once per machine; already present if the library is installed
claude plugin install cure-tri-lane@cure
/reload-plugins
```

One install per machine (user scope) covers every project. A project can disable it in its own `.claude/settings.json` under `enabledPlugins`.

## Requirements

| Requirement | Why | Check |
|---|---|---|
| Claude Code ≥ 2.1.255 | Fable 5.1 sessions; plugin hooks | `claude --version` |
| `codex` CLI, logged in with a ChatGPT plan | Codex lanes draw on Codex Pro | `codex login status` |
| `agy` (Antigravity CLI), signed in with a Google AI plan | Antigravity lane draws on the Google pools | `agy -p "/usage" --output-format json` |
| `gtimeout` (coreutils) or `timeout` | Wall-clock caps on lanes | `brew install coreutils` |
| Git repo with an integration branch | Worktrees per lane | — |

No API keys are read or stored. The lanes shell out to the two CLIs, which carry their own logins. Run the preflight to confirm everything at once:

```
python3 "$(claude plugin path cure-tri-lane 2>/dev/null || echo ~/.claude/plugins/cache/cure/cure-tri-lane/*)/skills/tri-lane/scripts/lane-preflight.py" --dir "$PWD"
```

## What you get

- `/cure-tri-lane:tri-lane` — the routing doctrine: declare a route, write the six-part spec, dispatch, verify, advisor, merge.
- Agents `codex-implementer`, `codex-reviewer`, `antigravity-analyst`, `cure-advisor`.
- `scripts/lane-preflight.py` and `scripts/lane-report.py` (stdlib Python, `--help`, `--json`).
- A PreToolUse guard that refuses `codex exec` without an explicit sandbox and headless `agy` without `--sandbox`.
- `skills/tri-lane/lanes.md`: exact flags, model slugs, caps, failure signatures, and the head-to-head log that justifies each repin.

## The incident that shaped the rails

On 2 Sep 2026, during design testing, Antigravity in plan mode reverted an uncommitted working tree because the machine's `agy` settings auto-approve every tool. The tree was restored from a diff saved beforehand. Hence: no lane ever touches a live tree, sandbox flags are explicit and hook-enforced, and the diff is saved before any cross-vendor run.

## Model pins and re-testing

Lane models are named in one place, `skills/tri-lane/lanes.md`. When a model generation changes, re-run the head-to-head on a real diff, log the result there, and repin. Do not pin models in agent frontmatter for lanes; the wrapper agents are Sonnet because they only run commands.

## Not included, on purpose

- OpenAI's `codex-plugin-cc`. Fine to install for manual `/codex:adversarial-review`; do not enable its Stop review gate. The automated lanes here call `codex exec` directly for deterministic, capped, inspectable runs.
- Gemini CLI. Dead for consumer Google plans since 18 June 2026; `agy` is the Google lane.
- Any Stop-hook or timed review loop. One advisor review per deliverable; audit reviews only on the trigger.
