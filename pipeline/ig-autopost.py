#!/usr/bin/env python3
"""Instagram auto-poster for The Videshi — posts Reels + Stories."""

import os, sys, json, time, subprocess, re, requests
from datetime import datetime, timezone

# ── Load credentials ──────────────────────────────────────────────
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

IG_USER_ID = ig_env['INSTAGRAM_USER_ID']
TOKEN = ig_env['INSTAGRAM_ACCESS_TOKEN']
IG_APP_SECRET = ig_env['INSTAGRAM_APP_SECRET']
SB_KEY = sb_env['SUPABASE_SERVICE_ROLE_KEY']
SUPABASE_URL = 'https://lboecaekpynbpyijrbfz.supabase.co'

# ── Step 1: Refresh token ─────────────────────────────────────────
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
            # Update .env.instagram
            env_path = os.path.expanduser('~/workspace/.env.instagram')
            with open(env_path) as f:
                content = f.read()
            content = re.sub(
                r'INSTAGRAM_ACCESS_TOKEN=.*',
                f'INSTAGRAM_ACCESS_TOKEN={TOKEN}',
                content
            )
            with open(env_path, 'w') as f:
                f.write(content)
            print(f"Token refreshed and saved (expires in {rj.get('expires_in', '?')}s)")
        else:
            print(f"Token unchanged (expires in {rj.get('expires_in', '?')}s)")
    else:
        print(f"Token refresh response (no new token): {rj}")
except Exception as e:
    print(f"Token refresh failed: {e} — continuing with existing token")

# ── Step 2: Fetch unposted articles ──────────────────────────────
print("\n=== Fetching unposted articles ===")
headers = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}"
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
if not articles:
    print("No unposted articles with images found. Nothing to do.")
    sys.exit(0)

print(f"Found {len(articles)} unposted articles")
for a in articles[:5]:
    print(f"  - [{a.get('category')}] {a.get('headline','')[:80]}")

# Pick up to 2
batch = articles[:2]

# ── Hashtag mapping ───────────────────────────────────────────────
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
    'food': '#IndianFood #Desi #IndianCuisine #NRIFood #DesiFood #IndianCooking #Foodie #IndianRecipes #DesiChef',
}

def extract_topic_hashtags(headline, max_tags=4):
    """Extract person names, company names, events from headline."""
    tags = []
    # Common patterns
    patterns = [
        # Person names (capitalized two+ word sequences)
        (r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b', lambda m: '#' + m.group(1).replace(' ', '')),
    ]
    # Known entities
    known = {
        'Modi': '#Modi #NarendraModi', 'Trump': '#Trump', 'Kohli': '#ViratKohli #Kohli',
        'Rohit': '#RohitSharma', 'Dhoni': '#MSDhoni', 'Bumrah': '#JaspritBumrah',
        'H-1B': '#H1BVisa', 'H1B': '#H1BVisa', 'IPL': '#IPL2026',
        'Infosys': '#Infosys', 'TCS': '#TCS', 'Wipro': '#Wipro',
        'Google': '#Google', 'Microsoft': '#Microsoft', 'Apple': '#Apple',
        'Tesla': '#Tesla', 'Amazon': '#Amazon', 'Meta': '#Meta',
        'Bollywood': '#Bollywood', 'Shah Rukh Khan': '#ShahRukhKhan #SRK',
        'Alia Bhatt': '#AliaBhatt', 'Deepika': '#DeepikaPadukone',
        'Mumbai': '#Mumbai', 'Delhi': '#Delhi', 'Bengaluru': '#Bengaluru',
        'Hyderabad': '#Hyderabad', 'Chennai': '#Chennai',
        'Sachin': '#SachinTendulkar', 'Hardik': '#HardikPandya',
        'AI': '#AI #ArtificialIntelligence', 'ChatGPT': '#ChatGPT',
        'Adani': '#Adani', 'Ambani': '#Ambani',
        'Sundar Pichai': '#SundarPichai', 'Satya Nadella': '#SatyaNadella',
        'Canada': '#Canada', 'UK': '#UK', 'Australia': '#Australia',
        'Jaishankar': '#Jaishankar', 'BCCI': '#BCCI',
        'Nifty': '#Nifty50', 'Sensex': '#Sensex',
        'Olympics': '#Olympics', 'World Cup': '#WorldCup',
        'Diljit': '#DiljitDosanjh', 'Priyanka': '#PriyankaChopra',
    }
    for term, hashtag in known.items():
        if term.lower() in headline.lower():
            for t in hashtag.split():
                if t not in tags:
                    tags.append(t)
    
    # Extract capitalized names not already matched
    names = re.findall(r'\b([A-Z][a-z]{2,}(?:\s+[A-Z][a-z]{2,})+)\b', headline)
    for name in names:
        tag = '#' + name.replace(' ', '')
        if tag not in tags and len(tag) > 4:
            tags.append(tag)
    
    return tags[:max_tags]

def build_caption(article):
    headline = article.get('headline', '')
    slug = article.get('slug', '')
    category = article.get('category', 'news')
    
    cat_tags = CATEGORY_HASHTAGS.get(category, CATEGORY_HASHTAGS['news'])
    topic_tags = extract_topic_hashtags(headline)
    
    all_tags = cat_tags.split() + topic_tags + ['#TheVideshi', '#Reels']
    # Deduplicate while preserving order
    seen = set()
    unique_tags = []
    for t in all_tags:
        tl = t.lower()
        if tl not in seen:
            seen.add(tl)
            unique_tags.append(t)
    # Max 20 hashtags
    unique_tags = unique_tags[:20]
    
    caption = f"""{headline}

📰 Read more: https://thevideshi.com/articles/{slug}

{' '.join(unique_tags)}"""
    return caption

# ── Step 3: Post Reel (first article) ────────────────────────────
reel_posted = False
reel_article = batch[0]
story_article = batch[1] if len(batch) > 1 else batch[0]

print(f"\n=== Generating Reel for: {reel_article['headline'][:80]} ===")
print(f"    Slug: {reel_article['slug']}")

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
    
    # Parse Supabase URL from output
    reel_url = None
    for line in result.stdout.split('\n'):
        if 'supabase.co/storage' in line:
            match = re.search(r'(https://[^\s]+supabase\.co/storage/[^\s]+)', line)
            if match:
                reel_url = match.group(1)
                break
    
    if not reel_url:
        print("ERROR: Could not find reel URL in generate-reel.py output")
        # Try to find the file directly
        slug_trunc = reel_article['slug'][:80]
        local_reel = os.path.expanduser(f"~/workspace/the-videshi-news/pipeline/reels/reel-{slug_trunc}.mp4")
        if os.path.exists(local_reel):
            print(f"Found local reel at {local_reel}, uploading manually...")
            reel_filename = f"reels/{slug_trunc}.mp4"
            with open(local_reel, 'rb') as rf:
                ur = requests.post(
                    f"{SUPABASE_URL}/storage/v1/object/article-images/{reel_filename}",
                    headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}",
                             "Content-Type": "video/mp4", "x-upsert": "true"},
                    data=rf.read(),
                    timeout=60
                )
            print(f"Manual upload response: {ur.status_code}")
            if ur.status_code in (200, 201):
                reel_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{reel_filename}"
            else:
                print(f"Upload failed: {ur.text[:500]}")
        else:
            print(f"No local reel found at {local_reel}")
    
    if reel_url:
        print(f"Reel URL: {reel_url}")
        
        # Step A2: Upload cover image
        cover_local = os.path.expanduser(f"~/workspace/the-videshi-news/pipeline/reels/reel-{reel_article['slug'][:80]}-cover.jpg")
        cover_public_url = None
        if os.path.exists(cover_local):
            cover_filename = f"reels/{reel_article['slug'][:80]}-cover.jpg"
            with open(cover_local, 'rb') as cf:
                cr = requests.post(
                    f"{SUPABASE_URL}/storage/v1/object/article-images/{cover_filename}",
                    headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}",
                             "Content-Type": "image/jpeg", "x-upsert": "true"},
                    data=cf.read(),
                    timeout=30
                )
            if cr.status_code in (200, 201):
                cover_public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{cover_filename}"
                print(f"Cover uploaded: {cover_public_url}")
            else:
                print(f"Cover upload failed: {cr.status_code} {cr.text[:200]}")
        else:
            print(f"No cover image at {cover_local}")
        
        # Step B: Create Reel container
        caption = build_caption(reel_article)
        print(f"\nCaption:\n{caption[:300]}...")
        
        container_data = {
            "video_url": reel_url,
            "media_type": "REELS",
            "caption": caption,
            "access_token": TOKEN
        }
        if cover_public_url:
            container_data["cover_url"] = cover_public_url
        
        print("\nCreating Reel container...")
        r = requests.post(
            f"https://graph.instagram.com/v25.0/{IG_USER_ID}/media",
            data=container_data,
            timeout=30
        )
        print(f"Container response: {r.status_code} {r.text[:500]}")
        rj = r.json()
        
        if 'id' in rj:
            container_id = rj['id']
            
            # Step C: Wait for processing
            print("Waiting for video processing...")
            finished = False
            for i in range(18):
                time.sleep(5)
                r_status = requests.get(
                    f"https://graph.instagram.com/v25.0/{container_id}",
                    params={"fields": "status_code", "access_token": TOKEN},
                    timeout=15
                )
                status = r_status.json().get('status_code', 'UNKNOWN')
                print(f"  Poll {i+1}/18: {status}")
                if status == 'FINISHED':
                    finished = True
                    break
                elif status == 'ERROR':
                    print(f"  ERROR details: {r_status.json()}")
                    break
            
            if finished:
                # Step D: Publish
                print("Publishing Reel...")
                r2 = requests.post(
                    f"https://graph.instagram.com/v25.0/{IG_USER_ID}/media_publish",
                    data={"creation_id": container_id, "access_token": TOKEN},
                    timeout=30
                )
                print(f"Publish response: {r2.status_code} {r2.text[:500]}")
                if 'id' in r2.json():
                    reel_posted = True
                    print(f"✅ Reel published! Media ID: {r2.json()['id']}")
                    
                    # Mark as instagrammed
                    now_utc = datetime.now(timezone.utc).isoformat()
                    patch_r = requests.patch(
                        f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{reel_article['id']}",
                        headers={**headers, "Content-Type": "application/json", "Prefer": "return=minimal"},
                        json={"instagrammed_at": now_utc},
                        timeout=15
                    )
                    print(f"Supabase update: {patch_r.status_code}")
                else:
                    print(f"❌ Reel publish failed: {r2.text[:500]}")
            else:
                print("❌ Video processing did not finish in time")
        else:
            print(f"❌ Container creation failed: {rj}")
    else:
        print("❌ No reel URL available — skipping Reel post")

except subprocess.TimeoutExpired:
    print("❌ generate-reel.py timed out after 180s")
except Exception as e:
    print(f"❌ Reel posting error: {e}")
    import traceback
    traceback.print_exc()

# ── Step 4: Post Story (second article or first if only one) ─────
print(f"\n=== Posting Story for: {story_article['headline'][:80]} ===")
story_posted = False

# Wait between posts
if reel_posted:
    print("Waiting 30s between posts...")
    time.sleep(30)

try:
    image_url = story_article.get('image_url', '')
    if not image_url:
        print("❌ No image_url for story article")
    else:
        # Create story container
        r = requests.post(
            f"https://graph.instagram.com/v25.0/{IG_USER_ID}/media",
            data={
                "image_url": image_url,
                "media_type": "STORIES",
                "access_token": TOKEN
            },
            timeout=30
        )
        print(f"Story container response: {r.status_code} {r.text[:500]}")
        rj = r.json()
        
        if 'id' in rj:
            container_id = rj['id']
            print("Waiting 8s for story processing...")
            time.sleep(8)
            
            r2 = requests.post(
                f"https://graph.instagram.com/v25.0/{IG_USER_ID}/media_publish",
                data={"creation_id": container_id, "access_token": TOKEN},
                timeout=30
            )
            print(f"Story publish response: {r2.status_code} {r2.text[:500]}")
            if 'id' in r2.json():
                story_posted = True
                print(f"✅ Story published! Media ID: {r2.json()['id']}")
                
                # Mark story article as instagrammed too (if different from reel article)
                if story_article['id'] != reel_article['id']:
                    now_utc = datetime.now(timezone.utc).isoformat()
                    patch_r = requests.patch(
                        f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{story_article['id']}",
                        headers={**headers, "Content-Type": "application/json", "Prefer": "return=minimal"},
                        json={"instagrammed_at": now_utc},
                        timeout=15
                    )
                    print(f"Supabase update for story article: {patch_r.status_code}")
            else:
                print(f"❌ Story publish failed: {r2.text[:500]}")
        else:
            print(f"❌ Story container failed: {rj}")

except Exception as e:
    print(f"❌ Story posting error: {e}")

# ── Summary ───────────────────────────────────────────────────────
print(f"\n{'='*50}")
print(f"SUMMARY")
print(f"{'='*50}")
print(f"Reel posted:  {'✅ YES' if reel_posted else '❌ NO'}")
print(f"  Article: {reel_article['headline'][:80]}")
print(f"Story posted: {'✅ YES' if story_posted else '❌ NO'}")
print(f"  Article: {story_article['headline'][:80]}")
print(f"{'='*50}")
