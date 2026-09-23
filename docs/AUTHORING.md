# AUTHORING — How a Cure skill is written (Wave 5 standard, 2026-09-23)

One SKILL.md is loaded by three runtimes: **Claude Code** (plugin), **Codex** (plugin, reads
`name` + `description` only), and **Antigravity** (flat plugin export, reads `name` +
`description`, honors `disable-model-invocation`). It is read by frontier models (Opus 5.5,
GPT-5.6, Gemini 3.x) that already know textbook engineering and business. Evidence for every
rule below: `docs/evaluations/2026-09-23/platform-facts.md`.

A skill earns its context only by adding what the model does not reliably do unprompted:
**Cure decisions and defaults, non-obvious gotchas, facts newer than training, a deterministic
procedure or script, and an output contract.** Everything else is rent.

## 1. Frontmatter

```yaml
---
name: accessibility-audit
description: "WCAG 2.2 AA audit of web and mobile UI. Use when reviewing screens, components, or a release for accessibility; outputs severity-ranked findings with fixes."
when_to_use: "NOT for design-system token work (design-system) or visual design (design-studio)."
argument-hint: "[path-or-url]"
metadata:
  verified: 2026-09-23
---
```

- **`description` is the trigger in every runtime.** First sentence ≤100 chars says *what*;
  the "Use when…" clause must start within the first **110 chars** (Codex truncates there at
  our library size). Third person, concrete key terms a user would type. ≤300 chars.
- **`when_to_use` is Claude-only.** Use it only for disambiguation ("NOT for… use X"). Never
  put the only trigger there. Combined description + when_to_use ≤350 chars.
- **`metadata.verified`**: the date someone last checked the skill's versions, prices, laws,
  and API names against a primary source. Set it only when you actually did that check.
- Keep existing Claude fields (`argument-hint`, `allowed-tools`, `disallowed-tools`,
  `context: fork`, `paths`, `disable-model-invocation`, `user-invocable`). Frontmatter must
  parse as strict YAML — a parse error silently drops the skill in Codex and Antigravity.

## 2. Context gathering (the `` !`cmd` `` block)

Injection runs only in Claude Code; Codex and Antigravity show the line as literal text.

- Inject **only what changes the output** of *this* skill. A tax, legal, marketing, sales, or
  comms skill does not need `package.json` or `git log`. Many skills need nothing at all.
- Every injected command is bounded (`head -n 20`, `2>/dev/null || echo "(none)"`) and the
  whole block stays ≤10 lines of output.
- Always introduce the block with the portable line:
  `Context (pre-filled in Claude Code; in other runtimes run these commands first):`
- Don't rely on `$ARGUMENTS` / `$0` substitution in prose — they stay literal outside Claude.
  Escape literal dollars before digits as `\$` (CLAUDE.md).

## 3. Body: outcome first, judgment over scripts

Keep the house format — Step 1 (Classify), Step 2 (Gather Context), Step 3+ — but:

- **Open with the outcome and the done criteria** in 2–4 lines: what a finished result looks
  like and when to stop.
- **Classify drives output.** Generation sections ("Code/Artifact Generation") run only when
  the Step-1 classification calls for building. A review, question, or live incident gets
  findings or an answer, not scaffolding. Title such sections `## Code/Artifact Generation`
  with a first line stating when they apply — never "(Required)".
- **No verification scaffolding.** Delete "double-check", "re-verify before responding", "use a
  subagent to verify", "include a final verification step". Opus 5 verifies on its own; the
  instructions cause over-verification (Anthropic, Opus 5 prompting guide). Keep *domain*
  acceptance criteria ("migration has a tested down path") — those are facts, not nagging.
- **Emphasis only for real invariants** (security, legal, money, irreversible actions), and
  say *why* in the same sentence. No ALL-CAPS for style. All three vendors say emphatic
  language over-triggers modern models.
- **Scope.** For narrow skills, say what not to do: "Deliver the requested artifact; don't
  refactor adjacent code or add unrequested sections."
- **Reviews and audits report everything they find**, each with severity and confidence;
  ranking or filtering happens after. Never "only report high-severity issues" — Opus 5 follows
  it literally and misses real bugs.
- **Delegation.** Suggest subagents only for large, independent, parallel work, and say so
  explicitly (Codex won't spawn unless told; Opus 5 over-spawns unless bounded).
- **Written deliverables**: add one calibration line — "Match length to the need; no filler
  sections or restated summaries."
- **Cut the textbook.** If a section restates what any senior practitioner (or the model)
  knows — REST basics, OWASP definitions, generic checklists — delete it or replace it with the
  Cure decision, the gotcha, or the threshold that is specific.
- **One source of truth.** When another skill owns a policy (coverage thresholds →
  `testing-strategy`; design tokens (W3C DTCG `$value`) → `design-studio`; MTTR definition →
  `dora-metrics`; OpenAPI 3.1 → `api-architect`), link to it instead of restating it.

## 4. Runtime-neutral wording

| Instead of | Write |
|---|---|
| "Use the WebSearch tool" | "Search the web (current sources, dated)" |
| "Use AskUserQuestion" | "Ask the user" |
| "Spawn an Agent / Task" | "Delegate to a subagent (if your runtime supports it)" |
| "`/cure-product-engineering:foo`" only | "the `foo` skill (`/cure-product-engineering:foo` in Claude Code, `$foo` in Codex)" — once per skill is enough |
| `.claude/…` paths as the only option | Claude path + neutral fallback |

## 5. Progressive disclosure

- SKILL.md ≤500 lines; aim for ≤300. Long tables, templates, and examples go to
  `reference/<topic>.md`, one level deep.
- Every pointer says **when** to read it: "Read the webhooks reference file when the
  integration handles subscriptions." Never "See reference/details.md for full detail."
- Don't move the core procedure out of the body — the body must be usable on its own.

## 6. Currency

- Versions, prices, API names, tax/legal thresholds, and model IDs are checked against a
  primary source before they are written, and dated (`metadata.verified`, or inline
  "(verified 2026-09-23, source)" for annually indexed figures).
- If it can't be confirmed, write "confirm before use", not a guess.
- Don't bake a year into search queries; say "current".
