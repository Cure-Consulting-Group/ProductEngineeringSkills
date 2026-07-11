---
name: rag-architect
description: "Design production RAG pipelines — chunking, embeddings, vector stores, hybrid retrieval, reranking, evals — with explicit cost and latency budgets"
when_to_use: "Use when designing or auditing a RAG pipeline (KB Q&A, agentic retrieval, hybrid search, multi-modal). NOT general LLM features (ai-feature-builder), LLM ops (llmops), or ML training."
argument-hint: "[pipeline-name]"
---

# RAG Architect

Design retrieval-augmented generation pipelines that survive contact with real corpora. Cure standard: every pipeline ships with an eval set, a cost budget, and a retrieval-quality dashboard. No eval set, no ship.

## Pre-Processing (Auto-Context)

Project context, gathered before the skill runs. Values are injected inline below; in an environment that does not execute them (e.g. Gemini), run the shown commands instead.

- Portfolio: !`sed -n '1,40p' PORTFOLIO.md 2>/dev/null || echo "(no PORTFOLIO.md)"`
- Stack manifest: !`head -40 package.json 2>/dev/null || head -40 build.gradle.kts 2>/dev/null || head -20 Podfile 2>/dev/null || echo "(none detected)"`
- Recent commits: !`git log --oneline -5 2>/dev/null || echo "(not a git repo)"`
- Layout: !`ls src/ app/ lib/ functions/ 2>/dev/null | head -25`

Use this context to tailor all output to the actual project.

Additionally gather (domain-specific):
- Grep for existing RAG code: `pgvector|pinecone|qdrant|weaviate|chroma|embeddings|openai\.embeddings` to extend rather than duplicate

## Step 1: Classify the RAG Type

| Pattern | Shape |
|---------|-------|
| **Knowledge-base Q&A** | Static-ish docs, single-shot retrieval, factual answer with citations |
| **Agentic retrieval** | Agent decides what to retrieve, can call retrieval tool multiple times in a loop |
| **Hybrid search** | BM25 + vector fused, for high-recall search (legal, medical, regulatory) |
| **Multi-modal RAG** | Text + image (OCR'd PDFs, screenshots, diagrams). Embed each modality, fuse at retrieval |
| **Conversational RAG** | Multi-turn, retrieval on rewritten query (HyDE or query rewrite) not raw user message |
| **Structured RAG (Text2SQL/KG)** | Corpus is tabular/relational; embed *schema* + few-shot, generate query |

If unclear, ask: *"Static docs, or does the agent need to choose what to fetch?"*

## Step 2: Gather Context

1. **Corpus** — total document count, total tokens, avg doc length? Below 10K docs → don't overthink the vector store.
2. **Update frequency** — once at ingest, daily reindex, real-time? Drives index choice.
3. **Latency budget** — p50 and p95. Real-time chat (<500ms retrieval), agentic (1–3s OK).
4. **Recall vs precision priority** — legal/medical/compliance: recall first. Search/discovery: precision first.
5. **Cost ceiling** — per-query cost, monthly cost. Drives reranker, embedding model, top-k.
6. **Failure mode** — wrong answer with confidence (hallucination) vs "I don't know" (abstain). Drives groundedness threshold.
7. **Multi-tenant?** — namespacing requirement, per-tenant index or shared with metadata filter.
8. **Privacy** — does corpus contain PII? Drives embedding-provider choice (no third-party APIs allowed → self-host).

## Step 3: Chunking Strategy

Chunking is where most RAG pipelines fail. Pick deliberately.

| Strategy | When to Use | Tradeoff |
|----------|-------------|----------|
| **Fixed-size (tokens)** | Uniform docs, fast iteration, baseline | Splits sentences/code blocks. Almost always wrong. |
| **Recursive character** | Default starting point for prose | Better than fixed, still arbitrary boundaries |
| **Semantic** (split on embedding distance) | Heterogeneous corpus | Slow ingest, hard to debug, ~15-25% recall lift |
| **Hierarchical / parent-child** | Long docs where context matters (contracts, RFCs) | Index small chunks, retrieve, return parent. Best-quality default for serious work. |
| **Propositions** (LLM rewrites into atomic facts) | Fact-dense corpora (knowledge bases, encyclopedic) | Highest precision, expensive ingest, brittle |
| **Structural** (markdown headers, code AST, table rows) | Code, tables, structured docs | Always do this when structure exists |

### Chunk Size and Overlap

```
prose:       512–1024 tokens, 10-15% overlap (~75 tokens)
code:        symbol-aware; one function/class per chunk
chat logs:   512 tokens, by speaker turn
tables:      one row per chunk + table schema in every chunk
mixed:       hierarchical, parent doc + 256-token children
```

Overlap exists to handle facts straddling chunk boundaries. More than 25% is waste. Zero overlap will burn you on edge facts.

Always store chunk metadata: `source_id`, `doc_id`, `parent_id`, `position`, `created_at`, `tenant_id`. Filtering on metadata is your fastest precision lever.

## Step 4: Embedding Model Selection

| Model | Dim | Cost | When |
|-------|-----|------|------|
| **OpenAI text-embedding-3-small** | 1536 (truncatable) | ~$0.02/M tokens | Default. Cheap, strong English, dimensionality reduction supported. |
| **OpenAI text-embedding-3-large** | 3072 (truncatable) | ~$0.13/M tokens | When you've tuned everything else and need a recall bump |
| **Voyage voyage-3 / voyage-large** | 1024–1536 | mid | Best-in-class for English RAG (per public benchmarks); strong code variant |
| **Cohere embed-v3** | 1024 | mid | Multilingual, supports input-type hints (query vs document) |
| **BGE / E5 / nomic-embed (self-host)** | 384–1024 | infra cost only | Privacy-constrained corpora, high volume, predictable cost |
| **Jina embeddings v3** | 1024 | low | Strong long-context (8K), multilingual, self-hostable |

### Decision Rules

- **Default**: `text-embedding-3-small` at 1536 dim. Boring, works, cheap.
- **Privacy required (PHI/PII can't leave VPC)**: self-host BGE-large or nomic-embed. Eat the infra cost.
- **Multilingual non-English-dominant**: Cohere embed-v3 or Jina v3.
- **Code-heavy corpus**: Voyage code variant or specialized code embeddings.
- **Truncation**: 3-small at dim=512 is ~95% as good as dim=1536 for many corpora; halve storage cost. Always evaluate before committing.

Never mix embedding models in one index. Reindex on switch.

## Step 5: Vector Store Selection

| Store | Use When | Avoid When |
|-------|----------|------------|
| **pgvector** | Already on Postgres. <10M vectors. Want metadata filters + SQL joins. | >50M vectors with high QPS — index becomes the bottleneck. |
| **Qdrant** | Self-host preferred, complex metadata filtering, hybrid built-in. | Don't want to operate another service. |
| **Pinecone** | Want fully managed, scale to billions, predictable latency. | Cost-sensitive at low volume; egress concerns. |
| **Weaviate** | Schema-first, hybrid search, multi-modal. | Smaller team — operational complexity. |
| **Chroma** | Local dev, prototypes, <1M vectors. | Production at any meaningful scale. |
| **Vespa** | Truly web-scale, complex ranking, you have an SRE team. | Anything else — overkill. |
| **Firestore vector / BigQuery vector** | Already on GCP, low/medium QPS, <1M vectors. | Recall-critical or high QPS. See `rules/firebase.md`. |

Default: **pgvector**. Move only when you've measured a bottleneck. "We might scale" is not a reason.

Index type: HNSW for almost everyone. IVF only when memory is the constraint. Tune `m` and `ef_construction` after baseline measurement, not before.

## Step 6: Retrieval

### Hybrid Retrieval (Default for Anything Serious)

```
Query → (parallel) BM25 search + Vector search
      → Reciprocal Rank Fusion (RRF, k=60)
      → top-N candidates (e.g. 50)
      → Reranker (cross-encoder or Cohere Rerank)
      → top-K final (e.g. 5–8)
      → Construct prompt with context + cite chunks
```

BM25 alone misses paraphrase. Vector alone misses exact identifiers, codes, named entities. Together: ~15–30% recall lift over either.

### Reranking

Almost always worth it past baseline:
- **Cohere Rerank v3**: managed, good English, ~$2/1k searches
- **bge-reranker-v2-m3**: self-host, multilingual, free at infra cost
- **cross-encoder/ms-marco-MiniLM-L-12-v2**: small, fast, classic baseline

Rerank top-50 → top-8. Latency cost: 50–150ms. Quality lift: usually substantial. Measure on your eval set.

### MMR (Maximum Marginal Relevance)

Use when answers benefit from diversity (research summaries, "give me three different perspectives"). Skip for pure factual Q&A — you want the most relevant chunk, not three sort-of-relevant chunks.

```
λ = 0.5  → balanced (default)
λ = 0.7  → relevance-heavy
λ = 0.3  → diversity-heavy
```

### Query Transformation

- **HyDE**: model writes a hypothetical answer, you embed *that*, search. Big win on short/vague queries.
- **Query rewrite**: model rewrites conversational follow-ups into standalone queries. Mandatory for chat RAG.
- **Multi-query**: generate 3 variants, retrieve, fuse. Costs 3× retrieval, often worth it on tough corpora.

Don't stack all of these. Pick one based on your eval results.

## Step 7: Eval (Non-Negotiable)

No eval set, no ship. The minimum:

### Ground Truth Set

50–200 (query, expected_relevant_chunk_ids, ideal_answer) tuples. Built from:
- Real user queries (logs, surveys)
- Synthetic queries generated by an LLM from your corpus, then human-reviewed
- Edge cases the team explicitly cares about

Version-control it. Update quarterly.

### Metrics

| Metric | What It Measures | Target |
|--------|------------------|--------|
| **Recall@k** | Did we retrieve the right chunk in top-k? | >0.85 at k=10 for serious use |
| **MRR (Mean Reciprocal Rank)** | How high in results was the right chunk? | >0.6 |
| **nDCG@k** | Ranking quality (graded relevance) | track over time, no absolute target |
| **Faithfulness** (LLM judge) | Does the answer follow from retrieved context? | >0.9 |
| **Answer relevancy** (LLM judge) | Does the answer address the question? | >0.85 |
| **Context precision** | What fraction of retrieved chunks were actually relevant? | >0.7 |
| **Abstention rate** | When we should say "I don't know", do we? | track; should be nonzero on adversarial set |

Tools: `ragas`, `trulens`, `promptfoo`, or a stdlib script. Cure preference: simple Python script that emits JSON, integrated into CI. See `rules/python.md`.

### CI Integration

```
On every PR that touches:
  - Chunking config
  - Embedding model
  - Retrieval pipeline
  - System prompts
→ Run eval. Block merge if Recall@10 drops >2pp or Faithfulness drops >3pp.
```

## Step 8: Production Concerns

### Caching

- **Query-level cache**: hash(query + filters) → cached retrieval result, 5–60min TTL. Easy 10–40% latency win on repeat queries.
- **Embedding cache**: hash(text) → embedding. Critical for ingestion of slowly-changing corpora.
- **Answer cache**: only for FAQ-style — risky for personalized/contextual answers.

### Index Versioning

Every reindex creates a new namespace/index, atomic cutover, old retained for 1 release:
```
prod_v23_2026-04-29  (current)
prod_v22_2026-04-15  (previous, kept for rollback)
prod_v21_2026-04-01  (deletable)
```

Embedding model change → new index, reindex full corpus, dual-read during validation, cut over, drop old.

### Observability for Retrieval Quality

Log per query:
- query, retrieved chunk_ids, top score, score gap (top1 - top5), final answer, citations claimed, eval-judge score (sampled)

Dashboards:
- p50/p95 retrieval latency
- top-1 score distribution (drift detector)
- abstention rate over time
- "no good answer" rate (top score below threshold)
- user thumbs-down rate per topic cluster

### Retrieval Drift

Cure standard: re-run eval set weekly in production against the live index. If Recall@10 drops more than 3pp from baseline, alert. Causes: corpus updates with new vocabulary, model API changes, index corruption. See `monitoring-alert` output style for alert format.

### Cost Model (Per Query, Estimate Before Building)

```
embed_query:    1 call × small model     ~$0.00002
vector_search:  1 query                   ~$0.00010 (managed) / $0 (self-host)
rerank:         1 call × 50 candidates    ~$0.002 (Cohere)
LLM_answer:     ~2K input + 500 output    $0.005-0.030 depending on model

per-query total: typically $0.01–0.04
break-even self-host vs managed: ~30K queries/day
```

If you can't predict per-query cost within 2x, stop and model it before writing code.

## Decision Matrix Summary

| Scale / Need | Stack |
|--------------|-------|
| Prototype, <10K docs, single team | Chroma + 3-small + cosine + no rerank |
| Prod, <1M docs, on Postgres | pgvector + 3-small + RRF hybrid + Cohere rerank |
| Prod, multi-tenant, 1–50M docs | Qdrant or Pinecone + 3-large + hybrid + rerank |
| Privacy-constrained, on-prem | Qdrant self-host + BGE-large + bge-reranker-v2 |
| Web-scale, complex ranking | Vespa + custom embeddings + multi-stage ranker |

## Anti-Patterns

- **Chunking by token count without semantic awareness**. Sentences cut mid-word, code chunks split at `if (`. Use structural chunking when structure exists.
- **No eval set**. "It seems to work in our demo." It doesn't.
- **Tuning by vibes**. Changing chunk size, top-k, and prompt simultaneously, then claiming it's "better." Change one variable, measure, repeat.
- **Ignoring retrieval drift**. Corpus grows, eval set rots, recall silently degrades, users notice before you do.
- **Mixing embedding models in one index**. Cosine distances are not comparable across models. Reindex on switch.
- **Reranking the wrong stage**. Reranker takes top-50 → top-8. Reranking top-5 → top-3 is wasted spend.
- **No abstention**. Every query gets an answer, even when nothing relevant retrieved. Define a top-1-score threshold below which the system says "I don't have that information."
- **Stuffing all retrieved chunks into the prompt**. More context ≠ better answer. Past ~5–10 chunks for most LLMs, signal-to-noise drops.
- **Ignoring metadata filters**. Vector search across the whole index when `tenant_id = X` would prune 99%. Filter first, search second.
- **Re-embedding on every query**. Cache. Always.
- **No groundedness check**. Hallucinations slip through. Run an LLM judge on (answer, retrieved context) for a sample of production traffic.
- **Treating RAG as the only solution**. Sometimes the answer is "use a database" or "fine-tune". RAG is not a hammer.

## When NOT to Use This Skill

- **General AI feature work** — use `ai-feature-builder`
- **LLM operationalization, model rollout, A/B test of prompts** — use `llmops`
- **Designing the API in front of the RAG system** — use `api-architect`
- **The "corpus" is one structured database** — write SQL, don't embed it. Consider Text2SQL.
- **Search over <500 short documents** — keyword search + LLM summarization is often enough; RAG is overkill.

## Code Generation (Required)

Generate actual scaffolding using Write:

1. **Ingestion pipeline**: `src/rag/ingest.py` — load → chunk → embed → upsert with metadata
2. **Retrieval module**: `src/rag/retrieve.py` — hybrid search, RRF, optional rerank
3. **Generator**: `src/rag/generate.py` — prompt construction, citation extraction, abstention logic
4. **Eval harness**: `tests/rag/eval.py` — runs ground-truth set, emits JSON of metrics
5. **Ground truth seed**: `tests/rag/ground_truth.jsonl` — starter format with 5 example tuples
6. **Config**: `src/rag/config.py` — chunk size, model names, top-k, thresholds — all in one place
7. **Observability**: `src/rag/logging.py` — per-query log schema for retrieval analytics

Before generating, Glob `**/rag/**` and `**/embeddings/**` and Read existing modules to extend rather than duplicate.
