# Worked example: valuing a studio product for a raise and an offer

**Every number here is illustrative**, chosen to show the method and to reconcile. None of it is
market data: in a real valuation each peer multiple, round and rate is looked up, sourced and dated
(see comps.md and dcf.md), and the result is not investment advice.

## The question

A Cure studio product (a vertical SaaS for youth-sports scheduling) is raising a seed extension, and
a strategic buyer has floated an acquisition. The owner asks: *what is it worth, and is the offer
good?*

| Fact (illustrative) | Value |
|---|---|
| ARR today | \$420,000 |
| Growth, next twelve months | 110% → NTM revenue \$882,000 |
| Gross margin | 78% |
| Net burn | \$55,000 / month, 18 months of runway |

## Step 1: Classify

Early-revenue and private, so the primary methods are **recent private rounds** and **public revenue
comps with a stated private-company discount** (comps.md, third row of the classify table). A DCF is
run only as a scenario check (dcf.md, classify). The offer is a **private deal**, so the merger test
is ownership, cash and payback, not EPS (merger.md, classify).

## Step 2: Comps with a private discount

| Input | Value | Note |
|---|---|---|
| Median EV / NTM revenue, nearest public vertical-SaaS peers | 6.0x | as-of date and source required |
| Private-company discount | 30% | size, illiquidity, key-person risk; state it, don't bury it |
| Applied multiple | 6.0 × (1 − 0.30) = **4.2x** | |
| Implied EV | 4.2 × \$882,000 = **\$3.70M** | |

## Step 3: Recent comparable rounds

Three seed/Series A rounds in the same sector and stage priced at **12x, 15x and 20x** ARR at the time
of the raise (post-money ÷ ARR). Median 15x × \$420,000 = **\$6.30M**. Rounds are priced on hope as much
as on revenue, which is why they sit above the discounted public comps.

## Step 4: DCF as a scenario check, and why it is not the answer

Venture discount rate 30%, terminal growth 4%, revenue growth slowing 80% → 60% → 40% → 30%, free-cash-
flow margin −45% → −15% → 5% → 15% → 20%:

| Year | Revenue | FCF | PV at 30% |
|---|---:|---:|---:|
| 1 | \$0.88M | −\$0.397M | −\$0.305M |
| 2 | \$1.59M | −\$0.238M | −\$0.141M |
| 3 | \$2.54M | \$0.127M | \$0.058M |
| 4 | \$3.56M | \$0.533M | \$0.187M |
| 5 | \$4.62M | \$0.925M | \$0.249M |

Sum of PVs \$0.047M; terminal value \$0.925M × 1.04 ÷ (0.30 − 0.04) = \$3.70M, worth \$0.996M today.
**EV \$1.04M, with the terminal value 95.5% of it**: well past the 75% flag in dcf.md. The cross-check
fails too: the terminal value implies about 0.6x terminal-year revenue, far below any peer multiple.
Both say the same thing: at this stage a DCF measures the discount rate, not the business. Report it as
a scenario and say so; don't average it into the range.

## Step 5: The range

| Method | EV |
|---|---:|
| Public comps, 30% private discount | \$3.70M |
| Comparable rounds, median | \$6.30M |
| **Range presented** | **\$3.7M – \$6.3M, mid \$5.0M** |
| DCF scenario (not in the range) | \$1.04M, TV 95.5% of EV |

The mid is the plain average of the two methods that measure the same thing; say so. Weight one higher
only with a reason you can state (e.g. "rounds in this sector reset 30% lower last quarter").

## Step 6: The offer, as a private deal

Offer \$5.0M: 60% cash (\$3.0M), 40% in the buyer's stock (\$2.0M at its last-round price, post-money
\$40M, so 2.0 ÷ 42.0 = **4.76%** of the buyer after issuance).

- **Headline vs. effective.** Private stock is illiquid; with a 30% haircut the stock is worth \$1.4M
  and the offer \$4.4M effective, below the \$5.0M mid even though the headline equals it.
- **What would make it good:** more cash, a stock price set at a discount to the last round, a
  liquidation-preference match, or an earn-out tied to the ARR the buyer is paying for.
- **The alternative is not zero.** Compare against raising the extension: 18 months of runway now,
  and what the round costs in dilution (hand the runway and raise timing to `burn-rate-tracker`).

## What the write-up says

```markdown
## Valuation: [studio product] — as of [date] (illustrative figures)
Range $3.7M–$6.3M EV, mid $5.0M: public revenue comps 4.2x NTM (6.0x peer median, 30% private
discount) and comparable rounds at 15x ARR (median of 12/15/20x). DCF scenario $1.04M, terminal value
95.5% of EV: reported, not used.
Offer: $5.0M headline (60/40 cash/stock), $4.4M effective after a 30% haircut on 4.76% of the buyer.
Counter: raise the cash share or price the stock below the last round; consider an ARR earn-out.
Not investment advice.
```
