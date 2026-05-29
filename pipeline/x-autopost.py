#!/usr/bin/env python3
"""Post recently published Videshi articles to X as long-form premium posts."""

import json
import os
import re
import sys
import tempfile
import time
from datetime import datetime

import requests
import tweepy

# --- Config ---
SUPABASE_URL = "https://lboecaekpynbpyijrbfz.supabase.co"
MAX_POSTS = 4
POST_DELAY = 30  # seconds between posts

# --- Load env ---
def load_env(path):
    env = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env

twitter_env = load_env("~/workspace/.env.twitter")
supabase_env = load_env("~/workspace/.env.supabase")

CONSUMER_KEY = twitter_env["TWITTER_CONSUMER_KEY"]
CONSUMER_SECRET = twitter_env["TWITTER_CONSUMER_SECRET"]
ACCESS_TOKEN = twitter_env["TWITTER_ACCESS_TOKEN"]
ACCESS_TOKEN_SECRET = twitter_env["TWITTER_ACCESS_TOKEN_SECRET"]
SUPABASE_KEY = supabase_env["SUPABASE_SERVICE_ROLE_KEY"]

# --- Category emoji mapping ---
CATEGORY_EMOJI = {
    "news": "🇮🇳",
    "immigration": "🛂",
    "nri-world": "🌏",
    "travel": "✈️",
    "lifestyle-health": "🧘",
    "lifestyle": "🧘",
    "markets-finance": "📈",
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
    "lifestyle-health": "LIFESTYLE & HEALTH",
    "lifestyle": "LIFESTYLE",
    "markets-finance": "MARKETS & FINANCE",
    "markets": "MARKETS",
    "technology": "TECHNOLOGY",
    "sports": "SPORTS",
    "entertainment": "ENTERTAINMENT",
    "food": "FOOD",
}


def strip_markdown(text):
    """Strip markdown formatting to plain text for X post."""
    if not text:
        return ""
    # Remove images
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    # Remove links but keep text
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    # Remove headers
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    # Remove bold/italic markers
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    text = re.sub(r'__([^_]+)__', r'\1', text)
    # Remove blockquotes
    text = re.sub(r'^>\s+', '', text, flags=re.MULTILINE)
    # Remove horizontal rules
    text = re.sub(r'^[-*_]{3,}\s*$', '', text, flags=re.MULTILINE)
    # Clean up extra whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def extract_key_points(body_text):
    """Extract key factual points from article body for takeaways."""
    sentences = re.split(r'(?<=[.!?])\s+', body_text)
    # Filter for sentences with numbers, names, or strong facts
    fact_sentences = []
    for s in sentences:
        s = s.strip()
        if len(s) < 20 or len(s) > 200:
            continue
        # Prefer sentences with numbers, percentages, dollar amounts, dates
        if re.search(r'(\d+[\.,]?\d*\s*(%|percent|billion|million|crore|lakh)|\$\d|₹\d)', s, re.I):
            fact_sentences.append(s)
        elif re.search(r'(first|largest|record|historic|unprecedented|biggest|highest|lowest)', s, re.I):
            fact_sentences.append(s)
    return fact_sentences[:6]  # Return up to 6 candidates


def compose_post(article):
    """Compose a long-form X premium post from article data."""
    cat = article.get("category", "news")
    emoji = CATEGORY_EMOJI.get(cat, "📰")
    label = CATEGORY_LABEL.get(cat, cat.upper())
    headline = article["headline"]
    subheadline = article.get("subheadline", "")
    slug = article["slug"]
    body = strip_markdown(article.get("body", "") or "")

    # Build summary paragraphs from body
    paragraphs = [p.strip() for p in body.split('\n\n') if p.strip() and len(p.strip()) > 50]
    
    # Take first 3-4 substantial paragraphs for the summary
    summary_paras = []
    total_words = 0
    for p in paragraphs[:6]:
        words = len(p.split())
        if total_words + words > 250:
            break
        summary_paras.append(p)
        total_words += words
    
    # If we got very little, just use what we have
    if total_words < 50 and paragraphs:
        summary_paras = paragraphs[:2]

    summary = "\n\n".join(summary_paras)

    # Extract key takeaways
    key_facts = extract_key_points(body)
    if not key_facts and subheadline:
        key_facts = [subheadline]

    # Build takeaways section
    takeaways = ""
    if key_facts:
        takeaway_lines = []
        for fact in key_facts[:4]:
            # Trim to a reasonable length
            if len(fact) > 150:
                fact = fact[:147] + "..."
            takeaway_lines.append(f"▸ {fact}")
        takeaways = "\n".join(takeaway_lines)

    # Compose the full post
    post = f"""{emoji} {label} | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

{headline}

{summary}"""

    if takeaways:
        post += f"""

━━━━━━━━━━━━━━━━━━━━━━━━

Key Takeaways:

{takeaways}"""

    post += f"""

━━━━━━━━━━━━━━━━━━━━━━━━

📰 Full story: thevideshi.com/articles/{slug}

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""

    # Trim if over 4000 chars
    if len(post) > 3900:
        # Shorten summary
        short_summary = "\n\n".join(summary_paras[:2])
        post = f"""{emoji} {label} | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

{headline}

{short_summary}"""
        if takeaways:
            post += f"""

━━━━━━━━━━━━━━━━━━━━━━━━

Key Takeaways:

{takeaways}"""
        post += f"""

━━━━━━━━━━━━━━━━━━━━━━━━

📰 Full story: thevideshi.com/articles/{slug}

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""

    return post[:4000]


def download_image(url):
    """Download image to a temp file, return path or None."""
    try:
        r = requests.get(url, timeout=15, stream=True)
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
        for chunk in r.iter_content(8192):
            tmp.write(chunk)
        tmp.close()
        # Check file size
        fsize = os.path.getsize(tmp.name)
        if fsize < 1000:
            print(f"  ⚠ Image too small ({fsize} bytes), skipping image")
            os.unlink(tmp.name)
            return None
        return tmp.name
    except Exception as e:
        print(f"  ⚠ Image download failed: {e}")
        return None


def main():
    # --- Fetch articles ---
    sb_headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
    }

    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        params={
            "status": "eq.published",
            "tweeted_at": "is.null",
            "order": "published_at.desc",
            "limit": "20",
            "select": "id,slug,headline,subheadline,category,tags,image_url,body",
        },
        headers=sb_headers,
    )
    r.raise_for_status()
    articles = r.json()
    print(f"Found {len(articles)} untweeted published articles")

    # Filter to those with images, pick up to MAX_POSTS
    candidates = [a for a in articles if a.get("image_url")]
    to_post = candidates[:MAX_POSTS]
    print(f"Selected {len(to_post)} articles to post\n")

    if not to_post:
        print("No articles to post.")
        return

    # --- Set up tweepy ---
    client = tweepy.Client(
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET,
    )

    auth = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api_v1 = tweepy.API(auth)

    # --- Tweet log ---
    log_path = os.path.expanduser("~/workspace/the-videshi-news/pipeline/tweet-log.json")
    tweet_log = {}
    if os.path.exists(log_path):
        with open(log_path) as f:
            tweet_log = json.load(f)

    posted = 0
    errors = []
    results = []

    for i, article in enumerate(to_post):
        print(f"--- Article {i+1}/{len(to_post)} ---")
        print(f"  [{article['category']}] {article['headline'][:80]}")
        print(f"  slug: {article['slug']}")

        # Compose long-form post
        post_text = compose_post(article)
        print(f"  Post length: {len(post_text)} chars")

        # Download and upload image
        media_ids = None
        img_path = None
        if article.get("image_url"):
            img_path = download_image(article["image_url"])
            if img_path:
                try:
                    media = api_v1.media_upload(filename=img_path)
                    media_ids = [media.media_id]
                    print(f"  ✓ Image uploaded (media_id: {media.media_id})")
                except Exception as e:
                    print(f"  ⚠ Image upload failed: {e}")
                    media_ids = None
                finally:
                    if img_path and os.path.exists(img_path):
                        os.unlink(img_path)

        # Post tweet
        try:
            kwargs = {"text": post_text}
            if media_ids:
                kwargs["media_ids"] = media_ids
            resp = client.create_tweet(**kwargs)
            tweet_id = resp.data["id"]
            tweet_url = f"https://x.com/thevideshi/status/{tweet_id}"
            print(f"  ✓ Posted! {tweet_url}")
            results.append((article["headline"][:60], tweet_url))

            # Update Supabase
            now = datetime.utcnow().isoformat() + "Z"
            patch_r = requests.patch(
                f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article['id']}",
                json={"tweeted_at": now},
                headers={**sb_headers, "Content-Type": "application/json", "Prefer": "return=minimal"},
            )
            if patch_r.status_code < 300:
                print(f"  ✓ Supabase updated (tweeted_at={now})")
            else:
                print(f"  ⚠ Supabase update failed: {patch_r.status_code} {patch_r.text}")

            # Log tweet
            tweet_log[str(tweet_id)] = {
                "article_id": article["id"],
                "slug": article["slug"],
                "posted_at": now,
            }
            with open(log_path, "w") as f:
                json.dump(tweet_log, f, indent=2)

            posted += 1

        except Exception as e:
            err_msg = str(e)
            print(f"  ✗ Tweet failed: {err_msg}")
            errors.append((article["slug"], err_msg))

        # Delay between posts
        if i < len(to_post) - 1:
            print(f"  Waiting {POST_DELAY}s...")
            time.sleep(POST_DELAY)

    # --- Summary ---
    print(f"\n{'='*50}")
    print(f"SUMMARY: Posted {posted}/{len(to_post)} articles")
    for title, url in results:
        print(f"  ✓ {title}... → {url}")
    if errors:
        print(f"ERRORS ({len(errors)}):")
        for slug, err in errors:
            print(f"  ✗ {slug}: {err}")


if __name__ == "__main__":
    main()
