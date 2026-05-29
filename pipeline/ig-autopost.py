#!/usr/bin/env python3
"""Instagram auto-poster for The Videshi — posts Reels + Stories."""

import os
import re
import json
import time
import subprocess
import requests
from datetime import datetime, timezone

# ── Load env ──────────────────────────────────────────────────────────────
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
SB_ANON = videshi_env['VITE_SUPABASE_PUBLISHABLE_KEY']
SUPABASE_URL = "https://lboecaekpynbpyijrbfz.supabase.co"

new_token = None

# ── Step 1: Refresh token ─────────────────────────────────────────────────
print("=== Refreshing Instagram token ===")
try:
    r = requests.get("https://graph.instagram.com/refresh_access_token", params={
        "grant_type": "ig_refresh_token",
        "access_token": TOKEN
    }, timeout=15)
    rj = r.json()
    if 'access_token' in rj:
        new_token = rj['access_token']
        TOKEN = new_token
        print(f"Token refreshed, expires in {rj.get('expires_in', '?')}s")
    else:
        print(f"Token refresh response (no new token): {rj}")
except Exception as e:
    print(f"Token refresh failed (non-fatal): {e}")

# ── Step 2: Fetch unposted articles ──────────────────────────────────────
print("\n=== Fetching unposted articles ===")
headers = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
}
r = requests.get(
    f"{SUPABASE_URL}/rest/v1/p2_articles",
    headers=headers,
    params={
        "status": "eq.published",
        "instagrammed_at": "is.null",
        "image_url": "not.is.null",
        "order": "published_at.desc",
        "limit": "20",
        "select": "id,slug,headline,subheadline,category,image_url"
    },
    timeout=15
)
articles = r.json()
if not isinstance(articles, list):
    print(f"Error fetching articles: {articles}")
    articles = []

# Filter out any with empty image_url just in case
articles = [a for a in articles if a.get('image_url')]
print(f"Found {len(articles)} unposted articles with images")

if not articles:
    print("Nothing to post. Exiting.")
    # Save token if refreshed
    if new_token:
        _save_token()
    exit(0)

# Pick up to 2
batch = articles[:2]
for a in batch:
    print(f"  - [{a['category']}] {a['headline'][:80]}")

# ── Hashtag builder ───────────────────────────────────────────────────────
CATEGORY_TAGS = {
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

# Common proper nouns → hashtag
KNOWN_ENTITIES = {
    "modi": "#Modi", "narendra modi": "#NarendraModi", "pm modi": "#PMModi",
    "rahul gandhi": "#RahulGandhi", "amit shah": "#AmitShah",
    "trump": "#Trump", "biden": "#Biden",
    "virat kohli": "#ViratKohli", "kohli": "#Kohli",
    "rohit sharma": "#RohitSharma", "bumrah": "#Bumrah", "jasprit bumrah": "#JaspritBumrah",
    "dhoni": "#Dhoni", "ms dhoni": "#MSDhoni", "sachin": "#Sachin",
    "shah rukh khan": "#ShahRukhKhan", "srk": "#SRK",
    "alia bhatt": "#AliaBhatt", "deepika padukone": "#DeepikaPadukone",
    "elon musk": "#ElonMusk", "sundar pichai": "#SundarPichai",
    "satya nadella": "#SatyaNadella", "sam altman": "#SamAltman",
    "infosys": "#Infosys", "tcs": "#TCS", "wipro": "#Wipro",
    "google": "#Google", "apple": "#Apple", "microsoft": "#Microsoft", "meta": "#Meta",
    "ipl": "#IPL2026", "t20 world cup": "#T20WorldCup",
    "mumbai": "#Mumbai", "delhi": "#Delhi", "bangalore": "#Bangalore", "bengaluru": "#Bengaluru",
    "hyderabad": "#Hyderabad", "chennai": "#Chennai", "kolkata": "#Kolkata",
    "h1b": "#H1BVisa", "h-1b": "#H1BVisa", "green card": "#GreenCard",
    "bcci": "#BCCI", "uscis": "#USCIS",
    "sensex": "#Sensex", "nifty": "#Nifty",
    "bollywood": "#Bollywood", "tollywood": "#Tollywood",
    "cricket": "#Cricket", "icc": "#ICC",
    "ai": "#AI", "chatgpt": "#ChatGPT", "gemini": "#Gemini",
    "rishi sunak": "#RishiSunak", "vivek ramaswamy": "#VivekRamaswamy",
    "adani": "#Adani", "ambani": "#Ambani",
    "neeraj chopra": "#NeerajChopra",
    "pv sindhu": "#PVSindhu",
}

def extract_topic_tags(headline, max_tags=4):
    """Extract entity-based hashtags from headline."""
    hl = headline.lower()
    tags = []
    # Check multi-word first (longer matches)
    checked = set()
    for entity, tag in sorted(KNOWN_ENTITIES.items(), key=lambda x: -len(x[0])):
        if entity in hl and tag not in checked:
            tags.append(tag)
            checked.add(tag)
            if len(tags) >= max_tags:
                break
    return tags

def build_caption(article):
    cat = article.get('category', 'news')
    headline = article['headline']
    slug = article['slug']

    cat_tags = CATEGORY_TAGS.get(cat, CATEGORY_TAGS['news'])
    topic_tags = extract_topic_tags(headline)

    all_tags = list(dict.fromkeys(cat_tags + topic_tags + ["#TheVideshi", "#Reels"]))
    # Max 20 hashtags
    all_tags = all_tags[:20]

    caption = f"""{headline}

📰 Read more: https://thevideshi.com/articles/{slug}

{' '.join(all_tags)}"""
    return caption

# ── Post Reel (first article) ────────────────────────────────────────────
reel_article = batch[0]
reel_posted = False
story_posted = False
errors = []

print(f"\n=== Generating Reel for: {reel_article['headline'][:60]}... ===")

try:
    # Step A: Generate reel video
    result = subprocess.run(
        ["python3", "generate-reel.py", "--slug", reel_article['slug'], "--upload"],
        cwd=os.path.expanduser("~/workspace/the-videshi-news/pipeline"),
        capture_output=True, text=True, timeout=180
    )
    print(f"Reel generator exit code: {result.returncode}")
    if result.stdout:
        print(f"STDOUT (last 500):\n{result.stdout[-500:]}")
    if result.stderr:
        print(f"STDERR (last 300):\n{result.stderr[-300:]}")

    # Parse supabase URL from output
    reel_url = None
    for line in result.stdout.split('\n'):
        if 'supabase.co/storage' in line and 'http' in line:
            match = re.search(r'(https://[^\s]+supabase\.co/storage/[^\s]+)', line)
            if match:
                reel_url = match.group(1)
                break

    if not reel_url:
        raise Exception(f"Could not find reel URL in generator output")

    print(f"Reel URL: {reel_url}")

    # Step A2: Upload cover image
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
            print(f"Cover upload failed ({cr.status_code}): {cr.text[:200]}")
    else:
        print(f"No cover image found at {cover_local}")

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

    print("Creating Reel container...")
    r = requests.post(
        f"https://graph.instagram.com/v25.0/{IG_USER_ID}/media",
        data=container_data,
        timeout=30
    )
    rj = r.json()
    print(f"Container response: {rj}")

    if 'id' not in rj:
        raise Exception(f"Failed to create container: {rj}")

    container_id = rj['id']

    # Step C: Poll for FINISHED
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
            raise Exception(f"Video processing failed: {r_status.json()}")

    if not finished:
        raise Exception("Video processing timed out after 90s")

    # Step D: Publish Reel
    print("Publishing Reel...")
    r2 = requests.post(
        f"https://graph.instagram.com/v25.0/{IG_USER_ID}/media_publish",
        data={"creation_id": container_id, "access_token": TOKEN},
        timeout=30
    )
    r2j = r2.json()
    print(f"Publish response: {r2j}")

    if 'id' in r2j:
        reel_posted = True
        print(f"✅ Reel posted! Media ID: {r2j['id']}")

        # Mark as instagrammed
        now_utc = datetime.now(timezone.utc).isoformat()
        patch_r = requests.patch(
            f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{reel_article['id']}",
            headers={**headers, "Content-Type": "application/json", "Prefer": "return=minimal"},
            json={"instagrammed_at": now_utc},
            timeout=10
        )
        print(f"Marked instagrammed: {patch_r.status_code}")
    else:
        raise Exception(f"Publish failed: {r2j}")

except Exception as e:
    err = f"Reel error: {e}"
    print(f"❌ {err}")
    errors.append(err)

# ── Post Story (second article, or first if only one) ────────────────────
time.sleep(30)  # Rate limit pause

# Use second article for story if available, else first
story_article = batch[1] if len(batch) > 1 else batch[0]
# Don't story the same article we just reeled unless it's the only one
if len(batch) == 1 and reel_posted:
    print("\n=== Only 1 article — skipping Story (already posted as Reel) ===")
else:
    print(f"\n=== Posting Story for: {story_article['headline'][:60]}... ===")
    try:
        # Create story container
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

        if 'id' not in rj:
            raise Exception(f"Story container failed: {rj}")

        story_container_id = rj['id']
        time.sleep(8)

        # Publish story
        r2 = requests.post(
            f"https://graph.instagram.com/v25.0/{IG_USER_ID}/media_publish",
            data={"creation_id": story_container_id, "access_token": TOKEN},
            timeout=30
        )
        r2j = r2.json()
        print(f"Story publish response: {r2j}")

        if 'id' in r2j:
            story_posted = True
            print(f"✅ Story posted! Media ID: {r2j['id']}")

            # Mark story article as instagrammed too
            now_utc = datetime.now(timezone.utc).isoformat()
            patch_r = requests.patch(
                f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{story_article['id']}",
                headers={**headers, "Content-Type": "application/json", "Prefer": "return=minimal"},
                json={"instagrammed_at": now_utc},
                timeout=10
            )
            print(f"Marked instagrammed: {patch_r.status_code}")
        else:
            raise Exception(f"Story publish failed: {r2j}")

    except Exception as e:
        err = f"Story error: {e}"
        print(f"⚠️ {err}")
        errors.append(err)

# ── Save refreshed token ─────────────────────────────────────────────────
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

# ── Summary ──────────────────────────────────────────────────────────────
print("\n" + "="*50)
print("SUMMARY")
print(f"  Reel posted:  {'✅ YES' if reel_posted else '❌ NO'}")
print(f"  Story posted: {'✅ YES' if story_posted else '❌ NO'}")
if errors:
    print(f"  Errors: {len(errors)}")
    for e in errors:
        print(f"    - {e}")
print("="*50)
