# Interview System Designer

Hiring is a system. Most engineering loops are not designed — they are accreted, copied from a previous employer, and never measured. This skill produces a loop that is calibrated to the role, defensible to candidates, and predictive of on-the-job performance. Cure ships these to clients who ask "help us hire engineers" and get a working interview system instead of a folder of leetcode questions.

## Pre-Processing (Auto-Context)

Before starting, gather context silently:
- Read `PORTFOLIO.md` if it exists in the project root or parent directories for product/team context
- Glob for: `INTERVIEW*.md`, `HIRING*.md`, `interview-loop*`, `rubric*` to find any existing materials
- Run: `git log --oneline -5 2>/dev/null` for recent context
- Note the client's stack so technical questions match the actual job (don't ask Rust questions for a TypeScript role)

## Step 1: Classify the Engagement

| Engagement Type | Trigger | Primary Deliverable |
|-----------------|---------|---------------------|
| Greenfield loop | New role, no existing process | Full loop design + rubrics + question bank + interviewer training plan |
| Calibration | Existing loop, but pass rate / accept rate / 6-month performance is off | Diagnosis + targeted fixes (one or two stages, not full rewrite) |
| Leaky loop fix | Specific failure mode (e.g., high attrition, gender skew, post-onsite ghosting) | Root-cause analysis + targeted intervention |
| Per-role tier | Senior IC / EM / Staff+ / New grad / Contractor | Loop tuned to the seniority, signal set, and time budget |

Cross-classify on the role tier. A senior IC loop and an EM loop share scaffolding but have different stages and rubrics. State both axes before designing.

## Step 2: Gather Context

1. **Role definition** — what does this person own in their first 6 months? If the client can't answer in two sentences, the role isn't ready to interview for.
2. **Must-have signals** — the 3-5 things they will demonstrably do every week. Examples: "ships production code under deadline pressure," "navigates ambiguous specs," "mentors juniors in PR review."
3. **Nice-to-have signals** — the 2-3 differentiators. Examples: "has shipped on Kubernetes," "speaks publicly," "has worked in regulated industries."
4. **Current bottleneck** — what's actually broken? Common framings:
   - **Low top-of-funnel pass rate** (everyone fails phone screen) → screen is miscalibrated or sourcing is off.
   - **Low onsite pass rate** → either screen is too easy or onsite stages don't match what the screen suggested they'd test.
   - **Low offer accept** → process feels bad to candidates, comp is off, or close is weak.
   - **Poor 6-month performance correlation** → loop measures the wrong things.
5. **Interviewer pool** — how many people, what seniority mix? A loop that requires 4 staff engineers for every onsite is a loop that won't run.
6. **Time budget** — total candidate time end-to-end. Senior IC: 4-6 hours of interviewing. Staff+: 6-8 hours plus a take-home or async exercise. Contractor: 90 minutes max.
7. **Compliance constraints** — EEOC, ban-the-box, salary history bans, geographies with specific rules.

## Step 3: Loop Design

### Default Senior IC Loop (Tune Per Role)

```
Stage 1 — Recruiter screen (30 min, phone)
  Signals: minimum bar (years, location, comp, work auth), motivation
  Pass rate target: 50-70% from sourced funnel

Stage 2 — Hiring manager screen (45 min, video)
  Signals: career narrative coherence, role fit, calibrated against JD
  Pass rate target: 40-60% from Stage 1

Stage 3 — Technical screen (60 min, video, code-share)
  Signals: live problem-solving, code reading, communication while coding
  Pass rate target: 30-50% from Stage 2

Stage 4 — Onsite loop (3-5 stages, ~4-6 hours total, ideally one block)
  Stage 4a — Coding (60 min): tighter scope than screen, focus on tradeoffs
  Stage 4b — System design (60 min): scoped to seniority
  Stage 4c — Behavioral / values (45 min): STAR-style
  Stage 4d — Domain-specific (45-60 min): security review / API design / debugging
                                            session / on-call scenario, depending on role
  Stage 4e (optional) — Bar raiser / cross-team (45 min)

Stage 5 — Debrief (30-45 min, all interviewers)
  Output: HIRE / NO HIRE decision with leveling recommendation

Stage 6 — Reference check + offer (parallel, 2-5 days)
```

### Loop Variants

| Role | Adjustments |
|------|-------------|
| **EM** | Replace one coding stage with people-management scenario; add direct-report panel; system design becomes org/process design |
| **Staff+** | Add architecture deep-dive on a system the candidate built; add cross-functional partner panel; coding stage becomes optional or replaced with code-review exercise |
| **New grad** | Two coding rounds, lighter system design (scoped components only), behavioral focused on learning velocity and collaboration |
| **Contractor** | Compress to: 30-min screen + 60-min technical + 30-min reference call. No onsite. Most signal comes from a paid 1-2 week trial engagement. |

### Total Time Budget Rule
If the loop exceeds 8 hours of candidate time across all stages, you will lose candidates to competitors. If the loop is under 3 hours total, you don't have enough signal. Stay in the band.

## Step 4: Stage Design

### Coding Stage

| Decision | Default | Notes |
|----------|---------|-------|
| Live or take-home | Live (60 min, video + code-share) | Take-homes have selection bias against people with caregiving responsibilities. If used, cap at 2 hours and pay for it. |
| Language | Candidate's choice from a published list | Never test on a language the candidate doesn't use daily |
| Problem type | Realistic engineering task (parse a file, implement a small API, debug a function) | Never abstract algorithms unless the role is genuinely algorithmic |
| Difficulty | Solvable in 35-45 minutes by a strong candidate, leaving time for discussion | Time pressure should never be the bar |
| What you measure | Problem decomposition, communication, code clarity, test thinking, debugging when stuck | Not: did they finish, did they remember the trick |

### System Design Stage

| Seniority | Scope | Target Signal |
|-----------|-------|---------------|
| Mid IC | Component-level (design a rate limiter, design a notification queue) | Can reason about state, failure, scale within one service |
| Senior IC | Service-level (design a URL shortener, design a feed) | Owns tradeoffs, knows when to push back on requirements |
| Staff+ | System-level (design a multi-region payment system, design an analytics platform) | Cross-system reasoning, cost/complexity tradeoffs, team and rollout strategy |

Anti-pattern: asking a senior IC to design Twitter at staff-level depth, then dinging them for "not going deep enough." Calibrate to the level being hired.

### Behavioral Stage

- STAR-format prompts (Situation, Task, Action, Result) tied directly to the must-have signals from Step 2.
- 3-4 prompts in 45 minutes. Probe for specifics — names of systems, sizes of teams, dates, outcomes.
- Score each behavioral signal independently on the rubric. Avoid the halo effect of one great story coloring everything.

### Domain-Specific Stage (Pick One)

| Role Flavor | Stage Design |
|-------------|--------------|
| Security-adjacent | Live security review of a small codebase; expect them to find OWASP-style issues |
| ML / data | Model evaluation exercise with a real (or realistic) dataset; discuss tradeoffs |
| Mobile | Live debugging of a UI bug; discuss platform-specific tradeoffs |
| Backend infra | On-call scenario simulation: an alert fires, walk me through your response |
| API / SDK | Design and critique a public API, focusing on developer experience |
| Frontend | Component architecture exercise; accessibility and performance tradeoffs |

## Step 5: Question Bank Construction

- **3-5 questions per stage**, rotated. Each interviewer picks from the bank, doesn't reuse the same question on consecutive candidates.
- **Calibration questions** — keep one "known difficulty" question that has been asked to dozens of candidates with documented score distributions. Use it to detect interviewer drift.
- **Retire-and-rotate cadence** — assume any question asked to >30 candidates is on Glassdoor. Rotate quarterly.
- **Document expected solutions** — every question has a 1-page interviewer guide with: prompt verbatim, expected approach, common candidate paths, follow-ups by skill level, rubric mapping.
- **Pre-asked check** — recruiter asks at the start of every onsite "have you seen this question before?" and gets a different one if yes. No penalty for honesty.

## Step 6: Rubrics

A rubric without concrete examples is decorative. Every signal score needs a behavioral anchor.

### Rubric Template (One Per Stage)

```
STAGE: Coding (Senior IC)
SIGNALS MEASURED:
  - Problem decomposition
  - Code clarity
  - Test thinking
  - Communication under uncertainty

SCORING:
┌────────────────┬──────────────────────────────────────────────────────┐
│ Score          │ Behavioral Anchor                                    │
├────────────────┼──────────────────────────────────────────────────────┤
│ STRONG NO HIRE │ Could not progress without leading; code did not run;│
│                │ no test thinking; gave up under uncertainty          │
├────────────────┼──────────────────────────────────────────────────────┤
│ NO HIRE        │ Reached partial solution with significant prompting; │
│                │ code worked for happy path only; mentioned tests but │
│                │ didn't write any                                     │
├────────────────┼──────────────────────────────────────────────────────┤
│ HIRE           │ Reached working solution with minor prompting; code  │
│                │ handled obvious edge cases; wrote 2-3 tests; talked  │
│                │ through tradeoffs clearly                            │
├────────────────┼──────────────────────────────────────────────────────┤
│ STRONG HIRE    │ Reached working solution unprompted; identified non- │
│                │ obvious edge cases; wrote tests first or alongside;  │
│                │ proposed a refactor or alternative approach unprompt-│
│                │ ed; communicated continuously                        │
└────────────────┴──────────────────────────────────────────────────────┘

LEVELING SIGNALS:
  - L4 (Mid): HIRE on coding alone is sufficient
  - L5 (Senior): Need HIRE on coding AND system design
  - L6 (Staff): Need STRONG HIRE on system design; coding is HIRE floor
```

### Decision Rule
- 4 of 4 HIRE = HIRE
- 3 of 4 HIRE with one NO HIRE = debate at debrief; bar raiser tiebreaks
- 2 of 4 HIRE = NO HIRE (don't talk yourself into it)
- Any STRONG NO HIRE = NO HIRE (one strong dissent ends the loop)

## Step 7: Calibration

### Shadow Rule for New Interviewers
- Round 1: shadow only, no scoring submitted.
- Round 2-3: scored independently, compared to lead interviewer's score, debriefed 1:1.
- Round 4+: full interviewer status, scores count.
- Never let a new interviewer be the only person evaluating a stage.

### Debrief Facilitation
- Hiring manager facilitates, votes last. (Voting first anchors the room.)
- Each interviewer states score and one piece of evidence before discussion.
- Disagreements are resolved by re-reading the rubric, not by the loudest voice.
- Time-box debrief to 45 minutes. If you can't decide in 45 minutes, you don't have enough signal — schedule one targeted follow-up.

### Dissent Protocol
A single interviewer's STRONG NO HIRE ends the loop. They must document the specific rubric anchor that wasn't met. This protects against pattern-matching bias from the majority and against pressure-to-hire dynamics.

### Quarterly Calibration Sessions
- All active interviewers attend.
- Watch a recorded interview together (with consent), score independently, compare.
- Surface drift: are some interviewers consistently 0.5 grades lower than the cohort? Are some always HIRE?
- Update the question bank: retire over-leaked questions, add new ones.

## Step 8: Evaluation Metrics

A loop you don't measure will degrade. Track these monthly:

| Metric | Target | What It Tells You |
|--------|--------|-------------------|
| Top-of-funnel → phone screen pass rate | 50-70% | Sourcing fit |
| Phone screen → onsite pass rate | 30-50% | Screen calibration |
| Onsite → offer pass rate | 30-50% | Onsite calibration; lower means onsite is too hard or screen lets too many through |
| Offer → accept rate | 70-85% | Candidate experience + comp fit |
| Time-to-offer (days from app to offer) | <21 days | Process efficiency |
| Candidate experience NPS | >50 | Whether you're poisoning the well |
| 6-month performance rating correlation with interview score | Positive, ideally >0.4 | Are you measuring the right thing |
| 12-month attrition by interview score | Lower attrition for higher-scored hires | Predictive validity |
| Demographic pass rates by stage | No statistically significant gap | Bias detection |

If 6-month performance correlation is near zero or negative: the loop is theater. Redesign Step 3 stages.

## When NOT to Use This Skill

- **Sourcing / pipeline strategy** — different problem; this skill assumes you have candidates.
- **Compensation benchmarking** — use levels.fyi data and a comp consultant.
- **Performance management of existing employees** — use `/performance-review`.
- **Non-engineering roles** — this skill is calibrated to engineering signals; sales / marketing / design loops have different shape.
- **Single-hire boutique searches** where the candidate is identified by name — design a custom diligence process, not a generalized loop.

## Anti-Patterns (All Findings in a Loop Audit)

- **Brainteasers** ("how many golf balls fit in a 747") — measure verbal puzzle skill, not job performance. Banned.
- **Language-specific gotchas** — testing JS coercion quirks or Python GIL trivia. Measures memorization, not engineering.
- **Single decision-maker** — one person can hire or veto unilaterally. Path to nepotism and bias.
- **No rubric** — "I'll know it when I see it." Indefensible to candidates, undetectable bias.
- **Interviewer as judge and jury** — the same person writes the question, scores it, and makes the hire decision with no oversight.
- **Take-homes over 4 hours** with no compensation. Selection bias.
- **Trick questions** with a single "aha" answer. Measures whether you've heard the trick.
- **Gauntlet onsite** of 6+ hours with no breaks. Measures stamina.
- **Whiteboard coding without execution** for senior roles. The job is to ship working code.
- **No structured behavioral** — vibes-based culture fit. Banned.
- **Asking the candidate to debug your actual production code** for free. Predatory.
- **Re-interviewing rejected candidates** after 6 months without process change. The loop is the same; you're hoping the candidate changed.
- **No debrief** — interviewers submit scores in isolation, hiring manager decides alone. You lose calibration signal.
- **Process drift** — the loop on paper is not the loop being run. Audit by observing 3 actual interviews.

## Output

Generate the deliverable matched to the engagement type from Step 1:

- **Greenfield**: full loop spec + per-stage rubrics + question bank with interviewer guides + interviewer training plan + metric dashboard schema.
- **Calibration**: targeted diagnosis (which stage, which signal, evidence from current data) + specific changes + measurement plan to verify the fix in 90 days.
- **Leaky loop fix**: root-cause analysis with data + intervention + monitoring plan.

Format the loop spec as a one-page summary table that the hiring manager can hand to every interviewer, plus per-stage detail pages. The hiring manager should be able to run a debrief from the materials alone, without you in the room.

## Cross-References

- `/qa-engineer` — for designing the technical question bank when the role is QA-focused.
- `/performance-review` — for the post-hire 6-month and 12-month evaluation that closes the loop on interview validity.
- `/legal-doc-scaffold` — for offer letter and contractor agreement templates.
- `/client-handoff` — when handing the running interview system back to the client team.
- `/technical-program-manager` — for hires into TPM-adjacent roles where the rubric needs program-management signals.
