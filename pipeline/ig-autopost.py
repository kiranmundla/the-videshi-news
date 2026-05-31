#!/usr/bin/env python3
"""Instagram autopost script for The Videshi — posts Reels + Stories."""

import os
import re
import sys
import json
import time
import subprocess
import requests
from datetime import datetime, timezone

# === Load environment ===
def load_env_file(path):
    """Load key=value pairs from a file."""
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

IG_USER_ID = ig_env['INSTAGRAM_USER_ID']
IG_TOKEN = ig_env['INSTAGRAM_ACCESS_TOKEN']
IG_APP_SECRET = ig_env.get('INSTAGRAM_APP_SECRET', '')
SB_SERVICE_KEY = sb_env['SUPABASE_SERVICE_ROLE_KEY']
SUPABASE_URL = "https://lboecaekpynbpyijrbfz.supabase.co"

new_token = None

# === Step 1: Refresh token ===
print("=== Refreshing Instagram token ===")
try:
    r = requests.get("https://graph.instagram.com/refresh_access_token", params={
        "grant_type": "ig_refresh_token",
        "access_token": IG_TOKEN
    }, timeout=15)
    rj = r.json()
    if 'access_token' in rj:
        new_token = rj['access_token']
        IG_TOKEN = new_token
        print(f"Token refreshed. Expires in {rj.get('expires_in', '?')} seconds.")
    else:
        print(f"Token refresh response (no new token): {rj}")
except Exception as e:
    print(f"Token refresh failed (non-fatal): {e}")

# === Step 2: Fetch unposted articles ===
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
    print(f"ERROR: Unexpected response: {articles}")
    sys.exit(1)

print(f"Found {len(articles)} unposted articles with images")

if not articles:
    print("No articles to post. Done.")
    sys.exit(0)

# Pick up to 2
batch = articles[:2]
for i, a in enumerate(batch):
    print(f"  [{i+1}] {a['category']}: {a['headline'][:80]}")

# === Hashtag mapping ===
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

def extract_topic_hashtags(headline):
    """Extract 2-4 topic-specific hashtags from the headline."""
    tags = []
    # Known person names
    persons = {
        "Modi": "#Modi #NarendraModi", "Virat Kohli": "#ViratKohli #Kohli",
        "Shah Rukh Khan": "#ShahRukhKhan #SRK", "Rohit Sharma": "#RohitSharma",
        "Bumrah": "#JaspritBumrah", "Dhoni": "#MSDhoni", "Sachin": "#SachinTendulkar",
        "Hardik Pandya": "#HardikPandya", "Trump": "#Trump", "Rahul Gandhi": "#RahulGandhi",
        "Elon Musk": "#ElonMusk", "Sundar Pichai": "#SundarPichai", "Satya Nadella": "#SatyaNadella",
        "Sam Altman": "#SamAltman", "Amit Shah": "#AmitShah", "Jaishankar": "#Jaishankar",
        "Adani": "#Adani", "Ambani": "#Ambani", "Jensen Huang": "#JensenHuang",
        "Zuckerberg": "#Zuckerberg", "Tim Cook": "#TimCook", "Bill Gates": "#BillGates",
        "Kejriwal": "#Kejriwal", "Yogi": "#YogiAdityanath",
        "Rishi Sunak": "#RishiSunak", "Vivek Ramaswamy": "#VivekRamaswamy",
        "Neeraj Chopra": "#NeerajChopra", "PV Sindhu": "#PVSindhu",
        "Kohli": "#ViratKohli", "H-1B": "#H1BVisa", "H1B": "#H1BVisa",
        "IPL": "#IPL2026", "T20": "#T20WorldCup",
        "Infosys": "#Infosys", "TCS": "#TCS", "Wipro": "#Wipro",
        "Google": "#Google", "Apple": "#Apple", "Microsoft": "#Microsoft",
        "Tesla": "#Tesla", "Meta": "#Meta", "Amazon": "#Amazon", "NVIDIA": "#NVIDIA",
        "Mumbai": "#Mumbai", "Delhi": "#Delhi", "Bengaluru": "#Bengaluru",
        "Chennai": "#Chennai", "Hyderabad": "#Hyderabad", "Kolkata": "#Kolkata",
        "New York": "#NewYork", "Silicon Valley": "#SiliconValley",
        "Bollywood": "#Bollywood", "BCCI": "#BCCI", "ICC": "#ICC",
        "AI": "#AI #ArtificialIntelligence", "ChatGPT": "#ChatGPT",
        "Sensex": "#Sensex", "Nifty": "#Nifty",
        "Diljit": "#DiljitDosanjh", "Priyanka Chopra": "#PriyankaChopra",
        "Alia Bhatt": "#AliaBhatt", "Deepika": "#DeepikaPadukone",
        "Ranveer": "#RanveerSingh",
    }
    for name, tag in persons.items():
        if name.lower() in headline.lower():
            for t in tag.split():
                if t not in tags:
                    tags.append(t)
    return tags[:4]

def build_caption(article):
    headline = article['headline']
    slug = article['slug']
    cat = article.get('category', 'news')
    
    cat_tags = CATEGORY_HASHTAGS.get(cat, CATEGORY_HASHTAGS['news'])
    topic_tags = extract_topic_hashtags(headline)
    
    all_tags = cat_tags.split() + topic_tags + ["#TheVideshi", "#Reels"]
    # Deduplicate preserving order
    seen = set()
    unique_tags = []
    for t in all_tags:
        tl = t.lower()
        if tl not in seen:
            seen.add(tl)
            unique_tags.append(t)
    # Cap at 20
    unique_tags = unique_tags[:20]
    
    caption = f"""{headline}

📰 Read more: https://thevideshi.com/articles/{slug}

{' '.join(unique_tags)}"""
    
    return caption

# === Step 3: Post first article as REEL ===
reel_posted = False
reel_article = batch[0]
story_article = batch[1] if len(batch) > 1 else batch[0]

print(f"\n=== Generating Reel for: {reel_article['headline'][:70]} ===")

# Step A: Generate reel video
try:
    result = subprocess.run(
        ["python3", "generate-reel.py", "--slug", reel_article['slug'], "--upload"],
        cwd=os.path.expanduser("~/workspace/the-videshi-news/pipeline"),
        capture_output=True, text=True, timeout=180
    )
    print(f"Reel generator exit code: {result.returncode}")
    print(f"STDOUT:\n{result.stdout[-2000:]}")
    if result.stderr:
        print(f"STDERR:\n{result.stderr[-1000:]}")
    
    # Parse Supabase URL from output
    reel_url = None
    for line in result.stdout.split('\n'):
        if 'supabase.co/storage' in line:
            match = re.search(r'(https://[^\s"\']+supabase\.co/storage/[^\s"\']+)', line)
            if match:
                reel_url = match.group(1)
                break
    
    if not reel_url:
        print("ERROR: Could not find reel URL in generator output")
        # Try looking for the file directly
        slug_short = reel_article['slug'][:80]
        expected_file = f"reels/reel-{slug_short}.mp4"
        local_path = os.path.expanduser(f"~/workspace/the-videshi-news/pipeline/{expected_file}")
        if os.path.exists(local_path):
            print(f"Found local file: {local_path}, uploading manually...")
            with open(local_path, 'rb') as vf:
                upload_r = requests.post(
                    f"{SUPABASE_URL}/storage/v1/object/article-images/{expected_file}",
                    headers={
                        "apikey": SB_SERVICE_KEY,
                        "Authorization": f"Bearer {SB_SERVICE_KEY}",
                        "Content-Type": "video/mp4",
                        "x-upsert": "true"
                    },
                    data=vf.read(),
                    timeout=60
                )
            if upload_r.status_code in (200, 201):
                reel_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{expected_file}"
                print(f"Uploaded reel: {reel_url}")
            else:
                print(f"Upload failed: {upload_r.status_code} {upload_r.text}")
    
    if reel_url:
        # Step A2: Upload cover image
        cover_local = os.path.expanduser(f"~/workspace/the-videshi-news/pipeline/reels/reel-{reel_article['slug'][:80]}-cover.jpg")
        cover_public_url = None
        if os.path.exists(cover_local):
            cover_filename = f"reels/{reel_article['slug'][:80]}-cover.jpg"
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
                print(f"Cover uploaded: {cover_public_url}")
            else:
                print(f"Cover upload failed: {cr.status_code} {cr.text}")
        else:
            print(f"No cover image found at {cover_local}")
        
        # Step B: Create Reel container
        caption = build_caption(reel_article)
        print(f"\nCaption ({len(caption)} chars):\n{caption[:200]}...")
        
        container_data = {
            "video_url": reel_url,
            "media_type": "REELS",
            "caption": caption,
            "access_token": IG_TOKEN
        }
        if cover_public_url:
            container_data["cover_url"] = cover_public_url
        
        print("\nCreating Reel container...")
        r = requests.post(
            f"https://graph.instagram.com/v25.0/{IG_USER_ID}/media",
            data=container_data,
            timeout=30
        )
        rj = r.json()
        print(f"Container response: {rj}")
        
        if 'id' in rj:
            container_id = rj['id']
            
            # Step C: Poll for processing
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
                    print(f"  ERROR in processing: {r_status.json()}")
                    break
            
            if finished:
                # Step D: Publish
                print("Publishing Reel...")
                r2 = requests.post(
                    f"https://graph.instagram.com/v25.0/{IG_USER_ID}/media_publish",
                    data={
                        "creation_id": container_id,
                        "access_token": IG_TOKEN
                    },
                    timeout=30
                )
                pub_result = r2.json()
                print(f"Publish response: {pub_result}")
                
                if 'id' in pub_result:
                    reel_posted = True
                    print(f"✅ Reel published! Media ID: {pub_result['id']}")
                    
                    # Mark as instagrammed
                    now_utc = datetime.now(timezone.utc).isoformat()
                    patch_r = requests.patch(
                        f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{reel_article['id']}",
                        headers=headers,
                        json={"instagrammed_at": now_utc},
                        timeout=15
                    )
                    print(f"Supabase update: {patch_r.status_code}")
                else:
                    print(f"❌ Reel publish failed: {pub_result}")
            else:
                print("❌ Video processing did not finish in time")
        else:
            print(f"❌ Container creation failed: {rj}")
    else:
        print("❌ No reel URL available, skipping reel post")

except subprocess.TimeoutExpired:
    print("❌ Reel generation timed out (180s)")
except Exception as e:
    print(f"❌ Reel error: {e}")
    import traceback
    traceback.print_exc()

# === Step 4: Wait between posts ===
if reel_posted:
    print("\nWaiting 30 seconds before story...")
    time.sleep(30)

# === Step 5: Post Story ===
story_posted = False
print(f"\n=== Posting Story for: {story_article['headline'][:70]} ===")

try:
    story_image = story_article.get('image_url', '')
    if not story_image:
        print("❌ No image URL for story article")
    else:
        print(f"Story image: {story_image[:100]}")
        
        # Create story container
        r = requests.post(
            f"https://graph.instagram.com/v25.0/{IG_USER_ID}/media",
            data={
                "image_url": story_image,
                "media_type": "STORIES",
                "access_token": IG_TOKEN
            },
            timeout=30
        )
        rj = r.json()
        print(f"Story container: {rj}")
        
        if 'id' in rj:
            container_id = rj['id']
            
            # Wait for processing
            print("Waiting 8 seconds for story processing...")
            time.sleep(8)
            
            # Publish
            r2 = requests.post(
                f"https://graph.instagram.com/v25.0/{IG_USER_ID}/media_publish",
                data={
                    "creation_id": container_id,
                    "access_token": IG_TOKEN
                },
                timeout=30
            )
            pub_result = r2.json()
            print(f"Story publish: {pub_result}")
            
            if 'id' in pub_result:
                story_posted = True
                print(f"✅ Story published! Media ID: {pub_result['id']}")
                
                # Mark story article as instagrammed too (if different from reel)
                if story_article['id'] != reel_article['id']:
                    now_utc = datetime.now(timezone.utc).isoformat()
                    patch_r = requests.patch(
                        f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{story_article['id']}",
                        headers=headers,
                        json={"instagrammed_at": now_utc},
                        timeout=15
                    )
                    print(f"Supabase update: {patch_r.status_code}")
            else:
                print(f"❌ Story publish failed: {pub_result}")
        else:
            print(f"❌ Story container failed: {rj}")

except Exception as e:
    print(f"❌ Story error (non-fatal): {e}")

# === Step 6: Save refreshed token ===
if new_token:
    print("\n=== Saving refreshed token ===")
    env_path = os.path.expanduser('~/workspace/.env.instagram')
    with open(env_path, 'r') as f:
        content = f.read()
    # Replace the token line
    content = re.sub(
        r'INSTAGRAM_ACCESS_TOKEN=.*',
        f'INSTAGRAM_ACCESS_TOKEN={new_token}',
        content
    )
    with open(env_path, 'w') as f:
        f.write(content)
    print("Token saved.")

# === Summary ===
print(f"\n{'='*50}")
print(f"SUMMARY")
print(f"{'='*50}")
print(f"Reel posted:  {'✅ YES' if reel_posted else '❌ NO'}")
print(f"  Article: {reel_article['headline'][:60]}")
print(f"Story posted: {'✅ YES' if story_posted else '❌ NO'}")
print(f"  Article: {story_article['headline'][:60]}")
print(f"Token refreshed: {'✅ YES' if new_token else '⚠️ NO (using existing)'}")
