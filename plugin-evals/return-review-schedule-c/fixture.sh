#!/usr/bin/env bash
# Fixture scaffold (runs only under --scaffold). A draft 2025 Form 1040 + Schedule C summary for a
# sole-proprietor software developer, with planted review findings: 1099-NEC total exceeds gross
# receipts by $14,350; the deductible half of SE tax (§164(f)) is missing from Schedule 1; a round
# home-office figure; an unexplained 400% supplies jump; and 2022–2024 software R&E still being
# amortized under old §174 when §174A (OBBBA) allows the remaining balance to be deducted.
set -euo pipefail
mkdir -p return-2025
cat > return-2025/summary.md <<'__FIXTURE_EOF__'
# Draft 2025 return — Dana Okafor (sole proprietor, custom software development)
Filing status: Single. Prepared by the taxpayer in tax software; not yet reviewed.

## Source documents received
| Form 1099-NEC payer | Amount |
|---|---|
| Brightline Health LLC | $88,000 |
| Northgate Logistics Inc. | $61,250 |
| Parcel & Pine Co. | $32,500 |
| Ozark Analytics LLC | $15,000 |
| **Total 1099-NEC** | **$196,750** |

Bank deposits from clients (business account): $196,750.

## Schedule C (as entered)
| Line | Item | 2025 | 2024 |
|---|---|---|---|
| 1 | Gross receipts | $182,400 | $171,900 |
| 8 | Advertising | $1,200 | $1,150 |
| 11 | Contract labor | $22,000 | $19,500 |
| 18 | Office expense / supplies | $9,800 | $1,950 |
| 22 | Supplies (software subscriptions) | $4,300 | $4,100 |
| 27a | Other: §174 amortization of 2022–2024 software development costs | $9,500 | $9,500 |
| 30 | Home office (simplified? no — actual expense method) | $6,000 | $3,412 |
| 31 | **Net profit** | **$129,600** | **$132,288** |

Unamortized balance of 2022–2024 §174 software development costs at 12/31/2024: $38,000.

## Schedule SE
Net earnings from self-employment (92.35% of $129,600): $119,686
Self-employment tax: $18,312

## Schedule 1
Line 3 business income: $129,600
Line 15 deductible part of self-employment tax: $0
Line 16 SEP/SIMPLE/qualified plans: $0

## Form 1040
AGI: $129,600
QBI deduction (§199A): $25,920 (20% of Schedule C net profit)
Standard deduction: $15,750
Taxable income: $87,930
Estimated payments made: $16,000
__FIXTURE_EOF__
