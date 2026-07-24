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

def fetch_og_image(source_url):
    """Fetch og:image meta tag from a source article URL.
    Returns image URL or None.
    """
    if not source_url:
        return None
    
    try:
        # Fetch just the head of the page (first 50KB should contain meta tags)
        result = subprocess.run(
            ["curl", "-sS", "-L", "--max-time", "8", "-r", "0-51200",
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
                img_url = match.group(1).strip()
                # Skip data URIs and tiny placeholders
                if img_url.startswith("data:"):
                    continue
                # Make relative URLs absolute
                if img_url.startswith("//"):
                    img_url = "https:" + img_url
                elif img_url.startswith("/"):
                    from urllib.parse import urlparse
                    parsed = urlparse(source_url)
                    img_url = f"{parsed.scheme}://{parsed.netloc}{img_url}"
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
        return [s["original_url"] for s in data if s.get("original_url")]
    except:
        return []


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


# ── Source 4: Wikipedia ──────────────────────────────────────────────────────

def fetch_wikipedia_image(entity_name):
    """Fetch image from Wikipedia REST API for a person/entity.
    Returns image URL or None.
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
        if img:
            return img
        return None
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
                 image_entities, image_must_show
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
    
    # ── Source 1: og:image from source articles ──────────────────────────
    if not img_url:
        source_urls = fetch_source_urls(topic_id) if topic_id else []
        for src_url in source_urls[:3]:
            og_img = fetch_og_image(src_url)
            if og_img and og_img not in used_images:
                ok, ctype, _ = verify_image_url(og_img)
                if ok:
                    img_url = og_img
                    # Attribution from source domain
                    try:
                        domain = urllib.parse.urlparse(src_url).netloc.replace("www.", "")
                        attribution = domain
                    except:
                        attribution = "Source Article"
                    source_name = "og:image"
                    print(f"    ✓ og:image from {attribution}")
                    break
    
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
    
    # ── Source 4: Wikipedia person image ─────────────────────────────────
    if not img_url and entities:
        for entity in entities[:3]:
            if isinstance(entity, str) and len(entity) > 2:
                wp_img = fetch_wikipedia_image(entity)
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
    
    # Compress
    compressed = compress_image(raw_bytes)
    
    # Upload
    filename = f"{slug}.jpg"
    final_url = upload_to_supabase(compressed, filename)
    if not final_url:
        print(f"    ✗ Upload to Supabase failed")
        return None, None, None
    
    # Caption — keep factual, only use first entity name if confident
    caption = None
    if entities and len(entities) > 0 and isinstance(entities[0], str):
        caption = entities[0]
    
    print(f"    ✅ Hero image ready: {source_name} → {final_url[-40:]}")
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
    # Test the image chain
    import sys
    test_url = sys.argv[1] if len(sys.argv) > 1 else "https://en.wikipedia.org/api/rest_v1/page/summary/Narendra_Modi"
    print(f"Testing og:image fetch for: {test_url}")
    og = fetch_og_image(test_url)
    print(f"  og:image: {og}")
    if og:
        ok, ct, _ = verify_image_url(og)
        print(f"  Verified: {ok} ({ct})")
