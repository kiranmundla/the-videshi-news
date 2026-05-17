#!/usr/bin/env python3
"""
Tech Pulse tweet scraper for The Videshi.

Modes:
  1. Standalone:  python3 scrape-tweets.py
     → Tries Twitter syndication API for each X leader.
  
  2. Manual update:  python3 scrape-tweets.py --update '<json>'
     → Accepts JSON to update specific leaders' latest posts.
     JSON format: [{"handle": "sama", "text": "...", "url": "https://x.com/...", "date": "...", "likes": 0, "retweets": 0}]

  3. From the pipeline cron, the subagent uses web_search to find
     latest tweets, then calls this script with --update to save them.
"""

import json
import os
import sys
import time
import re
import urllib.request
import urllib.error
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(SCRIPT_DIR, "..", "public", "data", "tech-buzz.json")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://platform.twitter.com/",
}


def fetch_timeline(handle: str) -> dict | None:
    """Fetch latest tweet from Twitter syndication endpoint."""
    url = f"https://syndication.twitter.com/srv/timeline-profile/screen-name/{handle}"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        html = resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        print(f"  ⚠ HTTP {e.code} for @{handle}")
        return None
    except Exception as e:
        print(f"  ⚠ Error fetching @{handle}: {e}")
        return None

    if len(html) < 200:
        print(f"  ⚠ Response too short ({len(html)} bytes)")
        return None

    tweets = []

    # Try multiple parsing strategies

    # Strategy 1: __NEXT_DATA__ JSON payload
    nextdata = re.search(r'<script[^>]*id="__NEXT_DATA__"[^>]*>(.*?)</script>', html)
    if nextdata:
        try:
            nd = json.loads(nextdata.group(1))
            timeline = nd.get("props", {}).get("pageProps", {}).get("timeline", {})
            for entry in timeline.get("entries", []):
                tweet = entry.get("content", {}).get("tweet", {})
                if tweet and tweet.get("id_str"):
                    tweets.append(tweet)
        except (json.JSONDecodeError, AttributeError):
            pass

    # Strategy 2: embedded JSON blob with entries
    if not tweets:
        json_blobs = re.findall(r'\{[^{}]*"entries"\s*:\s*\[.*?\]\s*[^{}]*\}', html, re.DOTALL)
        for blob in json_blobs:
            try:
                data = json.loads(blob)
                for entry in data.get("entries", []):
                    tweet = entry.get("content", {}).get("tweet", {})
                    if tweet and tweet.get("id_str"):
                        tweets.append(tweet)
            except json.JSONDecodeError:
                continue

    # Strategy 3: Parse timeline HTML for tweet links and text
    if not tweets:
        tweet_blocks = re.findall(
            r'<div[^>]*class="[^"]*timeline-Tweet[^"]*"[^>]*>(.*?)</div>\s*</div>',
            html, re.DOTALL
        )
        for block in tweet_blocks:
            link_m = re.search(r'href="(/[^/]+/status/\d+)"', block)
            text_m = re.search(r'class="[^"]*Tweet-text[^"]*"[^>]*>(.*?)</(?:p|div)', block, re.DOTALL)
            if link_m:
                text = re.sub(r'<[^>]+>', '', text_m.group(1)).strip() if text_m else ""
                tweet_url = f"https://x.com{link_m.group(1)}"
                tweets.append({
                    "id_str": link_m.group(1).split("/")[-1],
                    "full_text": text,
                    "_url": tweet_url,
                })

    if not tweets:
        # Save for debugging
        debug_path = f"/tmp/twitter_debug_{handle}.html"
        with open(debug_path, "w") as f:
            f.write(html)
        print(f"  ℹ No tweets parsed. Saved debug HTML ({len(html)} bytes) → {debug_path}")
        return None

    latest = tweets[0]
    user = latest.get("user", {})
    avatar = user.get("profile_image_url_https", "")
    if avatar:
        avatar = avatar.replace("_normal", "_400x400")

    return {
        "text": latest.get("full_text", latest.get("text", "")),
        "url": latest.get("_url", f"https://x.com/{handle}/status/{latest.get('id_str', '')}"),
        "date": latest.get("created_at", ""),
        "likes": latest.get("favorite_count", 0),
        "retweets": latest.get("retweet_count", 0),
        "avatar": avatar,
    }


def manual_update(json_str: str):
    """Update leaders with provided data."""
    updates = json.loads(json_str)
    
    with open(DATA_FILE) as f:
        data = json.load(f)

    leaders_by_handle = {l["handle"]: l for l in data.get("leaders", [])}
    updated = 0

    for update in updates:
        handle = update.get("handle")
        if handle and handle in leaders_by_handle:
            leader = leaders_by_handle[handle]
            leader["latestPost"] = {
                "url": update.get("url", ""),
                "text": update.get("text", ""),
                "date": update.get("date", ""),
                "likes": update.get("likes", 0),
                "retweets": update.get("retweets", 0),
            }
            if update.get("avatar"):
                leader["avatar"] = update["avatar"]
            print(f"✅ Updated @{handle}: {update.get('text', '')[:60]}...")
            updated += 1
        else:
            print(f"⚠ Handle @{handle} not found in tech-buzz.json")

    data["lastUpdated"] = datetime.now(timezone.utc).isoformat()
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\nUpdated {updated} leaders. Saved to {DATA_FILE}")


def scrape_all():
    """Scrape all X leaders."""
    with open(DATA_FILE) as f:
        data = json.load(f)

    leaders = data.get("leaders", [])
    updated = 0
    failed = 0

    for leader in leaders:
        handle = leader["handle"]
        platform = leader.get("platform", "x")

        if platform != "x":
            print(f"⏭ Skipping @{handle} (platform: {platform})")
            continue

        print(f"🔍 Fetching @{handle}...")
        time.sleep(3)  # Be nice to Twitter

        result = fetch_timeline(handle)
        if result:
            leader["latestPost"] = {
                "url": result["url"],
                "text": result["text"],
                "date": result["date"],
                "likes": result["likes"],
                "retweets": result["retweets"],
            }
            if result["avatar"]:
                leader["avatar"] = result["avatar"]
            print(f"  ✅ Got tweet: {result['text'][:80]}...")
            updated += 1
        else:
            print(f"  ❌ Could not fetch tweets")
            failed += 1

    data["lastUpdated"] = datetime.now(timezone.utc).isoformat()
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*50}")
    print(f"Updated: {updated}, Failed: {failed}")
    print(f"Saved to {DATA_FILE}")

    if failed > 0:
        print(f"\n💡 Tip: Use --update with JSON data from web search:")
        print(f'   python3 scrape-tweets.py --update \'[{{"handle":"sama","text":"...","url":"https://x.com/..."}}]\'')


if __name__ == "__main__":
    if "--update" in sys.argv:
        idx = sys.argv.index("--update")
        if idx + 1 < len(sys.argv):
            manual_update(sys.argv[idx + 1])
        else:
            # Read from stdin
            manual_update(sys.stdin.read())
    else:
        scrape_all()
