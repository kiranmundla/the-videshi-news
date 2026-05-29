#!/usr/bin/env python3
"""Instagram auto-poster for The Videshi — posts Reels + Stories."""

import os, sys, re, json, time, subprocess, datetime, requests

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
app_env = load_env_file('~/workspace/the-videshi-news/.env')

IG_USER_ID = ig_env['INSTAGRAM_USER_ID']
IG_TOKEN = ig_env['INSTAGRAM_ACCESS_TOKEN']
IG_APP_SECRET = ig_env['INSTAGRAM_APP_SECRET']
SB_URL = 'https://lboecaekpynbpyijrbfz.supabase.co'
SB_SERVICE_KEY = sb_env['SUPABASE_SERVICE_ROLE_KEY']

print(f"[INFO] IG User ID: {IG_USER_ID}")
print(f"[INFO] Token length: {len(IG_TOKEN)}")

# ── Step 1: Refresh token ─────────────────────────────────────────
print("\n[STEP 1] Refreshing Instagram token...")
try:
    r = requests.get("https://graph.instagram.com/refresh_access_token", params={
        "grant_type": "ig_refresh_token",
        "access_token": IG_TOKEN
    }, timeout=15)
    rj = r.json()
    if 'access_token' in rj:
        new_token = rj['access_token']
        if new_token != IG_TOKEN:
            # Update .env.instagram
            env_path = os.path.expanduser('~/workspace/.env.instagram')
            with open(env_path) as f:
                content = f.read()
            content = re.sub(
                r'INSTAGRAM_ACCESS_TOKEN=.*',
                f'INSTAGRAM_ACCESS_TOKEN={new_token}',
                content
            )
            with open(env_path, 'w') as f:
                f.write(content)
            IG_TOKEN = new_token
            print(f"[OK] Token refreshed and saved (expires_in={rj.get('expires_in', '?')}s)")
        else:
            print(f"[OK] Token still valid (expires_in={rj.get('expires_in', '?')}s)")
    else:
        print(f"[WARN] Token refresh response: {rj}")
except Exception as e:
    print(f"[WARN] Token refresh failed: {e} — continuing with existing token")

# ── Step 2: Fetch unposted articles ──────────────────────────────
print("\n[STEP 2] Fetching unposted articles...")
headers = {
    "apikey": SB_SERVICE_KEY,
    "Authorization": f"Bearer {SB_SERVICE_KEY}",
    "Content-Type": "application/json"
}
r = requests.get(
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
articles = r.json()
if not isinstance(articles, list):
    print(f"[ERROR] Unexpected response: {articles}")
    sys.exit(1)

# Filter out articles with empty image_url
articles = [a for a in articles if a.get('image_url') and a['image_url'].strip()]
print(f"[INFO] Found {len(articles)} unposted articles with images")

if not articles:
    print("[DONE] No articles to post. Exiting.")
    sys.exit(0)

# Pick up to 2
batch = articles[:2]
for i, a in enumerate(batch):
    print(f"  [{i+1}] {a['headline'][:80]}... (cat={a.get('category','?')}, slug={a['slug'][:50]})")

# ── Hashtag builder ──────────────────────────────────────────────
CATEGORY_TAGS = {
    "news": ["#India", "#NRI", "#IndiaNews", "#IndianDiaspora", "#BreakingNews", "#DesiNews", "#SouthAsian", "#IndianAmerican", "#NRINews"],
    "immigration": ["#Immigration", "#H1B", "#H1BVisa", "#NRI", "#GreenCard", "#IndianAmerican", "#USImmigration", "#VisaUpdate", "#USCIS", "#Desi"],
    "nri-world": ["#NRI", "#IndianDiaspora", "#NRILife", "#Desi", "#IndianAmerican", "#SouthAsian", "#DesiAbroad", "#NRICommunity"],
    "travel": ["#Travel", "#India", "#IndiaTravel", "#IncredibleIndia", "#TravelIndia", "#DesiTravel", "#Wanderlust"],
    "lifestyle-health": ["#Lifestyle", "#Desi", "#NRILife", "#IndianAmerican", "#DesiLifestyle", "#Wellness", "#Health", "#SouthAsian"],
    "markets-finance": ["#Markets", "#India", "#NRI", "#Nifty", "#Sensex", "#IndianMarkets", "#StockMarket", "#Finance", "#NRIInvesting"],
    "technology": ["#Tech", "#India", "#IndianTech", "#Startup", "#AI", "#TechNews", "#IndianEngineers", "#IndiansinTech"],
    "sports": ["#Cricket", "#India", "#IPL", "#IPL2026", "#IndianCricket", "#BCCI", "#CricketNews", "#Desi", "#TeamIndia"],
    "entertainment": ["#Bollywood", "#Entertainment", "#IndianCinema", "#Desi", "#BollywoodNews", "#DesiEntertainment"],
    "food": ["#IndianFood", "#Desi", "#IndianCuisine", "#NRIFood", "#DesiFood", "#IndianCooking", "#Foodie"],
}

def extract_topic_tags(headline):
    """Extract person/company/event/place hashtags from headline."""
    tags = []
    # Common patterns - person names (2+ capitalized words)
    words = headline.split()
    i = 0
    while i < len(words) - 1:
        w1 = re.sub(r'[^A-Za-z]', '', words[i])
        w2 = re.sub(r'[^A-Za-z]', '', words[i+1])
        if w1 and w2 and w1[0].isupper() and w2[0].isupper() and len(w1) > 1 and len(w2) > 1:
            tag = f"#{w1}{w2}"
            if len(tag) <= 30 and tag not in tags:
                tags.append(tag)
            i += 2
            continue
        i += 1
    # Single notable words
    notable = re.findall(r'\b([A-Z][a-z]{2,}(?:[A-Z][a-z]+)*)\b', headline)
    for w in notable:
        tag = f"#{w}"
        if tag not in tags and len(tag) > 4 and w.lower() not in ('the', 'for', 'and', 'with', 'from', 'into', 'over', 'after', 'what', 'how', 'why', 'new', 'says', 'could', 'will', 'has', 'have', 'been', 'more', 'most', 'about', 'like', 'than', 'just', 'also', 'back', 'year', 'years', 'first', 'last', 'next', 'here', 'there', 'where', 'when', 'then', 'this', 'that', 'these', 'those', 'some', 'other', 'many', 'much', 'every', 'still', 'only', 'even', 'well', 'very', 'real', 'now', 'out', 'way', 'big', 'top', 'best', 'key', 'set', 'gets', 'got', 'makes', 'made', 'take', 'takes', 'amid', 'amid', 'report', 'reports', 'global'):
            tags.append(tag)
    return tags[:4]

def build_caption(article):
    cat = (article.get('category') or 'news').lower()
    cat_tags = CATEGORY_TAGS.get(cat, CATEGORY_TAGS['news'])
    topic_tags = extract_topic_tags(article['headline'])
    
    all_tags = list(cat_tags)
    for t in topic_tags:
        if t not in all_tags:
            all_tags.append(t)
    all_tags.append("#TheVideshi")
    all_tags.append("#Reels")
    # Cap at 20
    all_tags = all_tags[:20]
    
    caption = f"""{article['headline']}

📰 Read more: https://thevideshi.com/articles/{article['slug']}

{' '.join(all_tags)}"""
    return caption

# ── Step 3: Generate and post Reel for first article ─────────────
reel_article = batch[0]
reel_posted = False
reel_error = None

print(f"\n[STEP 3] Generating reel for: {reel_article['headline'][:60]}...")
try:
    result = subprocess.run(
        ["python3", "generate-reel.py", "--slug", reel_article['slug'], "--upload"],
        cwd=os.path.expanduser("~/workspace/the-videshi-news/pipeline"),
        capture_output=True, text=True, timeout=180
    )
    print(f"[REEL GEN] exit={result.returncode}")
    stdout_lines = result.stdout.strip().split('\n') if result.stdout else []
    for line in stdout_lines[-20:]:
        print(f"  > {line}")
    if result.stderr:
        for line in result.stderr.strip().split('\n')[-10:]:
            print(f"  [err] {line}")
    
    # Find the Supabase public URL
    reel_url = None
    for line in stdout_lines:
        m = re.search(r'(https://[^\s]*supabase\.co/storage/[^\s]+\.mp4)', line)
        if m:
            reel_url = m.group(1)
            break
    
    if not reel_url:
        # Try broader URL match
        for line in stdout_lines:
            if 'supabase' in line and '.mp4' in line:
                m = re.search(r'(https://[^\s]+\.mp4)', line)
                if m:
                    reel_url = m.group(1)
                    break
    
    if not reel_url:
        raise Exception(f"No reel URL found in output. Last lines: {stdout_lines[-5:]}")
    
    print(f"[OK] Reel URL: {reel_url}")

    # Upload cover image
    slug_trunc = reel_article['slug'][:80]
    cover_local = os.path.expanduser(f"~/workspace/the-videshi-news/pipeline/reels/reel-{slug_trunc}-cover.jpg")
    cover_public_url = None
    if os.path.exists(cover_local):
        cover_filename = f"reels/{slug_trunc}-cover.jpg"
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
                timeout=30
            )
        if cr.status_code in (200, 201):
            cover_public_url = f"{SB_URL}/storage/v1/object/public/article-images/{cover_filename}"
            print(f"[OK] Cover uploaded: {cover_public_url}")
        else:
            print(f"[WARN] Cover upload failed: {cr.status_code} {cr.text[:200]}")
    else:
        print(f"[INFO] No cover image found at {cover_local}")

    # Create reel container
    caption = build_caption(reel_article)
    container_data = {
        "video_url": reel_url,
        "media_type": "REELS",
        "caption": caption,
        "access_token": IG_TOKEN
    }
    if cover_public_url:
        container_data["cover_url"] = cover_public_url
    
    print(f"\n[STEP 3B] Creating reel container...")
    r = requests.post(
        f"https://graph.instagram.com/v25.0/{IG_USER_ID}/media",
        data=container_data,
        timeout=30
    )
    rj = r.json()
    print(f"[API] Container response: {rj}")
    
    if 'id' not in rj:
        raise Exception(f"Container creation failed: {rj}")
    
    container_id = rj['id']
    
    # Poll for processing
    print(f"[STEP 3C] Waiting for video processing (container={container_id})...")
    finished = False
    for i in range(18):
        time.sleep(5)
        r_status = requests.get(
            f"https://graph.instagram.com/v25.0/{container_id}",
            params={"fields": "status_code", "access_token": IG_TOKEN},
            timeout=15
        )
        status = r_status.json().get('status_code', '?')
        print(f"  Poll {i+1}/18: {status}")
        if status == 'FINISHED':
            finished = True
            break
        elif status == 'ERROR':
            raise Exception(f"Video processing error: {r_status.json()}")
    
    if not finished:
        raise Exception("Video processing timed out (90s)")
    
    # Publish
    print(f"[STEP 3D] Publishing reel...")
    r2 = requests.post(
        f"https://graph.instagram.com/v25.0/{IG_USER_ID}/media_publish",
        data={"creation_id": container_id, "access_token": IG_TOKEN},
        timeout=30
    )
    r2j = r2.json()
    print(f"[API] Publish response: {r2j}")
    
    if 'id' in r2j:
        reel_posted = True
        print(f"[OK] Reel published! Media ID: {r2j['id']}")
        
        # Mark as instagrammed
        now_utc = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        pr = requests.patch(
            f"{SB_URL}/rest/v1/p2_articles?id=eq.{reel_article['id']}",
            headers={**headers, "Prefer": "return=minimal"},
            json={"instagrammed_at": now_utc},
            timeout=15
        )
        print(f"[OK] Marked instagrammed_at for {reel_article['id']} (status={pr.status_code})")
    else:
        raise Exception(f"Publish failed: {r2j}")

except Exception as e:
    reel_error = str(e)
    print(f"[ERROR] Reel posting failed: {e}")

# ── Step 4: Post Story for second article ────────────────────────
story_posted = False
story_error = None
story_article = batch[1] if len(batch) > 1 else batch[0]

# Use a different article for story if possible
if len(batch) > 1:
    story_article = batch[1]
else:
    story_article = batch[0]

print(f"\n[STEP 4] Posting story for: {story_article['headline'][:60]}...")
time.sleep(30)  # Rate limit buffer

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
    print(f"[API] Story container response: {rj}")
    
    if 'id' not in rj:
        raise Exception(f"Story container failed: {rj}")
    
    container_id = rj['id']
    time.sleep(8)
    
    # Publish story
    r2 = requests.post(
        f"https://graph.instagram.com/v25.0/{IG_USER_ID}/media_publish",
        data={"creation_id": container_id, "access_token": IG_TOKEN},
        timeout=30
    )
    r2j = r2.json()
    print(f"[API] Story publish response: {r2j}")
    
    if 'id' in r2j:
        story_posted = True
        print(f"[OK] Story published! Media ID: {r2j['id']}")
        
        # Mark instagrammed if different from reel article
        if story_article['id'] != reel_article['id']:
            now_utc = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
            pr = requests.patch(
                f"{SB_URL}/rest/v1/p2_articles?id=eq.{story_article['id']}",
                headers={**headers, "Prefer": "return=minimal"},
                json={"instagrammed_at": now_utc},
                timeout=15
            )
            print(f"[OK] Marked instagrammed_at for {story_article['id']} (status={pr.status_code})")
    else:
        raise Exception(f"Story publish failed: {r2j}")

except Exception as e:
    story_error = str(e)
    print(f"[WARN] Story posting failed: {e}")

# ── Summary ──────────────────────────────────────────────────────
print(f"\n{'='*50}")
print(f"INSTAGRAM AUTO-POST SUMMARY")
print(f"{'='*50}")
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
print(f"{'='*50}")
