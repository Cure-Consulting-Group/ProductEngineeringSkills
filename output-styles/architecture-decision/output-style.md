---
name: architecture-decision
description: Output style for Architecture Decision Records (ADRs) — context, decision, consequences, alternatives considered.
---

# Architecture Decision Record Output Style

When generating ADRs, follow this format:

## Structure

```
# ADR-{NNN}: {Title}

**Status:** Proposed | Accepted | Deprecated | Superseded by ADR-{NNN}
**Date:** YYYY-MM-DD
**Deciders:** [names/roles]
**Tags:** [architecture, infrastructure, security, etc.]

## Context

What is the issue that we're seeing that is motivating this decision or change?
Include technical and business context. Reference metrics, incidents, or requirements.

## Decision

What is the change that we're proposing and/or doing?
Be specific — name technologies, patterns, libraries.

## Consequences

### Positive
- [what becomes easier or better]

### Negative
- [what becomes harder or worse]

### Neutral
- [notable side effects that aren't clearly positive or negative]

## Alternatives Considered

### Option A: {name}
- **Pros:** ...
- **Cons:** ...
- **Why rejected:** ...

### Option B: {name}
- **Pros:** ...
- **Cons:** ...
- **Why rejected:** ...

## References
- [links to relevant docs, RFCs, discussions]
```

## Rules
- One decision per ADR — split compound decisions
- Context section must explain WHY, not just WHAT
- Always include at least 2 alternatives considered
- Consequences must include both positive and negative
- Status must be kept up to date
- ADRs are immutable once accepted — new ADRs supersede old ones
