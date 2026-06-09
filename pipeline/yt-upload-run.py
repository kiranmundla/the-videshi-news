#!/usr/bin/env python3
"""Upload unuploaded reels to YouTube Shorts."""

import json, os, time, re, sys
from datetime import datetime

# Load env files
def load_env(path):
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

yt_env = load_env('~/workspace/.env.youtube')
sb_env = load_env('~/workspace/.env.supabase')

YOUTUBE_CLIENT_ID = yt_env['YOUTUBE_CLIENT_ID']
YOUTUBE_CLIENT_SECRET = yt_env['YOUTUBE_CLIENT_SECRET']
YOUTUBE_REFRESH_TOKEN = yt_env['YOUTUBE_REFRESH_TOKEN']
SUPABASE_URL = sb_env.get('SUPABASE_URL', 'https://lboecaekpynbpyijrbfz.supabase.co')
SB_KEY = sb_env.get('SUPABASE_SERVICE_ROLE_KEY') or sb_env.get('SUPABASE_ANON_KEY') or sb_env.get('SUPABASE_KEY', '')

import requests as req
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Load tracking log
log_path = os.path.expanduser('~/workspace/the-videshi-news/pipeline/youtube-log.json')
yt_log = json.load(open(log_path)) if os.path.exists(log_path) else {}

# Find unuploaded reels
import glob
reel_dir = os.path.expanduser('~/workspace/the-videshi-news/pipeline/reels/')
all_reels = glob.glob(os.path.join(reel_dir, '*.mp4'))
unuploaded = []
for rp in all_reels:
    fn = os.path.basename(rp)
    if fn not in yt_log:
        unuploaded.append((rp, fn, os.path.getmtime(rp)))

unuploaded.sort(key=lambda x: x[2], reverse=True)

if not unuploaded:
    print("No unuploaded reels found.")
    sys.exit(0)

print(f"Found {len(unuploaded)} unuploaded reel(s). Processing up to 2...")

# Fetch recent articles from Supabase
r = req.get(
    f"{SUPABASE_URL}/rest/v1/p2_articles?status=eq.published&order=published_at.desc&limit=50&select=id,slug,headline,subheadline,category,tags",
    headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"},
    timeout=15
)
articles = r.json() if r.status_code == 200 else []
print(f"Fetched {len(articles)} recent articles for matching.")

# Category hashtag map
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

def extract_slug_words(filename):
    """Extract matching words from reel filename."""
    name = filename.replace('.mp4', '')
    name = re.sub(r'^reel-', '', name)
    # Remove trailing date pattern like -20260608
    name = re.sub(r'-\d{8}$', '', name)
    return name.split('-')

def match_article(filename, articles):
    """Find best matching article for a reel filename."""
    words = extract_slug_words(filename)
    if len(words) < 3:
        return None
    
    best_match = None
    best_score = 0
    
    for art in articles:
        slug = art.get('slug', '')
        # Count how many words from the filename appear in the article slug
        score = sum(1 for w in words if w in slug and len(w) > 2)
        if score > best_score and score >= min(3, len(words) * 0.4):
            best_score = score
            best_match = art
    
    return best_match

def make_title_from_filename(filename):
    """Construct a title from filename words."""
    words = extract_slug_words(filename)
    return ' '.join(w.capitalize() for w in words if len(w) > 1)

def extract_topic_hashtags(headline):
    """Extract topic-specific hashtags from headline."""
    tags = []
    # Person names and entities
    patterns = [
        (r'\b(Modi|Narendra Modi)\b', '#NarendraModi'),
        (r'\b(Trump)\b', '#Trump'),
        (r'\b(Kohli|Virat)\b', '#ViratKohli'),
        (r'\b(Dhoni)\b', '#MSDhoni'),
        (r'\b(Bumrah)\b', '#JaspritBumrah'),
        (r'\b(IPL)\b', '#IPL2026'),
        (r'\bH[- ]?1B\b', '#H1B'),
        (r'\b(USCIS)\b', '#USCIS'),
        (r'\b(Sensex)\b', '#Sensex'),
        (r'\b(Nifty)\b', '#Nifty'),
        (r'\b(RBI)\b', '#RBI'),
        (r'\b(Bollywood)\b', '#Bollywood'),
        (r'\b(Mumbai)\b', '#Mumbai'),
        (r'\b(Delhi)\b', '#Delhi'),
        (r'\b(Infosys)\b', '#Infosys'),
        (r'\b(TCS)\b', '#TCS'),
        (r'\b(Wipro)\b', '#Wipro'),
        (r'\b(Tata)\b', '#Tata'),
        (r'\b(Adani)\b', '#Adani'),
        (r'\b(Ambani)\b', '#Ambani'),
        (r'\b(tariff|trade)\b', '#Trade'),
        (r'\b(USTR|Section 301)\b', '#USTR'),
    ]
    for pat, tag in patterns:
        if re.search(pat, headline, re.IGNORECASE):
            tags.append(tag)
    return tags[:5]

# Build YouTube client
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

for reel_path, reel_filename, mtime in unuploaded[:2]:
    print(f"\n{'='*60}")
    print(f"Processing: {reel_filename}")
    
    # Match article
    article = match_article(reel_filename, articles)
    
    if article:
        headline = article['headline']
        subheadline = article.get('subheadline', '')
        slug = article['slug']
        category = article.get('category', 'news')
        print(f"  Matched article: {headline}")
        print(f"  Slug: {slug}")
    else:
        headline = make_title_from_filename(reel_filename)
        subheadline = ''
        slug = 'unknown'
        category = 'news'
        print(f"  No article match, using filename title: {headline}")
    
    # Build title (under 100 chars + #Shorts)
    title = headline[:93] + ' #Shorts' if len(headline) > 93 else headline + ' #Shorts'
    
    # Build hashtags
    base_hashtags = '#TheVideshi #Shorts #IndianDiaspora #NRI'
    cat_hashtags = CATEGORY_HASHTAGS.get(category, '#IndiaNews #DesiNews')
    topic_hashtags = ' '.join(extract_topic_hashtags(headline))
    all_hashtags = f"{base_hashtags} {cat_hashtags} {topic_hashtags}".strip()
    
    # Build description
    article_link = f"https://thevideshi.com/articles/{slug}" if slug != 'unknown' else "https://thevideshi.com"
    description = f"""{subheadline}

📰 Full story: {article_link}

The Videshi — News for the global Indian diaspora
🌐 thevideshi.com

Follow us:
📸 Instagram: https://instagram.com/the.videshi
🐦 X/Twitter: https://x.com/thevideshi
🧵 Threads: https://threads.net/@the.videshi

{all_hashtags}""".strip()
    
    # Build tags
    tags = ["The Videshi", "Indian Diaspora", "NRI", "India News", category.replace('-', ' ').title(), "Shorts"]
    # Add topic tags from headline
    for ht in extract_topic_hashtags(headline):
        clean = ht.replace('#', '')
        if clean not in tags:
            tags.append(clean)
    tags = tags[:12]
    
    print(f"  Title: {title}")
    print(f"  Tags: {tags}")
    
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
        yt_url = f"https://youtube.com/shorts/{video_id}"
        print(f"  ✅ Uploaded: {yt_url}")
        
        # Log
        yt_log[reel_filename] = {
            "video_id": video_id,
            "article_slug": slug,
            "uploaded_at": datetime.utcnow().isoformat() + "Z",
            "url": yt_url
        }
        with open(log_path, 'w') as f:
            json.dump(yt_log, f, indent=2)
        
        uploaded_count += 1
        
        # Wait between uploads
        if uploaded_count < 2 and len(unuploaded) > 1:
            print("  Waiting 10 seconds...")
            time.sleep(10)
            
    except Exception as e:
        error_msg = f"Error uploading {reel_filename}: {str(e)}"
        print(f"  ❌ {error_msg}")
        errors.append(error_msg)

print(f"\n{'='*60}")
print(f"SUMMARY:")
print(f"  Uploaded: {uploaded_count}")
print(f"  Errors: {len(errors)}")
for e in errors:
    print(f"    - {e}")
