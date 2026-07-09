#!/usr/bin/env python3
"""
social-feed-cache.py — Build a cached social feed JSON for the homepage.

Two-tier approach:
  1. DIRECT FETCH: Pulls recent tweets from VVIP/celebrity person handles
     per category via X API (small cost per run).
  2. ARTICLE HARVEST: Falls back to tweet URLs embedded in published articles
     (zero cost).

Person handles always shown first. Company/org handles excluded.
Writes public/data/social-feed.json for the homepage tweet scroll strips.
"""

import os, sys, json, re, requests
from datetime import datetime, timezone, timedelta

# ─── Load envs ────────────────────────────────────────────────────────────────

def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip())

load_env(os.path.expanduser("~/workspace/.env.supabase"))
load_env(os.path.expanduser("~/workspace/.env.twitter"))

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}

# ─── Config ───────────────────────────────────────────────────────────────────

STRIP_CATEGORIES = ["technology", "entertainment", "sports", "news", "immigration"]
TWEETS_PER_CATEGORY = 8
LOOKBACK_DAYS = 14
VVIP_TWEET_HOURS = 168  # look back 7 days for VVIP tweets
OUTPUT_PATH = os.path.expanduser("~/workspace/the-videshi-news/public/data/social-feed.json")

# VVIP person handles per category — these get direct API fetch
VVIP_HANDLES = {
    "technology": ["sundarpichai", "sataboreel", "satyanadella", "sama", "elonmusk", "tim_cook", "NandanNilekani", "jaboreel"],
    "entertainment": ["iamsrk", "priyankachopra", "deepikapadukone", "akshaykumar", "karanjohar", "diljitdosanjh", "aliaa08", "SrBachchan"],
    "sports": ["imVkohli", "ImRo45", "sachin_rt", "Jaspritbumrah93", "hardikpandya7", "Neeraj_chopra1", "SGanguly99", "Pvsindhu1"],
    "news": ["narendramodi", "DrSJaishankar", "AmitShah", "nsitharaman", "RahulGandhi"],
    "immigration": [],
}

# Company handles to exclude from article-harvested tweets
COMPANY_HANDLES = {
    "nvidia", "openai", "google", "microsoft", "meta", "apple", "amazon", "ibm",
    "googledeepmind", "anthropic", "tesla", "spacex", "infosys", "tcs", "wipro",
    "tatamotors", "reliancejio", "netflix", "netflixindia", "netflix_insouth",
    "icc", "bcci", "fifaworldcup", "formula1", "nba", "nfl",
    "sportstarweb", "bwfscore", "airnewsalerts", "moneycontrolcom",
    "indianembassyus", "robot2trade1", "1lsbongofficial",
}

# ─── Direct VVIP fetch via X API ──────────────────────────────────────────────

sys.path.insert(0, os.path.expanduser("~/workspace/the-videshi-news/pipeline"))

def fetch_vvip_tweets():
    """Fetch recent tweets from VVIP handles using the X API."""
    try:
        from fetch_tweets import fetch_recent_tweets
    except ImportError:
        # Fallback: import from fetch-tweets.py
        import importlib.util
        spec = importlib.util.spec_from_file_location("fetch_tweets",
            os.path.expanduser("~/workspace/the-videshi-news/pipeline/fetch-tweets.py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        fetch_recent_tweets = mod.fetch_recent_tweets

    results = {cat: [] for cat in STRIP_CATEGORIES}

    for cat, handles in VVIP_HANDLES.items():
        for handle in handles:
            if len(results[cat]) >= TWEETS_PER_CATEGORY:
                break
            try:
                tweets = fetch_recent_tweets(handle, hours=VVIP_TWEET_HOURS, max_results=5)
                handle_count = 0
                for t in tweets:
                    if len(results[cat]) >= TWEETS_PER_CATEGORY:
                        break
                    if handle_count >= 2:  # max 2 tweets per handle for variety
                        break
                    # Skip replies and very short tweets
                    text = t.get("text", "")
                    if text.startswith("@") or len(text) < 20:
                        continue
                    results[cat].append({
                        "tweet_url": t["url"],
                        "handle": handle,
                        "tweet_id": t["id"],
                        "category": cat,
                        "article_slug": "",
                        "article_headline": text[:200],
                        "published_at": t.get("created_at", ""),
                    })
                    handle_count += 1
            except Exception as e:
                print(f"  ⚠ {handle}: {e}", file=sys.stderr)
                continue

    return results


# ─── Article-harvested tweets (zero cost fallback) ────────────────────────────

def fetch_articles_with_embeds():
    cutoff = (datetime.now(timezone.utc) - timedelta(days=LOOKBACK_DAYS)).isoformat()
    resp = requests.get(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        params={
            "select": "id,headline,slug,category,body,published_at",
            "body": "like.*x.com/*/status/*",
            "status": "eq.published",
            "published_at": f"gte.{cutoff}",
            "order": "published_at.desc",
            "limit": 200,
        },
        timeout=30,
    )
    if resp.status_code != 200:
        print(f"❌ Supabase error {resp.status_code}: {resp.text[:200]}", file=sys.stderr)
        return []
    return resp.json()


def extract_article_tweets(articles):
    tweet_pattern = re.compile(r'https://(?:x\.com|twitter\.com)/(\w+)/status/(\d+)')
    by_category = {cat: [] for cat in STRIP_CATEGORIES}
    seen_tweet_ids = set()

    for article in articles:
        body = article.get("body", "") or ""
        cat = article.get("category", "")
        if cat not in by_category:
            continue

        matches = tweet_pattern.findall(body)
        for handle, tweet_id in matches:
            if tweet_id in seen_tweet_ids:
                continue
            seen_tweet_ids.add(tweet_id)

            if handle.lower() in ("thevideshi", "the_videshi"):
                continue
            if handle.lower() in COMPANY_HANDLES:
                continue

            by_category[cat].append({
                "tweet_url": f"https://x.com/{handle}/status/{tweet_id}",
                "handle": handle,
                "tweet_id": tweet_id,
                "category": cat,
                "article_slug": article.get("slug", ""),
                "article_headline": article.get("headline", ""),
                "published_at": article.get("published_at", ""),
            })

    return by_category


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("📡 Building social feed cache...")

    # Tier 1: Direct VVIP fetch
    print("  Fetching VVIP tweets via X API...")
    vvip_feed = fetch_vvip_tweets()
    vvip_total = sum(len(v) for v in vvip_feed.values())
    print(f"  Got {vvip_total} VVIP tweets")
    for cat, tweets in sorted(vvip_feed.items()):
        if tweets:
            handles = [t["handle"] for t in tweets]
            print(f"    {cat}: {handles}")

    # Tier 2: Article-harvested (fill remaining slots)
    print("  Harvesting from article embeds...")
    articles = fetch_articles_with_embeds()
    article_feed = extract_article_tweets(articles)

    # Merge: VVIP first, then article-harvested to fill gaps
    final = {}
    vvip_ids = set()
    for cat in STRIP_CATEGORIES:
        vvip = vvip_feed.get(cat, [])
        for t in vvip:
            vvip_ids.add(t["tweet_id"])
        article = [t for t in article_feed.get(cat, []) if t["tweet_id"] not in vvip_ids]
        merged = vvip + article
        final[cat] = merged[:TWEETS_PER_CATEGORY]

    total = sum(len(v) for v in final.values())
    print(f"  Final: {total} tweets across {sum(1 for v in final.values() if v)} categories")

    output = {
        "_generated": datetime.now(timezone.utc).isoformat(),
        "_description": "Cached social feed: VVIP person tweets + article-harvested fallback.",
        "categories": final,
    }

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(output, f, indent=2)

    print(f"  ✅ Written to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
