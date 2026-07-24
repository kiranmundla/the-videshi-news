#!/usr/bin/env python3
"""Upload unuploaded reels to YouTube Shorts for The Videshi."""

import json, os, sys, time, glob, re
from datetime import datetime

import requests as req
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# --- Load credentials ---
def load_env(path):
    env = {}
    if os.path.exists(path):
        for line in open(path):
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env

yt_env = load_env(os.path.expanduser('~/workspace/.env.youtube'))
sb_env = load_env(os.path.expanduser('~/workspace/.env.supabase'))

YOUTUBE_CLIENT_ID = yt_env.get('YOUTUBE_CLIENT_ID')
YOUTUBE_CLIENT_SECRET = yt_env.get('YOUTUBE_CLIENT_SECRET')
YOUTUBE_REFRESH_TOKEN = yt_env.get('YOUTUBE_REFRESH_TOKEN')

SUPABASE_URL = sb_env.get('SUPABASE_URL', 'https://lboecaekpynbpyijrbfz.supabase.co')
SB_KEY = sb_env.get('SUPABASE_SERVICE_ROLE_KEY') or sb_env.get('SUPABASE_ANON_KEY') or sb_env.get('SUPABASE_KEY')

REELS_DIR = os.path.expanduser('~/workspace/the-videshi-news/pipeline/reels')
LOG_PATH = os.path.expanduser('~/workspace/the-videshi-news/pipeline/youtube-log.json')
MAX_UPLOADS = 2

# --- Category hashtag map ---
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

def extract_slug_fragments(filename):
    """Extract slug fragments from reel filename."""
    name = filename
    # Strip prefix
    if name.startswith('ss-reel-'):
        name = name[len('ss-reel-'):]
    elif name.startswith('reel-'):
        name = name[len('reel-'):]
    # Strip .mp4
    name = name.replace('.mp4', '')
    # Strip trailing date patterns (e.g. -20260609, -20260609-1503)
    name = re.sub(r'-\d{8}(-\d{4})?$', '', name)
    return name.split('-')

def find_matching_article(fragments, articles):
    """Find best matching article from Supabase results."""
    best_match = None
    best_score = 0
    frag_set = set(f.lower() for f in fragments if len(f) > 2)
    
    for art in articles:
        slug = (art.get('slug') or '').lower()
        slug_words = set(slug.replace('-', ' ').split())
        overlap = len(frag_set & slug_words)
        if overlap > best_score:
            best_score = overlap
            best_match = art
    
    # Require at least 3 matching words
    if best_score >= 3:
        return best_match
    return None

def make_title_from_filename(fragments):
    """Construct title from filename fragments."""
    words = [f.capitalize() for f in fragments if len(f) > 1]
    title = ' '.join(words[:12])
    if len(title) > 90:
        title = title[:90].rsplit(' ', 1)[0]
    return title

def extract_topic_hashtags(headline):
    """Extract topic-specific hashtags from headline."""
    tags = []
    # Common person names and topics
    patterns = {
        r'modi': '#NarendraModi', r'kohli': '#ViratKohli', r'trump': '#Trump',
        r'h1b': '#H1BVisa', r'green.?card': '#GreenCard', r'uscis': '#USCIS',
        r'ipl': '#IPL2026', r'mumbai': '#Mumbai', r'delhi': '#Delhi',
        r'bollywood': '#Bollywood', r'infosys': '#Infosys', r'tata': '#Tata',
        r'akshay.?kumar': '#AkshayKumar', r'samuk': '#Samuk',
        r'alien': '#AlienMovie', r'suriya': '#Suriya',
        r'jaishankar': '#Jaishankar', r'rbi': '#RBI',
        r'sensex': '#Sensex', r'nifty': '#Nifty',
        r'cricket': '#Cricket', r'bcci': '#BCCI',
    }
    hl = headline.lower()
    for pat, tag in patterns.items():
        if re.search(pat, hl):
            tags.append(tag)
    return tags[:5]

def main():
    # Load tracking log
    yt_log = json.load(open(LOG_PATH)) if os.path.exists(LOG_PATH) else {}

    # Find unuploaded reels
    mp4s = sorted(glob.glob(os.path.join(REELS_DIR, '*.mp4')),
                  key=lambda f: os.path.getmtime(f), reverse=True)
    reel_files = [f for f in mp4s
                  if (os.path.basename(f).startswith('reel-') or os.path.basename(f).startswith('ss-reel-'))
                  and os.path.basename(f) != 'end-card.mp4']
    
    unuploaded = [f for f in reel_files if os.path.basename(f) not in yt_log]

    if not unuploaded:
        print("No unuploaded reels found. Nothing to do.")
        return

    print(f"Found {len(unuploaded)} unuploaded reel(s). Will upload up to {MAX_UPLOADS}.")

    # Fetch recent articles from Supabase
    articles = []
    try:
        r = req.get(
            f"{SUPABASE_URL}/rest/v1/p2_articles?status=eq.published&order=published_at.desc&limit=50&select=id,slug,headline,subheadline,category,tags",
            headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"},
            timeout=15
        )
        articles = r.json() if r.status_code == 200 else []
        print(f"Fetched {len(articles)} recent articles from Supabase")
    except Exception as e:
        print(f"Warning: Could not fetch articles: {e}")

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

    for reel_path in unuploaded[:MAX_UPLOADS]:
        reel_filename = os.path.basename(reel_path)
        print(f"\n--- Processing: {reel_filename} ---")

        # Extract slug fragments and match article
        fragments = extract_slug_fragments(reel_filename)
        article = find_matching_article(fragments, articles)

        if article:
            headline = article.get('headline', '')
            subheadline = article.get('subheadline', '') or ''
            slug = article.get('slug', '')
            category = article.get('category', 'news')
            print(f"  Matched article: {headline[:60]}...")
        else:
            headline = make_title_from_filename(fragments)
            subheadline = ''
            slug = ''
            category = 'entertainment'  # default
            print(f"  No article match. Using filename title: {headline}")

        # Compose title
        title = headline[:90]
        if len(title) + 8 <= 100:
            title += ' #Shorts'

        # Compose hashtags
        base_tags = '#TheVideshi #Shorts #IndianDiaspora #NRI'
        cat_tags = CATEGORY_HASHTAGS.get(category, '#IndiaNews #DesiNews')
        topic_tags = ' '.join(extract_topic_hashtags(headline))
        all_hashtags = f"{base_tags} {cat_tags}"
        if topic_tags:
            all_hashtags += f" {topic_tags}"

        # Compose description
        article_link = f"\n📰 Full story: https://thevideshi.com/articles/{slug}" if slug else ""
        description = f"""{subheadline}{article_link}

The Videshi — News for the global Indian diaspora
🌐 thevideshi.com

Follow us:
📸 Instagram: https://instagram.com/the.videshi
🐦 X/Twitter: https://x.com/thevideshi
🧵 Threads: https://threads.net/@the.videshi

{all_hashtags}"""

        # Tags list
        tags_list = ["The Videshi", "Indian Diaspora", "NRI", "India News", category.replace('-', ' ').title(), "Shorts"]
        # Add topic-specific tags from headline
        for word in fragments[:4]:
            if len(word) > 3:
                tags_list.append(word.capitalize())
        tags_list = tags_list[:12]

        # Upload
        try:
            body = {
                "snippet": {
                    "title": title,
                    "description": description,
                    "tags": tags_list,
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
            print(f"  ✅ Uploaded: https://youtube.com/shorts/{video_id}")

            # Log
            yt_log[reel_filename] = {
                "video_id": video_id,
                "article_slug": slug or "unknown",
                "uploaded_at": datetime.utcnow().isoformat() + "Z",
                "url": f"https://youtube.com/shorts/{video_id}"
            }
            with open(LOG_PATH, 'w') as f:
                json.dump(yt_log, f, indent=2)

            uploaded_count += 1

            # Wait between uploads
            if uploaded_count < MAX_UPLOADS and uploaded_count < len(unuploaded):
                print("  Waiting 10 seconds before next upload...")
                time.sleep(10)

        except Exception as e:
            error_msg = f"Error uploading {reel_filename}: {e}"
            print(f"  ❌ {error_msg}")
            errors.append(error_msg)

    # Summary
    print(f"\n=== SUMMARY ===")
    print(f"Uploaded: {uploaded_count}/{min(len(unuploaded), MAX_UPLOADS)}")
    if errors:
        print(f"Errors: {len(errors)}")
        for e in errors:
            print(f"  - {e}")

if __name__ == '__main__':
    main()
