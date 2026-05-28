#!/usr/bin/env python3
"""Upload unuploaded reels to YouTube Shorts."""
import os, json, time, re, glob, requests
from datetime import datetime, timezone

# --- Load credentials ---
def load_env(path):
    env = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip()
    return env

yt_env = load_env("~/workspace/.env.youtube")
sb_env = load_env("~/workspace/.env.supabase")

YOUTUBE_CLIENT_ID = yt_env["YOUTUBE_CLIENT_ID"]
YOUTUBE_CLIENT_SECRET = yt_env["YOUTUBE_CLIENT_SECRET"]
YOUTUBE_REFRESH_TOKEN = yt_env["YOUTUBE_REFRESH_TOKEN"]
SUPABASE_URL = sb_env.get("SUPABASE_URL", "https://lboecaekpynbpyijrbfz.supabase.co")
SB_KEY = sb_env.get("SUPABASE_SERVICE_ROLE_KEY") or sb_env.get("SUPABASE_ANON_KEY") or sb_env.get("SB_KEY")

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
reel_files = glob.glob(os.path.join(REELS_DIR, "reel-*.mp4"))
# Filter out test/dev files
reel_files = [f for f in reel_files if not os.path.basename(f).startswith("reel-v2")]
# Sort by modification time, newest first
reel_files.sort(key=lambda f: os.path.getmtime(f), reverse=True)

unuploaded = [f for f in reel_files if os.path.basename(f) not in yt_log]

print(f"Total reels: {len(reel_files)}, Already uploaded: {len(yt_log)}, Unuploaded: {len(unuploaded)}")

if not unuploaded:
    print("✅ No new reels to upload.")
    exit(0)

to_upload = unuploaded[:MAX_UPLOADS]
print(f"Will upload {len(to_upload)} reel(s):\n")

# --- Fetch recent articles from Supabase ---
try:
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/p2_articles?status=eq.published&order=published_at.desc&limit=50&select=id,slug,headline,subheadline,category,tags",
        headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"},
        timeout=15
    )
    articles = r.json() if r.status_code == 200 else []
    print(f"Fetched {len(articles)} recent articles from Supabase")
except Exception as e:
    print(f"⚠️ Failed to fetch articles: {e}")
    articles = []

def extract_slug_fragments(filename):
    """Extract slug fragments from reel filename."""
    name = filename.replace(".mp4", "")
    if name.startswith("reel-"):
        name = name[5:]
    # Remove trailing date (YYYYMMDD)
    name = re.sub(r'-\d{8}$', '', name)
    return name.split('-')

def match_article(filename, articles):
    """Find matching article by slug fragments."""
    fragments = extract_slug_fragments(filename)
    frag_str = '-'.join(fragments)
    
    best_match = None
    best_score = 0
    
    for art in articles:
        slug = art.get('slug', '')
        if not slug:
            continue
        # Count how many fragments appear in the slug
        score = sum(1 for f in fragments if f in slug)
        ratio = score / max(len(fragments), 1)
        if ratio > best_score and ratio >= 0.5:
            best_score = ratio
            best_match = art
    
    return best_match

def make_title_from_filename(filename):
    """Fallback: construct title from filename words."""
    name = filename.replace(".mp4", "").replace("reel-", "")
    name = re.sub(r'-\d{8}$', '', name)
    words = name.split('-')
    return ' '.join(w.capitalize() for w in words)

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

def generate_hashtags(category, headline):
    """Generate 15-20 hashtags."""
    base = '#TheVideshi #Shorts #IndianDiaspora #NRI'
    cat_tags = CATEGORY_HASHTAGS.get(category, '#IndiaNews #DesiNews')
    
    # Extract topic-specific hashtags from headline
    topic_tags = []
    # Remove common words and create hashtags from significant words
    words = re.findall(r'[A-Z][a-z]+(?:\s[A-Z][a-z]+)?', headline or '')
    for w in words[:5]:
        tag = '#' + w.replace(' ', '').replace("'", '')
        if len(tag) > 3 and tag not in base and tag not in cat_tags:
            topic_tags.append(tag)
    
    all_tags = f"{base} {cat_tags}"
    if topic_tags:
        all_tags += ' ' + ' '.join(topic_tags[:5])
    
    return all_tags

def generate_tags_list(category, headline):
    """Generate 8-12 YouTube tags."""
    tags = ["The Videshi", "Indian Diaspora", "NRI", "India News"]
    if category:
        tags.append(category.replace('-', ' ').title())
    tags.append("Shorts")
    
    # Extract key terms from headline
    if headline:
        words = re.findall(r'[A-Z][a-z]+(?:\s[A-Z][a-z]+)?', headline)
        for w in words[:4]:
            if w not in tags:
                tags.append(w)
    
    return tags[:12]

# --- YouTube upload setup ---
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

creds = Credentials(
    token=None,
    refresh_token=YOUTUBE_REFRESH_TOKEN,
    token_uri="https://oauth2.googleapis.com/token",
    client_id=YOUTUBE_CLIENT_ID,
    client_secret=YOUTUBE_CLIENT_SECRET
)

youtube = build("youtube", "v3", credentials=creds)

uploaded_count = 0
errors = []
results = []

for i, reel_path in enumerate(to_upload):
    filename = os.path.basename(reel_path)
    print(f"\n--- Uploading {i+1}/{len(to_upload)}: {filename} ---")
    
    # Match article
    article = match_article(filename, articles)
    
    if article:
        headline = article.get('headline', '')
        subheadline = article.get('subheadline', '')
        slug = article.get('slug', '')
        category = article.get('category', 'news')
        print(f"  Matched article: {headline[:80]}")
    else:
        headline = make_title_from_filename(filename)
        subheadline = "Latest news for the global Indian diaspora."
        slug = filename.replace('.mp4', '').replace('reel-', '')
        category = 'news'
        print(f"  No article match, using filename title: {headline[:80]}")
    
    # Compose title (under 100 chars, with #Shorts)
    shorts_suffix = " #Shorts"
    max_len = 100 - len(shorts_suffix)
    title = headline
    if len(title) > max_len:
        title = title[:max_len - 1].rsplit(' ', 1)[0]  # word-boundary cut
    title = f"{title}{shorts_suffix}"
    
    # Compose description
    hashtags = generate_hashtags(category, headline)
    description = f"""{subheadline}

📰 Full story: https://thevideshi.com/articles/{slug}

The Videshi — News for the global Indian diaspora
🌐 thevideshi.com

Follow us:
📸 Instagram: https://instagram.com/the.videshi
🐦 X/Twitter: https://x.com/thevideshi
🧵 Threads: https://threads.net/@the.videshi

{hashtags}"""
    
    tags = generate_tags_list(category, headline)
    
    print(f"  Title: {title}")
    print(f"  Category: {category}")
    print(f"  Tags: {tags}")
    
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
        
        # Log to tracking file
        yt_log[filename] = {
            "video_id": video_id,
            "article_slug": slug or "unknown",
            "uploaded_at": datetime.now(timezone.utc).isoformat(),
            "url": url
        }
        with open(LOG_PATH, 'w') as f:
            json.dump(yt_log, f, indent=2)
        
        uploaded_count += 1
        results.append((filename, url))
        
        # Wait between uploads
        if i < len(to_upload) - 1:
            print("  Waiting 10 seconds...")
            time.sleep(10)
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        errors.append((filename, str(e)))

# --- Summary ---
print(f"\n{'='*60}")
print(f"SUMMARY: {uploaded_count} uploaded, {len(errors)} errors")
for fn, url in results:
    print(f"  ✅ {fn} → {url}")
for fn, err in errors:
    print(f"  ❌ {fn}: {err}")
print(f"{'='*60}")
