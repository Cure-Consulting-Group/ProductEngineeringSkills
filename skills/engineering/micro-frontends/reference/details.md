# micro-frontends: detailed reference

> Reference material for the `micro-frontends` skill, split out for progressive disclosure. Loaded on demand from SKILL.md.

## Contents
- Step 4: Monorepo Management
- Step 7: State and Routing

## Step 4: Monorepo Management

### Turborepo Setup
```json
// turbo.json
{
  "$schema": "https://turbo.build/schema.json",
  "globalDependencies": ["**/.env.*local"],
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": [".next/**", "!.next/cache/**", "dist/**"]
    },
    "lint": {
      "dependsOn": ["^build"]
    },
    "test": {
      "dependsOn": ["^build"]
    },
    "dev": {
      "cache": false,
      "persistent": true
    },
    "type-check": {
      "dependsOn": ["^build"]
    }
  }
}
```

### Workspace Configuration
```json
// package.json (root)
{
  "name": "project-monorepo",
  "private": true,
  "workspaces": ["apps/*", "packages/*"],
  "scripts": {
    "build": "turbo run build",
    "dev": "turbo run dev",
    "lint": "turbo run lint",
    "test": "turbo run test",
    "type-check": "turbo run type-check",
    "clean": "turbo run clean && rm -rf node_modules"
  },
  "devDependencies": {
    "turbo": "^2.0.0"
  }
}
```

### Build Caching
```
Turborepo caches build outputs based on file hashes.
Remote caching shares cache across CI and developers.

# Enable Vercel Remote Cache (free for Vercel users)
npx turbo login
npx turbo link

# Or self-hosted cache (S3/GCS)
# Set TURBO_REMOTE_CACHE_SIGNATURE_KEY and TURBO_API/TURBO_TOKEN

Expected impact:
  - Local rebuilds: 80-95% cache hit rate (only rebuild changed packages)
  - CI builds: 60-80% cache hit rate (rebuild only affected apps)
  - Build time reduction: 3-10x for incremental changes

Cache rules:
  - turbo.json pipeline.build.outputs defines what gets cached
  - globalDependencies defines what invalidates ALL caches
  - Per-task inputs can be customized for fine-grained invalidation
```

### Nx Alternative
```
Use Nx instead of Turborepo when:
  ✅ Need built-in code generators (nx generate)
  ✅ Want affected-only testing (nx affected:test)
  ✅ Need module boundary enforcement (ESLint rules)
  ✅ Larger monorepo (>20 packages) — Nx has better graph analysis

// nx.json
{
  "targetDefaults": {
    "build": { "dependsOn": ["^build"], "cache": true },
    "test": { "cache": true },
    "lint": { "cache": true }
  },
  "affected": { "defaultBase": "main" }
}

// Enforce module boundaries (prevent circular deps)
// .eslintrc.json
{
  "rules": {
    "@nx/enforce-module-boundaries": ["error", {
      "depConstraints": [
        { "sourceTag": "scope:app", "onlyDependOnLibsWithTags": ["scope:shared", "scope:ui"] },
        { "sourceTag": "scope:ui", "onlyDependOnLibsWithTags": ["scope:shared"] },
        { "sourceTag": "scope:shared", "onlyDependOnLibsWithTags": ["scope:shared"] }
      ]
    }]
  }
}
```

## Step 7: State and Routing

### Cross-App Navigation
```typescript
// Option 1: URL-based routing (recommended for strong isolation)
// Each app owns a set of routes. Navigation = standard links.

// Host app rewrites in next.config.js or vercel.json:
{
  "rewrites": [
    { "source": "/checkout/:path*", "destination": "https://checkout.example.com/:path*" },
    { "source": "/dashboard/:path*", "destination": "https://dashboard.example.com/:path*" }
  ]
}

// User sees: example.com/checkout/cart → served by checkout app
// User sees: example.com/dashboard → served by dashboard app
// Shared header/footer loaded as shared component or edge-side include

// Option 2: Monorepo shared router (recommended for package-based approach)
// Single Next.js app with route groups per team:
app/
  (marketing)/        → Team A owns
    page.tsx
    pricing/page.tsx
  (dashboard)/        → Team B owns
    dashboard/page.tsx
    settings/page.tsx
  (checkout)/         → Team C owns
    checkout/page.tsx
    cart/page.tsx
  layout.tsx          → Shared layout (header, footer, providers)
```

### Shared Auth State
```typescript
// Auth MUST be shared across all micro-frontends.
// Never ask users to log in per-app.

// Option 1: Shared cookie (same domain)
// Set auth cookie on .example.com — accessible by all subdomains
// JWT token verified at edge middleware (see /edge-computing skill)

// Option 2: Shared auth package (monorepo)
// packages/auth/
import { AuthProvider, useAuth } from "@project/auth";

// AuthProvider wraps the entire app:
export function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthProvider
      firebaseConfig={config}
      onAuthStateChange={(user) => {
        // Sync auth state to all micro-frontends
        // Set cookie, update context, redirect if needed
      }}
    >
      {children}
    </AuthProvider>
  );
}

// Every app imports useAuth:
const { user, signIn, signOut, isLoading } = useAuth();
```

### Event Bus for Inter-App Communication
```typescript
// For loosely coupled communication between micro-frontends.
// Use sparingly — prefer URL params and shared state via auth/context.

// packages/event-bus/src/index.ts
type EventMap = {
  "cart:updated": { itemCount: number };
  "user:preferences-changed": { theme: "light" | "dark" };
  "notification:received": { message: string; type: "info" | "error" };
};

class EventBus {
  private listeners = new Map<string, Set<Function>>();

  on<K extends keyof EventMap>(event: K, callback: (data: EventMap[K]) => void) {
    if (!this.listeners.has(event)) this.listeners.set(event, new Set());
    this.listeners.get(event)!.add(callback);
    return () => this.listeners.get(event)!.delete(callback);
  }

  emit<K extends keyof EventMap>(event: K, data: EventMap[K]) {
    this.listeners.get(event)?.forEach((cb) => cb(data));
  }
}

// Singleton — shared across all micro-frontends
export const eventBus = new EventBus();

// Usage: eventBus.emit("cart:updated", { itemCount: 3 });
// Usage: const unsub = eventBus.on("cart:updated", (data) => updateBadge(data.itemCount));
```

### URL Ownership
```
Define clear URL ownership per team. No overlaps.

Team        URL Prefix        App
──────────────────────────────────────────────────
Marketing   /                 apps/web (marketing pages)
Marketing   /blog/*           apps/web
Product     /dashboard/*      apps/admin
Product     /settings/*       apps/admin
Commerce    /checkout/*       apps/checkout
Commerce    /cart/*            apps/checkout
Docs        /docs/*           apps/docs

Rules:
  - Each team owns a URL prefix — no shared routes
  - Shared layout (header, footer) is a package, not an app
  - Redirects between team boundaries use standard HTTP redirects
  - Deep linking must work — every route is bookmarkable
```
