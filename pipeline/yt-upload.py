#!/usr/bin/env python3
"""Upload unuploaded reels to YouTube Shorts for The Videshi."""

import json, os, re, time, glob
from datetime import datetime

import requests as req
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

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

yt_env = load_env("~/workspace/.env.youtube")
sb_env = load_env("~/workspace/.env.supabase")

YOUTUBE_CLIENT_ID = yt_env["YOUTUBE_CLIENT_ID"]
YOUTUBE_CLIENT_SECRET = yt_env["YOUTUBE_CLIENT_SECRET"]
YOUTUBE_REFRESH_TOKEN = yt_env["YOUTUBE_REFRESH_TOKEN"]
SUPABASE_URL = sb_env.get("SUPABASE_URL", "https://lboecaekpynbpyijrbfz.supabase.co")
SB_KEY = sb_env.get("SUPABASE_SERVICE_KEY") or sb_env.get("SUPABASE_KEY") or sb_env.get("SUPABASE_ANON_KEY")

REELS_DIR = os.path.expanduser("~/workspace/the-videshi-news/pipeline/reels")
LOG_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/youtube-log.json")
SKIP_PREFIXES = ["reel-v2-"]  # test files

# --- Load tracking log ---
if os.path.exists(LOG_PATH):
    with open(LOG_PATH) as f:
        yt_log = json.load(f)
else:
    yt_log = {}

# --- Find unuploaded reels ---
all_reels = glob.glob(os.path.join(REELS_DIR, "reel-*.mp4"))
# Filter out test files
all_reels = [r for r in all_reels if not any(os.path.basename(r).startswith(p) for p in SKIP_PREFIXES)]
# Filter out already uploaded
unuploaded = [r for r in all_reels if os.path.basename(r) not in yt_log]
# Sort by mtime newest first
unuploaded.sort(key=lambda x: os.path.getmtime(x), reverse=True)
# Take up to 2
to_upload = unuploaded[:2]

print(f"Total reels: {len(all_reels)}, Already uploaded: {len(all_reels) - len(unuploaded)}, To upload: {len(to_upload)}")

if not to_upload:
    print("Nothing to upload. All reels are already on YouTube.")
    exit(0)

# --- Fetch recent articles from Supabase ---
print("\nFetching recent articles from Supabase...")
try:
    r = req.get(
        f"{SUPABASE_URL}/rest/v1/p2_articles?status=eq.published&order=published_at.desc&limit=50&select=id,slug,headline,subheadline,category,tags",
        headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"},
        timeout=15
    )
    articles = r.json()
    print(f"  Fetched {len(articles)} recent articles")
except Exception as e:
    print(f"  Warning: Could not fetch articles: {e}")
    articles = []

def match_article(filename):
    """Match a reel filename to a Supabase article."""
    base = filename.replace(".mp4", "")
    # Strip reel- prefix
    if base.startswith("reel-"):
        base = base[5:]
    # Strip trailing date pattern (e.g., -20260529)
    base_no_date = re.sub(r'-\d{8}$', '', base)
    slug_words = set(base_no_date.split('-'))
    
    best_match = None
    best_score = 0
    for art in articles:
        slug = art.get("slug", "")
        slug_clean = re.sub(r'-\d{8}$', '', slug)
        art_words = set(slug_clean.split('-'))
        overlap = len(slug_words & art_words)
        score = overlap / max(len(slug_words), 1)
        if score > best_score and score > 0.4:
            best_score = score
            best_match = art
    return best_match

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

def extract_topic_hashtags(headline):
    """Extract topic-specific hashtags from headline."""
    tags = []
    # Common person/entity patterns
    words = headline.split()
    # Build potential hashtags from capitalized multi-word names
    i = 0
    while i < len(words):
        word = re.sub(r'[^\w]', '', words[i])
        if word and word[0].isupper() and len(word) > 2:
            # Check for multi-word name
            name_parts = [word]
            j = i + 1
            while j < len(words) and words[j][0:1].isupper():
                name_parts.append(re.sub(r'[^\w]', '', words[j]))
                j += 1
            if len(name_parts) > 1:
                tag = "#" + "".join(name_parts)
                if len(tag) < 30:
                    tags.append(tag)
            i = j
        else:
            i += 1
    return tags[:5]

def build_metadata(filename, article):
    """Build YouTube title, description, and tags."""
    if article:
        headline = article.get("headline", "")
        subheadline = article.get("subheadline", "")
        slug = article.get("slug", "")
        category = article.get("category", "news")
    else:
        # Construct from filename
        base = filename.replace(".mp4", "").replace("reel-", "")
        base = re.sub(r'-\d{8}$', '', base)
        headline = " ".join(w.capitalize() for w in base.split("-"))
        subheadline = headline
        slug = base
        category = "news"
    
    # Title: under 100 chars total (including " #Shorts" = 8 chars)
    suffix = " #Shorts"
    max_headline = 100 - len(suffix)
    if len(headline) > max_headline:
        headline = headline[:max_headline - 1].rsplit(' ', 1)[0] + "…"
    title = headline + suffix
    # Final safety check
    if len(title) > 100:
        title = title[:100]
    
    # Category hashtags
    cat_tags = CATEGORY_HASHTAGS.get(category, "#IndiaNews #DesiNews")
    topic_tags = extract_topic_hashtags(headline)
    topic_str = " ".join(topic_tags) if topic_tags else ""
    
    all_hashtags = f"#TheVideshi #Shorts #IndianDiaspora #NRI {cat_tags} {topic_str}".strip()
    
    description = f"""{subheadline}

📰 Full story: https://thevideshi.com/articles/{slug}

The Videshi — News for the global Indian diaspora
🌐 thevideshi.com

Follow us:
📸 Instagram: https://instagram.com/the.videshi
🐦 X/Twitter: https://x.com/thevideshi
🧵 Threads: https://threads.net/@the.videshi

{all_hashtags}"""
    
    # Tags list
    yt_tags = ["The Videshi", "Indian Diaspora", "NRI", "India News", category.replace("-", " ").title(), "Shorts"]
    # Add topic words from headline
    for w in headline.split()[:6]:
        clean = re.sub(r'[^\w]', '', w)
        if clean and len(clean) > 3 and clean not in yt_tags:
            yt_tags.append(clean)
    yt_tags = yt_tags[:12]
    
    return title, description, yt_tags, slug

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
print("  ✅ Authenticated")

# --- Upload loop ---
uploaded_count = 0
errors = []

for reel_path in to_upload:
    filename = os.path.basename(reel_path)
    print(f"\n{'='*60}")
    print(f"Uploading: {filename}")
    
    article = match_article(filename)
    if article:
        print(f"  Matched article: {article.get('headline', '')[:60]}...")
    else:
        print(f"  No article match — using filename-derived metadata")
    
    title, description, tags, slug = build_metadata(filename, article)
    print(f"  Title: {title}")
    print(f"  Tags: {tags}")
    
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
        
        # Log it
        yt_log[filename] = {
            "video_id": video_id,
            "article_slug": slug or "unknown",
            "uploaded_at": datetime.utcnow().isoformat() + "Z",
            "url": url
        }
        with open(LOG_PATH, 'w') as f:
            json.dump(yt_log, f, indent=2)
        
        uploaded_count += 1
        
        if uploaded_count < len(to_upload):
            print("  Waiting 10s before next upload...")
            time.sleep(10)
    
    except Exception as e:
        err_msg = f"Error uploading {filename}: {e}"
        print(f"  ❌ {err_msg}")
        errors.append(err_msg)

# --- Summary ---
print(f"\n{'='*60}")
print(f"SUMMARY: {uploaded_count}/{len(to_upload)} uploaded successfully")
if errors:
    print(f"Errors ({len(errors)}):")
    for e in errors:
        print(f"  - {e}")
for fn, data in yt_log.items():
    if fn in [os.path.basename(r) for r in to_upload]:
        print(f"  → {data['url']}")
