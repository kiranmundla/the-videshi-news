#!/usr/bin/env python3
"""
Enrich now-in-theaters.json with poster images from Wikipedia.
Also run as part of weekly refresh to source posters for new entries.

Run: python3 pipeline/fetch-theaters.py
Output: public/data/now-in-theaters.json (updated in-place)
"""
import json, os, sys, time
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


def fetch_wikipedia_image(title: str, year: int = 0) -> str:
    """Get poster/thumbnail from Wikipedia. Returns URL or empty string."""
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
                    print(f"  ✅ Poster found: {candidate}")
                    return hi_res
            time.sleep(0.3)
        except Exception as e:
            print(f"  ⚠️ Error for '{candidate}': {e}")
            continue

    print(f"  ❌ No poster found: {title}")
    return ""


def main():
    if not DATA.exists():
        print("❌ now-in-theaters.json not found")
        sys.exit(1)

    data = json.loads(DATA.read_text())
    movies = data.get("movies", [])
    updated = 0

    for movie in movies:
        if movie.get("poster_url"):
            print(f"  ⏭️ Already has poster: {movie['title']}")
            continue

        poster = fetch_wikipedia_image(movie["title"], movie.get("year", 0))
        if poster:
            movie["poster_url"] = poster
            updated += 1

    if updated:
        DATA.write_text(json.dumps(data, indent=2, ensure_ascii=False))
        print(f"\n✅ Updated {updated} poster(s)")
    else:
        print("\nℹ️ No new posters found")

    return updated


if __name__ == "__main__":
    count = main()

    # Auto-commit if posters were updated
    if count > 0:
        os.chdir(REPO)
        os.system("git add public/data/now-in-theaters.json")
        os.system(f'git commit -m "Update theater movie posters ({count} new)"')
        os.system("git push origin main")
