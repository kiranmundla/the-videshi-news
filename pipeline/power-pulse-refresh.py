#!/usr/bin/env python3
"""
power-pulse-refresh.py — Batch refresh all 4 Pulse sections via X API v2.
"""

import os, sys, json, time
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.join(os.path.expanduser("~/workspace/the-videshi-news/pipeline")))

def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip())

load_env(os.path.expanduser("~/workspace/.env.twitter"))

# Now import from the pipeline
from importlib.machinery import SourceFileLoader
ft = SourceFileLoader("fetch_tweets", os.path.expanduser("~/workspace/the-videshi-news/pipeline/fetch-tweets.py")).load_module()

LEADERS = [
    # India (12)
    {"name": "Narendra Modi", "handle": "narendramodi", "category": "india"},
    {"name": "PMO India", "handle": "PMOIndia", "category": "india"},
    {"name": "Amit Shah", "handle": "AmitShah", "category": "india"},
    {"name": "Rahul Gandhi", "handle": "RahulGandhi", "category": "india"},
    {"name": "Yogi Adityanath", "handle": "myogiadityanath", "category": "india"},
    {"name": "Arvind Kejriwal", "handle": "ArvindKejriwal", "category": "india"},
    {"name": "S Jaishankar", "handle": "DrSJaishankar", "category": "india"},
    {"name": "Nirmala Sitharaman", "handle": "nsitharaman", "category": "india"},
    {"name": "Gautam Adani", "handle": "gautam_adani", "category": "india"},
    {"name": "Mukesh Ambani", "handle": "reliancejio", "category": "india"},
    {"name": "Ratan Tata", "handle": "ratantata", "category": "india"},
    {"name": "President of India", "handle": "rashtrapatibhvn", "category": "india"},

    # World (11)
    {"name": "Donald Trump", "handle": "realDonaldTrump", "category": "world"},
    {"name": "Rishi Sunak", "handle": "RishiSunak", "category": "world"},
    {"name": "Vivek Ramaswamy", "handle": "VivekGRamaswamy", "category": "world"},
    {"name": "Usha Vance", "handle": "ushaVance", "category": "world"},
    {"name": "Kash Patel", "handle": "KashPatel", "category": "world"},
    {"name": "Sriram Krishnan", "handle": "SriramK", "category": "world"},
    {"name": "Ajay Banga", "handle": "AjayBanga", "category": "world"},
    {"name": "Keir Starmer", "handle": "Keir_Starmer", "category": "world"},
    {"name": "Anthony Albanese", "handle": "AlboMP", "category": "world"},
    {"name": "Emmanuel Macron", "handle": "EmmanuelMacron", "category": "world"},
    {"name": "Mohammed bin Rashid", "handle": "HHShkMohd", "category": "world"},

    # Tech (14)
    {"name": "Elon Musk", "handle": "elonmusk", "category": "tech"},
    {"name": "Mark Zuckerberg", "handle": "zuck", "category": "tech"},
    {"name": "Sundar Pichai", "handle": "sundarpichai", "category": "tech"},
    {"name": "Satya Nadella", "handle": "satyanadella", "category": "tech"},
    {"name": "Sam Altman", "handle": "sama", "category": "tech"},
    {"name": "Tim Cook", "handle": "tim_cook", "category": "tech"},
    {"name": "Jensen Huang", "handle": "nvidia", "category": "tech"},
    {"name": "Nandan Nilekani", "handle": "NandanNilekani", "category": "tech"},
    {"name": "Bill Gates", "handle": "BillGates", "category": "tech"},
    {"name": "Arvind Krishna", "handle": "ArvindKrishna", "category": "tech"},
    {"name": "Shantanu Narayen", "handle": "Adobe", "category": "tech"},
    {"name": "Parag Agrawal", "handle": "paraga", "category": "tech"},
    {"name": "Leena Nair", "handle": "LeenaNairCEO", "category": "tech"},
    {"name": "Raj Subramaniam", "handle": "FedEx", "category": "tech"},

    # Sports (15)
    {"name": "Virat Kohli", "handle": "imVkohli", "category": "sports"},
    {"name": "Rohit Sharma", "handle": "ImRo45", "category": "sports"},
    {"name": "MS Dhoni", "handle": "msdhoni", "category": "sports"},
    {"name": "Jasprit Bumrah", "handle": "Jaspritbumrah93", "category": "sports"},
    {"name": "Hardik Pandya", "handle": "hardikpandya93", "category": "sports"},
    {"name": "Sachin Tendulkar", "handle": "sachin_rt", "category": "sports"},
    {"name": "Sourav Ganguly", "handle": "SGanguly99", "category": "sports"},
    {"name": "BCCI", "handle": "BCCI", "category": "sports"},
    {"name": "ICC", "handle": "ICC", "category": "sports"},
    {"name": "IPL", "handle": "IPL", "category": "sports"},
    {"name": "Neeraj Chopra", "handle": "Neeraj_chopra1", "category": "sports"},
    {"name": "PV Sindhu", "handle": "Pvsindhu1", "category": "sports"},
    {"name": "Sania Mirza", "handle": "MirzaSania", "category": "sports"},
    {"name": "D Gukesh", "handle": "DGukesh", "category": "sports"},
    {"name": "Sunil Chhetri", "handle": "chetrisunil11", "category": "sports"},
]

def main():
    results = []
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    success_count = 0
    fallback_count = 0

    # Load existing data for fallback
    existing_path = os.path.expanduser("~/workspace/the-videshi-news/public/data/tech-buzz.json")
    existing_map = {}
    if os.path.exists(existing_path):
        try:
            existing = json.load(open(existing_path))
            for l in existing.get("leaders", []):
                existing_map[l["handle"].lower()] = l
        except:
            pass

    for leader in LEADERS:
        handle = leader["handle"]
        name = leader["name"]
        print(f"[{leader['category']}] @{handle} ({name})...", end=" ", flush=True)

        try:
            tweets = ft.fetch_recent_tweets(handle, hours=72, max_results=5)
            time.sleep(0.2)

            if tweets:
                tweet = tweets[0]
                tweet_text = tweet["text"].strip()
                tweet_url = tweet["url"]
                tweet_date = tweet["created_at"][:10] if tweet.get("created_at") else today
                print(f"OK ({len(tweets)} tweets)")
                success_count += 1
            else:
                # Use existing data as fallback
                ex = existing_map.get(handle.lower())
                if ex and ex.get("posts") and ex["posts"][0].get("text"):
                    tweet_text = ex["posts"][0]["text"]
                    tweet_url = ex["posts"][0].get("url", f"https://x.com/{handle}")
                    tweet_date = ex["posts"][0].get("timestamp", today)
                    print(f"REUSE (no new tweets)")
                else:
                    tweet_text = f"Follow my latest updates on X."
                    tweet_url = f"https://x.com/{handle}"
                    tweet_date = today
                    print(f"FALLBACK (no tweets)")
                fallback_count += 1

        except Exception as e:
            # Use existing data as fallback
            ex = existing_map.get(handle.lower())
            if ex and ex.get("posts") and ex["posts"][0].get("text"):
                tweet_text = ex["posts"][0]["text"]
                tweet_url = ex["posts"][0].get("url", f"https://x.com/{handle}")
                tweet_date = ex["posts"][0].get("timestamp", today)
                print(f"REUSE on error: {e}")
            else:
                tweet_text = f"Follow my latest updates on X."
                tweet_url = f"https://x.com/{handle}"
                tweet_date = today
                print(f"ERROR: {e}")
            fallback_count += 1

        results.append({
            "name": name,
            "handle": handle,
            "category": leader["category"],
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

    output = {
        "leaders": results,
        "lastUpdated": now_iso,
        "last_updated": now_iso
    }

    with open(existing_path, "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}")
    print(f"Wrote {len(results)} leaders to tech-buzz.json")
    print(f"API success: {success_count} | Reused/fallback: {fallback_count}")
    print(f"Updated: {now_iso}")

    # Self-validation
    print(f"\n--- VALIDATION ---")
    data = json.load(open(existing_path))
    assert "leaders" in data, "Missing top-level 'leaders' key"
    for l in data["leaders"]:
        assert isinstance(l.get("posts"), list) and len(l["posts"]) > 0, \
            f"SCHEMA BUG: {l.get('name')} missing posts[] array!"
        assert l["posts"][0].get("text"), \
            f"SCHEMA BUG: {l.get('name')} has empty text in posts[0]!"
        assert l.get("platform") == "x", \
            f"SCHEMA BUG: {l.get('name')} platform is not 'x'!"
    print(f"VALID: {len(data['leaders'])} leaders — all have posts[] with text")
    
    # Category breakdown
    cats = {}
    for l in data["leaders"]:
        c = l["category"]
        cats[c] = cats.get(c, 0) + 1
    for c, n in sorted(cats.items()):
        print(f"  {c}: {n}")

if __name__ == "__main__":
    main()
