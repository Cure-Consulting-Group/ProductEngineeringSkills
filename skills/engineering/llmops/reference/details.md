# llmops: detailed reference

> Reference material for the `llmops` skill, split out for progressive disclosure. Loaded on demand from SKILL.md.

## Contents
- Step 3: Prompt Management
- Step 4: Evaluation Pipelines
- Step 6: Guardrails and Safety

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
