#!/usr/bin/env python3
"""Instagram autopost: 1 Reel + 1 Story per run."""

import os, sys, time, json, re, subprocess, requests
from datetime import datetime, timezone

# --- Load credentials ---
def load_env(path):
    env = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env

ig_env = load_env('~/workspace/.env.instagram')
sb_env = load_env('~/workspace/.env.supabase')
app_env = load_env('~/workspace/the-videshi-news/.env')

IG_USER_ID = ig_env['INSTAGRAM_USER_ID']
IG_TOKEN = ig_env['INSTAGRAM_ACCESS_TOKEN']
IG_APP_SECRET = ig_env.get('INSTAGRAM_APP_SECRET', ig_env.get('META_APP_SECRET', ''))
SB_URL = sb_env.get('SUPABASE_URL', 'https://lboecaekpynbpyijrbfz.supabase.co')
SB_KEY = sb_env['SUPABASE_SERVICE_ROLE_KEY']

# --- Step 1: Refresh token ---
print("=== Refreshing IG token ===")
try:
    r = requests.get("https://graph.instagram.com/refresh_access_token", params={
        "grant_type": "ig_refresh_token",
        "access_token": IG_TOKEN
    }, timeout=15)
    rj = r.json()
    if 'access_token' in rj:
        new_token = rj['access_token']
        if new_token != IG_TOKEN:
            # Save back
            ig_path = os.path.expanduser('~/workspace/.env.instagram')
            with open(ig_path) as f:
                content = f.read()
            content = content.replace(IG_TOKEN, new_token)
            with open(ig_path, 'w') as f:
                f.write(content)
            IG_TOKEN = new_token
            print(f"  Token refreshed, expires in {rj.get('expires_in', '?')}s")
        else:
            print(f"  Token unchanged, expires in {rj.get('expires_in', '?')}s")
    else:
        print(f"  Token refresh response: {rj}")
except Exception as e:
    print(f"  Token refresh failed: {e} (continuing with existing token)")

# --- Step 2: Fetch articles ---
print("\n=== Fetching unposted articles ===")
headers = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}"
}
r = requests.get(
    f"{SB_URL}/rest/v1/p2_articles",
    params={
        "status": "eq.published",
        "instagrammed_at": "is.null",
        "image_url": "not.is.null",
        "order": "published_at.desc",
        "limit": "10",
        "select": "id,slug,headline,subheadline,category,image_url,published_at"
    },
    headers=headers,
    timeout=15
)
articles = r.json()
if not articles:
    print("No unposted articles with images. Nothing to do.")
    sys.exit(0)

print(f"  Found {len(articles)} unposted articles")
for a in articles[:5]:
    print(f"  - [{a['category']}] {a['headline'][:80]}...")

# Pick first 2
reel_article = articles[0]
story_article = articles[1] if len(articles) > 1 else None

# --- Hashtag logic ---
CATEGORY_HASHTAGS = {
    "news": "#India #NRI #IndiaNews #IndianDiaspora #BreakingNews #DesiNews #SouthAsian #IndianAmerican #NRINews",
    "immigration": "#Immigration #H1B #H1BVisa #NRI #GreenCard #IndianAmerican #USImmigration #VisaUpdate #USCIS #Desi",
    "nri-world": "#NRI #IndianDiaspora #NRILife #Desi #IndianAmerican #SouthAsian #DesiAbroad #NRICommunity",
    "travel": "#Travel #India #IndiaTravel #IncredibleIndia #TravelIndia #DesiTravel #Wanderlust",
    "lifestyle-health": "#Lifestyle #Desi #NRILife #IndianAmerican #DesiLifestyle #Wellness #Health #SouthAsian",
    "markets-finance": "#Markets #India #NRI #Nifty #Sensex #IndianMarkets #StockMarket #Finance #NRIInvesting",
    "technology": "#Tech #India #IndianTech #Startup #SiliconValley #AI #TechNews #IndiansinTech",
    "sports": "#Cricket #India #IPL #IndianCricket #BCCI #CricketNews #Desi #TeamIndia",
    "entertainment": "#Bollywood #Entertainment #IndianCinema #Desi #BollywoodNews #DesiEntertainment",
    "food": "#IndianFood #Desi #IndianCuisine #DesiFood #IndianCooking #Foodie"
}

def extract_topic_hashtags(headline, max_tags=4):
    """Extract person/company/event hashtags from headline."""
    tags = []
    # Common patterns
    patterns = {
        r'\bModi\b': '#Modi #NarendraModi',
        r'\bKohli\b': '#ViratKohli #Kohli',
        r'\bRahul\b.*\bGandhi\b': '#RahulGandhi',
        r'\bShah Rukh Khan\b|\bSRK\b': '#ShahRukhKhan #SRK',
        r'\bIPL\b': '#IPL2026',
        r'\bRCB\b': '#RCB',
        r'\bH-?1B\b': '#H1BVisa',
        r'\bEB-?2\b': '#EB2 #GreenCard',
        r'\bEB-?5\b': '#EB5 #GreenCard',
        r'\bNYU\b': '#NYU',
        r'\bColumbia\b': '#Columbia',
        r'\bBollywood\b': '#Bollywood',
        r'\bAnthrop': '#Anthropic',
        r'\bOpenAI\b': '#OpenAI',
        r'\bSpaceX\b': '#SpaceX',
        r'\bGoogle\b': '#Google',
        r'\bApple\b': '#Apple',
        r'\bMicrosoft\b': '#Microsoft',
        r'\bInfosys\b': '#Infosys',
        r'\bTCS\b': '#TCS',
        r'\bMonsoon\b': '#IndianMonsoon',
        r'\bEl Ni[ñn]o\b': '#ElNino',
        r'\bICC\b': '#ICC',
        r'\bOld Trafford\b': '#OldTrafford',
        r'\bGill\b': '#ShubmanGill',
        r'\bRahul\b(?!.*Gandhi)': '#KLRahul',
        r'\bIran\b': '#Iran',
        r'\bUS\b': '#US',
        r'\bHormuz\b': '#StraitOfHormuz',
        r'\bJacqueline\b': '#JacquelineFernandez',
        r'\bSuman Kalyanpur\b': '#SumanKalyanpur',
        r'\bLata\b': '#LataMangeshkar',
        r'\bIPO\b': '#IPO',
        r'\bCanada\b': '#Canada',
        r'\bEngland\b.*\bIndia\b|\bIndia\b.*\bEngland\b': '#ENGvIND',
        r'\bChunky Panday\b': '#ChunkyPanday',
    }
    for pattern, tag in patterns.items():
        if re.search(pattern, headline, re.IGNORECASE):
            tags.extend(tag.split())
    # Deduplicate
    seen = set()
    unique = []
    for t in tags:
        tl = t.lower()
        if tl not in seen:
            seen.add(tl)
            unique.append(t)
    return unique[:max_tags]

def build_caption(article):
    headline = article['headline']
    slug = article['slug']
    category = article.get('category', 'news')
    
    cat_tags = CATEGORY_HASHTAGS.get(category, CATEGORY_HASHTAGS['news'])
    topic_tags = extract_topic_hashtags(headline)
    
    all_tags = cat_tags.split() + topic_tags + ['#TheVideshi', '#Reels']
    # Deduplicate and limit to 20
    seen = set()
    unique_tags = []
    for t in all_tags:
        tl = t.lower()
        if tl not in seen:
            seen.add(tl)
            unique_tags.append(t)
    hashtags = ' '.join(unique_tags[:20])
    
    caption = f"""{headline}

📰 Read more: https://thevideshi.com/articles/{slug}

{hashtags}"""
    return caption

# --- Step 3: Generate and post Reel ---
print(f"\n=== Generating Reel for: {reel_article['headline'][:70]}... ===")
reel_slug = reel_article['slug']

try:
    result = subprocess.run(
        ["python3", "generate-reel.py", "--slug", reel_slug, "--upload"],
        cwd=os.path.expanduser("~/workspace/the-videshi-news/pipeline"),
        capture_output=True, text=True, timeout=180
    )
    print(f"  generate-reel.py exit code: {result.returncode}")
    if result.stdout:
        print(f"  STDOUT (last 500 chars): ...{result.stdout[-500:]}")
    if result.stderr:
        print(f"  STDERR (last 300 chars): ...{result.stderr[-300:]}")
    
    # Extract Supabase URL from output
    reel_url = None
    for line in result.stdout.split('\n'):
        if 'supabase.co/storage' in line and 'http' in line:
            match = re.search(r'(https://[^\s"\']+supabase\.co/storage/[^\s"\']+)', line)
            if match:
                reel_url = match.group(1)
                break
    
    if not reel_url:
        # Try alternative patterns
        for line in result.stdout.split('\n'):
            if 'http' in line and ('reel' in line.lower() or '.mp4' in line.lower()):
                match = re.search(r'(https://[^\s"\']+\.mp4[^\s"\']*)', line)
                if match:
                    reel_url = match.group(1)
                    break
    
    if not reel_url:
        print(f"  ERROR: Could not find reel URL in generate-reel.py output")
        print(f"  Full stdout:\n{result.stdout}")
        sys.exit(1)
    
    print(f"  Reel URL: {reel_url}")
    
except subprocess.TimeoutExpired:
    print("  ERROR: generate-reel.py timed out (180s)")
    sys.exit(1)
except Exception as e:
    print(f"  ERROR: generate-reel.py failed: {e}")
    sys.exit(1)

# Upload cover image if exists
truncated_slug = reel_slug[:80]
cover_local = os.path.expanduser(f"~/workspace/the-videshi-news/pipeline/reels/reel-{truncated_slug}-cover.jpg")
cover_public_url = None
if os.path.exists(cover_local):
    print(f"  Uploading cover image...")
    cover_filename = f"reels/{truncated_slug}-cover.jpg"
    with open(cover_local, 'rb') as cf:
        cr = requests.post(
            f"{SB_URL}/storage/v1/object/article-images/{cover_filename}",
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
        cover_public_url = f"{SB_URL}/storage/v1/object/public/article-images/{cover_filename}"
        print(f"  Cover uploaded: {cover_public_url}")
    else:
        print(f"  Cover upload failed: {cr.status_code} {cr.text[:200]}")

# Create Reel container
print("\n=== Creating Reel container ===")
caption = build_caption(reel_article)
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
print(f"  Container response: {json.dumps(rj)}")

if 'id' not in rj:
    print(f"  ERROR: Failed to create reel container")
    sys.exit(1)

container_id = rj['id']

# Wait for processing
print("  Waiting for video processing...")
finished = False
for i in range(18):
    time.sleep(5)
    r_status = requests.get(
        f"https://graph.instagram.com/v25.0/{container_id}",
        params={"fields": "status_code", "access_token": IG_TOKEN},
        timeout=15
    )
    status = r_status.json().get('status_code', 'UNKNOWN')
    print(f"    Poll {i+1}/18: {status}")
    if status == 'FINISHED':
        finished = True
        break
    elif status == 'ERROR':
        print(f"    ERROR status returned: {r_status.json()}")
        sys.exit(1)

if not finished:
    print("  ERROR: Video processing timed out (90s)")
    sys.exit(1)

# Publish Reel
print("\n=== Publishing Reel ===")
r2 = requests.post(
    f"https://graph.instagram.com/v25.0/{IG_USER_ID}/media_publish",
    data={"creation_id": container_id, "access_token": IG_TOKEN},
    timeout=30
)
r2j = r2.json()
print(f"  Publish response: {json.dumps(r2j)}")

if 'id' not in r2j:
    print(f"  ERROR: Failed to publish reel")
    sys.exit(1)

reel_media_id = r2j['id']
print(f"  ✅ REEL PUBLISHED! Media ID: {reel_media_id}")

# Mark as instagrammed
now_utc = datetime.now(timezone.utc).isoformat()
requests.patch(
    f"{SB_URL}/rest/v1/p2_articles?id=eq.{reel_article['id']}",
    headers={**headers, "Content-Type": "application/json", "Prefer": "return=minimal"},
    json={"instagrammed_at": now_utc},
    timeout=15
)
print(f"  Marked article as instagrammed: {reel_article['id']}")

# --- Step 4: Wait then post Story ---
if story_article:
    print(f"\n=== Waiting 30s before Story ===")
    time.sleep(30)
    
    print(f"=== Posting Story for: {story_article['headline'][:70]}... ===")
    
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
    sj = r.json()
    print(f"  Story container response: {json.dumps(sj)}")
    
    if 'id' in sj:
        story_container_id = sj['id']
        time.sleep(8)
        
        r2 = requests.post(
            f"https://graph.instagram.com/v25.0/{IG_USER_ID}/media_publish",
            data={"creation_id": story_container_id, "access_token": IG_TOKEN},
            timeout=30
        )
        s2j = r2.json()
        print(f"  Story publish response: {json.dumps(s2j)}")
        
        if 'id' in s2j:
            print(f"  ✅ STORY PUBLISHED! Media ID: {s2j['id']}")
            # Mark story article as instagrammed too
            requests.patch(
                f"{SB_URL}/rest/v1/p2_articles?id=eq.{story_article['id']}",
                headers={**headers, "Content-Type": "application/json", "Prefer": "return=minimal"},
                json={"instagrammed_at": now_utc},
                timeout=15
            )
            print(f"  Marked story article as instagrammed: {story_article['id']}")
        else:
            print(f"  Story publish failed (non-fatal): {s2j}")
    else:
        print(f"  Story container creation failed (non-fatal): {sj}")

# --- Summary ---
print("\n" + "="*50)
print("SUMMARY")
print("="*50)
print(f"Reel: ✅ Published (Media ID: {reel_media_id})")
print(f"  Article: {reel_article['headline'][:80]}")
if story_article:
    print(f"Story: attempted")
    print(f"  Article: {story_article['headline'][:80]}")
print(f"Token refreshed: yes")
print("Done!")
