#!/usr/bin/env python3
"""
videshi-media-curator.py — AI-powered media sourcing for The Videshi.

Uses article content to intelligently find the best media (images, embeds)
from multiple sources:
  1. Pexels API (free stock photos, with attribution)
  2. Wikimedia Commons (free, CC licensed)
  3. YouTube embeds (match highlights, speeches, demos)
  4. Twitter/X embeds (official statements, journalist posts)
  5. Instagram embeds (cultural, lifestyle, diaspora content)

The AI (this script's logic) analyzes article content to decide which
source type and search queries will yield the most relevant result.

Usage:
    python3 videshi-media-curator.py fetch              # Articles missing images
    python3 videshi-media-curator.py fetch --id <UUID>  # Specific article
    python3 videshi-media-curator.py fetch --refresh     # Re-source all
"""

import io
import json
import os
import re
import sys
import time
import urllib.parse
import requests

try:
    from PIL import Image, ImageEnhance
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

ENV_FILE = os.path.expanduser("~/workspace/.env.supabase")
PEXELS_ENV_FILE = os.path.expanduser("~/workspace/.env.pexels")
WIKIPEDIA_API = "https://en.wikipedia.org/w/api.php"
USER_AGENT = "TheVideshiBot/1.0 (https://thevideshi.com; contact@thevideshi.com)"
POLITE_DELAY = 0.5
UPLOAD_DELAY = 0.3
TARGET_WIDTH = 1200
JPEG_QUALITY = 88
PEXELS_API_URL = "https://api.pexels.com/v1/search"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_SKIP_LIST = os.path.join(SCRIPT_DIR, "image-skip-list.json")

# ---------------------------------------------------------------------------
# Category → search strategy mapping
# ---------------------------------------------------------------------------

CATEGORY_STRATEGY = {
    "sports":           {"primary": "youtube",  "fallback": "pexels",    "pexels_default": "cricket stadium India"},
    "entertainment":    {"primary": "youtube",  "fallback": "pexels",    "pexels_default": "Bollywood cinema"},
    "markets-finance":  {"primary": "pexels",   "fallback": "pexels",    "pexels_default": "stock market trading"},
    "technology":       {"primary": "pexels",   "fallback": "youtube",   "pexels_default": "technology innovation"},
    "news":             {"primary": "pexels",   "fallback": "twitter",   "pexels_default": "India news press"},
    "nri-world":        {"primary": "pexels",   "fallback": "instagram", "pexels_default": "Indian diaspora community"},
    "lifestyle-health": {"primary": "pexels",   "fallback": "instagram", "pexels_default": "Indian culture lifestyle"},
}

# Stop words for search query extraction
STOP_WORDS = {
    "the", "and", "for", "with", "from", "into", "that", "this", "will",
    "has", "have", "had", "are", "was", "were", "been", "not", "but",
    "its", "his", "her", "how", "why", "what", "who", "when", "after",
    "before", "about", "over", "under", "more", "most", "than", "new",
    "says", "said", "amid", "just", "also", "could", "would", "may",
    "can", "now", "set", "get", "back", "out", "top", "first", "last",
    "one", "two", "three", "four", "five", "year", "years", "day",
    "faces", "face", "amid", "signals", "becomes", "moves", "makes",
    "takes", "opens", "warns", "launches", "hits", "lands", "pushes",
    "seeks", "pledges", "demands", "blocks", "claims", "attacks",
}


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def _load_skip_ids():
    if not os.path.exists(IMAGE_SKIP_LIST):
        return set()
    try:
        with open(IMAGE_SKIP_LIST) as f:
            data = json.load(f)
        return set(data.get("skip_ids", []))
    except (json.JSONDecodeError, IOError):
        return set()


def load_env():
    env = {}
    if not os.path.exists(ENV_FILE):
        print(f"ERROR: {ENV_FILE} not found")
        sys.exit(1)
    with open(ENV_FILE) as f:
        for line in f:
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env


def supabase_headers(key):
    return {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
    }


def _load_pexels_key():
    key = os.environ.get("PEXELS_API_KEY")
    if key:
        return key
    if os.path.exists(PEXELS_ENV_FILE):
        with open(PEXELS_ENV_FILE) as f:
            for line in f:
                line = line.strip()
                if line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                if k.strip() == "PEXELS_API_KEY":
                    val = v.strip()
                    if val and not val.startswith("your_"):
                        return val
    return None


# ---------------------------------------------------------------------------
# Smart query extraction
# ---------------------------------------------------------------------------

def extract_search_queries(headline, category=None, body_excerpt=None):
    """
    Generate 2-3 smart search queries from article content.
    Returns a list of query strings, from most specific to most general.
    """
    queries = []

    # Clean headline
    clean = re.sub(r"[^a-zA-Z0-9\s'-]", " ", headline)
    words = clean.split()

    # Extract proper nouns and keywords
    proper_nouns = []
    keywords = []
    for w in words:
        w_lower = w.lower()
        if len(w) < 3 or w_lower in STOP_WORDS:
            continue
        if w[0].isupper() and len(w) > 2:
            proper_nouns.append(w)
        else:
            keywords.append(w)

    # Query 1: Most specific — proper nouns
    if proper_nouns:
        q1_parts = proper_nouns[:4]
        queries.append(" ".join(q1_parts))

    # Query 2: Mix of proper nouns + keywords
    q2_parts = proper_nouns[:2] + keywords[:2]
    if q2_parts and " ".join(q2_parts) not in queries:
        queries.append(" ".join(q2_parts[:4]))

    # Query 3: Category-specific fallback
    strategy = CATEGORY_STRATEGY.get(category, {})
    default_q = strategy.get("pexels_default", "India")
    if proper_nouns:
        q3 = f"{proper_nouns[0]} {default_q}"
    else:
        q3 = default_q
    if q3 not in queries:
        queries.append(q3)

    return queries[:3]


def extract_youtube_queries(headline, category=None):
    """Generate YouTube-optimized search queries."""
    queries = []
    clean = re.sub(r"[^a-zA-Z0-9\s'-]", " ", headline)
    words = clean.split()
    proper_nouns = [w for w in words if w[0].isupper() and len(w) > 2 and w.lower() not in STOP_WORDS]
    keywords = [w for w in words if w[0].islower() and len(w) > 3 and w.lower() not in STOP_WORDS]

    # For sports — look for match highlights
    if category == "sports":
        teams_players = " ".join(proper_nouns[:3])
        if teams_players:
            queries.append(f"{teams_players} highlights")
            queries.append(f"{teams_players} IPL 2026")

    # For entertainment — trailers, music, interviews
    elif category == "entertainment":
        names = " ".join(proper_nouns[:3])
        if names:
            queries.append(f"{names} official")
            queries.append(f"{names} trailer")

    # For tech — product demos, announcements
    elif category == "technology":
        entity = " ".join(proper_nouns[:3])
        if entity:
            queries.append(f"{entity} demo")
            queries.append(f"{entity} announcement")

    # General fallback
    if not queries:
        q = " ".join(proper_nouns[:3] + keywords[:2])
        if q.strip():
            queries.append(q)

    return queries[:2]


def extract_twitter_queries(headline, category=None):
    """Generate Twitter search queries to find relevant tweets."""
    clean = re.sub(r"[^a-zA-Z0-9\s'-]", " ", headline)
    words = clean.split()
    proper_nouns = [w for w in words if w[0].isupper() and len(w) > 2 and w.lower() not in STOP_WORDS]
    entity = " ".join(proper_nouns[:3])
    if entity:
        return [f"site:twitter.com OR site:x.com {entity}"]
    return []


def extract_instagram_queries(headline, category=None):
    """Generate Instagram search queries."""
    clean = re.sub(r"[^a-zA-Z0-9\s'-]", " ", headline)
    words = clean.split()
    proper_nouns = [w for w in words if w[0].isupper() and len(w) > 2 and w.lower() not in STOP_WORDS]
    entity = " ".join(proper_nouns[:3])
    if entity:
        return [f"site:instagram.com {entity}"]
    return []


# ---------------------------------------------------------------------------
# Pexels search (improved with multi-query)
# ---------------------------------------------------------------------------

# Patterns for bad Pexels images
BAD_ALT_RE = re.compile(
    r"\b(satellite|aerial|map|terrain|topograph|bird.?s?.?eye|overhead|"
    r"atlas|cartograph|globe|continent|region|province|state.?of|"
    r"district|geography|landscape.?view)\b",
    re.IGNORECASE,
)


def search_pexels(queries, headline=""):
    """
    Search Pexels with multiple queries, return best (url, attribution).
    Tries each query in order, picks best from combined results.
    """
    api_key = _load_pexels_key()
    if not api_key:
        print("    ⚠ No Pexels API key")
        return None, None

    all_photos = []
    seen_ids = set()

    for query in queries:
        print(f"    🔍 Pexels: \"{query}\"")
        try:
            resp = requests.get(
                PEXELS_API_URL,
                headers={"Authorization": api_key},
                params={"query": query, "per_page": 8, "orientation": "landscape"},
                timeout=15,
            )
            if resp.status_code in (401, 429):
                print(f"    ⚠ Pexels: status {resp.status_code}")
                continue
            resp.raise_for_status()
            photos = resp.json().get("photos", [])
            for p in photos:
                if p["id"] not in seen_ids:
                    seen_ids.add(p["id"])
                    all_photos.append(p)
        except requests.RequestException as e:
            print(f"    ⚠ Pexels error: {e}")
        time.sleep(POLITE_DELAY)

    if not all_photos:
        print("    ⚠ Pexels: no results across all queries")
        return None, None

    # Score and pick best
    headline_lower = headline.lower()
    headline_words = set(re.findall(r'[a-z]{3,}', headline_lower))
    best = None
    best_score = -1

    for photo in all_photos:
        alt = (photo.get("alt") or "").lower()
        # Skip bad patterns
        if BAD_ALT_RE.search(alt):
            continue

        score = 0
        # Size bonus
        w = photo.get("width", 0)
        h = photo.get("height", 0)
        if w >= 1200:
            score += 2
        elif w >= 800:
            score += 1
        # Landscape bonus
        if w > h:
            score += 1

        # Relevance: count matching words between alt and headline
        alt_words = set(re.findall(r'[a-z]{3,}', alt))
        overlap = headline_words & alt_words - STOP_WORDS
        score += len(overlap) * 2

        if score > best_score:
            best_score = score
            best = photo

    if not best:
        print("    ⚠ Pexels: all results filtered out")
        return None, None

    img_url = best.get("src", {}).get("large2x") or best.get("src", {}).get("large")
    photographer = best.get("photographer", "Unknown")
    attribution = f"Photo by {photographer} / Pexels"
    print(f"    ✅ Pexels: found ({best.get('width')}x{best.get('height')}) by {photographer}")
    return img_url, attribution


# ---------------------------------------------------------------------------
# YouTube search (via web scraping of YouTube search results)
# ---------------------------------------------------------------------------

def search_youtube(queries, headline=""):
    """
    Find a relevant YouTube video by scraping search results.
    Returns (embed_url, attribution) or (None, None).
    """
    for query in queries:
        print(f"    🔍 YouTube: \"{query}\"")
        try:
            search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote_plus(query)}"
            resp = requests.get(
                search_url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Accept-Language": "en-US,en;q=0.9",
                },
                timeout=15,
            )
            resp.raise_for_status()
            html = resp.text

            # Extract video IDs from the page (they appear in the JSON data)
            video_ids = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', html)
            # Dedupe while preserving order
            seen = set()
            unique_ids = []
            for vid in video_ids:
                if vid not in seen:
                    seen.add(vid)
                    unique_ids.append(vid)

            if not unique_ids:
                continue

            # Try to extract title for the first few results
            for video_id in unique_ids[:3]:
                # Extract the title from the JSON blob
                title_match = re.search(
                    rf'"videoId":"{video_id}".*?"title":\s*\{{"runs":\s*\[\{{"text":"([^"]+)"',
                    html,
                )
                title = title_match.group(1) if title_match else ""

                # Extract channel name
                channel_match = re.search(
                    rf'"videoId":"{video_id}".*?"ownerText":\s*\{{"runs":\s*\[\{{"text":"([^"]+)"',
                    html,
                )
                channel = channel_match.group(1) if channel_match else "YouTube"

                # Basic relevance: check if headline words appear in title
                if title:
                    title_lower = title.lower()
                    headline_words = set(re.findall(r'[a-z]{4,}', headline.lower()))
                    title_words = set(re.findall(r'[a-z]{4,}', title_lower))
                    overlap = headline_words & title_words - STOP_WORDS
                    if len(overlap) >= 1:
                        embed_url = f"https://www.youtube.com/watch?v={video_id}"
                        attribution = f"embed:youtube | {channel}"
                        print(f"    ✅ YouTube: \"{title[:60]}\" by {channel}")
                        return embed_url, attribution

                # If we can't verify relevance from title, accept first result for sports/entertainment
                if not title and video_id == unique_ids[0]:
                    embed_url = f"https://www.youtube.com/watch?v={video_id}"
                    attribution = f"embed:youtube | {channel}"
                    print(f"    ✅ YouTube: video {video_id} by {channel}")
                    return embed_url, attribution

        except requests.RequestException as e:
            print(f"    ⚠ YouTube search error: {e}")
        time.sleep(POLITE_DELAY)

    print("    ⚠ YouTube: no relevant results")
    return None, None


# ---------------------------------------------------------------------------
# Twitter/X search (via web search for tweet URLs)
# ---------------------------------------------------------------------------

def search_twitter(queries, headline=""):
    """
    Find a relevant tweet by searching for tweet URLs.
    Returns (tweet_url, attribution) or (None, None).
    """
    for query in queries:
        print(f"    🔍 Twitter/X: \"{query}\"")
        try:
            # Search for tweets via DuckDuckGo HTML (no API key needed)
            search_url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote_plus(query)}"
            resp = requests.get(
                search_url,
                headers={"User-Agent": USER_AGENT},
                timeout=15,
            )
            resp.raise_for_status()
            html = resp.text

            # Find tweet URLs in results
            tweet_urls = re.findall(
                r'https?://(?:twitter\.com|x\.com)/([a-zA-Z0-9_]+)/status/(\d+)',
                html,
            )

            if tweet_urls:
                handle, status_id = tweet_urls[0]
                tweet_url = f"https://x.com/{handle}/status/{status_id}"
                attribution = f"embed:twitter | @{handle}"
                print(f"    ✅ Twitter: @{handle}/status/{status_id}")
                return tweet_url, attribution

        except requests.RequestException as e:
            print(f"    ⚠ Twitter search error: {e}")
        time.sleep(POLITE_DELAY)

    print("    ⚠ Twitter: no relevant results")
    return None, None


# ---------------------------------------------------------------------------
# Instagram search (via web search for post URLs)
# ---------------------------------------------------------------------------

def search_instagram(queries, headline=""):
    """
    Find a relevant Instagram post by searching for post URLs.
    Returns (post_url, attribution) or (None, None).
    """
    for query in queries:
        print(f"    🔍 Instagram: \"{query}\"")
        try:
            search_url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote_plus(query)}"
            resp = requests.get(
                search_url,
                headers={"User-Agent": USER_AGENT},
                timeout=15,
            )
            resp.raise_for_status()
            html = resp.text

            # Find Instagram post URLs in results
            ig_urls = re.findall(
                r'https?://(?:www\.)?instagram\.com/(?:p|reel)/([a-zA-Z0-9_-]+)',
                html,
            )

            if ig_urls:
                shortcode = ig_urls[0]
                post_url = f"https://www.instagram.com/p/{shortcode}/"
                # Try to extract handle from page context
                handle_match = re.search(
                    rf'{shortcode}.*?instagram\.com/([a-zA-Z0-9_.]+)',
                    html,
                )
                handle = handle_match.group(1) if handle_match else "instagram"
                attribution = f"embed:instagram | @{handle}"
                print(f"    ✅ Instagram: post {shortcode} by @{handle}")
                return post_url, attribution

        except requests.RequestException as e:
            print(f"    ⚠ Instagram search error: {e}")
        time.sleep(POLITE_DELAY)

    print("    ⚠ Instagram: no relevant results")
    return None, None


# ---------------------------------------------------------------------------
# Image processing (reused from videshi-images.py)
# ---------------------------------------------------------------------------

def download_image(image_url):
    """Download an image and return PIL Image object."""
    if not HAS_PIL:
        return None
    try:
        resp = requests.get(
            image_url,
            headers={"User-Agent": USER_AGENT},
            timeout=30,
            stream=True,
        )
        resp.raise_for_status()
        content = b""
        for chunk in resp.iter_content(chunk_size=65536):
            content += chunk
            if len(content) > 20 * 1024 * 1024:
                print("    ⚠ Image too large (>20MB)")
                return None
        return Image.open(io.BytesIO(content))
    except Exception as e:
        print(f"    ⚠ Download failed: {e}")
        return None


def process_image(image_url):
    """Download, resize, enhance, return JPEG bytes."""
    img = download_image(image_url)
    if img is None:
        return None, 0
    try:
        if img.mode != "RGB":
            img = img.convert("RGB")
        if img.width < 200 or img.height < 100:
            print(f"    ⚠ Too small ({img.width}x{img.height})")
            return None, 0
        if img.width > TARGET_WIDTH:
            ratio = TARGET_WIDTH / img.width
            img = img.resize((TARGET_WIDTH, int(img.height * ratio)), Image.LANCZOS)
        elif img.width < 800:
            ratio = 800 / img.width
            img = img.resize((800, int(img.height * ratio)), Image.LANCZOS)
        # Subtle enhancement
        img = ImageEnhance.Sharpness(img).enhance(1.15)
        img = ImageEnhance.Contrast(img).enhance(1.05)
        img = ImageEnhance.Color(img).enhance(1.05)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=JPEG_QUALITY, optimize=True)
        jpeg_bytes = buf.getvalue()
        return jpeg_bytes, len(jpeg_bytes) / 1024
    except Exception as e:
        print(f"    ⚠ Processing failed: {e}")
        return None, 0


def upload_to_supabase(env, article_id, jpeg_bytes):
    """Upload JPEG to Supabase Storage, return public URL."""
    url = env["SUPABASE_URL"]
    key = env["SUPABASE_SERVICE_ROLE_KEY"]
    filename = f"{article_id}.jpg"
    try:
        resp = requests.post(
            f"{url}/storage/v1/object/article-images/{filename}",
            headers={
                "apikey": key,
                "Authorization": f"Bearer {key}",
                "Content-Type": "image/jpeg",
                "x-upsert": "true",
            },
            data=jpeg_bytes,
            timeout=30,
        )
        resp.raise_for_status()
        public_url = f"{url}/storage/v1/object/public/article-images/{filename}"
        return public_url
    except Exception as e:
        print(f"    ⚠ Upload failed: {e}")
        return None


def process_and_upload(env, article_id, source_url):
    """Full pipeline: download → resize → enhance → upload. Returns (url, size_kb)."""
    jpeg_bytes, size_kb = process_image(source_url)
    if jpeg_bytes is None:
        return None, 0
    img = Image.open(io.BytesIO(jpeg_bytes))
    public_url = upload_to_supabase(env, article_id, jpeg_bytes)
    if public_url:
        public_url = f"{public_url}?w={img.width}&h={img.height}"
    time.sleep(UPLOAD_DELAY)
    return public_url, size_kb


# ---------------------------------------------------------------------------
# Main orchestrator — decides strategy per article
# ---------------------------------------------------------------------------

def find_media_for_article(article):
    """
    AI-powered media sourcing: analyze article content to decide the best
    source type and search queries.

    Returns (url, attribution) where:
    - For images: url is the source image URL, attribution is "Photo by X / Pexels"
    - For embeds: url is the embed URL, attribution is "embed:type | @handle"
    """
    headline = article.get("headline", "")
    category = article.get("category") or article.get("vertical") or ""
    body = article.get("body", "")[:500]  # Use first 500 chars for context

    strategy = CATEGORY_STRATEGY.get(category, CATEGORY_STRATEGY.get("news", {}))
    primary = strategy.get("primary", "pexels")
    fallback = strategy.get("fallback", "pexels")

    print(f"  📋 Strategy: primary={primary}, fallback={fallback} (category={category})")

    # Generate queries
    pexels_queries = extract_search_queries(headline, category, body)
    youtube_queries = extract_youtube_queries(headline, category)
    twitter_queries = extract_twitter_queries(headline, category)
    instagram_queries = extract_instagram_queries(headline, category)

    # Try primary source
    url, attr = _try_source(primary, headline, category, pexels_queries, youtube_queries, twitter_queries, instagram_queries)
    if url:
        return url, attr

    # Try fallback source
    if fallback != primary:
        url, attr = _try_source(fallback, headline, category, pexels_queries, youtube_queries, twitter_queries, instagram_queries)
        if url:
            return url, attr

    # Last resort: try pexels if we haven't already
    if primary != "pexels" and fallback != "pexels":
        print("  📷 Last resort: Pexels")
        url, attr = search_pexels(pexels_queries, headline)
        if url:
            return url, attr

    print(f"  ❌ No suitable media found")
    return None, None


def _try_source(source_type, headline, category, pexels_q, youtube_q, twitter_q, instagram_q):
    """Try a specific source type."""
    if source_type == "pexels":
        print(f"  📷 Trying: Pexels")
        return search_pexels(pexels_q, headline)
    elif source_type == "youtube":
        print(f"  🎥 Trying: YouTube")
        return search_youtube(youtube_q, headline)
    elif source_type == "twitter":
        print(f"  🐦 Trying: Twitter/X")
        return search_twitter(twitter_q, headline)
    elif source_type == "instagram":
        print(f"  📷 Trying: Instagram")
        return search_instagram(instagram_q, headline)
    return None, None


# ---------------------------------------------------------------------------
# Supabase operations
# ---------------------------------------------------------------------------

def fetch_articles_needing_media(env, refresh=False, article_id=None):
    """Get articles that need media from Supabase."""
    url = env["SUPABASE_URL"]
    key = env["SUPABASE_SERVICE_ROLE_KEY"]
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
    }

    cols = "id,headline,subheadline,body,category,vertical,image_url,image_attribution,tags"

    if article_id:
        api_url = f"{url}/rest/v1/p2_articles?select={cols}&id=eq.{article_id}"
    else:
        api_url = (
            f"{url}/rest/v1/p2_articles?select={cols}"
            f"&status=eq.published"
            f"&or=(image_url.is.null,image_url.eq.)"
            f"&order=created_at.desc&limit=30"
        )

    resp = requests.get(api_url, headers=headers, timeout=15)
    resp.raise_for_status()
    articles = resp.json()

    if refresh and not article_id:
        api_url2 = (
            f"{url}/rest/v1/p2_articles?select={cols}"
            f"&status=eq.published"
            f"&order=created_at.desc&limit=300"
        )
        resp2 = requests.get(api_url2, headers=headers, timeout=15)
        resp2.raise_for_status()
        existing_ids = {a["id"] for a in articles}
        for a in resp2.json():
            if a["id"] not in existing_ids:
                articles.append(a)

    return articles


def update_article_media(env, article_id, media_url, attribution):
    """Update image_url and image_attribution for an article."""
    url = env["SUPABASE_URL"]
    key = env["SUPABASE_SERVICE_ROLE_KEY"]
    headers = supabase_headers(key)
    api_url = f"{url}/rest/v1/p2_articles?id=eq.{article_id}"
    payload = {"image_url": media_url, "image_attribution": attribution}
    resp = requests.patch(api_url, headers=headers, json=payload, timeout=15)
    resp.raise_for_status()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def is_embed(attribution):
    """Check if the attribution indicates an embed (not a regular image)."""
    if not attribution:
        return False
    return attribution.startswith("embed:")


def cmd_fetch(args):
    """Fetch and assign media to articles."""
    env = load_env()

    refresh = "--refresh" in args
    article_id = None
    if "--id" in args:
        idx = args.index("--id")
        if idx + 1 < len(args):
            article_id = args[idx + 1]

    print("=" * 60)
    print("🎬 Videshi Media Curator (AI-powered)")
    print("   Sources: Pexels · YouTube · Twitter/X · Instagram")
    print("   Strategy: Category-based with multi-query search")
    print("=" * 60)

    articles = fetch_articles_needing_media(env, refresh=refresh, article_id=article_id)

    if not articles:
        print("\n✅ No articles need media right now.")
        return

    print(f"\n📰 Found {len(articles)} article(s) needing media\n")

    skip_ids = _load_skip_ids()
    sourced = 0
    embeds = 0
    processed_images = 0
    skipped = 0
    failed = 0

    for i, article in enumerate(articles):
        headline = article.get("headline", "Unknown")
        aid = article["id"]
        current_url = article.get("image_url") or ""

        if aid in skip_ids:
            print(f"\n[{i+1}/{len(articles)}] {headline[:70]}")
            print(f"  🔒 Skipped (on skip list)")
            skipped += 1
            continue

        # Skip articles that already have processed images (unless refreshing)
        supabase_url = env.get("SUPABASE_URL", "")
        if (not refresh and not article_id
                and current_url.startswith(supabase_url)
                and "/article-images/" in current_url):
            continue

        print(f"\n[{i+1}/{len(articles)}] {headline[:70]}")

        # Find media
        media_url, attribution = find_media_for_article(article)

        if not media_url:
            skipped += 1
            continue

        # Handle based on type
        if is_embed(attribution):
            # Embed — just store the URL directly (no download/processing)
            try:
                update_article_media(env, aid, media_url, attribution)
                embed_type = attribution.split(":")[1].split("|")[0].strip()
                print(f"  💾 Embed ({embed_type}): {media_url[:80]}")
                print(f"  📝 Attribution: {attribution}")
                sourced += 1
                embeds += 1
            except Exception as e:
                print(f"  ⚠ Failed to update: {e}")
                failed += 1
        else:
            # Regular image — download, process, upload
            if HAS_PIL:
                print(f"  🖼 Processing: download → resize → enhance → upload")
                final_url, size_kb = process_and_upload(env, aid, media_url)
                if final_url:
                    try:
                        update_article_media(env, aid, final_url, attribution)
                        print(f"  💾 Processed: {size_kb:.0f}KB → Supabase Storage")
                        print(f"  📝 Attribution: {attribution}")
                        sourced += 1
                        processed_images += 1
                    except Exception as e:
                        print(f"  ⚠ Failed to update: {e}")
                        failed += 1
                else:
                    # Fallback: store raw URL
                    try:
                        update_article_media(env, aid, media_url, attribution)
                        print(f"  💾 Stored raw URL (processing failed)")
                        sourced += 1
                    except Exception as e:
                        print(f"  ⚠ Failed: {e}")
                        failed += 1
            else:
                # No PIL — store raw URL
                try:
                    update_article_media(env, aid, media_url, attribution)
                    print(f"  💾 Stored raw URL (no PIL)")
                    sourced += 1
                except Exception as e:
                    print(f"  ⚠ Failed: {e}")
                    failed += 1

    print(f"\n{'=' * 60}")
    print(f"📊 Results: {sourced} sourced ({processed_images} images, {embeds} embeds), {skipped} no match, {failed} errors")
    print(f"{'=' * 60}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    command = sys.argv[1]
    if command == "fetch":
        cmd_fetch(sys.argv[2:])
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
