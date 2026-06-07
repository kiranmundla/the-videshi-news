#!/usr/bin/env python3
"""Upload unuploaded reels to YouTube Shorts."""

import json, os, sys, time, re, glob, requests
from datetime import datetime

# --- Load env ---
def load_env(path):
    env = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip()
    return env

yt_env = load_env('~/workspace/.env.youtube')
sb_env = load_env('~/workspace/.env.supabase')

YOUTUBE_CLIENT_ID = yt_env['YOUTUBE_CLIENT_ID']
YOUTUBE_CLIENT_SECRET = yt_env['YOUTUBE_CLIENT_SECRET']
YOUTUBE_REFRESH_TOKEN = yt_env['YOUTUBE_REFRESH_TOKEN']
SUPABASE_URL = sb_env.get('SUPABASE_URL', 'https://lboecaekpynbpyijrbfz.supabase.co')
SB_KEY = sb_env.get('SUPABASE_SERVICE_KEY', sb_env.get('SUPABASE_ANON_KEY', ''))

REELS_DIR = os.path.expanduser('~/workspace/the-videshi-news/pipeline/reels')
LOG_PATH = os.path.expanduser('~/workspace/the-videshi-news/pipeline/youtube-log.json')

# --- Load tracking log ---
yt_log = json.load(open(LOG_PATH)) if os.path.exists(LOG_PATH) else {}

# --- Find unuploaded reels (skip test reels) ---
reels = sorted(glob.glob(os.path.join(REELS_DIR, '*.mp4')),
               key=lambda f: os.path.getmtime(f), reverse=True)
unuploaded = []
for r in reels:
    fname = os.path.basename(r)
    if fname in yt_log:
        continue
    if 'test' in fname.lower():
        print(f"⏭️  Skipping test reel: {fname}")
        continue
    unuploaded.append(r)

if not unuploaded:
    print("✅ No new reels to upload.")
    sys.exit(0)

print(f"📹 Found {len(unuploaded)} unuploaded reel(s). Will upload up to 2.\n")

# --- Fetch recent articles from Supabase ---
print("📰 Fetching recent articles from Supabase...")
try:
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/p2_articles?status=eq.published&order=published_at.desc&limit=50&select=id,slug,headline,subheadline,category,tags",
        headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"},
        timeout=15
    )
    articles = r.json()
    print(f"  Got {len(articles)} recent articles")
except Exception as e:
    print(f"  ⚠️ Could not fetch articles: {e}")
    articles = []

def match_article(filename):
    """Match reel filename to an article by slug fragments."""
    # Strip reel- prefix and .mp4
    base = filename.replace('reel-', '', 1).replace('.mp4', '')
    # Remove trailing date pattern (YYYYMMDD or just digits at end)
    base = re.sub(r'-?\d{8,}$', '', base)
    # Get significant words
    words = [w for w in base.split('-') if len(w) > 2]
    
    best_match = None
    best_score = 0
    
    for art in articles:
        slug = art.get('slug', '')
        if not slug:
            continue
        score = sum(1 for w in words if w in slug)
        ratio = score / max(len(words), 1)
        if ratio > best_score and ratio >= 0.4:
            best_score = ratio
            best_match = art
    
    return best_match

# Category-specific hashtag map
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

def extract_topic_hashtags(headline):
    """Extract 3-5 topic-specific hashtags from headline."""
    tags = []
    # Common patterns for person names, places, etc.
    words = headline.split()
    # Build multi-word name candidates
    name_parts = []
    for w in words:
        clean = re.sub(r'[^A-Za-z0-9]', '', w)
        if clean and clean[0].isupper() and len(clean) > 2:
            name_parts.append(clean)
        else:
            if name_parts:
                tags.append('#' + ''.join(name_parts))
                name_parts = []
    if name_parts:
        tags.append('#' + ''.join(name_parts))
    
    # Deduplicate and limit
    seen = set()
    unique = []
    for t in tags:
        tl = t.lower()
        if tl not in seen and len(t) > 3:
            seen.add(tl)
            unique.append(t)
    return unique[:5]

def compose_metadata(article, filename):
    """Compose YouTube title, description, and tags."""
    if article:
        headline = article.get('headline', '')
        subheadline = article.get('subheadline', '') or ''
        slug = article.get('slug', '')
        category = article.get('category', 'news')
        art_tags = article.get('tags', []) or []
    else:
        # Fallback: construct from filename
        base = filename.replace('reel-', '', 1).replace('.mp4', '')
        base = re.sub(r'-?\d{8,}$', '', base)
        headline = ' '.join(w.capitalize() for w in base.split('-'))
        subheadline = ''
        slug = base
        category = 'news'
        art_tags = []
    
    # Title: under 100 chars with #Shorts
    title = headline
    if len(title) + 8 > 100:
        title = title[:91] + '…'
    title = f"{title} #Shorts"
    
    # Hashtags
    base_tags = '#TheVideshi #Shorts #IndianDiaspora #NRI'
    cat_tags = CATEGORY_HASHTAGS.get(category, '#IndiaNews #DesiNews')
    topic_tags = ' '.join(extract_topic_hashtags(headline))
    all_hashtags = f"{base_tags} {cat_tags} {topic_tags}".strip()
    
    # Description
    article_url = f"https://thevideshi.com/articles/{slug}" if slug else "https://thevideshi.com"
    desc = f"""{subheadline}

📰 Full story: {article_url}

The Videshi — News for the global Indian diaspora
🌐 thevideshi.com

Follow us:
📸 Instagram: https://instagram.com/the.videshi
🐦 X/Twitter: https://x.com/thevideshi
🧵 Threads: https://threads.net/@the.videshi

{all_hashtags}"""
    
    # Tags list
    yt_tags = ["The Videshi", "Indian Diaspora", "NRI", "India News", category.replace('-', ' ').title(), "Shorts"]
    # Add topic-specific tags
    for t in extract_topic_hashtags(headline):
        tag_text = t.replace('#', '')
        if tag_text not in yt_tags:
            yt_tags.append(tag_text)
    yt_tags = yt_tags[:12]
    
    return title, desc, yt_tags, slug

# --- YouTube upload ---
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

for reel_path in unuploaded[:2]:
    fname = os.path.basename(reel_path)
    print(f"\n{'='*60}")
    print(f"📹 Processing: {fname}")
    
    # Match article
    article = match_article(fname)
    if article:
        print(f"  📰 Matched article: {article.get('headline', '')[:80]}")
    else:
        print(f"  ⚠️ No article match — using filename-derived title")
    
    title, desc, tags, slug = compose_metadata(article, fname)
    print(f"  📝 Title: {title}")
    
    # Upload
    body = {
        "snippet": {
            "title": title,
            "description": desc,
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
        
        # Log
        yt_log[fname] = {
            "video_id": video_id,
            "article_slug": slug or "unknown",
            "uploaded_at": datetime.utcnow().isoformat() + "Z",
            "url": url
        }
        with open(LOG_PATH, 'w') as f:
            json.dump(yt_log, f, indent=2)
        
        uploaded_count += 1
        results.append((fname, url))
        
        # Wait between uploads
        if uploaded_count < 2 and len(unuploaded) > 1:
            print("  ⏳ Waiting 10 seconds before next upload...")
            time.sleep(10)
            
    except Exception as e:
        print(f"  ❌ Upload failed: {e}")
        errors.append((fname, str(e)))

# --- Summary ---
print(f"\n{'='*60}")
print(f"📊 SUMMARY")
print(f"  Uploaded: {uploaded_count}")
for fname, url in results:
    print(f"    ✅ {fname}")
    print(f"       → {url}")
if errors:
    print(f"  Errors: {len(errors)}")
    for fname, err in errors:
        print(f"    ❌ {fname}: {err}")
print(f"{'='*60}")
