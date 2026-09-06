# Three-Perspective Design Review

For substantive assignments, three complementary perspectives review the work. They do not produce three versions of the same output and they do not vote. Constructive disagreement first, then one design direction from the architect (you).

## Perspectives

| Perspective | Owns | Asks |
|---|---|---|
| Creative Director | concept, originality, brand, art direction, storytelling, emotional resonance | Is there one idea? Could another product look identical? What is memorable? Where is it generic? |
| Product / UX Director | hierarchy, flows, usability, platform conventions, interaction, accessibility, responsive behaviour, scrolling | Is the primary action obvious? Does it feel native? What breaks at 200 percent text or 320 px? Which state is missing? |
| Design Systems / Production Director | components, tokens, consistency, states, scalability, implementation cost, asset completeness | Which values are not tokens? Which components lack states? What costs more to build than it returns? Which assets are missing? |

Each reviewer returns, in under 400 words: three strengths to keep, the five most important defects ranked, one thing they would change that the others will probably dislike, and a verdict (`ship`, `fix-first`, `rethink`).

## Routing

| Environment | How the three run |
|---|---|
| Claude Code, base library only | three parallel subagents (`general-purpose`), each given one perspective prompt from `design_review_panel.py --emit` plus the artefacts |
| Claude Code with `cure-tri-lane` installed | Creative Director stays with the architect's model family; Product/UX to the `codex-reviewer` lane; Systems/Production to the `antigravity-analyst` lane, so each verdict comes from a different model family |
| Any terminal with CLIs | `design_review_panel.py --run` executes the perspectives on `claude`, `codex`, and `gemini` from PATH, one perspective per backend where available, falling back to whichever backends exist |

Different model families per perspective are preferred: self-review from one family agrees with itself.

## Synthesis (the architect's job)

1. Label every finding `Confirmed`, `Disputed`, or `Unverified` against the artefacts. Reviewers over-state; zero confirmed defects is a valid outcome.
2. Where perspectives conflict, decide by the register (expressive vs utility) and the ten questions; write the decision and the losing argument in the decision record.
3. Fold the strongest ideas into one coherent design. Do not average them.
4. Fix confirmed defects, then run the critique gate in `critique-and-quality-bar.md`.
5. One panel per deliverable. Re-run only the perspective whose defects were fixed.
