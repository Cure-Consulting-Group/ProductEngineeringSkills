# Micro-Frontends

Architecture framework for scaling frontend applications across multiple teams. Use when decomposing a monolithic frontend, setting up a monorepo, designing shared component libraries, or enabling independent team deployments. Opinionated toward Next.js, Turborepo, and Vercel.

## Pre-Processing (Auto-Context)

Before starting, gather project context silently:
- Read `PORTFOLIO.md` if it exists in the project root or parent directories for product/team context
- Run: `cat package.json 2>/dev/null || cat build.gradle.kts 2>/dev/null || cat Podfile 2>/dev/null` to detect stack
- Run: `git log --oneline -5 2>/dev/null` for recent changes
- Run: `ls src/ app/ lib/ functions/ 2>/dev/null` to understand project structure
- Use this context to tailor all output to the actual project

## Step 1: Classify the Micro-Frontend Need

| Type | When to Use | Output |
|------|------------|--------|
| Greenfield Micro-Frontend | New multi-team product — design from scratch | Architecture decision, monorepo setup, shared library plan |
| Monolith Decomposition | Existing frontend is too large for one team to own | Decomposition strategy, migration plan, strangler fig approach |
| Monorepo Setup | Multiple apps sharing code — need build tooling | Turborepo/Nx config, workspace structure, task pipeline |
| Shared Library Extraction | Components duplicated across apps — extract and share | Package structure, versioning, design system setup |

## Step 2: Gather Context

1. **Team structure** -- how many teams will own frontend code? Do they deploy independently? Are they cross-functional (frontend + backend)?
2. **Current frontend** -- monolith size (files, routes, bundle size), framework (React/Next.js), deployment method?
3. **Deployment cadence** -- how often does each team ship? Is one team blocked by another's release schedule?
4. **Shared state needs** -- do apps share auth, user data, shopping cart, or other state? How tightly coupled are they?
5. **Performance budget** -- total bundle size target, LCP target, acceptable overhead from micro-frontend runtime?

## Step 3: Architecture Patterns

### Module Federation (Webpack 5 / Next.js)
```
When to use:
  ✅ Teams need runtime composition (load remote code at runtime)
  ✅ Apps share React version and core dependencies
  ✅ Need to update one app without redeploying others
  ❌ Not for simple component sharing (use packages instead)
  ❌ Adds runtime complexity — only justified for 3+ teams

How it works:
  Host app loads remote apps at runtime via federated modules.
  Each remote builds independently and exposes components/pages.

// next.config.js (host app)
const { NextFederationPlugin } = require("@module-federation/nextjs-mf");

module.exports = {
  webpack(config) {
    config.plugins.push(
      new NextFederationPlugin({
        name: "host",
        remotes: {
          checkout: "checkout@https://checkout.example.com/_next/static/ssr/remoteEntry.js",
          dashboard: "dashboard@https://dashboard.example.com/_next/static/ssr/remoteEntry.js",
        },
        shared: {
          react: { singleton: true, requiredVersion: "^18" },
          "react-dom": { singleton: true, requiredVersion: "^18" },
        },
      })
    );
    return config;
  },
};

// Usage in host:
const RemoteCheckout = dynamic(() => import("checkout/CheckoutPage"), {
  ssr: false,
  loading: () => <CheckoutSkeleton />,
});
```

### Single-SPA
```
When to use:
  ✅ Mixing frameworks (React + Vue + Angular) — rare but happens in acquisitions
  ✅ Need lifecycle management for multiple apps on one page
  ❌ Overkill if all apps are React/Next.js (use Module Federation or monorepo)
  ❌ Heavy runtime overhead

// Root config
import { registerApplication, start } from "single-spa";

registerApplication({
  name: "navbar",
  app: () => System.import("@org/navbar"),
  activeWhen: ["/"],
});

registerApplication({
  name: "dashboard",
  app: () => System.import("@org/dashboard"),
  activeWhen: ["/dashboard"],
});

start();
```

### Server-Side Composition
```
When to use:
  ✅ SEO-critical pages need full SSR from multiple teams
  ✅ Edge-side includes (ESI) for assembling pages at CDN level
  ✅ Maximum isolation — each team owns a full page/route
  ❌ Complex to set up, limited interactivity between fragments

Implementation:
  - Each team owns routes (e.g., /checkout/*, /dashboard/*)
  - Reverse proxy (Vercel rewrites, Cloudflare Workers, Nginx) routes to correct app
  - Shared header/footer served as edge-side includes or shared component
```

### Monorepo with Package Boundaries (Recommended Default)
```
When to use:
  ✅ 2-5 teams, all using React/Next.js — this is the default recommendation
  ✅ Want shared code without runtime overhead
  ✅ Need independent deployments but shared build infrastructure
  ✅ Strong typing and refactoring across packages

This is the right choice for 80% of teams considering micro-frontends.
Module Federation and single-spa add complexity that most teams don't need.

apps/
  web/            → Main customer-facing app (Next.js)
  admin/          → Admin dashboard (Next.js)
  docs/           → Documentation site (Next.js or Astro)
packages/
  ui/             → Shared design system components
  config/         → Shared ESLint, TypeScript, Tailwind configs
  lib/            → Shared utilities, hooks, API clients
  types/          → Shared TypeScript types
```

## Step 4: Monorepo Management

See [reference/details.md](reference/details.md) (section “Step 4: Monorepo Management”) for full detail.

## Step 5: Shared Dependency Strategy

### Design System as Internal Package
```
packages/ui/
  src/
    components/
      Button.tsx
      Input.tsx
      Modal.tsx
      DataTable.tsx
    primitives/         → Radix UI or Headless UI wrappers
    tokens/
      colors.ts
      spacing.ts
      typography.ts
    index.ts            → Public API (explicit exports only)
  package.json
  tsconfig.json
  tailwind.config.ts    → Shared Tailwind preset

// packages/ui/package.json
{
  "name": "@project/ui",
  "version": "0.0.0",
  "main": "./src/index.ts",
  "types": "./src/index.ts",
  "exports": {
    ".": "./src/index.ts",
    "./tokens": "./src/tokens/index.ts",
    "./tailwind": "./tailwind.config.ts"
  },
  "peerDependencies": {
    "react": "^18",
    "react-dom": "^18"
  }
}

// Usage in apps:
import { Button, DataTable } from "@project/ui";
import { colors } from "@project/ui/tokens";
```

### Version Alignment Policy
```
Shared dependencies MUST be pinned to the same version across all apps:

// packages/config/base-dependencies.json
{
  "react": "^18.3.0",
  "react-dom": "^18.3.0",
  "next": "^14.2.0",
  "typescript": "^5.4.0",
  "tailwindcss": "^3.4.0"
}

Enforcement:
  1. Syncpack for version alignment: npx syncpack lint
  2. Renovate/Dependabot with group updates (update React everywhere at once)
  3. CI check that fails if versions diverge

// .github/workflows/check-deps.yml
- name: Check dependency alignment
  run: npx syncpack lint --types prod,dev
```

### Shared Config Packages
```
packages/config/
  eslint/
    base.js           → Shared ESLint config
    react.js          → React-specific rules
    next.js           → Next.js-specific rules
  typescript/
    base.json         → Shared tsconfig
    react.json        → React tsconfig (extends base)
    next.json         → Next.js tsconfig (extends react)
  tailwind/
    preset.ts         → Shared Tailwind preset with design tokens

// apps/web/tsconfig.json
{ "extends": "@project/config/typescript/next.json" }

// apps/web/.eslintrc.js
module.exports = { extends: ["@project/config/eslint/next"] }

// apps/web/tailwind.config.ts
import preset from "@project/config/tailwind/preset";
export default { presets: [preset], content: ["./src/**/*.tsx", "../../packages/ui/**/*.tsx"] }
```

## Step 6: Independent Deployment

### Per-App CI/CD
```yaml
# .github/workflows/deploy-web.yml
name: Deploy Web App
on:
  push:
    branches: [main]
    paths:
      - 'apps/web/**'
      - 'packages/ui/**'      # Rebuild if shared UI changes
      - 'packages/lib/**'     # Rebuild if shared lib changes
      - 'packages/config/**'  # Rebuild if shared config changes

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup
        uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'npm'

      - run: npm ci

      - name: Build (with Turborepo cache)
        run: npx turbo run build --filter=web...
        env:
          TURBO_TOKEN: ${{ secrets.TURBO_TOKEN }}
          TURBO_TEAM: ${{ secrets.TURBO_TEAM }}

      - name: Deploy to Vercel
        run: vercel deploy --prod --token=${{ secrets.VERCEL_TOKEN }}
        working-directory: apps/web
```

### Contract Testing Between Micro-Frontends
```
When apps consume shared packages or remote modules,
test the contracts to prevent breaking changes.

// packages/ui/src/__tests__/Button.contract.test.tsx
// This test defines the public API contract for Button.
// If this test breaks, consuming apps will also break.
describe("Button contract", () => {
  it("renders with required props", () => {
    render(<Button onClick={vi.fn()}>Click me</Button>);
    expect(screen.getByRole("button")).toBeInTheDocument();
  });

  it("supports variant prop", () => {
    render(<Button variant="primary" onClick={vi.fn()}>Click</Button>);
    // Verify the contract — not the implementation
  });

  it("forwards ref", () => {
    const ref = createRef<HTMLButtonElement>();
    render(<Button ref={ref} onClick={vi.fn()}>Click</Button>);
    expect(ref.current).toBeInstanceOf(HTMLButtonElement);
  });
});

// Run contract tests in CI before publishing shared packages
// If contract tests fail → shared package update is blocked
```

### Preview Deployments Per PR
```
Every PR gets its own preview environment:

Vercel: automatic — every push to a PR branch gets a unique URL
  https://web-git-feature-xyz-team.vercel.app

For monorepos, configure per-app preview:
  1. Vercel project per app (web, admin, docs)
  2. Each linked to the same monorepo
  3. Root directory set to apps/web, apps/admin, etc.
  4. Vercel auto-detects which app changed and deploys only that one

GitHub PR comment (add via GitHub Action):
  "Preview deployments:
    - Web: https://web-git-BRANCH-team.vercel.app
    - Admin: https://admin-git-BRANCH-team.vercel.app
    - Storybook: https://storybook-git-BRANCH-team.vercel.app"
```

## Step 7: State and Routing

See [reference/details.md](reference/details.md) (section “Step 7: State and Routing”) for full detail.

## Code Generation (Required)

Generate monorepo infrastructure using Write:

1. **Root config**: `turbo.json` or `nx.json` — monorepo task orchestration
2. **Workspace config**: `pnpm-workspace.yaml` — package discovery
3. **Shared UI package**: `packages/ui/package.json` — component library setup
4. **Shared types**: `packages/types/package.json` — shared TypeScript types
5. **App template**: `apps/template/package.json` — starter app config with module federation
6. **CI workflow**: `.github/workflows/monorepo-ci.yml` — affected-only builds and tests

Before generating, Glob for existing workspace configs and Read package.json to understand current structure.

## Step 8: When NOT to Use Micro-Frontends

```
Do NOT use micro-frontends if:

❌ Small team (1-3 frontend developers)
   → Use a monolith. You don't have the coordination problem micro-frontends solve.

❌ Single product with one user journey
   → Micro-frontends add overhead without benefit for linear products.

❌ Premature optimization
   → "We might need multiple teams someday" is not a reason. Refactor when you need it.

❌ Performance-critical with tight bundle budget
   → Micro-frontend runtime adds 20-50KB overhead. If your total budget is 100KB, don't.

❌ Shared state everywhere
   → If every component needs access to the same state, you don't have independent frontends.

Instead, use:
  ✅ Monorepo with package boundaries (Turborepo) — gets you 80% of the benefits
  ✅ Route-based code splitting — Next.js does this automatically
  ✅ Feature flags — deploy independently without micro-frontend complexity
  ✅ Shared component library — extract UI without architectural overhead

The right question is NOT "should we use micro-frontends?"
The right question is: "Are teams blocked from shipping independently?"
If yes → micro-frontends. If no → monorepo with good boundaries.
```

## Step 9: Output

```
MICRO-FRONTEND ARCHITECTURE
Project: [NAME]
Date: [TODAY]
Prepared by: [NAME]

ARCHITECTURE SUMMARY
┌──────────────────────────┬────────────────────────────────────┐
│ Field                    │ Value                              │
├──────────────────────────┼────────────────────────────────────┤
│ Pattern                  │ [Monorepo / Module Fed / Compose]  │
│ Build Tool               │ [Turborepo / Nx]                   │
│ Apps                     │ [Count, names]                     │
│ Shared Packages          │ [Count: ui, lib, config, types]    │
│ Teams                    │ [Count, ownership map]             │
│ Deploy Strategy          │ [Per-app / monolithic]             │
│ Shared State             │ [Auth method, event bus if needed] │
│ Recommended?             │ [Yes / No — use monorepo instead]  │
└──────────────────────────┴────────────────────────────────────┘

DELIVERABLES GENERATED:
  - [ ] Architecture pattern selection with rationale
  - [ ] Monorepo workspace configuration (Turborepo or Nx)
  - [ ] Shared package structure (ui, config, lib, types)
  - [ ] Per-app CI/CD pipeline with path-based triggers
  - [ ] Shared dependency version alignment config
  - [ ] Cross-app routing and URL ownership map
  - [ ] Shared auth strategy
  - [ ] Contract tests for shared packages
  - [ ] Preview deployment setup per app
  - [ ] When-not-to-use assessment

RELATED SKILLS:
  - /nextjs-feature-scaffold — per-app Next.js patterns
  - /ci-cd-pipeline — CI/CD for monorepo deployments
  - /infrastructure-scaffold — hosting and deployment infra
  - /testing-strategy — testing pyramid for monorepo
```
