---
name: nextjs-feature-scaffold
description: "Scaffold Next.js features with App Router, Server/Client components, Tailwind, and data fetching patterns"
argument-hint: "[feature-name]"
---

# Next.js Feature Scaffold

Full-stack Next.js feature scaffolding with App Router, Server/Client components, TypeScript, and Tailwind CSS. Platform-aware patterns for static export (Firebase Hosting) and server-side (Vercel/Node).

## Step 1: Classify the Feature Type

| Feature | Pattern |
|---------|---------|
| Static page (marketing, blog) | Server Component, static export |
| Dynamic page (dashboard, profile) | Server Component + Client islands |
| Interactive form (contact, checkout) | Client Component with Server Action or API route |
| Data table / list | Server Component fetch + Client sort/filter |
| Auth-gated page | Middleware + layout guard |
| Real-time feature (chat, notifications) | Client Component + WebSocket/Firebase listener |
| API endpoint | Route Handler (`app/api/`) |
| Full CRUD feature | All of the above combined |

## Step 2: Gather Context

1. **Feature name** — what are we building?
2. **Data source** — Firebase, REST API, database, static?
3. **Auth required** — public, authenticated, role-based?
4. **Deployment target** — static export (Firebase) or server (Vercel)?
5. **i18n** — single language or multi-locale?
6. **SEO requirements** — metadata, structured data, OG tags?

## Step 3: Directory Structure

```
src/
├── app/
│   └── [lang]/                    # i18n segment (if multi-locale)
│       └── [feature]/
│           ├── page.tsx           # Route page (Server Component default)
│           ├── layout.tsx         # Feature layout (if needed)
│           ├── loading.tsx        # Loading UI (Suspense boundary)
│           ├── error.tsx          # Error boundary (Client Component)
│           ├── not-found.tsx      # 404 for this route
│           └── [id]/
│               └── page.tsx       # Dynamic route
├── components/
│   └── [feature]/
│       ├── FeatureList.tsx        # Server or Client depending on interactivity
│       ├── FeatureCard.tsx        # Presentational component
│       ├── FeatureForm.tsx        # Client Component ("use client")
│       └── FeatureFilters.tsx     # Client Component for interactive filtering
├── lib/
│   └── [feature]/
│       ├── actions.ts             # Server Actions (mutations)
│       ├── queries.ts             # Data fetching functions
│       ├── types.ts               # TypeScript interfaces
│       └── validation.ts          # Zod schemas for form validation
└── __tests__/
    └── [feature]/
        ├── page.test.tsx          # Route tests
        └── components.test.tsx    # Component tests
```

## Step 4: Code Generation Rules

1. **Server Components by default** — only add `"use client"` when the component needs useState, useEffect, event handlers, or browser APIs
2. **Never mix** — a Server Component cannot use hooks. Extract interactive parts into a separate Client Component child
3. **Data fetching in Server Components** — use `async` function components, not useEffect
4. **TypeScript strict** — no `any`, explicit return types on exported functions, Zod for runtime validation
5. **Tailwind only** — no CSS modules, no styled-components. Use `cn()` utility for conditional classes
6. **Accessible by default** — semantic HTML, ARIA labels on interactive elements, keyboard navigation
7. **Error boundaries** — every route gets `error.tsx`, every async operation gets try/catch
8. **Loading states** — every route with data fetching gets `loading.tsx`
9. **Metadata** — every page exports `generateMetadata` for SEO
10. **Images** — use `next/image` with explicit width/height. For static export: `unoptimized: true`

## Step 5: Component Decision Tree

```
Does this component need interactivity (state, effects, events)?
  ├── NO  → Server Component (default, no directive)
  │         Can it fetch data?
  │         ├── YES → async function component, fetch in body
  │         └── NO  → pure presentational, receives props
  └── YES → Client Component ("use client")
            Does it need data from server?
            ├── YES → Parent = Server Component passes data as props
            │         OR use Server Action for mutations
            └── NO  → Self-contained Client Component
```

## Step 6: Data Patterns

### Server-Side Data Fetching
```typescript
// lib/[feature]/queries.ts
import { cache } from 'react';

export const getFeatureById = cache(async (id: string) => {
  // Firebase, REST, or database call
  // Runs on server only — safe for secrets
});
```

### Server Actions (Mutations)
```typescript
// lib/[feature]/actions.ts
"use server";

import { revalidatePath } from 'next/cache';
import { z } from 'zod';

const schema = z.object({ name: z.string().min(1) });

export async function createFeature(formData: FormData) {
  const parsed = schema.safeParse(Object.fromEntries(formData));
  if (!parsed.success) return { error: parsed.error.flatten() };

  // Create in database/Firebase
  revalidatePath('/[lang]/[feature]');
  return { success: true };
}
```

### Client-Side State (when needed)
```typescript
// For complex client state: useReducer > useState
// For shared client state: React Context (small) or Zustand (large)
// For server cache: React Query / SWR (only if you need client-side refetching)
```

## Step 7: Static Export Constraints

When `output: "export"` (Firebase Hosting):
- No Server Actions — use API routes or Firebase callable functions
- No `revalidatePath` / `revalidateTag` — fully static
- No middleware redirects at runtime — use `firebase.json` redirects
- All dynamic routes need `generateStaticParams`
- Images require `unoptimized: true` in next.config
- Use client-side Firebase SDK for auth and real-time data

## Step 8: SEO & Metadata

```typescript
// Every page.tsx:
export async function generateMetadata({ params }): Promise<Metadata> {
  return {
    title: 'Page Title | Site Name',
    description: 'Clear description under 160 chars',
    openGraph: {
      title: '...',
      description: '...',
      type: 'website',
      images: ['/og-image.png'],
    },
  };
}
```

For blog/content pages, add JSON-LD:
```typescript
<script type="application/ld+json" dangerouslySetInnerHTML={{
  __html: JSON.stringify({
    "@context": "https://schema.org",
    "@type": "Article",
    headline: post.title,
    datePublished: post.date,
    author: { "@type": "Organization", name: "Company" },
  })
}} />
```

## Step 9: Testing Standards

```
Unit:        Vitest + React Testing Library
Integration: Vitest + MSW (mock API responses)
E2E:         Playwright (critical user flows)
```

Test file naming: `[component].test.tsx` co-located in `__tests__/`

## Generation Order

1. Types (`types.ts`)
2. Validation schemas (`validation.ts`)
3. Data queries (`queries.ts`)
4. Server actions or API routes (`actions.ts`)
5. Server Components (page, layout)
6. Client Components (forms, interactive elements)
7. Loading/Error boundaries
8. Tests
9. Summary table of generated files
