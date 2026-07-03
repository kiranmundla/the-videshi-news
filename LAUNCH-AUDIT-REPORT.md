# The Videshi — Launch Readiness Audit

**Date:** July 3, 2026  
**Verdict: READY WITH CAVEATS**

The site is functional, content-rich (6,481 articles, 177 events, 3,939 directory listings), and publishing ~129 articles/day via automated pipeline. The core reading experience works well. However, there are several issues that should be fixed before or shortly after a public launch announcement.

---

## 🔴 Launch Blockers (must fix before announcement)

### 1. RSS Feed Is Empty (0 items)
- **Where:** https://www.thevideshi.com/rss.xml
- **What:** The RSS channel metadata renders but zero `<item>` entries appear. The feed is useless for syndication, podcast apps, or anyone subscribing.
- **Root cause:** `api/rss.xml.ts` reads the Supabase anon key from `VITE_SUPABASE_PUBLISHABLE_KEY`, but Vercel has it set as `VITE_SUPABASE_ANON_KEY` (which is what the working prerender uses). The key resolves to empty string → Supabase returns `[]` → no items.
- **Fix:** Change line 7 in `api/rss.xml.ts` from `process.env.VITE_SUPABASE_PUBLISHABLE_KEY` to `process.env.VITE_SUPABASE_ANON_KEY`. One-line fix.

### 2. Directory Images — 78.5% Broken
- **Where:** `/directory` page, all listing cards
- **What:** 3,094 of 3,939 listings (78.5%) still use expired Google Places `photo_reference` tokens that return HTTP 400. Only 383 have been migrated to Supabase storage. ~462 have no image at all.
- **Impact:** The Directory page is a core feature and looks broken with most images failing to load.
- **Fix:** Run `pipeline/refresh-directory-photos.py` at scale. The weekly cron (`videshi-directory-photos`) only processes a batch — need a one-time bulk run to clear the backlog before launch.

### 3. 158 Published Articles Missing Hero Images
- **Where:** 2.4% of all published articles
- **What:** These articles render with no hero image, which looks unprofessional on article cards and article pages.
- **Fix:** Query `SELECT slug, headline FROM p2_articles WHERE status='published' AND (image_url IS NULL OR image_url='') ORDER BY published_at DESC` and either source images or hide these from prominent feeds.

---

## 🟡 Important Issues (fix within first week of launch)

### 4. Threads Links Use Deprecated `threads.net`
- **Where:** Footer (`SiteFooter.tsx` line 56) and Masthead social icons
- **What:** Both use `threads.net/@the.videshi` instead of `threads.com/@the.videshi`. Per AGENTS.md, `threads.net` → `.com` redirect breaks embed iframe postMessage validation.
- **Fix:** Find-replace `threads.net` → `threads.com` in `SiteFooter.tsx` and `Masthead.tsx`.

### 5. 25 Articles Have Double-Encoded Sources JSON
- **Where:** 0.4% of published articles
- **What:** Sources column contains escaped backslashes/quotes (JSON-in-JSON). The frontend `parseSources()` handles this gracefully but it's data debt.
- **Fix:** Run a SQL UPDATE to properly decode these rows. The double-encoding migration was done previously but these 25 were apparently missed.

### 6. No Canonical Link on Homepage
- **Where:** Homepage HTML `<head>`
- **What:** Article pages have canonical links (via prerender), but the homepage does not. This can cause duplicate-content issues with `thevideshi.com` vs `www.thevideshi.com`.
- **Fix:** Add `<link rel="canonical" href="https://www.thevideshi.com/" />` to `index.html`.

### 7. 404 Pages Return HTTP 200
- **Where:** Any non-existent URL (e.g. `/nonexistent-page`)
- **What:** Standard SPA behavior — Vercel serves `index.html` for all paths. The React router shows a "not found" component, but the HTTP status is 200. Search engines will index garbage URLs.
- **Fix:** Add a catch-all rewrite in `vercel.json` that serves a proper 404 for non-matching paths, or configure the prerender function to return 404 for bot requests to unknown routes (it already returns "Page Not Found" for Googlebot — just needs the HTTP status code set to 404).

### 8. 18 Articles Missing Subheadlines
- **Where:** 0.3% of published articles
- **What:** Minor, but articles without subheadlines look incomplete on cards and in social previews (og:description falls back to generic text).
- **Fix:** Batch-generate subheadlines via GPT for these 18 articles.

---

## 🟢 Nice to Have (polish items)

### 9. About / Contact / Privacy Pages
- **Where:** Routes exist (`/about`, `/contact`, `/privacy`) and are in the sitemap
- **What:** These pages exist in the router but need to be verified they have proper content — they're JS-rendered so couldn't be audited via static fetch.
- **Action:** Manually verify these pages have real content before launch. A news site needs a visible About page.

### 10. Instagram Handle Consistency
- **Where:** Various places in the codebase
- **What:** Some references use `the.videshi` (with dot, correct Instagram handle) while others use `thevideshi` (no dot). Ensure consistency.

### 11. Search Functionality — Needs Manual Verification
- **Where:** `/search?q=...`
- **What:** Search is entirely JS-rendered. The Supabase query works correctly (verified via API — returns results for "modi"). However, the live site search page couldn't be verified without JS execution in this audit. An earlier browser check returned 0 results for "modi" — this needs hands-on verification.
- **Action:** Open the site in a real browser, test search for "modi", "trump", "H-1B", "cricket". If 0 results, debug the client-side Supabase query.

### 12. World Cup Page Route
- **Where:** Navigation links
- **What:** The correct route is `/world-cup` but some external references may use `/world-cup-2026`. Consider adding a redirect or alias.

### 13. Voices → Stories Route Naming
- **Where:** Nav bar shows "Voices" but links to `/stories`
- **What:** Not a bug per se (the label is intentional), but could confuse direct URL visitors expecting `/voices`. Consider adding a redirect from `/voices` to `/stories`.

---

## ✅ What's Working Well

### Content Pipeline
- **6,481 published articles** with strong ~129/day cadence
- **5 most recent articles** all from today (Jul 3, 2026) — pipeline is healthy
- **902 articles in last 7 days** — no staleness concern
- **Zero articles** with null `published_at` or very short body (<200 chars)

### Homepage
- **103 articles** across 8 sections + 5 carousel items + 1 featured article
- Hero images loading correctly (101/103 on homepage)
- Image sources diverse: Wikimedia (74), Supabase (23), Pexels (4)

### Market Ticker
- Live data for Sensex, Nifty, S&P 500, Nasdaq
- Refreshing properly

### World Cup Page
- **88 matches** (72 group + 16 R32 knockout) with proper scores
- All 12 group standings calculated
- **582 highlight entries** (social post links)
- NRI Guide with venue details, Levi's Stadium correctly shows 7 matches including USA knockout
- Today's 3 matches (Jul 3) present and correct

### Social Previews (SSR)
- ✅ Article pages return unique og:title, og:description, og:image for ALL major bots
- ✅ Verified working for: Googlebot, WhatsApp, Twitterbot, LinkedInBot, Discordbot, TelegramBot, Applebot, facebookexternalhit
- ✅ Canonical links on article pages

### SEO
- **Sitemap:** 11,268 URLs, 6,481 article URLs — comprehensive
- **robots.txt:** properly configured
- **Article meta tags:** unique per article (title, description, og:image, canonical)

### Events
- **177 future events** through April 2027
- Good date coverage

### Infrastructure
- All static assets loading (favicon, OG default image, fonts, CSS, JS bundle)
- All 5 social media account links resolve to HTTP 200 (X, Instagram, Facebook, YouTube, Threads)

---

## Priority Action Plan

| # | Issue | Effort | Impact |
|---|-------|--------|--------|
| 1 | Fix RSS env var (one line) | 5 min | High — enables syndication |
| 4 | Fix Threads links `.net` → `.com` | 5 min | Medium — fixes embed breaks |
| 6 | Add homepage canonical | 5 min | Medium — SEO hygiene |
| 3 | Source missing hero images (158) | 2-3 hrs | High — visual quality |
| 2 | Bulk run directory photo refresh | 1-2 hrs | High — Directory page usability |
| 5 | Fix 25 double-encoded sources | 30 min | Low — cosmetic |
| 7 | 404 status code fix | 1 hr | Medium — SEO |
| 11 | Verify search works in browser | 15 min | High — core feature |
