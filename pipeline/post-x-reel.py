#!/usr/bin/env python3
"""Post a single reel to X/Twitter using manual chunked upload with requests."""

import os
import sys
import json
import time
import tempfile
import requests
from requests_oauthlib import OAuth1
from datetime import datetime, timezone

# Load env
def load_env(path):
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('#') and not line.startswith('export '):
                k, v = line.split('=', 1)
                os.environ[k] = v
            elif line.startswith('export '):
                line = line[7:]
                if '=' in line:
                    k, v = line.split('=', 1)
                    os.environ[k] = v

load_env('~/workspace/.env.twitter')
load_env('~/workspace/.env.supabase')

CONSUMER_KEY = os.environ['TWITTER_CONSUMER_KEY']
CONSUMER_SECRET = os.environ['TWITTER_CONSUMER_SECRET']
ACCESS_TOKEN = os.environ['TWITTER_ACCESS_TOKEN']
ACCESS_TOKEN_SECRET = os.environ['TWITTER_ACCESS_TOKEN_SECRET']
SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']

# Reel details
REEL_ID = "4baf43f8-9ffb-4f73-bcb9-1897ed9da505"
VIDEO_URL = "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/reels/ss-reel-india-equity-mutual-fund-inflows-crash-40-percent-may-bernst-20260611-0404.mp4"
HEADLINE = "India's Retail Investors Just Blinked. Equity Fund Inflows Crashed 40% in May."
SLUG = "india-equity-mutual-fund-inflows-crash-40-percent-may-bernstein-sip-warning-2026"

# Build tweet text (max 280 chars)
article_url = f"https://thevideshi.com/articles/{SLUG}"
tweet_text = f"🇮🇳 {HEADLINE[:200]}\n\n📰 {article_url}\n\n#IndianDiaspora #NRI #MutualFunds #India"
if len(tweet_text) > 280:
    tweet_text = tweet_text[:277] + "..."
print(f"Tweet text ({len(tweet_text)} chars):\n{tweet_text}\n")

auth = OAuth1(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
UPLOAD_URL = "https://upload.twitter.com/1.1/media/upload.json"
TWEET_URL = "https://api.twitter.com/2/tweets"

# Download video
print("Downloading video...")
resp = requests.get(VIDEO_URL, timeout=120)
resp.raise_for_status()
video_data = resp.content
video_size = len(video_data)
print(f"Video size: {video_size} bytes ({video_size/1024/1024:.1f} MB)")

# INIT
print("\n--- INIT ---")
init_resp = requests.post(UPLOAD_URL, data={
    'command': 'INIT',
    'total_bytes': video_size,
    'media_type': 'video/mp4',
    'media_category': 'tweet_video'
}, auth=auth, timeout=30)
print(f"INIT status: {init_resp.status_code}")
if init_resp.status_code != 202:
    print(f"INIT failed: {init_resp.text}")
    sys.exit(1)

media_id = init_resp.json()['media_id_string']
print(f"Media ID: {media_id}")

# APPEND (1MB chunks)
CHUNK_SIZE = 1 * 1024 * 1024
segment = 0
offset = 0
print(f"\n--- APPEND ({(video_size + CHUNK_SIZE - 1) // CHUNK_SIZE} chunks) ---")

while offset < video_size:
    chunk = video_data[offset:offset + CHUNK_SIZE]
    for attempt in range(3):
        try:
            append_resp = requests.post(UPLOAD_URL, data={
                'command': 'APPEND',
                'media_id': media_id,
                'segment_index': segment,
            }, files={
                'media': ('chunk.mp4', chunk, 'application/octet-stream')
            }, auth=auth, timeout=60)
            
            if append_resp.status_code in (200, 202, 204):
                print(f"  Segment {segment}: OK ({len(chunk)} bytes)")
                break
            else:
                print(f"  Segment {segment} attempt {attempt+1}: {append_resp.status_code} {append_resp.text}")
        except Exception as e:
            print(f"  Segment {segment} attempt {attempt+1} error: {e}")
        
        if attempt < 2:
            time.sleep(2 ** attempt)
    else:
        print(f"APPEND failed after 3 attempts at segment {segment}")
        sys.exit(1)
    
    offset += CHUNK_SIZE
    segment += 1

# FINALIZE
print("\n--- FINALIZE ---")
fin_resp = requests.post(UPLOAD_URL, data={
    'command': 'FINALIZE',
    'media_id': media_id,
}, auth=auth, timeout=30)
print(f"FINALIZE status: {fin_resp.status_code}")
fin_data = fin_resp.json()
print(f"FINALIZE response: {json.dumps(fin_data, indent=2)}")

if fin_resp.status_code not in (200, 201):
    print("FINALIZE failed")
    sys.exit(1)

# Poll STATUS if processing
if 'processing_info' in fin_data:
    print("\n--- STATUS polling ---")
    while True:
        pi = fin_data.get('processing_info', {})
        state = pi.get('state')
        wait = pi.get('check_after_secs', 5)
        print(f"  State: {state}, waiting {wait}s...")
        
        if state == 'succeeded':
            break
        elif state == 'failed':
            print(f"  Processing failed: {pi.get('error', {})}")
            sys.exit(1)
        
        time.sleep(wait)
        status_resp = requests.get(UPLOAD_URL, params={
            'command': 'STATUS',
            'media_id': media_id,
        }, auth=auth, timeout=30)
        fin_data = status_resp.json()

print("\nMedia upload complete!")

# Post tweet with v2 API
print("\n--- POST TWEET ---")
tweet_resp = requests.post(TWEET_URL, json={
    'text': tweet_text,
    'media': {
        'media_ids': [media_id]
    }
}, auth=auth, headers={'Content-Type': 'application/json'}, timeout=30)

print(f"Tweet status: {tweet_resp.status_code}")
print(f"Tweet response: {tweet_resp.text}")

if tweet_resp.status_code in (200, 201):
    tweet_data = tweet_resp.json()
    tweet_id = tweet_data.get('data', {}).get('id', '')
    print(f"\n✅ Tweet posted! ID: {tweet_id}")
    
    # Update Supabase
    now = datetime.now(timezone.utc).isoformat()
    patch_resp = requests.patch(
        f"{SUPABASE_URL}/rest/v1/prebuilt_reels?id=eq.{REEL_ID}",
        json={"x_posted_at": now, "x_tweet_id": tweet_id},
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        },
        timeout=15
    )
    print(f"Supabase update: {patch_resp.status_code}")
    if patch_resp.status_code in (200, 204):
        print("✅ Supabase updated")
    else:
        print(f"Supabase update failed: {patch_resp.text}")
else:
    print(f"\n❌ Tweet failed: {tweet_resp.text}")
    sys.exit(1)
