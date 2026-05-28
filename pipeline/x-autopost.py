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
supabase_env = load_env("~/workspace/.env.supabase")

CONSUMER_KEY = twitter_env["TWITTER_CONSUMER_KEY"]
CONSUMER_SECRET = twitter_env["TWITTER_CONSUMER_SECRET"]
ACCESS_TOKEN = twitter_env["TWITTER_ACCESS_TOKEN"]
ACCESS_TOKEN_SECRET = twitter_env["TWITTER_ACCESS_TOKEN_SECRET"]
SB_KEY = supabase_env["SUPABASE_SERVICE_ROLE_KEY"]

SB_HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json"
}

CATEGORY_EMOJI = {
    "news": "🇮🇳",
    "immigration": "🛂",
    "nri-world": "🌏",
    "travel": "✈️",
    "lifestyle": "🧘",
    "lifestyle-health": "🧘",
    "markets": "📈",
    "markets-finance": "📈",
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
    "lifestyle-health": "LIFESTYLE & HEALTH",
    "markets": "MARKETS & FINANCE",
    "markets-finance": "MARKETS & FINANCE",
    "technology": "TECHNOLOGY",
    "sports": "SPORTS",
    "entertainment": "ENTERTAINMENT",
    "food": "FOOD",
}

def fetch_untweeted_articles():
    url = (f"{SUPABASE_URL}/rest/v1/p2_articles"
           f"?status=eq.published&tweeted_at=is.null"
           f"&order=published_at.desc&limit=20"
           f"&select=id,slug,headline,subheadline,category,tags,image_url,body")
    r = requests.get(url, headers=SB_HEADERS, timeout=30)
    r.raise_for_status()
    return r.json()

def compose_post(article):
    cat = (article.get("category") or "news").lower()
    emoji = CATEGORY_EMOJI.get(cat, "📰")
    label = CATEGORY_LABEL.get(cat, cat.upper())
    headline = article.get("headline", "")
    subheadline = article.get("subheadline", "")
    body = article.get("body", "") or ""
    slug = article.get("slug", "")

    # Extract key content from body - first ~2000 chars for context
    body_text = body[:3000]

    # Build the summary from the article body
    # We'll create a concise journalistic summary
    summary_lines = []
    key_takeaways = []

    # Parse body for substance - split into paragraphs
    paragraphs = [p.strip() for p in body_text.split('\n') if p.strip()
                  and not p.strip().startswith('#')
                  and not p.strip().startswith('![')
                  and not p.strip().startswith('---')
                  and len(p.strip()) > 30]

    # Use subheadline + first few substantial paragraphs for summary
    summary_parts = []
    if subheadline:
        summary_parts.append(subheadline)
    for p in paragraphs[:5]:
        # Clean markdown formatting
        clean = p.replace('**', '').replace('*', '').replace('> ', '')
        if len(clean) > 30 and clean not in summary_parts:
            summary_parts.append(clean)
        if len(summary_parts) >= 3:
            break

    summary_text = '\n\n'.join(summary_parts[:3])

    # Extract key facts for takeaways
    for p in paragraphs:
        clean = p.replace('**', '').replace('*', '').replace('> ', '').strip()
        # Look for fact-dense sentences
        if any(c.isdigit() for c in clean) or '$' in clean or '%' in clean:
            if len(clean) < 200 and clean not in key_takeaways:
                key_takeaways.append(clean)
        if len(key_takeaways) >= 4:
            break

    # If we don't have enough takeaways from numbers, grab short impactful lines
    if len(key_takeaways) < 3:
        for p in paragraphs:
            clean = p.replace('**', '').replace('*', '').replace('> ', '').strip()
            if 30 < len(clean) < 150 and clean not in key_takeaways and clean not in summary_parts:
                key_takeaways.append(clean)
            if len(key_takeaways) >= 4:
                break

    # Build the post
    post = f"""{emoji} {label} | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

{headline.upper()}

{summary_text}

━━━━━━━━━━━━━━━━━━━━━━━━

Key Takeaways:

"""
    for t in key_takeaways[:4]:
        # Truncate long takeaways
        if len(t) > 150:
            t = t[:147] + "..."
        post += f"▸ {t}\n"

    post += f"""
━━━━━━━━━━━━━━━━━━━━━━━━

📰 Full story: thevideshi.com/articles/{slug}

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""

    # Trim if over 4000 chars
    if len(post) > 3900:
        # Shorten summary
        summary_text = '\n\n'.join(summary_parts[:2])
        post = f"""{emoji} {label} | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

{headline.upper()}

{summary_text}

━━━━━━━━━━━━━━━━━━━━━━━━

Key Takeaways:

"""
        for t in key_takeaways[:3]:
            if len(t) > 120:
                t = t[:117] + "..."
            post += f"▸ {t}\n"
        post += f"""
━━━━━━━━━━━━━━━━━━━━━━━━

📰 Full story: thevideshi.com/articles/{slug}

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""

    return post

def download_image(url):
    """Download image to temp file, return path or None."""
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        content_type = r.headers.get('content-type', 'image/jpeg')
        ext = '.jpg'
        if 'png' in content_type:
            ext = '.png'
        elif 'webp' in content_type:
            ext = '.webp'
        elif 'gif' in content_type:
            ext = '.gif'
        tmp = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
        tmp.write(r.content)
        tmp.close()
        return tmp.name
    except Exception as e:
        print(f"  ⚠️ Image download failed: {e}")
        return None

def mark_tweeted(article_id):
    now = datetime.utcnow().isoformat() + "Z"
    url = f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article_id}"
    r = requests.patch(url, headers=SB_HEADERS, json={"tweeted_at": now}, timeout=15)
    r.raise_for_status()

def log_tweet(tweet_id, article):
    log_path = os.path.expanduser("~/workspace/the-videshi-news/pipeline/tweet-log.json")
    tweet_log = {}
    if os.path.exists(log_path):
        with open(log_path) as f:
            tweet_log = json.load(f)
    tweet_log[str(tweet_id)] = {
        "article_id": article["id"],
        "slug": article["slug"],
        "posted_at": datetime.utcnow().isoformat() + "Z"
    }
    with open(log_path, 'w') as f:
        json.dump(tweet_log, f, indent=2)

def main():
    print("🐦 Videshi X Auto-Poster")
    print(f"⏰ {datetime.utcnow().isoformat()}Z\n")

    # Fetch articles
    articles = fetch_untweeted_articles()
    print(f"📋 Found {len(articles)} untweeted articles")

    # Filter: must have image_url
    eligible = [a for a in articles if a.get("image_url")]
    print(f"🖼️ {len(eligible)} have images")

    if not eligible:
        print("✅ Nothing to post — all caught up!")
        return

    # Take up to 4
    to_post = eligible[:4]
    print(f"📝 Will post {len(to_post)} articles\n")

    # Set up tweepy
    client = tweepy.Client(
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET
    )
    auth = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api_v1 = tweepy.API(auth)

    posted = 0
    errors = []

    for i, article in enumerate(to_post):
        slug = article.get("slug", "???")
        headline = article.get("headline", "???")
        print(f"--- [{i+1}/{len(to_post)}] {headline[:80]} ---")

        try:
            # Compose post
            post_text = compose_post(article)
            print(f"  📏 Post length: {len(post_text)} chars")

            # Handle image
            media_id = None
            img_path = None
            if article.get("image_url"):
                img_path = download_image(article["image_url"])
                if img_path:
                    try:
                        media = api_v1.media_upload(filename=img_path)
                        media_id = media.media_id
                        print(f"  🖼️ Image uploaded (media_id: {media_id})")
                    except Exception as e:
                        print(f"  ⚠️ Image upload failed: {e}")
                        media_id = None

            # Post tweet
            kwargs = {"text": post_text}
            if media_id:
                kwargs["media_ids"] = [media_id]

            response = client.create_tweet(**kwargs)
            tweet_id = response.data["id"]
            tweet_url = f"https://x.com/thevideshi/status/{tweet_id}"
            print(f"  ✅ Posted: {tweet_url}")

            # Update Supabase
            mark_tweeted(article["id"])
            print(f"  📝 Marked tweeted_at in Supabase")

            # Log tweet
            log_tweet(tweet_id, article)
            print(f"  📋 Logged to tweet-log.json")

            posted += 1

            # Clean up temp image
            if img_path and os.path.exists(img_path):
                os.unlink(img_path)

            # Wait between posts
            if i < len(to_post) - 1:
                print(f"  ⏳ Waiting 30s before next post...")
                time.sleep(30)

        except Exception as e:
            errors.append({"slug": slug, "error": str(e)})
            print(f"  ❌ ERROR: {e}")
            if img_path and os.path.exists(img_path):
                os.unlink(img_path)

    # Summary
    print(f"\n{'='*50}")
    print(f"📊 SUMMARY: {posted}/{len(to_post)} posted successfully")
    if errors:
        print(f"❌ {len(errors)} errors:")
        for e in errors:
            print(f"   - {e['slug']}: {e['error']}")
    print("Done!")

if __name__ == "__main__":
    main()
