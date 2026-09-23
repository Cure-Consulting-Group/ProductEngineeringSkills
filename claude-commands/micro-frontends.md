# Micro-Frontends

**Outcome:** a composition decision — no split, route-level split (Vercel microfrontends or Next.js multi-zones), or runtime composition (module federation) — with a URL ownership map, shared-auth approach, and migration path, justified by the team's actual release friction. Done when the decision record (Step 6) is filled in; files are written only if the user asks to set it up.

Default answer for most Cure clients: **don't split**. A monorepo with package boundaries (`monorepo-navigator`) plus feature flags solves the problem for teams that aren't blocked on each other's releases. The test is one question: *are teams blocked from shipping independently?*

## Pre-Processing (Auto-Context)

Context (pre-filled in Claude Code; in other runtimes run these commands first):

- Apps and workspace: !`ls apps packages 2>/dev/null | head -20; ls pnpm-workspace.yaml turbo.json nx.json microfrontends.json 2>/dev/null`
- Framework versions: !`grep -hoE '"(next|react|@vercel/microfrontends|@module-federation/[a-z-]+|single-spa)": *"[^"]+"' package.json apps/*/package.json 2>/dev/null | sort -u | head -10`
- Cross-app routing today: !`grep -lE "rewrites|assetPrefix" next.config.* apps/*/next.config.* vercel.json 2>/dev/null | head -5 || echo "(none)"`

## Step 1: Classify

| Situation | Output |
|---|---|
| "Should we do micro-frontends?" | Decision (Step 3) — usually "no, do X instead" |
| Greenfield multi-team product | Decision + URL ownership map + shared-auth plan |
| Monolith decomposition / framework migration | Strangler plan: route-by-route split behind one domain |
| Existing module federation or single-spa setup in trouble | Review findings with severity + migration path |
| Monorepo setup, build caching, shared packages only | Hand off to `monorepo-navigator` |

## Step 2: Gather Context

1. Teams: how many own frontend code, and do they deploy on different cadences today?
2. Friction evidence: releases waiting on another team, merge-queue contention, build times.
3. Frontend: framework(s) and versions, route count, bundle size, hosting (Vercel, Firebase Hosting, self-hosted).
4. Coupling: what state is shared across areas (auth, cart, user prefs)?
5. Performance budget: LCP/INP targets and JS budget.

## Step 3: Decision

| Pattern | Use when | Cost |
|---|---|---|
| **No split** — monorepo, package boundaries, feature flags | 1–5 teams, one framework, no release blocking | Lowest; handled by `monorepo-navigator` |
| **Route-level split, Vercel Microfrontends** | Teams own whole URL prefixes, on Vercel, want one domain | Vercel projects per app; `microfrontends.json` defines path routing; local proxy via `@vercel/microfrontends` / Turborepo. GA; Hobby and Pro include 2 microfrontend projects, extra Pro projects and routed requests are billed (confirm current pricing before quoting) |
| **Route-level split, Next.js multi-zones** | Same as above, self-hosted or not on Vercel | `rewrites` in the host app + `assetPrefix` per zone; hard navigations between zones (full page load) |
| **Runtime composition — module federation** | Several teams must ship widgets into the *same page* independently | Highest: shared-singleton version coupling, runtime failure modes. `@module-federation/nextjs-mf` is in maintenance mode — don't start new Next.js federation on it; for non-Next hosts use Module Federation 2 with Rspack/Rsbuild or Vite |
| **single-spa** | Mixed frameworks during an acquisition or rewrite | Heavy runtime; plan its removal |
| **Edge/server includes** | SEO-critical pages assembled from several teams' fragments | Complex; limited interactivity between fragments |

Route-level split is the default when splitting is justified: strongest isolation, no shared runtime, independent deploys, and it doubles as an incremental migration path (legacy app keeps unowned routes).

Don't split when: 1–3 frontend developers; one linear user journey; "we might need it someday"; shared state touches every screen; or the JS budget can't absorb duplicated framework runtime across zones.

## Step 4: Cross-Cutting Rules

- **URL ownership.** Each team owns URL prefixes; no shared routes. Shared header/footer is a package, not an app. Every route stays deep-linkable.
- **Auth is shared, once.** Same-site session cookie scoped to the parent domain (or the platform's single-domain routing); every app verifies the session server-side — never trust another zone's client state.
- **Shared dependencies.** Same major versions of React/Next across zones (enforce with syncpack or a CI check); design system as a versioned internal package with contract tests on its public API.
- **Cross-app communication.** Prefer URL state and server data; a typed event bus only for loosely coupled UI signals within one page (federation case).
- **Deploys.** Per-app pipelines triggered by path filters that include shared packages; preview per app per PR; CI conventions from `ci-cd-pipeline`, test policy from `testing-strategy`.

Read [reference/details.md](reference/details.md) when writing the routing config (multi-zones rewrites, route-group ownership in one app), the shared-auth provider, the typed event bus, or a URL ownership table.

## Step 5: Code/Artifact Generation

Applies only when the user asks to set up the chosen pattern. Generate for that pattern only: `microfrontends.json` and per-app `next.config` wiring (Vercel), or host `rewrites` + zone `assetPrefix` (multi-zones), or federation config (federation). Monorepo scaffolding (workspace, `turbo.json`, shared packages) is `monorepo-navigator`'s job. Don't generate a federation template when the decision was "no split" or route-level.

## Step 6: Output — Decision Record

```
MICRO-FRONTEND DECISION — [Project] — [date]
Pattern:          [No split / Vercel microfrontends / multi-zones / federation / single-spa]
Why:              [the release-friction evidence that justifies it, or why it doesn't]
Apps and owners:  [app → team → URL prefixes]
Shared:           [auth approach · design-system package · version policy]
Migration:        [route-by-route order, rollback per route]
Costs/risks:      [runtime, hosting, perf budget impact]
Revisit when:     [trigger, e.g. 4th team or cross-team release waits > 1/week]
```

Match length to the need; no filler sections or restated summaries.

## Related

`monorepo-navigator` (workspace, caching, package boundaries) · `nextjs-feature-scaffold` (per-app features) · `edge-computing` (edge routing) · `ci-cd-pipeline` (per-app pipelines) · `feature-flags` (decoupling release from deploy)
