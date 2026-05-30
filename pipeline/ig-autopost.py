#!/usr/bin/env python3
"""Instagram autopost script for The Videshi - posts Reels + Stories."""

import os
import sys
import json
import time
import subprocess
import re
from datetime import datetime, timezone

import requests

# --- Config ---
SUPABASE_URL = "https://lboecaekpynbpyijrbfz.supabase.co"
ENV_IG_PATH = os.path.expanduser("~/workspace/.env.instagram")

def load_env_file(path):
    """Load key=value pairs from an env file."""
    env = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            key, val = line.split('=', 1)
            env[key.strip()] = val.strip().strip('"').strip("'")
    return env

def save_env_file(path, env_dict):
    """Write env dict back to file."""
    with open(path, 'w') as f:
        for k, v in env_dict.items():
            f.write(f"{k}={v}\n")

# Load credentials
ig_env = load_env_file(ENV_IG_PATH)
IG_USER_ID = ig_env['INSTAGRAM_USER_ID']
TOKEN = ig_env['INSTAGRAM_ACCESS_TOKEN']
APP_SECRET = ig_env.get('INSTAGRAM_APP_SECRET', '')

sb_env = load_env_file(os.path.expanduser("~/workspace/.env.supabase"))
SB_SERVICE_KEY = sb_env['SUPABASE_SERVICE_ROLE_KEY']

# --- Step 1: Refresh token ---
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
            ig_env['INSTAGRAM_ACCESS_TOKEN'] = TOKEN
            save_env_file(ENV_IG_PATH, ig_env)
            print(f"  Token refreshed, expires in {rj.get('expires_in', '?')}s")
        else:
            print("  Token unchanged after refresh")
    else:
        print(f"  Token refresh response: {rj}")
except Exception as e:
    print(f"  Token refresh failed (non-fatal): {e}")

# --- Step 2: Fetch recent unposted articles ---
print("\n=== Fetching unposted articles ===")
headers = {
    "apikey": SB_SERVICE_KEY,
    "Authorization": f"Bearer {SB_SERVICE_KEY}",
    "Content-Type": "application/json"
}

r = requests.get(
    f"{SUPABASE_URL}/rest/v1/p2_articles",
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
articles = r.json()
if not isinstance(articles, list):
    print(f"  Error fetching articles: {articles}")
    sys.exit(1)

# Filter out articles with empty image_url
articles = [a for a in articles if a.get('image_url') and a.get('slug') and a.get('headline')]
print(f"  Found {len(articles)} unposted articles with images")

if not articles:
    print("  Nothing to post. Exiting.")
    sys.exit(0)

# Pick up to 2
batch = articles[:2]
for i, a in enumerate(batch):
    print(f"  [{i+1}] {a['category']}: {a['headline'][:80]}...")

# --- Hashtag logic ---
CATEGORY_HASHTAGS = {
    "news": ["#India", "#NRI", "#IndiaNews", "#IndianDiaspora", "#BreakingNews", "#DesiNews", "#SouthAsian", "#IndianAmerican", "#NRINews"],
    "immigration": ["#Immigration", "#H1B", "#H1BVisa", "#NRI", "#GreenCard", "#IndianAmerican", "#USImmigration", "#VisaUpdate", "#OPT", "#USCIS", "#Desi"],
    "nri-world": ["#NRI", "#IndianDiaspora", "#NRILife", "#Desi", "#IndianAmerican", "#SouthAsian", "#DesiAbroad", "#IndianImmigrant", "#NRICommunity"],
    "travel": ["#Travel", "#India", "#IndiaTravel", "#IncredibleIndia", "#TravelIndia", "#DesiTravel", "#IndianDestinations", "#TravelDiaries", "#Wanderlust"],
    "lifestyle-health": ["#Lifestyle", "#Desi", "#NRILife", "#IndianAmerican", "#DesiLifestyle", "#Wellness", "#Health", "#SouthAsian", "#DesiCulture"],
    "markets-finance": ["#Markets", "#India", "#NRI", "#Nifty", "#Sensex", "#BSE", "#NSE", "#IndianMarkets", "#StockMarket", "#Finance", "#NRIInvesting"],
    "technology": ["#Tech", "#India", "#IndianTech", "#Startup", "#H1B", "#SiliconValley", "#AI", "#TechNews", "#IndianEngineers", "#FAANG", "#IndiansinTech"],
    "sports": ["#Cricket", "#India", "#IPL", "#IPL2026", "#IndianCricket", "#BCCI", "#CricketNews", "#Desi", "#TeamIndia"],
    "entertainment": ["#Bollywood", "#Entertainment", "#IndianCinema", "#Desi", "#BollywoodNews", "#Tollywood", "#IndianMovies", "#DesiEntertainment"],
    "food": ["#IndianFood", "#Desi", "#IndianCuisine", "#NRIFood", "#DesiFood", "#IndianCooking", "#Foodie", "#IndianRecipes", "#DesiChef"],
}

def extract_topic_hashtags(headline, max_tags=4):
    """Extract person names, companies, events from headline."""
    tags = []
    # Common patterns to extract
    words = headline.split()
    # Multi-word proper nouns (consecutive capitalized words)
    i = 0
    while i < len(words):
        # Skip common words
        skip = {"the", "a", "an", "in", "on", "at", "to", "for", "of", "and", "or", "is", "are",
                "has", "have", "will", "with", "from", "by", "its", "their", "his", "her",
                "how", "why", "what", "when", "where", "as", "it", "be", "been", "being",
                "can", "could", "would", "should", "may", "might", "after", "before", "new",
                "amid", "over", "into", "not", "but", "up", "out", "all", "top", "key",
                "vs", "set", "big", "more", "most", "first", "last", "next"}
        clean = re.sub(r'[^A-Za-z0-9]', '', words[i])
        if clean and clean[0].isupper() and clean.lower() not in skip and len(clean) > 2:
            name_parts = [clean]
            j = i + 1
            while j < len(words):
                cj = re.sub(r'[^A-Za-z0-9]', '', words[j])
                if cj and cj[0].isupper() and cj.lower() not in skip and len(cj) > 1:
                    name_parts.append(cj)
                    j += 1
                else:
                    break
            tag = ''.join(name_parts)
            if len(tag) > 3 and tag not in tags:
                tags.append(f"#{tag}")
            i = j
        else:
            i += 1
    return tags[:max_tags]

def build_caption(article):
    cat = article.get('category', 'news')
    headline = article['headline']
    slug = article['slug']
    
    cat_tags = CATEGORY_HASHTAGS.get(cat, CATEGORY_HASHTAGS['news'])
    topic_tags = extract_topic_hashtags(headline)
    
    all_tags = list(dict.fromkeys(cat_tags + topic_tags + ["#TheVideshi", "#Reels"]))
    # Max 20 hashtags
    all_tags = all_tags[:20]
    
    caption = f"""{headline}

📰 Read more: https://thevideshi.com/articles/{slug}

{' '.join(all_tags)}"""
    
    return caption

# --- Step 3: Post first article as REEL ---
reel_article = batch[0]
reel_success = False
reel_error = None

print(f"\n=== Generating Reel for: {reel_article['headline'][:60]} ===")

try:
    # Step A: Generate reel video
    result = subprocess.run(
        ["python3", "generate-reel.py", "--slug", reel_article['slug'], "--upload"],
        cwd=os.path.expanduser("~/workspace/the-videshi-news/pipeline"),
        capture_output=True, text=True, timeout=180
    )
    print(f"  generate-reel.py exit code: {result.returncode}")
    if result.stdout:
        print(f"  stdout (last 500 chars): ...{result.stdout[-500:]}")
    if result.stderr:
        print(f"  stderr (last 300 chars): ...{result.stderr[-300:]}")
    
    if result.returncode != 0:
        raise Exception(f"generate-reel.py failed with exit code {result.returncode}")
    
    # Parse supabase URL from output
    reel_url = None
    for line in result.stdout.split('\n'):
        if 'supabase.co/storage' in line and 'http' in line:
            match = re.search(r'(https://[^\s]+supabase\.co/storage/[^\s]+)', line)
            if match:
                reel_url = match.group(1)
                break
    
    if not reel_url:
        raise Exception("Could not find Supabase reel URL in generate-reel.py output")
    
    print(f"  Reel URL: {reel_url}")
    
    # Step A2: Upload cover image
    slug_trunc = reel_article['slug'][:80]
    cover_local = os.path.expanduser(f"~/workspace/the-videshi-news/pipeline/reels/reel-{slug_trunc}-cover.jpg")
    cover_public_url = None
    
    if os.path.exists(cover_local):
        cover_filename = f"reels/{slug_trunc}-cover.jpg"
        with open(cover_local, 'rb') as cf:
            cr = requests.post(
                f"{SUPABASE_URL}/storage/v1/object/article-images/{cover_filename}",
                headers={
                    "apikey": SB_SERVICE_KEY,
                    "Authorization": f"Bearer {SB_SERVICE_KEY}",
                    "Content-Type": "image/jpeg",
                    "x-upsert": "true"
                },
                data=cf.read(),
                timeout=30
            )
        if cr.status_code in (200, 201):
            cover_public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{cover_filename}"
            print(f"  Cover uploaded: {cover_public_url}")
        else:
            print(f"  Cover upload failed: {cr.status_code} {cr.text[:200]}")
    else:
        print(f"  No cover image found at {cover_local}")
    
    # Step B: Create Reel container
    caption = build_caption(reel_article)
    container_data = {
        "video_url": reel_url,
        "media_type": "REELS",
        "caption": caption,
        "access_token": TOKEN
    }
    if cover_public_url:
        container_data["cover_url"] = cover_public_url
    
    print("  Creating Reel container...")
    r = requests.post(f"https://graph.instagram.com/v25.0/{IG_USER_ID}/media",
                      data=container_data, timeout=30)
    rj = r.json()
    print(f"  Container response: {rj}")
    
    if 'id' not in rj:
        raise Exception(f"Failed to create reel container: {rj}")
    
    container_id = rj['id']
    
    # Step C: Wait for processing
    print("  Waiting for video processing...")
    finished = False
    for i in range(18):
        time.sleep(5)
        r_status = requests.get(
            f"https://graph.instagram.com/v25.0/{container_id}",
            params={"fields": "status_code", "access_token": TOKEN},
            timeout=15
        )
        status = r_status.json().get('status_code', 'UNKNOWN')
        print(f"    Poll {i+1}/18: {status}")
        if status == 'FINISHED':
            finished = True
            break
        elif status == 'ERROR':
            raise Exception(f"Video processing failed: {r_status.json()}")
    
    if not finished:
        raise Exception("Video processing timed out after 90 seconds")
    
    # Step D: Publish Reel
    print("  Publishing Reel...")
    r2 = requests.post(f"https://graph.instagram.com/v25.0/{IG_USER_ID}/media_publish",
                       data={"creation_id": container_id, "access_token": TOKEN},
                       timeout=30)
    rj2 = r2.json()
    print(f"  Publish response: {rj2}")
    
    if 'id' in rj2:
        reel_success = True
        print(f"  ✅ Reel published! Media ID: {rj2['id']}")
        
        # Mark as instagrammed
        now_utc = datetime.now(timezone.utc).isoformat()
        patch_r = requests.patch(
            f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{reel_article['id']}",
            headers=headers,
            json={"instagrammed_at": now_utc},
            timeout=15
        )
        print(f"  Supabase update: {patch_r.status_code}")
    else:
        raise Exception(f"Reel publish failed: {rj2}")

except Exception as e:
    reel_error = str(e)
    print(f"  ❌ Reel failed: {e}")

# --- Step 4: Wait between posts ---
if reel_success:
    print("\n  Waiting 30s between posts...")
    time.sleep(30)

# --- Step 5: Post Story (use second article if available, else first) ---
story_article = batch[1] if len(batch) > 1 else batch[0]
# Don't post story of same article if reel already posted for it AND we only have 1 article
if len(batch) == 1 and reel_success:
    print("\n=== Skipping Story (only 1 article, already posted as Reel) ===")
    story_success = False
    story_error = "Skipped - same article as reel"
else:
    story_success = False
    story_error = None
    print(f"\n=== Posting Story for: {story_article['headline'][:60]} ===")
    
    try:
        # Create story container
        r = requests.post(f"https://graph.instagram.com/v25.0/{IG_USER_ID}/media", data={
            "image_url": story_article['image_url'],
            "media_type": "STORIES",
            "access_token": TOKEN
        }, timeout=30)
        rj = r.json()
        print(f"  Story container response: {rj}")
        
        if 'id' not in rj:
            raise Exception(f"Failed to create story container: {rj}")
        
        story_container_id = rj['id']
        
        # Wait for processing
        print("  Waiting 8s for processing...")
        time.sleep(8)
        
        # Publish story
        r2 = requests.post(f"https://graph.instagram.com/v25.0/{IG_USER_ID}/media_publish", data={
            "creation_id": story_container_id,
            "access_token": TOKEN
        }, timeout=30)
        rj2 = r2.json()
        print(f"  Story publish response: {rj2}")
        
        if 'id' in rj2:
            story_success = True
            print(f"  ✅ Story published! Media ID: {rj2['id']}")
            
            # Mark story article as instagrammed too
            now_utc = datetime.now(timezone.utc).isoformat()
            patch_r = requests.patch(
                f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{story_article['id']}",
                headers=headers,
                json={"instagrammed_at": now_utc},
                timeout=15
            )
            print(f"  Supabase update: {patch_r.status_code}")
        else:
            raise Exception(f"Story publish failed: {rj2}")
    
    except Exception as e:
        story_error = str(e)
        print(f"  ❌ Story failed (non-fatal): {e}")

# --- Summary ---
print("\n" + "="*50)
print("SUMMARY")
print("="*50)
print(f"  Reel posted:  {'✅ YES' if reel_success else '❌ NO'} — {reel_article['headline'][:60]}")
if reel_error:
    print(f"    Error: {reel_error}")
print(f"  Story posted: {'✅ YES' if story_success else '❌ NO'} — {story_article['headline'][:60]}")
if story_error:
    print(f"    Error: {story_error}")
print(f"  Articles remaining: {len(articles) - (1 if reel_success else 0) - (1 if story_success else 0)}")
