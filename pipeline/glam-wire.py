#!/usr/bin/env python3
"""Glam Wire — Instagram celebrity outing watcher + scorer (Phase 1: dry run).

Watches entertainment IG handles for fashion/outing moments, scores new posts
for glam-worthiness, writes candidates + a human-readable digest. No publishing.

Data sources, in priority order:
  1. Meta Business Discovery API (free, official) — needs META_IG_BUSINESS_ID
     + META_ACCESS_TOKEN in ~/workspace/.env.meta
  2. Apify instagram-post-scraper (fallback) — needs APIFY_API_TOKEN
  3. Fixture mode (no credentials) — scores sample posts so the pipeline is
     testable end-to-end without any token.

Usage:
  python3 -u glam-wire.py --dry-run    # default; prints digest, writes state
  python3 -u glam-wire.py --apply      # also writes candidates JSON for writer
"""
import argparse, json, os, re, subprocess, sys, time
from datetime import datetime, timezone

REPO = os.path.expanduser("~/workspace/the-videshi-news")
STATE_DIR = os.path.join(REPO, "pipeline", ".state")
SEEN_PATH = os.path.join(STATE_DIR, "glam-wire-seen.json")
CAND_PATH = os.path.join(STATE_DIR, "glam-wire-candidates.json")
os.makedirs(STATE_DIR, exist_ok=True)

GRAPH_VERSION = "v21.0"
RESULTS_PER_HANDLE = 5
SCORE_THRESHOLD = 7
MAX_CANDIDATES_PER_RUN = 4

# ---------------------------------------------------------------- env ----

def load_env(path):
    try:
        with open(os.path.expanduser(path)) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k, v)
    except FileNotFoundError:
        pass

load_env("~/workspace/.env.meta")
load_env("~/workspace/.env.apify")
load_env("~/workspace/.env.supabase")
load_env("~/workspace/.env.openai")

META_ID = os.environ.get("META_IG_BUSINESS_ID", "")
META_TOKEN = os.environ.get("META_ACCESS_TOKEN", "")
APIFY_TOKEN = os.environ.get("APIFY_API_TOKEN", "")
OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "")
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")

# ------------------------------------------------------------ handles ----

def load_handles(limit=60):
    """Entertainment IG handles from social_accounts."""
    if not (SUPABASE_URL and SUPABASE_KEY):
        print("  ⚠ Supabase not configured, using fallback handle list")
        return ["janhvikapoor", "aliaabhatt", "deepikapadukone", "ananyapanday",
                "kiaraaliaadvani", "saraalikhan95", "shanayakapoor02"]
    url = (f"{SUPABASE_URL}/rest/v1/social_accounts"
           "?select=handle&platform=eq.instagram&category=eq.entertainment"
           "&enabled=eq.true&limit=" + str(limit))
    r = subprocess.run(
        ["curl", "-sS", "-m", "30", url,
         "-H", f"apikey: {SUPABASE_KEY}",
         "-H", f"Authorization: Bearer {SUPABASE_KEY}"],
        capture_output=True, text=True, timeout=40)
    try:
        rows = json.loads(r.stdout or "[]")
        return [x["handle"].lower() for x in rows if x.get("handle")][:limit]
    except Exception as e:
        print(f"  ⚠ handle fetch failed: {e}")
        return []

# ------------------------------------------------------ Meta fetcher ----

def fetch_meta(handles):
    """Business Discovery: recent media for each handle. Returns {handle: [posts]}."""
    out = {}
    fields = ("business_discovery.username({h}){{username,followers_count,"
              "media.limit(%d){{id,caption,media_type,permalink,timestamp,"
              "like_count,comments_count}}}}" % RESULTS_PER_HANDLE)
    for h in handles:
        url = (f"https://graph.facebook.com/{GRAPH_VERSION}/{META_ID}"
               f"?fields={fields.format(h=h)}&access_token={META_TOKEN}")
        try:
            r = subprocess.run(["curl", "-sS", "-m", "30", url],
                               capture_output=True, text=True, timeout=40)
            data = json.loads(r.stdout or "{}")
            bd = data.get("business_discovery", {})
            posts = []
            for m in (bd.get("media", {}).get("data") or []):
                posts.append({
                    "id": m.get("id", ""),
                    "shortCode": (m.get("permalink", "").rstrip("/").split("/")[-1]),
                    "caption": m.get("caption", "") or "",
                    "timestamp": m.get("timestamp", ""),
                    "likesCount": m.get("like_count", 0),
                    "commentsCount": m.get("comments_count", 0),
                    "type": m.get("media_type", ""),
                    "url": m.get("permalink", ""),
                    "ownerUsername": h,
                    "source": "meta",
                })
            out[h] = posts
        except Exception as e:
            print(f"  ⚠ Meta fetch failed for @{h}: {e}")
        time.sleep(0.5)  # stay far under 200/hr
    return out

# ----------------------------------------------------- Apify fallback ----

def fetch_apify(handles):
    """Fallback: Apify instagram-post-scraper, batched. Returns {handle: [posts]}."""
    out = {}
    for i in range(0, len(handles), 10):
        batch = handles[i:i + 10]
        payload = json.dumps({"username": batch, "resultsLimit": RESULTS_PER_HANDLE})
        try:
            r = subprocess.run(
                ["curl", "-sS", "-X", "POST",
                 "https://api.apify.com/v2/acts/apify~instagram-post-scraper"
                 f"/run-sync-get-dataset-items?token={APIFY_TOKEN}",
                 "-H", "Content-Type: application/json", "-d", payload],
                capture_output=True, text=True, timeout=300)
            data = json.loads(r.stdout or "[]")
        except Exception as e:
            print(f"  ⚠ Apify batch failed: {e}")
            continue
        for item in data:
            if not isinstance(item, dict):
                continue
            owner = (item.get("ownerUsername") or "").lower()
            if not owner:
                m = re.search(r"instagram\.com/([^/]+)", item.get("inputUrl", ""))
                owner = m.group(1).lower() if m else ""
            if owner:
                out.setdefault(owner, []).append({
                    "id": item.get("id", ""),
                    "shortCode": item.get("shortCode", ""),
                    "caption": item.get("caption", "") or "",
                    "timestamp": item.get("timestamp", ""),
                    "likesCount": item.get("likesCount", 0),
                    "commentsCount": item.get("commentsCount", 0),
                    "type": item.get("type", ""),
                    "url": item.get("url", ""),
                    "ownerUsername": owner,
                    "source": "apify",
                })
    return out

# ------------------------------------------------------------- fixtures ----

FIXTURES = [
    {"ownerUsername": "janhvikapoor", "shortCode": "FIXgala001",
     "caption": "Paris nights in custom Pankaj S Heritage ivory muslin saree for the BoF 500 Gala. Styled by @rheakapoor ✨",
     "timestamp": "2026-10-04T20:00:00+00:00", "likesCount": 412000,
     "commentsCount": 3200, "type": "CAROUSEL_ALBUM",
     "url": "https://www.instagram.com/p/FIXgala001/", "source": "fixture"},
    {"ownerUsername": "aliaabhatt", "shortCode": "FIXairport002",
     "caption": "Airport diaries ✈️ comfy in @zara",
     "timestamp": "2026-10-04T08:00:00+00:00", "likesCount": 89000,
     "commentsCount": 400, "type": "IMAGE",
     "url": "https://www.instagram.com/p/FIXairport002/", "source": "fixture"},
    {"ownerUsername": "deepikapadukone", "shortCode": "FIXtbt003",
     "caption": "#throwback to Cannes 2022 ♥️",
     "timestamp": "2026-10-03T12:00:00+00:00", "likesCount": 200000,
     "commentsCount": 1500, "type": "IMAGE",
     "url": "https://www.instagram.com/p/FIXtbt003/", "source": "fixture"},
]

# ----------------------------------------------------------------- state ----

def load_seen():
    try:
        return json.load(open(SEEN_PATH))
    except Exception:
        return {}

def save_seen(seen):
    json.dump(seen, open(SEEN_PATH, "w"), indent=2)

# ----------------------------------------------------------------- scorer ----

SCORER_SYSTEM = """You are a fashion editor scoring Instagram posts for a celebrity glam wire (Indian diaspora audience).
Score 0-10: is this post a notable fashion/outing moment worth a short article?

8-10: red carpet, fashion week, awards, major event, striking editorial shoot
6-7:  airport look, vacation style, brand campaign with a strong look
3-5:  casual selfie, gym, food, throwback, meme, text quote card
0-2:  repost of someone else's content, ad without the person visible, irrelevant

Rules:
- The person must be visibly in an outfit (photo/reel, not text-only).
- Throwbacks (#throwback, #tbt) score 4 or less.
- Only name a designer if explicitly stated in the caption or tags — never guess.
- Be picky: a 7 means genuinely article-worthy, not merely nice.

Return JSON only: {"score": <int>, "reason": <string>, "event": <string or null>,
"designer": <string or null>, "outfit_visible": <bool>}"""

def score_post(post):
    if not OPENAI_KEY:
        # No-key heuristic fallback: keyword gate only
        cap = (post.get("caption") or "").lower()
        if re.search(r"#throwback|#tbt", cap):
            return {"score": 3, "reason": "throwback (heuristic)",
                    "event": None, "designer": None, "outfit_visible": True}
        hit = bool(re.search(
            r"gala|red carpet|fashion week|airport|shoot|campaign|couture|saree|gown",
            cap))
        return {"score": 7 if hit else 4,
                "reason": "keyword heuristic (no OpenAI key)",
                "event": None, "designer": None, "outfit_visible": True}
    user = (f"Handle: @{post['ownerUsername']}\n"
            f"Posted: {post.get('timestamp')}\n"
            f"Type: {post.get('type')}\n"
            f"Likes: {post.get('likesCount')}\n"
            f"Caption: {(post.get('caption') or '')[:600]}")
    payload = {
        "model": "gpt-4o-mini",
        "temperature": 0,
        "max_tokens": 200,
        "messages": [
            {"role": "system", "content": SCORER_SYSTEM},
            {"role": "user", "content": user},
        ],
    }
    try:
        r = subprocess.run(
            ["curl", "-sS", "-m", "30", "-X", "POST",
             "https://api.openai.com/v1/chat/completions",
             "-H", f"Authorization: Bearer {OPENAI_KEY}",
             "-H", "Content-Type: application/json",
             "-d", json.dumps(payload)],
            capture_output=True, text=True, timeout=40)
        text = json.loads(r.stdout or "{}")["choices"][0]["message"]["content"]
        m = re.search(r"\{.*\}", text, re.S)
        return json.loads(m.group(0)) if m else {"score": 0, "reason": "parse fail"}
    except Exception as e:
        return {"score": 0, "reason": f"scorer error: {e}"}

# ------------------------------------------------------------------- main ----

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", default=True)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--fixtures", action="store_true",
                    help="score built-in sample posts (tests scorer without tokens)")
    args = ap.parse_args()

    print("=== Glam Wire (Phase 1: dry run, no publishing) ===")
    handles = load_handles()
    print(f"  {len(handles)} entertainment handles tracked")

    if args.fixtures or not (META_ID and META_TOKEN or APIFY_TOKEN):
        if not args.fixtures:
            print("  ⚠ no Meta/Apify credentials — fixture mode (scorer test)")
        by_handle = {}
        for p in FIXTURES:
            by_handle.setdefault(p["ownerUsername"], []).append(p)
        source = "fixture"
    elif META_ID and META_TOKEN:
        print("  source: Meta Business Discovery (official)")
        by_handle = fetch_meta(handles)
        source = "meta"
    else:
        print("  source: Apify fallback")
        by_handle = fetch_apify(handles)
        source = "apify"

    seen = load_seen()
    new_posts, scored, candidates = 0, 0, []
    for h, posts in by_handle.items():
        known = set(seen.get(h, []))
        for p in posts:
            pid = p.get("shortCode") or p.get("id")
            if not pid or pid in known:
                continue
            new_posts += 1
            s = score_post(p)
            scored += 1
            known.add(pid)
            if s.get("score", 0) >= SCORE_THRESHOLD and len(candidates) < MAX_CANDIDATES_PER_RUN:
                candidates.append({
                    "handle": h,
                    "post_url": p.get("url"),
                    "permalink": p.get("url"),
                    "caption": (p.get("caption") or "")[:500],
                    "posted_at": p.get("timestamp"),
                    "likes": p.get("likesCount", 0),
                    "score": s.get("score"),
                    "score_reason": s.get("reason"),
                    "event": s.get("event"),
                    "designer": s.get("designer"),
                    "source": p.get("source", source),
                    "detected_at": datetime.now(timezone.utc).isoformat(),
                })
        seen[h] = sorted(known)[-50:]  # keep last 50 ids per handle
    save_seen(seen)

    print(f"\n  {new_posts} new posts, {scored} scored, "
          f"{len(candidates)} candidates (threshold {SCORE_THRESHOLD}/10)")
    print("\n── Digest ──────────────────────────────")
    if not candidates:
        print("  (no glam-worthy posts this run)")
    for c in candidates:
        print(f"  ★ {c['score']}/10  @{c['handle']} — {c['score_reason']}")
        if c["event"]:
            print(f"      event: {c['event']}")
        if c["designer"]:
            print(f"      designer: {c['designer']} (from caption)")
        print(f"      {c['post_url']}")

    if args.apply and candidates:
        json.dump({"generated_at": datetime.now(timezone.utc).isoformat(),
                   "candidates": candidates},
                  open(CAND_PATH, "w"), indent=2, ensure_ascii=False)
        print(f"\n  wrote {CAND_PATH}")
    print("=== done (dry run — nothing published) ===")

if __name__ == "__main__":
    main()
