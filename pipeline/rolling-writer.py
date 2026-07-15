#!/usr/bin/env python3
"""
Rolling Writer for The Videshi
Runs every hour. Scans p2_topics for high-scoring unwritten topics,
uses LLM to evaluate and pick the best 2-3, writes full articles.

Replaces the 6-8 hour batch category writers with a unified hourly writer.
Ensures fresh content appears every hour for returning visitors.

Articles are inserted with status="review" so the QA reviewer promotes them.
"""

import json, os, re, subprocess, sys, time, urllib.parse, hashlib, unicodedata
from datetime import datetime, timezone, timedelta
from focal_point import compute_focal_point, image_dimensions

# ── Env ──────────────────────────────────────────────────────────────────────

def load_env(path):
    path = os.path.expanduser(path)
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ[k.strip()] = v.strip().strip('"').strip("'")

load_env("~/workspace/.env.supabase")
load_env("~/workspace/.env.google-ai")
load_env("~/workspace/.env.pexels")
load_env("~/workspace/.env.openai")

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
SUPABASE_ACCESS_TOKEN = os.environ.get("SUPABASE_ACCESS_TOKEN", "")
GEMINI_KEY   = os.environ.get("GOOGLE_AI_API_KEY", "")
OPENAI_KEY   = os.environ.get("OPENAI_API_KEY", "")
PEXELS_KEY   = os.environ.get("PEXELS_API_KEY", "")

UA = "TheVideshi/1.0 (thevideshi.com)"

VALID_CATEGORIES = [
    "immigration", "technology", "news", "entertainment",
    "sports", "markets-finance", "nri-world", "food",
    "travel", "lifestyle-health"
]

MAX_ARTICLES_PER_RUN = 3
MIN_COMBINED_SCORE = 11  # minimum newsworthiness + diaspora_relevance for LLM eval
LOOKBACK_HOURS = 12      # how far back to look for topics
DEDUP_HOURS = 48         # how far back to check for duplicate articles

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# ── Helpers ──────────────────────────────────────────────────────────────────

def curl_json(method, url, data=None, headers=None, timeout=30):
    """HTTP request via curl, returns parsed JSON or None."""
    cmd = ["curl", "-s", "-X", method, url]
    if headers:
        for k, v in headers.items():
            cmd += ["-H", f"{k}: {v}"]
    if data is not None:
        cmd += ["-d", json.dumps(data) if isinstance(data, dict) else data]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if result.stdout.strip():
            return json.loads(result.stdout.strip())
    except (subprocess.TimeoutExpired, json.JSONDecodeError) as e:
        print(f"  ⚠ curl error: {e}", file=sys.stderr)
    return None


def curl_raw(method, url, headers=None, timeout=30):
    """HTTP request via curl, returns raw bytes."""
    cmd = ["curl", "-s", "-X", method, url]
    if headers:
        for k, v in headers.items():
            cmd += ["-H", f"{k}: {v}"]
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=timeout)
        return result.stdout
    except subprocess.TimeoutExpired:
        return None


def sb_query(sql):
    """Run SQL via Supabase Management API."""
    result = curl_json("POST",
        "https://api.supabase.com/v1/projects/lboecaekpynbpyijrbfz/database/query",
        data={"query": sql},
        headers={
            "Authorization": f"Bearer {SUPABASE_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        },
        timeout=30
    )
    return result if isinstance(result, list) else []


def sb_rest(method, table, params="", data=None):
    """Supabase REST API call."""
    url = f"{SUPABASE_URL}/rest/v1/{table}{params}"
    hdrs = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    return curl_json(method, url, data=data, headers=hdrs)


def call_openai(prompt, json_mode=True, max_tokens=4096, temperature=0.3, model="gpt-4o-mini"):
    """Call OpenAI GPT-4o-mini. Primary LLM for the rolling writer."""
    if not OPENAI_KEY:
        return None
    url = "https://api.openai.com/v1/chat/completions"
    body = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if json_mode:
        body["response_format"] = {"type": "json_object"}

    result = curl_json("POST", url, data=body, headers={
        "Authorization": f"Bearer {OPENAI_KEY}",
        "Content-Type": "application/json"
    }, timeout=120)
    if not result:
        return None

    try:
        text = result["choices"][0]["message"]["content"]
        if json_mode:
            parsed = json.loads(text)
            return parsed
        return text
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        print(f"  ⚠ OpenAI parse error: {e}", file=sys.stderr)
        if not json_mode:
            return None
        try:
            text = result["choices"][0]["message"]["content"]
            match = re.search(r'[\[{].*[}\]]', text, re.DOTALL)
            if match:
                return json.loads(match.group())
        except:
            pass
        return None


def call_gemini(prompt, json_mode=True, max_tokens=4096, temperature=0.3):
    """Call Gemini 2.5 Flash with thinkingBudget:0 for JSON output. Fallback only."""
    if not GEMINI_KEY:
        return None
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_KEY}"
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_tokens,
            "thinkingConfig": {"thinkingBudget": 0}
        }
    }
    if json_mode:
        body["generationConfig"]["responseMimeType"] = "application/json"

    result = curl_json("POST", url, data=body, headers={"Content-Type": "application/json"}, timeout=120)
    if not result:
        return None

    try:
        text = result["candidates"][0]["content"]["parts"][0]["text"]
        if json_mode:
            return json.loads(text)
        return text
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        print(f"  ⚠ Gemini parse error: {e}", file=sys.stderr)
        if not json_mode:
            return None
        try:
            text = result["candidates"][0]["content"]["parts"][0]["text"]
            match = re.search(r'[\[{].*[}\]]', text, re.DOTALL)
            if match:
                return json.loads(match.group())
        except:
            pass
        return None


def call_llm(prompt, json_mode=True, max_tokens=4096, temperature=0.3):
    """Call LLM: try OpenAI first, fall back to Gemini."""
    result = call_openai(prompt, json_mode=json_mode, max_tokens=max_tokens, temperature=temperature)
    if result is not None:
        return result
    print("  ⚠ OpenAI failed, trying Gemini fallback...")
    return call_gemini(prompt, json_mode=json_mode, max_tokens=max_tokens, temperature=temperature)


def is_hindi(text):
    """Check if text contains significant Devanagari characters (Hindi/Sanskrit)."""
    if not text:
        return False
    devanagari = sum(1 for c in text if '\u0900' <= c <= '\u097F')
    return devanagari > len(text) * 0.15


def make_slug(headline):
    """Generate a URL-safe slug from headline."""
    slug = re.sub(r'[^\w\s-]', '', headline.lower().strip())
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = re.sub(r'-+', '-', slug).strip('-')
    # Truncate to reasonable length
    parts = slug.split('-')
    result = []
    length = 0
    for p in parts:
        if length + len(p) > 80:
            break
        result.append(p)
        length += len(p) + 1
    return '-'.join(result) if result else slug[:80]


def extract_keywords(text, min_len=4):
    """Extract distinctive keywords from text for dedup comparison."""
    STOP = {
        'the', 'and', 'for', 'are', 'was', 'were', 'has', 'have', 'had',
        'with', 'from', 'that', 'this', 'will', 'been', 'being', 'after',
        'before', 'about', 'into', 'over', 'amid', 'says', 'said', 'more',
        'than', 'also', 'just', 'first', 'last', 'next', 'here', 'what',
        'when', 'where', 'which', 'while', 'under', 'could', 'would',
        'should', 'their', 'there', 'other', 'some', 'most', 'like',
        'make', 'makes', 'made', 'gets', 'your', 'they', 'them', 'india',
        'indian', 'people', 'world', 'year', 'years', 'time', 'news',
        'know', 'many', 'much', 'even', 'every', 'each', 'back', 'take',
        'only', 'very', 'well', 'still', 'does', 'look', 'need', 'come',
    }
    words = re.findall(r'[A-Za-z]+', text.lower())
    return [w for w in words if len(w) >= min_len and w not in STOP]


# ── Step 1: Gather candidate topics ─────────────────────────────────────────

def get_candidate_topics():
    """Get recent high-scoring topics that don't have articles yet."""
    print("Step 1: Gathering candidate topics...")

    # Get topics from last LOOKBACK_HOURS that are still pending
    # Use multiple queries to ensure diversity:
    # 1. Top by score (catches multi-signal stories)
    # 2. Top by recency (catches fresh breaking stories)
    # This ensures we don't miss IBM-type stories that have low signal_count
    # but high individual newsworthiness.
    sql = f"""
    (SELECT t.id, t.canonical_title, t.category, t.urgency,
           t.score_total, t.signal_count, t.keywords, t.status,
           t.created_at
    FROM p2_topics t
    WHERE t.created_at > now() - interval '{LOOKBACK_HOURS} hours'
      AND t.status = 'pending'
      AND t.score_total >= 40
    ORDER BY t.signal_count DESC, t.score_total DESC
    LIMIT 20)
    UNION
    (SELECT t.id, t.canonical_title, t.category, t.urgency,
           t.score_total, t.signal_count, t.keywords, t.status,
           t.created_at
    FROM p2_topics t
    WHERE t.created_at > now() - interval '{LOOKBACK_HOURS} hours'
      AND t.status = 'pending'
      AND t.score_total >= 40
    ORDER BY t.created_at DESC
    LIMIT 20)
    """
    topics = sb_query(sql)
    if not topics:
        print("  No candidate topics found.")
        return []

    print(f"  Found {len(topics)} raw candidates")

    # Filter out Hindi-only titles
    topics = [t for t in topics if not is_hindi(t.get('canonical_title', ''))]
    print(f"  After Hindi filter: {len(topics)}")

    # Filter out topics that already have articles (via topic_id)
    topic_ids = [t['id'] for t in topics]
    if topic_ids:
        ids_str = ','.join(f"'{tid}'" for tid in topic_ids)
        existing = sb_query(f"""
            SELECT topic_id FROM p2_articles
            WHERE topic_id IN ({ids_str})
              AND status IN ('published', 'review')
        """)
        existing_ids = {r['topic_id'] for r in (existing or [])}
        before = len(topics)
        topics = [t for t in topics if t['id'] not in existing_ids]
        if before != len(topics):
            print(f"  After topic_id dedup: {len(topics)} (removed {before - len(topics)} with existing articles)")

    return topics


def get_recent_articles():
    """Get recent article headlines for dedup comparison."""
    sql = f"""
    SELECT headline, slug, category FROM p2_articles
    WHERE published_at > now() - interval '{DEDUP_HOURS} hours'
      AND status IN ('published', 'review')
    ORDER BY published_at DESC
    LIMIT 100
    """
    return sb_query(sql) or []


def check_duplicate(topic_title, recent_articles, threshold=3):
    """Check if a topic is already covered by a recent article."""
    topic_kw = set(extract_keywords(topic_title))
    if not topic_kw:
        return False

    for art in recent_articles:
        art_kw = set(extract_keywords(art.get('headline', '')))
        overlap = topic_kw & art_kw
        if len(overlap) >= threshold:
            return True
    return False


# ── Step 2: LLM evaluation ──────────────────────────────────────────────────

def evaluate_topics(topics, recent_articles):
    """Use Gemini to score topics for newsworthiness and diaspora relevance."""
    print(f"\nStep 2: LLM evaluation of {len(topics)} candidates...")

    # Pre-filter duplicates
    filtered = []
    for t in topics:
        title = t.get('canonical_title', '')
        if check_duplicate(title, recent_articles):
            print(f"  SKIP (duplicate): {title[:60]}")
            continue
        filtered.append(t)

    if not filtered:
        print("  All topics already covered.")
        return []

    print(f"  {len(filtered)} topics after dedup filter")

    # Prepare signal list for LLM (max 25 to keep prompt manageable)
    signals_for_llm = []
    now = datetime.now(timezone.utc)
    for i, t in enumerate(filtered[:25]):
        # Calculate hours since signal arrived
        created = t.get('created_at', '')
        hours_ago = '?'
        if created:
            try:
                ct = datetime.fromisoformat(created.replace('Z', '+00:00'))
                hours_ago = round((now - ct).total_seconds() / 3600, 1)
            except Exception:
                pass
        signals_for_llm.append({
            "idx": i,
            "title": t.get('canonical_title', ''),
            "category": t.get('category', 'news'),
            "urgency": t.get('urgency', 'daily'),
            "signal_count": t.get('signal_count', 1),
            "score": t.get('score_total', 0),
            "keywords": t.get('keywords', []),
            "hours_ago": hours_ago
        })

    prompt = f"""You are the editor of The Videshi, an Indian diaspora news site serving NRIs (Non-Resident Indians) worldwide.

Below are news signals. Each includes `hours_ago` — how many hours since the signal arrived. Fresher stories (lower hours_ago) should score higher for newsworthiness, all else equal. A breaking result from 1 hour ago beats the same story arriving 8 hours late.

Score each for:
1. **newsworthiness** (1-10): How important is this story RIGHT NOW? Major events, breaking news, policy changes = 8-10. Routine/filler = 1-4. Penalize stories that are many hours old — they're less urgent.
2. **diaspora_relevance** (1-10): How relevant is this to Indians living abroad? Immigration, H-1B, India-US/UK/Canada relations, NRI investments, diaspora culture = 8-10. US market moves (S&P 500, Nasdaq, Fed rate decisions, FAANG/major tech earnings, 401k-relevant news) also score 7-9 because most NRIs live and invest in the US. Purely local Indian domestic news = 3-5. Irrelevant = 1-2.
3. **suggested_category**: One of: immigration, technology, news, entertainment, sports, markets-finance, nri-world, food, travel, lifestyle-health
4. **reason**: One sentence explaining your scoring.

Also flag if any are essentially about the same event (duplicate detection).

SIGNALS:
{json.dumps(signals_for_llm, indent=2)}

Score ALL signals. Be strict — a World Cup semifinal result scores 9-10. A random court case scores 3-4. A story about H-1B visa changes scores 9-10.

Return a JSON object with key "signals" containing the array:
{{"signals": [{{"idx": 0, "newsworthiness": 8, "diaspora_relevance": 7, "suggested_category": "news", "reason": "...", "is_duplicate_of": null}}, ...]}}"""

    result = call_llm(prompt, json_mode=True, max_tokens=3000)
    if not result:
        print("  ⚠ LLM evaluation failed, falling back to score_total ranking")
        return filtered[:MAX_ARTICLES_PER_RUN]

    # Handle different response shapes
    if isinstance(result, dict):
        # OpenAI wraps in object — extract the array
        result = result.get('signals') or result.get('items') or result.get('results') or []
    if not isinstance(result, list):
        print(f"  ⚠ Unexpected LLM response type: {type(result)}, falling back")
        return filtered[:MAX_ARTICLES_PER_RUN]

    # Merge LLM scores with topics
    scored = []
    for item in result:
        idx = item.get('idx')
        if idx is None or idx >= len(filtered):
            continue
        topic = filtered[idx]
        nw = item.get('newsworthiness', 5)
        dr = item.get('diaspora_relevance', 5)
        combined = nw + dr
        dup_of = item.get('is_duplicate_of')

        topic['llm_newsworthiness'] = nw
        topic['llm_diaspora_relevance'] = dr
        topic['llm_combined_score'] = combined
        topic['llm_category'] = item.get('suggested_category', topic.get('category', 'news'))
        topic['llm_reason'] = item.get('reason', '')
        topic['is_duplicate_of'] = dup_of

        if dup_of is not None:
            print(f"  SKIP (LLM dup): {topic['canonical_title'][:50]} (dup of #{dup_of})")
            continue

        if combined >= MIN_COMBINED_SCORE:
            scored.append(topic)
            print(f"  ✓ [{nw}+{dr}={combined}] [{topic['llm_category']:15s}] {topic['canonical_title'][:55]}")
        else:
            print(f"  ✗ [{nw}+{dr}={combined}] too low: {topic['canonical_title'][:55]}")

    # Sort by combined score desc
    scored.sort(key=lambda x: x.get('llm_combined_score', 0), reverse=True)

    # Category diversity: don't let one category take all slots
    selected = []
    cat_counts = {}
    for t in scored:
        cat = t.get('llm_category', 'news')
        count = cat_counts.get(cat, 0)
        if count >= 2 and len(selected) < MAX_ARTICLES_PER_RUN:
            # Allow max 2 from same category
            continue
        selected.append(t)
        cat_counts[cat] = count + 1
        if len(selected) >= MAX_ARTICLES_PER_RUN:
            break

    print(f"\n  Selected {len(selected)} topics to write:")
    for t in selected:
        print(f"    [{t.get('llm_combined_score', 0)}] [{t.get('llm_category', '?'):15s}] {t['canonical_title'][:60]}")

    return selected


# ── Step 3: Write articles ──────────────────────────────────────────────────

def get_signal_urls(topic_id):
    """Get source URLs from signals linked to this topic."""
    sql = f"""
    SELECT s.title, s.original_url, f.name as source_name
    FROM p2_topic_signals ts
    JOIN p2_signals s ON ts.signal_id = s.id
    JOIN p2_feed_sources f ON s.feed_source_id = f.id
    WHERE ts.topic_id = '{topic_id}'
    ORDER BY s.published_at DESC
    LIMIT 5
    """
    return sb_query(sql) or []


def write_article(topic):
    """Use Gemini to write a full article from a topic."""
    title = topic.get('canonical_title', '')
    category = topic.get('llm_category', topic.get('category', 'news'))
    if category not in VALID_CATEGORIES:
        category = 'news'

    # Get source URLs for reference
    signal_sources = get_signal_urls(topic['id'])
    source_context = "\n".join([
        f"- [{s.get('source_name', '?')}] {s.get('title', '')}: {s.get('original_url', '')}"
        for s in signal_sources
    ])

    prompt = f"""You are a senior journalist at The Videshi, a premium English-language news site for the Indian diaspora (NRIs worldwide). Write a complete article about:

TOPIC: {title}

CATEGORY: {category}

SOURCE REFERENCES (use these as basis — cite at least 2 of them):
{source_context if source_context else "Research the topic using your knowledge."}

REQUIREMENTS:
1. **headline**: 20-120 chars. Newspaper style — short, punchy, declarative. Not clickbait.
2. **subheadline**: 30-120 chars. Adds nuance/context the headline doesn't cover.
3. **body**: 600-900 words in markdown. Well-structured with ## subheadings. Include a diaspora perspective (why NRIs should care). Use present tense for current events. Include at least one section header. No promotional language.
4. **tags**: Array of 3-6 lowercase tags relevant to the article.
5. **slug**: lowercase-hyphenated URL slug from headline (max 80 chars).
6. **vertical**: Short descriptor: "geopolitics", "economy", "immigration", "tech", "entertainment", "sports", "cricket", "world-cup-2026", "diaspora-safety", "culture", etc.
7. **diaspora_angle**: One sentence explaining why NRIs/diaspora should care.
8. **sources**: Array of {{"name": "Source Name", "url": "https://..."}} — at least 2 real sources.
9. **newsworthiness**: Integer 1-30 (30 = massive global event, 20+ = major, 10-15 = moderate)
10. **diaspora_impact**: Integer 1-30 (how much it affects NRI daily life/interests)
11. **prominence**: Integer 1-20 (how prominent are the people/orgs involved)
12. **article_type**: "breaking" for urgent events, "analysis" for in-depth, "report" for standard reporting, "feature" for human interest
13. **image_search_query**: Specific search query to find a relevant hero image (e.g., "Narendra Modi G20", "H-1B visa stamp", "Spain France World Cup")
14. **image_must_show**: What the hero image must depict (e.g., "Narendra Modi speaking", "a US visa stamp")
15. **image_entities**: Array of main people/entities in the article (for image search)

STYLE GUIDE:
- Write like The Economist or Bloomberg, not like a blog
- Lead with the news, then context, then analysis
- Include specific numbers, names, dates where relevant
- Add a clear diaspora angle — how does this affect Indians abroad?
- Use ## for section headers, not #
- No "In conclusion" or "In summary" — end with impact or forward-looking point

Return a single JSON object with all these fields."""

    result = call_llm(prompt, json_mode=True, max_tokens=4000, temperature=0.4)
    if not result or not isinstance(result, dict):
        print(f"  ⚠ Article generation failed for: {title[:50]}")
        return None

    # Validate required fields
    headline = result.get('headline', '')
    body = result.get('body', '')
    if not headline or len(headline) < 15:
        print(f"  ⚠ Bad headline: {headline}")
        return None
    if not body or len(body) < 300:
        print(f"  ⚠ Body too short: {len(body)} chars")
        return None

    # Ensure slug has date suffix
    slug = result.get('slug', '') or make_slug(headline)
    slug = re.sub(r'[^a-z0-9-]', '', slug.lower())[:90]
    date_suffix = datetime.now(timezone.utc).strftime("-%Y%m%d")
    if not re.search(r'-\d{8}$', slug):
        slug = slug.rstrip('-')[:80] + date_suffix

    # Build article dict
    article = {
        "headline": headline[:200],
        "subheadline": (result.get('subheadline') or '')[:200],
        "body": body,
        "category": category,
        "vertical": result.get('vertical', 'general'),
        "tags": result.get('tags', []) or [],
        "slug": slug,
        "sources": json.dumps(result.get('sources', [{"name": "The Videshi", "url": "https://thevideshi.com"}])),
        "diaspora_angle": result.get('diaspora_angle', ''),
        "article_type": result.get('article_type', 'report'),
        "newsworthiness": min(30, max(1, result.get('newsworthiness', 15))),
        "diaspora_impact": min(30, max(1, result.get('diaspora_impact', 10))),
        "prominence": min(20, max(1, result.get('prominence', 10))),
        "status": "review",
        "is_featured": False,
        "is_editorial": False,
        "topic_id": topic['id'],
        "published_at": datetime.now(timezone.utc).isoformat(),
        "image_search_query": result.get('image_search_query', ''),
        "image_must_show": result.get('image_must_show', ''),
        "image_entities": result.get('image_entities', []),
    }

    # Calculate word count
    article["word_count"] = len(re.findall(r'\b\w+\b', body))

    # Compute initial score_total
    article["score_total"] = (
        article["newsworthiness"]
        + article["diaspora_impact"]
        + article["prominence"]
    )

    return article


# ── Step 4: Hero image ──────────────────────────────────────────────────────

def fetch_wikipedia_person_image(person_name):
    """Fetch a person's photo from Wikipedia. Returns URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}"
    result = curl_json("GET", url, headers={"User-Agent": UA})
    if result and isinstance(result, dict):
        img = (result.get("originalimage") or {}).get("source") or \
              (result.get("thumbnail") or {}).get("source")
        if img:
            print(f"    ✓ Wikipedia image for '{person_name}'")
            return img
    return None


# Wikimedia commons relevance gate
_COMMONS_STOP = {
    "the","a","an","of","in","on","at","to","for","and","or","with","as","by","from","is",
    "are","was","were","be","new","says","after","over","amid","how","why","what","2024",
    "2025","2026","india","indian","us","usa","american","uk","first","more","than",
    "people","man","woman","group","day","year","top","big","set","get","make","makes",
    "made","you","your","they","them","this","that","social","media","using","use",
}

def commons_relevance_ok(commons_title, headline, topic=""):
    """Check if Commons file title plausibly matches the article subject."""
    title_l = (commons_title or "").lower()
    head_l = (headline or "").lower()
    if not title_l:
        return False
    kws = set(w.lower() for w in re.findall(r'[A-Za-z][A-Za-z\'-]+', headline or '')
              if len(w) >= 4 and w.lower() not in _COMMONS_STOP)
    kws |= set(w.lower() for w in re.findall(r'[A-Za-z][A-Za-z\'-]+', topic or '')
               if len(w) >= 4 and w.lower() not in _COMMONS_STOP)
    if not kws:
        return True
    return any(kw in title_l for kw in kws)


def fetch_wikimedia_commons_image(search_query, headline=""):
    """Search Wikimedia Commons for relevant image."""
    params = urllib.parse.urlencode({
        "action": "query",
        "generator": "search",
        "gsrsearch": search_query,
        "gsrnamespace": "6",
        "gsrlimit": "5",
        "prop": "imageinfo",
        "iiprop": "url|size|mime",
        "iiurlwidth": "1200",
        "format": "json"
    })
    url = f"https://commons.wikimedia.org/w/api.php?{params}"
    result = curl_json("GET", url, headers={"User-Agent": UA})
    if not result or not isinstance(result, dict):
        return None

    pages = result.get("query", {}).get("pages", {})
    for pid, page in pages.items():
        ii = (page.get("imageinfo") or [{}])[0]
        mime = ii.get("mime", "")
        if not mime.startswith("image/") or mime == "image/svg+xml":
            continue
        if ii.get("width", 0) < 300:
            continue
        title = page.get("title", "")
        if not commons_relevance_ok(title, headline, search_query):
            continue
        img_url = ii.get("thumburl") or ii.get("url", "")
        if img_url:
            print(f"    ✓ Wikimedia Commons: {title[:50]}")
            return img_url
    return None


def fetch_pexels_image(query):
    """Search Pexels for a topical image. Returns URL or None."""
    if not PEXELS_KEY:
        return None
    url = f"https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=3&orientation=landscape"
    # Use curl to avoid urllib proxy issues
    cmd = [
        "curl", "-s", url,
        "-H", f"Authorization: {PEXELS_KEY}",
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        data = json.loads(result.stdout)
        photos = data.get("photos", [])
        if photos:
            # Use large2x for good quality
            img_url = photos[0].get("src", {}).get("large2x") or photos[0].get("src", {}).get("original")
            if img_url:
                print(f"    ✓ Pexels: {query[:40]}")
                return img_url
    except (subprocess.TimeoutExpired, json.JSONDecodeError, KeyError):
        pass
    return None


def download_image(url):
    """Download an image and return bytes."""
    cmd = ["curl", "-sS", "-L", "-A", UA, "-o", "-", url]
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=30)
        if result.returncode == 0 and len(result.stdout) > 5000:
            return result.stdout
    except subprocess.TimeoutExpired:
        pass
    return None


def compress_image(img_bytes, max_width=1200, quality=80):
    """Resize and compress image to JPEG. Returns bytes or None."""
    try:
        from PIL import Image
        import io
        img = Image.open(io.BytesIO(img_bytes))
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        if img.width > max_width:
            ratio = max_width / img.width
            img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=quality, optimize=True)
        compressed = buf.getvalue()
        if len(compressed) > 5000:
            return compressed
    except Exception as e:
        print(f"    ⚠ PIL compress error: {e}")
    return None


def upload_to_supabase(jpeg_bytes, filename):
    """Upload compressed JPEG to Supabase article-images bucket."""
    url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
    cmd = [
        "curl", "-s", "-X", "POST", url,
        "-H", f"apikey: {SUPABASE_KEY}",
        "-H", f"Authorization: Bearer {SUPABASE_KEY}",
        "-H", "Content-Type: image/jpeg",
        "-H", "x-upsert: true",
        "--data-binary", "@-"
    ]
    try:
        result = subprocess.run(cmd, input=jpeg_bytes, capture_output=True, timeout=60)
        stdout = result.stdout.decode('utf-8', errors='replace')
        if result.returncode == 0:
            try:
                resp = json.loads(stdout)
                if "error" in resp or "statusCode" in resp:
                    print(f"    ⚠ Upload error: {stdout[:200]}")
                    return None
            except json.JSONDecodeError:
                pass
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"    ✓ Uploaded to Supabase: {filename}")
            return public_url
    except subprocess.TimeoutExpired:
        pass
    print(f"    ⚠ Upload failed for {filename}")
    return None


def source_hero_image(article, used_images=None):
    """Multi-source image sourcing following IMAGE-SOURCING-RULES.md.
    
    Args:
        article: Article dict with headline, search_query, entities, etc.
        used_images: Optional set of image URLs already used in this batch.
                     If provided, will try to pick a different image.
    """
    headline = article.get("headline", "")
    search_query = article.get("image_search_query", "")
    entities = article.get("image_entities", [])
    must_show = article.get("image_must_show", "")
    slug = article.get("slug", "unknown")
    category = article.get("category", "")
    if used_images is None:
        used_images = set()

    print(f"  Sourcing hero image for: {headline[:50]}...")

    img_url = None
    attribution = "The Videshi"

    # Source 0: World Cup social images (for sports/WC articles)
    if category == "sports" and any(kw in headline.lower() for kw in ["world cup", "fifa", "semifinal", "final", "quarter"]):
        try:
            wc_cmd = f"cd {SCRIPT_DIR} && python3 wc_social_images.py --query \"{search_query or headline[:40]}\" --json-out --limit 3"
            result = subprocess.run(wc_cmd, shell=True, capture_output=True, text=True, timeout=15)
            if result.stdout.strip():
                wc_data = json.loads(result.stdout.strip())
                if wc_data and isinstance(wc_data, list) and len(wc_data) > 0:
                    # Pick first image not already used in this batch
                    for wc_item in wc_data:
                        candidate = wc_item.get("image_url")
                        if candidate and candidate not in used_images:
                            img_url = candidate
                            attribution = wc_item.get("image_credit", "FIFA/Social Media")
                            break
                    if img_url:
                        print(f"    ✓ WC social image found")
        except Exception as e:
            print(f"    ⚠ WC social images error: {e}")

    # Source 1: Wikipedia person image
    if not img_url and entities:
        for entity in entities[:3]:
            if isinstance(entity, str) and len(entity) > 2:
                wp_img = fetch_wikipedia_person_image(entity)
                if wp_img:
                    img_url = wp_img
                    attribution = "Wikimedia Commons"
                    break

    # Source 2: Wikimedia Commons search
    if not img_url:
        query = search_query or must_show or headline[:60]
        commons_img = fetch_wikimedia_commons_image(query, headline)
        if commons_img:
            img_url = commons_img
            attribution = "Wikimedia Commons"

    # Source 3: Pexels fallback
    if not img_url:
        query = search_query or must_show or headline[:40]
        pexels_img = fetch_pexels_image(query)
        if pexels_img:
            img_url = pexels_img
            attribution = "Pexels"

    if not img_url:
        print(f"    ✗ No image found (better than wrong image)")
        return None, None, None

    # Skip if this exact image was already used in the current batch
    if img_url in used_images:
        print(f"    ⚠ Image already used in this batch, skipping to avoid duplicate")
        return None, None, None

    # Download, compress, upload to Supabase
    raw_bytes = download_image(img_url)
    if not raw_bytes:
        print(f"    ⚠ Download failed: {img_url[:60]}")
        return None, None, None

    # Compute focal point before compression (higher quality = better detection)
    fx, fy = compute_focal_point(raw_bytes)
    iw, ih = image_dimensions(raw_bytes)
    article["focal_x"] = fx
    article["focal_y"] = fy
    if iw > 0 and ih > 0:
        article["img_w"] = iw
        article["img_h"] = ih
    face_flag = "👤" if (fx != 0.5 or fy != 0.5) else "📐"
    print(f"    {face_flag} Focal point: ({fx}, {fy}), {iw}×{ih}")

    compressed = compress_image(raw_bytes)
    if not compressed:
        # Use raw if compression fails (might still work)
        compressed = raw_bytes

    filename = f"{slug}.jpg"
    final_url = upload_to_supabase(compressed, filename)
    if not final_url:
        return None, None, None

    # Generate caption — keep it factual about what we KNOW, not what the image
    # should depict. The LLM's image_must_show describes what we searched for,
    # not necessarily what we found. Use a safe generic description.
    if entities and len(entities) > 0 and isinstance(entities[0], str):
        # Use the first entity as anchor but keep it generic
        caption = f"{entities[0]}"
    else:
        caption = None  # No caption is better than a wrong caption

    return final_url, attribution, caption


# ── Step 5: Insert article ──────────────────────────────────────────────────

def insert_article(article):
    """Insert article into p2_articles via REST API."""
    # Clean up internal fields not in DB
    db_article = {k: v for k, v in article.items()
                  if k not in ('image_search_query', 'image_must_show', 'image_entities')}

    result = sb_rest("POST", "p2_articles", data=db_article)
    if result and isinstance(result, list) and len(result) > 0:
        art = result[0]
        print(f"  ✓ Inserted: {art.get('headline', '')[:60]} (id: {art.get('id', '?')[:8]}...)")
        return art
    elif result and isinstance(result, dict):
        if 'error' in result or 'message' in result:
            print(f"  ✗ Insert error: {json.dumps(result)[:200]}")
            return None
        print(f"  ✓ Inserted article")
        return result
    print(f"  ✗ Insert failed: {json.dumps(result)[:200] if result else 'no response'}")
    return None


def update_topic_status(topic_id, status='used'):
    """Mark topic as used after article creation."""
    sb_query(f"UPDATE p2_topics SET status = '{status}' WHERE id = '{topic_id}'")


# ── Step 6: Trigger feed rebuild ─────────────────────────────────────────────

def rebuild_feeds():
    """Trigger feed rebuild."""
    print("\nStep 6: Rebuilding feeds...")
    try:
        result = subprocess.run(
            ["python3", "prebuild-feeds.py"],
            capture_output=True, text=True,
            cwd=SCRIPT_DIR,
            timeout=120
        )
        if result.returncode == 0:
            # Show last few lines of output
            lines = result.stdout.strip().split('\n')
            for line in lines[-5:]:
                print(f"  {line}")
            print("  ✓ Feeds rebuilt")
        else:
            print(f"  ⚠ Feed rebuild failed: {result.stderr[:200]}")
    except subprocess.TimeoutExpired:
        print("  ⚠ Feed rebuild timed out (120s)")


# ── Main pipeline ───────────────────────────────────────────────────────────

def run(dry_run=False):
    """Main rolling writer pipeline."""
    start = time.time()
    now = datetime.now(timezone.utc)
    print(f"{'='*60}")
    print(f"Rolling Writer — {now.strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"{'='*60}")

    if dry_run:
        print("*** DRY RUN — no articles will be inserted ***\n")

    # Step 1: Get candidates
    topics = get_candidate_topics()
    if not topics:
        print("\n✓ No qualifying topics. Slow news hour — exiting cleanly.")
        return 0

    # Get recent articles for dedup
    recent_articles = get_recent_articles()
    print(f"  Recent articles for dedup: {len(recent_articles)}")

    # Step 2: LLM evaluation
    selected = evaluate_topics(topics, recent_articles)
    if not selected:
        print("\n✓ No topics scored high enough. Exiting cleanly.")
        return 0

    if dry_run:
        print(f"\n*** DRY RUN complete. Would write {len(selected)} articles. ***")
        return 0

    # Steps 3-5: Write, image, insert each article
    written = 0
    batch_image_urls = set()  # Track images used in this batch to avoid duplicates
    for i, topic in enumerate(selected):
        print(f"\n{'—'*40}")
        print(f"Writing article {i+1}/{len(selected)}: {topic['canonical_title'][:60]}")
        print(f"{'—'*40}")

        # Step 3: Write article
        article = write_article(topic)
        if not article:
            print(f"  ✗ Skipping — article generation failed")
            continue

        print(f"  ✓ Generated: {article['headline'][:60]}")
        print(f"    Category: {article['category']}, Words: {article.get('word_count', 0)}")

        # Step 4: Hero image
        img_url, attribution, caption = source_hero_image(article, used_images=batch_image_urls)
        if img_url:
            article["image_url"] = img_url
            article["image_attribution"] = attribution
            article["image_caption"] = caption
            batch_image_urls.add(img_url)  # Track for batch dedup
        else:
            # No image — still publish, no image > wrong image
            article.pop("image_url", None)

        # Clean up non-DB fields
        article.pop("image_entities", None)
        article.pop("image_search_query", None)
        article.pop("image_must_show", None)

        # Step 5: Insert
        inserted = insert_article(article)
        if inserted:
            written += 1
            update_topic_status(topic['id'], 'used')
        else:
            print(f"  ✗ Insert failed for: {article['headline'][:50]}")

    # Step 6: Rebuild feeds if we wrote anything
    if written > 0:
        rebuild_feeds()

    elapsed = time.time() - start
    print(f"\n{'='*60}")
    print(f"Done. Wrote {written}/{len(selected)} articles in {elapsed:.1f}s")
    print(f"{'='*60}")
    return written


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv or "--dry" in sys.argv
    written = run(dry_run=dry_run)
    sys.exit(0)
