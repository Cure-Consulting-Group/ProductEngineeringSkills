# Product / UX Director Review

## Strengths to Keep
1. **Enforced Vertical Budget Cap:** Capping `AbovePrompt` strictly at 4 rows is a major UX win. It guarantees the user prompt remains pinned and visible regardless of laptop screen size or split-pane configurations.
2. **Fail-Closed Policy Guard Flow:** Defaulting to "Refuse the write" (Option 1) prevents accidental auto-allowances and enforces conscious human agency on compliance breaches.
3. **Ground-Truth Agent Audit:** Attaching verified git mutations to model context solves the critical problem of phantom completions and hallucinated agent tests.

## Five Defects Ranked
1. **Middle-Path Truncation on Narrow Breakpoints:** In 80-column viewports, long repository file paths (`mods/cure-policy-guard/hooks/register.ts`) will line-wrap and disrupt terminal formatting. Paths must use middle-truncation (`mods/.../register.ts`).
2. **Multi-Image Grid Cramming below 100 Columns:** Attempting to render 4 Kitty thumbnails side-by-side in a 90-column terminal results in narrow 18-column thumbnails that lose all diagram detail.
3. **Scrollback Disappearance of Toasts:** While a 10s toast for `EMPTY COMPLETION` is helpful, fast-scrolling model outputs can bury it. The verification note inside the prompt/context stream must carry a permanent warning header.
4. **Explicit Reason in Refusal Context:** When `$.ui.ask` fails or times out in headless sessions, the refusal context must clearly specify "refused by timeout/headless mode" versus "refused by human operator".
5. **Keyboard Accelerator Clarity:** Ensure that pressing `1` or `Enter` immediately executes the default "Refuse", while pressing `2` requires deliberate keying to allow.

## Contrarian Suggestion
Collapse multi-image layouts into a single focused carousel card (`Image 1 of 3 [Next: →]`) whenever terminal width is under 100 columns. Designers love multi-card grids, but in narrow terminals an individual readable image beats four unreadable slivers.

## Verdict
**FIX-FIRST** (Add middle-path truncation and <100 col image collapse rules, then ship).
