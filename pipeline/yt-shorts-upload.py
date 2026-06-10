#!/usr/bin/env python3
"""Upload prebuilt reels to YouTube Shorts for The Videshi."""

import json
import os
import re
import sys
import tempfile
import time
from datetime import datetime, timezone

import requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# --- Load env ---
def load_env(path):
    env = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.startswith('export '):
                line = line[7:]
            k, _, v = line.partition('=')
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env

yt_env = load_env('~/workspace/.env.youtube')
sb_env = load_env('~/workspace/.env.supabase')

YOUTUBE_CLIENT_ID = yt_env['YOUTUBE_CLIENT_ID']
YOUTUBE_CLIENT_SECRET = yt_env['YOUTUBE_CLIENT_SECRET']
YOUTUBE_REFRESH_TOKEN = yt_env['YOUTUBE_REFRESH_TOKEN']

SUPABASE_URL = sb_env['SUPABASE_URL']
SUPABASE_KEY = sb_env.get('SUPABASE_SERVICE_ROLE_KEY', sb_env.get('SUPABASE_ANON_KEY'))

SB_HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=minimal'
}

MAX_UPLOADS = 2

# Category-specific hashtags
CATEGORY_HASHTAGS = {
    'news': '#IndiaNews #BreakingNews #DesiNews #SouthAsian',
    'immigration': '#H1B #H1BVisa #GreenCard #USImmigration #USCIS',
    'nri-world': '#NRILife #DesiAbroad #IndianAmerican',
    'travel': '#TravelIndia #IncredibleIndia #IndiaTravel',
    'lifestyle-health': '#DesiLifestyle #Wellness #Health',
    'markets-finance': '#StockMarket #Nifty #Sensex #IndianMarkets',
    'technology': '#TechNews #IndianTech #SiliconValley #AI',
    'sports': '#Cricket #IPL #IPL2026 #TeamIndia #BCCI',
    'entertainment': '#Bollywood #BollywoodNews #IndianCinema #Tollywood',
    'food': '#IndianFood #IndianCuisine #DesiFood',
}

def extract_topic_hashtags(headline, max_tags=5):
    """Extract topic-specific hashtags from headline."""
    words = re.findall(r"[A-Z][a-z]+(?:\s[A-Z][a-z]+)?|[A-Z]{2,}", headline)
    tags = []
    seen = set()
    for w in words:
        tag = '#' + w.replace(' ', '').replace("'", '').replace('-', '')
        if tag.lower() not in seen and len(tag) > 3:
            seen.add(tag.lower())
            tags.append(tag)
        if len(tags) >= max_tags:
            break
    return tags

def compose_metadata(headline, subheadline, slug, category, tags_list):
    """Compose YouTube title, description, and tags."""
    # Title
    title = headline
    suffix = ' #Shorts'
    if len(title) + len(suffix) > 100:
        title = title[:100 - len(suffix) - 3] + '...'
    title += suffix

    # Hashtags
    base_hashtags = '#TheVideshi #Shorts #IndianDiaspora #NRI'
    cat_key = (category or '').lower().strip()
    cat_hashtags = CATEGORY_HASHTAGS.get(cat_key, '')
    topic_hashtags = ' '.join(extract_topic_hashtags(headline))
    all_hashtags = f"{base_hashtags} {cat_hashtags} {topic_hashtags}".strip()

    # Description
    sub = subheadline or headline
    description = f"""{sub}

📰 Full story: https://thevideshi.com/articles/{slug}

The Videshi — News for the global Indian diaspora
🌐 thevideshi.com

Follow us:
📸 Instagram: https://instagram.com/the.videshi
🐦 X/Twitter: https://x.com/thevideshi
🧵 Threads: https://threads.net/@the.videshi

{all_hashtags}"""

    # Tags
    yt_tags = ["The Videshi", "Indian Diaspora", "NRI", "India News", category or "News", "Shorts"]
    if tags_list:
        if isinstance(tags_list, str):
            tags_list = [t.strip() for t in tags_list.split(',')]
        for t in tags_list:
            if t and t not in yt_tags:
                yt_tags.append(t)
            if len(yt_tags) >= 12:
                break
    while len(yt_tags) < 8:
        for extra in ["South Asian", "Global Indian", "Diaspora News", "Breaking News"]:
            if extra not in yt_tags:
                yt_tags.append(extra)
            if len(yt_tags) >= 8:
                break

    return title, description, yt_tags[:12]


def main():
    # 1. Fetch pending reels from prebuilt_reels
    print("🔍 Fetching pending reels from prebuilt_reels...")
    url = (f"{SUPABASE_URL}/rest/v1/prebuilt_reels"
           f"?qa_passed=eq.true&yt_posted_at=is.null"
           f"&order=created_at.desc&limit=3"
           f"&select=id,article_id,article_slug,headline,video_path,video_url,caption")
    resp = requests.get(url, headers={k: v for k, v in SB_HEADERS.items() if k != 'Prefer'})
    if resp.status_code != 200:
        print(f"❌ Failed to fetch reels: {resp.status_code} {resp.text}")
        sys.exit(1)

    reels = resp.json()
    if not reels:
        print("✅ No pending reels to upload. All caught up!")
        return

    print(f"📦 Found {len(reels)} pending reel(s), will upload up to {MAX_UPLOADS}")

    # 2. Set up YouTube client
    creds = Credentials(
        token=None,
        refresh_token=YOUTUBE_REFRESH_TOKEN,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=YOUTUBE_CLIENT_ID,
        client_secret=YOUTUBE_CLIENT_SECRET,
    )
    youtube = build("youtube", "v3", credentials=creds)

    # 3. Load existing log
    log_path = os.path.expanduser('~/workspace/the-videshi-news/pipeline/youtube-log.json')
    if os.path.exists(log_path):
        with open(log_path) as f:
            yt_log = json.load(f)
    else:
        yt_log = {}

    uploaded = 0
    errors = []
    results = []

    for reel in reels[:MAX_UPLOADS]:
        reel_id = reel['id']
        article_id = reel.get('article_id')
        article_slug = reel.get('article_slug', '')
        headline = reel.get('headline', 'The Videshi News')
        video_url = reel.get('video_url')

        print(f"\n--- Reel {reel_id} ---")
        print(f"  Headline: {headline}")

        if not video_url:
            print(f"  ⚠️ No video_url, skipping")
            errors.append(f"Reel {reel_id}: no video_url")
            continue

        # Check for duplicate
        if reel_id in yt_log:
            print(f"  ⚠️ Already in log (video_id={yt_log[reel_id].get('video_id')}), skipping")
            continue

        # a) Download video
        print(f"  ⬇️ Downloading video...")
        try:
            dl = requests.get(video_url, timeout=120)
            dl.raise_for_status()
        except Exception as e:
            print(f"  ❌ Download failed: {e}")
            errors.append(f"Reel {reel_id}: download failed: {e}")
            continue

        tmp = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
        tmp.write(dl.content)
        tmp.close()
        print(f"  ✅ Downloaded {len(dl.content)/1024/1024:.1f} MB")

        # b) Fetch article metadata
        subheadline = ''
        category = 'News'
        art_tags = []
        slug = article_slug

        if article_id:
            art_url = (f"{SUPABASE_URL}/rest/v1/p2_articles"
                       f"?id=eq.{article_id}&select=headline,subheadline,slug,category,tags&limit=1")
            art_resp = requests.get(art_url, headers={k: v for k, v in SB_HEADERS.items() if k != 'Prefer'})
            if art_resp.status_code == 200 and art_resp.json():
                art = art_resp.json()[0]
                subheadline = art.get('subheadline', '')
                category = art.get('category', 'News')
                art_tags = art.get('tags') or []
                slug = art.get('slug', slug)
                print(f"  📰 Article: {category} | {slug}")

        # c) Compose metadata
        title, description, yt_tags = compose_metadata(headline, subheadline, slug, category, art_tags)
        print(f"  📝 Title: {title}")

        # d) Upload to YouTube
        print(f"  🚀 Uploading to YouTube...")
        try:
            body = {
                "snippet": {
                    "title": title,
                    "description": description,
                    "tags": yt_tags,
                    "categoryId": "25"
                },
                "status": {
                    "privacyStatus": "public",
                    "selfDeclaredMadeForKids": False
                }
            }

            media = MediaFileUpload(tmp.name, mimetype="video/mp4", resumable=True)

            request = youtube.videos().insert(
                part="snippet,status",
                body=body,
                media_body=media
            )

            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    print(f"  Upload progress: {int(status.progress() * 100)}%")

            video_id = response["id"]
            yt_url = f"https://youtube.com/shorts/{video_id}"
            print(f"  ✅ Uploaded: {yt_url}")

        except Exception as e:
            print(f"  ❌ Upload failed: {e}")
            errors.append(f"Reel {reel_id}: upload failed: {e}")
            os.unlink(tmp.name)
            continue
        finally:
            if os.path.exists(tmp.name):
                os.unlink(tmp.name)

        # e) Update Supabase
        now_utc = datetime.now(timezone.utc).isoformat()
        patch_url = f"{SUPABASE_URL}/rest/v1/prebuilt_reels?id=eq.{reel_id}"
        patch_body = {"yt_video_id": video_id, "yt_posted_at": now_utc}
        patch_resp = requests.patch(patch_url, json=patch_body, headers=SB_HEADERS)
        if patch_resp.status_code in (200, 204):
            print(f"  ✅ Supabase updated")
        else:
            print(f"  ⚠️ Supabase update failed: {patch_resp.status_code} {patch_resp.text}")

        # f) Log
        yt_log[reel_id] = {
            "video_id": video_id,
            "article_slug": slug,
            "uploaded_at": datetime.utcnow().isoformat() + "Z",
            "url": yt_url
        }
        with open(log_path, 'w') as f:
            json.dump(yt_log, f, indent=2)

        uploaded += 1
        results.append({"reel_id": reel_id, "video_id": video_id, "url": yt_url, "headline": headline})

        # g) Wait between uploads
        if uploaded < MAX_UPLOADS and reels.index(reel) < len(reels[:MAX_UPLOADS]) - 1:
            print("  ⏳ Waiting 10 seconds...")
            time.sleep(10)

    # Summary
    print(f"\n{'='*50}")
    print(f"📊 SUMMARY")
    print(f"  Uploaded: {uploaded}/{min(len(reels), MAX_UPLOADS)}")
    if results:
        for r in results:
            print(f"  🎬 {r['headline'][:60]}...")
            print(f"     {r['url']}")
    if errors:
        print(f"  ⚠️ Errors ({len(errors)}):")
        for e in errors:
            print(f"     - {e}")
    print(f"{'='*50}")


if __name__ == '__main__':
    main()
