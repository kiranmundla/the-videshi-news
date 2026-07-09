#!/usr/bin/env python3
"""
social-feed-cache.py — Build a cached social feed JSON for the homepage.

Extracts tweet URLs already embedded in published articles (zero X API cost),
groups by category, and writes public/data/social-feed.json for the homepage
tweet scroll strips.

Each entry: { tweet_url, handle, category, article_slug, article_headline, published_at }

Rotation: keeps the most recent 8 tweets per category. Cron runs every 6h
so tweets rotate naturally as new articles publish with embeds.
"""

import os, sys, json, re, requests
from datetime import datetime, timezone, timedelta

def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip())

load_env(os.path.expanduser("~/workspace/.env.supabase"))

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}

# Categories that get tweet strips on the homepage
STRIP_CATEGORIES = ["technology", "entertainment", "sports", "news", "immigration", "nri-world", "markets-finance"]
TWEETS_PER_CATEGORY = 8
LOOKBACK_DAYS = 14  # search last 2 weeks of articles

OUTPUT_PATH = os.path.expanduser("~/workspace/the-videshi-news/public/data/social-feed.json")


def fetch_articles_with_embeds():
    """Fetch recent published articles that contain X embed URLs."""
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


def extract_tweets(articles):
    """Extract tweet URLs from article bodies, grouped by category."""
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
            
            # Skip self-citations
            if handle.lower() in ("thevideshi", "the_videshi"):
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
    
    # Keep only the most recent N per category
    result = {}
    for cat, tweets in by_category.items():
        # Already sorted by article publish date (desc) from query
        result[cat] = tweets[:TWEETS_PER_CATEGORY]
    
    return result


def main():
    print("📡 Building social feed cache...")
    articles = fetch_articles_with_embeds()
    print(f"  Found {len(articles)} articles with X embeds in last {LOOKBACK_DAYS} days")
    
    feed = extract_tweets(articles)
    
    total = sum(len(v) for v in feed.values())
    print(f"  Extracted {total} unique tweets across {sum(1 for v in feed.values() if v)} categories:")
    for cat, tweets in sorted(feed.items()):
        if tweets:
            print(f"    {cat}: {len(tweets)} tweets")
    
    # Write output
    output = {
        "_generated": datetime.now(timezone.utc).isoformat(),
        "_description": "Cached tweet embeds for homepage social strips. Harvested from article embeds, zero API cost.",
        "categories": feed,
    }
    
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"  ✅ Written to {OUTPUT_PATH}")
    print(f"  💰 X API cost: $0.00 (harvested from existing embeds)")


if __name__ == "__main__":
    main()
