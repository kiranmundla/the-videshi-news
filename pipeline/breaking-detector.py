#!/usr/bin/env python3
"""
Breaking News Detector for The Videshi
Runs every 30 minutes. Scans p2_topics + web for high-urgency breaking stories
relevant to the Indian diaspora. Writes up to 2 articles per run.

Articles are inserted with status="review" so the QA reviewer promotes them.
"""

import json, os, re, subprocess, sys, time, urllib.parse, hashlib
from datetime import datetime, timezone, timedelta

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

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
GEMINI_KEY   = os.environ["GOOGLE_AI_API_KEY"]

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}
UA = "TheVideshi/1.0 (thevideshi.com)"

MAX_ARTICLES_PER_RUN = 2
URGENCY_THRESHOLD = 50  # Out of 100
LOOKBACK_MINUTES = 90
DEDUP_LOOKBACK_HOURS = 48

# ── Breaking keywords & source tiers ────────────────────────────────────────

BREAKING_KEYWORDS = {
    # Death / violence (very high urgency)
    "killed": 18, "dies": 16, "dead": 16, "shooting": 18, "attack": 16,
    "explosion": 16, "crash": 14, "earthquake": 16, "tsunami": 18,
    "war": 16, "assassination": 20, "massacre": 20, "bomb": 16,
    # Politics / geopolitics
    "sanctions": 12, "ceasefire": 14, "coup": 16, "impeach": 14,
    "resigned": 12, "fired": 10, "arrested": 14, "indicted": 14,
    "election": 10, "emergency": 14,
    # Business / tech
    "acquires": 10, "merger": 8, "ipo": 10, "layoffs": 10,
    "launches": 8, "bankrupt": 14,
    # Sports
    "wins": 8, "defeats": 8, "champion": 10, "world cup": 12,
    "semifinal": 10, "final": 8, "gold medal": 12, "record": 8,
    # General
    "breaking": 14, "just in": 12, "urgent": 12, "exclusive": 8,
}

# Diaspora relevance boosters
DIASPORA_KEYWORDS = {
    "india": 8, "indian": 10, "nri": 12, "diaspora": 12, "h-1b": 14,
    "h1b": 14, "visa": 10, "immigration": 10, "green card": 12,
    "bollywood": 8, "cricket": 8, "modi": 8, "rupee": 8,
    "desi": 8, "hindu": 6, "sikh": 6, "temple": 6,
    "pakistan": 6, "bangladesh": 6, "sri lanka": 6,
}

SOURCE_TIERS = {
    # Tier 1: Major wire services + flagships (15 pts)
    "reuters": 15, "associated press": 15, "ap news": 15, "bbc": 15,
    "al jazeera": 12, "new york times": 15, "washington post": 15,
    "cnn": 12, "guardian": 12,
    # Tier 2: Major Indian/Diaspora (12 pts)
    "ndtv": 12, "times of india": 12, "hindustan times": 12,
    "indian express": 12, "the hindu": 12, "livemint": 10,
    "economic times": 10, "scroll": 10, "the wire": 10,
    "firstpost": 10, "india today": 12,
    # Tier 3: Specialized (8 pts)
    "espncricinfo": 10, "cricbuzz": 8, "techcrunch": 10,
    "bloomberg": 12, "cnbc": 10, "moneycontrol": 8,
    "variety": 8, "deadline": 8, "hollywood reporter": 8,
}


def curl_json(url, method="GET", data=None, headers=None, timeout=20):
    """HTTP via curl (proxy-safe). Returns parsed JSON or None."""
    cmd = ["curl", "-sS", "-X", method, "--max-time", str(timeout)]
    if headers:
        for k, v in headers.items():
            cmd += ["-H", f"{k}: {v}"]
    if data:
        cmd += ["-d", json.dumps(data)]
    cmd.append(url)
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 5)
        if r.returncode != 0:
            return None
        return json.loads(r.stdout)
    except Exception as e:
        print(f"  ⚠ curl error: {e}")
        return None


# ── 1. Scan p2_topics for high-urgency pending items ────────────────────────

def fetch_recent_topics():
    """Get pending topics from the last LOOKBACK_MINUTES."""
    since = (datetime.now(timezone.utc) - timedelta(minutes=LOOKBACK_MINUTES)).isoformat()
    since_enc = urllib.parse.quote(since, safe='')
    url = (
        f"{SUPABASE_URL}/rest/v1/p2_topics"
        f"?status=eq.pending"
        f"&created_at=gte.{since_enc}"
        f"&select=id,canonical_title,vertical,urgency,score_total,signal_count,category,keywords,created_at"
        f"&order=created_at.desc"
        f"&limit=50"
    )
    return curl_json(url, headers=HEADERS) or []


def score_topic(topic):
    """Score a topic for breaking urgency (0-100)."""
    title = (topic.get("canonical_title") or "").lower()
    score = 0

    # Keyword scoring
    for kw, pts in BREAKING_KEYWORDS.items():
        if kw in title:
            score += pts

    # Diaspora relevance
    diaspora_score = 0
    for kw, pts in DIASPORA_KEYWORDS.items():
        if kw in title:
            diaspora_score += pts
    score += min(diaspora_score, 25)  # Cap diaspora bonus

    # Source tier (check topic's vertical + common source patterns)
    for source, pts in SOURCE_TIERS.items():
        if source in title:
            score += pts
            break

    # Signal count bonus (multiple sources = more important)
    signals = topic.get("signal_count") or 1
    if signals >= 5:
        score += 15
    elif signals >= 3:
        score += 10
    elif signals >= 2:
        score += 5

    # Recency bonus (more aggressive)
    created = topic.get("created_at", "")
    if created:
        try:
            dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
            age_min = (datetime.now(timezone.utc) - dt).total_seconds() / 60
            if age_min < 15:
                score += 15
            elif age_min < 30:
                score += 10
            elif age_min < 60:
                score += 5
        except:
            pass

    # p2_topics own score
    topic_score = topic.get("score_total") or 0
    if topic_score >= 70:
        score += 10
    elif topic_score >= 55:
        score += 5

    # Diaspora relevance multiplier: stories about India/diaspora get a 1.3x boost
    if diaspora_score >= 8:
        score = int(score * 1.3)

    return score


# ── 2. Check for duplicates against existing articles ───────────────────────

def fetch_recent_articles():
    """Get headlines of articles from the last DEDUP_LOOKBACK_HOURS."""
    since = (datetime.now(timezone.utc) - timedelta(hours=DEDUP_LOOKBACK_HOURS)).isoformat()
    since_enc = urllib.parse.quote(since, safe='')
    url = (
        f"{SUPABASE_URL}/rest/v1/p2_articles"
        f"?status=in.(published,review)"
        f"&published_at=gte.{since_enc}"
        f"&select=headline,slug,category"
        f"&order=published_at.desc"
        f"&limit=100"
    )
    return curl_json(url, headers=HEADERS) or []


def normalize(text):
    """Normalize text for comparison."""
    return re.sub(r'[^a-z0-9\s]', '', text.lower()).split()


def is_duplicate(candidate_title, existing_articles, min_overlap=0.45):
    """Check if candidate overlaps too much with any existing article."""
    cand_words = set(normalize(candidate_title))
    if len(cand_words) < 3:
        return True  # Too short to be meaningful

    for art in existing_articles:
        existing_words = set(normalize(art.get("headline", "")))
        if not existing_words:
            continue
        overlap = len(cand_words & existing_words)
        ratio = overlap / min(len(cand_words), len(existing_words))
        if ratio >= min_overlap:
            return True
    return False


# ── 3. Write article via Gemini ─────────────────────────────────────────────

def call_gemini(prompt, json_mode=True, max_tokens=4000):
    """Call Gemini 2.5 Flash with thinkingBudget=0 for JSON output."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_KEY}"
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": max_tokens,
            "temperature": 0.3,
            "thinkingConfig": {"thinkingBudget": 0}
        }
    }
    if json_mode:
        body["generationConfig"]["responseMimeType"] = "application/json"

    result = curl_json(url, method="POST", data=body, timeout=45,
                       headers={"Content-Type": "application/json"})
    if not result:
        return None

    try:
        text = result["candidates"][0]["content"]["parts"][0]["text"]
        if json_mode:
            return json.loads(text)
        return text
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        print(f"  ⚠ Gemini parse error: {e}")
        # Try extracting JSON from text
        if json_mode:
            try:
                raw = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                # Find JSON in the text
                match = re.search(r'\{.*\}', raw, re.DOTALL)
                if match:
                    return json.loads(match.group())
            except:
                pass
        return None


def web_search_context(query):
    """Use Gemini with Google Search grounding to get context on a breaking story."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_KEY}"
    body = {
        "contents": [{"parts": [{"text": f"Summarize the latest news about: {query}\n\nProvide key facts, quotes, and context in 300 words. Focus on the Indian diaspora angle if relevant. Include source names."}]}],
        "tools": [{"googleSearch": {}}],
        "generationConfig": {
            "maxOutputTokens": 2000,
            "temperature": 0.2,
            "thinkingConfig": {"thinkingBudget": 0}
        }
    }
    result = curl_json(url, method="POST", data=body, timeout=45,
                       headers={"Content-Type": "application/json"})
    if not result:
        return ""
    try:
        text = result["candidates"][0]["content"]["parts"][0]["text"]
        # Also try to extract grounding sources
        sources = []
        grounding = result.get("candidates", [{}])[0].get("groundingMetadata", {})
        for chunk in grounding.get("groundingChunks", []):
            web = chunk.get("web", {})
            if web.get("uri") and web.get("title"):
                sources.append({"name": web["title"], "url": web["uri"]})
        return text, sources[:4]
    except (KeyError, IndexError):
        return "", []


def determine_category(title, context=""):
    """Map a breaking story to the right Videshi category."""
    text = (title + " " + context).lower()

    if any(w in text for w in ["visa", "h-1b", "h1b", "green card", "immigration",
                                 "uscis", "ice ", "deportat", "asylum", "refugee"]):
        return "immigration"
    if any(w in text for w in ["cricket", "ipl", "bcci", "world cup", "semifinal",
                                 "match", "wicket", "innings", "rugby", "olympic",
                                 "medal", "tournament", "championship", "sport"]):
        return "sports"
    if any(w in text for w in ["bollywood", "film", "movie", "actor", "actress",
                                 "director", "ott", "netflix", "disney", "premiere",
                                 "box office", "album", "concert", "grammy"]):
        return "entertainment"
    if any(w in text for w in ["ai ", "artificial intelligence", "startup", "app ",
                                 "google", "microsoft", "apple", "meta ", "openai",
                                 "chip", "semiconductor", "software", "tech"]):
        return "technology"
    if any(w in text for w in ["stock", "market", "sensex", "nifty", "rupee",
                                 "ipo", "rbi", "fed ", "inflation", "gdp",
                                 "trade", "tariff", "oil", "crypto", "bitcoin"]):
        return "markets-finance"
    if any(w in text for w in ["nri", "abroad", "diaspora", "uk ", "canada",
                                 "australia", "expat", "overseas"]):
        return "nri-world"
    return "news"


def generate_slug(headline, date_str=None):
    """Generate a URL-friendly slug from a headline."""
    if not date_str:
        date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    # Clean headline
    slug = headline.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    slug = re.sub(r'-+', '-', slug)
    # Truncate to ~80 chars
    if len(slug) > 80:
        slug = slug[:80].rsplit('-', 1)[0]
    return f"{slug}-{date_str}"


# ── 4. Image sourcing (simplified for speed) ───────────────────────────────

def fetch_wikipedia_image(query):
    """Try Wikipedia REST API for a relevant image."""
    encoded = urllib.parse.quote(query.replace(' ', '_'))
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}"
    cmd = ["curl", "-sS", "--max-time", "10", "-A", UA, url]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=12)
        data = json.loads(r.stdout)
        img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
        if img:
            return img, "Wikimedia Commons"
    except:
        pass
    return None, None


def fetch_commons_image(query):
    """Search Wikimedia Commons for a relevant image."""
    params = urllib.parse.urlencode({
        "action": "query",
        "generator": "search",
        "gsrsearch": query,
        "gsrnamespace": "6",
        "gsrlimit": "3",
        "prop": "imageinfo",
        "iiprop": "url|size|mime",
        "iiurlwidth": "1200",
        "format": "json"
    })
    url = f"https://commons.wikimedia.org/w/api.php?{params}"
    cmd = ["curl", "-sS", "--max-time", "10", "-A", UA, url]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=12)
        data = json.loads(r.stdout)
        pages = data.get("query", {}).get("pages", {})
        for pid, page in pages.items():
            ii = page.get("imageinfo", [{}])[0]
            mime = ii.get("mime", "")
            if not mime.startswith("image/") or mime == "image/svg+xml":
                continue
            if ii.get("width", 0) < 400:
                continue
            img_url = ii.get("thumburl") or ii.get("url", "")
            if img_url:
                return img_url, "Wikimedia Commons"
    except:
        pass
    return None, None


def source_hero_image(headline, category, key_entity=None):
    """Find a hero image for the article. Returns (url, caption, attribution)."""
    # Try Wikipedia for person articles
    if key_entity:
        img, attr = fetch_wikipedia_image(key_entity)
        if img:
            return img, f"{key_entity}", attr

    # Try Commons with topic keywords
    search_terms = headline.split()[:6]
    search = " ".join(search_terms)
    img, attr = fetch_commons_image(search)
    if img:
        return img, headline[:60], attr

    # Broader commons search
    img, attr = fetch_commons_image(f"{category} {' '.join(search_terms[:3])}")
    if img:
        return img, headline[:60], attr

    return None, None, None


# ── 5. Write the article ───────────────────────────────────────────────────

def write_breaking_article(title, category, context, sources):
    """Use Gemini to write a full breaking news article for The Videshi."""
    prompt = f"""You are a senior editor at The Videshi, a news publication for the Indian diaspora in America and worldwide.

Write a breaking news article based on this developing story:

HEADLINE SIGNAL: {title}
CATEGORY: {category}
CONTEXT AND FACTS:
{context}

REQUIREMENTS:
1. Write a punchy, newspaper-style headline (under 120 characters)
2. Write a subheadline (1 sentence, ~30 words, adds nuance)
3. Write the full article body in Markdown (600-900 words)
4. Include a diaspora_angle: one sentence explaining why Indians abroad should care
5. Assign newsworthiness (1-30), diaspora_impact (1-30), prominence (1-20)
6. Generate 3-5 relevant tags (lowercase, hyphenated)
7. Identify the key person or entity for image sourcing (if any)

STYLE:
- Conversational but authoritative. Think Reuters meets Vice.
- Start with the hardest fact. No throat-clearing.
- Include the "so what" for diaspora readers early.
- Use ## subheadings to break up sections.
- End with context or what happens next, not a summary.

Return JSON with these exact fields:
{{
  "headline": "...",
  "subheadline": "...",
  "body": "... (markdown, 600-900 words)",
  "diaspora_angle": "...",
  "newsworthiness": 25,
  "diaspora_impact": 20,
  "prominence": 15,
  "tags": ["tag-1", "tag-2"],
  "key_entity": "Person or Entity Name for image" or null,
  "vertical": "short-descriptor like geopolitics, diaspora-safety, tech, sports"
}}"""

    result = call_gemini(prompt, json_mode=True, max_tokens=4000)
    if not result or "headline" not in result:
        print("  ✗ Gemini failed to generate article")
        return None

    # Source hero image
    key_entity = result.get("key_entity")
    hero_url, hero_caption, hero_attr = source_hero_image(
        result["headline"], category, key_entity
    )

    if not hero_url:
        print(f"  ⚠ No image found — article will publish without hero")

    slug = generate_slug(result["headline"])

    # Build sources JSON
    article_sources = sources if sources else [
        {"name": "Breaking Wire", "url": "https://www.reuters.com"}
    ]

    article = {
        "headline": result["headline"],
        "subheadline": result.get("subheadline", ""),
        "slug": slug,
        "body": result["body"],
        "category": category,
        "vertical": result.get("vertical", category),
        "status": "review",
        "is_editorial": False,
        "article_type": "breaking",
        "image_url": hero_url,
        "image_caption": hero_caption or "",
        "image_attribution": hero_attr or "",
        "sources": json.dumps(article_sources[:4]),
        "diaspora_angle": result.get("diaspora_angle", ""),
        "published_at": datetime.now(timezone.utc).isoformat(),
        "tags": result.get("tags", []),
        "newsworthiness": min(30, result.get("newsworthiness", 20)),
        "diaspora_impact": min(30, result.get("diaspora_impact", 15)),
        "prominence": min(20, result.get("prominence", 10)),
        "score_total": (
            min(30, result.get("newsworthiness", 20)) +
            min(30, result.get("diaspora_impact", 15)) +
            min(20, result.get("prominence", 10))
        ),
    }

    return article


def insert_article(article):
    """Insert article into Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/p2_articles"
    result = curl_json(url, method="POST", data=article, headers=HEADERS, timeout=30)
    if result and isinstance(result, list) and result:
        print(f"  ✓ Inserted: {result[0].get('slug', 'unknown')}")
        return result[0]
    elif result and isinstance(result, dict) and result.get("slug"):
        print(f"  ✓ Inserted: {result.get('slug', 'unknown')}")
        return result
    else:
        print(f"  ✗ Insert failed: {result}")
        return None


def mark_topic_used(topic_id):
    """Mark a p2_topics row as 'used' so it's not picked up again."""
    if not topic_id:
        return
    url = f"{SUPABASE_URL}/rest/v1/p2_topics?id=eq.{topic_id}"
    curl_json(url, method="PATCH",
              data={"status": "used", "updated_at": datetime.now(timezone.utc).isoformat()},
              headers=HEADERS)


def scan_web_for_breaking():
    """Use Gemini + Google Search to check for breaking events relevant to Indian diaspora.
    Returns list of dicts with title, category, score, context, sources."""
    prompt = """You are a breaking news scanner for The Videshi, a news site for the Indian diaspora.

Check for ANY of these happening RIGHT NOW (in the last 2-3 hours):
1. Major sports results: FIFA World Cup, cricket (India matches, IPL), Olympics
2. Breaking political news affecting India or Indian immigrants
3. Major tech layoffs/acquisitions affecting Indian workers
4. Attacks, disasters, or emergencies involving Indians abroad
5. Major immigration policy changes (H-1B, green card, visa announcements)
6. Major financial events (market crashes, RBI decisions, rupee moves)

For each genuinely breaking story (happened in last 2-3 hours, not old news):
Return JSON array of objects:
[
  {
    "title": "Short headline",
    "category": "one of: news, sports, technology, immigration, markets-finance, entertainment, nri-world",
    "urgency": 1-10 (10 = most urgent),
    "context": "2-3 sentence summary with key facts",
    "diaspora_relevant": true/false
  }
]

If nothing is genuinely breaking right now, return an empty array: []
Do NOT include stories older than 3 hours. Be strict about recency."""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_KEY}"
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "tools": [{"googleSearch": {}}],
        "generationConfig": {
            "maxOutputTokens": 2000,
            "temperature": 0.1,
            "thinkingConfig": {"thinkingBudget": 0}
        }
    }
    result = curl_json(url, method="POST", data=body, timeout=45,
                       headers={"Content-Type": "application/json"})
    if not result:
        return []

    try:
        text = result["candidates"][0]["content"]["parts"][0]["text"]
        # Extract JSON from text (may have surrounding markdown)
        match = re.search(r'\[.*\]', text, re.DOTALL)
        if match:
            items = json.loads(match.group())
        else:
            # Try as-is
            items = json.loads(text)
        if not isinstance(items, list):
            return []

        # Extract grounding sources
        grounding_sources = []
        grounding = result.get("candidates", [{}])[0].get("groundingMetadata", {})
        for chunk in grounding.get("groundingChunks", []):
            web = chunk.get("web", {})
            if web.get("uri") and web.get("title"):
                grounding_sources.append({"name": web["title"], "url": web["uri"]})

        # Convert to our format
        breaking = []
        for item in items:
            if not item.get("diaspora_relevant", False) and item.get("urgency", 0) < 7:
                continue  # Skip non-diaspora stories unless very urgent
            score = int(item.get("urgency", 5)) * 8  # Scale 1-10 → 8-80
            if item.get("diaspora_relevant"):
                score = int(score * 1.3)
            breaking.append({
                "title": item["title"],
                "category": item.get("category", "news"),
                "score": score,
                "context": item.get("context", ""),
                "sources": grounding_sources[:4],
            })
        return breaking
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        print(f"  ⚠ Web scan parse error: {e}")
        return []


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    print(f"=== Breaking News Detector — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} ===")

    # 1. Fetch recent topics
    topics = fetch_recent_topics()
    print(f"  Found {len(topics)} pending topics from last {LOOKBACK_MINUTES} min")

    # 1b. Also scan for live sports/event results via Gemini + Google Search
    print("  Checking for live breaking events via web...")
    web_breaking = scan_web_for_breaking()

    # 2. Score each topic
    scored = []
    for t in topics:
        s = score_topic(t)
        scored.append((s, t))
    scored.sort(key=lambda x: x[0], reverse=True)

    # Add web-sourced candidates as synthetic topics
    for wb in web_breaking:
        scored.append((wb["score"], {
            "id": None,
            "canonical_title": wb["title"],
            "category": wb["category"],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "_web_context": wb.get("context", ""),
            "_web_sources": wb.get("sources", []),
        }))

    scored.sort(key=lambda x: x[0], reverse=True)

    # Log top candidates
    if scored:
        print("\n  Top candidates:")
        for s, t in scored[:8]:
            marker = "✓" if s >= URGENCY_THRESHOLD else "·"
            print(f"    {marker} score={s:3d}  {t['canonical_title'][:70]}")

    # 3. Filter to those above threshold
    candidates = [(s, t) for s, t in scored if s >= URGENCY_THRESHOLD]
    if not candidates:
        print(f"\n  No topics above urgency threshold ({URGENCY_THRESHOLD}). Done.")
        return

    print(f"\n  {len(candidates)} candidates above threshold")

    # 4. Dedup against existing articles
    existing = fetch_recent_articles()
    print(f"  {len(existing)} existing articles in last {DEDUP_LOOKBACK_HOURS}h for dedup")

    viable = []
    for s, t in candidates:
        title = t["canonical_title"]
        if is_duplicate(title, existing):
            print(f"    SKIP (duplicate): {title[:60]}")
        else:
            viable.append((s, t))

    if not viable:
        print("  All candidates are duplicates of existing articles. Done.")
        return

    print(f"  {len(viable)} viable after dedup")

    # 5. Write articles (max MAX_ARTICLES_PER_RUN)
    written = 0
    for s, t in viable[:MAX_ARTICLES_PER_RUN]:
        title = t["canonical_title"]
        category = determine_category(title)

        print(f"\n  === Writing: {title[:70]} (score={s}, cat={category}) ===")

        # Get web context — use pre-fetched for web-sourced topics, or search for p2_topics
        pre_context = t.get("_web_context", "")
        pre_sources = t.get("_web_sources", [])
        if pre_context:
            context, web_sources = pre_context, pre_sources
        else:
            print("  Gathering web context...")
            context_result = web_search_context(title)
        if isinstance(context_result, tuple):
            context, web_sources = context_result
        else:
            context, web_sources = context_result or "", []

        if not context:
            print("  ⚠ No web context found — skipping")
            continue

        # Write the article
        print("  Writing article via Gemini...")
        article = write_breaking_article(title, category, context, web_sources)
        if not article:
            continue

        # Insert
        print("  Inserting into Supabase...")
        result = insert_article(article)
        if result:
            mark_topic_used(t["id"])
            written += 1
            print(f"  ✓ Breaking article #{written} published as 'review'")

    print(f"\n=== Done. Wrote {written} breaking article(s). ===")


if __name__ == "__main__":
    main()
