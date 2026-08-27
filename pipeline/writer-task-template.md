# V3 Writer Task — Article Writing Instructions

## Environment Setup
```bash
set -a; source ~/workspace/.env.supabase; source ~/workspace/.env.openai; source ~/workspace/.env.pexels; set +a
```

## For EACH assigned candidate:

### Step 1: Read Sources
- Open 2-3 source URLs via browser_open (Google News RSS URLs redirect to actual articles)
- Cross-reference multiple sources for facts
- If source_urls are empty, use browser_search with the title to find articles

### Step 2: Write the Article
Follow these rules exactly:

**HEADLINE**: 8-14 words, clear, no clickbait. For updates, lead with what's NEW.

**KEY TAKEAWAYS** (REQUIRED - at top of body):
```html
<div class="key-takeaways"><ul><li>Point 1</li><li>Point 2</li><li>Point 3</li></ul></div>
```
NO heading tag inside. Just the div with ul/li.

**BODY** (500-800 words, HTML with h2 subheadings):
1. Opening paragraph — news lead, no fluff
2. Context & Background
3. Impact & Analysis
4. Diaspora Angle (when natural, NOT forced)
5. What's Next / Looking Ahead

**Pull quotes** (1-2 max, only strong quotes):
```html
<blockquote class="pull-quote"><p>"Quote text"</p><cite>— Name, Title</cite></blockquote>
```

**RULES**:
- Write from sources only, no fabrication
- Include source citations naturally
- NO filler: "In a significant development," "It is worth noting"
- NO sycophantic qualifiers: "importantly," "notably"
- Use specific numbers, dates, names
- markets-finance: US/global-first, no forced NRI framing
- entertainment/sports: require Indian/diaspora connection

### Step 3: Generate slug
Format: kebab-case from headline, e.g., "whatsapp-strengthens-account-security-with-password-two-step-verification"

### Step 4: Insert into Supabase
```bash
set -a; source ~/workspace/.env.supabase; set +a

curl -sS "$SUPABASE_URL/rest/v1/p2_articles" \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Content-Type: application/json" \
  -H "Prefer: return=representation" \
  -d '{
    "headline": "...",
    "subheadline": "1-2 sentence summary for display",
    "body": "<div class=\"key-takeaways\">...</div><p>...</p>...",
    "slug": "...",
    "category": "...",
    "vertical": "same as category",
    "tags": ["tag1","tag2","tag3"],
    "sources": ["url1","url2"],
    "image_url": null,
    "image_caption": null,
    "image_attribution": null,
    "word_count": 600,
    "diaspora_angle": "1 sentence",
    "topic_id": "from candidate",
    "llm_score": from_candidate,
    "published_at": "NOW()",
    "article_type": "breaking",
    "status": "published"
  }'
```

IMPORTANT: The body HTML must be properly escaped in the JSON. Use a Python script to build and POST the JSON to avoid escaping issues.

### Step 5: Run image sourcer (after insert)
```bash
cd ~/workspace/the-videshi-news/pipeline
python3 -u image_sourcer.py --slug <article-slug> --apply
```

### Step 6: Run article polish (after insert)
```bash
cd ~/workspace/the-videshi-news/pipeline
set -a; source ~/workspace/.env.supabase; source ~/workspace/.env.openai; set +a
python3 -u article-polish.py --article-id <article_uuid> 2>&1
```

### Step 7: Update topic status
```bash
set -a; source ~/workspace/.env.supabase; set +a
curl -sS "$SUPABASE_URL/rest/v1/p2_topics?id=eq.<topic_id>" \
  -X PATCH \
  -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Content-Type: application/json" \
  -d '{"status": "published", "last_article_id": "<article_uuid>"}'
```

## Report format
For each article written, report:
- headline
- category
- slug
- article UUID (from insert response)
- image result (found or not)
- any issues

If an article fails at any step, continue with remaining articles.
