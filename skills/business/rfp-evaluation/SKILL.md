---
name: rfp-evaluation
description: "Evaluate an RFP/RFQ/ITB — extract every requirement, build the compliance matrix, map the scoring rubric to effort, track addenda"
when_to_use: "Use when a solicitation lands and you need to know what it requires and where the points are. NOT for the go/no-go call (use bid-decision). NOT for writing the response (use proposal-generator)."
argument-hint: "[solicitation-number]"
allowed-tools: ["Read", "Grep", "Glob", "Bash", "Write", "Edit", "WebSearch"]
---

# RFP Evaluation

Turn a solicitation document into a structured, actionable model of what the buyer is asking for.

The governing insight: **public-sector proposals are scored against a rubric by a committee, and screened for responsiveness before anyone reads the content.** A brilliant proposal that omits a required form scores zero. Evaluation work is therefore mechanical first and strategic second — extract the compliance surface completely, then decide where to spend effort based on where the points actually are.

## Pre-Processing (Auto-Context)

Solicitation context, gathered before the skill runs. Values are injected inline below; in an environment that does not execute them, run the shown commands instead.

- Bid folder: !`ls -d */ 2>/dev/null | head -10`
- Source documents: !`ls *.pdf 00-source/*.pdf 2>/dev/null | head -20`
- Extracted text present: !`ls 00-source/extracted/*.txt 2>/dev/null | head -20 || echo "(none — run extraction first)"`
- Existing analysis: !`ls 01-analysis/*.md 2>/dev/null || echo "(none)"`

## Step 0: Extract text before reading anything

Never evaluate from a PDF viewer. Extract to plaintext so requirements can be grepped, counted, and diffed against addenda.

```bash
mkdir -p 00-source/extracted
for f in 00-source/*.pdf; do
  pdftotext -layout "$f" "00-source/extracted/$(basename "$f" .pdf).txt"
done
```

`-layout` is mandatory — it preserves table columns, and requirement matrices and cost forms are always tables. Without it, requirement IDs separate from their text and the extraction is useless.

If `pdftotext` is unavailable: `python3 -c "import pypdf"` then extract per page. If the PDF is a scan with no text layer, say so explicitly and stop — OCR output is not reliable enough to build a compliance matrix from.

## Step 1: Classify the solicitation

| Type | Award basis | What matters most |
|------|-------------|-------------------|
| RFP (Request for Proposal) | Best value, scored rubric | Technical quality; price is one criterion among many |
| RFQ (Request for Quote) | Usually lowest price | Compliance + price. Narrative rarely moves the needle |
| ITB / IFB (Invitation to Bid) | Lowest responsive bid | Pure compliance. Sealed bid law usually applies |
| RFI (Request for Information) | No award | Positioning for the RFP that follows. Cheap and high-leverage |
| RFQu (Request for Qualifications) | Shortlist, price later | Past performance and team; price often prohibited |
| IDIQ / on-call / master agreement | Pool pre-qualification | Getting on the list, then competing per task order |

**Read the award clause carefully.** A document titled "RFP" that awards on lowest price is an ITB wearing a costume, and effort spent on narrative is wasted. Conversely, language about being "eligible to submit proposals for specific projects as needs arise" signals a pre-qualification pool, not a funded build — which changes the entire economics.

## Step 2: Build the facts table

Extract these before anything else. Every one is a hard constraint, and getting one wrong can void the bid.

| Fact | Where it usually hides |
|------|------------------------|
| Submission deadline — date, **time**, and timezone | Cover page; superseded by addenda |
| Submission channel (portal / email / physical) | Cover page, "Information for Proposers" |
| File count, naming convention, size limits | Submission requirements section |
| Question/RFI deadline | Cover page — **check whether it has passed** |
| Pre-proposal conference (mandatory?) | Often mandatory; missing it disqualifies |
| Contract term + option years | Contract award section |
| Rate escalation permitted? | Cost proposal section |
| Proposal validity period | "Irrevocable for N days" |
| Award basis + scoring rubric | Evaluation section |
| Multiple awards permitted? | Contract award section |
| Budget disclosed? | Often nowhere — note the absence explicitly |
| Incumbent (if any) | Search prior awards on the portal |
| Mandatory forms/certifications | Attached schedules, often a separate file |
| Insurance requirements | Insurance schedule; check limits AND endorsements |
| Set-asides (MBE/WBE/SDVOB/small business) | Compliance section — goal vs. requirement matters |

**Timezone and "prevailing time."** Many municipal solicitations say "prevailing time," meaning local time at the issuer. Convert and record it unambiguously.

## Step 3: Extract every numbered requirement

Requirements usually come as ID-prefixed tables (`F-1`, `T-3`, `S-7`, `AI-2`, `A-5`). Extract them **verbatim** — paraphrasing loses the operative verb, and "shall support" versus "shall describe an approach to" are very different obligations.

Build `01-analysis/requirements-matrix.md`:

```markdown
| ID | Requirement (verbatim) | Cx | Response | Narrative § |
|---|---|:--:|---|---|
| F-1 | <exact text> | 🟡 | | |
```

- **Cx** = our build complexity (🟢 routine · 🟡 substantial · 🔴 high-risk/specialist). This is our estimate, not the buyer's.
- **Response** = `Meets` / `Meets w/ config` / `Partial` / `Roadmap` / `Exception`, filled during drafting.
- **Narrative §** = where in the proposal we answer it.

Then **count them and state the count**. "63 requirements across five families" is a scoping fact that drives everything downstream.

### Catch the unnumbered requirements

The numbered tables are the easy part. Solicitations also bury mandatory content in prose:

- "Vendor must describe…" tables with no IDs
- Service-level tables where the vendor must **state a number** (uptime, RTO, RPO, patch timelines)
- Deliverables lists
- Phase/implementation models
- Submission-section content requirements that duplicate and *extend* the numbered list

Grep for the operative verbs across the extracted text:

```bash
grep -niE "shall |must |is required to |vendor will |proposer shall |describe (your|the|how)|provide (a|an|evidence)|identify (all|each)|state (the|your)" \
  00-source/extracted/*.txt | wc -l
```

If that count materially exceeds your numbered-requirement count, you are missing obligations.

## Step 4: Reconcile duplicate and conflicting requirement lists

Solicitations are assembled from templates and routinely contradict themselves. This is normal, not a defect to report — it is a trap to navigate.

**Method:** build the compliance checklist from the *union* of every section that lists required content, not from the most complete-looking one.

Common conflicts and the correct response:

| Conflict | Response |
|---|---|
| Two sections require different verbatim cover-letter language | **Include both sentences.** Satisfy whichever the evaluator checks |
| Two sections list overlapping but non-identical required content | Union of both. Cheap to over-satisfy, fatal to under-satisfy |
| Scoring table points don't sum to 100, or a row is missing its value | Flag it, allocate effort to the rows with confirmed points, watch for a correcting addendum |
| Deadline in the base document vs. an addendum | **Addenda always win.** Every addendum supersedes |
| Page limit stated in two places | Honor the stricter one |

Record every conflict you find in the checklist with both citations. If an RFI window is still open, these are your highest-value questions — a buyer who fixes a contradiction for you now cannot use it against you later.

## Step 5: Map the rubric to effort allocation

This is where evaluation becomes strategy. Extract the scoring table and convert points into a page/effort budget.

```markdown
| Criterion | Points | Proposal § | Effort share |
|---|---:|---|---:|
```

**Allocate effort proportional to points, not to how interesting the section is.** Engineers over-invest in architecture and under-invest in governance sections because architecture is more fun to write. The rubric does not care.

Look specifically for rubrics that **reward a specialist over a large firm**. When security, governance, accessibility, or methodology outweigh company size and past performance, a focused firm can win on writing quality alone. When qualifications and price dominate, incumbency and scale win and a small firm is buying a lottery ticket.

Compute and state the ratio explicitly:

> "Security + AI governance + accessibility = 45 of 100 points, more than functional fit and architecture combined, and nine times what vendor qualifications are worth."

That single sentence should drive the entire drafting plan.

## Step 6: Build the compliance checklist

Produce `01-analysis/compliance-checklist.md` covering, at minimum:

1. **Submission mechanics** — channel, deadline, file naming, size, format restrictions
2. **File-by-file contents** — exactly which document goes in which upload
3. **Signatures** — every block, who may sign, whether printed name and title are required
4. **Notarization** — which forms need a notary (book the appointment early)
5. **Addenda acknowledgements** — one row per addendum, including ones not yet issued
6. **Verbatim language** — quoted exactly, with a checkbox that it appears character-for-character
7. **Mandatory content** — every required section, cross-referenced to the source paragraph
8. **Mandatory forms** — table of schedules with signature/notary/status columns
9. **Confidentiality marking** — trade-secret/FOIA-exemption procedure, if the buyer offers one
10. **Eligibility bars** — arrears, debarment, prior performance, registration status
11. **Day-of pre-flight** — the final sequence, executed by someone who did not write the proposal

Every row cites its source paragraph. A checklist without citations cannot be audited and will not be trusted at 11 PM the night before submission.

## Step 7: Set up addendum tracking

Addenda change requirements, deadlines, and scope, and **failing to acknowledge one commonly renders a bid non-responsive**. This is the single most common unforced error in public-sector bidding.

- Record every addendum in the bid README with its date and what it changed
- Add an acknowledgement row to the compliance checklist for each
- **Add a row for addenda not yet issued** if the buyer has signaled more are coming
- Re-check the portal at T-24h and again on submission morning
- When one lands, diff it against the base: `diff <(cat old.txt) <(cat new.txt)`

If a pending addendum will answer questions material to pricing or scope, **do not finalize pricing before it lands**. Note this as a standing risk.

## Step 8: Flag what you could not resolve

End the evaluation with an explicit uncertainty list. For each item: what is ambiguous, why it matters, and whether it is still askable.

| Ambiguity | Impact | Askable? |
|---|---|---|
| Is this one funded build or a pre-qualification pool? | Determines whether the pursuit economics work at all | RFI window closed — watch for an addendum |

**"The RFI window has closed" is a material finding, not a footnote.** It means you are bidding blind on every ambiguity and cannot shape any requirement. Say so prominently.

## Artifact Generation (Required)

Generate using Write, in the bid folder:

1. `01-analysis/requirements-matrix.md` — every requirement, verbatim, with complexity and response columns
2. `01-analysis/compliance-checklist.md` — the responsiveness gate, fully cited
3. `README.md` — at-a-glance facts table, critical dates, standing alerts, reading order
4. `02-proposal/outline.md` — section map with rubric-weighted effort allocation

## Anti-patterns

| Anti-pattern | Why it fails |
|---|---|
| Reading the PDF instead of extracting text | Cannot grep, count, or diff against addenda |
| Paraphrasing requirements | Loses the operative verb; "describe" ≠ "provide" ≠ "support" |
| Building the checklist from one section | Solicitations duplicate and extend requirements across sections |
| Treating a self-contradiction as a blocker | Satisfy both readings and move on |
| Allocating effort by interest rather than points | The rubric is the only scoring function that exists |
| Ignoring a missing budget | An undisclosed budget against a huge scope is the central risk, not a detail |
| Starting to write before the checklist exists | You will discover a mandatory form in the final week |

## Handoff

- Go/no-go decision → `bid-decision`
- Contract terms and insurance → `public-sector-contracting`
- Effort and cost → `technical-estimation`, then `engineering-cost-model`
- Response drafting → `proposal-generator`
