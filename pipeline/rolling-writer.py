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
# Binary editorial gate — LLM decides yes/no, ranking uses freshness + signal count
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
    """Inject rendered data card HTML into article body.

    Strategy:
    - Key takeaways go at top (skip if body already has them)
    - Data cards are distributed mid-article, not all prepended
    - <youtube> tags are preserved in their position (not pushed to end)
    """
    import re

    if not data_cards and not key_takeaways:
        return body

    # Skip key-takeaways injection if body already has them
    has_existing_kt = 'key-takeaways' in body or 'vdc-takeaways' in body
    kt_block = ''
    if key_takeaways and not has_existing_kt:
        kt_block = f'{CARD_MARKER}\n{render_takeaways_html(key_takeaways)}'

    if not data_cards:
        return (kt_block + '\n\n' + body) if kt_block else body

    # Render all data cards
    card_htmls = [f'{CARD_MARKER}\n{render_card_html(c)}' for c in data_cards]

    # Find insertion points in the body: after </p> tags or <h2> tags
    p_ends = [m.end() for m in re.finditer(r'</p>', body, re.I)]
    h2_starts = [m.start() for m in re.finditer(r'<h2[\s>]', body, re.I)]

    # Build list of insertion points (prefer after h2 sections, fallback to p tags)
    if h2_starts:
        # Insert cards before h2 tags (which start new sections)
        insert_points = h2_starts
    elif len(p_ends) >= 3:
        # No h2 tags — insert after every 2-3 paragraphs
        insert_points = [p_ends[i] for i in range(1, len(p_ends), 2)]
    else:
        # Very short body — just append cards after body
        insert_points = []

    # Distribute cards across insertion points
    result = (kt_block + '\n\n') if kt_block else ''
    if not insert_points:
        # Short body: key takeaways first, then body, then cards at end
        result += body + '\n\n' + '\n\n'.join(card_htmls)
    else:
        # Insert cards at distributed points
        # First card after 1st section, second card after 2nd section, etc.
        card_positions = {}  # body_offset -> card_html
        for ci, card_html in enumerate(card_htmls):
            if ci < len(insert_points):
                card_positions[insert_points[ci]] = card_html
            else:
                # More cards than sections — append remaining after last insert point
                last = insert_points[-1]
                card_positions[last] = card_positions.get(last, '') + '\n\n' + card_html

        # Rebuild body with cards inserted
        sorted_positions = sorted(card_positions.keys(), reverse=True)
        modified_body = body
        for pos in sorted_positions:
            modified_body = modified_body[:pos] + '\n\n' + card_positions[pos] + '\n\n' + modified_body[pos:]
        result += modified_body

    return result

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

    prompt = f"""You are the editor of The Videshi, an Indian diaspora news site serving NRIs (Non-Resident Indians) in the US, UK, and Canada.

For each signal below, make a BINARY editorial decision: should The Videshi cover this? YES or NO.

Say YES if the story meets EITHER condition:
- It directly affects or interests Indians living abroad (immigration policy, Indian-origin leaders, diaspora safety, India-bilateral relations, Indian culture/food/entertainment accessible abroad, NRI investments, cricket/sports India competes in)
- It is a major global story that any informed reader would want to know (major market moves, geopolitical crises, landmark tech developments, World Cup results) — even without a specific India angle

Say NO if:
- It is generic US/world news an NRI would not care about MORE than a random American (random court cases, local US politics, gaming news, obscure product launches)
- It is pure India local news with no diaspora connection (city accidents, state-level politics, India-only entertainment gossip)
- It is noise: routine analyst upgrades, minor earnings, press releases disguised as news

Category guidance for borderline calls:
- **immigration**: Any H-1B, green card, EB-5, OPT, USCIS, visa policy = YES. Generic US border/asylum policy = YES only if it could ripple into legal immigration.
- **markets-finance**: FAANG earnings, S&P/Nasdaq big moves, Fed decisions, US macro = YES (NRIs live and invest in the US). Indian-CEO company news (Microsoft/Nadella, Google/Pichai, IBM/Krishna) = YES. Random mid-cap earnings, dividends = NO.
- **entertainment**: Bollywood/Indian content on global platforms, Indian talent in Hollywood, crossover cultural moments = YES. Pure India box office ₹crore numbers, Bollywood gossip = NO.
- **technology**: Indian-origin tech leaders, H-1B impact from layoffs, India semiconductor/AI policy = YES. Random product launches with no India angle = NO.
- **sports**: India cricket, World Cup with India, Indian athletes globally, MLC cricket = YES. Random non-India sports = NO.
- **food**: Indian restaurants/brands in US/UK/Canada, NRI food culture, Indian recipes = YES. Pure India food news = NO.
- **news**: NRI safety, hate crimes, bilateral relations, major India events (elections, disasters) = YES. India local news (city fires, highway crashes) = NO unless nationally significant.

Each includes `hours_ago`. A story from 12+ hours ago needs to be MORE significant to justify coverage — stale routine news should be NO even if the topic is borderline.

SIGNALS:
{json.dumps(signals_for_llm, indent=2)}

For EACH signal, return:
- "idx": signal index
- "cover": true or false (your YES/NO decision)
- "suggested_category": one of immigration, technology, news, entertainment, sports, markets-finance, nri-world, food, travel, lifestyle-health
- "reason": one sentence explaining your decision
- "is_duplicate_of": idx of an earlier signal covering the same event, or null

Return a JSON object:
{{"signals": [{{"idx": 0, "cover": true, "suggested_category": "news", "reason": "...", "is_duplicate_of": null}}, ...]}}"""

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

    # Merge LLM decisions with topics
    approved = []
    for item in result:
        idx = item.get('idx')
        if idx is None or idx >= len(filtered):
            continue
        topic = filtered[idx]
        cover = item.get('cover', False)
        dup_of = item.get('is_duplicate_of')

        topic['llm_category'] = item.get('suggested_category', topic.get('category', 'news'))
        topic['llm_reason'] = item.get('reason', '')
        topic['is_duplicate_of'] = dup_of

        if dup_of is not None:
            print(f"  SKIP (LLM dup): {topic['canonical_title'][:50]} (dup of #{dup_of})")
            continue

        if cover:
            approved.append(topic)
            print(f"  ✓ YES [{topic['llm_category']:15s}] {topic['canonical_title'][:60]}")
        else:
            print(f"  ✗ NO  [{topic['llm_category']:15s}] {topic['canonical_title'][:60]}  — {item.get('reason','')[:50]}")

    # Rank approved topics by freshness (hours_ago asc) then signal count (desc)
    approved.sort(key=lambda x: (x.get('hours_ago', 999), -x.get('signal_count', 1)))

    # Category diversity: don't let one category take all slots
    selected = []
    cat_counts = {}
    for t in approved:
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
        print(f"    [{t.get('llm_category', '?'):15s}] {t['canonical_title'][:60]}")

    return selected


# ── Step 3: Write articles ──────────────────────────────────────────────────

def get_signal_urls(topic_id):
    """Get source URLs from signals linked to this topic."""
    sql = f"""
    SELECT s.title, s.original_url, f.name as source_name, s.published_at
    FROM p2_topic_signals ts
    JOIN p2_signals s ON ts.signal_id = s.id
    JOIN p2_feed_sources f ON s.feed_source_id = f.id
    WHERE ts.topic_id = '{topic_id}'
    ORDER BY s.published_at DESC
    LIMIT 5
    """
    return sb_query(sql) or []


def get_event_time(topic_id):
    """Get the earliest signal published_at for this topic — when the event actually happened."""
    sql = f"""
    SELECT MIN(s.published_at) as event_at
    FROM p2_topic_signals ts
    JOIN p2_signals s ON ts.signal_id = s.id
    WHERE ts.topic_id = '{topic_id}'
    """
    rows = sb_query(sql) or []
    if rows and rows[0].get('event_at'):
        return rows[0]['event_at']
    return None


def get_signal_stats(topic_id):
    """Get signal count and max Google cluster size for this topic."""
    sql = f"""
    SELECT COUNT(*) as signal_count,
           COALESCE(MAX(s.google_cluster_size), 0) as google_cluster_size
    FROM p2_topic_signals ts
    JOIN p2_signals s ON ts.signal_id = s.id
    WHERE ts.topic_id = '{topic_id}'
    """
    rows = sb_query(sql) or []
    if rows:
        return rows[0].get('signal_count', 0), rows[0].get('google_cluster_size', 0)
    return 0, 0


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
3. **body**: 600-900 words in clean HTML. Use <h2> for section subheadings, <p> for paragraphs. Do NOT use markdown syntax (no ##, no **, no []()). Use present tense for current events. Include at least one section header. No promotional language.{'' if category == 'markets-finance' else ' Include a diaspora perspective (why NRIs should care).'}
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
- Use <h2> for section headers (HTML, not markdown ##)
- No "In conclusion" or "In summary" — end with impact, a forward-looking point, or what to watch next
- Output body as clean HTML (<h2>, <p>, <ul>/<li> for lists). No markdown. No ** for bold — use <strong> if needed.

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

    # Convert any stray markdown to HTML (safety net)
    body = re.sub(r'^### (.+)$', r'<h3>\1</h3>', body, flags=re.MULTILINE)
    body = re.sub(r'^## (.+)$', r'<h2>\1</h2>', body, flags=re.MULTILINE)
    body = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', body)

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
        "event_at": get_event_time(topic['id']),
        "image_search_query": result.get('image_search_query', ''),
        "image_must_show": result.get('image_must_show', ''),
        "image_entities": result.get('image_entities', []),
    }

    # Add signal stats (one query)
    sig_count, gcs = get_signal_stats(topic['id'])
    article["signal_count"] = sig_count
    article["google_cluster_size"] = gcs

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
