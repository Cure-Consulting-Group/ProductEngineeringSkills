---
globs: "**/*.tf,**/*.tfvars,**/terraform/**"
---

# Terraform / IaC Standards — Cure Consulting Group

When editing Terraform or infrastructure-as-code files, follow these standards:

## File Organization
- `main.tf` — primary resources
- `variables.tf` — input variables with descriptions and types
- `outputs.tf` — output values
- `providers.tf` — provider configs with version constraints
- `backend.tf` — remote state configuration
- `locals.tf` — computed local values
- One module per logical component (networking, compute, database, etc.)

## Naming
- Resources: `snake_case` with type prefix (`google_compute_instance.api_server`)
- Variables: `snake_case` with descriptive names — no abbreviations
- Modules: kebab-case directories (`modules/api-gateway/`)
- Tags: always include `project`, `environment`, `managed-by: terraform`

## Safety
- Remote state with locking (GCS bucket + lock, S3 + DynamoDB)
- State file never in git — `.gitignore` all `*.tfstate*`
- Plan before apply — always review `terraform plan` output
- Use `-target` for individual resource changes in production
- Separate state files per environment (dev, staging, prod)
- Use `prevent_destroy` lifecycle on critical resources (databases, storage buckets)

## Variables
- All variables must have `description` and `type`
- Sensitive variables marked `sensitive = true`
- Use `validation` blocks for input constraints
- Defaults for dev environment — require explicit values for production
- Use `terraform.tfvars` per environment, never hardcode values

## Modules
- Pin module versions (`source = "...?ref=v1.2.3"`)
- Modules expose only necessary outputs
- README.md in every module directory
- No provider configuration inside modules — inherit from root
