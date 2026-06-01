#!/usr/bin/env python3
"""Post recently published Videshi articles to X as long-form posts with images."""

import json
import os
import sys
import time
import tempfile
import requests
import tweepy
from datetime import datetime

# --- Config ---
SUPABASE_URL = "https://lboecaekpynbpyijrbfz.supabase.co"

def load_env(path):
    env = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip()
    return env

twitter_env = load_env("~/workspace/.env.twitter")
supa_env = load_env("~/workspace/.env.supabase")

CONSUMER_KEY = twitter_env["TWITTER_CONSUMER_KEY"]
CONSUMER_SECRET = twitter_env["TWITTER_CONSUMER_SECRET"]
ACCESS_TOKEN = twitter_env["TWITTER_ACCESS_TOKEN"]
ACCESS_TOKEN_SECRET = twitter_env["TWITTER_ACCESS_TOKEN_SECRET"]
SUPABASE_KEY = supa_env["SUPABASE_SERVICE_ROLE_KEY"]

SUPA_HEADERS = {
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

CATEGORY_LABEL = {
    "news": "NEWS",
    "immigration": "IMMIGRATION",
    "nri-world": "NRI WORLD",
    "travel": "TRAVEL",
    "lifestyle": "LIFESTYLE & HEALTH",
    "markets": "MARKETS & FINANCE",
    "technology": "TECHNOLOGY",
    "sports": "SPORTS",
    "entertainment": "ENTERTAINMENT",
    "food": "FOOD",
}

# --- Fetch untweeted articles ---
print("Fetching untweeted articles...")
resp = requests.get(
    f"{SUPABASE_URL}/rest/v1/p2_articles",
    params={
        "status": "eq.published",
        "tweeted_at": "is.null",
        "order": "published_at.desc",
        "limit": "20",
        "select": "id,slug,headline,subheadline,category,tags,image_url,body",
    },
    headers=SUPA_HEADERS,
)
resp.raise_for_status()
articles = resp.json()
print(f"Found {len(articles)} untweeted articles")

# Filter: must have image_url, pick up to 4
candidates = [a for a in articles if a.get("image_url")]
selected = candidates[:4]
print(f"Selected {len(selected)} articles to post (with images)")

if not selected:
    print("Nothing to post. Done.")
    sys.exit(0)

# --- Setup tweepy clients ---
# v2 client for posting tweets
client = tweepy.Client(
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET,
)

# v1.1 API for media upload
auth = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api_v1 = tweepy.API(auth)

# --- Compose posts ---
def compose_post(article):
    cat = (article.get("category") or "news").lower()
    emoji = CATEGORY_EMOJI.get(cat, "📰")
    label = CATEGORY_LABEL.get(cat, cat.upper())
    headline = article.get("headline", "")
    subheadline = article.get("subheadline", "")
    slug = article.get("slug", "")
    body = article.get("body", "") or ""

    # Extract key content from body (strip markdown formatting)
    body_clean = body.replace("##", "").replace("**", "").replace("*", "")
    # Get first ~1500 chars of body for context
    body_excerpt = body_clean[:2000]

    return {
        "emoji": emoji,
        "label": label,
        "headline": headline,
        "subheadline": subheadline,
        "slug": slug,
        "body_excerpt": body_excerpt,
        "category": cat,
    }


def build_post_text(info):
    """Build the actual post text. We'll use a template and fill from article data."""
    # This will be filled by the LLM-generated content passed in
    pass


# We'll generate the posts via template since we can't call an LLM from here
# Instead, extract key facts and build a compelling post

def extract_key_points(body_text, subheadline):
    """Extract sentences that look like key facts from the body."""
    import re
    sentences = re.split(r'(?<=[.!?])\s+', body_text)
    # Filter for substantive sentences (contain numbers, names, or key words)
    key_sentences = []
    for s in sentences:
        s = s.strip()
        if len(s) < 20 or len(s) > 200:
            continue
        # Prefer sentences with numbers, quotes, or specific details
        if any(c.isdigit() for c in s) or '"' in s or '$' in s or '%' in s:
            key_sentences.append(s)
        elif len(key_sentences) < 6:
            key_sentences.append(s)
        if len(key_sentences) >= 8:
            break
    return key_sentences


def create_post_content(article):
    """Create a long-form X post from article data."""
    cat = (article.get("category") or "news").lower()
    emoji = CATEGORY_EMOJI.get(cat, "📰")
    label = CATEGORY_LABEL.get(cat, cat.upper())
    headline = article.get("headline", "")
    subheadline = article.get("subheadline", "")
    slug = article.get("slug", "")
    body = article.get("body", "") or ""

    # Clean markdown
    import re
    body_clean = re.sub(r'!\[.*?\]\(.*?\)', '', body)  # remove images
    body_clean = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', body_clean)  # links to text
    body_clean = body_clean.replace("###", "").replace("##", "").replace("#", "")
    body_clean = body_clean.replace("**", "").replace("*", "")
    body_clean = re.sub(r'\n{3,}', '\n\n', body_clean).strip()

    # Get paragraphs
    paragraphs = [p.strip() for p in body_clean.split('\n\n') if p.strip() and len(p.strip()) > 30]

    # Build summary from first 2-3 substantive paragraphs
    summary_parts = []
    char_count = 0
    for p in paragraphs[:5]:
        if char_count > 600:
            break
        # Skip very short or header-like paragraphs
        if len(p) < 40:
            continue
        summary_parts.append(p)
        char_count += len(p)

    summary = "\n\n".join(summary_parts[:3])
    # Truncate if too long
    if len(summary) > 800:
        summary = summary[:797] + "..."

    # Extract key takeaways
    key_points = extract_key_points(body_clean, subheadline)
    takeaways = key_points[:4]

    # Build the post
    lines = []
    lines.append(f"{emoji} {label} | The Videshi")
    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("")
    lines.append(headline.upper() if len(headline) < 100 else headline)
    lines.append("")
    lines.append(summary)
    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("")
    lines.append("Key Takeaways:")
    lines.append("")
    for t in takeaways:
        t_clean = t.strip().rstrip('.')
        if len(t_clean) > 150:
            t_clean = t_clean[:147] + "..."
        lines.append(f"▸ {t_clean}")
    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("")
    lines.append(f"📰 Full story: thevideshi.com/articles/{slug}")
    lines.append("")
    lines.append("The Videshi — Your daily source for Indian diaspora news")
    lines.append("🌐 thevideshi.com")

    text = "\n".join(lines)

    # Ensure under 4000 chars
    if len(text) > 3900:
        # Trim summary
        summary = summary[:400] + "..."
        lines[6] = summary
        text = "\n".join(lines)

    return text


# --- Post loop ---
log_path = os.path.expanduser("~/workspace/the-videshi-news/pipeline/tweet-log.json")
if os.path.exists(log_path):
    with open(log_path) as f:
        tweet_log = json.load(f)
else:
    tweet_log = {}

posted = 0
errors = []
tweet_urls = []

for i, article in enumerate(selected):
    article_id = article["id"]
    slug = article.get("slug", "unknown")
    headline = article.get("headline", "No headline")

    print(f"\n--- Article {i+1}/{len(selected)}: {headline[:80]} ---")

    try:
        # Compose post
        post_text = create_post_content(article)
        print(f"Post length: {len(post_text)} chars")

        # Try to upload image
        media_id = None
        image_url = article.get("image_url", "")
        if image_url:
            try:
                print(f"Downloading image: {image_url[:80]}...")
                img_resp = requests.get(image_url, timeout=15)
                if img_resp.status_code == 200:
                    # Determine extension
                    ct = img_resp.headers.get("content-type", "image/jpeg")
                    ext = ".jpg"
                    if "png" in ct:
                        ext = ".png"
                    elif "webp" in ct:
                        ext = ".webp"
                    elif "gif" in ct:
                        ext = ".gif"

                    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
                        tmp.write(img_resp.content)
                        tmp_path = tmp.name

                    print(f"Uploading image to X ({len(img_resp.content)} bytes)...")
                    media = api_v1.media_upload(filename=tmp_path)
                    media_id = media.media_id
                    os.unlink(tmp_path)
                    print(f"Image uploaded: media_id={media_id}")
                else:
                    print(f"Image download failed: HTTP {img_resp.status_code}")
            except Exception as e:
                print(f"Image upload failed: {e} — posting without image")
                media_id = None

        # Post tweet
        tweet_kwargs = {"text": post_text}
        if media_id:
            tweet_kwargs["media_ids"] = [media_id]

        print("Posting tweet...")
        tweet_resp = client.create_tweet(**tweet_kwargs)
        tweet_id = tweet_resp.data["id"]
        tweet_url = f"https://x.com/thevideshi/status/{tweet_id}"
        print(f"✅ Posted: {tweet_url}")
        tweet_urls.append(tweet_url)

        # Update Supabase
        patch_resp = requests.patch(
            f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article_id}",
            headers=SUPA_HEADERS,
            json={"tweeted_at": datetime.utcnow().isoformat() + "Z"},
        )
        if patch_resp.status_code in (200, 204):
            print(f"✅ Supabase updated: tweeted_at set")
        else:
            print(f"⚠️ Supabase update returned {patch_resp.status_code}: {patch_resp.text}")

        # Log tweet
        tweet_log[str(tweet_id)] = {
            "article_id": article_id,
            "slug": slug,
            "posted_at": datetime.utcnow().isoformat() + "Z",
        }
        with open(log_path, "w") as f:
            json.dump(tweet_log, f, indent=2)

        posted += 1

    except Exception as e:
        error_msg = f"Error posting '{headline[:60]}': {e}"
        print(f"❌ {error_msg}")
        errors.append(error_msg)

    # Wait between posts
    if i < len(selected) - 1:
        print("Waiting 30s before next post...")
        time.sleep(30)

# --- Summary ---
print("\n" + "=" * 50)
print(f"SUMMARY: Posted {posted}/{len(selected)} articles to X")
if tweet_urls:
    print("\nTweet URLs:")
    for url in tweet_urls:
        print(f"  {url}")
if errors:
    print(f"\nErrors ({len(errors)}):")
    for e in errors:
        print(f"  - {e}")
print("=" * 50)
