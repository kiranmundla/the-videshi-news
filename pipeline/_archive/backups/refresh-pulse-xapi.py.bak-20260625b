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
try:
    import x_spend
except Exception:
    x_spend = None
from datetime import datetime, timezone, timedelta

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
    raw = data.get("data", [])
    if x_spend and raw:
        x_spend.add(reads=len(raw))
    media_map = {m["media_key"]: m for m in data.get("includes", {}).get("media", [])}
    out = []
    for t in raw:
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


def post_from_tweet(t, handle):
    """Convert a raw tweet dict into a publishable Pulse post (the bits the
    tile renders). Carries the tweet id so rotation can guarantee no repeats."""
    ts = (t.get("created_at") or "")[:10] or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    thumb = t["photos"][0] if t.get("photos") else ""
    return {
        "id": t.get("id", ""),
        "text": t.get("text", ""),
        "caption": t.get("text", ""),
        "url": t.get("url", f"https://x.com/{handle}"),
        "thumbnail": thumb,
        "timestamp": ts,
    }


def build_pool(tweets, handle, window_days=10, keep=5):
    """From the fetched tweets, keep the publishable subset for free daily
    rotation. Prefer meaningful tweets within a recency window so an inactive
    account doesn't surface months-old posts; if none qualify, fall back to
    the newest meaningful one. De-duped by tweet id so the same tweet can
    never appear twice in a leader's rotation."""
    import re as _re
    def meaningful(t):
        txt = (t.get("text") or "").strip()
        if not txt:
            return False
        return len(_re.sub(r'https?://\S+', '', txt).strip()) >= 15
    cands = [t for t in tweets if meaningful(t)]
    cands.sort(key=lambda t: t.get("created_at", ""), reverse=True)
    cutoff = (datetime.now(timezone.utc) - timedelta(days=window_days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    recent = [t for t in cands if (t.get("created_at") or "") >= cutoff]
    chosen = recent if recent else cands[:1]   # if nothing recent, just hold newest
    pool, seen = [], set()
    for t in chosen:
        tid = t.get("id", "")
        if tid and tid in seen:
            continue
        seen.add(tid)
        pool.append(post_from_tweet(t, handle))
        if len(pool) >= keep:
            break
    return pool


def main():
    leaders = json.load(open(LEADERS))

    # Load existing file to preserve real posts on API miss and to keep
    # the canonical handle list (current file has better handles than
    # pulse-leaders.json in a few cases).
    existing = {}
    existing_handle = {}
    last_ref = {}
    pools = {}
    pool_idxs = {}
    try:
        cur = json.load(open(OUT))
        for x in cur.get("leaders", []):
            existing[x["name"]] = x.get("posts", [{}])[0] if x.get("posts") else {}
            existing_handle[x["name"]] = x.get("handle", "")
            last_ref[x["name"]] = x.get("last_refreshed", "")
            pools[x["name"]] = x.get("pool", [])
            pool_idxs[x["name"]] = x.get("pool_idx", 0)
    except Exception:
        cur = {"leaders": []}

    # --- ROTATION: only refresh the N most-stale leaders per run (budget cap) ---
    # All 52 tiles stay live; each refreshes ~every ceil(52/N) runs.
    REFRESH_PER_RUN = int(os.environ.get("PULSE_REFRESH_PER_RUN", "13"))
    leaders_sorted = sorted(leaders, key=lambda L: last_ref.get(L["name"], ""))
    due = set(id(L) for L in leaders_sorted[:REFRESH_PER_RUN])
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    out_leaders = []
    fresh = kept = placeheld = rotated = 0

    if x_spend and x_spend.over_budget():
        print(f"X-BUDGET ceiling reached ({x_spend.status_line()}); skipping pulse refresh (keeping existing tiles).")
        return

    for ld in leaders:
        name0 = ld["name"]; h0 = HANDLE_OVERRIDE.get(name0) or existing_handle.get(name0) or ld["handle"]
        # Not in this run's rotation OR over budget -> NO API call.
        # Rotate the displayed tweet through this leader's stored pool (free),
        # so the tile still changes daily even without a fresh fetch.
        if id(ld) not in due or (x_spend and x_spend.over_budget()):
            pool = pools.get(name0, [])
            cur_post = existing.get(name0) or {}
            if len(pool) > 1:
                start = pool_idxs.get(name0, 0)
                cur_id = cur_post.get("id", "")
                idx = start
                # step forward to the next entry that isn't the one on screen
                for step in range(1, len(pool) + 1):
                    cand = (start + step) % len(pool)
                    if pool[cand].get("id", "") != cur_id:
                        idx = cand
                        break
                post = pool[idx]
                rotated += 1
            elif pool:
                idx = 0
                post = pool[0]
            else:
                idx = 0
                post = cur_post or None
            out_leaders.append({"name": name0, "handle": h0, "category": ld["category"],
                                "platform": "x", "posts": [post] if post else [],
                                "last_refreshed": last_ref.get(name0, ""),
                                "pool": pool, "pool_idx": idx})
            kept += 1
            continue
        name = ld["name"]
        handle = HANDLE_OVERRIDE.get(name) or existing_handle.get(name) or ld["handle"]
        category = ld["category"]

        post = None
        new_pool = []
        try:
            tweets = fetch_latest_original(handle, max_results=5)
            best = pick_best(tweets) if tweets else None
            if best:
                post = post_from_tweet(best, handle)
                new_pool = build_pool(tweets, handle)
                fresh += 1
                print(f"  ✅ {category[:6].ljust(6)} {handle.ljust(20)} fresh: {best['text'][:60].replace(chr(10),' ')}  (pool={len(new_pool)})")
        except Exception as e:
            print(f"  ⚠️  {handle}: {type(e).__name__} {str(e)[:100]}", file=sys.stderr)

        if post is None:
            prev = existing.get(name)
            if not is_placeholder(prev):
                post = prev
                new_pool = pools.get(name, [])  # keep whatever pool we had
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
            "last_refreshed": now_iso,
            "pool": new_pool if new_pool else [post],
            "pool_idx": 0,
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
        print(f"\nDRY RUN — fresh={fresh} kept={kept} rotated={rotated} placeholder={placeheld} total={len(out_leaders)}")
        return

    json.dump(data, open(OUT, "w"), ensure_ascii=False, indent=2)
    print(f"\n✅ Wrote {OUT}")
    print(f"   fresh={fresh} kept={kept} rotated={rotated} placeholder={placeheld} total={len(out_leaders)}")


if __name__ == "__main__":
    main()
