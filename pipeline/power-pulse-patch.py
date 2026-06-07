#!/usr/bin/env python3
"""
Patch fallback leaders with wider API window and web-sourced quotes.
"""
import os, sys, json, importlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ft = importlib.import_module("fetch-tweets")

OUT_PATH = os.path.expanduser("~/workspace/the-videshi-news/public/data/tech-buzz.json")
data = json.load(open(OUT_PATH))

# Find leaders with generic fallback text
fallback_leaders = []
for leader in data["leaders"]:
    if leader["posts"][0]["text"].startswith("Follow @"):
        fallback_leaders.append(leader)

print(f"Found {len(fallback_leaders)} leaders with fallback text")
print("Trying wider 168h (1 week) window...\n")

import re
def truncate_text(text, max_len=280):
    text = re.sub(r'\s*https://t\.co/\S+', '', text).strip()
    if len(text) > max_len:
        text = text[:max_len-3] + "..."
    return text

patched = 0
for leader in fallback_leaders:
    handle = leader["handle"]
    name = leader["name"]
    print(f"  Retrying @{handle} ({name}) with 168h window...", end=" ", flush=True)
    
    try:
        tweets = ft.fetch_recent_tweets(handle, hours=168, max_results=5)
        if tweets:
            tweets.sort(key=lambda t: -t.get("likes", 0))
            best = tweets[0]
            leader["posts"][0]["text"] = truncate_text(best["text"])
            leader["posts"][0]["caption"] = truncate_text(best["text"])
            leader["posts"][0]["url"] = best["url"]
            leader["posts"][0]["timestamp"] = best.get("created_at", "")[:10]
            print(f"✅ Got tweet from {best.get('created_at', '?')[:10]} (❤️ {best.get('likes', 0)})")
            patched += 1
        else:
            print(f"⚠️ Still nothing in 7 days")
    except Exception as e:
        print(f"❌ {str(e)[:60]}")

print(f"\nPatched {patched} additional leaders with real tweets")

# Save updated data
from datetime import datetime, timezone
data["lastUpdated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
data["last_updated"] = data["lastUpdated"]

with open(OUT_PATH, "w") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

# Report still-missing
still_fallback = [l for l in data["leaders"] if l["posts"][0]["text"].startswith("Follow @")]
if still_fallback:
    print(f"\nStill need web search fallback ({len(still_fallback)}):")
    for l in still_fallback:
        print(f"  - {l['name']} (@{l['handle']})")
