#!/usr/bin/env python3
"""Upload unuploaded reels to YouTube Shorts for The Videshi."""

import json, os, re, time, sys
from datetime import datetime

# Load env files
def load_env(path):
    env = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env

yt_env = load_env('~/workspace/.env.youtube')
sb_env = load_env('~/workspace/.env.supabase')

YOUTUBE_CLIENT_ID = yt_env['YOUTUBE_CLIENT_ID']
YOUTUBE_CLIENT_SECRET = yt_env['YOUTUBE_CLIENT_SECRET']
YOUTUBE_REFRESH_TOKEN = yt_env['YOUTUBE_REFRESH_TOKEN']
SUPABASE_URL = sb_env.get('SUPABASE_URL', 'https://lboecaekpynbpyijrbfz.supabase.co')
SB_KEY = sb_env.get('SUPABASE_SERVICE_KEY') or sb_env.get('SUPABASE_KEY') or sb_env.get('SUPABASE_ANON_KEY')

REELS_DIR = os.path.expanduser('~/workspace/the-videshi-news/pipeline/reels')
LOG_PATH = os.path.expanduser('~/workspace/the-videshi-news/pipeline/youtube-log.json')

# Load tracking log
yt_log = json.load(open(LOG_PATH)) if os.path.exists(LOG_PATH) else {}

# Get unuploaded reels sorted by mtime newest first
files = [f for f in os.listdir(REELS_DIR) if f.endswith('.mp4')]
files.sort(key=lambda f: os.path.getmtime(os.path.join(REELS_DIR, f)), reverse=True)
unuploaded = [f for f in files if f not in yt_log and 'test' not in f.lower()]

if not unuploaded:
    print("✅ No new reels to upload.")
    sys.exit(0)

print(f"Found {len(unuploaded)} unuploaded reel(s). Processing up to 2.")

# Fetch recent articles from Supabase
import requests as req

r = req.get(
    f"{SUPABASE_URL}/rest/v1/p2_articles?status=eq.published&order=published_at.desc&limit=50&select=id,slug,headline,subheadline,category,tags",
    headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"},
    timeout=15
)
articles = r.json()
print(f"Fetched {len(articles)} recent articles for matching.")

def extract_slug_words(filename):
    """Strip reel- prefix, trailing date, and .mp4 to get slug fragments."""
    name = filename.replace('.mp4', '')
    name = re.sub(r'^reel-', '', name)
    # Remove trailing date patterns like -20260605 or -2026060
    name = re.sub(r'-\d{7,8}$', '', name)
    return name.split('-')

def match_article(filename, articles):
    """Find best matching article by slug word overlap."""
    words = extract_slug_words(filename)
    slug_fragment = '-'.join(words)
    
    best_match = None
    best_score = 0
    
    for art in articles:
        slug = art.get('slug', '')
        # Check if slug contains the fragment
        if slug_fragment in slug:
            return art
        # Count word overlap
        score = sum(1 for w in words if w in slug and len(w) > 2)
        if score > best_score:
            best_score = score
            best_match = art
    
    if best_score >= 3:
        return best_match
    return None

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
    # Common person/topic patterns
    words = re.findall(r'[A-Z][a-z]+(?:\s[A-Z][a-z]+)?', headline or '')
    for w in words[:5]:
        tag = '#' + w.replace(' ', '')
        if len(tag) > 3 and tag not in tags:
            tags.append(tag)
    return ' '.join(tags[:5])

def compose_metadata(article, filename):
    """Compose YouTube title, description, and tags."""
    if article:
        headline = article.get('headline', '')
        subheadline = article.get('subheadline', '') or ''
        slug = article.get('slug', '')
        category = article.get('category', 'news')
        art_tags = article.get('tags', []) or []
    else:
        # Construct from filename
        words = extract_slug_words(filename)
        headline = ' '.join(w.capitalize() for w in words)
        subheadline = ''
        slug = '-'.join(words)
        category = 'news'
        art_tags = []
    
    # Title: under 100 chars with #Shorts
    title = headline
    if len(title) + 8 > 100:
        title = title[:91] + '…'
    title = f"{title} #Shorts"
    
    # Category hashtags
    cat_tags = CATEGORY_HASHTAGS.get(category, '#IndiaNews #DesiNews')
    topic_tags = make_topic_hashtags(headline)
    
    hashtags = f"#TheVideshi #Shorts #IndianDiaspora #NRI {cat_tags} {topic_tags}"
    
    description = f"""{subheadline}

📰 Full story: https://thevideshi.com/articles/{slug}

The Videshi — News for the global Indian diaspora
🌐 thevideshi.com

Follow us:
📸 Instagram: https://instagram.com/the.videshi
🐦 X/Twitter: https://x.com/thevideshi
🧵 Threads: https://threads.net/@the.videshi

{hashtags}"""
    
    # Tags list
    tags = ["The Videshi", "Indian Diaspora", "NRI", "India News", category.replace('-', ' ').title(), "Shorts"]
    # Add topic words from headline
    if article and article.get('headline'):
        important_words = [w for w in article['headline'].split() if len(w) > 4 and w[0].isupper()]
        for w in important_words[:4]:
            if w not in tags:
                tags.append(w)
    # Add article tags
    if art_tags:
        for t in art_tags[:3]:
            if t not in tags:
                tags.append(t)
    tags = tags[:12]
    
    return title, description, tags, slug

# Setup YouTube API
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

for reel_filename in unuploaded[:2]:
    print(f"\n--- Processing: {reel_filename}")
    reel_path = os.path.join(REELS_DIR, reel_filename)
    
    # Match article
    article = match_article(reel_filename, articles)
    if article:
        print(f"  Matched article: {article.get('headline', 'N/A')[:80]}")
    else:
        print("  No article match found, using filename-derived metadata")
    
    title, description, tags, slug = compose_metadata(article, reel_filename)
    print(f"  Title: {title}")
    
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
    
    try:
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
        
        # Log to youtube-log.json
        yt_log[reel_filename] = {
            "video_id": video_id,
            "article_slug": slug or "unknown",
            "uploaded_at": datetime.utcnow().isoformat() + "Z",
            "url": url
        }
        with open(LOG_PATH, 'w') as f:
            json.dump(yt_log, f, indent=2)
        
        uploaded_count += 1
        results.append((reel_filename, url))
        
        # Wait between uploads
        if uploaded_count < min(2, len(unuploaded)):
            print("  Waiting 10 seconds...")
            time.sleep(10)
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        errors.append((reel_filename, str(e)))

print(f"\n{'='*60}")
print(f"SUMMARY")
print(f"{'='*60}")
print(f"Uploaded: {uploaded_count}")
for fn, url in results:
    print(f"  ✅ {fn} → {url}")
if errors:
    print(f"Errors: {len(errors)}")
    for fn, err in errors:
        print(f"  ❌ {fn}: {err}")
print(f"Skipped test reels: yes")
