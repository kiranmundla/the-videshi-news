# Stale-Event Detection: Research & Architecture Recommendations

**Date:** 2026-09-01  
**Context:** The Videshi news pipeline (Python/Supabase/GPT-4o-mini)  
**Trigger:** Pipeline published a "meet the founder" profile about Aman Sanger (Cursor AI) on 2026-09-01, treating a mid-June SpaceX deal as breaking news  

---

## Executive Summary

The Videshi's pipeline currently conflates **article publication time** with **event occurrence time**. When a publisher puts out a new article about an old event — a profile piece, a retrospective, a "who is" explainer, or simply a recycled story — the pipeline sees a fresh `published_at` timestamp and treats the underlying event as new. The existing dedup layers (14-day LLM window, 60-day keyword check, 30-day published topic titles) all anchor on publication dates, so they cannot catch a newly published article about a weeks-old event unless the pipeline previously covered that same event within those windows.

This report documents how aggregators, NLP systems, APIs, and academic research handle this problem, then proposes a layered architecture that:

1. **Extracts event occurrence time** as a structured field, separate from publication time
2. **Classifies story mode** (new event vs. retrospective/profile/explainer)
3. **Maintains a persistent event ledger** that never ages out
4. **Uses indexed retrieval** against that ledger for fast candidate matching

All recommendations fit the existing GPT-4o-mini scoring workflow, require no custom model training, and stay within the ~$17/month OpenAI budget.

---

## The Failure: Anatomy of the Aman Sanger Incident

### Timeline

| Date | What happened |
|------|--------------|
| Mid-June 2026 | SpaceX invests in Cursor AI at $60B valuation. Multiple outlets report it. |
| 2026-06-20 | Pipeline ingests a Sanger/Cursor topic → **rejected** (presumably low score or duplicate at the time) |
| 2026-07-17 | Pipeline ingests another Sanger/Cursor topic → **rejected** again |
| 2026-09-01 04:58 UTC | A freshly published "meet the founder" article about Sanger triggers a new topic. Pipeline scores it as `new` because: (a) the 14-day LLM window doesn't reach back to June/July; (b) the 60-day keyword window has no *published* Sanger article to match against; (c) the two earlier *rejected* topics have aged out of the 30-day published-topic-title context. Pipeline publishes: `aman-sanger-indian-american-cursor-ai-spacex-60-billion-deal` |

### Why existing defenses failed

1. **Rejected topics age out.** The 30-day topic-title context only includes *published* topics. Both earlier Sanger/Cursor rejections disappeared from the pipeline's memory.

2. **Publication time ≠ event time.** The profile article was genuinely new (fresh URL, fresh `published_at`). But the underlying deal was 10+ weeks old. Nothing in the pipeline asks *when did this event actually happen?*

3. **No story-mode classification.** A "meet the founder" profile looks exactly like breaking news to the current prompt. The LLM sees a high-scoring Indian-American founder + $60B deal + SpaceX and rates it 4-5 without recognizing the retrospective framing.

4. **No persistent event memory.** The pipeline has no durable record of "SpaceX invested in Cursor AI at $60B" as a *real-world event*. Each run starts with a bounded window of recent content and no knowledge of events outside that window.

---

## Industry Landscape: How Aggregators Handle Freshness

### Google Search / Google News

Google's **Query Deserves Freshness (QDF)** algorithm, introduced in 2007 by Amit Singhal and expanded in the 2011 Freshness Update, dynamically adjusts how much weight freshness gets based on topic type:

- **Breaking/trending topics:** Fresh content ranked higher. QDF monitors news publication volume, blog activity, and search query spikes to detect "hot" topics.
- **Evergreen topics** (recipes, definitions): Freshness matters less; authority and quality dominate.
- **Recurring events** (elections, sports seasons): Freshness resets with each occurrence.

Google explicitly distinguishes freshness needs by query class: *"Different searches have different freshness needs. This algorithmic improvement is designed to better understand how to differentiate between these kinds of searches."* — Amit Singhal ([TechRadar, 2011](https://www.techradar.com/news/internet/google-announces-new-freshness-algorithm-for-search-1038597))

**Relevance to The Videshi:** Google has been publicly documented being fooled when publishers refresh timestamps on old articles ([Search Engine Land, 2013](https://searchengineland.com/google-news-showing-old-stories-as-new-a-google-bug-or-publisher-hack-167602)). This confirms that publication-time freshness alone is insufficient even for Google's scale. The key insight is **topic-class-aware freshness** — not all content needs the same recency standard.

### SmartNews

SmartNews publicly states it evaluates ~10 million articles/signals daily using NLP, engagement signals, cultural relevance, discovery, and diversity ([CACM](https://cacm.acm.org/news/new-news-aggregator-apps/)). No public documentation was found describing a specific event-time extraction mechanism. Their system appears to rely on multi-signal correlation (many sources reporting → trending) rather than explicit event dating.

### Apple News

Apple News documentation covers update schedules, source diversity, personalization, and editorial/algorithmic curation. No public source was found describing a stale-event detection algorithm. An academic audit ([arXiv:1908.00456](https://ar5iv.labs.arxiv.org/html/1908.00456)) examined Apple News for source diversity and personalization but not temporal event analysis.

### Open-source news pipeline (MecGlandorff/News)

An open-source news aggregation pipeline explicitly documents this exact failure mode as **Failure Mode #8: "Article timestamp differs from actual event date"**:

> *"An article published today may report an event from yesterday, last week, or months ago. The system treats the publication date as the event date."*
> **Current status:** *"Unmitigated structurally."*
> **Future improvement:** *"Extract event dates from article text as a separate field. Distinguish 'reported at' from 'occurred at.'"*

This confirms the problem is well-recognized in the community but rarely solved in practice. The same pipeline documents **Failure Mode #14** ("Old background information is mistaken for new development"), mitigated only by prompt design — no structural solution.

**Key takeaway:** No major aggregator has publicly documented a complete, production-grade solution for event-time vs. publication-time separation. Google's QDF addresses the *ranking* side (when to prefer fresh content) but doesn't solve the *classification* side (is this article about a new or old event?). The problem remains structurally unmitigated in most systems.

---

## Academic & NLP Methods

### Temporal Expression Extraction

Academic NLP has extensive work on extracting and normalizing temporal expressions from text. The core insight: **articles contain multiple dates, and the hard part is identifying which date belongs to the lead event.**

#### HeidelTime
- **What:** Open-source, multilingual temporal tagger producing TIMEX3 annotations.
- **Key feature:** Dedicated **news-document mode** that resolves relative expressions ("yesterday," "last week") against the document creation time.
- **Implementation:** Java/UIMA. Standalone mode available but operationally heavier than needed for a Python pipeline.
- **Accuracy:** Strong on explicit temporal expressions; less reliable on implicit event dating.
- **Source:** [github.com/JMendes1995/py_heideltime](https://github.com/JMendes1995/py_heideltime) (Python wrapper), [original paper](https://github.com/rudgern/heideltime)

#### Stanford SUTime
- Similar capabilities to HeidelTime. Java-based (Stanford CoreNLP). Resolves relative dates against a reference time. Used extensively in research but same operational weight concern for a lightweight Python pipeline.

#### Key research findings

**TIMELINE corpus (2023):** Explicitly distinguishes event time from document creation time. Supports fuzzy dates ("early June," "last quarter") and event coreference (linking multiple articles about the same real-world event). ([arXiv:2310.17802](https://arxiv.org/pdf/2310.17802))

**PAPEA — Political event extraction (2023):** Uses a practical three-step approach to event dating:
1. Resolve relative-time and weekday expressions anchored to the article's publication date
2. Extract explicit date formats
3. Fall back to publication-date-minus-one-day when no temporal expression exists

Reported accuracy: **52.5% exact-date match**, **80.1% within one week**. Performance degrades sharply when the event-publication gap exceeds one week. This is directly relevant: profile/retrospective articles about events weeks or months old will have poor date extraction from text alone, making the LLM's contextual understanding essential. ([Cambridge Political Science Research & Methods](https://www.cambridge.org/core/journals/political-science-and-research-methods/article/papea-a-modular-pipeline-for-the-automation-of-protest-event-analysis/90205C53AAAAA675F21AC19178418E68))

**ACL W11-4616 — Event relevance and position:** High-relevance events tend to appear in the headline or first two sentences. The paper treats publication-to-event-date distance as a relevance feature — events described far from the publication date are less likely to be the article's primary news. ([ACL Anthology](https://preview.aclanthology.org/credits/W11-4616.pdf))

### Critical Lesson: Date ≠ Lead Event Date

Articles routinely contain **multiple dates** for different purposes:
- The lead event date ("agreed in June")
- Historical context ("founded in 2017")
- Future milestones ("expected to close by Q4")
- Biographical details ("born in 1995")
- Financial periods ("FY 2025 revenue")

Extracting every date is dangerous. **The date must be linked to the lead event trigger**, ideally from the headline, deck, and first 2-3 paragraphs. This is why an LLM-based approach (which understands context) outperforms pure regex/NER for this specific task.

---

## API & Data Source Comparison

| Source | Exposes event time? | Notes |
|--------|-------------------|-------|
| **RSS/Atom feeds** | Publication time only | Standard `pubDate`/`published` field. No event-time field exists in the spec. |
| **NewsAPI** | Publication time only | `publishedAt` field. No event-date extraction. |
| **GDELT Event Stream** | Attempts event dating via `SQLDATE` | The main event stream tries to time-shift events, but the Global Knowledge Graph date is explicitly the article publication date, not the event date. GDELT codebook: *"this date is the date of publication of the news media… if the article discusses events in the past, the date is NOT time-shifted as it is for the GDELT event stream."* Structured events include actors, action type, location, and source URLs. |
| **GDELT GKG** | Publication date only | Explicitly documented as publication date, not event date. |
| **Crossref Event Data** | Distinguishes `occurred_at` vs `timestamp` vs update time | Clean temporal separation, but for news/blog sources `occurred_at` can still mean the content's publication time rather than the event discussed. Useful model for schema design. |
| **ACLED** | Event date + upload timestamp | Conflict event data with clean separation. Uses human coding, not automated extraction. |
| **Event Registry / AYLIEN** | Not verified | Searches did not establish a reliable public field representing the actual event date distinct from article publication. |

**Key takeaway:** No commonly used news API reliably provides the actual event occurrence date as a structured field. This must be extracted by the pipeline itself.

---

## Tools for the Pipeline

### Python `dateparser`

The most practical lightweight tool for The Videshi's stack:

- **200+ locales** supported
- **`search_dates()`** function extracts dates from longer text strings
- **`RELATIVE_BASE` setting** allows resolving relative expressions ("yesterday," "last week") against the article's publication time
- **Handles:** explicit dates ("June 15, 2026"), relative dates ("last month," "three weeks ago"), partial dates ("in June," "earlier this year"), durations and spans ("last week," "past month")
- **Pure Python**, pip-installable, no Java dependency

```python
from dateparser.search import search_dates
from dateparser import parse

# Resolve "last month" relative to article publication date
settings = {'RELATIVE_BASE': datetime(2026, 9, 1)}
result = parse("last month", settings=settings)
# → datetime(2026, 8, 1)

# Extract dates from article text
dates = search_dates(
    "The deal, announced in June, valued Cursor at $60 billion",
    settings=settings
)
# → [('in June', datetime(2026, 6, 1))]
```

**Caveat:** `search_dates()` is documented as limited and can produce false positives on common words. Best used as evidence for the LLM rather than as an automatic rejection mechanism.

### spaCy `DATE` entities

spaCy's NER identifies `DATE` entities but does not resolve them to actual dates or bind them to the lead event. Useful for a quick scan but insufficient alone.

### `htmldate`

Extracts webpage publication/update dates, not the occurrence date of the reported event. Already solved by the pipeline's existing `published_at` field.

---

## Proposed Architecture: Event Freshness Gate

### Design Principles

1. **Model event occurrence time separately from article publication time** — this is the core fix
2. **Extend the existing LLM call** — no additional API calls, no budget increase
3. **Persist event knowledge durably** — events don't age out like topic windows
4. **Use mechanical pre-processing for what doesn't need AI** — date extraction, pattern matching
5. **Shadow-mode first** — log decisions before enforcing them

### Layer 1: Mechanical Temporal Pre-Pass (Before LLM)

**Cost: $0. Effort: Low. Impact: Medium.**

Scan headline + RSS description + lead text (if available) for temporal expressions *before* the LLM scoring call. Feed the results as structured evidence into the LLM prompt.

```python
import dateparser
from dateparser.search import search_dates

def extract_temporal_signals(title, description, published_at):
    """Extract temporal evidence from article text."""
    text = f"{title}. {description}"
    pub_dt = dateparser.parse(published_at)
    settings = {'RELATIVE_BASE': pub_dt}
    
    found_dates = search_dates(text, settings=settings) or []
    
    signals = {
        'extracted_dates': [],
        'stale_cues': [],
        'profile_cues': [],
    }
    
    for phrase, dt in found_dates:
        age_days = (pub_dt - dt).days if dt < pub_dt else 0
        signals['extracted_dates'].append({
            'phrase': phrase,
            'resolved_date': dt.isoformat(),
            'age_days': age_days,
        })
    
    # High-precision stale phrases
    STALE_PATTERNS = [
        r'\b(?:announced|agreed|signed|closed|launched|raised)\s+in\b',
        r'\b(?:last|earlier)\s+(?:month|year|quarter|week)\b',
        r'\b(?:weeks|months)\s+ago\b',
        r'\b(?:back\s+in|dating\s+back)\b',
        r'\bhad\s+(?:acquired|invested|raised|announced|agreed)\b',
        r'\bafter\s+(?:its|the|a)\s+(?:june|july|august|january|february|march|april|may|september|october|november|december)\b',
    ]
    
    # Profile/repackaging cues
    PROFILE_PATTERNS = [
        r'\b(?:meet|who\s+is|get\s+to\s+know)\b',
        r'\b(?:the\s+)?(?:journey|story\s+behind|story\s+of|rise\s+of|how\s+.+\s+built)\b',
        r'\b(?:things?\s+(?:to|you\s+should)\s+know\s+about)\b',
        r'\b(?:everything\s+(?:you\s+need\s+to|to)\s+know)\b',
        r'\b(?:here\'?s?\s+(?:what|why|how|who))\b',  # explainer framing
    ]
    
    import re
    text_lower = text.lower()
    for pat in STALE_PATTERNS:
        if re.search(pat, text_lower):
            signals['stale_cues'].append(re.search(pat, text_lower).group())
    for pat in PROFILE_PATTERNS:
        if re.search(pat, text_lower):
            signals['profile_cues'].append(re.search(pat, text_lower).group())
    
    return signals
```

**For the Sanger incident:** This would have detected "meet the founder" as a profile cue, and if the description mentioned "June" or "earlier this year," would have flagged a 70+ day age gap.

### Layer 2: Extend GPT-4o-mini Scoring Output (The Core Fix)

**Cost: ~$0-2/month marginal (slightly longer output tokens). Effort: Low-Medium. Impact: Highest.**

Add structured event-time fields to the existing LLM scoring response schema. This is the single highest-impact change because it solves the root cause — the pipeline never asks *when did this happen?*

**New fields to add to the LLM response:**

```json
{
  "results": [{
    "id": 1,
    "relevant": true,
    "score": 4,
    "category": "technology",
    "coverage": "new",
    "reason": "...",

    "event_date": "2026-06",
    "event_date_precision": "month",
    "event_date_confidence": "high",
    "temporal_basis": "announced in June",
    "story_mode": "retrospective",
    "new_development": null,
    "event_signature": "spacex-cursor-ai-investment-60b"
  }]
}
```

**Field definitions:**

| Field | Type | Description |
|-------|------|-------------|
| `event_date` | string | When the lead event actually occurred. ISO date or partial: `"2026-06-15"`, `"2026-06"`, `"2026-Q2"`, `"2026"`. Null if genuinely breaking/same-day. |
| `event_date_precision` | enum | `"day"`, `"week"`, `"month"`, `"quarter"`, `"year"`, `"unknown"` |
| `event_date_confidence` | enum | `"high"` (explicit date in text), `"medium"` (inferred from context), `"low"` (rough estimate) |
| `temporal_basis` | string | The phrase or evidence used to determine the date. E.g., `"announced in June"`, `"last month"`, `"three weeks ago"` |
| `story_mode` | enum | `"new_event"` — genuinely new occurrence. `"major_update"` — substantive new development on a known event. `"retrospective"` — profile, "who is", "meet", "story behind". `"explainer"` — background/analysis piece. `"anniversary"` — marking an anniversary. `"evergreen"` — timeless content. |
| `new_development` | string\|null | If `story_mode` is `"major_update"`, what specifically is new? E.g., `"Deal officially closed"`, `"FDA approval granted"`. Null otherwise. |
| `event_signature` | string | Normalized slug: key entities + action + object. E.g., `"spacex-cursor-ai-investment-60b"`, `"india-chandrayaan-3-landing"`. Used for event ledger matching. |

**Prompt addition** (append to existing `LLM_PROMPT`):

```
EVENT TIMING — CRITICAL:
For each topic, determine WHEN the underlying event actually occurred, not when the article was published.
- If the article says "announced in June" or "agreed last month" or "weeks ago", the event_date is that past date, NOT today.
- If the article is a profile, "meet the founder", "who is", or retrospective about something that already happened, story_mode is "retrospective" and event_date is when the original event occurred.
- If the article reports something happening TODAY or within the last 48 hours with no backward-looking language, event_date is null (same-day).
- The temporal_basis must quote the actual phrase from the text that tells you when it happened.
- A retrospective/profile with NO new development is NOT the same as breaking news, even if the person or company is highly relevant to our audience.

TEMPORAL EVIDENCE FROM PRE-SCAN:
{temporal_signals_json}
Use this evidence to anchor your event_date, but rely on your own reading of the full text for story_mode and new_development.
```

**Token impact estimate:** Adding 7 fields to each result adds ~30-50 output tokens per topic. At 40 topics/batch, that's ~1,200-2,000 extra tokens per batch. At GPT-4o-mini output pricing ($0.60/M tokens), this costs ~$0.001 per batch — negligible.

### Layer 3: Decision Policy (Post-LLM Gate)

**Cost: $0. Effort: Low. Impact: High.**

After the LLM returns event-time fields, apply mechanical rules:

```python
def apply_event_freshness_gate(llm_result, pub_date):
    """Post-LLM gate: reject stale events repackaged as new."""
    event_date = llm_result.get('event_date')
    story_mode = llm_result.get('story_mode', 'new_event')
    new_dev = llm_result.get('new_development')
    confidence = llm_result.get('event_date_confidence', 'low')
    
    if not event_date or story_mode == 'new_event':
        return 'pass'  # Genuinely new or can't determine — let through
    
    # Calculate event age
    event_dt = dateparser.parse(event_date)
    if not event_dt:
        return 'pass'
    
    age_days = (pub_date - event_dt).days
    
    # Rule 1: Old event + retrospective/profile + no new development → reject
    if age_days > 14 and story_mode in ('retrospective', 'explainer', 'anniversary', 'evergreen'):
        if not new_dev:
            if confidence in ('high', 'medium'):
                return 'reject_stale'
            else:
                return 'flag_review'  # Low confidence — log but don't auto-reject
    
    # Rule 2: Old event + major_update + has new development → pass as update
    if story_mode == 'major_update' and new_dev:
        return 'pass_as_update'
    
    # Rule 3: Old event but no clear story mode → flag for review
    if age_days > 30 and confidence in ('high', 'medium'):
        return 'flag_review'
    
    return 'pass'
```

**Critical guardrails — never auto-reject:**
- Court rulings or verdicts (even if the underlying case is old)
- Death announcements, rescue outcomes, final death tolls
- Finalized deals or acquisitions (the closing itself is news)
- Election results (even if the campaign was covered for months)
- Any topic where `new_development` is non-null

These are genuine updates where the *outcome* is new even though the *event* is old. The current pipeline already handles outcome-vs-anticipation in the `coverage` classification prompt ("if we covered 'set to launch' and now the launch SUCCEEDED or FAILED — that's an update"). The event freshness gate must respect this.

### Layer 4: Persistent Event Ledger (Medium-Term)

**Cost: $0 infrastructure (Supabase). Effort: Medium. Impact: High.**

Create a `p2_events` table in Supabase that stores one durable row per normalized real-world event:

```sql
CREATE TABLE p2_events (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    event_signature TEXT NOT NULL,           -- normalized slug
    canonical_description TEXT,              -- "SpaceX invests in Cursor AI at $60B valuation"
    event_date TEXT,                         -- "2026-06" (partial OK)
    event_date_precision TEXT,               -- day/week/month/quarter/year
    entities TEXT[],                         -- ["SpaceX", "Cursor AI", "Aman Sanger"]
    action_type TEXT,                        -- "investment", "acquisition", "launch", "ruling"
    amounts TEXT[],                          -- ["$60B"]
    locations TEXT[],                        -- ["San Francisco"]
    state TEXT DEFAULT 'active',             -- active/concluded/superseded
    first_seen_at TIMESTAMPTZ DEFAULT NOW(),
    last_seen_at TIMESTAMPTZ DEFAULT NOW(),
    first_topic_id UUID,                     -- link to originating topic
    topic_ids UUID[],                        -- all related topics
    article_ids UUID[],                      -- all related published articles
    aliases TEXT[],                          -- alternate phrasings
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for fast candidate retrieval
CREATE INDEX idx_events_signature ON p2_events(event_signature);
CREATE INDEX idx_events_entities ON p2_events USING GIN(entities);
CREATE INDEX idx_events_event_date ON p2_events(event_date);
CREATE INDEX idx_events_last_seen ON p2_events(last_seen_at);

-- Full-text search on description + entities
CREATE INDEX idx_events_fts ON p2_events USING GIN(
    to_tsvector('english', canonical_description || ' ' || array_to_string(entities, ' '))
);
```

**Why this is better than widening dedup windows:**
- Events **never age out**. The SpaceX-Cursor event persists forever.
- Rejected topics contribute to the ledger (the June/July Sanger rejections would have created an event record).
- The ledger stores **semantic events** (entity + action + amount), not arbitrary publisher phrasing.
- Candidate matching is indexed — no 60-day or 90-day or all-time headline dump.

**Population strategy:**
1. **Going forward:** Every scored topic (accepted or rejected) generates or updates an event record from its `event_signature` + `event_date` + entities.
2. **No backfill required.** The ledger builds naturally over days/weeks. Within 2-4 weeks, it covers all actively recurring topics.
3. **Optional lightweight backfill:** Run a one-time pass over published articles in `p2_articles` to seed ~100-200 event records from the most recent 60 days. This is a single LLM call on ~200 headlines, costing ~$0.02.

### Layer 5: Candidate Retrieval Against the Ledger

**Cost: $0. Effort: Medium. Impact: High (combined with Layer 4).**

Before LLM scoring, check incoming topics against the event ledger:

```python
def find_matching_events(topic_title, topic_entities, event_date=None):
    """Retrieve candidate matching events from the ledger."""
    matches = []
    
    # 1. Exact signature match (fastest)
    sig = normalize_event_signature(topic_title)
    exact = sb_get("p2_events", {"event_signature": f"eq.{sig}"})
    if exact:
        matches.extend(exact)
    
    # 2. Entity overlap (PostgreSQL array overlap operator)
    if topic_entities:
        entity_list = ",".join(f'"{e}"' for e in topic_entities[:5])
        entity_matches = sb_get("p2_events", {
            "entities": f"ov.{{{entity_list}}}",
            "order": "last_seen_at.desc",
        }, range_header="0-9")
        if entity_matches:
            matches.extend(entity_matches)
    
    # 3. Full-text search on description
    keywords = extract_distinctive_keywords(topic_title)
    if keywords:
        fts_query = " & ".join(keywords[:4])
        fts_matches = sb_get("p2_events", {
            "canonical_description": f"fts.{fts_query}",
            "order": "last_seen_at.desc",
        }, range_header="0-4")
        if fts_matches:
            matches.extend(fts_matches)
    
    # Deduplicate by event ID
    seen_ids = set()
    unique = []
    for m in matches:
        if m['id'] not in seen_ids:
            seen_ids.add(m['id'])
            unique.append(m)
    
    return unique[:5]  # Return top 5 candidates
```

**If matching events are found**, inject them into the LLM prompt:

```
KNOWN EVENTS IN OUR RECORDS:
- "SpaceX invests in Cursor AI at $60B valuation" (event date: June 2026, first seen: 2026-06-20)
- [...]

If this topic covers the same event as one above, it is NOT new — classify accordingly.
```

This is lightweight: 1-3 extra lines in the prompt, no additional LLM call.

### Layer 6: Shadow Mode & Rollout

**Cost: $0. Effort: Low. Impact: Essential for safe deployment.**

1. **Week 1-2: Log only.** Add the temporal pre-pass and extended LLM fields. Log extracted `event_date`, `story_mode`, and what the gate *would* have decided. Do not reject anything.

2. **Review samples.** Check:
   - False positives: Would the gate have rejected a legitimate breaking story?
   - False negatives: Did the gate miss a recycled/stale article?
   - LLM compliance: Is the model reliably filling `event_date` and `story_mode`?

3. **Week 3: Enforce high-confidence cases only.** Auto-reject when ALL of:
   - `event_date` resolves to 14+ days ago
   - `event_date_confidence` is `high`
   - `story_mode` is `retrospective` or `explainer`
   - `new_development` is null
   - At least one `stale_cue` or `profile_cue` from the pre-pass

4. **Week 4+: Expand gradually.** Lower confidence thresholds, add event ledger matching, extend to `medium` confidence cases.

---

## Effort/Impact Matrix

| Recommendation | Impact | Effort | Cost | Priority |
|---------------|--------|--------|------|----------|
| Extend GPT-4o-mini output with `event_date` + `story_mode` fields | **Highest** | Low-Medium | ~$0-2/mo | **Do first** |
| Post-LLM decision gate (reject stale + retrospective + no new development) | **High** | Low | $0 | **Do with above** |
| `dateparser` temporal pre-pass (headline + description) | **Medium** | Low | $0 | **Do with above** |
| Profile/repackaging linguistic cue detection | **Medium** | Low | $0 | **Do with above** |
| Shadow-mode logging before enforcement | **Essential** | Low | $0 | **Do with above** |
| Persistent event ledger (`p2_events` table) | **High** | Medium | $0 | **Phase 2 (week 2-3)** |
| Indexed candidate retrieval against ledger | **High** | Medium | $0 | **Phase 2 (week 2-3)** |
| Rejected-topic event extraction (populate ledger from rejections) | **Medium** | Low | $0 | **Phase 2** |
| HeidelTime evaluation for multilingual feeds | Low | Medium | $0 | Optional/later |
| Embedding-based event similarity | Medium | High | $5-10/mo | Not recommended now |
| Ever-wider dedup windows (90d, 180d, all-time) | Low | Low | $0 | **Not recommended** |
| All-time raw headline prompts | Low-Medium | Low | $2-5/mo | **Not recommended** |

---

## What NOT to Do

### ❌ Widen dedup windows indefinitely
Kiran correctly identified: *"But rejected ones will age out also."* Making the window 90 days or 180 days just delays the problem. A profile piece about a 7-month-old event will still slip through. And the LLM context grows linearly with the window, burning tokens.

### ❌ Keep all rejected headlines forever in the LLM prompt
This scales linearly (~50 rejected topics/day × 365 days = 18,000+ headlines). Token cost becomes significant and the LLM's attention degrades with long context.

### ❌ Build full embedding/vector infrastructure
Overkill for this problem. The entity + keyword matching in Layer 5 provides sufficient recall for event deduplication without the infrastructure cost of maintaining embeddings.

### ❌ Rely on external APIs for event truth
No commonly used news API reliably provides event occurrence dates. This must be extracted by the pipeline itself.

### ❌ Train a custom model
Against constraints. GPT-4o-mini with structured output is sufficient for event-time extraction when properly prompted.

---

## Implementation Sequence

### Phase 1: Core Fix (Week 1)

1. **Add `extract_temporal_signals()` function** to `v3-select.py`
   - `pip install dateparser` in the pipeline environment
   - Scan headline + description for dates and stale/profile cues
   - Feed results as `TEMPORAL EVIDENCE` into the LLM prompt

2. **Extend `LLM_PROMPT`** with event-timing instructions and new output fields
   - `event_date`, `event_date_precision`, `event_date_confidence`
   - `temporal_basis`, `story_mode`, `new_development`, `event_signature`

3. **Parse new fields from LLM response** in `llm_score_topics()`
   - Store in the scored candidate dict
   - Log to stdout for shadow-mode review

4. **Add `apply_event_freshness_gate()`** function
   - Initially log-only: print what it *would* reject
   - Do not change any actual accept/reject decisions yet

5. **Store event fields on topics** — add columns to `p2_topics` or store in metadata

### Phase 2: Event Ledger (Weeks 2-3)

6. **Create `p2_events` table** in Supabase with indexes
7. **Populate from scored topics** — every scored topic creates/updates an event record
8. **Add candidate retrieval** — check incoming topics against the ledger before LLM scoring
9. **Inject matching events** into the LLM prompt as "KNOWN EVENTS"

### Phase 3: Enforcement (Weeks 3-4)

10. **Enable the freshness gate** for high-confidence cases
11. **Review false positives** from shadow-mode logs
12. **Tune thresholds** — age cutoff, confidence requirements, story-mode rules
13. **Add event ledger match as a hard signal** — if an event in the ledger matches with high confidence, override the LLM's `coverage` classification

---

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| LLM doesn't reliably fill new fields | Shadow mode catches this. Fields are advisory — the gate has fallback rules using the mechanical pre-pass. If the LLM consistently fails on `event_date`, the `dateparser` pre-pass provides backup evidence. |
| False positives: genuine update rejected as stale | The `new_development` field is the safety valve. Any non-null `new_development` passes through. Court rulings, election results, deal closings, and death announcements have explicit new developments. |
| False negatives: stale article slips through despite new fields | Acceptable in early phases — better to miss a few than reject good stories. The event ledger (Phase 2) adds a second layer of defense. |
| `dateparser` false positives on common words | Feed as evidence, never auto-reject. The LLM makes the final call. |
| Event ledger grows unbounded | Events are compact (~500 bytes each). At 50/day, that's ~18K rows/year — trivial for PostgreSQL. Add a `state = 'archived'` for events not seen in 12+ months if needed. |
| Added latency from pre-pass + ledger query | The `dateparser` pre-pass runs locally (~10-50ms per topic). Ledger queries are indexed PostgreSQL — ~5-20ms each. Total overhead: <1 second per batch. |

---

## Sources

### Industry & Aggregator
- Google QDF / Freshness Algorithm: [Search Engine Land](https://searchengineland.com/guide/query-deserves-freshness-qdf), [Search Engine Journal](https://www.searchenginejournal.com/google-algorithm-history/freshness-algorithm/), [TechRadar](https://www.techradar.com/news/internet/google-announces-new-freshness-algorithm-for-search-1038597), [SISTRIX](https://www.sistrix.com/ask-sistrix/google-updates-and-algorithm-changes/google-freshness-update/what-does-query-deserves-freshness-qdf-mean)
- Google News old stories as new: [Search Engine Land (2013)](https://searchengineland.com/google-news-showing-old-stories-as-new-a-google-bug-or-publisher-hack-167602)
- SmartNews overview: [CACM](https://cacm.acm.org/news/new-news-aggregator-apps/)
- Apple News audit: [arXiv:1908.00456](https://ar5iv.labs.arxiv.org/html/1908.00456)

### Academic / NLP
- TIMELINE corpus (event time vs. document time): [arXiv:2310.17802](https://arxiv.org/pdf/2310.17802)
- PAPEA event extraction pipeline: [Cambridge PSRM](https://www.cambridge.org/core/journals/political-science-and-research-methods/article/papea-a-modular-pipeline-for-the-automation-of-protest-event-analysis/90205C53AAAAA675F21AC19178418E68)
- Event relevance and temporal distance: [ACL W11-4616](https://preview.aclanthology.org/credits/W11-4616.pdf)
- HeidelTime: [GitHub](https://github.com/rudgern/heideltime), [Python wrapper](https://github.com/JMendes1995/py_heideltime)

### APIs & Data
- GDELT GKG Codebook: [data.gdeltproject.org](http://data.gdeltproject.org/documentation/GDELT-Global_Knowledge_Graph_Codebook.pdf)
- GDELT errors in real-time news: [GDELT Blog](https://blog.gdeltproject.org/learning-at-web-scale-errors-edge-cases-in-realtime-news-coverage/amp/)
- Crossref Event Data temporal fields: [eventdata.crossref.org/guide/data/time](https://www.eventdata.crossref.org/guide/data/time/)
- Open-source news pipeline failure modes: [MecGlandorff/News](https://github.com/mecglandorff/news/blob/HEAD/docs/failure-modes.md)

### Tools
- Python `dateparser`: [GitHub](https://github.com/Workable/python-dateparser), [Docs](https://dateparser.readthedocs.io/en/v1.0.0/index.html)
- `dateparser.search.search_dates`: [GitHub issue #326](https://github.com/scrapinghub/dateparser/issues/326)
