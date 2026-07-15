# Pipeline V2 — Unified Rolling News Pipeline

## Design Document — July 15, 2026 (Revised)

### Core Principle

Hatch is the editor AND writer. GPT-4o-mini API is only used for bulk mechanical classification where parallelism matters. Everything that requires judgment — writing, review, editorial decisions — is Hatch.

### Division of Labor

| Who | Does what | Cost |
|-----|----------|------|
| **Hatch** | Article writing, quality review, editorial decisions, new-development detection, scoring/ranking | $0 |
| **GPT-4o-mini API** | Batch signal classification, diaspora yes/no gate, one-sentence summaries for embeddings | ~$2.25–2.75/day |
| **Local compute** | LSH dedup, SBERT embeddings, HDBSCAN clustering, spaCy NER, keyword pre-filter | $0 |

---

## Signal Sources (all feed into unified `p2_signals`)

### 1. RSS Feeds (existing, 79 feeds)
- Polled every 15-30 min
- `source_type: 'rss'`

### 2. Google News RSS (new, free, no API key)

**a) Topic Feeds** — Top Stories, Business, Tech, Sports, Entertainment, World, Science, Health
- 40-70 items per feed, heavily clustered by Google (5+ sources per story)
- US edition + India edition for dual perspective
- Good for: catching major stories our RSS feeds miss

**b) Search Queries** — 10-15 diaspora-focused keyword queries
- Up to 100 items per query, no clustering
- Operators: exact phrases, OR, exclusion, geo editions
- Queries: H-1B/visa/green card, "Indian American", NRI/diaspora, Indian tech CEO, India-US trade, Bollywood international, USCIS, Indian startup, etc.

### 3. GDELT DOC API (new, free)
- Global news database, 100+ languages, updates every 15 min
- Up to 250 articles per query
- Gap-filler for stories not in RSS or Google News
- Diaspora-relevant queries run every 30-60 min

### 4. Email Newsletters (existing, rewired)
- Currently bypasses `p2_signals` — rewire to go through unified pool
- `source_type: 'newsletter'`
- USCIS, Boundless, NVIDIA, a16z, Qualcomm, MPI, CIS

### 5. Press Releases (future)
- PR Newswire, GlobeNewswire, Business Wire RSS filtered for India/diaspora
- `source_type: 'press_release'`

---

## Pipeline Architecture — One Rolling Loop

Runs every 30 minutes via single cron. Each phase is idempotent.

```
PHASE 1: INGEST (~30 sec, parallel fetches)
├── Fetch all RSS feeds (79)
├── Fetch Google News topic feeds (8 categories × 2 geo editions)
├── Fetch Google News search queries (10-15 queries)
├── Read pending email_signals
├── Fetch GDELT DOC API (diaspora queries)
└── All → p2_signals (with source_type tag)

PHASE 2: DEDUP (~10 sec, zero LLM cost)
├── URL normalization (strip tracking params, canonicalize)
├── Title normalization (strip publisher, lowercase, remove punctuation)
├── LSH/MinHash on title+snippet (>80% similarity = duplicate)
├── Cluster propagation (dup of already-clustered signal → inherit cluster)
└── Result: only unique signals pass through (60-80% filtered out)

PHASE 3: ENRICH (~15 sec, small GPT cost)
├── Full article extraction (newspaper3k) for signals worth enriching
├── One-sentence summary via GPT-4o-mini (batched, 20-30 per call)
├── NER extraction via spaCy (local, free)
├── Sentence embedding via SBERT all-MiniLM-L6-v2 (local, free)
└── Store embeddings in pgvector (Supabase native)

PHASE 4: DIASPORA GATE (~10 sec, small GPT cost)
├── Keyword pre-filter: auto-pass/reject on strong matches (40-60% handled, $0)
├── GPT-4o-mini binary yes/no on remaining signals (batched)
└── Result: only diaspora-relevant signals pass through

PHASE 5: CLUSTER (zero cost, local compute)
├── HDBSCAN on 3-signal distance matrix:
│   ├── Semantic distance (cosine similarity of SBERT embeddings) — weight 0.4
│   ├── Entity distance (Jaccard similarity of NER entities) — weight 0.4
│   └── Time distance (normalized time gap, 0-3 day window) — weight 0.2
├── 3-day rolling window
├── Match clusters against existing p2_topics
└── Match against already-published articles

PHASE 6: EDITORIAL DECISIONS (Hatch, $0)
├── For new topics: Is this worth covering? What angle?
├── For covered topics with new signals: New information or just echoes?
│   ├── New info → mark as DEVELOPING, write follow-up
│   └── Same facts → mark as SATURATED, skip
├── Priority ranking (cluster size + source authority + recency + diaspora strength)
├── Category balance check
└── Select top 2-3 articles to write this cycle

PHASE 7: WRITE (Hatch, $0)
├── Hatch writes articles directly from clustered source material
├── Source-grounded: only facts from source excerpts, cited inline
├── Diaspora angle baked in
├── Hero image sourcing (Wikipedia/Pexels/Commons)
└── Insert into Supabase with status="review" or "published"

PHASE 8: QA + PUBLISH (Hatch, $0)
├── Quality review (Hatch checks facts, sources, tone)
├── Score for ranking (display_score computation)
├── Rebuild feeds → commit → Vercel deploys
└── Live

Total cycle: ~5-8 minutes
Runs every: 30 minutes
Signal to live: ONE cycle (was 3-4 hours)
```

---

## Topic Lifecycle

Topics are not one-shot. They evolve:

```
EMERGING → COVERED → DEVELOPING → SATURATED
```

- **EMERGING**: New signals arriving, no article yet. Accumulate or write immediately if urgent.
- **COVERED**: Article published. Topic stays open. New signals checked for new info.
- **DEVELOPING**: Genuinely new information on a covered topic. Follow-up warranted.
- **SATURATED**: Thoroughly covered, new signals are just echoes. Stop writing.

Hatch manages these transitions — same judgment a human editor would make.

---

## Schema Changes

### p2_signals (add columns)
```sql
source_type      TEXT     -- 'rss', 'google_news', 'newsletter', 'press_release', 'gdelt'
google_cluster   INT      -- cluster size from Google News topic feeds
story_id         TEXT     -- canonical story identifier (from clustering)
entities         TEXT[]   -- NER-extracted entities
diaspora_relevant BOOL   -- binary gate result
embedding        vector(384) -- SBERT embedding (pgvector)
```

### p2_topics (add columns)
```sql
lifecycle        TEXT     -- 'emerging', 'covered', 'developing', 'saturated'
last_article_id  UUID     -- most recent published article on this topic
last_article_at  TIMESTAMPTZ
new_info_summary TEXT     -- what's new since last article
source_types     TEXT[]   -- which source types contributed
cluster_size     INT      -- total signals across all sources
```

---

## Cost Summary

| Component | Daily cost |
|-----------|-----------|
| GPT-4o-mini: signal classification + diaspora gate | ~$1.50–2.00 |
| GPT-4o-mini: one-sentence summaries (batched) | ~$0.50 |
| GPT-4o-mini: new-dev detection on edge cases | ~$0.25 |
| Hatch: writing, review, scoring, editorial | $0 |
| Local: dedup, embeddings, clustering, NER | $0 |
| Google News RSS, GDELT | $0 |
| **Total** | **~$2.25–2.75/day** |

Down from ~$5-6/day. ~50% cost reduction while adding more signal sources and smarter clustering.

---

## Migration Plan (incremental, current pipeline keeps running)

### Step 1: Google News + GDELT ingest
- Add as new signal sources into existing p2_signals
- Validate signal quality, measure gap-fill vs RSS
- No disruption to current pipeline

### Step 2: Better dedup + clustering
- Add LSH/MinHash, SBERT embeddings, spaCy NER
- Enable pgvector in Supabase
- HDBSCAN clustering replaces keyword-overlap
- Run in shadow mode alongside current clustering, compare results

### Step 3: Topic lifecycle
- Add lifecycle columns to p2_topics
- Implement EMERGING → COVERED → DEVELOPING → SATURATED
- Hatch handles new-development detection

### Step 4: Unify into rolling pipeline
- Collapse ingest + write + review + score + sync into one script
- Hatch writes articles directly (replaces GPT-4o-mini writer)
- Hatch does QA (replaces GPT-4o-mini reviewer)
- Single cron every 30 min replaces 10+ separate crons
- Retire old crons

---

## Open Questions

1. **Cycle frequency**: 30 min? 15 min? Tradeoff between freshness and Hatch compute time.
2. **Google News self-rate-limit**: How aggressive can we poll without getting blocked?
3. **Article updates vs follow-ups**: When new info arrives, update existing article in-place or publish new follow-up?
4. **How many articles per cycle**: 2-3 per 30-min run = 96-144/day capacity. Enough?
5. **GDELT reliability**: Need to test DOC API from this environment (proxy/egress).
