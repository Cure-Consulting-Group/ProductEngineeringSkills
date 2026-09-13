# Tri-Lane production runs by failure cause

**Date:** 2026-09-13  
**Source:** `lane-eval.py classify --production --all-projects` (Wave 4, T46) over every `.git/tri-lane/run/*` directory in the eight repositories  
**Evidence grade:** every run in this window predates 1.10.0, so no `report.json` or `verify.jsonl` exists; causes come from prose signatures in `final.md`, `stderr.log`, and `agy.stderr` (`evidence_grade: signature-only`). Treat counts as a floor for infra causes and expect a few false positives in prose (one `quota` hit is a `429` inside a Mermaid diagram).

## Histogram, 142 run directories

| Cause or state | Runs |
|---|---:|
| `unclassified` | 116 |
| `sandbox-denied` | 16 |
| `service-unavailable` | 7 |
| `refused-by-instruction` | 1 |
| `quota` | 1 |
| `scope-violation` | 1 |

`unclassified` = no failure signature and no report: documents, Antigravity-only audits, advisor calls, and Codex runs that completed cleanly. The instrumented runs from 1.10.0 onward classify from the report and the raw VERIFY streams instead.

## By repository

| Repository | `unclassified` | `sandbox-denied` | `service-unavailable` | `refused-by-instruction` | `quota` | `scope-violation` |
|---|---:|---:|---:|---:|---:|---:|
| DistrictZero | 6 | · | · | 1 | · | · |
| Finality | 12 | 1 | · | · | · | · |
| NationalLacrosseTourApp | 4 | · | · | · | · | · |
| cannabis-retail-platform | 15 | 2 | · | · | · | · |
| cure-finops-watchdog | 10 | · | · | · | · | · |
| iep-and-thrive | 21 | 7 | 4 | · | 1 | 1 |
| initiated-recruiting | 3 | 1 | · | · | · | · |
| statledger | 45 | 5 | 3 | · | · | · |

## What the causes say

- **Zero `cache-miss`.** Not one run in ten days carries a cold-cache signature. The gate for the Codex review's private-cache preparation lifecycle (five `cache-miss` in thirty logged tasks) is not met; that work stays held.
- **`sandbox-denied` is the dominant infra cause (16), and almost all of it is loopback.** Evidence lines are `listen EPERM 127.0.0.1` from an emulator hub, a Unix-socket restriction on `npx tsx`, and Xcode cache paths. This is the Gradle lock-listener class (closed at 1.9.2 by opening the sandbox network for Gradle) showing up for Firebase emulators, Node test servers, and Xcode. The fix is the same shape: a VERIFY profile that opens loopback for emulator-backed commands, recorded in GAPS, not a cache.
- **`service-unavailable` (7) is CoreSimulator and offline package resolution on iOS lanes.** Caching cannot supply a simulator; the SPM part would be the first real cache signal if it recurs under 1.10.0 evidence.
- **`scope-violation` (1)** is a model-class result and counts against the lane, per the 1.9.0 policy. No stall signature survived the word-boundary check (an earlier pass counted four `install` lines as stalls; the regex now requires the word).

Re-run after thirty instrumented tasks: `python3 tri-lane/skills/tri-lane/scripts/lane-eval.py classify --production --all-projects` and `lane-eval.py failures`.
