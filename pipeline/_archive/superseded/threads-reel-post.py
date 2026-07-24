#!/usr/bin/env python3
"""Post video reels from prebuilt_reels table to Threads (@the.videshi)."""

import os, sys, json, time, requests
from datetime import datetime, timezone

# --- Config ---
THREADS_USER_ID = "26854521280856098"
SUPABASE_URL = "https://lboecaekpynbpyijrbfz.supabase.co"
MAX_POSTS = 2
MAX_TEXT = 500

# Load env
def load_env(path):
    env = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env

threads_env = load_env("~/workspace/.env.threads")
supa_env = load_env("~/workspace/.env.supabase")

THREADS_ACCESS_TOKEN = threads_env["THREADS_ACCESS_TOKEN"]
SUPABASE_KEY = supa_env["SUPABASE_SERVICE_ROLE_KEY"]

supa_headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

# --- 1. Fetch pending reels ---
print("Fetching pending reels from prebuilt_reels...")
resp = requests.get(
    f"{SUPABASE_URL}/rest/v1/prebuilt_reels",
    params={
        "qa_passed": "eq.true",
        "threads_posted_at": "is.null",
        "order": "created_at.desc",
        "limit": "3",
        "select": "id,article_id,article_slug,headline,video_path,video_url,caption"
    },
    headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
)

if resp.status_code != 200:
    print(f"❌ Failed to fetch reels: {resp.status_code} {resp.text}")
    sys.exit(1)

reels = resp.json()
print(f"Found {len(reels)} pending reel(s)")

if not reels:
    print("No pending reels to post. Done.")
    sys.exit(0)

for r in reels[:3]:
    print(f"  - {r['id'][:8]}... | {r.get('headline','')[:60]} | video_url: {bool(r.get('video_url'))}")

# --- 2. Post up to MAX_POSTS ---
posted = []
errors = []
log_path = os.path.expanduser("~/workspace/the-videshi-news/pipeline/threads-log.json")

# Load existing log
try:
    with open(log_path) as f:
        log_data = json.load(f)
except:
    log_data = {}

for i, reel in enumerate(reels[:MAX_POSTS]):
    reel_id = reel["id"]
    headline = reel.get("headline", "")
    caption = reel.get("caption", "")
    slug = reel.get("article_slug", "")
    video_url = reel.get("video_url")

    if not video_url:
        print(f"⚠️  Reel {reel_id[:8]} has no video_url, skipping")
        errors.append({"id": reel_id, "error": "no video_url"})
        continue

    # Compose post text
    link = f"📰 thevideshi.com/articles/{slug}" if slug else ""
    prefix = f"🎬 {headline}\n\n"
    suffix = f"\n\n{link}" if link else ""
    budget = MAX_TEXT - len(prefix) - len(suffix)
    trimmed_caption = caption[:budget] if len(caption) > budget else caption
    post_text = f"{prefix}{trimmed_caption}{suffix}".strip()

    print(f"\n--- Posting reel {i+1}/{min(len(reels), MAX_POSTS)}: {reel_id[:8]} ---")
    print(f"  Headline: {headline[:80]}")
    print(f"  Video URL: {video_url[:100]}")
    print(f"  Text length: {len(post_text)} chars")

    try:
        # Step 1: Create video container
        print("  Step 1: Creating video container...")
        container_resp = requests.post(
            f"https://graph.threads.net/v1.0/{THREADS_USER_ID}/threads",
            data={
                "media_type": "VIDEO",
                "video_url": video_url,
                "text": post_text,
                "access_token": THREADS_ACCESS_TOKEN
            }
        )
        print(f"  Container response: {container_resp.status_code} {container_resp.text[:300]}")
        
        if container_resp.status_code != 200:
            errors.append({"id": reel_id, "error": f"container creation failed: {container_resp.status_code} {container_resp.text[:200]}"})
            continue

        container_data = container_resp.json()
        container_id = container_data.get("id")
        if not container_id:
            errors.append({"id": reel_id, "error": f"no container id: {container_data}"})
            continue

        print(f"  Container ID: {container_id}")

        # Step 2: Poll for video processing
        print("  Step 2: Waiting for video processing...")
        video_ready = False
        for attempt in range(30):  # Max ~5 min
            time.sleep(10)
            status_resp = requests.get(
                f"https://graph.threads.net/v1.0/{container_id}",
                params={"fields": "status,error_message", "access_token": THREADS_ACCESS_TOKEN}
            )
            status_data = status_resp.json()
            status = status_data.get("status", "UNKNOWN")
            print(f"    Poll {attempt+1}: {status}")

            if status == "FINISHED":
                video_ready = True
                break
            elif status == "ERROR":
                err_msg = status_data.get("error_message", "unknown error")
                print(f"  ❌ Video processing failed: {err_msg}")
                errors.append({"id": reel_id, "error": f"processing error: {err_msg}", "status_data": str(status_data)[:300]})
                break

        if not video_ready:
            if not any(e["id"] == reel_id for e in errors):
                errors.append({"id": reel_id, "error": "timeout waiting for video processing"})
            continue

        # Step 3: Publish
        print("  Step 3: Publishing...")
        pub_resp = requests.post(
            f"https://graph.threads.net/v1.0/{THREADS_USER_ID}/threads_publish",
            data={
                "creation_id": container_id,
                "access_token": THREADS_ACCESS_TOKEN
            }
        )
        print(f"  Publish response: {pub_resp.status_code} {pub_resp.text[:300]}")

        if pub_resp.status_code != 200:
            errors.append({"id": reel_id, "error": f"publish failed: {pub_resp.status_code} {pub_resp.text[:200]}"})
            continue

        post_id = pub_resp.json().get("id", "")
        now_utc = datetime.now(timezone.utc).isoformat()
        print(f"  ✅ Published! Post ID: {post_id}")

        # Step 4: Update Supabase
        print("  Updating Supabase...")
        patch_resp = requests.patch(
            f"{SUPABASE_URL}/rest/v1/prebuilt_reels?id=eq.{reel_id}",
            headers=supa_headers,
            json={"threads_post_id": str(post_id), "threads_posted_at": now_utc}
        )
        print(f"  Supabase update: {patch_resp.status_code}")

        posted.append({"id": reel_id, "post_id": post_id, "headline": headline})

        # Step 5: Log
        log_data[str(post_id)] = {
            "reel_id": reel_id,
            "headline": headline,
            "slug": slug,
            "platform": "threads",
            "type": "video_reel",
            "posted_at": now_utc,
            "video_url": video_url
        }

        # Wait between posts
        if i < min(len(reels), MAX_POSTS) - 1:
            print("  Waiting 15s before next post...")
            time.sleep(15)

    except Exception as e:
        print(f"  ❌ Exception: {e}")
        errors.append({"id": reel_id, "error": str(e)})

# Save log
with open(log_path, "w") as f:
    json.dump(log_data, f, indent=2)

# --- Summary ---
print(f"\n{'='*50}")
print(f"SUMMARY")
print(f"  Posted: {len(posted)}")
for p in posted:
    print(f"    ✅ {p['id'][:8]} → {p['post_id']} | {p['headline'][:60]}")
print(f"  Errors: {len(errors)}")
for e in errors:
    print(f"    ❌ {e['id'][:8]}: {e['error'][:100]}")
print(f"{'='*50}")
