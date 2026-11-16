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
  3. Verify the slug's title IS our title: strip the slug's trailing
     Fandango id and release-year tokens, then the slug must START with
     the query title's exact token sequence (digits inside the title
     itself — "Jailer 2", "418" — are significant and kept). A mere
     token overlap is not enough — it let "Pyre" resolve to "Children
     of the Pyre" on 2026-11-16. Extra slug words AFTER the title
     (Fandango sometimes appends a subtitle, e.g. "Prahaar: The Untold
     Story of Ujjwal Nikam") are allowed; extra words before or inside
     are not. Fail closed: no link beats a wrong-film link (the
     Google-showtimes ticket_url fallback remains).
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


def _tokens(s: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", s.lower().replace("-", " "))


def _slug_title_tokens(slug: str) -> list[str]:
    """Slug tokens minus Fandango's trailing numeric id and year token."""
    toks = _tokens(slug)
    if toks and toks[-1].isdigit():
        toks = toks[:-1]  # numeric movie id
    if toks and toks[-1].isdigit() and len(toks[-1]) == 4 and toks[-1][:2] in ("19", "20"):
        toks = toks[:-1]  # release year
    return toks


def title_match(query_title: str, slug: str) -> bool:
    """True only if the Fandango slug's title starts with our exact title.

    Digits inside the title itself are significant ("Jailer 2" must not
    match the original "Jailer"; "418" is a complete title). The old
    overlap rule passed any slug merely CONTAINING a single-token title
    — "Pyre" matched "children-of-the-pyre-125636", a different film
    (2026-11-16).
    """
    q = _tokens(query_title)
    s = _slug_title_tokens(slug)
    if not q or not s or len(s) < len(q):
        return False
    return s[: len(q)] == q


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
