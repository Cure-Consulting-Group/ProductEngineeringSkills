# Skill review rubric — Wave 5 (Opus 5.5 / Codex / Antigravity), 2026-09-23

Repo: /Volumes/CureVault/projects/ProductEngineeringSkills. Read-only review: do NOT edit any repo file.

Context: frontier models (Claude Opus 5.5, GPT-5.6, Gemini 3.x) already know generic engineering/business
knowledge. A skill earns its context only by adding what the model does NOT reliably do unprompted:
Cure-specific standards and decisions, non-obvious gotchas, current facts newer than training, a
deterministic procedure/script, or an output contract. The same SKILL.md is loaded by Claude Code
(plugin), Codex (plugin install from skills/, ignores Claude-only frontmatter), and Antigravity/Gemini
(Agent Skills standard; name+description only; `!`cmd`` injection renders as literal text).

Score each skill 1–5 on each dimension, then list concrete findings (quote line numbers):

1. **Signal density** — % of body that is Cure-specific / non-obvious vs. textbook material the model
   already knows (e.g. "What is a REST API", generic checklists, restated OWASP). Flag padding.
2. **Instruction style for modern models** — explains *why* rather than bare commands; no ALL-CAPS
   shouting / over-emphasis (Opus 4.5+ over-triggers on it); no rigid step scripts where judgment is
   better; clear stopping/done criteria; output contract defined. Flags over-prescription.
3. **Trigger quality** — description says what + when, distinct from sibling skills (name the
   overlapping sibling if any), would the model pick it correctly from a list of 103.
4. **Currency / correctness** — stale versions, APIs, model IDs, prices, laws/tax figures, dates;
   factual errors; broken relative links (check that referenced sibling files exist).
5. **Cross-runtime portability** — depends on Claude-only mechanics without a fallback: `!`cmd``
   injection whose output is irrelevant to this skill's domain (e.g. package.json for a tax skill),
   Claude tool names (Agent/Skill/Task/AskUserQuestion/WebSearch) without neutral phrasing,
   `context: fork` reliance, `$ARGUMENTS`, references to hooks/agents/output-styles that don't exist
   in Codex/Antigravity, paths like `.claude/`. Note guardrail prose presence for read-only skills.
6. **Progressive disclosure** — body size justified; long reference pushed to sibling files; sibling
   files actually referenced with guidance on when to read them.

Output (write to the file path given in your prompt) as Markdown:
- A table: skill | S1..S6 | total/30 | one-line verdict (KEEP / TIGHTEN / REWRITE / MERGE-INTO:<x> / DEPRECATE)
- Per skill with any score ≤3: 2–5 bullet findings with file:line evidence and a concrete fix.
- A "cross-cutting patterns" section: issues recurring in ≥3 skills, with counts.
- A "top 10 highest-leverage fixes" list for your slice.
Be skeptical and specific; no praise padding. Verify every claim against the file before writing it.
