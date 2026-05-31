#!/usr/bin/env python3
"""Instagram autopost script for The Videshi - posts Reels + Stories."""

import os, sys, json, time, re, subprocess, requests
from datetime import datetime, timezone

# --- Load env files ---
def load_env_file(path):
    env = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            key, val = line.split('=', 1)
            val = val.strip().strip('"').strip("'")
            env[key] = val
    return env

ig_env = load_env_file('~/workspace/.env.instagram')
sb_env = load_env_file('~/workspace/.env.supabase')
videshi_env = load_env_file('~/workspace/the-videshi-news/.env')

IG_USER_ID = ig_env['INSTAGRAM_USER_ID']
TOKEN = ig_env['INSTAGRAM_ACCESS_TOKEN']
IG_APP_SECRET = ig_env['INSTAGRAM_APP_SECRET']
SB_KEY = sb_env['SUPABASE_SERVICE_ROLE_KEY']
SB_ANON = videshi_env.get('VITE_SUPABASE_PUBLISHABLE_KEY', '')
SUPABASE_URL = "https://lboecaekpynbpyijrbfz.supabase.co"

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
            print(f"Token still valid (expires in {rj.get('expires_in', '?')}s)")
    else:
        print(f"Token refresh warning: {rj}")
except Exception as e:
    print(f"Token refresh error (continuing with existing): {e}")

# --- Step 2: Fetch unposted articles ---
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

if r.status_code != 200:
    print(f"ERROR fetching articles: {r.status_code} {r.text}")
    sys.exit(1)

articles = r.json()
# Filter out any with empty image_url
articles = [a for a in articles if a.get('image_url')]
print(f"Found {len(articles)} unposted articles with images")

if not articles:
    print("No articles to post. Done.")
    sys.exit(0)

# Pick up to 2 articles
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

def extract_topic_hashtags(headline):
    """Extract person/company/place names from headline for hashtags."""
    tags = []
    # Common patterns - names, companies, etc
    # Remove common words and extract capitalized multi-word names
    words = headline.split()
    i = 0
    while i < len(words):
        w = words[i]
        # Skip short/common words
        if len(w) <= 2 or w.lower() in ('the', 'and', 'for', 'from', 'with', 'has', 'its',
            'are', 'was', 'were', 'will', 'how', 'why', 'what', 'who', 'new', 'over',
            'after', 'into', 'that', 'this', 'than', 'more', 'most', 'can', 'may',
            'not', 'but', 'all', 'also', 'been', 'have', 'their', 'could', 'about',
            'says', 'said', 'amid', 'india', 'indian', 'nri', 'top', 'set', 'big', 'key'):
            i += 1
            continue
        # Check for capitalized words that could be names
        clean = re.sub(r'[^a-zA-Z0-9]', '', w)
        if clean and clean[0].isupper() and len(clean) > 2:
            # Try to combine consecutive capitalized words (e.g., "Narendra Modi")
            combined = clean
            j = i + 1
            while j < len(words) and j < i + 3:
                next_clean = re.sub(r'[^a-zA-Z0-9]', '', words[j])
                if next_clean and next_clean[0].isupper() and len(next_clean) > 1:
                    combined += next_clean
                    j += 1
                else:
                    break
            if len(combined) > 3:
                tags.append(f"#{combined}")
            i = j
        else:
            i += 1
    # Dedupe and limit
    seen = set()
    unique = []
    for t in tags:
        tl = t.lower()
        if tl not in seen:
            seen.add(tl)
            unique.append(t)
    return unique[:4]

def build_caption(article):
    headline = article['headline']
    slug = article['slug']
    category = article.get('category', 'news')

    cat_tags = CATEGORY_HASHTAGS.get(category, CATEGORY_HASHTAGS['news'])
    topic_tags = extract_topic_hashtags(headline)

    # Combine all hashtags, limit to 20
    all_tags = cat_tags.split() + topic_tags + ["#TheVideshi", "#Reels"]
    # Dedupe
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

# --- Step 3: Post REEL for first article ---
reel_article = batch[0]
reel_posted = False
reel_error = None
story_posted = False
story_error = None

print(f"\n=== Generating Reel for: {reel_article['headline'][:60]} ===")
try:
    result = subprocess.run(
        ["python3", "generate-reel.py", "--slug", reel_article['slug'], "--upload"],
        cwd=os.path.expanduser("~/workspace/the-videshi-news/pipeline"),
        capture_output=True, text=True, timeout=180
    )
    print(f"Reel generator stdout:\n{result.stdout[-1000:]}")
    if result.stderr:
        print(f"Reel generator stderr:\n{result.stderr[-500:]}")

    # Parse Supabase URL from output
    reel_url = None
    for line in result.stdout.split('\n'):
        if 'supabase.co/storage' in line:
            match = re.search(r'(https://[^\s"\']+supabase\.co/storage/[^\s"\']+)', line)
            if match:
                reel_url = match.group(1)
                break

    if not reel_url:
        raise Exception(f"Could not find reel URL in output. Exit code: {result.returncode}")

    print(f"Reel video URL: {reel_url}")

    # Upload cover image
    slug_trunc = reel_article['slug'][:80]
    cover_local = os.path.expanduser(f"~/workspace/the-videshi-news/pipeline/reels/reel-{slug_trunc}-cover.jpg")
    cover_public_url = None
    if os.path.exists(cover_local):
        cover_filename = f"reels/{slug_trunc}-cover.jpg"
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
            print(f"Cover image uploaded: {cover_public_url}")
        else:
            print(f"Cover upload warning: {cr.status_code} {cr.text[:200]}")
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

    print("Creating Reel container...")
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
        status = r_status.json().get('status_code', 'UNKNOWN')
        print(f"  Poll {i+1}/18: {status}")
        if status == 'FINISHED':
            finished = True
            break
        elif status == 'ERROR':
            raise Exception(f"Video processing failed: {r_status.json()}")

    if not finished:
        raise Exception("Video processing timed out after 90 seconds")

    # Publish Reel
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
        print(f"✅ Reel published! Media ID: {r2j['id']}")

        # Update instagrammed_at
        now_utc = datetime.now(timezone.utc).isoformat()
        patch_r = requests.patch(
            f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{reel_article['id']}",
            headers={**headers, "Prefer": "return=minimal"},
            json={"instagrammed_at": now_utc},
            timeout=10
        )
        print(f"Updated instagrammed_at: {patch_r.status_code}")
    else:
        raise Exception(f"Publish failed: {r2j}")

except Exception as e:
    reel_error = str(e)
    print(f"❌ Reel error: {e}")

# --- Step 4: Wait between posts ---
if reel_posted:
    print("\nWaiting 30 seconds before Story...")
    time.sleep(30)

# --- Step 5: Post Story for second article (or first if only one) ---
story_article = batch[1] if len(batch) > 1 else batch[0]
# Don't post story for the same article as the reel if we only have one
if len(batch) < 2:
    print("\nOnly 1 article available — skipping Story (same as Reel)")
else:
    print(f"\n=== Posting Story for: {story_article['headline'][:60]} ===")
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

        container_id = rj['id']

        # Wait for processing
        print("Waiting 8 seconds for story processing...")
        time.sleep(8)

        # Publish story
        r2 = requests.post(
            f"https://graph.instagram.com/v25.0/{IG_USER_ID}/media_publish",
            data={"creation_id": container_id, "access_token": TOKEN},
            timeout=30
        )
        r2j = r2.json()
        print(f"Story publish response: {r2j}")

        if 'id' in r2j:
            story_posted = True
            print(f"✅ Story published! Media ID: {r2j['id']}")

            # Update instagrammed_at for story article too
            now_utc = datetime.now(timezone.utc).isoformat()
            patch_r = requests.patch(
                f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{story_article['id']}",
                headers={**headers, "Prefer": "return=minimal"},
                json={"instagrammed_at": now_utc},
                timeout=10
            )
            print(f"Updated instagrammed_at: {patch_r.status_code}")
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
