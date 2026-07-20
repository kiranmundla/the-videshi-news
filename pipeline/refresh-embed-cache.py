#!/usr/bin/env python3
"""
refresh-embed-cache.py — Refresh the social embed handle cache.

Reads all X and IG handles from social-embed-registry.json, fetches their
recent posts via TwitterAPI.io and Apify, and writes the results to
pipeline/cache/embed_cache.json so enrich-on-publish.py can do instant
handle-based enrichment without live API calls.

Usage:
  python3 -u refresh-embed-cache.py                # refresh everything
  python3 -u refresh-embed-cache.py --x-only       # only refresh X handles
  python3 -u refresh-embed-cache.py --ig-only      # only refresh IG handles

Env: ~/workspace/.env.twitterapi-io, ~/workspace/.env.apify
"""

import os
import sys
import json
import time
import subprocess
import re
from datetime import datetime, timezone, timedelta

_dir = os.path.dirname(os.path.abspath(__file__))
REGISTRY_PATH = os.path.join(_dir, "social-embed-registry.json")
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
load_env(os.path.expanduser("~/workspace/.env.apify"))
load_env(os.path.expanduser("~/workspace/.env.supabase"))

TWITTERAPI_IO_KEY = os.environ.get("TWITTERAPI_IO_KEY", "")
TWITTERAPI_IO_BASE = os.environ.get("TWITTERAPI_IO_BASE", "https://api.twitterapi.io")
APIFY_API_TOKEN = os.environ.get("APIFY_API_TOKEN", "")


# ─── Registry ────────────────────────────────────────────────────────────────

def collect_handles():
    """Read registry and return unique X handles and IG handles."""
    with open(REGISTRY_PATH) as f:
        registry = json.load(f)

    x_handles = set()
    ig_handles = set()

    for category, data in registry.items():
        if category.startswith("_") or not isinstance(data, dict):
            continue
        for group in ("persons", "organizations"):
            for entry in data.get(group, []):
                x = entry.get("x")
                ig = entry.get("instagram")
                if x:
                    x_handles.add(x.lower())
                if ig:
                    ig_handles.add(ig.lower())

    return sorted(x_handles), sorted(ig_handles)


# ─── X / TwitterAPI.io ────────────────────────────────────────────────────────

def fetch_x_handle(handle, hours=48, max_results=20):
    """Fetch recent tweets from a handle via TwitterAPI.io using curl."""
    if not TWITTERAPI_IO_KEY:
        return []

    query = f"from:{handle}"
    try:
        result = subprocess.run(
            ["curl", "-sS",
             f"{TWITTERAPI_IO_BASE}/twitter/tweet/advanced_search",
             "-H", f"X-API-Key: {TWITTERAPI_IO_KEY}",
             "-G",
             "--data-urlencode", f"query={query}",
             "-d", "queryType=Latest"],
            capture_output=True, text=True, timeout=15,
        )
        if result.returncode != 0:
            print(f"  ⚠ curl error for @{handle}: {result.stderr[:120]}")
            return []
        data = json.loads(result.stdout)
    except Exception as e:
        print(f"  ⚠ Error fetching @{handle}: {e}")
        return []

    raw_tweets = data.get("tweets", [])
    if not raw_tweets:
        return []

    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    posts = []
    for t in raw_tweets[:max_results]:
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
        handle_actual = author.get("userName", "")

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
    """Fetch tweets for all X handles. Returns updated x cache dict."""
    x_cache = existing_cache.get("x", {})
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    total_posts = 0
    fetched = 0
    errors = 0

    for i, handle in enumerate(handles):
        print(f"  [{i+1}/{len(handles)}] @{handle} ... ", end="", flush=True)
        posts = fetch_x_handle(handle, hours=48, max_results=20)
        if posts is not None:
            x_cache[handle] = {
                "posts": posts,
                "fetched_at": now_iso,
            }
            total_posts += len(posts)
            fetched += 1
            print(f"{len(posts)} tweets")
        else:
            errors += 1
            print("error")

        # Small delay to avoid rate limiting
        if (i + 1) % 10 == 0 and i + 1 < len(handles):
            time.sleep(1)

    print(f"\n  X summary: {fetched} handles fetched, {total_posts} tweets cached, {errors} errors")
    return x_cache


# ─── Instagram / Apify ────────────────────────────────────────────────────────

def fetch_ig_posts_batch(handles, results_limit=12):
    """Batch-fetch recent posts from IG handles via Apify. Returns {handle: [posts]}."""
    if not APIFY_API_TOKEN:
        print("  ⚠ APIFY_API_TOKEN not set, skipping IG")
        return {}

    urls = [f"https://www.instagram.com/{h}/" for h in handles]
    payload = json.dumps({
        "directUrls": urls,
        "resultsType": "posts",
        "resultsLimit": results_limit,
        "searchType": "user",
        "searchLimit": 1,
    })

    try:
        result = subprocess.run(
            ["curl", "-sS", "-X", "POST",
             f"https://api.apify.com/v2/acts/apify~instagram-scraper/run-sync-get-dataset-items?token={APIFY_API_TOKEN}",
             "-H", "Content-Type: application/json",
             "-d", payload],
            capture_output=True, text=True, timeout=300,
        )
        if result.returncode != 0:
            print(f"  ⚠ Apify curl failed: {result.stderr[:200]}")
            return {}
        data = json.loads(result.stdout)
    except Exception as e:
        print(f"  ⚠ Apify call failed: {e}")
        return {}

    by_handle = {}
    for item in data:
        owner = (item.get("ownerUsername") or "").lower()
        if not owner:
            input_url = item.get("inputUrl", "")
            m = re.search(r'instagram\.com/([^/]+)', input_url)
            owner = m.group(1).lower() if m else ""
        if owner:
            by_handle.setdefault(owner, []).append({
                "shortCode": item.get("shortCode", ""),
                "caption": item.get("caption", ""),
                "timestamp": item.get("timestamp", ""),
                "likesCount": item.get("likesCount", 0),
                "commentsCount": item.get("commentsCount", 0),
                "type": item.get("type", ""),
                "url": item.get("url", ""),
                "displayUrl": item.get("displayUrl", ""),
                "ownerUsername": owner,
            })

    return by_handle


def refresh_ig_cache(handles, existing_cache):
    """Fetch IG posts for all handles. Returns updated ig cache dict."""
    ig_cache = existing_cache.get("ig", {})
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    if not handles:
        print("  No IG handles to fetch")
        return ig_cache

    # Batch in groups of 10
    BATCH_SIZE = 10
    total_posts = 0
    fetched = 0

    for i in range(0, len(handles), BATCH_SIZE):
        batch = handles[i:i + BATCH_SIZE]
        print(f"  Batch {i//BATCH_SIZE + 1}: {len(batch)} handles ({', '.join(batch[:5])}{'...' if len(batch) > 5 else ''}) ... ", end="", flush=True)

        results = fetch_ig_posts_batch(batch, results_limit=12)

        for h in batch:
            posts = results.get(h, [])
            ig_cache[h] = {
                "posts": posts,
                "fetched_at": now_iso,
            }
            total_posts += len(posts)
            fetched += 1

        batch_total = sum(len(results.get(h, [])) for h in batch)
        print(f"{batch_total} posts")

        if i + BATCH_SIZE < len(handles):
            time.sleep(2)

    print(f"\n  IG summary: {fetched} handles fetched, {total_posts} posts cached")
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
        print("\n── Instagram / Apify ──")
        if not APIFY_API_TOKEN:
            print("  ⚠ APIFY_API_TOKEN not set — skipping IG")
        else:
            cache["ig"] = refresh_ig_cache(ig_handles, cache)

    cache["refreshed_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    save_cache(cache)

    elapsed = time.time() - start
    x_total = sum(len(v.get("posts", [])) for v in cache.get("x", {}).values())
    ig_total = sum(len(v.get("posts", [])) for v in cache.get("ig", {}).values())
    print(f"\n═══ Done in {elapsed:.1f}s ═══")
    print(f"Cache: {x_total} X posts + {ig_total} IG posts → {CACHE_PATH}")


if __name__ == "__main__":
    main()
