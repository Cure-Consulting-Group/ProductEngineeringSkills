---
name: ai-feature-builder
description: "Builds user-facing LLM features: client wrapper, prompts, streaming UX, fallbacks, kill switch. Use when adding chat, summarization, extraction, or generation to an app."
when_to_use: "NOT for RAG (rag-architect), agent internals (agent-designer), pattern choice (agent-workflow-designer), or evals/cost/routing (llmops). PHI: pair with compliance-architect."
argument-hint: "[ai-feature-name]"
metadata:
  verified: 2026-09-23
---

# AI Feature Builder

**Outcome:** a shipped-quality AI feature in the product — typed LLM client, versioned prompts, streaming UI where it helps, a tested fallback path, a remote kill switch, and the responsible-AI checklist signed off. Done when the feature degrades gracefully with the model unavailable and can be turned off without a deploy.

This skill is the entry point and router for AI features. It owns the product-side wiring; the specialist skills own their domains:

| Need | Owner |
|------|-------|
| Single call vs workflow vs agent | `agent-workflow-designer` |
| Agent tools, memory, termination | `agent-designer` |
| Retrieval, chunking, embeddings, reranking | `rag-architect` |
| Cost tracking, budgets, routing, eval pipelines, prompt versioning in prod | `llmops` |
| PHI, HIPAA, BAAs | `compliance-architect` |

Deliver the requested feature. This skill owns `src/llm/client.ts`, `src/llm/prompts/`, and `src/llm/guardrails.ts`; cost tracking, budgets, and routing (`src/llm/cost-tracker.ts`, `budget.ts`, `router.ts`) belong to llmops — one owner per path.

## Pre-Processing (Auto-Context)

Context (pre-filled in Claude Code; in other runtimes run these commands first):

- Stack: !`ls package.json pyproject.toml requirements.txt build.gradle.kts Package.swift 2>/dev/null | head -5 || echo "(none detected)"`
- Existing LLM code: !`grep -rlE "@anthropic-ai|anthropic|openai|@google/genai|google.genai|vertexai|ai-sdk|from 'ai'" --include=*.ts --include=*.tsx --include=*.py --include=*.kt --include=*.swift --exclude-dir=node_modules --exclude-dir=.git . 2>/dev/null | head -8 || echo "(none)"`

Extend an existing client wrapper rather than adding a second one.

## Step 1: Classify the Feature

| Feature | Shape | Route elsewhere when… |
|---------|-------|----------------------|
| Chat / assistant | LLM + conversation state + streaming UI | it answers from your documents → `rag-architect` |
| Document processing | Parse → LLM extract → schema-validated output | — |
| Content generation | Prompt template + human review before publish | — |
| Classification / tagging | Single call, structured output, small tier | — |
| Voice | STT → LLM → TTS; latency budget per hop | — |
| Vision | Vision-capable model → structured extraction | — |
| Semantic search / Q&A over docs | — | always → `rag-architect` |
| Multi-step actions with tools | — | → `agent-workflow-designer`, then `agent-designer` |

## Step 2: Gather Context

Ask only what isn't known: what the user gets from the feature; provider (and whether a BAA/DPA is needed); latency tolerance (<2s, <10s, background); data sensitivity (PII, financial, health, minors); volume; cost ceiling; what the user sees when the model fails.

## Step 3: Cure Implementation Rules

**Prompts**
- User input goes in the user turn, never concatenated into the system prompt.
- Request structured output via the provider's native structured-output or strict-tool mode, and validate with a schema (Zod/Pydantic) anyway. Newer Claude models reject forced `tool_choice` (`any`/`tool`) — use `auto` + strict tools or structured outputs.
- Don't tune temperature by habit: newer Claude models (Opus 5 and later) reject sampling parameters and steer depth with `effort` instead (verified 2026-09-23, platform.claude.com/docs/en/models/opus-5-5/migration-guide). Check other providers' docs per model.
- Prompts are versioned files (`src/llm/prompts/{feature}.ts` or equivalent) with an ID logged on every call, so llmops can attribute regressions.

**Model choice** — describe the tier (small/mid/frontier), not a model name baked into code; read the model ID from config so it can change without a deploy. Check the provider's current lineup at build time (Anthropic: platform.claude.com/docs/en/models/overview).

**Streaming** — stream anything conversational or longer than ~2s. Show a typing indicator until the first token; render partial output if the stream breaks, with a retry affordance.

**Failure handling**

```
429           → exponential backoff (1s, 2s, 4s), max 3 retries, honor retry-after
5xx           → retry once, then fallback
timeout       → cancel at the latency budget, show fallback UI
schema fail   → one repair attempt, then fallback
Fallback order: same model retry → configured backup model/provider
                → cached or deterministic answer → graceful manual path
Never: crash, hang, or render raw model output or raw provider errors
```

A backup provider needs its own prompt tuning and eval run — a prompt tuned on one family is not a drop-in on another.

**Kill switch** — every AI feature sits behind a remote flag (Firebase Remote Config or LaunchDarkly; see `feature-flags`) that disables it without a redeploy and shows the manual path.

## Step 4: Testing

- Unit: prompt rendering, output parsing (valid, malformed, empty), fallback selection.
- Integration: record real responses and replay them (VCR pattern); simulate 429/5xx/timeout to exercise every fallback branch.
- Quality: ship with a golden set of ≥20 cases; the recurring eval pipeline is `llmops`.

## Step 5: Responsible-AI Checklist (ship gate)

- [ ] Users are told they're interacting with AI; generated content is labeled
- [ ] Users can report bad output, and reports reach a triage queue
- [ ] PII handling matches the privacy policy; provider data-retention and training terms checked
- [ ] No training on user data without explicit consent
- [ ] Bias tested for this use case's affected groups
- [ ] Human review path for high-stakes decisions (credit, health, employment, minors)
- [ ] Kill switch tested in staging

## Code/Artifact Generation

Applies when the user asks to build or extend the feature (not for a review or a question). Write in the detected stack:

1. LLM client wrapper — typed, timeout, retry policy above, streaming, model ID from config
2. Versioned prompt module for the feature
3. Feature integration (API route/Cloud Function + UI with streaming and fallback states)
4. Kill-switch flag wiring
5. Tests from Step 4, including recorded fixtures

For cost tracking, budgets, and eval CI, hand off to `llmops`; for retrieval, to `rag-architect`. In Claude Code these are `/cure-product-engineering:<name>`; in Codex, `$<name>`.
