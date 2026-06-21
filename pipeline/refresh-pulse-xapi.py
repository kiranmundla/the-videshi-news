#!/usr/bin/env python3
"""
Refresh tech-buzz.json (the Pulse strips: India/World/Tech/Sports Pulse)
DETERMINISTICALLY from the funded X API — no flaky web-search scraping.

Why this exists:
  The old `videshi-power-pulse` cron asked an agent to Google `site:x.com`
  for each leader's latest tweet. That failed ~half the time → cards fell
  back to "Follow @handle for the latest updates." We have a funded X API
  (OAuth1 user-context in ~/workspace/.env.twitter) that reads timelines
  cleanly, so use it directly.

Behavior per leader:
  - Pull recent original tweets (no RT/replies) via fetch_recent_tweets().
  - Use the most recent one with real text.
  - If the API returns nothing (inactive/protected/deceased account, or a
    transient error), KEEP the existing real post if there is one, so we
    never downgrade good data to a placeholder.
  - Only emit the "Follow @handle" placeholder when we have neither a fresh
    tweet nor an existing real post.

Schema (frontend reads leader.posts[0].text — do not change shape):
  {"leaders":[{name,handle,category,platform:"x",
               posts:[{text,caption,url,thumbnail,timestamp}]}],
   "lastUpdated":ISO,"last_updated":ISO}
"""
import json, os, sys, time
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
# fetch-tweets.py has a hyphen; import via a temp alias
import importlib.util
_spec = importlib.util.spec_from_file_location("fetch_tweets", os.path.join(HERE, "fetch-tweets.py"))
ft = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ft)

OUT = os.path.join(HERE, "..", "public", "data", "tech-buzz.json")
OUT = os.path.normpath(OUT)
LEADERS = os.path.join(HERE, "pulse-leaders.json")

# Handle corrections — accounts that renamed/moved since the list was built.
# Keyed by leader NAME so it doesn't matter what stale handle is on file.
HANDLE_OVERRIDE = {
    "Usha Vance": "SLOTUS",          # Second Lady official account
    "Mark Zuckerberg": "finkd",      # Zuck's actual personal handle
    "Hardik Pandya": "hardikpandya7",
    # Ratan Tata (deceased; RNTata2000 inactive) and Ajay Banga (no personal
    # handle) intentionally left to fall through to placeholder.
}


def is_placeholder(post):
    if not post:
        return True
    t = (post.get("text") or "").strip()
    if not t:
        return True
    if t.lower().startswith("follow @"):
        return True
    return False


def fetch_latest_original(handle, max_results=10):
    """Latest original tweets (no RT/replies), NO time window — returns the
    person's genuine most-recent words even if they post infrequently.
    This is the behavior the Pulse strips originally had."""
    uid = ft.get_user_id(handle)
    if not uid:
        return []
    sess = ft.get_oauth_session()
    params = {
        "max_results": max(5, min(max_results, 100)),
        "tweet.fields": "created_at,attachments,text,public_metrics",
        "expansions": "attachments.media_keys",
        "media.fields": "type,url,preview_image_url",
        "exclude": "retweets,replies",
    }
    r = sess.get(f"https://api.twitter.com/2/users/{uid}/tweets", params=params, timeout=20)
    if r.status_code != 200:
        print(f"  X API {r.status_code} for {handle}: {r.text[:120]}", file=sys.stderr)
        return []
    data = r.json()
    media_map = {m["media_key"]: m for m in data.get("includes", {}).get("media", [])}
    out = []
    for t in data.get("data", []):
        photos = []
        for mk in t.get("attachments", {}).get("media_keys", []):
            m = media_map.get(mk)
            if m and m.get("type") == "photo":
                photos.append(m.get("url", ""))
        out.append({
            "id": t["id"], "text": t.get("text", ""),
            "created_at": t.get("created_at", ""), "photos": photos,
            "url": f"https://x.com/{handle}/status/{t['id']}",
        })
    return out


def pick_best(tweets):
    """Most recent original tweet with meaningful text.
    Skip tweets whose text is just a bare t.co link (renders as a naked URL
    in the card) in favor of one with real words; fall back to newest if all
    are link-only."""
    import re as _re
    def meaningful(t):
        txt = (t.get("text") or "").strip()
        if not txt:
            return False
        stripped = _re.sub(r'https?://\S+', '', txt).strip()
        return len(stripped) >= 15
    cands = [t for t in tweets if (t.get("text") or "").strip()]
    if not cands:
        return None
    cands.sort(key=lambda t: t.get("created_at", ""), reverse=True)
    for t in cands:
        if meaningful(t):
            return t
    return cands[0]


def main():
    leaders = json.load(open(LEADERS))

    # Load existing file to preserve real posts on API miss and to keep
    # the canonical handle list (current file has better handles than
    # pulse-leaders.json in a few cases).
    existing = {}
    existing_handle = {}
    try:
        cur = json.load(open(OUT))
        for x in cur.get("leaders", []):
            existing[x["name"]] = x.get("posts", [{}])[0] if x.get("posts") else {}
            existing_handle[x["name"]] = x.get("handle", "")
    except Exception:
        cur = {"leaders": []}

    out_leaders = []
    fresh = kept = placeheld = 0

    for ld in leaders:
        name = ld["name"]
        handle = HANDLE_OVERRIDE.get(name) or existing_handle.get(name) or ld["handle"]
        category = ld["category"]

        post = None
        try:
            tweets = fetch_latest_original(handle, max_results=10)
            best = pick_best(tweets) if tweets else None
            if best:
                ts = (best.get("created_at") or "")[:10] or datetime.now(timezone.utc).strftime("%Y-%m-%d")
                thumb = best["photos"][0] if best.get("photos") else ""
                post = {
                    "text": best["text"],
                    "caption": best["text"],
                    "url": best["url"],
                    "thumbnail": thumb,
                    "timestamp": ts,
                }
                fresh += 1
                print(f"  ✅ {category[:6].ljust(6)} {handle.ljust(20)} fresh: {best['text'][:60].replace(chr(10),' ')}")
        except Exception as e:
            print(f"  ⚠️  {handle}: {type(e).__name__} {str(e)[:100]}", file=sys.stderr)

        if post is None:
            prev = existing.get(name)
            if not is_placeholder(prev):
                post = prev
                kept += 1
                print(f"  ↩️  {category[:6].ljust(6)} {handle.ljust(20)} kept existing real post")
            else:
                post = {
                    "text": f"Follow @{handle} for the latest updates.",
                    "caption": f"Follow @{handle} for the latest updates.",
                    "url": f"https://x.com/{handle}",
                    "thumbnail": "",
                    "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                }
                placeheld += 1
                print(f"  ⬜ {category[:6].ljust(6)} {handle.ljust(20)} placeholder (no tweet, no prior)")

        out_leaders.append({
            "name": name,
            "handle": handle,
            "category": category,
            "platform": "x",
            "posts": [post],
        })
        time.sleep(0.4)  # gentle pacing

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    data = {"leaders": out_leaders, "lastUpdated": now, "last_updated": now}

    # Self-validation (same as cron contract)
    for leader in data["leaders"]:
        assert isinstance(leader.get("posts"), list) and leader["posts"], \
            f"SCHEMA BUG: {leader.get('name')} missing posts[]"
        assert leader["posts"][0].get("text"), \
            f"SCHEMA BUG: {leader.get('name')} empty text"

    if "--dry-run" in sys.argv:
        print(f"\nDRY RUN — fresh={fresh} kept={kept} placeholder={placeheld} total={len(out_leaders)}")
        return

    json.dump(data, open(OUT, "w"), ensure_ascii=False, indent=2)
    print(f"\n✅ Wrote {OUT}")
    print(f"   fresh={fresh} kept={kept} placeholder={placeheld} total={len(out_leaders)}")


if __name__ == "__main__":
    main()
