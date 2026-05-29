#!/usr/bin/env python3
"""Auto-post recent Videshi articles to X (@thevideshi) as long-form posts with images."""

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
            if not line or line.startswith('#') or '=' not in line:
                continue
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
    "markets": "MARKETS",
    "markets-finance": "MARKETS & FINANCE",
    "technology": "TECHNOLOGY",
    "sports": "SPORTS",
    "entertainment": "ENTERTAINMENT",
    "food": "FOOD",
}

TWEET_LOG_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/tweet-log.json")


def fetch_untweeted_articles():
    """Fetch up to 20 recent published articles not yet tweeted."""
    url = (
        f"{SUPABASE_URL}/rest/v1/p2_articles"
        f"?status=eq.published&tweeted_at=is.null&order=published_at.desc&limit=20"
        f"&select=id,slug,headline,subheadline,category,tags,image_url,body"
    )
    resp = requests.get(url, headers=SB_HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.json()


def extract_body_text(body_md):
    """Extract plain text from markdown body for summarization context. Truncate to ~3000 chars."""
    if not body_md:
        return ""
    # Strip markdown images, links formatting but keep text
    import re
    text = re.sub(r'!\[.*?\]\(.*?\)', '', body_md)  # images
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)  # links -> text
    text = re.sub(r'#{1,6}\s*', '', text)  # headers
    text = re.sub(r'\*{1,2}([^*]+)\*{1,2}', r'\1', text)  # bold/italic
    text = re.sub(r'\n{3,}', '\n\n', text)  # excess newlines
    return text[:3000].strip()


def compose_post(article):
    """Compose a long-form X post from an article."""
    cat = (article.get("category") or "news").lower()
    emoji = CATEGORY_EMOJI.get(cat, "📰")
    label = CATEGORY_LABEL.get(cat, cat.upper())
    headline = article.get("headline", "")
    subheadline = article.get("subheadline", "")
    slug = article.get("slug", "")
    body_text = extract_body_text(article.get("body", ""))

    # Build a prompt-style approach: we'll craft the post directly from available content
    # Extract key info from body
    lines = body_text.split('\n')
    # Get substantial paragraphs
    paras = [l.strip() for l in lines if len(l.strip()) > 60]

    # Build summary from first few substantial paragraphs
    summary_source = '\n'.join(paras[:8]) if paras else subheadline or headline

    # Create a punchy rewritten headline
    punchy_headline = headline.upper() if len(headline) < 80 else headline.title()

    # Build 2-3 paragraph summary
    # Take first ~3 substantive paragraphs and condense
    summary_paras = []
    char_count = 0
    for p in paras:
        if char_count > 600:
            break
        # Clean up the paragraph
        clean = p.strip()
        if len(clean) > 40:
            summary_paras.append(clean)
            char_count += len(clean)

    if not summary_paras and subheadline:
        summary_paras = [subheadline]

    summary_text = '\n\n'.join(summary_paras[:3])

    # Extract key takeaways - look for numbers, names, concrete facts
    takeaways = []
    for p in paras:
        if any(c.isdigit() for c in p) or any(w in p.lower() for w in ['percent', 'million', 'billion', 'announced', 'according', 'expected', 'first', 'largest']):
            # Truncate to ~120 chars for bullet points
            ta = p[:120].strip()
            if len(ta) > 40:
                if not ta.endswith('.'):
                    # Try to end at a sentence or word boundary
                    last_period = ta.rfind('.')
                    last_space = ta.rfind(' ')
                    if last_period > 60:
                        ta = ta[:last_period+1]
                    elif last_space > 60:
                        ta = ta[:last_space]
                takeaways.append(ta)
        if len(takeaways) >= 4:
            break

    # If we didn't get enough takeaways, grab from subheadline and early paras
    if len(takeaways) < 3:
        if subheadline and subheadline not in '\n'.join(takeaways):
            takeaways.insert(0, subheadline[:120])
        for p in paras[:6]:
            if p[:120] not in '\n'.join(takeaways) and len(p) > 40:
                takeaways.append(p[:120])
            if len(takeaways) >= 4:
                break

    takeaways = takeaways[:4]

    # Compose the post
    post = f"""{emoji} {label} | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

{punchy_headline}

{summary_text}

━━━━━━━━━━━━━━━━━━━━━━━━

Key Takeaways:

"""
    for ta in takeaways:
        post += f"▸ {ta}\n"

    post += f"""
━━━━━━━━━━━━━━━━━━━━━━━━

📰 Full story: thevideshi.com/articles/{slug}

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""

    # Ensure under 4000 chars
    if len(post) > 3900:
        # Trim summary
        post = post[:3900]
        last_nl = post.rfind('\n')
        if last_nl > 3000:
            post = post[:last_nl]

    return post


def download_image(image_url):
    """Download image to temp file, return path or None."""
    try:
        resp = requests.get(image_url, timeout=15)
        resp.raise_for_status()
        content_type = resp.headers.get('content-type', 'image/jpeg')
        ext = '.jpg'
        if 'png' in content_type:
            ext = '.png'
        elif 'webp' in content_type:
            ext = '.webp'
        elif 'gif' in content_type:
            ext = '.gif'

        tmp = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
        tmp.write(resp.content)
        tmp.close()
        return tmp.name
    except Exception as e:
        print(f"  ⚠️ Image download failed: {e}")
        return None


def update_supabase(article_id):
    """Mark article as tweeted in Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article_id}"
    now = datetime.now(timezone.utc).isoformat()
    resp = requests.patch(url, headers=SB_HEADERS, json={"tweeted_at": now}, timeout=15)
    if resp.status_code < 300:
        print(f"  ✅ Supabase updated (tweeted_at)")
    else:
        print(f"  ⚠️ Supabase update failed: {resp.status_code} {resp.text}")


def log_tweet(tweet_id, article):
    """Log tweet ID locally for future management."""
    tweet_log = {}
    if os.path.exists(TWEET_LOG_PATH):
        with open(TWEET_LOG_PATH) as f:
            tweet_log = json.load(f)

    tweet_log[str(tweet_id)] = {
        "article_id": article["id"],
        "slug": article["slug"],
        "posted_at": datetime.now(timezone.utc).isoformat() + "Z",
    }

    os.makedirs(os.path.dirname(TWEET_LOG_PATH), exist_ok=True)
    with open(TWEET_LOG_PATH, "w") as f:
        json.dump(tweet_log, f, indent=2)


def main():
    print("=" * 60)
    print(f"🐦 Videshi X Auto-Poster — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 60)

    # Fetch articles
    articles = fetch_untweeted_articles()
    print(f"\n📦 Found {len(articles)} untweeted published articles")

    if not articles:
        print("Nothing to post. Exiting.")
        return

    # Filter: skip articles with no image_url
    with_images = [a for a in articles if a.get("image_url")]
    without_images = len(articles) - len(with_images)
    if without_images:
        print(f"  ⏭️ Skipping {without_images} articles with no image")

    # Pick up to 4, newest first (already ordered by published_at desc)
    to_post = with_images[:4]
    print(f"  📝 Will post {len(to_post)} articles\n")

    if not to_post:
        print("No eligible articles to post. Exiting.")
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
    errors = 0
    results = []

    for i, article in enumerate(to_post):
        slug = article.get("slug", "unknown")
        headline = article.get("headline", "No headline")
        print(f"{'─' * 50}")
        print(f"[{i+1}/{len(to_post)}] {headline}")
        print(f"  slug: {slug}")
        print(f"  category: {article.get('category', 'unknown')}")

        try:
            # Compose post
            post_text = compose_post(article)
            print(f"  📝 Post length: {len(post_text)} chars")

            # Download and upload image
            media_ids = None
            image_url = article.get("image_url", "")
            tmp_path = None
            if image_url:
                tmp_path = download_image(image_url)
                if tmp_path:
                    try:
                        media = api_v1.media_upload(filename=tmp_path)
                        media_ids = [media.media_id]
                        print(f"  🖼️ Image uploaded (media_id: {media.media_id})")
                    except Exception as e:
                        print(f"  ⚠️ Image upload failed: {e}")
                        media_ids = None

            # Post tweet
            kwargs = {"text": post_text}
            if media_ids:
                kwargs["media_ids"] = media_ids

            response = client.create_tweet(**kwargs)
            tweet_id = response.data["id"]
            tweet_url = f"https://x.com/thevideshi/status/{tweet_id}"
            print(f"  🐦 Posted! {tweet_url}")

            # Update Supabase
            update_supabase(article["id"])

            # Log tweet
            log_tweet(tweet_id, article)

            results.append({"slug": slug, "tweet_url": tweet_url, "success": True})
            posted += 1

            # Clean up temp file
            if tmp_path and os.path.exists(tmp_path):
                os.unlink(tmp_path)

            # Wait between posts
            if i < len(to_post) - 1:
                print(f"  ⏳ Waiting 30s before next post...")
                time.sleep(30)

        except Exception as e:
            print(f"  ❌ Error: {e}")
            errors += 1
            results.append({"slug": slug, "error": str(e), "success": False})
            if tmp_path and os.path.exists(tmp_path):
                os.unlink(tmp_path)

    # Summary
    print(f"\n{'=' * 60}")
    print(f"📊 SUMMARY")
    print(f"  ✅ Posted: {posted}")
    print(f"  ❌ Errors: {errors}")
    print(f"{'=' * 60}")
    for r in results:
        if r["success"]:
            print(f"  ✅ {r['slug']} → {r['tweet_url']}")
        else:
            print(f"  ❌ {r['slug']} → {r['error']}")


if __name__ == "__main__":
    main()
