#!/usr/bin/env python3 -u
"""Resolve Fandango movie-overview URLs for Indian movies in now-in-theaters.json.

No free US showtimes API exists (MovieGlu shut down; Gracenote/TMS is
enterprise; Fandango has no public API; scraping per-zip showtimes is
bot-blocked and ToS-gray). The honest architecture: deep-link each movie to
its Fandango overview page, where the user sees REAL showtimes for their
location. Fandango movie IDs are stable per film, so this is a one-time
resolution per movie, not ongoing scraping.

For each now-playing Indian movie without a fandango_url:
  1. GET https://www.fandango.com/search?q=<title>
  2. Take the first /<slug>-<id>/movie-overview link
  3. Verify the slug resembles the title (fuzzy token match)
  4. Store https://www.fandango.com/<slug>/movie-overview as fandango_url

Run: python3 -u pipeline/build-movie-tickets.py [--force]
Writes: public/data/now-in-theaters.json (in place)
"""
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(REPO, "public", "data", "now-in-theaters.json")

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
SEARCH_URL = "https://www.fandango.com/search?q="
DELAY_S = 2


def norm(s: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", s.lower()))


def title_match(query_title: str, slug: str) -> bool:
    """Fuzzy check that the Fandango slug is really our movie."""
    qtok = norm(query_title)
    stok = norm(slug.replace("-", " "))
    if not qtok or not stok:
        return False
    overlap = qtok & stok
    # at least half of the shorter token set must overlap
    need = max(1, min(len(qtok), len(stok)) // 2)
    return len(overlap) >= need


def resolve_fandango(title: str) -> str | None:
    url = SEARCH_URL + urllib.parse.quote(title)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            html = resp.read().decode("utf-8", "replace")
    except Exception as e:
        print(f"  [warn] search failed for {title!r}: {e}", flush=True)
        return None
    # first movie-overview link on the results page
    m = re.search(r'href="(/[^"]*?/movie-overview)"', html)
    if not m:
        return None
    path = m.group(1)
    slug = path.strip("/").rsplit("/movie-overview", 1)[0]
    if not title_match(title, slug):
        print(f"  [skip] {title!r}: top hit {slug!r} doesn't match", flush=True)
        return None
    return "https://www.fandango.com" + path


def main():
    force = "--force" in sys.argv
    with open(DATA_PATH, encoding="utf-8") as fh:
        data = json.load(fh)
    movies = data.get("movies", [])
    resolved = 0
    skipped = 0
    for m in movies:
        if not m.get("is_indian") or m.get("status") not in ("now_playing", "opening"):
            continue
        if m.get("fandango_url") and not force:
            continue
        title = m.get("title", "")
        print(f"[fandango] resolving {title!r}...", flush=True)
        url = resolve_fandango(title)
        time.sleep(DELAY_S)
        if url:
            m["fandango_url"] = url
            resolved += 1
            print(f"  -> {url}", flush=True)
        else:
            skipped += 1
    with open(DATA_PATH, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
    print(f"done: resolved={resolved} skipped={skipped} -> {DATA_PATH}")


if __name__ == "__main__":
    sys.exit(main())
