# TheVideshi.com Navigation & Content Audit

**Date:** 2026-07-03 14:26 PDT  
**Method:** `browser_open` for rendered content + `curl` for HTTP status/raw HTML + JS bundle route extraction  

---

## Architecture Overview

The site is a **pure client-side React SPA** (Vite-built). Every route — homepage, articles, search, 404 — returns the **same 6,563-byte HTML shell** (`HTTP 200`, `<div id="root"></div>`) regardless of the URL. All content is rendered in the browser via JavaScript. Data is loaded from:

- Static JSON files (`/data/homepage-feed.json`, `/data/market-indices.json`, etc.)
- Supabase backend (`lboecaekpynbpyijrbfz.supabase.co`)

**No SSR/SSG is in place.** This has significant SEO and crawlability implications (see Issues below).

---

## 1. Homepage (`/`)

| Check | Result |
|-------|--------|
| **Loads** | ✅ HTTP 200; `browser_open` extracted article text |
| **Articles visible** | ✅ ~20 headlines visible in extracted text |
| **Masthead (logo + search)** | ⚠️ Not in server HTML — rendered by JS; can't verify without execution |
| **Nav rows** | ⚠️ Same — JS-rendered, not in static HTML |

### Homepage Feed Breakdown (from `/data/homepage-feed.json`)

- **Generated at:** 2026-07-03T21:20:30 UTC (fresh)
- **Featured article:** 1 (SCOTUS birthright citizenship ruling)
- **Carousel:** 5 items (all with hero images)
- **Editorial:** None (null)
- **Sections:** 8 categories, 102 articles total

| Section | Article Count |
|---------|:------------:|
| news | 18 |
| nri-world | 12 |
| markets-finance | 12 |
| sports | 12 |
| technology | 12 |
| entertainment | 12 |
| lifestyle-health | 12 |
| food | 12 |

**Total article cards on homepage: 103** (1 featured + 5 carousel + 102 section cards; carousel items may overlap with sections)

### Market Ticker

✅ **Data exists** at `/data/market-indices.json` (fresh as of 2026-07-03T20:55 UTC):
- Sensex: 77,763.91 (+0.34%)
- Nifty 50: 24,270.85 (+0.43%)
- S&P 500: 7,483.24 (+0.00%)
- Nasdaq: data present

The ticker is JS-rendered, so whether it *displays* requires JS execution, but the data is live and available.

### Pulse Sections

❌ **Not present.** The homepage feed JSON has no `india_pulse`, `tech_pulse`, `sports_pulse`, or `world_pulse` keys. Top-level keys are: `generated_at`, `featured`, `editorial`, `sections`, `carousel`.

### Events Section on Homepage

❌ **Not present** in the homepage feed data. The "Explore" block at the bottom of the extracted text shows text links to Events, Directory, Classifieds, and Cars, but no event data is embedded in the feed.

### Footer Links

⚠️ Not visible in server-rendered HTML. The extracted homepage text shows an "Explore" block with: Events, Directory, Classifieds, Cars. Full footer is JS-rendered.

### Meta Tags

✅ **Present and correct** (static in the HTML `<head>`):

| Tag | Value |
|-----|-------|
| `<title>` | The Videshi — News for the global Indian diaspora |
| `meta description` | The Videshi: editorial reporting and analysis for the global Indian diaspora… |
| `og:title` | The Videshi |
| `og:description` | News for the global Indian diaspora |
| `og:image` | `https://www.thevideshi.com/og-default.jpg` (✅ loads, 243 KB) |
| `og:type` | website |
| `twitter:card` | summary_large_image |
| RSS link | `/rss.xml` |

**⚠️ CRITICAL:** These meta tags are **identical for every route** — article pages, category pages, search, etc. all serve the same `<head>`. Social sharing previews for any specific article will show the generic site title/image, not the article's own headline/hero.

---

## 2. Events (`/events`)

| Check | Result |
|-------|--------|
| HTTP status | 200 (same SPA shell) |
| Content via `browser_open` | ❌ "The requested URL was not found" (no extractable content) |
| In sitemap | ✅ Listed |
| JS route exists | ✅ `path:"/events"` with chunk `EventsPage-99P0qXYZ.js` |

**Verdict:** Route exists in the SPA, but content is entirely JS-rendered. Cannot verify if events load without JS execution.

---

## 3. Voices (`/voices`)

| Check | Result |
|-------|--------|
| HTTP status | 200 (same SPA shell) |
| Content via `browser_open` | ❌ No extractable content |
| JS route exists | ❌ **No `/voices` route** |
| Actual route | `/stories` (chunk: `StoriesPage-Crwaxdcg.js`) |
| In sitemap | ✅ `/stories` is listed; `/voices` is **not** |

**Verdict:** **URL mismatch.** The correct route is `/stories`, not `/voices`. The SPA has no `/voices` path — it would render whatever catch-all/404 the React router shows.

---

## 4. Directory (`/directory`)

| Check | Result |
|-------|--------|
| HTTP status | 200 (same SPA shell) |
| Content via `browser_open` | ❌ No extractable content |
| In sitemap | ✅ Listed |
| JS route exists | ✅ `path:"/directory"` with chunks for listing, detail, and submit pages |

**Verdict:** Route exists. Content is JS-rendered; can't verify data without JS execution.

---

## 5. Classifieds (`/classifieds`)

| Check | Result |
|-------|--------|
| HTTP status | 200 (same SPA shell) |
| Content via `browser_open` | ❌ No extractable content |
| In sitemap | ✅ Listed |
| JS route exists | ✅ `path:"/classifieds"` with full CRUD routes |

**Verdict:** Route exists. Content is JS-rendered.

---

## 6. World Cup 2026 (`/world-cup-2026`)

| Check | Result |
|-------|--------|
| HTTP status | 200 (same SPA shell) |
| Content via `browser_open` | ❌ No extractable content |
| JS route exists | ❌ **No `/world-cup-2026` route** |
| Actual route | `/world-cup` (data at `/data/worldcup.json`, 213 KB) |
| In sitemap | ✅ `/world-cup` is listed; `/world-cup-2026` is **not** |

**Verdict:** **URL mismatch.** The correct route is `/world-cup`, not `/world-cup-2026`. World Cup data file is large and fresh (213 KB JSON).

---

## 7. Search: `modi` (`/search?q=modi`)

| Check | Result |
|-------|--------|
| HTTP status | 200 (same SPA shell) |
| Content via `browser_open` | ❌ "No extractable content" |
| JS route exists | ✅ `path:"/search"` |

**⚠️ CANNOT DETERMINE RESULT COUNT.** Search is entirely client-side (JS queries Supabase). Without JS execution, we cannot verify whether 0 or N results appear. The `browser_open` tool extracts no rendered content from this page.

**This is an architectural limitation** — search results depend entirely on client-side JS + API calls. A bot or non-JS client would see nothing.

---

## 8. Search: `H-1B` (`/search?q=H-1B`)

Same as above. HTTP 200, no extractable content. Cannot verify result count without JS execution.

---

## 9. 404 Test (`/nonexistent-page-test-404`)

| Check | Result |
|-------|--------|
| HTTP status | **200** ❌ (should be 404) |
| Content | Same 6,563-byte SPA shell |
| Behavior | The React Router likely shows a client-side "not found" screen, but the HTTP status is 200 |

**🐛 BUG:** Non-existent pages return HTTP 200. This is bad for:
- Search engine crawling (Google will index garbage URLs)
- Monitoring tools (can't detect broken links)
- CDN/proxy caching (can't cache 404 responses differently)

---

## 10. Article Pages (2 tested)

### Article 1: SCOTUS Birthright Citizenship
- **URL:** `/articles/scotus-birthright-citizenship-indian-h1b-families-20260703`
- **HTTP status:** 200 (same SPA shell)
- **`browser_open`:** ❌ No extractable content
- **Hero image:** `https://upload.wikimedia.org/...Exterior_of_Supreme_Court_Building_20240601.jpg` → ✅ loads (243 KB)

### Article 2: India–Iran Diplomacy
- **URL:** `/articles/india-khamenei-funeral-delegation-iran-diplomacy-balancing-act-20260703`
- **HTTP status:** 200 (same SPA shell)
- **`browser_open`:** ❌ No extractable content
- **Hero image:** Wikimedia Commons (Khamenei portrait) → ✅ loads (1.04 MB)

**Verdict:** Article pages serve the same empty HTML shell. The JS fetches article data from Supabase at runtime. No server-rendered body content or article-specific meta tags.

---

## Image Health

| Metric | Count |
|--------|:-----:|
| Total articles in homepage feed | 103 |
| Articles with hero image URL | 101 |
| Articles with **empty** hero image URL | **2** |
| Image sources — Wikimedia Commons | 74 |
| Image sources — Supabase storage | 23 |
| Image sources — Pexels | 4 |

### Articles Missing Hero Images

1. **"India Just Logged Its Driest June in Fifteen Years…"** (`india-driest-june-monsoon-crisis-el-nino-kharif-sowing-food-inflation-20260703`) — Section: news
2. **"Alpha Opens to a Whimper, Not a Bang…"** (`alpha-opening-day-box-office-mixed-reviews-spy-universe-lowest-20260703`) — Section: entertainment

Both have `image_caption` and `image_credit` set, suggesting the image sourcing failed or the URL was cleared.

### Sampled Image URLs
All 4 sampled hero image URLs (Wikimedia) returned HTTP 200 with valid image data.

---

## Static Assets

| Asset | Status | Size |
|-------|--------|------|
| `/og-default.jpg` | ✅ 200 | 243 KB |
| `/favicon-32.png` | ✅ 200 | 736 B |
| `/apple-touch-icon.png` | ✅ 200 | 9.3 KB |
| `/assets/index-DkZ_FEtA.js` | ✅ 200 | Main JS bundle |
| `/assets/index-9zBQVPeL.css` | ✅ 200 | 130 KB |
| Playfair Display `.woff2` | ✅ 200 | 38 KB |
| `/robots.txt` | ✅ 200 | 105 B |
| `/sitemap.xml` | ✅ 200 | 2.67 MB |

---

## RSS Feed (`/rss.xml`)

❌ **EMPTY.** The feed has channel metadata (title, link, description, lastBuildDate) but **zero `<item>` entries**. The `lastBuildDate` is current (2026-07-03T21:28:01 GMT), so the feed is being regenerated but with no articles.

This means RSS readers and any feed aggregators see The Videshi as having no content.

---

## Sitemap (`/sitemap.xml`)

✅ **Comprehensive and large:**
- Total URLs: **11,268**
- Article URLs: **6,481**
- Includes all major non-article pages (events, directory, classifieds, about, contact, privacy, terms, travel, immigration sub-pages, stories, world-cup, category pages)

---

## Route Map (from JS Bundle)

The JS bundle defines these client-side routes:

### Category pages
`/news`, `/immigration`, `/technology`, `/sports`, `/markets-finance`, `/nri-world`, `/entertainment`, `/lifestyle-health`, `/travel`, `/food`, `/cars`

### Content pages
`/articles/:slug`, `/watch/:slug`

### Feature pages
`/events`, `/events/submit`, `/events/:slug`, `/events/:slug/edit`  
`/directory`, `/directory/submit`, `/directory/:slug`  
`/classifieds`, `/classifieds/submit`, `/classifieds/:slug`, `/classifieds/:slug/edit`  
`/stories` (Voices), `/stories/submit`, `/stories/:slug`  
`/cars`, `/cars/:slug`, `/cars/compare`, `/cars/deals`, `/cars/guide/*`  
`/world-cup`  
`/travel`, `/travel/visa-list/:status/:category`, `/travel/:destination`

### Immigration hub
`/immigration`, `/immigration/green-card`, `/immigration/h1b`, `/immigration/consulate-wait-times`, `/immigration/processing-times`, `/immigration/visas`, `/immigration/guides`, `/immigration/guides/:slug`

### Utility
`/search`, `/about`, `/contact`, `/privacy`, `/terms`, `/links`

### Admin (behind auth)
`/admin`, `/admin/articles`, `/admin/cars`, `/admin/classifieds`, `/admin/directory`, `/admin/events`, `/admin/stories`, `/admin/sources`, `/admin/featured`, `/admin/p2`

### Data files
`/data/homepage-feed.json`, `/data/market-indices.json`, `/data/market-charts.json`, `/data/now-in-theaters.json`, `/data/streaming-picks.json`, `/data/tech-buzz.json`, `/data/snapshots-pool.json`, `/data/worldcup.json`

---

## Summary of Issues

### 🔴 Critical

1. **No SSR/SSG** — Every page serves an empty `<div id="root"></div>`. Search engines that don't execute JS (most non-Google crawlers, social media link preview bots, many aggregators) see no content. This means:
   - No per-article meta tags for social sharing (all pages share the same generic og:title/og:image)
   - No crawlable article body text
   - Twitter/Facebook/LinkedIn link previews show "The Videshi — News for the global Indian diaspora" for every article, never the article's own headline or hero

2. **RSS feed is empty** — Zero `<item>` entries. Any RSS reader subscription shows nothing.

3. **404 returns HTTP 200** — Non-existent URLs return 200 with the SPA shell. Search engines will index junk URLs.

### 🟡 Moderate

4. **2 articles missing hero images** — Both published today (monsoon story, Alpha box office) have empty `hero_image_url` despite having caption/credit populated.

5. **URL mismatches in original nav spec:**
   - `/voices` → actual route is `/stories`
   - `/world-cup-2026` → actual route is `/world-cup`

6. **Search cannot be audited** — Search results are entirely client-side. Cannot determine whether `/search?q=modi` returns 0 or N results without JS execution.

### 🟢 Working Well

7. Homepage feed is fresh and comprehensive (103 articles, 8 sections, live market data)
8. All static assets load (favicon, OG image, fonts, CSS, JS bundle)
9. Sitemap is comprehensive (11,268 URLs, 6,481 articles)
10. robots.txt properly blocks `/admin` and `/api/`
11. 101 of 103 articles have hero images; sampled images all load
12. All SPA routes exist in the JS bundle
13. Multiple data JSON endpoints are live and returning fresh data
14. Google Site Verification tag is present

---

*Audit performed with `browser_open` (no JS execution) and `curl` for HTTP-level checks.*
