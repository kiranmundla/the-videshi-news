#!/usr/bin/env python3
"""
Shared media sourcing module for The Videshi pipeline.
Provides:
  1. YouTube trailer search (for movies/series/shows)
  2. Google CSE image search with CC license filter (when enabled)
  3. TMDB image search (when API key available)
  4. Content-type detection (movie, series, person, general)

Usage:
  from media_sources import (
      detect_content_type, search_youtube_trailer,
      search_google_images, source_best_image
  )

  # Detect what kind of article this is
  ctype = detect_content_type(headline, body)
  # ctype = "movie" | "series" | "person" | "general"

  # Find a YouTube trailer if it's a movie/series
  if ctype in ("movie", "series"):
      trailer_url = search_youtube_trailer(headline, ctype)
      if trailer_url:
          body += f"\n\n<youtube>{trailer_url}</youtube>\n"

  # Find better images
  image_url, caption = source_best_image(headline, ctype)
"""

import os, re, json, subprocess, time
import requests
from urllib.parse import quote, quote_plus

PIPELINE_DIR = os.path.dirname(os.path.abspath(__file__))

def _load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

_load_env(os.path.expanduser("~/workspace/.env.supabase"))

GOOGLE_CSE_KEY = os.environ.get("GOOGLE_CSE_KEY", "")
GOOGLE_CSE_ID = os.environ.get("GOOGLE_CSE_ID", "")


# ═══════════════════════════════════════════════════════════
# CONTENT TYPE DETECTION
# ═══════════════════════════════════════════════════════════

# Keywords that indicate movie/film content
MOVIE_KEYWORDS = [
    "film", "movie", "box office", "crore", "release date", "releases",
    "trailer", "teaser", "first look", "poster", "blockbuster",
    "directed by", "director", "screenplay", "cinematography",
    "opening weekend", "opening day", "collection", "grossing",
    "theatres", "theaters", "theatrical", "ott release", "streaming on",
    "bollywood", "tollywood", "kollywood", "sandalwood",
    "remake", "sequel", "prequel", "franchise",
]

# Keywords that indicate TV series/show
SERIES_KEYWORDS = [
    "season", "episode", "series", "showrunner", "premiere",
    "streaming", "web series", "ott", "hotstar", "netflix",
    "amazon prime", "jiocinema", "disney+", "hbo", "apple tv",
    "finale", "penultimate", "renewal", "renewed", "cancelled",
    "streaming picks", "what to watch", "binge",
]

# Common Bollywood/Indian film title patterns
FILM_TITLE_PATTERNS = [
    r"releasing? (?:on )?(?:june|july|august|september|october|november|december|january|february|march|april|may) \d+",
    r"₹[\d,]+ crore",
    r"\d+ crore",
    r"box office",
    r"first (?:day|weekend|week)",
    r"day \d+ collection",
]


def detect_content_type(headline, body=""):
    """
    Detect if article is about a movie, series, person, or general topic.
    Returns: "movie" | "series" | "person" | "general"
    """
    text = f"{headline} {body[:500]}".lower()

    movie_score = 0
    series_score = 0

    for kw in MOVIE_KEYWORDS:
        if kw in text:
            movie_score += 1

    for kw in SERIES_KEYWORDS:
        if kw in text:
            series_score += 1

    for pat in FILM_TITLE_PATTERNS:
        if re.search(pat, text):
            movie_score += 2

    # Series wins if it has stronger signals
    if series_score >= 2 and series_score > movie_score:
        return "series"
    if movie_score >= 2:
        return "movie"
    if series_score >= 2:
        return "series"

    return "general"


def extract_title_from_headline(headline, content_type="movie"):
    """
    Extract the movie/series title from a headline.
    E.g. "House of the Dragon Season 3 Premieres June 21" → "House of the Dragon"
    """
    # Remove common suffixes
    clean = re.sub(
        r"(?:Season \d+|S\d+|Episode \d+|Ep \d+|Part \d+|Vol\.? \d+|Chapter \d+).*$",
        "", headline, flags=re.IGNORECASE
    ).strip()

    # Remove trailer/teaser/review etc.
    clean = re.sub(
        r"\s*[-–—:]\s*(?:Official )?(?:Trailer|Teaser|Review|First Look|Poster|Box Office|Collection|Release Date|Premieres?|Streaming|OTT|Watch).*$",
        "", clean, flags=re.IGNORECASE
    ).strip()

    # Remove "Why/How/What" questions
    clean = re.sub(r"^(?:Why|How|What|When|Where)\s+", "", clean, flags=re.IGNORECASE).strip()

    # Remove quotes
    clean = re.sub(r"^['\"""'']+|['\"""'']+$", "", clean).strip()

    # Remove trailing punctuation
    clean = re.sub(r"[.!?,;:]+$", "", clean).strip()

    return clean if len(clean) > 2 else headline[:50]


# ═══════════════════════════════════════════════════════════
# YOUTUBE TRAILER SEARCH
# ═══════════════════════════════════════════════════════════

def _extract_youtube_id(url):
    """Extract video ID from YouTube URL."""
    m = re.search(
        r"(?:youtube\.com/watch\?.*v=|youtu\.be/|youtube\.com/embed/|youtube\.com/shorts/)([A-Za-z0-9_-]{11})",
        url
    )
    return m.group(1) if m else None


def search_youtube_trailer(headline, content_type="movie", body=""):
    """
    Search YouTube for an official trailer for the movie/series.
    Uses Google web search (site:youtube.com) as the search method.
    Returns: YouTube URL string or None
    """
    title = extract_title_from_headline(headline, content_type)
    search_queries = []

    if content_type == "series":
        # Try to detect season number
        season_match = re.search(r"Season\s*(\d+)", headline, re.IGNORECASE)
        if season_match:
            sn = season_match.group(1)
            search_queries.append(f"{title} Season {sn} official trailer")
        search_queries.append(f"{title} official trailer")
    else:
        # Movie
        year_match = re.search(r"20\d{2}", headline)
        year = year_match.group(0) if year_match else ""
        search_queries.append(f"{title} {year} official trailer".strip())
        search_queries.append(f"{title} trailer")

    for query in search_queries:
        try:
            # Use Google Custom Search API if available
            if GOOGLE_CSE_KEY and GOOGLE_CSE_ID:
                url = search_youtube_via_google_cse(query)
                if url:
                    return url

            # Fallback: use yt-dlp for YouTube search
            url = search_youtube_via_ytdlp(query)
            if url:
                return url

        except Exception as e:
            print(f"  ⚠ YouTube search error for '{query}': {e}")
            continue

    return None


def search_youtube_via_google_cse(query):
    """Search YouTube via Google CSE API."""
    try:
        r = requests.get(
            "https://www.googleapis.com/customsearch/v1",
            params={
                "key": GOOGLE_CSE_KEY,
                "cx": GOOGLE_CSE_ID,
                "q": f"site:youtube.com {query}",
                "num": 3,
            },
            timeout=10,
        )
        if r.status_code != 200:
            return None
        data = r.json()
        for item in data.get("items", []):
            link = item.get("link", "")
            vid_id = _extract_youtube_id(link)
            if vid_id:
                title_lower = item.get("title", "").lower()
                # Prefer official trailers
                if "trailer" in title_lower or "official" in title_lower:
                    url = f"https://youtube.com/watch?v={vid_id}"
                    print(f"  ✓ YouTube trailer (Google CSE): {url}")
                    return url
        # If no explicit trailer, take first YouTube result
        for item in data.get("items", []):
            vid_id = _extract_youtube_id(item.get("link", ""))
            if vid_id:
                url = f"https://youtube.com/watch?v={vid_id}"
                print(f"  ✓ YouTube video (Google CSE): {url}")
                return url
    except Exception as e:
        print(f"  ⚠ Google CSE YouTube search error: {e}")
    return None


def search_youtube_via_ytdlp(query, max_results=3):
    """Search YouTube via yt-dlp (no API key needed)."""
    try:
        result = subprocess.run(
            ["yt-dlp", "-j", "--flat-playlist", "--no-warnings",
             f"ytsearch{max_results}:{query}"],
            capture_output=True, text=True, timeout=20,
        )
        if result.returncode != 0:
            return None

        for line in result.stdout.strip().split("\n"):
            if not line.strip():
                continue
            try:
                data = json.loads(line)
                vid_id = data.get("id", "")
                title = data.get("title", "").lower()
                if vid_id and ("trailer" in title or "official" in title):
                    url = f"https://youtube.com/watch?v={vid_id}"
                    print(f"  ✓ YouTube trailer (yt-dlp): {url}")
                    return url
            except json.JSONDecodeError:
                continue

        # Fallback: take first result
        for line in result.stdout.strip().split("\n"):
            if not line.strip():
                continue
            try:
                data = json.loads(line)
                vid_id = data.get("id", "")
                if vid_id:
                    url = f"https://youtube.com/watch?v={vid_id}"
                    print(f"  ✓ YouTube video (yt-dlp): {url}")
                    return url
            except json.JSONDecodeError:
                continue
    except subprocess.TimeoutExpired:
        print("  ⚠ yt-dlp search timed out")
    except Exception as e:
        print(f"  ⚠ yt-dlp search error: {e}")
    return None


# ═══════════════════════════════════════════════════════════
# GOOGLE CSE IMAGE SEARCH
# ═══════════════════════════════════════════════════════════

def search_google_images(query, cc_only=True, num=5):
    """
    Search Google Custom Search for images.
    Returns list of {"url": str, "title": str, "context": str}
    """
    if not GOOGLE_CSE_KEY or not GOOGLE_CSE_ID:
        return []

    params = {
        "key": GOOGLE_CSE_KEY,
        "cx": GOOGLE_CSE_ID,
        "q": query,
        "searchType": "image",
        "num": num,
    }
    if cc_only:
        # Filter by usage rights: Creative Commons
        params["rights"] = "cc_publicdomain|cc_attribute|cc_sharealike"

    try:
        r = requests.get(
            "https://www.googleapis.com/customsearch/v1",
            params=params,
            timeout=10,
        )
        if r.status_code != 200:
            err = r.json().get("error", {}).get("message", "")
            print(f"  ⚠ Google CSE error: {err[:100]}")
            return []

        data = r.json()
        results = []
        for item in data.get("items", []):
            results.append({
                "url": item.get("link", ""),
                "title": item.get("title", ""),
                "context": item.get("image", {}).get("contextLink", ""),
                "width": item.get("image", {}).get("width", 0),
                "height": item.get("image", {}).get("height", 0),
                "source": "google_cse",
            })
        if results:
            print(f"  ✓ Google CSE: {len(results)} images for '{query}'")
        return results
    except Exception as e:
        print(f"  ⚠ Google CSE error: {e}")
        return []


# ═══════════════════════════════════════════════════════════
# OPENVERSE IMAGE SEARCH (existing, consolidated)
# ═══════════════════════════════════════════════════════════

def search_openverse(query, limit=5):
    """Search Openverse for CC-licensed images."""
    try:
        r = requests.get(
            "https://api.openverse.org/v1/images/",
            params={
                "q": query,
                "license": "by,by-sa,by-nd,pdm,cc0",
                "page_size": limit,
            },
            timeout=15,
        )
        if r.status_code != 200:
            return []
        results = []
        for item in r.json().get("results", []):
            w = item.get("width", 0)
            if w < 400:
                continue
            results.append({
                "url": item.get("url", ""),
                "title": item.get("title", ""),
                "width": w,
                "height": item.get("height", 0),
                "license": item.get("license", ""),
                "source": "openverse",
            })
        if results:
            print(f"  ✓ Openverse: {len(results)} images for '{query}'")
        return results
    except Exception as e:
        print(f"  ⚠ Openverse error: {e}")
        return []


# ═══════════════════════════════════════════════════════════
# WIKIMEDIA COMMONS / WIKIPEDIA IMAGE SEARCH
# ═══════════════════════════════════════════════════════════

def search_wikimedia_commons(query, limit=5):
    """Search Wikimedia Commons for CC images."""
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": query,
        "gsrnamespace": "6",
        "gsrlimit": str(limit),
        "prop": "imageinfo",
        "iiprop": "url|size|mime",
        "iiurlwidth": "1200",
        "format": "json",
    }
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params=params,
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=15,
        )
        if r.status_code != 200:
            return []
        pages = r.json().get("query", {}).get("pages", {})
        results = []
        for pid, page in pages.items():
            ii = page.get("imageinfo", [{}])[0]
            mime = ii.get("mime", "")
            if not mime.startswith("image/") or mime == "image/svg+xml":
                continue
            w = ii.get("width", 0)
            if w < 400:
                continue
            results.append({
                "url": ii.get("thumburl") or ii.get("url", ""),
                "original_url": ii.get("url", ""),
                "title": page.get("title", ""),
                "width": w,
                "height": ii.get("height", 0),
                "source": "wikimedia_commons",
            })
        if results:
            print(f"  ✓ Wikimedia Commons: {len(results)} images for '{query}'")
        return results
    except Exception as e:
        print(f"  ⚠ Wikimedia Commons error: {e}")
        return []


def fetch_wikipedia_image(subject):
    """Fetch the main image from a Wikipedia article."""
    encoded = quote(subject.replace(" ", "_"))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10,
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image for '{subject}': {img[:80]}...")
                return {
                    "url": img,
                    "title": data.get("title", subject),
                    "source": "wikipedia",
                }
    except Exception as e:
        print(f"  ⚠ Wikipedia error for '{subject}': {e}")
    return None


# ═══════════════════════════════════════════════════════════
# COMBINED IMAGE SOURCING
# ═══════════════════════════════════════════════════════════

def source_best_image(headline, content_type="general", person_name=None):
    """
    Find the best image for an article, trying multiple sources.
    Priority:
      1. Google CSE (when available) — best for specific movies/shows
      2. Wikipedia (for person articles)
      3. Wikimedia Commons
      4. Openverse

    Returns: (url, caption_text) or (None, None)
    """
    title = extract_title_from_headline(headline, content_type)
    candidates = []

    # Build search queries based on content type
    if content_type in ("movie", "series"):
        queries = [
            f"{title} film",
            f"{title} movie poster",
            f"{title} official",
        ]
        if content_type == "series":
            season_match = re.search(r"Season\s*(\d+)", headline, re.IGNORECASE)
            if season_match:
                queries.insert(0, f"{title} Season {season_match.group(1)}")
    elif person_name:
        queries = [person_name, f"{person_name} actor", f"{person_name} portrait"]
    else:
        queries = [title, headline[:50]]

    # 1. Google CSE (best quality, when available)
    for q in queries[:2]:
        results = search_google_images(q, cc_only=True, num=5)
        for r in results:
            if r.get("width", 0) >= 500:
                candidates.append({**r, "relevance": 4})
        if results:
            break
        time.sleep(0.3)

    # 2. Wikipedia (great for people and well-known movies)
    wiki_subjects = [title]
    if person_name:
        wiki_subjects.insert(0, person_name)
    for subj in wiki_subjects[:2]:
        wiki = fetch_wikipedia_image(subj)
        if wiki:
            candidates.append({**wiki, "relevance": 3})
            break

    # 3. Wikimedia Commons
    for q in queries[:2]:
        wc_results = search_wikimedia_commons(q)
        for r in wc_results[:3]:
            candidates.append({**r, "relevance": 2})
        if wc_results:
            break
        time.sleep(0.3)

    # 4. Openverse
    for q in queries[:2]:
        ov_results = search_openverse(q)
        for r in ov_results[:3]:
            candidates.append({**r, "relevance": 1})
        if ov_results:
            break
        time.sleep(0.3)

    # Sort by relevance and return best
    candidates.sort(key=lambda x: x.get("relevance", 0), reverse=True)

    for c in candidates:
        url = c.get("url", "")
        if not url:
            continue
        src = c.get("source", "unknown")
        caption = f"{c.get('title', title)} ({src.replace('_', ' ').title()}, CC)"
        return url, caption

    return None, None


# ═══════════════════════════════════════════════════════════
# TESTING / CLI
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Test media sources")
    parser.add_argument("headline", nargs="?", default="House of the Dragon Season 3 Premieres June 21")
    parser.add_argument("--type", choices=["movie", "series", "person", "general", "auto"], default="auto")
    parser.add_argument("--trailer", action="store_true", help="Search for trailer")
    parser.add_argument("--image", action="store_true", help="Search for image")
    parser.add_argument("--all", action="store_true", help="Test all")
    args = parser.parse_args()

    headline = args.headline
    ctype = args.type if args.type != "auto" else detect_content_type(headline)
    print(f"Headline: {headline}")
    print(f"Detected type: {ctype}")
    print()

    if args.trailer or args.all:
        print("── YouTube Trailer Search ──")
        url = search_youtube_trailer(headline, ctype)
        if url:
            print(f"  Found: {url}")
        else:
            print("  No trailer found")
        print()

    if args.image or args.all:
        print("── Image Search ──")
        img_url, caption = source_best_image(headline, ctype)
        if img_url:
            print(f"  Found: {img_url[:100]}")
            print(f"  Caption: {caption}")
        else:
            print("  No image found")
