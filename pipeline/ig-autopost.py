#!/usr/bin/env python3
"""Instagram autopost script for The Videshi — posts Reels + Stories."""

import os, sys, json, time, re, subprocess, requests
from datetime import datetime, timezone

# --- Load credentials ---
env_ig_path = os.path.expanduser("~/workspace/.env.instagram")
env_sb_path = os.path.expanduser("~/workspace/.env.supabase")
env_vite_path = os.path.expanduser("~/workspace/the-videshi-news/.env")

def load_env_file(path):
    d = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            d[k.strip()] = v.strip().strip('"').strip("'")
    return d

ig_env = load_env_file(env_ig_path)
sb_env = load_env_file(env_sb_path)
vite_env = load_env_file(env_vite_path)

IG_USER_ID = ig_env['INSTAGRAM_USER_ID']
TOKEN = ig_env['INSTAGRAM_ACCESS_TOKEN']
IG_APP_SECRET = ig_env['INSTAGRAM_APP_SECRET']
SB_KEY = sb_env['SUPABASE_SERVICE_ROLE_KEY']
SUPABASE_URL = "https://lboecaekpynbpyijrbfz.supabase.co"

print(f"[INFO] IG User ID: {IG_USER_ID}")
print(f"[INFO] Token length: {len(TOKEN)}")

# --- Step 1: Refresh token ---
print("\n[STEP 1] Refreshing Instagram token...")
try:
    r = requests.get("https://graph.instagram.com/refresh_access_token", params={
        "grant_type": "ig_refresh_token",
        "access_token": TOKEN
    }, timeout=30)
    rj = r.json()
    if 'access_token' in rj:
        new_token = rj['access_token']
        if new_token != TOKEN:
            print("[INFO] Token refreshed, updating .env.instagram")
            TOKEN = new_token
            # Rewrite the env file
            with open(env_ig_path, 'r') as f:
                lines = f.readlines()
            with open(env_ig_path, 'w') as f:
                for line in lines:
                    if line.strip().startswith('INSTAGRAM_ACCESS_TOKEN='):
                        f.write(f'INSTAGRAM_ACCESS_TOKEN={TOKEN}\n')
                    else:
                        f.write(line)
            print("[INFO] Token saved.")
        else:
            print("[INFO] Token unchanged after refresh.")
    else:
        print(f"[WARN] Token refresh response: {rj}")
except Exception as e:
    print(f"[WARN] Token refresh failed: {e} — continuing with existing token")

# --- Step 2: Fetch recent unposted articles ---
print("\n[STEP 2] Fetching recent unposted articles...")
headers = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
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
    timeout=30
)

if r.status_code != 200:
    print(f"[ERROR] Supabase fetch failed: {r.status_code} {r.text}")
    sys.exit(1)

articles = r.json()
# Filter out articles with empty image_url
articles = [a for a in articles if a.get('image_url') and a['image_url'].strip()]
print(f"[INFO] Found {len(articles)} unposted articles with images")

if not articles:
    print("[INFO] No articles to post. Done.")
    sys.exit(0)

# Pick up to 2
selected = articles[:2]
for i, a in enumerate(selected):
    print(f"  [{i+1}] {a['headline'][:80]}... (cat={a['category']}, slug={a['slug'][:50]})")

# --- Hashtag mapping ---
CATEGORY_HASHTAGS = {
    "news": ["#India", "#NRI", "#IndiaNews", "#IndianDiaspora", "#BreakingNews", "#DesiNews", "#SouthAsian", "#IndianAmerican", "#NRINews"],
    "immigration": ["#Immigration", "#H1B", "#H1BVisa", "#NRI", "#GreenCard", "#IndianAmerican", "#USImmigration", "#VisaUpdate", "#USCIS", "#Desi"],
    "nri-world": ["#NRI", "#IndianDiaspora", "#NRILife", "#Desi", "#IndianAmerican", "#SouthAsian", "#DesiAbroad", "#NRICommunity"],
    "travel": ["#Travel", "#India", "#IndiaTravel", "#IncredibleIndia", "#TravelIndia", "#DesiTravel", "#Wanderlust"],
    "lifestyle-health": ["#Lifestyle", "#Desi", "#NRILife", "#IndianAmerican", "#DesiLifestyle", "#Wellness", "#Health", "#SouthAsian"],
    "markets-finance": ["#Markets", "#India", "#NRI", "#Nifty", "#Sensex", "#IndianMarkets", "#StockMarket", "#Finance", "#NRIInvesting"],
    "technology": ["#Tech", "#India", "#IndianTech", "#Startup", "#AI", "#TechNews", "#IndianEngineers", "#IndiansinTech"],
    "sports": ["#Cricket", "#India", "#IPL", "#IPL2026", "#IndianCricket", "#BCCI", "#CricketNews", "#Desi", "#TeamIndia"],
    "entertainment": ["#Bollywood", "#Entertainment", "#IndianCinema", "#Desi", "#BollywoodNews", "#DesiEntertainment"],
    "food": ["#IndianFood", "#Desi", "#IndianCuisine", "#NRIFood", "#DesiFood", "#IndianCooking", "#Foodie"]
}

def extract_topic_hashtags(headline, max_tags=4):
    """Extract person/company/event names from headline as hashtags."""
    tags = []
    # Common patterns: capitalize words, remove small words
    words = headline.split()
    # Look for capitalized multi-word names (2-3 consecutive capitalized words)
    i = 0
    while i < len(words):
        w = words[i]
        # Skip short common words
        if w.lower() in ('the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'and', 'or', 'but', 'is', 'are',
                         'was', 'were', 'has', 'have', 'had', 'with', 'from', 'by', 'as', 'its', 'it', 'be',
                         'will', 'can', 'could', 'would', 'should', 'may', 'might', 'do', 'does', 'did',
                         'not', 'no', 'yes', 'how', 'why', 'what', 'when', 'where', 'who', 'which',
                         'new', 'over', 'after', 'amid', 'into', 'up', 'out', 'says', 'said'):
            i += 1
            continue
        # Clean punctuation
        clean = re.sub(r'[^A-Za-z0-9]', '', w)
        if len(clean) >= 3 and clean[0].isupper():
            # Check if next word is also capitalized (multi-word name)
            if i + 1 < len(words):
                next_clean = re.sub(r'[^A-Za-z0-9]', '', words[i+1])
                if len(next_clean) >= 2 and next_clean[0].isupper() and next_clean.lower() not in ('the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'and', 'or'):
                    combined = clean + next_clean
                    tags.append(f"#{combined}")
                    i += 2
                    continue
            tags.append(f"#{clean}")
        i += 1
    # Deduplicate and limit
    seen = set()
    result = []
    for t in tags:
        if t.lower() not in seen and len(t) > 3:
            seen.add(t.lower())
            result.append(t)
    return result[:max_tags]

def build_caption(article):
    cat = article.get('category', 'news')
    cat_tags = CATEGORY_HASHTAGS.get(cat, CATEGORY_HASHTAGS['news'])
    topic_tags = extract_topic_hashtags(article['headline'])
    
    all_tags = list(cat_tags) + topic_tags + ["#TheVideshi", "#Reels"]
    # Deduplicate preserving order
    seen = set()
    unique_tags = []
    for t in all_tags:
        if t.lower() not in seen:
            seen.add(t.lower())
            unique_tags.append(t)
    # Max 20
    unique_tags = unique_tags[:20]
    
    caption = f"{article['headline']}\n\n📰 Read more: https://thevideshi.com/articles/{article['slug']}\n\n{' '.join(unique_tags)}"
    return caption

# --- Step 3: Post first article as Reel ---
reel_posted = False
reel_article = selected[0]
print(f"\n[STEP 3] Generating Reel for: {reel_article['headline'][:80]}...")

try:
    # Step A: Generate reel video
    result = subprocess.run(
        ["python3", "generate-reel.py", "--slug", reel_article['slug'], "--upload"],
        cwd=os.path.expanduser("~/workspace/the-videshi-news/pipeline"),
        capture_output=True, text=True, timeout=180
    )
    print(f"[INFO] Reel generator exit code: {result.returncode}")
    if result.stdout:
        print(f"[INFO] Reel stdout (last 500 chars): {result.stdout[-500:]}")
    if result.stderr:
        print(f"[WARN] Reel stderr (last 300 chars): {result.stderr[-300:]}")
    
    # Find the Supabase URL in output
    reel_url = None
    for line in result.stdout.split('\n'):
        if 'supabase.co/storage' in line:
            match = re.search(r'(https://[^\s]+supabase\.co/storage/[^\s]+)', line)
            if match:
                reel_url = match.group(1)
                break
    
    if not reel_url:
        print("[ERROR] Could not find reel URL in generator output")
        raise Exception("No reel URL found")
    
    print(f"[INFO] Reel URL: {reel_url}")
    
    # Step A2: Upload cover image
    cover_slug = reel_article['slug'][:80]
    cover_local = os.path.expanduser(f"~/workspace/the-videshi-news/pipeline/reels/reel-{cover_slug}-cover.jpg")
    cover_public_url = None
    if os.path.exists(cover_local):
        cover_filename = f"reels/{cover_slug}-cover.jpg"
        with open(cover_local, 'rb') as cf:
            cr = requests.post(
                f"{SUPABASE_URL}/storage/v1/object/article-images/{cover_filename}",
                headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}",
                         "Content-Type": "image/jpeg", "x-upsert": "true"},
                data=cf.read(),
                timeout=60
            )
        if cr.status_code in (200, 201):
            cover_public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{cover_filename}"
            print(f"[INFO] Cover uploaded: {cover_public_url}")
        else:
            print(f"[WARN] Cover upload failed: {cr.status_code} {cr.text[:200]}")
    else:
        print(f"[INFO] No cover image found at {cover_local}")
    
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
    
    print("[INFO] Creating Reel container...")
    r = requests.post(f"https://graph.instagram.com/v25.0/{IG_USER_ID}/media", data=container_data, timeout=30)
    rj = r.json()
    print(f"[INFO] Container response: {rj}")
    
    if 'id' not in rj:
        raise Exception(f"Container creation failed: {rj}")
    
    container_id = rj['id']
    
    # Step C: Wait for processing
    print("[INFO] Waiting for video processing...")
    finished = False
    for i in range(18):
        time.sleep(5)
        r_status = requests.get(
            f"https://graph.instagram.com/v25.0/{container_id}",
            params={"fields": "status_code", "access_token": TOKEN},
            timeout=15
        )
        status = r_status.json().get('status_code', 'UNKNOWN')
        print(f"  Poll {i+1}/18: status={status}")
        if status == 'FINISHED':
            finished = True
            break
        elif status == 'ERROR':
            raise Exception(f"Video processing failed: {r_status.json()}")
    
    if not finished:
        print("[WARN] Video processing timed out after 90 seconds")
        raise Exception("Video processing timeout")
    
    # Step D: Publish Reel
    print("[INFO] Publishing Reel...")
    r2 = requests.post(f"https://graph.instagram.com/v25.0/{IG_USER_ID}/media_publish", data={
        "creation_id": container_id,
        "access_token": TOKEN
    }, timeout=30)
    r2j = r2.json()
    print(f"[INFO] Publish response: {r2j}")
    
    if 'id' in r2j:
        reel_posted = True
        print(f"[SUCCESS] Reel posted! Media ID: {r2j['id']}")
        
        # Update instagrammed_at
        now_utc = datetime.now(timezone.utc).isoformat()
        patch_r = requests.patch(
            f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{reel_article['id']}",
            headers={**headers, "Prefer": "return=minimal"},
            json={"instagrammed_at": now_utc},
            timeout=15
        )
        print(f"[INFO] Supabase update: {patch_r.status_code}")
    else:
        print(f"[ERROR] Reel publish failed: {r2j}")

except Exception as e:
    print(f"[ERROR] Reel posting failed: {e}")

# --- Step 4: Post Story (use second article if available, else first) ---
story_posted = False
story_article = selected[1] if len(selected) > 1 else selected[0]
# Don't post story for the same article if only 1
if len(selected) < 2:
    print("\n[STEP 4] Only 1 article — skipping Story (same as Reel)")
else:
    print(f"\n[STEP 4] Posting Story for: {story_article['headline'][:80]}...")
    
    # Wait between posts
    if reel_posted:
        print("[INFO] Waiting 30 seconds between posts...")
        time.sleep(30)
    
    try:
        # Create story container
        r = requests.post(f"https://graph.instagram.com/v25.0/{IG_USER_ID}/media", data={
            "image_url": story_article['image_url'],
            "media_type": "STORIES",
            "access_token": TOKEN
        }, timeout=30)
        rj = r.json()
        print(f"[INFO] Story container response: {rj}")
        
        if 'id' not in rj:
            raise Exception(f"Story container creation failed: {rj}")
        
        container_id = rj['id']
        
        # Wait for processing
        print("[INFO] Waiting 8 seconds for story processing...")
        time.sleep(8)
        
        # Publish story
        r2 = requests.post(f"https://graph.instagram.com/v25.0/{IG_USER_ID}/media_publish", data={
            "creation_id": container_id,
            "access_token": TOKEN
        }, timeout=30)
        r2j = r2.json()
        print(f"[INFO] Story publish response: {r2j}")
        
        if 'id' in r2j:
            story_posted = True
            print(f"[SUCCESS] Story posted! Media ID: {r2j['id']}")
            
            # Update instagrammed_at for story article too
            now_utc = datetime.now(timezone.utc).isoformat()
            patch_r = requests.patch(
                f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{story_article['id']}",
                headers={**headers, "Prefer": "return=minimal"},
                json={"instagrammed_at": now_utc},
                timeout=15
            )
            print(f"[INFO] Supabase update: {patch_r.status_code}")
        else:
            print(f"[ERROR] Story publish failed: {r2j}")
    
    except Exception as e:
        print(f"[ERROR] Story posting failed: {e}")

# --- Summary ---
print(f"\n{'='*50}")
print(f"SUMMARY")
print(f"{'='*50}")
print(f"Reel posted:  {'YES' if reel_posted else 'NO'}")
print(f"Story posted: {'YES' if story_posted else 'NO'}")
if reel_posted:
    print(f"Reel article: {reel_article['headline'][:80]}")
if story_posted:
    print(f"Story article: {story_article['headline'][:80]}")
print(f"{'='*50}")
