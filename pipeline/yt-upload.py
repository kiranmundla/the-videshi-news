#!/usr/bin/env python3
"""Upload unuploaded reels to YouTube Shorts."""

import json, os, re, time, sys
from datetime import datetime

# Load env files
def load_env(path):
    env = {}
    p = os.path.expanduser(path)
    if os.path.exists(p):
        for line in open(p):
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env

yt_env = load_env("~/workspace/.env.youtube")
sb_env = load_env("~/workspace/.env.supabase")

YOUTUBE_CLIENT_ID = yt_env.get("YOUTUBE_CLIENT_ID")
YOUTUBE_CLIENT_SECRET = yt_env.get("YOUTUBE_CLIENT_SECRET")
YOUTUBE_REFRESH_TOKEN = yt_env.get("YOUTUBE_REFRESH_TOKEN")
SUPABASE_URL = sb_env.get("SUPABASE_URL", "https://lboecaekpynbpyijrbfz.supabase.co")
SB_KEY = sb_env.get("SUPABASE_SERVICE_ROLE_KEY") or sb_env.get("SUPABASE_KEY") or sb_env.get("SUPABASE_ANON_KEY")

if not all([YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN]):
    print("❌ Missing YouTube credentials"); sys.exit(1)
if not SB_KEY:
    print("❌ Missing Supabase key"); sys.exit(1)

import requests as req
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

REELS_DIR = os.path.expanduser("~/workspace/the-videshi-news/pipeline/reels")
LOG_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/youtube-log.json")

# Load log
yt_log = {}
if os.path.exists(LOG_PATH):
    yt_log = json.load(open(LOG_PATH))

# Find unuploaded MP4s (exclude covers)
all_mp4s = []
for f in os.listdir(REELS_DIR):
    if f.endswith('.mp4') and not f.endswith('-cover.jpg') and f not in yt_log:
        fpath = os.path.join(REELS_DIR, f)
        all_mp4s.append((os.path.getmtime(fpath), f, fpath))

all_mp4s.sort(reverse=True)  # newest first
to_upload = all_mp4s[:2]

if not to_upload:
    print("✅ No unuploaded reels found. All caught up!")
    sys.exit(0)

print(f"Found {len(to_upload)} reel(s) to upload")

# Fetch recent articles from Supabase
print("Fetching recent articles from Supabase...")
r = req.get(
    f"{SUPABASE_URL}/rest/v1/p2_articles?status=eq.published&order=published_at.desc&limit=50&select=id,slug,headline,subheadline,category,tags",
    headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"},
    timeout=15
)
articles = r.json() if r.status_code == 200 else []
print(f"  Got {len(articles)} recent articles")

def extract_slug_words(filename):
    """Extract slug fragments from reel filename."""
    name = filename.replace('.mp4', '')
    name = re.sub(r'^reel-', '', name)
    name = re.sub(r'-\d{8}$', '', name)  # strip trailing date
    return name.split('-')

def find_matching_article(filename):
    """Find best matching article for a reel filename."""
    words = extract_slug_words(filename)
    slug_fragment = '-'.join(words)
    
    best_match = None
    best_score = 0
    
    for art in articles:
        slug = art.get('slug', '') or ''
        # Check how many words from the reel match the article slug
        score = sum(1 for w in words if w in slug and len(w) > 2)
        if score > best_score and score >= 3:
            best_score = score
            best_match = art
    
    return best_match

def make_title_from_filename(filename):
    """Construct title from filename words."""
    words = extract_slug_words(filename)
    # Capitalize and join
    title = ' '.join(w.capitalize() for w in words if len(w) > 1)
    return title[:90]

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
    """Generate hashtags based on category and headline."""
    base = '#TheVideshi #Shorts #IndianDiaspora #NRI'
    cat_tags = CATEGORY_HASHTAGS.get(category, '#IndiaNews #DesiNews')
    
    # Extract topic-specific hashtags from headline
    topic_tags = []
    # Common name patterns
    name_patterns = [
        (r'\bModi\b', '#NarendraModi'), (r'\bTrump\b', '#Trump'),
        (r'\bKohli\b', '#ViratKohli'), (r'\bDhoni\b', '#MSDhoni'),
        (r'\bIPL\b', '#IPL2026'), (r'\bBumrah\b', '#JaspritBumrah'),
        (r'\bH[- ]?1B\b', '#H1BVisa'), (r'\bOPT\b', '#OPT'),
        (r'\bUSCIS\b', '#USCIS'), (r'\bRBI\b', '#RBI'),
        (r'\bSensex\b', '#Sensex'), (r'\bNifty\b', '#Nifty'),
        (r'\bAmazon\b', '#Amazon'), (r'\bGoogle\b', '#Google'),
        (r'\bInfosys\b', '#Infosys'), (r'\bTCS\b', '#TCS'),
        (r'\bRupee\b', '#IndianRupee'), (r'\bBollywood\b', '#Bollywood'),
        (r'\bKhamenei\b', '#Khamenei'), (r'\bIran\b', '#Iran'),
        (r'\bHormuz\b', '#StraitOfHormuz'), (r'\bceasefire\b', '#Ceasefire'),
        (r'\bMounjaro\b', '#Mounjaro'), (r'\bGLP.?1\b', '#GLP1'),
        (r'\bQuad\b', '#Quad'), (r'\bDelhi\b', '#NewDelhi'),
        (r'\bMumbai\b', '#Mumbai'), (r'\bBengaluru\b', '#Bengaluru'),
        (r'\bair india\b', '#AirIndia'), (r'\bMamata\b', '#MamataBanerjee'),
    ]
    for pattern, tag in name_patterns:
        if re.search(pattern, headline, re.IGNORECASE):
            topic_tags.append(tag)
    
    all_tags = f"{base} {cat_tags} {' '.join(topic_tags[:5])}"
    return all_tags

def generate_tags_list(category, headline):
    """Generate tags array for YouTube."""
    tags = ["The Videshi", "Indian Diaspora", "NRI", "India News", "Shorts"]
    if category:
        tags.append(category.replace('-', ' ').title())
    # Extract key terms from headline
    for word in headline.split():
        clean = re.sub(r'[^a-zA-Z0-9]', '', word)
        if len(clean) > 3 and clean not in ['that', 'this', 'with', 'from', 'they', 'have', 'been', 'will', 'just', 'more', 'than']:
            tags.append(clean)
            if len(tags) >= 12:
                break
    return tags

# Build YouTube client
print("Authenticating with YouTube...")
creds = Credentials(
    token=None,
    refresh_token=YOUTUBE_REFRESH_TOKEN,
    token_uri="https://oauth2.googleapis.com/token",
    client_id=YOUTUBE_CLIENT_ID,
    client_secret=YOUTUBE_CLIENT_SECRET
)
youtube = build("youtube", "v3", credentials=creds)
print("  ✅ Authenticated")

uploaded = 0
errors = []

for i, (mtime, filename, filepath) in enumerate(to_upload):
    print(f"\n{'='*60}")
    print(f"Reel {i+1}/{len(to_upload)}: {filename}")
    
    # Find matching article
    article = find_matching_article(filename)
    
    if article:
        headline = article.get('headline', '')
        subheadline = article.get('subheadline', '') or ''
        slug = article.get('slug', '')
        category = article.get('category', 'news')
        print(f"  Matched article: {headline[:60]}...")
    else:
        headline = make_title_from_filename(filename)
        subheadline = "News for the global Indian diaspora"
        slug = re.sub(r'^reel-', '', filename.replace('.mp4', ''))
        category = 'news'
        print(f"  No article match, using filename title: {headline[:60]}")
    
    # Compose title (under 100 chars with #Shorts)
    title = headline
    if len(title) > 90:
        title = title[:87] + "..."
    title = f"{title} #Shorts"
    
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
    print(f"  Tags: {tags[:6]}...")
    
    # Upload
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
        
        media = MediaFileUpload(filepath, mimetype="video/mp4", resumable=True)
        
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
        yt_log[filename] = {
            "video_id": video_id,
            "article_slug": slug or "unknown",
            "uploaded_at": datetime.utcnow().isoformat() + "Z",
            "url": url
        }
        with open(LOG_PATH, 'w') as f:
            json.dump(yt_log, f, indent=2)
        
        uploaded += 1
        
        # Wait between uploads
        if i < len(to_upload) - 1:
            print("  Waiting 10s before next upload...")
            time.sleep(10)
    
    except Exception as e:
        err_msg = f"Error uploading {filename}: {e}"
        print(f"  ❌ {err_msg}")
        errors.append(err_msg)

print(f"\n{'='*60}")
print(f"📊 Summary: {uploaded} uploaded, {len(errors)} error(s)")
if errors:
    for e in errors:
        print(f"  ⚠️ {e}")
