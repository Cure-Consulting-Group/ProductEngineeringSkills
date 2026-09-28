# Legal domain

Four skills and three agents for legal work, New York first, built to a measured standard.

## Disclaimer

Everything here produces draft analysis for a licensed attorney to review. It is not legal
advice, creates no attorney-client relationship, and a benchmark score is not a license to
practice (NY Judiciary Law §§478, 484). Model output is never authority; citations are verified
or flagged, never assumed.

## How they fit together

```
legal-research ─────── authority, citation form, cite_check.py (every citation verified or flagged)
     │
legal-doctrine ─────── 14 subject files: majority rule → NY distinction → exam traps
     │
     ├──→ legal-analyst (agent) ──→ IRAC memo + authorities table ──→ attorney
     │
bar-benchmark ──────── measures the above: MBE / NYLE / MPRE / MEE-style bank, live two-arm runs

legal-doc-scaffold ─── ToS / privacy / NDA templates (user-invoked only)
contract-reviewer, legal-compliance (agents) ─ business-risk and compliance scans; hand doctrine
                                                questions to legal-analyst
```

| Skill / agent | Use when |
|---|---|
| `legal-research` | A question needs controlling authority, or a draft's citations need checking |
| `legal-doctrine` | Analyzing an issue by subject, or answering a bar-style question |
| `bar-benchmark` | Measuring competency or the skills' uplift; gating changes to legal skills |
| `legal-doc-scaffold` | Drafting ToS, privacy policy, SOW, NDA templates (explicit invocation only) |
| `legal-analyst` agent | End-to-end research memo with verified citations |

## Measuring it

```bash
python3 skills/legal/bar-benchmark/scripts/validate_bank.py
python3 skills/legal/bar-benchmark/scripts/run_live.py --backend claude --arm both
```

The bare arm is the model alone; the doctrine arm adds the matching reference file. The
difference is what the skills are worth. Results accumulate in `bar-benchmark/results/`; the
validation record for the bank is `bar-benchmark/benchmark/VALIDATION.md`.

## Citation verification setup (once per machine)

Nothing is required: case citations are checked against CourtListener's public search API
(one request a second) and statutes against nysenate.gov / Cornell LII with `--live`. For
faster batch case checks, create a free CourtListener account and export its token:

```bash
export COURTLISTENER_API_TOKEN=…
```
