#!/usr/bin/env python3
"""
Image Sourcing Module for The Videshi Pipeline.

Multi-source image chain with HTTP verification at every step.
Used by the rolling writer and any other article-creation script.

Priority order:
  1. Source article og:image (from original URL)
  2. RSS feed image (media:thumbnail stored in p2_signals)
  3. Media library cache (person_images table)
  4. Wikipedia person image
  5. Wikimedia Commons search
  6. Pexels fallback
  7. No image (better than broken image)

Every image URL is verified with HTTP GET before use.
"""

import os, re, json, subprocess, urllib.parse, hashlib, time
from io import BytesIO

# ── Env ──────────────────────────────────────────────────────────────────────

def _load_env(path):
    path = os.path.expanduser(path)
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

_load_env("~/workspace/.env.supabase")
_load_env("~/workspace/.env.pexels")

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
PEXELS_KEY   = os.environ.get("PEXELS_API_KEY", "")
UA = "TheVideshi/1.0 (thevideshi.com)"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# ── HTTP Helpers ─────────────────────────────────────────────────────────────

def verify_image_url(url, min_width=400):
    """Verify an image URL is reachable and returns actual image data.
    Uses GET with range header to avoid downloading entire file.
    Returns (ok, content_type, width_hint) or (False, None, 0) on failure.
    
    NEVER use HEAD requests to Wikimedia — they return 400 from this env.
    """
    if not url or not url.startswith("http"):
        return False, None, 0
    
    try:
        # Use curl with --max-time and just fetch headers + first bytes
        result = subprocess.run(
            ["curl", "-sS", "-o", "/dev/null", "-w",
             "%{http_code} %{content_type} %{size_download}",
             "-L", "--max-time", "8", "-r", "0-1023",
             "-A", UA, url],
            capture_output=True, text=True, timeout=12
        )
        parts = result.stdout.strip().split(" ", 2)
        if len(parts) < 2:
            return False, None, 0
        
        status = parts[0]
        ctype = parts[1] if len(parts) > 1 else ""
        size = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0
        
        # Accept 200 or 206 (partial content from range request)
        if status not in ("200", "206"):
            return False, None, 0
        
        # Must be an image type
        if not ctype.startswith("image/"):
            return False, ctype, 0
        
        # Reject SVGs and tiny icons
        if "svg" in ctype:
            return False, ctype, 0
        
        return True, ctype, 0  # Width requires full download; skip for verification
        
    except Exception as e:
        return False, None, 0


def download_image(url, timeout=15):
    """Download image bytes via curl. Returns bytes or None."""
    if not url:
        return None
    try:
        result = subprocess.run(
            ["curl", "-sS", "-L", "--max-time", str(timeout),
             "-A", UA, url],
            capture_output=True, timeout=timeout + 5
        )
        if result.returncode == 0 and len(result.stdout) > 1000:
            return result.stdout
        return None
    except:
        return None


def get_image_dimensions(img_bytes):
    """Get image dimensions without PIL. Returns (width, height) or (0, 0)."""
    try:
        from PIL import Image
        img = Image.open(BytesIO(img_bytes))
        return img.size
    except:
        # Fallback: check JPEG/PNG headers manually
        if img_bytes[:2] == b'\xff\xd8':  # JPEG
            return 800, 600  # Assume reasonable size for JPEGs
        elif img_bytes[:4] == b'\x89PNG':  # PNG
            import struct
            w = struct.unpack('>I', img_bytes[16:20])[0]
            h = struct.unpack('>I', img_bytes[20:24])[0]
            return w, h
        return 0, 0


# ── Source 1: og:image from source article URL ───────────────────────────────

# Known generic/placeholder og:image patterns (site logos, default social cards)
_OG_IMAGE_BLOCKLIST_PATTERNS = [
    "logo", "default", "placeholder", "social-card", "meta-image",
    "site-icon", "favicon", "brand-image", "og-default", "share-image",
    "generic", "fallback", "no-image", "noimage", "missing",
]
_OG_IMAGE_BLOCKLIST_PATHS = [
    "cdn.ncbi.nlm.nih.gov/pubmed/persistent/",
    "static01.nyt.com/vi-assets/",  # NYT generic assets, not article images
    "img.icons8.com/",
]

# Major news domains with high-quality editorial photos (preferred for og:image)
_PREFERRED_NEWS_DOMAINS = {
    "reuters.com", "bbc.com", "bbc.co.uk", "cnn.com", "ndtv.com",
    "indianexpress.com", "thehindu.com", "hindustantimes.com",
    "timesofindia.indiatimes.com", "theguardian.com", "nytimes.com",
    "washingtonpost.com", "aljazeera.com", "apnews.com", "france24.com",
    "livemint.com", "moneycontrol.com", "economictimes.indiatimes.com",
    "firstpost.com", "theprint.in", "scroll.in", "thewire.in",
    "news18.com", "cnbc.com", "bloomberg.com", "techcrunch.com",
    "theverge.com", "wired.com", "arstechnica.com", "espncricinfo.com",
    "cricbuzz.com", "skysports.com", "espn.com", "bbc.com/sport",
    "sky.com", "abc.net.au", "cbc.ca", "globalnews.ca",
}


def _is_generic_og_image(img_url):
    """Check if an og:image URL is a generic placeholder/logo rather than article-specific."""
    if not img_url:
        return True
    lower = img_url.lower()
    for pattern in _OG_IMAGE_BLOCKLIST_PATTERNS:
        if pattern in lower:
            return True
    for path in _OG_IMAGE_BLOCKLIST_PATHS:
        if path in lower:
            return True
    # Skip .gif (usually low-quality thumbnails or tracking pixels)
    if lower.endswith(".gif"):
        return True
    return False


def _og_image_domain_score(source_url):
    """Score how much we trust og:images from this domain.
    Higher = better quality photos expected.
    """
    try:
        domain = urllib.parse.urlparse(source_url).netloc.replace("www.", "").lower()
    except:
        return 0
    if domain in _PREFERRED_NEWS_DOMAINS:
        return 3
    # Any other real news domain
    if any(tld in domain for tld in (".com", ".co.uk", ".in", ".ca", ".au")):
        return 1
    return 0


def fetch_og_image(source_url):
    """Fetch og:image meta tag from a source article URL.
    Returns image URL or None. Skips generic placeholders/logos.
    """
    if not source_url:
        return None
    
    try:
        # Fetch the page head — no range limit (some sites reject range requests)
        result = subprocess.run(
            ["curl", "-sS", "-L", "--max-time", "8",
             "-A", UA, source_url],
            capture_output=True, text=True, timeout=12
        )
        html = result.stdout
        if not html:
            return None
        
        # Extract og:image
        patterns = [
            r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']',
            r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']',
            r'<meta[^>]+name=["\']twitter:image["\'][^>]+content=["\']([^"\']+)["\']',
        ]
        for pattern in patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                import html as _html
                img_url = _html.unescape(match.group(1).strip())
                # Skip data URIs and tiny placeholders
                if img_url.startswith("data:"):
                    continue
                # Make relative URLs absolute
                if img_url.startswith("//"):
                    img_url = "https:" + img_url
                elif img_url.startswith("/"):
                    parsed = urllib.parse.urlparse(source_url)
                    img_url = f"{parsed.scheme}://{parsed.netloc}{img_url}"
                # Skip generic placeholder images
                if _is_generic_og_image(img_url):
                    continue
                return img_url
        
        return None
    except:
        return None


# ── Source 2: Signal images (RSS media:thumbnail) ────────────────────────────

def fetch_signal_images(topic_id):
    """Get image URLs stored in p2_signals for a topic.
    Returns list of image URLs (may be empty).
    """
    if not topic_id or not SUPABASE_URL:
        return []
    
    try:
        result = subprocess.run(
            ["curl", "-sS", "--max-time", "10",
             f"{SUPABASE_URL}/rest/v1/p2_signals?topic_id=eq.{topic_id}&image_url=not.is.null&select=image_url,original_url&limit=5",
             "-H", f"apikey: {SUPABASE_KEY}",
             "-H", f"Authorization: Bearer {SUPABASE_KEY}"],
            capture_output=True, text=True, timeout=15
        )
        data = json.loads(result.stdout)
        return [s["image_url"] for s in data if s.get("image_url")]
    except:
        return []


def fetch_source_urls(topic_id):
    """Get original source URLs for a topic's signals.
    Decodes Google News redirect URLs to actual source URLs.
    Returns list of URLs.
    """
    if not topic_id or not SUPABASE_URL:
        return []
    
    try:
        result = subprocess.run(
            ["curl", "-sS", "--max-time", "10",
             f"{SUPABASE_URL}/rest/v1/p2_signals?topic_id=eq.{topic_id}&select=original_url&limit=5&order=published_at.desc",
             "-H", f"apikey: {SUPABASE_KEY}",
             "-H", f"Authorization: Bearer {SUPABASE_KEY}"],
            capture_output=True, text=True, timeout=15
        )
        data = json.loads(result.stdout)
        raw_urls = [s["original_url"] for s in data if s.get("original_url")]
        
        # Decode Google News redirect URLs to actual source URLs
        decoded = []
        for url in raw_urls:
            actual = _decode_gnews_url(url)
            if actual:
                decoded.append(actual)
        
        return decoded if decoded else raw_urls
    except:
        return []


def _decode_gnews_url(url):
    """Decode a Google News redirect URL to the actual source article URL.
    Returns decoded URL or None if not a Google News URL or decoding fails.
    """
    if not url or "news.google.com" not in url:
        return url  # Not a Google News URL, return as-is
    
    try:
        from googlenewsdecoder import new_decoderv1
        result = new_decoderv1(url, interval=1)
        if result.get("status") and result.get("decoded_url"):
            return result["decoded_url"]
        return None
    except Exception:
        return None


# ── Source 3: Media library cache ────────────────────────────────────────────

def fetch_cached_person_image(person_name):
    """Check person_images table for a cached, verified image.
    Returns image URL or None.
    """
    if not person_name or not SUPABASE_URL:
        return None
    
    try:
        encoded_name = urllib.parse.quote(person_name, safe='')
        result = subprocess.run(
            ["curl", "-sS", "--max-time", "10",
             f"{SUPABASE_URL}/rest/v1/person_images?name=ilike.{encoded_name}&select=image_url&limit=1",
             "-H", f"apikey: {SUPABASE_KEY}",
             "-H", f"Authorization: Bearer {SUPABASE_KEY}"],
            capture_output=True, text=True, timeout=15
        )
        data = json.loads(result.stdout)
        if data and data[0].get("image_url"):
            return data[0]["image_url"]
        return None
    except:
        return None


# ── Source 3.5: YouTube thumbnail ─────────────────────────────────────────────

_load_env("~/workspace/.env.youtube")

_YT_IMG_ACCESS_TOKEN = None
_YT_IMG_TOKEN_EXPIRY = 0

def _get_yt_image_token():
    """Get YouTube OAuth access token (cached ~50 min)."""
    global _YT_IMG_ACCESS_TOKEN, _YT_IMG_TOKEN_EXPIRY
    if _YT_IMG_ACCESS_TOKEN and time.time() < _YT_IMG_TOKEN_EXPIRY:
        return _YT_IMG_ACCESS_TOKEN
    cid = os.environ.get("YOUTUBE_CLIENT_ID", "")
    csec = os.environ.get("YOUTUBE_CLIENT_SECRET", "")
    rtok = os.environ.get("YOUTUBE_REFRESH_TOKEN", "")
    if not (cid and csec and rtok):
        return None
    try:
        import requests
        r = requests.post("https://oauth2.googleapis.com/token", data={
            "client_id": cid, "client_secret": csec,
            "refresh_token": rtok, "grant_type": "refresh_token",
        }, timeout=10)
        data = r.json()
        _YT_IMG_ACCESS_TOKEN = data.get("access_token")
        _YT_IMG_TOKEN_EXPIRY = time.time() + data.get("expires_in", 3600) - 120
        return _YT_IMG_ACCESS_TOKEN
    except:
        return None

# Non-Latin script detector for YouTube language filtering
_NON_LATIN_RE = re.compile(
    r'[\u0900-\u097F\u0980-\u09FF\u0C00-\u0C7F\u0C80-\u0CFF\u0B80-\u0BFF'
    r'\u0A00-\u0A7F\u0A80-\u0AFF\u0B00-\u0B7F\u0D00-\u0D7F'
    r'\u0600-\u06FF\u4E00-\u9FFF\u3040-\u30FF\uAC00-\uD7AF]'
)

# Junk content indicators in YouTube titles
_YT_SKIP_WORDS = {
    "compilation", "top 10", "top 5", "top 20", "meme", "memes", "funny",
    "prank", "reaction video", "fan edit", "whatsapp status",
    "#shorts", "tiktok", "roast", "exposed", "scam",
}

_YT_IMG_QUOTA_USED = 0
_YT_IMG_QUOTA_LIMIT = 4000  # Reserve ~4K units for image sourcing (rest for enricher)

def fetch_youtube_thumbnail(entity_name, headline):
    """Search YouTube for a specific, relevant video and return its thumbnail.
    
    Returns (thumbnail_url, video_title, channel) or (None, None, None).
    Prefers videos where entity name appears in the title (specific, not generic).
    """
    global _YT_IMG_QUOTA_USED
    if _YT_IMG_QUOTA_USED >= _YT_IMG_QUOTA_LIMIT:
        return None, None, None
    if not entity_name or len(entity_name) < 3:
        return None, None, None
    
    token = _get_yt_image_token()
    if not token:
        return None, None, None
    
    # Build a focused search query
    # Strip common stopwords from headline to get keywords
    _stop = {"the","of","in","and","for","a","an","is","at","on","to","with","by",
             "from","as","its","it","that","this","but","or","has","had","was",
             "were","are","be","been","have","his","her","he","she","they","their",
             "we","our","you","your","about","after","before","how","why","what",
             "when","where","who","new","says","said","could","would","will","can",
             "may","more","into","over","up","out","just","also","than","most","first"}
    headline_words = [w for w in headline.split() if w.lower() not in _stop and len(w) > 2]
    # Remove entity name words from keywords to avoid redundancy
    entity_words_lower = {w.lower() for w in entity_name.split()}
    keywords = [w for w in headline_words if w.lower() not in entity_words_lower][:3]
    query = f"{entity_name} {' '.join(keywords)}"
    
    from datetime import datetime, timedelta, timezone
    after = (datetime.now(timezone.utc) - timedelta(days=90)).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    try:
        import requests
        r = requests.get("https://www.googleapis.com/youtube/v3/search", params={
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": 5,
            "order": "relevance",
            "publishedAfter": after,
            "relevanceLanguage": "en",
        }, headers={"Authorization": f"Bearer {token}"}, timeout=15)
        _YT_IMG_QUOTA_USED += 100
        
        if r.status_code != 200:
            return None, None, None
        
        items = r.json().get("items", [])
        if not items:
            return None, None, None
        
        # Score each result
        entity_lower = entity_name.lower()
        entity_parts = [p for p in entity_lower.split() if len(p) > 2]
        best = None
        best_score = 0
        
        for item in items:
            snip = item.get("snippet", {})
            title = snip.get("title", "")
            channel = snip.get("channelTitle", "")
            title_lower = title.lower()
            channel_lower = channel.lower()
            
            score = 0
            
            # Entity name in title (strong signal — video IS about this person)
            if entity_lower in title_lower:
                score += 5
            elif all(p in title_lower for p in entity_parts):
                score += 4
            
            # Entity in channel (official channel)
            if entity_lower in channel_lower:
                score += 3
            
            # Keyword hits
            kw_hits = sum(1 for kw in keywords if kw.lower() in title_lower)
            score += kw_hits * 1.5
            
            # Penalty for junk
            for sw in _YT_SKIP_WORDS:
                if sw in title_lower:
                    score -= 5
            
            # Penalty for non-English
            non_latin = len(_NON_LATIN_RE.findall(title + " " + channel))
            if non_latin >= 3:
                score -= 10
            elif non_latin >= 1:
                score -= 3
            
            # Bonus for news/official content
            for ow in ("official", "press conference", "interview", "announcement", "keynote"):
                if ow in title_lower:
                    score += 1
                    break
            
            if score > best_score:
                best_score = score
                best = item
        
        # Require entity name in title (specificity gate) AND minimum score
        if not best or best_score < 4:
            return None, None, None
        
        vid_id = best["id"]["videoId"]
        title = best["snippet"]["title"]
        channel = best["snippet"]["channelTitle"]
        
        # Try maxresdefault first (1280x720), fall back to hqdefault (480x360)
        for quality in ["maxresdefault", "sddefault", "hqdefault"]:
            thumb_url = f"https://img.youtube.com/vi/{vid_id}/{quality}.jpg"
            ok, ctype, _ = verify_image_url(thumb_url, min_width=400)
            if ok:
                return thumb_url, title, channel
        
        return None, None, None
        
    except Exception as e:
        print(f"    ⚠ YouTube thumbnail search error: {e}")
        return None, None, None

def fetch_wikipedia_image(entity_name, article_context=None):
    """Fetch image from Wikipedia REST API for a person/entity.
    Returns image URL or None.
    
    If article_context (headline or body snippet) is provided, validates that
    the Wikipedia page is relevant — not a disambiguation page, generic concept,
    or landmark only geographically related to the article.
    """
    if not entity_name:
        return None
    
    encoded = urllib.parse.quote(entity_name.replace(" ", "_"))
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}"
    
    try:
        result = subprocess.run(
            ["curl", "-sS", "--max-time", "8", "-A", UA, url],
            capture_output=True, text=True, timeout=12
        )
        data = json.loads(result.stdout)
        img = (data.get("originalimage") or {}).get("source") or \
              (data.get("thumbnail") or {}).get("source")
        if not img:
            return None

        # ── Relevance guards (mirrors enrich-articles.py) ──
        wiki_desc = (data.get("description") or "").lower()
        wiki_type = (data.get("type") or "")

        # Reject disambiguation pages
        if wiki_type == "disambiguation" or "disambiguation" in wiki_desc or "referred to by the same term" in wiki_desc:
            print(f"    ⊘ Skipping Wikipedia image for '{entity_name}' — disambiguation page")
            return None

        # Reject generic concept pages
        _GENERIC_DESCS = {
            "international competition", "competition", "sporting event",
            "award", "awards ceremony", "trophy", "memorial",
            "concept", "term", "phrase", "expression", "song",
            "album", "single", "film", "television series",
            "video game", "book", "novel", "poem",
            "newspaper", "daily newspaper", "indian newspaper",
            "english-language newspaper", "publication", "news media",
            "magazine", "journal", "tabloid", "news agency",
            "sports competition", "tournament", "cup", "league",
            "recurring sporting event", "annual sporting event",
            "festival", "ceremony", "event",
            "prize", "prizes", "medal", "honour", "honor",
        }
        _GENERIC_DESC_KW = {
            "newspaper", "publication", "tabloid", "magazine",
            "front page", "news agency", "media company",
        }
        if wiki_desc in _GENERIC_DESCS:
            print(f"    ⊘ Skipping Wikipedia image for '{entity_name}' — generic concept: '{wiki_desc}'")
            return None
        if any(kw in wiki_desc for kw in _GENERIC_DESC_KW):
            print(f"    ⊘ Skipping Wikipedia image for '{entity_name}' — publication/media: '{wiki_desc}'")
            return None

        # Reject landmark/place images unless the entity is named in the article
        _PLACE_KW = {
            "monument", "landmark", "tower", "gate", "fort", "palace",
            "temple", "mosque", "church", "cathedral", "mausoleum",
            "bridge", "dam", "statue", "memorial", "building",
            "skyscraper", "shipyard", "factory", "port", "airport",
            "stadium", "arena", "park", "garden", "museum", "library",
            "observatory", "pier", "lighthouse", "arch", "obelisk",
            "stupa", "pagoda", "citadel", "fortress", "tomb",
            "residence", "house", "mansion", "hall", "complex",
            "city", "town", "village", "district", "municipality",
        }
        if article_context and any(kw in wiki_desc for kw in _PLACE_KW):
            if entity_name.lower() not in article_context.lower():
                print(f"    ⊘ Skipping Wikipedia image for '{entity_name}' — "
                      f"place ('{wiki_desc[:50]}') not mentioned by name in article")
                return None

        return img
    except:
        return None


# ── Source 5: Wikimedia Commons ──────────────────────────────────────────────

# Confusable subjects that need extra validation
_COMMONS_NEGATIVE = {
    "capitol": ["state capitol", "pennsylvania", "harrisburg", "austin", "sacramento", "olympia"],
    "white house": ["model", "replica", "miniature"],
    "supreme court": ["state supreme"],
}

_COMMONS_STOP = {
    "the", "and", "for", "with", "from", "that", "this", "will", "has", "have",
    "been", "after", "about", "over", "says", "said", "more", "than", "also",
    "new", "india", "indian", "us", "uk", "people", "world", "year", "time",
    "news", "social", "media", "photo", "image", "file", "commons",
}

def commons_relevance_ok(commons_title, headline, topic=""):
    """Check if a Commons file title is relevant to the headline."""
    title_l = (commons_title or "").lower()
    headline_l = (headline or "").lower()
    topic_l = (topic or "").lower()
    
    # Check confusable subjects
    for subject, negatives in _COMMONS_NEGATIVE.items():
        if subject in headline_l:
            for neg in negatives:
                if neg in title_l:
                    return False
    
    # Require at least 1 distinctive keyword match
    headline_words = set(re.findall(r'[a-z]{4,}', headline_l + " " + topic_l))
    distinctive = headline_words - _COMMONS_STOP
    if not distinctive:
        return True  # All-generic headline, don't over-filter
    
    for word in distinctive:
        if word in title_l:
            return True
    
    return False


def fetch_wikimedia_commons_image(search_query, headline=""):
    """Search Wikimedia Commons for a relevant image.
    Returns image URL or None.
    """
    if not search_query:
        return None
    
    params = urllib.parse.urlencode({
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrsearch": search_query,
        "gsrlimit": "5",
        "prop": "imageinfo",
        "iiprop": "url|mime|size",
        "iiurlwidth": "1200",
    })
    url = f"https://commons.wikimedia.org/w/api.php?{params}"
    
    try:
        result = subprocess.run(
            ["curl", "-sS", "--max-time", "10", "-A", UA, url],
            capture_output=True, text=True, timeout=15
        )
        data = json.loads(result.stdout)
        pages = (data.get("query") or {}).get("pages") or {}
        
        for page_id, page in sorted(pages.items(), key=lambda x: x[1].get("index", 999)):
            title = page.get("title", "")
            ii = (page.get("imageinfo") or [{}])[0]
            mime = ii.get("mime", "")
            
            if not mime.startswith("image/") or mime == "image/svg+xml":
                continue
            
            if not commons_relevance_ok(title, headline, search_query):
                continue
            
            # Prefer thumburl (resized) over full URL
            img_url = ii.get("thumburl") or ii.get("url")
            if img_url:
                return img_url
        
        return None
    except:
        return None


# ── Source 6: Pexels ─────────────────────────────────────────────────────────

def fetch_pexels_image(query):
    """Search Pexels for a topical image. Returns URL or None."""
    if not PEXELS_KEY or not query:
        return None
    
    encoded = urllib.parse.quote(query)
    url = f"https://api.pexels.com/v1/search?query={encoded}&per_page=3&orientation=landscape"
    
    try:
        result = subprocess.run(
            ["curl", "-sS", "--max-time", "8", url,
             "-H", f"Authorization: {PEXELS_KEY}"],
            capture_output=True, text=True, timeout=12
        )
        data = json.loads(result.stdout)
        photos = data.get("photos", [])
        for photo in photos:
            src = photo.get("src", {})
            img_url = src.get("large2x") or src.get("large") or src.get("original")
            if img_url:
                return img_url
        return None
    except:
        return None


# ── Upload ───────────────────────────────────────────────────────────────────

def compress_image(img_bytes, max_width=1200, quality=80):
    """Resize and compress image to JPEG. Returns bytes or None."""
    try:
        from PIL import Image
        img = Image.open(BytesIO(img_bytes))
        if img.mode in ('RGBA', 'P', 'LA'):
            img = img.convert('RGB')
        
        w, h = img.size
        if w > max_width:
            ratio = max_width / w
            img = img.resize((max_width, int(h * ratio)), Image.LANCZOS)
        
        out = BytesIO()
        img.save(out, format='JPEG', quality=quality, optimize=True)
        return out.getvalue()
    except:
        return img_bytes  # Return raw if compression fails


def upload_to_supabase(img_bytes, filename):
    """Upload image to Supabase article-images bucket. Returns public URL or None."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None
    
    url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
    
    try:
        result = subprocess.run(
            ["curl", "-sS", "--max-time", "15", "-X", "POST", url,
             "-H", f"apikey: {SUPABASE_KEY}",
             "-H", f"Authorization: Bearer {SUPABASE_KEY}",
             "-H", "Content-Type: image/jpeg",
             "-H", "x-upsert: true",
             "--data-binary", "@-"],
            input=img_bytes, capture_output=True, timeout=20
        )
        stdout = result.stdout.decode("utf-8", errors="replace") if isinstance(result.stdout, bytes) else result.stdout
        if result.returncode == 0:
            try:
                resp = json.loads(stdout)
                if "Key" in resp or "Id" in resp:
                    return f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            except:
                pass
            # Check for success even without JSON
            if "200" in stdout or not stdout.strip():
                return f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
        return None
    except:
        return None


# ── Main Image Chain ─────────────────────────────────────────────────────────

def source_hero_image(article, used_images=None):
    """Multi-source image sourcing with HTTP verification at every step.
    
    Args:
        article: Dict with headline, slug, category, topic_id, image_search_query,
                 image_entities, image_must_show. May also have 'sources' (list of URLs).
        used_images: Set of image URLs already used in this batch
    
    Returns:
        (final_url, attribution, caption) or (None, None, None)
    """
    headline = article.get("headline", "")
    slug = article.get("slug", "unknown")
    topic_id = article.get("topic_id")
    search_query = article.get("image_search_query", "")
    entities = article.get("image_entities", [])
    must_show = article.get("image_must_show", "")
    category = article.get("category", "")
    
    if used_images is None:
        used_images = set()
    
    print(f"  🖼  Sourcing image: {headline[:55]}...")
    
    img_url = None
    attribution = "The Videshi"
    source_name = None
    
    # ── Source 1: og:image from source articles (ranked by quality) ──────
    if not img_url:
        # Gather source URLs: prefer article's own sources (already decoded),
        # then fall back to signal URLs (may need Google News decoding)
        all_source_urls = []
        
        # Article's sources field (already real URLs, no decoding needed)
        article_sources = article.get("sources", [])
        if isinstance(article_sources, str):
            try:
                article_sources = json.loads(article_sources)
            except:
                article_sources = []
        if isinstance(article_sources, list):
            for src in article_sources:
                if isinstance(src, str) and src.startswith("http"):
                    all_source_urls.append(src)
                elif isinstance(src, dict) and src.get("url", "").startswith("http"):
                    all_source_urls.append(src["url"])
        
        # Signal URLs (from p2_signals, may need Google News decoding)
        if topic_id:
            signal_urls = fetch_source_urls(topic_id)
            for u in signal_urls:
                if u not in all_source_urls:
                    all_source_urls.append(u)
        
        # Collect all valid og:images with domain quality scores
        og_candidates = []
        for src_url in all_source_urls[:6]:
            og_img = fetch_og_image(src_url)
            if og_img and og_img not in used_images:
                ok, ctype, _ = verify_image_url(og_img)
                if ok:
                    domain_score = _og_image_domain_score(src_url)
                    try:
                        domain = urllib.parse.urlparse(src_url).netloc.replace("www.", "")
                    except:
                        domain = "Source Article"
                    og_candidates.append({
                        "img_url": og_img,
                        "domain": domain,
                        "score": domain_score,
                    })
        
        if og_candidates:
            # Pick the best: prefer higher domain score
            og_candidates.sort(key=lambda c: c["score"], reverse=True)
            best = og_candidates[0]
            img_url = best["img_url"]
            attribution = best["domain"]
            source_name = "og:image"
            print(f"    ✓ og:image from {attribution} (score {best['score']}, {len(og_candidates)} candidates)")
    
    # ── Source 2: RSS feed images (stored in p2_signals) ─────────────────
    if not img_url and topic_id:
        signal_images = fetch_signal_images(topic_id)
        for sig_img in signal_images:
            if sig_img not in used_images:
                ok, ctype, _ = verify_image_url(sig_img)
                if ok:
                    img_url = sig_img
                    attribution = "Feed Source"
                    source_name = "rss_thumbnail"
                    print(f"    ✓ RSS thumbnail")
                    break
    
    # ── Source 3: Media library cache (person_images) ────────────────────
    if not img_url and entities:
        for entity in entities[:3]:
            if isinstance(entity, str) and len(entity) > 2:
                cached = fetch_cached_person_image(entity)
                if cached and cached not in used_images:
                    ok, ctype, _ = verify_image_url(cached)
                    if ok:
                        img_url = cached
                        attribution = "Media Library"
                        source_name = "person_cache"
                        print(f"    ✓ Cached image for '{entity}'")
                        break
    
    # ── Source 3.5: YouTube thumbnail (specific, recent) ─────────────────
    # For named entities, a relevant YouTube video's thumbnail is often the
    # best image — it shows the actual person/event, not a generic stock photo.
    if not img_url and entities:
        main_entity = next((e for e in entities[:2] if isinstance(e, str) and len(e) > 2), None)
        if main_entity:
            yt_thumb, yt_title, yt_channel = fetch_youtube_thumbnail(main_entity, headline)
            if yt_thumb and yt_thumb not in used_images:
                img_url = yt_thumb
                attribution = f"YouTube / {yt_channel}" if yt_channel else "YouTube"
                source_name = "youtube_thumbnail"
                print(f"    ✓ YouTube thumbnail for '{main_entity}' → \"{yt_title[:50]}\"")
    
    # ── Source 4: Wikipedia person image ─────────────────────────────────
    if not img_url and entities:
        for entity in entities[:3]:
            if isinstance(entity, str) and len(entity) > 2:
                wp_img = fetch_wikipedia_image(entity, article_context=headline)
                if wp_img and wp_img not in used_images:
                    ok, ctype, _ = verify_image_url(wp_img)
                    if ok:
                        img_url = wp_img
                        attribution = "Wikimedia Commons"
                        source_name = "wikipedia"
                        print(f"    ✓ Wikipedia image for '{entity}'")
                        break
                    else:
                        print(f"    ✗ Wikipedia image FAILED verification for '{entity}'")
    
    # ── Source 5: Wikimedia Commons search ───────────────────────────────
    if not img_url:
        query = search_query or must_show or headline[:60]
        commons_img = fetch_wikimedia_commons_image(query, headline)
        if commons_img and commons_img not in used_images:
            ok, ctype, _ = verify_image_url(commons_img)
            if ok:
                img_url = commons_img
                attribution = "Wikimedia Commons"
                source_name = "commons_search"
                print(f"    ✓ Commons search result")
            else:
                print(f"    ✗ Commons image FAILED verification")
    
    # ── Source 6: Pexels fallback ────────────────────────────────────────
    if not img_url:
        query = search_query or must_show or headline[:40]
        pexels_img = fetch_pexels_image(query)
        if pexels_img and pexels_img not in used_images:
            ok, ctype, _ = verify_image_url(pexels_img)
            if ok:
                img_url = pexels_img
                attribution = "Pexels"
                source_name = "pexels"
                print(f"    ✓ Pexels fallback")
    
    # ── No image found ──────────────────────────────────────────────────
    if not img_url:
        print(f"    ✗ No image found — publishing without hero (better than broken)")
        return None, None, None
    
    # ── Download, compress, upload ──────────────────────────────────────
    raw_bytes = download_image(img_url)
    if not raw_bytes:
        print(f"    ✗ Download failed: {img_url[:60]}")
        return None, None, None
    
    # Check dimensions
    w, h = get_image_dimensions(raw_bytes)
    if w > 0 and w < 400:
        print(f"    ✗ Image too small ({w}x{h}), skipping")
        return None, None, None
    
    # Compute focal point if available
    fx, fy = 0.5, 0.5
    try:
        from focal_point import compute_focal_point, image_dimensions as fp_dims
        fx, fy = compute_focal_point(raw_bytes)
        w, h = fp_dims(raw_bytes)
        article["focal_x"] = fx
        article["focal_y"] = fy
        if w > 0 and h > 0:
            article["img_w"] = w
            article["img_h"] = h
    except:
        pass
    
    face_flag = "👤" if (fx != 0.5 or fy != 0.5) else "📐"
    print(f"    {face_flag} {source_name} → {w}×{h}, focal ({fx:.2f}, {fy:.2f})")
    
    # Use the original source URL directly — no Supabase upload.
    # Source CDNs (Wikipedia, Pexels, news sites) are fast and reliable.
    final_url = img_url
    
    # Caption — keep factual, only use first entity name if confident
    caption = None
    if entities and len(entities) > 0 and isinstance(entities[0], str):
        caption = entities[0]
    
    print(f"    ✅ Hero image ready: {source_name} → {final_url[-60:]}")
    return final_url, attribution, caption


# ── Extract RSS image from feed item ─────────────────────────────────────────

def extract_rss_image(entry_xml_element):
    """Extract image URL from an RSS/Atom entry's XML element.
    Checks: media:thumbnail, media:content, enclosure, image.
    
    Args:
        entry_xml_element: An xml.etree.ElementTree Element for an <item> or <entry>
    
    Returns:
        Image URL string or None
    """
    ns = {
        'media': 'http://search.yahoo.com/mrss/',
        'atom': 'http://www.w3.org/2005/Atom',
    }
    
    # 1. media:thumbnail
    thumb = entry_xml_element.find('media:thumbnail', ns)
    if thumb is not None:
        url = thumb.get('url')
        if url:
            return url
    
    # 2. media:content (type=image/*)
    for mc in entry_xml_element.findall('media:content', ns):
        mtype = mc.get('type', '')
        url = mc.get('url', '')
        if mtype.startswith('image/') and url:
            return url
        # Some feeds don't set type but have medium="image"
        if mc.get('medium') == 'image' and url:
            return url
    
    # 3. enclosure (type=image/*)
    for enc in entry_xml_element.findall('enclosure'):
        if enc.get('type', '').startswith('image/') and enc.get('url'):
            return enc.get('url')
    
    # 4. Check for image element (some custom feeds)
    img = entry_xml_element.find('image')
    if img is not None:
        url = img.get('url') or (img.find('url') is not None and img.find('url').text)
        if url:
            return url
    
    return None


if __name__ == "__main__":
    import sys, argparse

    parser = argparse.ArgumentParser(description="Image sourcer for The Videshi articles")
    parser.add_argument("--article-json", help="JSON string with article metadata")
    parser.add_argument("--slug", help="Fetch article from DB by slug and source its image")
    parser.add_argument("--backfill", action="store_true",
                        help="Find recent articles missing hero images and source them")
    parser.add_argument("--hours", type=int, default=6,
                        help="Hours to look back for --backfill (default: 6)")
    parser.add_argument("--apply", action="store_true",
                        help="Actually update the DB (default: dry run)")
    parser.add_argument("--test-url", help="Test og:image fetch for a URL")
    args = parser.parse_args()

    if args.test_url:
        print(f"Testing og:image fetch for: {args.test_url}")
        og = fetch_og_image(args.test_url)
        print(f"  og:image: {og}")
        if og:
            ok, ct, _ = verify_image_url(og)
            print(f"  Verified: {ok} ({ct})")

    elif args.article_json:
        article = json.loads(args.article_json)
        url, attr, caption = source_hero_image(article)
        result = {"image_url": url, "attribution": attr, "caption": caption}
        if article.get("focal_x") is not None:
            result["focal_x"] = article["focal_x"]
            result["focal_y"] = article["focal_y"]
        if article.get("img_w"):
            result["img_w"] = article["img_w"]
            result["img_h"] = article["img_h"]
        print("IMAGE_RESULT:" + json.dumps(result))

    elif args.slug:
        # Fetch article from DB and source its image
        r = subprocess.run(
            ["curl", "-s",
             f"{SUPABASE_URL}/rest/v1/p2_articles?select=id,headline,slug,category,topic_id,sources&slug=eq.{args.slug}&limit=1",
             "-H", f"apikey: {SUPABASE_KEY}",
             "-H", f"Authorization: Bearer {SUPABASE_KEY}"],
            capture_output=True, text=True, timeout=10
        )
        rows = json.loads(r.stdout)
        if not rows:
            print(f"ERROR: No article found with slug '{args.slug}'")
            sys.exit(1)
        article = rows[0]
        url, attr, caption = source_hero_image(article)
        if url:
            print(f"\n  Image found: {url[:80]}")
            if args.apply:
                patch = {"image_url": url, "image_attribution": attr}
                if caption:
                    patch["image_caption"] = caption
                if article.get("focal_x") is not None:
                    patch["focal_x"] = article["focal_x"]
                    patch["focal_y"] = article["focal_y"]
                pr = subprocess.run(
                    ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
                     "-X", "PATCH",
                     f"{SUPABASE_URL}/rest/v1/p2_articles?slug=eq.{args.slug}",
                     "-H", f"apikey: {SUPABASE_KEY}",
                     "-H", f"Authorization: Bearer {SUPABASE_KEY}",
                     "-H", "Content-Type: application/json",
                     "-H", "Prefer: return=minimal",
                     "-d", json.dumps(patch)],
                    capture_output=True, text=True, timeout=10
                )
                print(f"  DB update: HTTP {pr.stdout}")
            else:
                print("  (dry run — use --apply to update DB)")
        else:
            print("  No image found across all sources.")
        result = {"image_url": url, "attribution": attr, "caption": caption}
        print("IMAGE_RESULT:" + json.dumps(result))

    elif args.backfill:
        from datetime import datetime, timedelta, timezone
        cutoff = (datetime.now(timezone.utc) - timedelta(hours=args.hours)).strftime("%Y-%m-%dT%H:%M:%SZ")
        print(f"Backfilling hero images for articles published since {cutoff}...")
        encoded_cutoff = urllib.parse.quote(cutoff, safe='')
        r = subprocess.run(
            ["curl", "-s",
             f"{SUPABASE_URL}/rest/v1/p2_articles?select=id,headline,slug,category,topic_id,sources"
             f"&status=eq.published&image_url=is.null&published_at=gte.{encoded_cutoff}"
             f"&order=published_at.desc",
             "-H", f"apikey: {SUPABASE_KEY}",
             "-H", f"Authorization: Bearer {SUPABASE_KEY}"],
            capture_output=True, text=True, timeout=15
        )
        rows = json.loads(r.stdout)
        if not rows:
            print("No articles missing hero images.")
            sys.exit(0)
        print(f"Found {len(rows)} articles missing hero images.\n")
        used = set()
        fixed = 0
        failed = 0
        for article in rows:
            url, attr, caption = source_hero_image(article, used_images=used)
            if url:
                used.add(url)
                if args.apply:
                    patch = {"image_url": url, "image_attribution": attr}
                    if caption:
                        patch["image_caption"] = caption
                    if article.get("focal_x") is not None:
                        patch["focal_x"] = article["focal_x"]
                        patch["focal_y"] = article["focal_y"]
                    pr = subprocess.run(
                        ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
                         "-X", "PATCH",
                         f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article['id']}",
                         "-H", f"apikey: {SUPABASE_KEY}",
                         "-H", f"Authorization: Bearer {SUPABASE_KEY}",
                         "-H", "Content-Type: application/json",
                         "-H", "Prefer: return=minimal",
                         "-d", json.dumps(patch)],
                        capture_output=True, text=True, timeout=10
                    )
                    status = pr.stdout.strip()
                    if status == "204":
                        fixed += 1
                        print(f"    ✅ DB updated")
                    else:
                        print(f"    ⚠ DB patch returned {status}")
                else:
                    fixed += 1
                    print(f"    (dry run)")
            else:
                failed += 1

        mode = "APPLIED" if args.apply else "DRY RUN"
        print(f"\n{'='*50}")
        print(f"Backfill complete ({mode}): {fixed} fixed, {failed} still missing out of {len(rows)}")

    else:
        parser.print_help()
