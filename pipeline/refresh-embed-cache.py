#!/usr/bin/env python3
"""
refresh-embed-cache.py — Refresh the social embed handle cache.

Reads all X and IG handles from Supabase social_accounts table, fetches their
recent posts via TwitterAPI.io and the Meta Instagram connector, and writes the results to
pipeline/cache/embed_cache.json so enrich-on-publish.py can do instant
handle-based enrichment without live API calls.

Usage:
  python3 -u refresh-embed-cache.py                # refresh everything
  python3 -u refresh-embed-cache.py --x-only       # only refresh X handles
  python3 -u refresh-embed-cache.py --ig-only      # only refresh IG handles

Env: ~/workspace/.env.twitterapi-io, ~/workspace/.env.supabase
"""

import os
import sys
import json
import time
import subprocess
import re
from datetime import datetime, timezone, timedelta

_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _dir)
from social_registry import collect_handles  # DB-backed
CACHE_DIR = os.path.join(_dir, "cache")
CACHE_PATH = os.path.join(CACHE_DIR, "embed_cache.json")

# ─── Env ──────────────────────────────────────────────────────────────────────

def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip())

load_env(os.path.expanduser("~/workspace/.env.twitterapi-io"))
load_env(os.path.expanduser("~/workspace/.env.supabase"))

TWITTERAPI_IO_KEY = os.environ.get("TWITTERAPI_IO_KEY", "")
TWITTERAPI_IO_BASE = os.environ.get("TWITTERAPI_IO_BASE", "https://api.twitterapi.io")

# Instagram reads use the Meta Accounts Center-backed connector, not a
# developer-app token or scraper. Refreshes rotate through the registry:
# a bounded number of handles per run, oldest cache entries first.
INSTAGRAM_CLI = "/opt/hatch/bin/instagram-cli"
INSTAGRAM_ACCOUNT_ID = os.environ.get(
    "VIDESHI_INSTAGRAM_ACCOUNT_ID", "17841426005310230")
try:
    IG_MAX_HANDLES_PER_REFRESH = max(
        0, int(os.environ.get("VIDESHI_IG_MAX_HANDLES_PER_REFRESH", "40")))
except ValueError:
    IG_MAX_HANDLES_PER_REFRESH = 40
IG_RATE_LIMITED = False


# ─── Registry ────────────────────────────────────────────────────────────────
# collect_handles() is now imported from social_registry


# ─── X / TwitterAPI.io (cheap /user/last_tweets endpoint) ─────────────────────

def fetch_x_handle(handle, hours=48, max_results=20):
    """Fetch recent tweets from a handle via TwitterAPI.io /user/last_tweets (cheap endpoint).
    
    Uses /twitter/user/last_tweets (~15 credits) instead of /twitter/tweet/advanced_search
    (up to 300 credits). Same return format as before.
    """
    if not TWITTERAPI_IO_KEY:
        return []

    try:
        result = subprocess.run(
            ["curl", "-sS", "--max-time", "15",
             f"{TWITTERAPI_IO_BASE}/twitter/user/last_tweets",
             "-H", f"X-API-Key: {TWITTERAPI_IO_KEY}",
             "-G",
             "--data-urlencode", f"userName={handle}"],
            capture_output=True, text=True, timeout=20,
        )
        if result.returncode != 0:
            print(f"  \u26a0 curl error for @{handle}: {result.stderr[:120]}")
            return []
        data = json.loads(result.stdout)
    except Exception as e:
        print(f"  \u26a0 Error fetching @{handle}: {e}")
        return []

    raw_tweets = data.get("data", {}).get("tweets", []) or data.get("tweets", [])
    if not raw_tweets:
        return []

    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    posts = []
    for t in raw_tweets[:max_results]:
        # Skip retweets and replies
        if t.get("retweeted_tweet") or (t.get("text", "")).startswith("RT @"):
            continue
        if t.get("isReply"):
            continue

        created_str = t.get("createdAt", "")
        try:
            created = datetime.strptime(created_str, "%a %b %d %H:%M:%S %z %Y")
            if created < cutoff:
                continue
        except (ValueError, TypeError):
            pass

        media_list = t.get("extendedEntities", {}).get("media", [])
        photos = [m.get("media_url_https", "") for m in media_list if m.get("type") == "photo"]
        has_video = any(m.get("type") in ("video", "animated_gif") for m in media_list)
        author = t.get("author", {})
        handle_actual = author.get("userName", handle)

        posts.append({
            "id": t.get("id", ""),
            "text": t.get("text", ""),
            "created_at": created_str,
            "photos": photos,
            "photo_count": len(photos),
            "has_video": has_video,
            "url": t.get("url", f"https://x.com/{handle_actual}/status/{t.get('id', '')}"),
            "likes": t.get("likeCount", 0) or 0,
            "retweets": t.get("retweetCount", 0) or 0,
            "views": t.get("viewCount", 0) or 0,
            "verified": author.get("isBlueVerified", False),
            "handle": handle_actual,
            "followers": author.get("followers", 0) or 0,
        })

    return posts


def refresh_x_cache(handles, existing_cache):
    """Fetch tweets for X handles with self-tuning tiers.

    Handles with 3+ consecutive empty fetches drop to a once-daily check;
    active handles stay on the normal cycle. Streaks persist in the cache
    itself, so no extra state file is needed. Errors don't advance the
    streak — only genuinely empty results do.
    """
    x_cache = existing_cache.get("x", {})
    now = datetime.now(timezone.utc)
    now_iso = now.strftime("%Y-%m-%dT%H:%M:%SZ")

    total_posts = 0
    fetched = 0
    skipped = 0
    errors = 0

    for i, handle in enumerate(handles):
        entry = x_cache.get(handle, {})
        streak = entry.get("empty_streak", 0)
        # Quiet tier: 3+ straight empty fetches → check once daily, not every run
        if streak >= 3:
            last = entry.get("fetched_at")
            try:
                last_dt = datetime.strptime(last, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                if now - last_dt < timedelta(hours=23):
                    skipped += 1
                    continue
            except (TypeError, ValueError):
                pass  # unparseable timestamp → fetch normally

        print(f"  [{i+1}/{len(handles)}] @{handle} ... ", end="", flush=True)
        posts = fetch_x_handle(handle, hours=48, max_results=20)
        if posts is not None:
            new_streak = 0 if posts else streak + 1
            x_cache[handle] = {
                "posts": posts,
                "fetched_at": now_iso,
                "empty_streak": new_streak,
            }
            total_posts += len(posts)
            fetched += 1
            print(f"{len(posts)} tweets" + (f" (streak {new_streak})" if new_streak else ""))
        else:
            errors += 1
            print("error")

        # Small delay to avoid rate limiting
        if (i + 1) % 10 == 0 and i + 1 < len(handles):
            time.sleep(1)

    print(f"\n  X summary: {fetched} handles fetched ({skipped} quiet-tier skipped), "
          f"{total_posts} tweets cached, {errors} errors")
    return x_cache


# ─── Instagram / Meta connector ───────────────────────────────────────────────

def _ig_shortcode_from_url(url):
    m = re.search(r"instagram\.com/(?:p|reel|tv)/([^/?#]+)", url or "")
    return m.group(1) if m else ""


def _is_ig_rate_limit_text(text):
    low = (text or "").lower()
    return "429" in low or "too many requests" in low or "rate limit" in low


def _normalize_ig_post(item, requested_handle):
    if not isinstance(item, dict):
        return None
    owner = (item.get("username") or "").lower().lstrip("@")
    if owner != requested_handle:
        return None
    if item.get("visibility") and item.get("visibility") != "public":
        return None
    url = item.get("url") or ""
    shortcode = _ig_shortcode_from_url(url)
    if not shortcode:
        return None
    return {
        "shortCode": shortcode,
        "caption": item.get("post_caption") or item.get("caption") or "",
        "timestamp": item.get("created_at") or item.get("timestamp") or "",
        "likesCount": item.get("likes") or item.get("likesCount") or 0,
        "commentsCount": item.get("comments") or item.get("commentsCount") or 0,
        "type": item.get("media_type") or item.get("type") or "",
        "url": url,
        "displayUrl": item.get("displayUrl") or "",
        "ownerUsername": owner,
        "post_id": item.get("post_id") or item.get("id") or "",
    }


def fetch_ig_posts_batch(handles, results_limit=12):
    """Fetch recent public posts one handle at a time via the connector.

    The connector has no batch endpoint. A 429 stops the whole refresh;
    handles not reached keep their existing cache entries. Returns
    {handle: [posts]} only for handles actually queried successfully.
    """
    global IG_RATE_LIMITED
    by_handle = {}
    for raw_handle in handles:
        if IG_RATE_LIMITED:
            break
        handle = (raw_handle or "").lower().lstrip("@")
        if not handle:
            continue
        cmd = [INSTAGRAM_CLI, "posts",
               "--account-id", INSTAGRAM_ACCOUNT_ID,
               "--username", handle,
               "--limit", str(results_limit)]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
        except Exception as e:
            print(f"  ⚠ Instagram connector call failed for @{handle}: {e}")
            continue

        # Rate-limit detection is STRUCTURAL, never a substring scan of the
        # payload: post IDs and counts are long digit strings that can
        # legitimately contain "429". Trust the parsed provider_error
        # object; scan raw text only when the output is not JSON at all.
        try:
            start = result.stdout.find("{")
            data = json.loads(result.stdout[start:]) if start >= 0 else {}
            if not isinstance(data, dict):
                data = {}
        except (json.JSONDecodeError, TypeError):
            data = {}
        if not data:
            combined = f"{result.stdout}\n{result.stderr}"
            if _is_ig_rate_limit_text(combined):
                IG_RATE_LIMITED = True
                print("  ⚠ Instagram rate limit (429) — stopping IG refresh")
                break
            print(f"  ⚠ Instagram connector returned non-JSON for @{handle}")
            continue

        provider_error = data.get("provider_error") or data.get("error")
        if provider_error:
            err_text = json.dumps(provider_error)
            if _is_ig_rate_limit_text(err_text):
                IG_RATE_LIMITED = True
                print(f"  ⚠ Instagram rate limit (429) — stopping IG refresh: {err_text[:160]}")
                break
            print(f"  ⚠ Instagram connector error for @{handle}: {err_text[:160]}")
            continue
        if result.returncode != 0:
            print(f"  ⚠ Instagram connector exited {result.returncode} for @{handle}")
            continue

        posts = []
        for item in data.get("posts", []):
            normalized = _normalize_ig_post(item, handle)
            if normalized:
                posts.append(normalized)
        by_handle[handle] = posts
    return by_handle


def refresh_ig_cache(handles, existing_cache, max_handles=IG_MAX_HANDLES_PER_REFRESH):
    """Refresh a bounded, rotating slice of the IG registry.

    Handles with no cache entry go first, then the oldest entries. This
    respects Meta's practical per-account lookup limits instead of trying
    to read the entire registry in one run. Unreached handles keep their
    existing cache entries untouched.
    """
    ig_cache = dict(existing_cache.get("ig", {}))
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    if not handles:
        print("  No IG handles to fetch")
        return ig_cache

    def _fetched_at(handle):
        entry = ig_cache.get(handle)
        return entry.get("fetched_at", "") if isinstance(entry, dict) else ""

    ordered = sorted(handles, key=lambda h: (_fetched_at(h), h))
    selected = ordered[:max_handles] if max_handles else []
    deferred = ordered[len(selected):]
    print(f"  IG rotation: refreshing {len(selected)} of {len(handles)} handles; "
          f"{len(deferred)} deferred to a later refresh")

    results = fetch_ig_posts_batch(selected, results_limit=12)
    total_posts = 0
    for h, posts in results.items():
        ig_cache[h] = {"posts": posts, "fetched_at": now_iso}
        total_posts += len(posts)

    print(f"\n  IG summary: {len(results)} handles fetched, {total_posts} posts cached")
    return ig_cache


# ─── Cache I/O ────────────────────────────────────────────────────────────────

def load_cache():
    """Load existing cache from disk, or return empty structure."""
    if os.path.exists(CACHE_PATH):
        try:
            with open(CACHE_PATH) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {"x": {}, "ig": {}, "refreshed_at": None}


def save_cache(cache):
    """Write cache to disk."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(CACHE_PATH, "w") as f:
        json.dump(cache, f, indent=2)


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Refresh social embed handle cache")
    parser.add_argument("--x-only", action="store_true", help="Only refresh X handles")
    parser.add_argument("--ig-only", action="store_true", help="Only refresh IG handles")
    parser.add_argument("--ig-limit", type=int, default=IG_MAX_HANDLES_PER_REFRESH,
                        help="Max IG handles to refresh this run (rotating, oldest first)")
    args = parser.parse_args()

    do_x = not args.ig_only
    do_ig = not args.x_only

    print("═══ Social Embed Cache Refresh ═══")
    start = time.time()

    x_handles, ig_handles = collect_handles()
    print(f"Registry: {len(x_handles)} X handles, {len(ig_handles)} IG handles\n")

    cache = load_cache()

    if do_x:
        print("── X / TwitterAPI.io ──")
        if not TWITTERAPI_IO_KEY:
            print("  ⚠ TWITTERAPI_IO_KEY not set — skipping X")
        else:
            cache["x"] = refresh_x_cache(x_handles, cache)

    if do_ig:
        print("\n── Instagram / Meta connector ──")
        cache["ig"] = refresh_ig_cache(
            ig_handles, cache, max_handles=max(0, args.ig_limit))

    cache["refreshed_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    save_cache(cache)

    elapsed = time.time() - start
    x_total = sum(len(v.get("posts", [])) for v in cache.get("x", {}).values())
    ig_total = sum(len(v.get("posts", [])) for v in cache.get("ig", {}).values())
    print(f"\n═══ Done in {elapsed:.1f}s ═══")
    print(f"Cache: {x_total} X posts + {ig_total} IG posts → {CACHE_PATH}")


if __name__ == "__main__":
    main()
