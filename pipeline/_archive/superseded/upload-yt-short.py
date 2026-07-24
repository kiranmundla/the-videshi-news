#!/usr/bin/env python3
"""Upload unuploaded Instagram Reels as YouTube Shorts for The Videshi."""

import json, os, re, time, sys
from datetime import datetime, timezone

import requests as req
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# --- Load credentials ---
def load_env(path):
    env = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env

yt_env = load_env("~/workspace/.env.youtube")
sb_env = load_env("~/workspace/.env.supabase")

YOUTUBE_CLIENT_ID = yt_env["YOUTUBE_CLIENT_ID"]
YOUTUBE_CLIENT_SECRET = yt_env["YOUTUBE_CLIENT_SECRET"]
YOUTUBE_REFRESH_TOKEN = yt_env["YOUTUBE_REFRESH_TOKEN"]

SUPABASE_URL = sb_env.get("SUPABASE_URL", "https://lboecaekpynbpyijrbfz.supabase.co")
SB_KEY = sb_env.get("SUPABASE_ANON_KEY") or sb_env.get("SUPABASE_KEY") or sb_env.get("SUPABASE_SERVICE_ROLE_KEY")

REELS_DIR = os.path.expanduser("~/workspace/the-videshi-news/pipeline/reels")
LOG_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/youtube-log.json")
MAX_UPLOADS = 2

# --- Load tracking log ---
if os.path.exists(LOG_PATH):
    with open(LOG_PATH) as f:
        yt_log = json.load(f)
else:
    yt_log = {}

# --- Find unuploaded reels ---
reel_files = [f for f in os.listdir(REELS_DIR) if f.endswith('.mp4')]
unuploaded = [f for f in reel_files if f not in yt_log]
# Sort by modification time, newest first
unuploaded.sort(key=lambda f: os.path.getmtime(os.path.join(REELS_DIR, f)), reverse=True)

print(f"Total reels: {len(reel_files)}, Already uploaded: {len(yt_log)}, Unuploaded: {len(unuploaded)}")

if not unuploaded:
    print("✅ No new reels to upload.")
    sys.exit(0)

to_upload = unuploaded[:MAX_UPLOADS]
print(f"Will upload {len(to_upload)} reel(s):")
for f in to_upload:
    print(f"  - {f}")

# --- Fetch recent articles from Supabase ---
print("\nFetching recent articles from Supabase...")
r = req.get(
    f"{SUPABASE_URL}/rest/v1/p2_articles?status=eq.published&order=published_at.desc&limit=50&select=id,slug,headline,subheadline,category,tags",
    headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"},
    timeout=15
)
articles = r.json() if r.status_code == 200 else []
print(f"  Fetched {len(articles)} recent articles")

def extract_slug_fragments(filename):
    """Extract slug fragments from reel filename."""
    name = filename.replace('.mp4', '')
    name = re.sub(r'^reel-', '', name)
    # Remove trailing date (YYYYMMDD)
    name = re.sub(r'-\d{8}$', '', name)
    return name.split('-')

def find_matching_article(filename, articles):
    """Find the best matching article for a reel filename."""
    fragments = extract_slug_fragments(filename)
    frag_str = '-'.join(fragments)
    
    best_match = None
    best_score = 0
    
    for article in articles:
        slug = article.get('slug', '')
        if not slug:
            continue
        # Check how many fragments appear in the slug
        score = sum(1 for frag in fragments if frag in slug)
        # Bonus for consecutive fragment match
        if frag_str in slug:
            score += len(fragments)
        if score > best_score and score >= max(3, len(fragments) * 0.4):
            best_score = score
            best_match = article
    
    return best_match

CATEGORY_HASHTAGS = {
    'news': '#IndiaNews #BreakingNews #DesiNews #SouthAsian',
    'immigration': '#H1B #H1BVisa #GreenCard #USImmigration #USCIS',
    'nri-world': '#NRILife #DesiAbroad #IndianAmerican',
    'travel': '#TravelIndia #IncredibleIndia #IndiaTravel',
    'lifestyle-health': '#DesiLifestyle #Wellness #Health',
    'markets-finance': '#StockMarket #Nifty #Sensex #IndianMarkets',
    'technology': '#TechNews #IndianTech #SiliconValley #AI',
    'sports': '#Cricket #IPL #IPL2026 #TeamIndia #BCCI',
    'entertainment': '#Bollywood #BollywoodNews #IndianCinema #Tollywood',
    'food': '#IndianFood #IndianCuisine #DesiFood',
}

def make_topic_hashtags(headline):
    """Extract topic-specific hashtags from headline."""
    tags = []
    # Known person/entity patterns
    known = {
        'modi': '#NarendraModi', 'kohli': '#ViratKohli', 'rohit': '#RohitSharma',
        'dhoni': '#MSDhoni', 'trump': '#Trump', 'mamata': '#MamataBanerjee',
        'bjp': '#BJP', 'congress': '#Congress', 'tmc': '#TMC',
        'bengal': '#WestBengal', 'mumbai': '#Mumbai', 'delhi': '#Delhi',
        'ipl': '#IPL2026', 'bcci': '#BCCI', 'rbi': '#RBI',
        'infosys': '#Infosys', 'tcs': '#TCS', 'wipro': '#Wipro',
        'adani': '#Adani', 'ambani': '#Ambani', 'jaishankar': '#Jaishankar',
        'governor': '#Governor', 'assembly': '#Assembly',
    }
    hl_lower = headline.lower()
    for key, tag in known.items():
        if key in hl_lower and tag not in tags:
            tags.append(tag)
    return tags[:5]

def compose_metadata(article, filename):
    """Compose YouTube metadata for a reel."""
    if article:
        headline = article.get('headline', '')
        subheadline = article.get('subheadline', '') or ''
        slug = article.get('slug', '')
        category = article.get('category', 'news')
        article_tags = article.get('tags', []) or []
    else:
        # Construct from filename
        fragments = extract_slug_fragments(filename)
        headline = ' '.join(w.capitalize() for w in fragments)
        subheadline = ''
        slug = 'unknown'
        category = 'news'
        article_tags = []
    
    # Title: under 100 chars, with #Shorts
    title = headline
    if len(title) > 90:
        title = title[:87] + '...'
    title = f"{title} #Shorts"
    
    # Category hashtags
    cat_tags = CATEGORY_HASHTAGS.get(category, '#IndiaNews #DesiNews')
    topic_tags = make_topic_hashtags(headline)
    topic_str = ' '.join(topic_tags)
    
    hashtags = f"#TheVideshi #Shorts #IndianDiaspora #NRI {cat_tags} {topic_str}".strip()
    
    # Description
    article_link = f"https://thevideshi.com/articles/{slug}" if slug != 'unknown' else "https://thevideshi.com"
    description = f"""{subheadline}

📰 Full story: {article_link}

The Videshi — News for the global Indian diaspora
🌐 thevideshi.com

Follow us:
📸 Instagram: https://instagram.com/the.videshi
🐦 X/Twitter: https://x.com/thevideshi
🧵 Threads: https://threads.net/@the.videshi

{hashtags}"""
    
    # Tags list
    yt_tags = ["The Videshi", "Indian Diaspora", "NRI", "India News", category.replace('-', ' ').title(), "Shorts"]
    # Add topic tags
    for t in topic_tags:
        clean = t.replace('#', '')
        if clean not in yt_tags:
            yt_tags.append(clean)
    # Pad to 8-12
    for extra in article_tags[:4]:
        if extra not in yt_tags:
            yt_tags.append(extra)
    yt_tags = yt_tags[:12]
    
    return title, description, yt_tags, slug

# --- Build YouTube client ---
print("\nAuthenticating with YouTube...")
creds = Credentials(
    token=None,
    refresh_token=YOUTUBE_REFRESH_TOKEN,
    token_uri="https://oauth2.googleapis.com/token",
    client_id=YOUTUBE_CLIENT_ID,
    client_secret=YOUTUBE_CLIENT_SECRET
)
youtube = build("youtube", "v3", credentials=creds)
print("  ✅ YouTube client ready")

# --- Upload reels ---
uploaded_count = 0
errors = []
results = []

for i, reel_filename in enumerate(to_upload):
    reel_path = os.path.join(REELS_DIR, reel_filename)
    print(f"\n{'='*60}")
    print(f"[{i+1}/{len(to_upload)}] Uploading: {reel_filename}")
    print(f"  File size: {os.path.getsize(reel_path) / 1024 / 1024:.1f} MB")
    
    # Find matching article
    article = find_matching_article(reel_filename, articles)
    if article:
        print(f"  Matched article: {article['headline'][:80]}")
    else:
        print(f"  ⚠️ No article match found, using filename-derived title")
    
    title, description, tags, slug = compose_metadata(article, reel_filename)
    print(f"  Title: {title}")
    
    try:
        body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags,
                "categoryId": "25"
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False
            }
        }
        
        media = MediaFileUpload(reel_path, mimetype="video/mp4", resumable=True)
        
        request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media
        )
        
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"  Upload progress: {int(status.progress() * 100)}%")
        
        video_id = response["id"]
        url = f"https://youtube.com/shorts/{video_id}"
        print(f"  ✅ Uploaded: {url}")
        
        # Log
        yt_log[reel_filename] = {
            "video_id": video_id,
            "article_slug": slug or "unknown",
            "uploaded_at": datetime.now(timezone.utc).isoformat(),
            "url": url
        }
        with open(LOG_PATH, 'w') as f:
            json.dump(yt_log, f, indent=2)
        
        uploaded_count += 1
        results.append((reel_filename, url))
        
        # Wait between uploads
        if i < len(to_upload) - 1:
            print("  Waiting 10 seconds...")
            time.sleep(10)
    
    except Exception as e:
        err_msg = f"Failed to upload {reel_filename}: {e}"
        print(f"  ❌ {err_msg}")
        errors.append(err_msg)

# --- Summary ---
print(f"\n{'='*60}")
print(f"📊 SUMMARY")
print(f"  Uploaded: {uploaded_count}/{len(to_upload)}")
for fn, url in results:
    print(f"  ✅ {fn} → {url}")
if errors:
    print(f"  Errors: {len(errors)}")
    for e in errors:
        print(f"  ❌ {e}")
print(f"  Total in log: {len(yt_log)}")
