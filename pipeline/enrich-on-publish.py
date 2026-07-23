#!/usr/bin/env python3
"""
enrich-on-publish.py — Enrich articles with social embeds + hero image upgrade at publish time.

Uses the cached handle posts (from refresh-embed-cache.py) for instant
handle-based enrichment, plus live TwitterAPI.io search for articles
without registry matches.

This script handles:
  - X (Twitter) embed enrichment (cache + live search)
  - Instagram embed enrichment (cache + Apify live)
  - YouTube embed enrichment (Data API)
  - Hero image upgrade: replaces Pexels/stock heroes with real photos from
    authoritative tweets (with entity gate + graphic card filter)

Usage:
  python3 -u enrich-on-publish.py --hours 3              # dry run, last 3h
  python3 -u enrich-on-publish.py --hours 3 --apply      # apply changes
  python3 -u enrich-on-publish.py --article-ids ID1,ID2 --apply

Env: ~/workspace/.env.supabase, ~/workspace/.env.twitterapi-io,
     ~/workspace/.env.apify, ~/workspace/.env.youtube
"""

import os
import sys
import json
import re
import time
import subprocess
import argparse
from datetime import datetime, timezone, timedelta

_dir = os.path.dirname(os.path.abspath(__file__))
REGISTRY_PATH = os.path.join(_dir, "social-embed-registry.json")
CACHE_PATH = os.path.join(_dir, "cache", "embed_cache.json")
VERIFY_SCRIPT = os.path.join(_dir, "verify-tweet.sh")

# ─── Env ──────────────────────────────────────────────────────────────────────

def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip())

load_env(os.path.expanduser("~/workspace/.env.supabase"))
load_env(os.path.expanduser("~/workspace/.env.twitterapi-io"))
load_env(os.path.expanduser("~/workspace/.env.apify"))
load_env(os.path.expanduser("~/workspace/.env.youtube"))
load_env(os.path.expanduser("~/workspace/.env.openai"))

SB_URL = os.environ.get("SUPABASE_URL", "")
SB_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
TWITTERAPI_IO_KEY = os.environ.get("TWITTERAPI_IO_KEY", "")
TWITTERAPI_IO_BASE = os.environ.get("TWITTERAPI_IO_BASE", "https://api.twitterapi.io")
OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "")

# Categories eligible for social embeds
EMBED_CATEGORIES = {
    "news", "sports", "entertainment", "technology",
    "nri-world", "immigration", "markets-finance", "travel", "food",
    "lifestyle-health",
}


# ─── Key Takeaways generation ────────────────────────────────────────────────

def generate_key_takeaways(headline, body):
    """Generate 3-4 key takeaway bullet points from article headline + body using GPT-4o-mini."""
    if not OPENAI_KEY:
        return None
    # Strip HTML tags for a clean text input
    text = re.sub(r'<[^>]+>', ' ', body)
    text = re.sub(r'\s+', ' ', text).strip()
    # Limit to first ~2000 chars to save tokens
    text = text[:2000]

    prompt = f"""Given this news article headline and body, write 3-4 concise key takeaway bullet points.
Each bullet should be a single sentence capturing an essential fact. Write so a busy reader gets the full picture in 10 seconds.
Do NOT start bullets with "Key Takeaway:" or similar labels. Just the fact.

Headline: {headline}

Body: {text}

Return ONLY a JSON array of strings, e.g. ["First takeaway.", "Second takeaway.", "Third takeaway."]"""

    import tempfile
    payload = json.dumps({
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"},
        "max_tokens": 300,
        "temperature": 0,
    })
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
        tmp.write(payload)
        tmp_path = tmp.name

    try:
        cmd = [
            "curl", "-sS", "--max-time", "30",
            "-X", "POST", "https://api.openai.com/v1/chat/completions",
            "-H", f"Authorization: Bearer {OPENAI_KEY}",
            "-H", "Content-Type: application/json",
            "-d", f"@{tmp_path}",
        ]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=40)
        if r.returncode != 0:
            return None

        data = json.loads(r.stdout)
        if "error" in data:
            print(f"     ⚠ Key takeaways LLM error: {data['error'].get('message', '')}")
            return None

        content_str = data["choices"][0]["message"]["content"]
        content = json.loads(content_str)
        # Handle both {"takeaways": [...]} and direct [...]
        if isinstance(content, list):
            items = content
        elif isinstance(content, dict):
            # Try common keys
            items = content.get("takeaways") or content.get("key_takeaways") or content.get("bullets") or content.get("items") or []
            if not items:
                # Take the first list value found
                for v in content.values():
                    if isinstance(v, list):
                        items = v
                        break
        else:
            return None

        if not items or not isinstance(items, list):
            return None

        # Build HTML
        li_items = "\n".join(f"<li>{item}</li>" for item in items if isinstance(item, str) and item.strip())
        if not li_items:
            return None
        return f'<div class="key-takeaways"><ul>\n{li_items}\n</ul></div>'
    except Exception as e:
        print(f"     ⚠ Key takeaways error: {e}")
        return None
    finally:
        os.unlink(tmp_path)

# ─── Supabase helpers (curl-based) ────────────────────────────────────────────

def sb_get(endpoint, params=None):
    """GET from Supabase REST API via curl."""
    url = f"{SB_URL}/rest/v1/{endpoint}"
    cmd = ["curl", "-sS", url,
           "-H", f"apikey: {SB_KEY}",
           "-H", f"Authorization: Bearer {SB_KEY}"]
    if params:
        for k, v in params.items():
            cmd += ["-G", "--data-urlencode", f"{k}={v}"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return json.loads(r.stdout)
    except Exception as e:
        print(f"  ⚠ Supabase GET error: {e}")
        return []


def sb_patch(article_id, updates):
    """PATCH article in Supabase via curl."""
    url = f"{SB_URL}/rest/v1/p2_articles?id=eq.{article_id}"
    payload = json.dumps(updates)
    try:
        r = subprocess.run(
            ["curl", "-sS", "-X", "PATCH", url,
             "-H", f"apikey: {SB_KEY}",
             "-H", f"Authorization: Bearer {SB_KEY}",
             "-H", "Content-Type: application/json",
             "-H", "Prefer: return=minimal",
             "-d", payload],
            capture_output=True, text=True, timeout=15,
        )
        return r.returncode == 0
    except Exception as e:
        print(f"  ⚠ Supabase PATCH error: {e}")
        return False


# ─── Cache ────────────────────────────────────────────────────────────────────

def load_cache():
    """Load embed cache from disk."""
    if os.path.exists(CACHE_PATH):
        try:
            with open(CACHE_PATH) as f:
                cache = json.load(f)
            age = "unknown"
            if cache.get("refreshed_at"):
                try:
                    refreshed = datetime.fromisoformat(cache["refreshed_at"].replace("Z", "+00:00"))
                    age_min = (datetime.now(timezone.utc) - refreshed).total_seconds() / 60
                    age = f"{age_min:.0f}m ago"
                except:
                    pass
            print(f"  Cache loaded ({age}): {sum(len(v.get('posts',[])) for v in cache.get('x',{}).values())} X posts, "
                  f"{sum(len(v.get('posts',[])) for v in cache.get('ig',{}).values())} IG posts")
            return cache
        except (json.JSONDecodeError, IOError) as e:
            print(f"  ⚠ Cache load failed: {e}")
    else:
        print("  ⚠ No cache file found — handle-based enrichment will be skipped")
    return {"x": {}, "ig": {}, "refreshed_at": None}


# ─── Registry ────────────────────────────────────────────────────────────────

def load_registry():
    """Load the social embed registry."""
    with open(REGISTRY_PATH) as f:
        return json.load(f)


def match_handles(headline, registry, platform):
    """Match article headline to registry handles for a platform.
    Returns list of {name, handle, category, platform}."""
    headline_lower = headline.lower()
    matches = []

    for category, data in registry.items():
        if category.startswith("_") or not isinstance(data, dict):
            continue
        for group in ("persons", "organizations"):
            for entry in data.get(group, []):
                name = entry.get("name", "")
                handle = entry.get(platform, entry.get(f"{platform}_handle", ""))
                if not handle:
                    continue

                name_parts = name.lower().split()
                stopwords = {"the", "of", "in", "and", "for", "a", "an", "is", "at", "on", "to"}
                significant = [p for p in name_parts if p not in stopwords and len(p) > 2]
                if not significant:
                    continue

                if all(re.search(r'\b' + re.escape(w) + r'\b', headline_lower) for w in significant):
                    matches.append({
                        "name": name,
                        "handle": handle.lower(),
                        "category": category,
                        "platform": platform,
                        "group": group,  # "persons" or "organizations"
                    })

    return matches


# ─── X enrichment ─────────────────────────────────────────────────────────────

def score_tweet_relevance(tweet_text, headline, body_500):
    """Score how relevant a tweet is to an article (0-10)."""
    headline_words = set(
        w.lower() for w in re.findall(r'[a-zA-Z]{4,}', headline)
    ) - {"that", "this", "with", "from", "have", "been", "will", "just", "says",
         "about", "their", "after", "what", "when", "more", "than", "also"}

    tweet_lower = tweet_text.lower()
    matches = sum(1 for w in headline_words if w in tweet_lower)

    if any(w in tweet_lower for w in headline_words if len(w) > 5):
        matches += 2

    return min(matches, 10)


def source_authority(tweet):
    """Score source authority: 0=low, 1=mid, 2=credible, 3=official."""
    followers = tweet.get("followers", 0) or 0
    verified = tweet.get("verified", False)
    handle = (tweet.get("handle", "") or "").lower()

    OFFICIAL_HANDLES = {
        "ndtv", "httweets", "timesofindia", "indiatoday", "ani",
        "reuters", "ap", "bbcnews", "cnn", "nytimes", "washingtonpost",
        "cnbc", "bloomberg", "forbes", "wsj", "bcci", "icc",
        "techcrunch", "wired", "theverge",
    }

    if handle in OFFICIAL_HANDLES:
        return 3
    if verified and followers >= 100_000:
        return 3
    if verified and followers >= 10_000:
        return 2
    if followers >= 50_000:
        return 2
    if (verified and followers >= 5_000) or followers >= 25_000:
        return 1
    return 0


def build_topic_query(headline):
    """Extract 3-5 distinctive keywords from headline for topic search."""
    stopwords = {"the","a","an","in","on","at","to","for","of","and","or","is","are",
                 "was","were","has","had","have","been","be","will","can","may","with",
                 "its","it","by","from","that","this","says","said","after","over",
                 "new","set","how","why","what","who","but","not","all","into","up"}
    words = re.findall(r'[A-Za-z]{3,}', headline)
    keywords = [w for w in words if w.lower() not in stopwords]
    return " ".join(keywords[:5])


def live_search_x(query, max_results=10, hours=48):
    """Live search TwitterAPI.io (for topic-based search, not cached)."""
    if not TWITTERAPI_IO_KEY:
        return []
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
            return []
        data = json.loads(result.stdout)
    except Exception:
        return []

    raw_tweets = data.get("tweets", [])
    if not raw_tweets:
        return []

    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    results = []
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

        results.append({
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

    # Filter self-citations
    results = [t for t in results if (t.get("handle", "") or "").lower() != "thevideshi"]
    return results


def verify_tweet(tweet_id):
    """Verify tweet renders via react-tweet API."""
    try:
        result = subprocess.run(
            ["bash", VERIFY_SCRIPT, str(tweet_id)],
            capture_output=True, text=True, timeout=10,
        )
        return result.returncode == 0 and result.stdout.strip().startswith("VALID")
    except Exception:
        return False


def find_best_tweet(tweets, headline, body_500, min_score=5):
    """Score tweets and return the best one above min_score, or None."""
    best_tweet = None
    best_score = 0

    for tweet in tweets:
        topic_score = score_tweet_relevance(tweet["text"], headline, body_500)
        # Require minimum topic relevance of 5 before considering authority/photo bonuses.
        # Scoring: entity name match (~1) + long-word bonus (+2) = ~3-4 baseline.
        # Entity name + one coincidental verb (e.g. "build") = 4, NOT enough.
        # A genuinely on-topic tweet has 3+ real keyword overlaps → score 5+.
        # This prevents high-authority accounts (NVIDIA, Google) from embedding
        # any random tweet just because they're verified with many followers.
        if topic_score < 5:
            continue
        score = topic_score
        if tweet.get("photo_count", 0) > 0:
            score += 3
        authority = source_authority(tweet)
        score += authority
        if score < min_score:
            continue
        if score > best_score:
            best_score = score
            best_tweet = tweet

    return best_tweet, best_score


def enrich_x_from_cache(article, cache, registry):
    """Try handle-based X enrichment from cache. Returns (tweet, source_info) or (None, None)."""
    headline = article["headline"]
    body_500 = (article.get("body") or "")[:500]

    x_matches = match_handles(headline, registry, "x")
    if not x_matches:
        return None, None

    x_cache = cache.get("x", {})

    for m in x_matches[:3]:
        handle = m["handle"]
        cached = x_cache.get(handle)
        if not cached or not cached.get("posts"):
            continue

        tweets = cached["posts"]
        best, score = find_best_tweet(tweets, headline, body_500, min_score=5)
        if best:
            return best, {"source": "cache", "handle": handle, "name": m["name"], "score": score}

    return None, None


def enrich_x_from_search(article):
    """Try topic-search X enrichment (live API call). Returns (tweet, source_info) or (None, None)."""
    headline = article["headline"]
    body_500 = (article.get("body") or "")[:500]

    topic_q = build_topic_query(headline)
    if not topic_q:
        return None, None

    tweets = live_search_x(topic_q, max_results=10, hours=48)
    if not tweets:
        return None, None

    # Sort by authority then views
    tweets.sort(key=lambda t: (source_authority(t), t.get("views", 0) or 0), reverse=True)

    # Filter low-authority
    tweets = [t for t in tweets if source_authority(t) >= 1]

    best, score = find_best_tweet(tweets, headline, body_500, min_score=5)
    if best:
        return best, {"source": "search", "handle": best.get("handle", "?"), "score": score}

    return None, None


# ─── IG enrichment from cache ────────────────────────────────────────────────

def fetch_ig_posts_live(handles, results_limit=12):
    """Live-fetch recent posts from IG handles via Apify. Returns {handle: [posts]}."""
    token = os.environ.get("APIFY_API_TOKEN", "")
    if not token or not handles:
        return {}

    payload = json.dumps({
        "username": handles,
        "resultsLimit": results_limit,
    })

    try:
        result = subprocess.run(
            ["curl", "-sS", "-X", "POST",
             f"https://api.apify.com/v2/acts/apify~instagram-post-scraper/run-sync-get-dataset-items?token={token}",
             "-H", "Content-Type: application/json",
             "-d", payload],
            capture_output=True, text=True, timeout=180,
        )
        if result.returncode != 0:
            return {}
        data = json.loads(result.stdout)
        if isinstance(data, dict) and "error" in data:
            err_msg = data["error"].get("message", "")
            if "limit exceeded" in err_msg.lower():
                print(f"     ⚠ Apify monthly limit exceeded — skipping IG")
            else:
                print(f"     ⚠ Apify error: {err_msg[:80]}")
            return {}
    except Exception as e:
        print(f"     ⚠ Apify call failed: {e}")
        return {}

    by_handle = {}
    for item in data:
        owner = (item.get("ownerUsername") or "").lower()
        if not owner:
            input_url = item.get("inputUrl", "")
            m = re.search(r"instagram\.com/([^/]+)", input_url)
            owner = m.group(1).lower() if m else ""
        if owner:
            by_handle.setdefault(owner, []).append(item)
    return by_handle


def prefetch_ig_for_articles(articles, registry):
    """Collect matched IG handles across all articles and batch-fetch via Apify.
    Returns a dict like the ig cache: {handle: {"posts": [...], "fetched_at": ...}}
    """
    all_handles = set()
    for article in articles:
        headline = article.get("headline", "")
        body = article.get("body", "")
        if has_embed(body, "instagram"):
            continue  # already has an IG embed
        matches = match_handles(headline, registry, "instagram")
        for m in matches[:3]:
            all_handles.add(m["handle"].lower())

    if not all_handles:
        return {}

    handles_list = sorted(all_handles)
    print(f"\n  IG pre-fetch: {len(handles_list)} handles via Apify ({', '.join(handles_list[:5])}{'...' if len(handles_list) > 5 else ''})")

    results = fetch_ig_posts_live(handles_list, results_limit=12)
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    ig_live = {}
    total = 0
    for h in handles_list:
        posts = results.get(h, [])
        ig_live[h] = {"posts": posts, "fetched_at": now_iso}
        total += len(posts)
    print(f"  IG pre-fetch: {total} posts from {len([h for h in ig_live if ig_live[h]['posts']])} handles\n")
    return ig_live


def enrich_ig_from_cache(article, cache, registry, live_ig=None):
    """Try handle-based IG enrichment from cache or live fetch. Returns shortcode or None."""
    headline = article["headline"]
    ig_matches = match_handles(headline, registry, "instagram")
    if not ig_matches:
        return None, None

    # Merge cache and live data — live takes precedence
    ig_cache = cache.get("ig", {})
    if live_ig:
        merged = {**ig_cache, **live_ig}
    else:
        merged = ig_cache

    # Build topic keywords from headline
    stopwords = {
        "the","a","an","in","on","at","to","for","of","and","or","is","are",
        "was","were","has","had","have","been","be","will","can","may","with",
        "by","from","as","its","it","his","her","their","new","says","said",
        "after","over","how","why","what","who","than","amid","that","this",
    }

    for m in ig_matches[:3]:
        handle = m["handle"]
        cached = merged.get(handle)
        if not cached or not cached.get("posts"):
            continue

        # Exclude entity name words and stopwords from keywords
        name_words = {w.lower().strip(".,!?:;-'\"") for w in m["name"].split()}
        exclude = stopwords | name_words
        topic_kw = [
            w for w in headline.split()
            if len(w) > 2 and w.lower().strip(".,!?:;-'\"") not in exclude
        ]

        posts = cached["posts"]

        # First pass: try caption relevance matching (best if we find a topical post)
        scored = []
        for post in posts:
            caption = (post.get("caption", "") or "").lower()
            if not caption:
                continue
            keywords = [w.lower().strip(".,!?:;-") for w in topic_kw if len(w) > 2]
            hits = sum(1 for kw in keywords if kw in caption)
            if hits >= 2 or (hits >= 1 and len(keywords) <= 2):
                sc = post.get("shortCode", "")
                if sc:
                    scored.append((hits, sc, post))

        if scored:
            scored.sort(key=lambda x: -x[0])
            shortcode = scored[0][1]
            return shortcode, {"handle": handle, "name": m["name"]}

        # Second pass: no topical match — embed the most recent post ONLY for person handles.
        # For org handles (NVIDIA, Google, etc.), the latest post is about some
        # random product/announcement, not the article topic — irrelevant.
        # For persons, showing their latest post adds social proof and visual engagement.
        if m.get("group") == "persons":
            for post in posts:
                sc = post.get("shortCode", "")
                if sc:
                    return sc, {"handle": handle, "name": m["name"]}

    return None, None


# ─── YouTube enrichment ──────────────────────────────────────────────────────

_YT_ENV = None
_YT_ACCESS_TOKEN = None
_YT_TOKEN_EXPIRY = 0
_YT_QUOTA_USED = 0
_YT_QUOTA_LIMIT = 9500


def _load_yt_env():
    global _YT_ENV
    if _YT_ENV is None:
        _YT_ENV = {}
        path = os.path.expanduser("~/workspace/.env.youtube")
        if os.path.exists(path):
            with open(path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        _YT_ENV[k.strip()] = v.strip()
    return _YT_ENV


def _get_youtube_access_token():
    global _YT_ACCESS_TOKEN, _YT_TOKEN_EXPIRY
    if _YT_ACCESS_TOKEN and time.time() < _YT_TOKEN_EXPIRY:
        return _YT_ACCESS_TOKEN
    env = _load_yt_env()
    cid = env.get("YOUTUBE_CLIENT_ID", "")
    csec = env.get("YOUTUBE_CLIENT_SECRET", "")
    rtok = env.get("YOUTUBE_REFRESH_TOKEN", "")
    if not (cid and csec and rtok):
        return None
    try:
        payload = json.dumps({
            "client_id": cid, "client_secret": csec,
            "refresh_token": rtok, "grant_type": "refresh_token",
        })
        r = subprocess.run(
            ["curl", "-sS", "-X", "POST", "https://oauth2.googleapis.com/token",
             "-H", "Content-Type: application/json", "-d", payload],
            capture_output=True, text=True, timeout=10,
        )
        data = json.loads(r.stdout)
        _YT_ACCESS_TOKEN = data.get("access_token")
        _YT_TOKEN_EXPIRY = time.time() + data.get("expires_in", 3600) - 120
        return _YT_ACCESS_TOKEN
    except Exception as e:
        print(f"  ⚠ YouTube token error: {e}")
        return None


def search_youtube(query, max_results=5, published_after_days=60):
    """Search YouTube Data API v3 via curl."""
    global _YT_QUOTA_USED
    if _YT_QUOTA_USED >= _YT_QUOTA_LIMIT:
        return []
    token = _get_youtube_access_token()
    if not token:
        return []

    after = (datetime.now(timezone.utc) - timedelta(days=published_after_days)).strftime("%Y-%m-%dT%H:%M:%SZ")

    try:
        r = subprocess.run(
            ["curl", "-sS",
             "https://www.googleapis.com/youtube/v3/search",
             "-H", f"Authorization: Bearer {token}",
             "-G",
             "--data-urlencode", f"q={query}",
             "-d", "part=snippet",
             "-d", "type=video",
             "-d", f"maxResults={max_results}",
             "-d", "order=relevance",
             "-d", "relevanceLanguage=en",
             "--data-urlencode", f"publishedAfter={after}"],
            capture_output=True, text=True, timeout=15,
        )
        _YT_QUOTA_USED += 100
        data = json.loads(r.stdout)
        if "error" in data:
            print(f"  ⚠ YouTube API error: {json.dumps(data['error'])[:200]}")
            return []
        results = []
        for item in data.get("items", []):
            results.append({
                "videoId": item["id"]["videoId"],
                "title": item["snippet"]["title"],
                "channelTitle": item["snippet"]["channelTitle"],
                "publishedAt": item["snippet"]["publishedAt"],
            })
        return results
    except Exception as e:
        print(f"  ⚠ YouTube search error: {e}")
        return []


_YT_SKIP_TITLE_WORDS = {
    "compilation", "top 10", "top 5", "top 20", "meme", "memes", "funny",
    "prank", "reaction video", "fan edit", "whatsapp status",
    "#shorts", "tiktok", "roast", "exposed", "scam",
    # Music / entertainment junk
    "official audio", "official video", "music video", "lyrics", "lyric video",
    "audio only", "full album", "mixtape", "beat", "instrumental", "karaoke",
    "remix", "cover song", "dance cover", "fan cam", "fancam",
    # Other irrelevant content types
    "unboxing", "haul", "asmr", "mukbang", "gameplay", "walkthrough",
    "let's play", "speedrun", "tutorial makeup",
}

# Non-Latin script ranges (Devanagari, Telugu, Tamil, Bengali, Kannada, Malayalam,
# Gujarati, Gurmukhi, Arabic, Thai, CJK, etc.)
import unicodedata as _ud

def _is_non_english_title(title: str) -> bool:
    """Return True if >25% of alpha chars are non-Latin script."""
    alpha_chars = [c for c in title if c.isalpha()]
    if len(alpha_chars) < 3:
        return False
    non_latin = sum(1 for c in alpha_chars if _ud.category(c).startswith('L') and ord(c) > 0x024F)
    return (non_latin / len(alpha_chars)) > 0.25


def _check_yt_video_language(video_ids: list) -> dict:
    """Check defaultAudioLanguage for a batch of video IDs. Returns {id: lang_code}."""
    if not video_ids:
        return {}
    global _YT_QUOTA_USED
    if _YT_QUOTA_USED >= _YT_QUOTA_LIMIT:
        return {}
    token = _get_youtube_access_token()
    if not token:
        return {}
    try:
        r = subprocess.run(
            ["curl", "-sS",
             "https://www.googleapis.com/youtube/v3/videos",
             "-H", f"Authorization: Bearer {token}",
             "-G",
             "-d", "part=snippet",
             "-d", f"id={','.join(video_ids[:10])}"],
            capture_output=True, text=True, timeout=15,
        )
        _YT_QUOTA_USED += 1
        data = json.loads(r.stdout)
        result = {}
        for item in data.get("items", []):
            lang = item.get("snippet", {}).get("defaultAudioLanguage") or item.get("snippet", {}).get("defaultLanguage") or ""
            result[item["id"]] = lang.lower()
        return result
    except:
        return {}


def score_youtube_result(result, entity_name, keywords):
    """Score YouTube result for relevance."""
    title_lower = result["title"].lower()
    channel_lower = result["channelTitle"].lower()
    entity_lower = entity_name.lower()
    entity_parts = [p for p in entity_lower.split() if len(p) > 2]

    score = 0
    if entity_lower in title_lower:
        score += 4
    elif all(p in title_lower for p in entity_parts):
        score += 3
    if entity_lower in channel_lower:
        score += 3
    elif any(p in channel_lower for p in entity_parts if p not in {"the", "of", "in"}):
        score += 1

    kw_hits = sum(1 for kw in keywords if kw in title_lower)
    score += kw_hits * 1.5

    for skip_word in _YT_SKIP_TITLE_WORDS:
        if skip_word in title_lower:
            score -= 5

    # "official" bonus — but NOT for music content (official audio/video/music)
    _music_official = {"official audio", "official music", "official video", "official mv"}
    is_music_official = any(mo in title_lower for mo in _music_official)
    if not is_music_official:
        official_words = {"official", "press conference", "interview", "statement",
                          "announcement", "keynote", "launch", "podcast", "speech"}
        for ow in official_words:
            if ow in title_lower:
                score += 1
                break

    # Channel relevance penalty — if channel has zero overlap with entity or keywords,
    # it's likely an unrelated channel (random music, gaming, etc.)
    _channel_words = set(re.findall(r'[a-z]{3,}', channel_lower))
    _entity_words = set(re.findall(r'[a-z]{3,}', entity_lower))
    _all_relevant = _entity_words | set(keywords)
    if _channel_words and not (_channel_words & _all_relevant):
        score -= 2

    try:
        pub = datetime.fromisoformat(result["publishedAt"].replace("Z", "+00:00"))
        days_old = (datetime.now(timezone.utc) - pub).days
        if days_old <= 3:
            score += 2
        elif days_old <= 7:
            score += 1
    except:
        pass

    return score


def enrich_youtube(article, registry):
    """Try YouTube enrichment. Returns (url, info) or (None, None)."""
    headline = article["headline"]
    headline_lower = headline.lower()

    # Find matching entities in registry
    entity_matches = []
    for category, data in registry.items():
        if category.startswith("_") or not isinstance(data, dict):
            continue
        for group in ("persons", "organizations"):
            for entry in data.get(group, []):
                name = entry.get("name", "")
                name_parts = name.lower().split()
                stopwords = {"the", "of", "in", "and", "for", "a", "an", "is", "at", "on", "to"}
                significant = [p for p in name_parts if p not in stopwords and len(p) > 2]
                if not significant:
                    continue
                if all(re.search(r'\b' + re.escape(w) + r'\b', headline_lower) for w in significant):
                    entity_matches.append({"name": name, "category": category})

    if not entity_matches:
        return None, None

    best_yt = None
    for entity in entity_matches[:2]:
        name = entity["name"]
        # Extract search keywords from headline minus entity name
        clean = re.sub(re.escape(name), "", headline, flags=re.IGNORECASE).strip()
        clean = re.sub(r"[^\w\s]", " ", clean)
        words = clean.lower().split()
        yt_stopwords = {
            "the", "of", "in", "and", "for", "a", "an", "is", "at", "on", "to",
            "with", "by", "from", "as", "its", "it", "that", "this", "but", "or",
            "has", "had", "was", "were", "are", "be", "been", "being", "have",
            "new", "says", "said", "could", "would", "will", "can", "may", "more",
        }
        keywords = [w for w in words if w not in yt_stopwords and len(w) > 2][:4]
        query = f"{name} {' '.join(keywords[:3])}"

        results = search_youtube(query, max_results=5, published_after_days=60)
        if not results:
            continue

        # ── English language filter ──
        # Step 1: Drop results with non-Latin titles (Telugu, Hindi, etc.)
        results = [r for r in results if not _is_non_english_title(r["title"])]
        if not results:
            continue

        # Step 2: Check audio language via API for remaining candidates
        video_ids = [r["videoId"] for r in results]
        lang_map = _check_yt_video_language(video_ids)
        # Keep videos that are English, unlabeled, or have no language data
        english_results = []
        for r in results:
            lang = lang_map.get(r["videoId"], "")
            if lang and not lang.startswith("en"):
                continue  # skip confirmed non-English
            english_results.append(r)
        results = english_results
        if not results:
            continue

        for r in results:
            s = score_youtube_result(r, name, keywords)
            # Require >= 6 AND at least 2 keyword matches beyond entity name
            # Single-word entity names (Google, Apple, Meta) are too generic — require >= 8
            title_lower = r["title"].lower()
            kw_hits = sum(1 for kw in keywords if kw in title_lower)
            min_score = 8 if len(name.split()) == 1 else 6
            if s >= min_score and kw_hits >= 2 and (best_yt is None or s > best_yt["score"]):
                best_yt = {
                    "url": f"https://youtube.com/watch?v={r['videoId']}",
                    "title": r["title"],
                    "channel": r["channelTitle"],
                    "score": s,
                    "entity": name,
                }

    if best_yt:
        return best_yt["url"], best_yt

    return None, None


# ─── Body insertion ──────────────────────────────────────────────────────────

def _count_media_in_text(text):
    """Count media elements (embeds, figures, YouTube tags) in a chunk of HTML."""
    MEDIA_PATS = [
        r'<figure[^>]*>',
        r'<youtube>',
        r'https?://(?:x|twitter)\.com/\w+/status/',
        r'https?://(?:www\.)?instagram\.com/(?:p|reel|tv)/',
    ]
    return sum(len(re.findall(p, text, re.IGNORECASE)) for p in MEDIA_PATS)


def insert_embed_in_body(body, embed_url, platform="x"):
    """Insert an embed as high as possible without clustering with existing media."""
    from embed_placement import insert_embed_high
    if platform == "youtube":
        embed_line = f"\n\n<youtube>{embed_url}</youtube>\n"
    else:
        embed_line = f"\n\n{embed_url}\n"
    return insert_embed_high(body, embed_line)


def has_embed(body, platform):
    """Check if article body already has an embed of this type."""
    if platform in ("x", "twitter"):
        return bool(re.search(r'(?:twitter|x)\.com/\w+/status/', body or ""))
    elif platform == "instagram":
        return bool(re.search(r'instagram\.com/(?:p|reel|tv)/', body or ""))
    elif platform == "youtube":
        return bool(re.search(r'<youtube>.*?</youtube>', body or ""))
    return False


# ─── Hero image upgrade ──────────────────────────────────────────────────────

STOCK_DOMAINS = {"images.pexels.com", "images.unsplash.com", "pixabay.com",
                 "cdn.pixabay.com", "media.istockphoto.com", "thumbs.dreamstime.com"}

def _is_stock_hero(image_url):
    """Check if an image URL is from a stock photo provider."""
    if not image_url:
        return False
    url_lower = image_url.lower()
    return any(d in url_lower for d in STOCK_DOMAINS)


def _extract_distinctive_entities(headline):
    """Extract distinctive proper nouns from a headline for strict matching.
    Returns lowercase set of words specific enough to confirm same-story."""
    GENERIC = {
        "dead", "killed", "trapped", "injured", "dies", "death", "deaths",
        "seven", "eight", "nine", "ten", "dozen", "dozens", "hundreds",
        "two", "three", "four", "five", "six", "many", "several", "multiple",
        "landslide", "earthquake", "flood", "fire", "crash", "blast", "attack",
        "breaking", "news", "update", "report", "latest", "major", "massive",
        "india", "us", "uk", "china",
        "government", "minister", "president", "official", "police", "army",
        "workers", "people", "victims", "rescue", "relief", "tunnel",
        "construction", "under", "gas", "leak", "devastate",
        "new", "old", "first", "last", "top", "best", "worst",
        "says", "said", "announces", "launches", "wins", "loses",
        "scores", "century", "final", "match", "game", "cup",
        "million", "billion", "deal", "stake", "sells", "buys",
        "changes", "cap", "visa", "ban", "rule", "rules", "plan",
        "against", "after", "over", "into", "from", "with",
    }
    # Capitalized words (likely proper nouns)
    words = re.findall(r'\b[A-Z][a-z]{2,}\b', headline)
    # Acronyms (2+ uppercase letters) like USCIS, CRED, NASA
    acronyms = re.findall(r'\b[A-Z]{2,}\b', headline)
    entities = set()
    for w in words:
        if w.lower() not in GENERIC:
            entities.add(w.lower())
    for a in acronyms:
        if a.lower() not in GENERIC:
            entities.add(a.lower())
    return entities


def _download_and_upload_photo(photo_url, slug):
    """Download a tweet photo, verify it's a real photograph (not a graphic card),
    and upload to Supabase storage. Returns public URL or None."""
    import hashlib
    try:
        dl = subprocess.run(
            ["curl", "-sS", "--max-time", "10", "-o", "/tmp/_tweet_hero.jpg", photo_url],
            capture_output=True, timeout=15,
        )
        if dl.returncode != 0:
            return None

        with open("/tmp/_tweet_hero.jpg", "rb") as f:
            img_bytes = f.read()

        if len(img_bytes) < 5000:
            return None

        # ── Graphic card detection ──
        # Text cards on solid backgrounds have mostly near-black/near-white pixels.
        try:
            from PIL import Image
            import io
            img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
            w, h = img.size
            cx, cy = w // 2, h // 2
            crop = img.crop((max(0, cx-100), max(0, cy-100), min(w, cx+100), min(h, cy+100)))
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
                pixels = list(crop.getdata())
            total = len(pixels)
            near_black = sum(1 for r, g, b in pixels if (r + g + b) / 3 < 30)
            near_white = sum(1 for r, g, b in pixels if (r + g + b) / 3 > 225)
            solid_pct = (near_black + near_white) / total
            if solid_pct > 0.6:  # >60% solid = graphic card, not a photo
                return None
        except Exception:
            pass

        # Upload to Supabase storage
        h_hash = hashlib.md5(img_bytes).hexdigest()[:8]
        filename = f"tweet-hero-{slug[:40]}-{h_hash}.jpg"
        url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
        result = subprocess.run(
            ["curl", "-sS", "--max-time", "15", "-X", "POST", url,
             "-H", f"apikey: {SB_KEY}",
             "-H", f"Authorization: Bearer {SB_KEY}",
             "-H", "Content-Type: image/jpeg",
             "-H", "x-upsert: true",
             "--data-binary", "@-"],
            input=img_bytes, capture_output=True, timeout=20,
        )
        stdout = result.stdout.decode("utf-8", errors="replace") if isinstance(result.stdout, bytes) else result.stdout
        if result.returncode == 0:
            try:
                resp_json = json.loads(stdout)
                if "Key" in resp_json or "Id" in resp_json:
                    return f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
            except Exception:
                pass
            if not stdout.strip():
                return f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
        return None
    except Exception as e:
        print(f"     ⚠ Hero upload failed: {e}")
        return None


def try_hero_upgrade(article, all_tweets):
    """If article has a stock hero, try to replace it with a real photo from tweets.

    all_tweets: list of tweet dicts (already scored/filtered).
    Returns dict with upgrade info, or None.

    Uses two gates:
      1. Entity gate: tweet text must mention a distinctive entity from headline
      2. Graphic card filter: rejects text-on-solid-color images
    """
    image_url = article.get("image_url", "") or ""
    if not _is_stock_hero(image_url):
        return None

    headline = article.get("headline", "")
    slug = article.get("slug", "unknown")
    entities = _extract_distinctive_entities(headline)

    # Find best photo tweet by authority + followers, with entity match
    photo_candidates = []
    for tweet in all_tweets:
        photos = tweet.get("photos", [])
        if not photos:
            continue
        auth = source_authority(tweet)
        if auth < 2:
            continue
        # Entity gate: tweet must mention at least one distinctive entity
        if entities:
            tweet_lower = tweet.get("text", "").lower()
            if not any(e in tweet_lower for e in entities):
                continue
        photo_candidates.append((auth, tweet.get("followers", 0) or 0, photos[0], tweet))

    if not photo_candidates:
        return None

    # Pick highest authority, then most followers
    photo_candidates.sort(key=lambda x: (x[0], x[1]), reverse=True)
    best_auth, best_followers, best_photo_url, best_tweet = photo_candidates[0]

    new_hero_url = _download_and_upload_photo(best_photo_url, slug)
    if not new_hero_url:
        return None

    handle = best_tweet.get("handle", "")
    caption = f"Image: @{handle} via X" if handle else "Image via X"

    return {
        "old_hero": image_url,
        "new_hero": new_hero_url,
        "caption": caption,
        "source_handle": f"@{handle}",
        "source_photo": best_photo_url,
    }


# ─── Main ─────────────────────────────────────────────────────────────────────

def fetch_articles(article_ids=None, hours=3):
    """Fetch articles to enrich — either by IDs or recent window."""
    if article_ids:
        # Fetch specific articles
        id_filter = ",".join(f'"{aid}"' for aid in article_ids)
        params = {
            "select": "id,headline,slug,category,body,social_embeds,enriched_at,published_at,image_url",
            "id": f"in.({','.join(article_ids)})",
            "status": "eq.published",
        }
    else:
        since = (datetime.now(timezone.utc) - timedelta(hours=hours)).strftime("%Y-%m-%dT%H:%M:%SZ")
        params = {
            "select": "id,headline,slug,category,body,social_embeds,enriched_at,published_at,image_url",
            "status": "eq.published",
            "published_at": f"gte.{since}",
            "enriched_at": "is.null",
            "order": "published_at.desc",
            "limit": "50",
        }

    return sb_get("p2_articles", params)


def main():
    parser = argparse.ArgumentParser(description="Enrich articles with social embeds at publish time")
    parser.add_argument("--article-ids", type=str, help="Comma-separated article UUIDs")
    parser.add_argument("--hours", type=int, default=3, help="Look back N hours (default 3)")
    parser.add_argument("--apply", action="store_true", help="Apply changes to Supabase")
    parser.add_argument("--max", type=int, default=20, help="Max articles to process")
    args = parser.parse_args()

    print("═══ Enrich on Publish ═══")
    start = time.time()

    # Load resources
    cache = load_cache()
    registry = load_registry()

    # Fetch articles
    article_ids = args.article_ids.split(",") if args.article_ids else None
    articles = fetch_articles(article_ids=article_ids, hours=args.hours)

    if not isinstance(articles, list):
        print(f"  ⚠ Failed to fetch articles: {str(articles)[:200]}")
        return

    # Filter to eligible categories
    eligible = [a for a in articles if a.get("category") in EMBED_CATEGORIES]
    print(f"\nArticles: {len(articles)} total, {len(eligible)} in eligible categories")

    # Pre-fetch IG posts for matched handles (1 Apify call instead of cache)
    ig_cache_empty = not any(
        v.get("posts") for v in cache.get("ig", {}).values()
        if isinstance(v, dict)
    )
    live_ig = {}
    if ig_cache_empty:
        live_ig = prefetch_ig_for_articles(eligible[:args.max], registry)

    report = {"processed": 0, "x_embeds": 0, "ig_embeds": 0, "yt_embeds": 0, "hero_upgrades": 0, "skipped": 0}

    for article in eligible[:args.max]:
        headline = article["headline"]
        body = article.get("body") or ""
        category = article.get("category", "")
        social_embeds = article.get("social_embeds") or []
        # Parse if string (DB may return JSONB as string); guard against corrupted data
        if isinstance(social_embeds, str):
            try:
                social_embeds = json.loads(social_embeds)
                if not isinstance(social_embeds, list):
                    social_embeds = []
            except (json.JSONDecodeError, TypeError):
                social_embeds = []

        print(f"\n  📰 {headline[:75]}")
        print(f"     [{category}] embeds: {len(social_embeds)}")

        new_body = body
        new_embeds = list(social_embeds)
        changes = []

        # ── Dedup pull quotes (LLM sometimes generates identical ones) ──
        pq_pat = re.compile(r'<blockquote class="pull-quote">.*?</blockquote>', re.DOTALL)
        _seen_pqs = set()
        _pq_count = [0]  # mutable counter for closure
        def _dedup_pq(m):
            key = re.sub(r'\s+', ' ', m.group(0)).strip()
            if key in _seen_pqs:
                return ''
            _seen_pqs.add(key)
            _pq_count[0] += 1
            if _pq_count[0] > 2:
                return ''  # cap at 2 pull quotes
            return m.group(0)
        deduped_body = pq_pat.sub(_dedup_pq, new_body)
        if deduped_body != new_body:
            orig_count = len(pq_pat.findall(new_body))
            final_count = len(pq_pat.findall(deduped_body))
            removed_count = orig_count - final_count
            new_body = re.sub(r'\n{3,}', '\n\n', deduped_body)
            changes.append(f"dedup {removed_count} pull quote(s) ({orig_count}→{final_count})")
            print(f"     🔄 Removed {removed_count} pull quote(s) ({orig_count}→{final_count})")

        # ── Key Takeaways — generate if missing ──
        if 'key-takeaways' not in new_body and OPENAI_KEY:
            kt_html = generate_key_takeaways(headline, new_body)
            if kt_html:
                # Prepend to body (strip leading whitespace first)
                new_body = kt_html + "\n\n" + new_body.lstrip()
                changes.append("key-takeaways")
                print(f"     📋 Added key takeaways")

        # Collect all available embeds first, then insert in relevance order
        # so the best match gets the highest placement. Video gets a small
        # boost (+2) since it's inherently more engaging, but a high-relevance
        # tweet or IG post can still outrank a mediocre video.
        pending_embeds = []  # [(score, platform, embed_url, change_label)]

        # ── YouTube enrichment ──
        if not has_embed(body, "youtube"):
            has_x = has_embed(body, "x")
            has_ig = has_embed(body, "instagram")
            if not (has_x and has_ig):
                yt_url, info = enrich_youtube(article, registry)
                if yt_url:
                    yt_score = info.get("score", 5) + 2  # video engagement bonus
                    print(f"     YT: {yt_url} — \"{info['title'][:50]}\" [score:{info['score']}→{yt_score}]")
                    pending_embeds.append((yt_score, "youtube", yt_url, f"YT({info['entity'][:20]})"))
                    report["yt_embeds"] += 1
        else:
            print(f"     YT: already has embed")

        # ── X enrichment ──
        if not has_embed(body, "x"):
            tweet, info = enrich_x_from_cache(article, cache, registry)
            if tweet:
                print(f"     X (cache): @{info['handle']} → {tweet['url'][:60]} [score:{info['score']}]")
            else:
                tweet, info = enrich_x_from_search(article)
                if tweet:
                    print(f"     X (search): @{info['handle']} → {tweet['url'][:60]} [score:{info['score']}]")

            if tweet:
                if verify_tweet(tweet["id"]):
                    x_score = info.get("score", 5)
                    pending_embeds.append((x_score, "x", tweet["url"], f"X(@{info.get('handle','?')})"))
                    report["x_embeds"] += 1
                else:
                    print(f"     ⚠ Tweet verify failed")
        else:
            print(f"     X: already has embed")

        # ── IG enrichment ──
        if not has_embed(body, "instagram"):
            shortcode, info = enrich_ig_from_cache(article, cache, registry, live_ig=live_ig)
            if shortcode:
                ig_url = f"https://www.instagram.com/p/{shortcode}/"
                source = "live" if live_ig else "cache"
                ig_score = info.get("score", 5)
                print(f"     IG ({source}): @{info['handle']} → {ig_url} [score:{ig_score}]")
                pending_embeds.append((ig_score, "instagram", ig_url, f"IG(@{info['handle']})"))
                report["ig_embeds"] += 1
        else:
            print(f"     IG: already has embed")

        # Sort by relevance score descending — best match gets highest placement
        pending_embeds.sort(key=lambda x: x[0], reverse=True)
        for _score, platform, embed_url, change_label in pending_embeds:
            new_body = insert_embed_in_body(new_body, embed_url, platform)
            changes.append(change_label)

        # ── Hero image upgrade ──
        hero_upgrade = None
        image_url = article.get("image_url", "") or ""
        if _is_stock_hero(image_url):
            # Gather tweet candidates for hero photo (reuse topic search)
            topic_q = build_topic_query(headline)
            if topic_q:
                hero_tweets = live_search_x(topic_q, max_results=10, hours=72)
                if hero_tweets:
                    hero_upgrade = try_hero_upgrade(article, hero_tweets)
                    if hero_upgrade:
                        changes.append(f"Hero({hero_upgrade['source_handle']})")
                        report["hero_upgrades"] += 1
                        print(f"     🖼 Hero upgrade: {hero_upgrade['source_handle']} → {hero_upgrade['new_hero'][:60]}")
                    else:
                        print(f"     🖼 Hero: stock, but no valid photo tweet found")
            else:
                print(f"     🖼 Hero: stock, but no topic query")

        # ── Apply changes ──
        now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        if changes:
            change_desc = " + ".join(changes)
            if args.apply:
                updates = {"body": new_body, "social_embeds": new_embeds, "enriched_at": now_utc}
                if hero_upgrade:
                    updates["image_url"] = hero_upgrade["new_hero"]
                    updates["image_caption"] = hero_upgrade["caption"]
                if sb_patch(article["id"], updates):
                    print(f"     ✅ Applied: {change_desc}")
                else:
                    print(f"     ❌ Patch failed")
            else:
                print(f"     [DRY RUN] Would apply: {change_desc}")
            report["processed"] += 1
        else:
            # No embeds found, but still mark as enriched so we don't re-search
            if args.apply:
                sb_patch(article["id"], {"enriched_at": now_utc})
            report["skipped"] += 1

    elapsed = time.time() - start
    print(f"\n═══ Done in {elapsed:.1f}s ═══")
    print(f"Processed: {report['processed']}, Skipped: {report['skipped']}, Hero upgrades: {report['hero_upgrades']}")
    print(f"Embeds: {report['x_embeds']} X + {report['ig_embeds']} IG + {report['yt_embeds']} YT = {report['x_embeds']+report['ig_embeds']+report['yt_embeds']} total")
    print(f"YouTube API units used: {_YT_QUOTA_USED}")


if __name__ == "__main__":
    main()
