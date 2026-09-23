---
name: rag-architect
description: "Designs RAG pipelines: chunking, embeddings, vector store, reranking. Use when building or auditing retrieval over documents, a knowledge base, or semantic search with retrieval evals."
when_to_use: "NOT for general LLM features (use ai-feature-builder), prompt evals/cost/routing (use llmops), or agent design (use agent-designer)."
argument-hint: "[pipeline-name]"
metadata:
  verified: 2026-09-23
---

# RAG Architect

**Outcome:** a RAG design (or audit) with chosen chunking, embedding model, store, retrieval chain, eval set, per-query cost, and abstention rule — each choice justified against the corpus and budgets from Step 2. Done when the per-query cost is predictable within 2× and there is an eval that would catch a recall regression. Cure standard: no eval set, no ship. Match length to the need; no filler sections or restated summaries.

This skill owns retrieval quality, index drift, and chunking. Prompt evals, model routing, and LLM spend belong to `llmops`.

## Pre-Processing (Auto-Context)

Context (pre-filled in Claude Code; in other runtimes run these commands first):

- Language/stack: !`ls package.json pyproject.toml requirements.txt go.mod 2>/dev/null | head -4 || echo "(none detected)"`
- Existing retrieval code: !`grep -rlE 'pgvector|pinecone|qdrant|weaviate|chroma|embeddings\.create|embed\(' --include=*.py --include=*.ts . 2>/dev/null | grep -v node_modules | head -8 || echo "(none)"`

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

Choose by criteria, then confirm the current lineup and price on the vendor page — embedding generations turn over yearly. Lineup as checked 2026-09-23 (confirm before quoting prices):

| Criterion | Options (current generation) |
|---|---|
| Cheap managed default, English-heavy | OpenAI `text-embedding-3-small` (still OpenAI's current generation; truncatable dims) |
| Highest managed retrieval quality, general or code | Voyage `voyage-4` / `voyage-4-large` (superseded voyage-3.5 in 2026); Voyage code variants for code corpora |
| Multilingual or multimodal (text + images/PDF pages) | Cohere Embed v4 |
| PHI/PII can't leave the VPC, or very high volume | Self-hosted open models (BGE, E5, nomic, Jina, Qwen embedding families) — pick from the current MTEB retrieval leaderboard, then verify on your eval set |

Decision rules:
- Run your own 50–200-query eval on 2–3 candidates before committing; public benchmark rank rarely survives domain corpora unchanged.
- Truncated dimensions (Matryoshka-style, e.g. 512 of 1536) often keep ~95% of recall at a third of the storage — measure it.
- Never mix embedding models in one index; cosine scores aren't comparable across models. A model switch is a full reindex.

## Step 5: Vector Store Selection

| Store | Use When | Avoid When |
|-------|----------|------------|
| **pgvector** | Already on Postgres. <10M vectors. Want metadata filters + SQL joins. | >50M vectors with high QPS — index becomes the bottleneck. |
| **Qdrant** | Self-host preferred, complex metadata filtering, hybrid built-in. | Don't want to operate another service. |
| **Pinecone** | Want fully managed, scale to billions, predictable latency. | Cost-sensitive at low volume; egress concerns. |
| **Weaviate** | Schema-first, hybrid search, multi-modal. | Smaller team — operational complexity. |
| **Chroma** | Local dev, prototypes, <1M vectors. | Production at any meaningful scale. |
| **Vespa** | Truly web-scale, complex ranking, you have an SRE team. | Anything else — overkill. |
| **Firestore vector / BigQuery vector** | Already on GCP, low/medium QPS, <1M vectors. | Recall-critical or high QPS. |

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

Almost always worth it past baseline. Current options (checked 2026-09-23; confirm pricing): managed Cohere Rerank 4 (Pro/Fast, 32K context, 100+ languages) or Voyage `rerank-2.5` / `rerank-2.5-lite` (instruction-following); self-hosted `bge-reranker-v2-m3` (multilingual) or a small MS MARCO cross-encoder as the baseline.

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

## Step 7: Eval

The minimum before shipping:

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

Tools: `ragas`, `trulens`, `promptfoo`, or a plain script in the project's language that emits JSON and runs in CI (Cure preference: the plain script).

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

Cure standard: re-run eval set weekly in production against the live index. If Recall@10 drops more than 3pp from baseline, alert. Causes: corpus updates with new vocabulary, model API changes, index corruption. Wire the alert through the project's monitoring stack (`observability` skill).

### Cost Model (Per Query, Estimate Before Building)

Illustrative magnitudes — re-price from current vendor pages when estimating; LLM answer cost comes from `llmops`.

```
embed_query:    1 call × small model     ~\$0.00002
vector_search:  1 query                   ~\$0.00010 (managed) / \$0 (self-host)
rerank:         1 call × 50 candidates    ~\$0.002 (Cohere)
LLM_answer:     ~2K input + 500 output    \$0.005-0.030 depending on model

per-query total: typically \$0.01–0.04
break-even self-host vs managed: ~30K queries/day
```

If you can't predict per-query cost within 2x, stop and model it before writing code.

## Decision Matrix Summary

| Scale / Need | Stack |
|--------------|-------|
| Prototype, <10K docs, single team | Chroma + cheap managed embedding + cosine + no rerank |
| Prod, <1M docs, on Postgres | pgvector + managed embedding + RRF hybrid + managed rerank |
| Prod, multi-tenant, 1–50M docs | Qdrant or Pinecone + top-quality embedding + hybrid + rerank |
| Privacy-constrained, on-prem | Qdrant self-host + self-hosted embedding + bge-reranker-v2-m3 |
| Web-scale, complex ranking | Vespa + custom embeddings + multi-stage ranker |

## Anti-Patterns (Cure review checklist)

- Token-count chunking where structure exists (code split at `if (`, tables split mid-row).
- Tuning chunk size, top-k, and prompt at once — change one variable per eval run.
- Reranking top-5 → top-3 (wasted spend); rerank top-50 → top-8.
- No abstention threshold: define a top-1-score floor below which the answer is "I don't have that information."
- Stuffing every retrieved chunk into the prompt; past ~5–10 chunks signal-to-noise drops.
- Vector search across the whole index when a `tenant_id` filter would prune 99% — filter first.
- No sampled groundedness judge on production answers.

## When NOT to Use This Skill

- **General AI feature work** — use `ai-feature-builder`
- **LLM operationalization, model rollout, A/B test of prompts** — use `llmops`
- **Designing the API in front of the RAG system** — use `api-architect`
- **The "corpus" is one structured database** — write SQL, don't embed it. Consider Text2SQL.
- **Search over <500 short documents** — keyword search + LLM summarization is often enough; RAG is overkill.

## Code/Artifact Generation

Applies only when the request is to build (not design or audit) and the user wants files. Match the project's language (Python or TypeScript per the stack line above); extend existing retrieval modules found above instead of duplicating them. Typical set, under `src/rag/`: ingest (load → chunk → embed → upsert with metadata), retrieve (hybrid + RRF + optional rerank), generate (context assembly, citations, abstention), config (chunking, model names, top-k, thresholds in one place), per-query log schema; plus `tests/rag/` eval harness and a 5-case ground-truth seed.
