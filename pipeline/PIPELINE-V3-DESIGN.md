# Pipeline V3 Design — Topic-Centric Architecture

## Problem (V2)
- Google News gives us pre-grouped clusters, but we throw away the grouping and store only the lead article
- Selector re-clusters raw signals from scratch every run (keyword + LLM), redoing work Google already did
- 95% of signals re-evaluated every run (redundant LLM cost)
- p2_topics table exists but is unused — 108K "topics" that are just 1:1 copies of signals
- Zero signals have topic_id set — no link between signals and topics

## Architecture (V3)

```
Sources (Google News, RSS, Email)
    │
    ▼
  INGEST (every 30 min)
    1. Fetch feeds
    2. URL hash dedup → only NEW signals
    3. Google News clusters: extract sub-article URLs, preserve grouping
    4. GPT matching: send new signal titles + existing topic titles to gpt-4o-mini
       → matches signals to existing topics OR creates new topics
    5. Insert signals with topic_id linked
    6. Update topic signal_count, last_signal_at
    │
    ▼
  SELECTOR (every 2h)
    1. Read topics with status='pending' that have new signals since last evaluation
    2. GPT relevance scoring on TOPICS (not raw signals)
       → relevant / irrelevant / update
    3. Output candidates with ALL signal URLs per topic
    │
    ▼
  WRITER (per candidate)
    1. Read multiple source URLs from topic's signals
    2. Synthesize article from multiple sources
    3. Mark topic status='written', link to article
```

## Topic Lifecycle
```
pending → [GPT evaluates] → irrelevant (status='rejected')
                           → relevant → [writer creates article] → status='written'
                           → update → [writer creates update article] → status='written'

Re-evaluation trigger: rejected topic gets 5+ new signals → re-evaluate
Expiry: pending topics older than 7 days → status='expired'
```

## Key Design Decisions
1. **No keyword matching** — GPT handles all clustering ($0.006/run ≈ $9/month)
2. **URL hash is the signal dedup** — seen before? skip. New? process.
3. **Google clusters preserved** — sub-article URLs extracted and stored as signals
4. **Topic = the core entity** — maps to one article (or discard)
5. **Incremental by design** — each run only processes new signals
6. **State file not needed** — the URL hash in DB IS the state

## p2_topics Schema Changes Needed
- Add `last_signal_at` (timestamp) — when newest signal arrived
- Add `gpt_evaluated_at` (timestamp) — when GPT last scored relevance
- Add `source_urls` (text[]) — all signal URLs for this topic (denormalized for writer speed)
- Clean up statuses: only use pending/rejected/written/expired

## p2_signals Changes
- Actually SET topic_id on insert (currently always null)
- Google News sub-articles stored as separate signals with same topic_id

## Cost Estimate
- Ingest GPT clustering: ~$0.006/run × 48/day = $0.29/day
- Selector GPT scoring: ~$0.01/run × 12/day = $0.12/day
- Total: ~$0.41/day (~$12/month)
- Current V2 cost: ~$0.50/day — so roughly the same, but cleaner

## Migration Plan
1. Build new ingest as `v3-ingest.py` — test side by side
2. Clean p2_topics (archive 108K junk entries)
3. Build new selector as `v3-select.py`
4. Test for a few runs, compare output quality
5. Switch crons from V2 to V3
6. Retire V2 scripts
