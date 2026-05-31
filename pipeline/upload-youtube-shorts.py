#!/usr/bin/env python3
"""Upload unuploaded Instagram Reels as YouTube Shorts for The Videshi."""

import json
import os
import re
import time
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
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip()
    return env

yt_env = load_env("~/workspace/.env.youtube")
sb_env = load_env("~/workspace/.env.supabase")

YOUTUBE_CLIENT_ID = yt_env["YOUTUBE_CLIENT_ID"]
YOUTUBE_CLIENT_SECRET = yt_env["YOUTUBE_CLIENT_SECRET"]
YOUTUBE_REFRESH_TOKEN = yt_env["YOUTUBE_REFRESH_TOKEN"]

SUPABASE_URL = "https://lboecaekpynbpyijrbfz.supabase.co"
SB_KEY = sb_env.get("SUPABASE_SERVICE_KEY") or sb_env.get("SUPABASE_ANON_KEY") or sb_env.get("SB_KEY")

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
mp4_files_with_mtime = []
for f in mp4_files:
    if f not in yt_log:
        fpath = os.path.join(REELS_DIR, f)
        mp4_files_with_mtime.append((f, os.path.getmtime(fpath)))

# Sort by mtime, newest first
mp4_files_with_mtime.sort(key=lambda x: x[1], reverse=True)
unuploaded = [x[0] for x in mp4_files_with_mtime]

print(f"Found {len(unuploaded)} unuploaded reel(s)")
if not unuploaded:
    print("Nothing to upload.")
    exit(0)

# Limit to 2 per run
to_upload = unuploaded[:2]
print(f"Will upload: {to_upload}")

# --- Fetch recent articles from Supabase ---
print("\nFetching recent articles from Supabase...")
r = req.get(
    f"{SUPABASE_URL}/rest/v1/p2_articles?status=eq.published&order=published_at.desc&limit=50&select=id,slug,headline,subheadline,category,tags",
    headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"},
    timeout=15
)
articles = r.json()
print(f"Fetched {len(articles)} articles")

def extract_slug_words(filename):
    """Extract slug words from reel filename."""
    name = filename.replace('.mp4', '')
    # Strip reel- prefix
    if name.startswith('reel-'):
        name = name[5:]
    # Strip trailing date pattern like -20260531 or -2
    name = re.sub(r'-\d{8}$', '', name)
    name = re.sub(r'-\d$', '', name)
    return name.split('-')

def match_article(filename, articles):
    """Find the best matching article for a reel filename."""
    words = extract_slug_words(filename)
    slug_fragment = '-'.join(words)
    
    best_match = None
    best_score = 0
    
    for art in articles:
        slug = art.get('slug', '') or ''
        # Count how many words from the filename appear in the article slug
        score = sum(1 for w in words if w in slug)
        # Bonus for consecutive matches
        if slug_fragment[:20] in slug:
            score += 5
        if score > best_score and score >= 3:
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

def generate_topic_hashtags(headline):
    """Extract person/topic hashtags from headline."""
    tags = []
    # Common patterns
    words = headline.split()
    # Look for capitalized proper nouns (2+ consecutive)
    i = 0
    while i < len(words):
        if words[i][0:1].isupper() and len(words[i]) > 2:
            name_parts = [words[i].strip(',:;.!?')]
            j = i + 1
            while j < len(words) and words[j][0:1].isupper() and len(words[j]) > 2:
                name_parts.append(words[j].strip(',:;.!?'))
                j += 1
            if len(name_parts) >= 1:
                tag = '#' + ''.join(name_parts)
                if len(tag) > 3 and tag not in tags:
                    tags.append(tag)
            i = j
        else:
            i += 1
    return tags[:5]

def compose_metadata(filename, article):
    """Compose YouTube metadata for upload."""
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
    
    # Title: headline + #Shorts, under 100 chars
    title = headline
    suffix = ' #Shorts'
    if len(title) + len(suffix) > 100:
        title = title[:100 - len(suffix)]
    title += suffix
    
    # Hashtags
    base_hashtags = '#TheVideshi #Shorts #IndianDiaspora #NRI'
    cat_hashtags = CATEGORY_HASHTAGS.get(category, '#IndiaNews #DesiNews')
    topic_hashtags = ' '.join(generate_topic_hashtags(headline))
    all_hashtags = f"{base_hashtags} {cat_hashtags} {topic_hashtags}".strip()
    
    # Description
    article_url = f"https://thevideshi.com/articles/{slug}" if slug else "https://thevideshi.com"
    description = f"""{subheadline}

📰 Full story: {article_url}

The Videshi — News for the global Indian diaspora
🌐 thevideshi.com

Follow us:
📸 Instagram: https://instagram.com/the.videshi
🐦 X/Twitter: https://x.com/thevideshi
🧵 Threads: https://threads.net/@the.videshi

{all_hashtags}""".strip()
    
    # Tags
    tags = ["The Videshi", "Indian Diaspora", "NRI", "India News", category.replace('-', ' ').title(), "Shorts"]
    # Add topic tags from article tags
    if art_tags:
        for t in art_tags[:4]:
            if t not in tags:
                tags.append(t)
    # Add from headline
    for ht in generate_topic_hashtags(headline)[:2]:
        clean = ht.replace('#', '')
        if clean not in tags:
            tags.append(clean)
    tags = tags[:12]
    
    return title, description, tags, slug, category

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
print("Authenticated ✓")

# --- Upload loop ---
uploaded_count = 0
errors = []
results = []

for i, reel_filename in enumerate(to_upload):
    reel_path = os.path.join(REELS_DIR, reel_filename)
    print(f"\n{'='*60}")
    print(f"[{i+1}/{len(to_upload)}] Processing: {reel_filename}")
    
    # Match article
    article = match_article(reel_filename, articles)
    if article:
        print(f"  Matched article: {article.get('headline', '')[:80]}")
    else:
        print(f"  No article match found, using filename")
    
    title, description, tags, slug, category = compose_metadata(reel_filename, article)
    print(f"  Title: {title}")
    print(f"  Category: {category}")
    
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
        results.append((reel_filename, url))
        
        # Wait between uploads
        if i < len(to_upload) - 1:
            print("  Waiting 10 seconds...")
            time.sleep(10)
    
    except Exception as e:
        print(f"  ❌ Error: {e}")
        errors.append((reel_filename, str(e)))

# --- Summary ---
print(f"\n{'='*60}")
print(f"SUMMARY")
print(f"  Uploaded: {uploaded_count}/{len(to_upload)}")
for fn, url in results:
    print(f"  ✅ {fn} → {url}")
for fn, err in errors:
    print(f"  ❌ {fn}: {err}")
