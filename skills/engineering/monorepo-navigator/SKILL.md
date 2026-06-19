---
name: monorepo-navigator
description: "Navigate, work in, and improve monorepos — pnpm workspaces, Turborepo, Nx, Lerna, Yarn workspaces, Bazel, or untangling a folder that thinks it's a monorepo"
when_to_use: "Use when joining a client codebase that's a monorepo (or claims to be), introducing one, fixing slow CI, deduplicating shared deps, or extracting a package. NOT for single-package repos — those don't need this skill."
argument-hint: "[repo-path-or-task]"
---

# Monorepo Navigator

Most clients show up with a monorepo. Half of them are real monorepos. The other half are a folder of folders that someone called a monorepo and never wired up. Your job is to tell which is which, then either make it faster or make it actually one.

Cure default: pnpm workspaces + Turborepo for JS/TS. Nx if the team is already on it. Bazel only if the team has a dedicated build engineer. Lerna is legacy — migrate off.

## When NOT to use this skill

- Single-package repo. Adding workspace tooling for one package is overhead with no upside.
- Polyrepo with strong service boundaries already working. Don't merge them just to "consolidate."
- Team has fewer than 3 engineers and one product. Monorepo overhead pays off at scale, not at start.

## Pre-Processing (Auto-Context)

Before starting, gather context silently:
- `cat package.json 2>/dev/null` — detect workspaces, turbo, nx config
- `ls -la` for `pnpm-workspace.yaml`, `nx.json`, `turbo.json`, `lerna.json`, `WORKSPACE`, `MODULE.bazel`
- `cat pnpm-workspace.yaml 2>/dev/null && cat turbo.json 2>/dev/null && cat nx.json 2>/dev/null`
- Count packages: `find . -name package.json -not -path "*/node_modules/*" | wc -l`
- Check CI duration: scan `.github/workflows/*.yml` for cache and affected logic
- Use this to skip redundant questions in Step 2

## Step 1: Classify the Monorepo Type

| Signal | Type | Cure Verdict |
|--------|------|--------------|
| `pnpm-workspace.yaml` + `turbo.json` | pnpm + Turborepo | Default. Keep it. |
| `nx.json` + `package.json` workspaces | Nx | Fine if team knows Nx. Don't migrate away unless broken. |
| `lerna.json` (no Nx) | Lerna (legacy) | Migrate to pnpm + changesets. Lerna is on life support. |
| `package.json` with `workspaces` only | Yarn / npm workspaces, no task runner | Add Turbo or Nx. Workspaces alone don't give you caching. |
| `WORKSPACE` / `MODULE.bazel` | Bazel | Heavy. Only justified at 50+ packages or polyglot. |
| Multiple `package.json` files, no workspace config | "Folder that thinks it's a monorepo" | Either wire it up properly or split into polyrepo. |
| One `package.json`, deeply nested feature folders | Not a monorepo. It's a single package. | Stop calling it a monorepo. |

## Step 2: Gather Context

1. **Package count** — How many packages? Apps vs. libs split?
2. **Languages** — All TypeScript? Mixed Python / Go? (changes tooling story)
3. **CI duration** — Median PR CI time? p95? What's slow — install, build, or test?
4. **Deployment topology** — Monolithic deploy of everything on every push? Or per-package independent deploys?
5. **Current pain** — Pick the loudest:
   - Slow CI (install + build + test all packages every PR)
   - Coupled releases (one package's bug blocks all releases)
   - Shared dependency drift (3 versions of React across packages)
   - Circular deps or unclear ownership
   - "Where do I put this code?" — no clear package boundaries

The pain you name decides which steps below matter most.

## Step 3: Topology — Package Boundaries

Get this wrong and everything else is firefighting.

```
apps/                      — leaf nodes. Deployable units. Web app, mobile app, API service.
  web/
  mobile/
  api/

packages/                  — shared libraries. Composable. Versioned independently.
  ui/                      — design system primitives
  auth/                    — auth client + types
  config/                  — shared eslint, tsconfig, prettier
  utils/                   — pure functions, no side effects
  api-client/              — generated/typed API client

services/  (optional)      — backend microservices if not in apps/
  payments/
  notifications/
```

### Dependency direction rules (enforce in CI)

```
apps/*    →  packages/*    OK
apps/*    →  apps/*        NEVER. Apps share code via packages/, not by importing each other.
packages/* → packages/*    OK if no cycles.
packages/* → apps/*        NEVER. Libraries do not depend on applications.
```

Tooling to enforce:
- **Nx**: `nx.json` `enforceBuildableLibDependency` + module boundary lint rules
- **pnpm + Turbo**: `eslint-plugin-boundaries` or `dependency-cruiser` in CI
- **Bazel**: `visibility` attribute on every target

### Shared tooling (one source of truth)

```
packages/config/
  eslint-base.js       — extended by every package
  tsconfig-base.json   — extends:[] in every package's tsconfig.json
  jest-preset.js       — every package's jest.config.js requires this
  prettier.config.js   — root only, not per-package
```

Per-package configs extend, never redefine.

## Step 4: Build & Cache

The point of a monorepo is shared cache. If you don't have remote cache, you have a slow polyrepo.

| Stack | Local Cache | Remote Cache |
|-------|-------------|--------------|
| Turborepo | Free, default | Vercel Remote Cache (free for OSS, paid for teams) OR self-hosted via `turborepo-remote-cache` on S3/R2 |
| Nx | Free, default | Nx Cloud (free tier exists, paid for advanced features) OR self-hosted |
| Bazel | Free, default | BuildBuddy, EngFlow, or self-hosted Bazel Remote Cache on S3/GCS |

### Task graph correctness

Every task must declare its inputs and outputs. Otherwise cache is silently wrong.

```jsonc
// turbo.json
{
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "inputs": ["src/**", "package.json", "tsconfig.json"],
      "outputs": ["dist/**", ".next/**"]
    },
    "test": {
      "dependsOn": ["^build"],
      "inputs": ["src/**", "test/**", "package.json"],
      "outputs": ["coverage/**"]
    },
    "lint": {
      "inputs": ["src/**", ".eslintrc*", "package.json"],
      "outputs": []
    }
  }
}
```

Common mistakes:
- Missing `inputs` — Turbo defaults to "all files", so any change invalidates cache.
- Missing `outputs` — restored cache won't restore artifacts.
- Forgotten `^` prefix — task doesn't wait for upstream packages to build.

### Affected detection

Never run all packages on every PR. Use:
- `turbo run build --filter=...[origin/main]`
- `nx affected -t build --base=origin/main`
- `bazel query "rdeps(//..., set($CHANGED_TARGETS))"`

In CI, set the base ref to `origin/main` for PRs and `HEAD~1` for main pushes.

## Step 5: Versioning & Release

Pick one. Don't mix.

| Strategy | Best For | Tooling |
|----------|----------|---------|
| **Changesets** (independent versions) | Public packages, semver-strict consumers | `@changesets/cli` |
| **Semantic-release** (per-package, automated) | High-velocity teams that trust commit messages | `semantic-release` + monorepo plugin |
| **Single version (lockstep)** | Internal monorepo, all packages deploy together | Manual `pnpm version` at root, or Nx `release` |
| **Manual** | Small team, low release frequency | `pnpm publish` per package |

Cure default for client work: **changesets** for public/shared packages, **single-version** for app-only monorepos that deploy as a unit.

```
.changeset/
  config.json           — defines linked vs. independent packages
  README.md             — workflow explanation
  <random-name>.md      — pending change, written by contributor
```

## Step 6: Impact Analysis & CI Optimization

Given a diff, what must rebuild?

```bash
# Turborepo: dry-run shows the task graph
turbo run build test --filter=...[origin/main] --dry=json

# Nx: shows the affected graph
nx graph --affected --base=origin/main

# Bazel: query reverse deps
bazel query 'rdeps(//..., //packages/auth/...)'
```

### CI matrix optimization

```yaml
# .github/workflows/ci.yml — sketch
jobs:
  affected:
    runs-on: ubuntu-latest
    outputs:
      packages: ${{ steps.detect.outputs.packages }}
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - id: detect
        run: |
          PKGS=$(npx turbo run build --filter=...[origin/main] --dry=json | jq -c '[.tasks[].package] | unique')
          echo "packages=$PKGS" >> $GITHUB_OUTPUT

  build:
    needs: affected
    if: needs.affected.outputs.packages != '[]'
    strategy:
      matrix:
        package: ${{ fromJSON(needs.affected.outputs.packages) }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pnpm install --frozen-lockfile
      - run: pnpm --filter ${{ matrix.package }} build
      - run: pnpm --filter ${{ matrix.package }} test
```

Targets to hit:
- p50 PR CI time: under 5 min
- p95: under 10 min
- Cache hit rate on unchanged packages: 100% (if not, your inputs are wrong)

## Step 7: Refactoring Inside a Monorepo

### Extracting a library from an app

1. Create `packages/<name>/` with `package.json`, `tsconfig.json`, `src/index.ts`
2. Move source files. Update imports inside the new package to relative paths.
3. In the consuming app, replace deep imports (`../../../lib/foo`) with `@org/<name>`
4. Add `"@org/<name>": "workspace:*"` to the app's `dependencies`
5. Run `pnpm install` (or `nx sync`) to wire workspace symlinks
6. Add to `tsconfig.json` `paths` if using path aliases for IDE
7. Run full build + test. Cache will be cold on first run — that's fine.

### Deduplicating dependencies

```bash
# Find version drift
pnpm dedupe --check
pnpm why react       # shows every version of react and who pulls it
npx syncpack list-mismatches    # cross-package version drift

# Fix
npx syncpack fix-mismatches     # writes the same version everywhere
pnpm dedupe                     # collapses duplicates in node_modules
```

Pin shared deps (React, Next, TypeScript) at root with `pnpm.overrides` so individual packages can't drift.

### Version mismatch resolution

When packages disagree on a peer dep version:
1. Identify the most-restrictive consumer (usually the app).
2. Set that version as the floor in `pnpm.overrides`.
3. Run `pnpm dedupe`.
4. If a package can't tolerate the override, that package owns the upgrade — don't fork.

## Anti-Patterns

| Anti-Pattern | Why It Hurts | Fix |
|--------------|--------------|-----|
| Circular deps between packages | Breaks tree-shaking, breaks topological build, breaks brain | `dependency-cruiser` in CI, refuse PRs that introduce cycles |
| `packages/shared/` as a junk drawer | Becomes a dep of everything; breaks the affected graph; rebuilds everything every PR | Split by concern: `ui/`, `utils/`, `types/`, `config/`. Never name a package "shared" or "common." |
| No affected detection in CI | Every PR runs every package's tests — slow and expensive | Add `--filter=...[origin/main]` or `nx affected` immediately |
| Deploying all apps on every merge | Couples release cycles, slows recovery, increases blast radius | Per-app deploy workflows triggered on `paths:` filters |
| `apps/*` importing from `apps/*` | Creates an undeclared shared library inside an app boundary | Extract the shared code to `packages/`. Enforce with lint. |
| One `tsconfig.json` at root, none per package | Loses incremental builds, loses per-package strict-ness | Per-package tsconfigs extending a base config |
| Lockfile per package | Defeats the entire point of a workspace | Single root lockfile only |
| Generated code committed inside `node_modules` or other workspace's `src/` | Breaks cache, breaks isolation | Generated code lives in its own package or its consuming package's `src/generated/` |

## Cross-References

- `/ci-cd-pipeline` — for the GitHub Actions affected-build matrix
- `/project-bootstrap` — when standing up a new monorepo from scratch
- `/release-management` — for changesets + semantic-release pipelines
- `rules/cicd.md` — CI standards that monorepos must conform to
- `rules/web.md` — TypeScript / Next.js rules that apply per package

## Step 8: Output

When invoked, produce in order:
1. **Diagnosis** — current type, package count, current pain (one paragraph).
2. **Recommended changes** — bulleted, ranked by impact-per-effort.
3. **Concrete diffs** — `turbo.json`, `pnpm-workspace.yaml`, CI workflow snippets, `.changeset/config.json`. Use the Write/Edit tools to apply them when the user confirms.
4. **Verification commands** — exact commands to run after, with expected output.
5. **Follow-up** — what to revisit in 2 weeks (cache hit rate, CI p95, dep drift).

Never recommend a tool migration (Lerna → pnpm, Yarn → pnpm, Nx → Turbo) without first confirming the team's bandwidth. Migration mid-engagement is a project, not a chore.
