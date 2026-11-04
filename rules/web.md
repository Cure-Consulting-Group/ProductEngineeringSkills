---
paths:
  - "**/*.tsx"
  - "**/*.jsx"
  - "**/app/**/*.{ts,js}"
  - "**/components/**/*.{ts,js}"
  - "**/lib/**/*.{ts,js}"
  - "**/proxy.ts"
  - "**/middleware.ts"
  - "**/next.config.*"
---

# Web Development Standards (Next.js + TypeScript)

- Next.js 16 App Router — Server Components by default; `'use client'` only at interactive leaves
- Async request APIs: `params`, `searchParams`, `cookies()`, `headers()`, `draftMode()` are Promises (sync access was removed in 16) — type `params: Promise<{ id: string }>` and `await` them, including in `generateMetadata()`
- Caching is opt-in: with `cacheComponents: true`, mark cacheable functions/components `'use cache'` plus `cacheLife()`/`cacheTag()`; after mutations use `updateTag()` (read-your-writes) or `revalidateTag(tag, 'max')`
- `proxy.ts` replaces `middleware.ts` — redirects, rewrites, headers only; never the only auth check. Verify the session in every Server Action and Route Handler (each is a public endpoint)
- Server Actions for mutations — no API routes for form submissions
- Zod 4 at every boundary (forms, API responses, env vars): `safeParse`, then `z.flattenError()`
- TypeScript strict — no `any`, no `@ts-ignore`
- Tailwind v4, CSS-first: tokens under `@theme` in global CSS, no `tailwind.config.ts` by default; no CSS-in-JS
- Server data comes from Server Components; TanStack Query only for client-only or live data
- Testing: Vitest + React Testing Library for unit/component tests, Playwright for E2E
- Accessibility: semantic HTML, labelled controls, keyboard navigation, WCAG 2.2 AA minimum

Verified 2026-10-24: Next.js 16.4 is current (nextjs.org/blog, 2026-10-06). Matches `nextjs-feature-scaffold` and `web-design-expert`.
