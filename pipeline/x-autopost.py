#!/usr/bin/env python3
"""Post recent Videshi articles to X (@thevideshi) as long-form posts with images."""

import json
import os
import sys
import time
import tempfile
from datetime import datetime, timezone

import requests
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

TWEET_LOG_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/tweet-log.json")

# --- Fetch articles ---
def fetch_untweeted_articles():
    url = (
        f"{SUPABASE_URL}/rest/v1/p2_articles"
        "?status=eq.published&tweeted_at=is.null"
        "&order=published_at.desc&limit=20"
        "&select=id,slug,headline,subheadline,category,tags,image_url,body"
    )
    resp = requests.get(url, headers=SUPA_HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.json()

# --- Compose post ---
def compose_post(article):
    cat = (article.get("category") or "news").lower()
    emoji = CATEGORY_EMOJI.get(cat, "📰")
    cat_label = cat.upper().replace("-", " ")

    headline = article.get("headline", "").strip()
    subheadline = article.get("subheadline", "").strip()
    slug = article.get("slug", "")
    body = article.get("body", "") or ""

    # Extract body text (strip markdown formatting for context)
    body_plain = body.replace("**", "").replace("*", "").replace("#", "").replace(">", "").strip()
    # Take first ~2000 chars of body for summarization context
    body_excerpt = body_plain[:2000]

    # Build a journalist-quality summary from the body
    # We'll construct from the actual content
    paragraphs = [p.strip() for p in body_plain.split("\n\n") if p.strip() and len(p.strip()) > 40]
    
    # Get the most informative paragraphs (skip very short ones)
    good_paragraphs = []
    for p in paragraphs:
        # Skip markdown artifacts, headers, image references
        if p.startswith("![") or p.startswith("---") or len(p) < 50:
            continue
        good_paragraphs.append(p)
    
    # Build summary from first 2-3 good paragraphs, trimmed
    summary_parts = []
    total_chars = 0
    for p in good_paragraphs[:4]:
        # Trim paragraph to ~150 chars max each
        if len(p) > 200:
            # Cut at sentence boundary
            sentences = p.split(". ")
            trimmed = ""
            for s in sentences:
                if len(trimmed) + len(s) < 200:
                    trimmed += s + ". "
                else:
                    break
            p = trimmed.strip()
        if total_chars + len(p) > 500:
            break
        summary_parts.append(p)
        total_chars += len(p)
    
    summary_text = "\n\n".join(summary_parts) if summary_parts else subheadline

    # Extract key takeaways - find factual sentences with numbers, names, dates
    takeaways = []
    for p in good_paragraphs:
        sentences = [s.strip() for s in p.replace(". ", ".\n").split("\n") if s.strip()]
        for s in sentences:
            # Prefer sentences with numbers, dollar signs, percentages, or proper nouns
            has_data = any(c.isdigit() for c in s) or "$" in s or "%" in s
            if has_data and len(s) > 30 and len(s) < 200 and s not in takeaways:
                takeaways.append(s)
                if len(takeaways) >= 4:
                    break
        if len(takeaways) >= 4:
            break
    
    # If we don't have enough data-driven takeaways, add from subheadline
    if len(takeaways) < 3 and subheadline:
        sub_sentences = [s.strip() for s in subheadline.split(". ") if s.strip()]
        for s in sub_sentences:
            if s not in takeaways:
                if not s.endswith('.'):
                    s += '.'
                takeaways.append(s)
                if len(takeaways) >= 4:
                    break

    # If still not enough, pull short informative sentences
    if len(takeaways) < 3:
        for p in good_paragraphs:
            sentences = [s.strip() for s in p.replace(". ", ".\n").split("\n") if s.strip()]
            for s in sentences:
                if len(s) > 40 and len(s) < 180 and s not in takeaways:
                    takeaways.append(s)
                    if len(takeaways) >= 4:
                        break
            if len(takeaways) >= 4:
                break

    takeaway_lines = ""
    for t in takeaways[:4]:
        # Clean up
        t = t.strip().rstrip(".")
        t += "."
        takeaway_lines += f"▸ {t}\n"

    post = f"""{emoji} {cat_label} | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

{headline.upper()}

{summary_text}

━━━━━━━━━━━━━━━━━━━━━━━━

Key Takeaways:

{takeaway_lines.strip()}

━━━━━━━━━━━━━━━━━━━━━━━━

📰 Full story: thevideshi.com/articles/{slug}

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""

    # Ensure within 4000 char limit
    if len(post) > 3900:
        # Trim summary
        summary_text = summary_text[:300] + "..."
        post = f"""{emoji} {cat_label} | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

{headline.upper()}

{summary_text}

━━━━━━━━━━━━━━━━━━━━━━━━

Key Takeaways:

{takeaway_lines.strip()}

━━━━━━━━━━━━━━━━━━━━━━━━

📰 Full story: thevideshi.com/articles/{slug}

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""

    return post


def download_image(url):
    """Download image to temp file, return path or None."""
    try:
        resp = requests.get(url, timeout=15, stream=True)
        resp.raise_for_status()
        content_type = resp.headers.get("Content-Type", "image/jpeg")
        ext = ".jpg"
        if "png" in content_type:
            ext = ".png"
        elif "webp" in content_type:
            ext = ".webp"
        elif "gif" in content_type:
            ext = ".gif"
        
        tmp = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
        for chunk in resp.iter_content(8192):
            tmp.write(chunk)
        tmp.close()
        
        # Check file size
        fsize = os.path.getsize(tmp.name)
        if fsize < 1000:  # Too small, probably error page
            os.unlink(tmp.name)
            return None
        return tmp.name
    except Exception as e:
        print(f"  ⚠️ Image download failed: {e}")
        return None


def mark_tweeted(article_id):
    """Update Supabase tweeted_at."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    url = f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article_id}"
    resp = requests.patch(url, headers=SUPA_HEADERS, json={"tweeted_at": now}, timeout=15)
    if resp.status_code < 300:
        print(f"  ✅ Supabase tweeted_at updated")
    else:
        print(f"  ⚠️ Supabase update failed: {resp.status_code} {resp.text}")


def log_tweet(tweet_id, article):
    """Log tweet ID locally."""
    tweet_log = {}
    if os.path.exists(TWEET_LOG_PATH):
        try:
            tweet_log = json.load(open(TWEET_LOG_PATH))
        except:
            tweet_log = {}
    tweet_log[str(tweet_id)] = {
        "article_id": article["id"],
        "slug": article["slug"],
        "posted_at": datetime.now(timezone.utc).isoformat() + "Z",
    }
    with open(TWEET_LOG_PATH, "w") as f:
        json.dump(tweet_log, f, indent=2)


def main():
    print("=" * 60)
    print(f"🐦 X Autopost — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 60)

    # Fetch untweeted articles
    articles = fetch_untweeted_articles()
    print(f"\n📋 Found {len(articles)} untweeted articles")

    if not articles:
        print("Nothing to post. Exiting.")
        return

    # Filter: must have image_url, take up to 4
    candidates = [a for a in articles if a.get("image_url")]
    print(f"📷 {len(candidates)} have images")

    to_post = candidates[:4]
    print(f"📝 Will post {len(to_post)} articles\n")

    if not to_post:
        print("No eligible articles. Exiting.")
        return

    # Set up tweepy
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

    for i, article in enumerate(to_post):
        print(f"\n{'─' * 50}")
        print(f"[{i+1}/{len(to_post)}] {article['headline'][:80]}")
        print(f"  Category: {article.get('category', 'news')}")
        print(f"  Slug: {article['slug']}")

        # Compose post
        post_text = compose_post(article)
        print(f"  Post length: {len(post_text)} chars")

        # Download and upload image
        media_ids = None
        img_path = None
        if article.get("image_url"):
            print(f"  📷 Downloading image...")
            img_path = download_image(article["image_url"])
            if img_path:
                try:
                    media = api_v1.media_upload(filename=img_path)
                    media_ids = [media.media_id]
                    print(f"  📷 Image uploaded (media_id: {media.media_id})")
                except Exception as e:
                    print(f"  ⚠️ Image upload failed: {e}")
                    media_ids = None

        # Post tweet
        try:
            kwargs = {"text": post_text}
            if media_ids:
                kwargs["media_ids"] = media_ids
            response = client.create_tweet(**kwargs)
            tweet_id = response.data["id"]
            tweet_url = f"https://x.com/thevideshi/status/{tweet_id}"
            print(f"  ✅ Posted! {tweet_url}")

            # Mark in Supabase
            mark_tweeted(article["id"])

            # Log locally
            log_tweet(tweet_id, article)

            posted += 1
        except Exception as e:
            print(f"  ❌ Post failed: {e}")
            errors += 1
        finally:
            if img_path and os.path.exists(img_path):
                os.unlink(img_path)

        # Wait between posts
        if i < len(to_post) - 1:
            print("  ⏳ Waiting 30s...")
            time.sleep(30)

    print(f"\n{'=' * 60}")
    print(f"📊 Summary: {posted} posted, {errors} errors out of {len(to_post)} attempted")
    print("=" * 60)


if __name__ == "__main__":
    main()
