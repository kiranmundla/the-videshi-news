# The Videshi — Pipeline Architecture

**Author:** Engineering  
**Date:** July 16, 2026  
**Status:** Design — Review before implementation

---

## Executive Summary

The Videshi's editorial pipeline has three layers: **Ingest** (gather signals from the web), **Cluster** (group signals into topics), and **Write** (produce articles from topics). Today these layers are spread across five scripts with conflicting responsibilities, 100+ cron definitions with massive duplication, and zero feed coverage for three of ten editorial categories. This document replaces all of it with a clean, opinionated architecture.

**Key decisions made here:**
1. Two scripts, not five: `v2-ingest.py` (signals + clustering) and `rolling-writer.py` (writing + images).
2. Kill all category writers. One writer, one cadence, enforced category quotas.
3. Add 25 RSS feeds for food, travel, lifestyle, and entertainment.
4. Tighten Google News queries around diaspora relevance — no generic queries.
5. Consolidate crons from ~100 to ~15 non-duplicate definitions.

---

## 1. Feed Strategy

### Design Principle: Diaspora Relevance

Every story must pass a simple test: **Would an Indian living in the US/UK/Canada care about this more than a random local would?**

This does not mean every headline needs the word "Indian." It means:
- A Fed rate decision qualifies because NRIs hold US mortgages.
- An NVIDIA earnings beat qualifies because Indian engineers are a huge part of that workforce.
- A "Best New Restaurants in Nashville" list does NOT qualify unless it's an Indian restaurant.
- A Bollywood film release qualifies. A random Netflix docuseries does not, unless it features Indian subjects.

### 1.1 RSS Feed Inventory

**Current state: 77 active feeds.** Coverage by category:

| Category | Current Feeds | Gap |
|---|---|---|
| technology | 18 | Overcovered. Drop 4 vendor blogs (AWS, Intel, Google DeepMind, Meta Engineering). |
| economy/markets | 17 | Adequate, but "economy" vertical ≠ "markets-finance" category. Relabel. |
| immigration | 13 | Strong. Keep all. |
| politics/news | 10 | Adequate. |
| sports | 9 | Good. Cricket-heavy (correct for audience). |
| entertainment | 8 | Adequate Bollywood+Hollywood mix. Add 2 Indian OTT sources. |
| diaspora/nri-world | 8 | Good for community news. |
| **food** | **0** | **Complete blind spot.** |
| **travel** | **0** | **Complete blind spot.** |
| **lifestyle-health** | **0** | **Complete blind spot.** |

### 1.2 Feeds to Add

All feeds below have been selected for diaspora relevance. Generic food/travel/lifestyle outlets (Bon Appétit, Lonely Planet, WebMD) are excluded because they drown the signal pool with irrelevant content and force the writer's LLM scoring to filter 95% noise for 5% usable stories. The right approach: feed the pipeline Indian-specific or diaspora-adjacent sources, and let Google News handle the occasional crossover story.

#### Food (7 feeds) — Indian-specific per editorial direction

| Feed | URL | Why |
|---|---|---|
| NDTV Food | `https://feeds.feedburner.com/ndtvfood-latest` | Indian recipes, restaurant reviews, food news. *(Original `/rss/recipes` returns 403; FeedBurner mirror works.)* |
| Eater (search "Indian") | `https://www.eater.com/rss/index.xml` | US restaurant scene — catches Indian restaurants winning awards, chef profiles. High volume, but the LLM filter handles relevance. |
| Swasthi's Indian Recipes | `https://www.indianhealthyrecipes.com/feed/` | Pure Indian recipe content, popular with diaspora. *(Feed returned 0 items in testing — may use Atom format or require browser UA. Verify in production before activating.)* |
| Hebbar's Kitchen | `https://hebbarskitchen.com/feed/` | Most popular Indian food blog, strong SEO/social |
| Veg Recipes of India | `https://www.vegrecipesofindia.com/feed/` | Vegetarian Indian cooking, huge NRI audience |
| Indian Express Food | `https://indianexpress.com/section/lifestyle/food-wine/feed/` | Indian food news, restaurant openings, trends |
| Spice Cravings | `https://spicecravings.com/feed` | Indian Instant Pot recipes — massively popular with US NRIs |

#### Travel (6 feeds) — India travel + NRI travel needs

| Feed | URL | Why |
|---|---|---|
| The Points Guy | `https://thepointsguy.com/feed/` | Credit card points, airline miles — NRIs are power travelers. Air India reviews, lounge access, booking hacks. Core diaspora interest. |
| NDTV Travel | `https://www.ndtv.com/rss/travel` | India travel news, new routes, tourism |
| Condé Nast Traveller India | `https://www.cntraveller.in/feed/` | India destinations, luxury travel |
| Skift | `https://skift.com/feed/` | Travel industry news — airline routes, airport changes, visa policies. Catches Air India/IndiGo fleet stories. |
| Live From a Lounge | `https://livefromalounge.com/feed/` | Airport lounges, premium travel — high NRI relevance |
| India Times Travel | `https://timesofindia.indiatimes.com/travel/rssfeeds/7968293.cms` | India travel guides and news |

#### Lifestyle-Health (6 feeds) — wellness, culture, NRI life

| Feed | URL | Why |
|---|---|---|
| Indian Express Lifestyle | `https://indianexpress.com/section/lifestyle/feed/` | Health, fitness, culture from Indian lens |
| Hindustan Times Lifestyle | `https://www.hindustantimes.com/feeds/rss/lifestyle/rssfeed.xml` | Indian lifestyle, wellness. *(Original `/lifestyle/rss` path returns 000; full RSS feed path works.)* |
| Yoga Journal | `https://www.yogajournal.com/feed/` | Yoga practice, wellness — strong NRI audience |
| Well+Good | `https://www.wellandgood.com/feed/` | Wellness trends. High volume but frequently covers turmeric/Ayurveda/yoga — diaspora-adjacent. |
| Mint Lounge | `https://lifestyle.livemint.com/rss/lounge` | Culture, books, food, wellness — premium Indian lifestyle |
| Brown Girl Magazine | `https://browngirlmagazine.com/feed/` | South Asian diaspora culture, identity, lifestyle — core audience |

#### Entertainment additions (2 feeds) — Indian OTT and streaming

| Feed | URL | Why |
|---|---|---|
| Film Companion | `https://www.filmcompanion.in/feed/` | Indian film criticism, reviews, industry analysis |
| Pinkvilla Entertainment | `https://www.pinkvilla.com/feed/entertainment` | Bollywood news, TV, OTT releases |

**Total new feeds: 21.** Total after additions: ~98 active.

#### Feeds to deactivate (4) — reduce tech noise

| Feed | Reason |
|---|---|
| AWS News Blog | Vendor product announcements, no diaspora angle |
| Intel Newsroom | Vendor PR, rarely relevant |
| Google DeepMind Blog | Research papers, not news |
| Meta Engineering | Engineering blog posts, not news |

These are not bad feeds — they're just wrong for a news pipeline. They generate signals that always score below the writer's relevance threshold, wasting LLM evaluation tokens.

**Total after cleanup: ~95 active feeds.**

> **Feed validation note:** 8 of the 21 proposed feeds were validated with HTTP 200 and confirmed items. 2 needed URL corrections (applied above). ~10 returned HTTP 000 (proxy timeout in the dev environment at 10s). Known-working feeds like Bollywood Hungama and BBC all returned 200 immediately, so the 000s are almost certainly proxy/latency issues, not dead feeds. Validate each in production (or with a longer timeout) before marking active. Swasthi's returned 200 but 0 items — may need Atom-format parsing or a browser User-Agent.

### 1.3 Google News Queries

Google News serves two purposes: (a) catch breaking stories that RSS feeds are slow to pick up, and (b) cover topic intersections that no single RSS feed targets.

#### Topic Feeds (keep as-is)
8 topics × 2 geos (US + India) = 16 feeds. These are the broad safety nets:
- Top Stories, World, Business, Technology, Entertainment, Sports, Science, Health

These catch major stories regardless of our query design. Keep them.

#### Search Queries — 20 total

**Type A — Diaspora-explicit (10 queries).** These target stories that mention Indians directly.

```
'H-1B visa OR "green card" OR "EB-2" OR "EB-3" OR USCIS'
'"Indian American" OR "Indian origin" OR "Indian diaspora"'
'"Indian CEO" OR "Indian founder" OR "Indian startup"'
'OCI card OR "Indian passport" OR "Indian consulate"'
'NRI OR "non-resident Indian" OR "overseas Indian"'
'Infosys OR TCS OR Wipro OR "HCL Tech" OR "Tech Mahindra"'
'Bollywood OR "Indian film" OR "Indian cinema"'
'"Indian restaurant" OR "Indian food" OR Diwali OR Holi'
'"Indian student" abroad OR "Indian community"'
'India cricket OR "Team India" OR IPL'
```

**Type B — Diaspora-adjacent (10 queries).** These target stories that affect NRIs without necessarily saying "Indian." Each has a clear rationale.

```
# Immigration — policy changes that directly impact H-1B/green card holders
'"work visa" policy OR "immigration reform" OR "visa processing"'
'DACA OR "immigration court" OR "premium processing"'

# Tech — companies and trends that employ/affect large Indian workforce
'NVIDIA OR Google layoffs OR "Silicon Valley" hiring'
'AI regulation OR semiconductor OR "chip act"'

# Markets — the two markets NRIs actually invest in
'"Federal Reserve" rate OR Sensex OR Nifty OR "rupee dollar"'

# Entertainment — Indian-origin talent in Hollywood + streaming
'"Dev Patel" OR "Mindy Kaling" OR "Hasan Minhaj" OR "Priyanka Chopra"'
'"Alia Bhatt" OR "Ram Charan" OR "SS Rajamouli" OR "Indian film" festival'

# Food — Indian-specific only
'"Indian food" OR "Indian recipe" OR biryani OR "dosa" OR "Indian restaurant"'
'turmeric OR "masala" OR "Indian grocery" OR "Indian spice" OR paneer'

# Travel — flights to India and India tourism
'"Air India" OR "IndiGo airlines" OR "India flights" OR "India travel"'
```

**What's NOT here (and why):**
- `Netflix OR streaming` → generates thousands of irrelevant results
- `"S&P 500" OR NASDAQ` → already covered by 17 economy/markets RSS feeds
- `yoga OR meditation OR Ayurveda` → too generic, catches wellness clickbait
- `"Michelin star" OR "food trend"` → not Indian-specific
- `immigration reform OR deportation` → too broad, catches US-Mexico border stories

The topic feeds (Health, Science, Entertainment etc.) already catch the broad category news. Type B queries don't need to duplicate that — they need to catch the *diaspora-adjacent* stories that the topic feeds rank low because they're not mainstream enough.

### 1.4 Diaspora Relevance Standard by Category

This is the editorial rubric the writer's LLM evaluator uses to score `diaspora_relevance` (1-10). A story needs ≥5 to proceed.

| Category | Qualifies (7-10) | Marginal (4-6) | Reject (1-3) |
|---|---|---|---|
| **immigration** | H-1B/EB/OCI policy, USCIS processing, deportation affecting Indians | Generic US immigration (border, asylum) that may set precedent | State DMV changes, local court cases |
| **technology** | Indian-origin tech leaders, H-1B layoff impact, India chip policy | Major product launches (iPhone, etc.) that NRIs buy | Random app updates, gaming news |
| **news** | NRI safety/hate crimes, India elections/disasters, bilateral relations | Major US/world events that NRIs follow as residents | Local US crime, India city-level news |
| **entertainment** | Bollywood releases on US/UK platforms, Indian-origin Hollywood talent | Big Hollywood releases with Indian cast, Indian music global | Pure India box office ₹crore numbers, celeb gossip |
| **sports** | India cricket always, Indian-origin athletes, MLC, World Cup with India angle | Olympics with India medal prospects, FIFA World Cup (NRIs follow) | Random domestic Indian league, non-India international sports |
| **markets-finance** | FAANG earnings (NRIs own these stocks), Fed rate (NRI mortgages), Sensex major moves | Mid-cap earnings of India-adjacent companies | Random small-cap, routine daily market moves |
| **food** | Indian restaurants opening/awarded in US/UK/Canada, Indian grocery, fusion cuisine, Indian recipes | Indian food trends globally | Pure India restaurant news, non-Indian food |
| **travel** | Air India/IndiGo routes, India travel advisories, NRI travel tips | International airport/airline news affecting India routes | Random domestic India tourism, non-India travel |
| **lifestyle-health** | NRI health concerns, Ayurveda/yoga research, South Asian health disparities | Wellness trends popular with diaspora (turmeric, meditation) | Generic US health news |
| **nri-world** | Community events abroad, diaspora org news, cultural celebrations | Indian-origin achievements in any field | India-only community events |

### 1.5 Daily Article Targets

**Total target: 50-65 articles/day.** Quality over quantity.

| Category | Target/day | Rationale |
|---|---|---|
| news | 8-12 | Breaking stories, major events. High signal volume but strict diaspora filter. |
| technology | 6-10 | Indian tech ecosystem + Silicon Valley = core audience interest. |
| immigration | 5-8 | Core USP — the category readers come for. Every policy change matters. |
| sports | 5-8 | Cricket-heavy. Spikes during IPL/World Cup. |
| markets-finance | 5-8 | US markets + India markets. NRIs actively invest in both. |
| entertainment | 5-7 | Bollywood + crossover. Steady stream, not spikes. |
| nri-world | 4-6 | Community news. Lower volume but high loyalty. |
| lifestyle-health | 3-5 | Wellness, culture. New category — build slowly. |
| travel | 3-5 | Flights, destinations, points. Seasonal variation. |
| food | 3-5 | Indian recipes, restaurants. New category — build slowly. |

---

## 2. Ingest Architecture

### Design Decision: One Script

`v2-ingest.py` becomes the single ingest script. It handles RSS, Google News, and email newsletters in one pass. `rss-ingest.py` and `google-news-ingest.py` are retired.

**Why one script:**
- Dedup must happen across all source types in a single hash window. Separate scripts with separate hash loads waste memory and miss cross-source duplicates.
- A single run produces a single log. When ingest breaks, there's one place to look.
- Google News rate limiting is easier to manage in one process.

### 2.1 Data Flow

```
RSS Feeds (p2_feed_sources)  ─┐
Google News (topic + search)  ─┼──→ v2-ingest.py ──→ p2_signals ──→ Clustering ──→ p2_topics
Email Newsletters             ─┘                     (with image_url)              (with category)
```

### 2.2 Signal Schema

Each signal in `p2_signals`:

| Field | Source | Notes |
|---|---|---|
| title | All | First 500 chars |
| original_url | All | The source article URL |
| url_hash | Computed | MD5 of normalized URL (strip tracking params, www, trailing slash) |
| feed_source_id | RSS only | UUID from p2_feed_sources; NULL for Google News/email |
| source_type | All | `rss`, `google_news`, or `newsletter` |
| source_name | All | Feed name or publication name |
| published_at | All | Parsed from RSS pubDate or email received_at |
| fetched_at | Computed | UTC timestamp of this ingest run |
| image_url | RSS/GN | media:thumbnail, media:content, or enclosure image URL |
| google_cluster_size | GN only | Number of sources in Google News cluster |
| is_processed | System | Set true after clustering |

### 2.3 Dedup Strategy

- **Hash window:** 14 days. Load all `url_hash` values from `p2_signals` where `fetched_at >= now - 14d`.
- **Normalization:** Strip `utm_*`, `fbclid`, `gclid`, `ref`, `source` params. Strip `www.` prefix. Strip trailing slashes. Lowercase hostname.
- **Cross-source dedup:** Same hash window applies to RSS, Google News, and email. A BBC story picked up by RSS won't be re-ingested when Google News surfaces it.
- **Batch dedup:** Within a single ingest run, track seen hashes in memory to avoid inserting the same story twice from two Google News queries.

### 2.4 Clustering (Critical Gap — Must Fix)

**Current bug:** `v2-ingest.py` inserts signals but does NOT cluster them into topics. The rolling writer reads from `p2_topics`, not `p2_signals`. If v2-ingest runs alone, no topics are created, and the writer has nothing to write.

The clustering logic currently lives in `rss-ingest.py` (lines 201-354). It needs to move into `v2-ingest.py`.

**Clustering algorithm (port from rss-ingest.py):**

1. Load all `is_processed = false` signals (limit 500, ordered by `fetched_at DESC`).
2. For each signal, extract title keywords (words ≥4 chars, excluding stop words).
3. Try to match to an existing cluster using ≥50% keyword overlap (relative to smaller set).
4. If no match, create a new cluster.
5. For each cluster:
   - Pick the best title (longest) as `canonical_title`.
   - Detect category from title keywords.
   - Compute scores: `score_significance = min(50 + n*10, 90)`, `score_source_avail = min(n*20, 90)`, `score_total = weighted average`.
   - Insert into `p2_topics` with `status = 'pending'`.
   - Link signals to topic via `p2_topic_signals`.
6. Mark all clustered signals as `is_processed = true`.

**Category detection keywords** (merge from both scripts, harmonize to valid categories):

| Category | Trigger keywords |
|---|---|
| sports | cricket, ipl, sports, tennis, match, wicket, football, soccer, fifa, world cup, athlete, olympics |
| entertainment | bollywood, film, movie, actor, actress, box office, ott, netflix, streaming, music, album, celebrity |
| technology | tech, ai, startup, software, google, apple, meta, chip, nvidia, openai, microsoft, quantum, semiconductor |
| immigration | visa, immigration, green card, h1b, h-1b, uscis, deportation, asylum, work permit, eb-2, eb-3, opt |
| nri-world | nri, diaspora, indian-american, indian american, indian origin, overseas indian, oci, pio |
| markets-finance | market, sensex, nifty, stock, gdp, rupee, rbi, nasdaq, dow jones, s&p 500, earnings, fed, inflation |
| food | recipe, biryani, masala, curry, paneer, dosa, tikka, tandoori, indian food, indian restaurant, spice |
| travel | airline, flights, airport, tourism, travel advisory, air india, indigo, passport, lounge |
| lifestyle-health | health, yoga, wellness, ayurveda, meditation, fitness, mental health, skincare |
| news | *(default)* |

### 2.5 Image Capture at Ingest

RSS feeds carry images in `media:thumbnail`, `media:content`, and `enclosure` tags. v2-ingest.py already extracts these (after recent patches). The `image_url` column in `p2_signals` stores them for the image sourcer to use later.

Google News RSS items sometimes carry images too — the current `parse_rss()` function handles both RSS 2.0 and Atom with media namespace extraction.

### 2.6 Error Handling

- **Per-feed timeout:** 8 seconds. A slow feed doesn't block the run.
- **Parallel fetching:** 10 workers. Total ingest run should complete in <90 seconds.
- **Retry:** No per-feed retry. A feed that fails will be picked up next run (30 min later).
- **Rate limiting:** Google News doesn't officially rate-limit RSS, but to be safe, fetches are throttled by the thread pool (max 10 concurrent). No explicit delay needed.
- **Total run timeout:** 120 seconds hard limit (enforced by cron `timeout`).

---

## 3. Writer Architecture

### Design Decision: One Writer, Category Quotas

`rolling-writer.py` is the only writer. All 10 category-specific writers are retired. The rolling writer runs every hour, picks the top 3 topics, writes them, and inserts with `status = 'review'`.

### 3.1 Topic Selection

The writer's topic selection pipeline:

```
p2_topics (status='pending', last 12h, score >= 40)
  → Keyword dedup against articles from last 48h
  → LLM scoring: newsworthiness (1-10) × diaspora_relevance (1-10)
  → Filter: diaspora_relevance >= 5 AND combined >= 13
  → Sort by combined score DESC
  → Category diversity cap: max 2 from same category per run
  → Select top 3
```

**The LLM prompt is the core editorial intelligence.** It contains detailed scoring rubrics per category (Section 1.4 above). The prompt tells the model to penalize stale topics (`hours_ago` field) — a breaking story from 1 hour ago beats the same story arriving 8 hours late.

### 3.2 Category Quotas (New — Must Implement)

**Problem:** High-signal categories (news, tech, immigration) always win the top-3 spots because they have more feeds → more signals → higher cluster scores. Food/travel/lifestyle get starved.

**Solution: Guaranteed minimum coverage.**

After the standard top-3 selection, the writer checks a "coverage table" — how many articles were published in each category in the last 12 hours:

```python
CATEGORY_FRESHNESS_TARGET = {
    # Max hours before a category is considered "stale"
    "news": 3,
    "technology": 4,
    "immigration": 6,
    "sports": 4,
    "markets-finance": 4,
    "entertainment": 6,
    "nri-world": 8,
    "lifestyle-health": 8,
    "travel": 10,
    "food": 10,
}
```

If ANY category has no articles newer than its freshness target, the writer:
1. Finds the best pending topic in that category (score >= 10, any diaspora_relevance).
2. Adds it as a 4th article for this run (or replaces the lowest-scoring pick if we're at capacity).
3. Lowers the diaspora_relevance floor to 3 for stale categories — these are "coverage duty" articles.

This guarantees every category section on the homepage stays fresh without manual intervention. The freshness targets are intentionally loose for new categories (food/travel at 10 hours) — we don't force low-quality filler when there genuinely isn't a good story.

### 3.3 Article Generation

The writer sends the topic title, source URLs, and category to GPT-4o-mini (primary) or Gemini 2.5 Flash (fallback, with `thinkingBudget: 0`).

The prompt enforces:
- Headline: 20-120 chars, newspaper style
- Body: 600-900 words, markdown with `##` subheadings
- Diaspora angle per category (except markets-finance for US-market stories — those are written as straight financial journalism because the reader IS in the US)
- Style: The Economist / Bloomberg, not a blog
- Sources: At least 2 real sources cited
- No fabricated dates, quotes, or statistics

**Output fields:**
headline, subheadline, body, category, vertical, tags, slug, sources, diaspora_angle, article_type, newsworthiness (1-30), diaspora_impact (1-30), prominence (1-20), image_search_query, image_must_show, image_entities

### 3.4 Image Sourcing

After article generation, `image_sourcer.py` runs the 6-source priority chain:

1. **og:image** from source article URL → curl source, extract meta tag, verify HTTP 200
2. **RSS feed image** from `p2_signals.image_url` → already captured at ingest, verify
3. **Media library** from `person_images` table → cached, verified person photos
4. **Wikipedia** person image → REST API summary endpoint, verify (GET, never HEAD)
5. **Wikimedia Commons** search → API search, relevance gate (`commons_relevance_ok`), verify
6. **Pexels** fallback → landscape, ≥800px, with attribution
7. **No image** → publish without hero (no image > broken image)

Every URL is verified with `curl -o /dev/null -w "%{http_code} %{content_type}"` before use. Never HEAD (returns 400 from this environment for Wikimedia).

After verification, the image is downloaded, compressed to JPEG (max 1200px wide, 80% quality), focal point computed, and uploaded to Supabase Storage `article-images/` bucket.

**Batch dedup:** A set of `used_images` tracks URLs used in the current writer run to prevent two articles from getting the same hero image.

### 3.5 Cadence

- **Ingest:** Every 30 minutes. Catches new stories promptly.
- **Writer:** Every 60 minutes. Produces 2-4 articles per run = 48-96/day.
- **Reviewer:** Every 2 hours. Scores and auto-revises or promotes.

---

## 4. Quality Gates

### 4.1 Article Reviewer (`review-articles.py`)

Articles are inserted with `status = 'review'`. The reviewer cron runs every 2 hours in `--pre-publish` mode:

1. **Pre-checks (no LLM):** Duplicate embeds, duplicate images, broken image URLs.
2. **LLM scoring:** GPT-4o-mini (primary) + Gemini 2.5 Flash (fallback). Scores overall quality 1-10.
3. **Auto-action:**
   - Score 7+ → `status = 'published'` (auto-promoted)
   - Score 4-6 → LLM revision with feedback, then re-score
   - Score 1-3 → `status = 'archived'` if both reviewers agree, else revision attempt
4. **Embed cleanup:** Irrelevant tweet/social embeds auto-removed. Duplicate embeds deduped.

### 4.2 Image Verification

Built into `image_sourcer.py`:
- Every image URL verified with HTTP GET before use
- Rejects SVG, images <400px wide
- Content-type must start with `image/`
- Download, compress, re-upload to own storage (never hotlink external images in production)

### 4.3 Body-Level Duplicate Detection

The writer does keyword-level dedup against articles from the last 48 hours (≥3 shared distinctive keywords = duplicate). The site monitor has Layer C entity-based dedup for post-publish detection, but this is currently fragile with single-word entities (see AGENTS.md) and should be used for alerting, not auto-unpublishing.

### 4.4 Hindi Filter

Signals with >15% Devanagari characters are dropped. The Videshi is English-only. This runs in the writer's topic selection, not at ingest (some Hindi-titled signals cluster with English ones and improve topic scores).

---

## 5. Cron Topology

### Target State: 15 Core Crons

Every cron has exactly one definition file. No duplicates.

#### Tier 1 — Pipeline Core (must be running for content to flow)

| Cron ID | Script | Cadence | Purpose |
|---|---|---|---|
| `videshi-v2-ingest` | `v2-ingest.py` | Every 30min | Ingest signals from RSS + Google News + email. Cluster into topics. |
| `videshi-rolling-writer` | `rolling-writer.py` | Every 60min | Pick top topics, write articles, source images, insert with status=review. |
| `videshi-article-reviewer` | `review-articles.py --pre-publish` | Every 2h | Score, revise, promote or archive articles. |

#### Tier 2 — Content Quality & Distribution

| Cron ID | Script | Cadence | Purpose |
|---|---|---|---|
| `videshi-json-sync` | `prebuild-feeds.py` | Every 10min | Rebuild JSON feeds for frontend. |
| `videshi-enricher` | `enrich-articles.py` | Every 6h | Add inline images, data cards, key takeaways to published articles. |
| `videshi-site-monitor` | `site-monitor.py` | Every 6h | Check for broken images, dead links, stale sections. |
| `videshi-article-ranker` | `article-ranker.py` | Every 30min | Recompute display_score for homepage ranking. |

#### Tier 3 — Social Distribution

| Cron ID | Script | Cadence | Purpose |
|---|---|---|---|
| `videshi-x-autopost` | `x-autopost.py` | Every 6h | Post top articles to X/Twitter. |
| `videshi-fb-autopost` | `fb-autopost.py` | Every 3h | Post to Facebook page. |
| `videshi-distribute-reels` | `distribute-reels.py` | Every 6h | Post reels to IG/Threads/YT/X. |

#### Tier 4 — Live Data & Supporting

| Cron ID | Script | Cadence | Purpose |
|---|---|---|---|
| `videshi-live` | Various market/IPL/snapshot scripts | Every 1h | Refresh live data widgets. |
| `videshi-email-signal-ingest` | `gmail-scanner.py` | Every 3h | Scan email inbox for newsletter signals. |
| `videshi-healthcheck` | Health check script | Every 2h | Monitor pipeline health, alert on failures. |
| `videshi-ping-google` | Indexing API | Every 3h | Submit new articles to Google for indexing. |

#### Tier 5 — Periodic Maintenance

| Cron ID | Script | Cadence | Purpose |
|---|---|---|---|
| `videshi-content-gap-audit` | Gap audit script | Daily | Check category freshness, flag gaps. |

### Crons to Retire

**All category writers** (videshi-writer-{food,travel,entertainment,immigration,news,tech,sports,nri-world,lifestyle,markets}) — replaced by rolling writer.

**Legacy ingest crons:**
- `videshi-ingest` (rss-ingest.py) — replaced by v2-ingest
- `videshi-pipeline` (legacy heartbeat) — replaced by discrete crons

**Duplicate/stale crons:**
- All `_archive/` definitions
- All duplicate ID definitions (some cron IDs appear 2-4 times with different cadences)
- `videshi-writer` (old unified writer, different from rolling-writer)
- `videshi-v2-writer` (was planned as Hatch/Claude-based writer, not needed — rolling writer handles it)

**Total retired: ~85 cron definitions.** The cron.d directory should go from ~100 files to ~15.

---

## 6. Monitoring & Health

### 6.1 Key Metrics

| Metric | Healthy Range | Alert Threshold |
|---|---|---|
| Signals ingested per run | 50-300 | < 10 signals = feed failure |
| Topics created per run | 20-100 | < 5 topics = clustering failure |
| Articles written per day | 40-70 | < 20 = writer down |
| Articles per category (trailing 24h) | ≥ 1 each | Any category at 0 for 12h+ |
| Image success rate | > 85% | < 70% = image chain broken |
| Reviewer promotion rate | > 60% | < 40% = writer quality dropping |
| Time from signal to published article | < 3h median | > 6h = pipeline stuck |

### 6.2 Health Check Script

`videshi-healthcheck` (every 2h) runs a simple dashboard query:

```sql
-- Articles per category, last 24h
SELECT category, count(*) FROM p2_articles
WHERE published_at > now() - interval '24 hours'
  AND status = 'published'
GROUP BY category;

-- Signals per source_type, last 6h (should be > 0 for each)
SELECT source_type, count(*) FROM p2_signals
WHERE fetched_at > now() - interval '6 hours'
GROUP BY source_type;

-- Unprocessed signals (should be < 100; if growing = clustering stuck)
SELECT count(*) FROM p2_signals WHERE is_processed = false;
```

If any category has 0 articles for 12+ hours or unprocessed signals exceed 500, report to main chat.

---

## 7. Migration Plan

### Phase 1: Code Changes (no production impact)

1. **Port clustering into v2-ingest.py.** Copy the clustering logic from `rss-ingest.py` lines 201-354 into v2-ingest.py as Step 5 after signal insertion. Test with `--dry-run`.

2. **Add category quotas to rolling-writer.py.** Implement the freshness check and stale-category backfill. Test with `--dry-run`.

3. **Insert new RSS feeds into `p2_feed_sources`.** 21 new feeds (food: 7, travel: 6, lifestyle-health: 6, entertainment: 2). Deactivate 4 tech vendor blogs.

4. **Update Google News queries in v2-ingest.py.** Replace Type B queries with diaspora-adjacent versions (already done in code, needs the food-specific query update).

### Phase 2: Cutover

5. **Run v2-ingest.py manually once.** Verify: signals inserted, topics created, categories distributed. Check that food/travel/lifestyle signals appear.

6. **Run rolling-writer.py manually once (no --dry-run).** Verify: articles written across categories including at least one food/travel/lifestyle. Check image sourcing works end-to-end.

7. **Enable v2-ingest cron** (30min interval). Start time: now.

8. **Enable rolling-writer cron** (60min interval). Start time: 30 min after v2-ingest (so there are topics ready).

9. **Enable article-reviewer cron** (2h interval).

10. **Disable legacy crons:**
    - `videshi-ingest` (rss-ingest.py)
    - `videshi-pipeline` (legacy heartbeat)
    - All `videshi-writer-*` category writers
    - `videshi-v2-writer`
    - `videshi-writer` (old unified)

### Phase 3: Cleanup (next day)

11. **Archive retired cron files** to `cron.d/_archive/`.
12. **Deduplicate remaining crons** — ensure each ID has exactly one definition file.
13. **Monitor for 24h.** Check: articles per category, image success rate, reviewer promotion rate.
14. **Git commit** all changes.

### Rollback Plan

If v2-ingest or rolling-writer fail in production:
1. Disable the failing cron.
2. Re-enable `videshi-ingest` (rss-ingest.py) — it still works, just doesn't have Google News or new feeds.
3. Re-enable `videshi-rolling-writer` with the old code (git stash the changes).
4. The writer doesn't need clustering — it reads from p2_topics, and rss-ingest.py creates topics.

The new feeds in p2_feed_sources are safe to leave active even during rollback — rss-ingest.py reads all active feeds.

---

## Appendix A: Current Cron Inventory (for cleanup reference)

The following cron IDs have multiple definition files and need deduplication:

- `videshi-article-reviewer` (3 files: 30min, 6h, 1h)
- `videshi-fb-autopost` (3 files: 3h, 6h, 12h)
- `videshi-ig-autopost` (2 files: 3h, 8h)
- `videshi-pipeline` (2 files: 30min, 3h)
- `videshi-writer-entertainment` (5 files: 2h, 6h, 8h, 6h, once)
- `videshi-writer-food` (3 files: 12h, 12h, once)
- `videshi-writer-news` (3 files: 2h, 8h, 6h)
- `videshi-writer-tech` (4 files: 3h, 6h, 8h, 6h)
- `videshi-writer-sports` (3 files: once, 3h, 8h)
- `videshi-writer-nri-world` (3 files: 12h, 6h, 8h)

These create unpredictable scheduling behavior — when two definitions share an ID, the scheduler may run either or both.

## Appendix B: File Inventory

**Keep and maintain:**
- `v2-ingest.py` — Unified ingest + clustering
- `rolling-writer.py` — Unified writer
- `image_sourcer.py` — Image sourcing module
- `review-articles.py` — Article reviewer
- `prebuild-feeds.py` — JSON feed builder
- `enrich-articles.py` — Article enricher (inline images, data cards)

**Archive (move to `_archive/`):**
- `rss-ingest.py` — Replaced by v2-ingest
- `google-news-ingest.py` — Replaced by v2-ingest
- `v2-select.py` — Was for V2 writer candidate selection, no longer needed

**Reference docs:**
- `PIPELINE-ARCHITECTURE.md` — This document
- `SOURCING-STRATEGY.md` — Superseded by this document but keep for historical context
- `IMAGE-SOURCING-RULES.md` — Detailed image rules (referenced by image_sourcer.py)
