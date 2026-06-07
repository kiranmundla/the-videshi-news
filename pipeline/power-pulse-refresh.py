#!/usr/bin/env python3
"""
Power Pulse Refresh — fetch latest tweets for all leaders via X API v2.
"""

import os, sys, json, time
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
        {"name": "Shantanu Narayen", "handle": "shantanunarayen"},
        {"name": "Parag Agrawal", "handle": "paraga"},
        {"name": "Leena Nair", "handle": "leenanair"},
        {"name": "Raj Subramaniam", "handle": "rajsubramaniam"},
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

# ─── Setup ─────────────────────────────────────────────────────────────────────

def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip())

load_env(os.path.expanduser("~/workspace/.env.twitter"))

sess = requests.Session()
retry = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
sess.mount("https://", HTTPAdapter(max_retries=retry))

_bearer = None
def get_bearer():
    global _bearer
    if _bearer:
        return _bearer
    key = os.environ.get("TWITTER_CONSUMER_KEY", "")
    secret = os.environ.get("TWITTER_CONSUMER_SECRET", "")
    resp = sess.post("https://api.twitter.com/oauth2/token",
                     auth=(key, secret),
                     data={"grant_type": "client_credentials"})
    resp.raise_for_status()
    _bearer = resp.json()["access_token"]
    return _bearer

# ─── User ID cache ─────────────────────────────────────────────────────────────

CACHE_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/.x-user-ids.json")

def load_cache():
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH) as f:
            return json.load(f)
    return {}

def save_cache(c):
    with open(CACHE_PATH, "w") as f:
        json.dump(c, f, indent=2)

def get_user_id(handle):
    cache = load_cache()
    h = handle.lower()
    if h in cache:
        return cache[h]
    # lookup
    token = get_bearer()
    resp = sess.get(f"https://api.twitter.com/2/users/by/username/{handle}",
                    headers={"Authorization": f"Bearer {token}"})
    if resp.status_code == 200:
        data = resp.json().get("data")
        if data:
            uid = data["id"]
            cache[h] = uid
            save_cache(cache)
            return uid
    print(f"  ⚠️  Could not resolve user ID for @{handle}: {resp.status_code} {resp.text[:200]}", file=sys.stderr)
    return None

# ─── Fetch tweets ──────────────────────────────────────────────────────────────

def fetch_recent_tweets(handle, hours=72):
    uid = get_user_id(handle)
    if not uid:
        return []
    
    token = get_bearer()
    start = (datetime.now(timezone.utc) - timedelta(hours=hours)).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    params = {
        "max_results": 5,
        "start_time": start,
        "tweet.fields": "created_at,text,public_metrics",
        "exclude": "retweets,replies",
    }
    
    resp = sess.get(f"https://api.twitter.com/2/users/{uid}/tweets",
                    headers={"Authorization": f"Bearer {token}"},
                    params=params)
    
    if resp.status_code == 429:
        print(f"  ⚠️  Rate limited on @{handle}", file=sys.stderr)
        return []
    
    if resp.status_code != 200:
        print(f"  ⚠️  Error fetching @{handle}: {resp.status_code} {resp.text[:200]}", file=sys.stderr)
        return []
    
    data = resp.json()
    tweets = data.get("data", [])
    return tweets

# ─── Main ──────────────────────────────────────────────────────────────────────

def main():
    results = []
    total = sum(len(v) for v in LEADERS.values())
    done = 0
    rate_limited = False
    
    for category, leaders in LEADERS.items():
        for leader in leaders:
            done += 1
            name = leader["name"]
            handle = leader["handle"]
            print(f"[{done}/{total}] {name} (@{handle}) [{category}]...")
            
            tweets = []
            if not rate_limited:
                tweets = fetch_recent_tweets(handle)
                if not tweets:
                    # Check if we're being rate limited globally
                    pass
                time.sleep(0.3)  # gentle rate limiting
            
            tweet_text = ""
            tweet_url = f"https://x.com/{handle}"
            tweet_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            
            if tweets:
                # Pick the most engaging tweet (highest engagement)
                best = max(tweets, key=lambda t: (
                    t.get("public_metrics", {}).get("like_count", 0) +
                    t.get("public_metrics", {}).get("retweet_count", 0) * 2
                ))
                tweet_text = best.get("text", "").strip()
                tweet_id = best.get("id", "")
                if tweet_id:
                    tweet_url = f"https://x.com/{handle}/status/{tweet_id}"
                created = best.get("created_at", "")
                if created:
                    tweet_date = created[:10]
                
                # Clean up tweet text - remove t.co URLs at end
                import re
                tweet_text = re.sub(r'\s*https://t\.co/\S+$', '', tweet_text).strip()
                
                print(f"  ✅ Got tweet: {tweet_text[:80]}...")
            else:
                print(f"  ❌ No tweets found")
            
            results.append({
                "name": name,
                "handle": handle,
                "category": category,
                "platform": "x",
                "tweet_text": tweet_text,
                "tweet_url": tweet_url,
                "tweet_date": tweet_date,
            })
    
    # Save intermediate results
    out_path = os.path.expanduser("~/workspace/the-videshi-news/pipeline/pulse-raw-results.json")
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Done. {len(results)} leaders processed.")
    print(f"   Results saved to {out_path}")
    
    # Count successes
    with_tweets = sum(1 for r in results if r["tweet_text"])
    print(f"   {with_tweets}/{len(results)} have tweets")

if __name__ == "__main__":
    main()
