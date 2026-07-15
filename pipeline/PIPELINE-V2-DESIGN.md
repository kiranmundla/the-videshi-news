# Pipeline V2 — Unified Rolling News Pipeline

## Design Document — July 15, 2026

### Problem

The current pipeline is fragmented: separate crons for ingest (RSS), email newsletters, writing, reviewing, scoring, and feed sync — each running independently on hourly cycles. Stories take 3-4 hours from signal to live. Signal sources don't talk to each other. Dedup is mechanical (keyword overlap), can't distinguish "same story, different outlet" from "same topic, new development." Important stories get missed because they're not in our 79 RSS feeds.

### North Star

A single rolling pipeline that acts like an intelligent editor:
- Sees everything (RSS + Google News + newsletters + press releases)
- Recognizes what's the same story vs. genuinely new information  
- Makes editorial judgments about what our readers need to see
- Gets stories live in one cycle, not four

---

## Signal Sources

All sources feed into one unified pool: `p2_signals`

### 1. RSS Feeds (existing, 79 feeds)
- Polled hourly
- Each item = one signal with `source_type: 'rss'`
- Source quality varies: Tier A (Reuters, BBC) vs Tier B (blogs)

### 2. Google News RSS (new)
Two modes, both free, no API key:

**a) Topic Feeds** — pre-built categories (Top Stories, Business, Tech, Sports, etc.)
- ~40-70 items per feed, **heavily clustered** (Google groups related articles)
- Cluster size = instant signal strength (5+ sources = major story)
- Good for: catching major stories we missed, understanding story magnitude
- US edition + India edition for dual perspective

**b) Search Queries** — keyword-based, diaspora-focused
- Up to 100 items per query, no clustering
- Operators: exact phrases, OR/exclusion, geo edition
- Good for: niche diaspora stories (H-1B, NRI investment, Indian American achievements)
- ~10-15 targeted queries covering our core beats

**Query list (initial):**
```
"H-1B visa" OR "green card India" OR "EB-2" OR "OPT"
"Indian American" OR "Indian origin"
"NRI" OR "Indian diaspora" OR "non-resident Indian"
Indian tech CEO OR "Indian origin" CEO
India US trade OR India UK trade
Bollywood US release OR Indian film international
India cricket OR "Indian Premier League"
USCIS OR "immigration India"
"hate crime" Indian OR "Indian student" abroad
Indian startup unicorn OR "Indian founder"
```

### 3. Email Newsletters (existing, needs rewiring)
- Currently: gmail-scanner → email_signals → email-signal-ingest → p2_topics (bypasses p2_signals)
- Change: email-signal-ingest writes to `p2_signals` with `source_type: 'newsletter'`
- Sources: USCIS, Boundless, NVIDIA, a16z, Qualcomm, MPI, CIS newsletters

### 4. Press Releases (future)
- PR Newswire, GlobeNewswire, Business Wire RSS feeds filtered for India/diaspora keywords
- `source_type: 'press_release'`

### 5. Social/X (future, when credits available)
- Trending topics mentioning India/diaspora
- `source_type: 'social'`

---

## The Intelligent Decisions (where GPT comes in)

### Decision 1: Signal Triage — "What is this about?"

**When:** Every new signal arrives  
**Input:** Signal title + snippet + source  
**GPT decides:**
- **Entity extraction**: Who/what is this about? (e.g., "Anil Menon", "H-1B", "SpaceX")
- **Story ID**: A canonical story identifier (e.g., "anil-menon-iss-launch-2026-07")
- **Category**: immigration / technology / markets-finance / entertainment / sports / news / nri-world
- **Diaspora relevant?** Yes/No (binary gate — no 1-10 scale)
- **Story stage**: breaking / developing / background / opinion

This replaces the mechanical keyword-overlap clustering. GPT understands that "Menon reaches ISS" and "Indian astronaut docks at space station" are the same story, even with zero keyword overlap.

**Cost control:** Use GPT-4o-mini. Batch signals — send 20-30 at once, not one-by-one. ~$0.01-0.02 per batch.

### Decision 2: Topic Intelligence — "Should we cover this?"

**When:** After clustering, for each topic  
**Input:** Topic with all its signals, our recent published articles  
**GPT decides:**

For **new topics** (no published article):
- **Newsworthiness** (1-10): How important right now?
- **Cover?** Yes/No based on: newsworthiness + diaspora relevance + signal strength
- **Urgency**: Write now vs. wait for more signals
- **Angle**: What's the diaspora angle for this story?

For **existing topics** (already published):
- **New information?** Does this signal add materially new facts beyond what we published?
  - "Menon launches" → published ✓ → "Menon arrives at ISS" → YES, new development
  - "Menon launches" → published ✓ → "Another outlet reports Menon launched" → NO, same facts
- **Update or follow-up?** If new info, should we update the existing article or write a follow-up?
- **What changed?** One-line summary of the new development

### Decision 3: Editorial Prioritization — "What do we write next?"

**When:** After all signals are triaged and topics scored  
**Input:** All eligible topics with scores, current site state, recent articles  
**GPT decides:**
- **Top N to write** (considering category diversity, recency, reader value)
- **Story angle** for each (the diaspora-specific lens)
- **Priority order** (breaking first, then developing, then features)
- **What NOT to write** and why (too similar to recent article, low value, wait for more info)

This is the "editor's meeting" — one intelligent pass that looks at the full picture, not individual threshold checks.

---

## Topic Lifecycle

Topics are not one-shot. They have a lifecycle:

```
EMERGING → COVERED → DEVELOPING → SATURATED
```

- **EMERGING**: New signals coming in, no article published yet. Accumulate signals, wait for strength OR write immediately if high-urgency.
- **COVERED**: Article published. Topic stays open. New signals are checked for "new info?"
- **DEVELOPING**: New material information arrives on a covered topic. Follow-up article warranted.
- **SATURATED**: Topic has been covered thoroughly, new signals are just echoes. Stop writing.

GPT manages these transitions. A human editor would naturally do this — "we already covered the launch, but the ISS arrival is new, write a follow-up. The third article about the same launch from a different outlet? Skip."

---

## Rolling Pipeline Architecture

One script, one loop, runs every 30 minutes:

```
┌─────────────────────────────────────────────────┐
│  PHASE 1: INGEST (parallel, ~30 sec)            │
│  ├─ Fetch all 79 RSS feeds                      │
│  ├─ Fetch 8 Google News topic feeds              │
│  ├─ Fetch 10-15 Google News search queries       │
│  ├─ Read pending email_signals                   │
│  └─ All → p2_signals (with source_type tag)      │
│                                                  │
│  PHASE 2: TRIAGE (GPT batch, ~15 sec)           │
│  ├─ New signals → GPT: entity, story ID,         │
│  │   category, diaspora Y/N, stage               │
│  ├─ Cluster by story ID                          │
│  ├─ Match against existing topics + published    │
│  │   articles                                    │
│  └─ Result: new topics, updated topics,          │
│     developing stories                           │
│                                                  │
│  PHASE 3: EDITORIAL (GPT, ~10 sec)              │
│  ├─ Score all eligible topics                    │
│  ├─ For covered topics: new info check           │
│  ├─ Prioritize: what to write, what angle        │
│  └─ Select top 2-3 articles to write             │
│                                                  │
│  PHASE 4: WRITE (GPT, ~60 sec per article)      │
│  ├─ Generate articles with diaspora angle        │
│  ├─ Source hero images                           │
│  └─ Insert with status = "review"                │
│                                                  │
│  PHASE 5: QA + PUBLISH (~30 sec)                │
│  ├─ Quality review (GPT)                         │
│  ├─ Score for ranking                            │
│  ├─ Approve or reject                            │
│  └─ Rebuild feeds → live                         │
└─────────────────────────────────────────────────┘

Total cycle: ~4-5 minutes
Runs every: 30 minutes
Signal to live: ONE cycle (was 3-4 hours)
```

---

## Schema Changes Needed

### p2_signals (add columns)
```sql
source_type     TEXT    -- 'rss', 'google_news', 'newsletter', 'press_release'
google_cluster  INT     -- cluster size from Google News (if applicable)
story_id        TEXT    -- GPT-assigned canonical story identifier
entities        TEXT[]  -- extracted entities
diaspora_relevant BOOL  -- binary gate
```

### p2_topics (add columns)
```sql
lifecycle       TEXT    -- 'emerging', 'covered', 'developing', 'saturated'
last_article_id UUID    -- link to most recent published article on this topic
last_article_at TIMESTAMPTZ
new_info_summary TEXT   -- what's new since last article
source_types    TEXT[]  -- which source types contributed signals
```

---

## Cost Estimate

Per cycle (30 min):
- GPT-4o-mini triage batch (30-50 signals): ~$0.02
- GPT-4o-mini editorial decision: ~$0.01
- GPT-4o-mini article writing (2-3 articles): ~$0.06
- GPT-4o-mini QA review: ~$0.02

**~$0.11 per cycle × 48 cycles/day = ~$5.28/day**

Current spend: ~$6/day (before category writer retirement). So roughly comparable, but doing much more work (Google News scanning, intelligent triage, topic lifecycle management).

---

## Migration Plan

1. Add Google News ingest as a standalone test first (validate signal quality)
2. Add source_type + story_id columns to p2_signals
3. Build the GPT triage step (entity extraction + story ID + diaspora gate)
4. Rewire email-signal-ingest to go through p2_signals
5. Build topic lifecycle (emerging/covered/developing/saturated)
6. Merge ingest + write + review + score into one rolling script
7. Retire individual crons, replace with single rolling pipeline cron

---

## Open Questions

1. **Cycle frequency**: 30 min? 15 min? 1 hour? Tradeoff between freshness and cost.
2. **Google News rate limits**: No documented limit, but should we self-limit to avoid blocks?
3. **Article updates vs follow-ups**: When new info arrives, update the existing article in-place or publish a new follow-up? (UX question)
4. **Story ID stability**: GPT might assign different story IDs to the same story across runs. Need a matching layer.
5. **Press release sources**: Which PR wire RSS feeds are worth adding?
