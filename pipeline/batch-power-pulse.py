#!/usr/bin/env python3
"""
Batch Power Pulse refresh — fetch latest tweets for all 52 leaders via X API v2.
"""

import os
import sys
import json
import time
from datetime import datetime, timezone

# Add pipeline to path so we can import fetch-tweets functions
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import from fetch-tweets
from importlib.util import spec_from_file_location, module_from_spec
spec = spec_from_file_location("fetch_tweets", os.path.join(os.path.dirname(os.path.abspath(__file__)), "fetch-tweets.py"))
ft = module_from_spec(spec)
spec.loader.exec_module(ft)

# ─── Leader definitions ───────────────────────────────────────────────────────
# Using verified X handles from the user ID cache

LEADERS = [
    # INDIA (12)
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

    # WORLD (11)
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

    # TECH (14)
    {"name": "Elon Musk", "handle": "elonmusk", "category": "tech"},
    {"name": "Mark Zuckerberg", "handle": "finkd", "category": "tech"},
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
    {"name": "Raj Subramaniam", "handle": "rajsubram", "category": "tech"},

    # SPORTS (15)
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

def main():
    results = []
    total = len(LEADERS)
    
    for i, leader in enumerate(LEADERS):
        name = leader["name"]
        handle = leader["handle"]
        category = leader["category"]
        
        print(f"[{i+1}/{total}] Fetching @{handle} ({name})...", flush=True)
        
        try:
            tweets = ft.fetch_recent_tweets(handle, hours=72, max_results=5)
        except Exception as e:
            print(f"  ❌ Error: {e}", flush=True)
            tweets = []
        
        if tweets:
            # Pick the best tweet (most liked, prefer non-trivial text)
            best = max(tweets, key=lambda t: t.get("likes", 0))
            tweet_text = best["text"]
            tweet_url = best["url"]
            tweet_date = best["created_at"][:10] if best.get("created_at") else datetime.now(timezone.utc).strftime("%Y-%m-%d")
            print(f"  ✅ Found {len(tweets)} tweets, best: {tweet_text[:60]}...", flush=True)
        else:
            tweet_text = ""
            tweet_url = f"https://x.com/{handle}"
            tweet_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            print(f"  ⚠️ No tweets found", flush=True)
        
        results.append({
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
                    "timestamp": tweet_date
                }
            ]
        })
        
        # Small delay to avoid rate limits
        if i < total - 1:
            time.sleep(0.3)
    
    # Build final output
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    output = {
        "leaders": results,
        "lastUpdated": now_iso,
        "last_updated": now_iso
    }
    
    out_path = os.path.expanduser("~/workspace/the-videshi-news/public/data/tech-buzz.json")
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Wrote {len(results)} leaders to {out_path}")
    
    # Count stats
    with_tweets = sum(1 for r in results if r["posts"][0]["text"])
    without_tweets = sum(1 for r in results if not r["posts"][0]["text"])
    print(f"   With tweets: {with_tweets}")
    print(f"   Without tweets: {without_tweets}")
    
    return output

if __name__ == "__main__":
    main()
