# V3 Writer Cron Body — Article Quality Standard

## Step 1 — Get the candidate list (selector already ran)
A dedicated selector job (videshi-v3-select) runs at :25, 20 minutes before this writer. CHECK FOR ITS OUTPUT FIRST — do not launch another selector unless none exists:
1. Look for a fresh candidate file (mtime < 45 min): `/tmp/v3-candidates.json`, then `~/workspace/the-videshi-news/pipeline/.state/v3-candidates.json` (persistent backup). If either exists, is fresh, and has a non-empty candidates array — use it and skip to Step 2.
2. Only if no fresh file exists: launch the selector DETACHED (nohup+disown — a bare `&` background is killed when the worker turn ends) and poll for its output — do NOT rely on a single blocking call:
```
cd ~/workspace/the-videshi-news/pipeline && nohup python3 -u v3-select.py --per-cat 3 > /tmp/v3-select.log 2>&1 & disown
```
Poll every 30s for up to 15 minutes until `/tmp/v3-candidates.json` has an mtime newer than the run start. The selector is lock-protected (exit 2 = another instance already running; just wait for its output), checkpoints scoring progress so killed runs don't lose work, and writes candidates atomically to both `/tmp` and a persistent backup. A backgrounded process is NOT a failure — wait for the file.
3. Last resort: use the persistent backup if it is < 6h old with a non-empty candidates array. Otherwise report the selector failure and stop — never write articles without a candidate list.

### 1b. Claim the candidate batch (prevents double-publish races)
Two writers must NEVER work the same candidate file — on 2026-09-14 two recovery runs processed the same batch and 7 duplicate articles went live. Before writing anything:
```bash
CAND=$(ls -t /tmp/v3-candidates.json ~/workspace/the-videshi-news/pipeline/.state/v3-candidates.json 2>/dev/null | head -1)
MTIME=$(stat -c %Y "$CAND"); NOW=$(date +%s)
CLAIM=~/workspace/the-videshi-news/pipeline/.state/v3-writer-claim.json
if [ -f "$CLAIM" ] && [ "$(python3 -c "import json;print(json.load(open('$CLAIM')).get('candidates_mtime'))")" = "$MTIME" ] && [ $((NOW - $(stat -c %Y "$CLAIM"))) -lt 21600 ]; then
  echo "CLAIMED: another writer already took this batch ($(cat $CLAIM)) — exiting"; exit 2
fi
python3 -c "import json,time;json.dump({'candidates_mtime':$MTIME,'claimed_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'run':'writer-'},open('$CLAIM','w'))"
echo "Batch claimed: $CAND (mtime $MTIME)"
```
If you see CLAIMED, stop immediately — do not write, do not publish. (Claims expire after 6h so a crashed run can't block the next slot forever; a fresh selector output always has a new mtime and is claimable.)

## Step 2 — Read candidates
Read `/tmp/v3-candidates.json`. It has a `candidates` array — each entry has `topic_id`, `title`, `category`, `llm_score`, `coverage` ("new" or "update"), `source_urls`, `all_signals`, and `llm_reason`.
Fallback: if `/tmp/v3-candidates.json` is missing or stale (>30 min old), use `~/workspace/the-videshi-news/pipeline/.state/v3-candidates.json` provided it is < 6h old and has a non-empty candidates array.

Write ONLY these candidates. Do NOT generate additional articles beyond what's in this JSON.

## Step 3 — Write articles (ONLY from candidates)

For each candidate in the JSON array:

### 3a. Dedup check FIRST
Query `p2_articles` for articles with similar headlines in the last 3 days:
`GET /rest/v1/p2_articles?select=headline&created_at=gte.<3 days ago>&status=eq.published&limit=200`
If a published article already covers the same story, SKIP this candidate — and close the loop so the selector stops re-serving it:
`PATCH /rest/v1/p2_topics?id=eq.<topic_id>` with `{"status": "rejected", "evaluated_at": "<now UTC ISO>"}`.
Without this write-back the topic stays `pending` and the selector re-selects it after its 6-hour cooldown, wasting a writer cycle every run until the topic ages out.

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
- **Reader-utility bullet (required where applicable):** at least one bullet must answer "what does this mean for ME?" with concrete specifics — dollar/rupee amounts, dates, deadlines, eligibility rules, or action steps. Write "H-1B renewals filed after October 1 carry a $100,000 fee per petition," not "fees are increasing significantly." For immigration, markets-finance, nri-world, travel, and lifestyle-health stories this bullet is mandatory. For pure global news with no direct reader impact, omit it — NEVER invent utility where none exists.

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

> **image_backfill_blocked:** some articles carry `image_backfill_blocked=true` (standing intentional-null decisions, e.g. no verified photo exists for the named person). The sourcer skips these automatically — never force an image onto them. If you later verify a real photo, apply it with `source-image.py`, which clears the block.

This runs the full image chain automatically:
1. og:image from source articles (decodes Google News URLs, ranks by domain quality; AI-generated og:images rejected by filename markers like `Gemini_`, `midjourney`, `dall-e`)
2. RSS feed thumbnails from p2_signals
3. Media library cache (person_images table)
4. YouTube thumbnails (entity-specific, with title match gate)
5. **Official source (writer-provided URL)** — if you pass `--official-url`, the sourcer fetches that page's image directly, no search needed
6. Official source auto-discovery (government/company domains via keyword matching)
7. PR Newswire press images
8. Wikipedia person images
9. Wikimedia Commons search
10. Pexels fallback (last resort; photo alt text must share a content word with the query or it is rejected as irrelevant)

**Official source URL (recommended for institutional stories):** When the story is about a government agency, company announcement, or official program — and you know the official page (e.g., the NASA press release, the ISRO announcement, the company's press page) — pass it directly:
```bash
python3 -u image_sourcer.py --slug <article-slug> --official-url "https://www.nasa.gov/news-release/..." --apply
```
This skips all search and pulls the official image straight from the source. It's the most reliable path — official images are topically perfect and copyright-safe (US government = public domain, Indian government = free for news use, company press = provided for media). The sourcer validates it's not a logo and checks topical relevance.

It also computes focal points for face-aware cropping and updates the DB directly.

The script outputs `IMAGE_RESULT:{...}` JSON with the result, including an `image_source` field naming which source provided it (`person_cache`, `wikipedia`, `wikipedia_headline_guard`, `commons_search`, `og:image`, `rss_thumbnail`, `youtube_thumbnail`, `pexels`). Check the output to confirm it found an image.

**⚠️ NAMED-PERSON VERIFICATION (mandatory, before publish):**
If the article is about a NAMED PERSON (person's name in the headline or the story's clear subject):
1. If `image_source` is `person_cache`, `wikipedia`, or `wikipedia_headline_guard` → identity is verified by source. Keep it.
2. Otherwise (`og:image`, `rss_thumbnail`, `youtube_thumbnail`, `commons_search`, `pexels`) → you MUST download the hero image and visually verify the person in the photo is the article's subject. Look at it with the read tool.
3. If you cannot positively confirm the identity → set `image_url` to null via Supabase PATCH and leave the article imageless. The enricher's manual review will source a verified photo within 4 hours. A few hours imageless beats hours with the wrong face.

**When you null a hero image on purpose, also set `image_backfill_blocked: true` on the article row.** Otherwise the image-sourcer backfill re-applies the same bad image in the next cycle (2026-10-05: the backfill re-set both an AI-generated Livemint infographic and a notthebee meme composite that writers had already nulled). PATCH: `{"image_url": null, "image_caption": "", "image_attribution": "", "image_backfill_blocked": true}`.

This check is non-negotiable. Wrong-person photos that go live erode reader trust instantly.

**If you need caption text for a specific article**, the sourcer uses the first entity name as a basic caption. For better captions, you can PATCH the `image_caption` field after the sourcer runs.

**Image Caption Rules (when writing/updating captions):**
- Two sentences. First: what the image shows. Second: the news context.
- Factual, plain style. Describe what is literally in the image.
- NO flowery bridging: "symbolizing," "reflects," "illustrating," "representing"
- NO speculation about what's not visible in the image
- **If `image_url` is null at publish time, leave `image_caption` null too — never write a caption for an image you haven't seen.** A caption describing an imagined image survives the backfill and goes live mismatched with the actual sourced photo (2026-10-11: caption described a 'restaurant dining room' while the sourced Pexels photo was a Hong Kong skyline). The sourcer writes a factual caption from the photo's own metadata when the image arrives.
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
- `kids_relevant` (from candidate JSON — copy the selector's flag verbatim; feeds the /kids Latest Stories section. If the candidate lacks it, default false)
- `published_at` (NOW), `article_type` (default 'breaking')

> **Note:** stage article JSON files in `pipeline/.state/` (e.g. `.state/v3-article-<topicid>.json`), never `/tmp` — this server's tmpfs is wiped mid-run. Insert with `python3 -u v3-insert-article.py <json>` (curl-based; urllib fails through the proxy).

### 3e2. Match scorecard (sports match-result articles only)
If the article reports the RESULT of a completed sports match (cricket, football, etc.) — not a preview, not a tournament announcement, not a transfer story — include a `match_scorecard` entry in the article's `data_cards` array. The frontend renders this as a professional scorecard card at the top of the article.

Add to `data_cards`:
```json
{
  "type": "match_scorecard",
  "sport": "cricket",
  "format": "T20I",
  "venue": "JSCA International Stadium, Ranchi",
  "date": "2026-10-10",
  "teams": [
    {"name": "West Indies", "short": "WI", "score": "252/4", "overs": "18.3"},
    {"name": "India", "short": "IND", "score": "249/5", "overs": "20"}
  ],
  "result": "West Indies won by 6 wickets",
  "series_status": "Series leveled 1-1",
  "top_performers": [
    {"name": "Shai Hope", "team": "WI", "stat": "102* (45)"},
    {"name": "Sherfane Rutherford", "team": "WI", "stat": "84 (37)"},
    {"name": "Mayank Yadav", "team": "IND", "stat": "3/38"}
  ],
  "scorecard_url": "https://www.espncricinfo.com/series/.../full-scorecard"
}
```

Rules:
- **Only for completed matches.** Previews, squad announcements, and tournament news do NOT get a scorecard.
- **Scores from source material only** — never invent or estimate. If the exact score isn't in your sources, omit the scorecard.
- **Top performers: max 3**, the genuine standouts (centuries, 5-wicket hauls, match-winning knocks). Include team short code.
- **`scorecard_url`**: link to the ESPNcricinfo full scorecard when you can find it; omit if you can't verify the URL.
- **Team order**: winning team first, then the loser (or batting order for draws).
- For non-cricket sports, adapt: football uses `score: "2-1"` without `overs`; `format` becomes the competition (e.g. "Premier League").

### 3e3. Key dates box (deadline-driven stories only)
If the article centers on a sequence of dates the reader must track — court injunction timelines, IPO date sequences, festival calendars, visa bulletin windows — include a `key_dates` entry in the article's `data_cards` array. The frontend renders this as a date-badge timeline card.

Add to `data_cards`:
```json
{
  "type": "key_dates",
  "title": "Key Dates",
  "dates": [
    {"date": "2026-10-19", "event": "Anchor investor allocation", "source_url": "https://..."},
    {"date": "2026-10-21", "event": "Public issue opens for subscription"},
    {"date": "2026-10-28", "event": "Expected listing date"}
  ]
}
```

Rules:
- **Dates must be real and sourced** — never estimate. Every date should come from your sources.
- **Chronological order**, earliest first.
- **Event text is one line** — concise, no paragraphs.
- **`source_url` optional** — link to the authoritative source for that date when available.
- **`title` optional** — defaults to "Key Dates". Use a specific title when it helps ("IPO Timeline", "Court Battle Timeline").
- **Only when dates are the story.** Don't add a dates box for articles that merely mention a date or two in passing.

### 3e4. How-to box (NRI/actionable how-to content only)
If the article explains HOW to do something actionable — apply for an IPO as an NRI, check visa status, open an account — include a `how_to` entry in the article's `data_cards` array. The frontend renders this as a numbered step-by-step card.

Add to `data_cards`:
```json
{
  "type": "how_to",
  "title": "How NRIs Can Apply for the Jio IPO",
  "steps": [
    {"step": "Open an NRE/NRO demat account", "detail": "Required for IPO bidding; link your PAN.", "link": "https://...", "link_text": "SEBI guide"},
    {"step": "Apply via ASBA through your bank", "detail": "Block the bid amount; no money leaves until allotment."},
    {"step": "Check allotment on the registrar's site", "link": "https://..."}
  ]
}
```

Rules:
- **Steps must be genuinely actionable** — the reader should be able to follow them. No vague steps like "Do your research."
- **`detail` optional** — one clarifying sentence per step max.
- **`link`/`link_text` optional** — link to the authoritative page for that step (government site, bank page, application portal).
- **Max 6 steps.** If the process is longer, group or link out.
- **Only for real how-to content.** News articles that mention a process in passing do NOT get a how-to box.

### 3e5. Checklist card (eligibility/requirements only)
If the article lists eligibility criteria, required documents, or program requirements — include a `checklist` entry in the article's `data_cards` array. The frontend renders this as a checkbox-style list with an optional "catch" callout.

Add to `data_cards`:
```json
{
  "type": "checklist",
  "title": "Eligibility Checklist",
  "items": [
    {"text": "Canadian PR or citizenship", "note": "Required — work permits don't qualify"},
    {"text": "Complete the Touchstone assessment"},
    {"text": "Pass the certification exam"}
  ],
  "catch_text": "Must commit to a 3-year return-of-service in an underserved area."
}
```

Rules:
- **Every item must be a real requirement** from your sources. Never invent criteria.
- **`note` optional** — one clarifying note per item max.
- **`catch_text` optional** — use it for the hidden gotcha, the fine print, the thing people miss. Keep it to one sentence.
- **Max 8 items.** Longer lists belong in the body.
- **Only for genuine checklists.** Don't force eligibility framing onto articles that don't have requirements.

### 3e6. Price comparison table (cost comparisons only)
If the article compares costs — savings breakdowns, service pricing, fare comparisons — include a `price_compare` entry in the article's `data_cards` array. The frontend renders this as a clean comparison table with an optional highlighted "best" row.

Add to `data_cards`:
```json
{
  "type": "price_compare",
  "title": "Savings Breakdown",
  "headers": ["Item", "Regular Fare", "Student Fare"],
  "rows": [
    ["Base fare", "$1,200", "$1,080"],
    ["Change fee", "$150", "Free"],
    ["Total", "$1,350", "$1,080"]
  ],
  "highlight_row": 2
}
```

Rules:
- **Numbers must come from your sources** — never estimate prices.
- **`headers`**: first column is the label, the rest are the options being compared. Keep to 2–4 columns.
- **`rows`**: each row is an array of strings matching the header count. Keep to 3–6 rows.
- **`highlight_row` optional** — 0-based index of the row to highlight as the best option. Use sparingly: only when one option is genuinely the best deal.
- **Only for real comparisons.** Don't manufacture a table from a single price mentioned in passing.

### 3e7. Recipe card (food articles only)
If the article includes a recipe, diet plan, or dish — include a `recipe` entry in the article's `data_cards` array. The frontend renders this as a clean card with ingredients, numbered method steps, time/servings, and optional nutrition.

Add to `data_cards`:
```json
{
  "type": "recipe",
  "title": "Shahi Paneer",
  "ingredients": ["250g paneer, cubed", "2 onions, finely chopped", "1 cup tomato puree"],
  "steps": ["Heat ghee in a pan over medium heat.", "Add onions and sauté until golden brown.", "Stir in tomato puree and spices; simmer 10 minutes."],
  "prep_time": "15 min",
  "cook_time": "25 min",
  "servings": "4",
  "nutrition": [
    { "label": "Calories", "value": "320 kcal" },
    { "label": "Protein", "value": "14g" }
  ]
}
```

Rules:
- **Everything must come from your sources** — never invent ingredients, quantities, times, or nutrition values.
- **`ingredients` and `steps` are both required** — the card won't render without them.
- **`prep_time`, `cook_time`, `servings`, `nutrition` are optional** — include when the source provides them, omit when it doesn't.
- **Use for real recipes only** — not for restaurant reviews or food news without a dish to make.

### 3e8. Story so far (developing stories — AUTOMATIC, no data card needed)
The "Story So Far" block is generated automatically from the article's linked developing storylines (the `storyline_articles` table). You do NOT need to add a `story_so_far` data card — the frontend's `StorySoFar` component fetches the storyline's recent articles and renders the timeline itself.

Your job: link the article to its storyline correctly (see the storyline-linking step). The block appears automatically when the article belongs to an active or emerging storyline.

### 3e9. Critic table (movie reviews only)
If the article is a movie review that synthesizes multiple named critics — include a `critic_table` entry in the article's `data_cards` array. The frontend renders this as a critic-by-critic breakdown with name, publication, rating, key verdict quote, and link.

Add to `data_cards`:
```json
{
  "type": "critic_table",
  "title": "What Critics Are Saying",
  "critics": [
    {
      "name": "Anupama Chopra",
      "publication": "Film Companion",
      "rating": "4/5",
      "verdict": "A stunning achievement that announces a major new voice.",
      "url": "https://www.filmcompanion.in/reviews/..."
    },
    {
      "name": "Rajeev Masand",
      "publication": "News18",
      "rating": "3.5/5",
      "verdict": "Flawed but impossible to look away from.",
      "url": "https://www.news18.com/movies/..."
    }
  ]
}
```

Rules:
- **Every critic, rating, and quote must come from your sources** — never invent a critic or paraphrase a verdict you didn't read.
- **`name` and `verdict` are required** for each entry; `publication`, `rating`, and `url` are optional but strongly preferred.
- **`verdict`** should be the critic's key takeaway in their own words (a short quote or faithful paraphrase), not your summary.
- **Include 3–6 critics** for a proper consensus picture. Fewer than 3 isn't a table — just mention them in the body.
- **Link to the full review** whenever the URL is available.

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

## ENRICHMENT BAR — Making Articles Rich and Useful (2026-10-11)

Every article should end with the reader able to DO something they couldn't do before reading. These are non-negotiable:

1. **One actionable sentence in every diaspora section.** Not "this strikes a chord" — name the link, the form, the number, the store. If the diaspora angle can't produce one action, cut the section.

2. **Utility articles ship with named links.** Travel → booking/ETA/visa links. Immigration → application/government pages. Finance → account/broker/regulator links. Health → CDC/schedule pages. No exceptions — an article telling readers about a program without linking to it is incomplete.

3. **Social embeds are not optional for social-native stories.** If the story IS a post (an X announcement, an Instagram reel tour, a founder's post), the embed is the article's primary source — find it at write time. Do NOT rely on the 4-hour enricher window; if the post is older than that, the enricher will miss it.

4. **Quantify the thesis.** Articles asserting a trend need one data section that adjudicates the claim — a comparison table, a count, a timeline. Don't just quote someone saying "X is rising" — show the numbers.

5. **Name the mechanism.** Policy stories must unpack the mechanism in one paragraph. Never name-drop an acronym (SHANTI, SIR, D/S) the reader can't act on — explain what it does and who it affects.

6. **Absolute risk, not just relative.** Health articles: convert relative reductions to percentage points against the baseline rate. One sentence of arithmetic — "from 2% to 1.7%" not just "15% lower risk."

7. **Verify single-source stories.** Any story built on one wire release gets an explicit verification attempt (registry lookup, named client, second source) or a stated "couldn't independently verify" note.

8. **Balance developing stories.** Opposition-wire stories need the other side's response in the same article. One paragraph minimum.

9. **Trailer articles: franchise primer + cast + watch path.** Every trailer piece: what came before (one paragraph), who's in it, where the diaspora reader watches it (theater/streaming, US availability).

10. **Deep-link our own explainers.** When an article touches a topic we've covered (TDS, visa types, codeshares), link to our own article in-body. Free engagement — do it at write time.

11. **Flag highly visual stories.** When the story is about something readers need to SEE to understand — a natural phenomenon (bioluminescence, eclipses), a new product, architecture, fashion, food, a place — set `is_visual_story: true` on the article. The image becomes non-negotiable for these, not best-effort. The enricher prioritizes backfilling visual stories first. A visual story without a picture is an incomplete article.

## Movie Review Format (when writing a movie review article)
All movie reviews MUST follow The Videshi Rating format:
1. **Rating data** (stored as article fields, rendered as "THE VIDESHI RATING" card):
   - `star_rating`: overall rating out of 5 (half-star increments, e.g. 3.5)
   - `category_ratings`: exactly these four keys — "Story", "Direction", "Climax", "Performances" — each out of 5
   - `rating_consensus`: editorial paragraph (e.g. "Critics broadly praise the finale's face-off, docking it for a slow first half — a 3.5-star consensus across 18 published reviews.")
2. **Body structure** using these exact bullet headers:
   - "The consensus:" — X published critic reviews average Y/5, range, where most land
   - "What's praised:" — specific things critics praised
   - "What's criticized:" — specific criticisms (even for well-reviewed films)
   - "What this means for you:" — should the diaspora audience watch it, practical info

Report a brief summary: headlines, categories, and total articles published.
