#!/usr/bin/env python3
"""Upload unuploaded Instagram Reels as YouTube Shorts."""

import json, os, re, time, sys
from datetime import datetime
from dotenv import load_dotenv

import requests as req
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# --- Load env ---
load_dotenv(os.path.expanduser("~/workspace/.env.youtube"))
load_dotenv(os.path.expanduser("~/workspace/.env.supabase"))

YOUTUBE_CLIENT_ID = os.environ["YOUTUBE_CLIENT_ID"]
YOUTUBE_CLIENT_SECRET = os.environ["YOUTUBE_CLIENT_SECRET"]
YOUTUBE_REFRESH_TOKEN = os.environ["YOUTUBE_REFRESH_TOKEN"]
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://lboecaekpynbpyijrbfz.supabase.co")
SB_KEY = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_ANON_KEY") or os.environ["SUPABASE_KEY"]

REELS_DIR = os.path.expanduser("~/workspace/the-videshi-news/pipeline/reels")
LOG_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/youtube-log.json")
MAX_UPLOADS = 2

# --- Category hashtag map ---
CATEGORY_TAGS = {
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

def extract_slug_fragments(filename):
    """Strip reel- prefix, trailing date, and .mp4 to get slug fragments."""
    name = filename.replace(".mp4", "")
    name = re.sub(r"^reel-", "", name)
    # Strip trailing date like -20260531 or -2026060 (truncated)
    name = re.sub(r"-\d{7,8}$", "", name)
    return name.split("-")

def find_matching_article(fragments, articles):
    """Find best matching article by checking slug overlap with fragments."""
    best_match = None
    best_score = 0
    frag_set = set(fragments)
    for art in articles:
        slug = art.get("slug", "") or ""
        slug_words = set(slug.split("-"))
        overlap = len(frag_set & slug_words)
        if overlap > best_score:
            best_score = overlap
            best_match = art
    # Require at least 3 matching words for a confident match
    if best_score >= 3:
        return best_match
    return None

def make_title_from_filename(fragments):
    """Construct a title from filename fragments."""
    words = [w.capitalize() for w in fragments[:12]]
    return " ".join(words)

def generate_hashtags(category, headline):
    """Generate 15-20 hashtags."""
    base = "#TheVideshi #Shorts #IndianDiaspora #NRI"
    cat_tags = CATEGORY_TAGS.get(category, "#IndiaNews #DesiNews")

    # Extract topic-specific hashtags from headline
    topic_tags = []
    # Common patterns: proper nouns, multi-word names
    words = re.findall(r"[A-Z][a-z]+(?:\s[A-Z][a-z]+)*", headline or "")
    for w in words[:5]:
        tag = "#" + w.replace(" ", "").replace("'", "")
        if tag not in base and tag not in cat_tags and len(tag) > 3:
            topic_tags.append(tag)

    all_tags = f"{base} {cat_tags}"
    if topic_tags:
        all_tags += " " + " ".join(topic_tags[:5])
    return all_tags

def main():
    # Load tracking log
    yt_log = {}
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH) as f:
            yt_log = json.load(f)

    # Find unuploaded reels sorted by mtime (newest first)
    mp4s = [f for f in os.listdir(REELS_DIR) if f.endswith(".mp4")]
    mp4s_with_time = [(f, os.path.getmtime(os.path.join(REELS_DIR, f))) for f in mp4s]
    mp4s_with_time.sort(key=lambda x: x[1], reverse=True)

    unuploaded = [(f, t) for f, t in mp4s_with_time if f not in yt_log]

    if not unuploaded:
        print("✅ No unuploaded reels found. All caught up!")
        return

    print(f"Found {len(unuploaded)} unuploaded reel(s). Will upload up to {MAX_UPLOADS}.")

    # Fetch recent articles from Supabase
    try:
        r = req.get(
            f"{SUPABASE_URL}/rest/v1/p2_articles?status=eq.published&order=published_at.desc&limit=50&select=id,slug,headline,subheadline,category,tags",
            headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"},
            timeout=15
        )
        articles = r.json() if r.status_code == 200 else []
        print(f"Fetched {len(articles)} recent articles for matching.")
    except Exception as e:
        print(f"⚠️ Could not fetch articles: {e}")
        articles = []

    # Build YouTube client
    creds = Credentials(
        token=None,
        refresh_token=YOUTUBE_REFRESH_TOKEN,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=YOUTUBE_CLIENT_ID,
        client_secret=YOUTUBE_CLIENT_SECRET,
    )
    youtube = build("youtube", "v3", credentials=creds)

    uploaded_count = 0
    errors = []

    for reel_filename, mtime in unuploaded[:MAX_UPLOADS]:
        reel_path = os.path.join(REELS_DIR, reel_filename)
        print(f"\n📹 Processing: {reel_filename}")

        # Extract info
        fragments = extract_slug_fragments(reel_filename)
        article = find_matching_article(fragments, articles)

        if article:
            headline = article.get("headline", "")
            subheadline = article.get("subheadline", "") or ""
            slug = article.get("slug", "")
            category = article.get("category", "news")
            print(f"  Matched article: {slug}")
        else:
            headline = make_title_from_filename(fragments)
            subheadline = ""
            slug = "-".join(fragments)
            category = "news"
            print(f"  No article match — using filename title: {headline}")

        # Compose metadata
        title = headline[:93] + " #Shorts" if len(headline) > 93 else headline + " #Shorts"
        if len(title) > 100:
            title = headline[:90] + "… #Shorts"

        hashtags = generate_hashtags(category, headline)

        description = f"""{subheadline}

📰 Full story: https://thevideshi.com/articles/{slug}

The Videshi — News for the global Indian diaspora
🌐 thevideshi.com

Follow us:
📸 Instagram: https://instagram.com/the.videshi
🐦 X/Twitter: https://x.com/thevideshi
🧵 Threads: https://threads.net/@the.videshi

{hashtags}"""

        tags_list = [
            "The Videshi", "Indian Diaspora", "NRI", "India News",
            category.replace("-", " ").title(), "Shorts"
        ]
        # Add topic tags from headline
        topic_words = re.findall(r"[A-Z][a-z]+(?:\s[A-Z][a-z]+)*", headline or "")
        for tw in topic_words[:6]:
            if tw not in tags_list:
                tags_list.append(tw)
        tags_list = tags_list[:12]

        body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags_list,
                "categoryId": "25",
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False,
            },
        }

        print(f"  Title: {title}")
        print(f"  Tags: {tags_list}")

        try:
            media = MediaFileUpload(reel_path, mimetype="video/mp4", resumable=True)
            request = youtube.videos().insert(
                part="snippet,status",
                body=body,
                media_body=media,
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
                "url": url,
            }
            with open(LOG_PATH, "w") as f:
                json.dump(yt_log, f, indent=2)

            uploaded_count += 1

            # Wait between uploads
            if uploaded_count < MAX_UPLOADS and uploaded_count < len(unuploaded):
                print("  ⏳ Waiting 10 seconds...")
                time.sleep(10)

        except Exception as e:
            err_msg = f"❌ Failed to upload {reel_filename}: {e}"
            print(err_msg)
            errors.append(err_msg)

    # Summary
    print(f"\n{'='*50}")
    print(f"📊 Summary: {uploaded_count} uploaded, {len(errors)} error(s)")
    if errors:
        for e in errors:
            print(f"  {e}")

if __name__ == "__main__":
    main()
