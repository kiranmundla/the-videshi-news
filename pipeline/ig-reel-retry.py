#!/usr/bin/env python3
"""Upload reel video and cover to Supabase, then post as Instagram Reel."""

import os, sys, json, time, re, requests
from datetime import datetime, timezone

def load_env_file(path):
    env = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            v = v.strip().strip('"').strip("'")
            env[k] = v
    return env

ig_env = load_env_file('~/workspace/.env.instagram')
sb_env = load_env_file('~/workspace/.env.supabase')

IG_USER_ID = ig_env['INSTAGRAM_USER_ID']
IG_TOKEN = ig_env['INSTAGRAM_ACCESS_TOKEN']
SB_URL = 'https://lboecaekpynbpyijrbfz.supabase.co'
SB_KEY = sb_env['SUPABASE_SERVICE_ROLE_KEY']

slug = 'zohran-mamdani-nyc-mayor-coge-government-efficiency-bezos-endorsement-diaspora-20260531'
slug_short = slug[:80]
article_id = None  # will fetch

# Fetch the article ID
headers = {
    'apikey': SB_KEY,
    'Authorization': f'Bearer {SB_KEY}',
    'Content-Type': 'application/json'
}
r = requests.get(
    f"{SB_URL}/rest/v1/p2_articles?slug=eq.{slug}&select=id,headline,category",
    headers=headers, timeout=15
)
articles = r.json()
if not articles:
    print(f"Article not found for slug: {slug}")
    sys.exit(1)
article = articles[0]
article_id = article['id']
print(f"Article: {article['headline'][:80]}")
print(f"ID: {article_id}")

# Upload video to Supabase storage (using curl to bypass proxy issues)
video_path = os.path.expanduser(f"~/workspace/the-videshi-news/pipeline/reels/reel-{slug_short}.mp4")
cover_path = os.path.expanduser(f"~/workspace/the-videshi-news/pipeline/reels/reel-{slug_short}-cover.jpg")

print("\n=== Uploading video via curl ===")
import subprocess

# Upload video
video_sb_path = f"reels/{slug_short}.mp4"
cmd = [
    'curl', '-s', '-w', '%{http_code}', '-o', '/tmp/upload_resp.json',
    '-X', 'POST',
    f'{SB_URL}/storage/v1/object/article-images/{video_sb_path}',
    '-H', f'apikey: {SB_KEY}',
    '-H', f'Authorization: Bearer {SB_KEY}',
    '-H', 'Content-Type: video/mp4',
    '-H', 'x-upsert: true',
    '--data-binary', f'@{video_path}',
    '--max-time', '120'
]
result = subprocess.run(cmd, capture_output=True, text=True, timeout=130)
http_code = result.stdout.strip()
print(f"Video upload HTTP: {http_code}")

if http_code not in ('200', '201'):
    with open('/tmp/upload_resp.json') as f:
        print(f"Response: {f.read()[:500]}")
    sys.exit(1)

video_public_url = f"{SB_URL}/storage/v1/object/public/article-images/{video_sb_path}"
print(f"Video URL: {video_public_url}")

# Upload cover
cover_sb_path = f"reels/{slug_short}-cover.jpg"
cmd2 = [
    'curl', '-s', '-w', '%{http_code}', '-o', '/tmp/upload_resp2.json',
    '-X', 'POST',
    f'{SB_URL}/storage/v1/object/article-images/{cover_sb_path}',
    '-H', f'apikey: {SB_KEY}',
    '-H', f'Authorization: Bearer {SB_KEY}',
    '-H', 'Content-Type: image/jpeg',
    '-H', 'x-upsert: true',
    '--data-binary', f'@{cover_path}',
    '--max-time', '60'
]
result2 = subprocess.run(cmd2, capture_output=True, text=True, timeout=70)
http_code2 = result2.stdout.strip()
print(f"Cover upload HTTP: {http_code2}")
cover_public_url = f"{SB_URL}/storage/v1/object/public/article-images/{cover_sb_path}" if http_code2 in ('200', '201') else None

# Build caption
headline = article['headline']
caption = f"""{headline}

📰 Read more: https://thevideshi.com/articles/{slug}

#India #NRI #IndiaNews #IndianDiaspora #BreakingNews #DesiNews #SouthAsian #IndianAmerican #NRINews #NewYork #DOGE #IndianAmerican #TheVideshi #Reels"""

print(f"\nCaption:\n{caption[:300]}")

# Create Reel container
print("\n=== Creating Reel container ===")
container_data = {
    "video_url": video_public_url,
    "media_type": "REELS",
    "caption": caption,
    "access_token": IG_TOKEN
}
if cover_public_url:
    container_data["cover_url"] = cover_public_url

r = requests.post(
    f"https://graph.instagram.com/v25.0/{IG_USER_ID}/media",
    data=container_data, timeout=30
)
rj = r.json()
print(f"Container response: {rj}")

if 'id' not in rj:
    print(f"FAILED to create container")
    sys.exit(1)

container_id = rj['id']

# Poll for processing
print("Waiting for video processing...")
finished = False
for i in range(18):
    time.sleep(5)
    r_status = requests.get(
        f"https://graph.instagram.com/v25.0/{container_id}",
        params={"fields": "status_code", "access_token": IG_TOKEN},
        timeout=15
    )
    status = r_status.json().get('status_code', 'UNKNOWN')
    print(f"  Poll {i+1}/18: {status}")
    if status == 'FINISHED':
        finished = True
        break
    elif status == 'ERROR':
        print(f"  ERROR: {r_status.json()}")
        sys.exit(1)

if not finished:
    print("Timed out waiting for processing")
    sys.exit(1)

# Publish
print("\n=== Publishing Reel ===")
r2 = requests.post(
    f"https://graph.instagram.com/v25.0/{IG_USER_ID}/media_publish",
    data={"creation_id": container_id, "access_token": IG_TOKEN},
    timeout=30
)
r2j = r2.json()
print(f"Publish response: {r2j}")

if 'id' in r2j:
    print(f"✅ Reel posted! Media ID: {r2j['id']}")
    
    # Mark instagrammed_at
    now_utc = datetime.now(timezone.utc).isoformat()
    patch_r = requests.patch(
        f"{SB_URL}/rest/v1/p2_articles?id=eq.{article_id}",
        headers=headers,
        json={"instagrammed_at": now_utc},
        timeout=15
    )
    print(f"Updated instagrammed_at: {patch_r.status_code}")
else:
    print(f"❌ Reel publish failed: {r2j}")
    sys.exit(1)
