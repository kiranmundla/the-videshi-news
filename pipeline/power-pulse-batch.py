#!/usr/bin/env python3
"""
Batch fetch latest tweets for all Power Pulse leaders via X API v2.
Outputs tech-buzz.json for the frontend.
"""

import os, sys, json, time
from datetime import datetime, timezone, timedelta

# Add pipeline dir to path so we can import fetch-tweets functions
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from importlib import import_module

# Import fetch-tweets module
spec = __import__('importlib').util.spec_from_file_location(
    "fetch_tweets",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "fetch-tweets.py")
)
ft = __import__('importlib').util.module_from_spec(spec)
spec.loader.exec_module(ft)

# Leader definitions: (name, x_handle, category)
LEADERS = [
    # India (12)
    ("Narendra Modi", "narendramodi", "india"),
    ("PMO India", "pmoindia", "india"),
    ("Amit Shah", "amitshah", "india"),
    ("Rahul Gandhi", "rahulgandhi", "india"),
    ("Yogi Adityanath", "myogiadityanath", "india"),
    ("Arvind Kejriwal", "arvindkejriwal", "india"),
    ("S Jaishankar", "drsjaishankar", "india"),
    ("Nirmala Sitharaman", "nsitharaman", "india"),
    ("Gautam Adani", "gautam_adani", "india"),
    ("Mukesh Ambani", "reliancejio", "india"),  # No personal X, use Reliance Jio
    ("Ratan Tata", "ratantata", "india"),  # Deceased Oct 2024
    ("President of India", "rashtrapatibhvn", "india"),

    # World (11)
    ("Donald Trump", "realdonaldtrump", "world"),
    ("Rishi Sunak", "rishisunak", "world"),
    ("Vivek Ramaswamy", "vivekgramaswamy", "world"),
    ("Usha Vance", "ushavance", "world"),
    ("Kash Patel", "kashpatel", "world"),
    ("Sriram Krishnan", "sriramk", "world"),
    ("Ajay Banga", "ajay_banga", "world"),
    ("Keir Starmer", "keir_starmer", "world"),
    ("Anthony Albanese", "albomp", "world"),
    ("Emmanuel Macron", "emmanuelmacron", "world"),
    ("Mohammed bin Rashid", "hhshkmohd", "world"),

    # Tech (14)
    ("Elon Musk", "elonmusk", "tech"),
    ("Mark Zuckerberg", "finkd", "tech"),  # X handle is @finkd
    ("Sundar Pichai", "sundarpichai", "tech"),
    ("Satya Nadella", "satyanadella", "tech"),
    ("Sam Altman", "sama", "tech"),
    ("Tim Cook", "tim_cook", "tech"),
    ("Jensen Huang", "jensenhuang", "tech"),
    ("Nandan Nilekani", "nandannilekani", "tech"),
    ("Bill Gates", "billgates", "tech"),
    ("Arvind Krishna", "arvindkrishna", "tech"),
    ("Shantanu Narayen", "adobe", "tech"),  # Uses corporate handle
    ("Parag Agrawal", "paraga", "tech"),
    ("Leena Nair", "leenanair", "tech"),
    ("Raj Subramaniam", "rajsubramaniam", "tech"),

    # Sports (15)
    ("Virat Kohli", "imvkohli", "sports"),
    ("Rohit Sharma", "imro45", "sports"),
    ("MS Dhoni", "msdhoni", "sports"),
    ("Jasprit Bumrah", "jaspritbumrah93", "sports"),
    ("Hardik Pandya", "hardikpandya7", "sports"),
    ("Sachin Tendulkar", "sachin_rt", "sports"),
    ("Sourav Ganguly", "sganguly99", "sports"),
    ("BCCI", "bcci", "sports"),
    ("ICC", "icc", "sports"),
    ("IPL", "ipl", "sports"),
    ("Neeraj Chopra", "neeraj_chopra1", "sports"),
    ("PV Sindhu", "pvsindhu1", "sports"),
    ("Sania Mirza", "mirzasania", "sports"),
    ("D Gukesh", "dgukesh", "sports"),
    ("Sunil Chhetri", "chetrisunil11", "sports"),
]

def fetch_leader_tweet(name, handle, hours=72):
    """Fetch the most recent tweet for a leader."""
    try:
        tweets = ft.fetch_recent_tweets(handle, hours=hours, max_results=5)
        if tweets:
            # Pick most recent (first in list, API returns chronologically)
            best = tweets[0]
            return {
                "text": best["text"],
                "url": best["url"],
                "timestamp": best["created_at"][:10] if best.get("created_at") else datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            }
    except Exception as e:
        print(f"  ⚠ API error for @{handle}: {e}", file=sys.stderr)
    return None

def main():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    leaders_json = []
    success = 0
    fallback = 0
    failed = 0
    
    for name, handle, category in LEADERS:
        print(f"Fetching @{handle} ({name})...", end=" ", flush=True)
        
        result = fetch_leader_tweet(name, handle, hours=72)
        
        if result:
            tweet_text = result["text"]
            tweet_url = result["url"]
            tweet_date = result["timestamp"]
            print(f"✅ got tweet ({tweet_date})")
            success += 1
        else:
            # No tweet found — mark for web search fallback
            tweet_text = None
            tweet_url = f"https://x.com/{handle}"
            tweet_date = today
            print(f"❌ no tweets in 72h")
            failed += 1
        
        leader_entry = {
            "name": name,
            "handle": handle,
            "category": category,
            "platform": "x",
            "posts": [
                {
                    "text": tweet_text or f"[NEEDS_FALLBACK]",
                    "caption": tweet_text or f"[NEEDS_FALLBACK]",
                    "url": tweet_url,
                    "thumbnail": "",
                    "timestamp": tweet_date,
                }
            ]
        }
        leaders_json.append(leader_entry)
        
        # Small delay to avoid rate limiting
        time.sleep(0.2)
    
    # Write output
    output = {
        "leaders": leaders_json,
        "lastUpdated": now_iso,
        "last_updated": now_iso,
    }
    
    out_path = os.path.expanduser("~/workspace/the-videshi-news/public/data/tech-buzz.json")
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n📊 Results: {success} tweets, {failed} need fallback")
    
    # Print leaders needing fallback
    needs_fallback = [l for l in leaders_json if l["posts"][0]["text"] == "[NEEDS_FALLBACK]"]
    if needs_fallback:
        print("\n🔍 Leaders needing web search fallback:")
        for l in needs_fallback:
            print(f"  - {l['name']} (@{l['handle']})")
    
    # Output the needs-fallback list as JSON for easy parsing
    fallback_path = "/tmp/pulse-fallback-needed.json"
    with open(fallback_path, "w") as f:
        json.dump([{"name": l["name"], "handle": l["handle"], "category": l["category"]} for l in needs_fallback], f)
    
    print(f"\nFallback list written to {fallback_path}")

if __name__ == "__main__":
    main()
