#!/usr/bin/env python3
"""Retry upload for the Canada-Carney reel that timed out."""

import json
import os
import time
from datetime import datetime, timezone

import requests as req
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import socket

# Set default socket timeout to 120s
socket.setdefaulttimeout(120)

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

yt_env = load_env("~/workspace/.env.youtube")
sb_env = load_env("~/workspace/.env.supabase")

YOUTUBE_CLIENT_ID = yt_env["YOUTUBE_CLIENT_ID"]
YOUTUBE_CLIENT_SECRET = yt_env["YOUTUBE_CLIENT_SECRET"]
YOUTUBE_REFRESH_TOKEN = yt_env["YOUTUBE_REFRESH_TOKEN"]
SUPABASE_URL = sb_env.get("SUPABASE_URL", "https://lboecaekpynbpyijrbfz.supabase.co")
SB_KEY = sb_env.get("SUPABASE_SERVICE_KEY") or sb_env.get("SUPABASE_ANON_KEY") or sb_env.get("SUPABASE_KEY", "")

LOG_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/youtube-log.json")
REEL_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/reels/reel-canada-carney-one-seat-majority-india-cepa-trade-deal-20260527.mp4")

reel_name = os.path.basename(REEL_PATH)
print(f"Retrying upload: {reel_name}")
print(f"File size: {os.path.getsize(REEL_PATH) / 1024:.0f} KB")

# Get article info
headline = "Canada's Government Just Shrank to a One-Seat Majority. The India Trade Deal Could Be Next."
subheadline = ""
slug = "canada-carney-one-seat-majority-india-cepa-trade-deal-20260527"
category = "News"

# Try to get subheadline from Supabase
try:
    resp = req.get(
        f"{SUPABASE_URL}/rest/v1/p2_articles?slug=eq.{slug}&select=headline,subheadline,category",
        headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"},
        timeout=15
    )
    data = resp.json()
    if data:
        headline = data[0].get("headline", headline)
        subheadline = data[0].get("subheadline", "")
        category = data[0].get("category", "News")
        print(f"  Got article details: {headline[:80]}")
except Exception as e:
    print(f"  Warning fetching article: {e}")

title = headline
if len(title) > 90:
    title = title[:87] + "..."
title = f"{title} #Shorts"

description = f"""{subheadline}

📰 Full story: https://thevideshi.com/articles/{slug}

The Videshi — News for the global Indian diaspora
🌐 thevideshi.com

Follow us:
📸 Instagram: https://instagram.com/the.videshi
🐦 X/Twitter: https://x.com/thevideshi
🧵 Threads: https://threads.net/@the.videshi

#TheVideshi #IndianDiaspora #NRI #IndiaNews #Shorts"""

tags = ["The Videshi", "Indian Diaspora", "NRI", "India News", category, "Shorts"]

# Build YouTube client with longer timeout
creds = Credentials(
    token=None,
    refresh_token=YOUTUBE_REFRESH_TOKEN,
    token_uri="https://oauth2.googleapis.com/token",
    client_id=YOUTUBE_CLIENT_ID,
    client_secret=YOUTUBE_CLIENT_SECRET
)

youtube = build("youtube", "v3", credentials=creds)

body = {
    "snippet": {
        "title": title,
        "description": description,
        "tags": tags,
        "categoryId": "25"
    },
    "status": {
        "privacyStatus": "public",
        "selfDeclaredMadeForKids": False
    }
}

media = MediaFileUpload(REEL_PATH, mimetype="video/mp4", resumable=True, chunksize=1024*1024)

request = youtube.videos().insert(
    part="snippet,status",
    body=body,
    media_body=media
)

print("Uploading...")
response = None
retries = 0
while response is None:
    try:
        status, response = request.next_chunk()
        if status:
            print(f"  Upload progress: {int(status.progress() * 100)}%")
    except Exception as e:
        retries += 1
        if retries > 3:
            raise
        print(f"  Chunk error (retry {retries}/3): {e}")
        time.sleep(5)

video_id = response["id"]
url = f"https://youtube.com/shorts/{video_id}"
print(f"✅ Uploaded: {url}")

# Update log
with open(LOG_PATH) as f:
    yt_log = json.load(f)

yt_log[reel_name] = {
    "video_id": video_id,
    "article_slug": slug,
    "uploaded_at": datetime.now(timezone.utc).isoformat(),
    "url": url
}

with open(LOG_PATH, 'w') as f:
    json.dump(yt_log, f, indent=2)

print(f"Log updated. Total entries: {len(yt_log)}")
