---
paths:
  - "**/Dockerfile*"
  - "**/*.dockerfile"
  - "**/compose*.{yaml,yml}"
  - "**/docker-compose*"
  - "**/.dockerignore"
---

# Docker Standards — Cure Consulting Group

When editing Docker files, follow these standards:

## Dockerfile
- Multi-stage builds — separate build and runtime stages
- Current LTS base images: `node:24-alpine` (Node 20 is end-of-life; Node 26 is not LTS yet), pinned by digest in production (`node:24-alpine@sha256:...`)
- Run as non-root — `RUN addgroup -S app && adduser -S app -G app` then `USER app`
- Order layers by change frequency — OS deps first, app deps (`npm ci --omit=dev`) middle, source last
- BuildKit mounts: `RUN --mount=type=cache` for package caches, `--mount=type=secret` for build-time credentials — never secrets in `ARG`/`ENV`
- `.dockerignore` excludes `node_modules`, `.git`, `.env*`, build artifacts
- HEALTHCHECK on every production image

## Compose
- New projects use `compose.yaml` (the canonical name; `docker-compose.yml` is read only for backward compatibility); no top-level `version:` key
- Pin image versions — never `latest`
- `depends_on` with `condition: service_healthy`
- Named volumes for persistent data — no bind mounts in production
- Environment via `.env` or secrets — not inline in the compose file
- Resource limits on every service (`deploy.resources.limits`)
- Separate networks for frontend, backend and database tiers

## Security
- Scan images with `trivy` or `grype` in CI before pushing
- No `--privileged` — add specific capabilities (`cap_add`) only when needed
- Read-only root filesystem where possible (`read_only: true`)
- No SSH in containers — use `docker exec` for debugging

Verified 2026-10-24: Node 24 LTS, Node 20 EOL, Node 26 Current (nodejs.org/en/about/previous-releases); `compose.yaml` preferred (docs.docker.com/compose/intro/compose-application-model).
