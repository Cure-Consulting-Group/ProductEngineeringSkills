---
paths:
  - "**/*.ts"
  - "**/*.tsx"
  - "**/*.js"
  - "**/*.jsx"
---

# Web Development Standards (Next.js + TypeScript)

- Next.js App Router — Server Components by default, Client Components only for interactivity
- Server Actions for mutations — no API routes for form submissions
- TypeScript strict mode — no `any` types, no `@ts-ignore`
- Tailwind CSS for styling — no CSS modules, no inline styles, no styled-components
- Zod for runtime validation at all boundaries (forms, API responses, env vars)
- Data fetching: fetch() in Server Components with cache/revalidation, React Query for client-side
- Metadata API for SEO — generateMetadata() in layouts and pages
- Testing: Vitest for unit tests, Playwright for E2E
- Accessibility: semantic HTML, ARIA labels, keyboard navigation, WCAG AA minimum
