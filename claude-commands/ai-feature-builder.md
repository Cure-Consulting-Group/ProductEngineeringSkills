# AI Feature Builder

Build production AI features: LLM integration, RAG pipelines, voice/vision, and intelligent automation. Ship AI that's reliable, cost-aware, and safe — not a demo.

## Step 1: Classify the AI Feature Type

| Feature | Architecture |
|---------|-------------|
| Chatbot / conversational | LLM + conversation memory + streaming UI |
| Document processing | Upload → OCR/parse → LLM extract → structured output |
| Smart search | Embeddings + vector DB + semantic search |
| Recommendations | User data → embedding similarity → ranked results |
| Content generation | LLM + prompt template + guardrails + human review |
| Voice interaction | Speech-to-text → LLM → text-to-speech |
| Image/vision analysis | Vision model → structured extraction |
| Workflow automation | Trigger → LLM decision → action → verification |
| RAG (retrieval-augmented) | Query → retrieve context → LLM with context → response |

## Step 2: Gather Context

1. **Feature description** — what should the AI do for the user?
2. **Model provider** — OpenAI, Google Gemini, Anthropic Claude, or open-source?
3. **Latency tolerance** — real-time (<2s), near-real-time (<10s), async (background)?
4. **Data sensitivity** — PII, financial, health, children? (determines guardrails)
5. **Volume** — expected requests per day/hour?
6. **Budget** — cost ceiling per request or per month?
7. **Fallback** — what happens when the AI fails or returns garbage?

## Step 3: Architecture Patterns

### Direct LLM Call (simplest)
```
User Input → Prompt Template → LLM API → Parse Response → UI
```
Use for: content generation, simple Q&A, classification

### RAG (Retrieval-Augmented Generation)
```
User Query
  → Embed query (text-embedding model)
  → Search vector DB (Pinecone, Firestore vector, pgvector)
  → Retrieve top-K relevant chunks
  → Construct prompt: system + context chunks + user query
  → LLM generates answer grounded in retrieved context
  → Response with source citations
```
Use for: knowledge bases, documentation search, domain-specific Q&A

### Agent / Multi-Step
```
User Request
  → LLM plans steps (tool selection)
  → Execute tool 1 → result
  → Execute tool 2 → result
  → LLM synthesizes final response
```
Use for: complex workflows, multi-source data, actions with side effects

## Step 4: Implementation Rules

### Prompt Engineering
- **System prompt**: define role, constraints, output format. Keep under 500 tokens
- **Few-shot examples**: include 2-3 input/output examples for complex tasks
- **Output format**: always request structured output (JSON) for programmatic use
- **Temperature**: 0-0.3 for factual/extraction, 0.7-1.0 for creative
- **Never** put user input directly into system prompt — always in the user message

### Guardrails (Non-Negotiable)
```
Input guardrails:
  - Validate input length (reject > max tokens)
  - Sanitize PII before sending to external LLM (if required by policy)
  - Rate limit per user (prevent abuse / cost spikes)
  - Content moderation on user input (if public-facing)

Output guardrails:
  - Parse structured output with schema validation (Zod)
  - Reject responses that fail schema validation → fallback
  - Content filtering on LLM output (profanity, harmful content)
  - Confidence thresholds — low confidence → human review queue
  - Never display raw LLM output without parsing
```

### Cost Management
```
Per-request cost formula:
  (input_tokens × input_price) + (output_tokens × output_price)

Cost controls:
  - Set max_tokens on every request (prevents runaway responses)
  - Cache identical requests (hash prompt → cache response, TTL 1hr+)
  - Use smaller models for simple tasks (classification, extraction)
  - Use larger models only for complex reasoning
  - Log token usage per feature for cost attribution
  - Set monthly budget alerts
```

### Streaming Responses
```typescript
// For chat/conversational features — always stream
// Users perceive streaming as faster even when total time is the same

// Server: return ReadableStream
// Client: consume with async iterator, render token-by-token
// Show typing indicator while first token loads
// Handle stream interruption gracefully (partial response display)
```

## Step 5: Data Pipeline for RAG

```
Document Ingestion:
  1. Upload document (PDF, DOCX, HTML, TXT)
  2. Extract text (pdf-parse, mammoth, cheerio)
  3. Chunk text (500-1000 tokens per chunk, 100 token overlap)
  4. Generate embeddings (text-embedding-3-small or equivalent)
  5. Store in vector DB with metadata (source, page, date)

Query Pipeline:
  1. Embed user query with same model
  2. Vector similarity search (top 5-10 chunks)
  3. Re-rank results (optional, improves quality)
  4. Construct prompt with retrieved context
  5. Generate response with citations
```

## Step 6: Error Handling & Fallbacks

```
LLM API errors:
  - 429 Rate Limited → exponential backoff (1s, 2s, 4s, max 3 retries)
  - 500/503 Server Error → retry once, then fallback
  - Timeout (>30s) → cancel, show fallback UI
  - Invalid response → log, show "I couldn't process that" message

Fallback hierarchy:
  1. Retry with same model
  2. Try backup model (e.g., GPT-4 fails → try Gemini)
  3. Return cached similar response (if available)
  4. Show graceful error with manual alternative
  5. Never: crash, hang, or show raw error to user
```

## Step 7: Testing AI Features

```
Unit tests:
  - Prompt template generates correct string for given inputs
  - Output parser handles valid JSON, malformed JSON, empty response
  - Guardrails block known-bad inputs
  - Cost calculation is accurate

Integration tests (use recorded responses):
  - Record real LLM responses → replay in tests (VCR pattern)
  - Test full pipeline: input → prompt → (recorded) response → parsed output
  - Test fallback paths with simulated errors

Evaluation tests:
  - Maintain a golden dataset (input → expected output pairs)
  - Run weekly eval: measure accuracy, hallucination rate, relevance
  - Track eval scores over time (regression detection)
```

## Step 8: Responsible AI Checklist

Before shipping any AI feature:
- [ ] Users know they're interacting with AI (transparency)
- [ ] AI-generated content is labeled as such
- [ ] User can report bad/harmful AI output (feedback loop)
- [ ] PII handling complies with privacy policy
- [ ] No training on user data without explicit consent
- [ ] Bias testing done for the specific use case
- [ ] Human review path exists for high-stakes decisions
- [ ] Kill switch: feature can be disabled without redeployment (remote config)
