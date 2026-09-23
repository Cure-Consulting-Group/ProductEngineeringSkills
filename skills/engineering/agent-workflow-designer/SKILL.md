---
name: agent-workflow-designer
description: "Picks the shape of an LLM system: single call, workflow pattern, or autonomous agent. Use when deciding how to structure an AI feature, or when an agent is too slow, costly, or flaky."
when_to_use: "NOT for an agent's tools/memory/stop rules (agent-designer), feature code (ai-feature-builder), eval/cost ops (llmops), or Claude Code loops (engagement-automation)."
argument-hint: "[task-or-system-name]"
metadata:
  verified: 2026-09-23
---

# Agent Workflow Designer

**Outcome:** a pattern decision — the chosen shape, the decision path that led there, and a skeleton adapted to the project's stack. Done when the user can name the pattern, the reason, and the anti-patterns ruled out. This skill owns the single-call / workflow / agent decision for the library; `agent-designer` takes over once "agent" is the answer.

Scope: AI workflows *inside a product*. Automating the coding harness itself (loops, routines, hooks, CI cron) is `engagement-automation`. Pattern vocabulary follows Anthropic's "Building Effective Agents" (https://www.anthropic.com/engineering/building-effective-agents) — the model knows it; this skill adds Cure's thresholds and defaults.

## Pre-Processing (Auto-Context)

Context — run these read-only commands first; skip any that fail or aren't permitted (they only tailor the output):

- Stack: `ls package.json pyproject.toml requirements.txt go.mod build.gradle.kts Package.swift 2>/dev/null | head -5 || echo "(none detected)"`
- Existing LLM orchestration: `grep -rlE "RunnableSequence|StateGraph|orchestrator|evaluator|tool_use|tool_choice" --include=*.ts --include=*.py --exclude-dir=node_modules --exclude-dir=.git . 2>/dev/null | head -5 || echo "(none)"`

If orchestration code exists, read it and classify the current shape before recommending a new one.

## Step 1: Classify the Pattern Fit

Five workflow patterns (parallelization has two variants) plus the autonomous agent. Pick one; if you can't, go to Step 2.

| Pattern | Shape | Fits when |
|---------|-------|-----------|
| **Prompt chaining** | Sequential calls, gate between steps | Ordered, individually checkable steps |
| **Routing** | Cheap classifier picks one of N handlers | Distinct input classes with different optimal handling |
| **Parallelization — sectioning** | Independent subtasks in parallel, then aggregate | Genuinely independent work; latency matters |
| **Parallelization — voting** | Same task, several prompts/models, aggregate | Higher confidence needed; false negatives are costly |
| **Orchestrator-workers** | Planner dispatches a per-input plan to workers | Subtask list unknown until you see the input |
| **Evaluator-optimizer** | Generate, critique against a rubric, repeat | Quality criteria can be written down and checked |
| **Autonomous agent** | LLM in a loop with tools and environment feedback | Open-ended, unknown step count — last resort |

## Step 2: Gather Context

Ask only what the conversation hasn't already answered:

1. Can you write the steps down for ~90% of inputs? (yes → workflow)
2. Is there a checkable success criterion (schema, test pass, judge score)? Evaluator-optimizer requires one.
3. Latency budget: sync (<10s), async (<5 min), background?
4. Cost ceiling per task, and volume per day.
5. Failure cost: annoying, expensive, or catastrophic? Catastrophic pushes toward voting plus human review.
6. How will on-call debug a bad output?

## Step 3: Decide

### Single call vs. workflow vs. agent (canonical matrix — other skills link here)

| Signal | Single call | Workflow | Agent |
|--------|-------------|----------|-------|
| Steps known in advance | Yes | Yes | No |
| Plan adapts to intermediate results | No | No | Yes |
| Tool count | 0 | 0–3, fixed | 3–15, dynamic |
| LLM calls per task | 1 | 1–5 | commonly 10–50 |
| Cost per task (relative) | 1× | a few × | 5–50× a workflow |
| Latency | <2s | 2–10s | 10s–minutes |
| Eval and debug difficulty | Low | Medium (bisect per step) | High (trajectory traces) |

**Default to the leftmost column that works.** Cure rule: build the workflow first; migrate to an agent only when the workflow covers <70% of cases or the dispatch logic starts to look like a planner.

### Decision tree (first match wins)

```
Single LLM call with no tools does it?            → SINGLE CALL. Stop.
Steps fixed and known in advance?
  ├─ several distinct input classes               → ROUTING
  ├─ independent subtasks, need speed             → PARALLELIZATION (sectioning)
  ├─ independent, need confidence                 → PARALLELIZATION (voting)
  └─ sequential                                   → PROMPT CHAINING
Plan depends on intermediate results?
  ├─ planner can write the plan once up front     → ORCHESTRATOR-WORKERS
  ├─ checkable quality criterion exists           → EVALUATOR-OPTIMIZER
  └─ otherwise                                    → AUTONOMOUS AGENT → hand off to agent-designer
```

## Step 4: Cure defaults per pattern

The model knows the textbook shapes; these are the parameters Cure holds teams to.

| Pattern | Defaults and gotchas |
|---------|---------------------|
| Chaining | A schema-validating gate after every step; fail fast or retry once, never pass garbage forward |
| Routing | ≤7 categories; smallest model tier for the classifier; always a `fallback` handler below a confidence threshold |
| Sectioning | Only for data-independent subtasks; aggregator is its own prompt, not string concatenation |
| Voting | Distinct prompts (or models) per voter — identical prompts share a failure mode and give false consensus |
| Orchestrator-workers | Cap plan size (default 10 tasks) and validate plan length before dispatch; cache the orchestrator's system prompt |
| Evaluator-optimizer | Validate the evaluator against a human-labeled set first (it is the load-bearing piece); cap iterations at 3–5 and log "max iterations hit" |
| Agent | Stop at the decision; tools, memory, termination, and evals belong to `agent-designer` |

**Composition:** nest smaller patterns inside larger ones (router → per-branch chain; orchestrator with evaluator-optimizer workers; an agent whose tools are deterministic workflows). A workflow inside an agent's reasoning loop, or an agent inside an agent, is usually wrong — replace the inner one with a tool.

## Anti-Patterns

| Anti-pattern | Fix |
|--------------|-----|
| Agent where a workflow would do | Write the steps down; if you can, build the workflow |
| Parallelizing dependent steps | Chain them |
| Evaluator-optimizer with an unvalidated evaluator | Measure evaluator–human agreement first |
| Voting with the same prompt three times | Distinct prompts or models |
| Orchestrator with no plan cap | Cap and validate plan size |
| Agent with no termination | See agent-designer, termination step |
| Overlapping routing categories | Merge near-duplicates; low confidence → fallback |
| Chaining without gates | Validate each step's output |

## Step 5: Output

Deliver a pattern decision (inline for a quick question; `docs/architecture/pattern-decision-{name}.md` when the user wants a document):

1. Context summary (Step 2 answers)
2. Decision path through Step 3, naming the chosen pattern
3. Skeleton for the chosen pattern in the project's language
4. Composition map, if several patterns combine
5. Anti-patterns checked; justify any that apply
6. Migration plan with a kill switch, if replacing an existing shape

Match length to the need; no filler sections or restated summaries.

## Code/Artifact Generation

Applies only when the user asks to build the chosen pattern (not for a decision or a review). Detect the stack first and write in its language; extend existing orchestration code rather than duplicating it.

1. Pattern implementation (e.g. `src/llm/workflows/{pattern}.ts` or the Python equivalent)
2. Gate/validator module for chain steps or generator/evaluator handoff
3. Unit tests with mocked LLM calls: happy path, gate failure, max-iteration case
4. Ten starter eval cases — hand the eval pipeline itself to `llmops`

Related: `agent-designer` (agent internals), `ai-feature-builder` (surrounding feature), `llmops` (prompt versioning, evals, cost, guardrails), `rag-architect` (retrieval). In Claude Code these are `/cure-product-engineering:<name>`; in Codex, `$<name>`.
