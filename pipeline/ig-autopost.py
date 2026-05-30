#!/usr/bin/env python3
"""Instagram auto-poster for The Videshi — posts Reels + Stories."""

import os
import re
import sys
import json
import time
import subprocess
import requests
from datetime import datetime, timezone

# --- Load credentials ---
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
IG_APP_SECRET = ig_env.get('INSTAGRAM_APP_SECRET', '')
SB_KEY = sb_env['SUPABASE_SERVICE_ROLE_KEY']
SUPABASE_URL = "https://lboecaekpynbpyijrbfz.supabase.co"

print(f"IG User ID: {IG_USER_ID}")
print(f"Token length: {len(TOKEN)}")

# --- Step 1: Refresh token ---
print("\n=== Refreshing Instagram token ===")
try:
    r = requests.get("https://graph.instagram.com/refresh_access_token", params={
        "grant_type": "ig_refresh_token",
        "access_token": TOKEN
    }, timeout=30)
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
            print("Token refreshed and saved!")
        else:
            print("Token unchanged after refresh.")
        print(f"Expires in: {rj.get('expires_in', 'unknown')} seconds")
    else:
        print(f"Token refresh warning: {rj}")
except Exception as e:
    print(f"Token refresh error (non-fatal): {e}")

# --- Step 2: Fetch articles not yet posted to Instagram ---
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
    timeout=30
)

if r.status_code != 200:
    print(f"ERROR fetching articles: {r.status_code} {r.text}")
    sys.exit(1)

articles = r.json()
print(f"Found {len(articles)} unposted articles with images")

if not articles:
    print("No articles to post. Exiting.")
    sys.exit(0)

# Pick up to 2 articles
batch = articles[:2]
for i, a in enumerate(batch):
    print(f"  [{i+1}] {a['headline'][:80]}... ({a['category']})")

# --- Hashtag mapping ---
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
    """Extract person/company/event names from headline as hashtags."""
    tags = []
    # Common patterns
    patterns = [
        # Indian political figures
        (r'\bModi\b', '#Modi'), (r'\bNarendra Modi\b', '#NarendraModi'),
        (r'\bRahul Gandhi\b', '#RahulGandhi'), (r'\bAmit Shah\b', '#AmitShah'),
        (r'\bYogi\b', '#YogiAdityanath'), (r'\bKejriwal\b', '#Kejriwal'),
        (r'\bJaishankar\b', '#Jaishankar'),
        # Cricket
        (r'\bKohli\b', '#ViratKohli'), (r'\bVirat\b', '#ViratKohli'),
        (r'\bRohit\b', '#RohitSharma'), (r'\bDhoni\b', '#MSDhoni'),
        (r'\bBumrah\b', '#JaspritBumrah'), (r'\bHardik\b', '#HardikPandya'),
        (r'\bSachin\b', '#Sachin'),
        # Bollywood
        (r'\bShah Rukh Khan\b', '#ShahRukhKhan'), (r'\bSRK\b', '#SRK'),
        (r'\bAamir Khan\b', '#AamirKhan'), (r'\bSalman Khan\b', '#SalmanKhan'),
        (r'\bDeepika\b', '#DeepikaPadukone'), (r'\bRanveer\b', '#RanveerSingh'),
        (r'\bAlia\b', '#AliaBhatt'), (r'\bPriyanka\b', '#PriyankaChopra'),
        (r'\bAnushka\b', '#AnushkaSharma'),
        # Tech
        (r'\bInfosys\b', '#Infosys'), (r'\bTCS\b', '#TCS'), (r'\bWipro\b', '#Wipro'),
        (r'\bGoogle\b', '#Google'), (r'\bApple\b', '#Apple'), (r'\bMicrosoft\b', '#Microsoft'),
        (r'\bTesla\b', '#Tesla'), (r'\bNvidia\b', '#Nvidia'),
        (r'\bSundar\b', '#SundarPichai'), (r'\bSatya\b', '#SatyaNadella'),
        (r'\bElon Musk\b', '#ElonMusk'), (r'\bSam Altman\b', '#SamAltman'),
        # Events / places
        (r'\bIPL\b', '#IPL2026'), (r'\bT20\b', '#T20WorldCup'),
        (r'\bMumbai\b', '#Mumbai'), (r'\bDelhi\b', '#Delhi'), (r'\bBengaluru\b', '#Bengaluru'),
        (r'\bHyderabad\b', '#Hyderabad'), (r'\bChennai\b', '#Chennai'),
        (r'\bNew York\b', '#NewYork'), (r'\bSilicon Valley\b', '#SiliconValley'),
        # Misc
        (r'\bTrump\b', '#Trump'), (r'\bH[- ]?1B\b', '#H1BVisa'),
        (r'\bAdani\b', '#Adani'), (r'\bAmbani\b', '#Ambani'),
        (r'\bRishi Sunak\b', '#RishiSunak'),
    ]
    seen = set()
    for pattern, tag in patterns:
        if re.search(pattern, headline, re.IGNORECASE) and tag.lower() not in seen:
            tags.append(tag)
            seen.add(tag.lower())
            if len(tags) >= max_tags:
                break
    return tags

def build_caption(article, is_reel=True):
    headline = article['headline']
    slug = article['slug']
    cat = article.get('category', 'news')

    cat_tags = CATEGORY_HASHTAGS.get(cat, CATEGORY_HASHTAGS['news'])
    topic_tags = extract_topic_hashtags(headline)
    suffix_tags = ["#TheVideshi"]
    if is_reel:
        suffix_tags.append("#Reels")

    # Combine, dedup, max 20
    all_tags = []
    seen = set()
    for t in topic_tags + cat_tags + suffix_tags:
        if t.lower() not in seen:
            all_tags.append(t)
            seen.add(t.lower())
    all_tags = all_tags[:20]

    caption = f"""{headline}

📰 Read more: https://thevideshi.com/articles/{slug}

{' '.join(all_tags)}"""
    return caption

def mark_instagrammed(article_id):
    now = datetime.now(timezone.utc).isoformat()
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article_id}",
        headers={
            "apikey": SB_KEY,
            "Authorization": f"Bearer {SB_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        },
        json={"instagrammed_at": now},
        timeout=30
    )
    print(f"  Mark instagrammed: {r.status_code}")

# --- Post Reel (first article) ---
reel_article = batch[0]
reel_posted = False
story_posted = False

print(f"\n=== Generating Reel for: {reel_article['headline'][:60]}... ===")
try:
    result = subprocess.run(
        ["python3", "generate-reel.py", "--slug", reel_article['slug'], "--upload"],
        cwd=os.path.expanduser("~/workspace/the-videshi-news/pipeline"),
        capture_output=True, text=True, timeout=180
    )
    print(f"Reel generator exit code: {result.returncode}")
    if result.stdout:
        print(f"STDOUT (last 500 chars):\n{result.stdout[-500:]}")
    if result.stderr:
        print(f"STDERR (last 300 chars):\n{result.stderr[-300:]}")

    # Parse Supabase URL from output
    reel_url = None
    for line in result.stdout.split('\n'):
        if 'supabase.co/storage' in line:
            match = re.search(r'(https://[^\s]+supabase\.co/storage/[^\s]+)', line)
            if match:
                reel_url = match.group(1)
                break

    if not reel_url:
        print("ERROR: Could not find reel URL in generator output")
        # Try to find any URL
        for line in result.stdout.split('\n'):
            if 'http' in line.lower():
                print(f"  Found line with URL: {line.strip()}")
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
                    timeout=60
                )
            if cr.status_code in (200, 201):
                cover_public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{cover_filename}"
                print(f"Cover uploaded: {cover_public_url}")
            else:
                print(f"Cover upload failed: {cr.status_code} {cr.text[:200]}")
        else:
            print(f"No cover image found at {cover_local}")

        # Create Reel container
        caption = build_caption(reel_article, is_reel=True)
        print(f"\nCaption:\n{caption[:200]}...")

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
        rj = r.json()
        print(f"Container response: {rj}")

        if 'id' in rj:
            container_id = rj['id']

            # Poll for FINISHED
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
                    print(f"  ERROR in processing: {r_status.json()}")
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
                r2j = r2.json()
                print(f"Publish response: {r2j}")
                if 'id' in r2j:
                    reel_posted = True
                    mark_instagrammed(reel_article['id'])
                    print(f"✅ Reel posted successfully! Media ID: {r2j['id']}")
                else:
                    print(f"❌ Reel publish failed: {r2j}")
            else:
                print("❌ Video processing did not finish in time")
        else:
            print(f"❌ Container creation failed: {rj}")

except subprocess.TimeoutExpired:
    print("❌ Reel generator timed out (180s)")
except Exception as e:
    print(f"❌ Reel error: {e}")

# --- Wait between posts ---
if reel_posted:
    print("\nWaiting 30 seconds before story...")
    time.sleep(30)

# --- Post Story (second article if available, else first) ---
story_article = batch[1] if len(batch) > 1 else batch[0]
# Don't post story of same article as reel unless it's the only one
if len(batch) == 1 and reel_posted:
    print("\nOnly 1 article available — skipping story (already posted as Reel)")
else:
    print(f"\n=== Posting Story for: {story_article['headline'][:60]}... ===")
    try:
        print(f"Story image URL: {story_article['image_url']}")
        r = requests.post(
            f"https://graph.instagram.com/v25.0/{IG_USER_ID}/media",
            data={
                "image_url": story_article['image_url'],
                "media_type": "STORIES",
                "access_token": TOKEN
            },
            timeout=30
        )
        rj = r.json()
        print(f"Story container response: {rj}")

        if 'id' in rj:
            container_id = rj['id']
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
            r2j = r2.json()
            print(f"Story publish response: {r2j}")
            if 'id' in r2j:
                story_posted = True
                # Mark story article as instagrammed too
                if story_article['id'] != reel_article.get('id'):
                    mark_instagrammed(story_article['id'])
                print(f"✅ Story posted successfully! Media ID: {r2j['id']}")
            else:
                print(f"⚠️ Story publish failed: {r2j}")
        else:
            print(f"⚠️ Story container failed: {rj}")
    except Exception as e:
        print(f"⚠️ Story error (non-fatal): {e}")

# --- Summary ---
print("\n" + "="*50)
print("SUMMARY")
print("="*50)
print(f"Reel posted:  {'✅ Yes' if reel_posted else '❌ No'}")
if reel_posted:
    print(f"  Article: {reel_article['headline'][:70]}")
print(f"Story posted: {'✅ Yes' if story_posted else '❌ No'}")
if story_posted:
    print(f"  Article: {story_article['headline'][:70]}")
print(f"Total articles processed: {1 if reel_posted else 0} reel + {1 if story_posted else 0} story")
