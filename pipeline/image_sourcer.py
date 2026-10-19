#!/usr/bin/env python3
"""
Image Sourcing Module for The Videshi Pipeline.

Multi-source image chain with HTTP verification at every step.
Used by the rolling writer and any other article-creation script.

Priority order:
  1. Source article og:image (from original URL)
  2. RSS feed image (media:thumbnail stored in p2_signals)
  3. Media library cache (person_images table)
  3.5. YouTube thumbnail (specific, recent)
  3.6. Official source (government / company press pages — curated allowlist)
  3.7. PR Newswire India (press-approved images)
  3.8. Person profile (subject's own institutional profile page —
       exact-name alt verified; named-person articles, before Wikipedia)
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

def _safe_run(cmd, **kwargs):
    """subprocess.run that never leaks the command into tracebacks.

    Curl commands embed the Supabase service-role key in -H headers; a bare
    subprocess.TimeoutExpired stringifies the full argv (key included) into
    logs. This wrapper converts timeouts/errors into a sanitized RuntimeError.
    """
    try:
        return subprocess.run(cmd, **kwargs)
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"subprocess timed out after {kwargs.get('timeout')}s")
    except Exception as e:
        raise RuntimeError(f"subprocess failed: {type(e).__name__}")


def _patch_article_and_verify(filter_param, payload):
    """PATCH p2_articles and verify at least one row was actually updated.

    PostgREST returns 204 even when zero rows match the filter, so a bare
    status-code check cannot distinguish a real write from a no-op (e.g. a
    slug/id typo). We request return=representation and require a non-empty
    row array before reporting success.
    """
    pr = _safe_run(
        ["curl", "-s", "-w", "\n%{http_code}",
         "-X", "PATCH",
         f"{SUPABASE_URL}/rest/v1/p2_articles?{filter_param}&select=id",
         "-H", f"apikey: {SUPABASE_KEY}",
         "-H", f"Authorization: Bearer {SUPABASE_KEY}",
         "-H", "Content-Type: application/json",
         "-H", "Prefer: return=representation",
         "-d", json.dumps(payload)],
        capture_output=True, text=True, timeout=30
    )
    body, _, code = pr.stdout.rpartition("\n")
    try:
        rows = json.loads(body) if body.strip() else []
    except (json.JSONDecodeError, ValueError):
        rows = []
    return code.strip() in ("200", "201", "204") and isinstance(rows, list) and len(rows) > 0

# ── Image-write overlap lock ─────────────────────────────────────────────────
# Several writers PATCH image_url on p2_articles (image_sourcer --slug,
# image_sourcer --backfill, source-image.py --apply, the 4h enricher).
# The lock serializes the DB writes only — it must NOT be held during the
# slow network sourcing phase, or parallel writers block each other for
# minutes and the lock looks "stale". Hold time should be milliseconds.
# flock() is kernel-managed: it is always released when the holder's fd
# closes or the process dies, so it can never go stale by itself.

def _acquire_image_lock(timeout_secs=30):
    """Acquire the image-write lock, waiting up to timeout_secs.

    Returns the open file handle (caller MUST close it to release, ideally
    in a try/finally), or None if the lock could not be acquired in time.
    The holder's PID is written into the lock file for debugging.
    """
    import fcntl
    import time
    _lock_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              ".state", "image-write.lock")
    os.makedirs(os.path.dirname(_lock_path), exist_ok=True)
    fh = open(_lock_path, "w")
    deadline = time.time() + timeout_secs
    while True:
        try:
            fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
            fh.write(f"{os.getpid()}\n")
            fh.flush()
            return fh
        except (IOError, OSError):
            if time.time() >= deadline:
                fh.close()
                return None
            time.sleep(0.2)

# ── HTTP Helpers ─────────────────────────────────────────────────────────────

def verify_image_url(url, min_width=800):
    """Verify an image URL is reachable and returns actual image data.
    Downloads the full image and validates bytes with PIL — a range-request
    pre-check alone is not enough (misconfigured CDNs can return 200/206 with
    an image content-type for the first bytes while the full file 404s; seen
    2026-09-19 with a Healthline og:image that passed twice).
    Returns (ok, content_type, width) or (False, None, 0) on failure.

    HERO QUALITY BAR (2026-10-11): min_width defaults to 800px. Hero images
    below 800px wide look pixelated on modern displays. All sources in the
    hero chain (og:image, RSS, cache, YouTube, official, PRN, Wikipedia,
    Commons, Pexels) must meet this bar.

    NEVER use HEAD requests to Wikimedia — they return 400 from this env.
    """
    if not url or not url.startswith("http"):
        return False, None, 0

    try:
        # Full download via curl (follows redirects)
        result = subprocess.run(
            ["curl", "-sS", "-L", "--max-time", "15", "-A", UA, url],
            capture_output=True, timeout=20
        )
        if result.returncode != 0 or not result.stdout or len(result.stdout) < 1000:
            return False, None, 0
        img_bytes = result.stdout

        # Validate actual image bytes with PIL
        try:
            from PIL import Image
            from io import BytesIO
            img = Image.open(BytesIO(img_bytes))
            img.verify()  # raises on truncated/corrupt data
            img = Image.open(BytesIO(img_bytes))  # reopen after verify
            width, height = img.size
        except Exception:
            # Fallback: JPEG/PNG magic bytes
            if img_bytes[:2] == b'\xff\xd8':
                width, height = 800, 600
            elif img_bytes[:4] == b'\x89PNG':
                width, height = 800, 600
            else:
                return False, None, 0

        # Reject SVG masquerading as raster
        if img_bytes[:5].lower().startswith(b'<?xml') or b'<svg' in img_bytes[:200].lower():
            return False, None, 0

        # Minimum width check
        if width < min_width:
            return False, None, 0

        # Guess content type from magic bytes
        if img_bytes[:2] == b'\xff\xd8':
            ctype = "image/jpeg"
        elif img_bytes[:4] == b'\x89PNG':
            ctype = "image/png"
        elif img_bytes[:4] == b'RIFF' and img_bytes[8:12] == b'WEBP':
            ctype = "image/webp"
        elif img_bytes[:6] in (b'GIF87a', b'GIF89a'):
            ctype = "image/gif"
        else:
            ctype = "image/unknown"

        return True, ctype, width

    except Exception:
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

# Generic social-card filenames served at domain root are site branding, not
# article art (2026-10-07: 1stheadlines.com/og.jpg — a "1st HEADLINES / Breaking
# News Headlines" logo — was accepted as the hero for a wrestlers-visa story).
# Only treated as generic when the path is shallow (<=2 segments); an
# article-specific path like /wp-content/uploads/2026/07/og.jpg is fine.
_ROOT_SOCIAL_FILENAMES = {
    "og.jpg", "og.jpeg", "og.png", "og.webp",
    "og-image.jpg", "og-image.jpeg", "og-image.png",
    "share.jpg", "share.jpeg", "share.png",
    "default.jpg", "default.jpeg", "default.png",
    "social.jpg", "social.jpeg", "social.png",
    "preview.jpg", "thumbnail.jpg",
}
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

# AI-generation markers in image filenames. The pipeline never publishes
# AI-generated article images (standing editorial rule), so an og:image whose
# filename advertises AI generation is treated as generic/rejected.
# (2026-09-13: Hindustan Times CDN serves AI-generated og:images with a
# 'Gemini_' filename prefix — one slipped into the BRICS gala article.)
# (2026-09-19: Mint serves ChatGPT-generated og:images with a 'chat_<digits>'
# filename prefix — one slipped onto the H-1B $100k-fee article twice, and a
# human review confirmed it was AI-generated. The trailing underscore keeps it
# specific; "chatgpt" alone does not match Mint's 'chat_' naming.)
# Filename-level only, like "logo": a directory named e.g. "gemini" elsewhere
# in the path is not evidence the image itself is AI-generated.
_AI_GENERATED_FILENAME_MARKERS = [
    "gemini", "ai-generated", "aigenerated", "midjourney", "dall-e",
    "dalle", "firefly", "stable-diffusion", "stablediffusion",
    "leonardo", "imagen", "chatgpt", "chat_",
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
    """Check if an og:image URL is a generic placeholder/logo rather than article-specific.

    NOTE (2026-09-12): Hindustan Times serves ALL editorial images from a CDN path
    like /ht-img/img/YYYY/MM/DD/{size}/logo/{filename} — "logo" there is a crop-preset
    directory marker, not an actual logo image. A blanket "logo" substring match was
    rejecting every HT og:image and dropping home-tour (and other) articles to
    Wikipedia portraits. So "logo" is only generic when it appears in the filename,
    not in an intermediate directory segment.
    """
    if not img_url:
        return True
    lower = img_url.lower()
    try:
        path = urllib.parse.urlparse(lower).path
    except Exception:
        path = lower
    segments = [s for s in path.split("/") if s]
    filename = segments[-1] if segments else ""
    dir_segments = segments[:-1]

    # The filename is checked against every pattern (site-logo.png etc. still caught)
    for pattern in _OG_IMAGE_BLOCKLIST_PATTERNS:
        if pattern in filename:
            return True
    # AI-generated images are never acceptable as article heroes (standing
    # editorial rule). A filename advertising AI generation (e.g. HT CDN's
    # 'Gemini_' prefix) rejects the og:image so the cascade falls through to
    # Wikipedia/Commons/Pexels instead of ranking the AI image above them.
    for marker in _AI_GENERATED_FILENAME_MARKERS:
        if marker in filename:
            return True
    # Directory segments are checked too (catches /default/550x309.jpg style
    # placeholders), but NOT for "logo" — several news CDNs (HT included) use
    # /logo/ as a structural directory marker in real editorial image URLs.
    for pattern in _OG_IMAGE_BLOCKLIST_PATTERNS:
        if pattern == "logo":
            continue
        for seg in dir_segments:
            if pattern in seg:
                return True

    for path_prefix in _OG_IMAGE_BLOCKLIST_PATHS:
        if path_prefix in lower:
            return True
    # Skip .gif (usually low-quality thumbnails or tracking pixels)
    if lower.endswith(".gif"):
        return True
    # Root-level generic social filenames are site branding, not article art
    if len(segments) <= 2 and filename in _ROOT_SOCIAL_FILENAMES:
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


def _og_image_topical_ok(img_url, headline, topic=""):
    """Mechanical relevance gate for og:image candidates (added 2026-09-20).

    A source page's og:image can depict a different story than the article
    being written — e.g. a live-blog page whose og:image is a cricket photo
    used as the hero for a shooting article (wrong photo went live on the
    Asian Games shooting-silver piece and had to be removed manually).
    Require the image URL's filename to share at least one distinctive
    content word with the headline/topic. Filenames that are pure hashes or
    numeric tokens cannot be judged and are allowed through; a filename with
    recognizable words but zero overlap is rejected — null is better than
    wrong, consistent with the Pexels alt-text gate.
    """
    fname = (img_url or "").rsplit("/", 1)[-1].lower()
    words = re.findall(r"[a-z]{4,}", fname)
    judgeable = [w for w in words if not re.fullmatch(r"[0-9a-f]{10,}|[0-9]{6,}", w)]
    if not judgeable:
        return True  # hash/numeric filename — cannot judge, allow
    headline_words = set(
        re.findall(r"[a-z]{4,}", ((headline or "") + " " + (topic or "")).lower())
    )
    distinctive = headline_words - _COMMONS_STOP
    if not distinctive:
        return True  # all-generic headline, don't over-filter
    for w in judgeable:
        stem = w[:-1] if w.endswith("s") and len(w) > 4 else w
        for d in distinctive:
            dstem = d[:-1] if d.endswith("s") and len(d) > 4 else d
            if stem == dstem or stem.startswith(dstem) or dstem.startswith(stem):
                return True
    return False


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
        result = _safe_run(
            ["curl", "-sS", "--max-time", "60",
             f"{SUPABASE_URL}/rest/v1/p2_signals?topic_id=eq.{topic_id}&image_url=not.is.null&select=image_url,original_url&limit=5",
             "-H", f"apikey: {SUPABASE_KEY}",
             "-H", f"Authorization: Bearer {SUPABASE_KEY}"],
            capture_output=True, text=True, timeout=70
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
        result = _safe_run(
            ["curl", "-sS", "--max-time", "60",
             f"{SUPABASE_URL}/rest/v1/p2_signals?topic_id=eq.{topic_id}&select=original_url&limit=5&order=published_at.desc",
             "-H", f"apikey: {SUPABASE_KEY}",
             "-H", f"Authorization: Bearer {SUPABASE_KEY}"],
            capture_output=True, text=True, timeout=70
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

    Uses pipeline/gnews-decode.py (curl-based; the `googlenewsdecoder` PyPI
    package is unreliable on this box — its API surface moved and its httpx
    client chokes on the box's bracketed IPv6 no_proxy entries).
    """
    if not url or "news.google.com" not in url:
        return url  # Not a Google News URL, return as-is

    try:
        import subprocess
        import sys as _sys
        script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gnews-decode.py")
        proc = subprocess.run(
            [_sys.executable, script, url],
            capture_output=True, text=True, timeout=90,
        )
        for line in proc.stdout.splitlines():
            parts = line.split("\t", 1)
            if len(parts) == 2 and parts[1] and parts[1] != "ERROR" and parts[1].startswith("http"):
                return parts[1]
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
        encoded_name = urllib.parse.quote(person_name.lower(), safe='')
        result = _safe_run(
            ["curl", "-sS", "--max-time", "60",
             f"{SUPABASE_URL}/rest/v1/person_images?person_name_lower=eq.{encoded_name}&select=image_url&limit=1",
             "-H", f"apikey: {SUPABASE_KEY}",
             "-H", f"Authorization: Bearer {SUPABASE_KEY}"],
            capture_output=True, text=True, timeout=70
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
        
        # YouTube thumbnail quality (2026-10-11): maxresdefault (1280x720) only.
        # Lower qualities (sddefault 640x480, hqdefault 480x360) fail the 800px
        # hero bar. Never use default.jpg (120x90) or mqdefault.jpg (320x180).
        thumb_url = f"https://img.youtube.com/vi/{vid_id}/maxresdefault.jpg"
        ok, ctype, _ = verify_image_url(thumb_url)  # min_width=800 default
        if ok:
            return thumb_url, title, channel

        return None, None, None
        
    except Exception as e:
        print(f"    ⚠ YouTube thumbnail search error: {e}")
        return None, None, None


# ── Source 3.7: PR Newswire India ─────────────────────────────────────────────
def fetch_prnewswire_image(query):
    """Search PR Newswire India for press releases matching the query and
    return the highest-res press-approved image (mma.prnewswire.com).

    PR Newswire images are distributed for media use, making them copyright-safe
    for news articles. Prefers ?p=original for full resolution.

    Returns image URL or None.
    """
    if not query or len(query) < 3:
        return None
    try:
        import urllib.parse
        encoded = urllib.parse.quote(query)
        search_url = f"https://www.prnewswire.com/in/search/news/?keyword={encoded}"
        result = _safe_run(
            ["curl", "-sSL", "--max-time", "15", "-A", UA, search_url],
            capture_output=True, text=True, timeout=20
        )
        html = result.stdout
        # Find press release links: /in/news-releases/<slug>-<id>.html
        links = re.findall(r'href="(/in/news-releases/[a-z0-9\-]+\-\d+\.html)"', html)
        # Relevance: query words should appear in the release URL slug
        # (prevents e.g. "Bollywood" matching a gym opening that mentions it once)
        _qwords = {w.lower() for w in re.findall(r'[a-zA-Z]{3,}', query)}
        seen = set()
        for link in links:
            if link in seen:
                continue
            seen.add(link)
            slug = link.split("/")[-1].rsplit("-", 1)[0].lower().replace("-", " ")
            if _qwords and not (_qwords & set(slug.split())):
                continue  # query not in release title — skip
            release_url = f"https://www.prnewswire.com{link}"
            r2 = _safe_run(
                ["curl", "-sSL", "--max-time", "15", "-A", UA, release_url],
                capture_output=True, text=True, timeout=20
            )
            # Extract mma.prnewswire.com images, prefer ?p=original
            imgs = re.findall(r'https?://mma\.prnewswire\.com/media/\d+/[^"\'\s\)<>]+', r2.stdout)
            # Dedupe by base URL (strip ?p= params)
            by_base = {}
            for img in imgs:
                base = img.split("?")[0]
                # Skip tiny thumbnails and logos
                if any(x in base.lower() for x in ("logo", "icon", "thumb")):
                    continue
                if base not in by_base:
                    by_base[base] = img
            if by_base:
                # Prefer the ?p=original variant if available, else first found
                for base, img in by_base.items():
                    if "?p=original" in img or img == base:
                        # Use ?p=original for full resolution
                        full = base + "?p=original" if "?" not in img else img
                        print(f"    ✓ PR Newswire image for '{query}'")
                        return full
                # Fallback to first image found
                first = next(iter(by_base.values()))
                print(f"    ✓ PR Newswire image for '{query}'")
                return first
        return None
    except Exception as e:
        print(f"    ⚠ PR Newswire search error: {e}")
        return None


# ── Official-source images (government & company press pages) ────────────────
# Kiran's directive (2026-10-11): "Any government website or company website
# are all public information." For institutional stories (space missions,
# policy announcements, company launches), the official source has the most
# topically accurate and copyright-safe images: US federal government works
# are public domain, PIB images are free for news use, and company press
# images are distributed for media use.
#
# Conservative by design: ONLY domains on the curated allowlist below are
# ever fetched or trusted. Better to miss an image than to pull from a
# sketchy domain. Never used for celebrity/person stories — the entity match
# itself is the gate (person-led headlines match no institutional entity),
# plus an explicit person-headline guard below.

# (keyword, official domain, attribution display name).
# Keyword matched case-insensitively on word boundaries against the
# headline + entities + topic. Longest keyword wins when several match.
_OFFICIAL_SOURCE_MAP = [
    # — US government —
    ("james webb", "nasa.gov", "NASA"),
    ("artemis", "nasa.gov", "NASA"),
    ("nasa", "nasa.gov", "NASA"),
    ("white house", "whitehouse.gov", "The White House"),
    ("whitehouse", "whitehouse.gov", "The White House"),
    ("state department", "state.gov", "U.S. Department of State"),
    ("homeland security", "dhs.gov", "U.S. Department of Homeland Security"),
    ("uscis", "uscis.gov", "USCIS"),
    ("department of housing", "hud.gov", "HUD"),
    ("federal reserve", "federalreserve.gov", "Federal Reserve"),
    ("supreme court", "supremecourt.gov", "U.S. Supreme Court"),
    ("justice department", "justice.gov", "U.S. Department of Justice"),
    ("department of energy", "energy.gov", "U.S. Department of Energy"),
    ("treasury department", "treasury.gov", "U.S. Treasury"),
    ("social security administration", "ssa.gov", "Social Security Administration"),
    ("internal revenue service", "irs.gov", "IRS"),
    # — Indian government —
    ("press information bureau", "pib.gov.in", "PIB"),
    ("gaganyaan", "isro.gov.in", "ISRO"),
    ("chandrayaan", "isro.gov.in", "ISRO"),
    ("isro", "isro.gov.in", "ISRO"),
    ("prime minister's office", "pmindia.gov.in", "PMO India"),
    ("reserve bank of india", "rbi.org.in", "RBI"),
    ("securities and exchange board", "sebi.gov.in", "SEBI"),
    ("ministry of electronics", "meity.gov.in", "MeitY"),
    ("meity", "meity.gov.in", "MeitY"),
    ("income tax department", "incometax.gov.in", "Income Tax Department"),
    ("election commission", "eci.gov.in", "Election Commission of India"),
    ("niti aayog", "niti.gov.in", "NITI Aayog"),
    ("uidai", "uidai.gov.in", "UIDAI"),
    ("aadhaar", "uidai.gov.in", "UIDAI"),
    # — Companies (official press/newsroom pages) —
    ("reliance industries", "relianceindustries.com", "Reliance Industries"),
    ("reliance", "relianceindustries.com", "Reliance Industries"),
    ("tata consultancy", "tcs.com", "TCS"),
    ("infosys", "infosys.com", "Infosys"),
    ("wipro", "wipro.com", "Wipro"),
    ("hcltech", "hcltech.com", "HCLTech"),
    ("adani", "adani.com", "Adani Group"),
    ("air india", "airindia.com", "Air India"),
    ("indigo", "goindigo.in", "IndiGo"),
    ("tata", "tata.com", "Tata"),
    ("jio", "jio.com", "Jio"),
    ("apple", "apple.com", "Apple"),
    ("google", "blog.google", "Google"),
    ("alphabet", "blog.google", "Google"),
    ("microsoft", "microsoft.com", "Microsoft"),
    ("openai", "openai.com", "OpenAI"),
    ("nvidia", "nvidia.com", "NVIDIA"),
    ("tesla", "tesla.com", "Tesla"),
    ("spacex", "spacex.com", "SpaceX"),
    ("samsung", "samsung.com", "Samsung"),
    ("amazon", "aboutamazon.com", "Amazon"),
    ("meta", "about.fb.com", "Meta"),
    ("zomato", "zomato.com", "Zomato"),
    # — short acronyms last (word-boundary matched, lowest priority) —
    ("pib", "pib.gov.in", "PIB"),
    ("rbi", "rbi.org.in", "RBI"),
    ("sebi", "sebi.gov.in", "SEBI"),
    ("pmo", "pmindia.gov.in", "PMO India"),
    ("irs", "irs.gov", "IRS"),
    ("hud", "hud.gov", "HUD"),
    ("doj", "justice.gov", "U.S. Department of Justice"),
    ("dhs", "dhs.gov", "U.S. Department of Homeland Security"),
    ("cdc", "cdc.gov", "CDC"),
    ("nih", "nih.gov", "NIH"),
    ("fda", "fda.gov", "FDA"),
    ("faa", "faa.gov", "FAA"),
    ("fcc", "fcc.gov", "FCC"),
    ("epa", "epa.gov", "EPA"),
    ("noaa", "noaa.gov", "NOAA"),
    ("usgs", "usgs.gov", "USGS"),
    ("tcs", "tcs.com", "TCS"),
]

_OFFICIAL_CACHE_PATH = os.path.join(SCRIPT_DIR, ".state", "official-image-cache.json")
_OFFICIAL_CACHE_TTL_SECS = 7 * 24 * 3600

# Domain → display name for writer-provided URLs (derived from _OFFICIAL_SOURCE_MAP)
_OFFICIAL_DOMAIN_NAMES = {}
for _kw, _dom, _disp in _OFFICIAL_SOURCE_MAP:
    _OFFICIAL_DOMAIN_NAMES.setdefault(_dom, _disp)

# ── Brand-first image sourcing (2026-10-11, Kiran's directive) ──────────────
# When an article is about a COMPANY or BRAND (not a person), the brand's own
# website has professional product/brand photography that's on-brand and
# copyright-safe for news use. This beats amateur Commons uploads every time.
# (brand keyword, official domain, attribution display name)
_BRAND_DOMAIN_MAP = [
    ("mother's recipe", "mothersrecipe.com", "Mother's Recipe"),
    ("mothers recipe", "mothersrecipe.com", "Mother's Recipe"),
    ("tata", "tata.com", "Tata"),
    ("reliance", "ril.com", "Reliance Industries"),
    ("jio", "jio.com", "Jio"),
    ("infosys", "infosys.com", "Infosys"),
    ("tcs", "tcs.com", "TCS"),
    ("wipro", "wipro.com", "Wipro"),
    ("hcl", "hcltech.com", "HCLTech"),
    ("zomato", "zomato.com", "Zomato"),
    ("swiggy", "swiggy.com", "Swiggy"),
    ("flipkart", "flipkart.com", "Flipkart"),
    ("ola", "olacabs.com", "Ola"),
    ("paytm", "paytm.com", "Paytm"),
    ("phonepe", "phonepe.com", "PhonePe"),
    ("byju", "byjus.com", "BYJU'S"),
    ("boat", "boat-lifestyle.com", "boAt"),
    ("noise", "gonoise.com", "Noise"),
    ("titan", "titan.co.in", "Titan"),
    ("asian paints", "asianpaints.com", "Asian Paints"),
    ("dabur", "dabur.com", "Dabur"),
    ("patanjali", "patanjaliayurved.net", "Patanjali"),
    ("haldiram", "haldirams.com", "Haldiram's"),
    ("amul", "amul.com", "Amul"),
    ("britannia", "britannia.co.in", "Britannia"),
    ("parle", "parleproducts.com", "Parle"),
    ("marico", "marico.com", "Marico"),
    ("godrej", "godrej.com", "Godrej"),
    ("mahindra", "mahindra.com", "Mahindra"),
    ("bajaj", "bajajauto.com", "Bajaj"),
    ("hero motocorp", "heromotocorp.com", "Hero MotoCorp"),
    ("air india", "airindia.com", "Air India"),
    ("indigo", "goindigo.in", "IndiGo"),
]


def _match_brand(headline, entities=None):
    """Match a brand/company name in headline/entities to its official domain.
    Returns (domain, display_name) or (None, None).
    Skips person-led headlines — brands only, never people."""
    text = (headline or "").lower()
    if entities:
        text += " " + " ".join(str(e).lower() for e in entities if e)
    best = None
    best_len = 0
    for keyword, domain, display in _BRAND_DOMAIN_MAP:
        # Word-boundary match
        if re.search(r"\b" + re.escape(keyword) + r"\b", text):
            if len(keyword) > best_len:
                best = (domain, display)
                best_len = len(keyword)
    return best or (None, None)


def fetch_brand_image(headline, entities=None):
    """Fetch a professional brand/product image from the company's official site.

    For brand/company stories, the official site has professional photography
    that's on-brand and copyright-safe. Tries the brand's homepage and product
    pages for og:image, with logo rejection via the existing guard.

    Returns (image_url, attribution) or (None, None)."""
    domain, display = _match_brand(headline, entities)
    if not domain:
        return None, None
    print(f"    🏷️ brand-first: trying {domain} for '{display}'")
    # Try homepage og:image first, then fall back to a site search
    for url in (f"https://www.{domain}/", f"https://{domain}/"):
        img = fetch_og_image(url)
        if img and not _is_generic_og_image(img):
            ok, _, _ = verify_image_url(img)
            if ok:
                print(f"    ✓ brand image from {display}")
                return img, display
    print(f"    ⊘ brand site yielded no usable image")
    return None, None


def _official_cache_load():
    try:
        with open(_OFFICIAL_CACHE_PATH) as f:
            return json.load(f)
    except Exception:
        return {}


def _official_cache_save(cache):
    try:
        os.makedirs(os.path.dirname(_OFFICIAL_CACHE_PATH), exist_ok=True)
        with open(_OFFICIAL_CACHE_PATH, "w") as f:
            json.dump(cache, f)
    except Exception as e:
        print(f"    ⚠ official-image cache write failed: {e}")


def _match_official_entity(headline, entities, topic=""):
    """Match an institutional entity (agency/company/program) in the article.

    Returns (domain, display_name) or None. Longest keyword wins.
    Person-led headlines ("Shai Hope's century...") match no institutional
    entity and are naturally excluded; an explicit guard below also skips
    when the headline names a person but the institution appears only in
    the entities list (likely a person-centric story).
    """
    combined = " ".join([
        headline or "",
        topic or "",
        " ".join(e for e in (entities or []) if isinstance(e, str)),
    ]).lower()
    headline_l = (headline or "").lower()
    best = None
    best_len = 0
    for keyword, domain, display in _OFFICIAL_SOURCE_MAP:
        if re.search(r"\b" + re.escape(keyword) + r"\b", combined):
            if len(keyword) > best_len:
                best = (domain, display, keyword)
                best_len = len(keyword)
    if not best:
        return None
    domain, display, keyword = best
    # Person-headline guard: if the headline leads with a named person and the
    # institutional keyword does NOT appear in the headline itself, this is a
    # person-centric story — do not source an institutional image for it.
    person = headline_person_name(headline)
    if person and not re.search(r"\b" + re.escape(keyword) + r"\b", headline_l):
        print(f"    ⊘ official-source skipped: person-led headline ('{person}')")
        return None
    return domain, display


def _bing_site_search(domain, query, max_results=8):
    """Site-restricted web search via Bing RSS (no API key, works via curl).

    Returns official-domain article URLs only — anything off-domain is
    dropped, as are generic section fronts (domain root, bare query URLs).
    """
    # Generic section-front paths that never carry a story-specific og:image
    _SKIP_PATHS = {"/", "/index.html", "/index.htm", "/home", ""}
    try:
        q = urllib.parse.quote(f"site:{domain} {query}")
        url = f"https://www.bing.com/search?q={q}&format=rss"
        result = _safe_run(
            ["curl", "-sSL", "--max-time", "15",
             "-A", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
             url],
            capture_output=True, text=True, timeout=20,
        )
        html = result.stdout or ""
        links = re.findall(r"<link>(https?://[^<]+)</link>", html)
        out = []
        for link in links:
            try:
                parsed = urllib.parse.urlparse(link)
                netloc = parsed.netloc.lower().replace("www.", "")
            except Exception:
                continue
            # Strict domain allowlist: exact domain or its subdomain only
            if not (netloc == domain or netloc.endswith("." + domain)):
                continue
            # Skip generic fronts — we want story-specific pages. A query
            # string on the homepage (?m=0 etc.) doesn't make it a story.
            if parsed.path.rstrip("/") in _SKIP_PATHS:
                continue
            if link not in out:
                out.append(link)
            if len(out) >= max_results:
                break
        return out
    except Exception as e:
        print(f"    ⚠ official-source search error: {e}")
        return []


_NASA_IMAGE_API_LOGOS = ("logo", "patch", "emblem", "insignia", "seal", "flag")


def _fetch_nasa_image_api(query):
    """Search NASA's public image library API (images-api.nasa.gov).

    No API key needed. US federal works are public domain — always
    copyright-safe. Skips logos/patches/emblems; returns the ~large.jpg
    variant (hero-appropriate size; ~orig is often 20MB+).

    The API AND-matches every query term, so news verbs ("delays",
    "announces") yield zero hits. Retry with progressively shorter
    queries (dropping leading words) until something hits.
    Returns (image_url, "NASA") or (None, None).
    """
    if not query:
        return None, None
    words = query.split()
    # Try full query, then progressively shorter (drop leading words first —
    # the entity name and news verbs sit at the front)
    attempts = [" ".join(words[i:]) for i in range(len(words))]
    # Dedupe, keep order, require at least 1 word
    seen, queries = set(), []
    for a in attempts:
        if a and a not in seen:
            seen.add(a)
            queries.append(a)
    for q in queries[:4]:
        try:
            encoded = urllib.parse.quote(q)
            url = (f"https://images-api.nasa.gov/search?q={encoded}"
                   f"&media_type=image&page_size=20")
            result = _safe_run(
                ["curl", "-sSL", "--max-time", "15", "-A", UA, url],
                capture_output=True, text=True, timeout=20,
            )
            data = json.loads(result.stdout or "{}")
            items = data.get("collection", {}).get("items", [])
            for it in items:
                meta = (it.get("data") or [{}])[0]
                title = (meta.get("title") or "").lower()
                nasa_id = meta.get("nasa_id", "")
                if not nasa_id:
                    continue
                if any(x in title for x in _NASA_IMAGE_API_LOGOS):
                    continue
                img_url = (f"https://images-assets.nasa.gov/image/"
                           f"{nasa_id}/{nasa_id}~large.jpg")
                ok, ctype, _ = verify_image_url(img_url)
                if ok:
                    print(f"    ✓ NASA image library: \"{meta.get('title', '')[:55]}\"")
                    return img_url, "NASA"
            # No usable image in this attempt's results — try shorter query
        except Exception as e:
            print(f"    ⚠ NASA image API error: {e}")
            return None, None
    return None, None


def fetch_official_source_image(headline, entities=None, topic="", official_url=None):
    """Fetch a press/official image from a government or company website.

    Two modes:
    1. Writer-provided URL (official_url): fetch og:image directly from that
       page — no search needed. This is the reliable path.
    2. Auto-discovery: match institutional entity → site:-restricted search
       on the official domain → extract og:image → validate.

    Returns (image_url, attribution_display_name) or (None, None).
    Results (including misses) are cached for 7 days.
    """
    # ── Mode 1: Writer provided the official URL directly ──
    # This is the reliable path — no search, just fetch and validate.
    if official_url:
        print(f"    🔗 official-source: writer-provided URL {official_url[:60]}")
        img_url = fetch_og_image(official_url)
        if img_url:
            if _is_generic_og_image(img_url):
                print(f"    ⊘ official og:image is generic/logo, skipping")
            elif not _og_image_topical_ok(img_url, headline, topic):
                print(f"    ⊘ official og:image failed topical gate, skipping")
            else:
                ok, ctype, _ = verify_image_url(img_url)
                if ok:
                    # Derive attribution from domain
                    domain = urllib.parse.urlparse(official_url).netloc.replace("www.", "")
                    display = _OFFICIAL_DOMAIN_NAMES.get(domain, domain)
                    print(f"    ✓ official-source image from {display}")
                    return img_url, display
                print(f"    ✗ official-source image FAILED verification")
        # Writer URL didn't yield — fall through to auto-discovery
        print(f"    ⊘ writer URL yielded nothing, trying auto-discovery")

    if not headline:
        return None, None
    match = _match_official_entity(headline, entities, topic)
    if not match:
        return None, None
    domain, display = match

    # Distinctive query words from the headline (entity keyword kept in —
    # it focuses the site: search on the right announcement). Take up to 10
    # so topical nouns late in long headlines ("...for NASA Telescope That
    # Will Hunt for Life" → "telescope") are not cut off.
    words = re.findall(r"[a-z]{4,}", (headline or "").lower())
    seen_q, qwords = set(), []
    for w in words:
        if w not in _COMMONS_STOP and w not in seen_q:
            seen_q.add(w)
            qwords.append(w)
        if len(qwords) >= 10:
            break
    query = " ".join(qwords) if qwords else (topic or headline)[:60]
    cache_key = f"{domain}::{query}"

    cache = _official_cache_load()
    now = time.time()
    if cache_key in cache:
        entry = cache[cache_key]
        if now - entry.get("ts", 0) < _OFFICIAL_CACHE_TTL_SECS:
            print(f"    ✓ official-source cache hit ({display})")
            return entry.get("url"), entry.get("attribution")

    print(f"    🔎 official-source: searching {domain} for '{query[:50]}'")
    # NASA gets its dedicated public image API first — far more reliable
    # than web search for space imagery (public domain, always safe).
    # The API AND-matches every term, so feed it specific nouns, not news
    # verbs: use the longest distinctive words (specific nouns like
    # "telescope", "artemis" beat leading verbs like "delays").
    if domain == "nasa.gov":
        by_len = sorted(qwords, key=len, reverse=True)
        # Exclude the entity keyword itself when it's the longest (e.g.
        # "nasa") — it adds no specificity to a nasa.gov-scoped query.
        api_words = [w for w in by_len if w != qwords[0]][:3] or qwords[:3]
        nasa_query = " ".join(api_words)
        nasa_url, _ = _fetch_nasa_image_api(nasa_query)
        if nasa_url:
            cache[cache_key] = {"url": nasa_url, "attribution": display,
                                "ts": now}
            _official_cache_save(cache)
            return nasa_url, display
        print(f"    ⊘ NASA image API found nothing, falling back to site search")
    # Two passes: (1) news angle with full distinctive keywords,
    # (2) program angle with just the entity + main topic noun — official
    # program/mission pages carry the best topical images and Bing ranks
    # them reliably, while specific press releases come and go.
    seen_pages = set()
    page_urls = []
    topic_noun = qwords[1] if len(qwords) > 1 else ""
    queries = [query]
    if topic_noun and topic_noun != qwords[0]:
        queries.append(f"{qwords[0]} {topic_noun}")
    for q in queries:
        for page_url in _bing_site_search(domain, q):
            if page_url not in seen_pages:
                seen_pages.add(page_url)
                page_urls.append(page_url)
    for page_url in page_urls[:8]:
        img_url = fetch_og_image(page_url)
        if not img_url:
            continue
        if _is_generic_og_image(img_url):
            print(f"    ⊘ official og:image is generic/logo, skipping")
            continue
        if not _og_image_topical_ok(img_url, headline, topic):
            print(f"    ⊘ official og:image failed topical gate, skipping")
            continue
        ok, ctype, _ = verify_image_url(img_url)
        if ok:
            print(f"    ✓ official-source image from {display} ({page_url[:60]})")
            cache[cache_key] = {"url": img_url, "attribution": display, "ts": now}
            _official_cache_save(cache)
            return img_url, display
        print(f"    ✗ official-source image FAILED verification")
    # Cache the miss so we don't re-search every run
    cache[cache_key] = {"url": None, "attribution": None, "ts": now}
    _official_cache_save(cache)
    return None, None


def fetch_wikipedia_image(entity_name, article_context=None, article_headline=None):
    """Fetch image from Wikipedia REST API for a person/entity.
    Returns image URL or None.
    
    If article_context (headline or body snippet) is provided, validates that
    the Wikipedia page is relevant — not a disambiguation page, generic concept,
    or landmark only geographically related to the article.
    article_headline, if provided, is checked for place/landmark entities —
    the article must be *about* the place, not just mentioning it.
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
        img_info = data.get("originalimage") or data.get("thumbnail") or {}
        img = img_info.get("source")
        if not img:
            return None

        # ── Minimum resolution guard ──
        # Reject tiny thumbnails (e.g., 283px fair-use posters) — they'd look
        # pixelated as hero images. 800px wide is the minimum (2026-10-11 bar).
        _w = img_info.get("width") or 0
        if _w and _w < 800:
            print(f"    ⊘ Skipping Wikipedia image for '{entity_name}' — "
                  f"too small ({_w}px wide, minimum 600px)")
            return None

        # ── Filename-vs-entity cross-check ──
        # Wikipedia sometimes returns a page with a photo of the wrong
        # person (e.g., search "Devendra Nath Mahto" → file Sanjay_Seth.jpg).
        # Split camelCase too ("RanveerBrar.jpg" → ranveer + brar) so legit
        # single-token filenames aren't falsely rejected.
        _fname_raw = os.path.basename(img.split("?")[0]).rsplit(".", 1)[0].replace("_", " ")
        _fname_raw = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", _fname_raw)
        _ent_parts = {w.lower() for w in entity_name.split() if len(w) > 2}
        _fname_name_parts = {w.lower() for w in _fname_raw.split()
                             if len(w) > 2 and w[0].isupper()}
        if _fname_name_parts and not (_fname_name_parts & _ent_parts):
            print(f"    ⊘ Skipping Wikipedia image for '{entity_name}' — "
                  f"filename '{_fname_raw}' looks like a different entity")
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
            "prize", "medal", "honour", "honor",
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
            "university", "college", "institute", "school",
            "airline", "railway", "railroad",
        }
        if article_context and any(kw in wiki_desc for kw in _PLACE_KW):
            # For place/landmark entities, check the HEADLINE not just body text.
            # A person's name matching a landmark (e.g., "Margherita Fontana")
            # shouldn't pull a fountain photo into an unrelated article.
            check_text = (article_headline or article_context or "").lower()
            if entity_name.lower() not in check_text:
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

# Venue kinds that make a Commons photo depict a specific identifiable business.
# A photo titled e.g. "Indian Taj restaurant" shows THAT restaurant — it must not
# illustrate an article about a different venue/location.
_VENUE_KINDS = {
    "restaurant", "restaurants", "cafe", "café", "cafes", "dhaba", "eatery",
    "hotel", "hotels", "bar", "bars", "pub", "pubs", "mall", "malls",
    "market", "markets", "stadium", "stadiums", "arena", "museum",
    "theatre", "theater", "temple", "airport", "station", "school",
    "college", "hospital", "resort", "cinema", "gallery", "club",
}

def _commons_venue_name(commons_title):
    """Extract the proper-noun venue name preceding a venue word.

    "Eksteriør Indian Taj restaurant" -> "Indian Taj". Returns None when the
    title has no venue word with a preceding proper noun (e.g. generic
    "Restaurant interior" or non-venue photos like "Newlands2").
    """
    # All words (any case) for venue-word detection; proper-noun name is taken
    # from capitalized words preceding the venue word.
    words = re.findall(r"[A-Za-zÀ-Þà-öø-ÿ]+", commons_title or "")
    for i, w in enumerate(words):
        if w.lower() in _VENUE_KINDS and i > 0:
            name = [x for x in words[max(0, i - 2):i] if x[0].isupper()]
            if name:
                return " ".join(name)
    return None


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
    
    # Venue-specificity guard (2026-10-11): a Commons photo of a specific named
    # venue (e.g. "Eksteriør Indian Taj restaurant", a Danish restaurant) must
    # not illustrate an article about a different venue/location (e.g.
    # "Sai Kung's Top Indian Restaurant ..."). If the title names a venue whose
    # proper nouns don't appear in the headline, reject outright.
    venue_name = _commons_venue_name(commons_title)
    if venue_name:
        name_words = set(re.findall(r"[a-zà-öø-ÿ]{3,}", venue_name.lower())) - _COMMONS_STOP
        if name_words and not any(w in headline_l for w in name_words):
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

_PEXELS_QUERY_STOPWORDS = {
    "the", "a", "an", "and", "for", "with", "from", "about", "what", "how",
    "why", "when", "new", "top", "best", "his", "her", "their", "its",
    "this", "that", "these", "those", "are", "was", "were", "has", "have",
    "had", "will", "would", "could", "should", "into", "over", "under",
    "after", "before", "says", "said",
}


def _pexels_alt_matches(query, alt):
    """Mechanical relevance gate for Pexels results.

    Pexels' fuzzy search returns plausible-looking but unrelated stock for
    specific queries (person names, film titles — e.g. an unrelated stock
    photo for 'Main Na Raha Mera'). Require the photo's alt text to share
    content words with the query; otherwise return no image (null > wrong)
    so the article publishes hero-less instead of with a wrong photo.

    Two hardening layers (2026-09-20):
    1. Token matching, not substring: query word "state" must not match the
       alt token "states". Stemming is applied to the QUERY word only (so
       "airports" still matches alt token "airport"), never to alt tokens.
    2. Multi-word queries need >= 2 distinct content-word matches. A single
       generic word match (e.g. "department" on a USDA building photo for a
       "State Department" query) caused a wrong-image pick.
    """
    if not alt or not query:
        return False
    q_words = {
        w for w in re.findall(r"[a-z]+", query.lower())
        if len(w) > 3 and w not in _PEXELS_QUERY_STOPWORDS
    }
    if not q_words:
        return False
    alt_tokens = {w for w in re.findall(r"[a-z]+", alt.lower()) if len(w) > 2}

    def _stem(w):
        # light plural stemming so "trains" matches "train"
        return w[:-1] if w.endswith("s") and len(w) > 4 else w

    hits = {_stem(w) for w in q_words} & alt_tokens
    if len(q_words) == 1:
        return bool(hits)
    return len(hits) >= 2


def fetch_pexels_image(query):
    """Search Pexels for a topical image. Returns (url, alt) or (None, None).

    Only returns a photo whose alt text passes the relevance gate
    (_pexels_alt_matches); irrelevant fuzzy matches are rejected so the
    article falls through to hero-less rather than a wrong image.

    The alt text is returned alongside the URL because it describes what the
    photo ACTUALLY shows — the hero caption is built from it, never from a
    description written before the image was sourced (2026-10-11: a caption
    for an imagined 'restaurant dining room' survived a backfill that
    sourced a Hong Kong skyline, and the mismatch went live).
    """
    if not PEXELS_KEY or not query:
        return None, None

    encoded = urllib.parse.quote(query)
    url = f"https://api.pexels.com/v1/search?query={encoded}&per_page=5&orientation=landscape"

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
            if img_url and _pexels_alt_matches(query, photo.get("alt", "")):
                return img_url, photo.get("alt", "")
        return None, None
    except:
        return None, None


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

# ── Identity guard (2026-09-16) ─────────────────────────────────────────────
# Never put a Pexels/generic stock photo on a named-person article —
# wrong photo is worse than no photo. Before the Pexels fallback,
# check whether the headline names a verifiable person; if Wikipedia
# has their photo, use it instead of stock; if the person can't be
# verified, leave the article imageless.
_HEADLINE_TITLE_WORDS = {
    "expert", "experts", "vendor", "vendors", "minister", "ministers",
    "official", "officials", "doctor", "doctors", "study", "studies",
    "report", "reports", "court", "courts", "police", "army", "government",
    "team", "teams", "party", "parties", "panel", "panels", "committee",
    "committees", "board", "boards", "bank", "banks",
    "company", "companies", "group", "groups", "school", "schools",
    "university", "universities", "hospital", "hospitals",
    "institute", "institutes",
    "center", "centres", "centre", "festival", "festivals", "award", "awards",
    "cup", "cups", "league", "leagues",
    "tournament", "tournaments", "championship", "championships",
    # Headline plurals are common org subjects ("Radiology Groups Join...",
    # "Banks Post...", "Universities Sue...") — the singular-only list let
    # "Radiology Groups" through as a person's name and blocked the Pexels
    # fallback (2026-10-05; same class as the "No Handshake" fix)
    # Economy/finance nouns: two-word phrases like "Mortgage Rates", "Gas Prices",
    # "Bond Market" are never a person's name (2026-09-21 health check found
    # "Mortgage Rates" misdetected, which blocked Pexels fallback entirely)
    "rate", "rates", "price", "prices", "market", "markets", "stock", "stocks",
    "bond", "bonds", "fund", "funds", "oil", "gas", "growth", "inflation",
    "deficit", "surplus", "trade", "economy", "revenue", "profits", "earnings",
    "cost", "costs", "demand", "supply", "housing", "mortgage", "tax", "taxes",
}
_HEADLINE_PREFIX_WORDS = {
    "pm", "cm", "dr", "shri", "smt", "lt", "gen", "mr", "mrs", "ms",
    "india", "indian", "us", "uk", "supreme", "high", "federal",
    "breaking", "exclusive", "watch", "live",
    # Org/economic acronyms that lead headlines but are never a person's name
    # ("Fed Delivers...", "RBI Cuts...", "ECB Holds...") — case-insensitive match
    "fed", "rbi", "ecb", "imf", "wto",
    # Indian scheme/program names commonly leading headlines — not people
    "aadhaar", "nris", "nri",
    # Indian city names leading headlines ("Delhi Destroys...") — a city is
    # never a person's given name. Common verb-second-word headlines like
    # "Delhi Cracks Down" / "Mumbai Rains" false-positive the person guard.
    "delhi", "mumbai", "bengaluru", "bangalore", "hyderabad", "chennai",
    "kolkata", "pune", "ahmedabad", "jaipur", "lucknow", "surat", "kanpur",
    "nagpur", "indore", "thane", "bhopal", "patna", "vadodara", "ghaziabad",
    "ludhiana", "agra", "nashik", "faridabad", "meerut", "rajkot", "varanasi",
    "srinagar", "amritsar", "allahabad", "prayagraj", "ranchi", "howrah",
    "coimbatore", "jabalpur", "gwalior", "vijayawada", "jodhpur", "madurai",
    "raipur", "kota", "guwahati", "chandigarh", "mysuru", "mysore",
    "gurgaon", "gurugram", "noida",
    # US city names leading headlines — a city is never a person's given
    # name (2026-10-09: "Plano's Jashan Becomes..." was misread as a person
    # named "Plano Jashan", blocking Pexels on a food headline)
    "plano", "dallas", "houston", "austin", "seattle", "chicago", "atlanta",
    # Indian state names leading headlines — never a person's given name
    "kerala", "punjab", "tamil", "tamilnadu", "karnataka", "maharashtra",
    "gujarat", "rajasthan", "bihar", "bengal", "assam", "odisha", "goa",
    "telangana", "haryana", "kashmir", "ladakh",
    # Rank/title words that lead headlines — never a given name
    # ("Air Marshal Arjan Singh...", "Air India Adds...") — cf. "Dr", "Lt" above
    "air",
    # Country names leading headlines ("Nepal Ends Flood Search...",
    # "China Launches...") — a country is never a person's given name.
    # Ambiguous ones that ARE also given names (israel, jordan, chad,
    # georgia) are deliberately excluded — a false negative there keeps the
    # conservative identity-safe behavior.
    "nepal", "pakistan", "bangladesh", "china", "japan", "korea",
    "australia", "canada", "france", "germany", "russia", "ukraine",
    "iran", "saudi", "qatar", "singapore", "malaysia", "thailand",
    "vietnam", "indonesia", "philippines", "afghanistan", "myanmar",
    "bhutan", "maldives", "srilanka", "turkey", "italy", "spain",
    "brazil", "mexico", "egypt", "kenya", "nigeria", "argentina",
    "colombia", "netherlands", "switzerland", "sweden", "norway",
    "peru", "cuba", "oman", "mali", "uae",
}
# Prepositions / interrogatives / conjunctions as first word: a person's
# given name can never be "After", "Across", "Why", "While" ...
# ("After Years in America...", "Across Punjab, farmers..."). Safe because
# proper names don't start with these words. Note: months ("March", "May")
# and common-noun names ("Bill", "Rose", "Mark") are deliberately NOT here.
_HEADLINE_NONNAME_FIRST_WORDS = {
    "after", "before", "across", "amid", "among", "around", "between",
    "beyond", "during", "under", "over", "through", "toward", "towards",
    "without", "within", "despite", "against", "along", "upon", "until",
    "versus", "via", "inside", "beneath", "beside", "behind", "below",
    "above", "how", "why", "when", "what", "where", "which", "while",
    "since", "amongst", "and", "but", "or", "nor", "as", "of", "to",
    "in", "on", "at", "by", "for", "from",
    # Negation as first word: a person's given name can never be "No"
    # ("No Handshake, No Trophy...") — fixes false-positive person guard
    "no", "not",
    # Adverb leads that are never a given name ("Still LA's Best Biryani...")
    # — fixes false-positive person guard that blocked Pexels for a food
    # headline
    "still",
    # Number words as first word: a given name is never a number
    # ("Five Visa Application Mistakes...", "Ten Ways to...") — a count of
    # people, not a person's name; fixes false-positive person guard
    "one", "two", "three", "four", "five", "six", "seven", "eight",
    "nine", "ten", "eleven", "twelve", "dozen", "first", "second", "third",
    "fifth",
    # Common adjective leads that are never a given name
    # ("New Study Finds...", "Global Markets Rally..." — fixes false-positive
    # person guard that blocked Pexels for clearly non-person headlines)
    "new", "global",
    # Descriptive adjectives that are never given names ("Electric Blue Waves..."
    # was misread as person "Electric Blue", blocking image sourcing)
    "electric", "blue", "red", "green", "golden", "dark", "bright",
}
# Collective-noun leads that are never a person's given name
# ("Fans Mourn...", "Students Protest...", "Workers Strike...") — a person's
# name is never a plural collective. Applied to the headline's first word.
_HEADLINE_COLLECTIVE_WORDS = {
    "fans", "workers", "students", "travelers", "travellers", "passengers",
    "voters", "residents", "customers", "employees", "nurses", "teachers",
    "farmers", "migrants", "immigrants", "expats", "pilgrims", "devotees",
    "tourists", "airports", "startups", "agencies", "associations",
    "unions", "colleges", "institutions", "airlines", "retailers",
    # Nationality plurals — never a person's given name (2026-10-07:
    # "Americans' One-Year Inflation..." was misread as a named person,
    # blocking Pexels backfill on a generic markets headline)
    "americans", "indians", "nris", "europeans", "asians", "canadians",
    "australians", "britons", "russians", "ukrainians", "israelis",
    "palestinians", "chinese", "japanese", "koreans", "mexicans",
    # 2026-10-12: "Witnesses Say Tiger Victim Posed for Photos..." was read as
    # a person named "Witnesses Say", blocking Pexels on a generic news
    # headline. A witness is a collective/plural noun, never a given name.
    "witnesses",
    # 2026-10-19 audit: crowd plurals from the Manipur ambush headline
    # ("...Firewood Collectors Ambushed, Protesters Reach CM's Gate") —
    # same class as "witnesses": a crowd is never a given name.
    "protesters", "demonstrators", "onlookers", "bystanders", "mourners",
    "collectors",
}
# First-word org nouns that can never be a person's given name. Reuses the
# title-word list (minus bank/banks) because a headline starting with an
# org/collective noun ("Universities Sue...", "Doctors Warn...", "Companies
# Hire...") is never about a person named that. bank/banks excluded:
# Banks is a real surname/stage name (the singer BANKS) — the one ambiguous
# word keeps the conservative (identity-safe) behavior.
_HEADLINE_FIRST_ORG_WORDS = _HEADLINE_TITLE_WORDS - {"bank", "banks"}
# Well-known proper nouns (public companies, US states) that are effectively
# never a person's given name as a headline lead ("Nvidia Nears..." is the
# company; "Pennsylvania Measles..." is the state — not a person named
# Pennsylvania) — fixes false-positive person guards that blocked Pexels for
# markets and news headlines (2026-10-07). Kept tight: ambiguous words
# ("apple", "meta", "tesla", "georgia", "virginia") stay out, preserving
# conservative identity-safe behavior for anything that could be a real name.
_HEADLINE_PROPER_NONPERSON_WORDS = {
    "nvidia", "pennsylvania", "google", "chatgpt",
    # 2026-10-07: "ChatGPT's Teen Safety..." — AI product name treated as a
    # person's given name, blocking Pexels on a generic tech article.
    # 2026-10-07: "Flu Arrives Early..." — disease noun treated as a person's
    # given name ("Flu Arrives"), blocking Pexels backfill on a public-health
    # headline. A disease name is effectively never a person's given name.
    "flu",
    # 2026-10-10: "East Bay Upscale Indian Dining Wave Gains Momentum" — the
    # Bay Area region read as a person's name ("East Bay"), blocking Pexels
    # and leaving a food article imageless. "East" is effectively never a
    # person's given name as a headline lead.
    "east",
}
# Possessive place leads: "[Place]'s [Business]" ("Hoover's Kabob-Licious",
# "Hartlepool's Seaton Tandoori") is a place's business, not a person named
# Hoover/Hartlepool. Without this the identity guard blocks Pexels and the
# article goes imageless (2026-10-07: two food articles). Kept tight and
# documented per encounter — the conservative direction (imageless) is safe,
# this just recovers the photo.
_HEADLINE_PLACE_POSSESSIVE_WORDS = {
    "hoover", "hartlepool",
    # 2026-10-12: "King's Lynn Tandoori named England's best curry restaurant
    # ..." was read as a person named "King's Lynn", blocking Pexels on a
    # generic food headline. King's Lynn is an English town — the place owns
    # the business. Only possessive leads are affected; "King Charles ..."
    # (non-possessive) still engages the person guard correctly.
    "king",
}
# Multi-word place phrases that must not be read as a person's name.
# "Sai Kung's Top Indian Restaurant..." is a Hong Kong district, not a person
# named "Sai Kung" (2026-10-11: the guard blocked Pexels and left a food
# article imageless). Checked as a two-word phrase so "Sai" alone is still
# treated as a given name ("Sai Pallavi's Wedding..." stays guarded). Kept
# tight and documented per encounter.
_HEADLINE_PLACE_PHRASE_WORDS = {
    "sai kung",
    # 2026-10-12: "West Indies' Plan B Against Abhishek Sharma Revealed..."
    # was read as a person named "West Indies'", blocking Pexels on a sports
    # headline. The West Indies is the Caribbean region (and cricket team),
    # not a person.
    "west indies",
}
# Determiners / possessives: "Raise Your Sum..." is never a person's name
_HEADLINE_DETERMINER_WORDS = {
    "your", "my", "our", "his", "her", "their", "its",
    "this", "that", "these", "those",
}
# Past-tense / 3rd-person verbs: "Rat Found Swimming...", "Body Found in
# Lake..." — a second-position verb is never a surname. A person's name +
# verb puts the verb third ("Varun Chakravarthy Ruled Out..."). Kept tight
# and documented per encounter (2026-10-08: the rat-in-gulab-jamun article
# was gate-blocked as a "named person" because of the verb-second lead).
_HEADLINE_COMMON_VERB_WORDS = {
    "found", "dies", "die", "rises", "rise", "falls", "fall", "launches",
    "wins", "win", "loses", "lose", "returns", "return", "quits", "quit",
    "resigns", "reveals", "backs", "slams", "warns", "urges", "hails",
    "swims", "swim", "breaks", "break", "drowns", "crashes", "crash",
    "arrested", "jailed", "fined", "cleared", "clears", "suspends",
    "suspend",
    # 3rd-person-singular headline verbs (\"Navratri Begins\", \"Expo Opens\"):
    # a surname never reads like one of these (2026-10-11).
    "begins", "ends", "opens", "closes", "starts", "hits", "tops",
    "faces", "sees", "beats", "celebrates", "debuts", "unveils",
    "announces", "confirms", "extends", "expands", "enters", "crosses",
    "hosts", "eyes", "mulls", "slashes", "hikes", "rolls", "kicks",
    "strikes", "strike",
    # Modal/auxiliary verbs ("Automation Could Shrink...", "Drone Strikes
    # Tanker..." misread as person names 2026-10-11 — left two tech/news
    # articles imageless): no surname reads like one of these.
    "could", "would", "should", "might", "can", "will", "shall",
    # 2026-10-12: "Panama Declares Emergency as 200+ Aftershocks..." was read
    # as a person named "Panama Declares", blocking Pexels on a news headline.
    # Same family as the "announces"/"confirms" 3rd-person verbs above.
    "declares",
    # 2026-10-19 audit: more headline verb FORMS (3rd-person -s / past
    # tense / modals) — a surname never reads like one of these, but the
    # missing forms were passing as surnames: "Sammy Hopes..." (fake
    # surname "Hopes"), "...Kamboj Earns Test Recall", "Google Adopts...",
    # "FSSAI Proposes...", "...Sharma Replaces Bhavina Patel".
    "earns", "hopes", "replaces", "asked", "adopts", "proposes", "puts",
    "requires", "targets", "referred", "sends", "sent", "rams", "finds",
    "seeks", "calls", "tells", "shows", "lands", "picks", "leaves",
    "joins", "meets", "helps", "attract", "attracts", "hires",
    "triggered", "ambushed", "cannot", "triggers", "reach", "reaches",
    # Sports-headline verb forms that follow a name ("...Ruled Out",
    # "...Wins", "...Bags Gold") — these terminate a name run; without
    # them the full-name recovery above would swallow the verb as a
    # third name part. Same for memorial verbs ("Mother Teresa
    # Remembered...").
    "ruled", "named", "picked", "signs", "scores", "takes", "bags",
    "clinches", "seals", "leads", "plays", "won", "lost", "drew",
    "remembered", "mourned", "honoured", "honored", "celebrated",
}
# Storm/weather system leads: "Hurricane Isaias Shuts...", "Tropical Storm
# X...", "Cyclone Y..." — a storm name is not a person's name. The first word
# is never a given name, so the Pexels guard must not engage (2026-10-09:
# "Hurricane Isaias Shuts 72% of Gulf Oil Output" was treated as a person
# and blocked Pexels, leaving a weather article imageless). Kept tight —
# "storm" only as a FIRST word; a mid-headline "storm" is irrelevant.
_HEADLINE_STORM_WORDS = {
    "hurricane", "tropical", "cyclone", "typhoon", "storm",
}
# Nationality / demonym adjectives (incl. language-community adjectives).
# As a headline's FIRST word a demonym is a descriptor modifying the noun
# after it ("British Mother Referred...", "Pakistani Man Jailed...") —
# it is never a person's given name. (2026-10-19 audit: "British Mother"
# passed as a person and kept a story with no named person in it
# imageless.) Ambiguous given names stay out, per the file's convention:
# "georgia"/"jordan"/"chad" are names, their demonyms are not.
_HEADLINE_DEMONYM_WORDS = {
    "american", "british", "canadian", "australian", "mexican", "indian",
    "pakistani", "bangladeshi", "nepali", "lankan", "chinese", "japanese",
    "korean", "russian", "ukrainian", "french", "german", "italian",
    "spanish", "portuguese", "belgian", "swiss", "austrian", "polish",
    "greek", "turkish", "iranian", "iraqi", "israeli", "palestinian",
    "lebanese", "syrian", "jordanian", "egyptian", "libyan", "tunisian",
    "algerian", "moroccan", "sudanese", "ethiopian", "eritrean",
    "somali", "kenyan", "tanzanian", "ugandan", "nigerian", "ghanaian",
    "cameroonian", "senegalese", "malian", "mauritian", "fijian",
    "afghan", "burmese", "thai", "vietnamese", "cambodian", "laotian",
    "indonesian", "malaysian", "singaporean", "filipino", "taiwanese",
    "mongolian", "tibetan", "kazakh", "uzbek", "armenian", "georgian",
    "brazilian", "argentine", "chilean", "peruvian", "colombian",
    "venezuelan", "ecuadorian", "bolivian", "paraguayan", "uruguayan",
    "cuban", "haitian", "jamaican", "dominican", "honduran", "panamanian",
    "african", "asian", "european", "arab", "persian", "kurdish",
    "pashtun", "sindhi", "baloch", "punjabi", "bengali", "gujarati",
    "marathi", "odia", "assamese", "kashmiri", "malayali", "keralite",
    "telugu", "kannada", "bhutanese", "maldivian",
}
# Kinship nouns and role/activity nouns as the SECOND word of a headline
# lead: in "British Mother ..." / "Para Shooter Rakesh Nidagundi ..." the
# second word names the subject's relation or role — the pair is a
# descriptor phrase, not a name (2026-10-19 audit). Singular forms are
# restricted to words that are essentially never surnames ("son" is a
# real surname — Son Heung-min — and stays out; profession surnames like
# Baker/Cook/Player/Singer/Farmer/Driver also stay out); plural role
# nouns are always safe because surnames are singular.
_HEADLINE_ROLE_SECOND_WORDS = {
    # kinship / relation
    "mother", "father", "parents", "husband", "wife", "daughter",
    "brother", "sister", "sibling", "siblings", "family", "widow",
    "widower", "grandmother", "grandfather", "grandma", "grandpa",
    "mom", "dad", "spouse", "couple", "twins", "boyfriend", "girlfriend",
    "bearer",
    # role / activity (singular — never surnames)
    "shooter", "golfer", "swimmer", "wrestler", "influencer", "activist",
    "devotee", "tourist", "visitor", "student", "worker", "shopkeeper",
    "homemaker", "housewife", "jobseeker",
    # role / activity (plural — surnames are singular)
    "workers", "students", "tourists", "visitors", "devotees",
    "shooters", "golfers", "players", "singers", "actors", "farmers",
    "teachers", "lawyers", "nurses", "engineers", "drivers", "riders",
    "dancers", "runners", "boxers", "coaches", "employees", "jobseekers",
    "lawmakers", "legislators", "politicians", "bureaucrats",
}
# Pronouns: a headline leading with a pronoun ("He Asked Followers for
# Diwali Sweets...") is a narrative lead — a pronoun is never a given
# name (2026-10-19 audit: "He Asked" passed as a named person).
_HEADLINE_PRONOUN_WORDS = {
    "he", "she", "it", "they", "we", "you", "i",
    "him", "her", "them", "us",
}


def headline_person_name(headline):
    """Detect a named person at the start of a headline.

    "Ranveer Brar's Tandoori..." → "Ranveer Brar"
    "Varun Chakravarthy Ruled Out..." → "Varun Chakravarthy"
    Returns None for non-person leads ("Ayurveda Expert Shares...",
    "Allahabad Vendor's...", "Supreme Court Rules...").
    """
    if not headline:
        return None
    h = headline.strip()
    # Possessive lead with quoted next word ("Warsh's 'Dose of
    # Accommodation'..."): the two-word regex below can't match a quoted
    # second token, so detect the possessive subject first — it IS the named
    # person. Without this the identity guard never ran and a generic Pexels
    # stock photo went on a named-person article. Prefix/org possessives
    # ("India's", "Fed's") are still excluded below.
    mp = re.match(r"^([A-Z][A-Za-z.'-]*?['’]s)\s+(?=['\"“”‘’])", h)
    if mp:
        subject = re.sub(r"['’]s$", "", mp.group(1))
        base = subject.lower().rstrip(".")
        if base not in _HEADLINE_PREFIX_WORDS and base not in _HEADLINE_NONNAME_FIRST_WORDS:
            return subject
        return None
    m = re.match(r"^([A-Za-z][\w.'-]*)\s+([A-Za-z][\w.'-]*)", h)
    if not m:
        return None
    first, second = m.group(1), m.group(2)
    # Strip possessive suffix for the word-list checks ("India's" → "india",
    # plural possessive "Americans'" → "americans") (2026-10-07)
    first_base = re.sub(r"['’]s$|['’]$", "", first.lower()).rstrip(".")
    if first_base in _HEADLINE_PREFIX_WORDS:
        return None
    # Possessive place + business ("Hoover's Kabob-Licious"): the place owns
    # the business; not a person. Only applies when the possessive is on the
    # FIRST word — "Ranveer Brar's" (possessive on second) is still a person.
    if re.search(r"['’]s$", first) and first_base in _HEADLINE_PLACE_POSSESSIVE_WORDS:
        return None
    # Possessive on the FIRST token at all ("Anthropic's Junior Tech
    # Hires..."): the possessive closes the subject noun phrase at token
    # 1, so tokens 1+2 can never be a two-word person name — a person's
    # possessive rides on the LAST name token ("Ranveer Brar's").
    # Single-token possessive subjects outside the prefix/place lists
    # (companies, brands) slipped through as fake people and engaged the
    # identity guard on non-person stories (2026-10-19 audit).
    if re.search(r"['’]s$", first):
        return None
    # ALL-CAPS short lead words are org/acronyms (IIT, UPI, EPF, NPS, PFRDA),
    # never a person's given name
    if first.isupper() and len(first) <= 5:
        return None
    # Preposition/interrogative leads ("After Years...", "Why India..."):
    # a given name never starts with one
    if first_base in _HEADLINE_NONNAME_FIRST_WORDS:
        return None
    # Demonym / pronoun leads ("British Mother...", "He Asked..."): a
    # nationality adjective or a pronoun in first position is a
    # descriptor or a narrative pronoun, never a given name (2026-10-19)
    if first_base in _HEADLINE_DEMONYM_WORDS or first_base in _HEADLINE_PRONOUN_WORDS:
        return None
    # Org/collective-noun leads ("Universities Sue...", "Doctors Warn...",
    # "Fans Mourn..."): a given name never starts with one
    if first_base in _HEADLINE_FIRST_ORG_WORDS or first_base in _HEADLINE_COLLECTIVE_WORDS:
        return None
    # Public-company / place leads ("Nvidia Nears...", "Pennsylvania Measles..."):
    # a proper noun that is effectively never a person's given name
    if first_base in _HEADLINE_PROPER_NONPERSON_WORDS:
        return None
    # Storm/weather-system leads ("Hurricane Isaias Shuts..."): a storm name
    # is not a person's name — the Pexels guard must not engage (2026-10-09)
    if first_base in _HEADLINE_STORM_WORDS:
        return None
    # Style/descriptor adjectives ("Kolkata-Style Kathi Rolls...", "Delhi-Style
    # Chaat..."): a hyphenated -style/-inspired first word is a cuisine or
    # product descriptor, never a given name — "Kolkata-Style" is not a person.
    # Without this, generic food headlines were gate-blocked as "named person"
    # and stayed imageless (2026-10-11).
    if re.search(r"-(style|inspired|fusion)$", first_base):
        return None
    # Gerund verbs leading the headline ("Replacing Russian...", "Building New...")
    # — a given name never ends in -ing ("Singh" is a surname, handled below)
    if first_base.endswith("ing") and first_base != "singh" and len(first_base) > 4:
        return None
    second_base = re.sub(r"['’]s$", "", second.lower()).rstrip(".")
    if second_base in _HEADLINE_DETERMINER_WORDS:
        return None
    # Verb-second leads ("Rat Found Swimming...") are never a person's name.
    if second_base in _HEADLINE_COMMON_VERB_WORDS:
        return None
    # Ordinal-prefixed hyphenated words ("First-Ever", "Second-Half") are
    # never surnames: "Stanley's First-Ever Diwali Collection..." is a brand
    # possessive, not a named person (2026-10-08).
    if re.match(r"^(first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth)-",
                second_base):
        return None
    # Names don't contain digits ("Delhi H1N1", "10m Air Rifle")
    if any(ch.isdigit() for ch in second):
        return None
    if second_base in _HEADLINE_TITLE_WORDS:
        return None
    # Kinship / role noun as the second word ("British Mother", "Para
    # Shooter"): token 2 names the subject's relation or role, not a
    # surname — the pair is a descriptor phrase, not a name (2026-10-19)
    if second_base in _HEADLINE_ROLE_SECOND_WORDS:
        return None
    # Multi-word place phrases ("Sai Kung's ..."): the district is not a person.
    # Checked on the two-word phrase so "Sai" alone still passes as a given
    # name ("Sai Pallavi's Wedding..."). Kept tight and documented per
    # encounter. Trailing bare possessive ("West Indies'") is normalized so
    # the phrase lookup hits (2026-10-12).
    if f"{first_base} {second_base}".rstrip("’'") in _HEADLINE_PLACE_PHRASE_WORDS:
        return None
    # Both words capitalized, second not a title → likely a person's name.
    # Length gate runs on the possessive-stripped base: "LA's" → "la" (2
    # chars) must not pass as a surname — "Still LA's Best Biryani..." is
    # not a person. Checking len(second) let the 4-char "LA's" through.
    if first[0].isupper() and second[0].isupper() and len(first) > 1 and len(second_base) > 2:
        # Strip possessive: "Ranveer Brar's" → "Ranveer Brar"
        parts = [first, re.sub(r"['’]s$", "", second)]
        # Full-name recovery (2026-10-19 audit): a three-part name was
        # truncated to its first two tokens — "Min Woo Lee Withdraws..."
        # yielded "Min Woo", sending the identity guard's Wikipedia
        # lookup and the profile search after a non-existent person.
        # Consume a following token as a third name part only when it is
        # itself name-shaped: a single capitalized alphabetic word (no
        # hyphen/digit — "Agarwal's Fold-Flat Spoon" must not extend)
        # belonging to none of the non-name word classes (headline verbs
        # end name runs: "...Sutar Hits", "...Kamboj Earns"). Skipped
        # when token 2 carried the possessive: "'s" closes the name
        # phrase, so what follows is a new noun phrase, never a name
        # part ("Ranveer Brar's Tandoori..." stays "Ranveer Brar").
        tm = None
        if not re.search(r"['’]s$", second):
            tm = re.match(r"\s+([A-Za-z][\w.'-]*)", h[m.end():])
        if tm:
            third = re.sub(r"['’]s$", "", tm.group(1)).rstrip(".")
            if (re.fullmatch(r"[A-Za-z]+", third)
                    and len(third) > 1
                    and not (tm.group(1).isupper() and len(tm.group(1)) <= 5)
                    and third.lower() not in _NAME_PART_REJECT_WORDS):
                parts.append(third)
        return " ".join(parts)
    return None


# ── Source 3.8: Person profile (subject's own institutional profile) ─────────
# Added 2026-10-17 after the Ramya Anche failure: her article and reel shipped
# with a generic NASA HQ building photo from the Wikipedia fallback because
# the chain had no step for the named person's OWN institutional profile
# photo. Her verified portrait was on her Steward Observatory profile page
# (astro.arizona.edu/person/ramya-anche, img alt exactly "Ramya Anche",
# 3024×4032) the whole time — no step ever looked there.
#
# This step runs BEFORE Wikipedia for named-person articles. It finds the
# subject's official profile page (university/faculty profile, agency or
# company bio, team/org profile) and accepts ONLY a portrait whose alt
# text (or figcaption) EXACTLY matches the person's name (normalized; a
# trailing credential suffix like ", MD" / ", PhD" is stripped before
# comparing). Search is Brave (Bing ignores site:/quoted queries from
# this box — measured 2026-10-17). Candidate pages come from, in order:
# site-search on INSTITUTIONAL domains derived from the article's own
# sources (.edu/.gov/.mil/.org source hosts only), general search
# (institutional TLDs, or profile-shaped paths on other official domains,
# never news-article paths), and conventional /person/<slug>-style URL
# guesses on the derived domains.
#
# Identity gates, all mandatory (hardened after the first dry run caught
# an EssentiallySports photo of Minjee Lee alt-texted "Min Woo Lee"):
# exact-name alt/caption; the page must be ABOUT the person (name in
# <title> or name slug in the URL path); non-institutional pages must
# also share a distinctive headline word (namesake screen); standard
# hero floors (≥800px wide — CMS full-size variants are tried when the
# rendered derivative is too small); group photos rejected when face
# detection is available. Anything short of all that is rejected,
# because a wrong photo is worse than no photo. Verified portraits are
# uploaded to Supabase storage and cached in person_images (source 3)
# so repeat stories reuse them.

_PROFILE_MISS_CACHE_PATH = os.path.join(SCRIPT_DIR, ".state", "person-profile-miss.json")
_PROFILE_MISS_TTL_SECS = 3 * 24 * 3600

# Trailing credential tokens allowed after an exact name in a profile alt
# ("Rachna Shroff, MD" → "Rachna Shroff"). Nothing else may follow the name.
_PROFILE_CREDENTIAL_TOKENS = {
    "md", "phd", "do", "mph", "mpp", "ms", "ma", "bs", "ba", "mba",
    "facp", "facc", "face", "esq", "jd", "rn", "dds", "dmd", "scd", "drph",
}

# URL path fragments that mark a page as a person/profile page.
_PROFILE_PATH_TOKENS = (
    "/person/", "/people/", "/faculty", "/profile", "/profiles/",
    "/staff/", "/team/", "/bio/", "/bios/", "/directory/", "/player",
    "/roster/", "/member/", "/experts/", "/doctor", "/physician",
    "/scientist", "/researcher", "/author", "/speaker",
)

# Domains that are never a person's institutional profile (news/social/wiki).
_PROFILE_EXCLUDED_DOMAINS = {
    "facebook.com", "instagram.com", "twitter.com", "x.com", "youtube.com",
    "linkedin.com", "wikipedia.org", "wikimedia.org", "tiktok.com",
    "reddit.com", "bing.com", "google.com", "duckduckgo.com",
    # Profile aggregators — not the person's institution; namesake traps
    # (a ResearchGate "Min Woo Lee" is a materials scientist, not the golfer)
    "researchgate.net", "academia.edu", "zoominfo.com",
    "ndtv.com", "indianexpress.com", "thehindu.com", "hindustantimes.com",
    "timesofindia.indiatimes.com", "theguardian.com", "nytimes.com",
    "washingtonpost.com", "bbc.com", "bbc.co.uk", "cnn.com", "reuters.com",
    "apnews.com", "aljazeera.com", "livemint.com", "moneycontrol.com",
    "firstpost.com", "theprint.in", "scroll.in", "thewire.in", "news18.com",
    "cnbc.com", "bloomberg.com", "espncricinfo.com", "cricbuzz.com",
}

# Tokens that disqualify a capitalized headline window as a person's name in
# the mid-headline scan: professions/titles, org words, nationality
# adjectives, extra headline verbs. A false candidate costs one search at
# most — the exact-name alt gate downstream can never let a wrong photo in.
_PROFILE_SCAN_BAD_TOKENS = (
    _HEADLINE_TITLE_WORDS | _HEADLINE_PREFIX_WORDS
    | _HEADLINE_NONNAME_FIRST_WORDS | _HEADLINE_COLLECTIVE_WORDS
    | _HEADLINE_COMMON_VERB_WORDS | _HEADLINE_DETERMINER_WORDS
    | _HEADLINE_DEMONYM_WORDS | _HEADLINE_ROLE_SECOND_WORDS
    | _HEADLINE_PRONOUN_WORDS
    | {
        "inc", "corp", "ltd", "llc", "co", "university", "college",
        "institute", "school", "hospital", "department", "ministry",
        "association", "foundation", "council", "commission", "agency",
        "bureau", "services", "solutions", "industries", "enterprises",
        "airlines", "airways", "motors", "pharma", "capital", "partners",
        "ventures", "network", "news", "times", "post", "journal",
        "gazette", "tribune", "herald", "express", "global", "national",
        "international",
        "american", "british", "canadian", "australian", "african",
        "asian", "european", "mexican", "pakistani", "bangladeshi",
        "nepali", "lankan", "korean", "chinese", "japanese", "russian",
        "researcher", "astronomer", "scientist", "golfer", "player",
        "coach", "actor", "actress", "singer", "lawyer", "judge",
        "officer", "chief", "director", "professor", "doctor", "engineer",
        "founder", "author", "artist", "chef", "expert", "official",
        "minister", "senator", "governor", "mayor", "captain",
        "withdraws", "withdraw", "returned", "returns", "killed", "dead",
        "arrested", "charged", "sentenced", "convicted", "never",
        "wanted", "fraudster", "fugitive", "suspect", "victim",
        # Headline verbs/role nouns/topic nouns seen in the 2026-10-17
        # no-image batch — none of these is ever part of a person's name
        "are", "is", "say", "says", "claiming", "claims", "promising",
        "promises", "warns", "warning", "turning", "rewriting",
        "triggers", "trigger", "alter", "backdate", "husband", "wife",
        "murder", "jobs", "visas", "diagnosis", "spasms", "illness",
        "mission", "million", "case", "plot", "violent", "document",
        "rules", "heroines", "lawmakers", "temple", "immigration",
        "lead", "leads", "older", "hate", "citizenship", "false", "claim",
        "illinois", "california", "texas", "florida", "ohio", "georgia",
        "arizona", "nevada", "oregon", "colorado", "virginia",
        # 2026-10-19 audit: articles/relative pronouns, resultative
        # adjectives, focusing adverbs, role descriptors, and event/org/
        # topic nouns the scan kept minting as "people" ("Unbeaten
        # Only", "The Flowers", "Counter-Extremism Programme", "Ebola
        # Cases", "Crore Investment", "Roadside Crew"). None of these is
        # ever part of a person's name.
        "the", "a", "an", "who",
        "unbeaten", "undefeated", "only", "also", "former", "defending",
        "reigning", "biggest", "largest", "junior", "senior",
        "designer", "stage", "crew", "staff", "agents",
        "programme", "program", "summit", "conference", "campaign",
        "scheme", "initiative", "games", "prevent",
        "cases", "total", "exemption", "crore", "lakh", "rs", "arm",
    }
)

# Words that disqualify a token as an additional name part in
# headline_person_name's full-name recovery: every non-name class above.
_NAME_PART_REJECT_WORDS = (
    _PROFILE_SCAN_BAD_TOKENS | _HEADLINE_STORM_WORDS
    | _HEADLINE_PROPER_NONPERSON_WORDS
)


def _norm_person_name(s):
    """Normalize a name/alt for comparison: lowercase, letters+spaces only."""
    s = (s or "").lower()
    s = re.sub(r"[^a-z\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def _profile_alt_matches(alt_text, person_name):
    """Identity gate: alt/caption must be EXACTLY the person's name
    (normalized), allowing only trailing credential tokens (MD, PhD, …)."""
    n = _norm_person_name(alt_text)
    t = _norm_person_name(person_name)
    if not n or not t:
        return False
    if n == t:
        return True
    nt, tt = n.split(), t.split()
    while len(nt) > len(tt) and nt[-1] in _PROFILE_CREDENTIAL_TOKENS:
        nt.pop()
    return " ".join(nt) == t


def _registrable_domain(host):
    """news.arizona.edu → arizona.edu (with common two-part suffix handling)."""
    host = (host or "").lower().split(":")[0].replace("www.", "")
    parts = [p for p in host.split(".") if p]
    if len(parts) <= 2:
        return host
    if parts[-2] in ("co", "com", "org", "net", "gov", "ac") and \
            parts[-1] in ("uk", "in", "au", "nz", "za", "jp", "br"):
        return ".".join(parts[-3:])
    return ".".join(parts[-2:])


def _looks_like_person_name(name):
    """Shape check for writer-provided entities: 2–4 capitalized tokens,
    no org/title tokens. Deliberately stricter than the headline scan."""
    if not isinstance(name, str):
        return False
    toks = [t.strip(".,'’") for t in name.split()]
    if not (2 <= len(toks) <= 4):
        return False
    for t in toks:
        if not t:
            return False
        if t.lower() in _PROFILE_SCAN_BAD_TOKENS:
            return False
        if t.isupper() and len(t) > 1:
            return False  # acronym token (NASA, FBI) — not a name part
        if not (t[0].isupper() or t.lower() in ("van", "von", "de", "der", "bin", "al")):
            return False
    return True


def _headline_name_scan(headline):
    """Find candidate person names mid-headline ("... Astronomer Ramya
    Anche to Lead ...", "... Researcher Rachna Shroff Dies ...") where
    headline_person_name() — which only reads the lead — returns None.

    Generates 2–3 token capitalized windows, latest-in-run first (a name
    usually ends its capitalized run, right before the verb). Windows
    containing a bad token are dropped. False candidates are harmless:
    each costs one search and the exact-name alt gate decides.
    """
    tokens = re.findall(r"[A-Za-z][A-Za-z.'’-]*", headline or "")
    runs, run = [], []
    for t in tokens:
        base = re.sub(r"['’]s$|['’]$", "", t).rstrip(".")
        if t[:1].isupper() and base.lower() not in _HEADLINE_COMMON_VERB_WORDS \
                and not (t.isupper() and len(t) <= 5):
            run.append(base)
            # Sentence boundary (multi-sentence headlines — "...Diwali
            # Sweets. They Sent a TV..."): a token ending in '.' that is
            # not a short abbreviation ("Dr.", "St.", "U.S.") closes the
            # run, or windows straddle the boundary and invent people
            # ("Sweets They Sent") (2026-10-19 audit).
            if t.endswith(".") and len(t) > 3 and t.count(".") == 1:
                if len(run) >= 2:
                    runs.append(run)
                run = []
        else:
            if len(run) >= 2:
                runs.append(run)
            run = []
    if len(run) >= 2:
        runs.append(run)
    out = []
    for run in runs:
        windows = []
        for start in range(len(run) - 2, -1, -1):
            windows.append(run[start:start + 2])
            if start + 3 <= len(run):
                windows.append(run[start:start + 3])
        for w in windows:
            if any(tok.lower() in _PROFILE_SCAN_BAD_TOKENS for tok in w):
                continue
            name = " ".join(w)
            if name not in out:
                out.append(name)
    return out


def _person_name_candidates(article):
    """Ordered candidate names for the profile lookup:
    headline lead → writer entities → mid-headline scan. Capped at 6."""
    names = []

    def _add(n):
        n = re.sub(r"['’]s$", "", (n or "").strip())
        if n and n.lower() not in {x.lower() for x in names} and 3 <= len(n) <= 42:
            names.append(n)

    lead = headline_person_name(article.get("headline", ""))
    if lead:
        _add(lead)
    for e in (article.get("image_entities") or [])[:4]:
        if _looks_like_person_name(e):
            _add(e)
    for n in _headline_name_scan(article.get("headline", "")):
        _add(n)
    return names[:6]


def _brave_search_links(query, max_results=10):
    """Web search via Brave Search HTML (no API key), result URLs in rank
    order. Search route measured 2026-10-17: Bing (RSS and HTML) ignores
    site:/quoted queries from this box and returns loose single-term
    matches (a site:arizona.edu query for an astronomer returned a film
    actress's pages), while Brave honors both operators and ranked the
    real Steward Observatory profile #2 for "Ramya Anche" arizona.
    Honors site: restrictions, so it serves both the derived-domain and
    general searches below."""
    try:
        q = urllib.parse.quote(query)
        url = f"https://search.brave.com/search?q={q}"
        result = _safe_run(
            ["curl", "-sSL", "--max-time", "15",
             "-A", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
             url],
            capture_output=True, text=True, timeout=20,
        )
        links = re.findall(r'href="(https?://[^"]+)"', result.stdout or "")
        out = []
        for link in links:
            try:
                parsed = urllib.parse.urlparse(link)
            except Exception:
                continue
            if _registrable_domain(parsed.netloc) == "brave.com":
                continue
            if parsed.path.lower().endswith(
                    (".css", ".js", ".png", ".jpg", ".svg", ".ico", ".woff2")):
                continue
            if link not in out:
                out.append(link)
            if len(out) >= max_results:
                break
        return out
    except Exception as e:
        print(f"    ⚠ person-profile search error: {e}")
        return []


def _profile_page_candidates(person_name, article):
    """Candidate official profile pages for a person, best first:
    (1) site-search on non-news domains derived from the article's own
        sources (a UA News source → search arizona.edu), then
    (2) general web search, filtered to institutional domains (.edu/.gov/
        .org/.mil) or strongly profile-shaped URLs on other official
        domains (e.g. a tour's /player/ page)."""
    pages = []

    def _add(u):
        if u and u not in pages:
            pages.append(u)

    # (1) Domains derived from the article's own sources
    src_urls = []
    raw_sources = article.get("sources") or []
    if isinstance(raw_sources, str):
        try:
            raw_sources = json.loads(raw_sources)
        except Exception:
            raw_sources = []
    if isinstance(raw_sources, list):
        for src in raw_sources:
            if isinstance(src, str) and src.startswith("http"):
                src_urls.append(src)
            elif isinstance(src, dict) and str(src.get("url", "")).startswith("http"):
                src_urls.append(src["url"])
    if article.get("topic_id"):
        try:
            for u in fetch_source_urls(article["topic_id"]):
                if u not in src_urls:
                    src_urls.append(u)
        except Exception:
            pass
    derived = []
    for u in src_urls:
        try:
            parsed_u = urllib.parse.urlparse(u)
            host = parsed_u.netloc.lower()
            dom = _registrable_domain(host)
        except Exception:
            continue
        # INSTITUTIONAL GATE for derived domains (hardened 2026-10-17):
        # only .edu/.gov/.mil/.org source hosts make their registrable
        # domain "the subject's institution". A .com news source must NOT
        # qualify — in the first dry run, an EssentiallySports article
        # about Minjee Lee carried an image alt-texted "Min Woo Lee" (her
        # brother), and the derived-domain path let that page in. Alt text
        # on content-farm pages is not identity verification.
        if not host.endswith((".edu", ".gov", ".mil", ".org")):
            continue
        if dom and dom not in derived and dom not in _PROFILE_EXCLUDED_DOMAINS:
            derived.append(dom)
    for dom in derived[:2]:
        for link in _brave_search_links(f'site:{dom} "{person_name}"'):
            _add(link)

    # (2) General web search
    for query in (f'"{person_name}" profile', f'"{person_name}" faculty profile'):
        for link in _brave_search_links(query, max_results=10):
            try:
                parsed = urllib.parse.urlparse(link)
            except Exception:
                continue
            dom = _registrable_domain(parsed.netloc)
            if dom in _PROFILE_EXCLUDED_DOMAINS:
                continue
            tld_ok = parsed.netloc.lower().endswith(
                (".edu", ".gov", ".org", ".mil"))
            path = parsed.path.lower()
            if not tld_ok:
                # Non-institutional domains qualify ONLY via a profile-
                # shaped path (a tour's /player/ page, a team's /roster/
                # page) — and never via a news-article path, whose image
                # alt text is written for a different story (the Minjee
                # Lee near-miss above arrived on a /golf-news-… path).
                if re.search(r"/news/|[-_]news[-_.\/]|/article|/stor(y|ies)/|"
                             r"/(19|20)\d{2}/\d{1,2}/", path):
                    continue
                if not any(tok in path for tok in _PROFILE_PATH_TOKENS):
                    continue
            _add(link)
        if len(pages) >= 8:
            break

    # (3) Last resort: conventional profile-URL patterns on the derived
    # institutional domains (…/person/<name-slug> is the UA pattern that
    # held Ramya Anche's portrait). Tried last; a 404 simply yields no
    # exact-name image and the lookup moves on.
    slug = re.sub(r"[^a-z0-9]+", "-", person_name.lower()).strip("-")
    for dom in derived[:2]:
        for host in (dom, f"www.{dom}"):
            for pat in ("/person/", "/people/", "/faculty/", "/profile/"):
                _add(f"https://{host}{pat}{slug}")
    return pages[:10]


def _portrait_url_variants(url):
    """Full-size variants of a CMS-styled portrait URL. Profile pages often
    render a styled derivative below the hero floor (measured 2026-10-17:
    Arizona's Drupal served the 760px 'az_medium' derivative while the
    3024×4032 original sat at the style-stripped path). Variants:
    the URL itself, the Drupal style-stripped original
    (/styles/<style>/public/ → /), and the WordPress size-suffix-stripped
    original (-<w>x<h> before the extension)."""
    out = [url]
    stripped = re.sub(r"/styles/[^/]+/public/", "/", url)
    if stripped != url:
        out.append(stripped)
    wp = re.sub(r"-\d{2,4}x\d{2,4}(\.[a-zA-Z0-9]+)(\?.*)?$", r"\1\2", url)
    if wp != url:
        out.append(wp)
    return out


def _is_logo_filename(img_url):
    """Narrow logo check for profile portraits. The og:image generic guard
    is NOT reused here: its directory-segment patterns false-positive on
    standard CMS paths (Drupal's /sites/default/files/ tripped it on the
    verified Ramya Anche portrait). The exact-name alt is the identity
    gate; this only screens out obvious non-portrait files."""
    try:
        fname = urllib.parse.urlparse(img_url).path.rsplit("/", 1)[-1].lower()
    except Exception:
        fname = (img_url or "").lower()
    return any(x in fname for x in
               ("logo", "icon", "favicon", "sprite", "placeholder"))


def _extract_exact_name_portrait(page_url, person_name, context_words=None):
    """Fetch a profile page and find an <img> whose alt EXACTLY matches the
    person's name (or a <figure> whose figcaption does).
    Returns (image_url_variants, site_name, fetched_ok, page_title,
    topical_ok) — variants are the matched src plus its full-size CMS
    variants, best-evidence first. topical_ok reports whether the page's
    visible text shares a distinctive headline word (namesake screen for
    non-institutional pages); it is True when no context words were given."""
    try:
        result = _safe_run(
            ["curl", "-sSL", "--max-time", "15", "-A", UA, page_url],
            capture_output=True, text=True, timeout=20,
        )
        html = result.stdout or ""
    except Exception:
        return None, None, False, None, True
    if not html:
        return None, None, False, None, True

    import html as _html_mod
    site_name = None
    m = re.search(r'property=["\']og:site_name["\'][^>]+content=["\']([^"\']+)["\']',
                  html, re.IGNORECASE)
    if m:
        site_name = _html_mod.unescape(m.group(1).strip()) or None
    page_title = None
    mt = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
    if mt:
        page_title = _html_mod.unescape(
            re.sub(r"<[^>]+>", " ", mt.group(1))).strip() or None
    # Topical corroboration: does the page's visible text share any
    # distinctive headline word (excluding the person's own name tokens)?
    topical_ok = True
    if context_words:
        visible = re.sub(r"<(script|style)\b.*?</\1>", " ", html,
                         flags=re.IGNORECASE | re.DOTALL)
        visible = _html_mod.unescape(re.sub(r"<[^>]+>", " ", visible)).lower()
        topical_ok = any(w in visible for w in context_words)

    def _attr(tag, name):
        mm = re.search(name + r'\s*=\s*"([^"]*)"', tag, re.IGNORECASE) or \
            re.search(name + r"\s*=\s*'([^']*)'", tag, re.IGNORECASE)
        return _html_mod.unescape(mm.group(1).strip()) if mm else ""

    def _img_variants(tag):
        urls = []
        src = _attr(tag, "src") or _attr(tag, "data-src") or _attr(tag, "data-lazy-src")
        if src and not src.startswith("data:"):
            urls.append(urllib.parse.urljoin(page_url, src))
        srcset = _attr(tag, "srcset")
        if srcset:
            for part in srcset.split(","):
                u = part.strip().split(" ")[0]
                if u and not u.startswith("data:"):
                    urls.append(urllib.parse.urljoin(page_url, u))
        variants = []
        for u in urls:
            for v in _portrait_url_variants(u):
                if v not in variants:
                    variants.append(v)
        return variants

    for m in re.finditer(r"<img\b[^>]*>", html, re.IGNORECASE):
        tag = m.group(0)
        if _profile_alt_matches(_attr(tag, "alt"), person_name):
            variants = _img_variants(tag)
            if variants:
                return variants, site_name, True, page_title, topical_ok
    # figcaption fallback: figure whose caption is exactly the name
    for fm in re.finditer(r"<figure\b.*?</figure>", html, re.IGNORECASE | re.DOTALL):
        block = fm.group(0)
        cap = re.search(r"<figcaption[^>]*>(.*?)</figcaption>", block,
                        re.IGNORECASE | re.DOTALL)
        if cap:
            cap_text = re.sub(r"<[^>]+>", " ", cap.group(1))
            if _profile_alt_matches(cap_text, person_name):
                im = re.search(r"<img\b[^>]*>", block, re.IGNORECASE)
                if im:
                    variants = _img_variants(im.group(0))
                    if variants:
                        return variants, site_name, True, page_title, topical_ok
    return None, site_name, True, page_title, topical_ok


def _count_faces(img_bytes):
    """Haar face count for the group-photo gate. -1 = detection unavailable
    (cv2 missing) — the exact-name alt gate still applies on its own."""
    try:
        import cv2
        import numpy as np
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return -1
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        faces = cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5,
            minSize=(int(gray.shape[1] * 0.04), int(gray.shape[0] * 0.04)))
        return len(faces)
    except Exception:
        return -1


def _profile_miss_fresh(person_lower):
    try:
        with open(_PROFILE_MISS_CACHE_PATH) as f:
            cache = json.load(f)
        ts = cache.get(person_lower, {}).get("ts", 0)
        return (time.time() - ts) < _PROFILE_MISS_TTL_SECS
    except Exception:
        return False


def _profile_record_miss(person_lower):
    try:
        cache = {}
        if os.path.exists(_PROFILE_MISS_CACHE_PATH):
            with open(_PROFILE_MISS_CACHE_PATH) as f:
                cache = json.load(f)
        cache[person_lower] = {"ts": time.time()}
        os.makedirs(os.path.dirname(_PROFILE_MISS_CACHE_PATH), exist_ok=True)
        with open(_PROFILE_MISS_CACHE_PATH, "w") as f:
            json.dump(cache, f)
    except Exception:
        pass


def _cache_person_profile_image(person_name, image_url, attribution,
                                source_url, w, h):
    """Insert a verified profile portrait into person_images (source 3)
    so repeat stories reuse it. Skips if the person is already cached."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        return
    try:
        if fetch_cached_person_image(person_name):
            return
        # NOTE: person_name_lower is a GENERATED column — never insert it.
        payload = {
            "person_name": person_name,
            "image_url": image_url,
            "orientation": "portrait" if h >= w else "landscape",
            "license": "institutional profile",
            "attribution": attribution,
            "source_url": source_url,
            "img_w": w,
            "img_h": h,
            "use_count": 0,
        }
        r = _safe_run(
            ["curl", "-sS", "--max-time", "15", "-X", "POST",
             f"{SUPABASE_URL}/rest/v1/person_images",
             "-H", f"apikey: {SUPABASE_KEY}",
             "-H", f"Authorization: Bearer {SUPABASE_KEY}",
             "-H", "Content-Type: application/json",
             "-H", "Prefer: return=minimal",
             "-d", json.dumps(payload)],
            capture_output=True, text=True, timeout=20,
        )
        if r.returncode == 0 and '"code"' not in (r.stdout or ""):
            print(f"    💾 person-profile: cached '{person_name}' in person_images")
        else:
            print(f"    ⚠ person-profile cache insert rejected: {(r.stdout or '')[:160]}")
    except Exception as e:
        print(f"    ⚠ person-profile cache insert failed: {e}")


def fetch_person_profile_image(article):
    """Source 3.8: the named subject's own institutional profile portrait.

    Finds the subject's official profile page, accepts only an exact-name
    alt/caption portrait that clears the standard hero gates (≥800px wide,
    not a group photo when face detection is available, not a generic/
    logo image), uploads it to Supabase storage, and caches it in
    person_images.

    Returns (image_url, attribution, person_name) or (None, None, None).
    Returning None is a correct outcome — null beats a wrong photo.
    """
    names = _person_name_candidates(article)
    if not names:
        return None, None, None
    # Distinctive headline words for the namesake screen (the person's own
    # name tokens are subtracted per-candidate inside the loop).
    headline_words = {
        w for w in re.findall(r"[a-z]{4,}", (article.get("headline") or "").lower())
    } - _COMMONS_STOP
    for name in names:
        ctx_words = headline_words - set(_norm_person_name(name).split())
        if _profile_miss_fresh(name.lower()):
            print(f"    ⊘ person-profile: '{name}' recently missed, skipping")
            continue
        print(f"    🎓 person-profile: looking up '{name}'")
        pages = _profile_page_candidates(name, article)
        fetched_any = False
        hit = None
        name_slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
        for page_url in pages[:8]:
            variants, site_name, fetched, page_title, topical_ok = \
                _extract_exact_name_portrait(page_url, name, ctx_words)
            fetched_any = fetched_any or fetched
            if not variants:
                continue
            # Page-about-person check: the page itself must be ABOUT this
            # person — their name in the <title> or their name slug in the
            # URL path. An exact-name alt on a page about someone else
            # (a sibling, a namesake) is not identity verification.
            title_ok = page_title and \
                _norm_person_name(name) in _norm_person_name(page_title)
            slug_ok = name_slug in urllib.parse.urlparse(page_url).path.lower()
            if not title_ok and not slug_ok:
                print(f"    ⊘ person-profile: page not about '{name}' "
                      f"(title/path check) — {page_url[:56]}")
                continue
            # Namesake screen for NON-institutional pages: an institutional
            # domain (.edu/.gov/.mil/.org) is itself the corroboration,
            # but a profile-shaped page anywhere else must also share a
            # distinctive headline word — a same-named stranger's profile
            # (different field, different life) shares none.
            page_host = urllib.parse.urlparse(page_url).netloc.lower()
            if not page_host.endswith((".edu", ".gov", ".mil", ".org")) \
                    and ctx_words and not topical_ok:
                print(f"    ⊘ person-profile: no topical corroboration on "
                      f"non-institutional page — {page_url[:56]}")
                continue
            for img_url in variants:
                if _is_logo_filename(img_url):
                    continue
                ok, ctype, vw = verify_image_url(img_url)  # 800px hero floor
                if not ok:
                    continue
                raw = download_image(img_url)
                if not raw:
                    continue
                pw, ph = get_image_dimensions(raw)
                if pw < 800:
                    continue
                faces = _count_faces(raw)
                if faces >= 2:
                    print(f"    ⊘ person-profile: '{name}' image has {faces} faces (group photo), skipping")
                    continue
                attribution = site_name or _registrable_domain(
                    urllib.parse.urlparse(page_url).netloc)
                # Upload to our storage so the hero survives the institution
                # redesigning its site; fall back to the source URL if the
                # upload fails (it was verified reachable above).
                slug_name = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
                fname = f"person-images/{slug_name}-{int(time.time())}.jpg"
                uploaded = upload_to_supabase(compress_image(raw), fname)
                final_url = uploaded or img_url
                _cache_person_profile_image(name, final_url, attribution,
                                            page_url, pw, ph)
                print(f"    ✓ person-profile: '{name}' ← {page_url[:64]}")
                hit = (final_url, attribution, name)
                break
            if hit:
                break
            print(f"    ⊘ person-profile: '{name}' exact-name portrait(s) failed verification/size floor on {page_url[:50]}")
        if hit:
            return hit
        if fetched_any:
            _profile_record_miss(name.lower())
    return None, None, None


# ── Image Quality Scoring (2026-10-11) ────────────────────────────────────
# Kiran's directive: "pick the best, not the first." Instead of taking the
# first image that passes validation, collect candidates from multiple
# sources, score each, and use the highest-scoring one.

import math
import datetime
import concurrent.futures

# Source reputation: professional/curated sources outrank amateur uploads.
# Higher = more trustworthy, professionally produced, copyright-safe.
_SOURCE_REPUTATION = {
    "brand_official": 100,   # Brand's own site — professional product photography
    "official_source": 95,   # Government/company press — professional, copyright-safe
    "person_cache": 90,      # Curated media library — human-verified
    "person_profile": 88,    # Subject's own institutional profile — exact-name alt verified
    "prnewswire": 85,        # Press-approved wire images — professional
    "wikipedia": 75,         # Identity-verified, variable recency
    "wikipedia_headline_guard": 75,
    "og:image": 70,          # Publisher og:image — topical but variable quality
    "youtube_thumbnail": 65, # HD thumbnails — good but capped at 1280x720
    "commons_search": 55,    # Commons — variable quality and age
    "rss_thumbnail": 40,     # RSS feed images — variable
    "pexels": 25,            # Stock photos — last resort
}


def _parse_upload_date(date_str):
    """Parse a Commons/Wikipedia timestamp like '2020-05-15T10:30:00Z'."""
    if not date_str:
        return None
    try:
        # Handle ISO format with Z suffix
        s = date_str.replace("Z", "+00:00")
        dt = datetime.datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=datetime.timezone.utc)
        return dt
    except Exception:
        return None


def score_image_candidate(url, source_name, width, height, upload_date=None):
    """Score an image candidate for hero selection. Higher = better.

    Factors:
    - Source reputation (0-100): professional sources outrank amateur uploads
    - Resolution (0-50): log scale — 800px≈20, 1600px≈35, 3200px≈50
    - Aspect ratio (0-20): heroes display at 16:9, prefer 1.3-2.0 landscape
    - Freshness (0-15): prefer recent, mild penalty for >5 years old

    Returns a float score. Typical range: 30 (poor) to 185 (excellent).
    """
    score = 0.0

    # 1. Source reputation
    score += _SOURCE_REPUTATION.get(source_name, 30)

    # 2. Resolution — log scale so 4K isn't 4x better than 1080p
    if width > 0 and height > 0:
        mp = (width * height) / 1_000_000  # megapixels
        # 0.64MP (800x800) ≈ 18, 2MP (1600x1200) ≈ 30, 8MP ≈ 44
        score += min(50, 15 * math.log10(max(mp, 0.1)) + 25)

    # 3. Aspect ratio — heroes display at ~16:9 (1.78)
    if width > 0 and height > 0:
        aspect = width / height
        if 1.3 <= aspect <= 2.0:
            score += 20  # Ideal hero range
        elif 1.0 <= aspect < 1.3 or 2.0 < aspect <= 2.5:
            score += 10  # Acceptable
        elif 0.7 <= aspect < 1.0 or 2.5 < aspect <= 3.0:
            score += 0   # Usable but will crop awkwardly
        else:
            score -= 20  # Extreme portrait or panoramic — crops badly

    # 4. Freshness — prefer recent images (the 2010 Himesh Reshammiya problem)
    if upload_date:
        try:
            now = datetime.datetime.now(datetime.timezone.utc)
            age_days = (now - upload_date).days
            if age_days < 0:
                pass  # Future date? Ignore.
            elif age_days < 365:
                score += 15  # <1 year: fresh
            elif age_days < 1825:
                score += 10  # <5 years: good
            elif age_days < 3650:
                score += 5   # <10 years: acceptable
            # >10 years: no bonus, but no penalty either (better old than nothing)
        except Exception:
            pass

    return round(score, 1)


def _fetch_commons_with_date(search_query, headline="", max_results=5):
    """Search Commons and return candidates with upload dates.
    Returns list of {url, title, upload_date} dicts.
    """
    if not search_query:
        return []
    params = urllib.parse.urlencode({
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrsearch": search_query,
        "gsrlimit": str(max_results),
        "prop": "imageinfo",
        "iiprop": "url|mime|size|timestamp",  # timestamp added for freshness scoring
        "iiurlwidth": "1200",
    })
    url = f"https://commons.wikimedia.org/w/api.php?{params}"
    candidates = []
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
            img_url = ii.get("thumburl") or ii.get("url")
            if img_url:
                candidates.append({
                    "url": img_url,
                    "title": title,
                    "upload_date": _parse_upload_date(ii.get("timestamp")),
                })
    except Exception:
        pass
    return candidates


def _collect_hero_candidates(article, used_images=None):
    """Collect image candidates from fast sources in parallel.

    Returns list of dicts: {img_url, attribution, source_name, upload_date, extra}
    Up to ~10 candidates; the scorer picks the best 5 to download and rank.

    Slow sources (official_source Bing search, PR Newswire) are NOT included
    here — they run as fallback if fast sources yield nothing.
    """
    headline = article.get("headline", "")
    topic_id = article.get("topic_id")
    search_query = article.get("image_search_query", "")
    entities = article.get("image_entities", [])
    must_show = article.get("image_must_show", "")
    used = used_images or set()

    candidates = []

    def _try_og():
        """og:image from source articles — collect multiple, not just best."""
        results = []
        all_source_urls = []
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
        if topic_id:
            try:
                signal_urls = fetch_source_urls(topic_id)
                for u in signal_urls:
                    if u not in all_source_urls:
                        all_source_urls.append(u)
            except:
                pass
        for src_url in all_source_urls[:6]:
            try:
                og_img = fetch_og_image(src_url)
                if og_img and og_img not in used:
                    if not _og_image_topical_ok(og_img, headline, search_query):
                        continue
                    try:
                        domain = urllib.parse.urlparse(src_url).netloc.replace("www.", "")
                    except:
                        domain = "Source Article"
                    results.append({
                        "img_url": og_img,
                        "attribution": domain,
                        "source_name": "og:image",
                        "upload_date": None,
                    })
            except:
                continue
        return results

    def _try_person_cache():
        results = []
        for entity in (entities or [])[:3]:
            if isinstance(entity, str) and len(entity) > 2:
                try:
                    cached = fetch_cached_person_image(entity)
                    if cached and cached not in used:
                        results.append({
                            "img_url": cached,
                            "attribution": "Media Library",
                            "source_name": "person_cache",
                            "upload_date": None,
                        })
                except:
                    continue
        return results

    def _try_youtube():
        results = []
        main_entity = next((e for e in (entities or [])[:2]
                           if isinstance(e, str) and len(e) > 2), None)
        if main_entity:
            try:
                yt_thumb, yt_title, yt_channel = fetch_youtube_thumbnail(main_entity, headline)
                if yt_thumb and yt_thumb not in used:
                    results.append({
                        "img_url": yt_thumb,
                        "attribution": f"YouTube / {yt_channel}" if yt_channel else "YouTube",
                        "source_name": "youtube_thumbnail",
                        "upload_date": None,
                    })
            except:
                pass
        return results

    def _try_person_profile():
        results = []
        try:
            pp_url, pp_attr, pp_name = fetch_person_profile_image(article)
            if pp_url and pp_url not in used:
                results.append({
                    "img_url": pp_url,
                    "attribution": pp_attr or "Official Profile",
                    "source_name": "person_profile",
                    "upload_date": None,
                    "person_name": pp_name,
                })
        except Exception as e:
            print(f"    ⚠ person-profile source failed: {e}")
        return results

    def _try_brand():
        results = []
        try:
            brand_img, brand_attr = fetch_brand_image(headline, entities)
            if brand_img and brand_img not in used:
                results.append({
                    "img_url": brand_img,
                    "attribution": brand_attr or "Official Brand Site",
                    "source_name": "brand_official",
                    "upload_date": None,
                })
        except:
            pass
        return results

    def _try_wikipedia():
        results = []
        for entity in (entities or [])[:3]:
            if isinstance(entity, str) and len(entity) > 2:
                try:
                    wp_img = fetch_wikipedia_image(entity, article_context=headline)
                    if wp_img and wp_img not in used:
                        results.append({
                            "img_url": wp_img,
                            "attribution": "Wikimedia Commons",
                            "source_name": "wikipedia",
                            "upload_date": None,  # Wikipedia REST API doesn't return dates
                        })
                except:
                    continue
        return results

    def _try_commons():
        results = []
        query = search_query or must_show or headline[:60]
        try:
            for c in _fetch_commons_with_date(query, headline, max_results=5):
                if c["url"] not in used:
                    results.append({
                        "img_url": c["url"],
                        "attribution": "Wikimedia Commons",
                        "source_name": "commons_search",
                        "upload_date": c["upload_date"],
                    })
        except:
            pass
        return results

    # Run fast sources in parallel (I/O-bound curl subprocesses)
    with concurrent.futures.ThreadPoolExecutor(max_workers=7) as ex:
        future_map = {
            ex.submit(_try_og): "og",
            ex.submit(_try_person_cache): "cache",
            ex.submit(_try_youtube): "youtube",
            ex.submit(_try_person_profile): "person_profile",
            ex.submit(_try_brand): "brand",
            ex.submit(_try_wikipedia): "wikipedia",
            ex.submit(_try_commons): "commons",
        }
        for fut in concurrent.futures.as_completed(future_map):
            try:
                result = fut.result()
                if result:
                    candidates.extend(result)
            except Exception as e:
                print(f"    ⚠ candidate source '{future_map[fut]}' failed: {e}")

    # Dedup by URL
    seen = set()
    unique = []
    for c in candidates:
        if c["img_url"] not in seen:
            seen.add(c["img_url"])
            unique.append(c)

    print(f"    📊 Collected {len(unique)} candidates from fast sources")
    return unique


def _score_and_rank_candidates(candidates, headline=""):
    """Download candidates in parallel, score each, return ranked list.

    Returns list of (candidate_dict, score, width, height, img_bytes) sorted
    by score descending. Candidates that fail download or the 800px bar are
    excluded.
    """
    if not candidates:
        return []

    def _download_and_measure(cand):
        try:
            img_bytes = download_image(cand["img_url"], timeout=12)
            if not img_bytes:
                return None
            w, h = get_image_dimensions(img_bytes)
            if w < 800:  # Hero quality bar
                return None
            score = score_image_candidate(
                cand["img_url"], cand["source_name"], w, h,
                cand.get("upload_date"))
            return (cand, score, w, h, img_bytes)
        except Exception:
            return None

    ranked = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
        futures = [ex.submit(_download_and_measure, c) for c in candidates[:10]]
        for fut in concurrent.futures.as_completed(futures):
            try:
                result = fut.result()
                if result:
                    ranked.append(result)
            except Exception:
                continue

    ranked.sort(key=lambda x: x[1], reverse=True)

    # Log all candidates and winner for debugging
    for cand, score, w, h, _ in ranked:
        print(f"      [{score:6.1f}] {cand['source_name']:20s} {w}x{h}  {cand['img_url'][:60]}")
    if ranked:
        winner = ranked[0]
        print(f"    🏆 Winner: {winner[0]['source_name']} (score {winner[1]})")

    return ranked


def source_hero_image(article, used_images=None):
    """Multi-source image sourcing with HTTP verification at every step.
    
    Args:
        article: Dict with headline, slug, category, topic_id, image_search_query,
                 image_entities, image_must_show. May also have 'sources' (list of URLs).
        used_images: Set of image URLs already used in this batch
    
    Returns:
        (final_url, attribution, caption, source_name) or (None, None, None, None)
        source_name is one of: og:image, rss_thumbnail, person_cache,
        person_profile, youtube_thumbnail, official_source, prnewswire,
        wikipedia, commons_search, wikipedia_headline_guard, pexels — or
        None when no image was found.
    """
    headline = article.get("headline", "")
    slug = article.get("slug", "unknown")
    topic_id = article.get("topic_id")
    search_query = article.get("image_search_query", "")
    entities = article.get("image_entities", [])
    must_show = article.get("image_must_show", "")
    category = article.get("category", "")
    
    # ── NEW: Collect → Score → Pick (2026-10-11) ──────────────────────────
    # Kiran's directive: "pick the best, not the first." Collect candidates
    # from fast sources in parallel, score each by quality, use the winner.
    # Slow sources (official_source, PR Newswire, Pexels) remain as fallback.
    print(f"  🖼  Sourcing image: {headline[:55]}...")

    used = used_images or set()
    pexels_alt = None

    # ── Phase 1: Collect candidates from fast sources (parallel) ──────────
    candidates = _collect_hero_candidates(article, used)

    # ── Phase 2: Named-person identity filter ─────────────────────────────
    # "Wrong photo is worse than no photo." For named-person articles, only
    # identity-verified sources are eligible. Commons and Pexels are NOT
    # identity-verified and are excluded here (Pexels was already skipped;
    # Commons relevance check is not an identity check).
    person = headline_person_name(headline)
    _IDENTITY_SAFE = {
        "person_cache", "person_profile", "wikipedia", "wikipedia_headline_guard",
        "youtube_thumbnail", "og:image", "brand_official", "official_source",
    }
    if person:
        before = len(candidates)
        candidates = [c for c in candidates if c["source_name"] in _IDENTITY_SAFE]
        dropped = before - len(candidates)
        if dropped:
            print(f"    🛡  Named-person filter: dropped {dropped} non-identity-verified candidates")

    # ── Person-profile precedence (2026-10-17) ────────────────────────────
    # An exact-name-verified portrait from the subject's own institutional
    # profile outranks Wikipedia outright: the Ramya Anche article shipped
    # a NASA HQ building photo from the Wikipedia fallback (scored on size/
    # aspect) while her verified portrait sat on her university profile.
    # When the profile step verified a portrait, Wikipedia candidates are
    # dropped so scoring can never resurrect that failure mode.
    if any(c["source_name"] == "person_profile" for c in candidates):
        before = len(candidates)
        candidates = [c for c in candidates if c["source_name"] != "wikipedia"]
        if len(candidates) < before:
            print(f"    🎓 person-profile precedence: dropped {before - len(candidates)} Wikipedia candidate(s)")

    # ── Phase 3: Score, rank, and try winners ─────────────────────────────
    ranked = _score_and_rank_candidates(candidates, headline)

    img_url = None
    attribution = "The Videshi"
    source_name = None
    raw_bytes = None
    w, h = 0, 0
    winner_person = None

    for cand, score, cw, ch, cbytes in ranked:
        # Near-square gate for publisher images (likely logos/placeholders)
        if cand["source_name"] in ("og:image", "rss_thumbnail") and cw > 0 and ch > 0:
            aspect = cw / ch
            if 0.85 <= aspect <= 1.18:
                print(f"    ✗ Near-square publisher image ({cw}x{ch}, likely logo), trying next")
                continue
        img_url = cand["img_url"]
        attribution = cand["attribution"]
        source_name = cand["source_name"]
        winner_person = cand.get("person_name")
        raw_bytes = cbytes
        w, h = cw, ch
        print(f"    ✓ Selected: {source_name} (score {score}) → {img_url[:60]}")
        break

    # ── Phase 4: Fallback to slow sources if fast sources yielded nothing ──
    # (official_source with Bing search, PR Newswire, Pexels)
    tried = set()
    if not img_url:
        print(f"    ⏳ Fast sources yielded nothing, trying slow sources...")
        _writer_official_url = globals().get("_WRITER_OFFICIAL_URL")

        # Slow source A: Official source (government/company)
        if not person:  # Never fires for person-led headlines anyway
            try:
                off_img, off_attr = fetch_official_source_image(
                    headline, entities, search_query,
                    official_url=_writer_official_url)
                if off_img and off_img not in used:
                    ok, ctype, vw = verify_image_url(off_img)
                    if ok:
                        img_url = off_img
                        attribution = off_attr or "Official Source"
                        source_name = "official_source"
                        print(f"    ✓ Official-source image ({attribution})")
            except Exception as e:
                print(f"    ⚠ official-source failed: {e}")

        # Slow source B: PR Newswire
        if not img_url:
            prn_query = search_query or (entities[0] if entities else None) or headline[:40]
            if prn_query and isinstance(prn_query, str):
                try:
                    prn_img = fetch_prnewswire_image(prn_query)
                    if prn_img and prn_img not in used:
                        ok, ctype, vw = verify_image_url(prn_img)
                        if ok:
                            # Download to score
                            pb = download_image(prn_img)
                            if pb:
                                pw, ph = get_image_dimensions(pb)
                                if pw >= 800:
                                    img_url = prn_img
                                    attribution = "PR Newswire"
                                    source_name = "prnewswire"
                                    raw_bytes = pb
                                    w, h = pw, ph
                                    print(f"    ✓ PR Newswire image")
                except Exception as e:
                    print(f"    ⚠ prnewswire failed: {e}")

        # Slow source C: Pexels (never for named persons)
        if not img_url and not person:
            tags = article.get("tags") or []
            first_tag = tags[0] if tags else ""
            h_words = {w for w in re.findall(r"[a-z]+", (headline or "").lower())
                       if len(w) > 3}
            topic_tag, best = "", 0
            for t in tags:
                toks = {w for w in re.findall(r"[a-z]+", str(t).lower())
                        if len(w) > 3}
                s = len(toks & h_words)
                if s > best:
                    best, topic_tag = s, t
            query = search_query or must_show or topic_tag or first_tag or headline[:40]
            try:
                pexels_img, p_alt = fetch_pexels_image(query)
                if pexels_img and pexels_img not in used:
                    ok, ctype, vw = verify_image_url(pexels_img)
                    if ok:
                        pb = download_image(pexels_img)
                        if pb:
                            pw, ph = get_image_dimensions(pb)
                            if pw >= 800:
                                img_url = pexels_img
                                attribution = "Pexels"
                                source_name = "pexels"
                                pexels_alt = p_alt
                                raw_bytes = pb
                                w, h = pw, ph
                                print(f"    ✓ Pexels fallback")
            except Exception as e:
                print(f"    ⚠ pexels failed: {e}")

        # Named-person headline guard: try Wikipedia once more before giving up
        if not img_url and person:
            try:
                wp_img = fetch_wikipedia_image(person, article_context=headline)
                if wp_img and wp_img not in used:
                    ok, ctype, vw = verify_image_url(wp_img)
                    if ok:
                        pb = download_image(wp_img)
                        if pb:
                            pw, ph = get_image_dimensions(pb)
                            if pw >= 800:
                                img_url = wp_img
                                attribution = "Wikimedia Commons"
                                source_name = "wikipedia_headline_guard"
                                raw_bytes = pb
                                w, h = pw, ph
                                print(f"    ✓ Wikipedia headline guard for '{person}'")
            except Exception:
                pass
            if not img_url:
                print(f"    ⊘ Named-person article ('{person}') — staying imageless")

    # ── No candidate left ───────────────────────────────────────────────
    if not img_url:
        print(f"    ✗ No image found — publishing without hero (better than broken)")
        return None, None, None, None

    # Ensure we have bytes and dimensions (slow-source path may not have them)
    if raw_bytes is None:
        raw_bytes = download_image(img_url)
        if not raw_bytes:
            print(f"    ✗ Download failed: {img_url[:60]}")
            return None, None, None, None
        w, h = get_image_dimensions(raw_bytes)

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
    except Exception as e:
        # Never fail the article over focal detection, but never fail silently
        # either: a missing cv2 install leaves every image center-cropped (0.5, 0.5).
        print(f"    ⚠ focal-point detection unavailable ({e}); using center crop")
    
    face_flag = "👤" if (fx != 0.5 or fy != 0.5) else "📐"
    print(f"    {face_flag} {source_name} → {w}×{h}, focal ({fx:.2f}, {fy:.2f})")
    
    # Use the original source URL directly — no Supabase upload.
    # Source CDNs (Wikipedia, Pexels, news sites) are fast and reliable.
    final_url = img_url
    
    # Caption — keep factual, only use first entity name if confident
    caption = None
    if source_name == "pexels" and pexels_alt and len(pexels_alt.strip()) >= 4:
        # The photo's own alt text describes what it ACTUALLY shows. Build
        # the caption from that — never from a description written before
        # the image was sourced (2026-10-11: a writer's caption for an
        # imagined 'restaurant dining room' survived a backfill that
        # sourced a city skyline, and the mismatch went live).
        alt = pexels_alt.strip().rstrip(".")
        caption = alt[0].upper() + alt[1:] + " (file photo)"
    elif source_name == "person_profile" and winner_person:
        # Factual, plain: the verified subject's name (photo is their
        # institutional profile portrait).
        caption = winner_person
    elif entities and len(entities) > 0 and isinstance(entities[0], str):
        caption = entities[0]
    
    print(f"    ✅ Hero image ready: {source_name} → {final_url[-60:]}")
    return final_url, attribution, caption, source_name


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
    parser.add_argument("--official-url",
                        help="Writer-provided official source URL (government/company page) — fetches its image directly, skipping search")
    args = parser.parse_args()

    # Writer-provided official URL → global for the sourcing chain
    # (fetch_official_source_image checks this before auto-discovery)
    global _WRITER_OFFICIAL_URL
    _WRITER_OFFICIAL_URL = args.official_url or None

    if args.test_url:
        print(f"Testing og:image fetch for: {args.test_url}")
        og = fetch_og_image(args.test_url)
        print(f"  og:image: {og}")
        if og:
            ok, ct, _ = verify_image_url(og)
            print(f"  Verified: {ok} ({ct})")

    elif args.article_json:
        article = json.loads(args.article_json)
        url, attr, caption, src_name = source_hero_image(article)
        result = {"image_url": url, "attribution": attr, "caption": caption, "image_source": src_name}
        if article.get("focal_x") is not None:
            result["focal_x"] = article["focal_x"]
            result["focal_y"] = article["focal_y"]
        if article.get("img_w"):
            result["img_w"] = article["img_w"]
            result["img_h"] = article["img_h"]
        print("IMAGE_RESULT:" + json.dumps(result))

    elif args.slug:
        # NOTE: the image-write lock is taken only around the DB PATCH below,
        # not during the (slow) network sourcing — see _acquire_image_lock.
        # Fetch article from DB and source its image
        r = _safe_run(
            ["curl", "-s",
             f"{SUPABASE_URL}/rest/v1/p2_articles?select=id,headline,slug,category,topic_id,sources,tags,image_search_query,image_entities,image_backfill_blocked&slug=eq.{args.slug}&limit=1",
             "-H", f"apikey: {SUPABASE_KEY}",
             "-H", f"Authorization: Bearer {SUPABASE_KEY}"],
            capture_output=True, text=True, timeout=30
        )
        rows = json.loads(r.stdout) if r.stdout and r.stdout.strip() else None
        if rows is None:
            print(f"ERROR: Failed to fetch article (empty response, exit={r.returncode}) for slug '{args.slug}'")
            sys.exit(1)
        if not rows:
            print(f"ERROR: No article found with slug '{args.slug}'")
            sys.exit(1)
        article = rows[0]
        if article.get("image_backfill_blocked"):
            print(f"SKIP: article '{args.slug}' has image_backfill_blocked=true — leaving imageless per standing decision.")
            sys.exit(0)
        url, attr, caption, src_name = source_hero_image(article)
        if url:
            print(f"\n  Image found: {url[:80]}")
            if args.apply:
                patch = {"image_url": url, "image_attribution": attr}
                if caption:
                    patch["image_caption"] = caption
                if article.get("focal_x") is not None:
                    patch["focal_x"] = article["focal_x"]
                    patch["focal_y"] = article["focal_y"]
                _lfh = _acquire_image_lock()
                if _lfh is None:
                    print("  DB update: ⚠ could not acquire image-write lock in 30s — image NOT saved")
                else:
                    try:
                        if _patch_article_and_verify(f"slug=eq.{args.slug}", patch):
                            print("  DB update: ✅ confirmed (1 row updated)")
                        else:
                            print("  DB update: ⚠ PATCH matched no rows — image NOT saved")
                    finally:
                        _lfh.close()  # release image-write lock
            else:
                print("  (dry run — use --apply to update DB)")
        else:
            print("  No image found across all sources.")
        result = {"image_url": url, "attribution": attr, "caption": caption, "image_source": src_name}
        print("IMAGE_RESULT:" + json.dumps(result))

    elif args.backfill:
        from datetime import datetime, timedelta, timezone
        # NOTE: the image-write lock is taken per-PATCH below, not for the
        # whole backfill run — see _acquire_image_lock.
        cutoff = (datetime.now(timezone.utc) - timedelta(hours=args.hours)).strftime("%Y-%m-%dT%H:%M:%SZ")
        print(f"Backfilling hero images for articles published since {cutoff}...")
        encoded_cutoff = urllib.parse.quote(cutoff, safe='')
        r = _safe_run(
            ["curl", "-s",
             f"{SUPABASE_URL}/rest/v1/p2_articles?select=id,headline,slug,category,topic_id,sources,tags"
             f"&status=eq.published&image_url=is.null&image_backfill_blocked=is.false&published_at=gte.{encoded_cutoff}"
             f"&order=published_at.desc",
             "-H", f"apikey: {SUPABASE_KEY}",
             "-H", f"Authorization: Bearer {SUPABASE_KEY}"],
            capture_output=True, text=True, timeout=15
        )
        rows = json.loads(r.stdout) if r.stdout and r.stdout.strip() else None
        if rows is None:
            print(f"ERROR: Failed to fetch articles for backfill (empty response, exit={r.returncode})")
            sys.exit(1)
        if not rows:
            print("No articles missing hero images.")
            sys.exit(0)
        print(f"Found {len(rows)} articles missing hero images.\n")
        used = set()
        fixed = 0
        failed = 0
        for article in rows:
            url, attr, caption, _src = source_hero_image(article, used_images=used)
            if url:
                used.add(url)
                if args.apply:
                    patch = {"image_url": url, "image_attribution": attr}
                    if caption:
                        patch["image_caption"] = caption
                    if article.get("focal_x") is not None:
                        patch["focal_x"] = article["focal_x"]
                        patch["focal_y"] = article["focal_y"]
                    _lfh = _acquire_image_lock()
                    if _lfh is None:
                        failed += 1
                        print(f"    ⚠ lock timeout — image NOT saved for {article.get('slug')}")
                    else:
                        try:
                            if _patch_article_and_verify(f"id=eq.{article['id']}", patch):
                                fixed += 1
                                print(f"    ✅ DB updated")
                            else:
                                failed += 1
                                print(f"    ⚠ PATCH matched no rows — image NOT saved")
                        finally:
                            _lfh.close()  # release image-write lock
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
