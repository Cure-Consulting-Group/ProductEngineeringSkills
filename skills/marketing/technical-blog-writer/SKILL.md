---
name: technical-blog-writer
description: "Crafts high-impact technical blog posts modeled after Netflix/Uber engineering blogs, translated for business owners. Use when you need to explain complex engineering feats using the 'Famous Actor' simple-explanation tone with clear visual concepts."
argument-hint: "[topic-or-title]"
---

# Technical Blog Writer Skill

This skill translates deep engineering complexity into high-leverage business narratives. It balances the technical authority of a "Tier 1" engineering blog (Netflix, Uber, Square) with the accessibility of a "Famous Actor" explaining a product to a common person.

## The "Famous Actor" Tone
Do not "dumb down" the tech; "smart up" the context.
- **Authority**: Speak with the confidence of an expert.
- **Relatability**: Use physical, everyday analogies (kitchens, highways, plumbing).
- **Directness**: Avoid corporate jargon and passive voice.
- **The "So What?"**: Every paragraph must anchor back to cost, risk, or growth.

## Core Frameworks

### 1. The SCQA Narrative Arc (Uber Style)
- **Situation**: The baseline. "Our app handles 1M requests."
- **Complication**: The villain. "But as we scaled, the database became a traffic jam."
- **Question**: The challenge. "How do we keep the cars moving without building a 20-lane highway we can't afford?"
- **Answer**: The hero. "We implemented [Technical Solution], which is essentially an automated GPS for data."

### 2. The "Evolutionary" Arc (Pinterest Style)
- **Problem**: What was breaking?
- **Chaos**: The honest mess of trying to fix it.
- **Simplification**: How we returned to "boring" but powerful reliability.

## Workflow

### Step 1: Extract the "Alpha"
Identify the specific engineering achievement.
- Is it a **Scale** feat? (Handling more users)
- Is it an **Efficiency** feat? (Lowering costs)
- Is it a **Reliability** feat? (Preventing crashes)

### Step 2: Select the Analogy (The "ELI5" Bridge)
Choose a physical metaphor that a business owner can touch.
- **Technical Debt** → A stack of dirty pans in a busy kitchen.
- **Microservices** → A LEGO castle vs. a solid clay block.
- **APIs** → A restaurant menu and a waiter.
- **Cloud Scalability** → An accordion hotel that grows during festivals.

### Step 3: Map the Visuals
Describe 2-3 visual concepts that pass the "Grunt Test" (understandable in 5 seconds).
- **Diagram A**: "Before vs. After" architectural simplification.
- **Diagram B**: The physical analogy visualized (e.g., the "Dirty Pans" stack).
- **Chart C**: The "Aha!" metric (e.g., P99 latency dropping like a cliff).

### Step 4: Write the Post
- **Title**: Action-oriented (4-8 words).
- **Hook**: A "Scale Fact" to establish stakes.
- **Body**: The SCQA or Evolutionary narrative.
- **Conclusion**: The business impact summary.

## Standard Output Format

```markdown
# [Action-Oriented Title]

## The Hook
[1-2 sentences on the scale or business stakes.]

## The Challenge: [The "Villain"]
[Describe the complication using a physical analogy.]

## The Solution: [The "Hero"]
[Introduce the technical feat as the solution to the analogy.]

## Visual Concept: [Name]
- **Description**: [What the image shows]
- **Business Insight**: [What the owner learns from looking at it]

## The "So What?" (Business Impact)
- **Growth**: [Benefit]
- **Cost**: [Savings]
- **Risk**: [Reduction]
```

## Quality Standards
- **Grunt Test**: Can a non-technical person understand the diagrams?
- **Grandfather Test**: Can you explain the core concept without using its technical name?
- **No Fluff**: Every sentence must provide either technical authority or business clarity.
