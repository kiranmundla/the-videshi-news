#!/usr/bin/env python3
"""
refresh-power-pulse.py -- Batch-fetch latest tweets for all Pulse leaders via X API v2.
Writes tech-buzz.json for The Videshi's 4 Pulse sections.
"""

import os, sys, json, time, re
from datetime import datetime, timezone, timedelta

# Reuse fetch-tweets.py infrastructure
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from importlib.machinery import SourceFileLoader
ft = SourceFileLoader("fetch_tweets", os.path.join(os.path.dirname(os.path.abspath(__file__)), "fetch-tweets.py")).load_module()

LEADERS = [
    # ---- India Pulse (12) ----
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
    # ---- Power Pulse / World (11) ----
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
    # ---- Tech Pulse (14) ----
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
    # ---- Sports Pulse (15) ----
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

OUTPUT_PATH = os.path.expanduser("~/workspace/the-videshi-news/public/data/tech-buzz.json")

def main():
    results = []
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    total = len(LEADERS)
    success = 0
    fallback = 0

    for i, leader in enumerate(LEADERS):
        name = leader["name"]
        handle = leader["handle"]
        category = leader["category"]

        print(f"[{i+1}/{total}] @{handle} ({name})...", end=" ", flush=True)

        try:
            tweets = ft.fetch_recent_tweets(handle, hours=72, max_results=5)
        except Exception as e:
            print(f"ERROR: {e}")
            tweets = []

        if tweets:
            tweet = tweets[0]
            text = tweet["text"].strip()
            text_clean = re.sub(r'https://t\.co/\S+', '', text).strip()
            if not text_clean:
                text_clean = text
            url = tweet["url"]
            ts = tweet.get("created_at", today)[:10]
            print(f"OK ({len(text_clean)}ch)")
            success += 1
        else:
            text_clean = f"Follow @{handle} for the latest updates."
            url = f"https://x.com/{handle}"
            ts = today
            print(f"fallback")
            fallback += 1

        results.append({
            "name": name,
            "handle": handle,
            "category": category,
            "platform": "x",
            "posts": [{
                "text": text_clean,
                "caption": text_clean,
                "url": url,
                "thumbnail": "",
                "timestamp": ts,
            }]
        })

        # Rate limit: 1s pause every 15 requests
        if (i + 1) % 15 == 0:
            time.sleep(1)

    output = {
        "leaders": results,
        "lastUpdated": now_iso,
        "last_updated": now_iso,
    }

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}")
    print(f"Written {len(results)} leaders to tech-buzz.json")
    print(f"Tweets found: {success}/{total}, Fallbacks: {fallback}/{total}")

    # Self-validation
    data = json.load(open(OUTPUT_PATH))
    assert "leaders" in data, "Missing top-level 'leaders' key"
    for ld in data["leaders"]:
        assert isinstance(ld.get("posts"), list) and len(ld["posts"]) > 0, \
            f"SCHEMA BUG: {ld.get('name')} missing posts[]"
        assert ld["posts"][0].get("text"), \
            f"SCHEMA BUG: {ld.get('name')} empty text in posts[0]"
        assert ld.get("platform") == "x", \
            f"SCHEMA BUG: {ld.get('name')} platform != x"
    print(f"VALIDATED {len(data['leaders'])} leaders -- all have posts[] with text")

if __name__ == "__main__":
    main()
