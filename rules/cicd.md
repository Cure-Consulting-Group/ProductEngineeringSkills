---
globs: ".github/workflows/**,**/.github/workflows/**"
---

# CI/CD Standards — Cure Consulting Group

When editing GitHub Actions workflows, follow these standards:

## Workflow Structure
- One workflow per concern: `ci.yml` (test+lint), `deploy.yml` (deploy), `release.yml` (version+publish)
- Pin action versions to SHA, not tags (`actions/checkout@abc123` not `@v4`)
- Use `concurrency` groups to cancel in-progress runs on same branch
- Set `timeout-minutes` on all jobs (default 30 for builds, 10 for lints)
- Use `workflow_call` for reusable workflows — don't duplicate steps across files

## Secrets & Security
- Never echo or log secrets — use `::add-mask::` for dynamic values
- Secrets in `${{ secrets.* }}` — never in workflow file text
- Use OIDC for cloud provider auth (GCP Workload Identity, AWS OIDC) — avoid long-lived keys
- Minimum permissions with `permissions:` block on every workflow and job
- Pin runners to specific versions for reproducibility

## Caching & Performance
- Cache dependencies (`actions/cache` or built-in caching in setup actions)
- Use matrix builds for cross-platform testing
- Parallelize independent jobs — sequential only when dependent
- Artifacts for sharing between jobs (`actions/upload-artifact`)

## Quality Gates
- Required checks before merge: lint, test, type-check, build
- No direct push to main — PR-only with required reviews
- Branch protection rules enforced
- Status checks must pass on latest commit (not stale)

## Deploy Patterns
- Staging auto-deploy on merge to main
- Production manual approval via environment protection rules
- Rollback via revert commit — not manual action
- Smoke tests after every deployment
