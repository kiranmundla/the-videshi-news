#!/usr/bin/env python3
"""
Power Pulse batch refresh — fetch latest tweets for all 52 leaders via X API v2.
Outputs tech-buzz.json in the required schema.
"""

import os
import sys
import json
import time
from datetime import datetime, timezone, timedelta

# Add pipeline dir to path so we can reuse fetch-tweets functions
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from importlib import import_module

# Manually load the fetch-tweets module
import importlib.util
spec = importlib.util.spec_from_file_location("fetch_tweets", 
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "fetch-tweets.py"))
ft = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ft)

# ─── Leader definitions ───────────────────────────────────────────────────────

LEADERS = {
    "india": [
        ("Narendra Modi", "narendramodi"),
        ("PMO India", "pmoindia"),
        ("Amit Shah", "amitshah"),
        ("Rahul Gandhi", "rahulgandhi"),
        ("Yogi Adityanath", "myogiadityanath"),
        ("Arvind Kejriwal", "arvindkejriwal"),
        ("S Jaishankar", "drsjaishankar"),
        ("Nirmala Sitharaman", "nsitharaman"),
        ("Gautam Adani", "gautam_adani"),
        ("Mukesh Ambani", "reliancejio"),
        ("Ratan Tata", "ratantata"),
        ("President of India", "rashtrapatibhvn"),
    ],
    "world": [
        ("Donald Trump", "realdonaldtrump"),
        ("Rishi Sunak", "rishisunak"),
        ("Vivek Ramaswamy", "vivekgramaswamy"),
        ("Usha Vance", "ushavance"),
        ("Kash Patel", "kashpatel"),
        ("Sriram Krishnan", "sriramk"),
        ("Ajay Banga", "ajay_banga"),
        ("Keir Starmer", "keir_starmer"),
        ("Anthony Albanese", "albomp"),
        ("Emmanuel Macron", "emmanuelmacron"),
        ("Mohammed bin Rashid", "hhshkmohd"),
    ],
    "tech": [
        ("Elon Musk", "elonmusk"),
        ("Mark Zuckerberg", "zuck"),
        ("Sundar Pichai", "sundarpichai"),
        ("Satya Nadella", "satyanadella"),
        ("Sam Altman", "sama"),
        ("Tim Cook", "tim_cook"),
        ("Jensen Huang", "jensenhuang"),
        ("Nandan Nilekani", "nandannilekani"),
        ("Bill Gates", "billgates"),
        ("Arvind Krishna", "arvindkrishna"),
        ("Shantanu Narayen", "adobe"),
        ("Parag Agrawal", "paraga"),
        ("Leena Nair", "leenanair"),
        ("Raj Subramaniam", "rajsubram"),
    ],
    "sports": [
        ("Virat Kohli", "imvkohli"),
        ("Rohit Sharma", "imro45"),
        ("MS Dhoni", "msdhoni"),
        ("Jasprit Bumrah", "jaspritbumrah93"),
        ("Hardik Pandya", "hardikpandya7"),
        ("Sachin Tendulkar", "sachin_rt"),
        ("Sourav Ganguly", "sganguly99"),
        ("BCCI", "bcci"),
        ("ICC", "icc"),
        ("IPL", "ipl"),
        ("Neeraj Chopra", "neeraj_chopra1"),
        ("PV Sindhu", "pvsindhu1"),
        ("Sania Mirza", "mirzasania"),
        ("D Gukesh", "dgukesh"),
        ("Sunil Chhetri", "chetrisunil11"),
    ],
}

def truncate_text(text, max_len=280):
    """Clean up tweet text - remove t.co links at end, trim."""
    import re
    # Remove trailing t.co URLs
    text = re.sub(r'\s*https://t\.co/\S+$', '', text)
    text = re.sub(r'\s*https://t\.co/\S+$', '', text)  # second pass for multiple
    return text.strip()

def main():
    leaders_data = []
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    total = sum(len(v) for v in LEADERS.values())
    done = 0
    failed = []
    
    for category, leader_list in LEADERS.items():
        for name, handle in leader_list:
            done += 1
            print(f"[{done}/{total}] Fetching @{handle} ({name})...", flush=True)
            
            try:
                tweets = ft.fetch_recent_tweets(handle, hours=72, max_results=5)
                
                if tweets:
                    # Pick the most liked/engaged tweet
                    best = max(tweets, key=lambda t: t.get("likes", 0) + t.get("retweets", 0))
                    tweet_text = truncate_text(best["text"])
                    tweet_url = best["url"]
                    tweet_date = best.get("created_at", "")[:10] or today
                    print(f"   ✅ Got tweet: {tweet_text[:80]}...")
                else:
                    tweet_text = ""
                    tweet_url = f"https://x.com/{handle}"
                    tweet_date = today
                    failed.append((name, handle))
                    print(f"   ⚠️ No tweets found in 72h")
                
                leaders_data.append({
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
                
            except Exception as e:
                print(f"   ❌ Error: {e}", flush=True)
                failed.append((name, handle))
                leaders_data.append({
                    "name": name,
                    "handle": handle,
                    "category": category,
                    "platform": "x",
                    "posts": [
                        {
                            "text": "",
                            "caption": "",
                            "url": f"https://x.com/{handle}",
                            "thumbnail": "",
                            "timestamp": today,
                        }
                    ]
                })
            
            # Small delay to avoid rate limiting
            time.sleep(0.3)
    
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    output = {
        "leaders": leaders_data,
        "lastUpdated": now_iso,
        "last_updated": now_iso,
    }
    
    out_path = os.path.expanduser("~/workspace/the-videshi-news/public/data/tech-buzz.json")
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*60}")
    print(f"✅ Wrote {len(leaders_data)} leaders to tech-buzz.json")
    if failed:
        print(f"⚠️ {len(failed)} leaders had no tweets: {', '.join(f'@{h}' for _, h in failed)}")
    print(f"{'='*60}")
    
    # Return failed list for caller
    return failed

if __name__ == "__main__":
    failed = main()
    # Output failed handles as JSON for the caller
    if failed:
        print(f"\nFAILED_HANDLES={json.dumps([h for _, h in failed])}")
