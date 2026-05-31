#!/usr/bin/env python3
"""Instagram autopost for The Videshi — posts Reels + Stories."""

import os, sys, json, time, re, subprocess, requests
from datetime import datetime, timezone

# --- Load credentials ---
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
videshi_env = load_env_file('~/workspace/the-videshi-news/.env')

IG_USER_ID = ig_env['INSTAGRAM_USER_ID']
IG_TOKEN = ig_env['INSTAGRAM_ACCESS_TOKEN']
IG_APP_SECRET = ig_env['INSTAGRAM_APP_SECRET']
SB_URL = 'https://lboecaekpynbpyijrbfz.supabase.co'
SB_SERVICE_KEY = sb_env['SUPABASE_SERVICE_ROLE_KEY']

print(f"IG User ID: {IG_USER_ID}")
print(f"Token length: {len(IG_TOKEN)}")

# --- Step 1: Refresh token ---
print("\n=== Refreshing Instagram token ===")
try:
    r = requests.get("https://graph.instagram.com/refresh_access_token", params={
        "grant_type": "ig_refresh_token",
        "access_token": IG_TOKEN
    }, timeout=30)
    rj = r.json()
    if 'access_token' in rj:
        new_token = rj['access_token']
        if new_token != IG_TOKEN:
            # Update the env file
            env_path = os.path.expanduser('~/workspace/.env.instagram')
            with open(env_path) as f:
                content = f.read()
            content = content.replace(IG_TOKEN, new_token)
            with open(env_path, 'w') as f:
                f.write(content)
            IG_TOKEN = new_token
            print(f"Token refreshed and saved (expires in {rj.get('expires_in', '?')}s)")
        else:
            print(f"Token unchanged (expires in {rj.get('expires_in', '?')}s)")
    else:
        print(f"Token refresh warning: {rj}")
except Exception as e:
    print(f"Token refresh error (continuing with existing): {e}")

# --- Step 2: Fetch unposted articles ---
print("\n=== Fetching unposted articles ===")
headers = {
    'apikey': SB_SERVICE_KEY,
    'Authorization': f'Bearer {SB_SERVICE_KEY}',
    'Content-Type': 'application/json'
}

r = requests.get(
    f"{SB_URL}/rest/v1/p2_articles",
    params={
        'status': 'eq.published',
        'instagrammed_at': 'is.null',
        'image_url': 'not.is.null',
        'order': 'published_at.desc',
        'limit': '20',
        'select': 'id,slug,headline,subheadline,category,image_url'
    },
    headers=headers,
    timeout=30
)

if r.status_code != 200:
    print(f"Supabase error {r.status_code}: {r.text}")
    sys.exit(1)

articles = r.json()
print(f"Found {len(articles)} unposted articles")

if not articles:
    print("No articles to post. Done.")
    sys.exit(0)

# Pick up to 2
batch = articles[:2]
for a in batch:
    print(f"  - [{a['category']}] {a['headline'][:80]}...")

# --- Hashtag mapping ---
CATEGORY_HASHTAGS = {
    'news': '#India #NRI #IndiaNews #IndianDiaspora #BreakingNews #DesiNews #SouthAsian #IndianAmerican #NRINews',
    'immigration': '#Immigration #H1B #H1BVisa #NRI #GreenCard #IndianAmerican #USImmigration #VisaUpdate #OPT #USCIS #Desi',
    'nri-world': '#NRI #IndianDiaspora #NRILife #Desi #IndianAmerican #SouthAsian #DesiAbroad #IndianImmigrant #NRICommunity',
    'travel': '#Travel #India #IndiaTravel #IncredibleIndia #TravelIndia #DesiTravel #IndianDestinations #TravelDiaries #Wanderlust',
    'lifestyle-health': '#Lifestyle #Desi #NRILife #IndianAmerican #DesiLifestyle #Wellness #Health #SouthAsian #DesiCulture',
    'markets-finance': '#Markets #India #NRI #Nifty #Sensex #BSE #NSE #IndianMarkets #StockMarket #Finance #NRIInvesting',
    'technology': '#Tech #India #IndianTech #Startup #H1B #SiliconValley #AI #TechNews #IndianEngineers #FAANG #IndiansinTech',
    'sports': '#Cricket #India #IPL #IPL2026 #IndianCricket #BCCI #CricketNews #Desi #TeamIndia',
    'entertainment': '#Bollywood #Entertainment #IndianCinema #Desi #BollywoodNews #Tollywood #IndianMovies #DesiEntertainment',
    'food': '#IndianFood #Desi #IndianCuisine #NRIFood #DesiFood #IndianCooking #Foodie #IndianRecipes #DesiChef'
}

def extract_topic_hashtags(headline, max_tags=4):
    """Extract person/company/event names from headline as hashtags."""
    tags = []
    # Common patterns
    known = {
        'Modi': '#NarendraModi #Modi', 'Rahul Gandhi': '#RahulGandhi',
        'Virat Kohli': '#ViratKohli #Kohli', 'Rohit Sharma': '#RohitSharma',
        'Shah Rukh Khan': '#ShahRukhKhan #SRK', 'Dhoni': '#MSDhoni #Dhoni',
        'Bumrah': '#JaspritBumrah', 'Sachin': '#SachinTendulkar',
        'Trump': '#Trump', 'Elon Musk': '#ElonMusk', 'Musk': '#ElonMusk',
        'Zuckerberg': '#Zuckerberg', 'Sundar Pichai': '#SundarPichai',
        'Satya Nadella': '#SatyaNadella', 'Sam Altman': '#SamAltman',
        'Infosys': '#Infosys', 'TCS': '#TCS', 'Wipro': '#Wipro',
        'Google': '#Google', 'Apple': '#Apple', 'Microsoft': '#Microsoft',
        'Tesla': '#Tesla', 'Amazon': '#Amazon', 'Meta': '#Meta',
        'IPL': '#IPL2026', 'H-1B': '#H1BVisa', 'H1B': '#H1BVisa',
        'Mumbai': '#Mumbai', 'Delhi': '#Delhi', 'Bangalore': '#Bangalore',
        'Chennai': '#Chennai', 'Hyderabad': '#Hyderabad', 'Kolkata': '#Kolkata',
        'New York': '#NewYork', 'Silicon Valley': '#SiliconValley',
        'AI': '#ArtificialIntelligence', 'Bollywood': '#Bollywood',
        'BCCI': '#BCCI', 'ICC': '#ICC', 'FIFA': '#FIFA',
        'Adani': '#Adani', 'Ambani': '#Ambani',
        'Jaishankar': '#Jaishankar', 'BJP': '#BJP', 'Congress': '#Congress',
        'RBI': '#RBI', 'Sensex': '#Sensex', 'Nifty': '#Nifty',
        'Diljit': '#DiljitDosanjh', 'Shreya Ghoshal': '#ShreyaGhoshal',
        'Priyanka Chopra': '#PriyankaChopra', 'Deepika': '#DeepikaPadukone',
        'Alia Bhatt': '#AliaBhatt', 'Ranbir': '#RanbirKapoor',
        'Kohli': '#ViratKohli', 'Hardik Pandya': '#HardikPandya',
        'Rishabh Pant': '#RishabhPant', 'KL Rahul': '#KLRahul',
        'Suryakumar': '#SuryakumarYadav', 'Gill': '#ShubmanGill',
    }
    for name, tag in known.items():
        if name.lower() in headline.lower():
            for t in tag.split():
                if t not in tags:
                    tags.append(t)
    return tags[:max_tags]

def build_caption(article):
    cat = article.get('category', 'news')
    headline = article['headline']
    slug = article['slug']
    
    cat_tags = CATEGORY_HASHTAGS.get(cat, CATEGORY_HASHTAGS['news'])
    topic_tags = extract_topic_hashtags(headline)
    
    # Build hashtag string, max 20 total
    all_tags = cat_tags.split() + topic_tags + ['#TheVideshi', '#Reels']
    # Deduplicate preserving order
    seen = set()
    unique_tags = []
    for t in all_tags:
        tl = t.lower()
        if tl not in seen:
            seen.add(tl)
            unique_tags.append(t)
    unique_tags = unique_tags[:20]
    
    caption = f"""{headline}

📰 Read more: https://thevideshi.com/articles/{slug}

{' '.join(unique_tags)}"""
    
    return caption

# --- Step 3: Post first article as Reel ---
reel_article = batch[0]
reel_posted = False
reel_error = None

print(f"\n=== Generating Reel for: {reel_article['headline'][:60]}... ===")

try:
    # Step A: Generate reel video
    result = subprocess.run(
        ["python3", "generate-reel.py", "--slug", reel_article['slug'], "--upload"],
        cwd=os.path.expanduser("~/workspace/the-videshi-news/pipeline"),
        capture_output=True, text=True, timeout=180
    )
    print(f"generate-reel.py exit code: {result.returncode}")
    if result.stdout:
        print(f"STDOUT:\n{result.stdout[-2000:]}")
    if result.stderr:
        print(f"STDERR:\n{result.stderr[-1000:]}")
    
    if result.returncode != 0:
        raise Exception(f"generate-reel.py failed with exit code {result.returncode}")
    
    # Parse the Supabase public URL from output
    reel_url = None
    for line in result.stdout.split('\n'):
        if 'supabase.co/storage' in line and 'http' in line:
            match = re.search(r'(https://[^\s]+supabase\.co/storage/[^\s]+)', line)
            if match:
                reel_url = match.group(1)
                break
    
    if not reel_url:
        raise Exception("Could not find Supabase URL in generate-reel.py output")
    
    print(f"Reel URL: {reel_url}")
    
    # Step A2: Upload cover image
    cover_slug = reel_article['slug'][:80]
    cover_local = os.path.expanduser(f"~/workspace/the-videshi-news/pipeline/reels/reel-{cover_slug}-cover.jpg")
    cover_public_url = None
    
    if os.path.exists(cover_local):
        cover_filename = f"reels/{cover_slug}-cover.jpg"
        with open(cover_local, 'rb') as cf:
            cr = requests.post(
                f"{SB_URL}/storage/v1/object/article-images/{cover_filename}",
                headers={
                    "apikey": SB_SERVICE_KEY,
                    "Authorization": f"Bearer {SB_SERVICE_KEY}",
                    "Content-Type": "image/jpeg",
                    "x-upsert": "true"
                },
                data=cf.read(),
                timeout=60
            )
        if cr.status_code in (200, 201):
            cover_public_url = f"{SB_URL}/storage/v1/object/public/article-images/{cover_filename}"
            print(f"Cover uploaded: {cover_public_url}")
        else:
            print(f"Cover upload failed ({cr.status_code}): {cr.text[:200]}")
    else:
        print(f"No cover image found at {cover_local}")
    
    # Step B: Create Reel container
    caption = build_caption(reel_article)
    print(f"\nCaption:\n{caption[:300]}...")
    
    container_data = {
        "video_url": reel_url,
        "media_type": "REELS",
        "caption": caption,
        "access_token": IG_TOKEN
    }
    if cover_public_url:
        container_data["cover_url"] = cover_public_url
    
    r = requests.post(
        f"https://graph.instagram.com/v25.0/{IG_USER_ID}/media",
        data=container_data,
        timeout=30
    )
    rj = r.json()
    print(f"Container response: {rj}")
    
    if 'id' not in rj:
        raise Exception(f"Failed to create reel container: {rj}")
    
    container_id = rj['id']
    
    # Step C: Wait for processing
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
            raise Exception(f"Video processing error: {r_status.json()}")
    
    if not finished:
        raise Exception("Video processing timed out (90s)")
    
    # Step D: Publish Reel
    r2 = requests.post(
        f"https://graph.instagram.com/v25.0/{IG_USER_ID}/media_publish",
        data={"creation_id": container_id, "access_token": IG_TOKEN},
        timeout=30
    )
    r2j = r2.json()
    print(f"Publish response: {r2j}")
    
    if 'id' in r2j:
        reel_posted = True
        print(f"✅ Reel posted! Media ID: {r2j['id']}")
        
        # Update instagrammed_at
        now_utc = datetime.now(timezone.utc).isoformat()
        patch_r = requests.patch(
            f"{SB_URL}/rest/v1/p2_articles?id=eq.{reel_article['id']}",
            headers=headers,
            json={"instagrammed_at": now_utc},
            timeout=15
        )
        print(f"Updated instagrammed_at: {patch_r.status_code}")
    else:
        raise Exception(f"Reel publish failed: {r2j}")

except Exception as e:
    reel_error = str(e)
    print(f"❌ Reel error: {e}")

# --- Step 4: Post Story (second article, or first if only one) ---
story_posted = False
story_error = None

# Use second article for story if available, else first
story_article = batch[1] if len(batch) > 1 else batch[0]
# Don't post story of the same article we just reeled if we only have one
if len(batch) == 1 and reel_posted:
    print("\n=== Only 1 article available, skipping story (already posted as reel) ===")
else:
    print(f"\n=== Posting Story for: {story_article['headline'][:60]}... ===")
    
    # Wait between posts
    if reel_posted:
        print("Waiting 30s between posts...")
        time.sleep(30)
    
    try:
        # Create story container
        r = requests.post(
            f"https://graph.instagram.com/v25.0/{IG_USER_ID}/media",
            data={
                "image_url": story_article['image_url'],
                "media_type": "STORIES",
                "access_token": IG_TOKEN
            },
            timeout=30
        )
        rj = r.json()
        print(f"Story container response: {rj}")
        
        if 'id' not in rj:
            raise Exception(f"Failed to create story container: {rj}")
        
        story_container_id = rj['id']
        
        # Wait for processing
        print("Waiting 8s for story processing...")
        time.sleep(8)
        
        # Publish story
        r2 = requests.post(
            f"https://graph.instagram.com/v25.0/{IG_USER_ID}/media_publish",
            data={"creation_id": story_container_id, "access_token": IG_TOKEN},
            timeout=30
        )
        r2j = r2.json()
        print(f"Story publish response: {r2j}")
        
        if 'id' in r2j:
            story_posted = True
            print(f"✅ Story posted! Media ID: {r2j['id']}")
            
            # Update instagrammed_at for story article too (if different from reel)
            if story_article['id'] != reel_article['id']:
                now_utc = datetime.now(timezone.utc).isoformat()
                patch_r = requests.patch(
                    f"{SB_URL}/rest/v1/p2_articles?id=eq.{story_article['id']}",
                    headers=headers,
                    json={"instagrammed_at": now_utc},
                    timeout=15
                )
                print(f"Updated instagrammed_at for story article: {patch_r.status_code}")
        else:
            raise Exception(f"Story publish failed: {r2j}")
    
    except Exception as e:
        story_error = str(e)
        print(f"⚠️ Story error (non-fatal): {e}")

# --- Summary ---
print("\n" + "="*50)
print("INSTAGRAM AUTOPOST SUMMARY")
print("="*50)
print(f"Reel posted:  {'✅ YES' if reel_posted else '❌ NO'}")
if reel_posted:
    print(f"  Article: {reel_article['headline'][:70]}")
if reel_error:
    print(f"  Error: {reel_error[:200]}")
print(f"Story posted: {'✅ YES' if story_posted else '❌ NO'}")
if story_posted:
    print(f"  Article: {story_article['headline'][:70]}")
if story_error:
    print(f"  Error: {story_error[:200]}")
print("="*50)
