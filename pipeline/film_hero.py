#!/usr/bin/env python3
"""
film_hero.py — the resolution rule for film-article heroes.

Root cause it fixes (2026-10-31, Udta Teer): a movie review's hero
was the roster `poster_url` — a Wikipedia film poster. en.wikipedia
posters are non-free (fair-use) files, and Wikipedia's non-free
content policy caps the stored file itself at tiny sizes (the Udta
Teer poster file IS 283x354 px — there is no bigger variant to
request). fetch-theaters.py took the REST summary's thumbnail URL
(for a non-free file the "thumbnail" is the raw file; its
/330px- -> /500px- string swap is a no-op) and DISCARDED the
width/height the API returned alongside it. movie-reviews.py then
published that URL as the article hero unconditionally, where it
renders full-width (~1100 px) — visibly blurry. enrich-on-publish
never re-checked it (its hero upgrade only fires for stock heroes).

The rule (one rule, all film-hero paths):

  1. A poster (or any candidate hero) whose TRUE width is below
     HERO_MIN_WIDTH never ships as a film article's hero.
  2. Below the floor, prefer the film's official trailer still —
     the maxres thumbnail (1280x720) of the roster trailer that
     review_trailer.py already gates (allowlisted channel +
     trailer title naming the film + US region) — with a caption
     that honestly calls it a trailer still.
  3. If neither a >=floor poster nor a gated trailer exists, the
     article ships with NO hero (the pipeline's standing
     fail-closed behaviour — no blurry upscale, no stock photo
     for a named film).

HERO_MIN_WIDTH = 800 is the pipeline's existing hero floor
(image_sourcer.verify_image_url's 2026-10-11 quality bar, and the
named-person portrait floor) — posters join the same bar instead
of bypassing it.

Widths are measured truthfully, never inferred from a URL variant
name where a placeholder can masquerade (i.ytimg serves a 120x90
placeholder at maxresdefault.jpg for videos with no maxres):
  - Wikimedia thumb URLs carry the served width in the path.
  - Wikimedia file URLs are measured via the API's imageinfo
    (GET — Wikimedia HEAD returns 400 from this box).
  - Anything else (incl. a candidate maxres thumbnail) is measured
    from the downloaded bytes.
Measurements are cached in .state/film-hero-widths.json so the
publish path pays at most one lookup per URL, ever. At roster
fetch time, fetch-theaters.py now records poster_width directly
from the REST summary, so the common case needs no lookup at all.

Callers: movie-reviews.py (publish), enrich-on-publish.py
(backstop for film heroes placed by any other route). Pure given
injectables for tests; the live defaults hit the network.
"""
import json
import os
import re
import subprocess
from urllib.parse import unquote, urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE_PATH = os.path.join(HERE, ".state", "film-hero-widths.json")

HERO_MIN_WIDTH = 800

_YT_VARIANT_WIDTHS = {"maxresdefault": 1280, "sddefault": 640,
                      "hqdefault": 480, "mqdefault": 320, "default": 120}
_WIKI_THUMB_RE = re.compile(r"/(\d+)px-")
_YT_THUMB_RE = re.compile(r"/(maxresdefault|sddefault|hqdefault|"
                          r"mqdefault|default)\.jpg")

_cache = None


def _load_cache():
    global _cache
    if _cache is None:
        try:
            with open(CACHE_PATH) as f:
                _cache = json.load(f)
        except Exception:
            _cache = {}
    return _cache


def _store_width(url, width):
    cache = _load_cache()
    if width and cache.get(url) != width:
        cache[url] = width
        try:
            os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
            with open(CACHE_PATH, "w") as f:
                json.dump(cache, f)
        except Exception:
            pass


def trailer_maxres_url(video_id):
    return f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg"


def _wikimedia_parts(url):
    """(api_host, filename) for an upload.wikimedia.org file URL."""
    u = urlparse(url or "")
    if "upload.wikimedia.org" not in u.netloc:
        return None
    parts = [p for p in unquote(u.path).split("/") if p]
    if len(parts) < 2 or parts[0] != "wikipedia":
        return None
    fname = parts[-1]
    if parts[-2] == "thumb" or (len(parts) > 2 and parts[2] == "thumb"):
        # thumb URL: .../thumb/<h>/<hh>/<File>/<w>px-<File>
        fname = parts[-2] if len(parts) >= 2 else fname
    lang = parts[1]
    api = ("commons.wikimedia.org" if lang == "commons"
           else f"{lang}.wikipedia.org")
    return api, fname


def fetch_wikimedia_dims(url):
    """(width, height) of a Wikimedia file via API imageinfo (GET —
    HEAD returns 400 from this box). (None, None) on any failure."""
    parts = _wikimedia_parts(url)
    if not parts:
        return None, None
    api, fname = parts
    args = ["curl", "-sS", "--max-time", "15", "-A", "TheVideshi/1.0",
            "-G", f"https://{api}/w/api.php",
            "--data-urlencode", "action=query",
            "--data-urlencode", "prop=imageinfo",
            "--data-urlencode", "iiprop=size",
            "--data-urlencode", f"titles=File:{fname}",
            "--data-urlencode", "format=json"]
    try:
        r = subprocess.run(args, capture_output=True, text=True, timeout=20)
        data = json.loads(r.stdout)
        for page in (data.get("query", {}).get("pages", {}) or {}).values():
            ii = (page.get("imageinfo") or [{}])[0]
            if ii.get("width"):
                return ii["width"], ii.get("height")
    except Exception:
        pass
    return None, None


def _download_width(url):
    """True pixel width from the downloaded bytes (the only honest
    measure for hosts with no metadata API — and for i.ytimg, whose
    maxresdefault URL serves a 120x90 placeholder when a video has
    no maxres). None when unmeasurable."""
    try:
        import image_sourcer
        raw = image_sourcer.download_image(url)
        if not raw:
            return None
        w, _h = image_sourcer.get_image_dimensions(raw)
        return w or None
    except Exception:
        return None


def measure_image_width(url):
    """Best truthful width for an image URL, or None.

    Cheap sources first (URL-carried width, cache, Wikimedia
    imageinfo); a byte download is the last resort. Results are
    cached. YouTube thumbnail variant names are NOT trusted here —
    see _download_width's placeholder warning; ytimg URLs go
    straight to byte measurement.
    """
    if not url:
        return None
    u = urlparse(url)
    if "wikimedia.org" in u.netloc:
        m = _WIKI_THUMB_RE.search(u.path)
        if m:
            return int(m.group(1))
        cache = _load_cache()
        if url in cache:
            return cache[url]
        w, _h = fetch_wikimedia_dims(url)
        if w:
            _store_width(url, w)
        return w
    cache = _load_cache()
    if url in cache:
        return cache[url]
    w = _download_width(url)
    if w:
        _store_width(url, w)
    return w


def _default_poster_caption(film):
    title = film.get("title") or ""
    director = film.get("director") or ""
    if director:
        return f"'{title}' directed by {director}, now in theaters."
    return f"'{title}', now in theaters."


def resolve_film_hero(film, article=None, *, poster_width=None,
                      width_of=None, meta_fetcher=None):
    """Decide the hero for one film article.

    `film` is a roster-shaped dict (title, poster_url, trailer_url,
    optionally poster_width recorded at fetch time). Returns:

      {"hero_kind": "poster",        "image_url": ..., "image_caption": None, ...}
      {"hero_kind": "trailer_still", "image_url": ..., "image_caption": ...}
      {"hero_kind": "none",          "image_url": None, ...}

    image_caption is None for a kept poster (the caller keeps its
    existing caption behaviour); a trailer still always carries its
    honest caption. Fail-closed throughout: an unmeasurable poster
    is treated as below the floor, a maxres candidate that does not
    byte-measure >= the floor is rejected, and a trailer that fails
    review_trailer's gate is never used.
    """
    import review_trailer

    width_of = width_of or measure_image_width
    title = film.get("title") or ""
    poster = (film.get("poster_url") or "").strip()
    out = {"film_title": title, "poster_url": poster or None,
           "poster_width": None, "reason": ""}

    if poster:
        w = poster_width
        if w is None:
            w = film.get("poster_width") or None
        if w is None:
            w = width_of(poster)
        out["poster_width"] = w
        if w and w >= HERO_MIN_WIDTH:
            out.update(hero_kind="poster", image_url=poster,
                       image_caption=None,
                       reason=f"poster clears the floor ({w}px)")
            return out
        out["reason"] = (f"poster below the floor "
                         f"({w}px < {HERO_MIN_WIDTH}px)"
                         if w else "poster width unproven — "
                                   "treated as below the floor")

    video_id = review_trailer.video_id_from_url(film.get("trailer_url")
                                                or "")
    if video_id:
        fetcher = meta_fetcher or review_trailer.fetch_video_meta
        meta = fetcher(video_id)
        ok, greason = review_trailer.gate_trailer(film, meta)
        if ok:
            murl = trailer_maxres_url(video_id)
            mw = width_of(murl)
            if mw and mw >= HERO_MIN_WIDTH:
                out.update(
                    hero_kind="trailer_still", image_url=murl,
                    image_caption=(f"Still from the official trailer "
                                   f"of '{title}'."),
                    reason=(out["reason"] + "; gated trailer still "
                            f"at {mw}px" if out["reason"] else
                            f"gated trailer still at {mw}px"))
                return out
            out["reason"] += (f"; trailer maxres measures "
                              f"{mw}px — rejected")
        else:
            out["reason"] += f"; trailer gate: {greason}"

    out.update(hero_kind="none", image_url=None, image_caption=None,
               reason=out["reason"] + "; no hero (fail-closed)")
    return out


def fix_article_hero(article, roster=None, **kwargs):
    """Backstop for enrich-on-publish: if this article is about a
    roster film and its current hero measures below the floor,
    return {"image_url": ..., "image_caption": ...} updates that
    swap in the gated trailer still or clear the hero. None when
    the article is not a roster-film article, has no hero, or its
    hero already clears the floor.

    Extra kwargs are forwarded to resolve_film_hero (test
    injectables)."""
    if (article.get("category") or "").lower() != "entertainment":
        return None
    current = (article.get("image_url") or "").strip()
    if not current:
        return None
    import review_trailer
    film = review_trailer.match_roster_film(
        article, review_trailer.load_roster() if roster is None
        else roster)
    if not film:
        return None
    width_of = kwargs.get("width_of") or measure_image_width
    w = width_of(current)
    if w and w >= HERO_MIN_WIDTH:
        return None
    decision_film = dict(film)
    if current != (film.get("poster_url") or ""):
        # The current hero is not the roster poster (e.g. a small
        # actor photo a legacy route placed): judge the poster on
        # its own merits too, but the swap candidate is the same —
        # the gated trailer or nothing.
        decision_film["poster_url"] = current
        decision_film.pop("poster_width", None)
    res = resolve_film_hero(decision_film, article, **kwargs)
    if res["hero_kind"] == "poster":
        return None  # current hero IS a >=floor poster — untouched
    print(f"     🎞 Film hero fix ({film.get('title')}): "
          f"{res['reason']}")
    return {"image_url": res["image_url"],
            "image_caption": res["image_caption"]}


if __name__ == "__main__":
    import sys
    film = {"title": sys.argv[1] if len(sys.argv) > 1 else "",
            "poster_url": sys.argv[2] if len(sys.argv) > 2 else "",
            "trailer_url": sys.argv[3] if len(sys.argv) > 3 else ""}
    print(json.dumps(resolve_film_hero(film), indent=1))
