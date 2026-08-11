#!/usr/bin/env python3
"""
Pipeline V3 Ingest — Topic-centric signal ingestion for The Videshi.

Key difference from V2: preserves Google News cluster grouping and uses GPT
to match RSS/email signals to existing topics. Each signal is processed once
(URL hash dedup), and every signal gets a topic_id.

Sources: RSS feeds (from p2_feed_sources) + Google News (topic + search) + email_signals.
Outputs: signals → p2_signals (with topic_id), topics → p2_topics.

Usage:
  python3 v3-ingest.py                  # full run
  python3 v3-ingest.py --dry-run        # no DB writes
  python3 v3-ingest.py --rss-only       # skip Google News
  python3 v3-ingest.py --google-only    # skip RSS
"""

import os, sys, json, hashlib, re, html, time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from urllib.parse import quote as urlquote, urlparse, parse_qs, urlencode
from concurrent.futures import ThreadPoolExecutor, as_completed
from email.utils import parsedate_to_datetime
import subprocess
import uuid

# ── Options ───────────────────────────────────────────────────────────────────

DRY_RUN      = "--dry-run" in sys.argv
RSS_ONLY     = "--rss-only" in sys.argv
GOOGLE_ONLY  = "--google-only" in sys.argv
VERBOSE      = "--verbose" in sys.argv or DRY_RUN

NOW          = datetime.now(timezone.utc)
NOW_ISO      = NOW.isoformat()
HASH_WINDOW  = 14  # days of hashes to load for dedup
FEED_TIMEOUT = 8   # seconds per feed
MAX_WORKERS  = 10  # parallel feed fetches
TOPIC_WINDOW = 336  # hours (14 days) — match against topics in this window; Google News can resurface stories for weeks

# ── Supabase ──────────────────────────────────────────────────────────────────

def load_env(*paths):
    env = {}
    for p in paths:
        p = os.path.expanduser(p)
        if not os.path.exists(p):
            continue
        with open(p) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    env[k.strip()] = v.strip().strip('"').strip("'")
    return env

ENV = load_env("~/workspace/.env.supabase", "~/workspace/.env.openai")
SB_URL = ENV.get("SUPABASE_URL", "")
SB_KEY = ENV.get("SUPABASE_SERVICE_ROLE_KEY", "")
OPENAI_KEY = ENV.get("OPENAI_API_KEY", "")

def sb_get(endpoint, params=None, range_header=None):
    url = f"{SB_URL}/rest/v1/{endpoint}"
    if params:
        qs = "&".join(f"{k}={urlquote(str(v), safe='.,()')}" for k, v in params.items())
        url = f"{url}?{qs}"
    cmd = ["curl", "-sS", "--max-time", "20", url,
           "-H", f"apikey: {SB_KEY}",
           "-H", f"Authorization: Bearer {SB_KEY}"]
    if range_header:
        cmd += ["-H", f"Range: {range_header}"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=25)
    try:
        return json.loads(r.stdout)
    except:
        return []

def sb_post(endpoint, data, upsert=False):
    """Post data to Supabase. Uses temp file for large payloads."""
    url = f"{SB_URL}/rest/v1/{endpoint}"
    if upsert:
        url += "?on_conflict=url_hash"
        prefer = "resolution=ignore-duplicates,return=minimal"
    else:
        prefer = "return=minimal"
    headers = [
        "-H", f"apikey: {SB_KEY}",
        "-H", f"Authorization: Bearer {SB_KEY}",
        "-H", "Content-Type: application/json",
        "-H", f"Prefer: {prefer}",
    ]
    payload = json.dumps(data)
    # Use temp file for large payloads
    import tempfile
    if len(payload) > 50000:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            tmp.write(payload)
            tmp_path = tmp.name
        try:
            cmd = ["curl", "-sS", "--max-time", "30", "-X", "POST", url] + headers + ["-d", f"@{tmp_path}"]
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=35)
            ok = r.returncode == 0 and r.stdout.strip() in ("", "[]")
            if not ok:
                print(f"    ⚠️  sb_post {endpoint} FAIL (large): rc={r.returncode} body={r.stdout[:300]}")
            return ok
        finally:
            os.unlink(tmp_path)
    else:
        cmd = ["curl", "-sS", "--max-time", "20", "-X", "POST", url] + headers + ["-d", payload]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=25)
        ok = r.returncode == 0 and r.stdout.strip() in ("", "[]")
        if not ok:
            print(f"    ⚠️  sb_post {endpoint} FAIL: rc={r.returncode} body={r.stdout[:300]}")
        return ok


def flush_to_db(new_topics, signals, topic_signal_counts, label=""):
    """Write a batch of topics + signals to DB immediately. Returns counts."""
    if DRY_RUN:
        return len(new_topics), len(signals)

    topics_written = 0
    signals_written = 0

    # Insert new topics
    if new_topics:
        topic_rows = []
        for t in new_topics:
            count = topic_signal_counts.get(t["id"], 0)
            topic_rows.append({
                "id": t["id"],
                "canonical_title": t["canonical_title"],
                "vertical": "general",
                "keywords": [],
                "status": "pending",
                "signal_count": count,
                "created_at": NOW_ISO,
                "updated_at": NOW_ISO,
                "last_signal_at": NOW_ISO,
                "lifecycle": "emerging",
                "source_types": ["google_news", "rss"],
            })
        BATCH = 50
        for i in range(0, len(topic_rows), BATCH):
            batch = topic_rows[i:i+BATCH]
            if sb_post("p2_topics", batch):
                topics_written += len(batch)

    # Insert signals (upsert to skip dupes)
    if signals:
        # Normalize keys — PostgREST PGRST102 requires all objects to have the same keys
        all_keys = set()
        for row in signals:
            all_keys.update(row.keys())
        for row in signals:
            for k in all_keys:
                if k not in row:
                    row[k] = None

        BATCH = 50
        for i in range(0, len(signals), BATCH):
            batch = signals[i:i+BATCH]
            ok = sb_post("p2_signals", batch, upsert=True)
            if ok:
                signals_written += len(batch)
            else:
                print(f"    ⚠️  Signal batch {i}-{i+len(batch)} FAILED (sb_post returned False)")

    if topics_written or signals_written:
        print(f"    💾 DB flush{' ('+label+')' if label else ''}: {topics_written} topics, {signals_written} signals")

    return topics_written, signals_written

def sb_patch(endpoint, data, match_params):
    url = f"{SB_URL}/rest/v1/{endpoint}"
    qs = "&".join(f"{k}={urlquote(str(v), safe='.,()')}" for k, v in match_params.items())
    url = f"{url}?{qs}"
    payload = json.dumps(data)
    cmd = ["curl", "-sS", "--max-time", "20", "-X", "PATCH", url,
           "-H", f"apikey: {SB_KEY}",
           "-H", f"Authorization: Bearer {SB_KEY}",
           "-H", "Content-Type: application/json",
           "-H", "Prefer: return=minimal",
           "-d", payload]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=25)
    return r.returncode == 0

# ── URL normalization ─────────────────────────────────────────────────────────

TRACKING_PARAMS = {
    'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
    'fbclid', 'gclid', 'ref', 'source', 'ncid', 'ocid', 'dicbo', 'ito',
    'ns_mchannel', 'ns_source', 'ns_campaign', 'ns_linkname', 'ns_fee',
}

def normalize_url(url):
    try:
        parsed = urlparse(url)
        if parsed.query:
            params = parse_qs(parsed.query, keep_blank_values=True)
            clean = {k: v for k, v in params.items() if k.lower() not in TRACKING_PARAMS}
            query = urlencode(clean, doseq=True)
        else:
            query = ""
        path = parsed.path.rstrip('/')
        netloc = parsed.netloc.lower()
        if netloc.startswith('www.'):
            netloc = netloc[4:]
        return f"{parsed.scheme}://{netloc}{path}{'?' + query if query else ''}"
    except:
        return url

def url_hash(url):
    normalized = normalize_url(url)
    return hashlib.md5(normalized.encode()).hexdigest()

# ── Feed fetching ─────────────────────────────────────────────────────────────

def fetch_url(url, timeout=FEED_TIMEOUT):
    cmd = ["curl", "-sS", "--max-time", str(timeout),
           "-A", "Mozilla/5.0 (compatible; TheVideshi/1.0; +https://thevideshi.com)",
           url]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout+5)
        return r.stdout if r.returncode == 0 else ""
    except:
        return ""

def parse_pub_date(pub_str):
    if not pub_str:
        return None
    try:
        dt = parsedate_to_datetime(pub_str)
        return dt.isoformat()
    except:
        try:
            return datetime.fromisoformat(pub_str.replace('Z', '+00:00')).isoformat()
        except:
            return None

def parse_feed_xml(xml_str):
    """Parse RSS/Atom feed. Returns list of items with sub_articles for Google News."""
    items = []
    try:
        root = ET.fromstring(xml_str)
    except ET.ParseError:
        return items

    media_ns = {'media': 'http://search.yahoo.com/mrss/'}

    # RSS 2.0
    for item in root.findall('.//item'):
        title = (item.findtext('title') or '').strip()
        link = (item.findtext('link') or '').strip()
        pub = (item.findtext('pubDate') or item.findtext('dc:date') or '').strip()
        source_el = item.find('source')
        source_name = (source_el.text or '').strip() if source_el is not None else ''

        # Google News: extract sub-articles from description
        desc_raw = html.unescape(item.findtext('description') or '')
        sub_articles = []
        if '<li>' in desc_raw:
            # Extract all linked articles from the cluster
            for match in re.finditer(r'<a\s+href="([^"]+)"[^>]*>([^<]{10,})</a>\s*<font[^>]*>([^<]*)</font>', desc_raw):
                sub_url, sub_title, sub_source = match.group(1), match.group(2).strip(), match.group(3).strip()
                sub_articles.append({
                    'url': sub_url,
                    'title': sub_title,
                    'source_name': sub_source,
                })

        cluster_size = len(sub_articles) + 1 if sub_articles else 1

        # Extract image
        img_url = None
        thumb = item.find('media:thumbnail', media_ns)
        if thumb is not None:
            img_url = thumb.get('url')
        if not img_url:
            for mc in item.findall('media:content', media_ns):
                if mc.get('type', '').startswith('image/') or mc.get('medium') == 'image':
                    img_url = mc.get('url')
                    break

        if title and link:
            items.append({
                'title': title, 'url': link, 'pub': pub,
                'source_name': source_name, 'cluster_size': cluster_size,
                'image_url': img_url,
                'sub_articles': sub_articles,  # NEW: preserve cluster
            })

    # Atom
    ns = {'atom': 'http://www.w3.org/2005/Atom'}
    for entry in root.findall('.//atom:entry', ns):
        title = (entry.findtext('atom:title', '', ns) or '').strip()
        link_el = entry.find("atom:link[@rel='alternate']", ns)
        if link_el is None:
            link_el = entry.find("atom:link", ns)
        link = link_el.get('href', '') if link_el is not None else ''
        pub = (entry.findtext('atom:published', '', ns) or entry.findtext('atom:updated', '', ns) or '').strip()
        if title and link:
            items.append({
                'title': title, 'url': link, 'pub': pub,
                'source_name': '', 'cluster_size': 1,
                'image_url': None, 'sub_articles': [],
            })

    return items

def fetch_single_feed(feed):
    name = feed.get("name", "?")
    url = feed.get("url", "")
    source_type = feed.get("source_type", "rss")
    try:
        xml_str = fetch_url(url)
        if not xml_str:
            return feed, []
        items = parse_feed_xml(xml_str)
        for item in items:
            item['feed_id'] = feed.get("id")
            item['feed_name'] = name
            item['source_type'] = source_type
        if VERBOSE and items:
            print(f"  ✓ {name}: {len(items)} items")
        return feed, items
    except Exception as e:
        if VERBOSE:
            print(f"  ⚠ {name}: {e}")
        return feed, []

# ── Google News feeds ─────────────────────────────────────────────────────────

GOOGLE_NEWS_TOPICS = {
    "Top Stories":   "",
    "World":         "CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FtVnVHZ0pWVXlnQVAB",
    "Business":      "CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVdZU0FtVnVHZ0pWVXlnQVAB",
    "Technology":    "CAAqJggKIiBDQkFTRWdvSUwyMHZNRGRqTVhZU0FtVnVHZ0pWVXlnQVAB",
    "Entertainment": "CAAqJggKIiBDQkFTRWdvSUwyMHZNREpxYW5RU0FtVnVHZ0pWVXlnQVAB",
    "Sports":        "CAAqJggKIiBDQkFTRWdvSUwyMHZNRFp1ZEdvU0FtVnVHZ0pWVXlnQVAB",
    "Science":       "CAAqJggKIiBDQkFTRWdvSUwyMHZNRFp0Y1RjU0FtVnVHZ0pWVXlnQVAB",
    "Health":        "CAAqIQgKIhtDQkFTRGdvSUwyMHZNR3QwTlRFU0FtVnVLQUFQAQ",
}

GOOGLE_NEWS_GEOS = [
    {"name": "US",    "hl": "en-US", "gl": "US", "ceid": "US:en"},
    {"name": "India", "hl": "en-IN", "gl": "IN", "ceid": "IN:en"},
]

GOOGLE_NEWS_SEARCHES = [
    'H-1B visa OR "green card" OR "EB-2" OR "EB-3" OR USCIS',
    '"Indian American" OR "Indian origin" OR "Indian diaspora"',
    '"Indian CEO" OR "Indian founder" OR "Indian startup"',
    'OCI card OR "Indian passport" OR "Indian consulate"',
    'NRI OR "non-resident Indian" OR "overseas Indian"',
    'Infosys OR TCS OR Wipro OR "HCL Tech" OR "Tech Mahindra"',
    'Bollywood OR "Indian film" OR "Indian cinema"',
    '"Indian restaurant" OR "Indian food" OR Diwali OR Holi',
    '"Indian student" abroad OR "Indian community"',
    'India cricket OR "Team India" OR IPL',
    '"work visa" policy OR "immigration reform" OR "visa processing"',
    'DACA OR "immigration court" OR "premium processing"',
    'NVIDIA OR Google layoffs OR "Silicon Valley" hiring',
    'AI regulation OR semiconductor OR "chip act"',
    '"Federal Reserve" rate OR Sensex OR Nifty OR "rupee dollar"',
    '"Dev Patel" OR "Mindy Kaling" OR "Hasan Minhaj" OR "Priyanka Chopra"',
    '"Indian food" OR "Indian recipe" OR biryani OR "dosa" OR "Indian restaurant"',
    'turmeric OR "masala" OR "Indian grocery" OR "Indian spice" OR paneer',
    '"Air India" OR "IndiGo airlines" OR "India flights" OR "India travel"',
    # Kids & education — Indian-origin youth achievements, competitions, and education
    '"Indian American" student (competition OR award OR winner OR science OR spelling)',
    '"Indian origin" (kid OR teen OR student) (wins OR award OR champion OR finalist)',
    '"South Asian" student (scholarship OR achievement OR award OR research)',
    '"Indian American" (school OR education OR youth) program',
]

def build_google_feeds():
    feeds = []
    for geo in GOOGLE_NEWS_GEOS:
        for topic_name, topic_id in GOOGLE_NEWS_TOPICS.items():
            if topic_id:
                url = f"https://news.google.com/rss/topics/{topic_id}?hl={geo['hl']}&gl={geo['gl']}&ceid={geo['ceid']}"
            else:
                url = f"https://news.google.com/rss?hl={geo['hl']}&gl={geo['gl']}&ceid={geo['ceid']}"
            feeds.append({
                "id": None,
                "name": f"GN:{topic_name}({geo['name']})",
                "url": url,
                "source_type": "google_news",
            })
    for query in GOOGLE_NEWS_SEARCHES:
        url = f"https://news.google.com/rss/search?q={urlquote(query)}&hl=en-US&gl=US&ceid=US:en"
        feeds.append({
            "id": None,
            "name": f"GN:Search({query[:30]})",
            "url": url,
            "source_type": "google_news",
        })
    return feeds

# ── Email signals ─────────────────────────────────────────────────────────────

def fetch_email_signals():
    rows = sb_get("email_signals", {
        "processed": "eq.false",
        "select": "id,subject,from_address,body_text,received_at",
        "order": "received_at.desc",
        "limit": "100",
    })
    if not rows or isinstance(rows, dict):
        return []
    signals = []
    for row in rows:
        subject = (row.get("subject") or "").strip()
        if not subject:
            continue
        signals.append({
            'title': subject[:500],
            'url': f"email://{row['id']}",
            'pub': row.get("received_at", ""),
            'source_name': row.get("from_address", ""),
            'source_type': "newsletter",
            'cluster_size': 1,
            'feed_id': None,
            'feed_name': f"Email:{row.get('from_address','')}",
            'sub_articles': [],
            'email_id': row["id"],
        })
    return signals

# ── GPT topic matching ────────────────────────────────────────────────────────

def call_gpt(messages, max_tokens=4000, retries=2):
    """Call OpenAI gpt-4o-mini via curl, using a temp file for the payload."""
    payload = json.dumps({
        "model": "gpt-4o-mini",
        "messages": messages,
        "temperature": 0.1,
        "max_tokens": max_tokens,
        "response_format": {"type": "json_object"},
    })
    # Use temp file to avoid "Argument list too long" with large payloads
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
        tmp.write(payload)
        tmp_path = tmp.name
    try:
        for attempt in range(retries + 1):
            cmd = [
                "curl", "-sS", "--max-time", "120",
                "-X", "POST", "https://api.openai.com/v1/chat/completions",
                "-H", f"Authorization: Bearer {OPENAI_KEY}",
                "-H", "Content-Type: application/json",
                "-d", f"@{tmp_path}",
            ]
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=130)
            try:
                resp = json.loads(r.stdout)
                content = resp["choices"][0]["message"]["content"]
                usage = resp.get("usage", {})
                cost = (usage.get("prompt_tokens", 0) * 0.15 + usage.get("completion_tokens", 0) * 0.6) / 1_000_000
                return json.loads(content), cost
            except Exception as e:
                if attempt < retries:
                    wait = 5 * (attempt + 1)  # 5s, 10s backoff
                    print(f"  ⚠ GPT attempt {attempt+1} failed: {e}, retrying in {wait}s...")
                    if not r.stdout:
                        print(f"    (empty response, stderr: {r.stderr[:200]})")
                    time.sleep(wait)
                    continue
                print(f"  ⚠ GPT error after {retries+1} attempts: {e}")
                if r.stdout:
                    print(f"    Response: {r.stdout[:300]}")
                else:
                    print(f"    (empty response, stderr: {r.stderr[:200]})")
                return None, 0
    finally:
        os.unlink(tmp_path)

def match_signals_to_topics(new_signals, existing_topics, chunk_size=250):
    """
    Use GPT to match new signals to existing topics or group them into new topics.
    Chunks signals to keep prompt size manageable.
    
    Returns: dict mapping signal index → topic_id (existing or new uuid)
    Also returns: list of new topic dicts to create
    """
    if not new_signals:
        return {}, [], 0

    # Limit existing topics to most recent 500 (sorted by recency in the query)
    match_topics = existing_topics[:500]

    all_signal_topic_map = {}
    all_new_topics = []
    total_cost = 0

    # Process in chunks
    for chunk_start in range(0, len(new_signals), chunk_size):
        chunk = new_signals[chunk_start:chunk_start + chunk_size]

        # Build prompt — cap topics at 500 to keep prompt manageable
        prompt_topics = match_topics[-500:] if len(match_topics) > 500 else match_topics
        topic_lines = []
        topic_id_map = {}
        for i, t in enumerate(prompt_topics):
            topic_lines.append(f"{i+1}. {t['canonical_title'][:120]}")
            topic_id_map[i+1] = t['id']

        signal_lines = []
        for i, s in enumerate(chunk):
            signal_lines.append(f"{i+1}. {s['title'][:120]}")

        system_prompt = """You are a news editor matching article headlines to story topics.

Given EXISTING TOPICS and NEW HEADLINES, for each headline either:
- Match it to an existing topic number if it covers THE SAME news event/story
- Mark it as "new" if it's a different story

For "new" headlines, group ones that cover the same story with the same group number.

Be STRICT about matching: headlines must be about the SAME specific event, not just the same general subject.
"H-1B cap reached 2027" and "H-1B fraud arrests" are DIFFERENT topics.
"Mexico earthquake 7.4" and "Massive quake hits Mexico-Guatemala border" are the SAME topic.

Output JSON:
{
  "matches": [
    {"signal": 1, "topic": 3},
    {"signal": 2, "topic": "new", "group": 1},
    {"signal": 3, "topic": "new", "group": 1},
    {"signal": 4, "topic": "new", "group": 2}
  ]
}"""

        existing_section = "\n".join(topic_lines) if topic_lines else "(none)"
        user_prompt = f"EXISTING TOPICS:\n{existing_section}\n\nNEW HEADLINES:\n" + "\n".join(signal_lines)

        result, cost = call_gpt([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ], max_tokens=16000)
        total_cost += cost

        if not result or "matches" not in result:
            print(f"  ⚠ GPT matching failed for chunk {chunk_start}-{chunk_start+len(chunk)}, creating individual topics")
            for i, s in enumerate(chunk):
                tid = str(uuid.uuid4())
                global_idx = chunk_start + i
                all_signal_topic_map[global_idx] = tid
                all_new_topics.append({
                    "id": tid,
                    "canonical_title": s["title"][:500],
                    "signal_count": 0,
                })
            continue

        # Process GPT results
        new_topic_groups = {}

        for m in result["matches"]:
            sig_idx = m.get("signal", 0) - 1  # 1-indexed → 0-indexed
            if sig_idx < 0 or sig_idx >= len(chunk):
                continue

            global_idx = chunk_start + sig_idx
            topic_ref = m.get("topic")

            if isinstance(topic_ref, int) and topic_ref in topic_id_map:
                all_signal_topic_map[global_idx] = topic_id_map[topic_ref]
            elif topic_ref == "new":
                group = m.get("group", sig_idx)
                if group not in new_topic_groups:
                    tid = str(uuid.uuid4())
                    new_topic_groups[group] = tid
                    new_topic = {
                        "id": tid,
                        "canonical_title": chunk[sig_idx]["title"][:500],
                        "signal_count": 0,
                    }
                    all_new_topics.append(new_topic)
                    # Add to match_topics so future chunks can match against it
                    match_topics.append(new_topic)
                    topic_id_map[len(match_topics)] = tid
                all_signal_topic_map[global_idx] = new_topic_groups[group]
            else:
                tid = str(uuid.uuid4())
                all_signal_topic_map[global_idx] = tid
                new_topic = {
                    "id": tid,
                    "canonical_title": chunk[sig_idx]["title"][:500],
                    "signal_count": 0,
                }
                all_new_topics.append(new_topic)
                match_topics.append(new_topic)
                topic_id_map[len(match_topics)] = tid

        # Handle signals not in GPT output
        for i in range(len(chunk)):
            global_idx = chunk_start + i
            if global_idx not in all_signal_topic_map:
                tid = str(uuid.uuid4())
                all_signal_topic_map[global_idx] = tid
                new_topic = {
                    "id": tid,
                    "canonical_title": chunk[i]["title"][:500],
                    "signal_count": 0,
                }
                all_new_topics.append(new_topic)
                match_topics.append(new_topic)

        print(f"  Chunk {chunk_start+1}-{chunk_start+len(chunk)}: matched ({len(chunk)} signals, ${cost:.4f})")

    return all_signal_topic_map, all_new_topics, total_cost

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    t0 = time.time()
    print(f"\n{'='*60}")
    print(f"Pipeline V3 Ingest — {NOW.strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"  Mode: {'DRY RUN' if DRY_RUN else 'LIVE'}")
    print(f"{'='*60}")

    # ── Step 1: Load existing URL hashes for dedup ────────────────────────────
    print(f"\n── Step 1: Loading existing hashes ({HASH_WINDOW}d window) ──")
    existing_hashes = set()
    cutoff = (NOW - timedelta(days=HASH_WINDOW)).isoformat()
    offset = 0
    while True:
        rows = sb_get("p2_signals", {
            "select": "url_hash",
            "fetched_at": f"gte.{cutoff}",
        }, range_header=f"{offset}-{offset+999}")
        if not rows or isinstance(rows, dict):
            break
        for row in rows:
            existing_hashes.add(row.get("url_hash", ""))
        if len(rows) < 1000:
            break
        offset += 1000
    print(f"  Loaded {len(existing_hashes)} recent hashes")

    # ── Step 2: Fetch all feeds ───────────────────────────────────────────────
    print(f"\n── Step 2: Fetching feeds ──")
    all_feeds = []

    if not GOOGLE_ONLY:
        rss_feeds = sb_get("p2_feed_sources", {
            "select": "id,name,url",
            "is_active": "eq.true",
            "limit": "200",
        })
        if isinstance(rss_feeds, list):
            for f in rss_feeds:
                f["source_type"] = "rss"
            all_feeds.extend(rss_feeds)
            print(f"  RSS feeds: {len(rss_feeds)}")

    if not RSS_ONLY:
        gn_feeds = build_google_feeds()
        all_feeds.extend(gn_feeds)
        print(f"  Google News feeds: {len(gn_feeds)}")

    all_items = []
    feed_stats = {"success": 0, "empty": 0}
    print(f"  Fetching {len(all_feeds)} feeds ({MAX_WORKERS} workers)...")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(fetch_single_feed, f): f for f in all_feeds}
        for future in as_completed(futures):
            feed, items = future.result()
            if items:
                all_items.extend(items)
                feed_stats["success"] += 1
            else:
                feed_stats["empty"] += 1

    # Email signals
    if not GOOGLE_ONLY and not RSS_ONLY:
        email_items = fetch_email_signals()
        if email_items:
            all_items.extend(email_items)
            print(f"  Email signals: {len(email_items)}")

    print(f"  Feeds OK: {feed_stats['success']}, empty/error: {feed_stats['empty']}")
    print(f"  Total raw items: {len(all_items)}")

    # ── Step 3: Dedup — only keep new signals ─────────────────────────────────
    print(f"\n── Step 3: Dedup ──")
    seen = {}
    new_items = []
    for item in all_items:
        h = url_hash(item["url"])
        # Also hash sub-articles
        sub_hashes = []
        for sub in item.get("sub_articles", []):
            sh = url_hash(sub["url"])
            sub["_hash"] = sh
            sub_hashes.append(sh)

        if h not in seen and h not in existing_hashes:
            seen[h] = True
            item["_hash"] = h
            new_items.append(item)
        # Even if lead is a dupe, sub-articles might be new — we'll handle in clustering

    print(f"  New signals: {len(new_items)} (skipped {len(all_items) - len(new_items)} dupes)")

    if not new_items:
        elapsed = time.time() - t0
        print(f"\n✅ No new signals. Done in {elapsed:.1f}s")
        return

    # ── Step 4: Separate Google News clusters from standalone signals ─────────
    print(f"\n── Step 4: Separating clusters ──")
    google_clusters = []  # items with sub_articles (Google News clusters)
    standalone_signals = []  # RSS/email items without sub_articles

    # Reject signals with published_at older than 30 days (Google News
    # sometimes resurfaces years-old articles in search results)
    STALE_SIGNAL_DAYS = 30
    stale_cutoff = (NOW - timedelta(days=STALE_SIGNAL_DAYS)).isoformat()
    stale_skipped = 0

    for item in new_items:
        pub = item.get("pub") or ""
        parsed_pub = parse_pub_date(pub)
        if parsed_pub and parsed_pub < stale_cutoff:
            stale_skipped += 1
            continue
        if item.get("sub_articles") and item.get("source_type") == "google_news":
            google_clusters.append(item)
        else:
            standalone_signals.append(item)

    if stale_skipped:
        print(f"  ⚠ Skipped {stale_skipped} stale signals (published >{STALE_SIGNAL_DAYS}d ago)")

    print(f"  Google News clusters: {len(google_clusters)}")
    print(f"  Standalone signals (RSS/email): {len(standalone_signals)}")

    # ── Step 5: Load existing topics for matching ─────────────────────────────
    print(f"\n── Step 5: Loading recent topics for matching ──")
    topic_cutoff = (NOW - timedelta(hours=TOPIC_WINDOW)).isoformat()
    existing_topics = []
    offset = 0
    while True:
        # Only load V3-created topics (have last_signal_at set) to avoid 108K old junk
        # Include rejected/published so GPT can match incoming signals to
        # stories we already have — prevents the same story spawning dozens
        # of orphan topics (e.g. Kunal Shah/WhatsApp: 65 duplicate topics in 2 days)
        page = sb_get("p2_topics", {
            "select": "id,canonical_title,signal_count,status",
            "created_at": f"gte.{topic_cutoff}",
            "last_signal_at": "not.is.null",
            "order": "created_at.desc",
            "limit": "1000",
        }, range_header=f"{offset}-{offset+999}")
        if not page or isinstance(page, dict):
            break
        existing_topics.extend(page)
        if len(page) < 1000:
            break
        offset += 1000
    print(f"  Loaded {len(existing_topics)} recent topics ({TOPIC_WINDOW}h window)")

    # ── Step 6: Process Google News clusters ──────────────────────────────────
    #    Each cluster becomes/merges-into a topic. Sub-articles become signals.
    print(f"\n── Step 6: Processing Google News clusters ──")
    total_gpt_cost = 0
    total_topics_written = 0
    total_signals_written = 0

    # First, use GPT to match Google cluster lead articles to existing topics
    if google_clusters:
        gn_match_map, gn_new_topics, cost = match_signals_to_topics(google_clusters, existing_topics)
        total_gpt_cost += cost

        # Add new topics to existing_topics so standalone signals can match against them
        for nt in gn_new_topics:
            existing_topics.append(nt)

        print(f"  GPT matched {sum(1 for v in gn_match_map.values() if v in {t['id'] for t in existing_topics} - {t['id'] for t in gn_new_topics})} to existing topics")
        print(f"  Created {len(gn_new_topics)} new topics from Google clusters")

        # Build signals from clusters
        gn_signals = []
        gn_topic_counts = {}
        for i, cluster in enumerate(google_clusters):
            topic_id = gn_match_map.get(i)
            if not topic_id:
                continue

            # Lead article signal
            gn_signals.append({
                "title": cluster["title"][:500],
                "original_url": cluster["url"][:2000],
                "url_hash": cluster["_hash"],
                "published_at": parse_pub_date(cluster.get("pub")),
                "fetched_at": NOW_ISO,
                "is_processed": True,
                "source_type": "google_news",
                "source_name": cluster.get("source_name", "")[:200] or None,
                "google_cluster_size": min(cluster.get("cluster_size", 1), 32767),
                "topic_id": topic_id,
                "feed_source_id": cluster.get("feed_id"),
                "image_url": (cluster.get("image_url") or "")[:2000] or None,
            })
            gn_topic_counts[topic_id] = gn_topic_counts.get(topic_id, 0) + 1

            # Sub-article signals (same topic_id)
            for sub in cluster.get("sub_articles", []):
                sh = sub.get("_hash", url_hash(sub["url"]))
                if sh in existing_hashes or sh in seen:
                    continue
                seen[sh] = True
                gn_signals.append({
                    "title": sub["title"][:500],
                    "original_url": sub["url"][:2000],
                    "url_hash": sh,
                    "published_at": parse_pub_date(cluster.get("pub")),
                    "fetched_at": NOW_ISO,
                    "is_processed": True,
                    "source_type": "google_news",
                    "source_name": sub.get("source_name", "")[:200] or None,
                    "google_cluster_size": 1,
                    "topic_id": topic_id,
                })
                gn_topic_counts[topic_id] = gn_topic_counts.get(topic_id, 0) + 1

        # 💾 Flush Google cluster data to DB immediately
        tw, sw = flush_to_db(gn_new_topics, gn_signals, gn_topic_counts, "google clusters")
        total_topics_written += tw
        total_signals_written += sw

    # ── Step 7: Process standalone signals (RSS/email) ────────────────────────
    print(f"\n── Step 7: Processing standalone signals ──")
    if standalone_signals:
        ss_match_map, ss_new_topics, cost = match_signals_to_topics(standalone_signals, existing_topics)
        total_gpt_cost += cost

        matched_existing = sum(1 for i, v in ss_match_map.items()
                              if v not in {t['id'] for t in ss_new_topics})
        print(f"  GPT matched {matched_existing} to existing topics")
        print(f"  Created {len(ss_new_topics)} new topics from RSS/email")

        ss_signals = []
        ss_topic_counts = {}
        for i, sig in enumerate(standalone_signals):
            topic_id = ss_match_map.get(i)
            if not topic_id:
                continue

            ss_signals.append({
                "title": sig["title"][:500],
                "original_url": sig["url"][:2000],
                "url_hash": sig["_hash"],
                "published_at": parse_pub_date(sig.get("pub")),
                "fetched_at": NOW_ISO,
                "is_processed": True,
                "source_type": sig.get("source_type", "rss"),
                "source_name": sig.get("source_name", "")[:200] or None,
                "google_cluster_size": 1,
                "topic_id": topic_id,
                "feed_source_id": sig.get("feed_id"),
            })
            ss_topic_counts[topic_id] = ss_topic_counts.get(topic_id, 0) + 1

        # 💾 Flush standalone signal data to DB immediately
        tw, sw = flush_to_db(ss_new_topics, ss_signals, ss_topic_counts, "RSS/email")
        total_topics_written += tw
        total_signals_written += sw

    print(f"\n  Total GPT cost: ${total_gpt_cost:.4f}")

    # ── Summary ───────────────────────────────────────────────────────────────
    elapsed = time.time() - t0
    print(f"\n{'='*60}")
    print(f"V3 INGEST COMPLETE")
    print(f"  Topics written: {total_topics_written}")
    print(f"  Signals written: {total_signals_written}")
    print(f"  GPT cost: ${total_gpt_cost:.4f}")
    print(f"  Time: {elapsed:.1f}s")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
