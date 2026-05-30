#!/usr/bin/env python3
"""Upload unuploaded reels to YouTube Shorts for The Videshi."""

import json, os, time, re, requests, httplib2
from datetime import datetime, timezone
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google_auth_httplib2 import AuthorizedHttp
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Load env
load_dotenv(os.path.expanduser("~/workspace/.env.youtube"))
load_dotenv(os.path.expanduser("~/workspace/.env.supabase"))

YOUTUBE_CLIENT_ID = os.environ["YOUTUBE_CLIENT_ID"]
YOUTUBE_CLIENT_SECRET = os.environ["YOUTUBE_CLIENT_SECRET"]
YOUTUBE_REFRESH_TOKEN = os.environ["YOUTUBE_REFRESH_TOKEN"]
SUPABASE_URL = "https://lboecaekpynbpyijrbfz.supabase.co"
SB_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SB_KEY", "")

REELS_DIR = os.path.expanduser("~/workspace/the-videshi-news/pipeline/reels")
LOG_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/youtube-log.json")
MAX_UPLOADS = 2

# Category hashtag map
CATEGORY_HASHTAGS = {
    "news": "#IndiaNews #BreakingNews #DesiNews #SouthAsian",
    "immigration": "#H1B #H1BVisa #GreenCard #USImmigration #USCIS",
    "nri-world": "#NRILife #DesiAbroad #IndianAmerican",
    "travel": "#TravelIndia #IncredibleIndia #IndiaTravel",
    "lifestyle-health": "#DesiLifestyle #Wellness #Health",
    "markets-finance": "#StockMarket #Nifty #Sensex #IndianMarkets",
    "technology": "#TechNews #IndianTech #SiliconValley #AI",
    "sports": "#Cricket #IPL #IPL2026 #TeamIndia #BCCI",
    "entertainment": "#Bollywood #BollywoodNews #IndianCinema #Tollywood",
    "food": "#IndianFood #IndianCuisine #DesiFood",
}

def load_log():
    if os.path.exists(LOG_PATH):
        return json.load(open(LOG_PATH))
    return {}

def save_log(log):
    with open(LOG_PATH, 'w') as f:
        json.dump(log, f, indent=2)

def get_unuploaded_reels(log):
    mp4s = [f for f in os.listdir(REELS_DIR) if f.endswith('.mp4')]
    unuploaded = [f for f in mp4s if f not in log]
    # Sort by mtime, newest first
    unuploaded.sort(key=lambda f: os.path.getmtime(os.path.join(REELS_DIR, f)), reverse=True)
    return unuploaded[:MAX_UPLOADS]

def extract_slug_fragments(filename):
    """Extract slug fragments from reel filename."""
    name = filename.replace('.mp4', '')
    # Strip reel- prefix
    if name.startswith('reel-'):
        name = name[5:]
    # Strip trailing date (YYYYMMDD)
    name = re.sub(r'-\d{8}$', '', name)
    return name.split('-')

def find_matching_article(fragments):
    """Query Supabase for matching article."""
    try:
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/p2_articles?status=eq.published&order=published_at.desc&limit=30&select=id,slug,headline,subheadline,category,tags",
            headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"},
            timeout=15
        )
        articles = r.json()
        if not isinstance(articles, list):
            print(f"  ⚠️ Supabase returned non-list: {articles}")
            return None

        frag_str = '-'.join(fragments)
        for art in articles:
            slug = art.get('slug', '') or ''
            # Check if slug contains enough fragments
            match_count = sum(1 for f in fragments if f in slug)
            if match_count >= len(fragments) * 0.5:
                return art
        return None
    except Exception as e:
        print(f"  ⚠️ Supabase error: {e}")
        return None

def generate_hashtags(category, headline):
    """Generate hashtags based on category and headline."""
    base = "#TheVideshi #Shorts #IndianDiaspora #NRI"
    cat_tags = CATEGORY_HASHTAGS.get(category, "#IndiaNews #DesiNews")
    
    # Extract topic-specific hashtags from headline
    topic_tags = []
    # Find capitalized proper nouns / key terms
    words = re.findall(r'[A-Z][a-z]+(?:\s[A-Z][a-z]+)*', headline or '')
    for w in words[:5]:
        tag = '#' + w.replace(' ', '')
        if tag not in base and tag not in cat_tags and len(tag) > 3:
            topic_tags.append(tag)
    
    # Common known hashtags from content
    headline_lower = (headline or '').lower()
    if 'h1b' in headline_lower or 'h-1b' in headline_lower:
        topic_tags.append('#H1B')
    if 'modi' in headline_lower:
        topic_tags.append('#NarendraModi')
    if 'trump' in headline_lower:
        topic_tags.append('#Trump')
    if 'layoff' in headline_lower:
        topic_tags.append('#TechLayoffs')
    if 'uscis' in headline_lower:
        topic_tags.append('#USCIS')
    
    all_tags = f"{base} {cat_tags} {' '.join(topic_tags[:5])}"
    return all_tags

def compose_metadata(article, filename):
    """Compose YouTube title, description, tags."""
    if article:
        headline = article.get('headline', '')
        subheadline = article.get('subheadline', '') or ''
        slug = article.get('slug', '')
        category = article.get('category', 'news')
        tags_list = article.get('tags', []) or []
    else:
        # Construct from filename
        fragments = extract_slug_fragments(filename)
        headline = ' '.join(w.capitalize() for w in fragments)
        subheadline = ''
        slug = '-'.join(fragments)
        category = 'news'
        tags_list = []

    # Title: under 100 chars + #Shorts
    title = headline[:93] + " #Shorts" if len(headline) > 93 else headline + " #Shorts"
    
    # Hashtags
    hashtags = generate_hashtags(category, headline)
    
    # Description
    description = f"""{subheadline}

📰 Full story: https://thevideshi.com/articles/{slug}

The Videshi — News for the global Indian diaspora
🌐 thevideshi.com

Follow us:
📸 Instagram: https://instagram.com/the.videshi
🐦 X/Twitter: https://x.com/thevideshi
🧵 Threads: https://threads.net/@the.videshi

{hashtags}"""

    # Tags
    yt_tags = ["The Videshi", "Indian Diaspora", "NRI", "India News", category.replace('-', ' ').title(), "Shorts"]
    for t in tags_list[:4]:
        if isinstance(t, str) and t not in yt_tags:
            yt_tags.append(t)
    # Add topic from headline
    for word in headline.split()[:3]:
        clean = word.strip(',:;!?.')
        if len(clean) > 3 and clean not in yt_tags:
            yt_tags.append(clean)
    yt_tags = yt_tags[:12]

    return title, description, yt_tags, slug

def upload_to_youtube(reel_path, title, description, tags):
    """Upload video to YouTube."""
    creds = Credentials(
        token=None,
        refresh_token=YOUTUBE_REFRESH_TOKEN,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=YOUTUBE_CLIENT_ID,
        client_secret=YOUTUBE_CLIENT_SECRET
    )

    http = httplib2.Http(timeout=300)
    authed_http = AuthorizedHttp(creds, http=http)
    youtube = build("youtube", "v3", http=authed_http)

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

    media = MediaFileUpload(reel_path, mimetype="video/mp4", resumable=True, chunksize=5*1024*1024)

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )

    response = None
    while response is None:
        status, response = request.next_chunk(num_retries=5)
        if status:
            print(f"  Upload progress: {int(status.progress() * 100)}%")

    return response["id"]

def main():
    yt_log = load_log()
    unuploaded = get_unuploaded_reels(yt_log)
    
    if not unuploaded:
        print("✅ No unuploaded reels found. All caught up!")
        return
    
    print(f"📹 Found {len(unuploaded)} unuploaded reel(s)")
    uploaded_count = 0
    errors = []
    urls = []

    for i, filename in enumerate(unuploaded):
        print(f"\n--- Reel {i+1}/{len(unuploaded)}: {filename} ---")
        reel_path = os.path.join(REELS_DIR, filename)
        
        # Extract and match
        fragments = extract_slug_fragments(filename)
        print(f"  Slug fragments: {fragments[:5]}...")
        article = find_matching_article(fragments)
        
        if article:
            print(f"  ✅ Matched article: {article.get('headline', '')[:60]}...")
        else:
            print(f"  ⚠️ No article match, using filename")
        
        title, description, tags, slug = compose_metadata(article, filename)
        print(f"  Title: {title}")
        
        try:
            video_id = upload_to_youtube(reel_path, title, description, tags)
            url = f"https://youtube.com/shorts/{video_id}"
            print(f"  ✅ Uploaded: {url}")
            
            # Log
            yt_log[filename] = {
                "video_id": video_id,
                "article_slug": slug or "unknown",
                "uploaded_at": datetime.now(timezone.utc).isoformat(),
                "url": url
            }
            save_log(yt_log)
            uploaded_count += 1
            urls.append(url)
            
            # Wait between uploads
            if i < len(unuploaded) - 1:
                print("  ⏳ Waiting 10s...")
                time.sleep(10)
        except Exception as e:
            print(f"  ❌ Upload failed: {e}")
            errors.append((filename, str(e)))

    print(f"\n{'='*50}")
    print(f"📊 Summary: {uploaded_count}/{len(unuploaded)} uploaded")
    for url in urls:
        print(f"  🔗 {url}")
    if errors:
        print(f"  ❌ Errors:")
        for fn, err in errors:
            print(f"    - {fn}: {err}")

if __name__ == "__main__":
    main()
