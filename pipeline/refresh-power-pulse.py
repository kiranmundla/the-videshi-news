#!/usr/bin/env python3
"""
refresh-power-pulse.py - Batch fetch latest tweets for all Pulse leaders via X API v2.
Reads leader registry from pulse-leaders.json, outputs tech-buzz.json.
"""
import os, sys, json, re, time
from datetime import datetime, timezone, timedelta

# Import fetch-tweets functions
import importlib.util
spec = importlib.util.spec_from_file_location("fetch_tweets",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "fetch-tweets.py"))
ft = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ft)

LEADERS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pulse-leaders.json")
OUTPUT_PATH = os.path.expanduser("~/workspace/the-videshi-news/public/data/tech-buzz.json")

def clean_tweet_text(text):
    """Remove trailing t.co URLs from tweet text."""
    text = text.strip()
    cleaned = re.sub(r'\s*https://t\.co/\S+', '', text).strip()
    return cleaned if cleaned else text

def main():
    with open(LEADERS_PATH) as f:
        leaders = json.load(f)

    now = datetime.now(timezone.utc).isoformat()
    results = []
    success = 0
    fail = 0

    for i, leader in enumerate(leaders):
        handle = leader["handle"]
        name = leader["name"]
        print(f"[{i+1}/{len(leaders)}] @{handle} ({name})...", end=" ", flush=True)

        tweet_data = None
        try:
            tweets = ft.fetch_recent_tweets(handle, hours=48, max_results=10)
            if tweets:
                # Sort by likes, pick best
                tweets.sort(key=lambda t: -t.get("likes", 0))
                best = tweets[0]
                text = clean_tweet_text(best["text"])
                tweet_data = {
                    "text": text,
                    "url": best["url"],
                    "timestamp": best.get("created_at", now)[:10],
                }
                print(f"OK ({len(tweets)} tweets, best: {best.get('likes',0)} likes)")
            else:
                print("no tweets found")
        except Exception as e:
            print(f"ERROR: {e}")

        entry = {
            "name": name,
            "handle": f"@{handle}",
            "category": leader["category"],
            "platform": "x",
            "posts": []
        }

        if tweet_data:
            entry["posts"].append({
                "text": tweet_data["text"],
                "caption": tweet_data["text"],
                "url": tweet_data["url"],
                "thumbnail": "",
                "timestamp": tweet_data["timestamp"],
            })
            success += 1
        else:
            entry["posts"].append({
                "text": f"Follow @{handle} for the latest updates.",
                "caption": f"Follow @{handle} for the latest updates.",
                "url": f"https://x.com/{handle}",
                "thumbnail": "",
                "timestamp": now[:10],
            })
            fail += 1

        results.append(entry)

        # Small delay every 10 requests
        if (i + 1) % 10 == 0:
            time.sleep(0.5)

    output = {
        "leaders": results,
        "lastUpdated": now,
        "last_updated": now,
    }

    with open(OUTPUT_PATH, "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}")
    print(f"Done: {success} fetched, {fail} fallbacks, {len(results)} total")
    print(f"Written to {OUTPUT_PATH}")

    # Validate
    print("\nValidating...")
    data = json.load(open(OUTPUT_PATH))
    assert "leaders" in data, "Missing top-level 'leaders' key"
    for ld in data["leaders"]:
        assert isinstance(ld.get("posts"), list) and len(ld["posts"]) > 0, \
            f"SCHEMA BUG: {ld.get('name')} missing posts[]!"
        assert ld["posts"][0].get("text"), \
            f"SCHEMA BUG: {ld.get('name')} empty text!"
    print(f"VALIDATED {len(data['leaders'])} leaders - all have posts[] with text")

if __name__ == "__main__":
    main()
