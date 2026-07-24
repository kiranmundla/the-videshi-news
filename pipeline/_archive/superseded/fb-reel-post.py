#!/usr/bin/env python3
"""Post 1 reel to The Videshi Facebook Page. Called by videshi-fb-reels cron."""

import os, sys, json, time, glob, re, requests
from datetime import datetime, timezone

# --- Config ---
REELS_DIR = os.path.expanduser("~/workspace/the-videshi-news/pipeline/reels")
LOG_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/fb-reels-log.json")

def load_env(path):
    env = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env

fb_env = load_env("~/workspace/.env.facebook")
sb_env = load_env("~/workspace/.env.supabase")

FB_PAGE_ID = fb_env["FB_PAGE_ID"]
FB_TOKEN = fb_env["FB_PAGE_ACCESS_TOKEN"]
SUPABASE_URL = sb_env.get("SUPABASE_URL", "https://lboecaekpynbpyijrbfz.supabase.co")
SUPABASE_KEY = sb_env.get("SUPABASE_ANON_KEY") or sb_env.get("SUPABASE_SERVICE_ROLE_KEY")

# --- Load dedup log ---
try:
    with open(LOG_PATH) as f:
        fb_reels_log = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    fb_reels_log = {}

# --- Find candidates ---
reel_files = sorted(glob.glob(os.path.join(REELS_DIR, "reel-*.mp4")), key=os.path.getmtime, reverse=True)
candidates = [f for f in reel_files if os.path.basename(f) not in fb_reels_log]

# Skip intermediates
skip_words = ['preview-', '-v2-', '-v2.', '-v3-', '-v4-', '-v5-', 'test', '-assembled',
              '-music', '-landscape-', '-normalized']
candidates = [f for f in candidates if not any(x in os.path.basename(f) for x in skip_words)]

# If a -final version exists, skip the non-final base
final_bases = set()
for c in candidates:
    bn = os.path.basename(c)
    if '-final.' in bn or bn.endswith('-final.mp4'):
        base = bn.replace('-final.mp4', '.mp4')
        final_bases.add(base)

candidates = [c for c in candidates if os.path.basename(c) not in final_bases]

print(f"Total reel files: {len(reel_files)}")
print(f"Already posted: {len(fb_reels_log)}")
print(f"Candidates: {len(candidates)}")

if not candidates:
    print("No new reels to post.")
    sys.exit(0)

# Pick the most recent
reel_path = candidates[0]
filename = os.path.basename(reel_path)
file_size = os.path.getsize(reel_path)
print(f"\nPosting: {filename} ({file_size / 1e6:.1f} MB)")

# --- Extract slug and find article ---
slug_parts = filename.replace('reel-', '').replace('.mp4', '').replace('-final', '')
# Remove trailing date (7-8 digits, e.g. 20260609 or 2026060)
slug_clean = re.sub(r'-\d{7,8}$', '', slug_parts)
# Also remove trailing -n suffix
slug_clean = re.sub(r'-n$', '', slug_clean)

print(f"Slug search: {slug_clean}")

# Fetch recent articles
r = requests.get(
    f"{SUPABASE_URL}/rest/v1/p2_articles",
    params={
        "status": "eq.published",
        "order": "published_at.desc",
        "limit": "50",
        "select": "id,slug,headline,subheadline,category"
    },
    headers={"apikey": SUPABASE_KEY},
    timeout=15
)
articles = r.json() if r.status_code == 200 else []

# Match by slug word overlap
matched = None
slug_words = set(slug_clean.split('-'))
best_overlap = 0
for a in articles:
    a_words = set((a.get('slug') or '').split('-'))
    overlap = len(slug_words & a_words)
    if overlap > best_overlap and overlap >= 3:
        best_overlap = overlap
        matched = a

if matched:
    headline = matched['headline']
    slug = matched['slug']
    category = (matched.get('category') or 'News').replace('-', ' ').title()
    subheadline = matched.get('subheadline', '')
    print(f"Matched article: {headline[:80]}...")
else:
    headline = ' '.join(w.capitalize() for w in slug_clean.split('-'))
    slug = slug_clean
    category = 'News'
    subheadline = ''
    print(f"No article match, using filename: {headline[:80]}")

# --- Build caption ---
caption_parts = [headline]
if subheadline:
    caption_parts.append(f"\n{subheadline}")
caption_parts.append(f"\n📰 Read more: https://thevideshi.com/articles/{slug}")
caption_parts.append("\n#TheVideshi #IndianDiaspora #NRI #NRINews #DesiNews #SouthAsian #IndianAmerican #Reels")

# Category-specific hashtags
cat_tags = {
    'entertainment': '#Bollywood #Entertainment #IndianCinema',
    'sports': '#Cricket #IndianSports #IPL',
    'technology': '#Tech #IndianTech #AI',
    'nri world': '#NRIWorld #Immigration #H1B',
    'markets & finance': '#IndianMarkets #Finance #Economy',
    'news': '#India #BreakingNews #IndiaNews',
}
cat_lower = category.lower()
for k, v in cat_tags.items():
    if k in cat_lower:
        caption_parts.append(v)
        break

description = '\n'.join(caption_parts)
print(f"\nCaption:\n{description}\n")

# === STEP 1: Initialize upload session ===
print("=== Step 1: Init upload session ===")
init_resp = requests.post(
    f"https://graph.facebook.com/v25.0/{FB_PAGE_ID}/video_reels",
    data={
        "upload_phase": "start",
        "access_token": FB_TOKEN
    },
    timeout=30
)
init_data = init_resp.json()

if 'error' in init_data:
    print(f"❌ Init failed: {init_data['error'].get('message', str(init_data))[:200]}")
    sys.exit(1)

video_id = init_data.get('video_id')
print(f"Video ID: {video_id}")

# === STEP 2: Upload binary ===
print("=== Step 2: Upload video binary ===")
with open(reel_path, 'rb') as vf:
    video_data = vf.read()

upload_resp = requests.post(
    f"https://rupload.facebook.com/video-upload/v25.0/{video_id}",
    headers={
        "Authorization": f"OAuth {FB_TOKEN}",
        "offset": "0",
        "file_size": str(file_size),
        "Content-Type": "application/octet-stream"
    },
    data=video_data,
    timeout=120
)
upload_data = upload_resp.json()

if not upload_data.get('success'):
    print(f"❌ Upload failed: {upload_data}")
    sys.exit(1)

print("Video uploaded successfully")

# === STEP 3: Wait and publish ===
print("=== Step 3: Wait for processing + publish ===")
time.sleep(10)

publish_resp = requests.post(
    f"https://graph.facebook.com/v25.0/{FB_PAGE_ID}/video_reels",
    data={
        "upload_phase": "finish",
        "video_id": video_id,
        "video_state": "PUBLISHED",
        "description": description,
        "access_token": FB_TOKEN
    },
    timeout=30
)
publish_data = publish_resp.json()

if publish_data.get('success') or publish_data.get('id'):
    reel_id = publish_data.get('id', video_id)
    print(f"\n✅ Reel published! ID: {reel_id}")

    fb_reels_log[filename] = {
        "video_id": str(video_id),
        "reel_id": str(reel_id),
        "headline": headline[:100],
        "posted_at": datetime.now(timezone.utc).isoformat()
    }
    with open(LOG_PATH, 'w') as f:
        json.dump(fb_reels_log, f, indent=2)
    print(f"Logged. Total in FB reels log: {len(fb_reels_log)}")
else:
    error_msg = publish_data.get('error', {}).get('message', str(publish_data))
    print(f"\n❌ Publish failed: {error_msg[:200]}")
    sys.exit(1)
