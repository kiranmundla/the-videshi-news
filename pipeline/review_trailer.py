#!/usr/bin/env python3
"""
review_trailer.py — the roster trailer step for movie reviews.

Root cause it fixes (2026-10-31, Udta Teer): a movie review's trailer
was never embedded at production time.

  - movie-reviews.py has no trailer step (never did — `git log -S
    trailer` on it is empty). It publishes, then runs polish +
    enrich-on-publish.
  - enrich-on-publish's YouTube routes cannot find a film trailer:
    enrich_youtube() only searches for social-registry entities named
    in the headline (a film's star may not be registered — Ayushmann
    Khurrana is not — and a film title never is), and the
    official-video pass is env-gated OFF in that subprocess and maps
    channels by studio names appearing in the body (a review
    synthesis may never name the studio — "Dharma" appears 0 times
    in the Udta Teer review).
  - The trailer was known all along: the film's now-in-theaters.json
    roster entry carries trailer_url (sourced by fetch-theaters.py).
    movie-reviews.py reads poster_url from that same movie_data and
    ignores trailer_url. Of the 5 review roundups published Oct
    17–31, ZERO had a trailer at production; 2 (Prahaar, Jailer 2)
    still have none — the enricher's search-based catch-up is a
    lottery, not a mechanism.

This module is that mechanism. Given an article, it finds the film in
the theater roster, takes the roster's trailer video, and gates it
exactly as hard as every other trailer embed in the pipeline:

  1. Channel identity — the video's channelId must be on the
     trailer-channels.json allowlist (or its channel title must match
     an allowlisted name/alias, embed_placement's canonical set).
  2. Shared gate — embed_placement.youtube_embed_reject_reason
     (pirate-bait; trailer/teaser titles only from official channels).
  3. The title must actually say trailer/teaser AND name the film —
     fetch-theaters' roster URL comes from a first-hit scrape, so a
     wrong film's trailer on the right channel is a real failure
     mode this layer exists to catch.
  4. US region — official_video_pass.region_allows_us semantics
     (an embed that renders is not an embed that plays). Metadata
     lookup failure fails closed: no metadata, no embed.

Callers: enrich-on-publish.py (invoked at production time by BOTH
movie-reviews.py and the v3 writer, and again by the enricher
catch-up) — so single reviews and review roundups are covered by the
same single step. Pure given injectables (roster / meta_fetcher) for
tests; no writes.
"""
import json
import os
import re
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
ROSTER_PATH = os.path.join(REPO, "public", "data", "now-in-theaters.json")
TRAILER_CHANNELS_PATH = os.path.join(HERE, "trailer-channels.json")

_VIDEO_ID_RE = re.compile(r"(?:v=|youtu\.be/|/embed/)([A-Za-z0-9_-]{11})")
_TRAILERISH_RE = re.compile(r"\b(?:trailer|teaser)\b", re.IGNORECASE)
_NON_WORD_RE = re.compile(r"[^a-z0-9]+")

# Words that carry no film-identity signal in a title.
_TITLE_STOPWORDS = {"the", "a", "an", "of", "part", "chapter"}


def video_id_from_url(url):
    """11-char video id from a watch/youtu.be/embed URL, else None
    (a YouTube *search* URL — fetch-theaters' fallback — yields None:
    it is not an embeddable trailer)."""
    if not url:
        return None
    m = _VIDEO_ID_RE.search(url)
    return m.group(1) if m else None


def _norm(text):
    return _NON_WORD_RE.sub(" ", (text or "").lower()).strip()


def _title_tokens(title):
    """Significant tokens of a film title (identity-bearing words)."""
    toks = [t for t in _norm(title).split() if t not in _TITLE_STOPWORDS]
    strong = [t for t in toks if len(t) >= 3]
    return strong if strong else toks


def _title_slug(title):
    return re.sub(r"\s+", "-", _norm(title)).strip("-")


def load_roster(path=None):
    try:
        with open(path or ROSTER_PATH) as f:
            return json.load(f).get("movies", [])
    except Exception:
        return []


def match_roster_film(article, roster):
    """The roster film this article reviews, or None.

    Match routes, strongest first: the roster's review_slug IS this
    article's slug (movie-reviews.py Step 7 links them); the film
    title appears as contiguous words in the headline (the writer's
    single-review shape: 'Udta Teer: Ayushmann Khurrana Soars...');
    the article slug carries the film's title slug (the roundup
    shape: 'udta-teer-review-roundup-critics'). Only films with an
    embeddable roster trailer are candidates.
    """
    slug = (article.get("slug") or "").lower()
    headline_n = _norm(article.get("headline") or "")
    candidates = []
    for film in roster or []:
        vid = video_id_from_url(film.get("trailer_url") or "")
        if not vid:
            continue
        title = film.get("title") or ""
        if not title:
            continue
        strength = None
        if film.get("review_slug") and slug == film["review_slug"].lower():
            strength = 3
        elif _norm(title) and f" {_norm(title)} " in f" {headline_n} ":
            strength = 2
        else:
            tslug = _title_slug(title)
            if tslug and (slug == tslug or slug.startswith(tslug + "-")):
                strength = 1
        if strength:
            candidates.append((strength, len(title), film))
    if not candidates:
        return None
    candidates.sort(key=lambda c: (c[0], c[1]), reverse=True)
    return candidates[0][2]


def _allowlist_channel_ids(path=None):
    try:
        with open(path or TRAILER_CHANNELS_PATH) as f:
            cfg = json.load(f)
        return {(c.get("channel_id") or "").strip()
                for c in cfg.get("channels", []) if c.get("channel_id")}
    except Exception:
        return set()


def fetch_video_meta(video_id, token=None):
    """Live metadata for one video via the Data API (snippet +
    contentDetails in a single call): {title, channel_id,
    channel_title, region_restriction}. Returns None when the lookup
    itself fails or the video does not exist — callers fail closed.
    region_restriction is None when the video carries no restriction
    field at all (plays worldwide), which is NOT a lookup failure.
    """
    if token is None:
        try:
            from official_video_pass import get_youtube_token
            token = get_youtube_token()
        except Exception:
            token = None
    if not token:
        return None
    args = ["curl", "-sS", "https://www.googleapis.com/youtube/v3/videos",
            "-H", f"Authorization: Bearer {token}", "-G",
            "--data-urlencode", f"id={video_id}",
            "--data-urlencode", "part=snippet,contentDetails"]
    try:
        r = subprocess.run(args, capture_output=True, text=True, timeout=20)
        items = json.loads(r.stdout).get("items") or []
    except Exception:
        return None
    if not items:
        return None
    item = items[0]
    snippet = item.get("snippet") or {}
    details = item.get("contentDetails") or {}
    return {
        "title": snippet.get("title") or "",
        "channel_id": snippet.get("channelId") or "",
        "channel_title": snippet.get("channelTitle") or "",
        "region_restriction": details.get("regionRestriction"),
    }


def gate_trailer(film, meta, channel_ids=None):
    """Gate a roster trailer candidate. Returns (ok, reason).

    Mirrors the pipeline's standing trailer gates — see module
    docstring. Pure: `meta` is fetch_video_meta()'s dict (or a test
    fixture of the same shape).
    """
    from embed_placement import (official_trailer_channels,
                                 youtube_embed_reject_reason)
    from official_video_pass import region_allows_us

    if not meta:
        return False, "metadata lookup failed — rejected (fail-closed)"

    # 1 ── channel identity: allowlisted channel id, or the channel
    # title matching an allowlisted name/alias (embed_placement's set).
    ids = _allowlist_channel_ids() if channel_ids is None else channel_ids
    title_ok = (meta.get("channel_title") or "").strip().lower() \
        in official_trailer_channels()
    if meta.get("channel_id") not in ids and not title_ok:
        return False, (f"channel '{meta.get('channel_title')}' "
                       f"({meta.get('channel_id')}) is not on the "
                       f"trailer allowlist")

    # 2 ── shared gate: pirate-bait + unofficial-trailer rules.
    reason = youtube_embed_reject_reason(meta.get("title") or "",
                                         meta.get("channel_title") or "")
    if reason:
        return False, f"shared gate: {reason}"

    # 3 ── the title must say trailer/teaser and name THIS film.
    vtitle = meta.get("title") or ""
    if not _TRAILERISH_RE.search(vtitle):
        return False, "video title does not say trailer/teaser"
    vtoks = set(_norm(vtitle).split())
    missing = [t for t in _title_tokens(film.get("title") or "")
               if t not in vtoks]
    if missing:
        return False, (f"video title does not name the film "
                       f"(missing: {', '.join(missing)})")

    # 4 ── US region: an embed that renders is not an embed that plays.
    if not region_allows_us(meta.get("region_restriction")):
        return False, (f"region-blocked for US audience: "
                       f"{meta.get('region_restriction')}")

    return True, "accepted"


def review_trailer_for_article(article, roster=None, meta_fetcher=None):
    """Decide the roster trailer embed for one article.

    Returns {status, ...} with status in {accepted, no_film,
    rejected}. On accepted: video_id, url, title, channel,
    film_title. Pure given injectables; the live defaults read the
    roster file and the YouTube Data API. No writes.
    """
    film = match_roster_film(article,
                             load_roster() if roster is None else roster)
    if not film:
        return {"status": "no_film"}
    video_id = video_id_from_url(film.get("trailer_url") or "")
    if not video_id:
        return {"status": "no_film", "film_title": film.get("title"),
                "reason": "roster trailer_url is not an embeddable "
                          "watch URL"}
    fetcher = meta_fetcher or fetch_video_meta
    meta = fetcher(video_id)
    ok, reason = gate_trailer(film, meta)
    if not ok:
        return {"status": "rejected", "film_title": film.get("title"),
                "video_id": video_id, "reason": reason}
    return {"status": "accepted", "film_title": film.get("title"),
            "video_id": video_id,
            "url": f"https://youtube.com/watch?v={video_id}",
            "title": meta.get("title") or "",
            "channel": meta.get("channel_title") or ""}


if __name__ == "__main__":
    import sys
    art = {"headline": sys.argv[1] if len(sys.argv) > 1 else "",
           "slug": sys.argv[2] if len(sys.argv) > 2 else "",
           "category": "entertainment", "body": ""}
    print(json.dumps(review_trailer_for_article(art), indent=1))
