#!/usr/bin/env python3
"""Instagram autopost for The Videshi — posts Reels + Stories."""

import os, sys, re, json, time, subprocess, datetime, requests

# ── Load credentials ──────────────────────────────────────────────
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

IG_USER_ID = ig_env['INSTAGRAM_USER_ID']
TOKEN = ig_env['INSTAGRAM_ACCESS_TOKEN']
IG_APP_SECRET = ig_env['INSTAGRAM_APP_SECRET']
SB_KEY = sb_env['SUPABASE_SERVICE_ROLE_KEY']
SUPABASE_URL = 'https://lboecaekpynbpyijrbfz.supabase.co'

# ── Step 1: Refresh token ────────────────────────────────────────
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
            # Save back
            ig_path = os.path.expanduser('~/workspace/.env.instagram')
            with open(ig_path) as f:
                content = f.read()
            content = re.sub(
                r'INSTAGRAM_ACCESS_TOKEN=.*',
                f'INSTAGRAM_ACCESS_TOKEN={TOKEN}',
                content
            )
            with open(ig_path, 'w') as f:
                f.write(content)
            print(f"Token refreshed and saved (expires in {rj.get('expires_in', '?')}s)")
        else:
            print(f"Token unchanged (expires in {rj.get('expires_in', '?')}s)")
    else:
        print(f"Token refresh warning: {rj}")
except Exception as e:
    print(f"Token refresh failed (non-fatal): {e}")

# ── Step 2: Fetch unposted articles ─────────────────────────────
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
    print(f"ERROR: Supabase fetch failed: {r.status_code} {r.text[:300]}")
    sys.exit(1)

articles = r.json()
# Filter out any with empty/null image_url just in case
articles = [a for a in articles if a.get('image_url')]
print(f"Found {len(articles)} unposted articles with images")

if not articles:
    print("Nothing to post. Exiting.")
    sys.exit(0)

# Pick up to 2
batch = articles[:2]
for i, a in enumerate(batch):
    print(f"  [{i+1}] {a['category']}: {a['headline'][:80]}...")

# ── Hashtag builder ──────────────────────────────────────────────
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
    """Extract person names, companies, events from headline."""
    tags = []
    # Common patterns
    patterns = [
        # Person names (capitalized multi-word)
        (r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b', lambda m: '#' + m.group(1).replace(' ', '')),
    ]
    # Known entities
    known = {
        'Modi': '#Modi', 'Narendra Modi': '#NarendraModi', 'Trump': '#Trump',
        'Kohli': '#ViratKohli', 'Virat Kohli': '#ViratKohli',
        'Rohit Sharma': '#RohitSharma', 'Dhoni': '#Dhoni', 'MS Dhoni': '#MSDhoni',
        'Bumrah': '#JaspritBumrah', 'Hardik Pandya': '#HardikPandya',
        'Shah Rukh Khan': '#ShahRukhKhan', 'SRK': '#SRK',
        'Alia Bhatt': '#AliaBhatt', 'Deepika': '#DeepikaPadukone',
        'Priyanka Chopra': '#PriyankaChopra', 'Ranveer Singh': '#RanveerSingh',
        'Infosys': '#Infosys', 'TCS': '#TCS', 'Wipro': '#Wipro',
        'Google': '#Google', 'Apple': '#Apple', 'Microsoft': '#Microsoft',
        'Tesla': '#Tesla', 'OpenAI': '#OpenAI', 'Meta': '#Meta',
        'IPL': '#IPL2026', 'T20': '#T20WorldCup', 'Champions Trophy': '#ChampionsTrophy',
        'H1B': '#H1BVisa', 'H-1B': '#H1BVisa',
        'Mumbai': '#Mumbai', 'Delhi': '#Delhi', 'Bangalore': '#Bangalore',
        'Hyderabad': '#Hyderabad', 'Chennai': '#Chennai',
        'New York': '#NewYork', 'Silicon Valley': '#SiliconValley',
        'Adani': '#Adani', 'Ambani': '#Ambani', 'Ratan Tata': '#RatanTata',
        'Sachin': '#SachinTendulkar', 'Tendulkar': '#SachinTendulkar',
        'Sundar Pichai': '#SundarPichai', 'Satya Nadella': '#SatyaNadella',
        'Sam Altman': '#SamAltman', 'Elon Musk': '#ElonMusk',
        'BCCI': '#BCCI', 'ICC': '#ICC',
        'Bollywood': '#Bollywood', 'Tollywood': '#Tollywood',
        'AI': '#AI', 'ChatGPT': '#ChatGPT',
        'Sensex': '#Sensex', 'Nifty': '#Nifty',
        'Rahul Gandhi': '#RahulGandhi', 'Amit Shah': '#AmitShah',
        'Kejriwal': '#Kejriwal', 'Yogi': '#YogiAdityanath',
        'Jaishankar': '#Jaishankar',
        'RBI': '#RBI', 'Fed': '#FederalReserve',
        'Diljit': '#DiljitDosanjh', 'Diljit Dosanjh': '#DiljitDosanjh',
        'Arijit Singh': '#ArijitSingh',
    }
    headline_lower = headline.lower()
    for entity, tag in known.items():
        if entity.lower() in headline_lower:
            if tag not in tags:
                tags.append(tag)
    # Also try extracting capitalized proper nouns not already caught
    words = re.findall(r'\b([A-Z][a-z]{2,}(?:\s+[A-Z][a-z]{2,})*)\b', headline)
    skip = {'The', 'And', 'For', 'With', 'From', 'After', 'Before', 'Over', 'Under',
            'About', 'Into', 'Through', 'During', 'Without', 'Between', 'Behind',
            'Beyond', 'Why', 'How', 'What', 'When', 'Where', 'Who', 'Which',
            'India', 'Indian', 'American', 'Global', 'New', 'Big', 'Top', 'Best',
            'First', 'Last', 'Next', 'More', 'Most', 'Other', 'Every', 'Each',
            'Read', 'Could', 'Would', 'Should', 'Will', 'Can', 'May', 'Must',
            'South', 'North', 'East', 'West', 'Asian', 'World'}
    for w in words:
        if w not in skip and len(w) > 3:
            tag = '#' + w.replace(' ', '')
            if tag not in tags:
                tags.append(tag)
            if len(tags) >= max_tags:
                break
    return tags[:max_tags]

def build_caption(article):
    cat = article.get('category', 'news').lower()
    cat_tags = CATEGORY_HASHTAGS.get(cat, CATEGORY_HASHTAGS['news'])
    topic_tags = extract_topic_hashtags(article['headline'])

    all_tags = list(dict.fromkeys(cat_tags + topic_tags + ['#TheVideshi', '#Reels']))
    # Max 20 hashtags
    all_tags = all_tags[:20]

    caption = f"{article['headline']}\n\n"
    caption += f"📰 Read more: https://thevideshi.com/articles/{article['slug']}\n\n"
    caption += ' '.join(all_tags)
    return caption

def build_story_caption(article):
    """Lighter caption for stories (no Reels tag)."""
    cat = article.get('category', 'news').lower()
    cat_tags = CATEGORY_HASHTAGS.get(cat, CATEGORY_HASHTAGS['news'])[:5]
    topic_tags = extract_topic_hashtags(article['headline'], max_tags=2)
    all_tags = list(dict.fromkeys(cat_tags + topic_tags + ['#TheVideshi']))[:10]

    caption = f"📰 {article['headline']}\n\nRead more at thevideshi.com\n\n"
    caption += ' '.join(all_tags)
    return caption

# ── Step 3: Post Reel (first article) ───────────────────────────
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
    print(f"Reel generator stdout:\n{result.stdout[-1500:]}")
    if result.stderr:
        print(f"Reel generator stderr:\n{result.stderr[-500:]}")

    # Parse public URL from output
    reel_url = None
    for line in result.stdout.split('\n'):
        if 'supabase.co/storage' in line and 'http' in line:
            match = re.search(r'(https://[^\s]+supabase\.co/storage/[^\s]+)', line)
            if match:
                reel_url = match.group(1)
                break

    if not reel_url:
        print("ERROR: Could not find reel URL in generator output")
        # Try to find the file locally and upload manually
        reel_dir = os.path.expanduser("~/workspace/the-videshi-news/pipeline/reels")
        possible = [f for f in os.listdir(reel_dir) if reel_article['slug'][:40] in f and f.endswith('.mp4')]
        if possible:
            local_path = os.path.join(reel_dir, possible[0])
            print(f"Found local reel: {local_path}, uploading manually...")
            reel_filename = f"reels/{reel_article['slug'][:80]}.mp4"
            with open(local_path, 'rb') as vf:
                ur = requests.post(
                    f"{SUPABASE_URL}/storage/v1/object/article-images/{reel_filename}",
                    headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}",
                             "Content-Type": "video/mp4", "x-upsert": "true"},
                    data=vf.read(),
                    timeout=60
                )
            if ur.status_code in (200, 201):
                reel_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{reel_filename}"
                print(f"Manually uploaded reel: {reel_url}")
            else:
                print(f"Manual upload failed: {ur.status_code} {ur.text[:200]}")

    if reel_url:
        # Upload cover image
        cover_slug = reel_article['slug'][:80]
        cover_local = os.path.expanduser(f"~/workspace/the-videshi-news/pipeline/reels/reel-{cover_slug}-cover.jpg")
        cover_public_url = None
        if os.path.exists(cover_local):
            cover_filename = f"reels/{cover_slug}-cover.jpg"
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
                print(f"Cover upload failed (non-fatal): {cr.status_code}")
        else:
            print(f"No cover image found at {cover_local}")

        # Create Reel container
        caption = build_caption(reel_article)
        print(f"\nCaption ({len(caption)} chars):\n{caption[:200]}...\n")

        container_data = {
            "video_url": reel_url,
            "media_type": "REELS",
            "caption": caption,
            "access_token": TOKEN
        }
        if cover_public_url:
            container_data["cover_url"] = cover_public_url

        print("Creating Reel container...")
        rc = requests.post(
            f"https://graph.instagram.com/v25.0/{IG_USER_ID}/media",
            data=container_data,
            timeout=30
        )
        rcj = rc.json()
        print(f"Container response: {rcj}")

        if 'id' in rcj:
            container_id = rcj['id']

            # Poll until FINISHED
            print("Waiting for video processing...")
            finished = False
            for i in range(18):
                time.sleep(5)
                rs = requests.get(
                    f"https://graph.instagram.com/v25.0/{container_id}",
                    params={"fields": "status_code", "access_token": TOKEN},
                    timeout=15
                )
                status = rs.json().get('status_code', 'UNKNOWN')
                print(f"  Poll {i+1}/18: {status}")
                if status == 'FINISHED':
                    finished = True
                    break
                elif status == 'ERROR':
                    print(f"  ERROR in processing: {rs.json()}")
                    break

            if finished:
                # Publish
                print("Publishing Reel...")
                rp = requests.post(
                    f"https://graph.instagram.com/v25.0/{IG_USER_ID}/media_publish",
                    data={"creation_id": container_id, "access_token": TOKEN},
                    timeout=30
                )
                rpj = rp.json()
                print(f"Publish response: {rpj}")

                if 'id' in rpj:
                    reel_posted = True
                    print(f"✅ Reel published! Media ID: {rpj['id']}")

                    # Update Supabase
                    now_utc = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
                    up = requests.patch(
                        f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{reel_article['id']}",
                        headers={**headers, "Prefer": "return=minimal"},
                        json={"instagrammed_at": now_utc},
                        timeout=15
                    )
                    print(f"Supabase update: {up.status_code}")
                else:
                    print(f"❌ Reel publish failed: {rpj}")
            else:
                print("❌ Video processing did not finish in time")
        else:
            print(f"❌ Container creation failed: {rcj}")
    else:
        print("❌ No reel URL available, skipping reel post")

except subprocess.TimeoutExpired:
    print("❌ Reel generation timed out (180s)")
except Exception as e:
    print(f"❌ Reel error: {e}")

# ── Step 4: Post Story (second article if available, else first) ─
print("\n=== Posting Story ===")
time.sleep(30)  # Rate limit buffer

# Use second article for story if we have two, otherwise use first
story_article = batch[1] if len(batch) > 1 else batch[0]
# But if the reel article is the same as the story article, that's fine for stories (different surface)

print(f"Story article: {story_article['headline'][:60]}...")

try:
    # Create story container
    sr = requests.post(
        f"https://graph.instagram.com/v25.0/{IG_USER_ID}/media",
        data={
            "image_url": story_article['image_url'],
            "media_type": "STORIES",
            "access_token": TOKEN
        },
        timeout=30
    )
    srj = sr.json()
    print(f"Story container response: {srj}")

    if 'id' in srj:
        story_container_id = srj['id']
        print("Waiting for story processing...")
        time.sleep(8)

        # Publish story
        sp = requests.post(
            f"https://graph.instagram.com/v25.0/{IG_USER_ID}/media_publish",
            data={"creation_id": story_container_id, "access_token": TOKEN},
            timeout=30
        )
        spj = sp.json()
        print(f"Story publish response: {spj}")

        if 'id' in spj:
            story_posted = True
            print(f"✅ Story published! Media ID: {spj['id']}")

            # Mark story article as instagrammed too (if different from reel article)
            if story_article['id'] != reel_article['id']:
                now_utc = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
                up2 = requests.patch(
                    f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{story_article['id']}",
                    headers={**headers, "Prefer": "return=minimal"},
                    json={"instagrammed_at": now_utc},
                    timeout=15
                )
                print(f"Story article Supabase update: {up2.status_code}")
        else:
            print(f"⚠️ Story publish failed: {spj}")
    else:
        print(f"⚠️ Story container failed: {srj}")

except Exception as e:
    print(f"⚠️ Story error (non-fatal): {e}")

# ── Summary ──────────────────────────────────────────────────────
print(f"\n{'='*50}")
print(f"SUMMARY")
print(f"  Reel posted:  {'✅ YES' if reel_posted else '❌ NO'} — {reel_article['headline'][:60]}")
print(f"  Story posted: {'✅ YES' if story_posted else '❌ NO'} — {story_article['headline'][:60]}")
print(f"{'='*50}")
