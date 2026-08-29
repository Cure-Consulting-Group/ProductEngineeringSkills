# Capture Management

Find and position for the right opportunities, rather than reacting to whichever solicitation happens to land.

The central fact of government business development: **most public solicitations are effectively decided before they are published.** Not corruptly — through ordinary market research, vendor demos, RFI responses, and incumbent relationships that shape what the agency writes down. A firm that first encounters an opportunity on the bid portal is competing at a structural disadvantage against firms that helped shape it.

Capture is the work of being early. Bidding is what happens after capture succeeds or fails.

## Pre-Processing (Auto-Context)

- Current pipeline: !`sed -n '1,40p' PIPELINE.md ../PIPELINE.md 2>/dev/null || echo "(no PIPELINE.md)"`
- Past pursuits: !`ls -d archive/*/ ../archive/*/ 2>/dev/null | head -20 || echo "(no archive)"`
- Portfolio: !`sed -n '1,30p' PORTFOLIO.md 2>/dev/null || echo "(none)"`

## Step 1: Define the target profile before searching

Searching without a profile produces a pipeline of things you cannot win. Write the profile first, from evidence about what you can actually deliver and prove.

```markdown
## Target opportunity profile

**Contract value:** $__ – $__          (below: not worth bid cost. above: capacity/bonding fails)
**Duration:** __ – __ months
**Buyer type:** <municipal / county / state / school district / authority / federal>
**Geography:** <where we're licensed, insured, and can staff>
**Scope:** <what we have shipped and can evidence>
**Team size implied:** ≤ __ FTE peak
**Disqualifiers:** <bonding thresholds, clearances, certifications we lack>
**Sweet spot:** <the specific thing we win on>
```

### Sizing the target realistically

The most common error entering public-sector work is chasing contracts far too large. Signs a solicitation is out of range:

- Implied peak team exceeds your headcount
- Required past performance exceeds your largest completed contract by more than ~3×
- Insurance or bonding requirements exceed what you carry
- The scope spans domains where you have no evidence

**Enter a market at the bottom and build up.** A \$150K contract you deliver well produces a reference that qualifies you for the \$500K one. There is no substitute for that first reference, and no shortcut past it.

## Step 2: Source opportunities systematically

| Source | Coverage | Notes |
|---|---|---|
| SAM.gov | US federal | Free. Registration required to bid |
| State procurement portals | State agencies | One per state; most are free to register |
| Regional bid systems (BidNet/Empire State, Bonfire, OpenGov, Periscope, DemandStar) | Local government | Some charge for full access |
| Individual agency sites | Small local | Often the least-competitive work; frequently not aggregated |
| GSA Schedules / state master contracts | Pre-qualified pools | Long lead time, high leverage once on |
| Cooperative purchasing (NASPO, Sourcewell, OMNIA) | Multi-agency | One award, many buyers |
| Board and council agendas | **Pre-solicitation** | Where budget approvals appear before RFPs — the highest-leverage source |
| Grant awards to agencies | **Pre-solicitation** | Funded programs must be spent; RFPs follow |

**The last two matter most.** A council agenda approving a program budget, or a state/federal grant award to an agency, tells you an RFP is coming months before it publishes. That window is when capture is possible.

Set portal alerts by commodity/NAICS code and review weekly. Record everything qualifying in the pipeline, including opportunities you decline — the pattern of what you decline tells you whether the target profile is right.

## Step 3: Work the pre-RFP window

Everything here is ordinary, legal market engagement. It is what every established government contractor does, and skipping it is why new entrants lose.

| Activity | Timing | Value |
|---|---|---|
| **Respond to every relevant RFI/Sources Sought** | 6–18 mo before | Highest leverage available. Your language can enter the requirements |
| Request a capabilities briefing | Anytime | Most agencies will take one |
| Attend industry days and pre-proposal conferences | As scheduled | Sometimes mandatory; always reveals the field |
| Read the agency's strategic plan, IT roadmap, budget | Anytime | Public. Tells you what is coming |
| **Submit written questions during the RFI window** | Before the RFP | Ambiguities you fix now cannot hurt you later |
| Review prior awards to the same agency | Anytime | Reveals incumbents, real budgets, and evaluation patterns |
| FOIA/FOIL a winning proposal from a past award | Anytime | Legal, underused, and extremely instructive on format and depth |

**Prior-award research is the cheapest intelligence available.** Most portals publish award notices with vendor and dollar amount. That tells you the agency's actual spending range — which matters enormously when the current solicitation discloses no budget.

### The RFI signal

If an RFI window has already closed when you find the solicitation, you have missed the only opportunity to shape or clarify it. Treat that as a negative capture signal, not a neutral fact: someone else answered it, and the requirements may reflect their language.

## Step 4: Solve the past-performance problem

New entrants face a circular barrier: you need public-sector references to win public-sector work. The ways through, roughly in order of speed:

| Path | Timeline | Notes |
|---|---|---|
| **Subcontract to a prime** | Immediate | Fastest route to citable past performance. Actively pursue primes bidding work you can support |
| **Small/simple contracts first** | 3–9 mo | Micro-purchases, small local agencies, single-department work |
| **Set-aside certifications** | 3–12 mo | MBE/WBE/SDVOB/8(a)/HUBZone where eligible — materially narrows the field |
| **Teaming or joint venture** | Per pursuit | Combine your technical depth with a partner's qualifications. Must be arranged before submission |
| **Adjacent-sector references** | Immediate | Nonprofit, healthcare, education work sometimes accepted where "public sector" is defined loosely |
| **Cooperative/master contract vehicles** | 6–18 mo | High effort, high leverage — you compete in a smaller pool afterward |

**Check certification eligibility early.** Set-asides are the single largest structural advantage available to a qualifying small firm, and certification takes months. If eligible and uncertified, that is usually the highest-ROI business development action available.

## Step 5: Assess the competitive field

Before committing, know who else is bidding.

| Question | How to answer |
|---|---|
| Who holds the incumbent contract? | Prior award notices; agency budget documents |
| Who bid last time? | Bid tabulations are usually public |
| What did the last award go for? | Award notices |
| Does the scope match a specific product? | Read requirements for feature-list fingerprints |
| Is the agency happy with the incumbent? | Council minutes, audit reports, press |

**A displeased agency with an expiring incumbent contract is the best opportunity in government contracting.** They are motivated to change, and the incumbent's advantage inverts.

## Step 6: Maintain the pipeline

```markdown
| Opportunity | Agency | Est. value | RFP expected | Stage | Capture actions taken | Fit |
|---|---|---:|---|---|---|---|
```

Stages: `Identified` → `Qualified` → `Capture` (pre-RFP engagement underway) → `Bid` → `Submitted` → `Won/Lost`

**Health checks:**

- Are opportunities entering at `Identified`/`Capture`, or first appearing at `Bid`? If everything enters at `Bid`, you are reacting, not capturing
- Is pipeline value ≥ 3–5× your revenue target, given realistic win rates?
- Are you declining enough? A qualified pipeline with no declines means the profile is too loose

## Step 7: Build the reusable asset library

Most of a public-sector proposal is reusable. Building it once converts every future bid from weeks to days.

| Asset | Reuse |
|---|---|
| Company profile, ownership, financial stability | Every bid |
| Corporate disclosure questionnaire answers | Every bid |
| Past performance write-ups (one per project) | Every bid |
| Named staff resumes in proposal format | Every bid |
| Security architecture and controls narrative | Most technical bids |
| Accessibility approach and testing methodology | Most public bids |
| AI governance framework | Increasingly, most bids |
| QA, SDLC, and project methodology | Every bid |
| Insurance certificates and W-9 | Every bid |
| Standard exceptions language | Every bid |

**Version and date every asset.** Stale past performance and expired certificates are a common self-inflicted compliance failure.

## Anti-patterns

| Anti-pattern | Why it fails |
|---|---|
| Finding opportunities only on bid portals | You arrive after requirements are set |
| Skipping RFI responses | Forfeits the only chance to shape requirements |
| Chasing contracts far above your size | Capacity, bonding, or past performance disqualifies you |
| No target profile | Produces a pipeline of unwinnable pursuits |
| Ignoring set-aside eligibility | Forfeits the largest structural advantage available |
| Never subcontracting | Slowest possible path to first past performance |
| Not researching prior awards | Bidding blind on budget and field |
| Rebuilding boilerplate every bid | Weeks of avoidable work per pursuit |
| Pipeline with no declines | The profile is too loose to be useful |

## Handoff

- A specific solicitation lands → `rfp-evaluation`
- Pursue or not → `bid-decision`
- Contract terms in the target market → `public-sector-contracting`
- Market sizing and ICP → `market-research`
- Positioning and messaging → `go-to-market`
