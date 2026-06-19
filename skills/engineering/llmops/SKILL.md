---
name: llmops
description: "Operationalize LLM features — prompt versioning, evaluation pipelines, cost optimization, guardrails, RAG monitoring, and model lifecycle management"
when_to_use: "Use when operationalizing LLM features — prompt versioning, eval pipelines, cost optimization, guardrails, or model lifecycle management. NOT for building new AI features (use ai-feature-builder)."
argument-hint: "[ai-feature-or-pipeline]"
---

# LLMOps

Production operations framework for LLM-powered features. Every AI feature at Cure Consulting Group ships with versioned prompts, automated evaluation, cost guardrails, safety filters, and monitoring. No LLM feature goes to production without these operational controls. Shipping a prompt without eval is shipping code without tests.

## Pre-Processing (Auto-Context)

Before starting, gather project context silently:
- Read `PORTFOLIO.md` if it exists in the project root or parent directories for product/team context
- Run: `cat package.json 2>/dev/null || cat build.gradle.kts 2>/dev/null || cat Podfile 2>/dev/null` to detect stack
- Run: `git log --oneline -5 2>/dev/null` for recent changes
- Run: `ls src/ app/ lib/ functions/ 2>/dev/null` to understand project structure
- Use this context to tailor all output to the actual project

## Step 1: Classify the LLMOps Need

| Need | Scope | Starting Point |
|------|-------|---------------|
| New AI feature productionization | Full LLMOps stack — prompts, eval, guardrails, monitoring, cost controls | Start at Step 3 |
| Eval pipeline setup | Build offline and online evaluation for existing AI feature | Jump to Step 4 |
| Cost optimization | Reduce LLM spend without degrading quality | Jump to Step 5 |
| Guardrail implementation | Add safety filters, input validation, output validation | Jump to Step 6 |
| RAG monitoring | Monitor retrieval quality, index freshness, embedding drift | Jump to Step 7 |

## Step 2: Gather Context

1. **Models used** -- which LLMs are in play (GPT-4o, Claude, Gemini, open-source)? Are there multiple models for different tasks?
2. **Deployment target** -- where does the AI feature run (Firebase Functions, Cloud Run, edge, client-side)?
3. **Current spend** -- monthly LLM API costs, tokens per day, cost per user interaction?
4. **Latency requirements** -- what's the acceptable response time (sub-second for autocomplete, 5-10s for generation)?
5. **Compliance** -- data residency, PII handling, content moderation requirements, industry regulations?
6. **Evaluation maturity** -- are there existing evals, golden datasets, human eval processes?
7. **RAG pipeline** -- is there a retrieval component? What's the index size, embedding model, chunking strategy?
8. **User volume** -- requests per day, peak concurrency, growth trajectory?

## Step 3: Prompt Management

See [reference/details.md](reference/details.md) (section “Step 3: Prompt Management”) for full detail.

## Step 4: Evaluation Pipelines

See [reference/details.md](reference/details.md) (section “Step 4: Evaluation Pipelines”) for full detail.

## Step 5: Cost Optimization

### Model Tiering Strategy

```
MODEL ROUTING FRAMEWORK

Tier 1 — Small/Fast (for simple tasks):
  Models: Claude Haiku, GPT-4o-mini, Gemini Flash
  Use for: Classification, extraction, formatting, short Q&A
  Cost: ~$0.25/M input, ~$1/M output tokens
  Latency: <500ms typical

Tier 2 — Standard (for most tasks):
  Models: Claude Sonnet, GPT-4o, Gemini Pro
  Use for: Content generation, summarization, analysis, RAG synthesis
  Cost: ~$3/M input, ~$15/M output tokens
  Latency: 1-3s typical

Tier 3 — Large/Powerful (for complex tasks):
  Models: Claude Opus, o1, Gemini Ultra
  Use for: Complex reasoning, code generation, multi-step analysis
  Cost: ~$15/M input, ~$75/M output tokens
  Latency: 5-30s typical

Router Implementation:
```

```typescript
// lib/llm/router.ts
interface RoutingDecision {
  model: string;
  tier: number;
  reason: string;
}

export function routeRequest(request: LLMRequest): RoutingDecision {
  // Classification/extraction → Tier 1
  if (request.taskType === "classify" || request.taskType === "extract") {
    return { model: "claude-haiku", tier: 1, reason: "Simple structured task" };
  }

  // Short input + short expected output → Tier 1
  if (request.inputTokens < 500 && request.maxOutputTokens < 200) {
    return { model: "claude-haiku", tier: 1, reason: "Short input/output" };
  }

  // Complex reasoning, code gen, multi-step → Tier 3
  if (request.taskType === "code-generation" || request.taskType === "complex-reasoning") {
    return { model: "claude-sonnet", tier: 2, reason: "Complex task (use Tier 3 only if Tier 2 eval fails)" };
  }

  // Default → Tier 2
  return { model: "claude-sonnet", tier: 2, reason: "Standard generation task" };
}
```

### Caching Strategy

```typescript
// lib/llm/cache.ts
import { createHash } from "crypto";

interface CacheConfig {
  semanticCache: boolean;         // Cache similar (not identical) queries
  ttlSeconds: number;             // Time to live
  maxEntries: number;             // Max cache size
}

// Exact match cache (for deterministic prompts: classification, extraction)
function exactCacheKey(prompt: string, model: string, temperature: number): string {
  return createHash("sha256").update(`${model}:${temperature}:${prompt}`).digest("hex");
}

// Semantic cache (for similar queries with same intent)
async function semanticCacheKey(query: string, threshold: number = 0.95): Promise<string | null> {
  const embedding = await getEmbedding(query);
  const nearest = await vectorStore.findNearest(embedding, { threshold });
  return nearest?.cacheKey || null;
}

// Cache rules by task type:
// Classification (temperature=0) → exact cache, TTL 24h
// FAQ answers → semantic cache, TTL 1h
// Creative generation → no cache (non-deterministic)
// User-specific responses → no cache (personalized)
```

### Token Budget Enforcement

```typescript
// lib/llm/budget.ts
interface TokenBudget {
  maxInputTokensPerCall: number;
  maxOutputTokensPerCall: number;
  maxTokensPerSession: number;
  maxTokensPerUserPerDay: number;
  maxDailySpend: number;
}

const BUDGETS: Record<string, TokenBudget> = {
  "chat-assistant": {
    maxInputTokensPerCall: 8000,
    maxOutputTokensPerCall: 2000,
    maxTokensPerSession: 50000,
    maxTokensPerUserPerDay: 200000,
    maxDailySpend: 500,  // dollars
  },
  "content-summarizer": {
    maxInputTokensPerCall: 100000,
    maxOutputTokensPerCall: 4000,
    maxTokensPerSession: 200000,
    maxTokensPerUserPerDay: 500000,
    maxDailySpend: 200,
  },
};

export async function checkBudget(feature: string, userId: string, tokens: number): Promise<boolean> {
  const budget = BUDGETS[feature];
  if (!budget) throw new Error(`No budget defined for feature: ${feature}`);

  const dailyUsage = await getDailyUsage(feature, userId);
  if (dailyUsage + tokens > budget.maxTokensPerUserPerDay) {
    logger.warn("Token budget exceeded", { feature, userId, dailyUsage, requested: tokens });
    return false;
  }

  const dailySpend = await getDailySpend(feature);
  if (dailySpend > budget.maxDailySpend) {
    logger.error("Daily spend limit exceeded", { feature, dailySpend, limit: budget.maxDailySpend });
    // Page on-call if spend is 2x limit
    if (dailySpend > budget.maxDailySpend * 2) {
      await alertOncall(`LLM spend alert: ${feature} at $${dailySpend} (limit: $${budget.maxDailySpend})`);
    }
    return false;
  }

  return true;
}
```

### Cost Dashboard and Alerts

```
COST MONITORING

Dashboard Panels:
  - [Timeseries] Daily LLM spend by feature
  - [Timeseries] Daily LLM spend by model
  - [Stat]       Month-to-date spend vs budget
  - [Timeseries] Cost per request trend
  - [Timeseries] Token usage (input vs output) by feature
  - [Stat]       Cache hit rate (higher = more savings)
  - [Table]      Top 10 most expensive user sessions (identify abuse)

Alerts:
  - Daily spend >120% of average → Slack notification
  - Daily spend >200% of average → page on-call
  - Single user >$50/day in LLM costs → investigate (possible abuse or bug)
  - Cache hit rate drops below 30% → investigate (cache invalidation issue?)
  - Average cost per request increases >50% → check model routing
```

## Step 6: Guardrails and Safety

See [reference/details.md](reference/details.md) (section “Step 6: Guardrails and Safety”) for full detail.

## Step 7: RAG Pipeline Monitoring

### Retrieval Quality Metrics

```
RETRIEVAL METRICS

Precision@K:
  Definition: Of the top K retrieved documents, how many are relevant?
  Formula: relevant_in_top_k / k
  Target: >0.8 for k=5
  Measure: Compare retrieved docs against human-judged relevance

Recall:
  Definition: Of all relevant documents, how many were retrieved?
  Formula: relevant_retrieved / total_relevant
  Target: >0.9
  Measure: Requires known-relevant document set per query

MRR (Mean Reciprocal Rank):
  Definition: Average of 1/rank of first relevant result
  Formula: mean(1 / rank_of_first_relevant)
  Target: >0.7
  Measure: First relevant document should be in top 2-3 results

NDCG (Normalized Discounted Cumulative Gain):
  Definition: Quality of ranking considering position
  Target: >0.8
  Measure: Relevant documents should be ranked higher
```

### Index Freshness Monitoring

```typescript
// lib/rag/monitoring.ts

interface IndexHealth {
  totalDocuments: number;
  lastIndexedAt: Date;
  staleDocs: number;          // Docs not re-indexed since source update
  averageChunkSize: number;
  embeddingModel: string;
  embeddingDimension: number;
}

// Monitor and alert on:
// - Index age: if lastIndexedAt > 24 hours → warning
// - Stale documents: if staleDocs > 10% of total → re-index trigger
// - Document count: sudden drop indicates indexing failure
// - Embedding model version: track for drift detection

async function checkIndexHealth(): Promise<IndexHealth> {
  const health = await vectorStore.getHealth();

  if (health.staleDocs / health.totalDocuments > 0.1) {
    await triggerReindex("Stale document threshold exceeded");
  }

  if (Date.now() - health.lastIndexedAt.getTime() > 24 * 60 * 60 * 1000) {
    logger.warn("Index is stale", { lastIndexed: health.lastIndexedAt });
  }

  return health;
}
```

### Embedding Drift Detection

```
EMBEDDING DRIFT DETECTION

What is drift:
  - Embedding model update changes vector space geometry
  - Source documents change character (new terminology, different style)
  - Query patterns shift (users ask different types of questions)

Detection:
  - Track average cosine similarity between queries and top results
  - If average similarity drops >10% over 7 days → investigate
  - Compare embedding distributions monthly (centroid shift)
  - Monitor retrieval quality metrics alongside similarity scores

Response:
  - If model updated: full re-index required (cannot mix embedding versions)
  - If content drift: re-evaluate chunking strategy, update golden eval set
  - If query drift: analyze new query patterns, potentially add new content
```

### Chunk Quality Analysis

```
CHUNK QUALITY CHECKLIST

Chunking Rules:
  - Chunk size: 500-1000 tokens (test what works for your content)
  - Overlap: 50-100 tokens between chunks (prevent information loss at boundaries)
  - Respect document structure: don't split mid-sentence, mid-paragraph, or mid-section
  - Include metadata: source document, section title, page number, last updated date

Quality Checks:
  - [ ] No orphan chunks (chunks that make no sense without context)
  - [ ] No duplicate chunks (same content indexed multiple times)
  - [ ] Metadata is complete and accurate
  - [ ] Chunk boundaries align with semantic boundaries
  - [ ] Average retrieval score for test queries > 0.8

Monitoring:
  - Track average chunk length (should be consistent)
  - Track chunks per document (sudden changes indicate processing issues)
  - Sample random chunks monthly for quality review
```

## Step 8: Incident Response for AI Features

### AI-Specific Incident Types

```
INCIDENT TYPE               DETECTION                         RESPONSE
──────────────────────────────────────────────────────────────────────────────
Model degradation           Quality eval scores drop >10%     Switch to fallback model,
                            User satisfaction drops >15%       investigate, re-evaluate

Cost spike                  Daily spend >200% of average      Activate cost limits,
                            Single-user spend anomaly          investigate traffic source

Safety incident             Toxic output detected by filter   Disable feature immediately,
                            User report of harmful content    preserve logs, investigate

Hallucination spike         Faithfulness score drops >15%     Check RAG index freshness,
                            User reports of incorrect info    re-run eval pipeline

Latency degradation         p95 latency >2x normal            Check model provider status,
                            Timeout rate increases              activate caching, consider
                                                               model downgrade

Data leak                   PII detected in LLM output        Disable feature, audit logs,
                            Prompt injection succeeded         notify security team, notify
                                                               affected users if required
```

### AI Incident Runbook

```
AI INCIDENT RESPONSE STEPS

1. Detect: automated quality monitoring, user feedback, cost alerts
2. Classify: model issue, safety issue, cost issue, data issue
3. Mitigate:
   - Model issue → switch to fallback model
   - Safety issue → disable feature, enable safe-mode responses only
   - Cost issue → enforce strict rate limits, disable non-critical features
   - Data issue → disable feature, preserve logs for investigation
4. Investigate: check eval scores, review user reports, analyze logs
5. Fix: update prompt, fix guardrails, update model config, re-index
6. Verify: re-run eval pipeline, confirm metrics back to baseline
7. Post-mortem: update golden dataset with new failure cases
```

## Step 9: Output

```
LLMOPS REPORT
Feature: [NAME]
Date: [TODAY]
Prepared by: [NAME]

CURRENT STATE ASSESSMENT
┌──────────────────────────┬──────────────────────────────────────┐
│ Component                │ Status                               │
├──────────────────────────┼──────────────────────────────────────┤
│ Prompt versioning        │ [Not started / Partial / Complete]   │
│ Offline evaluation       │ [Not started / Partial / Complete]   │
│ Online evaluation        │ [Not started / Partial / Complete]   │
│ CI eval pipeline         │ [Not started / Partial / Complete]   │
│ Model routing            │ [Not started / Partial / Complete]   │
│ Caching                  │ [Not started / Partial / Complete]   │
│ Token budgets            │ [Not started / Partial / Complete]   │
│ Input guardrails         │ [Not started / Partial / Complete]   │
│ Output guardrails        │ [Not started / Partial / Complete]   │
│ RAG monitoring           │ [Not started / Partial / Complete]   │
│ Cost monitoring          │ [Not started / Partial / Complete]   │
│ Incident response plan   │ [Not started / Partial / Complete]   │
└──────────────────────────┴──────────────────────────────────────┘

DELIVERABLES GENERATED:
  - [ ] Prompt management system with version control
  - [ ] Golden dataset for offline evaluation
  - [ ] LLM-as-judge evaluation pipeline
  - [ ] CI/CD eval integration (fail PR if quality drops)
  - [ ] Model routing with tier strategy
  - [ ] Caching layer (exact + semantic)
  - [ ] Token budget enforcement per feature/user
  - [ ] Input validation (PII, injection, topic boundaries)
  - [ ] Output validation (safety, hallucination, format)
  - [ ] Rate limiting per user
  - [ ] Fallback chain for model unavailability
  - [ ] RAG retrieval quality monitoring
  - [ ] Cost dashboard and spend alerts
  - [ ] AI-specific incident response plan
```

## Code Generation (Required)

Generate LLMOps infrastructure using Write:

1. **Eval pipeline**: `.github/workflows/prompt-eval.yml` — CI workflow that runs prompt evaluations on PR
2. **Golden dataset**: `evals/golden-dataset.jsonl` — starter test cases (10 examples)
3. **Eval runner**: `evals/run-eval.ts` — script that runs prompts against golden dataset and scores
4. **Prompt registry**: `src/prompts/registry.ts` — versioned prompt templates with metadata
5. **Cost tracker**: `src/llm/cost-tracker.ts` — middleware that logs token usage and cost per request
6. **Guardrails**: `src/llm/guardrails.ts` — input/output validation, PII detection, content filtering

Before generating, Grep for existing LLM usage (`openai|anthropic|gemini|Claude|GPT|completion`) to understand current integration.

Cross-references: Use `/ai-feature-builder` for designing the AI feature itself. Use `/observability` for setting up the monitoring infrastructure that LLMOps metrics feed into. Use `/incident-response` for the broader incident response framework. Use `/engineering-cost-model` for projecting LLM costs as part of total project cost.
