#!/usr/bin/env python3
"""
power-pulse-refresh.py — Fetch latest tweets for all Pulse leaders via X API v2
and write tech-buzz.json for The Videshi frontend.
"""

import os, sys, json, time
from datetime import datetime, timezone, timedelta
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ─── Config ───────────────────────────────────────────────────────────────────

OUTPUT_PATH = os.path.expanduser("~/workspace/the-videshi-news/public/data/tech-buzz.json")
USER_ID_CACHE = os.path.expanduser("~/workspace/the-videshi-news/pipeline/.x-user-ids.json")

# X handle → display name, category
# Using correct X handles (NOT Instagram handles)
LEADERS = [
    # India Pulse (12)
    {"name": "Narendra Modi", "handle": "narendramodi", "category": "india"},
    {"name": "PMO India", "handle": "pmoindia", "category": "india"},
    {"name": "Amit Shah", "handle": "amitshah", "category": "india"},
    {"name": "Rahul Gandhi", "handle": "rahulgandhi", "category": "india"},
    {"name": "Yogi Adityanath", "handle": "myogiadityanath", "category": "india"},
    {"name": "Arvind Kejriwal", "handle": "arvindkejriwal", "category": "india"},
    {"name": "S Jaishankar", "handle": "drsjaishankar", "category": "india"},
    {"name": "Nirmala Sitharaman", "handle": "nsitharaman", "category": "india"},
    {"name": "Gautam Adani", "handle": "gautam_adani", "category": "india"},
    {"name": "Mukesh Ambani", "handle": "reliancejio", "category": "india"},
    {"name": "Ratan Tata", "handle": "ratantata", "category": "india"},
    {"name": "President of India", "handle": "rashtrapatibhvn", "category": "india"},
    # World / Power Pulse (11)
    {"name": "Donald Trump", "handle": "realdonaldtrump", "category": "world"},
    {"name": "Rishi Sunak", "handle": "rishisunak", "category": "world"},
    {"name": "Vivek Ramaswamy", "handle": "vivekgramaswamy", "category": "world"},
    {"name": "Usha Vance", "handle": "ushavance", "category": "world"},
    {"name": "Kash Patel", "handle": "kashpatel", "category": "world"},
    {"name": "Sriram Krishnan", "handle": "sriramk", "category": "world"},
    {"name": "Ajay Banga", "handle": "ajay_banga", "category": "world"},
    {"name": "Keir Starmer", "handle": "keir_starmer", "category": "world"},
    {"name": "Anthony Albanese", "handle": "albomp", "category": "world"},
    {"name": "Emmanuel Macron", "handle": "emmanuelmacron", "category": "world"},
    {"name": "Mohammed bin Rashid", "handle": "hhshkmohd", "category": "world"},
    # Tech Pulse (14)
    {"name": "Elon Musk", "handle": "elonmusk", "category": "tech"},
    {"name": "Mark Zuckerberg", "handle": "zuck", "category": "tech"},
    {"name": "Sundar Pichai", "handle": "sundarpichai", "category": "tech"},
    {"name": "Satya Nadella", "handle": "satyanadella", "category": "tech"},
    {"name": "Sam Altman", "handle": "sama", "category": "tech"},
    {"name": "Tim Cook", "handle": "tim_cook", "category": "tech"},
    {"name": "Jensen Huang", "handle": "jensenhuang", "category": "tech"},
    {"name": "Nandan Nilekani", "handle": "nandannilekani", "category": "tech"},
    {"name": "Bill Gates", "handle": "billgates", "category": "tech"},
    {"name": "Arvind Krishna", "handle": "arvindkrishna", "category": "tech"},
    {"name": "Shantanu Narayen", "handle": "adobe", "category": "tech"},
    {"name": "Parag Agrawal", "handle": "paraga", "category": "tech"},
    {"name": "Leena Nair", "handle": "leenanair", "category": "tech"},
    {"name": "Raj Subramaniam", "handle": "rajsubramaniam", "category": "tech"},
    # Sports Pulse (15)
    {"name": "Virat Kohli", "handle": "imvkohli", "category": "sports"},
    {"name": "Rohit Sharma", "handle": "imro45", "category": "sports"},
    {"name": "MS Dhoni", "handle": "msdhoni", "category": "sports"},
    {"name": "Jasprit Bumrah", "handle": "jaspritbumrah93", "category": "sports"},
    {"name": "Hardik Pandya", "handle": "hardikpandya7", "category": "sports"},
    {"name": "Sachin Tendulkar", "handle": "sachin_rt", "category": "sports"},
    {"name": "Sourav Ganguly", "handle": "sganguly99", "category": "sports"},
    {"name": "BCCI", "handle": "bcci", "category": "sports"},
    {"name": "ICC", "handle": "icc", "category": "sports"},
    {"name": "IPL", "handle": "ipl", "category": "sports"},
    {"name": "Neeraj Chopra", "handle": "neeraj_chopra1", "category": "sports"},
    {"name": "PV Sindhu", "handle": "pvsindhu1", "category": "sports"},
    {"name": "Sania Mirza", "handle": "mirzasania", "category": "sports"},
    {"name": "D Gukesh", "handle": "dgukesh", "category": "sports"},
    {"name": "Sunil Chhetri", "handle": "chetrisunil11", "category": "sports"},
]

# ─── HTTP session ─────────────────────────────────────────────────────────────

_session = requests.Session()
_retry = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
_session.mount("https://", HTTPAdapter(max_retries=_retry))

# ─── Auth ─────────────────────────────────────────────────────────────────────

def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip())

load_env(os.path.expanduser("~/workspace/.env.twitter"))

_bearer_cache = None

def get_bearer_token():
    global _bearer_cache
    if _bearer_cache:
        return _bearer_cache
    key = os.environ.get("TWITTER_CONSUMER_KEY", "")
    secret = os.environ.get("TWITTER_CONSUMER_SECRET", "")
    if not key or not secret:
        raise RuntimeError("Missing TWITTER_CONSUMER_KEY / TWITTER_CONSUMER_SECRET")
    resp = _session.post("https://api.twitter.com/oauth2/token",
                         auth=(key, secret),
                         data={"grant_type": "client_credentials"})
    resp.raise_for_status()
    _bearer_cache = resp.json()["access_token"]
    return _bearer_cache

# ─── User ID ──────────────────────────────────────────────────────────────────

def load_user_id_cache():
    if os.path.exists(USER_ID_CACHE):
        with open(USER_ID_CACHE) as f:
            return json.load(f)
    return {}

def save_user_id_cache(cache):
    with open(USER_ID_CACHE, "w") as f:
        json.dump(cache, f, indent=2)

def get_user_id(handle):
    cache = load_user_id_cache()
    handle_lower = handle.lower()
    if handle_lower in cache:
        return cache[handle_lower]
    bearer = get_bearer_token()
    resp = _session.get(
        f"https://api.twitter.com/2/users/by/username/{handle}",
        headers={"Authorization": f"Bearer {bearer}"},
        timeout=10,
    )
    if resp.status_code == 200:
        uid = resp.json().get("data", {}).get("id")
        if uid:
            cache[handle_lower] = uid
            save_user_id_cache(cache)
            return uid
    print(f"  ⚠ Could not resolve user ID for @{handle}: {resp.status_code}", file=sys.stderr)
    return None

# ─── Fetch tweets ─────────────────────────────────────────────────────────────

def fetch_latest_tweet(handle, hours=72):
    """Fetch the most recent original tweet from a handle."""
    uid = get_user_id(handle)
    if not uid:
        return None

    bearer = get_bearer_token()
    start_time = (datetime.now(timezone.utc) - timedelta(hours=hours)).strftime("%Y-%m-%dT%H:%M:%SZ")

    params = {
        "max_results": 5,
        "start_time": start_time,
        "tweet.fields": "created_at,text,public_metrics",
        "exclude": "retweets,replies",
    }

    resp = _session.get(
        f"https://api.twitter.com/2/users/{uid}/tweets",
        headers={"Authorization": f"Bearer {bearer}"},
        params=params,
        timeout=15,
    )

    if resp.status_code == 429:
        # Rate limited - wait and retry once
        reset = resp.headers.get("x-rate-limit-reset")
        if reset:
            wait_time = max(int(reset) - int(time.time()), 1)
            wait_time = min(wait_time, 60)  # cap at 60s
            print(f"  ⏳ Rate limited, waiting {wait_time}s...", file=sys.stderr)
            time.sleep(wait_time)
            resp = _session.get(
                f"https://api.twitter.com/2/users/{uid}/tweets",
                headers={"Authorization": f"Bearer {bearer}"},
                params=params,
                timeout=15,
            )

    if resp.status_code != 200:
        print(f"  ⚠ API error for @{handle}: {resp.status_code} {resp.text[:100]}", file=sys.stderr)
        return None

    data = resp.json()
    tweets = data.get("data", [])
    if not tweets:
        return None

    # Return the most recent tweet
    t = tweets[0]
    tweet_text = t.get("text", "").strip()
    # Clean up t.co links at the end
    import re
    tweet_text = re.sub(r'\s*https://t\.co/\S+$', '', tweet_text).strip()

    return {
        "id": t["id"],
        "text": tweet_text,
        "created_at": t.get("created_at", ""),
    }

# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    print(f"🔄 Power Pulse refresh starting — {len(LEADERS)} leaders")
    
    # Warm up bearer token
    get_bearer_token()
    print("✅ Bearer token acquired")

    results = []
    success_count = 0
    fail_count = 0
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    for i, leader in enumerate(LEADERS):
        name = leader["name"]
        handle = leader["handle"]
        category = leader["category"]
        
        print(f"[{i+1}/{len(LEADERS)}] {name} (@{handle})...", end=" ", flush=True)
        
        tweet = fetch_latest_tweet(handle)
        
        if tweet:
            tweet_url = f"https://x.com/{handle}/status/{tweet['id']}"
            tweet_date = tweet["created_at"][:10] if tweet["created_at"] else today
            text = tweet["text"]
            print(f"✅ ({len(text)} chars)")
            success_count += 1
        else:
            # Fallback: use profile URL with a generic note
            tweet_url = f"https://x.com/{handle}"
            text = f"Follow @{handle} for the latest updates."
            tweet_date = today
            print("⚠ No recent tweet, using fallback")
            fail_count += 1

        results.append({
            "name": name,
            "handle": handle,
            "category": category,
            "platform": "x",
            "posts": [
                {
                    "text": text,
                    "caption": text,
                    "url": tweet_url,
                    "thumbnail": "",
                    "timestamp": tweet_date,
                }
            ]
        })

        # Small delay to avoid rate limits (10,000 calls/15 min = ~11/s, but be nice)
        if (i + 1) % 15 == 0:
            time.sleep(2)

    # Write output
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    output = {
        "leaders": results,
        "lastUpdated": now_iso,
        "last_updated": now_iso,
    }

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Written {len(results)} leaders to tech-buzz.json")
    print(f"   Success: {success_count}, Fallback: {fail_count}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
