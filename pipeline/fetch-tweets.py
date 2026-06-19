#!/usr/bin/env python3
"""
fetch-tweets.py — Fetch recent tweets with photos from registry handles via X API v2.

Given an article's topic and matched handles, returns the best tweet to embed:
prioritizes tweets WITH photos, most recent, and most relevant text.

Usage:
  python3 fetch-tweets.py <handle> [--hours 48] [--photos-only] [--json]
  python3 fetch-tweets.py --match-article <article_id>

Env: ~/.env.twitter (TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
"""

import os
import sys
import json
import re
import argparse
import requests
from datetime import datetime, timezone, timedelta
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ─── Resilient HTTP session ───────────────────────────────────────────────────

_session = requests.Session()
_retry = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
_session.mount("https://", HTTPAdapter(max_retries=_retry))

# ─── Auth ──────────────────────────────────────────────────────────────────────

def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip())

load_env(os.path.expanduser("~/workspace/.env.twitter"))
load_env(os.path.expanduser("~/workspace/.env.supabase"))

# NOTE (2026-06-18): The app-only OAuth2 bearer flow (POST /oauth2/token) hangs
# indefinitely through the egress proxy — every X read job stalled there, which
# looked like "depleted credits" but was purely an auth-path bug. The account and
# quota are fine. We now sign requests with OAuth 1.0a user context (same 4 keys
# already in .env.twitter), which works through the proxy and needs no new creds.

_oauth_session_cache = None

def get_oauth_session():
    """Return an OAuth1 user-context session for X API v2 reads."""
    global _oauth_session_cache
    if _oauth_session_cache is not None:
        return _oauth_session_cache
    from requests_oauthlib import OAuth1Session
    ck = os.environ.get("TWITTER_CONSUMER_KEY", "")
    cs = os.environ.get("TWITTER_CONSUMER_SECRET", "")
    at = os.environ.get("TWITTER_ACCESS_TOKEN", "")
    ats = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET", "")
    if not all([ck, cs, at, ats]):
        raise RuntimeError("Missing OAuth1 keys in .env.twitter "
                           "(need TWITTER_CONSUMER_KEY/SECRET + ACCESS_TOKEN/SECRET)")
    s = OAuth1Session(ck, cs, at, ats)
    s.mount("https://", HTTPAdapter(max_retries=_retry))
    _oauth_session_cache = s
    return s


# ─── User ID lookup (cached) ──────────────────────────────────────────────────

USER_ID_CACHE_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/.x-user-ids.json")

def load_user_id_cache():
    if os.path.exists(USER_ID_CACHE_PATH):
        with open(USER_ID_CACHE_PATH) as f:
            return json.load(f)
    return {}

def save_user_id_cache(cache):
    with open(USER_ID_CACHE_PATH, "w") as f:
        json.dump(cache, f, indent=2)

def get_user_id(handle):
    cache = load_user_id_cache()
    handle_lower = handle.lower()
    if handle_lower in cache:
        return cache[handle_lower]

    sess = get_oauth_session()
    resp = sess.get(
        f"https://api.twitter.com/2/users/by/username/{handle}",
        timeout=15,
    )
    if resp.status_code == 200:
        uid = resp.json().get("data", {}).get("id")
        if uid:
            cache[handle_lower] = uid
            save_user_id_cache(cache)
            return uid
    return None


# ─── Fetch tweets ─────────────────────────────────────────────────────────────

def fetch_recent_tweets(handle, hours=48, max_results=10):
    """
    Fetch recent tweets from a handle via X API v2.
    Returns list of dicts with id, text, created_at, photos (list of URLs), has_video.
    """
    uid = get_user_id(handle)
    if not uid:
        return []

    sess = get_oauth_session()
    start_time = (datetime.now(timezone.utc) - timedelta(hours=hours)).strftime("%Y-%m-%dT%H:%M:%SZ")

    params = {
        "max_results": min(max_results, 100),
        "start_time": start_time,
        "tweet.fields": "created_at,attachments,text,public_metrics",
        "expansions": "attachments.media_keys",
        "media.fields": "type,url,preview_image_url,width,height",
        "exclude": "retweets,replies",
    }

    resp = sess.get(
        f"https://api.twitter.com/2/users/{uid}/tweets",
        params=params,
        timeout=20,
    )

    if resp.status_code != 200:
        print(f"X API error {resp.status_code}: {resp.text[:200]}", file=sys.stderr)
        return []

    data = resp.json()
    tweets_raw = data.get("data", [])

    # Build media lookup
    media_map = {}
    for m in data.get("includes", {}).get("media", []):
        media_map[m["media_key"]] = m

    results = []
    for t in tweets_raw:
        media_keys = t.get("attachments", {}).get("media_keys", [])
        photos = []
        has_video = False
        for mk in media_keys:
            m = media_map.get(mk)
            if not m:
                continue
            if m["type"] == "photo":
                photos.append(m.get("url", ""))
            elif m["type"] in ("video", "animated_gif"):
                has_video = True

        metrics = t.get("public_metrics", {})
        results.append({
            "id": t["id"],
            "text": t.get("text", ""),
            "created_at": t.get("created_at", ""),
            "photos": photos,
            "photo_count": len(photos),
            "has_video": has_video,
            "url": f"https://x.com/{handle}/status/{t['id']}",
            "likes": metrics.get("like_count", 0),
            "retweets": metrics.get("retweet_count", 0),
        })

    return results


def best_photo_tweet(handle, hours=48, topic_keywords=None):
    """
    Get the single best tweet to embed: prefer photos, then relevance, then recency.
    """
    tweets = fetch_recent_tweets(handle, hours=hours)
    if not tweets:
        return None

    photo_tweets = [t for t in tweets if t["photo_count"] > 0]

    # If topic keywords given, score by relevance
    if topic_keywords and photo_tweets:
        for t in photo_tweets:
            text_lower = t["text"].lower()
            t["_relevance"] = sum(1 for kw in topic_keywords if kw.lower() in text_lower)
        photo_tweets.sort(key=lambda t: (-t["_relevance"], -t["likes"]))
        if photo_tweets[0]["_relevance"] > 0:
            return photo_tweets[0]

    # Fallback: most-liked photo tweet
    if photo_tweets:
        photo_tweets.sort(key=lambda t: -t["likes"])
        return photo_tweets[0]

    # No photo tweets — return most-liked overall
    tweets.sort(key=lambda t: -t["likes"])
    return tweets[0] if tweets else None


# ─── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch recent tweets from X API")
    parser.add_argument("handle", nargs="?", help="X handle (without @)")
    parser.add_argument("--hours", type=int, default=48, help="Look back N hours (default 48)")
    parser.add_argument("--photos-only", action="store_true", help="Only show tweets with photos")
    parser.add_argument("--topic", type=str, help="Comma-separated topic keywords for relevance scoring")
    parser.add_argument("--best", action="store_true", help="Return only the single best tweet")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    if not args.handle:
        parser.print_help()
        sys.exit(1)

    if args.best:
        keywords = args.topic.split(",") if args.topic else None
        tweet = best_photo_tweet(args.handle, hours=args.hours, topic_keywords=keywords)
        if tweet:
            if args.json:
                print(json.dumps(tweet, indent=2))
            else:
                media = f"📸{tweet['photo_count']}" if tweet['photo_count'] else "📝"
                print(f"{media} {tweet['created_at'][:16]}")
                print(f"   {tweet['text'][:120]}")
                print(f"   {tweet['url']}")
                print(f"   ❤️ {tweet['likes']}  🔁 {tweet['retweets']}")
        else:
            print(f"No tweets from @{args.handle} in last {args.hours}h")
        sys.exit(0)

    tweets = fetch_recent_tweets(args.handle, hours=args.hours)

    if args.photos_only:
        tweets = [t for t in tweets if t["photo_count"] > 0]

    if args.json:
        print(json.dumps(tweets, indent=2))
    else:
        print(f"@{args.handle} — {len(tweets)} tweets in last {args.hours}h\n")
        for t in tweets:
            media = f"📸{t['photo_count']}" if t['photo_count'] else ("🎥" if t['has_video'] else "📝")
            print(f"{media} {t['created_at'][:16]} — {t['text'][:90].replace(chr(10), ' ')}")
            print(f"   {t['url']}  ❤️ {t['likes']}")
            print()
