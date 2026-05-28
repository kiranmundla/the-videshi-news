#!/usr/bin/env python3
"""Post recent Videshi articles to Threads (@the.videshi)."""

import json, os, sys, time, requests
from datetime import datetime

# --- Config ---
THREADS_USER_ID = "26854521280856098"
SUPABASE_URL = "https://lboecaekpynbpyijrbfz.supabase.co"
LOG_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/threads-log.json")

# Load env
def load_env(path):
    env = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip()
    return env

threads_env = load_env("~/workspace/.env.threads")
supa_env = load_env("~/workspace/.env.supabase")

THREADS_ACCESS_TOKEN = threads_env["THREADS_ACCESS_TOKEN"]
SUPABASE_KEY = supa_env["SUPABASE_SERVICE_ROLE_KEY"]

# Category emoji map
EMOJI = {
    "news": "🇮🇳", "immigration": "🛂", "nri-world": "🌏",
    "travel": "✈️", "lifestyle-health": "🧘", "markets-finance": "📈",
    "technology": "💻", "sports": "🏏", "entertainment": "🎬", "food": "🍛",
}

# --- Load tracking log ---
if os.path.exists(LOG_PATH):
    with open(LOG_PATH) as f:
        threads_log = json.load(f)
else:
    threads_log = {}

# --- Fetch recent articles ---
headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
}
resp = requests.get(
    f"{SUPABASE_URL}/rest/v1/p2_articles",
    params={
        "status": "eq.published",
        "order": "published_at.desc",
        "limit": "10",
        "select": "id,slug,headline,subheadline,category,image_url,body",
    },
    headers=headers,
)
resp.raise_for_status()
articles = resp.json()
print(f"Fetched {len(articles)} recent published articles")

# Filter: not yet posted, has image_url
candidates = []
for a in articles:
    aid = str(a["id"])
    if aid in threads_log:
        continue
    if not a.get("image_url"):
        print(f"  Skipping {a['slug']} — no image_url")
        continue
    candidates.append(a)

candidates = candidates[:3]
print(f"Will post {len(candidates)} articles to Threads")

if not candidates:
    print("Nothing to post.")
    sys.exit(0)


def compose_post(article):
    """Compose a Threads post matching X style, within 500 chars."""
    cat = (article.get("category") or "news").lower()
    emoji = EMOJI.get(cat, "📰")
    cat_display = cat.upper().replace("-", " ")
    slug = article["slug"]
    headline = article["headline"]
    body = article.get("body") or ""
    subheadline = article.get("subheadline") or ""

    # Build punchy headline (ALL CAPS) — use the headline but punch it up
    punchy = headline.upper()

    # Build summary — use subheadline if good, else first meaningful sentence from body
    summary = ""
    if subheadline and len(subheadline) > 20:
        summary = subheadline
    else:
        # Extract from body — find first real sentence
        sentences = []
        for line in body.split("\n"):
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("![") or line.startswith("*"):
                continue
            # Split into sentences
            for s in line.split(". "):
                s = s.strip().rstrip(".")
                if len(s) > 30:
                    sentences.append(s + ".")
                    break
            if sentences:
                break
        summary = sentences[0] if sentences else subheadline

    url = f"📰 thevideshi.com/articles/{slug}"
    header = f"{emoji} {cat_display} | The Videshi"
    sep = "━━━━━━━━━━━━━━━━━━━━"

    post = f"{header}\n\n{sep}\n\n{punchy}\n\n{summary}\n\n{url}"

    # Trim if over 500 chars
    if len(post) > 500:
        # Shorten summary
        avail = 500 - len(header) - len(sep) - len(punchy) - len(url) - 10  # 10 for newlines
        if avail > 20:
            summary = summary[:avail-3].rsplit(" ", 1)[0] + "..."
        else:
            summary = ""
        post = f"{header}\n\n{sep}\n\n{punchy}\n\n{summary}\n\n{url}" if summary else f"{header}\n\n{sep}\n\n{punchy}\n\n{url}"

    return post[:500]


def post_to_threads(text, image_url):
    """Two-step Threads publish: create container, then publish."""
    # Step 1: Create media container
    container_data = {
        "media_type": "IMAGE",
        "image_url": image_url,
        "text": text,
        "access_token": THREADS_ACCESS_TOKEN,
    }
    resp = requests.post(
        f"https://graph.threads.net/v1.0/{THREADS_USER_ID}/threads",
        data=container_data,
    )

    if resp.status_code != 200 or "id" not in resp.json():
        print(f"  Image container failed ({resp.status_code}): {resp.text}")
        print("  Falling back to TEXT-only post...")
        container_data = {
            "media_type": "TEXT",
            "text": text,
            "access_token": THREADS_ACCESS_TOKEN,
        }
        resp = requests.post(
            f"https://graph.threads.net/v1.0/{THREADS_USER_ID}/threads",
            data=container_data,
        )
        if resp.status_code != 200 or "id" not in resp.json():
            return None, f"Text fallback also failed: {resp.status_code} {resp.text}"

    container_id = resp.json()["id"]
    print(f"  Container created: {container_id}")

    # Step 2: Wait for processing then publish
    time.sleep(12)

    resp = requests.post(
        f"https://graph.threads.net/v1.0/{THREADS_USER_ID}/threads_publish",
        data={
            "creation_id": container_id,
            "access_token": THREADS_ACCESS_TOKEN,
        },
    )

    if resp.status_code != 200 or "id" not in resp.json():
        return None, f"Publish failed: {resp.status_code} {resp.text}"

    post_id = resp.json()["id"]
    return post_id, None


# --- Post articles ---
posted = 0
errors = []

for i, article in enumerate(candidates):
    slug = article["slug"]
    aid = str(article["id"])
    print(f"\n[{i+1}/{len(candidates)}] Posting: {slug}")

    text = compose_post(article)
    print(f"  Post text ({len(text)} chars):")
    for line in text.split("\n"):
        print(f"    {line}")

    post_id, err = post_to_threads(text, article["image_url"])

    if err:
        print(f"  ERROR: {err}")
        errors.append({"slug": slug, "error": err})
        continue

    print(f"  Published! Post ID: {post_id}")

    # Update log
    threads_log[aid] = {
        "slug": slug,
        "threads_post_id": str(post_id),
        "posted_at": datetime.utcnow().isoformat() + "Z",
    }
    with open(LOG_PATH, "w") as f:
        json.dump(threads_log, f, indent=2)

    posted += 1

    # Wait between posts
    if i < len(candidates) - 1:
        print("  Waiting 10s before next post...")
        time.sleep(10)

# --- Summary ---
print(f"\n{'='*40}")
print(f"SUMMARY: {posted} posted, {len(errors)} errors")
if errors:
    for e in errors:
        print(f"  Error: {e['slug']} — {e['error']}")
print(f"Total in threads-log.json: {len(threads_log)}")
