#!/usr/bin/env python3
"""Upload unuploaded Instagram Reels as YouTube Shorts for The Videshi."""

import json, os, re, time, sys
from datetime import datetime
from dotenv import load_dotenv

# Load env
load_dotenv(os.path.expanduser("~/workspace/.env.youtube"))
load_dotenv(os.path.expanduser("~/workspace/.env.supabase"))

YOUTUBE_CLIENT_ID = os.environ.get("YOUTUBE_CLIENT_ID")
YOUTUBE_CLIENT_SECRET = os.environ.get("YOUTUBE_CLIENT_SECRET")
YOUTUBE_REFRESH_TOKEN = os.environ.get("YOUTUBE_REFRESH_TOKEN")
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://lboecaekpynbpyijrbfz.supabase.co")
SB_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY") or os.environ.get("SUPABASE_ANON_KEY")

REELS_DIR = os.path.expanduser("~/workspace/the-videshi-news/pipeline/reels")
LOG_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/youtube-log.json")
MAX_UPLOADS = 2

# Verify creds
for name, val in [("YOUTUBE_CLIENT_ID", YOUTUBE_CLIENT_ID), ("YOUTUBE_CLIENT_SECRET", YOUTUBE_CLIENT_SECRET),
                   ("YOUTUBE_REFRESH_TOKEN", YOUTUBE_REFRESH_TOKEN), ("SUPABASE_KEY", SB_KEY)]:
    if not val:
        print(f"❌ Missing {name}")
        sys.exit(1)

# Load log
yt_log = {}
if os.path.exists(LOG_PATH):
    with open(LOG_PATH) as f:
        yt_log = json.load(f)

# Find unuploaded reels (MP4 only, not covers)
all_reels = []
for fn in os.listdir(REELS_DIR):
    if fn.endswith(".mp4") and not fn.endswith("-cover.jpg"):
        full = os.path.join(REELS_DIR, fn)
        if fn not in yt_log:
            all_reels.append((fn, os.path.getmtime(full)))

# Sort newest first
all_reels.sort(key=lambda x: x[1], reverse=True)
print(f"📊 Found {len(all_reels)} unuploaded reel(s)")

if not all_reels:
    print("✅ Nothing to upload.")
    sys.exit(0)

# Fetch recent articles from Supabase
import requests as req
try:
    r = req.get(
        f"{SUPABASE_URL}/rest/v1/p2_articles?status=eq.published&order=published_at.desc&limit=30&select=id,slug,headline,subheadline,category,tags",
        headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"},
        timeout=15
    )
    articles = r.json() if r.status_code == 200 else []
    print(f"📰 Fetched {len(articles)} recent articles")
except Exception as e:
    print(f"⚠️ Supabase fetch failed: {e}")
    articles = []

def extract_slug_fragments(filename):
    """Strip reel- prefix and trailing date + .mp4 to get slug fragments."""
    name = filename.replace(".mp4", "")
    if name.startswith("reel-"):
        name = name[5:]
    # Remove trailing date pattern (YYYYMMDD)
    name = re.sub(r'-?\d{8}$', '', name)
    return name.split("-")

def match_article(filename, articles):
    """Find matching article by slug fragments."""
    fragments = extract_slug_fragments(filename)
    frag_str = "-".join(fragments)
    
    best_match = None
    best_score = 0
    
    for art in articles:
        slug = art.get("slug", "")
        if not slug:
            continue
        # Count how many fragments appear in the slug
        score = sum(1 for f in fragments if f in slug)
        # Bonus for exact substring match
        if frag_str in slug or slug in frag_str:
            score += 10
        if score > best_score and score >= max(3, len(fragments) * 0.5):
            best_score = score
            best_match = art
    
    return best_match

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

def generate_hashtags(category, headline):
    """Generate 15-20 hashtags."""
    base = "#TheVideshi #Shorts #IndianDiaspora #NRI"
    cat_tags = CATEGORY_HASHTAGS.get(category, "#IndiaNews #DesiNews #SouthAsian")
    
    # Extract topic hashtags from headline
    topic_tags = []
    # Common patterns - names, places, orgs
    words = re.findall(r'[A-Z][a-z]+(?:\s[A-Z][a-z]+)*', headline or "")
    for w in words[:5]:
        tag = "#" + w.replace(" ", "")
        if len(tag) > 3 and tag not in base and tag not in cat_tags:
            topic_tags.append(tag)
    
    # Known entities
    entity_map = {
        "uscis": "#USCIS", "h1b": "#H1B", "h-1b": "#H1B", "green card": "#GreenCard",
        "modi": "#NarendraModi", "trump": "#Trump", "kohli": "#ViratKohli",
        "ipl": "#IPL2026", "mumbai": "#Mumbai", "delhi": "#Delhi",
        "sensex": "#Sensex", "nifty": "#Nifty", "rbi": "#RBI",
        "infosys": "#Infosys", "tcs": "#TCS", "wipro": "#Wipro",
        "bollywood": "#Bollywood", "cricket": "#Cricket",
        "iran": "#Iran", "hormuz": "#StraitOfHormuz",
        "air india": "#AirIndia", "rfe": "#RFE", "aos": "#AOS",
        "adjustment of status": "#AdjustmentOfStatus",
    }
    hl_lower = (headline or "").lower()
    for key, tag in entity_map.items():
        if key in hl_lower and tag not in base and tag not in cat_tags:
            topic_tags.append(tag)
    
    # Deduplicate
    seen = set()
    unique_topics = []
    for t in topic_tags:
        if t.lower() not in seen:
            seen.add(t.lower())
            unique_topics.append(t)
    
    all_tags = f"{base} {cat_tags} {' '.join(unique_topics[:6])}"
    return all_tags

def compose_metadata(article, filename):
    """Compose YouTube title, description, tags."""
    if article:
        headline = article.get("headline", "")
        subheadline = article.get("subheadline", "")
        slug = article.get("slug", "")
        category = article.get("category", "news")
    else:
        # Construct from filename
        fragments = extract_slug_fragments(filename)
        headline = " ".join(f.capitalize() for f in fragments)
        subheadline = ""
        slug = ""
        category = "news"
    
    # Title: under 100 chars + #Shorts
    title = headline
    if len(title) > 90:
        title = title[:87] + "..."
    title = f"{title} #Shorts"
    
    # Description
    article_link = f"\n📰 Full story: https://thevideshi.com/articles/{slug}" if slug else ""
    hashtags = generate_hashtags(category, headline)
    
    description = f"""{subheadline}{article_link}

The Videshi — News for the global Indian diaspora
🌐 thevideshi.com

Follow us:
📸 Instagram: https://instagram.com/the.videshi
🐦 X/Twitter: https://x.com/thevideshi
🧵 Threads: https://threads.net/@the.videshi

{hashtags}"""
    
    # Tags
    tags = ["The Videshi", "Indian Diaspora", "NRI", "India News", category.replace("-", " ").title(), "Shorts"]
    # Add topic words from headline
    topic_words = re.findall(r'[A-Z][a-z]+(?:\s[A-Z][a-z]+)*', headline or "")
    for tw in topic_words[:4]:
        if tw not in tags:
            tags.append(tw)
    if len(tags) < 8:
        tags.extend(["South Asian", "Desi News"])
    tags = tags[:12]
    
    return title, description, tags, slug

# Setup YouTube client
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

uploaded = []
errors = []

for i, (reel_fn, mtime) in enumerate(all_reels[:MAX_UPLOADS]):
    reel_path = os.path.join(REELS_DIR, reel_fn)
    print(f"\n{'='*60}")
    print(f"📹 [{i+1}/{min(len(all_reels), MAX_UPLOADS)}] Uploading: {reel_fn}")
    
    # Match article
    article = match_article(reel_fn, articles)
    if article:
        print(f"  📰 Matched article: {article.get('headline', '')[:60]}...")
    else:
        print(f"  ⚠️ No article match, using filename-derived title")
    
    title, description, tags, slug = compose_metadata(article, reel_fn)
    print(f"  📝 Title: {title}")
    
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
        yt_url = f"https://youtube.com/shorts/{video_id}"
        print(f"  ✅ Uploaded: {yt_url}")
        
        # Log
        yt_log[reel_fn] = {
            "video_id": video_id,
            "article_slug": slug or "unknown",
            "uploaded_at": datetime.utcnow().isoformat() + "Z",
            "url": yt_url
        }
        with open(LOG_PATH, 'w') as f:
            json.dump(yt_log, f, indent=2)
        
        uploaded.append((reel_fn, yt_url))
        
        # Wait between uploads
        if i < min(len(all_reels), MAX_UPLOADS) - 1:
            print("  ⏳ Waiting 10s before next upload...")
            time.sleep(10)
    
    except Exception as e:
        print(f"  ❌ Upload failed: {e}")
        errors.append((reel_fn, str(e)))

# Summary
print(f"\n{'='*60}")
print(f"📊 SUMMARY")
print(f"  Uploaded: {len(uploaded)}")
print(f"  Errors: {len(errors)}")
for fn, url in uploaded:
    print(f"  ✅ {fn} → {url}")
for fn, err in errors:
    print(f"  ❌ {fn}: {err}")
