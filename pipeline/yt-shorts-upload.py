#!/usr/bin/env python3
"""Upload unuploaded Instagram Reels as YouTube Shorts for The Videshi."""

import json, os, sys, time, re
from datetime import datetime

import requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# --- Config ---
REELS_DIR = os.path.expanduser("~/workspace/the-videshi-news/pipeline/reels")
LOG_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/youtube-log.json")
ENV_YT = os.path.expanduser("~/workspace/.env.youtube")
ENV_SB = os.path.expanduser("~/workspace/.env.supabase")
MAX_UPLOADS = 2

# --- Load env files ---
def load_env(path):
    env = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip()
    return env

yt_env = load_env(ENV_YT)
sb_env = load_env(ENV_SB)

YOUTUBE_CLIENT_ID = yt_env["YOUTUBE_CLIENT_ID"]
YOUTUBE_CLIENT_SECRET = yt_env["YOUTUBE_CLIENT_SECRET"]
YOUTUBE_REFRESH_TOKEN = yt_env["YOUTUBE_REFRESH_TOKEN"]
SUPABASE_URL = sb_env.get("SUPABASE_URL", "https://lboecaekpynbpyijrbfz.supabase.co")
SB_KEY = sb_env.get("SUPABASE_SERVICE_KEY", sb_env.get("SUPABASE_KEY", ""))

# --- Load tracking log ---
if os.path.exists(LOG_PATH):
    with open(LOG_PATH) as f:
        yt_log = json.load(f)
else:
    yt_log = {}

# --- Find unuploaded reels ---
reel_files = [f for f in os.listdir(REELS_DIR) if f.endswith(".mp4")]
reel_files_with_mtime = [(f, os.path.getmtime(os.path.join(REELS_DIR, f))) for f in reel_files]
reel_files_with_mtime.sort(key=lambda x: x[1], reverse=True)  # newest first

unuploaded = [(f, mt) for f, mt in reel_files_with_mtime if f not in yt_log]
print(f"Total reels: {len(reel_files)}, Already uploaded: {len(yt_log)}, Unuploaded: {len(unuploaded)}")

if not unuploaded:
    print("Nothing to upload.")
    sys.exit(0)

to_upload = unuploaded[:MAX_UPLOADS]
print(f"Will upload {len(to_upload)} reel(s) this run.\n")

# --- Fetch recent articles from Supabase ---
try:
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/p2_articles?status=eq.published&order=published_at.desc&limit=50&select=id,slug,headline,subheadline,category,tags",
        headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"},
        timeout=15
    )
    articles = r.json()
    print(f"Fetched {len(articles)} recent articles for matching.\n")
except Exception as e:
    print(f"Warning: Could not fetch articles: {e}")
    articles = []

# --- Category hashtag map ---
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

def extract_slug_words(filename):
    """Extract slug words from reel filename."""
    name = filename.replace(".mp4", "")
    # Strip reel- prefix
    if name.startswith("reel-"):
        name = name[5:]
    # Strip trailing date (YYYYMMDD)
    name = re.sub(r'-?\d{8}$', '', name)
    return name.split("-")

def match_article(filename, articles):
    """Try to find a matching article for a reel filename."""
    slug_words = extract_slug_words(filename)
    slug_fragment = "-".join(slug_words)
    
    best_match = None
    best_score = 0
    
    for art in articles:
        slug = art.get("slug", "")
        if not slug:
            continue
        # Count how many slug words appear in the article slug
        score = sum(1 for w in slug_words if w in slug and len(w) > 2)
        # Normalize by total words
        if len(slug_words) > 0:
            norm_score = score / len(slug_words)
        else:
            norm_score = 0
        if norm_score > best_score and norm_score >= 0.4:
            best_score = norm_score
            best_match = art
    
    return best_match

def make_title_from_filename(filename):
    """Fallback: construct title from filename words."""
    words = extract_slug_words(filename)
    title = " ".join(w.capitalize() for w in words if len(w) > 1)
    return title[:90]

def extract_topic_hashtags(headline):
    """Extract person/topic specific hashtags from headline."""
    tags = []
    # Common names/topics to hashtagify
    words = headline.split()
    # Find capitalized multi-word names
    i = 0
    while i < len(words):
        w = re.sub(r'[^\w]', '', words[i])
        if len(w) > 2 and w[0].isupper() and w not in ('The', 'And', 'For', 'With', 'From', 'Into', 'Has', 'Are', 'How', 'Why', 'What', 'New', 'Its', 'Not', 'But', 'Can', 'Will', 'May', 'Now', 'Get', 'All', 'His', 'Her', 'Out', 'Top', 'Big'):
            # Check if next word is also capitalized (multi-word name)
            if i + 1 < len(words):
                w2 = re.sub(r'[^\w]', '', words[i+1])
                if len(w2) > 1 and w2[0].isupper() and w2 not in ('The', 'And', 'For', 'With', 'From', 'Into', 'Has', 'Are', 'How', 'Why', 'What', 'New', 'Its', 'Not', 'But', 'Can', 'Will', 'May', 'Now', 'Get', 'All', 'His', 'Her', 'Out', 'Top', 'Big'):
                    tags.append(f"#{w}{w2}")
                    i += 2
                    continue
            tags.append(f"#{w}")
        i += 1
    return tags[:5]

def compose_metadata(article, filename, category):
    """Compose YouTube metadata."""
    if article:
        headline = article.get("headline", "")
        subheadline = article.get("subheadline", "")
        slug = article.get("slug", "unknown")
        cat = article.get("category", category or "news")
        tags_list = article.get("tags", []) or []
    else:
        headline = make_title_from_filename(filename)
        subheadline = "News for the global Indian diaspora"
        slug = "unknown"
        cat = "news"
        tags_list = []

    # Title
    title = headline[:92] + " #Shorts" if len(headline) <= 92 else headline[:89] + "... #Shorts"

    # Hashtags
    base_hashtags = "#TheVideshi #Shorts #IndianDiaspora #NRI"
    cat_hashtags = CATEGORY_HASHTAGS.get(cat, "#IndiaNews #DesiNews")
    topic_hashtags = " ".join(extract_topic_hashtags(headline))
    all_hashtags = f"{base_hashtags} {cat_hashtags} {topic_hashtags}".strip()

    # Description
    article_link = f"https://thevideshi.com/articles/{slug}" if slug != "unknown" else "https://thevideshi.com"
    description = f"""{subheadline}

📰 Full story: {article_link}

The Videshi — News for the global Indian diaspora
🌐 thevideshi.com

Follow us:
📸 Instagram: https://instagram.com/the.videshi
🐦 X/Twitter: https://x.com/thevideshi
🧵 Threads: https://threads.net/@the.videshi

{all_hashtags}"""

    # Tags
    yt_tags = ["The Videshi", "Indian Diaspora", "NRI", "India News", cat.replace("-", " ").title(), "Shorts"]
    # Add topic-specific tags from headline
    for t in extract_topic_hashtags(headline)[:4]:
        tag_clean = t.replace("#", "")
        if tag_clean not in yt_tags:
            yt_tags.append(tag_clean)
    # Add from article tags
    if isinstance(tags_list, list):
        for t in tags_list[:3]:
            if isinstance(t, str) and t not in yt_tags:
                yt_tags.append(t)
    yt_tags = yt_tags[:12]

    return title, description, yt_tags, slug

# --- YouTube client ---
creds = Credentials(
    token=None,
    refresh_token=YOUTUBE_REFRESH_TOKEN,
    token_uri="https://oauth2.googleapis.com/token",
    client_id=YOUTUBE_CLIENT_ID,
    client_secret=YOUTUBE_CLIENT_SECRET,
)
youtube = build("youtube", "v3", credentials=creds)

# --- Upload loop ---
uploaded_count = 0
errors = []
results = []

for idx, (reel_filename, mtime) in enumerate(to_upload):
    reel_path = os.path.join(REELS_DIR, reel_filename)
    print(f"--- [{idx+1}/{len(to_upload)}] {reel_filename} ---")
    
    # Match article
    article = match_article(reel_filename, articles)
    if article:
        print(f"  Matched article: {article.get('slug', 'unknown')}")
    else:
        print(f"  No article match found, using filename-based title")
    
    title, description, tags, slug = compose_metadata(article, reel_filename, None)
    print(f"  Title: {title}")
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
        
        # Log
        yt_log[reel_filename] = {
            "video_id": video_id,
            "article_slug": slug,
            "uploaded_at": datetime.utcnow().isoformat() + "Z",
            "url": url
        }
        with open(LOG_PATH, 'w') as f:
            json.dump(yt_log, f, indent=2)
        
        uploaded_count += 1
        results.append((reel_filename, url))
        
        # Wait between uploads
        if idx < len(to_upload) - 1:
            print("  Waiting 10s before next upload...")
            time.sleep(10)
    
    except Exception as e:
        err_msg = f"Failed to upload {reel_filename}: {e}"
        print(f"  ❌ {err_msg}")
        errors.append(err_msg)

# --- Summary ---
print(f"\n{'='*60}")
print(f"SUMMARY: Uploaded {uploaded_count}/{len(to_upload)} reels")
for fn, url in results:
    print(f"  ✅ {fn} → {url}")
for err in errors:
    print(f"  ❌ {err}")
print(f"Total in log: {len(yt_log)}")
