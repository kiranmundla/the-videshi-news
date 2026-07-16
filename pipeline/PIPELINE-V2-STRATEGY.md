# The Videshi V2 Pipeline — Strategy Proposal

**Date:** July 16, 2026  
**Status:** Draft for review

---

## The Problem

The V2 pipeline launched with systemic gaps that should have been caught during research:

1. **No image verification** — Articles publish with Wikipedia URLs that may 404, SVG thumbnails, or logos instead of photos. No check before the image goes to the hero slot.
2. **No signal sources for 3 categories** — Food, Travel, and Lifestyle have zero RSS feeds and zero Google News queries. They run on whatever leftover signals get categorized there.
3. **CDN serves stale data** — The homepage reads a static JSON file deployed through git. Updates take 5+ minutes to propagate, and Vercel's edge cache can serve stale data indefinitely.
4. **No category floor in article selection** — The selector picks highest-scoring stories with a max of 3 per category, but no minimum. Thin categories get zero picks every time.
5. **No editorial curation layer** — The sidebar/editorial slot requires `is_editorial=true`, which is never set. The sidebar shows whatever the frontend falls back to.

These aren't edge cases. They're the basics of running a news site.

---

## Signal Sourcing Strategy

### Current approach
- RSS feeds (49 active, but concentrated in tech/immigration/news)
- Google News: 7 topic feeds × 2 geos + 12 keyword searches
- **Zero feeds for: food, travel, lifestyle**
- Entertainment: 8 RSS feeds (not recently fetched) + 1 Google News search

### Proposed: Three-Layer Signal Ingestion

**Layer 1: Broad Google News Category Scanning** (NEW — Kiran's direction)

Scan Google News topic feeds for ALL categories, not just keyword searches:
- Business → Markets/Finance
- Technology → Technology
- Entertainment → Entertainment
- Sports → Sports
- Science → Technology/News
- Health → Lifestyle/Health
- World → News/NRI World
- Nation (India geo) → News

For each feed: ingest ALL stories, then run a **post-ingestion diaspora relevance filter** (not pre-filter). This is the key shift — cast a wide net, then score for relevance.

**Layer 2: Targeted Diaspora Searches** (existing, improved)
Keep keyword searches for diaspora-specific stories that broad category feeds won't catch:
- Immigration-specific queries (H-1B, green card, OPT, USCIS, etc.)
- "Indian diaspora", "NRI", "Indian American" + category terms
- Add: "Indian restaurant", "Indian food", "Bollywood", "Indian travel", "India tourism"

**Layer 3: RSS Feeds** (existing, expanded)

Add feeds for the starving categories:

| Category | New Feeds to Add |
|---|---|
| Food | Eater, Bon Appétit, Serious Eats, NDTV Food, IndianHealthyRecipes |
| Travel | Condé Nast Traveler, Lonely Planet India, Travel+Leisure, India Today Travel |
| Lifestyle | HuffPost Life, Times of India Lifestyle, Health.com |
| Entertainment | Screen Rant, Collider, Pinkvilla, BollywoodLife |

---

## Article Selection Strategy

### Current
- Score by: cluster_size × 15 + source_diversity × 12 + recency + diaspora_boost
- Max 3 per category, no minimum
- Result: immigration/tech/news dominate; food/travel/lifestyle get 0

### Proposed: Category-Balanced Selection

1. **Category floor**: Guarantee **at least 1 article per active category** if signals exist
2. **Category ceiling**: Keep max 3 per category  
3. **Fill remaining slots** by raw score across all categories
4. **Separate food/travel/lifestyle** — currently lumped into a single "lifestyle" bucket in category keywords; split them

Selection priority order:
1. Fill the floor (1 per category, highest scored)
2. Fill remaining budget with top-scoring across all categories (respecting ceiling)

---

## Image Sourcing Strategy

### Current
The V2 writer grabs Wikipedia URLs without verification. SVG logos get picked as hero images. No fallback chain.

### Proposed: Verified Image Pipeline

Every article gets an image through this chain. Each step verifies the URL returns HTTP 200 before accepting:

1. **Source article's own image** — if the original source has an `og:image` or article image, prefer that (with rights check)
2. **Wikipedia REST API** — `GET /api/rest_v1/page/summary/{entity}` → use `originalimage.source` for JPGs, `thumbnail.source` for non-SVGs. **Reject SVGs and logos.**
3. **Wikimedia Commons** — search for relevant photos. Apply the existing `commons_relevance_ok()` gate.
4. **Pexels API** — free stock photos, good quality, clear licensing
5. **No image** — if nothing works, publish without a hero image rather than a broken one

**Verification gate**: Before publishing, `curl -s -o /dev/null -w '%{http_code}'` the final URL. If not 200, move to next source or publish without image.

**Hero image quality rules**:
- Must be a photograph (reject SVGs, logos, seals, flags unless the article is about that specific symbol)
- Must be ≥600px wide
- Must be relevant to the article subject (not just a keyword match)

---

## Feed & Deploy Strategy

### Current
`prebuild-feeds.py` builds a static JSON file → committed to git → Vercel deploys. Updates take 5-15 minutes to reach users.

### Proposed: Two changes

**Immediate fix (done):** Cache-bust all static JSON fetches with `?v=Date.now()` so the browser always gets the latest version from the CDN, not a stale cached copy.

**Next step:** The homepage already falls back to direct Supabase queries when the static feed fails. Consider making direct Supabase the primary path for the most time-sensitive sections (Just In, Featured), keeping the static feed as a fast CDN cache for category sections that don't need sub-minute freshness.

---

## Quality Gates

What should be automatically verified before an article goes live:

| Check | What | Action on Fail |
|---|---|---|
| **Hero image loads** | HTTP GET returns 200 | Don't publish; try next image source |
| **No duplicate** | Slug + headline similarity check | Skip article |
| **Category assigned** | Must map to a valid homepage section | Flag for manual review |
| **Body length** | Minimum 200 words | Flag as stub |
| **Headline length** | 10-120 characters | Truncate or flag |
| **Diaspora angle** | Body mentions diaspora/NRI/Indian relevance | Pass-through (not all articles need explicit angle) |

---

## Implementation Plan

### Phase 1: Fix what's broken NOW (today)
- [x] Fix broken hero image URLs in DB
- [x] Cache-bust static JSON fetches
- [x] Expand Just In from 8 to 15 articles
- [ ] Deploy and verify CDN serves fresh data

### Phase 2: Signal source expansion (next 2-3 days)
- Add RSS feeds for food, travel, lifestyle, entertainment
- Add broad Google News category scanning (all topics, both geos)
- Add post-ingestion diaspora relevance filter
- Implement category floor (min 1 per category) in selector

### Phase 3: Image pipeline (next 3-5 days)
- Build verified image sourcing chain (source → Wikipedia → Commons → Pexels)
- Add image URL verification before publish
- Reject SVGs/logos/non-photos for hero slots
- Backfill missing images on existing articles

### Phase 4: Quality and freshness (next week)
- Add pre-publish quality gates
- Consider direct Supabase for time-sensitive homepage sections
- Editorial curation tooling (easy way to mark articles as featured/editorial)
- Category page freshness monitoring

---

## Cost Impact

- Google News scanning: **$0** (public RSS feeds)
- New RSS feeds: **$0**
- Pexels API: **$0** (free tier, 200 requests/hour)
- Diaspora relevance filter: GPT-4o-mini, ~$0.50/day for 200 signals
- Image verification: `curl` calls, **$0**

Total incremental cost: **~$0.50/day**

---

## What This Fixes

| Issue | Before | After |
|---|---|---|
| Broken hero images | Published with unverified URLs | Every image verified before publish |
| Food/Travel/Lifestyle | 3 articles each, no signal sources | Dedicated RSS feeds + Google News |
| Stale homepage | CDN cache serves old data 15+ min | Cache-bust ensures fresh data on load |
| Category imbalance | Top categories dominate, thin ones empty | Floor ensures every category represented |
| Image quality | SVG logos in hero slots | Photo-only, min 600px, relevance check |

---

*Ready for Kiran's review. No changes deployed until approved.*
