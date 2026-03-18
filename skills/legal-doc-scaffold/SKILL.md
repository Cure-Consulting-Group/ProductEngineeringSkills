---
name: legal-doc-scaffold
description: "Generate Terms of Service, Privacy Policy, SOW, and NDA scaffolds with attorney disclaimer"
argument-hint: "[company-or-product]"
disable-model-invocation: true
---

# Legal Document Scaffold

## Pre-Processing (Auto-Context)

Before starting, gather project context silently:
- Read `PORTFOLIO.md` if it exists in the project root or parent directories for product/team context
- Run: `cat package.json 2>/dev/null || cat build.gradle.kts 2>/dev/null || cat Podfile 2>/dev/null` to detect stack
- Run: `git log --oneline -5 2>/dev/null` for recent changes
- Run: `ls src/ app/ lib/ functions/ 2>/dev/null` to understand project structure
- Use this context to tailor all output to the actual project

> **IMPORTANT DISCLAIMER — READ BEFORE PROCEEDING:** These are starting-point scaffolds for reference and drafting purposes only. They do NOT constitute legal advice and do NOT create an attorney-client relationship. These documents have NOT been reviewed by a licensed attorney and may not be appropriate for your jurisdiction, industry, or specific situation. ALWAYS have every legal document reviewed and approved by a licensed attorney in your jurisdiction before publishing, signing, or relying on it in any business context. Failure to do so may result in unenforceable agreements, regulatory violations, or legal liability. The use of these scaffolds is entirely at your own risk.

Generates first-draft legal documents for SaaS products, mobile apps, and consulting engagements.

## Disclaimer Enforcement (Required)

Every generated document MUST begin with this notice block before any content:

```markdown
> **LEGAL DISCLAIMER:** This document is a scaffold for reference purposes only and does NOT constitute legal advice. It has not been reviewed by a licensed attorney. Have this document reviewed by qualified legal counsel in your jurisdiction before use.
```

Additionally, every section that touches jurisdiction-specific law, data privacy, intellectual property, or liability MUST include an inline `<!-- ATTORNEY REVIEW: [specific reason] -->` comment.

The disclaimer MUST also be repeated verbatim at the end of every generated document.

## Document Types

| Request | Document |
|---------|----------|
| App / SaaS | Terms of Service |
| App / SaaS | Privacy Policy |
| App / SaaS | EULA (mobile app) |
| B2B SaaS | Data Processing Agreement |
| Consulting | Statement of Work |
| Consulting | Consulting Agreement |
| Any | NDA (Mutual or One-Way) |
| App | Refund / Cancellation Policy |

## Step 1: Gather Context

Before generating, confirm:
1. **Document type** — which document(s) needed?
2. **Product name + company name** — legal entity name
3. **Product type** — mobile app / web app / API / consulting service
4. **Data collected** — what user data is collected? (email, payment, location, health, etc.)
5. **Target geography** — US only? EU users? (GDPR implications)
6. **Third-party services** — Firebase, Stripe, Mixpanel, etc.
7. **Business model** — subscription / one-time / freemium / consulting
8. **Minors** — is the platform open to users under 13? Under 18?

## Step 2: Compliance Flags

Based on context, auto-flag applicable requirements:

| Condition | Requirement |
|-----------|-------------|
| Collecting email / PII | Privacy Policy required |
| Payment processing | Must mention Stripe, PCI compliance note |
| Users in EU | GDPR: data subject rights, DPA with processors |
| Users in California | CCPA: right to know, delete, opt-out of sale |
| App on App Store | Apple EULA passthrough required |
| App on Play Store | Google Play Developer Policy compliance |
| Users under 13 | COPPA — do not collect data; add age gate |
| Health/fitness data | HIPAA adjacent — strong disclaimer needed |
| SaaS B2B | DPA often required by enterprise customers |

## Consulting Documents (Cure Consulting Group)

For SOW and consulting agreements, always include:
- Clear scope of work (what's in, what's out)
- Deliverables with acceptance criteria
- Payment terms (milestone or net-30)
- IP ownership (work-for-hire vs. licensed)
- Confidentiality
- Limitation of liability
- Change order process
- Termination clause

## Refund & Cancellation Policy Template

```markdown
## Refund & Cancellation Policy — [Product Name]

**Subscriptions:**
You may cancel your subscription at any time. Cancellation takes effect at the end of
your current billing period. We do not provide prorated refunds for partial months.

**Refunds:**
We offer a [14-day / 30-day] money-back guarantee for first-time subscribers. To request
a refund, contact support@[domain] within [N] days of your initial charge.

After the refund window, all charges are final and non-refundable, except where required
by applicable law.

**App Store Purchases:**
If you purchased through the Apple App Store or Google Play Store, refunds are subject
to their respective refund policies. We are unable to process refunds for app store
purchases directly.

**Contact:** support@[domain]
```

## Output Format

- Generate as clean Markdown
- Use `[COMPANY NAME]`, `[PRODUCT NAME]`, `[DATE]`, `[EMAIL]` as fill-in placeholders
- Highlight sections that need attorney review with `<!-- ATTORNEY REVIEW: [reason] -->`
- Include a "Document Info" header with version, date, and applicable laws
- **Start every document with the full legal disclaimer block** (see Disclaimer Enforcement above)
- **End every document with the full legal disclaimer block** — repeated, never omitted
- Inline `<!-- ATTORNEY REVIEW -->` comments are required on: jurisdiction clauses, limitation of liability, data subject rights, IP ownership, indemnification, and governing law sections
