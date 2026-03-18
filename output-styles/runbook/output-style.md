---
name: runbook
description: Output style for operational runbooks — step-by-step procedures, troubleshooting guides, escalation paths, and recovery procedures.
---

# Runbook Output Style

When generating operational runbooks, follow this format:

## Structure

```
# Runbook: {Procedure Name}

**Last Updated:** YYYY-MM-DD
**Owner:** [team/person]
**Severity Impact:** P1-Critical | P2-High | P3-Medium | P4-Low
**Estimated Duration:** X minutes

## Prerequisites
- [ ] Access to [system/tool]
- [ ] Permissions: [required roles]
- [ ] Tools installed: [list]

## When to Use
Describe the symptoms or triggers that indicate this runbook should be followed.

## Steps

### 1. [Action Name]
**What:** Description of what this step does
**Command:**
```bash
command --flag value
```
**Expected Output:** What you should see if successful
**If it fails:** What to do if this step fails

### 2. [Next Action]
...

## Verification
How to confirm the procedure was successful:
- [ ] Check 1
- [ ] Check 2

## Rollback
If the procedure needs to be reversed:
1. Step to undo
2. Step to undo

## Escalation
| Condition | Escalate To | Contact |
|-----------|-------------|---------|
| Step X fails after retry | On-call engineer | #incident-channel |
| Data loss detected | Engineering lead | @name |

## Common Issues
| Symptom | Cause | Fix |
|---------|-------|-----|
```

## Rules
- Every step must have a verification check or expected output
- Every destructive step must have a rollback procedure
- Commands must be copy-pasteable — no pseudo-code
- Include timing estimates for each section
- Escalation contacts must be real (update quarterly)
- Write for the person who's never seen this before at 3am
