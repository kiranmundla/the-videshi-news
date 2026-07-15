# Pipeline V2 Research Report — The Videshi

**Date**: July 2026  
**Purpose**: Research findings and architecture recommendations for the next-generation automated news pipeline  
**Audience**: Pipeline development planning for thevideshi.com

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [News Aggregation & Story Clustering Architecture](#2-news-aggregation--story-clustering-architecture)
3. [AI-Powered Newsrooms — Industry State of the Art](#3-ai-powered-newsrooms--industry-state-of-the-art)
4. [Signal Source Optimization](#4-signal-source-optimization)
5. [Story Clustering & Deduplication](#5-story-clustering--deduplication)
6. [Story Timeline & Evolution Tracking](#6-story-timeline--evolution-tracking)
7. [Editorial Intelligence](#7-editorial-intelligence)
8. [Quality, Trust & Hallucination Prevention](#8-quality-trust--hallucination-prevention)
9. [Pipeline Architecture](#9-pipeline-architecture)
10. [LLM Cost Optimization](#10-llm-cost-optimization)
11. [Open Source Tooling](#11-open-source-tooling)
12. [Synthesized Architecture Recommendation](#12-synthesized-architecture-recommendation)

---

## 1. Executive Summary

This report synthesizes research across industry practices, academic literature, and production systems to inform the design of The Videshi's Pipeline V2. The core challenge: transform a fragmented cron-based pipeline into a unified, intelligent system that can **identify every important diaspora story** (recall over precision), **cluster related signals into coherent topics**, **distinguish genuinely new developments from duplicate coverage**, and **produce publishable articles with minimal hallucination** — all within a ~$5-6/day LLM budget.

### Key Findings

- **Story clustering is a solved-enough problem** for The Videshi's scale. A three-signal approach (semantic embeddings + named entity overlap + time decay) with HDBSCAN clustering, preceded by LSH-based deduplication, matches what production systems like Feedly and Reuters use — scaled down appropriately.
- **The "new development vs. duplicate" problem is the hardest unsolved piece.** No off-the-shelf tool handles this well. It requires LLM judgment comparing new signal content against already-published article content — a gap where The Videshi's pipeline must build custom logic.
- **Full streaming architecture is overkill.** RSS is inherently poll-based. A tight polling loop (15-30 min) with a unified processing pipeline is the right architecture, not Kafka or event-driven systems.
- **Model routing can cut LLM costs 50-70%.** Use the cheapest model (GPT-4o mini or Mistral Small) for binary classification (diaspora yes/no, duplicate yes/no), and reserve more capable models for editorial decisions and article writing.
- **Hallucination prevention in automated article writing requires a multi-layer approach**: source-grounded prompts (strict "write only from these sources" instructions), post-generation verification (claim extraction + source matching), and constrained output schemas. No single technique is sufficient.

### The Videshi's Constraints (as inputs to all recommendations)

| Constraint | Value |
|---|---|
| Daily LLM budget | ~$5-6/day |
| Signal volume | 79 RSS feeds, ~113K signals, ~98K topics |
| Publishing volume | 65-80 articles/day |
| Infrastructure | Supabase (PostgreSQL), Python scripts, Vercel frontend |
| Current LLM | GPT-4o-mini for all tasks |
| North star | "Don't miss any important story" — recall over precision |
| Diaspora lens | Binary yes/no gate preferred over scoring |
| Google Cloud | Billing blocked ($235 outstanding) — Gemini unavailable |
| Complexity ceiling | No Kafka, no complex infra — Python crons on a simple server |

---

## 2. News Aggregation & Story Clustering Architecture

### 2.1 Feedly's Production Architecture

Feedly processes ~1.7 million articles/day (~20/second) and represents the most well-documented production news clustering system. Their architecture offers several transferable lessons:

**Dedup-first pipeline**: Feedly runs Locality Sensitive Hashing (LSH) deduplication *before* clustering, which dramatically reduces the number of articles that need expensive embedding and clustering operations. For The Videshi's ~113K signals, this could reduce the clustering workload by 60-80%.

**Cluster propagation shortcut**: When a new article is identified as a near-duplicate of one already assigned to a cluster, it inherits that cluster assignment immediately via stream processing — no need to wait for the next batch clustering run. This reduces latency from 15-20 minutes (batch) to near-instant for the majority of articles. This is a key insight: most "new" articles are duplicates of something already clustered, so the expensive clustering operation only needs to run on genuinely novel content.

**Density-based clustering**: Feedly uses density-based clustering (similar to DBSCAN/HDBSCAN) for the batch process, which handles the uneven distribution of news topics naturally — major breaking stories form dense clusters while niche topics remain small or singleton.

**Relevance to The Videshi**: At ~113K signals, The Videshi operates at roughly 1/15th of Feedly's scale. The dedup-first + cluster-propagation architecture is directly applicable and would bring the computationally expensive clustering step down to a manageable number of truly novel signals.

### 2.2 Zeyong Cai's Three-Signal Clustering (Research Implementation)

A detailed Medium series by Zeyong Cai documents building a news aggregator from scratch, with findings that are particularly relevant to The Videshi's diaspora focus:

**Three-signal distance function**: Rather than relying on a single similarity measure, this approach combines three complementary signals:

1. **Semantic distance** — Cosine similarity between sentence embeddings (SBERT/MiniLM). Captures topical similarity but fails when topics are semantically close but refer to different events (e.g., "WhatsApp update" vs "Instagram update" — both Meta, both social media, both "update").

2. **Entity distance** — Jaccard similarity of NER-extracted entities. This is the critical second signal that prevents over-broad clustering. Two articles about Meta but mentioning different products, people, or organizations get separated. For The Videshi, entity overlap is especially valuable because diaspora stories often involve specific people, organizations, and places that should not be conflated.

3. **Time distance** — Normalized time gap between articles. Splits stories that evolve over multiple days into coherent sub-events (e.g., "GPT-4o released" vs "GPT-4o hits usage limits" vs "GPT-4o opens to free users" are related but distinct events separated by time).

**Embedding input matters**: Testing showed that **one-sentence summaries** produce the best embeddings for clustering — better than title-only (too sparse) or full-article text (too noisy, dilutes the core topic). This suggests a cheap preprocessing step: use the cheapest LLM to generate a single-sentence summary of each signal, then embed that summary.

**HDBSCAN as clustering algorithm**: Hierarchical Density-Based Spatial Clustering of Applications with Noise. Key advantages over K-means or agglomerative clustering:
- Does not require choosing the number of clusters in advance
- Explicitly labels noise points (articles that don't belong to any cluster) rather than forcing every article into a cluster
- Handles clusters of varying density and size
- Works well with the three-signal distance matrix

**Weight tuning**: The weights for the three signals (w_s, w_e, w_t) are project-specific and need tuning. For The Videshi, entity weight should likely be higher than in a general news aggregator, because diaspora stories are defined partly by the specific entities involved (Indian companies, politicians, diaspora organizations, specific countries).

### 2.3 Academic Findings

**Agglomerative hierarchical clustering + SentenceBERT** substantially outperforms other approaches for news story chain detection according to recent comparative studies. This aligns with the HDBSCAN recommendation since HDBSCAN is itself hierarchical and density-based.

**TF-IDF remains competitive** for short-text event detection (tweet-level content), sometimes beating deep embeddings. This is relevant for The Videshi's RSS signal titles, which are short. A hybrid approach — TF-IDF for initial fast filtering, embeddings for deeper semantic matching — could be efficient.

**3-day moving window**: Academic work on news story chains finds that most stories are relevant for approximately 3 days. This suggests the clustering window should be ~3 days (not 24 hours, which would miss multi-day stories; not 7 days, which would create overly broad clusters).

**Unsupervised methods preferred**: Since new topics appear continuously and the topic distribution shifts daily, supervised classifiers trained on historical data degrade quickly. Unsupervised clustering (HDBSCAN, density-based) is the right paradigm.

---

## 3. AI-Powered Newsrooms — Industry State of the Art

### 3.1 Reuters News Tracer

The gold standard for automated news detection, though operating at a scale far beyond The Videshi's needs:

- Processes **12-13 million tweets/day**, rejects 80% as noise, creates ~6,000 event clusters
- Classifies and prioritizes events by comparing topic signatures against 31 official news accounts
- Includes veracity checking: finds earliest tweet, checks against fake news database
- Auto-writes headlines and summaries for detected events
- **Detected breaking news 8-18 minutes ahead of major outlets** (San Bernardino shooting, Ecuador earthquake, Brussels/Chelsea bombings)
- Runs under 40 milliseconds per tweet across 13 servers with 10 algorithms
- Uses over 700 signals for veracity determination

**Relevance**: The architecture pattern is transferable — noise rejection → clustering → classification → prioritization → generation — even though the scale is not. The concept of comparing detected events against a "reference set" of trusted sources (Reuters uses 31 accounts; The Videshi could use a curated list of key diaspora-relevant feeds) is directly applicable for prioritization.

### 3.2 Semafor Signals

Microsoft/OpenAI-sponsored breaking news feed that represents the "AI-assisted journalism" model:

- AI tools help journalists search across languages and geographies
- Produces ~12 posts/day, **all written by journalists**
- AI is a research aid only — humans evaluate, verify, compose summaries, and cite sources

**Relevance**: For The Videshi's highest-priority stories (developing situations, sensitive topics), this human-in-the-loop model should be the target. The pipeline should surface and prepare these stories; a human editor approves or edits them.

### 3.3 Associated Press — Template-Based Generation

AP uses NLG (Automated Insights' Wordsmith platform) for corporate earnings stories — going from 300 articles/quarter to thousands. This is **template + rule-based**, not LLM-based, and works because earnings reports have highly structured, predictable data.

**Relevance**: For certain categories of The Videshi's content (market data roundups, sports scores, election results), template-based generation with data slot-filling could be more reliable and cheaper than LLM generation. These articles have predictable structures and rely on factual data that can be extracted and verified.

### 3.4 Artifact (now Yahoo News)

Built by the Instagram founders, Artifact's recommendation system uses:

- **Transformer-based recommendation** for personalization
- **Dwell time over clicks** as the engagement signal — measuring whether people actually read articles, not just whether they clicked. This counters clickbait.
- **Epsilon-Greedy exploration** with 10-20% explore budget — intentionally showing some articles outside the user's established preferences to prevent filter bubbles

**Relevance**: The dwell-time insight is relevant for The Videshi's feedback loop. If article performance data is available (from Vercel analytics), tracking time-on-page rather than just pageviews would give better signal about article quality.

### 3.5 DRIVE Local

An automated local news system that processes diverse input formats (emails, PDFs, scanned documents) into publishable articles:

- Produces **1,000+ AI articles/month**
- Achieved **80% reduction in manual effort**

**Relevance**: Demonstrates that automated article production at The Videshi's scale (65-80/day ≈ 2,000/month) is well within what production systems achieve. DRIVE Local's multi-format input processing is also relevant — The Videshi could ingest press releases, government announcements, and other structured documents beyond RSS.

---

## 4. Signal Source Optimization

### 4.1 Current State: Google News RSS

The Videshi currently relies on Google News RSS feeds. Testing reveals:

**Topic feeds** (e.g., `/rss/topics/...`):
- Return 38-70 items per feed
- Heavily clustered — 90%+ of items have 5+ sources covering the same story
- Good for getting the "big stories" but poor for niche/long-tail diaspora content

**Search query feeds** (e.g., `/rss/search?q=...`):
- Return up to 100 items
- No clustering — every article is a separate entry
- Support operators: `"exact phrase"`, `OR`, `-exclude`, `when:1h/1d/7d`, `hl=`, `gl=`, `ceid=`
- Geo editions available: US (`ceid=US:en`), India (`ceid=IN:en`), UK (`ceid=GB:en`)
- **`when=` time filter returned 0 results in testing** — may be unreliable/broken

**Rate limiting**: No documented rate limits, but Google could throttle or block aggressive polling. Self-impose 2-8 second delays between requests.

**Key gap**: Google News RSS provides no metadata beyond title, link, publication date, and source. No article text, no summaries, no entities, no categories. Every signal requires a full article fetch + extraction step.

### 4.2 GDELT — Free Supplementary Source

The Global Database of Events, Language, and Tone is a 100% free, open database monitoring broadcast, print, and web news in 100+ languages:

- **DOC API**: Last 3 months of global news across 65 languages, no authentication required, returns up to 250 articles per query
- Updates every **15 minutes**
- Provides volume timelines, tone analysis, source country/language breakdowns
- Available via Google BigQuery (free tier), raw CSV downloads, or the Analysis Service

**Use case for The Videshi**: GDELT's DOC API could serve as a gap-filler — running queries for diaspora-relevant topics that might not surface in Google News RSS. Example: `query=india+diaspora&mode=artlist&maxrecords=250&format=json` every 30 minutes. GDELT's tone analysis could also pre-filter for stories with strong positive/negative sentiment (more newsworthy).

**Caveat**: Google BigQuery access may be blocked by the billing issue. The DOC API and raw CSV downloads should still work since they're not GCP services.

### 4.3 Paid News APIs — Comparative Assessment

| API | Free Tier | Paid Starting | Sources | Key Feature | Fit for The Videshi |
|---|---|---|---|---|---|
| **Perigon** | Limited | Custom | 200K+ | Pre-clustered "Stories" endpoint with summaries; vector search | Best fit if budget allows — the Stories endpoint does clustering for you |
| **NewsAPI.org** | Dev/test only | $449/mo | 80K+ | Simple, well-documented | Too expensive for the feature set |
| **NewsData.io** | Yes (limited) | Custom | 97K+ | 8 years historical data | Good for backfill/research, not real-time pipeline |
| **Mediastack** | Yes | Low | 7,500+ | 13 languages | Too few sources for diaspora coverage |
| **NewsMesh** | No | $29/mo | Varies | ML enrichment (entities, sentiment) | Interesting for enrichment layer |
| **APITube** | Yes | Varies | Varies | Free sentiment + entity extraction | Could supplement entity extraction |

**Recommendation**: Stay with Google News RSS + GDELT as primary free sources. Perigon is the only paid API worth considering — its "Stories" endpoint with pre-clustered events and summaries would eliminate the need for custom clustering infrastructure, but only if the budget accommodates it. At the current $5-6/day LLM budget, adding a paid API subscription would need to demonstrably save more in LLM costs than it adds in API fees.

### 4.4 Source Strategy Recommendation

A **layered source architecture**:

1. **Primary**: Google News RSS (79 feeds, polled every 15-30 min) — breadth coverage
2. **Supplementary**: GDELT DOC API (targeted diaspora queries, polled every 30-60 min) — gap-filling
3. **Future/Optional**: Perigon Stories API — if budget allows, replaces custom clustering with pre-clustered events
4. **Direct feeds**: RSS from key diaspora outlets (The Hindu, Hindustan Times, NDTV, Times of India, BBC South Asia, etc.) — higher reliability than Google News intermediation

---

## 5. Story Clustering & Deduplication

### 5.1 The Two-Stage Problem

The Videshi's pipeline must solve two distinct problems that are often conflated:

**Stage 1: Signal Deduplication** — "Is this article reporting the same facts as another article I've already seen?"
- Same event, same facts, different publications
- Solution: Near-duplicate detection (fast, mechanical)

**Stage 2: Story Clustering** — "Which articles are about the same story/topic?"
- Related articles covering different angles of the same event
- Solution: Semantic clustering with entity and time signals

These must run sequentially: dedup first (cheap, fast, removes 60-80% of volume), then cluster the remaining unique signals (expensive, slower, but on a much smaller set).

### 5.2 Stage 1: Signal Deduplication — Recommended Approach

**Primary method: LSH (MinHash)**
- Locality Sensitive Hashing with MinHash signatures for O(1) duplicate lookup
- Threshold: ~80% text similarity (Feedly's proven threshold)
- Library: Hugging Face's **DataTrove** provides production-grade MinHash dedup

**Supplementary method: Title normalization** (from MediaCloud)
- Strip publisher name from title
- Lowercase, remove punctuation
- Same-source, same-day matching on normalized titles
- Catches duplicates that LSH might miss due to different article bodies but identical headlines

**Neural fallback: Bi-encoder similarity**
- For signals that pass LSH but seem suspiciously similar
- Encode titles with SBERT, flag pairs above 0.9 cosine similarity
- More expensive but catches paraphrased duplicates

**Cluster propagation** (from Feedly):
- When a new signal is identified as a duplicate of something already in a cluster, immediately assign it to that cluster
- Bypass the batch clustering step entirely for these signals
- This handles the majority of incoming signals with minimal computation

### 5.3 Stage 2: Story Clustering — Recommended Approach

**Algorithm: HDBSCAN** on a three-signal distance matrix:

```
distance(a, b) = w_s * semantic_dist(a, b) 
               + w_e * entity_dist(a, b) 
               + w_t * time_dist(a, b)
```

Where:
- `semantic_dist` = 1 - cosine_similarity(embedding_a, embedding_b) using SBERT embeddings of one-sentence summaries
- `entity_dist` = 1 - jaccard_similarity(entities_a, entities_b) using NER-extracted entities
- `time_dist` = normalized time gap (0 = same time, 1 = >3 days apart)

**Suggested starting weights** (tune empirically):
- w_s = 0.4 (semantic similarity)
- w_e = 0.4 (entity overlap — high weight for diaspora relevance)
- w_t = 0.2 (time decay)

**Window**: 3-day rolling window (aligned with academic finding that story chains are most relevant for ~3 days).

**Embedding strategy**: Generate one-sentence summaries via cheapest LLM (GPT-4o mini), then embed summaries with `all-MiniLM-L6-v2` (free, local, fast). Embedding the summary rather than the full text or just the title is the empirically best approach.

### 5.4 The Hardest Problem: New Development vs. Duplicate Coverage

This is the gap where no existing tool or technique fully solves the problem:

> "India announces new semiconductor fab" published on Monday. On Tuesday, 15 articles report the same announcement. On Wednesday, 3 articles report that TSMC will partner on the fab. The Tuesday articles are duplicates; the Wednesday articles are new developments on the same story.

**Current state of the art**: No off-the-shelf system reliably distinguishes these. Academic work on "story chains" and "event evolution" addresses this theoretically, but practical implementations are thin.

**Recommended approach for The Videshi** — a two-pass LLM check:

1. **Pass 1 (cheap, fast)**: Binary classification — "Does this signal contain information not present in the existing cluster summary?" Use GPT-4o mini with the cluster's current summary + the new signal's title/snippet. Cost: ~$0.001 per check.

2. **Pass 2 (if Pass 1 says "yes")**: Deeper analysis — "What specific new information does this signal add?" Use GPT-4o mini with more context (full cluster summary + new signal's extracted text). Outputs: new facts, new entities, updated timeline. Cost: ~$0.005 per check.

This is where the pipeline's editorial judgment lives, and it's the component most likely to need iteration and tuning after deployment.

---

## 6. Story Timeline & Evolution Tracking

### 6.1 Academic Approaches

**Story Disambiguation (Entity Graphs + Learning-to-Rank)**:
- Represents each story as a graph of entities and their relationships
- Uses a learning-to-rank framework to match new articles to existing story threads
- Semi-supervised updates allow the story model to evolve as new information arrives
- Relevant for multi-day stories like elections, policy changes, or ongoing crises

**newsLens System (Batch + Cross-Time Linking)**:
- Processes articles in time batches, computing topic centroids for each batch
- Links centroids across batches to form story timelines
- Simple but effective for editorial dashboards — shows "how did this story evolve?"

**LLM-Based Timeline Summarization**:
- **TimelineReasoner**: Uses a "global event memory" + agentic loop for iterative refinement of story timelines
- **NTS-CoT (News Timeline Summarization with Chain-of-Thought)**: Uses chain-of-thought reasoning to reduce hallucinations when summarizing story evolution

### 6.2 Recommendation for The Videshi

Story timeline tracking is a **Phase 2 feature** — valuable but not critical for launch. The initial pipeline should:

1. Maintain a cluster summary that updates as new signals arrive (incremental summarization)
2. Track the list of sources and timestamps within each cluster
3. Flag when a cluster receives new signals after 24+ hours of inactivity (potential "story resurgence")

Full timeline visualization and evolution tracking can be built later using the cluster metadata.

---

## 7. Editorial Intelligence

### 7.1 The Diaspora Gate

The Videshi's core editorial filter: "Is this story relevant to the Indian diaspora?"

**Current approach**: LLM classification (GPT-4o mini) on every signal.

**Recommended V2 approach — a cascading filter**:

1. **Keyword pre-filter** (zero LLM cost): Check title + snippet against a curated keyword list (diaspora, NRI, OCI, immigration, visa, H-1B, Indian-American, etc.). If strong keyword match → auto-pass. If strong negative match (purely domestic Indian politics with no diaspora angle) → auto-reject.

2. **Cheap LLM binary gate** (GPT-4o mini or Mistral Small): For signals that don't match keyword rules, run a binary yes/no classification. The prompt should be tight: "Would this story be relevant to an Indian living in the US, UK, Canada, Australia, or the Middle East? Answer only YES or NO."

3. **Confidence-based escalation**: If the cheap model outputs low confidence (which can be approximated via logprobs or by asking for a confidence score), escalate to a more capable model for a second opinion.

**Cost estimate**: With keyword pre-filter handling 40-60% of signals, and the cheap LLM gate handling the rest, the total cost for diaspora classification across ~113K signals would be approximately:
- 50K signals × ~200 tokens each × $0.15/1M input + $0.60/1M output ≈ **$1.50-$2.50/day**

### 7.2 Story Prioritization

After clustering and diaspora gating, the pipeline needs to prioritize which stories to write:

**Signals for prioritization** (weighted):
- Cluster size (more sources = bigger story)
- Source authority (tier-1 outlets vs. blogs)
- Recency (freshness premium)
- Topic category alignment (politics, business, tech, culture, sports)
- Diaspora relevance strength (does the story directly affect diaspora, or is it tangentially relevant?)
- Novelty (is this a new topic or an update to something already published?)

**Implementation**: A scoring function, not an LLM call. Each signal gets a numeric priority score based on weighted features. LLM judgment is reserved for the harder editorial questions (should we cover this controversial topic? what angle?).

### 7.3 Article Type Routing

Not every story needs the same treatment. V2 should route stories to different generation paths:

| Story Type | Volume | Generation Method | Human Review |
|---|---|---|---|
| Breaking news | 5-10/day | Fast summary from cluster sources | Post-publish review |
| Standard coverage | 40-50/day | Full article from cluster sources | Optional spot-check |
| Analysis/feature | 5-10/day | LLM draft with heavy source grounding | Pre-publish review |
| Data stories (markets, scores) | 10-15/day | Template-based with data slot-filling | None needed |
| Sensitive topics | 2-5/day | Human-written or heavily edited LLM draft | Mandatory pre-publish |

---

## 8. Quality, Trust & Hallucination Prevention

### 8.1 The Core Risk

Automated news article generation faces a fundamental tension: LLMs are excellent at producing fluent, well-structured prose but will confidently fabricate facts, quotes, statistics, and attributions when their training data doesn't contain the specific information needed. For a news publication, a single fabricated quote or invented statistic can destroy credibility.

### 8.2 Multi-Layer Prevention Architecture

Research consistently shows that **no single technique is sufficient**. The recommended approach layers multiple defenses:

#### Layer 1: Source-Grounded Prompts (Pre-Generation)

The most effective hallucination prevention happens before generation begins:

- **Strict source constraint**: "Write this article using ONLY the information in the following source excerpts. Do not add any facts, quotes, statistics, or claims not present in these sources."
- **Tagged-context prompting**: Each source excerpt is tagged with its origin (`[Source: Reuters, June 15]`, `[Source: Hindustan Times, June 15]`), and the model is instructed to cite sources inline.
- **Constrained output schema**: Define the article structure (headline, summary, body paragraphs, sources) as a JSON schema. This forces the model to fill specific fields rather than free-generating, reducing drift.
- **"If not found, say so" instruction**: Explicitly instruct the model to write "Information not available in sources" rather than inventing answers to gaps.

#### Layer 2: Retrieval-Augmented Generation (During Generation)

For The Videshi's use case, RAG is built into the pipeline design:

- The clustering step already aggregates multiple source articles per topic
- The article writer receives the full text (or key excerpts) of all cluster sources
- This is effectively RAG without the vector database — the "retrieval" is done by the clustering pipeline

**Key insight from research**: RAG still hallucinates when (a) retrieval fails (no relevant sources), (b) context is noisy (too many irrelevant sources mixed in), (c) the model ignores evidence in favor of parametric knowledge, or (d) prompts are too open-ended. Mitigations: curate cluster sources to remove noise, use specific prompts, and always verify post-generation.

#### Layer 3: Post-Generation Verification ("Generate then Check")

A two-pass system is the most production-proven approach:

1. **Claim extraction**: Parse the generated article into atomic claims (e.g., "India's GDP grew 6.7% in Q2" or "PM Modi met with President Biden on Thursday").

2. **Source matching**: For each claim, check whether it appears in (or can be inferred from) the source materials provided to the generator. Claims without source support are flagged.

3. **Action on flags**: Three options depending on severity:
   - Remove the unsupported claim
   - Add a "could not verify" disclaimer
   - Reject the article for human review

**Cost**: The verification pass roughly doubles the LLM cost per article, but only needs to run on the article text (not the full source materials), keeping it manageable.

#### Layer 4: Structural Safeguards

- **No "creative" generation**: The pipeline should never ask the LLM to "write an engaging article about X" with no source material. Every article generation call must include source texts.
- **Quote attribution**: If the generated article contains a quote, the pipeline should verify that the exact quote (or a close paraphrase) appears in at least one source. Fabricated quotes are the highest-damage hallucination type.
- **Number verification**: Statistics, percentages, monetary amounts, and dates extracted from the generated article should be cross-checked against source materials. Numerical hallucinations are common and damaging.
- **Entity consistency**: Named entities in the generated article should all appear in the source materials. New entities not in sources are a hallucination signal.

### 8.3 Quality Assurance Pipeline

Beyond hallucination prevention, overall article quality requires:

1. **Style consistency**: Enforce The Videshi's editorial style via system prompt or few-shot examples. Template structures help maintain consistency across articles.

2. **Factual freshness**: Ensure the model uses information from the cluster sources, not from its training data. A common failure mode: the model "knows" outdated information about a topic and mixes it with current source data.

3. **Plagiarism avoidance**: While LLMs generally paraphrase rather than copy verbatim, articles generated from a single source can be too close to the original. The pipeline should check that no paragraph is >70% similar to any single source.

4. **Automated scoring**: Run a quality gate on every generated article:
   - Readability score (length, complexity)
   - Source citation count (minimum 2 sources per article)
   - Claim density (facts per paragraph)
   - Entity coverage (% of source entities mentioned)
   - Headline-body alignment

### 8.4 Human Oversight Model

Even with all automated safeguards, some human oversight is essential:

- **Pre-publish review**: For sensitive topics (politics, religion, communal issues), controversial stories, and stories with high public interest. The pipeline flags these automatically.
- **Post-publish spot-checks**: Random sampling of 5-10% of published articles for quality audit. Results feed back into prompt tuning.
- **Reader feedback loop**: Mechanism for readers to report factual errors. These reports trigger re-verification of the specific article and inform pipeline improvements.

---

## 9. Pipeline Architecture

### 9.1 Streaming vs. Batch vs. Hybrid

**Full streaming (Kafka, Flink, etc.)**: Overkill for The Videshi. These systems are designed for millions of events/second with sub-second latency requirements. The Videshi processes ~113K signals/day (~1.3/second average) and doesn't need sub-minute latency. The infrastructure complexity, operational overhead, and cost are not justified.

**Pure batch (hourly/daily crons)**: The current approach. Works but creates fragmentation (many independent cron jobs), makes it hard to maintain state across runs, and introduces unnecessary latency (stories that arrive at minute 1 wait until the next batch at minute 60).

**Recommended: Tight polling loop with unified pipeline**:

The key principle: "Stop asking 'when should this run?' Start asking 'what should trigger this?'" But for RSS feeds, polling IS the trigger — RSS doesn't push. So the architecture should be:

- A single "orchestrator" process that runs continuously (or on a very tight interval, e.g., every 15 minutes)
- Each run: poll all RSS feeds → dedup → cluster → prioritize → write → publish
- State persists in PostgreSQL (Supabase) between runs
- No separate crons for different pipeline stages — one unified flow

### 9.2 Recommended Pipeline Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    SIGNAL INGESTION                          │
│  Google News RSS (79 feeds) + GDELT DOC API + Direct RSS    │
│  Poll every 15-30 min                                        │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    DEDUPLICATION                              │
│  1. URL normalization                                        │
│  2. Title normalization (strip publisher, lowercase)         │
│  3. LSH (MinHash) on title+snippet (>80% → duplicate)       │
│  4. Cluster propagation (dup of clustered → inherit cluster) │
│  Cost: ~$0/day (no LLM)                                     │
└──────────────────────────┬──────────────────────────────────┘
                           │ (unique signals only)
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    ENRICHMENT                                │
│  1. Full article extraction (newspaper3k / readability)      │
│  2. One-sentence summary (cheapest LLM)                      │
│  3. NER extraction (spaCy or LLM)                            │
│  4. Sentence embedding (all-MiniLM-L6-v2, local)            │
│  Cost: ~$0.50-1.00/day (LLM summaries only)                 │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    DIASPORA GATE                              │
│  1. Keyword pre-filter (zero cost)                           │
│  2. LLM binary classification (GPT-4o mini)                  │
│  Cost: ~$1.50-2.50/day                                       │
└──────────────────────────┬──────────────────────────────────┘
                           │ (diaspora-relevant signals only)
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    STORY CLUSTERING                           │
│  HDBSCAN on 3-signal distance matrix                         │
│  (semantic + entity + time) over 3-day window                │
│  Cost: ~$0/day (embeddings already computed)                 │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    EDITORIAL PRIORITIZATION                   │
│  1. Cluster scoring (size, source authority, recency)        │
│  2. New-development detection (LLM: does this cluster        │
│     contain info not in already-published articles?)         │
│  3. Article type routing                                     │
│  Cost: ~$0.50-1.00/day                                       │
└──────────────────────────┬──────────────────────────────────┘
                           │ (top-priority clusters)
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    ARTICLE GENERATION                        │
│  1. Source-grounded writing (LLM with cluster sources)       │
│  2. Post-generation verification (claim extraction + check)  │
│  3. Quality gate (automated scoring)                         │
│  4. Image sourcing (Commons, source images)                  │
│  Cost: ~$1.50-2.50/day                                       │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    PUBLISH & MONITOR                          │
│  1. Write to Supabase                                        │
│  2. Vercel rebuild trigger                                   │
│  3. Post-publish quality spot-check                          │
│  4. Performance tracking (views, dwell time)                 │
└─────────────────────────────────────────────────────────────┘
```

### 9.3 State Management

All pipeline state in PostgreSQL (Supabase):

| Table | Purpose |
|---|---|
| `signals` | Raw ingested signals with dedup status |
| `signal_embeddings` | Vector embeddings for clustering |
| `clusters` | Active story clusters with summary, entities, scores |
| `cluster_signals` | Junction: which signals belong to which cluster |
| `articles` | Generated articles with quality scores |
| `article_sources` | Attribution: which sources contributed to which article |
| `pipeline_runs` | Audit log of each pipeline execution |

**pgvector extension** for Supabase: Enables vector similarity search directly in PostgreSQL, avoiding the need for a separate vector database (FAISS, Pinecone, etc.). Supabase supports pgvector natively.

### 9.4 Unified Script Architecture

Replace the current fragmented cron jobs with a single orchestrator:

```python
# pipeline_v2.py — single entry point
def run_pipeline():
    # 1. Ingest signals from all sources
    new_signals = ingest_all_sources()
    
    # 2. Dedup against existing signals
    unique_signals = dedup(new_signals)
    
    # 3. Enrich unique signals
    enriched = enrich(unique_signals)  # extract, summarize, NER, embed
    
    # 4. Diaspora gate
    diaspora_signals = diaspora_filter(enriched)
    
    # 5. Update clusters
    clusters = update_clusters(diaspora_signals)
    
    # 6. Prioritize and select
    stories = prioritize(clusters)
    
    # 7. Generate articles
    articles = generate_articles(stories)
    
    # 8. Quality gate and publish
    publish(articles)
```

A single cron job runs `pipeline_v2.py` every 15-30 minutes. Each step is idempotent — safe to re-run on failure. State transitions are recorded in PostgreSQL, so a crash at step 5 doesn't re-process steps 1-4 on the next run.

---

## 10. LLM Cost Optimization

### 10.1 Current Pricing Landscape (2026)

| Model | Input/1M tokens | Output/1M tokens | Context | Best For |
|---|---|---|---|---|
| **Mistral Small 3.2** | $0.06 | $0.18 | 128K | Absolute cheapest — binary classification |
| **GPT-4o mini** | $0.15 | $0.60 | 128K | Best value for editorial decisions |
| **DeepSeek V3** | $0.25 | $1.10 | 128K | Open source, cheap |
| **Gemini Flash Lite** | $0.25 | $1.50 | 1M | Bulk classification/triage |
| **Gemini 2.5 Flash** | $0.30 | $2.50 | 1M | Good balance, large context |
| **GPT-4.1 mini** | $0.40 | $1.60 | 1M | Upgraded GPT-4o mini |
| **Llama 4 Scout** | $0.11 | $0.34 | 10M | Open source, huge context |
| **Claude Haiku 4.5** | $1.00 | $5.00 | 200K | Best instruction following |

**Note**: Gemini models are currently unavailable to The Videshi due to Google Cloud billing being blocked.

### 10.2 Model Routing Strategy

The key insight from cost research: **model routing** — classifying task complexity with the cheapest model and routing to the appropriate tier — can cut costs 50-70%.

**Tier 1 — Binary Classification** (cheapest model):
- Diaspora yes/no gate
- Duplicate yes/no check
- Is this signal newsworthy? yes/no
- **Model**: GPT-4o mini ($0.15/$0.60) or Mistral Small 3.2 ($0.06/$0.18) if accessible
- **Volume**: ~113K signals/day × ~200 tokens each ≈ 23M tokens/day
- **Cost**: ~$3.50/day at GPT-4o mini rates, ~$1.40/day at Mistral Small rates

**Tier 2 — Structured Extraction** (mid-tier model):
- One-sentence summary generation
- Entity extraction
- Article type classification
- New-development detection
- **Model**: GPT-4o mini ($0.15/$0.60)
- **Volume**: ~20-30K unique signals/day × ~500 tokens each ≈ 10-15M tokens/day
- **Cost**: ~$1.50-2.25/day

**Tier 3 — Article Writing** (capable model):
- Full article generation from cluster sources
- Post-generation verification
- Quality scoring
- **Model**: GPT-4o mini or GPT-4.1 mini for standard articles; GPT-4o for complex analysis pieces
- **Volume**: 65-80 articles/day × ~3,000 tokens each (input + output) ≈ 200-240K tokens/day
- **Cost**: ~$0.15-0.40/day (surprisingly cheap because article count is low relative to signal count)

### 10.3 Projected Daily Cost Budget

| Pipeline Stage | Estimated Daily Cost |
|---|---|
| Signal classification & gating | $1.50-2.50 |
| Enrichment (summaries, NER) | $0.50-1.00 |
| Editorial decisions (prioritization, new-dev detection) | $0.50-1.00 |
| Article generation | $0.50-1.00 |
| Quality verification | $0.25-0.50 |
| **Total** | **$3.25-6.00** |

This fits within the $5-6/day budget, with room for the lower end of estimates if keyword pre-filtering is effective at reducing the LLM classification volume.

### 10.4 Cost Reduction Levers

If costs exceed budget:

1. **Aggressive keyword pre-filtering**: Can eliminate 40-60% of signals before any LLM call
2. **Batch prompting**: Send multiple signals in a single LLM call (10-20 per call) with structured output. Reduces per-call overhead.
3. **Caching**: Cache embeddings and classifications. Signals from the same source on the same day are often duplicates that should hit cache.
4. **Local models**: For simple binary classification, a fine-tuned local model (DistilBERT, ~66M params) could run on CPU for zero marginal cost. Training data: historical diaspora yes/no classifications.
5. **Prompt optimization**: Shorter, tighter prompts reduce token count. Every word in the system prompt is multiplied by 113K signals/day.

---

## 11. Open Source Tooling

### 11.1 Recommended Stack

| Tool | Purpose | Install | Notes |
|---|---|---|---|
| **HDBSCAN** | Density-based clustering | `pip install hdbscan` | No k required, handles noise |
| **sentence-transformers** | SBERT embeddings | `pip install sentence-transformers` | Model: `all-MiniLM-L6-v2` (fast, good quality) |
| **DataTrove** | Production MinHash dedup | `pip install datatrove` | From Hugging Face, battle-tested |
| **feedparser** | RSS parsing | `pip install feedparser` | Standard, reliable |
| **newspaper3k** | Full article extraction | `pip install newspaper3k` | Handles paywall-free sites; may need `newspaper4k` for maintained version |
| **spaCy** | NER extraction | `pip install spacy` | Model: `en_core_web_sm` for speed, `en_core_web_trf` for accuracy |
| **FAISS** | Vector similarity search | `pip install faiss-cpu` | From Facebook; alternative: use pgvector in Supabase directly |
| **pgvector** | Vector search in PostgreSQL | Supabase native | Avoids separate vector DB |
| **pygooglenews** | Google News RSS client | `pip install pygooglenews` | Wraps Google News RSS with Python interface |

### 11.2 Infrastructure

| Component | Current | V2 Recommendation |
|---|---|---|
| Database | Supabase (PostgreSQL) | Keep — add pgvector extension |
| LLM API | OpenAI (GPT-4o mini) | Keep as primary; add Mistral as cost fallback |
| Hosting | Vercel (frontend) | Keep |
| Pipeline runner | Cron jobs | Single unified script on tight interval |
| Embeddings | None | Local SBERT (`all-MiniLM-L6-v2`) |
| Article extraction | Custom/ad hoc | `newspaper3k` / `newspaper4k` |

---

## 12. Synthesized Architecture Recommendation

### 12.1 Implementation Phases

#### Phase 1: Foundation (Weeks 1-3)
**Goal**: Unified pipeline with dedup and basic clustering

1. Build the unified `pipeline_v2.py` orchestrator
2. Implement LSH dedup (DataTrove MinHash) + title normalization
3. Set up pgvector in Supabase for embedding storage
4. Implement SBERT embedding pipeline (local, no LLM cost)
5. Port existing diaspora gate with keyword pre-filter optimization
6. Basic HDBSCAN clustering on semantic distance only (single signal)
7. **Ship**: Replace fragmented crons with single 15-min pipeline

#### Phase 2: Intelligence (Weeks 4-6)
**Goal**: Three-signal clustering, editorial prioritization, new-development detection

1. Add NER extraction (spaCy) as second clustering signal
2. Add time decay as third clustering signal
3. Tune HDBSCAN weights empirically
4. Build priority scoring function
5. Implement new-development detection (LLM comparison against published articles)
6. Add article type routing
7. **Ship**: Smarter story selection, fewer duplicate articles

#### Phase 3: Quality (Weeks 7-9)
**Goal**: Hallucination prevention, automated quality gates

1. Implement source-grounded article generation prompts
2. Build post-generation verification pipeline (claim extraction + source matching)
3. Add automated quality scoring gate
4. Implement quote and number verification
5. Build human review queue for sensitive topics
6. **Ship**: Higher-quality articles, fewer factual errors

#### Phase 4: Optimization (Weeks 10-12)
**Goal**: Cost optimization, performance feedback, advanced features

1. Implement model routing (cheapest model per task)
2. Add batch prompting for signal classification
3. Build performance feedback loop (which articles get read?)
4. Add GDELT as supplementary source
5. Implement story timeline tracking (nice-to-have)
6. **Ship**: Lower costs, better story selection based on reader behavior

### 12.2 Key Design Decisions

| Decision | Recommendation | Rationale |
|---|---|---|
| Clustering algorithm | HDBSCAN | No k needed, handles noise, handles varying cluster sizes |
| Clustering signals | Semantic + Entity + Time | Prevents over-broad clusters; Entity especially important for diaspora |
| Embedding model | `all-MiniLM-L6-v2` (local) | Free, fast, good quality; embed one-sentence summaries |
| Dedup method | LSH (MinHash) first, then bi-encoder | Fast pre-filter + accurate neural fallback |
| Diaspora gate | Keyword pre-filter → LLM binary | Cuts LLM cost 40-60% |
| LLM for classification | GPT-4o mini | Best cost/quality ratio for binary decisions |
| LLM for writing | GPT-4o mini (standard) / GPT-4o (complex) | Standard articles don't need expensive models |
| Vector store | pgvector (Supabase native) | No new infrastructure |
| Pipeline architecture | Single unified script, 15-min interval | Replaces fragmented crons, maintains state |
| Article verification | Post-generation claim extraction + source matching | Most production-proven approach |
| Story timeline | Phase 2/deferred | Nice-to-have, not launch-critical |

### 12.3 Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Hallucinated facts in published articles | Medium | Critical | Multi-layer verification, human review for sensitive topics |
| Over-broad clusters (unrelated stories merged) | Medium | High | Entity signal + time decay prevent this; tune weights |
| Missed stories (under-clustering) | Low-Medium | High | Err toward more clusters (lower HDBSCAN min_cluster_size); recall > precision |
| LLM cost overrun | Low | Medium | Keyword pre-filtering, batch prompting, cost monitoring alerts |
| Google News RSS rate limiting | Low | High | Add GDELT + direct RSS feeds as fallbacks |
| Single point of failure (unified script) | Medium | Medium | Idempotent steps, crash recovery from PostgreSQL state |
| OpenAI API outage | Low | High | Add Mistral/DeepSeek as fallback LLM providers |

### 12.4 Success Metrics

| Metric | Current (estimated) | V2 Target |
|---|---|---|
| Story coverage (% of important diaspora stories covered) | ~70-80% | >95% |
| Duplicate articles published | ~10-15% of total | <2% |
| Factual accuracy (spot-check sample) | Unknown | >98% of claims source-verified |
| Time to publish (signal → article) | 1-4 hours (batch dependent) | <45 minutes |
| Daily LLM cost | ~$5-6 | ~$3.50-5.00 |
| Pipeline reliability (successful runs / attempted runs) | Fragmented (varies by cron) | >99% |

---

## Appendix A: Key References & Sources

- Feedly's dedup and clustering architecture (Feedly engineering blog)
- Zeyong Cai's news aggregator series (Medium) — three-signal clustering with HDBSCAN
- Reuters News Tracer — production-scale event detection
- MediaCloud dedup approach — title/URL normalization
- Academic: Agglomerative clustering + SentenceBERT for story chain detection
- Academic: Story disambiguation via entity graphs
- Academic: TimelineReasoner and NTS-CoT for timeline summarization
- Semafor Signals — AI-assisted journalism model
- AP Wordsmith — template-based NLG for structured content
- Artifact/Yahoo — transformer-based recommendation with dwell time
- GDELT Project — free global news database
- Perigon API — pre-clustered news stories endpoint
- Stack Overflow blog — assertion gating and journalistic principles for AI

## Appendix B: Glossary

- **LSH (Locality Sensitive Hashing)**: A technique for finding similar items in large datasets in O(1) time by hashing similar items to the same bucket
- **MinHash**: A specific LSH scheme that estimates Jaccard similarity between sets (used for document dedup)
- **HDBSCAN**: Hierarchical Density-Based Spatial Clustering of Applications with Noise — a clustering algorithm that finds dense regions of varying density
- **SBERT**: Sentence-BERT — BERT fine-tuned to produce sentence-level embeddings that capture semantic meaning
- **NER**: Named Entity Recognition — extracting people, places, organizations, etc. from text
- **RAG**: Retrieval-Augmented Generation — grounding LLM outputs in retrieved documents
- **pgvector**: PostgreSQL extension for vector similarity search
- **Cluster propagation**: Feedly's technique of assigning duplicates to existing clusters without re-running batch clustering
