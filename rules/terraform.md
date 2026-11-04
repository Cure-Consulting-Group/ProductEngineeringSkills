---
paths:
  - "**/*.tf"
  - "**/*.tfvars"
  - "**/terraform/**"
  - "**/.terraform.lock.hcl"
---

# Terraform / IaC Standards — Cure Consulting Group

When editing Terraform or infrastructure-as-code files, follow these standards:

## File Organization
- `main.tf` (resources), `variables.tf`, `outputs.tf`, `providers.tf` (with `required_providers` + `required_version`), `backend.tf`, `locals.tf`
- One module per logical component (networking, compute, database, etc.)

## Naming
- Resources: `snake_case` (`google_compute_instance.api_server`)
- Variables: `snake_case`, descriptive — no abbreviations
- Modules: kebab-case directories (`modules/api-gateway/`)
- Labels/tags: always `project`, `environment`, `managed-by = "terraform"`

## State and Safety
- Remote state with locking: GCS backend (locks natively) or S3 with `use_lockfile = true`. DynamoDB locking (`dynamodb_table`) is deprecated — migrate off it
- State never in git — `.gitignore` `*.tfstate*` and `.terraform/`; DO commit `.terraform.lock.hcl`
- Separate state per environment (dev, staging, prod)
- CI applies a saved plan: `terraform plan -out=tfplan` → review → `terraform apply tfplan`
- No `-target` in production — it is for recovering from errors, and it hides drift from the plan. Refactor with `moved`, `import` and `removed` blocks instead
- `prevent_destroy` lifecycle on critical resources (databases, storage buckets)

## Variables
- Every variable has `description` and `type`; secrets marked `sensitive = true`
- `validation` blocks for input constraints
- Defaults for dev only — production values are explicit
- One `*.tfvars` per environment; never hardcode values

## Modules
- Pin module versions (`?ref=v1.2.3` or a registry `version`) and providers (`~>`)
- Expose only necessary outputs; README.md in every module
- No provider configuration inside modules — inherit from root

Verified 2026-10-24: S3 `use_lockfile` and deprecated DynamoDB locking per developer.hashicorp.com/terraform/language/backend/s3.
