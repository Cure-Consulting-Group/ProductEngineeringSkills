# SEO & Content Engine

Technical SEO, content strategy, and search optimization for web apps, marketing sites, and blogs. Organic traffic is the cheapest acquisition channel — engineer it.

## Step 1: Classify the SEO Need

| Need | Output |
|------|--------|
| Technical SEO audit | Checklist of issues + fixes |
| Page optimization | Meta tags, structured data, performance |
| Content strategy | Topic clusters, keyword map, calendar |
| Blog optimization | Per-post SEO checklist |
| Local SEO | Google Business Profile, local schema |
| Site architecture | URL structure, internal linking, sitemap |

## Step 2: Gather Context

1. **Site URL** — what domain are we optimizing?
2. **Business type** — SaaS, agency, e-commerce, local business?
3. **Target audience** — who are we trying to reach?
4. **Current traffic** — starting from zero or improving existing?
5. **Competitors** — who ranks for our target terms?
6. **Content capacity** — how many pieces per month?

## Step 3: Technical SEO Checklist

### Critical (Fix Immediately)
- [ ] Every page has unique `<title>` (50-60 chars) and `<meta description>` (120-155 chars)
- [ ] One `<h1>` per page, matches search intent
- [ ] Canonical URLs set on all pages (`<link rel="canonical">`)
- [ ] `robots.txt` allows crawling of important pages
- [ ] `sitemap.xml` exists, includes all public pages, submitted to Search Console
- [ ] HTTPS everywhere, no mixed content
- [ ] No broken links (404s) — check with crawler
- [ ] Mobile-friendly (passes Google Mobile-Friendly Test)
- [ ] Page speed: LCP < 2.5s, FID < 100ms, CLS < 0.1

### Important
- [ ] `hreflang` tags for multi-language sites
- [ ] Structured data (JSON-LD) on all applicable pages
- [ ] Image `alt` text on every image (descriptive, not keyword-stuffed)
- [ ] Clean URL structure (no query params for indexable pages)
- [ ] Internal linking between related pages (3+ internal links per page)
- [ ] 301 redirects for moved/deleted pages (no redirect chains)
- [ ] favicon and apple-touch-icon present
- [ ] Open Graph and Twitter Card meta tags

### Performance (Core Web Vitals)
```
LCP (Largest Contentful Paint):  < 2.5s
  Fix: optimize images, preload hero image, reduce server response time

FID (First Input Delay):  < 100ms
  Fix: reduce JavaScript bundle, defer non-critical scripts

CLS (Cumulative Layout Shift):  < 0.1
  Fix: set explicit dimensions on images/video, avoid dynamic content injection

INP (Interaction to Next Paint):  < 200ms
  Fix: break up long tasks, reduce DOM size
```

## Step 4: Structured Data (JSON-LD)

### Organization (homepage)
```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Company Name",
  "url": "https://example.com",
  "logo": "https://example.com/logo.png",
  "sameAs": ["https://linkedin.com/company/...", "https://twitter.com/..."]
}
```

### Service (service pages)
```json
{
  "@context": "https://schema.org",
  "@type": "Service",
  "name": "Custom App Development",
  "provider": { "@type": "Organization", "name": "Company" },
  "description": "...",
  "areaServed": "US"
}
```

### BlogPosting (blog posts)
```json
{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": "Post Title",
  "datePublished": "2026-01-15",
  "author": { "@type": "Organization", "name": "Company" },
  "image": "https://example.com/post-image.png"
}
```

### FAQ (FAQ sections)
```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "How long does it take to build an app?",
      "acceptedAnswer": { "@type": "Answer", "text": "..." }
    }
  ]
}
```

## Step 5: Content Strategy Framework

### Topic Clusters
```
Pillar Page (broad, high-volume keyword):
  "Custom App Development for Small Businesses"
    └── Cluster posts (long-tail, specific):
        ├── "How Much Does It Cost to Build a Mobile App in 2026?"
        ├── "Native vs Cross-Platform: Which Is Right for Your Business?"
        ├── "5 Signs Your Business Needs a Custom App"
        ├── "How to Choose an App Development Agency"
        └── "What to Expect in Your First App Development Sprint"

Each cluster post links back to pillar page.
Pillar page links to all cluster posts.
```

### Keyword Research Process
```
1. Seed terms: brainstorm 10-20 terms your ICP would search
2. Expand: use Google autocomplete, People Also Ask, related searches
3. Validate: check search volume + difficulty (Ahrefs, SEMrush, Ubersuggest)
4. Prioritize: target low-difficulty, high-intent keywords first
5. Map: assign one primary keyword per page (no cannibalization)
```

### Content Calendar
```
Frequency: 2-4 posts per month (consistency > volume)
Mix:
  40% — Educational (how-to, guides, explainers)
  30% — Thought leadership (opinions, trends, predictions)
  20% — Case studies (real projects, real results)
  10% — News/updates (product launches, company milestones)
```

## Step 6: Blog Post SEO Checklist

Before publishing every post:
- [ ] Primary keyword in title, H1, first 100 words, URL slug
- [ ] Title under 60 chars, compelling (not keyword-stuffed)
- [ ] Meta description under 155 chars with primary keyword
- [ ] URL slug: short, keyword-rich, hyphen-separated
- [ ] 3+ internal links to other site pages
- [ ] 1-2 external links to authoritative sources
- [ ] Images with descriptive alt text
- [ ] Minimum 800 words (1500+ for pillar content)
- [ ] Subheadings (H2, H3) break up content logically
- [ ] Conclusion with CTA (contact, related post, newsletter)
- [ ] Open Graph image set (1200x630px)

## Step 7: Local SEO (for agency/consulting)

- [ ] Google Business Profile claimed and complete
- [ ] NAP (Name, Address, Phone) consistent across all listings
- [ ] LocalBusiness JSON-LD on website
- [ ] Reviews strategy (ask satisfied clients)
- [ ] Location pages if serving multiple cities
