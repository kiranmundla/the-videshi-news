# The Videshi Pipeline — Current State Analysis (2026-07-08)

## Pipeline Architecture

### Data Flow
```
RSS Feeds (23 sources) → p2_signals (103K+ total) → p2_topics (clustered) → Writer Scripts → p2_articles → Review Gate → Published
```

### Feed Sources (23 active, stored in `p2_feed_sources`)
**Tier A (18 sources):** American Bazaar, Business Standard, Economic Times, Hindustan Times, India Today, Indian Express, LiveMint, NDTV Top Stories, New India Abroad, PIB Press Releases, RBI Press Releases, SEBI RSS, The Hindu, The Print, The Wire, Times of India, TOI NRI Section, USCIS News (scrape)

**Tier B (5 sources):** BBC India, Desi Bulletin, ET Tech, Indian Eagle News, NRI Pulse

**Verticals covered:** politics, economy, tech, culture, diaspora, immigration, science, entertainment, sports

---

## Last 7 Days Article Production (Jul 1–8, 2026)

### Total Published: **485 articles** (~69/day avg)

#### Daily Breakdown
| Date | Published |
|------|-----------|
| Jul 8 (today, partial) | 31 |
| Jul 7 | 46 |
| Jul 6 | 41 |
| Jul 5 | 40 |
| Jul 4 | 43 |
| Jul 3 | 128 |
| Jul 2 | 126 |
| Jul 1 | 30 |

**Notable:** Jul 2–3 had 2–3× normal volume (126–128/day), while Jul 1 and Jul 4–8 are at 30–46/day. Likely a batch catch-up or writer burst on Jul 2–3.

### Category Distribution (Last 7 Days)
| Category | Articles | % Share | Avg Review Score |
|----------|----------|---------|------------------|
| technology | 86 | 17.7% | 79.6 |
| news | 79 | 16.3% | 0.0* |
| entertainment | 72 | 14.8% | 0.0* |
| immigration | 68 | 14.0% | 81.7 |
| travel | 49 | 10.1% | 77.1 |
| sports | 36 | 7.4% | 2.2 |
| nri-world | 31 | 6.4% | 69.3 |
| food | 24 | 4.9% | 75.9 |
| lifestyle-health | 21 | 4.3% | 0.0* |
| markets-finance | 19 | 3.9% | 0.0* |

*Score 0.0 = review scores not populated for those categories (likely bypassing or using different review path).

### Article Pipeline Funnel (Last 7 Days)
| Status | Count |
|--------|-------|
| published | 485 |
| draft | 8 |
| review | 2 |
| archived | 1 |

Very high publish rate (97.8%) — almost everything created gets published.

---

## 30-Day Category Distribution (for trend comparison)
| Category | 30-Day | 7-Day | Trend |
|----------|--------|-------|-------|
| news | 635 | 79 | Stable core |
| technology | 592 | 86 | ↑ Elevated recently |
| entertainment | 502 | 72 | Stable |
| travel | 407 | 49 | Slight dip |
| immigration | 368 | 68 | Stable/strong |
| sports | 306 | 36 | Stable |
| lifestyle-health | 274 | 21 | ↓ Down from ~9/day to ~3/day |
| nri-world | 253 | 31 | Stable |
| markets-finance | 152 | 19 | Stable |
| food | 135 | 24 | ↑ Up from ~4.5/day to ~3.4/day (normalish) |

**30-day total: ~3,624 published articles (~121/day avg)**

---

## Signal Ingestion
- **Total signals ingested (all time):** 103,583
- **Last 7 days:** 9,564 signals (~1,366/day)
- **Conversion rate:** 485 published / 9,564 signals ≈ **5.1%** signal-to-article conversion

### Topic Clustering (Last 7 Days)
| Category | Vertical | Topics |
|----------|----------|--------|
| news | politics | 8,082 |
| technology | tech | 620 |
| entertainment | entertainment | 238 |
| markets-finance | economy | 175 |
| lifestyle-health | culture | 154 |
| sports | sports | 130 |
| nri-world | diaspora | 52 |

**Note:** news/politics dominates the topic signal space (85%+), but the writers distribute output more evenly across categories.

---

## Automated Pipeline (Cron Jobs)

### Content Writers (9 category-specific)
| Writer | Cadence | Category |
|--------|---------|----------|
| immigration | every 6h | immigration |
| news | every 8h | news |
| tech | every 8h | technology |
| entertainment | every 8h | entertainment |
| sports | daily 08:00 | sports |
| lifestyle | daily 09:00 | lifestyle-health |
| travel | daily 10:00 | travel |
| food | daily 11:00 | food |
| nri-world | every 12h | nri-world |

### Pipeline Infrastructure
| Job | Cadence | Purpose |
|-----|---------|---------|
| videshi-ingest | every 1h | RSS feed ingestion |
| videshi-live | every 1h | Live/breaking news |
| videshi-article-reviewer | every 30m | Review gate (GPT/Gemini QA) |
| videshi-json-sync | every 10m | Sync to static JSON |
| videshi-ping-google | every 3h | Google indexing |
| article-enricher | every 6h | Social embeds, data cards |
| videshi-enrich-data-cards | every 3h | Data card enrichment |
| videshi-dedupe-body-images | every 3h | Image deduplication |
| videshi-healthcheck | every 2h | Site monitoring |
| videshi-site-monitor | every 6h | Site health |

### Distribution
| Job | Cadence | Platform |
|-----|---------|----------|
| videshi-x-autopost | every 6h | X/Twitter |
| videshi-distribute-reels | every 6h | IG/YT/Threads/X reels |
| videshi-reel-pipeline | every 8h | Reel build (Shotstack) |
| videshi-newsletter-daily | daily 07:00 | Email newsletter |
| videshi-newsletter (weekly) | Sun 07:00 | Weekly digest |

### Supporting Jobs
| Job | Cadence | Purpose |
|-----|---------|---------|
| videshi-visa-alerts | every 30m | Visa wait time alerts |
| videshi-visa-updates | daily 08:00 | Visa data refresh |
| videshi-wait-times | daily 06:00 | Consulate wait times |
| videshi-events | every 12h | Events ingestion |
| celebrity-buzz-refresh | every 6h | Celebrity content |
| videshi-media-library-source | daily 03:30 | Media library |
| videshi-morning-credential-check | daily 06:30 | API key validation |
| worldcup-scores | every 2h | World Cup live scores |
| worldcup-recap | daily 23:45 | Match recaps |

---

## Reels Pipeline
- **Total reels built:** 82 (79 QA passed, 3 failed)
- **Build cadence:** every 8h via Shotstack
- **Distribution:** every 6h to IG/YT/Threads/X

---

## Key Observations

1. **Heavy automation:** 47+ active cron jobs, 9 category writers, all running unattended.
2. **Volume is high:** ~69 articles/day (7-day), ~121 articles/day (30-day). The 30-day number is inflated by batch catch-ups.
3. **Immigration dominance in quality:** immigration articles score highest (81.7 avg) despite many categories having no scores populated.
4. **Lifestyle-health declining:** dropped from ~9/day (30-day avg) to ~3/day recently.
5. **Signal oversupply:** 9,564 signals → 485 articles = 5% conversion. News/politics signals are 85%+ of intake but only 16% of output — writers are correctly diversifying.
6. **markets-finance is the smallest vertical** at 3.9% of output despite having dedicated writer + market charts infrastructure.
7. **No dedicated RSS feeds for entertainment, sports, food, or travel** — these categories are generated from general news feeds or specialized writer prompts.
