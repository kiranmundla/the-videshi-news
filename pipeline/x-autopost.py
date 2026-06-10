#!/usr/bin/env python3
"""Post recently published Videshi articles to X as long-form posts with images."""

import json
import os
import sys
import time
import tempfile
import requests
import tweepy
from datetime import datetime, timezone

# --- Config ---
SUPABASE_URL = "https://lboecaekpynbpyijrbfz.supabase.co"

def load_env(path):
    env = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.startswith('export '):
                line = line[7:]
            key, _, val = line.partition('=')
            env[key.strip()] = val.strip()
    return env

twitter_env = load_env("~/workspace/.env.twitter")
supabase_env = load_env("~/workspace/.env.supabase")

CONSUMER_KEY = twitter_env["TWITTER_CONSUMER_KEY"]
CONSUMER_SECRET = twitter_env["TWITTER_CONSUMER_SECRET"]
ACCESS_TOKEN = twitter_env["TWITTER_ACCESS_TOKEN"]
ACCESS_TOKEN_SECRET = twitter_env["TWITTER_ACCESS_TOKEN_SECRET"]
SUPABASE_KEY = supabase_env["SUPABASE_SERVICE_ROLE_KEY"]

SB_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}

CATEGORY_EMOJI = {
    "news": "🇮🇳",
    "immigration": "🛂",
    "nri-world": "🌏",
    "travel": "✈️",
    "lifestyle": "🧘",
    "markets": "📈",
    "technology": "💻",
    "sports": "🏏",
    "entertainment": "🎬",
    "food": "🍛",
}

# --- Fetch articles ---
print("Fetching unposted articles from Supabase...")
resp = requests.get(
    f"{SUPABASE_URL}/rest/v1/p2_articles",
    headers=SB_HEADERS,
    params={
        "status": "eq.published",
        "tweeted_at": "is.null",
        "order": "published_at.desc",
        "limit": "20",
        "select": "id,slug,headline,subheadline,category,tags,image_url,body",
    },
    timeout=30,
)
resp.raise_for_status()
articles = resp.json()
print(f"Found {len(articles)} unposted articles.")

# Filter: must have image_url, pick up to 4
candidates = [a for a in articles if a.get("image_url")]
selected = candidates[:4]
print(f"Selected {len(selected)} articles to post (with images).")

if not selected:
    print("No articles to post. Done.")
    sys.exit(0)

# --- Setup tweepy ---
client = tweepy.Client(
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET,
)
auth = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api_v1 = tweepy.API(auth)

# --- Compose post ---
def compose_post(article):
    """Use the article body to compose a long-form X post."""
    cat = (article.get("category") or "news").lower()
    emoji = CATEGORY_EMOJI.get(cat, "📰")
    cat_label = cat.upper().replace("-", " ")
    headline = article.get("headline", "").strip()
    subheadline = article.get("subheadline", "").strip()
    slug = article.get("slug", "")
    body = article.get("body", "") or ""

    # Truncate body for context (first ~3000 chars is plenty for summary extraction)
    body_excerpt = body[:3000]

    return {
        "emoji": emoji,
        "cat_label": cat_label,
        "headline": headline,
        "subheadline": subheadline,
        "slug": slug,
        "body_excerpt": body_excerpt,
        "category": cat,
    }

def build_post_text(info, summary_paragraphs, takeaways, punchy_headline):
    """Build the final post text."""
    lines = []
    lines.append(f'{info["emoji"]} {info["cat_label"]} | The Videshi')
    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("")
    lines.append(punchy_headline)
    lines.append("")
    lines.append(summary_paragraphs)
    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("")
    lines.append("Key Takeaways:")
    lines.append("")
    for t in takeaways:
        lines.append(f"▸ {t}")
    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("")
    lines.append(f'📰 Full story: thevideshi.com/articles/{info["slug"]}')
    lines.append("")
    lines.append("The Videshi — Your daily source for Indian diaspora news")
    lines.append("🌐 thevideshi.com")

    text = "\n".join(lines)
    # Ensure under 4000 chars
    if len(text) > 3900:
        # Trim summary paragraphs
        text = text[:3900]
    return text


def download_image(url):
    """Download image to temp file, return path or None."""
    try:
        r = requests.get(
            url,
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=15,
            stream=True,
        )
        r.raise_for_status()
        # Determine extension
        ct = r.headers.get("Content-Type", "")
        ext = ".jpg"
        if "png" in ct:
            ext = ".png"
        elif "webp" in ct:
            ext = ".webp"
        elif "gif" in ct:
            ext = ".gif"

        tmp = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
        for chunk in r.iter_content(8192):
            tmp.write(chunk)
        tmp.close()
        # Check file size
        fsize = os.path.getsize(tmp.name)
        if fsize < 1000:
            print(f"  Image too small ({fsize} bytes), skipping image attach.")
            os.unlink(tmp.name)
            return None
        print(f"  Downloaded image: {fsize} bytes → {tmp.name}")
        return tmp.name
    except Exception as e:
        print(f"  Image download failed: {e}")
        return None


def upload_media(img_path):
    """Upload image to X, return media object or None."""
    try:
        media = api_v1.media_upload(filename=img_path)
        print(f"  Media uploaded: media_id={media.media_id}")
        return media
    except Exception as e:
        print(f"  Media upload failed: {e}")
        return None


# --- Process each article ---
LOG_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/tweet-log.json")
tweet_log = {}
if os.path.exists(LOG_PATH):
    with open(LOG_PATH) as f:
        tweet_log = json.load(f)

posted = 0
errors = []
results = []

for i, article in enumerate(selected):
    info = compose_post(article)
    print(f"\n--- Article {i+1}/{len(selected)}: {info['headline'][:80]} ---")
    print(f"  Category: {info['cat_label']}, Slug: {info['slug']}")

    # We need to generate a good summary + takeaways from the body.
    # Since we can't call an LLM from within the script, we'll do a smart extraction.
    body = info["body_excerpt"]
    headline = info["headline"]
    subheadline = info["subheadline"]

    # Write article data to a temp file for the main agent to process
    article_data_path = f"/tmp/article_{i}.json"
    with open(article_data_path, "w") as f:
        json.dump({
            "headline": headline,
            "subheadline": subheadline,
            "body": body,
            "category": info["category"],
            "slug": info["slug"],
        }, f)

    print(f"  Article data written to {article_data_path}")
    print(f"  NEEDS_LLM_SUMMARY")

print("\n=== Articles prepared. LLM summaries needed. ===")

# Save selected articles info for the parent to use
with open("/tmp/selected_articles.json", "w") as f:
    json.dump(selected, f, indent=2)

print(f"Selected articles saved to /tmp/selected_articles.json")
