# SEO Audit Findings — The Videshi
**Date:** 2026-06-07
**Audited by:** Hatch (automated pipeline audit)

## Executive Summary

Google Search Console shows only **33 indexed pages out of 5,831+ published articles**. The root cause is that The Videshi is a Vite SPA with bot-specific prerendering only for article pages — all other page types serve empty HTML shells to crawlers.

## Current SEO Infrastructure

### ✅ What's Working

1. **robots.txt** — Clean configuration. Allows all crawlers except `/admin` and `/api/`. Includes sitemap reference.

2. **Sitemap** — Dynamic serverless function at `api/sitemap.xml.ts` fetches all articles from Supabase. Properly paginated with `<sitemapindex>` for large catalogs.

3. **Article prerendering** — `vercel.json` has a rewrite rule that intercepts known bot user-agents (Googlebot, Bingbot, Twitterbot, etc.) on `/articles/:slug` paths and redirects them to `/api/prerender?slug=:slug`. The prerender API returns full server-side HTML with:
   - Complete `<meta>` OG tags and Twitter cards
   - JSON-LD structured data (`NewsArticle` schema)
   - Full article body in the HTML
   - Proper 404 for missing articles

4. **Client-side SEO** — `react-helmet-async` sets dynamic `<title>`, OG tags, and JSON-LD on article pages for JavaScript-capable crawlers.

### ⚠️ What's Broken

1. **Only `/articles/:slug` pages are prerendered for bots.** All other page types serve the default `index.html` SPA shell — which contains only static, generic meta tags (same title, same description, same OG image for every non-article page).

   **Affected page types with no bot prerendering:**
   - Homepage (`/`)
   - Category pages (`/sports`, `/entertainment`, `/news`, `/technology`, etc.)
   - Events pages (`/events`, `/events/:slug`)
   - Directory pages (`/directory`, `/directory/:slug`)
   - Classifieds pages (`/classifieds`, `/classifieds/:slug`)
   - Cars pages (`/cars`, `/cars/:slug`)
   - Any static pages (`/about`, `/contact`, etc.)

2. **No SSR/SSG framework.** The app is a pure Vite + React SPA. There's no Next.js, Remix, Astro, or similar framework. No `react-snap` or prerender-spa-plugin. The only server-side rendering is the custom prerender API for article pages.

3. **Static `index.html` meta tags are generic.** The fallback `index.html` has hardcoded OG tags that don't reflect the actual page content. When Google crawls `/sports`, it sees the same title and description as `/entertainment`.

## Root Cause Analysis

The **33/5,831 indexing ratio** is explained by:

1. **Article pages** (5,800+) — These SHOULD be indexed since they have bot prerendering. The low number (33) suggests Google may not be discovering them efficiently through the sitemap, or crawl budget is being exhausted on empty SPA pages.

2. **Non-article pages** — These are effectively invisible to crawlers. Google sees an empty `<div id="root"></div>` with generic meta tags. While Googlebot can execute JavaScript, it deprioritizes JS rendering and may time out on SPA hydration.

3. **Possible crawl budget waste** — If Google is spending crawl budget trying to render category pages, events, etc. (and failing/timing out), it may be deprioritizing the entire domain.

## Recommendations

### Priority 1 — Immediate (High Impact)

**Expand bot prerendering to category and key listing pages.**

Add rewrite rules in `vercel.json` for bot user-agents on these paths:
- `/` (homepage)
- `/sports`, `/entertainment`, `/news`, `/technology`, `/immigration`, `/nri-world`, `/travel`, `/food`, `/lifestyle-health`, `/markets-finance`
- `/events`, `/directory`, `/classifieds`, `/cars`

Create corresponding prerender API endpoints that return proper HTML with:
- Category-specific `<title>` and `<meta description>`
- OG tags with category-specific images
- A list of recent article links (for crawl discovery)
- JSON-LD `CollectionPage` or `ItemList` schema

### Priority 2 — Medium Term

**Improve sitemap discovery and submission.**
- Verify the sitemap is submitted in Google Search Console
- Consider adding `<lastmod>` dates to sitemap entries
- Add non-article pages to the sitemap (category pages, events, etc.)
- Consider breaking the sitemap into per-category sitemaps for faster processing

**Add internal linking in prerendered pages.**
- Homepage prerender should link to all category pages
- Category prerender should link to recent articles
- This helps Google discover and crawl article pages even if sitemap processing is slow

### Priority 3 — Long Term

**Consider migrating to an SSR framework.**
- Next.js, Remix, or Astro would provide SSR out of the box
- This eliminates the need for custom bot prerendering entirely
- Every page would be crawlable and indexable by default
- Better Core Web Vitals (LCP, FID) which affect search ranking

**Alternatively, use a prerendering service.**
- Services like Prerender.io or Rendertron can cache server-rendered versions of all pages
- Less migration effort than a full framework switch
- Can be added as a Vercel middleware or edge function

## Technical Details

### Files Examined
- `the-videshi-news/index.html` — SPA entry point with static meta tags
- `the-videshi-news/src/pages/ArticlePage.tsx` — Client-side article rendering with react-helmet-async
- `the-videshi-news/api/prerender.ts` — Bot prerender endpoint for articles
- `the-videshi-news/api/sitemap.xml.ts` — Dynamic sitemap generator
- `the-videshi-news/vercel.json` — Rewrite rules including bot UA detection
- `the-videshi-news/public/robots.txt` — Crawler directives

### Package Dependencies (SEO-related)
- `react-helmet-async` — Client-side meta tag management
- No prerender/SSR packages installed

## Conclusion

The site's SEO architecture is correctly implemented for article pages but completely missing for all other page types. The immediate fix (expanding bot prerendering to category pages) should significantly improve indexing. The 33-page index count likely reflects Google indexing a handful of pages it managed to render via JavaScript, while the sitemap-discovered articles are being deprioritized due to overall domain crawl quality signals.
