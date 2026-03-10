# Audit Report Style

When generating audits (feature audit, security review, accessibility audit, performance review, code review):

## Formatting Rules

- Start with a severity summary badge: `PASS ✓` / `WARN ⚠` / `FAIL ✗` with overall score
- Use severity levels consistently: Critical > High > Medium > Low > Info
- Every finding has: severity, location (file:line), description, remediation
- Use checklists `- [x]` for passed items, `- [ ]` for failed items
- Include a scored summary table at the top
- Use `> ⚠️ WARNING:` callouts for critical findings

## Structure

1. **Audit Summary** — Overall score, pass/fail count, highest severity finding
2. **Scope** — What was audited, what was excluded
3. **Findings by Severity** — Critical first, then descending
4. **Checklist Results** — Full checklist with pass/fail per item
5. **Remediation Plan** — Prioritized action items with effort estimates
6. **Positive Observations** — What's done well (important for morale)

## Finding Format

```
### [SEVERITY] Finding Title

**Location:** `path/to/file.kt:42`
**Category:** Security | Performance | Architecture | Testing | Accessibility
**Impact:** What happens if this isn't fixed

**Description:**
Concise explanation of the issue.

**Remediation:**
Specific steps to fix, with code example if applicable.

**Effort:** Low (< 1hr) | Medium (1-4hr) | High (4-8hr) | Critical (8hr+)
```

## Scoring

- Use percentage-based scoring: (passed checks / total checks) × 100
- Color-code: ≥90% = Pass, 70-89% = Warning, <70% = Fail
- Weight critical findings 3x, high 2x, medium 1x, low 0.5x

## Tone

- Objective — findings are facts, not opinions
- Constructive — every finding includes remediation
- Prioritized — critical items first, nice-to-haves last
- Balanced — acknowledge what's done well alongside gaps
