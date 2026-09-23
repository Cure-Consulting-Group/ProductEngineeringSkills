# portfolio-registry: detailed reference

> Reference material for the `portfolio-registry` skill, split out for progressive disclosure. Loaded on demand from SKILL.md.

## Contents
- Shared Infrastructure
- Cross-Product Dependencies

## Shared Infrastructure

### Authentication
| Field | Value |
|-------|-------|
| Provider | [Firebase Auth / Auth0 / custom] |
| Shared identity | [Yes/No — do products share user accounts?] |
| SSO | [Yes/No — single sign-on across products?] |
| MFA | [Required / Optional / Not implemented] |
| Auth project ID | [Firebase project ID if shared] |
| Custom claims | [List any shared custom claims: role, org_id, etc.] |

### Design System
| Field | Value |
|-------|-------|
| Shared base | [Yes/No — spacing, type scale, 8pt grid] |
| Per-brand theming | [Color, typography, imagery per product] |
| Token source | [Style Dictionary / Figma Variables / Tailwind config / manual] |
| Token repo | [github.com/org/design-tokens or N/A] |
| Component library | [Shared UI lib or per-product] |
| Design tool | [Figma / Sketch / none] |

### Analytics
| Field | Value |
|-------|-------|
| Platform | [Firebase Analytics / Mixpanel / PostHog / Amplitude] |
| Cross-product user ID | [Yes/No — can you track a user across products?] |
| Event taxonomy | [Standardized / Per-product / None] |
| Portfolio dashboard | [URL or N/A] |
| Data warehouse | [BigQuery / Snowflake / N/A] |

### CI/CD
| Field | Value |
|-------|-------|
| Provider | [GitHub Actions / CircleCI / Bitrise] |
| Shared workflows | [List reusable workflow files] |
| Deployment strategy | [Per-product / Unified / Mixed] |
| Artifact registry | [GitHub Packages / GCP Artifact Registry / N/A] |
| Mobile distribution | [Firebase App Distribution / TestFlight / Google Play Internal] |

### AI Infrastructure
| Field | Value |
|-------|-------|
| Models in use | [GPT-4, Claude, Gemini — list which product uses which] |
| API key management | [Per-product keys (required) / Shared keys (fix this)] |
| Cost tracking | [Per-product / Shared / Not tracked (fix this)] |
| Monthly AI spend | [$X total, $X per product] |
| Rate limiting | [Implemented / Not implemented] |
| Prompt management | [Version controlled / Ad hoc] |

### Domains & DNS
| Field | Value |
|-------|-------|
| Registrar | [Cloudflare / GoDaddy / Google Domains / Namecheap] |
| DNS provider | [Cloudflare / Route53 / Cloud DNS] |
| SSL | [Auto via Cloudflare / Let's Encrypt / GCP-managed] |
| Domains | [List all domains across portfolio] |

### Secrets Management
| Field | Value |
|-------|-------|
| Secrets vault | [1Password / GCP Secret Manager / AWS Secrets Manager] |
| Rotation policy | [90 days / manual / none] |
| Environment injection | [dotenv / GCP Secret Manager / GitHub Secrets] |

## Cross-Product Dependencies

### Dependency Matrix

| From | To | Type | What | Risk if Broken | Mitigation |
|------|----|------|------|----------------|------------|
| Vendly | Shared Firebase | Infrastructure | Auth, Firestore, Cloud Functions | All auth fails, data inaccessible | Multi-region, failover config |
| Autograph | OpenAI API | External vendor | GPT-4 for medical transcription | Core feature unusable | Fallback to Claude, queue system |
| The Initiated | Vendly design tokens | Design | Shared spacing, grid, type scale | Inconsistent UI | Tokens versioned, pinned |
| Antigravity | VS Code upstream | Open source | Fork base, extension API | Feature divergence, security patches | Weekly upstream sync, patch process |
| All products | GitHub Actions | CI/CD | Build, test, deploy pipelines | No deploys, no PR checks | Local build fallback documented |
| All products | Firebase Auth | Identity | User authentication | Complete auth failure | Status page monitoring, cached tokens |

### Dependency Rules
- Every external dependency must have a documented fallback or degradation strategy
- Shared infrastructure changes require notification to ALL dependent product teams
- Breaking changes to shared services require 2-week migration window minimum
- Vendor dependencies must be evaluated quarterly for cost, reliability, and alternatives
- Cross-product data flows must be documented in security review scope

### Circular Dependency Check
[List any circular dependencies — these are architectural red flags that need resolution]
- [None / List if found]
