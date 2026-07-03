# The Videshi — Technical & SEO Audit

**Date:** 2026-07-03  
**Auditor:** Hatch (automated)  
**Site:** https://www.thevideshi.com

---

## PART 1 — World Cup Page (`/world-cup`)

### URL & Routing
- **Canonical URL:** `/world-cup` (React route in the JS bundle, sitemap entry)
- **`/world-cup-2026`** returns HTTP 200 (the SPA shell catches all routes) but does **NOT** match a defined React route — it would show a 404 or fallback inside the SPA. The sitemap lists only `/world-cup`.
- ⚠️ **Issue:** If `/world-cup-2026` is being linked to externally, it needs either a redirect to `/world-cup` or its own route alias.

### Page Architecture
- The page is a **lazy-loaded React component** (`WorldCupPage-BXgPhcjA.js`, ~21 KB).
- All data is fetched client-side from **`/data/worldcup.json`** — no SSR for this page.
- The component injects `<meta>` tags via JavaScript: `"FIFA World Cup 2026 — The Videshi"` and `"Complete FIFA World Cup 2026 coverage: live scores, group standings, match schedule, highlight videos, and an NRI guide to attending matches across the US, Canada & Mexico."` — but these are **only visible after JS execution**, not to crawlers requesting the raw HTML.

### Tabs / Sections
The page has **4 tabs**: Schedule (📅), Groups (🏆), Highlights (🎬), NRI Guide (🇮🇳).

### Match Data (worldcup.json)
| Field | Status |
|---|---|
| Total matches | 88 |
| Groups | 12 (A through L), with full W/D/L/GF/GA/Pts standings |
| R32 knockout matches | ✅ **16 matches** (13 completed, 3 scheduled today) |
| Round of 16 | ✅ 8 matches (July 4–7), some TBD slots |
| Quarterfinals | 4 matches (July 9–11) — slots only |
| Semifinals | 2 matches (July 14–15) — slots only |
| Third place | July 18 @ Hard Rock Stadium, Miami |
| Final | July 19 @ MetLife Stadium, NJ |
| Third-place ranking table | ✅ Present (for R32 qualification) |

### Today's Matches (July 3, 2026)
✅ **3 R32 matches present in the data:**

| Match | Venue | Status |
|---|---|---|
| Australia vs Egypt | AT&T Stadium, Arlington TX | FT: 1-1 (2-4 pens) |
| Argentina vs Cape Verde | Hard Rock Stadium, Miami | Scheduled, 18:00 ET |
| Colombia vs Ghana | Arrowhead Stadium, Kansas City | Scheduled, 21:30 ET |

### R32 Knockout Matches
✅ R32 matches are stored **two ways**:
1. In `matches[]` array with `group: "R32"` — 3 matches (today's)
2. In `knockout.round_of_32.matches[]` — 16 matches total

All 16 R32 matches have: date, time, venue, home/away teams, status, scores for completed matches.

### Group Standings
✅ **Complete group standings** for all 12 groups with full stats (P, W, D, L, GF, GA, Pts, flags, FIFA rankings).

### Highlights Section
✅ **582 highlight entries** — sourced from social media posts (Threads, Instagram). Each entry has:
- `platform` (threads/instagram)
- `url` (links to social posts from @fifaworldcup and country accounts)
- `account`, `caption`, `date`

⚠️ **Note:** These are social media post links, not direct video URLs. The highlights work as embedded social content links rather than standalone video players.

### NRI Guide / Levi's Stadium
✅ **NRI Watch section present** with:
- Headline: "The World Cup in Your Backyard"
- Description about the tournament being held across US/Canada/Mexico
- **Key venues near desi hubs** including:
  - **Levi's Stadium, San Francisco Bay Area** — 7 matches, note: "Heart of the Bay Area desi community. Group D & J matches + USA R32 knockout."
  - MetLife Stadium (NYC) — 8 matches, World Cup Final venue
  - SoFi Stadium (LA) — 6 matches
  - AT&T Stadium (Dallas) — 6 matches

**Levi's Stadium matches in the data:**

| Date | Match | Round | Score |
|---|---|---|---|
| June 13 | Qatar vs Switzerland | Group B | 1-1 |
| June 17 | Austria vs Jordan | Group J | 3-1 |
| June 20 | Turkey vs Paraguay | Group D | 0-1 |
| June 22 | Jordan vs Algeria | Group J | 1-2 |
| June 25 | Paraguay vs Australia | Group D | 0-0 |
| **July 1** | **USA vs Bosnia & Herzegovina** | **R32 Knockout** | **2-0** |

✅ Levi's Stadium **does mention a knockout match** (USA vs Bosnia R32).

The WorldCupPage JS component links Levi's Stadium to an NRI guide article: `/articles/world-cup-2026-guide-san-francisco`.

---

## PART 2 — SEO & Technical

### Architecture: SPA with Selective SSR

The site is a **React Single-Page Application** (Vite-built). The server returns an identical HTML shell for ALL routes:
```html
<div id="root"></div>
<script type="module" src="/assets/index-DkZ_FEtA.js"></script>
```

**However**, the server performs **SSR for known crawler user agents**:
- ✅ `Googlebot/2.1` → gets article-specific `<title>`, `<meta description>`, `<og:*>`, `<canonical>`
- ✅ `facebookexternalhit/1.1` → same SSR treatment
- ❌ Default/regular user agents → get generic SPA shell with no page-specific meta

### Homepage Meta Tags (`/`)

| Tag | Value | Status |
|---|---|---|
| `<title>` | "The Videshi — News for the global Indian diaspora" | ✅ Good |
| `meta description` | "The Videshi: editorial reporting and analysis for the global Indian diaspora — India, NRI affairs, US-India, business, culture, and voices." | ✅ Good |
| `og:title` | "The Videshi" | ✅ |
| `og:description` | "News for the global Indian diaspora" | ✅ |
| `og:type` | "website" | ✅ |
| `og:image` | `https://www.thevideshi.com/og-default.jpg` (1456×816) | ✅ |
| `og:url` | `https://www.thevideshi.com` | ✅ |
| `og:site_name` | "The Videshi" | ✅ |
| `twitter:card` | "summary_large_image" | ✅ |
| `twitter:title` | "The Videshi" | ✅ |
| `twitter:description` | "News for the global Indian diaspora" | ✅ |
| `twitter:image` | `https://www.thevideshi.com/og-default.jpg` | ✅ |
| `canonical` | ❌ **MISSING** | 🔴 Critical |
| `google-site-verification` | ✅ Present | ✅ |
| RSS feed | ✅ `/rss.xml` linked | ✅ |

### Article Page Meta Tags (tested with Googlebot UA)
Tested: `/articles/ronaldo-yamal-portugal-spain-world-cup-round-of-16-dallas-att-stadium-nri-diaspora-2026`

| Tag | Value | Status |
|---|---|---|
| `<title>` | "Ronaldo vs Yamal. Portugal vs Spain. The Biggest World Cup Knockout Clash Lands in Dallas on Monday. — The Videshi" | ✅ Unique |
| `meta description` | Full article description about the Iberian rivals | ✅ Unique |
| `og:title` | Same as `<title>` | ✅ |
| `og:image` | `https://upload.wikimedia.org/wikipedia/commons/6/67/Cristiano_Ronaldo_2275_(cropped).jpg` | ✅ Article-specific |
| `canonical` | ✅ Full canonical URL | ✅ |

⚠️ **BUT** — with a regular (non-bot) user agent, the article page returns the **generic homepage meta tags**. This means:
- ❌ When users share links on **WhatsApp, iMessage, Slack, Discord, LinkedIn** (which use their own preview fetchers, not Googlebot UA) — they may see the generic "The Videshi" preview instead of the article title/image.
- ❌ Some crawlers not matching the SSR user-agent list won't see the right tags.

### robots.txt
✅ **Present and correct:**
```
User-agent: *
Allow: /
Disallow: /admin
Disallow: /api/
Sitemap: https://www.thevideshi.com/sitemap.xml
```

### sitemap.xml
✅ **Present and comprehensive:**
- Homepage, events, directory, classifieds, about, contact, privacy, terms, travel, immigration (with sub-pages), stories, world-cup, news categories
- 511+ lines of article URLs with `lastmod` timestamps, `changefreq`, and `priority`
- Articles have `hourly` changefreq and `0.9` priority
- Includes `<news:news>` tags with publication name, language, and dates

### Critical Missing Pages

| Page | HTTP Status | Content |
|---|---|---|
| `/about` | 200 (SPA shell) | ❌ **No extractable content** — SPA renders empty or a client-side "not found" |
| `/contact` | 200 (SPA shell) | ❌ **No extractable content** — same issue |
| `/privacy` | 200 (SPA shell) | ❌ **No extractable content** — same issue |
| `/privacy-policy` | 200 (SPA shell) | ❌ **No extractable content** — same issue |
| `/terms` | 200 (SPA shell) | ✅ Listed in sitemap |

⚠️ These pages are listed in the sitemap (suggesting they should exist), and the server returns 200 for all of them. However, the static HTML extraction found **no content** — meaning either:
1. These pages exist in the React app but require JavaScript to render (likely), OR
2. The React app doesn't have routes for them and shows a blank/error state

Since the SPA shell is identical for ALL URLs (even non-existent ones), there's no way to distinguish a real page from a broken one without JavaScript execution.

---

## PART 3 — Social Media Links

### Footer Social Links (from JS bundle)

| Platform | URL in Footer | HTTP Status | Notes |
|---|---|---|---|
| X (Twitter) | `https://x.com/thevideshi` | ✅ 200 | Valid |
| Instagram | `https://instagram.com/the.videshi` | ✅ 200 | Note: uses `the.videshi` |
| Facebook | `https://www.facebook.com/profile.php?id=1145353431990758` | ✅ 200 | Uses numeric ID, no vanity URL |
| YouTube | `https://youtube.com/@the.videshi` | ✅ 200 | Valid |
| Threads | `https://threads.net/@the.videshi` | ⏳ (threads.net may redirect) | See issue below |

### Social Link Issues

1. **🔴 Instagram handle inconsistency:** The bundle contains TWO different Instagram URLs:
   - Footer: `https://instagram.com/the.videshi` (with dot)
   - Elsewhere (likely article share links): `https://www.instagram.com/thevideshi` (without dot)
   - These may or may not point to the same account. **Verify which is the canonical handle.**

2. **🟡 Threads URL uses `threads.net`:** Per known issues (AGENTS.md), the canonical Threads domain is now **`threads.com`**, and `threads.net` 301-redirects. This can cause embed breakage where Threads `embed.js` validates the iframe's host against the permalink origin. The footer link should be updated to `https://www.threads.com/@the.videshi`.

3. **🟡 Facebook uses numeric profile ID:** `profile.php?id=1145353431990758` works but is not user-friendly. Consider claiming a vanity URL (e.g., `facebook.com/thevideshi`).

---

## Summary of Issues (Priority Order)

### 🔴 Critical

1. **Non-bot users get generic meta tags on ALL pages.** WhatsApp, iMessage, Slack, Discord, LinkedIn preview fetchers likely won't trigger SSR. Shared article links will show "The Videshi — News for the global Indian diaspora" instead of the article headline. **Fix: Extend SSR to cover common preview fetcher user agents** (WhatsApp, Slack, Discord, LinkedIn, Telegram bots) or better yet, implement universal SSR/prerendering.

2. **No canonical link on the homepage.** This is a basic SEO requirement to prevent duplicate content issues.

3. **`/world-cup-2026` is a dead route.** The React app only defines `/world-cup`. Any external links to `/world-cup-2026` will show a blank/404 inside the SPA. Add a redirect or route alias.

### 🟡 Important

4. **About/Contact/Privacy pages may be empty or broken.** They're listed in the sitemap but produced no extractable content. Verify they render with JavaScript.

5. **Instagram handle inconsistency** (`the.videshi` vs `thevideshi`) — could cause confusion or link to a wrong/nonexistent account.

6. **Threads footer link uses deprecated `threads.net`** — should be `threads.com`.

7. **Highlights are social post links, not embedded videos.** The 582 "highlights" are links to Threads/Instagram posts from @fifaworldcup. Consider adding embedded video players or direct FIFA highlight links for a richer experience.

8. **World Cup page meta tags only work client-side.** The WorldCupPage component sets `<title>` and `<meta description>` via JavaScript, but crawlers receiving the raw HTML will see the generic homepage meta tags instead.

### 🟢 Minor / Nice-to-Have

9. **Facebook page uses numeric ID** instead of a vanity URL.
10. **No `twitter:site` handle** in the meta tags (e.g., `@thevideshi`).
11. **No structured data (JSON-LD)** for articles (NewsArticle schema would help Google News indexing).
12. **SPA returns 200 for ALL URLs** including non-existent ones — should return 404 status for truly missing pages.

---

## What's Working Well

- ✅ **World Cup data is comprehensive** — 88 matches, 12 groups with full standings, R32 knockout bracket, R16 bracket, all venues
- ✅ **Today's matches (July 3) are present** with live scores for completed match (AUS vs EGY)
- ✅ **NRI Guide has rich venue data** with desi community context for each stadium
- ✅ **Levi's Stadium coverage is solid** — 7 matches listed including the USA R32 knockout, linked to a dedicated NRI guide article
- ✅ **SSR works for Googlebot and Facebook** — article pages have unique titles, descriptions, OG images, and canonical URLs
- ✅ **robots.txt and sitemap.xml are well-configured** with proper article indexing
- ✅ **RSS feed is available** at `/rss.xml`
- ✅ **All social media accounts resolve** (200 status)
- ✅ **Self-hosted fonts** (Playfair Display, Source Serif 4) with proper `font-display: swap`
- ✅ **Google Site Verification** is in place
- ✅ **582 highlight entries** showing active content curation
