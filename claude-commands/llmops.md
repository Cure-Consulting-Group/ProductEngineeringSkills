# LLMOps

**Outcome:** the operational layer for an existing or about-to-ship LLM feature — versioned prompts with an eval gate in CI, a cost model with the caching/batch/routing levers applied, budgets and alerts, and an AI incident runbook. Done when a prompt or model change cannot reach production without passing the eval, and spend per feature is visible and capped. Match length to the need; no filler sections or restated summaries.

**Ownership boundary.** This skill owns *operations*: evals, prompt lifecycle, model routing, caching, batching, budgets, cost tracking, monitoring, AI incidents. It does not create the LLM client wrapper, prompt templates, or input/output guardrail code — `ai-feature-builder` owns `src/llm/client.ts`, `src/llm/prompts/`, and `src/llm/guardrails.ts`; extend those, don't regenerate them. Retrieval metrics, index drift, and chunking belong to `rag-architect`.

## Pre-Processing (Auto-Context)

Context — run these read-only commands first; skip any that fail or aren't permitted (they only tailor the output):

- LLM SDKs in use: `grep -E '"(@anthropic-ai/sdk|openai|@google/genai|ai|langchain)"' package.json 2>/dev/null | head -8; grep -iE '^(anthropic|openai|google-genai|langchain)' requirements.txt pyproject.toml 2>/dev/null | head -5 || echo "(none detected)"`
- Existing LLM/eval code: `ls -d src/llm evals eval prompts 2>/dev/null || echo "(none)"`

## Step 1: Classify

| Need | Deliver |
|---|---|
| Productionize a new AI feature | Steps 3–7, plus Code/Artifact Generation |
| Eval pipeline for an existing feature | Step 3 (+ generation of eval files only) |
| "The LLM bill is too high" | Step 4 cost audit: ranked levers with estimated savings; no scaffolding unless asked |
| Model or prompt rollout / migration | Step 3 gate + Step 5 routing + rollback plan |
| Live AI incident | Step 7 runbook only — mitigate first, generate nothing until the feature is stable |

## Step 2: Gather Context

Ask only for what the SDK scan above doesn't answer: models and providers per task; monthly spend and tokens/request if known (or `usage` logs); latency budget per route (autocomplete <1s vs generation 5–30s); request volume; data-residency/PII/ZDR constraints; existing evals or golden sets.

## Step 3: Evals and Prompt Lifecycle

Cure rules:
- **Every prompt lives in git** with its config (model ID, effort/thinking settings, `max_tokens`, output schema) and a semver: major = behavior change, minor = quality change, patch = wording. No prompts that live only in a dashboard or env var.
- **Golden set per prompt**: ≥100 cases (≥200 for customer-facing or regulated), sampled to match production traffic, plus empty/very long/adversarial/injection cases. Every production failure becomes a new case.
- **Grading, cheapest first**: deterministic checks (schema, `mustContain`, exact label) → LLM judge with a rubric → human review. An LLM judge is calibrated against ≥50 human-labelled cases before its scores gate anything; re-calibrate when judge and humans disagree on >20%.
- **CI gate**: any PR touching `prompts/**`, model IDs, or routing config runs the eval for the affected prompts and fails if the score drops >3 points against the main-branch baseline or below the prompt's floor. Post the diff of scores to the PR.
- **Online signals** after release: thumbs-down rate, regenerate rate, edit distance on accepted output, abstention rate, format-violation rate. A prompt A/B assigns by stable user hash and logs the prompt version on every call.
- **Model migration** is a prompt change: re-run the full golden set on the new model, re-tune effort, and diff cost per completed task (not per request) before switching.

Read `reference/details.md` when you are generating the eval harness, golden-set format, judge rubric, or CI workflow — it has the file layouts and templates.

## Step 4: Cost — levers in order

Model prices change; quote from the provider's pricing page at the time of the estimate and date it. Anthropic reference (verified 2026-09-23, platform.claude.com/docs/en/about-claude/pricing), per million tokens:

| Model (ID) | Input | Output | Cache read | Batch in/out |
|---|---|---|---|---|
| Claude Haiku 4.5 (`claude-haiku-4-5`, snapshot `claude-haiku-4-5-20251001`) | \$1 | \$5 | \$0.10 | \$0.50 / \$2.50 |
| Claude Sonnet 5 (`claude-sonnet-5`) | \$2 | \$10 | \$0.20 | \$1 / \$5 |
| Claude Opus 5.5 (`claude-opus-5-5`) | \$4 | \$20 | \$0.20 (0.05×) | \$2 / \$10 |
| Claude Fable 5.1 (`claude-fable-5-1`) | \$10 | \$50 | \$0.25 (0.025×) | \$5 / \$25 |

Cache writes cost 1.25× input (5-minute TTL) or 2× (1-hour TTL); a 5-minute cache pays off after one read. Caching and Batch discounts stack. For other providers, look up the current price list; don't reuse remembered numbers.

Apply levers in this order — free wins before quality trade-offs:

1. **Prompt caching.** Put stable content first (tools → system → long documents → few-shot), volatile content (timestamps, user IDs, the question) last. Mark the stable prefix with `cache_control` (or top-level automatic caching). Verify with `usage.cache_read_input_tokens` > 0 on repeat requests — zero means a silent invalidator (a timestamp in the system prompt, unsorted JSON, a changing tool list). Prefixes below the model's minimum cacheable length don't cache. Target ≥70% of input tokens served from cache on chat and agent routes.
2. **Batch API** for anything not user-facing within seconds (nightly classification, backfills, eval runs, report generation): 50% off input and output, results within 24h, keyed by `custom_id` in any order. Eval runs in CI that don't block a human can batch too.
3. **Input hygiene**: trim retrieved context to what the eval shows is used, drop stale conversation turns (or use server-side compaction/context editing), cap tool-result size.
4. **Output hygiene**: structured outputs for machine-read results, explicit length guidance, realistic `max_tokens` per route.
5. **Effort** (Claude 4.6+ models): lower `output_config.effort` per route where the eval holds. Measure the most capable model at low/medium effort before building a multi-model cascade — one model keeps one cache namespace, and caches are model-scoped.
6. **Model routing** (Step 5) — last, because it trades quality and forfeits cache reuse across models.

Budgets: every feature gets a per-user daily token cap and a per-feature daily spend cap enforced before the call; over-budget requests degrade (smaller model or queued) rather than fail. Alerts: daily spend >120% of the 7-day average → channel notification; >200% → page on-call; single user >\$50/day → investigate abuse; cache-read share drops >20 points → investigate an invalidator; cost per completed task +50% → check routing and prompt size.

## Step 5: Model Routing

Route by task, with each route's model chosen by eval, not by tier folklore:

| Route | Default | Escalate when |
|---|---|---|
| Classification, extraction, formatting, short Q&A | Small tier (Haiku 4.5) | Eval accuracy below floor |
| Generation, summarization, RAG synthesis, most chat | Mid tier (Sonnet 5), effort low/medium | Eval fails on hard slice |
| Multi-step reasoning, code, agentic loops | Frontier (Opus 5.5) at medium/high effort | — |
| Most demanding long-horizon work | Fable 5.1 only when evals prove the gain justifies 2.5× Opus 5.5 | — |

Model-behavior gotchas that break old ops code (Anthropic, 2026): on Opus 5.5 and Fable 5.1 thinking cannot be disabled (control depth with effort), `temperature`/`top_p` are rejected on current Opus/Sonnet/Fable models, forced `tool_choice` is rejected on Opus 5.5/Fable 5.1, and assistant prefill is removed — so a "temperature 0 for determinism" cache-key or a prefill-based JSON trick must be replaced (structured outputs; key the exact cache on prompt + model + schema). Fallback chains: retry with backoff on 429/5xx/overload (the SDK retries twice by default), then fall to a secondary model whose eval passes, then to a cached or non-AI response. Never retry a safety refusal on a different model to get around it; handle `stop_reason: "refusal"` explicitly.

Application-level caches (distinct from prompt caching): exact-match cache for deterministic routes (classification, extraction) keyed on prompt version + model + normalized input, TTL ≤24h; semantic cache only for FAQ-style answers with a similarity threshold validated on the golden set; never cache personalized or user-specific responses.

## Step 6: Monitoring

Log per call: feature, prompt version, model ID, effort, input/cached/output tokens, cost, latency (TTFT and total), stop reason, guardrail verdicts, user/session hash. Dashboards: spend by feature and by model; cache-read share; cost per completed task; p50/p95 latency; refusal, error, and fallback rates; guardrail trigger rate; online quality signals from Step 3. Feed these into the project's monitoring stack (`observability` skill); retrieval-quality panels come from `rag-architect`.

## Step 7: AI Incident Runbook

| Incident | Detect | First action |
|---|---|---|
| Quality regression | Sampled judge score −10%, thumbs-down +15% | Pin the previous prompt/model version via config; re-run the golden set |
| Cost spike | Spend >200% of 7-day average | Enforce budgets, check for loops/abuse, check cache-read share |
| Safety/data leak | Guardrail hit on output, PII in output, successful injection | Kill switch the feature (remote config), preserve logs, involve security |
| Latency | p95 >2× baseline, timeouts | Check provider status, shed to cached/smaller-model route |
| Provider outage | Error rate >5% | Fallback chain; communicate degraded mode |

Mitigate before investigating. Afterwards, add the failing inputs to the golden set and follow the `incident-response` skill for the postmortem.

## Code/Artifact Generation

Applies when Step 1 is "productionize" or "eval pipeline" and the user wants files. Detect the stack first and match its language; extend existing files rather than duplicating them.

- `evals/<prompt>/golden.jsonl`, `evals/run-eval.(ts|py)`, and a CI workflow `.github/workflows/prompt-eval.yml` (eval pipeline)
- `prompts/<name>/` with versioned prompt files and `config.json` (only if prompts aren't already versioned — otherwise add config beside them)
- `src/llm/cost-tracker.*` (usage → cost logging from `usage` fields), `src/llm/budget.*`, `src/llm/router.*`

Don't create `src/llm/client.*` or `src/llm/guardrails.*`; if missing, point to `ai-feature-builder`. Related: `engineering-cost-model` for project-level LLM cost projections.
