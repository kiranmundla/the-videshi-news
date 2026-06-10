#!/usr/bin/env python3
"""Post prebuilt video reels to Threads (@the.videshi)."""

import requests
import json
import time
import os
from datetime import datetime, timezone

# --- Config ---
THREADS_ACCESS_TOKEN = os.environ["THREADS_ACCESS_TOKEN"]
THREADS_USER_ID = "26854521280856098"
SUPABASE_URL = "https://lboecaekpynbpyijrbfz.supabase.co"
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
LOG_FILE = os.path.expanduser("~/workspace/the-videshi-news/pipeline/threads-log.json")

sb_headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}

# Load existing log
if os.path.exists(LOG_FILE):
    with open(LOG_FILE) as f:
        log = json.load(f)
else:
    log = {}

# --- Fetch pending reels ---
resp = requests.get(
    f"{SUPABASE_URL}/rest/v1/prebuilt_reels",
    params={
        "qa_passed": "eq.true",
        "threads_posted_at": "is.null",
        "order": "created_at.desc",
        "limit": "3",
        "select": "id,article_id,article_slug,headline,video_path,video_url,caption,created_at",
    },
    headers=sb_headers,
)
resp.raise_for_status()
reels = resp.json()
print(f"Found {len(reels)} pending reels")

if not reels:
    print("Nothing to post.")
    exit(0)

# Deduplicate by article_slug — keep only the newest per slug
seen_slugs = {}
for r in reels:
    slug = r["article_slug"]
    if slug not in seen_slugs:
        seen_slugs[slug] = {"post": r, "dupes": []}
    else:
        seen_slugs[slug]["dupes"].append(r)

# We'll post up to 2 unique articles
to_post = []
dupe_ids = []
for slug, info in seen_slugs.items():
    to_post.append(info["post"])
    for d in info["dupes"]:
        dupe_ids.append(d["id"])
    if len(to_post) >= 2:
        break

print(f"Will post {len(to_post)} reel(s), marking {len(dupe_ids)} duplicate(s) as skipped")

posted_count = 0
errors = []

for reel in to_post:
    reel_id = reel["id"]
    headline = reel["headline"]
    slug = reel["article_slug"]
    video_url = reel["video_url"]
    
    # Compose post text (max 500 chars)
    link = f"📰 thevideshi.com/articles/{slug}"
    prefix = f"🎬 {headline}\n\n"
    suffix = f"\n\n{link}"
    
    # Use the caption field but trim the existing URL and hashtags since we format our own
    raw_caption = reel.get("caption") or ""
    # Extract just the summary part (between headline and "Full story:" or hashtags)
    caption_lines = raw_caption.split("\n")
    summary_lines = []
    for line in caption_lines:
        line_s = line.strip()
        if line_s.startswith("Full story:") or line_s.startswith("#") or line_s.startswith("📰"):
            continue
        if line_s == headline:
            continue
        if line_s:
            summary_lines.append(line_s)
    summary = " ".join(summary_lines) if summary_lines else ""
    
    max_summary = 500 - len(prefix) - len(suffix)
    if len(summary) > max_summary:
        summary = summary[:max_summary - 3] + "..."
    
    post_text = f"{prefix}{summary}{suffix}"
    print(f"\n--- Posting reel {reel_id[:8]}... ---")
    print(f"  Headline: {headline[:70]}")
    print(f"  Video URL: {video_url[:80]}")
    print(f"  Post text ({len(post_text)} chars)")
    
    # Step 1: Create video container
    try:
        container_resp = requests.post(
            f"https://graph.threads.net/v1.0/{THREADS_USER_ID}/threads",
            data={
                "media_type": "VIDEO",
                "video_url": video_url,
                "text": post_text,
                "access_token": THREADS_ACCESS_TOKEN,
            },
        )
        print(f"  Container response: {container_resp.status_code} {container_resp.text[:200]}")
        container_resp.raise_for_status()
        container_id = container_resp.json()["id"]
        print(f"  Container ID: {container_id}")
    except Exception as e:
        err = f"Container creation failed for {reel_id[:8]}: {e}"
        print(f"  ❌ {err}")
        errors.append(err)
        continue
    
    # Step 2: Poll for video processing
    print("  Waiting for video processing...")
    processing_ok = False
    for i in range(30):  # Max ~5 min
        time.sleep(10)
        try:
            status_resp = requests.get(
                f"https://graph.threads.net/v1.0/{container_id}",
                params={"fields": "status", "access_token": THREADS_ACCESS_TOKEN},
            )
            status_data = status_resp.json()
            status = status_data.get("status", "UNKNOWN")
            print(f"  Poll {i+1}: {status}")
            if status == "FINISHED":
                processing_ok = True
                break
            elif status == "ERROR":
                err = f"Video processing error for {reel_id[:8]}: {status_data}"
                print(f"  ❌ {err}")
                errors.append(err)
                break
        except Exception as e:
            print(f"  Poll error: {e}")
    
    if not processing_ok:
        if not any(reel_id[:8] in e for e in errors):
            errors.append(f"Video processing timed out for {reel_id[:8]}")
        continue
    
    # Step 3: Publish
    try:
        pub_resp = requests.post(
            f"https://graph.threads.net/v1.0/{THREADS_USER_ID}/threads_publish",
            data={
                "creation_id": container_id,
                "access_token": THREADS_ACCESS_TOKEN,
            },
        )
        print(f"  Publish response: {pub_resp.status_code} {pub_resp.text[:200]}")
        pub_resp.raise_for_status()
        post_id = pub_resp.json()["id"]
        print(f"  ✅ Published! Post ID: {post_id}")
    except Exception as e:
        err = f"Publish failed for {reel_id[:8]}: {e}"
        print(f"  ❌ {err}")
        errors.append(err)
        continue
    
    # Step 4: Update Supabase
    now_utc = datetime.now(timezone.utc).isoformat()
    patch_resp = requests.patch(
        f"{SUPABASE_URL}/rest/v1/prebuilt_reels?id=eq.{reel_id}",
        headers=sb_headers,
        json={"threads_post_id": str(post_id), "threads_posted_at": now_utc},
    )
    print(f"  Supabase update: {patch_resp.status_code}")
    
    # Step 5: Log
    log[str(post_id)] = {
        "type": "video_reel",
        "reel_id": reel_id,
        "headline": headline,
        "slug": slug,
        "threads_post_id": str(post_id),
        "posted_at": now_utc,
    }
    
    posted_count += 1
    
    # Wait between posts
    if to_post.index(reel) < len(to_post) - 1:
        print("  Waiting 15s before next post...")
        time.sleep(15)

# Mark duplicates as skipped
if dupe_ids:
    now_utc = datetime.now(timezone.utc).isoformat()
    for did in dupe_ids:
        patch_resp = requests.patch(
            f"{SUPABASE_URL}/rest/v1/prebuilt_reels?id=eq.{did}",
            headers=sb_headers,
            json={"threads_post_id": "skipped-duplicate", "threads_posted_at": now_utc},
        )
        print(f"Marked duplicate {did[:8]} as skipped: {patch_resp.status_code}")

# Save log
with open(LOG_FILE, "w") as f:
    json.dump(log, f, indent=2)

print(f"\n=== SUMMARY ===")
print(f"Posted: {posted_count}")
print(f"Duplicates skipped: {len(dupe_ids)}")
print(f"Errors: {len(errors)}")
for e in errors:
    print(f"  - {e}")
