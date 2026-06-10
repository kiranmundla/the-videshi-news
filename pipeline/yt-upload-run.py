#!/usr/bin/env python3
"""Upload unuploaded reels to YouTube Shorts."""

import json, os, time, re, sys, requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load env
load_dotenv(os.path.expanduser("~/workspace/.env.youtube"))
load_dotenv(os.path.expanduser("~/workspace/.env.supabase"))

YOUTUBE_CLIENT_ID = os.environ["YOUTUBE_CLIENT_ID"]
YOUTUBE_CLIENT_SECRET = os.environ["YOUTUBE_CLIENT_SECRET"]
YOUTUBE_REFRESH_TOKEN = os.environ["YOUTUBE_REFRESH_TOKEN"]
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://lboecaekpynbpyijrbfz.supabase.co")
SB_KEY = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_KEY") or os.environ.get("SUPABASE_ANON_KEY")

REELS_DIR = os.path.expanduser("~/workspace/the-videshi-news/pipeline/reels")
LOG_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/youtube-log.json")

# Skip patterns - not real reels
SKIP_PATTERNS = ["voice-audition", "end-card"]

# Category hashtag map
CATEGORY_HASHTAGS = {
    "news": "#IndiaNews #BreakingNews #DesiNews #SouthAsian",
    "nri-world": "#NRILife #DesiAbroad #IndianAmerican",
    "immigration": "#H1B #H1BVisa #GreenCard #USImmigration #USCIS",
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
        with open(LOG_PATH) as f:
            return json.load(f)
    return {}

def save_log(log):
    with open(LOG_PATH, 'w') as f:
        json.dump(log, f, indent=2)

def get_unuploaded_reels(log):
    """Get reel files not yet in log, sorted newest first, skipping non-reels."""
    import glob
    mp4s = sorted(
        glob.glob(os.path.join(REELS_DIR, "*.mp4")),
        key=lambda f: os.path.getmtime(f),
        reverse=True
    )
    results = []
    for path in mp4s:
        fname = os.path.basename(path)
        if fname in log:
            continue
        if any(skip in fname for skip in SKIP_PATTERNS):
            continue
        # Only process files that start with 'reel-' or 'ss-reel-'
        if not (fname.startswith("reel-") or fname.startswith("ss-reel-")):
            continue
        results.append(path)
    return results

def extract_slug_fragments(filename):
    """Extract slug-like fragments from reel filename."""
    name = filename.replace(".mp4", "")
    # Strip prefixes
    if name.startswith("ss-reel-"):
        name = name[len("ss-reel-"):]
    elif name.startswith("reel-"):
        name = name[len("reel-"):]
    # Strip trailing date patterns like -20260610 or -20260609-1823
    name = re.sub(r'-\d{8}(-\d{4})?$', '', name)
    return name.split("-")

def find_matching_article(fragments, articles):
    """Find best matching article by slug fragment overlap."""
    best_match = None
    best_score = 0
    frag_set = set(fragments)
    
    for art in articles:
        slug = art.get("slug", "") or ""
        slug_words = set(slug.split("-"))
        overlap = len(frag_set & slug_words)
        # Require at least 3 matching words
        if overlap > best_score and overlap >= 3:
            best_score = overlap
            best_match = art
    return best_match

def fetch_recent_articles():
    """Fetch recent published articles from Supabase."""
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/p2_articles?status=eq.published&order=published_at.desc&limit=50&select=id,slug,headline,subheadline,category,tags",
        headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"},
        timeout=15
    )
    r.raise_for_status()
    return r.json()

def make_title_from_filename(fragments):
    """Construct a title from filename fragments."""
    title = " ".join(w.capitalize() for w in fragments if len(w) > 1)
    return title[:90]

def generate_hashtags(category, headline):
    """Generate hashtags based on category and headline content."""
    base = "#TheVideshi #Shorts #IndianDiaspora #NRI"
    cat_tags = CATEGORY_HASHTAGS.get(category, "#IndiaNews #DesiNews")
    
    # Extract topic-specific hashtags from headline
    topic_tags = []
    # Common person/topic patterns
    headline_lower = (headline or "").lower()
    words = re.findall(r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?', headline or "")
    for w in words[:5]:
        tag = "#" + w.replace(" ", "")
        if len(tag) > 3 and tag not in base and tag not in cat_tags:
            topic_tags.append(tag)
    
    topic_str = " ".join(topic_tags[:5])
    return f"{base} {cat_tags} {topic_str}".strip()

def compose_metadata(article, fragments, category_override=None):
    """Compose YouTube title, description, tags."""
    if article:
        headline = article.get("headline", "")
        subheadline = article.get("subheadline", "") or ""
        slug = article.get("slug", "")
        category = article.get("category", "news")
        tags_list = article.get("tags") or []
    else:
        headline = make_title_from_filename(fragments)
        subheadline = ""
        slug = "-".join(fragments)
        category = category_override or "news"
        tags_list = []
    
    # Title: keep under 100 chars with #Shorts
    title = headline[:90].strip()
    if not title.endswith("#Shorts"):
        if len(title) + 9 <= 100:
            title = f"{title} #Shorts"
    
    # Description
    hashtags = generate_hashtags(category, headline)
    article_url = f"https://thevideshi.com/articles/{slug}" if slug else "https://thevideshi.com"
    
    description = f"""{subheadline}

📰 Full story: {article_url}

The Videshi — News for the global Indian diaspora
🌐 thevideshi.com

Follow us:
📸 Instagram: https://instagram.com/the.videshi
🐦 X/Twitter: https://x.com/thevideshi
🧵 Threads: https://threads.net/@the.videshi

{hashtags}"""
    
    # Tags
    yt_tags = ["The Videshi", "Indian Diaspora", "NRI", "India News", category.replace("-", " ").title(), "Shorts"]
    if isinstance(tags_list, list):
        for t in tags_list[:4]:
            if t and t not in yt_tags:
                yt_tags.append(t)
    # Add headline keywords
    for w in re.findall(r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?', headline or ""):
        if w not in yt_tags and len(yt_tags) < 12:
            yt_tags.append(w)
    
    return title, description, yt_tags[:12]

def upload_to_youtube(reel_path, title, description, tags):
    """Upload a video to YouTube."""
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
    return video_id

def main():
    log = load_log()
    unuploaded = get_unuploaded_reels(log)
    
    if not unuploaded:
        print("✅ No new reels to upload.")
        return
    
    print(f"Found {len(unuploaded)} unuploaded reel(s)")
    
    # Fetch articles for matching
    try:
        articles = fetch_recent_articles()
        print(f"Fetched {len(articles)} recent articles for matching")
    except Exception as e:
        print(f"⚠️ Could not fetch articles: {e}")
        articles = []
    
    uploaded = 0
    errors = []
    urls = []
    
    # Process up to 2 per run
    for reel_path in unuploaded[:2]:
        fname = os.path.basename(reel_path)
        print(f"\n📤 Processing: {fname}")
        
        try:
            fragments = extract_slug_fragments(fname)
            article = find_matching_article(fragments, articles)
            
            if article:
                print(f"  Matched article: {article.get('headline', '')[:60]}...")
            else:
                print(f"  No article match, using filename fragments")
            
            title, description, tags = compose_metadata(article, fragments)
            print(f"  Title: {title}")
            
            video_id = upload_to_youtube(reel_path, title, description, tags)
            url = f"https://youtube.com/shorts/{video_id}"
            print(f"  ✅ Uploaded: {url}")
            
            # Log it
            log[fname] = {
                "video_id": video_id,
                "article_slug": article.get("slug", "unknown") if article else "unknown",
                "uploaded_at": datetime.utcnow().isoformat() + "Z",
                "url": url
            }
            save_log(log)
            
            uploaded += 1
            urls.append(url)
            
            # Wait between uploads
            if uploaded < min(2, len(unuploaded)):
                print("  ⏳ Waiting 10s before next upload...")
                time.sleep(10)
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
            errors.append((fname, str(e)))
    
    # Summary
    print(f"\n{'='*50}")
    print(f"📊 Summary: {uploaded} uploaded, {len(errors)} errors")
    for url in urls:
        print(f"  🔗 {url}")
    for fname, err in errors:
        print(f"  ❌ {fname}: {err}")

if __name__ == "__main__":
    main()
