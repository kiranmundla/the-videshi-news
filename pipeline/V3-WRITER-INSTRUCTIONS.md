# V3 Writer Cron Body — Article Quality Standard

## Step 1 — Run V3 selector
```
cd ~/workspace/the-videshi-news/pipeline && timeout 900 python3 -u v3-select.py --per-cat 3 2>&1
```

## Step 2 — Read candidates
Read `/tmp/v3-candidates.json`. It has a `candidates` array — each entry has `topic_id`, `title`, `category`, `llm_score`, `coverage` ("new" or "update"), `source_urls`, `all_signals`, and `llm_reason`.

Write ONLY these candidates. Do NOT generate additional articles beyond what's in this JSON.

## Step 3 — Write articles (ONLY from candidates)

For each candidate in the JSON array:

### 3a. Dedup check FIRST
Query `p2_articles` for articles with similar headlines in the last 3 days:
`GET /rest/v1/p2_articles?select=headline&created_at=gte.<3 days ago>&status=eq.published&limit=200`
If a published article already covers the same story, SKIP this candidate.

### 3b. Read source material
If the candidate has `source_urls`: read 2-4 of them via `browser_open` to get actual article text. Also check the `all_signals` array for additional source URLs.

**If source_urls is empty (no linked signals):** Use `browser_search` with the candidate's `title` to find 2-3 actual news articles about the topic. Read the top results. The title always contains the original headline and source name, so the search will find the right articles.

Cross-reference multiple sources — never rewrite a single wire story.

### 3c. Write the article — PROFESSIONAL JOURNALISM STANDARD

You are writing for The Videshi, a professional news publication for the Indian diaspora. Write like a senior journalist at Reuters, Bloomberg, or The Economist. Every article must include these structural elements:

#### HEADLINE
- Clear, informative, engaging. No clickbait. 8-14 words.
- For `coverage: "update"`: Lead with what's NEW (e.g., "Court Reverses H-1B Ban After..." not "H-1B Update")

#### KEY TAKEAWAYS (required — appears at top of body)
- 3-4 bullet points summarizing the essential facts
- Written so a busy reader gets the full picture in 10 seconds
- Use `<div class="key-takeaways">` wrapper in the HTML body — NO heading tag inside
- Format: `<div class="key-takeaways"><ul><li>...</li></ul></div>`
- Do NOT include a `<h3>Key Takeaways</h3>` or any heading — the styling handles it. Just the bullets.

#### ARTICLE BODY (500-800 words, HTML format)
Structure with clear `<h2>` subheadings. Must include:

1. **Opening paragraph** — The news lead. What happened, who's involved, why it matters. No fluff, no "In a significant development..." — just the news.

2. **Context & Background** — What led to this? What's the history? NRIs especially need context because they may not follow every thread of a story. Provide the background a smart reader needs to understand WHY this matters, not just WHAT happened. This is what separates professional journalism from press-release rewrites.

3. **Impact & Analysis** — What does this mean going forward? Who benefits, who's affected? For policy/regulation stories: concrete examples of how this changes things.

4. **Diaspora Angle** (when natural, not forced) — How does this affect Indians abroad? For immigration: direct impact. For markets: portfolio implications. For culture: community connection. For some stories (pure global news), a brief line is fine. NEVER force a diaspora angle where none exists — it reads as amateur.

5. **What's Next / Looking Ahead** — What to watch for. Next steps, upcoming decisions, timeline.

#### WRITING RULES
- Write from source material only — no parametric knowledge, no fabrication
- Include source citations naturally ("according to Reuters," "the USCIS announced")
- **Pull quotes**: When an article has a strong, important quote from a key figure, use a styled blockquote to make it stand out:
  ```html
  <blockquote class="pull-quote">
    <p>"The goal is straightforward: to ensure the Fed is best positioned to achieve our objectives in this consequential time."</p>
    <cite>— Kevin Warsh, Federal Reserve Chairman</cite>
  </blockquote>
  ```
  Use 1-2 pull quotes per article maximum. Only for genuinely impactful quotes that capture the story's essence — not filler quotes. **NEVER repeat the same pull quote — each must be unique text.**
- NO generic filler phrases: "In a significant development," "It is worth noting," "This comes at a time when"
- NO sycophantic qualifiers: "importantly," "notably," "interestingly"
- Vary sentence length. Short punchy sentences mixed with longer analytical ones.
- Use specific numbers, dates, names — concrete details, not vague summaries
- For markets-finance: US/global-first tone, straight financial journalism. No forced NRI framing on FAANG earnings or Fed decisions.
- For food: Indian-specific focus, recipes and cultural context
- For entertainment: Cover both Bollywood and Hollywood with equal depth

### 3d. Hero Image — Use image_sourcer.py (DO NOT source manually)

**Insert the article FIRST with `image_url` set to null**, then run the automated image sourcer:

```bash
cd ~/workspace/the-videshi-news/pipeline
python3 -u image_sourcer.py --slug <article-slug> --apply
```

This runs the full 7-source image chain automatically:
1. og:image from source articles (decodes Google News URLs, ranks by domain quality)
2. RSS feed thumbnails from p2_signals
3. Media library cache (person_images table)
4. YouTube thumbnails (entity-specific, with title match gate)
5. Wikipedia person images
6. Wikimedia Commons search
7. Pexels fallback

It also computes focal points for face-aware cropping and updates the DB directly.

The script outputs `IMAGE_RESULT:{...}` JSON with the result. Check the output to confirm it found an image.

**If you need caption text for a specific article**, the sourcer uses the first entity name as a basic caption. For better captions, you can PATCH the `image_caption` field after the sourcer runs.

**Image Caption Rules (when writing/updating captions):**
- Two sentences. First: what the image shows. Second: the news context.
- Factual, plain style. Describe what is literally in the image.
- NO flowery bridging: "symbolizing," "reflects," "illustrating," "representing"
- NO speculation about what's not visible in the image
- Person identity must match — exact name, recent/current photo
- Example: "Indian Prime Minister Narendra Modi addresses Parliament during the Budget session. The government announced new tax incentives for returning NRIs."

**⚠️ CRITICAL — A wrong image is worse than no image:**
If the sourcer returns no image, leave `image_url` as null. A missing image is always better than a wrong one. The enrichment pipeline will attempt again later.

**⚠️ DO NOT manually source images by calling Wikipedia/Pexels/og:image APIs yourself.** The script handles all of this with proper verification, Google News URL decoding, HTTP validation, and deduplication. Manual sourcing is slow, error-prone, and the #1 cause of missing hero images.

### 3e. Insert into p2_articles
Insert with `status="published"`. Required fields:
- `headline`, `subheadline` (1-2 sentence summary for display below headline and on cards — NOT the key takeaways), `body` (HTML), `slug`, `category`, `vertical` (same as category)
- `tags` (array), `sources` (array of source URLs used)
- `image_url`, `image_caption`, `image_attribution`
- `word_count`, `diaspora_angle` (1-sentence summary)
- `topic_id` (from candidate JSON)
- `llm_score` (from candidate JSON — the selector's relevance score, 1-5)
- `published_at` (NOW), `article_type` (default 'breaking')

### 3f. Update topic status
After successful article insert, PATCH the p2_topics row:
`PATCH /rest/v1/p2_topics?id=eq.<topic_id>` with `{"status": "published", "last_article_id": "<new_article_id>"}`

## Step 4 — Polish articles (one GPT call: takeaways + data cards + proofread)
After inserting each article, run the combined polish script on it:

```bash
cd ~/workspace/the-videshi-news/pipeline
set -a; source ~/workspace/.env.supabase; source ~/workspace/.env.openai; set +a

# One GPT-4o-mini call per article: key_takeaways JSON, data_cards JSON, grammar/image proofread
python3 -u article-polish.py --article-id <article_uuid> 2>&1
```

This replaces three separate GPT calls (enrich-data-cards, enrich-on-publish key_takeaways, proofread-article) with a single call. Run it per article right after insert. If it fails, continue — the article is published and readable, and the review-articles safety net will catch issues later.

## Step 4.2 — Enrich articles (social embeds, inline images)
After polishing, run social embed enrichment (no GPT — just API lookups):

```bash
cd ~/workspace/the-videshi-news/pipeline
set -a; source ~/workspace/.env.supabase; source ~/workspace/.env.openai; source ~/workspace/.env.google-ai; source ~/workspace/.env.pexels 2>/dev/null; source ~/workspace/.env.twitterapi-io; source ~/workspace/.env.apify; source ~/workspace/.env.youtube; set +a

# Social embeds (X, IG, YouTube) + hero image upgrade from tweet photos
timeout 180 python3 -u enrich-on-publish.py --hours 3 --apply 2>&1

# Inline images + pull quotes (body enrichment)
timeout 600 python3 -u enrich-articles.py --hours 3 --apply 2>&1
```

If any enrichment script fails, continue — articles are already published and readable.

## Step 4.3 — Hero Image Backfill (safety net)
After enrichment, backfill any articles still missing hero images:
```bash
cd ~/workspace/the-videshi-news/pipeline
python3 -u image_sourcer.py --backfill --hours 3 --apply 2>&1
```

## Step 5 — Rebuild feeds
```
cd ~/workspace/the-videshi-news/pipeline && python3 -u prebuild-feeds.py 2>&1
```

## Step 6 — Commit and push
```
cd ~/workspace/the-videshi-news && git add -A && git commit -m "V3 pipeline articles $(date +%Y-%m-%d)" && git push origin main 2>&1
```

## RULES
- Write ONLY candidates from the JSON. No extras.
- Skip any candidate that duplicates an existing article.
- If `coverage` is "update" but dedup shows we already covered the SAME new development, skip.
- If the selector outputs 0 candidates, skip everything and report nothing.
- If an API error occurs mid-run, continue with remaining candidates.
- Every article MUST have Key Takeaways bullets at the top (no heading, just `<div class="key-takeaways"><ul>...</ul></div>`).
- Do NOT include an "At a Glance" / summary card table — we don't use those.
- Use 1-2 pull quotes per article when strong quotes exist: `<blockquote class="pull-quote"><p>"..."</p><cite>— Name, Title</cite></blockquote>`
- Image captions are factual plain style — two sentences, no flowery language.
- Images and video enrichment (inline body images, data cards, embeds) are handled by a SEPARATE enrichment pipeline after publish — the writer does NOT add those. The writer only handles the hero image.

Report a brief summary: headlines, categories, and total articles published.
