# Skill review: business (14), finance (4), marketing (6), tax (12). Wave 5 rubric, 2026-09-23

Reviewer scope: I read every SKILL.md in full and skimmed the sibling reference files (all tax `reference/`, finops and investor-reporting `reference/details.md`, `tax/README.md`, bin wrappers). This was a read-only review. Line numbers refer to `skills/<domain>/<skill>/SKILL.md` unless another path is given.

Legend: S1 signal density · S2 instruction style · S3 trigger · S4 currency/correctness · S5 portability · S6 progressive disclosure.

## Scorecard

| Skill | S1 | S2 | S3 | S4 | S5 | S6 | /30 | Verdict |
|---|---|---|---|---|---|---|---|---|
| **business/** | | | | | | | | |
| bid-decision | 4 | 4 | 3 | 3 | 3 | 4 | 21 | TIGHTEN: fix EV example, trim trigger |
| buyer-intelligence | 5 | 4 | 3 | 4 | 3 | 4 | 23 | TIGHTEN: trigger 385 chars |
| capture-management | 4 | 4 | 3 | 4 | 3 | 4 | 22 | TIGHTEN: de-dup sourcing with buyer-intelligence |
| public-sector-contracting | 4 | 4 | 4 | 4 | 3 | 4 | 23 | KEEP |
| rfp-evaluation | 4 | 4 | 3 | 4 | 3 | 4 | 22 | TIGHTEN: folder convention clash with triage |
| solicitation-triage | 5 | 4 | 3 | 4 | 3 | 4 | 23 | TIGHTEN: trigger 384 chars |
| technical-estimation | 4 | 4 | 4 | 3 | 3 | 4 | 22 | TIGHTEN: PERT arithmetic, double-counted risk |
| burn-rate-tracker | 2 | 2 | 4 | 2 | 2 | 2 | 14 | REWRITE |
| engineering-cost-model | 3 | 3 | 2 | 2 | 2 | 3 | 15 | TIGHTEN: remove PERT dup, refresh prices |
| saas-financial-model | 2 | 3 | 3 | 2 | 2 | 3 | 15 | REWRITE: textbook, LTV formula error |
| finops | 3 | 2 | 4 | 2 | 2 | 3 | 16 | TIGHTEN: stale model price table |
| fundraising-materials | 2 | 2 | 3 | 2 | 2 | 2 | 13 | REWRITE: SAFE math error, duplicates investor-reporting |
| investor-reporting | 3 | 3 | 3 | 3 | 2 | 3 | 17 | TIGHTEN: own data-room/cap-table, drop registry |
| proposal-generator | 3 | 2 | 4 | 3 | 2 | 3 | 17 | TIGHTEN |
| **finance/** | | | | | | | | |
| comps-analysis | 1 | 3 | 3 | 3 | 5 | 4 | 19 | MERGE-INTO: investment-banker agent (or rewrite with Cure data-source rules) |
| dcf-modeling | 1 | 3 | 4 | 2 | 5 | 4 | 19 | REWRITE: equity-bridge error |
| equity-research | 1 | 3 | 3 | 3 | 5 | 4 | 19 | MERGE-INTO: equity-analyst agent |
| merger-modeling | 1 | 3 | 4 | 4 | 5 | 4 | 21 | MERGE-INTO: investment-banker agent |
| **marketing/** | | | | | | | | |
| go-to-market | 2 | 3 | 4 | 3 | 2 | 4 | 18 | TIGHTEN |
| growth-engineering | 2 | 3 | 4 | 3 | 2 | 3 | 17 | TIGHTEN: cut AARRR textbook |
| instagram-publishing-setup | 5 | 4 | 5 | 3 | 4 | 4 | 25 | KEEP: check Graph API version |
| product-marketing | 3 | 2 | 4 | 2 | 2 | 2 | 15 | TIGHTEN: move registry out, refresh platform specs |
| seo-content-engine | 2 | 3 | 3 | 2 | 2 | 3 | 15 | TIGHTEN: FID and Mobile-Friendly Test are dead |
| technical-blog-writer | 3 | 4 | 3 | 4 | 5 | 4 | 23 | KEEP |
| **tax/** | | | | | | | | |
| audit-risk-substantiation | 5 | 4 | 4 | 3 | 4 | 5 | 25 | TIGHTEN: ES-disclosure contradiction |
| cpa-benchmark | 5 | 5 | 4 | 3 | 3 | 5 | 25 | TIGHTEN: TCP QBI item, Node dependency |
| cpa-standards | 4 | 4 | 4 | 2 | 5 | 4 | 23 | TIGHTEN: pre-2024 SSTS structure |
| deductions-and-credits | 4 | 4 | 4 | 2 | 5 | 5 | 24 | TIGHTEN: §25D/§21/§51 stale for 2026 |
| estimated-tax-compliance | 4 | 4 | 4 | 4 | 5 | 4 | 25 | KEEP |
| irc-lookup | 5 | 4 | 4 | 3 | 3 | 5 | 24 | TIGHTEN: QBI 2026 figure |
| nonprofit-dissolution | 5 | 4 | 5 | 4 | 5 | 4 | 27 | KEEP |
| return-review | 4 | 4 | 4 | 3 | 5 | 5 | 25 | KEEP (one stale opportunity line) |
| software-dev-tax | 5 | 4 | 4 | 3 | 4 | 5 | 25 | TIGHTEN: §174A retro window |
| tax-preparation | 4 | 4 | 4 | 4 | 5 | 5 | 26 | KEEP |
| tax-recommendations | 4 | 4 | 4 | 2 | 5 | 5 | 24 | TIGHTEN: worked example is wrong |
| tax-strategies | 4 | 4 | 4 | 3 | 5 | 5 | 25 | TIGHTEN: WOTC / 401(k) deadlines |

**Distribution (n=36):** 13–15: 6 · 16–18: 5 · 19–21: 5 · 22–24: 11 · 25–27: 9. Median about 22. By domain: tax averages 24.8, the public-sector cluster in business averages 22.3, the rest of business averages 15.3, finance 19.5, marketing 18.8.

**Verdicts:** KEEP 7 · TIGHTEN 22 · REWRITE 4 · MERGE-INTO 3 · DEPRECATE 0.

---

## Per-skill findings (every skill with any score ≤3)

### bid-decision (S3 3, S4 3, S5 3)
- **Arithmetic error at `:107`.** It reads "A 15% chance at \$400K of margin against a \$60K bid cost is EV-positive (\$0K... marginally)." 0.15 × 400K − 60K = 0, so the EV is zero, not positive, and the parenthetical is garbled. Fix: use 0.20 × 400K − 60K = +20K, or say "break-even".
- **Mislabelled injection at `:19`.** "Days remaining: !`date`" prints today's date, not the days remaining. `:18` assumes `../../PIPELINE.md`, while sibling skills probe `PIPELINE.md ../PIPELINE.md` (solicitation-triage `:34`), so the path convention is inconsistent across the cluster.
- **Trigger is 367 chars.** Three of the four NOT-clauses (`:4`) restate the handoff table. Keep one NOT (solicitation-triage) and put the rest in the Handoff section.
- The "read the operative verb" guidance (`:39`) and "request a debrief on every loss" (`:160`) are duplicated verbatim in solicitation-triage `:101` and buyer-intelligence `:195`. Pick one owner and cross-reference from the others.

### buyer-intelligence (S3 3, S5 3)
- The trigger is 385 chars (`:3-4`). Drop the "NOT for sourcing" clause, because capture-management already disclaims the reverse.
- Pre-processing (`:28-32`) is five `!` probes. On Antigravity they render as literal text, and unlike rfp-evaluation `:17` there is no "run these yourself" fallback sentence. Add the standard fallback line.
- The source table `:163-171` duplicates capture-management `:53-64` (agendas, budgets, grants, portal feeds). Keep it in one place.

### capture-management (S3 3, S5 3)
- The trigger is 373 chars and lists three NOT-clauses (`:4`). Trim it.
- Pre-processing `:19-21` has no fallback line (see above).
- `:59` "GSA Schedules" is fine. `:96` lists "8(a)/HUBZone" without noting that federal set-aside certification is SBA-run and has changed, so add a "verify current program status" note or drop the federal detail. This is minor.

### public-sector-contracting (S5 3)
- `:4` routes to the "contract-reviewer agent", which exists only in Claude Code. Rephrase neutrally: "commercial MSA review (the contract-reviewer agent under Claude Code)".
- Pre-processing `:19-21` has no fallback line.

### rfp-evaluation (S3 3, S5 3)
- **Folder convention conflicts with the upstream skill.** solicitation-triage extracts into `src/*.txt` (triage `:41-42`), but this skill expects `00-source/*.pdf` and `00-source/extracted/` (`:20-31`). A PROMOTEd pursuit therefore finds no extracted text. Pick one layout.
- `:37` falls back to `python3 -c "import pypdf"`, which is a pip dependency. That contradicts the repo's stdlib-only norm. Say "if pypdf is installed" or give an OS-native fallback.
- The trigger is 391 chars (`:4`).
- `:176` `diff <(cat old.txt) <(cat new.txt)` is a needless process substitution. Use `diff old.txt new.txt`.

### solicitation-triage (S3 3, S5 3)
- The trigger is 384 chars.
- `:35-36` probe globs such as `src/*.pdf`, which conflict with rfp-evaluation's `00-source/` (see above).
- Gate criterion 8, "RFI window still open" (`:140`), combined with the "below 8 of 10 → decline" threshold (`:144`), means a closed RFI window plus two other misses auto-declines. That is harsh for RFQuals and pool vehicles. State whether criterion 8 applies to every instrument.

### technical-estimation (S4 3, S5 3)
- **Wrong PERT value at `:41`.** The example row is O=320, M=560, P=1200. (320 + 2240 + 1200)/6 = 626.7, but the row says 613. This skill exists to be auditable, so its own example must add up.
- **Double counting at `:171-180`.** The skill applies a reference-class multiplier (×1.4) and then adds a risk reserve on top. The historical actual/estimate ratio already contains realized risk, so stacking both counts it twice. Either apply the named-risk reserve to the bottom-up number only, or say explicitly why the two do not overlap.
- `:171` labels the estimate "Budgetary (−10%/+25%)", but the 80% range at `:180` is −15%/+17%. Reconcile the two.
- `:19` injects `package.json`. That only matters if an existing repo is in scope, so gate the injection on that.

### burn-rate-tracker (14/30, REWRITE)
- **The guardrail claim is false and contradicted.** `:11-16` claims read-only is "enforced by the `allowed-tools` / `disallowed-tools` frontmatter". The frontmatter has only `allowed-tools` (`:6`), which per CLAUDE.md restricts nothing, and there is no `disallowed-tools`. `:380-385` then mandates "Generate using Write" into three files, and `:393` runs a Python script, which needs Bash, a tool that is not in `allowed-tools`. Decide whether the skill writes. If it is read-only, set `disallowed-tools: Write Edit` and make the artifacts inline. If it is not, delete the banner.
- **The script path is wrong.** `:393` says `skills/burn-rate-tracker/scripts/...`, but the file is under `skills/business/...`. A PATH wrapper `bin/cure-runway` already exists and is never mentioned, so point to that.
- **Stale and inconsistent content.** `:244` "Haiku/4o-mini … instead of Opus/GPT-4" uses 2024 model names. The runway rules contradict each other: `:181` says start fundraising below 6 months, `:322` says actively fundraise at 6–9 months, and `:345` says start at 9 months. saas-financial-model `:193` says 6+ and investor-reporting `:231` says below 6. `:171` says 12-month, but the artifact at `:384` says 18-month.
- **Low signal.** Gross burn, net burn and runway (`:98-113`) are textbook. The tier-savings tables (`:234-276`) are invented dollar ranges with no source. The hard-coded portfolio (`:29`, `:44`, `:296-300`) belongs in PORTFOLIO.md, which the skill already injects at `:22`.
- `:23-25` injects package.json, git log and src layout into a finance skill. That is irrelevant context on every call. Keep only the PORTFOLIO probe.

### engineering-cost-model (15/30)
- **The trigger is 497 chars** (`:3-4`), right at the audit's 500 flag. It has four NOT-clauses. The classification row "Client proposal | SOW-ready cost breakdown" (`:40`) contradicts "NOT for client-facing SOWs" (`:4`).
- **Stale facts.** `:240-243` hard-codes "2025" into the search queries. `:156` says "SendGrid … 100 emails/day free", but SendGrid retired its free plan in 2025 (verify). `:140` says "Auth: 10K verifications/month (phone)", which contradicts finops `reference/details.md:88` ("\$0.01-0.06 per SMS"). `:157` "OpenAI API: \$0.50-15 per 1M tokens" is an undated band.
- **Duplicated estimation method.** The three-point estimate `:54-69` duplicates technical-estimation's PERT without the σ roll-up. Keep the hour tables, which are the Cure-specific value, and point to technical-estimation for the method.
- The payment structure at `:310-313` (30/30/30/10) contradicts proposal-generator `:153` ("Final 20% due on go-live"). Pick one Cure default.
- The script path `:253` is wrong (it is missing `business/`), and `bin/cure-cost-estimator` exists but is not mentioned. The false read-only banner problem is the same as in burn-rate-tracker (`:11-16`).

### saas-financial-model (15/30, REWRITE)
- **Correctness.** `:69` gives LTV = ARPU / churn and `:78` gives payback = CAC / ARPU. Both ignore gross margin, so they overstate LTV and understate payback. Only the script's optional `--gross-margin` (`:259`) corrects this. Make margin-adjusted the default in the prose.
- **Mostly textbook.** Around 70% of the body is textbook material: MRR/ARR definitions (`:54-89`), break-even (`:152-174`) and benchmark tables with no source or date (`:268-278`). The Runway section (`:176-196`) duplicates burn-rate-tracker, and its rule "Raise when you have 6+ months" (`:193`) conflicts with the other skills.
- The READ-ONLY banner (`:11-16`) contradicts "Artifact Generation (Required) … Write" (`:248-253`). The script path `:261` is wrong, and `bin/cure-unit-economics` exists. `:242` "2025" query is stale.
- Rewrite target: Cure's pricing defaults, the script contract, and which benchmark sources to trust. Aim for about 120 lines.

### finops (16/30)
- **Stale model price table at `:179-189`.** It lists GPT-4o-mini \$0.15, Claude Haiku \$0.25, GPT-4 \$30 and Claude Opus \$15, all 2024-era prices. Current Opus-class pricing is far lower, so the "Premium" tier advice is wrong. Replace the table with "look up current prices; route by capability tier" and name tiers without prices.
- **Shouting.** "Every project MUST have" (`:52`) and "Every GCP resource MUST be tagged" (`:67`). Explain why instead, for example that untagged spend cannot be attributed.
- **Outdated tooling.** "Looker Studio or Data Studio" (`:55`): Data Studio was renamed in 2022. `gsutil label set` (`:79`): gsutil is superseded by `gcloud storage`. The Cloud Run CUD percentages `:132-133` need verifying against current flexible-CUD terms.
- **Contradiction.** Recurring Mode says "read-only run" (`:433`), but Artifact Generation requires writing `.tf`, `.sh` and `.sql` files (`:377-382`). State that the recurring run writes only the report.
- `:70-78` uses "antigravity" as the example label. That is a portfolio product name that collides with Google Antigravity, a runtime this same library targets.

### fundraising-materials (13/30, REWRITE)
- **The SAFE math is wrong (`:343-353`).** "Price per share at round: \$14M / 10M shares = \$1.40" uses post-money. The round price is pre-money over pre-money fully diluted shares, which gives \$1.20 here. The skill also never distinguishes post-money SAFEs (the YC standard since 2018, where the cap is divided by company capitalization including the SAFEs) from pre-money SAFEs. A founder running this gets wrong dilution. Fix it or delegate to one canonical cap-table section.
- **Statistics that could be mistaken for fact.** `:71-75` has "LATAM merchants lose 12% of revenue…" and "Enterprises spend \$2M+/year…". `:90`, `:96-97` give TAM figures. None has a source, and they are presented as slide content. Mark them clearly as placeholders or delete them.
- **Duplicated sections.** The investor update (`:206-247`), data room (`:249-328`) and cap table (`:330-393`) are duplicated in investor-reporting (`:56-149`, `:249-338`, `reference/details.md:220+`). This contradicts the trigger at `:4` ("NOT for ongoing investor updates"). Keep the deck and pipeline here and move the rest.
- The READ-ONLY banner (`:11-16`) contradicts the required Write artifacts (`:447-455`). At 492 lines the file is at the 500 cap and has no reference files. `:456` "2025" query is stale.

### investor-reporting (17/30)
- **Hard-coded portfolio everywhere.** It appears at `:21`, `:45-49`, `:115-119` and `:345-427`. The KPI tables for five products (`:345-427`, about 85 lines) belong in `reference/` or in PORTFOLIO.md. "Antigravity — AI agent orchestration IDE" (`:394`) contradicts product-marketing `:129-136`, which calls it a framework that is "VS Code-native".
- **The example names a real organization.** "Signed LOI with Baptist Health for Autograph pilot" (`:83`) could be read as fact. Use a placeholder.
- **Thresholds conflict with siblings.** "When to RAISE: Runway < 6 months" (`:231`) and "When to CUT: Runway < 4 months" (`:237`) conflict with burn-rate-tracker (see above). Centralize the thresholds in one skill.
- `:14-17` injects package.json and git log. Keep only PORTFOLIO.

### proposal-generator (17/30)
- **Misapplied "DESTRUCTIVE" banner (`:11-16`).** The skill drafts markdown into `docs/proposals/`, which is not destructive. The banner plus `disable-model-invocation: true` (`:6`) is over-emphasis, and it keeps the skill from auto-triggering on "draft a SOW". Keep the confirm-before-send rule, drop the DESTRUCTIVE framing, and reconsider the flag.
- The Cure-specific value is the terms block (`:250-283`) and the rate and payment defaults. The generic proposal skeleton (`:69-136`) is textbook. The final-payment split conflicts with engineering-cost-model (see above).
- `:24-27` injects the *current* repo's package.json and git log into a client proposal. That is almost always the wrong repo.
- `:58` "Use WebSearch to validate market rates" is a Claude tool name. Say "search the web, if available".

### comps-analysis / dcf-modeling / equity-research / merger-modeling (S1 = 1 for all four)
- **All four are pure textbook.** A frontier model reproduces every one of these workflows unprompted. They contain no Cure-specific data sources, no date or as-of discipline beyond one line, no calculators, and no link to Cure's portfolio. For example, none says how to value a pre-revenue studio product, which is the only valuation Cure plausibly does.
- **dcf-modeling `:39` double-counts cash.** "Equity Value: Enterprise Value − Net Debt − Minority Interest + Cash." Net debt already nets cash, so it should be EV − net debt − minority interest − preferred (+ non-operating assets). That is a real error.
- **comps-analysis `:71` is nonsense in context.** "Clean Architecture: Separate data extraction logic from valuation calculations" is an engineering rule pasted into a finance skill.
- **They overlap with agents.** They duplicate the `investment-banker` agent (Comps/DCF/LBO) and the `equity-analyst` agent. Merge them into the agents' bodies, or into one `valuation` skill with a script (DCF, sensitivity grid and accretion/dilution in stdlib Python). That would earn the context.

### go-to-market (18/30)
- It is a generic 4P/launch template (`:23-86`). The only opinionated line is `:21` ("cuts low-leverage activities"), and nothing in the body does that. Add Cure's actual defaults: channel priorities for a small studio, the kill list, pricing-tier defaults.
- `:15-17` injects package.json and git log, which is irrelevant to GTM. `:90` "using Write" and `:100` "Use WebSearch" are Claude tool names.
- `:63` has tiers "Free / Starter / Pro / Elite", while saas-financial-model `:121-126` has "Free/Starter/Pro/Enterprise". Pick one Cure default.

### growth-engineering (17/30)
- Around 60% is textbook: AARRR (`:43-74`), the K-factor formula (`:164-168`), Hook-model loops (`:118-131`), generic A/B guidance (`:227-251`). Benchmarks have no source: "Two-sided rewards outperform one-sided 2-3x" (`:186`), "D30 >20% consumer, >40% B2B" (`:58`).
- The genuinely Cure-specific line is `:294` ("Cure default: no credit card required, reverse trial model"). Lead with the defaults and cut the rest.
- `:141` "Cloud Function / cron job" is fine. `:307-310` mandates four generated files, including a TS sample-size calculator, which duplicates the ab-test-analyst agent. Make it optional.

### instagram-publishing-setup (S4 3)
- `:96` and `:106` pin `graph.instagram.com/v23.0`. v23 shipped around mid-2025, and by 2026-09 newer versions exist and v23's deprecation date should be checked. Pin a version in one variable and add "check the current Graph API version". I could not confirm v23 is still supported, so verify it.
- `:87` `pbpaste` and `:127` `sips` are macOS-only. Add Linux equivalents (`xclip -o`, `convert`/`magick`).
- Otherwise this is the model skill in the slice: experiential traps, a bundled checker, and a troubleshooting table.

### product-marketing (15/30)
- **Stale facts.** "58-skill standardized delivery framework" (`:169`); the library has 103. "YouTube Shorts … under 60 seconds" (`:222`): Shorts allow up to 3 minutes since Oct 2024. "Instagram Reels 30s max" (`:184`) confuses the recommended length with the platform limit, which is several minutes now. "Hashtags: 15–20" (`:188`, `:201`): Instagram guidance moved to 3–5 and a hashtag cap was reported in late 2025. I cannot confirm the cap as of 2026, so verify it. Every platform rule is presented as "Do not deviate" (`:179`).
- **The product registry (`:71-173`, about 100 lines) should be a sibling file or PORTFOLIO.md.** It duplicates burn-rate-tracker, fundraising-materials and investor-reporting, and its "Antigravity" entry conflicts with the others.
- **Over-prescription.** "Do not deviate" (`:179`), "Output this exact structure for every content piece" (`:322`), and seven principles in bold.
- `:18-21` injects package.json and git log, which is irrelevant.

### seo-content-engine (15/30)
- **Dead metrics and tools.** `:71` and `:88-89` use FID as a Core Web Vital, but it was replaced by INP in March 2024. INP is listed at `:94` alongside it, which is contradictory. `:70` refers to the "Google Mobile-Friendly Test", which was retired in Dec 2023. `:46` has a "search volume 2025" query.
- **Wasted effort on FAQPage.** The FAQPage JSON-LD (`:136-149`) is presented as a standard page type, but Google restricted FAQ rich results to authoritative government and health sites in 2023. Add that caveat or drop it.
- **Trigger is 411 chars.** The when_to_use has two NOT-clauses plus quoted keywords.
- **Contradiction.** Recurring Mode claims "read-only run" (`:218`), but `:52-58` makes Write-generated files "Required". Also, `next-sitemap.config.js` and `src/components/*.tsx` assume Next.js pages-era patterns. The App Router has a native `sitemap.ts` and a metadata API.

### technical-blog-writer (S3 3)
- It overlaps the `technical-content-strategist` agent, whose description is nearly identical ("Famous Actor" tone, Netflix/Uber style). Differentiate the trigger ("single post" versus "content program") or fold the skill into the agent.

### audit-risk-substantiation (S4 3)
- **It contradicts its own reference file.** `:59-61` says disclosure "does **not** help for … §7701(o) failures". `reference/penalty-map.md:17` correctly says disclosure "Reduces 40%→20%" under §6662(i). `:55-56` "40% strict liability" is also only the undisclosed rate. Fix the SKILL.md text.
- `:65-69` "`audit-risk` binding" is fine as binding-name indirection.

### cpa-benchmark (S4 3, S5 3)
- **The bundled answer key has a likely-wrong threshold.** `benchmark/questions/tcp-planning.json:11` gives the 2026 §199A threshold as \$201,775 (see irc-lookup below). A benchmark that grades against a wrong figure penalizes correct answers.
- **Node dependency.** The runner is `run.mjs` (`:21-31`), so it needs Node. The repo convention is stdlib Python for bundled scripts (CLAUDE.md, `docs/SCRIPTS_CONVENTION.md`). It lives under `benchmark/`, not `scripts/`, so the audit may not catch it, but Codex and Antigravity hosts without Node cannot run it. Either port it or state the Node requirement in the frontmatter description.
- The overlay path `.claude/tax-benchmark/questions/` (`:72`) is Claude-specific. The env var alternative (`:73`) is the portable path, so lead with it.
- Items citing "SSTS No. 6" (`reg-core.json:8,11`) inherit the SSTS numbering issue below.

### cpa-standards (S4 2)
- **Out-of-date SSTS structure.** `:22` says SSTS were "revised effective 2024", but `:71-81` presents the *pre-2024* seven-statement structure ("No. 1"…"No. 7"). The revised SSTS (effective Jan 1, 2024) are renumbered in a 1.x scheme, and I believe they add standards (for example on data protection and representing taxpayers). Verify the exact section list against the AICPA text.
- **The SSTS No. 1 standard shown is stale.** `:75` "realistic possibility of success" is the pre-2010 SSTS No. 1 standard. It has since been aligned to the taxing authority's standard: substantial authority, or reasonable basis with disclosure. This sits directly next to the correct position ladder at `:30-36`, so the file contradicts itself.
- The same "SSTS No. N" numbering recurs in `reference/circular-230-checklist.md:18,30,35,37,80`, `reference/workpaper-standards.md:37` and `return-review/reference/common-errors.md:55-56`.

### deductions-and-credits (S4 2)
Currency problems for TY2026:
- **§25D is presented as live.** `reference/credits-catalog.md:96-100` shows §25D with no termination flag. OBBBA terminated §25D for expenditures after 2025-12-31, and the screening list `:130` only says "check termination dates" next to §30D. §25C (also terminated after 2025) is not mentioned.
- **§21 rates are stale.** `credits-catalog.md:87` says "20–35% of up to \$3,000/\$6,000". OBBBA raised the maximum §21 rate (to 50% at low AGI) from 2026, and §129 DCAP goes to \$7,500 in 2026. I am confident about the direction but not about the exact phase-down schedule, so verify.
- **WOTC (§51) is presented as live.** `credits-catalog.md:52-56` treats it as available. Its statutory authorization ran through hires beginning work by 2025-12-31, and I cannot confirm it was extended in 2026. Mark it `VERIFY`.
- **Broken reference.** `SKILL.md:92` "see `retirement-plan`" names no skill in the library and no documented binding. Remove it or name the binding.
- `reference/deductions-catalog.md:14` omits the 2026 SECURE 2.0 changes: the mandatory Roth catch-up for prior-year FICA wages over about \$150k, and the age 60–63 super catch-up. Both are material to the "largest lever" row.
- Confirmed or plausible 2026 figures: HSA \$4,400/\$8,750; 402(g) \$24,500; catch-up \$8,000; 415(c) \$72,000; DB \$290,000; SALT \$40,400/\$20,200 MFS with the phase-down above ~\$505k; §179 \$2.56M/\$4.09M; mileage 72.5¢. I could not independently confirm mileage and §179 against the IRS notice, so they are plausible but unconfirmed.

### irc-lookup (S4 3, S5 3)
- **The QBI threshold example looks wrong (`:81`).** It says "2026 threshold \$201,775 single / \$403,500 MFJ per Rev. Proc. 2025-32". The MFJ threshold is statutorily 2× single, and §199A(e)(2) rounds to multiples of \$50. \$201,775 fails both tests (2 × 201,775 = 403,550). The consistent pair is \$201,750 / \$403,500. Verify against Rev. Proc. 2025-32 before trusting either. Because this is the skill's model of a complete citation, the error propagates.
- **obbba-changes.md is accurate as I understand P.L. 119-21.** Standard deduction 2026 \$16,100/\$32,200/\$24,150; SALT; tips, overtime, senior and car-loan; AMT 50% phase-out; §168(k); §163(j); 1099 thresholds; §1202 tiering and the \$15M/\$75M caps. The `VERIFY` flag on §1202 is conservative; the figures match the enacted text as I know it. Gaps: no 2025 standard deduction (\$15,750/\$31,500/\$23,625), and no entries for the §25C/§25D/§30D terminations, §21/§129 changes, Trump accounts, or the estate exemption (\$15M).
- `obbba-changes.md:53-55`: "Rescheduling was not enacted by OBBBA" is true. Federal marijuana rescheduling was advancing administratively (a late-2025 executive order), and I cannot confirm its 2026 status. If Schedule III took effect, §280E stops applying to state-legal marijuana. Mark it `VERIFY`, not settled.
- `:26` routes bindings through `.claude/tax-profile.md`, a Claude-specific path. Offer a neutral location, or say "wherever the project keeps its tax profile".

### return-review (S4 3)
- `:106` lists "§174A retroactive" as a live accounting-method opportunity. For small businesses the retroactive 2022–2024 election had a deadline, which I believe was about July 6, 2026 under Rev. Proc. 2025-28, so it has likely passed. Verify. The accelerated recovery of unamortized 2022–2024 domestic R&E is a separate item that remains relevant for the 2025 return.

### software-dev-tax (S4 3)
- **The retroactive-election window is presented as open.** `:62-70` "The retroactive opportunity … claimed via Form 3115" does not mention that the small-business retroactive election had a filing deadline, which I believe was about 2026-07-06 per Rev. Proc. 2025-28, via amended returns or an election statement rather than Form 3115. As of 2026-09-23 it is likely closed. The 1- or 2-year recovery of unamortized amounts is a separate, still-live method change. Split the two and date the first. I am fairly but not fully confident of the deadline, so verify. The same issue appears in `irc-lookup/reference/obbba-changes.md:36` and `tax-recommendations/reference/scoring-model.md:88`.
- `:31` cites §174(c)(3) as the software rule for domestic development. After OBBBA, domestic R&E lives in §174A, which carries its own software-development rule, and §174 now governs foreign R&E. Cite §174A's provision and verify the subsection.
- `:218-225` correctly uses the `cure-repo-activity` PATH wrapper. It is the only skill in the slice that does.

### tax-recommendations (S4 2)
- **The flagship example is wrong (`:23-25`).** It says "Adopt a solo 401(k) by 12/31 — \$24,500 … deferral saves ~\$8,900 federal + SE". Elective deferrals do not reduce SE tax (§1402 is computed before the deferral), so "+ SE" is wrong. Also, SECURE 2.0 §317 lets a sole proprietor with no employees establish a solo 401(k) after year-end and make first-year employee deferrals until the return due date, so "by 12/31" is stale for exactly the taxpayer in the example. This is the skill's model of a good recommendation, so fix it first.

### tax-strategies (S4 3)
- `:80` says "401(k) by year end for deferrals". This is stale for sole proprietors under SECURE 2.0 §317; state the exception. It is repeated in `reference/strategy-playbook.md:158` and `tax-preparation/reference/filing-calendar-2026.md:34`.
- `:84` lists the Form 8850 (WOTC) deadline as live. See the WOTC note above. It is repeated in `tax-preparation/reference/elections-and-deadlines.md:13` and `filing-calendar-2026.md:54`.
- `:81` gives the NY PTET election as March 15. That is correct for NY, but several states' PTETs were drafted around the pre-OBBBA 2025 SALT-cap sunset. Add "confirm the state PTET is still in force for the year".

---

## Cross-cutting patterns (≥3 skills)

| # | Pattern | Count | Skills |
|---|---|---|---|
| 1 | **Boilerplate `!` auto-context with an irrelevant stack probe** (package.json/build.gradle/Podfile + git log + src layout) in non-code skills. On Antigravity it renders as literal text, and in Claude it spends tokens on noise. | 12 of 18 skills using `!` injection | burn-rate-tracker, engineering-cost-model, finops, fundraising-materials, investor-reporting, proposal-generator, saas-financial-model, technical-estimation, go-to-market, growth-engineering, product-marketing, seo-content-engine |
| 2 | `!` injection **without** the "run these yourself" fallback sentence | 5 | bid-decision, buyer-intelligence, capture-management, public-sector-contracting, technical-estimation |
| 3 | **Hard-coded portfolio registry** (Vendly/Autograph/The Initiated/Antigravity/TwntyHoops) duplicated in skill bodies instead of PORTFOLIO.md. "Antigravity" is described inconsistently (framework, IDE, "VS Code-native") and collides with Google Antigravity, a runtime this library targets. | 4 (+finops label example) | burn-rate-tracker, fundraising-materials, investor-reporting, product-marketing |
| 4 | **READ-ONLY banner falsely claiming frontmatter enforcement** (only `allowed-tools` present, which does not restrict). 3 of the 4 then require Write artifacts or Bash scripts. | 4 | burn-rate-tracker, engineering-cost-model, fundraising-materials, saas-financial-model |
| 5 | **Recurring Mode says "read-only run"** while the body mandates "Artifact Generation (Required) … Write" | 4 | burn-rate-tracker, finops, investor-reporting, seo-content-engine |
| 6 | **Year-stamped "2025" search queries**, stale by construction | 4 | engineering-cost-model, fundraising-materials, saas-financial-model, seo-content-engine |
| 7 | **Stale AI model names or prices** (GPT-4, 4o-mini, Haiku \$0.25, Opus \$15) | 3 | finops, burn-rate-tracker, engineering-cost-model |
| 8 | **Wrong bundled-script paths** (missing `business/`) and the existing `bin/cure-*` PATH wrapper never mentioned | 3 | burn-rate-tracker, engineering-cost-model, saas-financial-model |
| 9 | **Trigger text over the 350-char target** | 7 | engineering-cost-model (497), seo-content-engine (411), rfp-evaluation (391), buyer-intelligence (385), solicitation-triage (384), capture-management (373), bid-decision (367) |
| 10 | **Claude-only tool names in prose** (WebSearch/Write) without neutral phrasing, or in `allowed-tools` | 17 | all 11 `allowed-tools` business skills, plus finops, go-to-market, growth-engineering, seo-content-engine, investor-reporting, proposal-generator |
| 11 | **Contradictory cross-skill thresholds or defaults** (runway raise/cut triggers; payment split 30/30/30/10 vs 20% final; pricing tier names) | 6 | burn-rate-tracker, saas-financial-model, investor-reporting, engineering-cost-model, proposal-generator, go-to-market |
| 12 | **Duplicated sections across skills** (investor update, data room and cap table in 2 skills; runway in 3; RFI/debrief/operative-verb/FOIA guidance repeated across the public-sector cluster) | 9 | fundraising-materials, investor-reporting, saas-financial-model, burn-rate-tracker, bid-decision, buyer-intelligence, capture-management, solicitation-triage, rfp-evaluation |
| 13 | **Textbook-only body (S1 ≤2)** | 10 | all 4 finance, saas-financial-model, burn-rate-tracker, fundraising-materials, go-to-market, growth-engineering, seo-content-engine |
| 14 | **Tax: 2026 currency drift on post-2025 law** (terminated credits, SECURE 2.0 timing, §174A retro window, SSTS revision, QBI figure) | 7 skills plus 6 reference files | deductions-and-credits, cpa-standards, tax-recommendations, tax-strategies, software-dev-tax, irc-lookup, cpa-benchmark |
| 15 | **Tax: Claude-specific `.claude/` path for the taxpayer profile and overlays** | 2 SKILL.md + README + template | irc-lookup, cpa-benchmark (also `tax/README.md:11,85`) |

Positive pattern worth copying: tax skills and instagram-publishing-setup use no `!` injection, reference sibling files with guidance on when to read them, flag their own uncertainty (`VERIFY`/`RECALL`), and write for judgment rather than scripts. The public-sector cluster is high-signal and experiential, and its main problems are length and duplication.

---

## Top 10 highest-leverage fixes

1. **Fix tax-recommendations `:23-25`.** The model recommendation claims the deferral saves SE tax and uses a stale 12/31 adoption rule. Then fix the same 401(k) timing in tax-strategies `:80`, strategy-playbook `:158` and filing-calendar `:34`. This is the example every recommendation copies.
2. **Verify and correct the 2026 §199A threshold** (\$201,775 is not a \$50 multiple, and MFJ ≠ 2× single) in irc-lookup `:81` and `cpa-benchmark/.../tcp-planning.json:11`. The benchmark currently grades against it.
3. **Refresh deductions-and-credits for TY2026.** Mark §25D and §25C terminated after 2025; update §21 and §129 for OBBBA; set WOTC to `VERIFY`/lapsed; remove the `retirement-plan` dead reference; add the SECURE 2.0 2026 catch-up rules.
4. **Date the §174A small-business retroactive election** (likely closed about 2026-07-06, verify) and separate it from the still-live unamortized-R&E recovery. The fix goes in software-dev-tax `:62-70`, obbba-changes `:36`, return-review `:106` and scoring-model `:88`.
5. **Rewrite the cpa-standards SSTS table (`:71-81`)** to the 2024 revised structure and drop "realistic possibility" (`:75`). Propagate the change to the three reference files and the benchmark item.
6. **Fix the fundraising-materials SAFE math (`:343-353`)** and choose one canonical home for the data room, cap table and investor update, which means deleting the duplicates. Remove the unsourced market statistics (`:71-97`).
7. **Remove the irrelevant package.json/git-log injection from 12 non-code skills** and keep only the PORTFOLIO probe. Add the fallback sentence to the 5 public-sector skills that lack it. This is one mechanical sweep and cuts per-call noise across a third of the slice.
8. **Resolve the READ-ONLY vs Write contradiction in 4 skills.** Either add `disallowed-tools: Write Edit` and make the artifacts inline, or delete the false "enforced by frontmatter" banner. Fix the recurring-mode wording in 4 skills and the script paths in 3 (point to `bin/cure-runway`, `cure-cost-estimator` and `cure-unit-economics`).
9. **Collapse the four finance skills** into the investment-banker and equity-analyst agents, or into one `valuation` skill with a stdlib DCF/sensitivity/accretion script. Fix the DCF equity bridge (`dcf-modeling:39`) in whatever survives.
10. **Move the portfolio registry out of 4 skill bodies into PORTFOLIO.md** or a sibling reference file, reconcile the "Antigravity" description, and refresh the dead platform facts in the same pass. These include FID and the Mobile-Friendly Test (seo-content-engine `:70-71,88`), Shorts ≤60s and the hashtag counts (product-marketing `:188,222`), the "58-skill" figure (`:169`), and the 2024 model price table (finops `:179-189`).

### Figures I could not confirm as current (flagged, not asserted)
- Whether WOTC (§51) was reauthorized for hires after 2025-12-31.
- The exact Rev. Proc. 2025-28 deadline for the §174A small-business retroactive election (I believe 2026-07-06).
- The exact 2026 §199A threshold (I believe \$201,750/\$403,500).
- Federal marijuana rescheduling status in 2026 (affects §280E).
- The 2026 standard mileage rate of 72.5¢ and §179 \$2.56M/\$4.09M: plausible, but I have not verified them against IRS notices.
- The OBBBA §21 phase-down schedule.
- The revised SSTS section list.
- Instagram Graph API v23.0 support status and any 2025–26 hashtag cap.
- The SendGrid free-tier retirement.
- Current Cloud Run CUD percentages.
