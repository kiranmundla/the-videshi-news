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
# focal_point imported inside image_sourcer

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
MIN_COMBINED_SCORE = 13  # minimum newsworthiness + diaspora_relevance for LLM eval
LOOKBACK_HOURS = 12      # how far back to look for topics
DEDUP_HOURS = 48         # how far back to check for duplicate articles

# Category freshness targets — max hours before a category is "stale" and needs
# a forced article. Prevents high-signal categories (news, tech) from starving
# lower-volume categories (food, travel, lifestyle-health).
CATEGORY_FRESHNESS_TARGET = {
    "news": 3,
    "technology": 4,
    "immigration": 6,
    "sports": 4,
    "markets-finance": 4,
    "entertainment": 6,
    "nri-world": 8,
    "lifestyle-health": 8,
    "travel": 10,
    "food": 10,
}

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

CARD_MARKER = '<!-- data-card -->'

# ── Data card rendering (inline from render-data-cards.py) ───────────────────

def _esc(s):
    return (str(s) if s is not None else "").replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"',"&quot;")

def render_card_html(card):
    """Render a data card dict to HTML using vdc-* CSS classes."""
    ctype = card.get("card_type", "stat_grid")
    title = _esc(card.get("card_title", ""))
    hs = card.get("hero_stat")
    items = card.get("items", [])
    source = _esc(card.get("source_note", ""))

    html = '<div class="vdc"><div class="vdc-glow"></div>'
    if title:
        html += f'<div class="vdc-title">{title}</div>'

    if hs:
        val = _esc(hs.get("value", ""))
        label = _esc(hs.get("label", ""))
        trend = _esc(hs.get("trend", ""))
        trend_cls = "vdc-hero-trend-neg" if (trend.startswith("↓") or trend.startswith("-")) else "vdc-hero-trend"
        html += '<div class="vdc-hero">'
        html += f'<div class="vdc-hero-num">{val}</div>'
        if trend:
            html += f'<div class="{trend_cls}">{trend}</div>'
        if label:
            html += f'<div class="vdc-hero-label">{label}</div>'
        html += '</div>'

    if ctype == "stat_grid":
        html += '<div class="vdc-grid">'
        for item in items:
            v = _esc(item.get("value", ""))
            l = _esc(item.get("label", ""))
            html += f'<div class="vdc-stat"><div class="vdc-stat-val">{v}</div><div class="vdc-stat-lbl">{l}</div></div>'
        html += '</div>'

    elif ctype == "comparison":
        max_nv = max((abs(i.get("numeric_value") or 0) for i in items), default=1) or 1
        for item in items:
            name = _esc(item.get("name", item.get("label", "")))
            val = _esc(item.get("value", ""))
            nv = item.get("numeric_value") or 0
            pct = max(int(abs(nv) / abs(max_nv) * 100), 12)
            fill_cls = "vdc-bar-fill-neg" if nv < 0 else "vdc-bar-fill"
            html += (f'<div class="vdc-bar-row"><div class="vdc-bar-name">{name}</div>'
                     f'<div class="vdc-bar-track"><div class="{fill_cls}" style="width:{pct}%">{val}</div></div></div>')

    elif ctype == "timeline":
        html += '<div class="vdc-tl">'
        for item in items:
            dt = _esc(item.get("date", ""))
            ev = _esc(item.get("event", item.get("text", "")))
            html += (f'<div class="vdc-tl-item"><div class="vdc-tl-dot"></div>'
                     f'<div class="vdc-tl-date">{dt}</div><div class="vdc-tl-event">{ev}</div></div>')
        html += '</div>'

    elif ctype == "highlights":
        for item in items:
            stat = _esc(item.get("stat", item.get("value", "")))
            text = _esc(item.get("text", item.get("label", "")))
            badge = f'<span class="vdc-badge">{stat}</span> ' if stat else ""
            html += (f'<div class="vdc-bullet"><span class="vdc-bullet-arrow">›</span>{badge}{text}</div>')

    if source:
        html += f'<div class="vdc-footer">{source}</div>'
    html += '</div>'
    return html

def render_takeaways_html(takeaways):
    """Render key takeaways list to HTML."""
    if not takeaways:
        return ""
    html = '<div class="vdc-takeaways"><div class="vdc-takeaways-title">Key Takeaways</div><ul>'
    for t in takeaways:
        html += f'<li>{_esc(t)}</li>'
    html += '</ul></div>'
    return html

def inject_data_cards(body, data_cards, key_takeaways):
    """Inject rendered data card HTML into article body."""
    blocks = []
    # Key takeaways always go first
    if key_takeaways:
        blocks.append(f'{CARD_MARKER}\n{render_takeaways_html(key_takeaways)}')
    # Data cards: stat_grid/after_lead first, then mid-article cards
    for card in (data_cards or []):
        blocks.append(f'{CARD_MARKER}\n{render_card_html(card)}')
    if not blocks:
        return body
    # Prepend all cards before the article body
    return '\n\n'.join(blocks) + '\n\n' + body

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
    # The topic table has many low-quality signals all at the same score (~52).
    # We need to cast a WIDE net and let the LLM evaluation do the real filtering.
    # Strategy:
    # 1. Top by signal_count (catches multi-signal stories that multiple feeds picked up)
    # 2. Top by recency (catches fresh breaking stories even if single-signal)
    # 3. Sample across categories (ensures category diversity)
    sql = f"""
    (SELECT t.id, t.canonical_title, t.category, t.urgency,
           t.score_total, t.signal_count, t.keywords, t.status,
           t.created_at
    FROM p2_topics t
    WHERE t.created_at > now() - interval '{LOOKBACK_HOURS} hours'
      AND t.status = 'pending'
      AND t.score_total >= 40
    ORDER BY t.signal_count DESC, t.score_total DESC
    LIMIT 50)
    UNION
    (SELECT t.id, t.canonical_title, t.category, t.urgency,
           t.score_total, t.signal_count, t.keywords, t.status,
           t.created_at
    FROM p2_topics t
    WHERE t.created_at > now() - interval '{LOOKBACK_HOURS} hours'
      AND t.status = 'pending'
      AND t.score_total >= 40
    ORDER BY t.created_at DESC
    LIMIT 50)
    UNION
    (SELECT t.id, t.canonical_title, t.category, t.urgency,
           t.score_total, t.signal_count, t.keywords, t.status,
           t.created_at
    FROM p2_topics t
    WHERE t.created_at > now() - interval '{LOOKBACK_HOURS} hours'
      AND t.status = 'pending'
      AND t.score_total >= 40
    ORDER BY random()
    LIMIT 100)
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
    SELECT headline, subheadline, slug, category FROM p2_articles
    WHERE published_at > now() - interval '{DEDUP_HOURS} hours'
      AND status IN ('published', 'review')
    ORDER BY published_at DESC
    LIMIT 200
    """
    return sb_query(sql) or []


def check_duplicate(topic_title, recent_articles, threshold=3):
    """Check if a topic is already covered by a recent article.
    
    Returns the matched article headline if duplicate, else None.
    Uses category-aware matching: within the same category, threshold is lower (2).
    Checks both headline and subheadline for broader coverage detection.
    """
    topic_kw = set(extract_keywords(topic_title))
    if not topic_kw:
        return None

    for art in recent_articles:
        # Combine headline + subheadline keywords for the article
        art_text = art.get('headline', '')
        sub = art.get('subheadline', '')
        if sub:
            art_text += ' ' + sub
        art_kw = set(extract_keywords(art_text))
        overlap = topic_kw & art_kw

        if len(overlap) >= threshold:
            return art.get('headline', 'unknown')

    return None


# ── Step 2: LLM evaluation ──────────────────────────────────────────────────

def evaluate_topics(topics, recent_articles):
    """Use Gemini to score topics for newsworthiness and diaspora relevance."""
    print(f"\nStep 2: LLM evaluation of {len(topics)} candidates...")

    # Pre-filter duplicates
    filtered = []
    for t in topics:
        title = t.get('canonical_title', '')
        dup_match = check_duplicate(title, recent_articles)
        if dup_match:
            print(f"  SKIP (duplicate of \"{dup_match[:40]}\"): {title[:60]}")
            continue
        filtered.append(t)

    if not filtered:
        print("  All topics already covered.")
        return []

    print(f"  {len(filtered)} topics after dedup filter")

    # Prepare signal list for LLM (max 25 to keep prompt manageable)
    signals_for_llm = []
    now = datetime.now(timezone.utc)
    for i, t in enumerate(filtered[:80]):
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
2. **diaspora_relevance** (1-10): How relevant is this to Indians living abroad? The reader is an NRI in the US/UK/Canada — would they specifically seek this out? Score per category:

**immigration**: H-1B, green card, EB-5, OPT, visa processing, USCIS policy, deportation, citizenship = 8-10. Generic US immigration (border, asylum, non-Indian) = 4-6 only if it affects policy broadly. Pure India domestic immigration law = 2-3.

**markets-finance**: FAANG/mega-cap earnings (Apple, Google, Microsoft, Amazon, Meta, Tesla, NVIDIA, Netflix, JPMorgan, Goldman Sachs), S&P 500/Nasdaq big moves, Fed rate decisions, US inflation/CPI, US jobs/housing = 7-9 (NRIs live and invest in the US). Indian-CEO companies (Google/Pichai, Microsoft/Nadella, IBM/Krishna, Starbucks/Narasimhan) = 8-9. NRI investment angles (remittances, FCNR/NRE deposits, India mutual funds for NRIs) = 8-10. Random mid-cap earnings, dividends, analyst upgrades = 2-4 (noise). Indian markets (Sensex, RBI, rupee) = 6-8 ONLY for major events with NRI impact, 3-5 for routine daily moves.

**entertainment**: Bollywood/Indian films releasing or streaming in US/UK/Canada theaters/platforms (where NRIs watch) = 7-9. Indian actors/directors at international festivals, awards, or Hollywood projects = 8-10. Indian-origin talent in global entertainment = 8-10. Crossover cultural moments (Indian music at Coachella, Indian shows on Netflix global) = 7-9. Pure India box office numbers (₹crore collections, opening day records) with NO international release or diaspora viewing angle = 2-3. India-only TV show drama, Bollywood gossip/weddings/breakups with no diaspora connection = 1-3.

**technology**: Indian-origin tech leaders (Pichai, Nadella, Agrawal) = 8-9. Indian tech companies expanding globally or hiring/laying off in US = 7-9. H-1B/immigration impact from tech layoffs = 8-10. India semiconductor/AI policy affecting global supply chain = 7-8. Random tech product launches with no India/diaspora angle = 2-4.

**sports**: India cricket (always relevant to diaspora) = 7-9. World Cup / Olympics with India or Indian-origin athletes = 8-10. Indian sports leagues with global broadcast (IPL, ISL) = 7-8. Indian-origin athletes in US/UK/global sports = 8-10. NRI community sports (MLC cricket, diaspora football) = 8-10. Random non-India international sports = 2-3.

**food**: Indian restaurants opening/winning awards in US/UK/Canada = 8-10. Indian grocery/food brands in Western supermarkets = 7-9. NRI food culture, fusion cuisine = 7-8. Pure India restaurant/food news with no diaspora angle = 2-3.

**news**: Stories directly affecting NRIs (safety, hate crimes, discrimination, bilateral relations, travel advisories) = 8-10. Major India events that every NRI follows (elections, disasters, geopolitical crises) = 7-9. Indian-origin people in global headlines = 7-9. Pure India local news (city fires, highway accidents, local politics) = 2-4 unless scale/impact is national. Generic US/world news with no India/diaspora connection = 2-3.

**nri-world**: Community achievements, diaspora organizations, cultural events abroad = 8-10. This is the core diaspora category.

**lifestyle-health, travel**: NRI-specific health/travel concerns (India travel tips, healthcare for NRIs visiting India, wellness trends in diaspora) = 7-9. Generic health/travel news = 2-4.

DEFAULT RULE: If an NRI in the US would not care about this story MORE than a random American would, score 1-4. The diaspora angle must be genuine, not forced.
3. **suggested_category**: One of: immigration, technology, news, entertainment, sports, markets-finance, nri-world, food, travel, lifestyle-health
4. **reason**: One sentence explaining your scoring.

Also flag if any are essentially about the same event (duplicate detection).

SIGNALS:
{json.dumps(signals_for_llm, indent=2)}

Score ALL signals. Be strict — a World Cup semifinal result scores 9-10. A random court case scores 3-4. A story about H-1B visa changes scores 9-10.

Return a JSON object with key "signals" containing the array:
{{"signals": [{{"idx": 0, "newsworthiness": 8, "diaspora_relevance": 7, "suggested_category": "news", "reason": "...", "is_duplicate_of": null}}, ...]}}"""

    result = call_llm(prompt, json_mode=True, max_tokens=5000)
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

        if dr < 5:
            print(f"  ✗ [{nw}+{dr}={combined}] low diaspora relevance: {topic['canonical_title'][:55]}")
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

    today_str = datetime.now(timezone.utc).strftime('%B %d, %Y')
    prompt = f"""You are a senior journalist at The Videshi, a premium English-language news site for the Indian diaspora (NRIs worldwide).

TODAY'S DATE: {today_str}. All events described are current unless explicitly historical. Do NOT invent dates, quotes, or statistics. If you are unsure of a specific date, score, or detail, omit it rather than fabricate it. NEVER reference dates from past years (2023, 2024, 2025) for current events.

COPYRIGHT & SYNTHESIS RULES (critical — violations destroy the publication):
- Extract FACTS ONLY from source articles: numbers, dates, names, events, outcomes. NEVER copy sentences, phrases, or paraphrased paragraphs from any source. Every sentence must be your original prose.
- SYNTHESIZE across multiple sources to build a more complete picture than any single source provides. Do not rewrite one wire story — combine facts from all available references.
- ADD CONTEXT the sources don't provide: who the person/company is, historical background, relevant public statistics (e.g., "India's IT sector employs 5.4 million people" for a tech layoff story, or "H-1B visa applications hit 780,000 in FY2025" for an immigration story). Use widely-known public facts to enrich the article.
- The finished article must be MORE USEFUL than any single source. A reader who already read Reuters should learn something new from your piece — broader context, clearer data, diaspora perspective.

Write a complete article about:

TOPIC: {title}

CATEGORY: {category}

SOURCE REFERENCES (extract facts from these — cite at least 2, but write entirely original prose):
{source_context if source_context else "Research the topic using your knowledge."}

REQUIREMENTS:
1. **headline**: 20-120 chars. Newspaper style — short, punchy, declarative. Not clickbait.
2. **subheadline**: 30-120 chars. Adds nuance/context the headline doesn't cover.
3. **body**: 600-900 words in markdown. Well-structured with ## subheadings. Use present tense for current events. Include at least one section header. No promotional language.{'' if category == 'markets-finance' else ' Include a diaspora perspective (why NRIs should care).'}
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
16. **key_takeaways**: Array of 3-5 bullet point strings. Each is a complete, standalone insight under 20 words. These appear as a highlighted card at the top of the article, letting readers grasp the story in 10 seconds. Every stat/number MUST come from the article body.
17. **data_cards**: Array of 0-2 data cards. Include ONLY if the article has meaningful numbers/statistics. Each card has:
    - "card_title": Punchy editorial title (NOT the article headline repeated)
    - "card_type": One of "stat_grid", "comparison", "timeline", "highlights"
    - "hero_stat" (for stat_grid only): {{"value": "$70B", "label": "Market Cap Loss", "trend": "↓ 12%"}}
    - "items": Array of data points:
      - stat_grid: [{{"value": "12%", "label": "Share Drop"}}, ...] — 2-4 items
      - comparison: [{{"name": "CrowdStrike", "value": "+15%", "numeric_value": 15}}, ...] — 3-6 items sorted by numeric_value desc
      - timeline: [{{"date": "Jul 10", "event": "..."}}, ...] — 3-6 items chronological
      - highlights: [{{"text": "...", "stat": "42%"}}, ...] — 3-5 items
    - "source_note" (optional): Brief source attribution
    If no meaningful stats exist, return an EMPTY array []. Do not force cards with generic filler.

STYLE GUIDE:
- Write like The Economist or Bloomberg — authoritative, precise, data-rich. Not a blog, not a press release.
- Lead with the news (what happened), then context (why it matters), then analysis (what comes next).
- Include specific numbers, names, dates, and data points throughout. Vague claims like "significant growth" are unacceptable — find the number or omit the claim.
- Every article must contain at least 3 concrete data points (percentages, dollar amounts, counts, dates). Pull these from the source facts AND from public knowledge to enrich the piece.
- NEVER open with "In a significant development..." or "In a major move..." or any similar throat-clearing. Start with the news itself.
- No filler phrases, no promotional language, no rhetorical questions in headlines.
- For markets-finance: if the story is about major US/global companies (earnings, stock moves), US market indices (S&P 500, Nasdaq, Dow), Fed decisions, US inflation, jobs data, housing, or mortgage rates — write it as straight financial journalism for a US-based audience. Do NOT add "here's what it means for NRIs" or "diaspora perspective" paragraphs. Do NOT mention NRIs, remittances, or Indians abroad. These stories are inherently relevant to readers who live and invest in the US. Only add a diaspora angle when the story is about Indian markets (Sensex, RBI, rupee) and the NRI connection genuinely needs explaining.
- For other categories: weave in diaspora context naturally where it adds value. Don't force a "why NRIs should care" section — if the connection is obvious (H-1B policy change), the article speaks for itself. Add it when it's not obvious (a tech layoff's impact on H-1B workers, or an Indian food trend reaching US cities).
- Use ## for section headers, not #
- No "In conclusion" or "In summary" — end with impact, a forward-looking point, or what to watch next

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

    # Render data cards and key takeaways into the body
    key_takeaways = result.get('key_takeaways', [])
    data_cards = result.get('data_cards', [])

    # Validate key_takeaways
    if isinstance(key_takeaways, list) and key_takeaways:
        key_takeaways = [str(t) for t in key_takeaways if t][:5]
    else:
        key_takeaways = []

    # Validate data_cards
    valid_card_types = {"stat_grid", "comparison", "timeline", "highlights"}
    validated_cards = []
    if isinstance(data_cards, list):
        for card in data_cards[:2]:
            if (isinstance(card, dict)
                and card.get("card_title")
                and card.get("card_type") in valid_card_types
                and isinstance(card.get("items"), list)
                and len(card["items"]) >= 1):
                validated_cards.append(card)
    data_cards = validated_cards

    # Inject rendered HTML into body
    if key_takeaways or data_cards:
        article["body"] = inject_data_cards(article["body"], data_cards, key_takeaways)
        n_kt = len(key_takeaways)
        n_dc = len(data_cards)
        print(f"  📊 Data cards: {n_kt} takeaways, {n_dc} cards")

    # Save JSON for the enriched_at / data_cards / key_takeaways columns
    article["key_takeaways"] = key_takeaways
    article["data_cards"] = data_cards
    article["enriched_at"] = datetime.now(timezone.utc).isoformat()
    article["cards_rendered_at"] = datetime.now(timezone.utc).isoformat()

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

# Import from shared image sourcing module
from image_sourcer import source_hero_image


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


# ── Category Freshness: stale-category backfill ─────────────────────────────

def get_stale_categories():
    """Find categories that haven't had a new article within their freshness target."""
    stale = []
    for cat, max_hours in CATEGORY_FRESHNESS_TARGET.items():
        sql = f"""
        SELECT published_at FROM p2_articles
        WHERE category = '{cat}'
          AND status IN ('published', 'review')
        ORDER BY published_at DESC
        LIMIT 1
        """
        result = sb_query(sql)
        if not result:
            stale.append(cat)
            continue
        last_pub = result[0].get('published_at', '')
        try:
            last_dt = datetime.fromisoformat(last_pub.replace('Z', '+00:00'))
            hours_since = (datetime.now(timezone.utc) - last_dt).total_seconds() / 3600
            if hours_since > max_hours:
                stale.append(cat)
        except (ValueError, TypeError):
            stale.append(cat)
    return stale


def get_backfill_topics(stale_categories, recent_articles):
    """Find the best pending topic in each stale category for forced writing."""
    backfill = []
    for cat in stale_categories:
        sql = f"""
        SELECT t.id, t.canonical_title, t.category, t.urgency,
               t.score_total, t.signal_count, t.keywords, t.status,
               t.created_at
        FROM p2_topics t
        WHERE t.created_at > now() - interval '24 hours'
          AND t.status = 'pending'
          AND t.category = '{cat}'
          AND t.score_total >= 10
        ORDER BY t.score_total DESC, t.signal_count DESC
        LIMIT 5
        """
        candidates = sb_query(sql)
        if not candidates:
            continue

        # Filter out duplicates and Hindi
        for t in candidates:
            title = t.get('canonical_title', '')
            if is_hindi(title):
                continue
            if check_duplicate(title, recent_articles, threshold=3):
                continue
            # Check not already written
            existing = sb_query(f"""
                SELECT id FROM p2_articles
                WHERE topic_id = '{t["id"]}' AND status IN ('published','review')
                LIMIT 1
            """)
            if existing:
                continue
            # Found a usable topic for this stale category
            t['llm_category'] = cat
            t['is_backfill'] = True
            backfill.append(t)
            print(f"  📌 Backfill [{cat}]: {title[:60]}")
            break

    return backfill


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
        print("\n✓ No topics scored high enough.")
        # Still check for stale categories even if no top picks
        selected = []

    # Step 2b: Category freshness — backfill stale categories
    stale = get_stale_categories()
    if stale:
        # Don't backfill categories we're already writing about
        already_covered = {t.get('llm_category', t.get('category', 'news')) for t in selected}
        stale_uncovered = [c for c in stale if c not in already_covered]
        if stale_uncovered:
            print(f"\n  📊 Stale categories ({len(stale_uncovered)}): {', '.join(stale_uncovered)}")
            backfill = get_backfill_topics(stale_uncovered, recent_articles)
            if backfill:
                selected.extend(backfill)
                print(f"  Added {len(backfill)} backfill topics")
    else:
        print("  All categories fresh ✓")

    if not selected:
        print("\n✓ No topics to write. Exiting cleanly.")
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
