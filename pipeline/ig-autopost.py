#!/usr/bin/env python3
"""Instagram auto-poster for The Videshi — posts Reels + Stories."""

import os, sys, re, json, time, subprocess, hashlib, hmac
from datetime import datetime, timezone

import requests

# ── Load credentials ──────────────────────────────────────────────────
def load_env_file(path):
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

ig_env = load_env_file('~/workspace/.env.instagram')
sb_env = load_env_file('~/workspace/.env.supabase')
app_env = load_env_file('~/workspace/the-videshi-news/.env')

IG_USER_ID = ig_env['INSTAGRAM_USER_ID']
IG_TOKEN = ig_env['INSTAGRAM_ACCESS_TOKEN']
IG_APP_SECRET = ig_env.get('INSTAGRAM_APP_SECRET', ig_env.get('META_APP_SECRET', ''))
SB_URL = 'https://lboecaekpyanbpyijrbfz.supabase.co'
SB_URL = 'https://lboecaekpynbpyijrbfz.supabase.co'
SB_SERVICE_KEY = sb_env['SUPABASE_SERVICE_ROLE_KEY']

print(f"[INFO] IG User ID: {IG_USER_ID}")
print(f"[INFO] Token (last 8): ...{IG_TOKEN[-8:]}")

# ── Step 1: Refresh token ────────────────────────────────────────────
print("\n[STEP 1] Refreshing Instagram access token...")
try:
    r = requests.get("https://graph.instagram.com/refresh_access_token", params={
        "grant_type": "ig_refresh_token",
        "access_token": IG_TOKEN
    }, timeout=15)
    rj = r.json()
    if 'access_token' in rj:
        new_token = rj['access_token']
        if new_token != IG_TOKEN:
            print(f"[INFO] Token refreshed (new last 8: ...{new_token[-8:]})")
            # Update the env file
            env_path = os.path.expanduser('~/workspace/.env.instagram')
            with open(env_path) as f:
                content = f.read()
            content = content.replace(IG_TOKEN, new_token)
            with open(env_path, 'w') as f:
                f.write(content)
            IG_TOKEN = new_token
            print("[INFO] Token saved to .env.instagram")
        else:
            print("[INFO] Token unchanged after refresh")
    else:
        print(f"[WARN] Token refresh response: {rj}")
except Exception as e:
    print(f"[WARN] Token refresh failed: {e} — continuing with existing token")

# ── Step 2: Fetch unposted articles ──────────────────────────────────
print("\n[STEP 2] Fetching unposted articles from Supabase...")
headers = {
    "apikey": SB_SERVICE_KEY,
    "Authorization": f"Bearer {SB_SERVICE_KEY}",
    "Content-Type": "application/json"
}
resp = requests.get(
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
if resp.status_code != 200:
    print(f"[ERROR] Supabase fetch failed: {resp.status_code} {resp.text[:500]}")
    sys.exit(1)

articles = resp.json()
print(f"[INFO] Found {len(articles)} unposted articles with images")

if not articles:
    print("[INFO] No articles to post. Exiting.")
    sys.exit(0)

# Pick up to 2 articles
batch = articles[:2]
for i, a in enumerate(batch):
    print(f"  [{i+1}] {a['category']}: {a['headline'][:80]}...")

# ── Hashtag helper ────────────────────────────────────────────────────
CATEGORY_HASHTAGS = {
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

def extract_topic_hashtags(headline, max_tags=4):
    """Extract person/company/event names from headline for hashtags."""
    tags = []
    # Common patterns — proper nouns, multi-word names
    # Remove common words and extract capitalized sequences
    words = headline.split()
    i = 0
    while i < len(words) and len(tags) < max_tags:
        w = words[i]
        # Skip common lowercase words
        if w[0].isupper() and len(w) > 2 and w not in {'The', 'And', 'For', 'New', 'How', 'Why', 'What', 'With', 'From', 'After', 'Over', 'Will', 'Has', 'Can', 'May', 'But', 'Its', 'His', 'Her', 'Not', 'Are', 'Was', 'Top', 'Best', 'All'}:
            # Try to grab multi-word names
            name = w
            j = i + 1
            while j < len(words) and words[j][0:1].isupper() and words[j] not in {'The', 'And', 'For', 'New', 'In', 'On', 'At', 'To', 'Is', 'Of'}:
                name += words[j]
                j += 1
            # Clean punctuation
            clean = re.sub(r'[^A-Za-z0-9]', '', name)
            if len(clean) > 3 and clean not in {'India', 'Indian', 'American', 'United', 'States'}:
                tag = f"#{clean}"
                if tag not in tags:
                    tags.append(tag)
            i = j
        else:
            i += 1
    return tags

def build_caption(article):
    headline = article['headline']
    slug = article['slug']
    cat = article.get('category', 'news').lower()
    
    cat_tags = CATEGORY_HASHTAGS.get(cat, CATEGORY_HASHTAGS['news'])
    topic_tags = extract_topic_hashtags(headline)
    
    all_tags = cat_tags.split() + topic_tags + ["#TheVideshi", "#Reels"]
    # Deduplicate and limit to 20
    seen = set()
    unique_tags = []
    for t in all_tags:
        if t.lower() not in seen:
            seen.add(t.lower())
            unique_tags.append(t)
    unique_tags = unique_tags[:20]
    
    caption = f"""{headline}

📰 Read more: https://thevideshi.com/articles/{slug}

{' '.join(unique_tags)}"""
    
    return caption

# ── Step 3: Generate & Post Reel for first article ────────────────────
reel_posted = False
story_posted = False
reel_article = batch[0]
story_article = batch[1] if len(batch) > 1 else batch[0]

print(f"\n[STEP 3] Generating Reel for: {reel_article['headline'][:60]}...")
print(f"  slug: {reel_article['slug']}")

try:
    result = subprocess.run(
        ["python3", "generate-reel.py", "--slug", reel_article['slug'], "--upload"],
        cwd=os.path.expanduser("~/workspace/the-videshi-news/pipeline"),
        capture_output=True, text=True, timeout=180
    )
    print(f"[INFO] generate-reel.py exit code: {result.returncode}")
    if result.stdout:
        print(f"[INFO] stdout (last 500): {result.stdout[-500:]}")
    if result.stderr:
        print(f"[WARN] stderr (last 300): {result.stderr[-300:]}")
    
    # Parse the Supabase URL from output
    reel_url = None
    for line in result.stdout.split('\n'):
        if 'supabase.co/storage/' in line:
            match = re.search(r'(https://[^\s]+supabase\.co/storage/[^\s]+)', line)
            if match:
                reel_url = match.group(1)
                break
    
    if not reel_url:
        print("[ERROR] Could not find reel URL in generate-reel.py output")
        # Try to find the file directly
        slug_short = reel_article['slug'][:80]
        local_reel = os.path.expanduser(f"~/workspace/the-videshi-news/pipeline/reels/reel-{slug_short}.mp4")
        if os.path.exists(local_reel):
            print(f"[INFO] Found local reel file: {local_reel}")
            # Upload it ourselves
            reel_filename = f"reels/{slug_short}.mp4"
            with open(local_reel, 'rb') as rf:
                ur = requests.post(
                    f"{SB_URL}/storage/v1/object/article-images/{reel_filename}",
                    headers={"apikey": SB_SERVICE_KEY, "Authorization": f"Bearer {SB_SERVICE_KEY}",
                             "Content-Type": "video/mp4", "x-upsert": "true"},
                    data=rf.read(),
                    timeout=60
                )
            if ur.status_code in (200, 201):
                reel_url = f"{SB_URL}/storage/v1/object/public/article-images/{reel_filename}"
                print(f"[INFO] Uploaded reel to: {reel_url}")
            else:
                print(f"[ERROR] Failed to upload reel: {ur.status_code} {ur.text[:200]}")
        else:
            print(f"[ERROR] No local reel file at {local_reel}")
    
    if reel_url:
        # Upload cover image if exists
        cover_local = os.path.expanduser(f"~/workspace/the-videshi-news/pipeline/reels/reel-{reel_article['slug'][:80]}-cover.jpg")
        cover_public_url = None
        if os.path.exists(cover_local):
            cover_filename = f"reels/{reel_article['slug'][:80]}-cover.jpg"
            with open(cover_local, 'rb') as cf:
                cr = requests.post(
                    f"{SB_URL}/storage/v1/object/article-images/{cover_filename}",
                    headers={"apikey": SB_SERVICE_KEY, "Authorization": f"Bearer {SB_SERVICE_KEY}",
                             "Content-Type": "image/jpeg", "x-upsert": "true"},
                    data=cf.read(),
                    timeout=30
                )
            if cr.status_code in (200, 201):
                cover_public_url = f"{SB_URL}/storage/v1/object/public/article-images/{cover_filename}"
                print(f"[INFO] Cover image uploaded: {cover_public_url}")
            else:
                print(f"[WARN] Cover upload failed: {cr.status_code}")
        
        # Create Reel container
        caption = build_caption(reel_article)
        print(f"\n[STEP 3B] Creating Reel container on Instagram...")
        container_data = {
            "video_url": reel_url,
            "media_type": "REELS",
            "caption": caption,
            "access_token": IG_TOKEN
        }
        if cover_public_url:
            container_data["cover_url"] = cover_public_url
        
        r = requests.post(f"https://graph.instagram.com/v25.0/{IG_USER_ID}/media",
                          data=container_data, timeout=30)
        rj = r.json()
        print(f"[INFO] Container response: {rj}")
        
        if 'id' in rj:
            container_id = rj['id']
            
            # Poll for FINISHED
            print("[STEP 3C] Waiting for video processing...")
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
                    print(f"[ERROR] Video processing failed: {r_status.json()}")
                    break
            
            if finished:
                # Publish
                print("[STEP 3D] Publishing Reel...")
                r2 = requests.post(
                    f"https://graph.instagram.com/v25.0/{IG_USER_ID}/media_publish",
                    data={"creation_id": container_id, "access_token": IG_TOKEN},
                    timeout=30
                )
                r2j = r2.json()
                print(f"[INFO] Publish response: {r2j}")
                
                if 'id' in r2j:
                    reel_posted = True
                    print(f"[SUCCESS] Reel published! Media ID: {r2j['id']}")
                    
                    # Mark as instagrammed
                    now_utc = datetime.now(timezone.utc).isoformat()
                    patch_r = requests.patch(
                        f"{SB_URL}/rest/v1/p2_articles?id=eq.{reel_article['id']}",
                        headers=headers,
                        json={"instagrammed_at": now_utc},
                        timeout=10
                    )
                    print(f"[INFO] Marked instagrammed_at: {patch_r.status_code}")
                else:
                    print(f"[ERROR] Reel publish failed: {r2j}")
            else:
                print("[ERROR] Video processing did not finish in time")
        else:
            print(f"[ERROR] Container creation failed: {rj}")
    else:
        print("[ERROR] No reel URL available — skipping reel post")

except subprocess.TimeoutExpired:
    print("[ERROR] generate-reel.py timed out after 180s")
except Exception as e:
    print(f"[ERROR] Reel generation/posting failed: {e}")
    import traceback
    traceback.print_exc()

# ── Step 4: Post Story ────────────────────────────────────────────────
print(f"\n[STEP 4] Posting Story for: {story_article['headline'][:60]}...")
print(f"  image_url: {story_article['image_url'][:100]}...")

# Wait between posts
if reel_posted:
    print("[INFO] Waiting 30s between posts...")
    time.sleep(30)

try:
    r = requests.post(f"https://graph.instagram.com/v25.0/{IG_USER_ID}/media", data={
        "image_url": story_article['image_url'],
        "media_type": "STORIES",
        "access_token": IG_TOKEN
    }, timeout=30)
    rj = r.json()
    print(f"[INFO] Story container response: {rj}")
    
    if 'id' in rj:
        story_container_id = rj['id']
        print("[INFO] Waiting 8s for story processing...")
        time.sleep(8)
        
        r2 = requests.post(
            f"https://graph.instagram.com/v25.0/{IG_USER_ID}/media_publish",
            data={"creation_id": story_container_id, "access_token": IG_TOKEN},
            timeout=30
        )
        r2j = r2.json()
        print(f"[INFO] Story publish response: {r2j}")
        
        if 'id' in r2j:
            story_posted = True
            print(f"[SUCCESS] Story published! Media ID: {r2j['id']}")
            
            # Mark story article as instagrammed too (if different from reel)
            if story_article['id'] != reel_article['id']:
                now_utc = datetime.now(timezone.utc).isoformat()
                patch_r = requests.patch(
                    f"{SB_URL}/rest/v1/p2_articles?id=eq.{story_article['id']}",
                    headers=headers,
                    json={"instagrammed_at": now_utc},
                    timeout=10
                )
                print(f"[INFO] Marked story article instagrammed_at: {patch_r.status_code}")
        else:
            print(f"[WARN] Story publish failed: {r2j}")
    else:
        print(f"[WARN] Story container creation failed: {rj}")

except Exception as e:
    print(f"[WARN] Story posting failed: {e}")

# ── Summary ───────────────────────────────────────────────────────────
print(f"\n{'='*50}")
print(f"SUMMARY")
print(f"{'='*50}")
print(f"Reel posted:  {'✅ YES' if reel_posted else '❌ NO'}")
print(f"  Article: {reel_article['headline'][:60]}")
print(f"Story posted: {'✅ YES' if story_posted else '❌ NO'}")
print(f"  Article: {story_article['headline'][:60]}")
print(f"{'='*50}")
