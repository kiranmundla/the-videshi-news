#!/usr/bin/env python3
"""Post recently published Videshi articles to X as long-form posts with images."""

import json
import os
import sys
import time
import tempfile
import requests
from datetime import datetime, timezone

import tweepy

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
    "culture": "🧘",
    "lifestyle-health": "🧘",
    "markets": "📈",
    "markets-finance": "📈",
    "economy": "📈",
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
    "lifestyle": "LIFESTYLE",
    "culture": "LIFESTYLE & HEALTH",
    "lifestyle-health": "LIFESTYLE & HEALTH",
    "markets": "MARKETS & FINANCE",
    "markets-finance": "MARKETS & FINANCE",
    "economy": "MARKETS & FINANCE",
    "technology": "TECHNOLOGY",
    "sports": "SPORTS",
    "entertainment": "ENTERTAINMENT",
    "food": "FOOD",
}

# --- Init tweepy ---
client = tweepy.Client(
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET,
)

auth = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api_v1 = tweepy.API(auth)

# --- Fetch articles ---
print("Fetching unpublished-to-X articles...")
resp = requests.get(
    f"{SUPABASE_URL}/rest/v1/p2_articles",
    params={
        "status": "eq.published",
        "tweeted_at": "is.null",
        "order": "published_at.desc",
        "limit": "20",
        "select": "id,slug,headline,subheadline,category,tags,image_url,body",
    },
    headers=SB_HEADERS,
)
resp.raise_for_status()
articles = resp.json()
print(f"Found {len(articles)} untweeted articles")

# Filter articles with image_url and pick up to 4
candidates = [a for a in articles if a.get("image_url")]
to_post = candidates[:4]
print(f"Will post {len(to_post)} articles (with images)")

if not to_post:
    print("Nothing to post. Done.")
    sys.exit(0)

# --- Compose and post ---
LOG_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/tweet-log.json")

def load_tweet_log():
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH) as f:
            return json.load(f)
    return {}

def save_tweet_log(log):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, 'w') as f:
        json.dump(log, f, indent=2)

def extract_summary(body, max_words=250):
    """Extract a clean text summary from markdown body."""
    if not body:
        return ""
    import re
    # Remove markdown images, links, headers, bold, italic
    text = re.sub(r'!\[.*?\]\(.*?\)', '', body)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    text = re.sub(r'<[^>]+>', '', text)
    # Split into paragraphs, take first few
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip() and len(p.strip()) > 40]
    result = []
    word_count = 0
    for p in paragraphs:
        words = p.split()
        if word_count + len(words) > max_words:
            break
        result.append(p)
        word_count += len(words)
        if len(result) >= 3:
            break
    return '\n\n'.join(result)

def extract_takeaways(body, subheadline):
    """Extract key facts for takeaways."""
    import re
    facts = []
    if subheadline:
        # Split subheadline on common delimiters
        parts = re.split(r'[;|•]', subheadline)
        for p in parts:
            p = p.strip()
            if len(p) > 15:
                facts.append(p)
    if body:
        # Look for bullet points or numbered lists in body
        lines = body.split('\n')
        for line in lines:
            line = line.strip()
            if re.match(r'^[-*▸•]\s+', line):
                clean = re.sub(r'^[-*▸•]\s+', '', line).strip()
                clean = re.sub(r'\*\*([^*]+)\*\*', r'\1', clean)
                clean = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', clean)
                if 20 < len(clean) < 200:
                    facts.append(clean)
            if len(facts) >= 6:
                break
    # Deduplicate and return top 4
    seen = set()
    unique = []
    for f in facts:
        key = f.lower()[:30]
        if key not in seen:
            seen.add(key)
            unique.append(f)
    return unique[:4]

def compose_post(article):
    cat = (article.get("category") or "news").lower()
    emoji = CATEGORY_EMOJI.get(cat, "🇮🇳")
    label = CATEGORY_LABEL.get(cat, "NEWS")
    headline = article.get("headline", "").strip()
    slug = article.get("slug", "")
    body = article.get("body", "")
    subheadline = article.get("subheadline", "")

    summary = extract_summary(body, max_words=200)
    takeaways = extract_takeaways(body, subheadline)

    # Build the post
    lines = []
    lines.append(f"{emoji} {label} | The Videshi")
    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("")
    lines.append(headline.upper() if len(headline) < 80 else headline)
    lines.append("")
    if summary:
        lines.append(summary)
        lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("")
    if takeaways:
        lines.append("Key Takeaways:")
        lines.append("")
        for t in takeaways:
            lines.append(f"▸ {t}")
        lines.append("")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append("")
    lines.append(f"📰 Full story: thevideshi.com/articles/{slug}")
    lines.append("")
    lines.append("The Videshi — Your daily source for Indian diaspora news")
    lines.append("🌐 thevideshi.com")

    post_text = '\n'.join(lines)

    # Trim if over 4000 chars
    if len(post_text) > 3900:
        # Shorten summary
        summary = extract_summary(body, max_words=120)
        lines_short = []
        lines_short.append(f"{emoji} {label} | The Videshi")
        lines_short.append("")
        lines_short.append("━━━━━━━━━━━━━━━━━━━━━━━━")
        lines_short.append("")
        lines_short.append(headline.upper() if len(headline) < 80 else headline)
        lines_short.append("")
        if summary:
            lines_short.append(summary)
            lines_short.append("")
        lines_short.append("━━━━━━━━━━━━━━━━━━━━━━━━")
        lines_short.append("")
        if takeaways:
            lines_short.append("Key Takeaways:")
            lines_short.append("")
            for t in takeaways[:3]:
                lines_short.append(f"▸ {t}")
            lines_short.append("")
            lines_short.append("━━━━━━━━━━━━━━━━━━━━━━━━")
            lines_short.append("")
        lines_short.append(f"📰 Full story: thevideshi.com/articles/{slug}")
        lines_short.append("")
        lines_short.append("The Videshi — Your daily source for Indian diaspora news")
        lines_short.append("🌐 thevideshi.com")
        post_text = '\n'.join(lines_short)

    return post_text

def download_image(url):
    """Download image to temp file, return path or None."""
    try:
        r = requests.get(url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=15)
        r.raise_for_status()
        ct = r.headers.get("Content-Type", "image/jpeg")
        ext = ".jpg"
        if "png" in ct:
            ext = ".png"
        elif "webp" in ct:
            ext = ".webp"
        elif "gif" in ct:
            ext = ".gif"
        tmp = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
        tmp.write(r.content)
        tmp.close()
        return tmp.name
    except Exception as e:
        print(f"  Image download failed: {e}")
        return None

posted = 0
errors = []
tweet_log = load_tweet_log()

for i, article in enumerate(to_post):
    headline = article.get("headline", "N/A")
    slug = article.get("slug", "")
    article_id = article["id"]
    print(f"\n--- [{i+1}/{len(to_post)}] {headline[:80]} ---")

    post_text = compose_post(article)
    print(f"  Post length: {len(post_text)} chars")

    # Try to attach image
    media_ids = None
    image_url = article.get("image_url", "")
    tmp_path = None
    if image_url:
        tmp_path = download_image(image_url)
        if tmp_path:
            try:
                media = api_v1.media_upload(filename=tmp_path)
                media_ids = [media.media_id]
                print(f"  Image uploaded: media_id={media.media_id}")
            except Exception as e:
                print(f"  Image upload to X failed: {e}")
                media_ids = None

    # Post tweet
    try:
        kwargs = {"text": post_text}
        if media_ids:
            kwargs["media_ids"] = media_ids
        tweet_resp = client.create_tweet(**kwargs)
        tweet_id = tweet_resp.data["id"]
        tweet_url = f"https://x.com/thevideshi/status/{tweet_id}"
        print(f"  ✅ Posted: {tweet_url}")

        # Update Supabase
        now_utc = datetime.now(timezone.utc).isoformat()
        patch_resp = requests.patch(
            f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article_id}",
            headers=SB_HEADERS,
            json={"tweeted_at": now_utc},
        )
        if patch_resp.status_code < 300:
            print(f"  Supabase updated: tweeted_at={now_utc}")
        else:
            print(f"  Supabase update warning: {patch_resp.status_code} {patch_resp.text}")

        # Log tweet
        tweet_log[str(tweet_id)] = {
            "article_id": article_id,
            "slug": slug,
            "posted_at": datetime.utcnow().isoformat() + "Z",
        }
        save_tweet_log(tweet_log)

        posted += 1

    except Exception as e:
        err_msg = f"Tweet failed for '{headline[:50]}': {e}"
        print(f"  ❌ {err_msg}")
        errors.append(err_msg)

    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)

    # Wait between posts
    if i < len(to_post) - 1:
        print("  Waiting 30s...")
        time.sleep(30)

# --- Summary ---
print(f"\n{'='*50}")
print(f"SUMMARY: Posted {posted}/{len(to_post)} articles to X")
if errors:
    print(f"Errors ({len(errors)}):")
    for e in errors:
        print(f"  - {e}")
print(f"{'='*50}")
