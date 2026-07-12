# Homepage Article Ranking — Research & Recommendation

## How Major News Sites Rank Articles

### Google News (Algorithmic)
Google's own documentation lists these ranking factors:
1. **Prominence** — How many outlets are covering it. Story clusters (groups of articles about the same event) form automatically; the more sources in a cluster, the higher it ranks.
2. **Freshness** — Newer articles prioritized for time-sensitive topics.
3. **Authoritativeness** — Source credibility, ownership transparency, editorial standards.
4. **Relevance** — Alignment with user interests/query.
5. **Location** — Geographic relevance to the user.
6. **Usability** — Page speed, mobile-friendliness.

Key insight: Google News creates **story clusters** — individual articles get grouped by event. A story covered by 50 outlets ranks higher than one covered by 2, regardless of publication time. This is their strongest signal for "importance."

### Apple News (Human + Algorithm Hybrid)
- **Top Stories**: Selected by a team of ~30 human editors (former journalists in NY, London, Sydney, Silicon Valley). They review 100-200 publisher pitches/day and select 5 leading stories, changing 5+ times/day.
- **Trending**: Algorithmically curated — research showed this skews toward celebrity/entertainment, while human-curated Top Stories featured more policy, international news.
- **For You**: Machine learning based on reading history, likes, saves.

Key insight: Apple found that **pure algorithmic curation skewed toward soft news and celebrity content**. Human editorial judgment was needed to surface policy, international affairs, and serious news. For an automated site, the LLM needs to replicate this editorial judgment.

### NDTV
- **Featured** banner position (editorial pick, biggest headline+image)
- Below that: "More News" in reverse-chronological order with editorial bumps
- Videos section prominent
- Breaking news overrides everything via a red banner

### BBC News
- Big hero with lead story
- "Most Read" sidebar (engagement-driven)
- Editorially curated section ordering
- Breaking news banner overrides normal hierarchy

### The Guardian
- Giant hero image for lead story
- "Headlines" section (editorial picks)
- "Most viewed" sidebar (engagement data)
- Live blogs pinned high for developing stories

### Common Patterns Across All Sites

| Signal | Used By | Weight |
|--------|---------|--------|
| Editorial judgment / importance | All | Highest |
| Recency (with decay) | All | High |
| Prominence (source count) | Google, Facebook | High |
| Engagement (clicks, shares) | BBC, Guardian, Reddit | Medium |
| Breaking news override | All | Override |
| Category balance | Most | Layout-level |
| Visual quality (hero image) | All | For hero selection |

---

## The Core Problem for The Videshi

Our current system: `ORDER BY published_at DESC` with a static `score_total` set by the writer at insert time (usually 78-85 for all articles). This means:

- A routine "Indian banks offer NRI 7% deposits" article posted at 10:30 AM sits above "World Cup semifinal showdown" posted at 10:00 AM
- Yesterday's massive breaking story disappears below today's filler
- There's no way to distinguish a senator's death from a lifestyle feature

We need: **Automatic newsworthiness scoring that surfaces major stories without human editors.**

---

## Proposed Ranking System

### Score Formula

```
display_score = newsworthiness + prominence + diaspora_impact + freshness_bonus
```

Each component is scored by GPT-4o-mini at article creation time:

#### 1. Newsworthiness (0-35 points)
How "big" is this story on a global/national news scale?

| Score | Level | Examples |
|-------|-------|---------|
| 30-35 | Historic/Breaking | Head of state death, major terror attack, war declaration, World Cup final |
| 25-29 | Major | Senator death, World Cup semifinal, major policy reversal, market crash |
| 18-24 | Significant | Cabinet reshuffle, major company layoff, tournament quarterfinal |
| 10-17 | Standard | Policy update, earnings report, routine diplomatic meeting |
| 1-9 | Feature/Soft | Lifestyle piece, food review, travel guide, opinion column |

#### 2. Prominence (0-25 points)
How widely is this story being covered? Computed from `p2_topics` — count how many distinct RSS feed sources have related topics.

| Score | Sources Covering It |
|-------|-------------------|
| 20-25 | 8+ feeds have related topics (massive story) |
| 15-19 | 5-7 feeds (widely covered) |
| 10-14 | 3-4 feeds (moderately covered) |
| 5-9 | 1-2 feeds (single-source or niche) |

#### 3. Diaspora Impact (0-20 points)
How directly does this affect NRIs in US/UK/Canada?

| Score | Impact Level |
|-------|-------------|
| 18-20 | Direct NRI impact: visa policy change, immigration rule, NRI tax law |
| 13-17 | Strong diaspora angle: Indian-origin achievement, bilateral policy |
| 8-12 | Moderate: India economy, Bollywood major release, cricket international |
| 3-7 | Tangential: General world news, domestic Indian politics |

#### 4. Freshness Bonus (0-20 points)
Time-decaying bonus that ensures today's news beats yesterday's.

```
freshness = 20 × max(0, 1 - (hours_since_publish / 36))
```

- Just published: +20
- 6 hours old: +16.7
- 12 hours old: +13.3
- 18 hours old: +10
- 24 hours old: +6.7
- 36+ hours old: +0

### Example Scores

| Article | News | Prom | Diasp | Fresh | Total |
|---------|------|------|-------|-------|-------|
| "Lindsey Graham dies at 70" (just published, 10 feeds) | 28 | 22 | 7 | 20 | **77** |
| "World Cup: England vs Argentina semifinal preview" (2h old, 8 feeds) | 27 | 20 | 12 | 18.9 | **77.9** |
| "H-1B visa fee hike takes effect today" (1h old, 6 feeds) | 22 | 17 | 20 | 19.4 | **78.4** |
| "Indian banks offer NRIs 7% on deposits" (3h old, 2 feeds) | 14 | 7 | 18 | 18.3 | **57.3** |
| "Bollywood: Dhamaal 4 box office collection Day 3" (6h old, 3 feeds) | 8 | 10 | 10 | 16.7 | **44.7** |
| Same H-1B article after 24h | 22 | 17 | 20 | 6.7 | **65.7** |
| Same Graham article after 24h | 28 | 22 | 7 | 6.7 | **63.7** |

Result: Breaking news and immigration headlines surface to hero position. After 24h they naturally decay below fresh important stories.

### Breaking News Override
If `newsworthiness >= 28` AND `hours_since_publish < 6`, the article gets an additional +15 "breaking" bonus, making it virtually guaranteed hero.

---

## Implementation Plan

### Step 1: LLM Scoring at Article Creation
In each writer script, after the article is generated, add a GPT-4o-mini call:

```
Score this article for a news homepage ranking:
Headline: {headline}
Category: {category}
Body (first 500 words): {body[:500]}

Return JSON: {
  "newsworthiness": 1-35 (how major is this story globally/nationally?),
  "diaspora_impact": 1-20 (how directly does this affect NRIs in US/UK/Canada?),
  "reasoning": "one sentence explaining the scores"
}
```

Write `newsworthiness` and `diaspora_impact` to new DB columns.

### Step 2: Prominence Score (Computed)
Run a lightweight function that counts how many distinct `p2_topics` entries share keywords with the article. This can run at article creation or periodically.

### Step 3: Freshness Decay (Computed at Read Time)
`freshness = 20 × max(0, 1 - (hours_since_publish / 36))`

Computed in the feed builder or frontend, not stored.

### Step 4: Display Score
```sql
display_score = COALESCE(newsworthiness, 15)
              + COALESCE(prominence, 8)
              + COALESCE(diaspora_impact, 10)
              + (20 * GREATEST(0, 1 - EXTRACT(EPOCH FROM (NOW() - published_at)) / 129600))
```

### Step 5: Hero Selection
```sql
SELECT * FROM p2_articles
WHERE status = 'published'
  AND image_url IS NOT NULL
  AND published_at > NOW() - INTERVAL '24 hours'
ORDER BY display_score DESC
LIMIT 1
```

### Step 6: Category Strips
Each category strip still shows its own articles, but sorted by display_score within the category.

---

## DB Changes Needed

```sql
ALTER TABLE p2_articles ADD COLUMN IF NOT EXISTS newsworthiness INTEGER;
ALTER TABLE p2_articles ADD COLUMN IF NOT EXISTS diaspora_impact INTEGER;
ALTER TABLE p2_articles ADD COLUMN IF NOT EXISTS prominence INTEGER;
```

## Migration
Backfill existing articles: run a batch GPT-4o-mini scoring job on the last 7 days of published articles (only ~400-500 articles). Older articles keep their current score_total as a fallback.
