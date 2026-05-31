#!/usr/bin/env python3
"""Upload unuploaded Instagram Reels as YouTube Shorts."""

import json, os, re, time, sys
from datetime import datetime

import requests as req
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# --- Load env files ---
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

yt_env = load_env("~/workspace/.env.youtube")
sb_env = load_env("~/workspace/.env.supabase")

YOUTUBE_CLIENT_ID = yt_env["YOUTUBE_CLIENT_ID"]
YOUTUBE_CLIENT_SECRET = yt_env["YOUTUBE_CLIENT_SECRET"]
YOUTUBE_REFRESH_TOKEN = yt_env["YOUTUBE_REFRESH_TOKEN"]

SUPABASE_URL = sb_env.get("SUPABASE_URL", "https://lboecaekpynbpyijrbfz.supabase.co")
SB_KEY = sb_env.get("SUPABASE_SERVICE_ROLE_KEY") or sb_env.get("SUPABASE_KEY") or sb_env.get("SUPABASE_ANON_KEY")

REELS_DIR = os.path.expanduser("~/workspace/the-videshi-news/pipeline/reels")
LOG_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/youtube-log.json")

# --- Load tracking log ---
if os.path.exists(LOG_PATH):
    with open(LOG_PATH) as f:
        yt_log = json.load(f)
else:
    yt_log = {}

# --- Find unuploaded reels ---
mp4_files = [f for f in os.listdir(REELS_DIR) if f.endswith('.mp4')]
unuploaded = [f for f in mp4_files if f not in yt_log]
# Sort by modification time, newest first
unuploaded.sort(key=lambda f: os.path.getmtime(os.path.join(REELS_DIR, f)), reverse=True)

print(f"Total reels: {len(mp4_files)}, Already uploaded: {len(mp4_files) - len(unuploaded)}, Unuploaded: {len(unuploaded)}")

if not unuploaded:
    print("Nothing to upload. Done.")
    sys.exit(0)

# Limit to 2 per run
to_upload = unuploaded[:2]
print(f"Will upload {len(to_upload)} reel(s) this run.")

# --- Fetch recent articles from Supabase ---
print("\nFetching recent articles from Supabase...")
r = req.get(
    f"{SUPABASE_URL}/rest/v1/p2_articles?status=eq.published&order=published_at.desc&limit=50&select=id,slug,headline,subheadline,category,tags",
    headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"},
    timeout=15
)
articles = r.json() if r.status_code == 200 else []
print(f"  Fetched {len(articles)} recent articles.")

def extract_slug_fragments(filename):
    """Extract slug fragments from reel filename."""
    name = filename.replace('.mp4', '')
    # Strip reel- prefix
    if name.startswith('reel-'):
        name = name[5:]
    # Strip trailing date (YYYYMMDD)
    name = re.sub(r'-\d{8}$', '', name)
    return name.split('-')

def find_matching_article(filename, articles):
    """Find the best matching article for a reel filename."""
    fragments = extract_slug_fragments(filename)
    frag_str = '-'.join(fragments)
    
    best_match = None
    best_score = 0
    
    for art in articles:
        slug = art.get('slug', '')
        if not slug:
            continue
        # Count matching fragments
        score = sum(1 for frag in fragments if frag in slug)
        # Bonus for consecutive match
        if frag_str in slug:
            score += len(fragments)
        if score > best_score and score >= max(3, len(fragments) * 0.4):
            best_score = score
            best_match = art
    
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

def generate_hashtags(category, headline):
    """Generate hashtags for YouTube description."""
    base = '#TheVideshi #Shorts #IndianDiaspora #NRI'
    cat_tags = CATEGORY_HASHTAGS.get(category, '#IndiaNews #DesiNews')
    
    # Extract topic-specific hashtags from headline
    topic_tags = []
    # Common patterns: proper nouns, acronyms
    words = re.findall(r'[A-Z][a-z]+(?:\s[A-Z][a-z]+)*|[A-Z]{2,}', headline or '')
    for w in words[:5]:
        tag = '#' + w.replace(' ', '').replace('-', '')
        if len(tag) > 3 and tag not in base and tag not in cat_tags:
            topic_tags.append(tag)
    
    all_tags = f"{base} {cat_tags}"
    if topic_tags:
        all_tags += ' ' + ' '.join(topic_tags[:5])
    return all_tags

def compose_metadata(article, filename):
    """Compose YouTube title, description, and tags."""
    if article:
        headline = article.get('headline', '')
        subheadline = article.get('subheadline', '')
        slug = article.get('slug', '')
        category = article.get('category', 'news')
        art_tags = article.get('tags', []) or []
    else:
        # Construct from filename
        fragments = extract_slug_fragments(filename)
        headline = ' '.join(w.capitalize() for w in fragments)
        subheadline = ''
        slug = '-'.join(fragments)
        category = 'news'
        art_tags = []
    
    # Title: under 100 chars with #Shorts
    title = headline
    if len(title) + 8 > 100:
        title = title[:91] + '…'
    title = f"{title} #Shorts"
    
    # Hashtags
    hashtags = generate_hashtags(category, headline)
    
    # Description
    desc_parts = []
    if subheadline:
        desc_parts.append(subheadline)
    desc_parts.append('')
    desc_parts.append(f'📰 Full story: https://thevideshi.com/articles/{slug}')
    desc_parts.append('')
    desc_parts.append('The Videshi — News for the global Indian diaspora')
    desc_parts.append('🌐 thevideshi.com')
    desc_parts.append('')
    desc_parts.append('Follow us:')
    desc_parts.append('📸 Instagram: https://instagram.com/the.videshi')
    desc_parts.append('🐦 X/Twitter: https://x.com/thevideshi')
    desc_parts.append('🧵 Threads: https://threads.net/@the.videshi')
    desc_parts.append('')
    desc_parts.append(hashtags)
    description = '\n'.join(desc_parts)
    
    # Tags
    tags = ["The Videshi", "Indian Diaspora", "NRI", "India News", category.replace('-', ' ').title(), "Shorts"]
    # Add topic words from headline
    for w in re.findall(r'[A-Z][a-z]+(?:\s[A-Z][a-z]+)*', headline or ''):
        if w not in tags and len(tags) < 12:
            tags.append(w)
    # Add article tags
    if isinstance(art_tags, list):
        for t in art_tags[:3]:
            if t not in tags and len(tags) < 12:
                tags.append(t)
    
    return title, description, tags, slug

# --- YouTube auth ---
print("\nAuthenticating with YouTube...")
creds = Credentials(
    token=None,
    refresh_token=YOUTUBE_REFRESH_TOKEN,
    token_uri="https://oauth2.googleapis.com/token",
    client_id=YOUTUBE_CLIENT_ID,
    client_secret=YOUTUBE_CLIENT_SECRET
)
youtube = build("youtube", "v3", credentials=creds)
print("  ✅ Authenticated.")

# --- Upload loop ---
uploaded_count = 0
errors = []

for i, reel_filename in enumerate(to_upload):
    reel_path = os.path.join(REELS_DIR, reel_filename)
    file_size_mb = os.path.getsize(reel_path) / (1024 * 1024)
    print(f"\n--- Reel {i+1}/{len(to_upload)}: {reel_filename} ({file_size_mb:.1f} MB) ---")
    
    # Find matching article
    article = find_matching_article(reel_filename, articles)
    if article:
        print(f"  📰 Matched article: {article['headline'][:80]}")
    else:
        print(f"  ⚠️  No article match found, using filename-derived title.")
    
    # Compose metadata
    title, description, tags, slug = compose_metadata(article, reel_filename)
    print(f"  📝 Title: {title}")
    print(f"  🏷️  Tags: {', '.join(tags[:5])}...")
    
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
        url = f"https://youtube.com/shorts/{video_id}"
        print(f"  ✅ Uploaded: {url}")
        
        # Log
        yt_log[reel_filename] = {
            "video_id": video_id,
            "article_slug": slug or "unknown",
            "uploaded_at": datetime.utcnow().isoformat() + "Z",
            "url": url
        }
        with open(LOG_PATH, 'w') as f:
            json.dump(yt_log, f, indent=2)
        
        uploaded_count += 1
        
        # Wait between uploads
        if i < len(to_upload) - 1:
            print("  ⏳ Waiting 10 seconds...")
            time.sleep(10)
    
    except Exception as e:
        err_msg = f"Failed to upload {reel_filename}: {e}"
        print(f"  ❌ {err_msg}")
        errors.append(err_msg)

# --- Summary ---
print(f"\n{'='*60}")
print(f"SUMMARY: {uploaded_count}/{len(to_upload)} uploaded successfully.")
if errors:
    print(f"ERRORS ({len(errors)}):")
    for e in errors:
        print(f"  - {e}")
print(f"{'='*60}")
