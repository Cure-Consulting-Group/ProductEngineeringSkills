# Wave 5 skill review — platform / product / security / legal (27 skills)

Reviewer slice: `skills/platform/` (11), `skills/product/` (11), `skills/security/` (4), `skills/legal/` (1).
Date: 2026-09-23. Read-only. Every SKILL.md read in full; sibling reference files skimmed (headings + targeted greps).
Line numbers refer to `SKILL.md` unless another file is named.

Scale: S1 signal density · S2 instruction style · S3 trigger quality · S4 currency/correctness · S5 cross-runtime portability · S6 progressive disclosure. 1 = poor, 5 = excellent.

## Scorecard

| Skill | S1 | S2 | S3 | S4 | S5 | S6 | Total/30 | Verdict |
|---|---|---|---|---|---|---|---|---|
| platform/chaos-engineering | 2 | 2 | 4 | 2 | 3 | 2 | 15 | TIGHTEN: cut the textbook resilience patterns, fix the wrong fault-injection advice, make code generation conditional |
| platform/ci-cd-pipeline | 3 | 2 | 4 | 2 | 3 | 4 | 18 | TIGHTEN: update runtimes and actions to 2026, replace JSON service-account keys with WIF |
| platform/disaster-recovery | 3 | 3 | 4 | 2 | 3 | 3 | 18 | TIGHTEN: Firestore backup and consistency facts are wrong or stale |
| platform/dora-metrics | 2 | 3 | 4 | 2 | 3 | 2 | 16 | TIGHTEN: core metric definitions are hidden in reference while ASCII dashboards sit in the body; DORA tiers are stale |
| platform/edge-computing | 2 | 3 | 3 | 1 | 3 | 2 | 14 | REWRITE: the Next.js/Vercel APIs are removed or deprecated |
| platform/engagement-automation | 5 | 4 | 4 | 4 | 2 | 5 | 24 | KEEP: small fixes only |
| platform/green-software | 2 | 3 | 4 | 2 | 3 | 4 | 18 | TIGHTEN |
| platform/incident-response | 2 | 2 | 4 | 3 | 3 | 3 | 17 | TIGHTEN: must not force code generation during a live incident |
| platform/infrastructure-scaffold | 3 | 2 | 3 | 1 | 3 | 3 | 15 | TIGHTEN (facts): several configs are wrong |
| platform/observability | 3 | 3 | 4 | 4 | 3 | 4 | 21 | TIGHTEN (minor) |
| platform/release-management | 3 | 3 | 4 | 2 | 3 | 4 | 19 | TIGHTEN |
| product/customer-onboarding | 2 | 2 | 4 | 4 | 3 | 4 | 19 | TIGHTEN |
| product/design-studio | 5 | 4 | 4 | 4 | 4 | 5 | 26 | KEEP: the model for the others |
| product/design-system | 2 | 2 | 3 | 2 | 3 | 3 | 15 | TIGHTEN: narrow to implementation and governance; adopt design-studio's token format |
| product/feature-audit | 4 | 2 | 2 | 3 | 4 | 4 | 19 | TIGHTEN: body does not deliver what the description promises; name collision |
| product/feature-flags | 3 | 3 | 3 | 3 | 3 | 3 | 18 | TIGHTEN |
| product/market-research | 3 | 2 | 3 | 2 | 2 | 5 | 17 | TIGHTEN: read-only banner contradicts required Write |
| product/portfolio-registry | 4 | 3 | 4 | 2 | 1 | 1 | 15 | REWRITE: over 500 lines, broken fences, Claude-only paths |
| product/product-design | 2 | 2 | 1 | 3 | 3 | 4 | 15 | MERGE-INTO:design-studio |
| product/product-manager | 2 | 2 | 3 | 3 | 3 | 4 | 17 | TIGHTEN |
| product/technology-radar | 4 | 3 | 4 | 2 | 3 | 3 | 19 | TIGHTEN: default radar is stale |
| product/uat | 3 | 3 | 4 | 4 | 3 | 4 | 21 | TIGHTEN (minor) |
| security/accessibility-audit | 2 | 2 | 4 | 3 | 4 | 2 | 17 | TIGHTEN: 430 lines of restated WCAG |
| security/compliance-architect | 3 | 3 | 4 | 1 | 3 | 3 | 17 | REWRITE (facts): penalties, BAA table and COPPA are wrong or stale |
| security/qsbs-compliance | 4 | 3 | 3 | 1 | 3 | 2 | 16 | REWRITE and move to `tax/`: predates OBBBA and contradicts `irc-lookup` |
| security/security-review | 2 | 3 | 4 | 2 | 4 | 4 | 19 | TIGHTEN |
| legal/legal-doc-scaffold | 2 | 1 | 2 | 2 | 3 | 3 | 13 | REWRITE |

Distribution: 13–15: 7 · 16–18: 11 · 19–21: 7 · 22+: 2 (engagement-automation 24, design-studio 26). Mean 17.7/30.
Verdicts: KEEP 2 · TIGHTEN 19 · REWRITE 5 (edge-computing, portfolio-registry, compliance-architect, qsbs-compliance, legal-doc-scaffold) · MERGE 1 (product-design → design-studio) · DEPRECATE 0.

---

## Per-skill findings (every skill has at least one score ≤3)

### platform/chaos-engineering (15)
- **S4, wrong advice.** L240 says "Cloud Run: set maxInstances=0 to simulate service unavailability". Max-instances 0 does not make a service unavailable. Fix: use ingress=internal, delete or disable the traffic tag, or remove IAM invoker for the test.
- **S4, contradicts itself.** L136 gives "User-facing API: 5 seconds"; L312 gives "User-facing: 30s". L175 treats Remote Config fetch interval as the kill-switch latency, but real-time Remote Config listeners exist. Fix: one timeout table, and point at real-time RC for kill switches.
- **S2.** L463–473 "Code Generation (Required)" writes 5 files, including `src/middleware/chaos.ts` and a CI workflow, no matter which of the four Step 1 types was chosen. A "Failure Mode Analysis" request should not scaffold middleware. Fix: map each deliverable to a Step 1 type.
- **S1 / S6.** L89–177 (circuit breaker, bulkhead, retry with backoff) and L258–325 (platform resilience) are textbook, and the body is 473 lines with no reference file. Fix: keep the Firebase/GCP injection methods (L233–256) and the steady-state hypotheses; drop or offload the rest.
- **S5.** L465 "using Write" and L473 "Grep for …" are Claude tool names. The generic `package.json` injection (L15–18) is marginal for this domain.

### platform/ci-cd-pipeline (18)
- **S4, stale runtimes.** Node 20 at L74 and L153 reached EOL in April 2026. `actions/checkout@v4`, `setup-node@v4` and `gradle/actions/setup-gradle@v3` (L72–103) are behind current majors, and `w9jds/firebase-action@v13.22.1` (L157) is pinned to an old CLI. Fix: Node 22/24 LTS, current action majors, pinned by SHA per `rules/cicd.md`.
- **S4, security posture.** L83, L111, L161 and L169 use a long-lived `FIREBASE_SERVICE_ACCOUNT` JSON key. The 2026 default is Workload Identity Federation (`google-github-actions/auth` with OIDC). This matters for a Cure standard.
- **S4, incorrect.** L211 says "TestFlight → expire current build, previous is auto-available". That is not an App Store rollback. L208 `hosting:clone` omits the `@VERSION` form needed to roll back. L27 recommends "Next.js + Firebase Hosting | …Export", but App Hosting is Firebase's supported Next.js path.
- **S2.** L219 says "You MUST generate actual workflow files using the Write tool", unconditionally. The Step 3 branch model ("main → auto-deploy to production") also contradicts release-management L17 ("never released directly from main") and infrastructure-scaffold L154 (production = `release/*`). Fix: pick one Cure branching policy and cross-reference it.

### platform/disaster-recovery (18)
- **S4, factual error.** L263 says Firestore multi-region gives "Strong consistency within region, eventual across regions". Firestore multi-region is strongly consistent. Fix the line; it drives Tier-1 RPO claims.
- **S4, stale.** L94–110 builds backups from `gcloud firestore export` plus Cloud Scheduler. Native Firestore scheduled backups (`gcloud firestore backups schedules create`) and 7-day PITR now exist and should be the default. `gsutil` (L133–159) is superseded by `gcloud storage`.
- **S4.** L238–244 proxies a CNAME to `*.cloudfunctions.net`, which fails on the Host header and certificate. L272 says Memorystore Standard gives failover "within zone"; it fails over across zones in a region. L201 labels shell commands as `yaml`.
- **S6.** L278 "See reference/details.md (section “Step 6: DR Runbooks”) for full detail". The runbooks are the core deliverable, but the pointer gives no guidance on when to read them. Meanwhile the vendor SLA table (L386–400) and alternate-tools list (L371–381) stay inline. The disclosure is inverted.

### platform/dora-metrics (16)
- **S4, stale.** The tiers use the 2021-era cut-offs: `reference/details.md` L136 "Elite: 0-15%" CFR, and body L158 "<15% (Elite)". The 2023/2024 State of DevOps reports renamed MTTR to "failed deployment recovery time", tightened elite CFR (about 5%), and added rework rate as a fifth metric. Fix: cite the report year and update the clusters.
- **S4, broken paths.** L379, L384 and L388 run `python3 skills/dora-metrics/scripts/...`. The skill now lives at `skills/platform/dora-metrics/`. Fix: skill-relative paths (`$SKILL_DIR/scripts/...`, or plain `scripts/...` with a note).
- **S6, inverted disclosure.** L45 moves the four metric definitions (the heart of the skill) to reference. Meanwhile about 75 lines of illustrative ASCII dashboards with fake numbers (L143–215) and the SPACE survey stay inline.
- **S2 / duplication.** L364–371 "Automated Metric Collection" (grep for revert/hotfix) duplicates the bundled scripts less rigorously, and L395 then requires generating `scripts/collect-dora-metrics.sh`, a third implementation. Fix: tell the model to run the bundled scripts and delete the other two paths.

### platform/edge-computing (14)
- **S4, removed APIs.** L109, L275 and L329 use `request.geo` and `request.ip`, which were removed in Next.js 15 (use `geolocation()`/`ipAddress()` from `@vercel/functions`). L94 and L492 use `middleware.ts`, renamed to `proxy.ts` in Next 16 (Node runtime by default).
- **S4, deprecated platform guidance.** L46–48 recommends `runtime = "edge"`. Vercel now steers to Node on Fluid compute. L354 names "Vercel KV", which was sunset and moved to Upstash via the Marketplace. L227 `revalidateTag(tag)` uses the pre-Next-16 single-argument form. L129 `"dynamicLinks": false` is a leftover from Firebase Dynamic Links, shut down in August 2025.
- **S4, code bug.** L302 says "Assign variant based on hash of user identifier", but L303 uses `Math.random()`. L334 uses an undefined `kv`.
- **S1 / S6.** 495 lines, mostly generic CDN and caching lore (L150–173, L196–206). The cost and latency table (L437–447) has no source. Fix: rewrite around Cure's actual Vercel and Firebase choices, about 200 lines, and cross-reference the Vercel plugin skills (`vercel:routing-middleware`, `vercel:cdn-caching`) when installed. S3 overlap: performance-review, nextjs-feature-scaffold.

### platform/engagement-automation (24)
- **S5.** The skill is entirely about Claude Code mechanisms (`/loop`, `/schedule`, `.claude/loop.md` at L61, hooks). Under Codex or Antigravity it will confidently recommend commands that do not exist. Fix: add one paragraph mapping each mechanism to its Codex and Antigravity equivalent, or saying "none; use CI cron".
- **S2 nit.** The guardrail list numbers item 5 twice (L93, L94). L73 "No exceptions" and L89 "absolute" add emphasis the rationale already carries.
- **S3.** Trigger text is 405 characters, over the 350 budget. Trim the "NOT for" clause.

### platform/green-software (18)
- **S4, stale or wrong.** L128 says "iOS: enable bitcode". Bitcode has been deprecated since Xcode 14. L75 recommends "Tau T2A"; GCP's current Arm line is Axion (C4A), and "60% less energy" has no source. L198 uses `api.electricitymap.org`; the current API domain is `electricitymaps.com`. L253 cites "SCI specification v1.0"; SCI is now ISO/IEC 21031:2024. L136 claims dark mode saves "30-60% display power … offer as default", an overclaim.
- **S1.** L80–107 and L111–137 are generic performance and mobile hygiene (compress, paginate, lazy load). Only the SCI method and region carbon data add anything. S3 overlap with `/finops` should be stated in the trigger.
- **S5.** L260 says "Use WebFetch or WebSearch". Use neutral phrasing ("if a web tool is available").

### platform/incident-response (17)
- **S2, harmful in context.** L22 says to use it "during active incidents". L465–473 then makes code generation required: a PagerDuty webhook Cloud Function, a status-page script, and more. That is the wrong behaviour mid-incident. Fix: gate code generation to the "build on-call procedures" path.
- **S1.** Severity ladders, communication templates and the post-mortem template (L43–356) are industry-standard boilerplate the model produces unprompted. Cure-specific value is thin: Firebase examples and 1Password. Fix: keep the Cure severity thresholds and escalation matrix; offload the templates.
- **S4 / consistency.** L381 defines MTTR from detection to resolution. dora-metrics defines MTTR from failure start. The two skills report different numbers for the same term.

### platform/infrastructure-scaffold (15)
- **S4, factual errors.** L420 says "Set Firestore daily spending limit in console", but Firestore has no daily spending limit (the legacy App Engine feature does not apply). L262–263 builds an "error rate > 5%" alert as a threshold of 0.05 on a raw `execution_count` using the 1st-gen `cloudfunctions.googleapis.com` metric, which does not measure a ratio and misses v2 functions (these are `cloud_run_revision`). L111 uses `request.geo` (removed in Next 15). L79 has a no-op rewrite (`/api/:path*` to itself).
- **S4, prices.** L430 gives Firestore "$0.06/100K reads, $0.18/100K writes". These are multi-region (nam5) rates presented as general. Label them or drop them. L125 has the Vercel A record `76.76.21.21`; verify it against current Vercel docs, which now show project-specific records.
- **S2 / S3.** L4 says "NOT for Terraform-specific guidance", yet L444 must generate `main.tf`, `variables.tf` and others, with no Terraform content in the skill. L438 "You MUST generate … using the Write tool". Overlaps firebase-architect (rules, indexes) and ci-cd-pipeline.
- **S2 / S6.** L330–339 has TypeScript inside a `bash` block. Step 10 "Output" (L456) comes after Cross-References. Steps 3, 4 and 6 are bare pointers to `reference/details.md` (484 lines).

### platform/observability (21)
- **S4, inconsistent maths.** L76 availability counts 200–399 as success (so 4xx fail), while L78 error rate counts only 500+. The L94–97 burn-rate thresholds (">2% in 1hr") and L132 (">10x in 5 minutes") use different conventions. Fix: adopt the SRE-workbook multiwindow table (14.4x/1h, 6x/6h) once.
- **S2.** L162–163 "MUST be actionable / MUST have a runbook link". The reasons are good; drop the caps.
- **S6.** Steps 3 and 4 (the three pillars and platform setup) are bare pointers (L64, L68) with no "read when…" guidance.

### platform/release-management (19)
- **S4, stale or wrong.** L346 says "FID <100ms"; FID was replaced by INP in March 2024 (observability L211 already uses INP, so the two skills disagree). L311 recommends `standard-version`, archived and deprecated. L168 "promote previous version to 100%": Play requires a higher versionCode, so you cannot re-promote an older build. L258 `hosting:clone PREVIOUS_VERSION live` has wrong syntax.
- **S2.** The L12–18 "Hard rules" conflict with each other. L16 says "Changelog is generated … no manual writing", but L303 says "Write in user-friendly language". L17 "never released directly from main" contradicts ci-cd-pipeline.
- **S4.** L145 gives a "<150MB AAB" budget; verify it against the current Play base-module download limit.

### product/customer-onboarding (19)
- **S2.** L46–51 are all-caps principles ("ONE GOAL PER SCREEN — never two asks"). L179–187 requires React files (`Step1Welcome.tsx`), but the description covers Android and iOS. L186 asks for "Day 1, Day 3, Day 7 email templates", while Step 7 (L133–150) defines five emails (0/1/3/5/7).
- **S1.** Mostly general onboarding lore. The Cure value is the Vendly and SpedUp activation examples (L68–69). Expand those, or name Cure's actual activation events per portfolio product.
- **S3.** Trigger is 443 characters, the longest in the slice.

### product/design-studio (26)
- **S4 nit.** L49–50 run `cat … | head -60 || echo "(no DESIGN.md)"`. The `||` never fires because `head` exits 0, so the fallback text never prints.
- **S2 nit.** L30 "none needs anything installed" contradicts the "Needs" column (SVG renderer, `FIGMA_TOKEN`).
- **S5.** L141 routes to `dataviz`, which is not a skill in this library (it is host-provided). Say "if available".
- **S3.** "Use for any design assignment" (L4) swallows product-design entirely. Resolve by merging (see product-design).

### product/design-system (15)
- **S4, conflicting formats.** L124–145 uses legacy Style Dictionary `"value"` tokens. design-studio (the sibling it hands off to) mandates W3C DTCG `$value` (`references/w3c_token_schema.json`). A single engagement gets two incompatible token files.
- **S4, stale.** L205–209 addons: `@storybook/addon-interactions` was folded into Storybook 9 core, and `storybook-dark-mode` does not support Storybook 9. L108 lists Tailwind v3 px breakpoints and L411 says "Update tailwind.config.ts", but Tailwind v4 is CSS-first (`@theme`). L173 `dynamicColorScheme` does not exist (the functions are `dynamicLightColorScheme`/`dynamicDarkColorScheme`).
- **S2.** L407 "You MUST generate" six files. L94 "8pt grid" is followed by "multiples of 4".
- **S3.** Overlaps design-studio Step 6 and product-design. Fix: scope to Storybook, Showkase and catalog setup, governance and distribution, consuming design-studio tokens.

### product/feature-audit (19)
- **S3, description ≠ body.** L3 promises audits of "security gaps, accessibility, analytics, and documentation", but Phases 1–4 cover only boundary, logic, wiring and tests. The scorecard (L148–157) has no Web column although Web is in scope. The name also collides with `anthropic-skills:feature-audit` in the session listing.
- **S3 / S2, Recurring Mode describes a different task.** L195 says "Monthly audit of shipped-vs-used features against analytics", which is not what the skill does. L194 `/loop 4w`: loops expire after 7 days (engagement-automation L62, `docs/AUTOMATION.md` L47), so a 4-week interval never fires. L72 "If any required input is missing, ask" cannot happen in an unattended run.
- **S2.** L59 "Execute all 5 phases in order. Do not skip phases. Do not summarize — audit." This rigid script fits a small feature poorly.
- **S4.** L103 `TaskResult` is deprecated in TCA 1.x. The skill assumes TCA everywhere (L101–107, L132), but technology-radar's default radar puts TCA in *Trial* and MVVM in Adopt.

### product/feature-flags (18)
- **S4, the query will not run.** L193–202 queries `analytics_events` with an `experiment_name` column. The Firebase BigQuery export is `events_*` with nested `event_params` (UNNEST). L179–183 logs `user_id` and `serverTimestamp` as event params, which is a PII and API mistake. Firebase Remote Config *rollouts* (Crashlytics-guarded) are the native answer to L242–246 but are not mentioned.
- **S2, contradictory lifespans.** L25 says 90 days; L114 and L283 say 60 days for release and 45 for experiments; L36 says 2–6 weeks. L170 "no significant difference after 2x estimated duration → ship Control" encourages peeking. L440 runs the check "on PR" while L293 runs it "weekly".
- **S3.** Overlaps the ab-test-analyst agent (experiment design, sample size) and growth-engineering. Hand off A/B statistics to the agent instead of restating them.

### product/market-research (17)
- **S2 / S5, direct contradiction.** L11 is a "READ-ONLY SKILL … do not edit files" banner, then L113–118 is "Artifact Generation (Required) — Generate using Write" with three `docs/*.md` files. The banner also claims Claude Code enforcement via `allowed-tools`/`disallowed-tools`, but only `allowed-tools` is set (L6), and per CLAUDE.md that restricts nothing.
- **S4.** L105 and L107 hard-code the years "2025 2026" in search queries. Use "[current year]".
- **S5.** L22–25 injects `package.json` and git log, which are irrelevant to market sizing. L103 "When using WebSearch" should read "if a web tool is available".
- **S3.** Overlaps the market-intelligence and competitive-intel agents and go-to-market. Add "NOT for …" routing.

### product/portfolio-registry (15)
- **S6, over limit and broken.** 503 lines, over the 500-line library rule. L235 opens a ```` ```markdown ```` fence that is never closed before `## Step 5` (L242) and another fence at L246, so Steps 4–5 render as code. Auto-detection is described twice (L111–118 and L120–138).
- **S5, Claude-only.** L13 and L460–462 use `~/.claude/PORTFOLIO.md` as the canonical location. L469 says "Add `@PORTFOLIO.md` to your CLAUDE.md". The Pre-Processing block (L19) reads only `./PORTFOLIO.md`, so the "global" file is never seen by any skill. Fix: project-root file canonical; mention AGENTS.md and GEMINI.md import equivalents.
- **S4, stale.** L408 "(29+ skills)" (actually 103). L193, L263, L358 and L396 name GPT-4 or GPT-4o. L228 and L399 list "Antigravity — AI agent orchestration IDE (VS Code fork, open source)" as a Cure product; this collides with Google Antigravity, which the library targets as a runtime. Verify with the owner.
- **S2 / privacy.** L126–132 scan `~/Documents`, `~/Projects` and similar, and read `.env*` files. Narrow the scan to what the user names, and never open `.env` (read `.env.example` only).
- **S1.** L11 "The highest-leverage artifact in the skill library … dramatically smarter" is puffery. Move the long templates (L148–454) to reference.

### product/product-design (15)
- **S3, redundant.** design-studio's trigger is "any design assignment". product-design adds a 140-line subset (tokens, touch targets, 8pt grid) already in design-studio references and in the three platform experts. The L12–15 routing to experts duplicates design-studio L93.
- **S2.** L74–80 "Artifact Generation (Required)" writes four docs for every request, including a "Design review / audit" (L54).
- **S4 nit.** L88 "Web minimum 44x44px" states AAA (2.5.5) as the minimum. accessibility-audit L155 correctly says 24px for AA.
- Fix: delete it and add an alias line in design-studio's description ("design spec, HIG/M3 spec") so auto-discovery still lands.

### product/product-manager (17)
- **S2, contradiction.** L4 "NOT for engineering specs (use sdlc)", and L153 says sdlc generates PRDs. Yet L141–143 "You MUST generate … PRD: `docs/prd/{feature-name}.md`".
- **S4 / S2.** RICE appears twice (L73–81 and L125–137) with different Effort units: "Person-weeks" at L80 and "Person-months" at L133. Scores are not comparable across runs.
- **S1.** OKR, RICE and north-star explanations are textbook. S3 overlaps the roadmap-strategist agent. The trigger is 370 characters.
- **S5.** L148 "Use WebSearch".

### product/technology-radar (19)
- **S4, stale default radar** (`reference/details.md`). L124 has "Claude API" in *Trial*, although the library is Claude-first. L147 "Evaluate GPT-4o". L181 says React Native has "bridge overhead" (the New Architecture has been the bridgeless default since 0.76). L44 references `tailwind.config` (Tailwind v4). L10 says "portfolio tech stack defined in CLAUDE.md", a Claude-only source.
- **S2.** L46 writes `docs/technology-radar.md`, but L28 and L431 call the artifact `TECHNOLOGY_RADAR.md`. L498 calls the recurring run "read-only" yet delivers an updated TECHNOLOGY_RADAR.md.
- **S6.** 498 lines, 2 short of the limit. The dependency-file checklist (L60–94) and the divergence tables (L382–405) can move to reference.

### product/uat (21)
- **S2, the gate is incoherent.** L169–175 weights binary GO/NOGO rows as partial scores ("X/30"). P1 is "Must-fix before release" (L105), yet the CONDITIONAL band (L182, 70–89) allows shipping with P1 failures. Fix: make P0 and P1 hard gates and score only the soft criteria.
- **S5.** L46 says "using test-plan output style", a Claude-only output-styles reference with no fallback description.
- **S6.** Step 4, the execution framework, is a bare pointer (L153).

### security/accessibility-audit (17)
- **S1 / S6.** L92–298 is a restatement of WCAG 2.2 and ARIA basics the model knows. The platform API lists (L247–298) are the only non-obvious part. 430 lines. Fix: keep the scan greps, the platform APIs, the Cure severity mapping and the report; cut the principle-by-principle recital.
- **S4.** L46 labels touch targets "WCAG 2.5.5" (AAA) with a `[0-3][0-9]dp` grep, which catches under 40, not under 44 or 48. L152 correctly cites 2.5.8 at 24px. L306 "Lighthouse 95+ for Level AA compliance" is a false equivalence. L90 calls WCAG 2.2 AA "the legally required standard in most jurisdictions", but ADA Title II, EN 301 549 and the EAA reference WCAG 2.1 AA.
- **S4, broken path.** L334–335 use `python3 skills/accessibility-audit/scripts/wcag_check.py`; the skill lives at `skills/security/accessibility-audit/`.
- **S2.** L62 "Execute all 9 steps in order. Do not skip steps." The Recurring Mode (L427) uses `/loop 1w`, but loops expire after 7 days. L430 "deliver WCAG violations as issues" is a write action inside a READ-ONLY skill.

### security/compliance-architect (17)
- **S4, wrong.** L309 says Google Analytics (GA4) BAA is "Available". Google does not sign a BAA for Google Analytics. L302 treats "Google Cloud / Firebase" as one BAA row, but several Firebase products (for example Analytics and Crashlytics) are outside Google's HIPAA-covered list. For Autograph (HIPAA) this matters.
- **S4, stale figures.** L52 HIPAA "up to $1.5M/year" (the inflation-adjusted cap is now over $2M). L53 COPPA "$50,120" (adjusted annually and higher since 2024). L55 CCPA "$2,500/$7,500" (adjusted in 2025). The 2025 COPPA Rule amendments are missing: separate consent for third-party disclosure, written retention policy and security program, with compliance due in April 2026. So are the CPPA ADMT and risk-assessment regulations (2026) and the PCI DSS 4.0.1 future-dated requirements (March 2025). Fix: move figures to a dated reference table with a `VERIFY` date, as the tax domain does.
- **S4, legal errors.** L136 "healthRecords … 6 years (HIPAA)": HIPAA's 6-year rule covers compliance documentation, not medical records (state law governs those). L159 and L181 "COPPA = re-consent annually" is not a COPPA requirement. L436 "30-day grace period (GDPR allows up to 30 days)": the one-month clock is for responding, and a 30-day grace before starting deletion risks breaching it. L265 vs L267: Firestore is the primary audit store, yet "Never store audit logs in the same database".
- **S3.** L4 "use dedicated skills when available" for FERPA. Point to the `legal-compliance` agent instead.

### security/qsbs-compliance (16)
- **S4, predates OBBBA (critical).** L19 ($10M or 10x), L60–65 ($50M) and L80–83 (5 years only) ignore the July 4, 2025 changes. For stock acquired after that date: $15M cap, $75M gross-asset test, and tiered 50/75/100% exclusion at 3/4/5 years. The library's own `skills/tax/irc-lookup/reference/obbba-changes.md` L43 documents this, so the two skills contradict each other.
- **S4, legal errors.** L82 says "Partial exclusion available via §1045 rollover"; §1045 is a deferral, not an exclusion. L86 applies the significant-redemption window as "2 years before or 1 year after"; the statute is 1 year before and after for >5% and 2 years before and after for the shareholder-related test, with de minimis thresholds. L51 is an unedited stream of thought ("voids QSBS retroactively …? No — …"), and L98 ("LLC conversion … voids … entirely") contradicts it.
- **S6.** `references/section-1202-tests.md` (65 lines) is never referenced from SKILL.md.
- **S3 / S5.** Misfiled under `security/`. It belongs in `tax/` beside irc-lookup and the tax-analyst agent. L170 routes to `corp-finance-ops`, which does not exist. The READ-ONLY banner claims frontmatter enforcement, but only `allowed-tools` is set.

### security/security-review (19)
- **S4, stale.** L148 recommends `EncryptedSharedPreferences`, but `androidx.security:security-crypto` is deprecated (use Keystore-backed DataStore or Tink). compliance-architect's Android pattern shares the problem. The description says "OWASP Top 10", but the body never maps to the 2025 list, the API Top 10, the Mobile Top 10 (2024) or the LLM Top 10. That is a gap for Cure's LLM products (L71 asks about "LLM APIs" and nothing follows).
- **S4.** L168 `script-src 'self'` breaks Next.js inline bootstrapping; recommend nonce plus `strict-dynamic`. L44's grep pattern is malformed (`\+ .*query|` + `.*sql`).
- **S1.** Steps 3–9 are a generic OWASP checklist. The Firebase section (L189–196) and the scan greps are the only differentiated content. The trigger is 443 characters.
- **S2.** L234 `/loop 1w` never fires because loops expire. L237 "deliver findings as PR comments or issues" is a write action inside a READ-ONLY skill.

### legal/legal-doc-scaffold (13)
- **S3, the body does not deliver.** The description promises ToS, Privacy Policy, SOW and NDA (plus EULA and DPA in L4). The only template in the body is a refund policy (L98–120). `disable-model-invocation: true` (L6) means "draft a privacy policy" will not auto-load the skill, and generating Markdown is not destructive. L4 routes to `nil-contracts`, which does not exist.
- **S2, shouting and repetition.** The disclaimer appears four times (L29 IMPORTANT DISCLAIMER in caps, L35–39, L43, L128–129), plus the "DESTRUCTIVE" banner (L11). Opus-class models over-apply this. Fix: one calm sentence explaining why attorney review is needed, plus the start and end disclaimer contract.
- **S4, wrong.** L82 "Users under 13 → COPPA — do not collect data". COPPA allows collection with verifiable parental consent, and compliance-architect designs exactly that flow. L83 treats health data as only "HIPAA adjacent", missing the FTC Health Breach Notification Rule and Washington's My Health My Data Act. There is no mention of the roughly 20 US state privacy laws in force by 2026.
- Fix: add `reference/` clause libraries per document type (with Cure's consulting SOW positions: IP, payment, change orders) and remove `disable-model-invocation`.

---

## Cross-cutting patterns (≥3 skills)

| # | Pattern | Count | Skills |
|---|---|---|---|
| 1 | **"Code/Artifact Generation (Required)" writes N files unconditionally**, usually "using the Write tool", regardless of the Step 1 classification | **17** | chaos, ci-cd, disaster-recovery, dora, edge, green, incident-response, infra-scaffold, release-mgmt, customer-onboarding, design-system, feature-flags, market-research, product-design, product-manager, technology-radar, uat |
| 2 | **Generic Pre-Processing block** (PORTFOLIO head, `package.json`/gradle/Podfile head, git log, `ls src/`) pasted verbatim. Irrelevant to the domain in at least market-research, legal-doc-scaffold, product-manager and product-design. `ls src/ …` has no fallback echo. | **24** of 27 (plus a tailored variant in design-studio) | all except engagement-automation, qsbs-compliance, design-studio |
| 3 | **Claude tool names in instructions** (Write, Grep, Glob, WebSearch, WebFetch) without neutral phrasing | **19** | e.g. chaos L465, green L260, market-research L103, product-manager L148, feature-audit L37 |
| 4 | **Bare reference pointers**: "See reference/details.md (section X) for full detail" with no guidance on when to read it, often offloading the *core* step while leaving illustrative ASCII inline | **12** | disaster-recovery, dora, incident-response, infra-scaffold, observability, release-mgmt, design-system, feature-flags, portfolio-registry, technology-radar, uat, compliance-architect |
| 5 | **Stale Next.js/Vercel/web APIs** (`request.geo`/`request.ip`, `middleware.ts`, edge runtime, Vercel KV, FID, `tailwind.config`) | **5** | edge-computing, infra-scaffold, release-management, design-system, technology-radar (ref) |
| 6 | **Stale CI pins** (Node 20 EOL, `actions/checkout@v4`, old action majors) | **4** | ci-cd, chaos, feature-flags, release-management (ref) |
| 7 | **Hard-coded script paths from before the domain move** (`python3 skills/<name>/scripts/...`) | **2** skills / 5 lines | dora-metrics L379/384/388, accessibility-audit L334/335. Mechanical fix; audit-library.py should catch it. |
| 8 | **Read-only contract violated or misdescribed**: banner claims frontmatter enforcement while only `allowed-tools` is set, and/or the skill then requires Write or issue creation | **5** | market-research, qsbs-compliance (allowed-tools only), feature-audit, accessibility-audit and security-review (recurring runs deliver issues/PR comments) |
| 9 | **Recurring Mode `/loop` interval ≥ 7 days**, so it never fires before the loop expires | **3** | feature-audit (4w), accessibility-audit (1w), security-review (1w) |
| 10 | **Rigid "execute all N steps, do not skip, do not summarize" scripts** | **3** | feature-audit L59, accessibility-audit L62, uat (L34/L67 hard stops) |
| 11 | **ALL-CAPS / over-emphasis** ("Hard rules", MUST/NEVER, "non-negotiable", caps banners) | **≥8** | release-mgmt, feature-flags, compliance-architect, observability, design-system, customer-onboarding, product-design, legal-doc-scaffold |
| 12 | **`when_to_use` restates `description`**, wasting trigger budget | **≥9** | dora, observability, release-mgmt, uat, market-research, green, edge, design-system, feature-flags |
| 13 | **Trigger text over the 350-character budget** | **6** | customer-onboarding 443, security-review 443, engagement-automation 405, feature-audit 389, product-manager 370, qsbs 353 |
| 14 | **Routes to skills that do not exist** | **3** | qsbs (`corp-finance-ops`), legal-doc-scaffold (`nil-contracts`), design-studio (`dataviz`, host-provided) |
| 15 | **Cross-skill contradictions** (the same fact stated differently) | **≥5 pairs** | branch policy (ci-cd vs release-mgmt vs infra); MTTR definition (incident vs dora); token format (design-system vs design-studio); FID vs INP (release-mgmt vs observability); TCA default (feature-audit vs technology-radar); QSBS thresholds (qsbs vs tax/irc-lookup) |
| 16 | **Dated legal/regulatory figures inline with no `VERIFY` date** | **3** | compliance-architect, qsbs-compliance, legal-doc-scaffold |

---

## Top 10 highest-leverage fixes (this slice)

1. **qsbs-compliance: rebase on OBBBA and move to `tax/`.** Adopt the $15M / $75M / 3-4-5-year tiering from `tax/irc-lookup/reference/obbba-changes.md`. Fix the §1045 and redemption-window errors (L82, L86), delete the L51 stream of thought, and link `references/section-1202-tests.md`. Wrong QSBS advice has a seven-figure blast radius for Vendly and Autograph.
2. **compliance-architect: correct the facts.** Remove the GA4 "BAA Available" row, split Firebase products by HIPAA coverage, fix the "6 years (HIPAA)" record retention, remove COPPA annual re-consent, add the 2025 COPPA amendments, CCPA 2026 regulations and PCI 4.0.1, and move penalty figures to a dated `VERIFY` table.
3. **Make "Code/Artifact Generation (Required)" conditional in all 17 skills.** Map each deliverable to the Step 1 classification ("if type = X, produce Y"), drop "You MUST … using the Write tool", and say "write files" neutrally. One sed-able edit pattern, and the largest instruction-style gain.
4. **Replace the generic Pre-Processing block (24 skills) with per-domain context, or remove it.** Keep git and stack for engineering skills; drop `package.json` for market-research, legal, product-manager and product-design. Add a fallback echo to `ls src/…`.
5. **edge-computing and infrastructure-scaffold: Next 15/16 and Vercel 2026 refresh.** Use `@vercel/functions` geolocation/ipAddress, `proxy.ts`, the Node runtime default and Upstash instead of Vercel KV. Remove "Firestore daily spending limit" and fix the v1-metric error-rate alert.
6. **Fix the read-only contract (5 skills).** Add `disallowed-tools` where the banner claims enforcement (market-research, qsbs). Remove the required Write from market-research, or drop its read-only banner. State that Recurring Mode delivery (issues and PR comments) is the one permitted write, done by the routine rather than the skill.
7. **Fix Recurring Mode intervals (3 skills).** `/loop 1w` and `/loop 4w` cannot fire before the 7-day expiry. Point weekly and monthly cadences at `/schedule` routines only, and consider an audit rule (interval ≥ 7d → error).
8. **Repair the stale script paths (dora-metrics, accessibility-audit) and add an audit check** for `python3 skills/<name>/` patterns that skip the domain folder.
9. **Merge product-design into design-studio, and narrow design-system** to Storybook, catalog, governance and distribution using DTCG `$value` tokens from design-studio. This removes 3-way trigger overlap and the conflicting token formats.
10. **Rewrite legal-doc-scaffold** with per-document clause references (ToS, Privacy Policy with a state-law matrix, SOW with Cure positions, NDA, DPA). Remove `disable-model-invocation` and the "DESTRUCTIVE" and quadruple-caps disclaimer. Fix the COPPA and health-data rows.

Honourable mentions: portfolio-registry (split under 500 lines, fix the unclosed fences at L235/L246, make the project-root file canonical); dora-metrics (update the DORA clusters and pull the definitions back into the body); ci-cd-pipeline (WIF instead of JSON keys, Node 22/24).
