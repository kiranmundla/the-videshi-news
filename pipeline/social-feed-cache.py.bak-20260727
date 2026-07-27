#!/usr/bin/env python3
"""
social-feed-cache.py — Build a cached social feed JSON for the homepage.

Two-layer cache:
  1. POOL (social-feed-pool.json): All fetched tweets per handle, refreshed
     from X API only when stale (>12h). One API call per handle returns 5 tweets.
  2. DISPLAY (social-feed.json): 1 tweet per handle, rotated each cron run
     so the homepage shows variety over time without extra API cost.

Person handles only — company/org handles excluded.
"""

import os, sys, json, re, hashlib, requests
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
DB_HEADERS = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}

# ─── Config ───────────────────────────────────────────────────────────────────

STRIP_CATEGORIES = ["technology", "sports", "news", "immigration", "world-leaders", "spirituality"]
TWEETS_PER_CATEGORY = 999     # no cap — show every handle we have
POOL_TWEETS_PER_HANDLE = 5    # tweets to cache per handle
POOL_MAX_AGE_HOURS = 12       # re-fetch from TwitterAPI.io when pool is older (was 120h/5d with X API)
VVIP_TWEET_HOURS = 336        # look back 14 days for tweets
LOOKBACK_DAYS = 14            # article harvest lookback

PIPELINE_DIR = os.path.expanduser("~/workspace/the-videshi-news/pipeline")
POOL_PATH = os.path.join(PIPELINE_DIR, "social-feed-pool.json")
OUTPUT_PATH = os.path.expanduser("~/workspace/the-videshi-news/public/data/social-feed.json")

# VVIP person handles per category — comprehensive diaspora-relevant list
# Pool refreshes every 12h. Each handle costs ~$0.034/mo via TwitterAPI.io
# ~51 handles → ~$1.73/mo
VVIP_HANDLES = {
    "technology": [
        "sundarpichai", "satyanadella", "sama", "elonmusk", "tim_cook",
        "NandanNilekani", "NikeshArora", "ArvindKrishna",
    ],
    "spirituality": [
        "SadhguruJV", "DeepakChopra", "BKShivani", "SriMSpeaks",
        "Amritanandamayi", "EckhartTolle", "ByronKatie", "RupertSpira",
        "DandapaniLLC", "JayShetty", "Osho", "brahmakumaris",
    ],
    "sports": [
        # Cricket
        "imVkohli", "ImRo45", "sachin_rt",
        "SGanguly99", "harbhajan_singh", "RishabhPant17", "ShubmanGill",
        "MohammadKaif", "ajinkyarahane88", "IrfanPathan",
        # Olympic / other sports
        "Neeraj_chopra1", "Pvsindhu1",
        "realmanubhaker", "nikhat_zareen",
    ],
    "news": [
        # Indian leaders
        "narendramodi", "DrSJaishankar", "AmitShah", "nsitharaman",
        "RahulGandhi", "myogiadityanath", "MamataOfficial", "ArvindKejriwal",
        "PMOIndia", "rashtrapatibhvn", "PiyushGoyal", "RajnathSingh",
        "ShashiTharoor", "JPNadda", "NitishKumar",
    ],
    "world-leaders": [
        # US
        "realDonaldTrump", "VP", "WhiteHouse",
        # UK
        "10DowningStreet", "RishiSunak",
        # Canada
        "JustinTrudeau",
        # Europe & other
        "ZelenskyyUa", "EmmanuelMacron",
        "BarackObama", "MichelleObama", "SecRubio",
    ],
    "immigration": [],
}

COMPANY_HANDLES = {
    "nvidia", "openai", "google", "microsoft", "meta", "apple", "amazon", "ibm",
    "googledeepmind", "anthropic", "tesla", "spacex", "infosys", "tcs", "wipro",
    "tatamotors", "reliancejio", "netflix", "netflixindia", "netflix_insouth",
    "icc", "bcci", "fifaworldcup", "formula1", "nba", "nfl",
    "sportstarweb", "bwfscore", "airnewsalerts", "moneycontrolcom",
    "indianembassyus", "robot2trade1", "1lsbongofficial",
}

# ─── Pool management ─────────────────────────────────────────────────────────

sys.path.insert(0, PIPELINE_DIR)

def load_pool():
    if os.path.exists(POOL_PATH):
        with open(POOL_PATH) as f:
            return json.load(f)
    return {"_refreshed_at": None, "_rotation_index": 0, "handles": {}}

def save_pool(pool):
    with open(POOL_PATH, "w") as f:
        json.dump(pool, f, indent=2)

def pool_is_fresh(pool):
    ts = pool.get("_refreshed_at")
    if not ts:
        return False
    refreshed = datetime.fromisoformat(ts)
    return (datetime.now(timezone.utc) - refreshed).total_seconds() < POOL_MAX_AGE_HOURS * 3600

def refresh_pool(pool):
    """Fetch tweets from TwitterAPI.io for all VVIP handles, update pool."""
    try:
        from fetch_tweets import fetch_recent_tweets_twitterapiio
    except ImportError:
        import importlib.util
        spec = importlib.util.spec_from_file_location("fetch_tweets",
            os.path.join(PIPELINE_DIR, "fetch-tweets.py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        fetch_recent_tweets_twitterapiio = mod.fetch_recent_tweets_twitterapiio

    handles_data = pool.get("handles", {})

    for cat, handles in VVIP_HANDLES.items():
        for handle in handles:
            key = f"{cat}:{handle.lower()}"
            try:
                tweets = fetch_recent_tweets_twitterapiio(handle, max_results=POOL_TWEETS_PER_HANDLE)
                good = []
                for t in tweets:
                    text = t.get("text", "")
                    if text.startswith("@") or text.startswith("RT @") or len(text) < 20:
                        continue
                    good.append({
                        "tweet_url": t["url"],
                        "handle": handle,
                        "tweet_id": t["id"],
                        "category": cat,
                        "text": text[:300],
                        "published_at": t.get("created_at", ""),
                        "photos": t.get("photos", []),
                    })
                if good:
                    handles_data[key] = good
                    print(f"    {handle} ({cat}): {len(good)} tweets cached")
            except Exception as e:
                print(f"    ⚠ {handle}: {e}", file=sys.stderr)

    pool["handles"] = handles_data
    pool["_refreshed_at"] = datetime.now(timezone.utc).isoformat()
    return pool


# ─── Article-harvested tweets (zero cost fallback) ────────────────────────────

def harvest_article_tweets():
    """Get person tweets embedded in articles (for categories with no VVIP handles)."""
    cutoff = (datetime.now(timezone.utc) - timedelta(days=LOOKBACK_DAYS)).isoformat()
    resp = requests.get(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=DB_HEADERS,
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
        return {}

    tweet_pattern = re.compile(r'https://(?:x\.com|twitter\.com)/(\w+)/status/(\d+)')
    by_category = {}
    seen = set()

    for article in resp.json():
        body = article.get("body", "") or ""
        cat = article.get("category", "")
        if cat not in STRIP_CATEGORIES:
            continue

        for handle, tweet_id in tweet_pattern.findall(body):
            h_lower = handle.lower()
            if tweet_id in seen or h_lower in COMPANY_HANDLES or h_lower in ("thevideshi", "the_videshi"):
                continue
            seen.add(tweet_id)
            by_category.setdefault(cat, []).append({
                "tweet_url": f"https://x.com/{handle}/status/{tweet_id}",
                "handle": handle,
                "tweet_id": tweet_id,
                "category": cat,
                "text": article.get("headline", ""),
                "published_at": article.get("published_at", ""),
            })

    return by_category


# ─── Display selection: 1 tweet per handle, rotated ──────────────────────────

def build_display(pool, article_tweets):
    """Pick 1 tweet per handle, rotating which one is shown each run."""
    rotation = pool.get("_rotation_index", 0)
    final = {}

    for cat in STRIP_CATEGORIES:
        display = []
        seen_handles = set()

        # VVIP handles first
        for handle in VVIP_HANDLES.get(cat, []):
            if len(display) >= TWEETS_PER_CATEGORY:
                break
            key = f"{cat}:{handle.lower()}"
            tweets = pool.get("handles", {}).get(key, [])
            if not tweets:
                continue

            # Rotate: pick a different tweet each run, prefer tweets with photos
            idx = rotation % len(tweets)
            pick = tweets[idx]
            # If this pick has no photo, check if any tweet for this handle does
            if not pick.get("photos"):
                photo_tweets = [t for t in tweets if t.get("photos")]
                if photo_tweets:
                    pick = photo_tweets[rotation % len(photo_tweets)]
            display.append({
                "tweet_url": pick["tweet_url"],
                "handle": pick["handle"],
                "tweet_id": pick["tweet_id"],
                "category": cat,
                "article_slug": "",
                "article_headline": pick.get("text", ""),
                "published_at": pick.get("published_at", ""),
                "photos": pick.get("photos", []),
            })
            seen_handles.add(handle.lower())

        # Fill remaining slots from article-harvested (1 per handle, no dupes)
        for t in article_tweets.get(cat, []):
            if len(display) >= TWEETS_PER_CATEGORY:
                break
            if t["handle"].lower() in seen_handles:
                continue
            seen_handles.add(t["handle"].lower())
            display.append(t)

        final[cat] = display

    return final


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("📡 Building social feed cache...")

    pool = load_pool()

    # Refresh pool from X API only if stale
    if pool_is_fresh(pool):
        print(f"  Pool is fresh (last refreshed: {pool['_refreshed_at']}), skipping API calls")
    else:
        print("  Pool stale or missing — fetching from X API...")
        pool = refresh_pool(pool)

    # Bump rotation index
    pool["_rotation_index"] = pool.get("_rotation_index", 0) + 1
    save_pool(pool)

    # Article-harvested fallback
    print("  Harvesting from article embeds (zero cost)...")
    article_tweets = harvest_article_tweets()

    # Build display: 1 tweet per handle, rotated
    display = build_display(pool, article_tweets)

    total = sum(len(v) for v in display.values())
    print(f"\n  Display: {total} tweets across {sum(1 for v in display.values() if v)} categories (1 per handle):")
    for cat, tweets in sorted(display.items()):
        if tweets:
            handles = [t["handle"] for t in tweets]
            print(f"    {cat}: {handles}")

    output = {
        "_generated": datetime.now(timezone.utc).isoformat(),
        "_description": "1 tweet per person, rotated each cron run. Pool refreshed every 12h.",
        "_rotation": pool["_rotation_index"],
        "categories": display,
    }

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\n  ✅ Written to {OUTPUT_PATH}")
    pool_handles = len(pool.get("handles", {}))
    pool_tweets = sum(len(v) for v in pool.get("handles", {}).values())
    print(f"  📦 Pool: {pool_tweets} tweets across {pool_handles} handles (rotates each run)")


if __name__ == "__main__":
    main()
