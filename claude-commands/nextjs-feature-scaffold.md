# Next.js Feature Scaffold

**Outcome:** a working feature in the project's existing conventions — typed data layer, Server Actions with validation and auth, Server Components by default with Client islands, loading/error/not-found boundaries, metadata, and tests — that builds and passes lint and tests. Done when the files in the Generation Order exist, `next build` succeeds, and the summary table lists what was created.

## Pre-Processing (Auto-Context)

Context (pre-filled in Claude Code; in other runtimes run these commands first):

- Versions: !`grep -oE '"(next|react|zod|tailwindcss|vitest|@playwright/test|firebase)": *"[^"]+"' package.json 2>/dev/null | head -8 || echo "(no package.json)"`
- Config flags: !`grep -hoE "output: *['\"][a-z]+['\"]|cacheComponents: *(true|false)|reactCompiler: *(true|false)" next.config.* 2>/dev/null | head -4 || echo "(defaults)"`
- Request interception: !`ls proxy.ts src/proxy.ts middleware.ts src/middleware.ts 2>/dev/null || echo "(none)"`
- Existing routes: !`find src/app app -maxdepth 3 -name page.tsx 2>/dev/null | head -12`

## Step 1: Classify the Feature Type

| Feature | Pattern |
|---|---|
| Static page (marketing, blog) | Server Component; `'use cache'` if Cache Components is on, else static by default |
| Dynamic page (dashboard, profile) | Server Component + Client islands; dynamic parts inside `<Suspense>` |
| Form (contact, checkout, settings) | Client form + Server Action with Zod validation and auth check |
| Data table / list | Server fetch + Client sort/filter via `searchParams` |
| Auth-gated page | Session check in the layout/page **and** in every Server Action/Route Handler; `proxy.ts` only for optimistic redirects |
| Real-time (chat, notifications) | Client Component + Firebase listener / WebSocket |
| API endpoint | Route Handler `app/api/<name>/route.ts` |
| Full CRUD | All of the above |

A question about Next.js (not a build request) gets an answer, not scaffolding.

## Step 2: Gather Context

Ask only what auto-context didn't answer: feature name; data source (Firestore, Postgres, REST); auth model (public, signed-in, role-based); deployment (Vercel/Node server vs `output: 'export'` on Firebase Hosting); i18n (`[lang]` segment or not); SEO needs.

## Step 3: Directory Structure (one layout — use it for generation)

```
src/
├── app/[lang]/<feature>/           # drop [lang] if single-locale
│   ├── page.tsx                    # Server Component
│   ├── loading.tsx · error.tsx ('use client') · not-found.tsx
│   └── [id]/page.tsx
├── components/<feature>/           # FeatureList, FeatureCard, FeatureForm ('use client'), FeatureFilters
├── lib/<feature>/
│   ├── queries.ts                  # server-only reads (import 'server-only')
│   ├── actions.ts                  # 'use server' mutations
│   ├── schema.ts                   # Zod schemas + inferred types
│   └── types.ts
└── __tests__/<feature>/            # unit/component tests; Playwright specs live in e2e/
```

If the project already uses a different convention (e.g. colocated `_components/`), follow the project.

## Step 4: Rules That Differ From Older Next.js (Next 15/16)

- **Async request APIs.** `params`, `searchParams`, `cookies()`, `headers()`, `draftMode()` are Promises; synchronous access was removed in Next 16. Type them `params: Promise<{ id: string }>` and `await` them — including in `generateMetadata`.
- **`proxy.ts` replaces `middleware.ts`** (Next 16; runs on Node.js, export `proxy`). Migrate with `npx @next/codemod@canary middleware-to-proxy .`. Keep it for redirects/rewrites/headers. **Never make it the only auth check**: CVE-2025-29927 bypassed middleware auth, and Server Actions skip proxy whenever a matcher excludes their route — verify the session inside every Server Action and Route Handler because each one is a public POST endpoint.
- **Caching is opt-in.** With `cacheComponents: true`, mark cacheable functions/components with `'use cache'` plus `cacheLife()` / `cacheTag()`; everything else renders per request. After mutations: `updateTag(tag)` in Server Actions for read-your-writes, `revalidateTag(tag, 'max')` for stale-while-revalidate (the single-argument form is deprecated), `revalidatePath('/[lang]/items/[id]', 'page')` — the type argument is required when the path contains dynamic segments.
- **Validation (Zod 4).** `schema.safeParse(...)`; return errors with `z.flattenError(result.error)` (flat forms) or `z.treeifyError` (nested) — `error.flatten()` is deprecated.
- **Forms.** `useActionState(action, initialState)` for pending/error state; `useFormStatus` in the submit button.
- **Server/Client split.** `'use client'` only for state, effects, event handlers, or browser APIs; pass Server Components as `children` into Client wrappers instead of converting the parent. Data reads happen in Server Components or `queries.ts` wrapped in React `cache()` for per-request dedupe.
- **Tailwind v4** is CSS-first (`@theme` in global CSS, no `tailwind.config.ts`); use tokens from `web-design-expert`, `cn()` for conditional classes.
- **Images.** `next/image` with dimensions; `images.remotePatterns` (not `domains`); local images with query strings need `images.localPatterns`.
- **Lint.** `next lint` is removed in Next 16; run ESLint (flat config `eslint.config.mjs`) or Biome directly.

### Static export (`output: 'export'`, Firebase Hosting)

No Server Actions, `proxy.ts`, ISR/revalidation, or cookies/headers at request time. Every dynamic route needs `generateStaticParams`; images need `unoptimized: true`; redirects go in `firebase.json`; auth and data use the client Firebase SDK plus callable Functions.

## Step 5: Minimal Server Action Pattern

```typescript
// src/lib/<feature>/actions.ts
'use server';
import { z } from 'zod';
import { updateTag } from 'next/cache';
import { getSession } from '@/lib/auth';
import { createItemSchema } from './schema';

export type ActionState = { ok: boolean; errors?: ReturnType<typeof z.flattenError> };

export async function createItem(_prev: ActionState, formData: FormData): Promise<ActionState> {
  const session = await getSession();            // auth inside the action, every time
  if (!session) return { ok: false };
  const parsed = createItemSchema.safeParse(Object.fromEntries(formData));
  if (!parsed.success) return { ok: false, errors: z.flattenError(parsed.error) };
  // write to Firestore / DB
  updateTag(`items-${session.userId}`);
  return { ok: true };
}
```

## Step 6: SEO

Every `page.tsx` exports `generateMetadata` (awaiting `params`) with title, description (<160 chars), and Open Graph. Content pages add JSON-LD via `<script type="application/ld+json">`. Deeper SEO work belongs to `seo-content-engine`.

## Code/Artifact Generation

Applies when Step 1 classified a build request (the default for this skill). Generate in this order, matching existing project conventions found in auto-context:

1. `lib/<feature>/schema.ts` and `types.ts`
2. `lib/<feature>/queries.ts`
3. `lib/<feature>/actions.ts` or `app/api/<name>/route.ts`
4. `app/.../<feature>/page.tsx` (+ `layout.tsx` if needed), with `generateMetadata`
5. Client components in `components/<feature>/`
6. `loading.tsx`, `error.tsx`, `not-found.tsx`
7. Tests in `__tests__/<feature>/` (Vitest + React Testing Library, MSW for network); a Playwright spec in `e2e/` only for a critical flow. Coverage and retry policy come from `testing-strategy`.
8. A summary table of files created.

Scaffold the requested feature only; don't refactor unrelated routes or upgrade dependencies unless asked.

## Related

`web-design-expert` (visual spec and tokens) · `database-architect` / `firebase-architect` (data model, rules) · `api-architect` (Route Handler contracts) · `testing-strategy` (test standards) · `e2e-testing` (Playwright) · `seo-content-engine` (metadata and structured data)
