#!/usr/bin/env python3
"""Upload unuploaded Instagram Reels as YouTube Shorts."""

import json, os, re, time, sys
from datetime import datetime

import requests as req
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ── Load env files ──────────────────────────────────────────────────────
def load_env(path):
    env = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env

yt_env = load_env("~/workspace/.env.youtube")
sb_env = load_env("~/workspace/.env.supabase")

YOUTUBE_CLIENT_ID = yt_env["YOUTUBE_CLIENT_ID"]
YOUTUBE_CLIENT_SECRET = yt_env["YOUTUBE_CLIENT_SECRET"]
YOUTUBE_REFRESH_TOKEN = yt_env["YOUTUBE_REFRESH_TOKEN"]
SUPABASE_URL = sb_env.get("SUPABASE_URL", "https://lboecaekpynbpyijrbfz.supabase.co")
SB_KEY = sb_env.get("SUPABASE_SERVICE_KEY") or sb_env.get("SUPABASE_ANON_KEY") or sb_env.get("SUPABASE_KEY")

REELS_DIR = os.path.expanduser("~/workspace/the-videshi-news/pipeline/reels")
LOG_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/youtube-log.json")

# ── Load tracking log ───────────────────────────────────────────────────
if os.path.exists(LOG_PATH):
    with open(LOG_PATH) as f:
        yt_log = json.load(f)
else:
    yt_log = {}

# ── Find unuploaded reels ──────────────────────────────────────────────
all_reels = sorted(
    [f for f in os.listdir(REELS_DIR) if f.endswith(".mp4")],
    key=lambda f: os.path.getmtime(os.path.join(REELS_DIR, f)),
    reverse=True,
)

unuploaded = [f for f in all_reels if f not in yt_log]
print(f"Total reels: {len(all_reels)}, already uploaded: {len(yt_log)}, unuploaded: {len(unuploaded)}")

if not unuploaded:
    print("Nothing to upload.")
    sys.exit(0)

batch = unuploaded[:2]
print(f"Will upload {len(batch)} reel(s): {batch}")

# ── Fetch recent articles from Supabase ─────────────────────────────────
r = req.get(
    f"{SUPABASE_URL}/rest/v1/p2_articles?status=eq.published&order=published_at.desc&limit=50&select=id,slug,headline,subheadline,category,tags",
    headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"},
    timeout=15,
)
articles = r.json() if r.status_code == 200 else []
print(f"Fetched {len(articles)} recent articles for matching.")

# ── Category hashtags ───────────────────────────────────────────────────
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

def extract_slug_words(filename):
    """Strip reel- prefix and trailing date + .mp4 to get slug fragments."""
    name = filename.replace(".mp4", "")
    if name.startswith("reel-"):
        name = name[5:]
    # Remove trailing date pattern (YYYYMMDD or partial)
    name = re.sub(r'-?\d{6,8}$', '', name)
    return name.split("-")

def find_matching_article(filename):
    words = extract_slug_words(filename)
    best_match = None
    best_score = 0
    for art in articles:
        slug = art.get("slug", "")
        slug_words = set(slug.split("-"))
        overlap = len(set(words) & slug_words)
        if overlap > best_score:
            best_score = overlap
            best_match = art
    if best_score >= 3:
        return best_match
    return None

def make_title_from_filename(filename):
    words = extract_slug_words(filename)
    # Filter out very short words and capitalize
    title = " ".join(w.capitalize() for w in words if len(w) > 1)
    return title[:90]

def extract_topic_hashtags(headline):
    """Extract proper nouns and key terms as hashtags."""
    tags = []
    # Find capitalized multi-word names
    words = headline.split()
    for w in words:
        clean = re.sub(r'[^a-zA-Z0-9]', '', w)
        if clean and clean[0].isupper() and len(clean) > 2 and clean.lower() not in {
            "the", "and", "for", "from", "with", "this", "that", "how", "why",
            "what", "who", "new", "its", "has", "are", "was", "will", "but",
            "not", "all", "can", "had", "her", "his", "one", "our", "out",
            "day", "get", "may", "now", "old", "see", "way", "top", "after",
            "first", "into", "just", "over", "than", "them", "they", "very",
            "could", "about", "every", "their", "india", "indian", "news",
        }:
            tags.append(f"#{clean}")
    return tags[:5]

def compose_metadata(article, filename):
    if article:
        headline = article["headline"]
        subheadline = article.get("subheadline", "")
        slug = article["slug"]
        category = article.get("category", "news")
        article_tags = article.get("tags", []) or []
    else:
        headline = make_title_from_filename(filename)
        subheadline = "Latest news from The Videshi — for the global Indian diaspora."
        slug = None
        category = "news"
        article_tags = []

    # Title
    title = headline[:90]
    if len(title) + 8 <= 100:
        title += " #Shorts"

    # Hashtags
    base_tags = "#TheVideshi #Shorts #IndianDiaspora #NRI"
    cat_tags = CATEGORY_TAGS.get(category, "#IndiaNews #DesiNews")
    topic_tags = " ".join(extract_topic_hashtags(headline))
    all_hashtags = f"{base_tags} {cat_tags} {topic_tags}".strip()

    # Description
    story_link = f"\n📰 Full story: https://thevideshi.com/articles/{slug}" if slug else ""
    description = f"""{subheadline}
{story_link}

The Videshi — News for the global Indian diaspora
🌐 thevideshi.com

Follow us:
📸 Instagram: https://instagram.com/the.videshi
🐦 X/Twitter: https://x.com/thevideshi
🧵 Threads: https://threads.net/@the.videshi

{all_hashtags}"""

    # YouTube tags
    yt_tags = ["The Videshi", "Indian Diaspora", "NRI", "India News", category.replace("-", " ").title(), "Shorts"]
    for t in article_tags[:3]:
        if t and t not in yt_tags:
            yt_tags.append(t)
    topic_words = extract_topic_hashtags(headline)
    for tw in topic_words[:3]:
        clean = tw.lstrip("#")
        if clean not in yt_tags:
            yt_tags.append(clean)
    yt_tags = yt_tags[:12]

    return title, description, yt_tags, slug or "unknown"

# ── YouTube client ──────────────────────────────────────────────────────
creds = Credentials(
    token=None,
    refresh_token=YOUTUBE_REFRESH_TOKEN,
    token_uri="https://oauth2.googleapis.com/token",
    client_id=YOUTUBE_CLIENT_ID,
    client_secret=YOUTUBE_CLIENT_SECRET,
)
youtube = build("youtube", "v3", credentials=creds)

# ── Upload loop ─────────────────────────────────────────────────────────
results = []
for i, reel_filename in enumerate(batch):
    reel_path = os.path.join(REELS_DIR, reel_filename)
    print(f"\n{'='*60}")
    print(f"[{i+1}/{len(batch)}] Processing: {reel_filename}")

    article = find_matching_article(reel_filename)
    if article:
        print(f"  Matched article: {article['headline'][:80]}")
    else:
        print("  No article match — using filename-derived title")

    title, description, tags, slug = compose_metadata(article, reel_filename)
    print(f"  Title: {title}")
    print(f"  Tags: {tags}")

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "25",
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(reel_path, mimetype="video/mp4", resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    try:
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"  Upload progress: {int(status.progress() * 100)}%")

        video_id = response["id"]
        url = f"https://youtube.com/shorts/{video_id}"
        print(f"  ✅ Uploaded: {url}")

        yt_log[reel_filename] = {
            "video_id": video_id,
            "article_slug": slug,
            "uploaded_at": datetime.utcnow().isoformat() + "Z",
            "url": url,
        }
        with open(LOG_PATH, "w") as f:
            json.dump(yt_log, f, indent=2)

        results.append({"file": reel_filename, "url": url, "status": "success"})

    except Exception as e:
        print(f"  ❌ Upload failed: {e}")
        results.append({"file": reel_filename, "error": str(e), "status": "failed"})

    if i < len(batch) - 1:
        print("  Waiting 10s before next upload...")
        time.sleep(10)

# ── Summary ─────────────────────────────────────────────────────────────
print(f"\n{'='*60}")
print("SUMMARY")
success = [r for r in results if r["status"] == "success"]
failed = [r for r in results if r["status"] == "failed"]
print(f"  Uploaded: {len(success)}, Failed: {len(failed)}")
for r in success:
    print(f"  ✅ {r['file']} → {r['url']}")
for r in failed:
    print(f"  ❌ {r['file']} → {r['error']}")
