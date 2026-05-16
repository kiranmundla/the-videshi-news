#!/usr/bin/env python3
"""
videshi-pexels.py — Pexels API image sourcing for The Videshi pipeline.

Searches Pexels for article-relevant images. Downloads, crops to 16:9,
resizes, and uploads to Supabase Storage.

Usage:
    python3 videshi-pexels.py search "headline text" --category news
    python3 videshi-pexels.py test                    # Test API connectivity

Requires PEXELS_API_KEY in environment or ~/workspace/.env.pexels
"""

import io
import json
import os
import re
import sys
import requests
from PIL import Image, ImageEnhance

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

PEXELS_API_URL = "https://api.pexels.com/v1/search"
PEXELS_ENV_FILE = os.path.expanduser("~/workspace/.env.pexels")
SUPABASE_ENV_FILE = os.path.expanduser("~/workspace/.env.supabase")

TARGET_WIDTH = 1200
TARGET_HEIGHT = 675
JPEG_QUALITY = 88

# Stop words for keyword extraction
STOP_WORDS = {
    "the", "a", "an", "in", "on", "at", "to", "for", "of", "and", "or",
    "is", "was", "are", "were", "be", "been", "being", "has", "had", "have",
    "do", "does", "did", "will", "would", "could", "should", "may", "might",
    "shall", "can", "with", "by", "from", "as", "into", "through", "during",
    "before", "after", "above", "below", "between", "under", "over", "about",
    "up", "out", "off", "its", "his", "her", "their", "our", "my", "your",
    "this", "that", "these", "those", "it", "he", "she", "they", "we", "you",
    "not", "no", "but", "so", "if", "than", "too", "very", "just", "also",
    "new", "says", "said", "after", "amid", "how", "why", "what",
}

# Category → fallback search terms when headline extraction is weak
CATEGORY_FALLBACK_TERMS = {
    "news": "India government parliament",
    "nri-world": "Indian diaspora abroad",
    "markets-finance": "stock market trading India",
    "technology": "technology India startup",
    "sports": "cricket India stadium",
    "entertainment": "Bollywood cinema India",
    "lifestyle-health": "yoga wellness India",
    "travel": "India travel landmark",
    "food": "Indian cuisine food",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_pexels_key():
    """Load Pexels API key from env var or .env.pexels file."""
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


def load_supabase_env():
    """Load Supabase credentials."""
    env = {}
    if os.path.exists(SUPABASE_ENV_FILE):
        with open(SUPABASE_ENV_FILE) as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip()
    return env


def extract_search_terms(headline, category=None):
    """
    Extract 2-4 search keywords from headline.
    Focuses on proper nouns and significant terms.
    """
    if not headline:
        return CATEGORY_FALLBACK_TERMS.get(category, "India news")

    # Clean up
    text = re.sub(r"[^a-zA-Z0-9\s'-]", " ", headline)
    words = text.split()

    # Keep proper nouns (capitalized words) and significant words
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

    # Build search query: prefer proper nouns, supplement with keywords
    search_parts = proper_nouns[:3]
    if len(search_parts) < 2:
        search_parts.extend(keywords[:2])

    if not search_parts:
        return CATEGORY_FALLBACK_TERMS.get(category, "India news")

    # Limit to 4 terms for focused results
    return " ".join(search_parts[:4])


def search_pexels(api_key, query, per_page=5):
    """Search Pexels API and return photo results."""
    headers = {"Authorization": api_key}
    params = {
        "query": query,
        "per_page": per_page,
        "orientation": "landscape",
    }

    try:
        resp = requests.get(PEXELS_API_URL, headers=headers, params=params, timeout=15)
        if resp.status_code == 401:
            print("  ⚠ Pexels API: Invalid API key")
            return []
        if resp.status_code == 429:
            print("  ⚠ Pexels API: Rate limit exceeded")
            return []
        resp.raise_for_status()
        data = resp.json()
        return data.get("photos", [])
    except requests.RequestException as e:
        print(f"  ⚠ Pexels API error: {e}")
        return []


def pick_best_photo(photos, headline):
    """Pick the best photo from Pexels results based on relevance."""
    if not photos:
        return None

    headline_lower = headline.lower()
    headline_words = set(headline_lower.split())

    best = None
    best_score = -1

    for photo in photos:
        score = 0
        alt = (photo.get("alt") or "").lower()

        # Score based on alt text relevance
        alt_words = set(alt.split())
        overlap = len(headline_words & alt_words)
        score += overlap * 2

        # Prefer larger images
        width = photo.get("width", 0)
        if width >= 1200:
            score += 2
        elif width >= 800:
            score += 1

        # Prefer landscape
        height = photo.get("height", 1)
        if width / height >= 1.3:
            score += 1

        if score > best_score:
            best_score = score
            best = photo

    return best


def download_and_process(image_url):
    """Download image, resize to 1200px wide, enhance. Returns JPEG bytes or None."""
    try:
        resp = requests.get(image_url, timeout=30, stream=True)
        resp.raise_for_status()

        content = b""
        for chunk in resp.iter_content(chunk_size=65536):
            content += chunk
            if len(content) > 20 * 1024 * 1024:
                print("    ⚠ Image too large (>20MB)")
                return None

        img = Image.open(io.BytesIO(content))

        # Convert to RGB
        if img.mode != "RGB":
            img = img.convert("RGB")

        # Skip tiny images
        if img.width < 400 or img.height < 200:
            print(f"    ⚠ Image too small ({img.width}x{img.height})")
            return None

        # Resize to max width 1200, preserving aspect ratio
        if img.width > TARGET_WIDTH:
            ratio = TARGET_WIDTH / img.width
            new_height = int(img.height * ratio)
            img = img.resize((TARGET_WIDTH, new_height), Image.LANCZOS)

        # Subtle enhancement
        img = ImageEnhance.Sharpness(img).enhance(1.15)
        img = ImageEnhance.Contrast(img).enhance(1.05)
        img = ImageEnhance.Color(img).enhance(1.05)

        # Save as JPEG
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=JPEG_QUALITY, optimize=True)
        return buffer.getvalue()

    except Exception as e:
        print(f"    ⚠ Download/process failed: {e}")
        return None


def upload_to_supabase(env, filename, jpeg_bytes):
    """Upload JPEG to Supabase Storage. Returns public URL or None."""
    url = env.get("SUPABASE_URL", "")
    key = env.get("SUPABASE_SERVICE_ROLE_KEY", "")

    if not url or not key:
        print("    ⚠ Supabase credentials not found")
        return None

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
        print(f"    ⚠ Supabase upload failed: {e}")
        return None


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_search(headline, category=None, article_id=None):
    """Search Pexels for an article image."""
    api_key = load_pexels_key()
    if not api_key:
        print(json.dumps({
            "found": False,
            "reason": "No PEXELS_API_KEY configured. Get one free at https://www.pexels.com/api/"
        }))
        return

    search_query = extract_search_terms(headline, category)
    print(f"  🔍 Pexels search: \"{search_query}\"")

    photos = search_pexels(api_key, search_query)
    if not photos:
        print(json.dumps({"found": False, "reason": "No results from Pexels"}))
        return

    best = pick_best_photo(photos, headline)
    if not best:
        print(json.dumps({"found": False, "reason": "No suitable photo found"}))
        return

    photographer = best.get("photographer", "Unknown")
    pexels_url = best.get("url", "")
    # Use large2x for high quality, fallback to large
    src = best.get("src", {})
    image_url = src.get("large2x") or src.get("large") or src.get("original", "")

    if not image_url:
        print(json.dumps({"found": False, "reason": "No image URL in result"}))
        return

    print(f"  📸 Found: {best.get('alt', '')[:60]} by {photographer}")

    # If article_id provided, download, process, and upload
    if article_id:
        sb_env = load_supabase_env()
        jpeg_bytes = download_and_process(image_url)
        if jpeg_bytes:
            filename = f"pexels-{article_id}.jpg"
            uploaded_url = upload_to_supabase(sb_env, filename, jpeg_bytes)
            if uploaded_url:
                # Add dimension hints
                img = Image.open(io.BytesIO(jpeg_bytes))
                uploaded_url = f"{uploaded_url}?w={img.width}&h={img.height}"
                result = {
                    "found": True,
                    "image_url": uploaded_url,
                    "photographer": photographer,
                    "pexels_url": pexels_url,
                    "attribution": f"Photo by {photographer} / Pexels",
                }
                print(json.dumps(result))
                return

    # Return the raw Pexels URL info (for preview or manual use)
    result = {
        "found": True,
        "image_url": image_url,
        "photographer": photographer,
        "pexels_url": pexels_url,
        "attribution": f"Photo by {photographer} / Pexels",
    }
    print(json.dumps(result))


def cmd_test():
    """Test Pexels API connectivity."""
    api_key = load_pexels_key()
    if not api_key:
        print("❌ No PEXELS_API_KEY found.")
        print(f"   Set it in {PEXELS_ENV_FILE} or as environment variable.")
        print(f"   Get a free key at https://www.pexels.com/api/")
        return

    print(f"🔑 API key found: {api_key[:8]}...")
    photos = search_pexels(api_key, "India temple", per_page=1)
    if photos:
        print(f"✅ Pexels API working! Got {len(photos)} result(s)")
        print(f"   Sample: {photos[0].get('alt', 'N/A')[:80]}")
    else:
        print("❌ No results returned — check API key validity")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "search":
        if len(sys.argv) < 3:
            print("Usage: videshi-pexels.py search \"headline\" [--category CAT] [--id ARTICLE_UUID]")
            sys.exit(1)
        headline = sys.argv[2]
        category = None
        article_id = None
        for i, arg in enumerate(sys.argv[3:], start=3):
            if arg == "--category" and i + 1 < len(sys.argv):
                category = sys.argv[i + 1]
            if arg == "--id" and i + 1 < len(sys.argv):
                article_id = sys.argv[i + 1]
        cmd_search(headline, category, article_id)

    elif cmd == "test":
        cmd_test()
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
