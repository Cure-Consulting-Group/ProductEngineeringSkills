# micro-frontends: detailed reference

Implementation detail for `micro-frontends`, read when writing routing config, shared auth, an event bus, or the URL ownership map. Monorepo setup (workspaces, Turborepo/Nx, remote cache) lives in `monorepo-navigator`.

## State and Routing

### Cross-App Navigation
```typescript
// Option 1: Next.js multi-zones (route-level split, self-hosted or any host)
// Zone app: next.config.ts
const nextConfig = { assetPrefix: '/checkout-static' };   // unique per zone; default zone needs none

// Host app: next.config.ts — rewrite the zone's pages AND its static assets
async rewrites() {
  return [
    { source: '/checkout', destination: `${process.env.CHECKOUT_ORIGIN}/checkout` },
    { source: '/checkout/:path+', destination: `${process.env.CHECKOUT_ORIGIN}/checkout/:path+` },
    { source: '/checkout-static/:path+', destination: `${process.env.CHECKOUT_ORIGIN}/checkout-static/:path+` },
  ];
}
// Gotchas (Next.js multi-zones guide, 2026):
//  - Cross-zone links use <a>, not <Link> — <Link> prefetches/soft-navigates and breaks across zones.
//  - Cross-zone navigation is a hard page load; keep pages visited together in one zone.
//  - Server Actions need experimental.serverActions.allowedOrigins = ['<user-facing domain>'].
//  - Use proxy.ts instead of rewrites only for dynamic routing (e.g. flag-driven migration).
// On Vercel, prefer Vercel Microfrontends: routing lives in microfrontends.json, not rewrites.

// User sees: example.com/checkout/cart → served by checkout app
// User sees: example.com/dashboard → served by dashboard app
// Shared header/footer loaded as shared component or edge-side include

// Option 2: No split — one Next.js app, route groups owned per team (CODEOWNERS on each group):
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
// One sign-in for all zones; each zone still verifies the session server-side.

// Option 1: Shared cookie (same domain)
// Set auth cookie on .example.com — accessible by all subdomains
// Verified server-side in each zone (layouts, Server Actions, Route Handlers) — proxy.ts may
// redirect early but must not be the only check (see nextjs-feature-scaffold)

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
