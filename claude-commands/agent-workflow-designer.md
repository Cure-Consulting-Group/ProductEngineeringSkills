# Agent Workflow Designer

Pick the right shape before you build. Most production AI failures come from picking an autonomous agent when a workflow would do, or stacking tools onto a workflow that needed an agent. This skill walks the decision and shows the implementation pattern for each shape.

Built from Anthropic's "Building Effective Agents" framework (docs.anthropic.com). Companion skills: `/agent-designer` for designing the internals of an autonomous agent once you've decided one is needed; `/ai-feature-builder` for the broader feature scaffold; `/llmops` for prompt versioning, evals, and cost guardrails on whatever you ship.

**Scope boundary:** this skill designs AI workflows *inside a product you're building*. If the question is how to automate Claude Code itself — recurring loops, scheduled cloud routines, hooks, CI cron — that's harness orchestration: use `/engagement-automation` instead.

## Pre-Processing (Auto-Context)

Before starting, gather project context silently:
- Read `PORTFOLIO.md` if it exists in the project root or parent directories for product/team context
- Run: `cat package.json 2>/dev/null || cat build.gradle.kts 2>/dev/null || cat Podfile 2>/dev/null` to detect stack
- Run: `git log --oneline -5 2>/dev/null` for recent changes
- Run: `ls src/ app/ lib/ functions/ 2>/dev/null` to understand project structure
- Grep for existing LLM patterns: `chain|router|orchestrator|evaluator|tool_use|@chain|RunnableSequence` to detect current shape
- Use this context to tailor all output to the actual project

## Step 1: Classify the Pattern Fit

There are six shapes. Pick exactly one. If you can't decide, you don't have enough context — go to Step 2.

| Pattern | Shape | When |
|---------|-------|------|
| **Prompt chaining** | Sequential LLM calls, each consuming the previous output, optional gates between | Decomposable into ordered steps; each step is verifiable |
| **Routing** | Classifier LLM picks one of N specialized downstream paths | Distinct input categories with different optimal handling |
| **Parallelization (sectioning)** | Split task into independent subtasks, run in parallel, aggregate | Subtasks are genuinely independent, latency matters |
| **Parallelization (voting)** | Same task to multiple LLMs/prompts, aggregate by majority or scoring | Need higher confidence than one call gives; safety-critical |
| **Orchestrator-workers** | Planner LLM dynamically dispatches subtasks to workers, synthesizes results | Subtask shape is dynamic, planned per input |
| **Evaluator-optimizer** | Generator LLM produces, evaluator LLM critiques, loop until criteria met | Iterative refinement where quality criteria are checkable |
| **Autonomous agent** | LLM in a loop with tools, dynamic plan, environment feedback | Open-ended task, unknown step count, requires environment interaction |

## Step 2: Gather Context

1. **Task structure** — can you write the steps down? If yes, you don't need an agent. If you can write them down with branches, you need a workflow.
2. **Predictability** — does the same input always need the same sequence of operations? (yes = workflow; no = agent)
3. **Evaluation availability** — is there a checkable success criterion (schema match, test pass, judge score)? Evaluator-optimizer requires this.
4. **Latency tolerance** — sync (<10s), async (<5min), background (hours)?
5. **Cost ceiling** — max dollars per task. Drives serial-vs-parallel and model tier choices.
6. **Failure cost** — wrong answer is annoying / expensive / catastrophic? Catastrophic pushes toward voting and human-in-the-loop.
7. **Volume** — requests per day. High volume + low complexity per call = chaining; low volume + high complexity = agent.
8. **Observability** — how will you debug a bad output? Workflows are inspectable per step; agents need trajectory traces.

## Step 3: Pattern Selection Decision Tree

Walk top to bottom. First match wins.

```
Can the task be done in a single LLM call with no tools?
├── Yes → use a single LLM call. Stop. Don't read further.
└── No
   │
   Are the steps fixed and known in advance?
   ├── Yes → workflow
   │  │
   │  Is there one input class or several?
   │  ├── Several distinct classes → ROUTING
   │  └── One class
   │     │
   │     Are subtasks independent?
   │     ├── Yes, run-in-parallel → PARALLELIZATION (sectioning)
   │     ├── Yes, want-higher-confidence → PARALLELIZATION (voting)
   │     └── No, sequential → PROMPT CHAINING
   │
   └── No, plan depends on intermediate results
      │
      Can a planner write the plan once at the start?
      ├── Yes → ORCHESTRATOR-WORKERS
      └── No
         │
         Is there a checkable quality criterion?
         ├── Yes → EVALUATOR-OPTIMIZER
         └── No → AUTONOMOUS AGENT (last resort)
```

**Bias toward workflows.** Agents cost 5–50x more per task and are 5–50x harder to debug. Earn the agent.

## Step 4: Implementation Patterns

Pseudocode for each shape. Use as the architectural skeleton; flesh out with the project's LLM client.

### 4.1 Prompt Chaining

```
input
  → llm_call_1(input) → step_1_output
  → optional gate: if not valid(step_1_output) then fail or retry
  → llm_call_2(step_1_output) → step_2_output
  → optional gate
  → llm_call_3(step_2_output) → final
```

Use when: marketing copy → translate; outline → draft → edit; extract → transform → format.

```typescript
async function chain(input: Input): Promise<Output> {
  const step1 = await llm("step-1-prompt", { input });
  if (!validateStep1(step1)) throw new ChainError("step-1 invalid", step1);
  const step2 = await llm("step-2-prompt", { previous: step1 });
  if (!validateStep2(step2)) throw new ChainError("step-2 invalid", step2);
  return await llm("step-3-prompt", { previous: step2 });
}
```

Notes: gates between steps are non-negotiable. They're how you stop garbage from compounding.

### 4.2 Routing

```
input
  → classifier_llm(input) → category
  → switch(category):
       "billing" → billing_handler(input)
       "support" → support_handler(input)
       "sales"   → sales_handler(input)
       default   → fallback_handler(input)
```

Use when: customer-service triage; question-type routing in RAG; cheap-vs-expensive model selection.

```typescript
async function route(input: Input): Promise<Output> {
  const category = await llm("classifier-prompt", { input, allowedCategories });
  const handler = handlers[category] ?? handlers.fallback;
  return await handler(input);
}
```

Notes: cap categories at ~7. Use a small/cheap model for the classifier — that's the whole point. Always include a `fallback` for low-confidence classifications.

### 4.3 Parallelization — Sectioning

```
input
  → split into independent subtasks [s1, s2, s3]
  → parallel: [llm(s1), llm(s2), llm(s3)] → [r1, r2, r3]
  → aggregator(r1, r2, r3) → final
```

Use when: long-doc summarization (chunk + map + reduce); multi-criteria evaluation; checking distinct rules in parallel.

```typescript
async function sectionParallel(input: Input): Promise<Output> {
  const sections = split(input);
  const results = await Promise.all(sections.map(s => llm("section-prompt", { section: s })));
  return await aggregate(results);
}
```

### 4.4 Parallelization — Voting

```
input
  → parallel: [llm_v1(input), llm_v2(input), llm_v3(input)] → [r1, r2, r3]
  → vote(r1, r2, r3) → final  (majority, or score-and-pick)
```

Use when: code review where false negatives are expensive; classification with high cost of error; safety filtering.

```typescript
async function vote(input: Input): Promise<Output> {
  const variants = ["safe-prompt-v1", "safe-prompt-v2", "safe-prompt-v3"];
  const votes = await Promise.all(variants.map(p => llm(p, { input })));
  return majorityVote(votes);
}
```

Notes: use **different prompts** for the voters, not the same prompt three times — same prompt → same failure mode → false consensus.

### 4.5 Orchestrator-Workers

```
input
  → orchestrator_llm(input) → plan: [task_1, task_2, ...] (dynamic)
  → for each task: assign to worker_llm(task) → result
  → orchestrator_llm(plan, results) → final
```

Use when: research tasks with unknown breadth; coding tasks where the file list isn't known in advance; multi-source data assembly.

```typescript
async function orchestrate(input: Input): Promise<Output> {
  const plan = await llm("planner-prompt", { input });  // returns array of tasks
  const results = await Promise.all(plan.tasks.map(t => llm("worker-prompt", { task: t })));
  return await llm("synthesizer-prompt", { plan, results });
}
```

Notes: cap plan size (e.g., max 10 tasks). Bound worker iteration. The orchestrator is the most expensive call — cache its system prompt.

### 4.6 Evaluator-Optimizer

```
draft = generator_llm(input)
loop up to N:
  feedback = evaluator_llm(draft, criteria)
  if feedback.acceptable: return draft
  draft = generator_llm(input, draft, feedback)
return draft (with note: "max iterations hit")
```

Use when: literary translation; iterative code refinement against tests; document quality where you can write the rubric down.

```typescript
async function evalOptimize(input: Input): Promise<Output> {
  let draft = await llm("generator-prompt", { input });
  for (let i = 0; i < MAX_ITERATIONS; i++) {
    const verdict = await llm("evaluator-prompt", { input, draft, rubric });
    if (verdict.acceptable) return draft;
    draft = await llm("generator-prompt", { input, prevDraft: draft, feedback: verdict.feedback });
  }
  return draft;  // log: max-iterations-hit
}
```

Notes: **the evaluator is the load-bearing piece.** A weak evaluator produces an infinite loop of bad drafts that pass. Validate the evaluator on a labeled set before trusting it. Cap iterations (3–5 typical).

### 4.7 Autonomous Agent

```
state = initial(input)
loop until stop_condition:
  thought, tool_call = llm(state, tools)
  result = execute_tool(tool_call)
  state = update(state, thought, tool_call, result)
return state.final_answer
```

For the design of the agent itself — tool schemas, memory, termination, evals — use **`/agent-designer`**. This skill stops at the decision to use one.

## Step 5: Composition

Real systems compose patterns. A few common stacks:

- **Router → Workflow per branch.** Classifier picks "FAQ" → chain; "complex query" → orchestrator-workers.
- **Chain with parallel section.** Chain step 2 fans out to a sectioning parallel, then continues.
- **Orchestrator with evaluator-optimizer workers.** Each worker iterates against a rubric before returning to the orchestrator.
- **Agent with workflow tools.** An autonomous agent's "tools" can themselves be deterministic workflows (e.g., a tool `summarize_doc` is internally a sectioning pattern).

Rule: **compose smaller patterns inside larger ones, not the reverse.** An agent inside a workflow step is fine. A workflow inside an agent's reasoning loop is rare and usually wrong (you've turned a workflow back into ad-hoc planning).

## Step 6: Choosing Between Agent and Workflow

The same decision through three lenses. If two of three say "workflow," pick workflow.

### Predictability

- Can you write the steps down for 90% of inputs? → **workflow**
- Can you only write down "here are the tools, figure it out"? → **agent**
- Can you write some steps down but not others? → **workflow with an agent step inside one node**

### Cost

- Workflows: predictable token cost per run; usually 1–5 LLM calls.
- Agents: variable token cost; commonly 10–50 LLM calls per task; 5–50x workflow cost.
- If 10x cost is unacceptable, you need a workflow even if the agent would be more elegant.

### Observability

- Workflows: each step logged separately, easy to bisect failures, easy to A/B prompts per step.
- Agents: trajectory logs only — debugging is reading 30-step traces. Eval is harder. Production debugging is much harder.
- If on-call has to debug this at 2am, prefer the workflow.

### The honest test

Build a workflow first. If it covers <70% of cases or the dispatch logic itself starts looking like a planner, *now* migrate to an agent. Don't start with the agent.

## Anti-Patterns

| Anti-pattern | Why it fails | Fix |
|--------------|--------------|-----|
| Using an agent when a workflow would do | 10x cost, 10x latency, 10x debug pain, no quality gain | Write the steps down. If you can, build the workflow. |
| Parallelizing dependent steps | Step 2 needs step 1's output; parallelism corrupts state | Use chaining, not parallelization. Reserve parallel for genuinely independent work. |
| Evaluator-optimizer with no real evaluator | Loop runs to max iterations, returns garbage that "passed" | Validate the evaluator on a labeled set before trusting it. Score evaluator agreement with humans first. |
| Voting with the same prompt three times | All three voters share the same failure mode → false consensus | Use distinct prompts (or distinct models) for voters. |
| Orchestrator with no plan cap | Planner emits 50 tasks for a small input; cost explodes | Cap plan size. Validate plan length before dispatching workers. |
| Agent with no termination | Loop runs until budget is exhausted | Iteration cap, cost cap, wall-clock cap, repetition detector. See `/agent-designer` Step 5. |
| Routing with overlapping categories | Classifier flips between two equally good categories; UX is non-deterministic | Tighten category definitions; merge near-duplicates; lower confidence threshold triggers fallback. |
| Chaining without gates | Step 1 returns garbage; step 2 confidently transforms garbage; user sees confident garbage | Validate each step's output. Fail fast or retry, don't pass through. |
| Composing agent-inside-agent | Inner agent loop consumes context; outer agent loses track | Replace inner agent with a tool (deterministic or workflow). |

## When NOT to Use This Skill

- You've already chosen a pattern and need internal design of an autonomous agent → `/agent-designer`
- You're building the AI feature scaffold (LLM client, prompts, guardrails) → `/ai-feature-builder`
- You're operationalizing prompts, evals, cost controls for a built feature → `/llmops`
- You're choosing between LLM providers or model sizes → that's a model-selection question, not a pattern question
- The task fits in one LLM call — there's no workflow to design

## Step 7: Output

Produce a `pattern-decision.md` with:

1. **Context summary** — answers to all 8 Step 2 questions
2. **Decision-tree walk** — show the path through Step 3; name the chosen pattern
3. **Implementation skeleton** — pseudocode from Step 4 for the chosen pattern, adapted to the project's stack
4. **Composition map** (if applicable) — how this pattern composes with others in the system
5. **Anti-pattern review** — confirm none of the Step 6 anti-patterns apply; if one does, justify
6. **Migration plan** (if upgrading from a previous shape) — current → target, with a kill switch

## Code Generation (Required)

Generate scaffolding using Write, scoped to the chosen pattern:

1. **Pattern skeleton**: `src/llm/workflows/{pattern}.ts` — typed implementation of the chosen pattern
2. **Validators / gates**: `src/llm/workflows/validators.ts` — schema validation between chain steps or between generator and evaluator
3. **Pattern test harness**: `tests/workflows/{pattern}.test.ts` — unit tests with mocked LLM calls covering happy path, gate failure, max-iteration cases
4. **Eval starter**: `evals/workflows/{pattern}.eval.ts` — golden-dataset eval scaffolding (10 starter cases)
5. **Pattern-decision doc**: `docs/architecture/pattern-decision-{name}.md` — the Step 7 output

Before generating, Grep for existing patterns (`chain|router|orchestrator|evaluator|tool_use`) and Read them to extend rather than duplicate.

Cross-references: `/agent-designer` for the internals once you've picked autonomous agent. `/ai-feature-builder` for the surrounding LLM feature scaffold. `/llmops` for prompt versioning, CI eval, cost monitoring, and guardrails on whatever pattern ships. See docs.anthropic.com for the source framework and current model recommendations.
