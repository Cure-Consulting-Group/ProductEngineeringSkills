# MAINTENANCE — Keeping the Library Aligned

The library maintains itself continuously; humans add a thin cadence on top.
Established 2026-07-11 after Wave 2 (see BACKLOG.md). Total human cost:
~30 min/month + ~1 day/quarter.

## Continuous (automated — zero effort, one rule)

Every PR runs the full gate: library audit (≥9.0 overall, ≥7.0 per item),
metadata sync, prompt-hook constraints (Stop/PostToolUseFailure only, ≤30s),
session-lifecycle non-blocking check, workflow syntax, legacy + Gemini parity.
`nightly-drift.yml` re-checks daily. Consuming projects self-update
(marketplace auto-update) and self-provision (loop.md, workflows) — there is
no fleet-rollout work.

**The one rule: never bypass `scripts/release.sh`.** It is the only path that
cannot ship a half-synced or below-bar release.

## Monthly (~30 minutes)

1. **Run bare `/loop` on this repo.** Eat our own maintenance loop: dependency
   CVEs, lint drift, TODO decay, doc staleness.
2. **Automation liveness.** Did every scheduled routine deliver its report
   since last check? A missing report is an incident, not a shrug
   (AUTOMATION.md rule). Loops expire in 7 days; webhooks and auth rot.
3. **Opportunistic tightening.** Fix a few of whatever the audit flags as LOW
   (currently trigger-text length advisories). Never let LOWs accumulate into
   a wave of their own.

## Quarterly — the meta-loop (~1 day, the one that matters)

Re-run the Wave 2 process against the then-current platform:

1. **Research** — claude-code-guide agent sweeps code.claude.com/docs for new
   execution primitives, frontmatter fields, hook events, plugin capabilities.
2. **Verify** — second agent confirms every claim with exact syntax before it
   enters a ticket. Non-negotiable: Wave 2's first research pass got 2 of 18
   platform facts wrong; encoding them would have broken 39 valid agents.
3. **Gap analysis → BACKLOG wave** — tickets in the T-numbered format
   (Status/Scope/Why/Blast radius/Acceptance/Effort), releases planned by
   semver, deviations recorded in a resolution table when done.
4. **Execute** — feature branch, per-release `release.sh` commits, PR, CI,
   merge, tags. Dry-run any new workflow against this repo before shipping it
   (Wave 2's dry-run caught a real CI blocker pre-merge).

### Standing watchlist (re-check every quarter)

- **Plugin-native workflows / output-styles / rules.** The moment plugins can
  ship these, delete the installer vendoring and the SessionStart provisioning
  hook — they exist only to work around this gap.
- **Agent-type hooks leaving experimental.** Candidate to upgrade the static
  PreToolUse security guard into a real skill-security-auditor invocation.
- **`proactiveTriggering`** becoming documented subagent frontmatter.
- **Platform floor.** Features assume Claude Code v2.1.196+ (loop scheduling
  semantics). Re-verify assumptions against release notes.
- **Skill-listing budget.** If the default budget grows or per-skill caps
  change, recalibrate DESC_COMBINED_WARN/FAIL in audit-library.py.

## Trigger-based (no schedule)

- **Consultant friction reports** from consuming projects → BACKLOG tickets
  immediately. This is the highest-signal input; the wave format is the
  container for anything bigger than a patch.
- **Publish pipeline failure** → fix same day; consumers auto-update from
  whatever main says.
- **Audit score drop or new CRIT** → blocks release by construction; treat the
  underlying cause, not the score.

## Non-negotiables (learned the hard way)

- **Nothing blocking, ever**: no network I/O in session-lifecycle hooks, every
  loop iteration terminates, prompt hooks fail open with timeouts. All
  CI-enforced — if a change needs one of these gates loosened, that is a
  design smell, not a gate problem.
- **No hand-maintained inventories.** Counts and versions live in one place
  and sync outward (`sync-metadata.py`). Wave 2 found three separate claims
  that had silently rotted, including a phantom skill.
- **Unattended runs are read-only, budget-capped, and deliver somewhere
  durable.** See AUTOMATION.md.
