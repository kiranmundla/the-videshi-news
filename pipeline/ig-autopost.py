#!/usr/bin/env python3
"""Instagram autopost for The Videshi — posts Reels + Stories for recent articles."""

import os
import re
import sys
import json
import time
import subprocess
import requests
from datetime import datetime, timezone

# --- Load env files ---
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
videshi_env = load_env_file('~/workspace/the-videshi-news/.env')

IG_USER_ID = ig_env['INSTAGRAM_USER_ID']
TOKEN = ig_env['INSTAGRAM_ACCESS_TOKEN']
IG_APP_SECRET = ig_env['INSTAGRAM_APP_SECRET']
SB_KEY = sb_env['SUPABASE_SERVICE_ROLE_KEY']
SB_ANON_KEY = videshi_env.get('VITE_SUPABASE_PUBLISHABLE_KEY', '')
SUPABASE_URL = "https://lboecaekpynbpyijrbfz.supabase.co"

new_token = None

# --- Step 1: Refresh token ---
print("=== Refreshing Instagram token ===")
try:
    r = requests.get("https://graph.instagram.com/refresh_access_token", params={
        "grant_type": "ig_refresh_token",
        "access_token": TOKEN
    }, timeout=15)
    resp = r.json()
    if 'access_token' in resp:
        new_token = resp['access_token']
        TOKEN = new_token
        print(f"Token refreshed, expires_in={resp.get('expires_in', '?')} seconds")
    else:
        print(f"Token refresh response (no new token): {resp}")
except Exception as e:
    print(f"Token refresh failed (non-fatal): {e}")

# --- Step 2: Fetch recent unposted articles ---
print("\n=== Fetching unposted articles ===")
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
    timeout=15
)
articles = r.json()
if not isinstance(articles, list):
    print(f"Error fetching articles: {articles}")
    sys.exit(1)

# Filter out articles with empty image_url
articles = [a for a in articles if a.get('image_url') and a.get('slug')]
print(f"Found {len(articles)} unposted articles with images")

if not articles:
    print("No articles to post. Done.")
    sys.exit(0)

# Pick up to 2
batch = articles[:2]
for a in batch:
    print(f"  - [{a['category']}] {a['headline'][:80]}")

# --- Hashtag mapping ---
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
    """Extract person names, companies, events from headline."""
    tags = []
    # Known patterns
    patterns = {
        r'\bModi\b': '#NarendraModi #Modi',
        r'\bVirat\s+Kohli\b': '#ViratKohli #Kohli',
        r'\bKohli\b': '#Kohli',
        r'\bRohit\s+Sharma\b': '#RohitSharma',
        r'\bDhoni\b': '#MSDhoni #Dhoni',
        r'\bBumrah\b': '#JaspritBumrah #Bumrah',
        r'\bShah\s*Rukh\s*Khan\b': '#ShahRukhKhan #SRK',
        r'\bSalman\s+Khan\b': '#SalmanKhan',
        r'\bAamir\s+Khan\b': '#AamirKhan',
        r'\bDeepika\b': '#DeepikaPadukone',
        r'\bRanveer\b': '#RanveerSingh',
        r'\bPriyanka\b': '#PriyankaChopra',
        r'\bAlia\b': '#AliaBhatt',
        r'\bAmitabh\b': '#AmitabhBachchan',
        r'\bTrump\b': '#Trump',
        r'\bBiden\b': '#Biden',
        r'\bElon\s+Musk\b': '#ElonMusk',
        r'\bMusk\b': '#ElonMusk',
        r'\bZuckerberg\b': '#Zuckerberg #Meta',
        r'\bSundar\s+Pichai\b': '#SundarPichai #Google',
        r'\bSatya\s+Nadella\b': '#SatyaNadella #Microsoft',
        r'\bSam\s+Altman\b': '#SamAltman #OpenAI',
        r'\bInfosys\b': '#Infosys',
        r'\bTCS\b': '#TCS',
        r'\bWipro\b': '#Wipro',
        r'\bGoogle\b': '#Google',
        r'\bApple\b': '#Apple',
        r'\bMicrosoft\b': '#Microsoft',
        r'\bTesla\b': '#Tesla',
        r'\bIPL\b': '#IPL #IPL2026',
        r'\bT20\s+World\s+Cup\b': '#T20WorldCup',
        r'\bWorld\s+Cup\b': '#WorldCup',
        r'\bMumbai\b': '#Mumbai',
        r'\bDelhi\b': '#Delhi',
        r'\bBengaluru\b|Bangalore\b': '#Bengaluru',
        r'\bHyderabad\b': '#Hyderabad',
        r'\bChennai\b': '#Chennai',
        r'\bNew\s+York\b': '#NewYork',
        r'\bH[-]?1B\b': '#H1BVisa #H1B',
        r'\bGreen\s+Card\b': '#GreenCard',
        r'\bOCI\b': '#OCI',
        r'\bVisa\b': '#Visa',
        r'\bNASA\b': '#NASA',
        r'\bISRO\b': '#ISRO',
        r'\bAI\b': '#AI #ArtificialIntelligence',
        r'\bBollywood\b': '#Bollywood',
        r'\bTollywood\b': '#Tollywood',
        r'\bRajasthan\b': '#Rajasthan',
        r'\bKerala\b': '#Kerala',
        r'\bGoa\b': '#Goa',
        r'\bAdani\b': '#Adani',
        r'\bAmbani\b': '#Ambani #Reliance',
        r'\bRishi\s+Sunak\b': '#RishiSunak',
        r'\bVivek\b': '#VivekRamaswamy',
        r'\bCanada\b': '#Canada',
        r'\bUK\b': '#UK',
        r'\bAustralia\b': '#Australia',
        r'\bNeeraj\s+Chopra\b': '#NeerajChopra',
        r'\bGukesh\b': '#Gukesh #Chess',
        r'\bOlympics\b': '#Olympics',
    }
    seen = set()
    for pattern, hashtag in patterns.items():
        if re.search(pattern, headline, re.IGNORECASE):
            for tag in hashtag.split():
                if tag.lower() not in seen:
                    seen.add(tag.lower())
                    tags.append(tag)
    return tags[:max_tags]

def build_caption(article):
    headline = article.get('headline', '')
    slug = article.get('slug', '')
    category = (article.get('category') or 'news').lower()
    
    cat_tags = CATEGORY_HASHTAGS.get(category, CATEGORY_HASHTAGS['news'])
    topic_tags = extract_topic_hashtags(headline)
    
    # Combine all hashtags, limit to 20 total
    all_tags = []
    seen = set()
    for tag in topic_tags:
        if tag.lower() not in seen:
            seen.add(tag.lower())
            all_tags.append(tag)
    for tag in cat_tags.split():
        if tag.lower() not in seen:
            seen.add(tag.lower())
            all_tags.append(tag)
    # Always append #TheVideshi #Reels
    for tag in ['#TheVideshi', '#Reels']:
        if tag.lower() not in seen:
            seen.add(tag.lower())
            all_tags.append(tag)
    all_tags = all_tags[:20]
    
    caption = f"""{headline}

📰 Read more: https://thevideshi.com/articles/{slug}

{' '.join(all_tags)}"""
    
    return caption

def mark_instagrammed(article_id):
    now_utc = datetime.now(timezone.utc).isoformat()
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article_id}",
        headers={
            "apikey": SB_KEY,
            "Authorization": f"Bearer {SB_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        },
        json={"instagrammed_at": now_utc},
        timeout=15
    )
    print(f"  Marked instagrammed_at: status={r.status_code}")

# --- Post Reel (first article) ---
reel_article = batch[0]
reel_posted = False
story_posted = False

print(f"\n=== Generating Reel for: {reel_article['headline'][:80]} ===")
try:
    result = subprocess.run(
        ["python3", "generate-reel.py", "--slug", reel_article['slug'], "--upload"],
        cwd=os.path.expanduser("~/workspace/the-videshi-news/pipeline"),
        capture_output=True, text=True, timeout=180
    )
    print(f"Reel generator stdout:\n{result.stdout[-1500:] if len(result.stdout) > 1500 else result.stdout}")
    if result.stderr:
        print(f"Reel generator stderr:\n{result.stderr[-500:]}")
    
    # Parse Supabase URL from output
    reel_url = None
    for line in result.stdout.split('\n'):
        if 'supabase.co/storage' in line and 'http' in line:
            match = re.search(r'(https://[^\s"\']+supabase\.co/storage/[^\s"\']+)', line)
            if match:
                reel_url = match.group(1)
                break
    
    if not reel_url:
        print("ERROR: Could not find reel URL in generator output")
        # Try to find any URL in the output
        for line in result.stdout.split('\n'):
            if 'http' in line.lower():
                print(f"  Line with URL: {line.strip()}")
    else:
        print(f"Reel URL: {reel_url}")
        
        # Upload cover image
        cover_slug = reel_article['slug'][:80]
        cover_local = os.path.expanduser(f"~/workspace/the-videshi-news/pipeline/reels/reel-{cover_slug}-cover.jpg")
        cover_public_url = None
        if os.path.exists(cover_local):
            cover_filename = f"reels/{cover_slug}-cover.jpg"
            with open(cover_local, 'rb') as cf:
                cr = requests.post(
                    f"{SUPABASE_URL}/storage/v1/object/article-images/{cover_filename}",
                    headers={
                        "apikey": SB_KEY,
                        "Authorization": f"Bearer {SB_KEY}",
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
                print(f"Cover upload failed: {cr.status_code} {cr.text[:200]}")
        else:
            print(f"No cover image found at {cover_local}")
        
        # Create Reel container
        caption = build_caption(reel_article)
        container_data = {
            "video_url": reel_url,
            "media_type": "REELS",
            "caption": caption,
            "access_token": TOKEN
        }
        if cover_public_url:
            container_data["cover_url"] = cover_public_url
        
        print(f"\nCreating Reel container...")
        r = requests.post(
            f"https://graph.instagram.com/v25.0/{IG_USER_ID}/media",
            data=container_data,
            timeout=30
        )
        resp = r.json()
        print(f"Container response: {resp}")
        
        if 'id' in resp:
            container_id = resp['id']
            
            # Poll for processing
            print("Waiting for video processing...")
            finished = False
            for i in range(18):
                time.sleep(5)
                r_status = requests.get(
                    f"https://graph.instagram.com/v25.0/{container_id}",
                    params={"fields": "status_code", "access_token": TOKEN},
                    timeout=15
                )
                status_resp = r_status.json()
                status_code = status_resp.get('status_code', 'UNKNOWN')
                print(f"  Poll {i+1}: {status_code}")
                if status_code == 'FINISHED':
                    finished = True
                    break
                elif status_code == 'ERROR':
                    print(f"  Video processing error: {status_resp}")
                    break
            
            if finished:
                # Publish
                print("Publishing Reel...")
                r2 = requests.post(
                    f"https://graph.instagram.com/v25.0/{IG_USER_ID}/media_publish",
                    data={
                        "creation_id": container_id,
                        "access_token": TOKEN
                    },
                    timeout=30
                )
                pub_resp = r2.json()
                print(f"Publish response: {pub_resp}")
                
                if 'id' in pub_resp:
                    reel_posted = True
                    mark_instagrammed(reel_article['id'])
                    print(f"✅ Reel posted successfully! Media ID: {pub_resp['id']}")
                else:
                    print(f"❌ Reel publish failed: {pub_resp}")
            else:
                print("❌ Video processing did not finish in time")
        else:
            print(f"❌ Container creation failed: {resp}")

except subprocess.TimeoutExpired:
    print("❌ Reel generation timed out (180s)")
except Exception as e:
    print(f"❌ Reel error: {e}")

# --- Wait between posts ---
if reel_posted and len(batch) > 1:
    print("\nWaiting 30 seconds before story...")
    time.sleep(30)

# --- Post Story (second article if available, else first) ---
story_article = batch[1] if len(batch) > 1 else batch[0]
# Only post story if it's a different article from the reel, or if reel failed
if story_article['id'] == reel_article['id'] and reel_posted:
    print("\n=== Skipping Story (same article as Reel, and Reel succeeded) ===")
else:
    print(f"\n=== Posting Story for: {story_article['headline'][:80]} ===")
    try:
        image_url = story_article['image_url']
        print(f"Story image URL: {image_url}")
        
        r = requests.post(
            f"https://graph.instagram.com/v25.0/{IG_USER_ID}/media",
            data={
                "image_url": image_url,
                "media_type": "STORIES",
                "access_token": TOKEN
            },
            timeout=30
        )
        resp = r.json()
        print(f"Story container response: {resp}")
        
        if 'id' in resp:
            container_id = resp['id']
            print("Waiting 8 seconds for story processing...")
            time.sleep(8)
            
            r2 = requests.post(
                f"https://graph.instagram.com/v25.0/{IG_USER_ID}/media_publish",
                data={
                    "creation_id": container_id,
                    "access_token": TOKEN
                },
                timeout=30
            )
            pub_resp = r2.json()
            print(f"Story publish response: {pub_resp}")
            
            if 'id' in pub_resp:
                story_posted = True
                # Mark the story article as instagrammed too if different from reel
                if story_article['id'] != reel_article['id']:
                    mark_instagrammed(story_article['id'])
                print(f"✅ Story posted successfully! Media ID: {pub_resp['id']}")
            else:
                print(f"⚠️ Story publish failed: {pub_resp}")
        else:
            print(f"⚠️ Story container failed: {resp}")
    except Exception as e:
        print(f"⚠️ Story error (non-fatal): {e}")

# --- Save refreshed token ---
if new_token:
    print("\n=== Saving refreshed token ===")
    env_path = os.path.expanduser('~/workspace/.env.instagram')
    with open(env_path, 'r') as f:
        lines = f.readlines()
    with open(env_path, 'w') as f:
        for line in lines:
            if line.strip().startswith('INSTAGRAM_ACCESS_TOKEN='):
                f.write(f'INSTAGRAM_ACCESS_TOKEN={new_token}\n')
            else:
                f.write(line)
    print("Token saved.")

# --- Summary ---
print(f"\n{'='*50}")
print(f"SUMMARY")
print(f"{'='*50}")
print(f"Reel posted:  {'✅ YES' if reel_posted else '❌ NO'}")
print(f"  Article: {reel_article['headline'][:60]}")
print(f"Story posted: {'✅ YES' if story_posted else '❌ NO'}")
if story_article['id'] != reel_article['id']:
    print(f"  Article: {story_article['headline'][:60]}")
print(f"{'='*50}")
