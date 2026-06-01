#!/usr/bin/env python3
"""One-shot: Upload the fixed RCB IPL 2026 reel to Instagram."""

import os
import re
import sys
import json
import time
import requests
from datetime import datetime, timezone

def load_env_file(path):
    env = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' not in line:
                continue
            k, v = line.split('=', 1)
            v = v.strip().strip('"').strip("'")
            env[k] = v
    return env

ig_env = load_env_file("~/workspace/.env.instagram")
sb_env = load_env_file("~/workspace/.env.supabase")

IG_USER_ID = ig_env["INSTAGRAM_USER_ID"]
TOKEN = ig_env["INSTAGRAM_ACCESS_TOKEN"]
SB_SERVICE_KEY = sb_env["SUPABASE_SERVICE_ROLE_KEY"]
SUPABASE_URL = "https://lboecaekpynbpyijrbfz.supabase.co"

ARTICLE_ID = "64a73793-9f17-437f-9c54-d73c50660f82"
ARTICLE_SLUG = "rcb-ipl-2026-champions-back-to-back-dynasty-kohli-sooryavanshi-editorial"
ARTICLE_HEADLINE = "From Memes to Monarchy: RCB's Dynasty Has Arrived"

REEL_FILE = os.path.expanduser("~/workspace/the-videshi-news/pipeline/reels/reel-rcb-ipl-2026-champions-back-to-back-dynasty-kohli-sooryavanshi-editorial-20260531.mp4")
COVER_FILE = os.path.expanduser("~/workspace/the-videshi-news/pipeline/reels/reel-rcb-ipl-2026-champions-back-to-back-dynasty-kohli-sooryavanshi-editorial-20260531-cover.jpg")

SB_HEADERS = {
    "apikey": SB_SERVICE_KEY,
    "Authorization": f"Bearer {SB_SERVICE_KEY}",
}

# ── Step 0: Refresh IG token ──────────────────────────────────────
print("=== Refreshing Instagram token ===")
try:
    r = requests.get("https://graph.instagram.com/refresh_access_token", params={
        "grant_type": "ig_refresh_token",
        "access_token": TOKEN
    }, timeout=15)
    rj = r.json()
    if 'access_token' in rj:
        new_token = rj['access_token']
        if new_token != TOKEN:
            TOKEN = new_token
            ig_env["INSTAGRAM_ACCESS_TOKEN"] = TOKEN
            with open(os.path.expanduser("~/workspace/.env.instagram"), 'w') as f:
                for k, v in ig_env.items():
                    f.write(f"{k}={v}\n")
            print(f"Token refreshed (expires in {rj.get('expires_in', '?')}s)")
        else:
            print(f"Token unchanged (expires in {rj.get('expires_in', '?')}s)")
    else:
        print(f"Token refresh response: {rj}")
except Exception as e:
    print(f"Token refresh failed (non-fatal): {e}")

# ── Step 1: Upload reel video to Supabase storage ────────────────
print("\n=== Uploading reel video to Supabase storage ===")
reel_storage_path = f"reels/{ARTICLE_SLUG}-20260531.mp4"

with open(REEL_FILE, 'rb') as f:
    reel_data = f.read()
print(f"Reel file size: {len(reel_data):,} bytes")

r = requests.post(
    f"{SUPABASE_URL}/storage/v1/object/article-images/{reel_storage_path}",
    headers={
        **SB_HEADERS,
        "Content-Type": "video/mp4",
        "x-upsert": "true"
    },
    data=reel_data,
    timeout=60
)
print(f"Upload response: {r.status_code} {r.text[:200]}")
if r.status_code not in (200, 201):
    print("ERROR: Reel upload failed")
    sys.exit(1)

reel_public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{reel_storage_path}"
print(f"Reel public URL: {reel_public_url}")

# Verify the URL is accessible
r_check = requests.head(reel_public_url, timeout=10)
print(f"URL check: {r_check.status_code}, Content-Type: {r_check.headers.get('Content-Type')}, Size: {r_check.headers.get('Content-Length')}")

# ── Step 2: Upload cover image to Supabase storage ───────────────
print("\n=== Uploading cover image to Supabase storage ===")
cover_storage_path = f"reels/{ARTICLE_SLUG}-20260531-cover.jpg"
cover_public_url = None

if os.path.exists(COVER_FILE):
    with open(COVER_FILE, 'rb') as f:
        cover_data = f.read()
    r = requests.post(
        f"{SUPABASE_URL}/storage/v1/object/article-images/{cover_storage_path}",
        headers={
            **SB_HEADERS,
            "Content-Type": "image/jpeg",
            "x-upsert": "true"
        },
        data=cover_data,
        timeout=30
    )
    if r.status_code in (200, 201):
        cover_public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{cover_storage_path}"
        print(f"Cover uploaded: {cover_public_url}")
    else:
        print(f"Cover upload failed (non-fatal): {r.status_code} {r.text[:200]}")
else:
    print("No cover file found, will skip cover_url")

# ── Step 3: Build caption ────────────────────────────────────────
caption = f"""{ARTICLE_HEADLINE}

🏏 RCB goes back-to-back! Kohli's 75* off 42, Rasikh's 3 wickets, and Vaibhav Sooryavanshi's record-breaking 72 sixes. The dynasty is real.

📰 Full story: https://thevideshi.com/articles/{ARTICLE_SLUG}

#IPL #IPL2026 #RCB #RCBChampions #ViratKohli #Kohli #Cricket #IndianCricket #BCCI #CricketNews #IPLFinal #RoyalChallengersBengaluru #VaibhavSooryavanshi #BackToBack #TheVideshi #Reels"""

print(f"\nCaption:\n{caption}\n")

# ── Step 4: Create Reel container on Instagram ───────────────────
print("=== Creating Instagram Reel container ===")
container_data = {
    "video_url": reel_public_url,
    "media_type": "REELS",
    "caption": caption,
    "access_token": TOKEN
}
if cover_public_url:
    container_data["cover_url"] = cover_public_url

r = requests.post(
    f"https://graph.instagram.com/v25.0/{IG_USER_ID}/media",
    data=container_data,
    timeout=30
)
rj = r.json()
print(f"Container response: {rj}")

if 'id' not in rj:
    print(f"ERROR: Container creation failed: {rj}")
    sys.exit(1)

container_id = rj['id']
print(f"Container ID: {container_id}")

# ── Step 5: Wait for video processing ────────────────────────────
print("\n=== Waiting for video processing ===")
finished = False
for i in range(24):  # Up to 2 minutes
    time.sleep(5)
    r_status = requests.get(
        f"https://graph.instagram.com/v25.0/{container_id}",
        params={"fields": "status_code", "access_token": TOKEN},
        timeout=15
    )
    status = r_status.json().get('status_code', 'UNKNOWN')
    print(f"  Poll {i+1}/24: {status}")
    if status == 'FINISHED':
        finished = True
        break
    elif status == 'ERROR':
        print(f"ERROR: Video processing failed: {r_status.json()}")
        sys.exit(1)

if not finished:
    print("WARNING: Video processing didn't finish in 2 min, attempting publish anyway")

# ── Step 6: Publish the Reel ─────────────────────────────────────
print("\n=== Publishing Reel ===")
r2 = requests.post(
    f"https://graph.instagram.com/v25.0/{IG_USER_ID}/media_publish",
    data={"creation_id": container_id, "access_token": TOKEN},
    timeout=30
)
r2j = r2.json()
print(f"Publish response: {r2j}")

if 'id' in r2j:
    media_id = r2j['id']
    print(f"\n✅ REEL POSTED — Media ID: {media_id}")
    
    # Mark article as instagrammed
    now = datetime.now(timezone.utc).isoformat()
    r3 = requests.patch(
        f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{ARTICLE_ID}",
        headers={
            **SB_HEADERS,
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        },
        json={"instagrammed_at": now},
        timeout=15
    )
    if r3.status_code in (200, 204):
        print(f"Marked article as instagrammed at {now}")
    else:
        print(f"WARNING: Failed to mark instagrammed: {r3.status_code} {r3.text}")
    
    print(f"\n🎉 SUCCESS: RCB IPL 2026 reel live on @thevideshi Instagram!")
else:
    print(f"\n❌ REEL PUBLISH FAILED: {r2j}")
    sys.exit(1)
