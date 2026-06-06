# The Videshi News — Deep Platform Audit
**Date:** 2026-06-06  
**Scope:** Strategy, Writer Crons, Pipeline, Frontend, Content, Social Embeds, Infrastructure

---

## Executive Summary

The Videshi is a well-architected Indian diaspora news platform producing **164 articles/day** across 10 categories (9 writer crons + lifestyle covering both lifestyle-health and markets-finance). Total published: **1,280 articles**. The pipeline runs 39 enabled crons covering content generation, enrichment, social media posting, health checks, and data refresh.

**Critical Issues Found: 3**  
**Important Issues Found: 8**  
**Nice-to-have Improvements: 7**

---

## 1. Writer Crons Audit

### Overview
| Category | Interval | Lines | Article Quality Section | Image Sourcing — MANDATORY | Dedup Check | Banned Rules | Social Embeds |
|----------|----------|-------|------------------------|---------------------------|-------------|--------------|---------------|
| entertainment | 2h | 194 | ❌ | ❌ (has own "Step 3") | ✅ | ✅ | ✅ (Step 4: IG) |
| news | 2h | 118 | ✅ | ✅ | ✅ | ✅ | ✅ |
| sports | 3h | 119 | ✅ | ✅ | ✅ | ✅ | ✅ |
| tech | 3h | 274 | ✅ | ✅ | ✅ | ✅ | ✅ |
| lifestyle | 4h | 118 | ✅ | ✅ | ✅ | ✅ | ✅ |
| immigration | 4h | 226 | ✅ | ✅ | ✅ | ✅ | ✅ |
| nri-world | 6h | 215 | ✅ | ✅ | ✅ | ✅ | ✅ |
| food | 12h | 100 | ❌ | ✅ (basic) | ✅ | ❌ | ✅ |
| travel | 4h | 219 | ✅ | ✅ | ✅ | ✅ | ✅ |

### Issues Found

#### 🔴 CRITICAL: Food writer used wrong DB column name
- **File:** `videshi-writer-food__interval@12h.md` line 53
- **Bug:** Referenced `content` column instead of `body`
- **Impact:** Articles may have been inserted with `content` field which Supabase ignores → body would be empty on the site
- **Status:** ✅ FIXED — changed to `body`

#### 🟡 IMPORTANT: Entertainment writer missing standardized sections
- Missing "Article Quality — STRICT" section (present in 7 of 9 writers)
- Missing "Image Sourcing — MANDATORY" section (has its own "Step 3" with `source-image.py`)
- Has unique "Step 4: Instagram Embeds" while others use unified "Social Embeds — Instagram & X"
- **Impact:** Inconsistent quality enforcement; entertainment's embed section only covers Instagram, not X
- **Recommendation:** Add Article Quality section; update social embed section to unified format covering both IG & X

#### 🟡 IMPORTANT: Food writer missing Banned Image Rules
- No BANNED sources section (other writers explicitly ban Facebook CDN, generic stock, tiny thumbnails)
- Missing "Article Quality — STRICT" section
- Image sourcing lists Pexels FIRST (should try Wikipedia/Commons first)
- **Recommendation:** Add banned rules and article quality section matching other writers

#### 🟢 NICE-TO-HAVE: Interval tuning
- Food at 12h produces only 18 articles/week (2 per day) — could increase to 8h for 3/day
- NRI-world at 6h produces 36/week — adequate but could be 4h given diaspora focus
- All intervals are reasonable for their category's news cycle

---

## 2. Social Embed Registry Audit

### Registry File: `pipeline/social-embed-registry.json`

| Category | Handles | Instagram | X/Twitter |
|----------|---------|-----------|-----------|
| entertainment | 35 | ✅ All have IG | 26 have X |
| sports | 21 | ⚠️ 17 missing IG | 18 have X |
| news | 8 | ⚠️ All 8 missing IG | ✅ All have X |
| technology | 10 | ⚠️ All 10 missing IG | 6 have X |
| markets-finance | 2 | ⚠️ Both missing IG | 1 has X |
| nri-world | 4 | ⚠️ All 4 missing IG | 3 have X |
| immigration | 0 | — | — |
| travel | 0 | — | — |

### 🔴 CRITICAL: Corrupted Handles — "abor/nsky" Artifacts
**8 handles had corruption** (random characters like "abor" or "nsky" inserted into the handle text):

| Person | Field | Corrupted | Correct |
|--------|-------|-----------|---------|
| Vicky Kaushal | X | vabornskyzhal09 | vickykaushal09 |
| Kamal Haasan | IG | ikaabornskyhaasan | ikamalhaasan |
| Kamal Haasan | X | ikaabornskyhaasan | ikamalhaasan |
| Allu Arjun | X | alabornskyrjun | alluarjun |
| AR Rahman | IG | araboriginals | arrahman |
| AR Rahman | X | arabornskyrahman | arrahman |

**Status:** ✅ ALL FIXED in `social-embed-registry.json`

### 🔴 CRITICAL: Same corrupted handles in `celebrity-buzz-refresh` cron
8 Instagram handles in the celebrity buzz refresh cron had identical corruption:
- @aaborishwaryaraibachchan_arb → @aishwaryaraibachchan_arb
- @samaborantharuthprabhuoffl → @samantharuthprabhuoffl
- @alaborluarjunonline → @alluarjunonline
- @jaborrntr → @jrntr
- @hraborithikroshan → @hrithikroshan
- @vaaborundhawan → @varundhawan
- @araborrahman → @arrahman
- @acabortorvijay → @actorvijay

**Status:** ✅ ALL FIXED in `celebrity-buzz-refresh__interval@6h.md`

### 🟡 IMPORTANT: Empty categories
- **Immigration**: 0 handles — immigration articles won't get social embeds
- **Travel**: 0 handles — travel articles won't get social embeds
- **Recommendation:** Add airline handles (AirIndia, IndiGo), tourism boards, immigration lawyers/influencers

### 🟡 IMPORTANT: Most categories lack Instagram handles
Sports, news, tech, markets, nri-world all have X handles but no Instagram handles. Since the social embed instructions prioritize Instagram, these categories will never get IG embeds.
- **Recommendation:** Add IG handles for top entities in each category (BCCI, Narendra Modi, Sundar Pichai, etc.)

---

## 3. Article Quality Analysis

### Content Stats (500 most recent articles)
| Category | Articles (500) | Avg Words | Min Words | Pexels Images |
|----------|---------------|-----------|-----------|---------------|
| entertainment | 88 | 697 | 512 | 0 |
| news | 97 | 731 | 400 | 30 |
| sports | 58 | 725 | 542 | 13 |
| technology | 63 | 720 | 552 | 36 |
| immigration | 37 | 828 | 594 | 23 |
| lifestyle-health | 33 | 751 | 618 | 23 |
| travel | 52 | 709 | 493 | 27 |
| food | 18 | 693 | 546 | ** (high) |
| nri-world | 36 | 763 | 568 | 22 |
| markets-finance | 18 | 880 | 751 | 6 |

### Strengths
- **Zero articles under 400 words** — the 600-800 word target is being met consistently
- **All articles have subheadlines** — zero missing
- **All articles have slugs** — zero missing, all human-readable
- **All articles have images** — zero missing
- **Writing quality is high** — openings are engaging, Economist-style, NRI-focused
- **Section formatting is consistent** — all use `## ` headers to break up content
- **No Follow: links remaining** — confirmed all removed from the database

### 🟡 IMPORTANT: Pexels Stock Images (200+ articles, 30.4% of recent 500)
This is the biggest content quality issue. Pexels images are generic stock photos — a stethoscope for health, a laptop for tech, a flag for politics. The enricher fixes ~4 per run but at 200+ affected articles, it can't keep up.

| Category | Pexels Articles |
|----------|----------------|
| technology | 36 |
| news | 30 |
| travel | 27 |
| lifestyle-health | 23 |
| immigration | 23 |
| nri-world | 22 |
| food | 20 |
| sports | 13 |
| markets-finance | 6 |

Entertainment has 0 Pexels images (uses `source-image.py` with Wikipedia/Commons).

**Root cause:** Non-entertainment writers try Wikipedia first per instructions, but often fall back to Pexels when Wiki search fails. The fallback is too easy.

**Recommendation:** 
1. Make Wikipedia/Commons the ONLY option (no Pexels fallback) for person-centric articles
2. Only allow Pexels for genuine stock scenarios (food photos, landscape stock)
3. Have the enricher run more aggressively on Pexels-image articles

### 🟡 IMPORTANT: Social Embeds Barely Working (2 out of 1,280 articles)
Only **2 articles** out of 1,280 published have Instagram embeds. Zero have X embeds. The social embed instructions were just added to all writers, so this should improve, but current adoption is near zero.

- Both IG embeds are in entertainment articles from today (Lagaan, House of the Dragon)
- The enricher ran today and added 0 IG embeds, 2 tweet embeds (via `patch-tweet-embed.py`)

**Root cause:** The social embed instructions are very new (just updated). Registry has empty categories (immigration, travel) and missing IG handles (sports, news, tech). Writers may not be executing the embed search step reliably.

---

## 4. Frontend Audit

### SocialEmbed.tsx — ✅ Working
- Instagram embeds use iframe approach: `instagram.com/p/SHORTCODE/embed/`
- Twitter/X embeds use `react-tweet` library with custom `TweetCard` component
- `detectSocialUrl()` correctly detects both `instagram.com/p/` and `twitter.com|x.com/status/` URLs
- Supports both `p/`, `reel/`, and `tv/` Instagram URL formats

### XOfficialEmbed.tsx — ✅ Working
- Uses official `platform.x.com/widgets.js` for rendering
- Supports both `x-official:URL` and `x-video:URL` formats
- Correct implementation with `blockquote.twitter-tweet` approach

### ArticlePage.tsx — ✅ Working
- Lines 262-268: Correctly detects both `detectSocialUrl` (standalone URLs) and `x-official:` prefix format
- Renders `SocialEmbed` for IG/Twitter URLs and `XOfficialEmbed` for `x-official:` format
- Markdown body is parsed with `ReactMarkdown` + `remarkGfm`
- YouTube embeds via `<youtube>` tags also handled

### ✅ Follow: links issue resolved
The previous "Follow:" links bug was a database content issue, not a frontend rendering bug. The links were in the article body but the frontend wasn't designed to strip them. They've since been removed from all articles in the database.

---

## 5. Pipeline Scripts Audit

### Key Active Scripts
| Script | Status | Notes |
|--------|--------|-------|
| `source-image.py` | ✅ Active | Used by entertainment writer, enricher |
| `social-embed-registry.json` | ✅ Fixed | Corrupted handles corrected |
| `get-enrichable-articles.py` | ✅ Active | Used by tweet-enricher |
| `patch-tweet-embed.py` | ✅ Active | Patches tweets into articles |
| `verify-tweet.sh` | ✅ Active | Validates tweet IDs |
| `tweet-enricher.py` | ✅ Active | Used by tweet-enricher cron |
| `enrich-articles.py` | ✅ Active | Used by enricher cron |
| `rss-ingest.py` | ✅ Active | RSS feed ingestion |
| `send-newsletter-daily.py` | ✅ Active | Daily newsletter |
| `scrape-wait-times.py` | ✅ Active | Consulate wait times |
| `scrape-visa-bulletin.py` | ✅ Active | Visa bulletin data |

### 🟢 NICE-TO-HAVE: Massive script accumulation
The `pipeline/` directory has **500+ Python scripts**, mostly one-off dated scripts (e.g., `entertainment-writer-20260518.py` through `entertainment-writer-20260606.py`). These are historical one-shot writer scripts from before the cron system was set up. They serve as an audit trail but clutter the directory.

**Recommendation:** Move dated scripts to `pipeline/archive/` to keep the active pipeline clean.

---

## 6. Non-Writer Crons Audit

### All Active Crons (39 enabled)

**Content Generation (9):** All writer crons — working  
**Content Enrichment (3):**
- `videshi-enricher` (6h) — fixes images, adds trailers, social embeds
- `videshi-tweet-enricher` (2h) — adds tweet embeds specifically
- `celebrity-buzz-refresh` (6h) — refreshes celebrity IG data for homepage

**Social Posting (5):**
- `videshi-fb-autopost` (12h), `videshi-fb-reels` (12h), `videshi-ig-autopost` (8h), `videshi-threads-autopost` (3h), `videshi-x-autopost` (2h), `videshi-youtube-shorts` (3h)

**Data/Infrastructure (10+):**
- `videshi-ingest` (1h) — RSS feed ingestion
- `videshi-live` (1h) — data refresh + event detection
- `videshi-json-sync` (10m) — JSON feed sync
- `videshi-health` (6h), `videshi-healthcheck` (2h) — health monitoring
- `videshi-site-monitor` (6h) — site monitoring
- `videshi-power-pulse` (6h) — power pulse data
- `videshi-ping-google` (3h) — SEO ping

**Daily (9):**
- Newsletter, quota tracker, scrapers (allevents, meetup A/B), visa updates, wait times, WhatsApp digests

### 🟡 IMPORTANT: Potential Enricher Overlap
Three separate crons now handle social embed enrichment:
1. **Writer crons** (9 of them) — each has social embed instructions
2. **videshi-tweet-enricher** (2h) — specifically searches for and patches tweets
3. **videshi-enricher** (6h) — reviews articles and adds social embeds + fixes images

This could cause conflicts: if a writer adds an embed, then the enricher runs and adds another one, or vice versa. The tweet-enricher checks for existing embeds before adding, which is good.

**Recommendation:** The tweet-enricher may become redundant now that all writers have social embed instructions. Monitor for a week, then consider disabling it if writers are reliably adding embeds.

### 🟢 NICE-TO-HAVE: Disabled WhatsApp digests
- `videshi-whatsapp-digest` (9am) — disabled
- `videshi-whatsapp-digest-pm` (6pm) — disabled
- These were likely disabled intentionally but could be a useful feature

### ✅ Old writer cron disabled
- `videshi-writer__interval@2h.md` — disabled, correctly labeled as "replaced by category-specific writers"

### ✅ Celebrity buzz photos disabled
- `celebrity-buzz-photos` — disabled (separate from refresh, which is active)

---

## 7. Strategy & Content Gaps

### Production Rate (last 7 days = 500 articles)
| Category | Articles/Week | Rate |
|----------|--------------|------|
| news | 97 | ~14/day |
| entertainment | 88 | ~13/day |
| technology | 63 | ~9/day |
| sports | 58 | ~8/day |
| travel | 52 | ~7/day |
| immigration | 37 | ~5/day |
| nri-world | 36 | ~5/day |
| lifestyle-health | 33 | ~5/day |
| markets-finance | 18 | ~3/day |
| food | 18 | ~3/day |

### Content Distribution Analysis
- **Heaviest:** News and entertainment dominate (~40% of output) — appropriate for a news site
- **Lightest:** Food and markets-finance at ~3/day — food could increase
- **Good balance:** Immigration, NRI-world, lifestyle-health each produce 5/day — solid coverage

### 🟢 NICE-TO-HAVE: No dedicated "lifestyle" or "markets" categories
The lifestyle writer produces both `lifestyle-health` AND `markets-finance` articles in a single cron. This means:
- One cron handles two categories at 4h intervals
- Markets-finance has less volume (18 vs 33 for lifestyle-health)
- Consider splitting into two separate crons if markets-finance needs more output

---

## 8. Summary of All Fixes Applied

### ✅ Fixed
1. **Food writer `content` → `body` column name** — would have caused empty article bodies
2. **8 corrupted handles in `social-embed-registry.json`** — Vicky Kaushal, Kamal Haasan, Allu Arjun, AR Rahman
3. **8 corrupted handles in `celebrity-buzz-refresh` cron** — Aishwarya Rai, Samantha, Allu Arjun, Jr NTR, Hrithik Roshan, Varun Dhawan, AR Rahman, Vijay Thalapathy

### ⬜ Recommended (Not Implemented — Needs Decision)

#### High Priority
4. **Add IG handles to sports, news, tech, nri-world** — currently have X only, embeds won't work for IG
5. **Populate immigration and travel social handles** — currently empty (0 handles)
6. **Add Article Quality + Banned Rules to food writer** — only writer missing these sections
7. **Update entertainment social embed section** to unified format covering both IG & X (currently IG-only)

#### Medium Priority
8. **Reduce Pexels dependency** — make Wikipedia/Commons primary, restrict Pexels to food/lifestyle only
9. **Monitor enricher overlap** — writers + tweet-enricher + enricher may duplicate work
10. **Archive 500+ dated pipeline scripts** to `pipeline/archive/`

#### Low Priority
11. **Increase food writer frequency** from 12h to 8h
12. **Consider splitting lifestyle/markets into two crons**
13. **Re-enable WhatsApp digests** if still desired
14. **Add missing IG handles for sports celebrities** — 17 of 21 sports handles lack IG

---

## Appendix: Cron Health Check

All crons running successfully. Last 5 runs for key crons:
- `videshi-tweet-enricher`: 5/5 succeeded
- `videshi-enricher`: 1/1 succeeded (enriched 6 articles, fixed 4 images, added 2 tweets)
- `videshi-health`: 5/5 succeeded

No failures detected in recent runs.
