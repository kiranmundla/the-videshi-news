#!/usr/bin/env python3
"""Instagram autopost for The Videshi — posts Reels + Stories."""

import os, sys, re, json, time, subprocess, requests
from datetime import datetime, timezone

# --- Config ---
SUPABASE_URL = "https://lboecaekpynbpyijrbfz.supabase.co"
ENV_IG_PATH = os.path.expanduser("~/workspace/.env.instagram")

def load_env_file(path):
    """Load KEY=VALUE from file, stripping quotes."""
    d = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                k, v = line.split('=', 1)
                d[k.strip()] = v.strip().strip('"').strip("'")
    return d

# Load credentials
ig_env = load_env_file(ENV_IG_PATH)
IG_USER_ID = ig_env['INSTAGRAM_USER_ID']
IG_TOKEN = ig_env['INSTAGRAM_ACCESS_TOKEN']
IG_APP_SECRET = ig_env['INSTAGRAM_APP_SECRET']

sb_env = load_env_file(os.path.expanduser("~/workspace/.env.supabase"))
SB_SERVICE_KEY = sb_env['SUPABASE_SERVICE_ROLE_KEY']

# --- Step 1: Refresh token ---
print("=== Refreshing Instagram token ===")
r = requests.get("https://graph.instagram.com/refresh_access_token", params={
    "grant_type": "ig_refresh_token",
    "access_token": IG_TOKEN
})
refresh_resp = r.json()
new_token = None
if 'access_token' in refresh_resp:
    new_token = refresh_resp['access_token']
    IG_TOKEN = new_token
    print(f"Token refreshed, expires in {refresh_resp.get('expires_in', '?')}s")
else:
    print(f"Token refresh warning: {refresh_resp}")

# --- Step 2: Fetch unposted articles ---
print("\n=== Fetching unposted articles ===")
headers = {
    "apikey": SB_SERVICE_KEY,
    "Authorization": f"Bearer {SB_SERVICE_KEY}",
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
    headers=headers
)
articles = r.json()
if not articles:
    print("No unposted articles found. Nothing to do.")
    sys.exit(0)

print(f"Found {len(articles)} unposted articles")
for a in articles[:5]:
    print(f"  - [{a['category']}] {a['headline'][:60]}...")

# Pick up to 2
batch = articles[:2]

# --- Hashtag map ---
CATEGORY_TAGS = {
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

def extract_topic_tags(headline):
    """Extract person/company/place names from headline as hashtags."""
    tags = []
    # Common patterns - capitalize words, remove spaces
    # Split headline into notable words (capitalized, multi-word names)
    words = headline.split()
    i = 0
    while i < len(words):
        w = words[i]
        # Skip short/common words
        if len(w) <= 2 or w.lower() in ('the', 'and', 'for', 'has', 'its', 'are', 'was', 'not', 'but', 'new', 'how', 'why', 'who', 'can', 'may', 'will', 'from', 'with', 'this', 'that', 'what', 'says', 'said', 'over', 'into', 'amid', 'after', 'more', 'than', 'also', 'just', 'been', 'most', 'some', 'all', 'now', 'out', 'top'):
            i += 1
            continue
        # Check if it's a capitalized word (potential proper noun)
        clean = re.sub(r'[^A-Za-z0-9]', '', w)
        if clean and clean[0].isupper() and len(clean) >= 3:
            # Try to grab multi-word name (2-3 words)
            name_parts = [clean]
            for j in range(1, 3):
                if i + j < len(words):
                    nw = re.sub(r'[^A-Za-z0-9]', '', words[i+j])
                    if nw and nw[0].isupper() and len(nw) >= 2:
                        name_parts.append(nw)
                    else:
                        break
                else:
                    break
            if len(name_parts) >= 2:
                tag = '#' + ''.join(name_parts)
                if len(tag) <= 30:
                    tags.append(tag)
                i += len(name_parts)
                continue
            else:
                # Single word proper noun
                if len(clean) >= 4:
                    tags.append(f'#{clean}')
            i += 1
        else:
            i += 1
    return tags[:4]  # Max 4 topic-specific

def build_caption(article):
    headline = article['headline']
    slug = article['slug']
    category = article.get('category', 'news')
    
    cat_tags = CATEGORY_TAGS.get(category, CATEGORY_TAGS['news'])
    topic_tags = extract_topic_tags(headline)
    topic_str = ' '.join(topic_tags) if topic_tags else ''
    
    # Count total tags
    all_tags = cat_tags + (' ' + topic_str if topic_str else '') + ' #TheVideshi #Reels'
    # Trim if over 20 tags
    tag_list = all_tags.split()
    if len(tag_list) > 20:
        tag_list = tag_list[:18] + ['#TheVideshi', '#Reels']
    tags_final = ' '.join(tag_list)
    
    caption = f"""{headline}

📰 Read more: https://thevideshi.com/articles/{slug}

{tags_final}"""
    return caption

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
        json={"instagrammed_at": now}
    )
    print(f"  Marked instagrammed: status {r.status_code}")

# --- Step 3: Post Reel (first article) ---
reel_article = batch[0]
story_article = batch[1] if len(batch) > 1 else batch[0]
reel_posted = False
story_posted = False
errors = []

print(f"\n=== Posting Reel: {reel_article['headline'][:60]}... ===")

# Step A: Generate reel video
print("  Generating reel video...")
try:
    result = subprocess.run(
        ["python3", "generate-reel.py", "--slug", reel_article['slug'], "--upload"],
        cwd=os.path.expanduser("~/workspace/the-videshi-news/pipeline"),
        capture_output=True, text=True, timeout=180
    )
    print(f"  generate-reel.py exit code: {result.returncode}")
    if result.stdout:
        print(f"  stdout (last 500 chars): ...{result.stdout[-500:]}")
    if result.stderr:
        print(f"  stderr (last 300 chars): ...{result.stderr[-300:]}")
    
    # Parse Supabase URL from output
    reel_url = None
    for line in result.stdout.split('\n'):
        if 'supabase.co/storage' in line:
            match = re.search(r'(https://[^\s]+supabase\.co/storage/[^\s]+)', line)
            if match:
                reel_url = match.group(1)
                break
    
    if not reel_url:
        raise Exception(f"Could not find reel URL in output. Full stdout:\n{result.stdout}")
    
    print(f"  Reel video URL: {reel_url}")
    
except Exception as e:
    print(f"  ERROR generating reel: {e}")
    errors.append(f"Reel generation failed: {e}")
    reel_url = None

if reel_url:
    # Step A2: Upload cover image
    slug_trunc = reel_article['slug'][:80]
    cover_local = os.path.expanduser(f"~/workspace/the-videshi-news/pipeline/reels/reel-{slug_trunc}-cover.jpg")
    cover_public_url = None
    
    if os.path.exists(cover_local):
        print("  Uploading cover image...")
        cover_filename = f"reels/{slug_trunc}-cover.jpg"
        with open(cover_local, 'rb') as cf:
            cr = requests.post(
                f"{SUPABASE_URL}/storage/v1/object/article-images/{cover_filename}",
                headers={
                    "apikey": SB_SERVICE_KEY,
                    "Authorization": f"Bearer {SB_SERVICE_KEY}",
                    "Content-Type": "image/jpeg",
                    "x-upsert": "true"
                },
                data=cf.read()
            )
        if cr.status_code in (200, 201):
            cover_public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{cover_filename}"
            print(f"  Cover uploaded: {cover_public_url}")
        else:
            print(f"  Cover upload failed: {cr.status_code} {cr.text[:200]}")
    else:
        print(f"  No cover image at {cover_local}")
    
    # Step B: Create Reel container
    caption = build_caption(reel_article)
    print(f"  Caption preview: {caption[:100]}...")
    
    container_data = {
        "video_url": reel_url,
        "media_type": "REELS",
        "caption": caption,
        "access_token": IG_TOKEN
    }
    if cover_public_url:
        container_data["cover_url"] = cover_public_url
    
    print("  Creating reel container...")
    r = requests.post(f"https://graph.instagram.com/v25.0/{IG_USER_ID}/media", data=container_data)
    container_resp = r.json()
    print(f"  Container response: {json.dumps(container_resp)[:300]}")
    
    if 'id' in container_resp:
        container_id = container_resp['id']
        
        # Step C: Poll for processing
        print("  Waiting for video processing...")
        finished = False
        for i in range(18):
            time.sleep(5)
            r_status = requests.get(
                f"https://graph.instagram.com/v25.0/{container_id}",
                params={"fields": "status_code", "access_token": IG_TOKEN}
            )
            status = r_status.json().get('status_code', 'UNKNOWN')
            print(f"    Poll {i+1}/18: {status}")
            if status == 'FINISHED':
                finished = True
                break
            elif status == 'ERROR':
                print(f"    Processing error: {r_status.json()}")
                errors.append(f"Reel processing error: {r_status.json()}")
                break
        
        if finished:
            # Step D: Publish
            print("  Publishing reel...")
            r2 = requests.post(f"https://graph.instagram.com/v25.0/{IG_USER_ID}/media_publish", data={
                "creation_id": container_id,
                "access_token": IG_TOKEN
            })
            publish_resp = r2.json()
            print(f"  Publish response: {json.dumps(publish_resp)[:300]}")
            
            if 'id' in publish_resp:
                reel_posted = True
                print(f"  ✅ Reel posted! Media ID: {publish_resp['id']}")
                mark_instagrammed(reel_article['id'])
            else:
                errors.append(f"Reel publish failed: {publish_resp}")
        else:
            if not errors or 'processing error' not in errors[-1]:
                errors.append("Reel processing timed out after 90s")
    else:
        errors.append(f"Reel container creation failed: {container_resp}")

# Wait before story
if reel_posted:
    print("\n  Waiting 30s before story...")
    time.sleep(30)

# --- Step 4: Post Story (second article, or first if only one) ---
print(f"\n=== Posting Story: {story_article['headline'][:60]}... ===")
try:
    img_url = story_article['image_url']
    if not img_url:
        raise Exception("No image_url for story article")
    
    print(f"  Image URL: {img_url[:100]}...")
    
    # Create story container
    r = requests.post(f"https://graph.instagram.com/v25.0/{IG_USER_ID}/media", data={
        "image_url": img_url,
        "media_type": "STORIES",
        "access_token": IG_TOKEN
    })
    story_container = r.json()
    print(f"  Story container: {json.dumps(story_container)[:300]}")
    
    if 'id' in story_container:
        story_container_id = story_container['id']
        print("  Waiting 8s for processing...")
        time.sleep(8)
        
        r2 = requests.post(f"https://graph.instagram.com/v25.0/{IG_USER_ID}/media_publish", data={
            "creation_id": story_container_id,
            "access_token": IG_TOKEN
        })
        story_publish = r2.json()
        print(f"  Story publish: {json.dumps(story_publish)[:300]}")
        
        if 'id' in story_publish:
            story_posted = True
            print(f"  ✅ Story posted! Media ID: {story_publish['id']}")
            # Only mark instagrammed if different from reel article
            if story_article['id'] != reel_article['id']:
                mark_instagrammed(story_article['id'])
        else:
            errors.append(f"Story publish failed: {story_publish}")
    else:
        errors.append(f"Story container failed: {story_container}")
        
except Exception as e:
    print(f"  Story error (non-fatal): {e}")
    errors.append(f"Story error: {e}")

# --- Step 5: Save refreshed token ---
if new_token:
    print("\n=== Saving refreshed token ===")
    with open(ENV_IG_PATH) as f:
        content = f.read()
    content = re.sub(
        r'INSTAGRAM_ACCESS_TOKEN=.*',
        f'INSTAGRAM_ACCESS_TOKEN={new_token}',
        content
    )
    with open(ENV_IG_PATH, 'w') as f:
        f.write(content)
    print("  Token saved.")

# --- Summary ---
print(f"\n{'='*50}")
print(f"SUMMARY")
print(f"{'='*50}")
print(f"Reel posted:  {'✅ YES' if reel_posted else '❌ NO'}")
print(f"  Article: {reel_article['headline'][:70]}")
print(f"Story posted: {'✅ YES' if story_posted else '❌ NO'}")
print(f"  Article: {story_article['headline'][:70]}")
if errors:
    print(f"\nErrors ({len(errors)}):")
    for e in errors:
        print(f"  - {e[:200]}")
print(f"{'='*50}")
