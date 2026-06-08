#!/usr/bin/env python3
"""
Power Pulse Refresh — fetch latest tweets for all 52 leaders via X API v2.
Outputs tech-buzz.json for The Videshi Pulse sections.
"""

import os
import sys
import json
import time
from datetime import datetime, timezone, timedelta
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ─── Config ───────────────────────────────────────────────────────────────────

LEADERS = {
    "india": [
        {"name": "Narendra Modi", "handle": "narendramodi"},
        {"name": "PMO India", "handle": "pmoindia"},
        {"name": "Amit Shah", "handle": "amitshah"},
        {"name": "Rahul Gandhi", "handle": "rahulgandhi"},
        {"name": "Yogi Adityanath", "handle": "myogiadityanath"},
        {"name": "Arvind Kejriwal", "handle": "arvindkejriwal"},
        {"name": "S Jaishankar", "handle": "drsjaishankar"},
        {"name": "Nirmala Sitharaman", "handle": "nsitharaman"},
        {"name": "Gautam Adani", "handle": "gautam_adani"},
        {"name": "Mukesh Ambani", "handle": "reliancejio"},
        {"name": "Ratan Tata", "handle": "ratantata"},
        {"name": "President of India", "handle": "rashtrapatibhvn"},
    ],
    "world": [
        {"name": "Donald Trump", "handle": "realdonaldtrump"},
        {"name": "Rishi Sunak", "handle": "rishisunak"},
        {"name": "Vivek Ramaswamy", "handle": "vivekgramaswamy"},
        {"name": "Usha Vance", "handle": "ushavance"},
        {"name": "Kash Patel", "handle": "kashpatel"},
        {"name": "Sriram Krishnan", "handle": "sriramk"},
        {"name": "Ajay Banga", "handle": "ajay_banga"},
        {"name": "Keir Starmer", "handle": "keir_starmer"},
        {"name": "Anthony Albanese", "handle": "albomp"},
        {"name": "Emmanuel Macron", "handle": "emmanuelmacron"},
        {"name": "Mohammed bin Rashid", "handle": "hhshkmohd"},
    ],
    "tech": [
        {"name": "Elon Musk", "handle": "elonmusk"},
        {"name": "Mark Zuckerberg", "handle": "zuck"},
        {"name": "Sundar Pichai", "handle": "sundarpichai"},
        {"name": "Satya Nadella", "handle": "satyanadella"},
        {"name": "Sam Altman", "handle": "sama"},
        {"name": "Tim Cook", "handle": "tim_cook"},
        {"name": "Jensen Huang", "handle": "jensenhuang"},
        {"name": "Nandan Nilekani", "handle": "nandannilekani"},
        {"name": "Bill Gates", "handle": "billgates"},
        {"name": "Arvind Krishna", "handle": "arvindkrishna"},
        {"name": "Shantanu Narayen", "handle": "adobe"},
        {"name": "Parag Agrawal", "handle": "paraga"},
        {"name": "Leena Nair", "handle": "leenanair"},
        {"name": "Raj Subramaniam", "handle": "fedex"},
    ],
    "sports": [
        {"name": "Virat Kohli", "handle": "imvkohli"},
        {"name": "Rohit Sharma", "handle": "imro45"},
        {"name": "MS Dhoni", "handle": "msdhoni"},
        {"name": "Jasprit Bumrah", "handle": "jaspritbumrah93"},
        {"name": "Hardik Pandya", "handle": "hardikpandya7"},
        {"name": "Sachin Tendulkar", "handle": "sachin_rt"},
        {"name": "Sourav Ganguly", "handle": "sganguly99"},
        {"name": "BCCI", "handle": "bcci"},
        {"name": "ICC", "handle": "icc"},
        {"name": "IPL", "handle": "ipl"},
        {"name": "Neeraj Chopra", "handle": "neeraj_chopra1"},
        {"name": "PV Sindhu", "handle": "pvsindhu1"},
        {"name": "Sania Mirza", "handle": "mirzasania"},
        {"name": "D Gukesh", "handle": "dgukesh"},
        {"name": "Sunil Chhetri", "handle": "chetrisunil11"},
    ],
}

OUTPUT_PATH = os.path.expanduser("~/workspace/the-videshi-news/public/data/tech-buzz.json")
USER_ID_CACHE_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/.x-user-ids.json")
ENV_PATH = os.path.expanduser("~/workspace/.env.twitter")

# ─── HTTP Session ─────────────────────────────────────────────────────────────

session = requests.Session()
retry = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
session.mount("https://", HTTPAdapter(max_retries=retry))

# ─── Auth ─────────────────────────────────────────────────────────────────────

def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip())

load_env(ENV_PATH)

_bearer_cache = None

def get_bearer_token():
    global _bearer_cache
    if _bearer_cache:
        return _bearer_cache
    key = os.environ.get("TWITTER_CONSUMER_KEY", "")
    secret = os.environ.get("TWITTER_CONSUMER_SECRET", "")
    if not key or not secret:
        raise RuntimeError("Missing TWITTER_CONSUMER_KEY / TWITTER_CONSUMER_SECRET")
    resp = session.post("https://api.twitter.com/oauth2/token",
                        auth=(key, secret),
                        data={"grant_type": "client_credentials"})
    resp.raise_for_status()
    _bearer_cache = resp.json()["access_token"]
    return _bearer_cache

# ─── User ID Cache ────────────────────────────────────────────────────────────

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
    
    bearer = get_bearer_token()
    resp = session.get(
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
    else:
        print(f"  ⚠ Could not resolve user ID for @{handle}: {resp.status_code}", file=sys.stderr)
    return None

# ─── Fetch Tweets ─────────────────────────────────────────────────────────────

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
    
    resp = session.get(
        f"https://api.twitter.com/2/users/{uid}/tweets",
        headers={"Authorization": f"Bearer {bearer}"},
        params=params,
        timeout=15,
    )
    
    if resp.status_code == 429:
        reset = resp.headers.get("x-rate-limit-reset")
        wait_secs = 16
        if reset:
            wait_secs = max(int(reset) - int(time.time()), 1) + 2
            wait_secs = min(wait_secs, 120)  # cap at 2 minutes
        print(f"  ⏳ Rate limited for @{handle}, waiting {wait_secs}s...", file=sys.stderr)
        time.sleep(wait_secs)
        # Retry once
        resp = session.get(
            f"https://api.twitter.com/2/users/{uid}/tweets",
            headers={"Authorization": f"Bearer {bearer}"},
            params=params,
            timeout=15,
        )
    
    if resp.status_code != 200:
        print(f"  ⚠ X API error for @{handle}: {resp.status_code} {resp.text[:200]}", file=sys.stderr)
        return None
    
    data = resp.json()
    tweets = data.get("data", [])
    
    if not tweets:
        return None
    
    # Return the most recent tweet
    t = tweets[0]
    return {
        "id": t["id"],
        "text": t.get("text", ""),
        "created_at": t.get("created_at", ""),
    }

# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    print(f"🔄 Power Pulse Refresh — {datetime.now(timezone.utc).isoformat()}")
    
    # Warm up bearer token
    get_bearer_token()
    print("✅ Bearer token acquired")
    
    all_leaders = []
    total = sum(len(v) for v in LEADERS.values())
    processed = 0
    api_failures = []
    
    for category, leaders in LEADERS.items():
        print(f"\n📂 Category: {category} ({len(leaders)} leaders)")
        
        for leader in leaders:
            processed += 1
            name = leader["name"]
            handle = leader["handle"]
            print(f"  [{processed}/{total}] @{handle} ({name})...", end=" ", flush=True)
            
            tweet = fetch_latest_tweet(handle)
            
            if tweet:
                tweet_text = tweet["text"]
                tweet_url = f"https://x.com/{handle}/status/{tweet['id']}"
                tweet_date = tweet["created_at"][:10] if tweet.get("created_at") else datetime.now(timezone.utc).strftime("%Y-%m-%d")
                print(f"✅ ({len(tweet_text)} chars)")
            else:
                # Fallback — use profile URL, mark for web search
                tweet_text = ""
                tweet_url = f"https://x.com/{handle}"
                tweet_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
                api_failures.append({"name": name, "handle": handle, "category": category})
                print("❌ no tweet found")
            
            all_leaders.append({
                "name": name,
                "handle": handle,
                "category": category,
                "platform": "x",
                "posts": [
                    {
                        "text": tweet_text,
                        "caption": tweet_text,
                        "url": tweet_url,
                        "thumbnail": "",
                        "timestamp": tweet_date,
                    }
                ]
            })
            
            # Small delay to avoid rate limits (15 req/15min for user timeline on free tier)
            time.sleep(1.1)
    
    # Write output
    now_iso = datetime.now(timezone.utc).isoformat()
    output = {
        "leaders": all_leaders,
        "lastUpdated": now_iso,
        "last_updated": now_iso,
    }
    
    with open(OUTPUT_PATH, "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Wrote {len(all_leaders)} leaders to {OUTPUT_PATH}")
    
    if api_failures:
        print(f"\n⚠ {len(api_failures)} leaders had no tweets (need web search fallback):")
        for f_item in api_failures:
            print(f"  - {f_item['name']} (@{f_item['handle']}) [{f_item['category']}]")
    
    # Output failures as JSON for downstream processing
    with open("/tmp/pulse-failures.json", "w") as f:
        json.dump(api_failures, f)
    
    return api_failures

if __name__ == "__main__":
    failures = main()
    sys.exit(0)
