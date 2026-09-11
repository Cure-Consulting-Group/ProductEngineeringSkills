---
name: buyer-intelligence
description: "Turn solicitations you cannot win into a durable buyer, incumbent, and renewal-date database — harvest sole source and award notices, and time the approach"
when_to_use: "Use after a DECLINE verdict, on any sole source or award notice, or when building a target-buyer dossier. NOT for sourcing or the target profile (use capture-management). NOT for screening a solicitation (use solicitation-triage)."
argument-hint: "[buyer-or-notice]"
allowed-tools: ["Read", "Grep", "Glob", "Bash", "Write", "Edit", "WebSearch", "WebFetch"]
---

# Buyer Intelligence

Harvest what you already paid for by reading.

Every solicitation you decline cost you the time it took to decline it. That cost is sunk either way —
the only question is whether you keep anything. Most firms keep nothing, throw the document away, and
meet the same buyer again eighteen months later knowing no more than the first time.

The compounding asset in public-sector business development is **not** a proposal boilerplate library.
It is a **buyer database with renewal dates on it.** Boilerplate makes each bid cheaper. A renewal
calendar tells you which bids to be early for — and being early is the only structural advantage
available to a firm that cannot outspend or out-credential the incumbents.

> **The governing asymmetry:** competitive solicitations hide the incumbent, the budget, and the renewal
> cycle. Sole source notices, award notices, and renewal notices publish all three, in public, for free —
> and almost nobody reads them, because you cannot bid them.

## Pre-Processing (Auto-Context)

- Existing dossiers: !`ls buyers/*.md ../buyers/*.md 2>/dev/null || grep -l "Buyer intelligence" PIPELINE.md ../PIPELINE.md 2>/dev/null || echo "(no dossiers yet)"`
- Pipeline buyer table: !`sed -n '/Buyer intelligence/,/^$/p' PIPELINE.md ../PIPELINE.md ../../PIPELINE.md 2>/dev/null | head -30 || echo "(none)"`
- Declined pursuits to mine: !`ls -d archive/*/ ../archive/*/ 2>/dev/null | head -20 || echo "(no archive)"`
- Target profile: !`sed -n '1,25p' TARGET-PROFILE.md ../TARGET-PROFILE.md 2>/dev/null || echo "(none)"`
- Today: !`date +%Y-%m-%d`

## Step 1: Know what each instrument gives you free

Different procurement documents leak different things. The ones you cannot bid tend to leak the most,
because the buyer has no reason to withhold competitive information when there is no competition.

| Document | Discloses | Why it is rich |
|---|---|---|
| **Sole source notification** | Incumbent **by name**, exact product and version, **exact annual spend**, customization inventory, interfaced third-party systems, renewal anniversary, buyer's name and direct line | The buyer must justify non-competition, so it describes the whole system in public. **The single richest document on any portal** |
| **Award / intent-to-award notice** | Winner, award amount, sometimes the full field and losing prices | Real budget, real field size, real competitive pricing |
| **Bid tabulation** | Every bidder and every price | Tells you who else works this buyer and at what number |
| **Renewal / amendment notice** | Contract still live, new end date, changed value | Free renewal-calendar entry |
| **Prior-year solicitation for the same scope** | The buyer's evaluation pattern and boilerplate | Their rubric habits repeat; so do their required forms |
| **RFI / Sources Sought** | What the buyer is *considering*, 6–18 months early | The shaping window — see `capture-management` |
| **Adopted budget, capital plan, IT roadmap** | Funded line items before any RFP exists | Public, ignored, and the earliest signal available |
| **Audit reports, council/board minutes** | Whether the buyer is *unhappy* with the incumbent | The precondition for displacement |
| **FOIA/FOIL of a winning proposal** | Format, depth, and what actually scored | Legal, underused, extremely instructive |

**Solicitation numbering is data.** A scheme like `WCSS26064` reads as issuer + fiscal year + sequence.
If the sequence is annual, it tells you roughly how many purchase actions that buyer runs a year — which
decides whether they deserve an issuer-level portal alert. Verify the inference against the portal's
solicitation history before relying on it.

## Step 2: Write the dossier

One file per buyer, appended to over years. It should answer, without re-reading anything: *is this buyer
worth working, what do they already own, who has them, and when is the next opening?*

```markdown
# Buyer — <Name>

**Type:** <municipal / county / state agency / school district / authority / special district / nonprofit>
**Scale:** <population, students, employees, budget — whatever sizes their procurements>
**In geography:** <yes/no per target profile>
**First observed:** <date> via <document>

## Procurement mechanics
| Portal | <BidNet / Bonfire / OpenGov / own site> |
| Centralized or departmental | <who actually signs> |
| Procuring authority for technology | <e.g. Dept. of IT buying for operating departments> |
| Named buyers | <name, email, phone — from the notice> |
| Approx. actions per year | <from numbering scheme or portal history> |
| Standard contract form | <link; note if reviewed in public-sector-contracting> |
| Insurance limits typically required | |
| Set-aside / local preference program | |
| Alert configured | <issuer-level? commodity codes? date set> |

## Systems and incumbents
| System | Vendor | Annual spend | Term / anniversary | Customizations | Source |
|---|---|---:|---|---|---|

## Evaluation pattern
<How they weight. Rubrics repeat across a buyer's solicitations far more than across buyers.>

## Satisfaction signals
<Audit findings, council complaints, press, repeated emergency procurements, scope churn.>

## Compliance regime
<What every bid to this buyer will require: FERPA, Ed Law §2-d, ADA Title II, state cyber standards,
retention schedules, prevailing wage, DPA/DSPP forms.>

## Contact restrictions
<No-contact clauses observed, blackout periods, and when they lift.>

## Openings
| What | When | Why we would win | Blocked on |
|---|---|---|---|

## History with us
| Date | Solicitation | Verdict | Record |
```

Keep the dossier where the pipeline can see it. A buyer table in `PIPELINE.md` with a pointer to the full
file is enough until the file grows past a page.

## Step 3: Read the incumbent honestly

An incumbent's name is only useful with an assessment attached. Most incumbency is not displaceable, and
knowing which kind you are looking at prevents a year of wasted courtship.

| Signal | Displaceability |
|---|---|
| Vertical-market software owned by a **consolidator** (Constellation/Harris, Tyler, CentralSquare, Roper) | 🔴 Very low on the product; the model is to hold the maintenance stream. **But see below** |
| System of record with years of accumulated data | 🔴 Very low — migration risk dominates every other consideration |
| Buyer-funded **custom modifications** held in the vendor's source tree | 🔴 Locked, and expensive. **The most reliable dissatisfaction generator** |
| Long-tenured professional services incumbent, no complaints | 🟡 Low; needs a satisfaction crack |
| Incumbent named in an audit finding or council complaint | 🟢 The best opportunity in government contracting |
| Contract expiring with no renewal option remaining | 🟢 Forced recompete |
| Repeated emergency procurements or scope amendments | 🟢 The incumbent is not delivering |
| Incumbent acquired, or product sunset announced | 🟢 Migration is coming whether the buyer likes it or not |

### The customization trap is a lead, not just a fact

When a sole source notice enumerates buyer-funded custom modifications — bespoke reports, third-party
interfaces, forms — read it carefully. The buyer paid to build those and now pays annually to be allowed
to keep using them. That is a recognizable and resented posture, and it is **not** displaceable by
proposing to replace the system.

It is, however, a candidate for a **bounded assessment engagement**: what the customization portfolio
actually costs, what it would take to insource or re-platform the interfaces, what exit would really
require. Small, low-risk, high-margin, needs no product — and it positions you for whatever follows. Note
it in the dossier as speculative until there is evidence the buyer is contemplating it.

## Step 4: Build the renewal calendar

This is the artifact that makes the rest of it compound. A one-line entry per known contract, sorted by
anniversary.

```markdown
| Anniversary | Buyer | System / scope | Incumbent | Annual value | Instrument seen | Capture window opens | Source |
|---|---|---|---:|---|---|---|---|
```

**Work backward from the anniversary**, not forward from the RFP:

| Months before anniversary | What is happening | What to do |
|---|---|---|
| 18–12 | Budget planning; the buyer decides whether to recompete | Capabilities briefing. This is the real window |
| 12–6 | Market research; RFI may publish | **Respond to every RFI.** Your language can enter the requirements |
| 6–3 | Requirements written; sole source notice may publish | If it is sole source, you are already too late for this cycle |
| 3–0 | Solicitation publishes, or renewal quietly executes | Bid, or log the next anniversary |

A recurring sole source notice is the cheapest calendar entry available: it publishes annually, names the
anniversary explicitly, and tells you exactly when next year's copy will appear. **Log the date the same
day you decline it.**

## Step 5: Source ahead of the portal

Everything on a bid portal arrives after the requirements were written. These do not.

| Source | Cadence | What it tells you |
|---|---|---|
| **Council / board / legislature agendas and minutes** | Weekly | Budget approvals and contract awards appear here months before any RFP. **Highest-leverage source available** |
| **Adopted operating and capital budgets** | Annual | Funded line items, by department, with dollar amounts |
| **Grant award announcements to the agency** | Monthly | Funded programs must be spent, and spending requires procurement |
| **Agency IT strategic plans and roadmaps** | Annual | Published, ignored, and explicitly forward-looking |
| **Audit reports (state comptroller, internal audit, IG)** | As issued | Names failing systems and vendors, on the record |
| **Portal award-notice feeds** | Weekly | Free incumbent and budget data across every buyer at once |
| **Regulatory compliance deadlines** | Known in advance | A jurisdiction-wide forcing function — see below |

### Compliance deadlines create buyers on a schedule

A regulatory deadline that applies to a whole class of entities creates a predictable, dated wave of
demand across every buyer in that class simultaneously. Accessibility mandates, records-retention rules,
data-privacy statutes, and cybersecurity standards all behave this way. Track the deadline, enumerate the
entities it binds in your geography, and note that **an entity past a compliance date is a live buyer who
does not need to publish an RFP to engage you** — a direct capabilities briefing is often the whole sale.

Confirm the applicable date and the entity's current posture before any outreach; a compliance approach
built on a wrong date is worse than no approach.

## Step 6: Time the approach

Intelligence is worth nothing if acting on it damages the relationship.

| Rule | Detail |
|---|---|
| **Honor no-contact clauses literally** | Most solicitations bar contacting the using department; some bar everything but the named buyer. This binds until award posts |
| **Treat the restriction as broader than its text** | If a notice bars contact about a corrections system, do not approach that department about anything until the award is issued. The appearance is the problem |
| **Time unrelated approaches after award** | An unrelated capabilities briefing request is legitimate — send it after the notice's procurement closes, not during |
| **Ask for a capabilities briefing directly** | Most agencies will take one. It requires no RFP, no window, and no competition |
| **Respond to every RFI in your market** | The single highest-leverage legal activity in the cycle |
| **Request a debrief on every loss** | Most public agencies must provide one. For a firm's first bids, it is worth more than the contract |

Everything here is ordinary, legal market engagement — what every established government contractor
does, and what new entrants skip.

## Step 7: Feed it back

Buyer intelligence that never changes a decision is a scrapbook. Three loops close it:

1. **Into the target profile.** If every decline in a market fails for the same reason, either fix that
   gap permanently or stop sourcing that market. Recurring declines are a standing tax.
2. **Into alert configuration.** A buyer that surfaces twice deserves an **issuer-level** alert, not
   commodity codes. Commodity codes describe commodities.
3. **Into the pursuit calendar.** Renewal anniversaries become dated pipeline actions with owners — not
   notes. An anniversary with no owner and no date is not intelligence, it is trivia.

Review the dossiers quarterly alongside the pipeline. Prune buyers with no openings after two review
cycles; the file is for buyers you are working, not every buyer you have ever read.

## Anti-patterns

| Anti-pattern | Why it fails |
|---|---|
| Discarding declined solicitations | Throws away intelligence already paid for in reading time |
| Skipping sole source and award notices because they cannot be bid | Skips the richest documents on the portal |
| Recording the incumbent without a displaceability read | A name with no assessment produces years of futile courtship |
| No renewal calendar | Guarantees arriving after the requirements are written, forever |
| Building the calendar forward from RFP dates | The capture window opens 12–18 months before the anniversary |
| Approaching the using department during a live procurement | Violates the no-contact clause and burns the buyer |
| Acting on a compliance deadline without verifying it | An approach built on a wrong date is worse than none |
| Dossiers nobody reads | Keep it in the pipeline's line of sight or it decays |
| Treating a customization inventory as a replacement pitch | Migration risk beats every argument. Sell the assessment, not the replacement |
| Intelligence with no dated action and no owner | Trivia |

## Handoff

- Screening a specific solicitation → `solicitation-triage`
- Building the pipeline and the target profile → `capture-management`
- A qualified solicitation from a dossiered buyer → `rfp-evaluation`, then `bid-decision`
- The buyer's standard contract form → `public-sector-contracting`
- Sizing the market a dossier reveals → `market-research`
- Turning an opening into an engagement → `proposal-generator`
