#!/usr/bin/env python3
"""
Pipeline V2 Ingest — Unified signal ingestion for The Videshi.

Sources: RSS feeds (from p2_feed_sources) + Google News (topic + search) + email_signals.
Fast: parallel feed fetching, 14-day hash window, URL normalization dedup.
Outputs: signals → p2_signals, clusters → p2_topics.

Usage:
  python3 v2-ingest.py                  # full run
  python3 v2-ingest.py --dry-run        # no DB writes
  python3 v2-ingest.py --rss-only       # skip Google News
  python3 v2-ingest.py --google-only    # skip RSS
"""

import os, sys, json, hashlib, re, time, html
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from urllib.parse import quote as urlquote, urlparse, parse_qs, urlencode
from concurrent.futures import ThreadPoolExecutor, as_completed
from email.utils import parsedate_to_datetime
import subprocess

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

ENV = load_env("~/workspace/.env.supabase")
SB_URL = ENV.get("SUPABASE_URL", "")
SB_KEY = ENV.get("SUPABASE_SERVICE_ROLE_KEY", "")

def sb_get(endpoint, params=None, range_header=None):
    """GET from Supabase REST API via curl."""
    url = f"{SB_URL}/rest/v1/{endpoint}"
    if params:
        # URL-encode values (critical: '+' in timestamps becomes space otherwise)
        qs = "&".join(f"{k}={urlquote(str(v), safe='.,')}" for k, v in params.items())
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
    """POST to Supabase REST API via curl."""
    url = f"{SB_URL}/rest/v1/{endpoint}"
    prefer = "return=minimal"
    headers = [
        "-H", f"apikey: {SB_KEY}",
        "-H", f"Authorization: Bearer {SB_KEY}",
        "-H", "Content-Type: application/json",
    ]
    if upsert:
        prefer += ", resolution=merge-duplicates"
        headers += ["-H", "on-conflict: url_hash"]
    cmd = ["curl", "-sS", "--max-time", "20", "-X", "POST", url,
           *headers,
           "-H", f"Prefer: {prefer}",
           "-d", json.dumps(data)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=25)
    if r.returncode != 0 or (r.stdout.strip() and '"code"' in r.stdout):
        return False
    return True

def sb_post_returning(endpoint, data):
    """POST to Supabase REST API, return the created object."""
    url = f"{SB_URL}/rest/v1/{endpoint}"
    cmd = ["curl", "-sS", "--max-time", "15", "-X", "POST", url,
           "-H", f"apikey: {SB_KEY}",
           "-H", f"Authorization: Bearer {SB_KEY}",
           "-H", "Content-Type: application/json",
           "-H", "Prefer: return=representation",
           "-d", json.dumps(data)]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
    try:
        result = json.loads(r.stdout)
        if isinstance(result, list) and result:
            return result[0]
        return result
    except:
        return None

def sb_patch(endpoint, filter_params, data):
    """PATCH Supabase REST API."""
    url = f"{SB_URL}/rest/v1/{endpoint}"
    if filter_params:
        qs = "&".join(f"{k}={urlquote(str(v), safe='.,()_')}" for k, v in filter_params.items())
        url = f"{url}?{qs}"
    cmd = ["curl", "-sS", "--max-time", "15", "-X", "PATCH", url,
           "-H", f"apikey: {SB_KEY}",
           "-H", f"Authorization: Bearer {SB_KEY}",
           "-H", "Content-Type: application/json",
           "-H", "Prefer: return=minimal",
           "-d", json.dumps(data)]
    subprocess.run(cmd, capture_output=True, text=True, timeout=20)

# ── URL normalization ─────────────────────────────────────────────────────────

TRACKING_PARAMS = {
    'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
    'fbclid', 'gclid', 'ref', 'source', 'ncid', 'ocid', 'dicbo', 'ito',
    'ns_mchannel', 'ns_source', 'ns_campaign', 'ns_linkname', 'ns_fee',
}

def normalize_url(url):
    """Normalize URL: strip tracking params, trailing slashes, fragments."""
    try:
        parsed = urlparse(url)
        # Strip fragments
        # Strip tracking query params
        if parsed.query:
            params = parse_qs(parsed.query, keep_blank_values=True)
            clean = {k: v for k, v in params.items() if k.lower() not in TRACKING_PARAMS}
            query = urlencode(clean, doseq=True)
        else:
            query = ""
        # Reconstruct
        path = parsed.path.rstrip('/')
        netloc = parsed.netloc.lower()
        # Strip www. prefix
        if netloc.startswith('www.'):
            netloc = netloc[4:]
        return f"{parsed.scheme}://{netloc}{path}{'?' + query if query else ''}"
    except:
        return url

def url_hash(url):
    """Hash a normalized URL for dedup."""
    normalized = normalize_url(url)
    return hashlib.md5(normalized.encode()).hexdigest()

# ── Feed fetching ─────────────────────────────────────────────────────────────

def fetch_url(url, timeout=FEED_TIMEOUT):
    """Fetch a URL via curl, return text or empty string."""
    cmd = ["curl", "-sS", "--max-time", str(timeout),
           "-A", "Mozilla/5.0 (compatible; TheVideshi/1.0; +https://thevideshi.com)",
           url]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout+5)
        return r.stdout if r.returncode == 0 else ""
    except:
        return ""

def parse_rss(xml_str):
    """Parse RSS/Atom XML, return list of {title, url, pub, source_name}."""
    items = []
    try:
        root = ET.fromstring(xml_str)
    except ET.ParseError:
        return items

    # RSS 2.0
    for item in root.findall('.//item'):
        title = (item.findtext('title') or '').strip()
        link = (item.findtext('link') or '').strip()
        pub = (item.findtext('pubDate') or item.findtext('dc:date') or '').strip()
        source_el = item.find('source')
        source_name = (source_el.text or '').strip() if source_el is not None else ''
        # Google News cluster size from description
        desc = html.unescape(item.findtext('description') or '')
        cluster_size = len(re.findall(r'<li>', desc)) + 1 if '<li>' in desc else 1
        if title and link:
            items.append({
                'title': title, 'url': link, 'pub': pub,
                'source_name': source_name, 'cluster_size': cluster_size
            })

    # Atom
    ns = {'atom': 'http://www.w3.org/2005/Atom'}
    for entry in root.findall('.//atom:entry', ns):
        title = (entry.findtext('atom:title', '', ns) or '').strip()
        link_el = entry.find("atom:link[@rel='alternate']", ns)
        if link_el is None:
            link_el = entry.find("atom:link", ns)
        link = (link_el.get('href', '') if link_el is not None else '').strip()
        pub = (entry.findtext('atom:published', '', ns) or entry.findtext('atom:updated', '', ns) or '').strip()
        if title and link:
            items.append({'title': title, 'url': link, 'pub': pub, 'source_name': '', 'cluster_size': 1})

    return items

def parse_rss2json(data):
    """Parse rss2json API response."""
    items = []
    for item in data.get("items", []):
        t = (item.get("title") or "").strip()
        u = (item.get("link") or "").strip()
        if t and u:
            items.append({'title': t, 'url': u, 'pub': item.get("pubDate", ""), 'source_name': '', 'cluster_size': 1})
    return items

def parse_pub_date(pub_str):
    """Parse various date formats to ISO string."""
    if not pub_str:
        return None
    try:
        return parsedate_to_datetime(pub_str).isoformat()
    except:
        pass
    # Try ISO format
    for fmt in ['%Y-%m-%dT%H:%M:%S%z', '%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%d %H:%M:%S']:
        try:
            return datetime.strptime(pub_str, fmt).replace(tzinfo=timezone.utc).isoformat()
        except:
            pass
    return None

def fetch_single_feed(feed):
    """Fetch one feed, return (feed_info, items) or (feed_info, [])."""
    name = feed.get("name", "?")
    url = feed.get("url", "")
    feed_id = feed.get("id")
    source_type = feed.get("source_type", "rss")

    try:
        if "rss2json.com" in url:
            raw = fetch_url(url)
            if not raw:
                return feed, []
            data = json.loads(raw)
            items = parse_rss2json(data)
        else:
            raw = fetch_url(url)
            if not raw:
                return feed, []
            items = parse_rss(raw)

        for item in items:
            item['feed_id'] = feed_id
            item['feed_name'] = name
            item['source_type'] = source_type
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
    'H-1B visa OR "green card" India OR "EB-2" OR "EB-3"',
    '"Indian American" OR "Indian origin" achievement',
    'NRI OR "Indian diaspora" OR "non-resident Indian"',
    '"Indian CEO" OR "Indian origin" CEO tech',
    'India US trade OR "India UK" trade deal',
    'Bollywood "US release" OR "Indian film" international',
    'USCIS OR "immigration India" policy',
    '"hate crime" Indian OR "Indian student" abroad safety',
    '"Indian startup" unicorn OR "Indian founder"',
    'India cricket OR "Indian Premier League" OR "Team India"',
    'OCI card OR "Indian passport" OR "Indian consulate"',
    'Infosys OR TCS OR Wipro OR HCL Tech',
]

def build_google_feeds():
    """Build list of feed dicts for Google News."""
    feeds = []
    # Topic feeds across geos
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
    # Search queries
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
    """Read unprocessed email_signals and convert to signal format."""
    rows = sb_get("email_signals", {"processed": "eq.false", "select": "id,subject,from_address,body_text,received_at", "order": "received_at.desc", "limit": "100"})
    if not rows or isinstance(rows, dict):
        return []

    signals = []
    for row in rows:
        subject = (row.get("subject") or "").strip()
        if not subject:
            continue
        signals.append({
            "title": subject[:500],
            "url": f"email://{row['id']}",
            "pub": row.get("received_at", ""),
            "source_name": row.get("from_address", ""),
            "source_type": "newsletter",
            "cluster_size": 1,
            "feed_id": None,
            "feed_name": f"Email:{row.get('from_address','')}",
            "email_id": row["id"],
        })
    return signals

# ── Clustering ────────────────────────────────────────────────────────────────

STOP_WORDS = {
    'the','and','for','are','was','were','has','have','had','with','from',
    'that','this','will','been','being','after','before','about','into',
    'over','amid','says','said','more','than','also','just','first','last',
    'next','here','what','when','where','which','while','under','could',
    'would','should','their','there','other','some','most','like','make',
    'only','very','well','still','does','look','need','come','news',
    'india','indian','people','world','year','years','time','back','take',
    'report','reports','new','gets','many','much','even','every','each',
}

def title_keywords(title):
    """Extract meaningful keywords from a title."""
    words = re.findall(r'[a-z]+', title.lower())
    return set(w for w in words if len(w) >= 4 and w not in STOP_WORDS)

def find_matching_cluster(sig_title, clusters):
    """Find existing cluster with >= 50% keyword overlap."""
    sig_kw = title_keywords(sig_title)
    if not sig_kw or len(sig_kw) < 2:
        return None
    best_key = None
    best_overlap = 0
    for key, sigs in clusters.items():
        cluster_kw = title_keywords(sigs[0]["title"])
        if not cluster_kw:
            continue
        overlap = len(sig_kw & cluster_kw)
        min_len = min(len(sig_kw), len(cluster_kw))
        if min_len >= 2 and overlap / min_len >= 0.5 and overlap > best_overlap:
            best_overlap = overlap
            best_key = key
    return best_key

CATEGORY_KEYWORDS = {
    "sports": ["cricket","ipl","sports","tennis","match","wicket","goal ","football","soccer","fifa","world cup","athlete"],
    "entertainment": ["bollywood","film","movie","actor","actress","box office","ott","netflix","music","album","celebrity"],
    "technology": ["tech","ai ","startup","software","google","apple","meta ","chip","nvidia","openai","microsoft","quantum"],
    "immigration": ["visa","immigration","green card","h1b","h-1b","uscis","deportation","asylum","work permit","eb-2","eb-3","opt "],
    "nri-world": ["nri","diaspora","indian-american","indian american","indian origin","overseas indian","oci ","pio "],
    "markets-finance": ["market","sensex","nifty","stock","gdp","rupee","rbi","nasdaq","dow jones","s&p 500","earnings","fed ","inflation"],
    "lifestyle": ["health","food","yoga","wellness","recipe","travel","fashion","beauty"],
}

def detect_category(title):
    """Detect article category from title keywords."""
    t = title.lower()
    for cat, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in t for kw in keywords):
            return cat
    return "news"

# ── Main pipeline ─────────────────────────────────────────────────────────────

def main():
    t0 = time.time()
    print(f"\n{'='*60}")
    print(f"Pipeline V2 Ingest — {NOW.strftime('%Y-%m-%d %H:%M UTC')}")
    if DRY_RUN: print("  [DRY RUN]")
    print(f"{'='*60}")

    # ── Step 1: Load recent hashes for dedup ──────────────────────────────────
    print(f"\n── Step 1: Loading {HASH_WINDOW}-day hash window ──")
    existing_hashes = set()
    cutoff = (NOW - timedelta(days=HASH_WINDOW)).isoformat()
    offset = 0
    PAGE = 1000  # Supabase default max per page
    while True:
        rows = sb_get("p2_signals", {
            "select": "url_hash",
            "fetched_at": f"gte.{cutoff}",
        }, range_header=f"{offset}-{offset+PAGE-1}")
        if not rows or isinstance(rows, dict):
            break
        for row in rows:
            existing_hashes.add(row.get("url_hash", ""))
        if len(rows) < PAGE:
            break
        offset += PAGE
    print(f"  Loaded {len(existing_hashes)} recent hashes ({HASH_WINDOW}d window)")

    # ── Step 2: Fetch all feeds in parallel ───────────────────────────────────
    print(f"\n── Step 2: Fetching feeds ──")
    all_feeds = []

    # RSS feeds from DB
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

    # Google News feeds
    if not RSS_ONLY:
        gn_feeds = build_google_feeds()
        all_feeds.extend(gn_feeds)
        print(f"  Google News feeds: {len(gn_feeds)}")

    # Fetch all feeds in parallel
    all_items = []
    feed_stats = {"success": 0, "empty": 0, "error": 0}

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

    # ── Step 3: Deduplicate ───────────────────────────────────────────────────
    print(f"\n── Step 3: Deduplication ──")
    seen = {}
    unique = []
    for item in all_items:
        h = url_hash(item["url"])
        if h not in seen and h not in existing_hashes:
            seen[h] = True
            item["_hash"] = h
            unique.append(item)
    print(f"  After dedup: {len(unique)} new signals (removed {len(all_items) - len(unique)} dupes)")

    if not unique:
        elapsed = time.time() - t0
        print(f"\n✅ No new signals. Done in {elapsed:.1f}s")
        return

    # ── Step 4: Insert signals ────────────────────────────────────────────────
    print(f"\n── Step 4: Inserting {len(unique)} signals ──")
    inserted = 0
    errors = 0

    if not DRY_RUN:
        # Build all rows
        all_rows = []
        for item in unique:
            row = {
                "title": item["title"][:500],
                "original_url": item["url"][:2000],
                "url_hash": item["_hash"],
                "published_at": parse_pub_date(item.get("pub")),
                "fetched_at": NOW_ISO,
                "is_processed": False,
                "source_type": item.get("source_type", "rss"),
                "source_name": item.get("source_name", "")[:200] or None,
                "google_cluster_size": min(item.get("cluster_size", 1), 32767),
            }
            if item.get("feed_id"):
                row["feed_source_id"] = item["feed_id"]
            all_rows.append(row)

        # Parallel batch insert — 5 workers, 50 rows per batch, upsert skips dupes
        BATCH_SIZE = 50
        batches = [all_rows[i:i+BATCH_SIZE] for i in range(0, len(all_rows), BATCH_SIZE)]

        def insert_batch(batch):
            ok = sb_post("p2_signals", batch, upsert=True)
            return len(batch) if ok else 0

        with ThreadPoolExecutor(max_workers=5) as pool:
            futures = [pool.submit(insert_batch, b) for b in batches]
            for f in as_completed(futures):
                try:
                    inserted += f.result()
                except:
                    errors += 1

        print(f"  Inserted/upserted: {inserted}, errors: {errors}")
    else:
        print(f"  [DRY RUN] Would insert {len(unique)} signals")

    # ── Step 5: Mark email signals as processed ────────────────────────────────
    if not DRY_RUN:
        email_ids = [item.get("email_id") for item in unique if item.get("email_id")]
        if email_ids:
            for eid in email_ids:
                sb_patch("email_signals", {"id": f"eq.{eid}"}, {"processed": True})
            print(f"\n── Step 5: Marked {len(email_ids)} email signals processed ──")

    # ── Summary ───────────────────────────────────────────────────────────────
    elapsed = time.time() - t0
    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"  Feeds scanned: {len(all_feeds)}")
    print(f"  Raw items: {len(all_items)}")
    print(f"  New signals: {len(unique)}")
    print(f"  Inserted: {inserted}")
    if errors: print(f"  Errors: {errors}")
    print(f"  Time: {elapsed:.1f}s")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
