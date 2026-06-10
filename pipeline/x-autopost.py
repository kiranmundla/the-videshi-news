#!/usr/bin/env python3
"""Post recently published Videshi articles to X as long-form posts with images."""

import json
import os
import re
import tempfile
import time
from datetime import datetime

import requests
import tweepy

# --- Config ---
SUPABASE_URL = "https://lboecaekpynbpyijrbfz.supabase.co"
MAX_POSTS = 4
POST_DELAY = 30  # seconds between posts
MAX_POST_CHARS = 4000
TARGET_CHARS = (800, 2000)

# --- Load keys ---
def load_env(path):
    env = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.startswith('export '):
                line = line[7:]
            if '=' in line:
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

# Category emoji mapping
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

def supabase_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
    }

def fetch_untweeted_articles():
    resp = requests.get(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        params={
            "status": "eq.published",
            "tweeted_at": "is.null",
            "order": "published_at.desc",
            "limit": "20",
            "select": "id,slug,headline,subheadline,category,tags,image_url,body",
        },
        headers=supabase_headers(),
    )
    resp.raise_for_status()
    return resp.json()

def strip_markdown(text):
    """Strip markdown formatting to get plain text for summarization."""
    if not text:
        return ""
    # Remove images
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    # Remove links but keep text
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    # Remove headers
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    # Remove bold/italic
    text = re.sub(r'\*{1,3}([^*]+)\*{1,3}', r'\1', text)
    text = re.sub(r'_{1,3}([^_]+)_{1,3}', r'\1', text)
    # Remove blockquotes
    text = re.sub(r'^>\s+', '', text, flags=re.MULTILINE)
    # Remove horizontal rules
    text = re.sub(r'^[-*_]{3,}\s*$', '', text, flags=re.MULTILINE)
    # Collapse whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def compose_post(article):
    """Compose a long-form X post from article data."""
    cat = article.get("category", "news")
    emoji = CATEGORY_EMOJI.get(cat, "📰")
    label = CATEGORY_LABEL.get(cat, cat.upper())
    headline = article.get("headline", "")
    subheadline = article.get("subheadline", "")
    slug = article.get("slug", "")
    body = strip_markdown(article.get("body", ""))

    # Extract key paragraphs from body for summary
    paragraphs = [p.strip() for p in body.split('\n\n') if p.strip() and len(p.strip()) > 50]

    # Build summary: 2-3 paragraphs, 150-250 words
    summary_parts = []
    word_count = 0
    for p in paragraphs[:6]:  # scan first 6 paragraphs
        words = p.split()
        if word_count + len(words) > 250:
            # Take partial if we need more
            if word_count < 100:
                remaining = 200 - word_count
                summary_parts.append(' '.join(words[:remaining]) + '...')
                word_count += remaining
            break
        summary_parts.append(p)
        word_count += len(words)
        if word_count >= 150:
            break

    summary = '\n\n'.join(summary_parts) if summary_parts else subheadline

    # Extract key takeaways from body
    takeaways = []
    # Look for bullet points, numbers, key facts
    sentences = re.split(r'[.!?]\s+', body)
    # Prioritize sentences with numbers, names, or strong facts
    fact_sentences = []
    for s in sentences:
        s = s.strip()
        if len(s) < 20 or len(s) > 200:
            continue
        # Prefer sentences with numbers, percentages, dollar amounts
        if re.search(r'\d+', s) and len(s) > 30:
            fact_sentences.append(s)
        elif any(word in s.lower() for word in ['first', 'largest', 'billion', 'million', 'percent', 'announced', 'launched', 'approved', 'rejected']):
            fact_sentences.append(s)

    # Deduplicate and pick top 4
    seen = set()
    for s in fact_sentences:
        key = s[:40].lower()
        if key not in seen:
            seen.add(key)
            takeaways.append(s.rstrip('.') if not s.endswith('...') else s)
        if len(takeaways) >= 4:
            break

    # If not enough from facts, use subheadline
    if len(takeaways) < 3 and subheadline:
        for part in subheadline.split('. '):
            part = part.strip().rstrip('.')
            if part and len(part) > 15 and part not in takeaways:
                takeaways.append(part)
            if len(takeaways) >= 4:
                break

    # Ensure at least 3
    if len(takeaways) < 3:
        for p in paragraphs[1:4]:
            first_sent = re.split(r'[.!?]\s+', p)[0].strip().rstrip('.')
            if first_sent and len(first_sent) > 20 and first_sent not in takeaways:
                takeaways.append(first_sent)
            if len(takeaways) >= 3:
                break

    takeaways = takeaways[:4]
    takeaway_text = '\n'.join(f'▸ {t}' for t in takeaways)

    # Make headline punchier - Title Case
    punchy_headline = headline.strip()
    # Remove trailing period
    if punchy_headline.endswith('.'):
        punchy_headline = punchy_headline[:-1]

    post = f"""{emoji} {label} | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

{punchy_headline}

{summary}

━━━━━━━━━━━━━━━━━━━━━━━━

Key Takeaways:

{takeaway_text}

━━━━━━━━━━━━━━━━━━━━━━━━

📰 Full story: thevideshi.com/articles/{slug}

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""

    # Trim if over limit
    if len(post) > MAX_POST_CHARS:
        # Shorten summary
        words = summary.split()
        while len(post) > MAX_POST_CHARS and len(words) > 50:
            words = words[:-10]
            summary = ' '.join(words) + '...'
            post = f"""{emoji} {label} | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

{punchy_headline}

{summary}

━━━━━━━━━━━━━━━━━━━━━━━━

Key Takeaways:

{takeaway_text}

━━━━━━━━━━━━━━━━━━━━━━━━

📰 Full story: thevideshi.com/articles/{slug}

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""

    return post

def download_image(url):
    """Download image to temp file, return path or None."""
    if not url:
        return None
    try:
        resp = requests.get(
            url,
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=15,
            stream=True,
        )
        resp.raise_for_status()
        # Determine extension
        ct = resp.headers.get("Content-Type", "")
        ext = ".jpg"
        if "png" in ct:
            ext = ".png"
        elif "webp" in ct:
            ext = ".webp"
        elif "gif" in ct:
            ext = ".gif"

        tmp = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
        for chunk in resp.iter_content(8192):
            tmp.write(chunk)
        tmp.close()

        # Check file size > 0
        if os.path.getsize(tmp.name) < 100:
            os.unlink(tmp.name)
            return None

        return tmp.name
    except Exception as e:
        print(f"  ⚠️  Image download failed: {e}")
        return None

def update_supabase_tweeted(article_id):
    """Mark article as tweeted in Supabase."""
    now = datetime.utcnow().isoformat() + "Z"
    resp = requests.patch(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        params={"id": f"eq.{article_id}"},
        json={"tweeted_at": now},
        headers=supabase_headers(),
    )
    if resp.status_code < 300:
        print(f"  ✅ Supabase updated (tweeted_at={now})")
    else:
        print(f"  ⚠️  Supabase update failed: {resp.status_code} {resp.text}")

def log_tweet(tweet_id, article):
    """Log tweet to local JSON file."""
    log_path = os.path.expanduser(
        "~/workspace/the-videshi-news/pipeline/tweet-log.json"
    )
    tweet_log = {}
    if os.path.exists(log_path):
        with open(log_path) as f:
            tweet_log = json.load(f)

    tweet_log[str(tweet_id)] = {
        "article_id": article["id"],
        "slug": article["slug"],
        "posted_at": datetime.utcnow().isoformat() + "Z",
    }

    with open(log_path, "w") as f:
        json.dump(tweet_log, f, indent=2)
    print(f"  ✅ Logged to tweet-log.json")

def main():
    print("=" * 60)
    print("The Videshi → X Autopost")
    print(f"Run time: {datetime.utcnow().isoformat()}Z")
    print("=" * 60)

    # Fetch articles
    articles = fetch_untweeted_articles()
    print(f"\n📋 Found {len(articles)} untweeted published articles")

    # Filter: must have image_url
    eligible = [a for a in articles if a.get("image_url")]
    print(f"📷 {len(eligible)} have images (eligible for posting)")

    # Pick top 4
    to_post = eligible[:MAX_POSTS]
    print(f"📝 Will post {len(to_post)} articles\n")

    if not to_post:
        print("Nothing to post. Done.")
        return

    # Init Twitter clients
    client = tweepy.Client(
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET,
    )

    auth = tweepy.OAuth1UserHandler(
        CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET
    )
    api_v1 = tweepy.API(auth)

    posted = 0
    errors = []
    tweet_urls = []

    for i, article in enumerate(to_post):
        print(f"\n{'─' * 50}")
        print(f"[{i+1}/{len(to_post)}] {article['headline'][:80]}")
        print(f"  Category: {article['category']} | Slug: {article['slug']}")

        # Compose post
        post_text = compose_post(article)
        print(f"  Post length: {len(post_text)} chars")

        # Download and upload image
        media_ids = None
        img_path = download_image(article.get("image_url"))
        if img_path:
            try:
                media = api_v1.media_upload(filename=img_path)
                media_ids = [media.media_id]
                print(f"  📷 Image uploaded (media_id={media.media_id})")
            except Exception as e:
                print(f"  ⚠️  Image upload failed: {e}")
            finally:
                try:
                    os.unlink(img_path)
                except:
                    pass
        else:
            print("  📷 No image (posting without)")

        # Post tweet
        try:
            kwargs = {"text": post_text}
            if media_ids:
                kwargs["media_ids"] = media_ids

            response = client.create_tweet(**kwargs)
            tweet_id = response.data["id"]
            tweet_url = f"https://x.com/thevideshi/status/{tweet_id}"
            print(f"  🐦 Posted! {tweet_url}")
            tweet_urls.append(tweet_url)

            # Update Supabase
            update_supabase_tweeted(article["id"])

            # Log locally
            log_tweet(tweet_id, article)

            posted += 1

        except Exception as e:
            error_msg = f"Tweet failed for {article['slug']}: {e}"
            print(f"  ❌ {error_msg}")
            errors.append(error_msg)

        # Wait between posts
        if i < len(to_post) - 1:
            print(f"  ⏳ Waiting {POST_DELAY}s...")
            time.sleep(POST_DELAY)

    # Summary
    print(f"\n{'=' * 60}")
    print(f"✅ SUMMARY: Posted {posted}/{len(to_post)} articles to X")
    if tweet_urls:
        print("\nTweet URLs:")
        for url in tweet_urls:
            print(f"  {url}")
    if errors:
        print(f"\n⚠️  Errors ({len(errors)}):")
        for e in errors:
            print(f"  {e}")
    print("=" * 60)

if __name__ == "__main__":
    main()
