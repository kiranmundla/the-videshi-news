#!/usr/bin/env python3
"""Post recently published Videshi articles to X (@thevideshi) as long-form posts with images."""

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

# Load env files
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

CATEGORY_LABELS = {
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

# --- Supabase helpers ---
SB_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}

def fetch_untweeted_articles():
    url = (
        f"{SUPABASE_URL}/rest/v1/p2_articles"
        "?status=eq.published&tweeted_at=is.null&order=published_at.desc&limit=20"
        "&select=id,slug,headline,subheadline,category,tags,image_url,body"
    )
    r = requests.get(url, headers=SB_HEADERS, timeout=30)
    r.raise_for_status()
    return r.json()

def mark_tweeted(article_id):
    url = f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article_id}"
    ts = datetime.utcnow().isoformat() + "Z"
    r = requests.patch(url, headers=SB_HEADERS, json={"tweeted_at": ts}, timeout=15)
    r.raise_for_status()
    return ts

# --- Tweet log ---
LOG_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/tweet-log.json")

def log_tweet(tweet_id, article):
    tweet_log = {}
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH) as f:
            tweet_log = json.load(f)
    tweet_log[str(tweet_id)] = {
        "article_id": article["id"],
        "slug": article["slug"],
        "posted_at": datetime.utcnow().isoformat() + "Z",
    }
    with open(LOG_PATH, "w") as f:
        json.dump(tweet_log, f, indent=2)

# --- Compose long-form post ---
def compose_post(article):
    cat = (article.get("category") or "news").lower()
    emoji = CATEGORY_EMOJI.get(cat, "📰")
    label = CATEGORY_LABELS.get(cat, cat.upper())
    slug = article.get("slug", "")
    headline = article.get("headline", "").strip()
    subheadline = article.get("subheadline", "").strip()
    body = article.get("body", "") or ""

    # Extract plain text from markdown body (strip markdown markers)
    body_clean = body
    for ch in ['#', '*', '`', '>', '---', '___']:
        body_clean = body_clean.replace(ch, '')
    # Collapse multiple newlines
    import re
    body_clean = re.sub(r'\n{3,}', '\n\n', body_clean).strip()

    # Truncate body for context (first ~2000 chars for summarization)
    body_excerpt = body_clean[:2000]

    # Build the summary paragraphs from body
    # Split body into paragraphs and pick the most informative ones
    paragraphs = [p.strip() for p in body_clean.split('\n\n') if len(p.strip()) > 40]

    # Build summary from first few meaningful paragraphs
    summary_parts = []
    char_count = 0
    for p in paragraphs[:6]:
        if char_count + len(p) > 600:
            break
        summary_parts.append(p)
        char_count += len(p)

    summary = '\n\n'.join(summary_parts) if summary_parts else (subheadline or headline)

    # Extract key facts for takeaways
    # Use subheadline + first few paragraphs for facts
    takeaway_source = f"{subheadline}\n{body_clean[:1500]}"
    # Pull sentences that have numbers, names, or concrete info
    sentences = re.split(r'[.!?]\s+', takeaway_source)
    takeaways = []
    for s in sentences:
        s = s.strip()
        if len(s) > 30 and len(s) < 200:
            # Prefer sentences with numbers, proper nouns, or concrete facts
            if any(c.isdigit() for c in s) or any(w[0].isupper() for w in s.split() if len(w) > 2):
                # Clean up and ensure proper ending
                s = s.rstrip('.,;:')
                if not s.endswith(('.', '!', '?')):
                    s += '.'
                takeaways.append(s)
                if len(takeaways) >= 4:
                    break

    # If we didn't get enough takeaways, add from meaningful sentences
    if len(takeaways) < 3:
        for s in sentences:
            s = s.strip()
            if len(s) > 40 and s not in takeaways:
                s = s.rstrip('.,;:')
                if not s.endswith(('.', '!', '?')):
                    s += '.'
                takeaways.append(s)
                if len(takeaways) >= 4:
                    break

    takeaways = takeaways[:4]

    # Build the post
    post = f"{emoji} {label} | The Videshi\n\n"
    post += "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    post += f"{headline.upper()}\n\n"
    post += f"{summary}\n\n"
    post += "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

    if takeaways:
        post += "Key Takeaways:\n\n"
        for t in takeaways:
            post += f"▸ {t}\n"
        post += "\n━━━━━━━━━━━━━━━━━━━━━━━━\n\n"

    post += f"📰 Full story: thevideshi.com/articles/{slug}\n\n"
    post += "The Videshi — Your daily source for Indian diaspora news\n"
    post += "🌐 thevideshi.com"

    # Ensure within 4000 chars
    if len(post) > 3900:
        # Trim summary
        over = len(post) - 3800
        summary = summary[:len(summary) - over - 3] + "..."
        # Rebuild
        post = f"{emoji} {label} | The Videshi\n\n"
        post += "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        post += f"{headline.upper()}\n\n"
        post += f"{summary}\n\n"
        post += "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        if takeaways:
            post += "Key Takeaways:\n\n"
            for t in takeaways[:3]:
                post += f"▸ {t}\n"
            post += "\n━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        post += f"📰 Full story: thevideshi.com/articles/{slug}\n\n"
        post += "The Videshi — Your daily source for Indian diaspora news\n"
        post += "🌐 thevideshi.com"

    return post

# --- Main ---
def main():
    print(f"[{datetime.utcnow().isoformat()}Z] Starting X autopost...")

    # Fetch articles
    articles = fetch_untweeted_articles()
    print(f"Found {len(articles)} untweeted articles")

    # Filter out articles without images, take up to 4
    articles_to_post = [a for a in articles if a.get("image_url")][:4]
    print(f"Selected {len(articles_to_post)} articles to post (with images)")

    if not articles_to_post:
        print("No articles to post. Done.")
        return

    # Init tweepy
    client = tweepy.Client(
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET,
    )

    auth = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api_v1 = tweepy.API(auth)

    posted = 0
    errors = []

    for i, article in enumerate(articles_to_post):
        slug = article.get("slug", "?")
        headline = article.get("headline", "?")
        print(f"\n--- Article {i+1}/{len(articles_to_post)}: {headline[:60]}... ---")

        try:
            # Compose post
            post_text = compose_post(article)
            print(f"Post length: {len(post_text)} chars")

            # Try to download and upload image
            media_id = None
            image_url = article.get("image_url", "")
            if image_url:
                try:
                    img_resp = requests.get(image_url, timeout=15)
                    img_resp.raise_for_status()
                    # Determine extension
                    ct = img_resp.headers.get("content-type", "image/jpeg")
                    ext = ".jpg"
                    if "png" in ct:
                        ext = ".png"
                    elif "webp" in ct:
                        ext = ".webp"

                    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
                        tmp.write(img_resp.content)
                        tmp_path = tmp.name

                    media = api_v1.media_upload(filename=tmp_path)
                    media_id = media.media_id
                    os.unlink(tmp_path)
                    print(f"Image uploaded: media_id={media_id}")
                except Exception as img_err:
                    print(f"Image upload failed: {img_err} — posting without image")
                    media_id = None

            # Post tweet
            tweet_kwargs = {"text": post_text}
            if media_id:
                tweet_kwargs["media_ids"] = [media_id]

            response = client.create_tweet(**tweet_kwargs)
            tweet_id = response.data["id"]
            tweet_url = f"https://x.com/thevideshi/status/{tweet_id}"
            print(f"✅ Posted: {tweet_url}")

            # Mark as tweeted in Supabase
            ts = mark_tweeted(article["id"])
            print(f"Marked tweeted_at={ts}")

            # Log tweet
            log_tweet(tweet_id, article)

            posted += 1

            # Wait between posts
            if i < len(articles_to_post) - 1:
                print("Waiting 30s...")
                time.sleep(30)

        except Exception as e:
            err_msg = f"Error posting '{slug}': {e}"
            print(f"❌ {err_msg}")
            errors.append(err_msg)

    # Summary
    print(f"\n{'='*50}")
    print(f"SUMMARY: Posted {posted}/{len(articles_to_post)} articles to X")
    if errors:
        print(f"Errors ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")
    print("Done.")

if __name__ == "__main__":
    main()
