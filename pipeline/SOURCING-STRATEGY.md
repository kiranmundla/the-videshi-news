# The Videshi — Sourcing Strategy v2

**Date:** July 16, 2026  
**Status:** Proposal — awaiting review

---

## The Problem

The pipeline has three signal sources — RSS feeds, Google News, and email newsletters — but all three are heavily skewed toward tech, immigration, and hard news. Three categories (food, travel, lifestyle) have **zero dedicated feeds and zero Google News queries**, so they produce roughly 15-19 articles per week while tech and news produce 85-90 each.

The Google News queries all contain explicit diaspora keywords ("Indian American", "Indian CEO", "Indian food"). This catches stories *about* Indians but misses stories that *matter to* Indians — a major US immigration policy change that doesn't mention "India" in the headline, a blockbuster Bollywood release covered by mainstream entertainment press, or a new restaurant trend that would resonate with NRI foodies.

---

## Current State

### RSS Feeds (77 active)

| Category | Feeds | Examples |
|---|---|---|
| Technology | 31 | Apple, Google, Microsoft, NVIDIA, Wired, TechCrunch, Ars Technica, MIT Tech Review |
| Economy/Markets | 17 | CNBC, MarketWatch, WSJ Markets, LiveMint, RBI, SEBI |
| Immigration | 13 | USCIS, BAL, Murthy Law, VisaVerge, Forbes Stuart Anderson, CIC News |
| Politics/News | 10 | BBC India, NDTV, Hindu, Times of India, India Today |
| Sports | 9 | ESPN, BBC Sport, CricBuzz, NDTV Sports, Sky Sports |
| Entertainment | 8 | Variety, Deadline, Bollywood Hungama, Koimoi, Filmfare, TMZ |
| Diaspora/NRI | 8 | Al Jazeera, American Bazaar, India West, NRI Pulse |
| Food | **0** | — |
| Travel | **0** | — |
| Lifestyle/Health | **0** | — |

### Google News (26 search queries + 8 topic feeds × 2 geos)

**Topic feeds** scan Top Stories, World, Business, Technology, Entertainment, Sports, Science, Health — both US and India editions. These are the broad nets.

**Search queries** — every single one contains a diaspora keyword:
- Immigration: "green card", "EB-2", "EB-3", "Indian passport", "Indian consulate"
- Achievement: "Indian American", "Indian origin achievement", "Indian CEO", "Indian doctor/engineer/scientist"
- Diaspora life: "Indian restaurant", "Indian food", "hate crime Indian", "Indian student abroad"
- Sports: "Indian Premier League", "Team India"
- Business: "Indian startup", "Indian founder"

**What this misses:**
- A US immigration executive order that doesn't say "India" — our RSS immigration feeds catch it, but Google News doesn't amplify it
- Bollywood coverage in mainstream press that uses actor names, not "Indian film"
- Food/restaurant stories that are culturally relevant but not tagged "Indian"
- Health/wellness trends popular with the NRI demographic
- Entertainment crossovers (Indian actors in Hollywood, streaming launches)

### Email Newsletters (24 signals total)

| Source | Count | Signal value |
|---|---|---|
| Qualcomm (Q4Inc) | 10 | Low — mostly SEC filings, daily stock quotes |
| a16z (Substack) | 4 | Medium — tech/VC perspective |
| USCIS | 2 | High — immigration policy direct from source |
| CIS | 2 | Medium — immigration research |
| MPI | 2 | Medium — migration policy |
| Google/setup | 3 | Zero — welcome emails |
| NVIDIA | 0 | Subscribed but no emails received yet |

**Verdict:** Newsletter channel is underutilized. Only 3 of 7 subscriptions produce actionable signals. Qualcomm SEC filings are noise.

---

## Proposed Strategy

### 1. RSS Feed Expansion

Add dedicated feeds for the three starving categories. These should be high-quality, regularly updated sources:

**Food (target: 8-10 feeds)**
- Eater (major US food news)
- Bon Appétit (recipes, trends)
- Serious Eats
- Food52
- Saveur (Indian food coverage is strong)
- Swasthi's Recipes / Indian food bloggers (RSS available)
- Condé Nast Traveller India — Food section
- The Infatuation (restaurant reviews, US cities)
- NDTV Food

**Travel (target: 8-10 feeds)**
- Condé Nast Traveler
- Travel + Leisure
- Lonely Planet
- The Points Guy (NRIs are frequent flyers — points/miles very relevant)
- Skift (travel industry news)
- NDTV Travel
- Atlas Obscura
- Nomadic Matt
- India Times Travel

**Lifestyle & Health (target: 6-8 feeds)**
- Well+Good
- Healthline
- Indian Express Lifestyle
- Hindustan Times Lifestyle
- Vogue India
- WebMD (health news)
- Yoga Journal (strong NRI audience)
- Mint Lounge

**Entertainment expansion (current 8 → 12)**
- Deadline India (if available)
- Screen Rant
- Collider
- JioCinema/Hotstar blog (streaming releases)

### 2. Google News Strategy — Flip the Model

**Current approach:** Search for "Indian" + keyword → only finds stories that mention Indians explicitly.

**New approach:** Scan by category first, filter for diaspora relevance second.

#### Layer 1: Broad Category Scanning (already in place)
The 8 topic feeds × 2 geos already do this. Keep them.

#### Layer 2: Smart Search Queries (rewrite)

Instead of all-diaspora-keyword queries, split into two types:

**Type A — Diaspora-specific (keep, refine):**
These target stories that are inherently about the diaspora. Keep 10-12 of the best current queries, drop redundant ones.

```
"H-1B" OR "green card" OR "EB-2" OR "EB-3" OR "USCIS"
"Indian American" achievement OR appointed OR elected
"Indian startup" OR "Indian unicorn" OR "Indian founder"
NRI OR "Indian diaspora" remittance OR deposit OR investment
"Indian restaurant" Michelin OR award OR opening
"Indian student" OR "Indian international student"
"OCI card" OR "Indian passport" OR "Indian consulate"
Bollywood OR "Indian film" box office OR release OR trailer
IPL OR "Indian cricket" OR "India cricket"
"Indian temple" OR "Diwali" OR "Holi" OR "Navratri"
```

**Type B — Category-relevant, no diaspora keyword (new):**
These catch important stories that affect the diaspora but don't mention "Indian" in the headline.

```
# Immigration (affects all H-1B holders)
immigration reform OR "immigration bill" OR visa policy
USCIS OR "green card backlog" OR "immigration court"
"work visa" OR "skilled worker" OR "employment-based"

# Markets (NRIs care about both US + India markets)
"S&P 500" OR NASDAQ OR "Fed rate" OR "interest rate"
Sensex OR Nifty OR "rupee" OR "RBI policy"
"tech layoffs" OR "tech hiring" OR "tech earnings"

# Entertainment (crossover content)
Netflix India OR "Prime Video India" OR Hotstar
"South Asian" film OR actor OR director
"box office" India OR Bollywood

# Food
"Indian cuisine" OR "South Asian food" OR curry OR biryani
Michelin Indian OR "Indian chef" OR "spice"

# Travel
"India flights" OR "Air India" OR "IndiGo"
"travel to India" OR "India tourism" OR "India visa"

# Health/Wellness
yoga OR Ayurveda OR meditation trending
"mental health" South Asian OR Indian
turmeric OR "Indian superfoods"
```

#### Layer 3: Trending Topic Detection (new)
Once a day, scan Google Trends for India + US, identify any surging topic that crosses our categories but isn't in our RSS or search queries. This is the "don't miss a major story" safety net.

### 3. Email Newsletter Overhaul

**Drop:**
- Qualcomm daily stock quotes and SEC filings (10 of 24 signals are noise)

**Keep:**
- USCIS (direct immigration policy)
- CIS, MPI (immigration research)
- a16z (tech/VC)

**Add (high-value, not yet subscribed):**
- Morning Brew (daily US business/markets)
- The Hustle (tech + business, daily)
- Eater Newsletter (food)
- Skift Daily (travel industry)
- The Points Guy daily (travel/loyalty — huge NRI audience)
- TechCrunch Daily (tech)
- AILA (immigration lawyers — members-only, but try)
- Times of India NRI edition newsletter
- Mint (Indian markets daily)

**Goal:** Get email newsletters from 24 low-quality signals to 50+ high-quality signals per week.

### 4. Category Balance in the Writer

The selector currently picks the top N stories by score. High-signal categories (news, tech, immigration) always win because they have more feeds → more signals → higher cluster scores.

**Fix: Enforce category minimums.**

Every writer run must produce at least:
- 1 article from the bottom 3 categories (food, travel, lifestyle)
- 1 entertainment article if none published in last 6 hours
- No more than 3 articles from any single category per run

This guarantees every section on the homepage stays fresh without over-producing in any one area.

### 5. Image Pipeline

**Current problem:** Writer generates Wikipedia URLs without verifying they exist. Broken images go straight to the hero slot.

**Proposed image chain (fail-forward):**

```
1. Source article's own image (og:image from the RSS item)
   → Verify: HTTP 200, ≥600px wide, not SVG/logo
   → If valid: use it (fastest, most relevant)

2. Media library cache (person_images table + local mirror)
   → Check if we already have a verified image for this subject
   → If found: use it (no network call needed)

3. Wikipedia / Wikimedia Commons
   → API query for the subject → get File: name → thumb URL
   → Verify: HTTP 200 (use GET, never HEAD — HEAD returns 400 from this env)
   → If valid: use it

4. Pexels (generic fallback)
   → Search query from headline keywords
   → Verify: landscape, ≥800px, relevant
   → If valid: use it with attribution

5. No image
   → Publish without hero image rather than publishing a broken one
   → Flag for manual review
```

**Key rules:**
- Every image URL gets a real HTTP GET check before it's written to the DB
- No fabricated Wikipedia URLs — use the API to find real pages
- Source article og:image is the best option and should be tried first
- Never use AI-generated images of real people

### 6. Unified Ingest (v2-ingest.py)

The v2-ingest script already exists and runs every 30 minutes. It handles RSS + Google News in one pass. Changes needed:

1. Add the new RSS feeds to `p2_feed_sources` table
2. Update `google-news-ingest.py` with the new search queries
3. Wire email_signals into the unified ingest loop
4. Add source_type tracking so we can measure which sources produce the best articles

---

## Implementation Order

| Step | What | Effort | Impact |
|---|---|---|---|
| 1 | Add RSS feeds for food/travel/lifestyle to `p2_feed_sources` | 30 min | High — fills the source blackout |
| 2 | Rewrite Google News queries (Type A + B split) | 1 hour | High — catches stories we're missing |
| 3 | Add category minimums to rolling writer | 30 min | High — guarantees homepage freshness |
| 4 | Image verification chain in writer | 2 hours | High — kills broken hero images |
| 5 | Newsletter subscriptions (new sources) | 1 hour | Medium — more signal diversity |
| 6 | Drop Qualcomm noise from email signals | 15 min | Low — cleaner signal pool |
| 7 | Google Trends daily scan | 2 hours | Medium — safety net for major stories |

---

## Success Metrics

After implementation, we should see:
- **Food/Travel/Lifestyle:** 5+ articles per day each (currently 2-3)
- **Zero broken hero images** (currently 5-10% failure rate on new articles)
- **All 10 homepage sections showing fresh content** (< 6 hours old)
- **No major story missed** across any category for more than 2 hours
- **Signal diversity:** At least 3 source types contributing to each category

---

## Open Questions

1. **Article volume target:** With expanded sources, should we go back to 65-80/day or stay at the current ~50?
2. **Source article images:** Using og:image from source articles means showing the source's photography. Is that OK legally? (Fair use for news commentary is defensible, but worth deciding.)
3. **Google News rate limiting:** How aggressively can we poll without getting blocked? Current: every 30 min. Proposed: keep at 30 min but with more queries.
4. **Email newsletter subscriptions:** Should I subscribe signals@thevideshi.com to the new sources, or should you do it to keep control?

---

## Appendix: Image Pipeline — Detailed Findings

### Current Flow (broken)

```
Writer picks topic → LLM generates image_search_query + image_entities
  → Wikipedia person lookup (entities)
  → Wikimedia Commons search (search query)
  → Pexels fallback (search query)
  → Upload to Supabase storage
```

**Problems:**
1. RSS feeds carry `media:thumbnail` images (verified: BBC, NDTV, etc.) but the ingest scripts **discard them** — `p2_signals` has no image column
2. The writer never fetches og:image from the source article URL — even though it has the `original_url`
3. Wikipedia lookups sometimes return wrong images (Pennsylvania State Capitol for US Capitol Hill)
4. No HTTP verification on any image URL before writing to DB
5. All 10 articles published today used Wikipedia/Commons — zero used the source article's actual image

### Proposed Flow

```
1. Source article's own image (og:image from original_url)
   → curl the source URL, extract og:image meta tag
   → HTTP GET verify: 200 OK, Content-Type starts with image/, ≥600px
   → BEST option: most relevant, already editorial-quality

2. RSS feed image (media:thumbnail stored at ingest time)
   → Already captured in p2_signals.image_url (new column)
   → HTTP GET verify
   → GOOD: editorial photo, already associated with the story

3. Media library cache (person_images)
   → Check if we have a verified image for this subject
   → No network call needed

4. Wikipedia / Wikimedia Commons
   → API query → get File: title → thumb URL
   → HTTP GET verify (never HEAD — returns 400 from this env)
   → Commons relevance gate still applies

5. Pexels (last resort)
   → Landscape, ≥800px
   → With attribution

6. No image
   → Publish without hero rather than publish a broken one
   → Log for manual review
```

### DB Changes Needed

```sql
-- Add image column to p2_signals
ALTER TABLE p2_signals ADD COLUMN image_url TEXT;
```

### Ingest Changes Needed

In `rss-ingest.py` and the RSS section of `v2-ingest.py`:
- Extract `media:thumbnail`, `media:content`, or `enclosure` image URL from each RSS item
- Store in `p2_signals.image_url`

In `google-news-ingest.py`:
- Google News RSS items sometimes carry images too — capture them

### Writer Changes Needed

In `rolling-writer.py` `source_hero_image()`:
- Add Source 0: fetch og:image from source article's `original_url`
- Add Source 0.5: check if any signal in the topic has an `image_url`
- Keep existing Wikipedia/Commons/Pexels as fallback chain
- Add HTTP GET verification wrapper around ALL image URLs

