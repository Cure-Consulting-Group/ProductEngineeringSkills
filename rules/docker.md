---
globs: "**/Dockerfile*,**/docker-compose*,**/.dockerignore"
---

# Docker Standards — Cure Consulting Group

When editing Docker files, follow these standards:

## Dockerfile
- Multi-stage builds — separate build and runtime stages
- Pin base image versions with SHA digests for production (`node:20-alpine@sha256:...`)
- Run as non-root user — `RUN addgroup -S app && adduser -S app -G app` then `USER app`
- Order layers by change frequency — OS deps first, app deps middle, source code last
- Use `.dockerignore` to exclude `node_modules`, `.git`, `.env`, build artifacts
- HEALTHCHECK instruction on all production images
- No secrets in build args or ENV — use runtime secrets mounting

## Docker Compose
- Pin image versions — never use `latest` tag
- Use `depends_on` with health checks (`condition: service_healthy`)
- Named volumes for persistent data — never bind mounts in production
- Environment variables via `.env` file or secrets — not inline in compose file
- Resource limits on all services (`deploy.resources.limits`)
- Network isolation — separate networks for frontend, backend, database tiers

## Security
- Scan images with `trivy` or `grype` in CI before pushing
- No `--privileged` flag — use specific capabilities (`--cap-add`) if needed
- Read-only root filesystem where possible (`read_only: true`)
- No SSH in containers — use `docker exec` for debugging
