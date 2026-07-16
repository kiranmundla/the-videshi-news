#!/usr/bin/env python3
"""
google-news-ingest.py — Fetch signals from Google News RSS feeds and insert into p2_signals.

Runs alongside existing RSS ingest. Adds source_type='google_news' signals.
Two modes:
  1. Topic feeds — pre-built categories (US + India editions), heavily clustered by Google
  2. Search queries — keyword-based, diaspora-focused, no clustering

Free, no API key. Self-rate-limited with delays between requests.
"""

import subprocess, sys, os, json, hashlib, time, re, html
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from urllib.parse import quote as urlquote

# ── Config ────────────────────────────────────────────────────────────────────

DRY_RUN = "--dry-run" in sys.argv
VERBOSE = "--verbose" in sys.argv or DRY_RUN
DELAY_BETWEEN_REQUESTS = 1  # seconds, be polite to Google

# Google News topic feed IDs (base64-encoded category IDs)
TOPIC_FEEDS = {
    "Top Stories":   "",  # empty = top stories (no topic path)
    "World":         "CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FtVnVHZ0pWVXlnQVAB",
    "Business":      "CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVdZU0FtVnVHZ0pWVXlnQVAB",
    "Technology":    "CAAqJggKIiBDQkFTRWdvSUwyMHZNRGRqTVhZU0FtVnVHZ0pWVXlnQVAB",
    "Entertainment": "CAAqJggKIiBDQkFTRWdvSUwyMHZNREpxYW5RU0FtVnVHZ0pWVXlnQVAB",
    "Sports":        "CAAqJggKIiBDQkFTRWdvSUwyMHZNRFp1ZEdvU0FtVnVHZ0pWVXlnQVAB",
    "Science":       "CAAqJggKIiBDQkFTRWdvSUwyMHZNRFp0Y1RjU0FtVnVHZ0pWVXlnQVAB",
    "Health":        "CAAqIQgKIhtDQkFTRGdvSUwyMHZNR3QwTlRFU0FtVnVLQUFQAQ",
}

# Geo editions to scan
GEO_EDITIONS = [
    {"name": "US",    "hl": "en-US", "gl": "US", "ceid": "US:en"},
    {"name": "India", "hl": "en-IN", "gl": "IN", "ceid": "IN:en"},
]

# Diaspora-focused search queries
SEARCH_QUERIES = [
    # ── Type A: Diaspora-specific (stories that mention "Indian" explicitly) ──
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

    # ── Type B: Diaspora-adjacent (affects NRIs without saying "Indian") ──
    # Immigration — policy changes that directly impact H-1B/green card holders
    '"work visa" policy OR "immigration reform" OR "visa processing"',
    'DACA OR "immigration court" OR "premium processing"',
    # Tech — companies and trends that employ/affect large Indian workforce
    'NVIDIA OR Google layoffs OR "Silicon Valley" hiring',
    'AI regulation OR semiconductor OR "chip act"',
    # Markets — US/India markets that NRIs invest in / are affected by
    '"Federal Reserve" rate OR Sensex OR Nifty OR "rupee dollar"',
    # Entertainment — crossover content NRIs care about
    '"Dev Patel" OR "Mindy Kaling" OR "Hasan Minhaj" OR "Priyanka Chopra"',
    # Food/Travel — diaspora lifestyle
    '"Trader Joes" Indian OR turmeric OR chai latte OR "spice" food trend',
    '"Air India" OR "IndiGo airlines" OR "India flights"',
]

# ── Supabase helpers ──────────────────────────────────────────────────────────

def load_env():
    env = {}
    for f in ['~/workspace/.env.supabase']:
        path = os.path.expanduser(f)
        if os.path.exists(path):
            with open(path) as fh:
                for line in fh:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        k, v = line.split('=', 1)
                        env[k.strip()] = v.strip().strip('"').strip("'")
    return env

ENV = load_env()
SUPABASE_URL = ENV.get('SUPABASE_URL', '')
SUPABASE_KEY = ENV.get('SUPABASE_SERVICE_ROLE_KEY', '')

def supabase_post(endpoint, data):
    """POST to Supabase REST API."""
    url = f"{SUPABASE_URL}/rest/v1/{endpoint}"
    payload = json.dumps(data)
    cmd = [
        "curl", "-sS", "--max-time", "15",
        "-X", "POST", url,
        "-H", f"apikey: {SUPABASE_KEY}",
        "-H", f"Authorization: Bearer {SUPABASE_KEY}",
        "-H", "Content-Type: application/json",
        "-H", "Prefer: return=minimal",
        "-d", payload,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
    if r.returncode != 0:
        print(f"  ⚠ curl error: {r.stderr[:200]}")
        return False
    if r.stdout.strip() and '"code"' in r.stdout:
        # Check for duplicate key (url_hash unique constraint)
        if '23505' in r.stdout or 'duplicate' in r.stdout.lower():
            return 'duplicate'
        print(f"  ⚠ Supabase error: {r.stdout[:200]}")
        return False
    return True

def check_existing_hashes(hashes):
    """Check which url_hashes already exist in p2_signals."""
    if not hashes:
        return set()
    # Build OR filter
    hash_filter = ",".join(f'"{h}"' for h in hashes)
    url = f"{SUPABASE_URL}/rest/v1/p2_signals?url_hash=in.({','.join(hashes)})&select=url_hash"
    cmd = [
        "curl", "-sS", "--max-time", "15", url,
        "-H", f"apikey: {SUPABASE_KEY}",
        "-H", f"Authorization: Bearer {SUPABASE_KEY}",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
    try:
        rows = json.loads(r.stdout)
        return {row['url_hash'] for row in rows}
    except:
        return set()

# ── Google News RSS fetching ──────────────────────────────────────────────────

def fetch_rss(url):
    """Fetch RSS feed via curl."""
    cmd = [
        "curl", "-sS", "--max-time", "15",
        "-A", "Mozilla/5.0 (compatible; TheVideshi/1.0; +https://thevideshi.com)",
        url
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
    if r.returncode != 0:
        print(f"  ⚠ Fetch failed: {url[:60]}...")
        return ""
    return r.stdout

def parse_rss_items(xml_str):
    """Parse RSS XML and extract items with metadata."""
    items = []
    try:
        root = ET.fromstring(xml_str)
    except ET.ParseError:
        return items

    for item in root.findall('.//item'):
        title = (item.findtext('title') or '').strip()
        link = (item.findtext('link') or '').strip()
        pub_date = (item.findtext('pubDate') or '').strip()
        source_el = item.find('source')
        source_name = (source_el.text or '').strip() if source_el is not None else ''

        # Extract cluster size from description (Google News clusters related articles in <ol>)
        desc = html.unescape(item.findtext('description') or '')
        cluster_articles = re.findall(r'<li>', desc)
        cluster_size = len(cluster_articles) + 1 if cluster_articles else 1  # +1 for the main article

        if not title or not link:
            continue

        # Parse pub_date to ISO
        published_at = None
        if pub_date:
            try:
                from email.utils import parsedate_to_datetime
                published_at = parsedate_to_datetime(pub_date).isoformat()
            except:
                pass

        # Resolve Google News redirect URL to get the actual article URL
        # Google News links are like: https://news.google.com/rss/articles/...
        # For now, use the Google News URL as-is (actual URL is behind redirect)
        actual_url = link

        items.append({
            'title': title,
            'url': actual_url,
            'published_at': published_at,
            'source_name': source_name,
            'cluster_size': cluster_size,
        })

    return items

def url_hash(url):
    """Generate consistent hash for URL dedup."""
    return hashlib.sha256(url.encode()).hexdigest()[:16]

# ── Feed fetching ─────────────────────────────────────────────────────────────

def fetch_topic_feeds():
    """Fetch all Google News topic feeds across geo editions."""
    all_items = []
    for geo in GEO_EDITIONS:
        for topic_name, topic_id in TOPIC_FEEDS.items():
            if topic_id:
                url = f"https://news.google.com/rss/topics/{topic_id}?hl={geo['hl']}&gl={geo['gl']}&ceid={geo['ceid']}"
            else:
                url = f"https://news.google.com/rss?hl={geo['hl']}&gl={geo['gl']}&ceid={geo['ceid']}"

            xml_str = fetch_rss(url)
            items = parse_rss_items(xml_str)
            for item in items:
                item['feed_type'] = 'topic'
                item['feed_name'] = f"{topic_name} ({geo['name']})"
            all_items.extend(items)

            if VERBOSE:
                print(f"  📂 {topic_name} ({geo['name']}): {len(items)} items")
            time.sleep(DELAY_BETWEEN_REQUESTS)

    return all_items

def fetch_search_feeds():
    """Fetch Google News search query feeds."""
    all_items = []
    for query in SEARCH_QUERIES:
        url = f"https://news.google.com/rss/search?q={urlquote(query)}&hl=en-US&gl=US&ceid=US:en"

        xml_str = fetch_rss(url)
        items = parse_rss_items(xml_str)
        for item in items:
            item['feed_type'] = 'search'
            item['feed_name'] = f"Search: {query[:40]}"
        all_items.extend(items)

        if VERBOSE:
            print(f"  🔍 [{query[:40]}]: {len(items)} items")
        time.sleep(DELAY_BETWEEN_REQUESTS)

    return all_items

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print(f"\n{'='*60}")
    print(f"Google News Ingest — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"{'='*60}")
    if DRY_RUN:
        print("🔸 DRY RUN — no database writes\n")

    # Phase 1: Fetch all feeds
    print("\n── Phase 1: Fetching Google News feeds ──")

    print("\nTopic feeds:")
    topic_items = fetch_topic_feeds()
    print(f"  Total topic feed items: {len(topic_items)}")

    print("\nSearch queries:")
    search_items = fetch_search_feeds()
    print(f"  Total search items: {len(search_items)}")

    all_items = topic_items + search_items
    print(f"\nTotal raw items: {len(all_items)}")

    # Phase 2: Deduplicate by URL
    print("\n── Phase 2: Deduplication ──")
    seen_hashes = {}
    unique_items = []
    for item in all_items:
        h = url_hash(item['url'])
        if h not in seen_hashes:
            seen_hashes[h] = item
            item['url_hash'] = h
            unique_items.append(item)

    print(f"  After URL dedup: {len(unique_items)} unique (removed {len(all_items) - len(unique_items)} dupes within this batch)")

    # Phase 3: Check against existing signals in DB
    print("\n── Phase 3: Checking against existing signals ──")
    batch_size = 200
    existing_hashes = set()
    all_hashes = [item['url_hash'] for item in unique_items]
    for i in range(0, len(all_hashes), batch_size):
        batch = all_hashes[i:i+batch_size]
        existing_hashes |= check_existing_hashes(batch)

    new_items = [item for item in unique_items if item['url_hash'] not in existing_hashes]
    print(f"  Already in DB: {len(existing_hashes)}")
    print(f"  New signals: {len(new_items)}")

    if not new_items:
        print("\n✅ No new signals to insert.")
        return

    # Phase 4: Insert new signals
    print(f"\n── Phase 4: Inserting {len(new_items)} new signals ──")
    inserted = 0
    skipped = 0
    errors = 0

    for item in new_items:
        row = {
            "title": item['title'][:500],
            "original_url": item['url'],
            "url_hash": item['url_hash'],
            "published_at": item.get('published_at'),
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "is_processed": False,
            "source_type": "google_news",
            "google_cluster_size": min(item.get('cluster_size', 1), 32767),
            "source_name": item.get('source_name', '')[:200],
        }

        if DRY_RUN:
            if VERBOSE and inserted < 10:
                print(f"  [DRY] [{row['source_name'][:15]:15s}] {row['title'][:70]}")
            inserted += 1
            continue

        result = supabase_post("p2_signals", row)
        if result == 'duplicate':
            skipped += 1
        elif result:
            inserted += 1
            if VERBOSE and inserted <= 5:
                print(f"  ✓ [{item.get('source_name','')[:15]:15s}] {item['title'][:60]}")
        else:
            errors += 1

    # Summary
    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"  Feeds scanned: {len(TOPIC_FEEDS) * len(GEO_EDITIONS) + len(SEARCH_QUERIES)} ({len(TOPIC_FEEDS) * len(GEO_EDITIONS)} topic + {len(SEARCH_QUERIES)} search)")
    print(f"  Raw items: {len(all_items)}")
    print(f"  After dedup: {len(unique_items)}")
    print(f"  Already in DB: {len(existing_hashes)}")
    print(f"  Inserted: {inserted}")
    if skipped: print(f"  Skipped (dup): {skipped}")
    if errors: print(f"  Errors: {errors}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
