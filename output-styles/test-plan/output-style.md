---
name: test-plan
description: Output style for test plans — objectives, scope, test cases, data requirements, coverage metrics, and success criteria.
---

# Test Plan Output Style

When generating test plans, follow this format:

## Structure

```
# Test Plan: {Feature/Release Name}

**Version:** X.X
**Date:** YYYY-MM-DD
**Author:** [name]
**Status:** Draft | In Review | Approved | Executing | Complete

## Objectives
What we're testing and why. Link to requirements/PRD.

## Scope

### In Scope
- [feature/component 1]
- [feature/component 2]

### Out of Scope
- [explicitly excluded items]

## Test Strategy

| Level | Framework | Coverage Target |
|-------|-----------|----------------|
| Unit | Jest/JUnit5/XCTest | 80% new code |
| Integration | Supertest/Espresso | Critical paths |
| E2E | Playwright/Maestro | Happy paths + top 3 error paths |
| Performance | k6/Lighthouse | Budgets met |

## Test Cases

### {Feature Area}

| ID | Description | Priority | Type | Steps | Expected Result | Status |
|----|-------------|----------|------|-------|-----------------|--------|
| TC-001 | [what] | P1 | Happy path | 1. Do X 2. Do Y | Z happens | Not run |
| TC-002 | [what] | P1 | Error path | 1. Do X | Error shown | Not run |

## Test Data Requirements
| Data | Source | Setup | Cleanup |
|------|--------|-------|---------|
| Test user | Seed script | Before suite | After suite |

## Environment
| Env | URL | Purpose |
|-----|-----|---------|
| Dev | localhost:3000 | Unit + integration |
| Staging | staging.app.com | E2E + UAT |

## Entry Criteria
- [ ] Code complete and merged to feature branch
- [ ] Build passes CI
- [ ] Test environment provisioned

## Exit Criteria
- [ ] All P1 test cases pass
- [ ] No P1/P2 bugs open
- [ ] Coverage meets thresholds
- [ ] Performance budgets met

## Risk Register
| Risk | Impact | Mitigation |
|------|--------|------------|
```

## Rules
- Every test case must have exactly one expected result
- Priority drives execution order: P1 first, then P2, then P3
- Test data setup must be automated — no manual data entry
- Include both happy paths and top error scenarios
- Exit criteria are pass/fail — no subjective assessments
