#!/usr/bin/env python3
"""Instagram auto-poster for The Videshi — posts Reels + Stories."""

import os
import re
import sys
import json
import time
import subprocess
from datetime import datetime, timezone

import requests

# ── Load credentials ──────────────────────────────────────────────
def load_env_file(path):
    """Parse KEY=VALUE (with optional quotes) from a file."""
    env = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' not in line:
                continue
            k, v = line.split('=', 1)
            v = v.strip().strip('"').strip("'")
            env[k] = v
    return env

ig_env = load_env_file("~/workspace/.env.instagram")
sb_env = load_env_file("~/workspace/.env.supabase")
vite_env = load_env_file("~/workspace/the-videshi-news/.env")

IG_USER_ID = ig_env["INSTAGRAM_USER_ID"]
TOKEN = ig_env["INSTAGRAM_ACCESS_TOKEN"]
IG_APP_SECRET = ig_env["INSTAGRAM_APP_SECRET"]
SB_SERVICE_KEY = sb_env["SUPABASE_SERVICE_ROLE_KEY"]
SUPABASE_URL = "https://lboecaekpynbpyijrbfz.supabase.co"

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
            # Rewrite .env.instagram preserving all other values
            ig_env["INSTAGRAM_ACCESS_TOKEN"] = TOKEN
            with open(os.path.expanduser("~/workspace/.env.instagram"), 'w') as f:
                for k, v in ig_env.items():
                    f.write(f"{k}={v}\n")
            print(f"Token refreshed and saved (expires in {rj.get('expires_in', '?')}s)")
        else:
            print(f"Token unchanged (expires in {rj.get('expires_in', '?')}s)")
    else:
        print(f"Token refresh response (no new token): {rj}")
except Exception as e:
    print(f"Token refresh failed (non-fatal): {e}")

# ── Step 2: Fetch unposted articles ──────────────────────────────
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

if r.status_code != 200:
    print(f"ERROR: Supabase fetch failed: {r.status_code} {r.text}")
    sys.exit(1)

articles = r.json()
print(f"Found {len(articles)} unposted articles with images")

if not articles:
    print("Nothing to post. Exiting.")
    sys.exit(0)

# Pick up to 2 articles
batch = articles[:2]
for a in batch:
    print(f"  - [{a['category']}] {a['headline'][:80]}...")

# ── Hashtag mapping ──────────────────────────────────────────────
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
    """Extract person/company/place names from headline as hashtags."""
    tags = []
    # Common patterns — person names, companies, places
    known = {
        "modi": "#NarendraModi #Modi", "trump": "#Trump #DonaldTrump",
        "kohli": "#ViratKohli #Kohli", "rohit": "#RohitSharma",
        "dhoni": "#MSDhoni #Dhoni", "bumrah": "#JaspritBumrah",
        "shah rukh": "#ShahRukhKhan #SRK", "salman khan": "#SalmanKhan",
        "aamir khan": "#AamirKhan", "deepika": "#DeepikaPadukone",
        "priyanka": "#PriyankaChopra", "alia": "#AliaBhatt",
        "infosys": "#Infosys", "tcs": "#TCS", "wipro": "#Wipro",
        "reliance": "#Reliance", "tata": "#Tata", "adani": "#Adani",
        "ambani": "#Ambani", "google": "#Google", "apple": "#Apple",
        "microsoft": "#Microsoft", "meta": "#Meta", "tesla": "#Tesla",
        "h-1b": "#H1BVisa #H1B", "h1b": "#H1BVisa #H1B",
        "green card": "#GreenCard", "ipl": "#IPL #IPL2026",
        "mumbai": "#Mumbai", "delhi": "#Delhi", "bangalore": "#Bangalore",
        "hyderabad": "#Hyderabad", "chennai": "#Chennai",
        "new york": "#NewYork", "silicon valley": "#SiliconValley",
        "jaishankar": "#Jaishankar", "rahul gandhi": "#RahulGandhi",
        "kejriwal": "#Kejriwal", "yogi": "#YogiAdityanath",
        "sundar pichai": "#SundarPichai", "satya nadella": "#SatyaNadella",
        "sam altman": "#SamAltman", "elon musk": "#ElonMusk",
        "bollywood": "#Bollywood", "cricket": "#Cricket",
        "sachin": "#SachinTendulkar", "bcci": "#BCCI",
        "canada": "#Canada", "uk": "#UK", "australia": "#Australia",
        "visa": "#Visa", "uscis": "#USCIS",
        "ai": "#AI #ArtificialIntelligence",
        "startup": "#Startup #IndianStartup",
    }
    hl = headline.lower()
    found = set()
    for pattern, tag_str in known.items():
        if pattern in hl:
            for t in tag_str.split():
                found.add(t)
    return list(found)[:4]

def build_caption(article):
    headline = article['headline']
    slug = article['slug']
    cat = article.get('category', 'news') or 'news'

    cat_tags = CATEGORY_HASHTAGS.get(cat, CATEGORY_HASHTAGS['news'])
    topic_tags = extract_topic_hashtags(headline)
    topic_str = " ".join(topic_tags)

    caption = f"""{headline}

📰 Read more: https://thevideshi.com/articles/{slug}

{cat_tags}
{topic_str}

#TheVideshi #Reels"""

    # Ensure max 20 hashtags
    all_tags = re.findall(r'#\w+', caption)
    if len(all_tags) > 20:
        # Keep first 18 + #TheVideshi + #Reels
        excess = len(all_tags) - 20
        # Remove some category tags from the middle
        cat_tag_list = cat_tags.split()
        trimmed = cat_tag_list[:len(cat_tag_list) - excess]
        cat_tags = " ".join(trimmed)
        caption = f"""{headline}

📰 Read more: https://thevideshi.com/articles/{slug}

{cat_tags}
{topic_str}

#TheVideshi #Reels"""

    return caption.strip()

def mark_instagrammed(article_id):
    now = datetime.now(timezone.utc).isoformat()
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article_id}",
        headers={
            "apikey": SB_SERVICE_KEY,
            "Authorization": f"Bearer {SB_SERVICE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        },
        json={"instagrammed_at": now},
        timeout=15
    )
    if r.status_code in (200, 204):
        print(f"  Marked article {article_id} as instagrammed at {now}")
    else:
        print(f"  WARNING: Failed to mark instagrammed: {r.status_code} {r.text}")

# ── Step 3: Post Reel for first article ──────────────────────────
reel_article = batch[0]
reel_posted = False
story_posted = False

print(f"\n=== Generating Reel for: {reel_article['headline'][:60]}... ===")

try:
    # Step A: Check for pre-built reel first, then fall back to generate-reel.py
    import glob
    slug_short = reel_article['slug'][:80]
    reels_dir = os.path.expanduser("~/workspace/the-videshi-news/pipeline/reels")
    prebuilt = sorted(glob.glob(os.path.join(reels_dir, f"reel-{slug_short}*.mp4")))
    # Also check for partial slug matches (e.g. kavya reels with shorter slug fragments)
    if not prebuilt:
        # Try matching first 40 chars of slug for broader match
        prebuilt = sorted(glob.glob(os.path.join(reels_dir, f"reel-{slug_short[:40]}*.mp4")))

    reel_url = None

    if prebuilt:
        # Use pre-built reel — upload to Supabase directly
        prebuilt_path = prebuilt[-1]  # newest if multiple
        print(f"📦 Found pre-built reel: {os.path.basename(prebuilt_path)}")
        print(f"   Uploading to Supabase storage...")
        storage_name = f"reels/{os.path.basename(prebuilt_path)}"
        with open(prebuilt_path, 'rb') as vf:
            ur = requests.post(
                f"{SUPABASE_URL}/storage/v1/object/article-images/{storage_name}",
                headers={
                    "apikey": SB_SERVICE_KEY,
                    "Authorization": f"Bearer {SB_SERVICE_KEY}",
                    "Content-Type": "video/mp4",
                    "x-upsert": "true"
                },
                data=vf.read(),
                timeout=120
            )
        if ur.status_code in (200, 201):
            reel_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{storage_name}"
            print(f"   ✅ Uploaded: {reel_url}")
        else:
            print(f"   ⚠️ Upload failed ({ur.status_code}), falling back to generate-reel.py")

    if not reel_url:
        # No pre-built reel or upload failed — generate fresh
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

        # Parse the Supabase URL from output
        for line in result.stdout.split('\n'):
            if 'supabase.co/storage' in line and 'http' in line:
                match = re.search(r'(https://[^\s]+supabase\.co/storage/[^\s]+)', line)
                if match:
                    reel_url = match.group(1)
                    break

    if not reel_url:
        print("ERROR: Could not find reel URL in generate-reel.py output")
        raise Exception("No reel URL found")

    print(f"Reel video URL: {reel_url}")

    # Step A2: Upload cover image to Supabase
    slug_short = reel_article['slug'][:80]
    cover_local = os.path.expanduser(f"~/workspace/the-videshi-news/pipeline/reels/reel-{slug_short}-cover.jpg")
    cover_public_url = None

    if os.path.exists(cover_local):
        cover_filename = f"reels/{slug_short}-cover.jpg"
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
    print(f"\nCaption:\n{caption}\n")

    container_data = {
        "video_url": reel_url,
        "media_type": "REELS",
        "caption": caption,
        "access_token": TOKEN
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
        raise Exception(f"Container creation failed: {rj}")

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
            raise Exception(f"Video processing error: {r_status.json()}")

    if not finished:
        print("WARNING: Video processing did not finish in 90s, attempting publish anyway")

    # Step D: Publish Reel
    r2 = requests.post(
        f"https://graph.instagram.com/v25.0/{IG_USER_ID}/media_publish",
        data={"creation_id": container_id, "access_token": TOKEN},
        timeout=30
    )
    r2j = r2.json()
    print(f"Publish response: {r2j}")

    if 'id' in r2j:
        reel_posted = True
        print(f"✅ REEL POSTED — Media ID: {r2j['id']}")
        mark_instagrammed(reel_article['id'])
    else:
        print(f"❌ Reel publish failed: {r2j}")

except Exception as e:
    print(f"❌ Reel posting failed: {e}")

# ── Step 4: Post Story for second article (or first if only one) ──
print("\n=== Posting Story ===")
# Use the second article if available, else first
story_article = batch[1] if len(batch) > 1 else batch[0]
# Don't re-story the same article we just reeled unless it's the only one
if len(batch) == 1 and reel_posted:
    print("Only one article available and already posted as Reel. Skipping story.")
else:
    print(f"Story article: {story_article['headline'][:60]}...")

    # Wait between posts
    if reel_posted:
        print("Waiting 30s between posts...")
        time.sleep(30)

    try:
        # Step A: Create story container
        r = requests.post(
            f"https://graph.instagram.com/v25.0/{IG_USER_ID}/media",
            data={
                "image_url": story_article['image_url'],
                "media_type": "STORIES",
                "access_token": TOKEN
            },
            timeout=30
        )
        sj = r.json()
        print(f"Story container response: {sj}")

        if 'id' not in sj:
            raise Exception(f"Story container failed: {sj}")

        story_container_id = sj['id']

        # Step B: Wait for processing
        print("Waiting 8s for story processing...")
        time.sleep(8)

        # Step C: Publish story
        r2 = requests.post(
            f"https://graph.instagram.com/v25.0/{IG_USER_ID}/media_publish",
            data={"creation_id": story_container_id, "access_token": TOKEN},
            timeout=30
        )
        r2j = r2.json()
        print(f"Story publish response: {r2j}")

        if 'id' in r2j:
            story_posted = True
            print(f"✅ STORY POSTED — Media ID: {r2j['id']}")
            # Mark story article as instagrammed too if it's different
            if story_article['id'] != reel_article['id']:
                mark_instagrammed(story_article['id'])
        else:
            print(f"❌ Story publish failed: {r2j}")

    except Exception as e:
        print(f"❌ Story posting failed (non-fatal): {e}")

# ── Summary ──────────────────────────────────────────────────────
print(f"""
========================================
SUMMARY
========================================
Reel posted:  {'✅ YES' if reel_posted else '❌ NO'}
  Article:    {reel_article['headline'][:70]}
Story posted: {'✅ YES' if story_posted else '❌ NO'}
  Article:    {story_article['headline'][:70] if story_article else 'N/A'}
========================================
""")
