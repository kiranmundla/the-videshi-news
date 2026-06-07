#!/usr/bin/env python3
"""
power-pulse-refresh.py — Batch fetch recent tweets for all Pulse leaders
and write tech-buzz.json for The Videshi frontend.
"""

import os
import sys
import json
import time
from datetime import datetime, timezone

# Add pipeline dir to path so we can import fetch-tweets functions
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import from fetch-tweets.py (module name with hyphen needs importlib)
import importlib
ft = importlib.import_module("fetch-tweets")

# Leader registry — using correct X handles (NOT Instagram)
LEADERS = [
    # India (12)
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

    # World (11)
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

    # Tech (14)
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

    # Sports (15)
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

def truncate_text(text, max_len=280):
    """Clean up tweet text for display."""
    # Remove t.co links at end
    import re
    text = re.sub(r'\s*https://t\.co/\S+', '', text).strip()
    if len(text) > max_len:
        text = text[:max_len-3] + "..."
    return text

def main():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    results = []
    success_count = 0
    fallback_count = 0
    fail_count = 0

    for i, leader in enumerate(LEADERS):
        name = leader["name"]
        handle = leader["handle"]
        category = leader["category"]

        print(f"[{i+1}/{len(LEADERS)}] Fetching @{handle} ({name})...", end=" ", flush=True)

        try:
            tweets = ft.fetch_recent_tweets(handle, hours=48, max_results=5)

            if tweets:
                # Pick most-liked tweet
                tweets.sort(key=lambda t: -t.get("likes", 0))
                best = tweets[0]
                tweet_text = truncate_text(best["text"])
                tweet_url = best["url"]
                tweet_date = best.get("created_at", today)[:10]
                print(f"✅ Got tweet (❤️ {best.get('likes', 0)})")
                success_count += 1
            else:
                # No tweets in 48h — use profile URL
                tweet_text = f"Follow @{handle} for the latest updates."
                tweet_url = f"https://x.com/{handle}"
                tweet_date = today
                print(f"⚠️ No recent tweets — using profile fallback")
                fallback_count += 1

        except Exception as e:
            tweet_text = f"Follow @{handle} for the latest updates."
            tweet_url = f"https://x.com/{handle}"
            tweet_date = today
            print(f"❌ Error: {str(e)[:60]}")
            fail_count += 1

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

        # Small delay to avoid rate limiting (10K/15min is generous but be polite)
        if (i + 1) % 10 == 0:
            time.sleep(1)

    output = {
        "leaders": results,
        "lastUpdated": now_iso,
        "last_updated": now_iso
    }

    out_path = os.path.expanduser("~/workspace/the-videshi-news/public/data/tech-buzz.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}")
    print(f"✅ Written {len(results)} leaders to tech-buzz.json")
    print(f"   Tweets found: {success_count}")
    print(f"   Profile fallback: {fallback_count}")
    print(f"   Errors: {fail_count}")
    print(f"   Last updated: {now_iso}")

    # Self-validation
    print(f"\n{'='*60}")
    print("Running schema validation...")
    data = json.load(open(out_path))
    assert "leaders" in data, "Missing top-level 'leaders' key"
    for leader in data["leaders"]:
        assert isinstance(leader.get("posts"), list) and len(leader["posts"]) > 0, \
            f"SCHEMA BUG: {leader.get('name')} missing posts[] array!"
        assert leader["posts"][0].get("text"), \
            f"SCHEMA BUG: {leader.get('name')} has empty text in posts[0]!"
        assert leader.get("platform") == "x", \
            f"SCHEMA BUG: {leader.get('name')} platform is not 'x'!"
    print(f"✅ Validated {len(data['leaders'])} leaders — all have posts[] with text")

    # Category breakdown
    cats = {}
    for l in data["leaders"]:
        cats[l["category"]] = cats.get(l["category"], 0) + 1
    for cat, count in sorted(cats.items()):
        print(f"   {cat}: {count} leaders")


if __name__ == "__main__":
    main()
