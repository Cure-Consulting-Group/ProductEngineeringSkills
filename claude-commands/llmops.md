# LLMOps

Production operations framework for LLM-powered features. Every AI feature at Cure Consulting Group ships with versioned prompts, automated evaluation, cost guardrails, safety filters, and monitoring. No LLM feature goes to production without these operational controls. Shipping a prompt without eval is shipping code without tests.

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

### Version Control for Prompts

```
prompts/
├── chat-assistant/
│   ├── system.v1.0.0.txt       # Production (current)
│   ├── system.v1.1.0.txt       # Staging (candidate)
│   ├── system.v0.9.0.txt       # Previous production
│   ├── config.json              # Model, temperature, max_tokens
│   └── eval/
│       ├── golden-dataset.jsonl  # Test cases for this prompt
│       └── eval-results.json     # Latest eval scores
├── content-summarizer/
│   ├── system.v2.0.0.txt
│   ├── config.json
│   └── eval/
│       ├── golden-dataset.jsonl
│       └── eval-results.json
└── README.md                    # Prompt catalog and ownership
```

Rules:
- **Every prompt is in git** -- no prompts stored only in dashboards, databases, or environment variables
- **Semantic versioning** -- major: behavior change, minor: quality improvement, patch: typo/formatting
- **Config alongside prompt** -- model, temperature, max_tokens, stop sequences travel with the prompt
- **Never edit production prompts directly** -- always go through: edit → eval → staging → production
- **Prompt ownership** -- every prompt has an owner who approves changes

### Prompt Template System

```typescript
// lib/prompts/loader.ts
import { readFileSync } from "fs";
import { join } from "path";

interface PromptConfig {
  model: string;
  temperature: number;
  maxTokens: number;
  stopSequences?: string[];
  version: string;
}

interface PromptTemplate {
  system: string;
  config: PromptConfig;
}

export function loadPrompt(name: string, version?: string): PromptTemplate {
  const dir = join(__dirname, "prompts", name);
  const config: PromptConfig = JSON.parse(readFileSync(join(dir, "config.json"), "utf-8"));
  const ver = version || config.version;
  const system = readFileSync(join(dir, `system.v${ver}.txt`), "utf-8");
  return { system, config };
}

// Typed variables — no string interpolation with unvalidated input
export function renderPrompt(template: string, variables: Record<string, string>): string {
  let rendered = template;
  for (const [key, value] of Object.entries(variables)) {
    // Validate variable content to prevent injection
    if (value.includes("{{") || value.includes("}}")) {
      throw new Error(`Prompt injection attempt detected in variable: ${key}`);
    }
    rendered = rendered.replace(new RegExp(`\\{\\{${key}\\}\\}`, "g"), value);
  }
  // Check for unreplaced variables
  const unreplaced = rendered.match(/\{\{[^}]+\}\}/g);
  if (unreplaced) {
    throw new Error(`Unreplaced prompt variables: ${unreplaced.join(", ")}`);
  }
  return rendered;
}
```

### A/B Testing Prompts in Production

```typescript
// lib/prompts/ab-test.ts
import { getRemoteConfig, getValue } from "firebase/remote-config";

interface ABTestConfig {
  name: string;
  variants: {
    control: { version: string; weight: number };
    treatment: { version: string; weight: number };
  };
  startDate: string;
  endDate: string;
  targetMetric: string;
}

export function selectPromptVariant(userId: string, testConfig: ABTestConfig): string {
  // Deterministic assignment based on user ID (consistent experience)
  const hash = hashString(`${userId}-${testConfig.name}`);
  const bucket = hash % 100;

  const controlThreshold = testConfig.variants.control.weight;
  const variant = bucket < controlThreshold ? "control" : "treatment";

  // Log assignment for analysis
  logEvent("prompt_ab_assignment", {
    test: testConfig.name,
    variant,
    userId,
    promptVersion: testConfig.variants[variant].version,
  });

  return testConfig.variants[variant].version;
}
```

### Prompt Regression Testing

```typescript
// eval/prompt-regression.ts
interface TestCase {
  input: Record<string, string>;
  expectedOutput?: string;       // Exact match (rare)
  mustContain?: string[];         // Required phrases
  mustNotContain?: string[];      // Forbidden phrases
  qualityThreshold?: number;      // LLM-judge score 0-1
}

async function runPromptRegression(
  promptName: string,
  version: string,
  goldenDataset: TestCase[]
): Promise<{ passed: number; failed: number; score: number }> {
  const prompt = loadPrompt(promptName, version);
  let passed = 0;
  let totalScore = 0;

  for (const testCase of goldenDataset) {
    const response = await callLLM(prompt, testCase.input);

    let casePassed = true;
    if (testCase.mustContain) {
      for (const phrase of testCase.mustContain) {
        if (!response.includes(phrase)) casePassed = false;
      }
    }
    if (testCase.mustNotContain) {
      for (const phrase of testCase.mustNotContain) {
        if (response.includes(phrase)) casePassed = false;
      }
    }
    if (testCase.qualityThreshold) {
      const score = await llmJudge(testCase.input, response);
      totalScore += score;
      if (score < testCase.qualityThreshold) casePassed = false;
    }

    if (casePassed) passed++;
  }

  return {
    passed,
    failed: goldenDataset.length - passed,
    score: totalScore / goldenDataset.length,
  };
}
```

## Step 4: Evaluation Pipelines

### Offline Evaluation

#### Golden Datasets

```
GOLDEN DATASET STRUCTURE (JSONL)
Each line is a JSON object:

{"id": "001", "input": {"query": "What's the refund policy?"}, "expected_category": "policy", "expected_contains": ["30 days", "full refund"], "human_rating": 4.5}
{"id": "002", "input": {"query": "My order hasn't arrived"}, "expected_category": "shipping", "expected_contains": ["tracking", "business days"], "human_rating": 4.0}

Rules:
  - Minimum 100 test cases per prompt (200+ for critical features)
  - Include edge cases: empty input, very long input, adversarial input
  - Include distribution of categories matching production traffic
  - Update golden dataset quarterly or when production issues are found
  - Version the dataset alongside the prompt
```

#### LLM-as-Judge

```typescript
// eval/llm-judge.ts
const JUDGE_PROMPT = `You are evaluating the quality of an AI assistant's response.

User Query: {{query}}
AI Response: {{response}}
Reference Answer: {{reference}}

Score the response on these dimensions (each 0-5):
1. Relevance: Does it address the user's question?
2. Accuracy: Is the information correct?
3. Completeness: Does it cover all important aspects?
4. Clarity: Is it well-written and easy to understand?
5. Safety: Does it avoid harmful, biased, or inappropriate content?

Respond in JSON:
{"relevance": X, "accuracy": X, "completeness": X, "clarity": X, "safety": X, "overall": X, "reasoning": "..."}`;

async function llmJudge(query: string, response: string, reference?: string): Promise<JudgeResult> {
  const result = await callLLM({
    model: "claude-sonnet-4-20250514",  // Use a strong model for judging
    temperature: 0,
    prompt: renderPrompt(JUDGE_PROMPT, { query, response, reference: reference || "N/A" }),
  });
  return JSON.parse(result);
}
```

#### Human Evaluation Protocols

```
HUMAN EVAL PROTOCOL

When to require human eval:
  - New prompt version with major changes
  - New AI feature launch
  - LLM-judge disagrees with golden dataset >20% of the time
  - Customer complaints about AI quality

Process:
  1. Sample 50-100 responses from staging
  2. 3 human raters per response (use majority vote)
  3. Rating rubric: 1-5 scale for relevance, accuracy, helpfulness
  4. Inter-rater reliability target: Cohen's kappa > 0.7
  5. Results inform: ship/don't ship decision + golden dataset updates

Tools:
  - Labelbox, Scale AI, or Argilla for structured annotation
  - Google Sheets with standardized rubric for small-scale eval
```

### Online Evaluation

```
ONLINE EVAL SIGNALS

Explicit Feedback:
  - Thumbs up/down on AI responses (target: >80% positive)
  - "Was this helpful?" prompt after AI interaction
  - Star ratings (1-5) for quality assessment
  - Free-text feedback for qualitative insights

Implicit Feedback:
  - Regeneration rate: user clicked "try again" (lower is better)
  - Copy rate: user copied the response (higher suggests value)
  - Follow-up rate: user asked clarifying question (moderate = engaging, high = confusing)
  - Abandonment rate: user left without completing task (lower is better)
  - Time to first action after response (shorter = more actionable)
  - Edit distance: how much user modified AI output (less = more accurate)

Automated Quality Checks:
  - Hallucination detection: compare claims against source docs
  - Format compliance: response matches expected schema
  - Latency tracking: time from request to first token, total response time
  - Token usage: input/output tokens per request
```

### Automated Eval in CI

```yaml
# .github/workflows/prompt-eval.yml
name: Prompt Evaluation
on:
  pull_request:
    paths:
      - "prompts/**"

jobs:
  eval:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20

      - name: Install dependencies
        run: npm ci

      - name: Detect changed prompts
        id: changes
        run: |
          CHANGED=$(git diff --name-only origin/main -- prompts/ | grep -oP 'prompts/[^/]+' | sort -u)
          echo "prompts=$CHANGED" >> $GITHUB_OUTPUT

      - name: Run evaluations
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          for prompt_dir in ${{ steps.changes.outputs.prompts }}; do
            npx ts-node eval/run-eval.ts --prompt "$prompt_dir" --threshold 0.85
          done

      - name: Post results to PR
        uses: actions/github-script@v7
        with:
          script: |
            const results = require('./eval/latest-results.json');
            const body = formatEvalResults(results);
            github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              body
            });

      - name: Fail if quality dropped
        run: npx ts-node eval/check-threshold.ts --min-score 0.85
```

### Eval Metrics Summary

```
EVALUATION METRICS REFERENCE

Metric          Formula                                Target      Alert Threshold
─────────────────────────────────────────────────────────────────────────────────
Accuracy        correct / total                        >90%        <85%
Relevance       relevant_responses / total              >95%        <90%
Faithfulness    claims_supported_by_source / claims     >95%        <90%
Toxicity        toxic_responses / total                 <0.1%       >0.5%
Latency (p50)   median response time                   <2s          >3s
Latency (p95)   95th percentile response time           <5s          >8s
Cost/request    total_cost / total_requests             <$0.05      >$0.10
User satisfaction  positive_feedback / total_feedback   >80%        <70%
Hallucination   responses_with_unsupported_claims / total  <5%      >10%
```

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

### Input Validation

```typescript
// lib/llm/guardrails/input.ts

interface InputValidation {
  isValid: boolean;
  reason?: string;
  sanitizedInput?: string;
}

export async function validateInput(input: string, config: GuardrailConfig): Promise<InputValidation> {
  // 1. Length check
  if (input.length > config.maxInputLength) {
    return { isValid: false, reason: "Input exceeds maximum length" };
  }
  if (input.trim().length === 0) {
    return { isValid: false, reason: "Empty input" };
  }

  // 2. PII detection
  const piiDetected = detectPII(input);
  if (piiDetected.length > 0 && config.blockPII) {
    return { isValid: false, reason: `PII detected: ${piiDetected.join(", ")}` };
  }

  // 3. Prompt injection detection
  const injectionScore = await detectInjection(input);
  if (injectionScore > 0.8) {
    logger.warn("Prompt injection attempt detected", { input: input.substring(0, 100), score: injectionScore });
    return { isValid: false, reason: "Suspicious input detected" };
  }

  // 4. Topic boundary check
  if (config.allowedTopics) {
    const topic = await classifyTopic(input);
    if (!config.allowedTopics.includes(topic)) {
      return { isValid: false, reason: `Off-topic request: ${topic}` };
    }
  }

  return { isValid: true, sanitizedInput: input };
}

// Injection detection patterns
function detectInjection(input: string): Promise<number> {
  const patterns = [
    /ignore (all )?(previous|above|prior) instructions/i,
    /you are now/i,
    /system prompt/i,
    /reveal your (instructions|prompt|system)/i,
    /pretend you are/i,
    /jailbreak/i,
    /DAN mode/i,
  ];
  const patternScore = patterns.some(p => p.test(input)) ? 0.9 : 0;

  // For higher confidence, also use a classifier model
  // return Math.max(patternScore, await classifierScore(input));
  return Promise.resolve(patternScore);
}
```

### Output Validation

```typescript
// lib/llm/guardrails/output.ts

interface OutputValidation {
  isValid: boolean;
  reason?: string;
  filteredOutput?: string;
}

export async function validateOutput(
  output: string,
  input: string,
  config: GuardrailConfig
): Promise<OutputValidation> {
  // 1. Format compliance
  if (config.expectedFormat === "json") {
    try { JSON.parse(output); } catch {
      return { isValid: false, reason: "Output is not valid JSON" };
    }
  }

  // 2. Safety filter
  const toxicity = await checkToxicity(output);
  if (toxicity.score > 0.7) {
    logger.error("Toxic output detected", { toxicityScore: toxicity.score, categories: toxicity.categories });
    return { isValid: false, reason: "Output failed safety check" };
  }

  // 3. Hallucination detection (for RAG)
  if (config.sourceDocuments) {
    const claims = extractClaims(output);
    const unsupported = claims.filter(claim => !isSupported(claim, config.sourceDocuments!));
    if (unsupported.length > 0) {
      logger.warn("Potential hallucination", { unsupportedClaims: unsupported });
      // Option: strip unsupported claims, or reject entirely
      if (unsupported.length / claims.length > 0.3) {
        return { isValid: false, reason: "Too many unsupported claims" };
      }
    }
  }

  // 4. PII in output (should never leak PII from context)
  const piiInOutput = detectPII(output);
  if (piiInOutput.length > 0) {
    const filtered = redactPII(output);
    return { isValid: true, filteredOutput: filtered };
  }

  return { isValid: true, filteredOutput: output };
}
```

### Rate Limiting

```typescript
// lib/llm/rate-limit.ts
interface RateLimits {
  requestsPerMinutePerUser: number;
  requestsPerHourPerUser: number;
  requestsPerDayPerUser: number;
  concurrentRequestsPerUser: number;
}

const RATE_LIMITS: RateLimits = {
  requestsPerMinutePerUser: 10,
  requestsPerHourPerUser: 100,
  requestsPerDayPerUser: 500,
  concurrentRequestsPerUser: 3,
};

// Use Redis or Firestore for distributed rate limiting
// Return 429 with Retry-After header when limit exceeded
```

### Fallback Strategy

```
FALLBACK CHAIN (model unavailable or over budget)

1. Primary model unavailable (API error, timeout, rate limited)
   → Retry with exponential backoff (max 3 retries, 1s/2s/4s)

2. Primary model still unavailable after retries
   → Fall back to secondary model (e.g., Claude → GPT-4o → Gemini)
   → Log fallback event for monitoring

3. All models unavailable
   → Return cached response if available (semantic cache)
   → If no cache: return graceful error message to user
   → NEVER show a raw API error to the user

4. Cost budget exceeded
   → Downgrade to cheaper model tier
   → If all tiers exceeded: queue request for next budget window
   → Notify user: "AI features are temporarily limited"

5. Safety filter triggered
   → Return safe default response
   → Log for review
   → Do NOT retry with different model (safety is safety)

Implementation:
  NEVER crash the application because an LLM is unavailable.
  ALWAYS have a non-AI fallback for critical user flows.
  AI features should degrade gracefully, not catastrophically.
```

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

Cross-references: Use `/ai-feature-builder` for designing the AI feature itself. Use `/observability` for setting up the monitoring infrastructure that LLMOps metrics feed into. Use `/incident-response` for the broader incident response framework. Use `/engineering-cost-model` for projecting LLM costs as part of total project cost.
