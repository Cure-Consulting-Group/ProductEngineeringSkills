---
name: seo-content-engine
description: "Technical SEO and search content strategy for websites. Use when a site needs to rank, an SEO audit, metadata, JSON-LD, sitemaps, Core Web Vitals, or keyword clusters."
when_to_use: "NOT for social posts (product-marketing), launch strategy (go-to-market), or one engineering post (technical-blog-writer)."
argument-hint: "[domain-or-topic]"
metadata:
  verified: 2026-09-23
---

# SEO & Content Engine

**Outcome:** search-ready pages and a content plan — every finding or recommendation tied to a page,
a target keyword with search intent, and a concrete fix. Done when the Step 3 critical items pass (or
each failure has a fix) and every planned piece has a keyword and intent. Match length to the need;
no filler sections or restated summaries.

## Pre-Processing (Auto-Context)

Context — run these read-only commands first; skip any that fail or aren't permitted (they only tailor the output):

- Framework: `grep -m2 -oE '"(next|astro|gatsby|nuxt|@remix-run/react)": *"[^"]+"' package.json 2>/dev/null | grep . || echo "(no web framework in package.json)"`
- SEO files: `ls app/sitemap.ts app/robots.ts src/app/sitemap.ts next-sitemap.config.js public/robots.txt 2>/dev/null | head -5 | grep . || echo "(none found)"`

## Step 1: Classify

| Need | Deliver |
|---|---|
| Technical audit | Every issue found, with severity (critical / important / minor), page, and fix |
| Page optimization | Metadata, JSON-LD, internal links for the named pages |
| Content strategy | Topic clusters, keyword map, calendar |
| Blog post optimization | Per-post checklist result |
| Local SEO | Business Profile, NAP, LocalBusiness schema |
| Site architecture | URL scheme, internal linking, sitemap |

## Step 2: Gather Context

Ask only for what is missing: domain, business type, audience, current traffic (Search Console
access?), competitors that rank for the target terms, and content capacity per month.

**Keyword research.** Search the web if a tool is available, with dated sources: "[keyword] search
volume [current year]", "[competitor domain] top pages", "[industry] trends [current year]" — "current
year" meaning the actual year at run time. Volumes from web search are rough; mark them as estimates
unless they come from Search Console, Ahrefs, or Semrush data the user provides. Classify every
keyword's intent (informational, commercial, transactional, navigational) and assign one primary
keyword per page to avoid cannibalization.

## Step 3: Technical Checklist (verified 2026-09-23)

**Critical**
- Unique `<title>` (~50–60 chars) and meta description (~120–155 chars) per page; one `<h1>` matching intent.
- Canonical on every indexable page; `robots.txt` doesn't block important paths; `sitemap.xml` lists public pages and is submitted in Search Console.
- HTTPS, no mixed content, no broken internal links, 301s without chains.
- Mobile usability via Lighthouse and Search Console — Google retired the Mobile-Friendly Test and its report in December 2023.
- **Core Web Vitals at p75 of real users:** LCP ≤2.5s, **INP ≤200ms**, CLS ≤0.1. INP replaced FID as a Core Web Vital on 2024-03-12; don't report FID. Use field data (Search Console / CrUX) over lab scores; deep fixes go to performance-review.

**Important**
- `hreflang` for multi-language sites (Vendly's es-DO / es-MX / pt-BR variants each need reciprocal tags).
- JSON-LD on applicable pages; descriptive image `alt`; clean indexable URLs without query params.
- 3+ contextual internal links per page; Open Graph + Twitter card tags with a 1200×630 image; favicon and apple-touch-icon.

## Step 4: Structured Data

Use JSON-LD. Cure defaults: `Organization` (homepage, with `logo` and `sameAs`), `Service` (service
pages), `BlogPosting` (posts, with `datePublished`, `author`, `image`), `BreadcrumbList` (deep pages),
`Product` + `Offer` (priced products), `LocalBusiness` (local SEO). Validate with Google's Rich Results
Test. Google trims supported rich-result types every year — check the Search Central structured-data
gallery before promising one.

Don't add `FAQPage` or `HowTo` markup for rich results: HowTo rich results were removed in 2023, and
Google stopped showing FAQ rich results for all sites on 2026-05-07 (they had been limited to
government and health sites since August 2023). Existing markup is harmless; keep genuine FAQ content
for readers.

## Step 5: Content Strategy

- **Topic clusters:** one pillar page on the broad commercial term, 4–8 cluster posts on long-tail questions; every cluster post links to the pillar and the pillar links to all of them.
- **Keyword process:** seed 10–20 ICP terms → expand with autocomplete, People Also Ask, related searches → validate volume and difficulty → start with low-difficulty, high-intent terms → map one primary keyword per page.
- **Calendar:** 2–4 posts a month (consistency beats volume); mix ~40% how-to, 30% point of view, 20% case studies, 10% news. Case studies need real client numbers and permission.
- **Per-post check:** primary keyword in title, H1, first 100 words, and slug; title under 60 chars; meta description under 155; 3+ internal and 1–2 authoritative external links; alt text; H2/H3 structure; a CTA; OG image set. Length follows intent — answer the query fully, don't pad to a word count.

## Step 6: Code/Artifact Generation

Applies when Step 1 calls for implementation or briefs. For Next.js App Router (Cure default), use the
built-ins rather than packages:

1. Metadata via the `metadata` export or `generateMetadata` in each route (including `openGraph`, `alternates.canonical`, `alternates.languages`).
2. `app/sitemap.ts` and `app/robots.ts` (no `next-sitemap` needed on the App Router).
3. A small JSON-LD component rendering `<script type="application/ld+json">` from a typed object.
4. `docs/content-briefs/{topic}.md` — keyword, intent, outline, internal links, CTA.

Pages Router projects: `next/head` plus `next-sitemap`. Write only what the classification needs.

## Recurring Mode

This is a recurring goal, not a one-shot (mechanism trade-offs: the `engagement-automation` skill).

- **Cadence:** weekly
- **Session loop:** none — session loops expire after 7 days, so a weekly cadence never fires in-session; it belongs in the cloud routine below.
- **Unattended:** cloud routine — weekly ranking check and brief generation for the active keyword set. Recipes: docs/AUTOMATION.md in the plugin repo.
- **Budget:** ~80k tokens/run; cap at one run per weekly period.
- **Guardrails:** writes only the report file (ranking deltas + new content briefs under `docs/content-briefs/`); no code or page changes; report on failure rather than retrying.
