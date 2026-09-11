# Repo Inventory — Template

One row per repository with activity in the tax year, one intake sheet per repo
that will carry a QRE. Build it from actual commit history rather than memory:

```bash
cure-repo-activity [ROOT] --year YYYY [--json]
```

Line counts are not a useful signal — they are inflated by committed lockfiles
and vendored dependencies. **Commit count and active months** are the reliable
activity measures, and neither is a substitute for a time study.

The three columns that decide the tax result are **Entity**, **Character**, and
**Release date**. Everything else is context.

## Character values

| Value | Meaning | §174A | §41 credit |
|---|---|---|---|
| `Commercial` | Sold/leased/licensed to third parties | Yes | Yes — exempt from the IUS test |
| `Internal-use` | Used only internally | Yes | Only if it clears the high threshold of innovation |
| `Client` | Built for a paying client who bears the risk / owns the IP | Yes | **No — funded research under §41(d)(4)(H)** |
| `Non-qualifying` | Marketing, cosmetic, routine | §162 | No |
| `Determine` | Not yet classified | — | — |

Mark each classification **provisional** until the owner confirms it. An
unconfirmed `Commercial` in a QRE base is a penalty exposure, not a rounding
issue.

## Inventory

| Repo | Product | Entity | Character | Commits | Months | Activity window | Release date | Notes |
|---|---|---|---|---:|---:|---|---|---|
| `shipped-app` | Customer-facing app | OpCo | Commercial | ~1,000 | ~8 | Q1 → Q3 | mid-year | Live in production; payments live |
| `beta-app` | Pre-release product | NewCo | Commercial | ~300 | ~6 | Q1 → Q3 | not yet released | Beta; entire year in the strong-QRE window |
| `internal-tooling` | Back-office automation | OpCo | Internal-use | ~100 | ~6 | Q1 → Q3 | n/a | IUS — high threshold of innovation applies |
| `client-site` | Client engagement | OpCo | **Client (CONFIRMED)** | ~50 | ~4 | Q2 → Q3 | n/a | Funded research — deductible, **no credit** |
| `marketing-site` | Company website | OpCo | Non-qualifying | ~25 | ~6 | Q1 → Q3 | n/a | Style and cosmetic work |
| `side-project` | Unclear | ? | Determine | ~25 | ~3 | Q1 → Q2 | ____ | If not a trade or business, **no deduction at all** (§262) |

## Per-repo intake — complete one per repo before year end

```
Repo:
Product / business component:
Owning entity:
Character:  Commercial | Internal-use | Client | Non-qualifying

Performed OUTSIDE the United States?          Y / N   -> if Y, 15-yr §174
Funded by a client who bore the risk?         Y / N   -> if Y, no credit
Does the client own the IP?                   Y / N   -> if Y, no credit

Commercial release date (or "not yet released"):  __________
   -> effort BEFORE this date is the strong-QRE window
   -> effort after is maintenance unless a genuinely new component

TECHNICAL UNCERTAINTY at project start (what was unknown?):


ALTERNATIVES evaluated, and how they were tested:


Evidence:  [ ] design docs  [ ] ADRs  [ ] spikes/abandoned branches
           [ ] benchmarks   [ ] tickets  [ ] commit history

PEOPLE - who worked on it, role, pct of their year, W-2 wages:
   name              role              pct     W-2 wages     >=80%?
   ______________    ____________     ___%    \$________      Y/N

CONTRACTORS - name, amount, US/foreign, risk clause, IP clause:
   ______________  \$________  US/FOR   risk: ______  IP to: ______

CLOUD/COMPUTE - dev/test/training vs production hosting:
   dev/test \$________   production \$________   basis: ______
```

## The questions that block a credit computation

Work these before computing anything. Each one can zero out a line of the claim.

1. **Which repos are client work?** Funded research is deductible but carries
   **no credit**. A repo named after a client is a prompt to confirm, not a
   conclusion — and an unflagged client site in the QRE base is the most common
   version of this error.
2. **Was there W-2 payroll?** No wages means **zero wage QREs**, and the credit
   collapses to supplies plus 65% of qualifying contractor spend. Paying wages
   solely to manufacture a credit is net-negative; the compensation has to be
   justified on its own terms first.
3. **What is each product's release date?** Effort before commercial release is
   the strong-QRE window; effort after it is maintenance unless a genuinely new
   component is being built. **Lock each release date as it happens** — it is the
   most perishable fact in the file and nobody reconstructs it accurately a year
   later.
4. **Which entity owns each repo?** An unassigned repo cannot be allocated to a
   return. Where one entity develops for another, the credit follows whoever bore
   the risk and holds the rights, not whoever wrote the code.
5. **Is every repo actually a trade or business?** A personal project is §262 —
   not deductible at all, let alone creditable.
6. **Does any repo serve a §280E industry without being in it?** A software
   vendor selling to a cannabis retailer is **not** trafficking, so §280E does
   not reach it. Book it separately from any licensed activity so the distinction
   is obvious on its face.
