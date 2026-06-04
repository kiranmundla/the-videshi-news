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

SUPABASE_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
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
    "culture": "LIFESTYLE & CULTURE",
    "lifestyle-health": "LIFESTYLE & HEALTH",
    "markets": "MARKETS & FINANCE",
    "markets-finance": "MARKETS & FINANCE",
    "economy": "MARKETS & FINANCE",
    "technology": "TECHNOLOGY",
    "sports": "SPORTS",
    "entertainment": "ENTERTAINMENT",
    "food": "FOOD",
}

# --- Tweepy setup ---
client = tweepy.Client(
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET,
)

auth = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api_v1 = tweepy.API(auth)

# --- Fetch articles ---
print("Fetching untweeted articles...")
resp = requests.get(
    f"{SUPABASE_URL}/rest/v1/p2_articles",
    params={
        "status": "eq.published",
        "tweeted_at": "is.null",
        "order": "published_at.desc",
        "limit": "20",
        "select": "id,slug,headline,subheadline,category,tags,image_url,body"
    },
    headers=SUPABASE_HEADERS
)
resp.raise_for_status()
articles = resp.json()
print(f"Found {len(articles)} untweeted articles")

# Filter and pick up to 4
selected = []
for a in articles:
    if a.get("image_url"):
        selected.append(a)
    if len(selected) >= 4:
        break

print(f"Selected {len(selected)} articles with images")

def compose_post(article):
    """Compose a long-form X post from article data."""
    cat = (article.get("category") or "news").lower()
    emoji = CATEGORY_EMOJI.get(cat, "📰")
    label = CATEGORY_LABEL.get(cat, cat.upper())
    headline = article.get("headline", "")
    subheadline = article.get("subheadline", "")
    slug = article.get("slug", "")
    body = article.get("body", "") or ""

    # Truncate body for context (first ~3000 chars for summarization)
    body_excerpt = body[:3000] if len(body) > 3000 else body

    return {
        "emoji": emoji,
        "label": label,
        "headline": headline,
        "subheadline": subheadline,
        "slug": slug,
        "body_excerpt": body_excerpt,
        "category": cat,
    }

def write_post_text(info):
    """Generate the actual post text. We do this deterministically from article content."""
    # Extract key sentences from body for summary
    body = info["body_excerpt"]
    headline = info["headline"]
    subheadline = info["subheadline"]

    # Strip markdown formatting for cleaner extraction
    import re
    clean_body = re.sub(r'#{1,6}\s+', '', body)
    clean_body = re.sub(r'\*\*(.+?)\*\*', r'\1', clean_body)
    clean_body = re.sub(r'\*(.+?)\*', r'\1', clean_body)
    clean_body = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', clean_body)
    clean_body = re.sub(r'!\[.*?\]\(.*?\)', '', clean_body)
    clean_body = re.sub(r'<[^>]+>', '', clean_body)

    # Split into paragraphs, filter empty
    paragraphs = [p.strip() for p in clean_body.split('\n\n') if p.strip() and len(p.strip()) > 30]

    # Take first 3-5 substantive paragraphs for the summary
    summary_paras = paragraphs[:5] if len(paragraphs) >= 5 else paragraphs[:3]
    summary_text = '\n\n'.join(summary_paras)

    # Trim summary to ~250 words
    words = summary_text.split()
    if len(words) > 250:
        summary_text = ' '.join(words[:250])
        # End at sentence boundary
        last_period = summary_text.rfind('.')
        if last_period > len(summary_text) * 0.6:
            summary_text = summary_text[:last_period + 1]

    # Extract key facts for takeaways from body
    sentences = re.split(r'(?<=[.!?])\s+', clean_body)
    # Find sentences with numbers, names, or key facts
    fact_sentences = []
    for s in sentences:
        s = s.strip()
        if len(s) < 20 or len(s) > 200:
            continue
        # Prefer sentences with numbers, dollar signs, percentages, or proper nouns
        if re.search(r'\d+|[$%]|billion|million|crore|lakh', s, re.I):
            fact_sentences.append(s)
        elif len(fact_sentences) < 4 and any(w[0].isupper() for w in s.split()[1:2]):
            fact_sentences.append(s)
        if len(fact_sentences) >= 4:
            break

    # Fallback: use subheadline + first sentences
    if len(fact_sentences) < 3:
        if subheadline:
            fact_sentences.insert(0, subheadline)
        for s in sentences[:10]:
            s = s.strip()
            if 30 < len(s) < 180 and s not in fact_sentences:
                fact_sentences.append(s)
            if len(fact_sentences) >= 4:
                break

    takeaways = fact_sentences[:4]

    # Build the post
    post = f"""{info['emoji']} {info['label']} | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

{headline.upper()}

{summary_text}

━━━━━━━━━━━━━━━━━━━━━━━━

Key Takeaways:

"""
    for t in takeaways:
        # Clean up the takeaway
        t = t.strip().rstrip('.')
        post += f"▸ {t}\n"

    post += f"""
━━━━━━━━━━━━━━━━━━━━━━━━

📰 Full story: thevideshi.com/articles/{info['slug']}

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""

    return post

def download_image(url):
    """Download image to temp file, return path or None."""
    try:
        r = requests.get(url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=15)
        r.raise_for_status()
        # Determine extension from content type
        ct = r.headers.get("content-type", "image/jpeg")
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

def update_supabase(article_id):
    """Mark article as tweeted in Supabase."""
    now = datetime.now(timezone.utc).isoformat()
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article_id}",
        headers=SUPABASE_HEADERS,
        json={"tweeted_at": now}
    )
    if r.status_code < 300:
        print(f"  Supabase updated (tweeted_at={now})")
    else:
        print(f"  Supabase update failed: {r.status_code} {r.text}")

def log_tweet(tweet_id, article):
    """Log tweet ID locally."""
    log_path = os.path.expanduser("~/workspace/the-videshi-news/pipeline/tweet-log.json")
    tweet_log = {}
    if os.path.exists(log_path):
        with open(log_path) as f:
            tweet_log = json.load(f)
    tweet_log[str(tweet_id)] = {
        "article_id": article["id"],
        "slug": article["slug"],
        "posted_at": datetime.now(timezone.utc).isoformat() + "Z"
    }
    with open(log_path, 'w') as f:
        json.dump(tweet_log, f, indent=2)
    print(f"  Logged to tweet-log.json")

# --- Post articles ---
posted = 0
errors = []
tweet_urls = []

for i, article in enumerate(selected):
    print(f"\n--- Article {i+1}/{len(selected)} ---")
    print(f"  Headline: {article['headline']}")
    print(f"  Slug: {article['slug']}")
    print(f"  Category: {article.get('category', 'unknown')}")

    try:
        info = compose_post(article)
        post_text = write_post_text(info)

        print(f"  Post length: {len(post_text)} chars")

        # Download and upload image
        media_ids = None
        img_path = None
        if article.get("image_url"):
            print(f"  Downloading image: {article['image_url'][:80]}...")
            img_path = download_image(article["image_url"])
            if img_path:
                try:
                    media = api_v1.media_upload(filename=img_path)
                    media_ids = [media.media_id]
                    print(f"  Image uploaded (media_id={media.media_id})")
                except Exception as e:
                    print(f"  Image upload to X failed: {e}")
                    media_ids = None

        # Post tweet
        kwargs = {"text": post_text}
        if media_ids:
            kwargs["media_ids"] = media_ids

        response = client.create_tweet(**kwargs)
        tweet_id = response.data["id"]
        tweet_url = f"https://x.com/thevideshi/status/{tweet_id}"
        print(f"  ✅ Posted: {tweet_url}")
        tweet_urls.append(tweet_url)

        # Update Supabase + log
        update_supabase(article["id"])
        log_tweet(tweet_id, article)
        posted += 1

        # Cleanup temp image
        if img_path and os.path.exists(img_path):
            os.unlink(img_path)

        # Wait between posts
        if i < len(selected) - 1:
            print("  Waiting 30s before next post...")
            time.sleep(30)

    except Exception as e:
        errors.append({"slug": article["slug"], "error": str(e)})
        print(f"  ❌ Error: {e}")
        if img_path and os.path.exists(img_path):
            os.unlink(img_path)

# --- Summary ---
print(f"\n{'='*50}")
print(f"SUMMARY: Posted {posted}/{len(selected)} articles to X")
if tweet_urls:
    print("Tweet URLs:")
    for url in tweet_urls:
        print(f"  {url}")
if errors:
    print(f"Errors ({len(errors)}):")
    for e in errors:
        print(f"  {e['slug']}: {e['error']}")
