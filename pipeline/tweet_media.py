#!/usr/bin/env python3
"""
Full media sets for in-body X (Twitter) embeds → public/data/tweet-media.json

Article pages render in-body tweets from static data when available so
photos can be browsed IN PLACE (strip + lightbox) and video posters render
without any runtime API call from the browser. Data comes from X's
syndication endpoint (cdn.syndication.twimg.com/tweet-result) — the same
zero-cost source react-tweet uses in the browser today; no TwitterAPI.io
calls, so the low API balance is untouched.

Cache: pipeline/.state/tweet_media_cache.json maps tweet_id → normalized
entry, or null for tweets the endpoint confirms are gone (deleted /
suspended). Transient failures are NOT cached, so the next run retries
them. Each prebuild run fetches at most MAX_NEW_PER_RUN uncached tweets.

Called from prebuild-feeds.py with the recent + stale article dicts
(front-end shape: "body" + "social_embeds" fields).
"""

import json
import math
import re
import subprocess
import time
from fractions import Fraction
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CACHE_PATH = REPO_ROOT / "pipeline" / ".state" / "tweet_media_cache.json"
OUT_PATH = REPO_ROOT / "public" / "data" / "tweet-media.json"
MAX_NEW_PER_RUN = 150

TWEET_URL_RE = re.compile(r"(?:twitter\.com|x\.com)/(\w+)/status/(\d+)")

# Same feature flags react-tweet sends (fetch-tweet.js); copied verbatim.
_FEATURES = (
    "tfw_timeline_list%3A%3Btfw_follower_count_sunset%3Atrue%3B"
    "tfw_tweet_edit_backend%3Atrue%3Btfw_refsrc_session%3Atrue%3B"
    "tfw_show_business_verified_badge%3Atrue%3B"
    "tfw_duplicate_scribes_to_settings%3Atrue%3B"
    "tfw_use_profile_image_shape_enabled%3Atrue%3B"
    "tfw_show_blue_verified_badge%3Atrue%3Btfw_legacy_timeline_sunset%3Atrue%3B"
    "tfw_show_gov_verified_badge%3Atrue%3B"
    "tfw_show_business_affiliate_badge%3Atrue%3Btfw_tweet_edit_frontend%3Atrue"
)

_B36 = "0123456789abcdefghijklmnopqrstuvwxyz"


def _js_number_to_string_36(x: float) -> str:
    """Replicate JS Number.prototype.toString(36) (shortest round-trip).

    Verified byte-identical against node's output for real tweet ids.
    """
    if x == int(x):
        n = int(x)
        s = ""
        while n:
            s = _B36[n % 36] + s
            n //= 36
        return s or "0"
    ip = int(x)
    s = ""
    n = ip
    while n:
        s = _B36[n % 36] + s
        n //= 36
    s = s or "0"
    frac = Fraction(x) - ip
    digits = []
    f = frac
    for _ in range(30):
        f *= 36
        d = int(f)
        digits.append(d)
        f -= d
        if f == 0:
            break
    for k in range(1, len(digits) + 1):
        cand = Fraction(ip)
        mult = Fraction(1, 36)
        for i in range(k):
            cand += digits[i] * mult
            mult /= 36
        if float(cand) == x:
            return s + "." + "".join(_B36[d] for d in digits[:k])
    return s + "." + "".join(_B36[d] for d in digits)


def syndication_token(tweet_id: str) -> str:
    """The token react-tweet computes: ((id / 1e15) * PI) in base-36,
    with every '0' and '.' stripped."""
    raw = _js_number_to_string_36((float(int(tweet_id)) / 1e15) * math.pi)
    return "".join(c for c in raw if c not in "0.")


def fetch_syndication(tweet_id: str) -> tuple[int, dict | None]:
    """GET the syndication payload via curl (urllib/requests fail through
    this box's proxy). Returns (http_status, payload|None)."""
    url = (
        "https://cdn.syndication.twimg.com/tweet-result"
        f"?id={tweet_id}&lang=en&features={_FEATURES}"
        f"&token={syndication_token(tweet_id)}"
    )
    try:
        r = subprocess.run(
            ["curl", "-sS", "--max-time", "20", "-A", "TheVideshi/1.0",
             url, "-w", "\n%{http_code}"],
            capture_output=True, text=True, timeout=35,
        )
    except (subprocess.TimeoutExpired, OSError):
        return 0, None
    body, _, code = r.stdout.rpartition("\n")
    try:
        status = int(code.strip())
    except ValueError:
        status = 0
    if status != 200:
        return status, None
    try:
        payload = json.loads(body)
    except (ValueError, TypeError):
        return status, None
    return status, payload if isinstance(payload, dict) else None


def _large_photo_url(media_url: str, sizes: dict) -> tuple[str, int, int]:
    """Largest served size for a photo: pbs /media/ URLs take
    ?format=<ext>&name=large; width/height from the payload's sizes.large
    (falling back to original_info)."""
    base = (media_url or "").split("?")[0]
    large = sizes.get("large") or {}
    w = int(large.get("w") or 0)
    h = int(large.get("h") or 0)
    if "/media/" in base:
        fmt = "png" if base.lower().endswith(".png") else "jpg"
        return f"{base}?format={fmt}&name=large", w, h
    return media_url, w, h


def normalize_tweet(payload: dict, tweet_id: str) -> dict | None:
    """Syndication payload → the static entry the frontend consumes.
    None when the payload carries no usable tweet (deleted/suspended)."""
    if not payload or not payload.get("id_str"):
        return None
    user = payload.get("user") or {}
    photos: list[dict] = []
    video: dict | None = None
    for m in payload.get("mediaDetails") or []:
        mtype = m.get("type")
        if mtype == "photo":
            url, w, h = _large_photo_url(m.get("media_url_https") or "",
                                         m.get("sizes") or {})
            if not w or not h:
                oi = m.get("original_info") or {}
                w = w or int(oi.get("width") or 0)
                h = h or int(oi.get("height") or 0)
            if url:
                photos.append({"url": url, "width": w, "height": h})
        elif mtype in ("video", "animated_gif") and video is None:
            vi = m.get("video_info") or {}
            ar = vi.get("aspect_ratio") or [16, 9]
            video = {
                "poster": m.get("media_url_https") or "",
                "aspect": [int(ar[0]), int(ar[1])],
                "duration_ms": int(vi.get("duration_millis") or 0),
                "type": mtype,
            }
    handle = user.get("screen_name") or ""
    return {
        "id": payload.get("id_str") or tweet_id,
        "url": (f"https://x.com/{handle}/status/{tweet_id}" if handle
                else f"https://x.com/i/status/{tweet_id}"),
        "text": payload.get("text") or "",
        "created_at": payload.get("created_at") or "",
        "favorite_count": int(payload.get("favorite_count") or 0),
        "conversation_count": int(payload.get("conversation_count") or 0),
        "user": {
            "name": user.get("name") or "",
            "screen_name": handle,
            "avatar": user.get("profile_image_url_https") or "",
            "verified": bool(user.get("is_blue_verified")
                             or user.get("verified")),
            "verified_type": user.get("verified_type") or None,
        },
        "photos": photos,
        "video": video,
        "media_count": len(photos) + (1 if video else 0),
    }


def extract_tweet_ids(articles: list[dict]) -> list[str]:
    """Tweet ids referenced by article bodies / social_embeds, in the
    order the articles were given (prebuild passes newest-first)."""
    seen: set[str] = set()
    ordered: list[str] = []
    for a in articles:
        texts = [a.get("body") or ""]
        embeds = a.get("social_embeds")
        if embeds:
            texts.append(json.dumps(embeds))
        for text in texts:
            for m in TWEET_URL_RE.finditer(text):
                tid = m.group(2)
                if tid not in seen:
                    seen.add(tid)
                    ordered.append(tid)
    return ordered


def build_tweet_media(articles: list[dict],
                      max_new: int = MAX_NEW_PER_RUN) -> dict:
    """Fetch any uncached tweets in `articles`, persist the cache, and
    write public/data/tweet-media.json for the ids this run covers."""
    ids = extract_tweet_ids(articles)
    cache: dict = {}
    if CACHE_PATH.exists():
        try:
            cache = json.loads(CACHE_PATH.read_text())
        except (ValueError, OSError):
            cache = {}

    missing = [t for t in ids if t not in cache]
    fetched = 0
    dead = 0
    for tid in missing[:max_new]:
        status, payload = fetch_syndication(tid)
        if status != 200:
            # Transient (proxy/rate limit) — leave uncached for next run.
            continue
        entry = normalize_tweet(payload or {}, tid)
        cache[tid] = entry
        fetched += 1
        if entry is None:
            dead += 1
        time.sleep(0.1)
    if fetched:
        CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False))

    out = {tid: cache[tid] for tid in ids if cache.get(tid)}
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(out, ensure_ascii=False,
                                   separators=(",", ":")))
    with_video = sum(1 for e in out.values() if e.get("video"))
    with_photos = sum(1 for e in out.values() if e.get("photos"))
    print(f"  ✓ tweet-media.json: {len(out)} tweets "
          f"({with_photos} with photos, {with_video} with video); "
          f"{fetched} newly fetched ({dead} gone), "
          f"{max(0, len(missing) - max_new)} deferred to next run")
    return out


if __name__ == "__main__":
    # Standalone smoke test: normalize the given tweet ids.
    import sys
    for tid in sys.argv[1:]:
        status, payload = fetch_syndication(tid)
        print(tid, "http", status)
        print(json.dumps(normalize_tweet(payload or {}, tid),
                         indent=1, ensure_ascii=False))
