#!/usr/bin/env python3
"""
videshi-images.py — Image sourcing for The Videshi news pipeline.

Searches Wikipedia page images (primary) and Wikimedia Commons (fallback)
for relevant, high-quality images and updates article image_url and
image_attribution fields in Supabase.

Usage:
    python3 videshi-images.py fetch              # Articles missing images
    python3 videshi-images.py fetch --refresh     # Also replace bad images
    python3 videshi-images.py fetch --id <UUID>   # Specific article
"""

import json
import os
import re
import sys
import time
import urllib.parse
import requests

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

ENV_FILE = os.path.expanduser("~/workspace/.env.supabase")
WIKIPEDIA_API = "https://en.wikipedia.org/w/api.php"
WIKIMEDIA_API = "https://commons.wikimedia.org/w/api.php"
USER_AGENT = "TheVideshiBot/1.0 (https://thevideshi.com; contact@thevideshi.com)"
POLITE_DELAY = 1.0          # seconds between API calls
THUMB_WIDTH = 800            # target width for thumbnails
MIN_SOURCE_WIDTH = 400       # reject originals narrower than this
MAX_RESULTS = 10             # results per Wikimedia search

# Patterns that indicate a bad / unusable image file name
BAD_FILENAME_RE = re.compile(
    r"Flag_of|flag_of|Map_of|map_of|Logo|logo|Icon|icon|"
    r"Coat_of_arms|coat_of_arms|seal_of|Seal_of|emblem|Emblem|"
    r"globe|Globe|locator|Locator|location_map|Location_map|"
    r"pictogram|Pictogram|symbol|Symbol|no_image|placeholder",
    re.IGNORECASE,
)

# Patterns for existing URLs we consider "bad" and want to replace
BAD_URL_RE = re.compile(
    r"hindustantimes\.com|htmedia|\.svg$|Flag_of_|flag_of_|"
    r"logo|icon|placeholder|default|thumbnail.*small|"
    r"upload\.wikimedia.*(?:map|globe|location|locator)",
    re.IGNORECASE,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_env():
    """Load Supabase credentials from the env file."""
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


def is_bad_url(url):
    """Return True if the URL is missing or looks low-quality."""
    if not url or not isinstance(url, str) or len(url.strip()) < 20:
        return True
    return bool(BAD_URL_RE.search(url))


def strip_html(text):
    """Remove HTML tags from attribution strings."""
    return re.sub(r"<[^>]+>", "", text).strip() if text else ""


def is_bad_filename(name):
    """Check if an image filename matches bad patterns."""
    return bool(BAD_FILENAME_RE.search(name))

# ---------------------------------------------------------------------------
# Wikipedia page image lookup (PRIMARY SOURCE)
# ---------------------------------------------------------------------------

def search_wikipedia_image(entity):
    """
    Look up the Wikipedia article for `entity` and return its lead image.
    Returns (thumb_url, attribution) or (None, None).
    """
    # Normalise entity to a plausible Wikipedia title
    title = entity.strip().replace(" ", "_")
    params = {
        "action": "query",
        "titles": title,
        "prop": "pageimages|pageprops",
        "piprop": "original|thumbnail",
        "pithumbsize": THUMB_WIDTH,
        "format": "json",
        "redirects": 1,
    }
    headers = {"User-Agent": USER_AGENT}

    try:
        resp = requests.get(WIKIPEDIA_API, params=params, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"    ⚠ Wikipedia API error: {e}")
        return None, None

    pages = data.get("query", {}).get("pages", {})
    for page_id, page in pages.items():
        if page_id == "-1":
            continue  # page not found

        # Get thumbnail (preferred — pre-sized to 800px)
        thumb = page.get("thumbnail", {})
        thumb_url = thumb.get("source")
        thumb_w = thumb.get("width", 0)
        thumb_h = thumb.get("height", 0)

        # Get original as fallback
        original = page.get("original", {})
        orig_url = original.get("source")
        orig_w = original.get("width", 0)
        orig_h = original.get("height", 0)

        # Pick the best URL
        chosen_url = thumb_url or orig_url
        chosen_w = thumb_w or orig_w
        chosen_h = thumb_h or orig_h

        if not chosen_url:
            continue

        # Filter bad images
        if is_bad_filename(chosen_url):
            continue
        if chosen_url.lower().endswith(".svg"):
            continue
        if chosen_url.lower().endswith(".pdf"):
            continue
        if chosen_w > 0 and chosen_w < MIN_SOURCE_WIDTH:
            continue

        # Clean tracking params
        chosen_url = chosen_url.split("?")[0]

        # Wikipedia images are typically CC-licensed or public domain
        page_title = page.get("title", entity)
        attribution = f"Wikipedia — {page_title}"

        return chosen_url, attribution

    return None, None


def search_wikipedia_for_article(article):
    """
    Try Wikipedia page image lookups for each entity in the article.
    Returns (thumb_url, attribution) or (None, None).
    """
    entities = article.get("image_entities")
    if not entities or not isinstance(entities, list):
        return None, None

    for entity in entities:
        if not entity or not isinstance(entity, str) or len(entity.strip()) < 2:
            continue
        print(f"  🌐 Wikipedia lookup: \"{entity}\"")
        url, attr = search_wikipedia_image(entity)
        if url:
            print(f"  ✅ Found via Wikipedia: {entity}")
            return url, attr
        time.sleep(POLITE_DELAY)

    # Also try the headline's key nouns as Wikipedia titles
    headline = article.get("headline", "")
    if headline:
        # Extract capitalised multi-word phrases likely to be entity names
        # e.g. "Ro Khanna", "Alabama", "Tamil Nadu"
        words = headline.split()
        # Try 2-word combos of capitalised words
        bigrams = []
        for i in range(len(words) - 1):
            w1, w2 = words[i], words[i + 1]
            if (w1[0:1].isupper() and w2[0:1].isupper()
                    and len(w1) > 1 and len(w2) > 1
                    and w1.lower() not in ("the", "for", "and", "from", "with", "that", "would", "will", "has", "its")):
                bigrams.append(f"{w1} {w2}")
        # Try up to 2 bigrams
        for bigram in bigrams[:2]:
            print(f"  🌐 Wikipedia lookup (headline): \"{bigram}\"")
            url, attr = search_wikipedia_image(bigram)
            if url:
                print(f"  ✅ Found via Wikipedia headline: {bigram}")
                return url, attr
            time.sleep(POLITE_DELAY)

    return None, None

# ---------------------------------------------------------------------------
# Wikimedia Commons search (FALLBACK SOURCE)
# ---------------------------------------------------------------------------

def search_wikimedia(query, limit=MAX_RESULTS):
    """Search Wikimedia Commons and return filtered image candidates."""
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": query,
        "gsrnamespace": 6,        # File namespace
        "gsrlimit": limit,
        "prop": "imageinfo",
        "iiprop": "url|size|mime|extmetadata",
        "iiurlwidth": THUMB_WIDTH,
        "format": "json",
    }
    headers = {"User-Agent": USER_AGENT}
    try:
        resp = requests.get(WIKIMEDIA_API, params=params, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"    ⚠ Wikimedia API error: {e}")
        return []

    pages = data.get("query", {}).get("pages", {})
    if not pages:
        return []

    candidates = []
    for page in pages.values():
        title = page.get("title", "")
        info_list = page.get("imageinfo", [])
        if not info_list:
            continue
        info = info_list[0]

        mime = info.get("mime", "")
        width = info.get("width", 0)
        height = info.get("height", 0)

        if "svg" in mime.lower():
            continue
        if "pdf" in mime.lower():
            continue
        if width < MIN_SOURCE_WIDTH:
            continue
        if is_bad_filename(title):
            continue
        # Reject PDFs disguised as images (filename check)
        if title.lower().endswith(".pdf"):
            continue
        if height > 0 and width > 0:
            ratio = width / height
            if ratio > 4.0 or ratio < 0.33:
                continue

        ext = info.get("extmetadata", {})
        artist_raw = ext.get("Artist", {}).get("value", "")
        artist = strip_html(artist_raw) or "Unknown"
        license_name = ext.get("LicenseShortName", {}).get("value", "")

        thumb_url = info.get("thumburl", "")
        if thumb_url:
            thumb_url = thumb_url.split("?")[0]

        full_url = info.get("url", "")
        if full_url:
            full_url = full_url.split("?")[0]

        is_landscape = width >= height
        score = 0
        if is_landscape:
            score += 50
        if width >= 800:
            score += 30
        elif width >= 600:
            score += 15
        if thumb_url:
            score += 20
        categories = ext.get("Categories", {}).get("value", "").lower()
        if any(kw in categories for kw in ["official", "portrait", "government", "congress"]):
            score += 15

        candidates.append({
            "title": title,
            "thumb_url": thumb_url,
            "full_url": full_url,
            "width": width,
            "height": height,
            "mime": mime,
            "artist": artist,
            "license": license_name,
            "score": score,
            "is_landscape": is_landscape,
        })

    candidates.sort(key=lambda c: c["score"], reverse=True)
    return candidates


def search_wikimedia_for_article(article):
    """
    Try Wikimedia Commons searches using various article fields.
    Returns (thumb_url, attribution) or (None, None).
    """
    headline = article.get("headline", "")

    # Try 1: image_search_query
    isq = article.get("image_search_query")
    if isq and isinstance(isq, str) and isq.strip():
        print(f"  🔍 Commons search: \"{isq}\"")
        candidates = search_wikimedia(isq)
        if candidates:
            best = candidates[0]
            url = best["thumb_url"] or best["full_url"]
            attr = format_commons_attribution(best)
            print(f"  ✅ Found via Commons search query: {best['title'][:60]}")
            return url, attr
        time.sleep(POLITE_DELAY)

    # Try 2: image_entities one by one
    entities = article.get("image_entities")
    if entities and isinstance(entities, list):
        for entity in entities[:3]:
            if not entity or not isinstance(entity, str):
                continue
            print(f"  🔍 Commons entity: \"{entity}\"")
            candidates = search_wikimedia(entity)
            if candidates:
                best = candidates[0]
                url = best["thumb_url"] or best["full_url"]
                attr = format_commons_attribution(best)
                print(f"  ✅ Found via Commons entity: {best['title'][:60]}")
                return url, attr
            time.sleep(POLITE_DELAY)

    # Try 3: first few tags
    tags = article.get("tags")
    if tags and isinstance(tags, list):
        tag_query = " ".join(tags[:3])
        print(f"  🔍 Commons tags: \"{tag_query}\"")
        candidates = search_wikimedia(tag_query)
        if candidates:
            best = candidates[0]
            url = best["thumb_url"] or best["full_url"]
            attr = format_commons_attribution(best)
            print(f"  ✅ Found via Commons tags: {best['title'][:60]}")
            return url, attr
        time.sleep(POLITE_DELAY)

    # Try 4: headline keywords
    if headline:
        words = [w for w in headline.split() if len(w) > 3][:5]
        if words:
            kw_query = " ".join(words)
            print(f"  🔍 Commons headline: \"{kw_query}\"")
            candidates = search_wikimedia(kw_query)
            if candidates:
                best = candidates[0]
                url = best["thumb_url"] or best["full_url"]
                attr = format_commons_attribution(best)
                print(f"  ✅ Found via Commons headline: {best['title'][:60]}")
                return url, attr
            time.sleep(POLITE_DELAY)

    return None, None


def format_commons_attribution(candidate):
    """Build a clean attribution string for Wikimedia Commons images."""
    artist = candidate.get("artist", "Unknown")
    license_name = candidate.get("license", "")
    if license_name:
        return f"{artist} / Wikimedia Commons ({license_name})"
    return f"{artist} / Wikimedia Commons"

# ---------------------------------------------------------------------------
# Combined image search — Wikipedia first, then Commons
# ---------------------------------------------------------------------------

def find_image_for_article(article):
    """
    Search for an image using a tiered strategy:
      1. Wikipedia page images (best for specific entities — people, places, orgs)
      2. Wikimedia Commons search (broader, editorial images)
    Returns (thumb_url, attribution) or (None, None).
    """
    # --- Tier 1: Wikipedia page images ---
    print("  📖 Tier 1: Wikipedia page images")
    url, attr = search_wikipedia_for_article(article)
    if url:
        return url, attr

    # --- Tier 2: Wikimedia Commons search ---
    print("  📚 Tier 2: Wikimedia Commons search")
    url, attr = search_wikimedia_for_article(article)
    if url:
        return url, attr

    print(f"  ❌ No suitable image found")
    return None, None

# ---------------------------------------------------------------------------
# Supabase operations
# ---------------------------------------------------------------------------

def fetch_articles_needing_images(env, refresh=False, article_id=None):
    """Get articles that need images from Supabase."""
    url = env["SUPABASE_URL"]
    key = env["SUPABASE_SERVICE_ROLE_KEY"]
    headers = supabase_headers(key)
    del headers["Prefer"]  # not needed for GET

    cols = "id,headline,image_url,image_search_query,image_entities,tags"
    articles = []

    if article_id:
        api_url = f"{url}/rest/v1/p2_articles?select={cols}&id=eq.{article_id}"
        resp = requests.get(api_url, headers=headers, timeout=15)
        resp.raise_for_status()
        articles = resp.json()
    else:
        # Articles with NULL or empty image_url
        api_url = (
            f"{url}/rest/v1/p2_articles?select={cols}"
            f"&status=eq.published"
            f"&or=(image_url.is.null,image_url.eq.)"
            f"&order=created_at.desc&limit=30"
        )
        resp = requests.get(api_url, headers=headers, timeout=15)
        resp.raise_for_status()
        articles = resp.json()

        if refresh:
            # In refresh mode, get ALL published articles and re-source images
            api_url2 = (
                f"{url}/rest/v1/p2_articles?select={cols}"
                f"&status=eq.published"
                f"&order=created_at.desc&limit=50"
            )
            resp2 = requests.get(api_url2, headers=headers, timeout=15)
            resp2.raise_for_status()
            existing_ids = {a["id"] for a in articles}
            for a in resp2.json():
                if a["id"] not in existing_ids:
                    articles.append(a)

    return articles


def update_article_image(env, article_id, image_url, attribution):
    """Update image_url and image_attribution for an article."""
    url = env["SUPABASE_URL"]
    key = env["SUPABASE_SERVICE_ROLE_KEY"]
    headers = supabase_headers(key)

    api_url = f"{url}/rest/v1/p2_articles?id=eq.{article_id}"
    payload = {"image_url": image_url}
    if attribution:
        payload["image_attribution"] = attribution

    resp = requests.patch(api_url, headers=headers, json=payload, timeout=15)
    resp.raise_for_status()

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def cmd_fetch(args):
    """Fetch and assign images to articles."""
    env = load_env()

    refresh = "--refresh" in args
    article_id = None
    if "--id" in args:
        idx = args.index("--id")
        if idx + 1 < len(args):
            article_id = args[idx + 1]
        else:
            print("ERROR: --id requires an article UUID")
            sys.exit(1)

    print("=" * 60)
    print("📷 Videshi Image Sourcing")
    print("   Tier 1: Wikipedia page images")
    print("   Tier 2: Wikimedia Commons search")
    print("=" * 60)

    articles = fetch_articles_needing_images(env, refresh=refresh, article_id=article_id)

    if not articles:
        print("\n✅ No articles need images right now.")
        return

    print(f"\n📰 Found {len(articles)} article(s) needing images\n")

    sourced = 0
    skipped = 0
    failed = 0

    for i, article in enumerate(articles):
        headline = article.get("headline", "Unknown")
        aid = article["id"]
        current_url = article.get("image_url")

        print(f"\n[{i+1}/{len(articles)}] {headline[:70]}")
        if current_url:
            print(f"  Current image (bad): {current_url[:80]}...")

        img_url, attribution = find_image_for_article(article)

        if img_url:
            try:
                update_article_image(env, aid, img_url, attribution)
                print(f"  💾 Updated — {attribution}")
                sourced += 1
            except Exception as e:
                print(f"  ⚠ Failed to update Supabase: {e}")
                failed += 1
        else:
            skipped += 1

    print(f"\n{'=' * 60}")
    print(f"📊 Results: {sourced} sourced, {skipped} no match, {failed} errors")
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
