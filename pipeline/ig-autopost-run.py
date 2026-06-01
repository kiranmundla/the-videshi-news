#!/usr/bin/env python3
"""Instagram autopost: 1 Reel + 1 Story per run."""

import os
import re
import sys
import json
import time
import subprocess
import requests
from datetime import datetime, timezone

# ── Load credentials ────────────────────────────────────────────────

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

ig_env = load_env('~/workspace/.env.instagram')
sb_env = load_env('~/workspace/.env.supabase')
vn_env = load_env('~/workspace/the-videshi-news/.env')

IG_USER_ID = ig_env['INSTAGRAM_USER_ID']
IG_TOKEN = ig_env['INSTAGRAM_ACCESS_TOKEN']
SB_URL = sb_env['SUPABASE_URL']
SB_KEY = sb_env['SUPABASE_SERVICE_ROLE_KEY']
ANON_KEY = vn_env['VITE_SUPABASE_PUBLISHABLE_KEY']

print(f"[init] IG user: {IG_USER_ID}")
print(f"[init] Supabase URL: {SB_URL}")

# ── Step 1: Refresh IG token ────────────────────────────────────────

print("\n[token] Refreshing Instagram access token...")
try:
    r = requests.get("https://graph.instagram.com/refresh_access_token", params={
        "grant_type": "ig_refresh_token",
        "access_token": IG_TOKEN
    }, timeout=15)
    token_resp = r.json()
    if 'access_token' in token_resp:
        new_token = token_resp['access_token']
        expires_in = token_resp.get('expires_in', 0)
        print(f"[token] ✅ Refreshed. Expires in {expires_in // 86400} days.")
        # Save back
        env_path = os.path.expanduser('~/workspace/.env.instagram')
        with open(env_path) as f:
            content = f.read()
        content = re.sub(
            r'INSTAGRAM_ACCESS_TOKEN=.*',
            f'INSTAGRAM_ACCESS_TOKEN={new_token}',
            content
        )
        with open(env_path, 'w') as f:
            f.write(content)
        IG_TOKEN = new_token
    else:
        print(f"[token] ⚠️ Refresh failed: {token_resp}")
except Exception as e:
    print(f"[token] ⚠️ Refresh error: {e}")

# ── Step 2: Fetch unposted articles ────────────────────────────────

print("\n[fetch] Loading unposted articles from Supabase...")
headers = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json"
}

r = requests.get(
    f"{SB_URL}/rest/v1/p2_articles",
    params={
        "status": "eq.published",
        "instagrammed_at": "is.null",
        "image_url": "not.is.null",
        "order": "published_at.desc",
        "limit": "20",
        "select": "id,slug,headline,subheadline,category,image_url"
    },
    headers=headers,
    timeout=15
)

if r.status_code != 200:
    print(f"[fetch] ❌ Supabase error {r.status_code}: {r.text[:300]}")
    sys.exit(1)

articles = r.json()
# Filter out articles without slug
articles = [a for a in articles if a.get('slug') and a.get('image_url')]
print(f"[fetch] Found {len(articles)} unposted articles with images.")

if not articles:
    print("[done] No unposted articles available. Nothing to do.")
    sys.exit(0)

# ── Step 3: Category → hashtags mapping ────────────────────────────

CATEGORY_TAGS = {
    "news": "#India #NRI #IndiaNews #IndianDiaspora #BreakingNews #DesiNews #SouthAsian #IndianAmerican #NRINews",
    "immigration": "#Immigration #H1B #H1BVisa #NRI #GreenCard #IndianAmerican #USImmigration #VisaUpdate #OPT #USCIS #Desi",
    "nri-world": "#NRI #IndianDiaspora #NRILife #Desi #IndianAmerican #SouthAsian #DesiAbroad #IndianImmigrant #NRICommunity",
    "travel": "#Travel #India #IndiaTravel #IncredibleIndia #TravelIndia #DesiTravel #IndianDestinations #TravelDiaries #Wanderlust",
    "lifestyle-health": "#Lifestyle #Desi #NRILife #IndianAmerican #DesiLifestyle #Wellness #Health #SouthAsian #DesiCulture",
    "markets-finance": "#Markets #India #NRI #Nifty #Sensex #BSE #NSE #IndianMarkets #StockMarket #Finance #NRIInvesting",
    "technology": "#Tech #India #IndianTech #Startup #H1B #SiliconValley #AI #TechNews #IndianEngineers #FAANG #IndiansinTech",
    "sports": "#Cricket #India #IPL #IPL2026 #IndianCricket #BCCI #CricketNews #Desi #TeamIndia",
    "entertainment": "#Bollywood #Entertainment #IndianCinema #Desi #BollywoodNews #Tollywood #IndianMovies #DesiEntertainment",
    "food": "#IndianFood #Desi #IndianCuisine #NRIFood #DesiFood #IndianCooking #Foodie #IndianRecipes #DesiChef",
}

def build_caption(article):
    headline = article['headline']
    slug = article['slug']
    cat = article.get('category', 'news')
    
    base_tags = CATEGORY_TAGS.get(cat, CATEGORY_TAGS['news'])
    
    # Extract topic-specific hashtags from headline
    # Simple heuristic: capitalize words > 3 chars that look like proper nouns
    words = headline.split()
    topic_tags = []
    for w in words:
        clean = re.sub(r'[^A-Za-z0-9]', '', w)
        if clean and clean[0].isupper() and len(clean) > 3:
            topic_tags.append(f"#{clean}")
    # Deduplicate and limit
    seen = set()
    unique_topic = []
    for t in topic_tags:
        tl = t.lower()
        if tl not in seen and tl not in base_tags.lower():
            seen.add(tl)
            unique_topic.append(t)
    topic_tags = unique_topic[:4]
    
    all_tags = base_tags + " " + " ".join(topic_tags)
    all_tags += " #TheVideshi #Reels"
    
    # Trim to max 20 hashtags
    tag_list = all_tags.split()
    tag_list = tag_list[:20]
    tags_str = " ".join(tag_list)
    
    caption = f"""{headline}

📰 Read more: https://thevideshi.com/articles/{slug}

{tags_str}"""
    return caption

# ── Step 4: Post Reel (first article) ──────────────────────────────

reel_article = articles[0]
print(f"\n[reel] Generating reel for: {reel_article['headline'][:80]}...")
print(f"[reel] Slug: {reel_article['slug']}")

reel_success = False
reel_media_id = None

try:
    # Run generate-reel.py
    result = subprocess.run(
        ["python3", "generate-reel.py", "--slug", reel_article['slug'], "--upload"],
        cwd=os.path.expanduser("~/workspace/the-videshi-news/pipeline"),
        capture_output=True, text=True, timeout=180
    )
    print(f"[reel] generate-reel.py exit code: {result.returncode}")
    if result.stdout:
        print(f"[reel] stdout (last 500): {result.stdout[-500:]}")
    if result.stderr:
        print(f"[reel] stderr (last 300): {result.stderr[-300:]}")
    
    # Parse Supabase URL from output
    reel_url = None
    for line in result.stdout.split('\n'):
        if 'supabase.co/storage' in line:
            match = re.search(r'(https://[^\s]+supabase\.co/storage/[^\s]+)', line)
            if match:
                reel_url = match.group(1)
                break
    
    if not reel_url:
        print("[reel] ❌ Could not parse reel URL from generate-reel.py output")
        # Try to find any .mp4 URL
        for line in result.stdout.split('\n'):
            if '.mp4' in line and 'http' in line:
                match = re.search(r'(https?://[^\s]+\.mp4[^\s]*)', line)
                if match:
                    reel_url = match.group(1)
                    print(f"[reel] Found alternate URL: {reel_url}")
                    break
    
    if reel_url:
        print(f"[reel] Video URL: {reel_url}")
        
        # Upload cover image if exists
        slug_short = reel_article['slug'][:80]
        cover_local = os.path.expanduser(f"~/workspace/the-videshi-news/pipeline/reels/reel-{slug_short}-cover.jpg")
        cover_public_url = None
        if os.path.exists(cover_local):
            cover_filename = f"reels/{slug_short}-cover.jpg"
            with open(cover_local, 'rb') as cf:
                cr = requests.post(
                    f"{SB_URL}/storage/v1/object/article-images/{cover_filename}",
                    headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}",
                             "Content-Type": "image/jpeg", "x-upsert": "true"},
                    data=cf.read(),
                    timeout=30
                )
            cover_public_url = f"{SB_URL}/storage/v1/object/public/article-images/{cover_filename}"
            print(f"[reel] Cover uploaded: {cover_public_url}")
        
        # Create reel container
        caption = build_caption(reel_article)
        container_data = {
            "video_url": reel_url,
            "media_type": "REELS",
            "caption": caption,
            "access_token": IG_TOKEN
        }
        if cover_public_url:
            container_data["cover_url"] = cover_public_url
        
        print("[reel] Creating container...")
        r = requests.post(
            f"https://graph.instagram.com/v25.0/{IG_USER_ID}/media",
            data=container_data,
            timeout=30
        )
        resp = r.json()
        print(f"[reel] Container response: {resp}")
        
        if 'id' in resp:
            container_id = resp['id']
            
            # Poll for FINISHED
            print("[reel] Waiting for video processing...")
            finished = False
            for i in range(18):
                time.sleep(5)
                r_status = requests.get(
                    f"https://graph.instagram.com/v25.0/{container_id}",
                    params={"fields": "status_code", "access_token": IG_TOKEN},
                    timeout=15
                )
                status = r_status.json().get('status_code', 'UNKNOWN')
                print(f"[reel]   Poll {i+1}/18: {status}")
                if status == 'FINISHED':
                    finished = True
                    break
                elif status == 'ERROR':
                    print("[reel] ❌ Video processing failed")
                    break
            
            if finished:
                # Publish
                r2 = requests.post(
                    f"https://graph.instagram.com/v25.0/{IG_USER_ID}/media_publish",
                    data={"creation_id": container_id, "access_token": IG_TOKEN},
                    timeout=30
                )
                pub_resp = r2.json()
                print(f"[reel] Publish response: {pub_resp}")
                
                if 'id' in pub_resp:
                    reel_media_id = pub_resp['id']
                    reel_success = True
                    print(f"[reel] ✅ Reel published! Media ID: {reel_media_id}")
                    
                    # Mark as instagrammed
                    now_utc = datetime.now(timezone.utc).isoformat()
                    requests.patch(
                        f"{SB_URL}/rest/v1/p2_articles?id=eq.{reel_article['id']}",
                        headers=headers,
                        json={"instagrammed_at": now_utc},
                        timeout=15
                    )
                    print(f"[reel] Article marked instagrammed_at={now_utc}")
                else:
                    print(f"[reel] ❌ Publish failed: {pub_resp}")
            else:
                print("[reel] ❌ Video never finished processing")
        else:
            print(f"[reel] ❌ Container creation failed: {resp}")
    else:
        print("[reel] ❌ No reel URL found — skipping reel")

except subprocess.TimeoutExpired:
    print("[reel] ❌ generate-reel.py timed out after 180s")
except Exception as e:
    print(f"[reel] ❌ Error: {e}")

# ── Step 5: Post Story (second article, or first if only one) ──────

time.sleep(30)  # Rate limit buffer

# Use a DIFFERENT article for the story (second if available)
story_article = articles[1] if len(articles) > 1 else articles[0]
# Don't story the same article as the reel unless it's the only one
if story_article['id'] == reel_article['id'] and len(articles) > 1:
    story_article = articles[1]

print(f"\n[story] Posting story for: {story_article['headline'][:80]}...")
story_success = False

try:
    r = requests.post(
        f"https://graph.instagram.com/v25.0/{IG_USER_ID}/media",
        data={
            "image_url": story_article['image_url'],
            "media_type": "STORIES",
            "access_token": IG_TOKEN
        },
        timeout=30
    )
    story_resp = r.json()
    print(f"[story] Container response: {story_resp}")
    
    if 'id' in story_resp:
        story_container = story_resp['id']
        time.sleep(8)
        
        r2 = requests.post(
            f"https://graph.instagram.com/v25.0/{IG_USER_ID}/media_publish",
            data={"creation_id": story_container, "access_token": IG_TOKEN},
            timeout=30
        )
        pub_resp = r2.json()
        print(f"[story] Publish response: {pub_resp}")
        
        if 'id' in pub_resp:
            story_success = True
            print(f"[story] ✅ Story published! Media ID: {pub_resp['id']}")
        else:
            print(f"[story] ❌ Publish failed: {pub_resp}")
    else:
        print(f"[story] ❌ Container creation failed: {story_resp}")
except Exception as e:
    print(f"[story] ⚠️ Story error (non-fatal): {e}")

# ── Summary ─────────────────────────────────────────────────────────

print("\n" + "="*60)
print("INSTAGRAM AUTOPOST SUMMARY")
print("="*60)
print(f"Reel:  {'✅ Posted' if reel_success else '❌ Failed'} — {reel_article['headline'][:60]}")
if reel_media_id:
    print(f"       Media ID: {reel_media_id}")
print(f"Story: {'✅ Posted' if story_success else '❌ Failed'} — {story_article['headline'][:60]}")
print(f"Articles remaining: {len(articles) - (1 if reel_success else 0)}")
print("="*60)
