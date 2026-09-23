# Engineering skills review — Wave 5 rubric (2026-09-23)

Scope: all 40 `skills/engineering/*/SKILL.md`, plus sibling reference files skimmed (headings plus targeted greps).
S1 Signal density · S2 Instruction style · S3 Trigger · S4 Currency/correctness · S5 Portability · S6 Progressive disclosure. I checked every line number below against the file.

## Scorecard

| skill | S1 | S2 | S3 | S4 | S5 | S6 | /30 | verdict |
|---|---|---|---|---|---|---|---|---|
| agent-designer | 3 | 3 | 4 | 2 | 3 | 3 | 18 | TIGHTEN |
| agent-workflow-designer | 2 | 3 | 3 | 3 | 3 | 3 | 17 | MERGE-INTO:agent-designer |
| ai-feature-builder | 2 | 2 | 2 | 2 | 3 | 3 | 14 | REWRITE |
| analytics-implementation | 3 | 3 | 3 | 3 | 3 | 4 | 19 | TIGHTEN |
| android-design-expert | 2 | 3 | 3 | 2 | 3 | 3 | 16 | TIGHTEN |
| android-feature-scaffold | 3 | 3 | 4 | 3 | 3 | 4 | 20 | TIGHTEN |
| api-architect | 2 | 3 | 4 | 2 | 3 | 4 | 18 | TIGHTEN |
| api-gateway | 2 | 3 | 3 | 3 | 3 | 2 | 16 | TIGHTEN |
| client-communication | 2 | 3 | 3 | 4 | 2 | 2 | 16 | TIGHTEN (move to business/) |
| client-handoff | 3 | 3 | 4 | 3 | 2 | 2 | 17 | TIGHTEN |
| cure-infra-bootstrap | 4 | 3 | 3 | 2 | 2 | 4 | 18 | TIGHTEN |
| data-migration | 2 | 3 | 4 | 2 | 3 | 2 | 16 | TIGHTEN |
| database-architect | 3 | 3 | 3 | 2 | 3 | 3 | 17 | TIGHTEN |
| e2e-testing | 3 | 2 | 4 | 2 | 3 | 4 | 18 | TIGHTEN |
| env-secrets-manager | 4 | 4 | 4 | 4 | 4 | 3 | 23 | KEEP |
| firebase-architect | 3 | 3 | 4 | 2 | 3 | 4 | 19 | TIGHTEN |
| git-worktree-manager | 4 | 4 | 3 | 2 | 2 | 3 | 18 | TIGHTEN |
| i18n | 3 | 3 | 3 | 2 | 3 | 3 | 17 | TIGHTEN |
| interview-system-designer | 4 | 3 | 4 | 3 | 3 | 4 | 21 | TIGHTEN (move to business/) |
| ios-architect | 3 | 3 | 4 | 2 | 3 | 4 | 19 | TIGHTEN |
| ios-design-expert | 2 | 3 | 3 | 1 | 3 | 3 | 15 | REWRITE |
| llmops | 2 | 3 | 3 | 1 | 3 | 2 | 14 | REWRITE |
| mcp-server-builder | 4 | 4 | 4 | 2 | 2 | 4 | 20 | TIGHTEN |
| micro-frontends | 2 | 3 | 2 | 1 | 3 | 3 | 14 | REWRITE |
| monorepo-navigator | 4 | 4 | 3 | 3 | 3 | 4 | 21 | KEEP (small fixes) |
| nextjs-feature-scaffold | 3 | 3 | 4 | 2 | 3 | 4 | 19 | TIGHTEN |
| notification-architect | 3 | 3 | 3 | 2 | 3 | 2 | 16 | TIGHTEN |
| offline-first | 3 | 3 | 3 | 2 | 3 | 2 | 16 | TIGHTEN |
| parallel-agent-orchestration | 5 | 4 | 4 | 3 | 3 | 5 | 24 | KEEP |
| performance-review | 3 | 3 | 3 | 2 | 2 | 3 | 16 | TIGHTEN |
| project-bootstrap | 3 | 3 | 2 | 3 | 3 | 2 | 16 | MERGE-INTO:cure-infra-bootstrap |
| project-manager | 2 | 3 | 3 | 3 | 3 | 4 | 18 | TIGHTEN (move to product/) |
| rag-architect | 4 | 4 | 4 | 3 | 3 | 4 | 22 | KEEP |
| sdlc | 2 | 2 | 3 | 3 | 2 | 4 | 16 | TIGHTEN |
| self-improving-memory | 4 | 4 | 4 | 2 | 2 | 4 | 20 | TIGHTEN |
| stitch-design | 3 | 2 | 1 | 2 | 2 | 4 | 14 | REWRITE |
| stripe-integration | 3 | 3 | 3 | 2 | 3 | 4 | 18 | TIGHTEN |
| test-accounts | 4 | 3 | 4 | 2 | 3 | 2 | 18 | TIGHTEN |
| testing-strategy | 3 | 3 | 3 | 3 | 3 | 4 | 19 | TIGHTEN |
| web-design-expert | 2 | 3 | 2 | 2 | 3 | 4 | 16 | TIGHTEN |

**Distribution:** mean 17.7/30. 14–16: 15 skills · 17–19: 17 · 20–22: 6 · 23–24: 2. Lowest dimension: S4 currency (mean 2.4, with 21 skills at ≤2).
**Verdicts:** KEEP 4 · TIGHTEN 29 · REWRITE 5 · MERGE 2 · DEPRECATE 0.

---

## Per-skill findings

### agent-designer (18)
- The same decision matrix appears twice in one file: L42–54 and again at L269–286. Keep one.
- The model tier table (L222–225) names GPT-4o-mini, GPT-4o and o1, which are superseded. Replace it with tier descriptions (small/mid/frontier) plus "check current lineup". L322 still points to docs.anthropic.com.
- "Code Generation (Required)" (L309–318) always writes 6 TypeScript files under `src/agent/`, whatever the stack and even when the user asked only for a design doc. Make it conditional and stack-aware.
- The auto-context block (L18–21) injects package.json and Podfile, which say little about agent design. Keep only the grep at L26.

### agent-workflow-designer (17): merge into agent-designer
- The workflow patterns restate Anthropic's "Building Effective Agents", which frontier models already know. The TS pseudocode (L106–224) is textbook.
- The pattern table is internally wrong: L32 says "There are six shapes" but lists 7 rows (L36–42). L309 says "confirm none of the Step 6 anti-patterns", but the anti-patterns sit in an unnumbered section and Step 6 is "Choosing Between Agent and Workflow".
- It covers the same ground as agent-designer's agent-vs-workflow matrix, which appears twice there. Fold the decision tree (L59–85) and the anti-pattern table (L281–291) into agent-designer as one section.
- Trigger is 357 chars, over the 350 budget.

### ai-feature-builder (14): rewrite
- Almost all of it is generic: temperature ranges, "use JSON", retry with backoff (L93–196). Its RAG content (L71–81, L143–159) duplicates rag-architect, and the guardrails and cost content duplicates llmops.
- It generates the same files as llmops: `src/llm/guardrails.ts` and `src/llm/cost-tracker.ts` (L32–33 here, llmops L428–429). Two skills write one path.
- Stale models: "GPT-4 fails → try Gemini" (L172) and `text-embedding-3-small` (L150). The temperature advice (L99) ignores reasoning-model and extended-thinking constraints.
- Instruction style: "You MUST" (L28), "Non-Negotiable" (L102), and the Code Generation block comes before Step 1 (L26).
- The trigger (L4) routes to "medical-ai when available", which does not exist, and never excludes rag-architect or agent-designer.
- Fix: cut it to a router plus the Cure-specific pieces (kill switch through remote config L208, responsible-AI checklist), and point to rag-architect, llmops and agent-designer.

### analytics-implementation (19)
- The consent section (L175–192) predates Google Consent Mode v2, which the EEA has required since 2024. It uses the old CCPA "Do Not Sell" wording instead of CPRA's "Sell or Share". `Analytics.setAnalyticsCollectionEnabled` (L191) is the iOS API only.
- The funnels and dashboards (L108–130, L211–227) are generic, and "Code Generation (Required)" (L203) sits between Steps 7 and 8.
- The trigger does not name ab-test-analyst or growth-engineering, which overlap on A/B test setup (L31).

### android-design-expert (16)
- The body is a pointer, and Step 3 "(Always Apply)" (L52–54) lives in an on-demand file. The reference contradicts itself: "13 tones per hue" followed by a list of 16 tones, and "5 key colors" followed by 6 (reference/details.md L21–31).
- Currency: no M3 Expressive, no edge-to-edge (enforced at targetSdk 35), no Large/XL width classes (the reference shows only 3, L143–156), and it uses the deprecated `windowWidthSizeClass` API. Predictive back is described as API 34+ (L116).
- "Code Generation (Required)" (L100–110) writes Theme.kt, Color.kt and friends even when the request is design guidance.
- `paths: "*.kt,*.kts"` (L6) auto-attaches the skill on every Kotlin edit, which adds noise.

### android-feature-scaffold (20)
- Two file layouts contradict each other. The tree (L14–30) has `data/dto` mappers and separate `UiState`/`UiEvent`/`UiAction` files. Code Generation (L135–139) uses `data/mapper/`, `presentation/{feature}/…Contract.kt`, and separate `test/`.
- Rule 3 (L89), "every suspend call wrapped in `runCatching`", is a real bug source: it swallows `CancellationException`. Prescribe a cancellation-safe wrapper.
- `NavigateTo(val route: String)` (L73) is stringly typed. Navigation 2.8+ type-safe routes are the current default, and it never mentions `collectAsStateWithLifecycle`.
- It never references `rules/android.md`, which carries the same standards.

### api-architect (18)
- It is mostly textbook REST (L44–118).
- The error envelope (L94–103, L201–218) ignores RFC 9457 Problem Details. The rate-limit headers (L148–151) use legacy `X-RateLimit-*` instead of the IETF `RateLimit`/`RateLimit-Policy` fields. The versioning section (L168) conflates `Sunset` with the `Deprecation` header (RFC 9745).
- It contradicts itself: OpenAPI 3.0.3 at L173–176 versus 3.1 at L194. Query params are snake_case (`per_page`, `created_after`, L108/L114) while the JSON is camelCase (`perPage`, `createdAt`, L80/L88).
- `admin.auth().verifyIdToken` (L125) is the namespaced API, where api-gateway (L200) uses the modular one. Its rate-limit defaults (20/min anonymous) conflict with api-gateway's (10/min, L205).

### api-gateway (16)
- 381 lines, all inline. The monitoring section (L299–363) duplicates observability and performance-review.
- Questionable advice: return "2 hours ago" display strings from the BFF (L128), which breaks caching and i18n, and "Android: return dimension values in dp" (L132).
- The "API versioning" row (L31) overlaps api-architect, and the rate-limit numbers differ between the two skills.
- The example timestamp is from 2024 (L306), and the Cloud Run cold-start figure "~200ms" (L97) is unsupported.

### client-communication (16)
- This is a business/PM skill filed under engineering, and it overlaps project-manager's risk register and status report (project-manager L40–41, L146–150).
- The auto-context (L16–19) injects package.json and Podfile into a status-email task. That is irrelevant context in every runtime.
- Progressive disclosure is inverted: the core weekly status template was moved to reference/details.md (L143–145) while demo checklists and meeting-agenda boilerplate stay inline. 479 lines.
- "Artifact Generation (Required)" (L434–440) writes 4 files even when the user wants one email.
- The trigger has no NOT clause (it overlaps project-manager and client-handoff).

### client-handoff (17)
- 496 lines, right at the 500 cap. The runbook, arguably the most operational artifact, is pushed out to the reference while static tables stay inline.
- It relies on Claude-only mechanisms: "using runbook output style" (L47) and `context: fork`. Neither exists in Codex or Antigravity.
- Currency: the APNs row "Apple Push Cert (APNs) [DATE]" (L191) should recommend the non-expiring .p8 key, which notification-architect L186 does. It hardcodes vendor prices (SendGrid "\$90/mo" L171).
- "Artifact Generation (Required)" comes before Step 2 Gather Context (L42 vs L51).

### cure-infra-bootstrap (18)
- The READ-ONLY banner (L12–17) contradicts the skill's purpose: `init` and `apply` write CLAUDE.md, `.claude/` and the manifest (L29–33). The banner also says read-only is "enforced by `allowed-tools`/`disallowed-tools`", but no `disallowed-tools` is set and `allowed-tools` restricts nothing (repo CLAUDE.md says so explicitly).
- Stale: `--skills-version 5.0.0` (L77); the library is at 7.9.0.
- The skills-repo discovery paths (L50–52) don't include the actual checkout location (`/Volumes/CureVault/projects/...`). The "once published to GitHub Packages" note (L98) needs a status check.
- It overlaps project-bootstrap: both "bootstrap CLAUDE.md + STATE.md". The L4 claim "bootstrap is the only supported path" conflicts with project-bootstrap existing at all.

### data-migration (16)
- 498 lines. The generic migration strategies (big bang, CDC, blue-green, strangler; L56–147) are textbook. The Firestore section, the only Cure-specific part, is the part pushed to the reference (L400–402).
- The Firestore CDC sample uses v1 `functions.firestore.document().onWrite` (L393–397), against Cure's Functions v2 standard. It should be `onDocumentWritten`.
- "Batch read: getAll() with pagination (500 docs per batch)" (L157) conflates getAll with pagination. The 500-op batch framing (L201) should point to BulkWriter for bulk loads.
- Deterministic IDs that include the migration version (L211) break idempotency across re-versioned runs.

### database-architect (17)
- Factual error: Firestore "500 writes/sec per document" (L68). The sustained limit is about 1 write/sec per document; 500/50/5 is the ramp rule for collections. "Limited aggregation" is also dated now that count/sum/avg exist.
- Stale defaults (L297–310): Firebase BOM 33.x, PostgreSQL 16, Room 2.6.x, Flyway 10.x. The rollback template (L263) uses `V{NNN}__rollback`, but Flyway undo files are `U{NNN}__`.
- It overlaps data-migration (dual-write, expand-contract; L129–139), firebase-architect (Firestore modeling; L94–100) and offline-first (Room/SwiftData).

### e2e-testing (18)
- Shouting and rigidity: "Page Object Model is mandatory… No exceptions" (L10, L49–51). "Assertions live in the page object" (L57) contradicts Playwright's own guidance.
- Currency: `waitForLoadState('networkidle')` (L125) is discouraged by Playwright. It lists FID (L31), which was retired in March 2024 in favour of INP. The reference CI config pins Node 20 (ci-and-quality.md L100), which went EOL in April 2026.
- Inconsistent paths: the structure is `e2e/pages/` (L67) but Code Generation writes `tests/pages/` (L399). It mentions Maestro (L398), which appears nowhere in the reference.
- It contradicts testing-strategy: the reference uses "Retries: 1 in CI" (ci-and-quality.md L138), while testing-strategy L222 says "Never retry flaky tests in CI."

### env-secrets-manager (23): keep
- Minor: `.env.example` naming is inconsistent (`DB_HOST…` at L71 versus `DB_URL` at L86), and it says `STRIPE_PUBLIC_KEY` where Stripe's term is "publishable".
- 295 lines inline. The audit-report template (L220–265) could move to a sibling file. The guardrail prose for non-Claude runtimes (L13–18) is present.

### firebase-architect (19)
- Stale defaults (L112–115): `firebase-bom:33.x` and "ktx" (KTX modules were removed from BoM 34), and Node 20.
- It says "Cloud Functions v2" (L4, L115) but generates "onCreate/onUpdate/onDelete handlers" (L101), which are v1 names. v2 uses `onDocumentCreated` and friends. `FieldValue.serverTimestamp()` (L79) is the namespaced form.
- It is thin on the non-obvious parts: no security-rules patterns beyond "deny-by-default" (L96), and no App Check or named-database guidance.
- The output contract (L84–90, TS + Kotlin) differs from Code Generation (L94–103, which adds Swift, storage rules and firebase.json).

### git-worktree-manager (18)
- Bug: "Create worktree on a PR" runs `gh pr checkout 1234 --branch pr-1234` (L88) first. That switches the *current* checkout, which defeats the purpose. Use `git fetch origin pull/1234/head:pr-1234`.
- Bug: the port helper derives its index from `git worktree list | grep -n "$(pwd)"` (L150). That prefix-matches (`acme` matches `acme-feature-…`), and ports shift whenever a worktree is removed.
- Escaped dollars inside scripts (`WORKTREE_DIR="\$1"` L175, `awk '{print \$2}'` L240/248/302/313, `local name="\$1"` L287) render literally in Codex and Antigravity, which produces broken scripts. Put scripts in a sibling `scripts/` file instead.
- Broken cross-reference: `/git-workflow` (L204, L342) does not exist. The trigger is 463 chars, the largest in the slice.

### i18n (17)
- Android `<item quantity="zero">` (L121) is ignored for English; zero is only used by locales with a grammatical zero. It is presented as working.
- Contradictory web stack: next-intl 3.x plus `messages/` (L88, L377), but Code Generation writes `locales/en.json` with "i18next or react-intl" (L394–395). next-intl v4 and Next 16 `proxy.ts` replace `middleware.ts` (L91, L194).
- `dir="auto"` on `<html>` (L231) is wrong; set `dir="rtl"` per locale. `Locale("es","MX")` (L173) is deprecated since JDK 19.
- 407 lines inline. The pseudolocale content appears twice (L245–250 and L314–319).

### interview-system-designer (21)
- Wrong cross-references: `/performance-review` is offered for "performance management of existing employees" (L235, L269), but it is the *system performance* skill. `/technical-program-manager` (L272) does not exist, and `/qa-engineer` (L268) is an agent, not a skill.
- Currency gap: no policy on AI assistants in coding rounds, the main loop-design question in 2025–26.
- An HR skill filed in engineering. The package.json/Podfile injection is mostly irrelevant; the "match the stack" note at L26 is its only use.

### ios-architect (19)
- Stale: "Swift 5.10+" (L158) and "iOS 17+ recommended" (L73). Nothing on Swift 6 strict concurrency, Swift 6.2 default MainActor isolation, or Observation-based DI.
- "Cancel [Task] in `deinit`" (L91) is a Swift 6 isolation gotcha on `@MainActor` view models. Prefer `.task {}`, which auto-cancels.
- Inconsistent naming: the tree (L30–35, L42) has `…Repository.swift` as a protocol, `…RepositoryImpl.swift` and `…Module.swift`. Code Generation (L140–143) uses `…RepositoryProtocol.swift`, `Data/…Repository.swift` and `…Assembly.swift`.
- It lists StoreKit 2 and TCA as request types (L63, L65) but gives no guidance for either.

### ios-design-expert (15): rewrite
- Missing iOS 26 Liquid Glass and the new tab-bar and toolbar behaviour: `grep -i liquid|glass` over SKILL and reference returns nothing. Fixed dimensions like the "Tab bar: 49pt" (reference L29) and "Tab bar ALWAYS visible" (reference L233) are now wrong. The anti-pattern "Hiding the tab bar during non-fullscreen flows" (L116) conflicts with minimize-on-scroll.
- Its "Always Apply" foundations live in the on-demand reference (L53–55).
- Code Generation writes a design system (L100–110) for guidance requests, and `paths: "*.swift"` (L6) attaches it on every Swift edit.

### llmops (14): rewrite
- Stale tiers and prices (L59–75): GPT-4o-mini, GPT-4o, o1 and Gemini Ultra, with Haiku at "\$0.25/M" and Opus at "\$15/\$75", which are two generations old. The reference pins `claude-sonnet-4-20250514` as the judge (reference L219) and falls back to GPT-4o (L498).
- The biggest cost levers are absent: no prompt caching and no Batch API. `grep` finds neither in the SKILL or the reference.
- Router bug: the comment says Tier 3 but the code returns `tier: 2` (L99–101).
- The RAG monitoring (L219–329) duplicates rag-architect (chunk sizes 500–1000 here versus 512–1024 there), and the guardrails and cost files duplicate ai-feature-builder.
- The core Steps 3, 4 and 6 are pushed to a reference that is itself 520 lines, over the cap, while a generic code-heavy Step 5 stays inline.

### mcp-server-builder (20)
- Outdated SDK patterns: the low-level `Server` with `list_tools`/`call_tool` (L148–206) instead of `FastMCP` (Python) and `McpServer.registerTool` (TS), with `mcp>=1.0.0` and `^1.0.0` pins.
- Protocol drift: it invents a `confirm: const true` argument (L97, L277) and ignores the spec's tool annotations (`destructiveHint`, `readOnlyHint`), elicitation, `outputSchema`/`structuredContent`, and OAuth 2.1 authorization.
- Correctness: "Error: throw McpError" (L107–111). The spec says tool-execution failures should come back as a result with `isError: true` so the model can self-correct. JSON-RPC errors are for protocol faults.
- The test loop is Claude-only (`claude mcp list`, `claude --debug`; L241–245) and has no Codex `config.toml` or Antigravity equivalent.

### micro-frontends (14): rewrite
- Stale: React 18, Next 14.2 and Tailwind 3.4 pins (L68–69, L183, L199–203); `@module-federation/nextjs-mf` (L56), whose support for Next.js ended; `.eslintrc.js` (L233); Node 20 (L265).
- It says "opinionated toward Vercel" (L10) but omits Vercel's native microfrontends and multi-zones.
- Self-contradictory: it recommends a plain monorepo for "80% of teams" (L132), yet Code Generation always emits a module-federation app template (L343). It uses `npm ci` (L268) while generating `pnpm-workspace.yaml` (L340).
- The monorepo half overlaps monorepo-navigator, and the trigger has no NOT clause. Keep only the runtime-composition decision and move monorepo content to monorepo-navigator.

### monorepo-navigator (21): keep, small fixes
- `enforceBuildableLibDependency` is not an `nx.json` key (L96); it is an option of `@nx/enforce-module-boundaries`.
- Vercel Remote Cache is "free for OSS, paid for teams" (L118): outdated, since Remote Cache has been free on all Vercel plans since late 2024. "Lerna is on life support" (L43) is also dated; Nx maintains it.
- Lint inputs use `.eslintrc*` (L141); flat config is `eslint.config.*`. Trigger is 372 chars.

### nextjs-feature-scaffold (19)
- Two directory layouts contradict: Step 3 uses `src/lib/[feature]/actions.ts`, `src/components/[feature]/` and `src/__tests__/` (L59–74). Code Generation uses `src/app/{feature}/actions.ts`, `…/components/` and `…/__tests__/` (L212–217).
- Next 15/16 currency: `params` is a Promise (L159 destructures it synchronously). "Middleware + layout guard" (L31) should be Next 16 `proxy.ts`, and auth must not rely on middleware alone after CVE-2025-29927. No Cache Components or `'use cache'`. `revalidatePath('/[lang]/[feature]')` (L133) needs the `'page'` type argument.
- Zod `.flatten()` (L130) is deprecated in Zod 4, and `tailwind.config.ts` (L220) reflects the Tailwind v3 model.

### notification-architect (16)
- Missing Android 13+ `POST_NOTIFICATIONS` runtime permission and the Gmail/Yahoo 2024 bulk-sender rules (RFC 8058 one-click unsubscribe).
- Factual issues: "Max 2000 topics per app" (L211); the 2000 limit is per app instance. Data-only messages "handled… even when app is killed" (L224) is false for force-stopped apps. The open-rate target (L365) ignores Apple Mail Privacy Protection inflation.
- The FCM payload uses the legacy `click_action` (L111). Recommending a "dedicated IP" for transactional mail by default (L335) is bad advice at low volume.
- 457 lines, no siblings. The trigger has no NOT clause (it overlaps growth-engineering and customer-onboarding).

### offline-first (16)
- Deprecated Firebase APIs: `enableIndexedDbPersistence` (L138, L465) and `isPersistenceEnabled` (L136) should be `persistentLocalCache` and `PersistentCacheSettings`. "No cold cache queries without prior listener" (L139) is wrong; `getDocsFromCache` exists.
- The Background Sync API is presented as general (L327) but is Chromium-only. Stale versions: Room 2.6, WorkManager 2.9, Coil 2.x (L448–452).
- 494 lines, no siblings. The platform code samples should move to a reference file. It overlaps database-architect's Room/SwiftData guidance.

### parallel-agent-orchestration (24): keep
- References `AUTOMATION.md` (L68, L90) with no path. That file lives in the plugin repo's docs/ and is absent in consuming projects.
- `isolation: worktree` (L38) is Claude-specific; add a neutral "one worktree per subagent" phrasing.

### performance-review (16)
- Lists FID (L76) next to INP, though FID was retired in March 2024. TTI (L81) was dropped from Lighthouse 10. "dylib < 6 frameworks" (L135) is outdated.
- The auto-baseline runs `npx next build` (L30): slow, it writes `.next/`, and it contradicts the "read-only run" in its own Recurring Mode (L446).
- Claude-only steps: "Web Search" (L41), `/loop 4w` (L443), and "docs/AUTOMATION.md in the plugin repo" (L444).
- The name collides with employee performance reviews (interview-system-designer already mis-routes to it). The optimization strategies, the actionable part, are in the reference while generic budget tables stay inline.

### project-bootstrap (16): merge into cure-infra-bootstrap
- Duplicate purpose: both skills generate CLAUDE.md and STATE.md, and cure-infra-bootstrap claims to be "the only supported path". There is also a project-bootstrapper agent.
- The generated CLAUDE.md template (L97–315) runs about 220 lines, against current guidance to keep CLAUDE.md short. It belongs in a sibling template file, while the short interview was pushed out instead.
- Broken markdown: a nested ``` block (L354–364) inside the ```markdown fence (L323) closes the fence early.
- The AI cost-guardrail condition lists "Gemini / Vertex / OpenAI" (L87, L265) and omits Anthropic, though inspection detects it (L49).

### project-manager (18)
- Generic scrum content (L23–150), misfiled (PM, not engineering), and it overlaps client-communication's status and risk material.
- Velocity from `git log | grep -c "feat:"` (L154–157) is not velocity. "Use Grep on git log" (L168) confuses the Grep tool with shell grep.
- The classify table promises Gantt, kickoff, launch readiness and post-mortem (L38–45) with no guidance for any of them. "Artifact Generation (Required)" always writes 5 files (L159–166).

### rag-architect (22): keep
- Dated defaults: `text-embedding-3-small` as the default (L81, L90), voyage-3, Cohere Rerank v3 and embed-v3 (L83–84, L132). Date the table or phrase it as selection criteria.
- Claude/plugin-only references: "`monitoring-alert` output style" (L227), `rules/firebase.md` and `rules/python.md` (L108, L181).
- Code Generation forces Python (`src/rag/*.py`, L280–286), while the sibling AI skills force TypeScript. Make it stack-aware.

### sdlc (16)
- Step 3 "Generate Artifacts" is empty (L67–69). There are no PRD, ADR or RFC templates; the ADR relies on the "architecture-decision output style" (L139), which doesn't exist in Codex or Antigravity.
- Contradiction: "small requests inline" (L128) versus "You MUST generate actual documents using Write" (L135).
- Overlaps product-manager and prd on PRDs. Trigger is 356 chars. The DoD's ≥80% coverage (L107) disagrees with testing-strategy's 70% platform minimums.

### self-improving-memory (20)
- Factual error about the harness: it looks for `MEMORY.md` at repo root and `.claude/memory/` (L16–17, L40). Claude Code auto-memory lives in `~/.claude/projects/<project>/memory/MEMORY.md`, as this session's own memory path shows.
- No fallback for Codex (AGENTS.md) or Antigravity (GEMINI.md), even though the description frames it as Claude-only.

### stitch-design (14): rewrite
- Invalid frontmatter: L6–7 (`  tools: [stitch-mcp]` / `  env: [...]`) are indented keys with no parent. `yaml.safe_load` fails ("while parsing a block mapping"). The skill may not load, or may load with a mangled `argument-hint`, and audit-library.py did not catch it.
- Over-triggering: "Be aggressive — design intent triggers this skill even without explicit 'Stitch' mentions" (L80), plus a 12-row trigger table (L63–78). This collides with design-studio, product-design and the android, ios and web design experts. It needs an explicit NOT clause.
- Client-specific design systems (Vendly, The Initiated, Autograph; L309–322 and `assets/DESIGN.md.*`) ship to every consuming project, which is a confidentiality concern.
- Supply chain: it depends on the individual-scoped npm package `@_davideast/stitch-mcp` (L34, L50), run through unpinned `npx`. The `workflows/*.yaml` files use Claude tool names (`tool: Read`) and are not consumed by any harness.

### stripe-integration (18)
- Correctness: the Firestore shape uses subscription-level `currentPeriodStart/End` (L121–122). From API version 2025-03-31.basil, those fields moved to subscription items. The `stripe@14.x` pin (L164) is several majors behind.
- Webhook event lists disagree: `invoice.payment_succeeded` (L104) versus `invoice.paid` (L145). It never mentions the raw-body requirement for signature verification in Cloud Functions (`req.rawBody`), the #1 gotcha.
- "CardElement" (L64) is legacy on Android. The architecture diagram is Android-only (L26), yet it generates iOS too (L155). The trigger routes to a nonexistent "stripe-connect when available" (L4).

### test-accounts (18)
- Contradiction: L77–89 says do NOT standardize on plus-addressing, yet every persona uses `test+…@{domain}.com` (L140–147), and so do the reset prefix `'test+'` (L385), the E2E emails (L445) and the Apple sandbox (L176).
- 503 lines, over the 500 cap.
- "Test Clocks: max 3 active per account" (L486) is wrong; the limit is 3 customers per test clock. The fixed password pattern `TestPass123!{persona}` (L152) is guessable for staging accounts. `listUsers(1000)` (L388) only reads the first page.
- The "no scheduled reaper" org policy (L124) is good Cure-specific content; keep it.

### testing-strategy (19)
- Coverage thresholds disagree: platform minimums are 70% on business logic (L72, L89, L101), while Coverage Rules say ≥80% (L187–188).
- "Never retry flaky tests in CI" (L222) contradicts e2e-testing's 1 retry in CI.
- The framework-detection grep `describe|it|test|expect` (L32) matches nearly any file. The trigger is 435 chars, over budget.

### web-design-expert (16)
- Tailwind v3 model throughout: `tailwind.config.ts` (L112, L118) and reference `darkMode: 'class'` (reference L224). Tailwind v4's CSS-first `@theme` shipped in January 2025.
- `paths: "*.ts,*.tsx,*.css,*.html"` (L6) attaches the skill on essentially every web edit. It overlaps design-studio, design-system, product-design and stitch-design, and its only NOT clause names nextjs-feature-scaffold.
- The body is a stub pointing to a 573-line reference, which exceeds the 500-line guidance. "cva or class-variance-authority" (L114) names the same library twice.

---

## Cross-cutting patterns (≥3 skills)

| # | Pattern | Count | Examples |
|---|---|---|---|
| 1 | The same boilerplate auto-context (PORTFOLIO + package.json/Gradle/Podfile head + git log + ls), whatever the domain. Irrelevant for comms, HR, PM and doc skills, and re-run on every invocation. | 36/40 | client-communication, interview-system-designer, project-manager, sdlc, self-improving-memory (has its own) |
| 2 | "Code/Artifact Generation (Required)" writes N files unconditionally, often TypeScript regardless of stack and often placed before Gather Context. | 29/40 (8 add "You MUST") | ai-feature-builder L26, client-handoff L42, test-accounts L31 |
| 3 | Stale versions, models, APIs or prices | 21 skills scored S4 ≤2 | LLM tiers in 3 skills (agent-designer, llmops, ai-feature-builder); Firebase BoM 33/KTX or Node 20 in 5; FID in 2; Tailwind v3 in 3 |
| 4 | Two file layouts or two thresholds inside the same skill | 9 | android-feature-scaffold, ios-architect, nextjs, e2e, i18n, api-architect, stripe, test-accounts, testing-strategy |
| 5 | Mechanical "Step N" split into `reference/details.md`, with no guidance on when to read it. Often the most Cure-specific or most-used step is moved out while generic material stays inline, and "(Always Apply)" steps live in on-demand files. | 12/14 skills with siblings | data-migration, llmops, performance-review, client-communication, android/ios/web design |
| 6 | Near or over the 500-line cap, or long with no siblings | 8 | test-accounts 503, data-migration 498, client-handoff 496, offline-first 494, client-communication 479, project-bootstrap 464, notification 457, llmops reference 520 |
| 7 | "When to use" and NOT clauses live only in `when_to_use`, which Antigravity ignores, so 0/40 descriptions carry the "when". 8 skills have no NOT clause at all. | 40 / 8 | micro-frontends, offline-first, notification, i18n, stitch, client-* |
| 8 | Trigger text over the 350-char budget | 6 | git-worktree 463, testing-strategy 435, monorepo 372, cure-infra 358, agent-workflow 357, sdlc 356 |
| 9 | Claude-only mechanisms without a neutral fallback: output styles, `rules/*.md`, AUTOMATION.md, `/loop`, `claude mcp`, `isolation: worktree`, Web Search | 10 | client-handoff, sdlc, rag-architect, performance-review, mcp-server-builder, parallel-agent-orchestration, git-worktree, monorepo |
| 10 | Broken or wrong cross-references (nonexistent skill, agent cited as a skill, wrong skill) | 6 | git-worktree `/git-workflow`; interview `/technical-program-manager`, `/qa-engineer`, `/performance-review`; ai-feature-builder medical-ai; stripe-integration stripe-connect |
| 11 | Overlapping clusters with duplicate or contradictory content | 5 clusters | AI (agent-designer, agent-workflow, ai-feature-builder, llmops, rag; duplicate generated files); bootstrap (project-bootstrap, cure-infra-bootstrap); monorepo (micro-frontends, monorepo-navigator); API (api-architect, api-gateway rate limits); testing (e2e retries vs testing-strategy) |
| 12 | Non-engineering skills filed in engineering/ | 4 | client-communication, client-handoff, interview-system-designer, project-manager |
| 13 | Unescaped-looking `\$` inside shell scripts, which breaks copy-paste outside Claude Code | 1 hard break (git-worktree, 7 occurrences); cosmetic `\$` in prices in 4 more | agent-designer, llmops, client-handoff, rag-architect |

---

## Top 10 highest-leverage fixes (engineering slice)

1. **Fix stitch-design's frontmatter.** L6–7 is invalid YAML. Remove the "Be aggressive" trigger (L80) and add a NOT clause. Move the client DESIGN.md seeds (Vendly, The Initiated, Autograph) out of the distributed plugin. Add a `yaml.safe_load` check to `scripts/audit-library.py`, which missed this.
2. **Delete or specialise the shared auto-context block in 36 skills.** Keep domain greps (as env-secrets-manager, monorepo and sdlc do) and drop the package.json/Podfile head where it is irrelevant. This is the largest per-invocation token cut and removes `!`-injection dependence for Antigravity.
3. **Make "Code Generation (Required)" conditional in 29 skills.** Offer files, detect the stack, and write only on request. Reconcile the duplicate layouts in android-feature-scaffold, ios-architect, nextjs-feature-scaffold, e2e-testing and i18n.
4. **Consolidate the AI cluster.** Merge agent-workflow-designer into agent-designer, and reduce ai-feature-builder to a router plus Cure specifics. Make llmops own guardrails and cost, and rag-architect own RAG. This ends the duplicate `src/llm/guardrails.ts` and `cost-tracker.ts` outputs.
5. **Replace hard-coded model and price tables** in llmops, agent-designer, ai-feature-builder and rag-architect with dated, tiered guidance. Add prompt caching and the Batch API to llmops, and fix its router bug (L99–101).
6. **Merge project-bootstrap into cure-infra-bootstrap.** Correct the false READ-ONLY and `allowed-tools` enforcement banner (L12–17), bump `--skills-version` from 5.0.0, and move the ~220-line CLAUDE.md template into a template file.
7. **Run a platform currency sweep.** ios-design-expert needs iOS 26 Liquid Glass (rewrite). ios-architect needs Swift 6.x. android-design-expert needs M3 Expressive, edge-to-edge and new width classes. firebase-architect and data-migration need BoM 34 without KTX, Functions v2 triggers and Node 22. offline-first needs the `persistentLocalCache` API. nextjs, web-design-expert and micro-frontends need Next 16 `proxy.ts`, async `params`, Tailwind v4 and React 19. performance-review and e2e-testing need FID replaced by INP.
8. **Fix correctness bugs.** stripe-integration: `current_period_*` moved to items in basil, plus the missing webhook rawBody gotcha. database-architect: the "500 writes/sec per document" claim. mcp-server-builder: tool errors should use `isError`, and it should use tool annotations. git-worktree-manager: `gh pr checkout` hijacks the main tree, and the port-index grep. self-improving-memory: the wrong auto-memory path. android-feature-scaffold: `runCatching` swallows cancellation.
9. **Resolve cross-skill and in-skill contradictions.** test-accounts: plus-addressing policy versus `test+` personas. testing-strategy: 70% versus 80% coverage, and no-retry versus e2e's 1 retry. api-architect: OpenAPI 3.0.3 versus 3.1, rate limits versus api-gateway. Adopt RFC 9457 errors and IETF RateLimit headers.
10. **Fix triggers and references for Antigravity.** Fold a short "Use when… NOT …" into `description` for all 40, since `when_to_use` is invisible to Antigravity. Add NOT clauses to the 8 skills without one, and trim the 6 over 350 chars. Fix the 6 broken cross-references. Move the 4 non-engineering skills to business/ or product/.
