#!/usr/bin/env python3
"""
Enrich now-in-theaters.json with poster images, YouTube trailers,
and Wikipedia cast photos.

Run: python3 pipeline/fetch-theaters.py
Output: public/data/now-in-theaters.json (updated in-place)
"""
import json, os, re, sys, time
from pathlib import Path
from urllib.parse import quote

try:
    import requests
except ImportError:
    os.system(f"{sys.executable} -m pip install requests -q")
    import requests

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "public" / "data" / "now-in-theaters.json"

HEADERS = {"User-Agent": "TheVideshi/1.0 (https://thevideshi.com; editorial)"}
WIKI_API = "https://en.wikipedia.org/api/rest_v1/page/summary"

# Browser-like UA for YouTube scraping
YT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}


def fetch_wikipedia_image(title: str, year: int = 0):
    """Get poster/thumbnail from Wikipedia.

    Returns (url, width, height) — width/height are the TRUE pixel
    size of the poster file itself, from the REST summary's
    originalimage (falling back to the thumbnail's dims). Recording
    them matters: en.wikipedia posters are non-free files whose
    stored size is capped by policy (~283px for Udta Teer), and for
    such files the summary's "thumbnail" IS the raw file, so the
    /500px- rewrite below is a no-op and the URL alone hides the
    fact that the poster can never fill a hero slot. film_hero.py
    reads poster_width at publish time to apply the >=800px rule
    without a live lookup. Returns ("", 0, 0) when no poster.
    """
    candidates = [title]
    base = title.split(":")[0].strip() if ":" in title else title
    if base != title:
        candidates.append(base)

    for b in [title, base]:
        candidates.append(f"{b} (film)")
        if year:
            candidates.append(f"{b} ({year} film)")

    seen = set()
    unique = []
    for c in candidates:
        if c not in seen:
            seen.add(c)
            unique.append(c)

    for candidate in unique:
        try:
            encoded = quote(candidate.replace(" ", "_"), safe="/_:()%")
            url = f"{WIKI_API}/{encoded}"
            resp = requests.get(url, headers=HEADERS, timeout=8)
            if resp.status_code == 200:
                data = resp.json()
                thumb = data.get("thumbnail", {}).get("source", "")
                if thumb:
                    # Get higher resolution version
                    hi_res = thumb.replace("/330px-", "/500px-")
                    orig = data.get("originalimage", {})
                    width = orig.get("width") or \
                        data.get("thumbnail", {}).get("width") or 0
                    height = orig.get("height") or \
                        data.get("thumbnail", {}).get("height") or 0
                    print(f"  ✅ Poster found: {candidate} "
                          f"({width}x{height})")
                    return hi_res, width, height
            time.sleep(0.3)
        except Exception as e:
            print(f"  ⚠️ Error for '{candidate}': {e}")
            continue

    print(f"  ❌ No poster found: {title}")
    return "", 0, 0


def youtube_search_url(title: str, suffix: str = "official trailer") -> str:
    """Build a YouTube search URL for the trailer."""
    query = f"{title} {suffix}".strip()
    return f"https://www.youtube.com/results?search_query={quote(query)}"


def try_find_youtube_trailer(title: str, year: int = 0, language: str = "") -> str:
    """
    Try to find actual YouTube video ID by searching.
    Include language to avoid wrong-language matches.
    Falls back to search URL if we can't find a direct link.
    """
    lang_tag = f" {language}" if language and language != "English" else ""
    queries = [
        f"{title}{lang_tag} official trailer {year}" if year else f"{title}{lang_tag} official trailer",
        f"{title}{lang_tag} trailer",
        f"{title} trailer {year}" if year else f"{title} trailer",
    ]

    for query in queries:
        try:
            search_url = f"https://www.youtube.com/results?search_query={quote(query)}"
            resp = requests.get(search_url, headers=YT_HEADERS, timeout=10)

            if resp.status_code == 200:
                # Extract video IDs from the page
                video_ids = re.findall(r'"videoId":"([A-Za-z0-9_-]{11})"', resp.text)
                if video_ids:
                    vid = video_ids[0]
                    print(f"  🎬 YouTube trailer found: {vid} for '{title}'")
                    return f"https://www.youtube.com/watch?v={vid}"

            time.sleep(0.5)
        except Exception as e:
            print(f"  ⚠️ YouTube search error for '{title}': {e}")
            continue

    # Fall back to search URL
    print(f"  📎 Using YouTube search URL for: {title}")
    return youtube_search_url(title)


def fetch_person_photo(name: str) -> str:
    """Get a person's photo from Wikipedia. Returns URL or empty string."""
    candidates = [name]
    # Also try with "(actor)" or "(actress)" suffix for disambiguation
    candidates.append(f"{name} (actor)")
    candidates.append(f"{name} (actress)")

    for candidate in candidates:
        try:
            encoded = quote(candidate.replace(" ", "_"), safe="/_:()%")
            url = f"{WIKI_API}/{encoded}"
            resp = requests.get(url, headers=HEADERS, timeout=8)
            if resp.status_code == 200:
                data = resp.json()
                # Verify it looks like a person article (has a thumbnail)
                thumb = data.get("thumbnail", {}).get("source", "")
                if thumb:
                    # Get a reasonable size for cast photos
                    photo = thumb.replace("/330px-", "/300px-")
                    return photo
            time.sleep(0.15)
        except Exception as e:
            print(f"    ⚠️ Error fetching photo for '{candidate}': {e}")
            continue

    return ""


def build_cast_details(cast_names: list, limit: int = 6) -> list:
    """Build cast_details with Wikipedia photos for up to `limit` cast members."""
    if not cast_names:
        return []

    details = []
    for name in cast_names[:limit]:
        print(f"    🔍 Looking up: {name}")
        photo = fetch_person_photo(name)
        entry = {"name": name, "photo_url": photo}
        if photo:
            print(f"    ✅ Photo found for {name}")
        else:
            print(f"    ❌ No photo for {name}")
        details.append(entry)

    return details


def main():
    if not DATA.exists():
        print("❌ now-in-theaters.json not found")
        sys.exit(1)

    data = json.loads(DATA.read_text())
    movies = data.get("movies", [])
    updated = 0

    for movie in movies:
        title = movie["title"]
        year = movie.get("year", 0)
        language = movie.get("language", "")

        print(f"\n{'='*50}")
        print(f"Processing: {title}")
        print(f"{'='*50}")

        # 1. Poster (+ its true dimensions — see fetch_wikipedia_image)
        if movie.get("poster_url") and movie.get("poster_width"):
            print(f"  ⏭️ Already has poster ({movie['poster_width']}px)")
        elif movie.get("poster_url"):
            # Poster predates dimension recording: measure it once
            # via the API (film_hero caches by URL) and store the
            # width so publish-time decisions need no live lookup.
            try:
                import film_hero
                w, h = film_hero.fetch_wikimedia_dims(movie["poster_url"])
            except Exception:
                w, h = None, None
            if w:
                movie["poster_width"] = w
                if h:
                    movie["poster_height"] = h
                updated += 1
                print(f"  📐 Poster dimensions recorded: {w}x{h}")
            else:
                print(f"  ⏭️ Already has poster (dimensions unmeasured)")
        else:
            poster, p_width, p_height = fetch_wikipedia_image(title, year)
            if poster:
                movie["poster_url"] = poster
                if p_width:
                    movie["poster_width"] = p_width
                if p_height:
                    movie["poster_height"] = p_height
                updated += 1

        # 2. YouTube trailer
        if movie.get("trailer_url") and "watch?v=" in movie.get("trailer_url", ""):
            print(f"  ⏭️ Already has trailer")
        else:
            print(f"  🔍 Searching YouTube trailer...")
            trailer = try_find_youtube_trailer(title, year, language)
            movie["trailer_url"] = trailer
            updated += 1

        # 3. Cast details with photos
        cast = movie.get("cast", [])
        if movie.get("cast_details") and len(movie["cast_details"]) > 0:
            print(f"  ⏭️ Already has cast_details ({len(movie['cast_details'])} entries)")
        elif cast:
            print(f"  📸 Fetching cast photos for {len(cast[:6])} actors...")
            movie["cast_details"] = build_cast_details(cast, limit=6)
            updated += 1
        else:
            print(f"  ℹ️ No cast list to enrich")

    # Write back
    DATA.write_text(json.dumps(data, indent=2, ensure_ascii=False))

    # Summary
    trailers = sum(1 for m in movies if "watch?v=" in m.get("trailer_url", ""))
    cast_enriched = sum(1 for m in movies if m.get("cast_details"))
    with_photos = sum(
        sum(1 for c in m.get("cast_details", []) if c.get("photo_url"))
        for m in movies
    )
    print(f"\n{'='*50}")
    print(f"✅ Done — {len(movies)} movies processed")
    print(f"   Embeddable trailers: {trailers}/{len(movies)}")
    print(f"   Cast-enriched movies: {cast_enriched}/{len(movies)}")
    print(f"   Total cast photos found: {with_photos}")
    print(f"{'='*50}")

    return updated


if __name__ == "__main__":
    count = main()

    # Auto-commit if data was updated
    if count > 0:
        os.chdir(REPO)
        os.system("git add public/data/now-in-theaters.json")
        os.system('git commit -m "Enrich theater movies (trailers + cast photos)"')
        os.system("git push origin main")
