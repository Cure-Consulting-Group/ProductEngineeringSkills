# Solicitation Triage

Decide fast whether a solicitation is addressed to you at all.

The governing fact of portal-driven business development: **most of what arrives in a bid feed is not
addressed to your firm, and the expensive mistake is reading it as though it might be.** A public
procurement portal is a firehose of legally-required publications — renewals, notices, formalities,
commodity purchases, and construction work — filtered by commodity codes that were never designed to
describe consulting. Reading each one carefully is a full-time job that produces nothing.

Triage is a **sorting function with a fixed time budget**. Its output is a verdict and a paragraph of
intelligence — never a bid folder. Building structure before deciding is how sunk cost starts arguing
for the bid.

> **The one-hour rule.** One hour, one file, one verdict. If triage runs longer than an hour, the answer
> is usually no — a solicitation that takes three hours to understand well enough to disqualify is
> telling you what bidding and delivering it would be like.

## Pre-Processing (Auto-Context)

Triage context, gathered before the skill runs. Values are injected inline below; in an environment that
does not execute them, run the shown commands instead.

- Today: !`date +%Y-%m-%d`
- Target profile: !`sed -n '1,40p' TARGET-PROFILE.md ../TARGET-PROFILE.md ../../TARGET-PROFILE.md 2>/dev/null || echo "(no TARGET-PROFILE.md — write one first, see capture-management)"`
- Pipeline: !`sed -n '1,25p' PIPELINE.md ../PIPELINE.md ../../PIPELINE.md 2>/dev/null || echo "(no PIPELINE.md)"`
- Documents in hand: !`ls *.pdf *.docx *.xlsx src/*.pdf src/*.xlsx 2>/dev/null | head -20 || echo "(none staged)"`
- Prior verdicts: !`ls -d ../triage/*/ ../archive/*/ triage/*/ archive/*/ 2>/dev/null | head -20 || echo "(no history)"`

Extract text before reading, so the documents are greppable:

```bash
mkdir -p src
for f in src/*.pdf; do pdftotext -layout "$f" "${f%.pdf}.txt"; done
```

`-layout` preserves table columns, which is what makes cost forms and rubrics readable as text.

## Step 1: Classify the instrument before reading the scope

**This is the step most firms skip, and it disqualifies more solicitations than the scope does.** The
document type determines whether a response is even possible, and half of a typical portal feed is
instruments that a services firm cannot win by writing a better proposal.

| Instrument | What it actually is | Correct response | Typical verdict |
|---|---|---|---|
| **RFP** (Request for Proposals) | Competitive, evaluated against a published rubric, technical merit counts | Full proposal | **The only instrument worth a full pursuit** |
| **RFQ** (Request for Quotes) | Price competition on a defined scope | Quote | Bid only if the scope is genuinely defined and price is winnable |
| **ITB / IFB** (Invitation to Bid) | Lowest responsive responsible bidder, no technical scoring | Sealed bid | Decline unless you are structurally the low cost |
| **RFI / Sources Sought / Market Research** | Pre-solicitation. Not an award vehicle | **Always respond** — this is the shaping window | **Respond, never "bid"** — highest leverage in the whole cycle |
| **Sole Source Notification / Notice of Intent** | Buyer intends to award non-competitively and must publish first | Statement of Capabilities — **only if genuinely responsive** | **Decline and harvest.** See below |
| **Prequalification / RFQual / SOQ** | Builds a shortlist for future work | Qualifications package | Respond if in-market — cheap option on future RFPs |
| **Cooperative / piggyback notice** (OGS, NASPO, Sourcewell, OMNIA) | Buyer purchasing off someone else's awarded contract | None available | Decline — unless you hold the vehicle |
| **Renewal / amendment / change order notice** | Existing contract extended | None | Decline and harvest the renewal date |
| **Emergency procurement** | Award already made under emergency authority | None | Decline; note what broke |
| **BPA / IDIQ / term contract / on-call** | Pool award; task orders compete later | Pool response | Often excellent for small firms — low per-task bid cost afterward |
| **Bid tabulation / award notice** | Results of a closed procurement | None | **Pure intelligence.** Incumbent, price, and field, published free |

### Sole source notices deserve a specific rule

A sole source notification is the publish-and-see-if-anyone-objects step a buyer must take before
awarding without competition. It typically permits exactly two responses: prove you can supply the
incumbent's product (usually requiring **the incumbent's own written authorization**), or propose an
alternative meeting the same requirements.

Read the alternative path's conditions carefully. Language like *"without disrupting current operations
or requiring substantial data conversion"* is **written to be unsatisfiable** — no replacement of a
system of record avoids substantial data conversion. When that clause is present, the notice is a
procedural formality, not a market test.

**The rule: triage in ten minutes, never file, always harvest.** Filing a Statement of Capabilities that
is non-responsive on its face costs you credibility with a named buyer and buys nothing — these notices
create no shortlist, no bidders list, and no scoring record. But see `buyer-intelligence`: sole source
notices disclose the incumbent, the exact product, the exact annual spend, the customization inventory,
and the renewal anniversary, all in public, for free.

## Step 2: The ten-minute read order

Read these four things, in this order, before page 5 of the scope. Each can end triage on its own.

| Order | Read | Ends triage when |
|---|---|---|
| 1 | **The instrument type** (Step 1) | It is not an instrument you can respond to |
| 2 | **The cost form** | Per-unit pricing → product procurement (Step 3) |
| 3 | **The scoring rubric** | Product match + price > ~50% of available points |
| 4 | **Mandatory qualifications** | A bar you cannot clear and cannot team around |

**The cost form and the rubric are usually findable in ten minutes and disqualify more solicitations
than the scope does.** Scope is what everyone reads first and is the least decisive of the four.

### Mandatory qualifications: read the operative verb

"Must provide three public-sector references" is a bar. "Should demonstrate relevant experience" is a
preference. Bars are long-lead procurement facts — references, licensure, insurance limits, bonding,
certifications, registrations — and **no amount of writing fixes them in the final week.** If a bar is
unclearable and teaming is not permitted, triage is over regardless of how good the fit looks.

## Step 3: The services-versus-product test

The most common way a small consulting firm wastes a week: treating a **product procurement** as a
services engagement. The buyer wants to license something that already exists. You are being invited to
be a reference quote in someone else's win.

| Fingerprint | Reading |
|---|---|
| **Per-unit cost template** — per image, per GB, per user, per seat, per transaction, per request | 🔴 Product. An incumbent with volume pricing wins on arithmetic |
| A rubric line for "**product match**" or a feature-by-feature compliance matrix | 🔴 Product, and probably written from a specific product's datasheet |
| Requirements enumerated as feature checkboxes rather than outcomes | 🔴 Wired to an existing system |
| "Must integrate with `<named commercial system>`" without naming an integration standard | 🟡 Incumbent-adjacent; check who owns that system |
| Demo or sandbox required at proposal time | 🔴 You must already have a shipping product |
| Migration required "without substantial data conversion" | 🔴 Unsatisfiable by anyone but the incumbent |
| **Milestone or hourly pricing**, deliverable-based | 🟢 Services engagement — you compete |
| Rubric weighting technical approach, methodology, governance, accessibility, security | 🟢 Specialist territory |

**Check the cost form before reading the scope.** Its shape tells you what kind of firm the document was
written for, faster than any amount of prose.

## Step 4: Run the gate check

Score against the firm's written target profile. If there is no written profile, stop and write one —
`capture-management` covers it. Triage without a profile is opinion.

| # | Criterion | Pass? |
|---|---|:--:|
| 1 | Value inside the target band | ☐ |
| 2 | Implied peak team within capacity | ☐ |
| 3 | Duration within the target range | ☐ |
| 4 | Insurance limits and endorsements bindable | ☐ |
| 5 | Past performance satisfiable, or teaming permitted | ☐ |
| 6 | No bonding, no clearances | ☐ |
| 7 | Payment terms the balance sheet can float | ☐ |
| 8 | RFI window still open | ☐ |
| 9 | Rubric weights technical quality over size and price | ☐ |
| 10 | You can name a **specific** reason you would win | ☐ |

**Below 8 of 10 → decline without further analysis.** Set the threshold before scoring; moving it after
seeing the total is how a firm rationalizes a pursuit it has already committed to emotionally.

Criterion 10 is the one that catches wishful pursuits. "We're a good fit" is not a reason. "The rubric
puts 45 of 100 points on accessibility and AI governance, which large SIs answer with boilerplate" is.

### Hard disqualifiers — any one ends triage

- Deadline passed or unreachable alongside current delivery commitments
- **Requires a product you do not have** — including a license, a platform, or an OEM authorization
- Requires a facility, fleet, licensure, or physical operation
- Requires a professional opinion only a licensed firm may sign (audit, legal, engineering seal, medical)
- Sustained team beyond capacity
- Bonding or clearances
- Insurance you cannot bind
- Uncapped liability on safety-critical scope

## Step 5: Reach one of four verdicts

| Verdict | Meaning | Action |
|---|---|---|
| **PROMOTE** | Passed the gate. Worth the day it costs to evaluate properly | Move to `active/`, rename with the due date, build the full folder, run `rfp-evaluation` |
| **WATCH** | Right buyer, wrong solicitation — or the call hinges on a pending fact | Stays in triage **with a revisit date**. No date means no verdict |
| **DECLINE** | Failed the gate | Move to `archive/`. **Keep the record** — the reason is what makes the pipeline learn |
| **DECLINE AND HARVEST** | Unwinnable as a bid, valuable as intelligence | Decline, then run `buyer-intelligence` before filing it away |

The fourth verdict is the one firms omit, and it covers most of a portal feed. Sole source notices, award
notices, cooperative piggybacks, and product procurements are all unwinnable and all informative. **A
solicitation you cannot bid still tells you a buyer's incumbent, budget, renewal date, and procurement
cadence** — which is the input to winning the next one.

**Nothing stays in triage without a verdict.** A folder with no verdict older than two weeks is a process
failure, not a pending decision.

## Step 6: Write one file

One `QUALIFY.md`, verdict at the top, no subfolders. Wanting an `01-analysis/` directory is the signal to
promote, not to build structure in triage.

```markdown
# Qualification — <SOLICITATION>

**VERDICT: <PROMOTE / WATCH / DECLINE / DECLINE AND HARVEST>**
**Triaged:** <date> by <name> · **Time spent:** <minutes>
**Revisit by:** <date, if WATCH>

> One line: why this verdict.

## Facts
| Issuer | Solicitation # | **Instrument** | **Due** | Channel | Term | Est. value |
| Award basis | Multiple awards? | Addenda | Questions deadline | Pre-proposal conference | No-contact clause |

## Gate check — _ / 10
<the table, with a note per failed line>

## Hard disqualifiers
<checked list>

## What it actually is
<2–4 sentences. Services, product, or hybrid? What kind of firm was this written for?
Distinguishing that is most of the qualification work.>

## Effort order of magnitude
<Bracket only — hundreds / low thousands / 10k+ hours. Do not decompose in triage.>

## Verdict and rationale
<3–5 sentences.>

## If DECLINE — is there another angle?
| Subcontract to a likely prime | Bid one unbundled area | Position for next cycle | Adjacent need revealed |

## Intelligence worth keeping
<buyer, incumbent, rubric pattern, renewal date, follow-on need — hand to `buyer-intelligence`>
```

Then record the verdict in the pipeline. **Including the declines** — the pattern of what you decline is
the only calibration signal the target profile ever gets.

## Step 7: Triage at portal volume

A weekly alert batch is a different task from a single solicitation. Budget by instrument, not by
document length.

| Pass | Budget | Action |
|---|---|---|
| **Sort by instrument** | ~1 min each | Step 1 classification from the title and first page. Most of the batch resolves here |
| **Cost form and rubric** | ~10 min each | Only for surviving RFP/RFQ/RFQual items |
| **Full triage** | ≤ 1 hr each | Only for those that pass the ten-minute read |
| **Harvest** | ~10 min each | Every sole source notice, award notice, and renewal notice in the batch |

Realistic shape of a week's feed for a small services firm: a large majority resolve at pass 1, a handful
reach pass 2, and zero to two reach full triage. **A batch that produces no declines means the alerts
are mis-tuned, not that the market is rich.**

Tune the feed at the source. Issuer-level alerts on named target buyers outperform commodity-code alerts,
because commodity codes describe commodities and consulting is not one.

## Calibration

Review quarterly, against the record of declines.

| Signal | Reading |
|---|---|
| No declines in the pipeline | Profile is too loose, or you are not sourcing enough |
| Nothing qualifies for two quarters | Profile is too tight, or you are looking in the wrong places |
| Everything declines for the **same** reason | Fix that gap permanently, or re-tune the alerts. It is a standing tax |
| Declines are caught late (after hours of reading) | Move the catching test earlier in the read order |
| Triage regularly exceeds an hour | The profile lacks a bright line the documents can be tested against |

When a test catches two or more declines, promote it up the read order. Cure's services-versus-product
test earned its place at position 2 that way.

## Anti-patterns

| Anti-pattern | Why it fails |
|---|---|
| Reading the scope first | The scope is the least decisive of the four things worth reading |
| Not classifying the instrument | You will write a proposal to a document that cannot be responded to |
| Building a bid folder before the verdict | Sunk cost then argues for bidding |
| Filing against a sole source notice with no authorization or product | Non-responsive on its face; spends credibility with a named buyer for nothing |
| Treating an unsatisfiable clause as an opening | "Without substantial data conversion" is a wall, not a door |
| Triaging without a written target profile | Produces opinion, not qualification |
| Adjusting the gate threshold after scoring | Rationalizing a decision already made |
| Discarding declines | Throws away intelligence you already paid for by reading |
| WATCH with no revisit date | A deferral wearing a verdict's clothes |
| Commodity-code alerts only | Commodity codes do not describe consulting; you get noise and miss target buyers |

## Handoff

- Passed the gate, needs full requirement extraction → `rfp-evaluation`
- Requirements extracted, needs the resourced go/no-go → `bid-decision`
- Declined but the buyer is worth keeping → `buyer-intelligence`
- Contract form attached and worth reviewing before promoting → `public-sector-contracting`
- No target profile yet, or the pipeline is empty → `capture-management`
- Effort bracket needs to become a real number → `technical-estimation`
