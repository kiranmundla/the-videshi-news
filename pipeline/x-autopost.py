#!/usr/bin/env python3
"""Post recently published Videshi articles to X (@thevideshi) as long-form posts with images."""

import json, os, sys, time, tempfile, requests
from datetime import datetime, timezone

import tweepy

# --- Config ---
SUPABASE_URL = "https://lboecaekpynbpyijrbfz.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
CONSUMER_KEY = os.environ["TWITTER_CONSUMER_KEY"]
CONSUMER_SECRET = os.environ["TWITTER_CONSUMER_SECRET"]
ACCESS_TOKEN = os.environ["TWITTER_ACCESS_TOKEN"]
ACCESS_TOKEN_SECRET = os.environ["TWITTER_ACCESS_TOKEN_SECRET"]

MAX_ARTICLES = 4

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

# --- Supabase helpers ---
def sb_headers():
    return {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
        "Content-Type": "application/json",
    }

def fetch_untweeted_articles():
    url = (
        f"{SUPABASE_URL}/rest/v1/p2_articles"
        "?status=eq.published&tweeted_at=is.null"
        "&order=published_at.desc&limit=20"
        "&select=id,slug,headline,subheadline,category,tags,image_url,body"
    )
    r = requests.get(url, headers=sb_headers(), timeout=30)
    r.raise_for_status()
    return r.json()

def mark_tweeted(article_id):
    url = f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article_id}"
    now = datetime.now(timezone.utc).isoformat()
    r = requests.patch(url, headers=sb_headers(), json={"tweeted_at": now}, timeout=30)
    r.raise_for_status()

# --- Tweet composition ---
def compose_tweet(article):
    cat = (article.get("category") or "news").lower()
    emoji = CATEGORY_EMOJI.get(cat, "📰")
    cat_label = cat.upper().replace("-", " ")
    headline = article.get("headline", "").strip()
    subheadline = article.get("subheadline", "").strip()
    slug = article.get("slug", "")
    body = article.get("body", "") or ""

    # Build a summary from the body — extract first ~300 words of meaningful content
    # Strip markdown formatting for cleaner reading
    import re
    clean = body
    # Remove markdown images
    clean = re.sub(r'!\[.*?\]\(.*?\)', '', clean)
    # Remove markdown links but keep text
    clean = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', clean)
    # Remove headers
    clean = re.sub(r'^#{1,6}\s+', '', clean, flags=re.MULTILINE)
    # Remove bold/italic markers
    clean = re.sub(r'\*{1,3}([^*]+)\*{1,3}', r'\1', clean)
    # Remove horizontal rules
    clean = re.sub(r'^---+$', '', clean, flags=re.MULTILINE)
    # Collapse whitespace
    clean = re.sub(r'\n{3,}', '\n\n', clean).strip()

    # Get paragraphs (skip very short ones)
    paragraphs = [p.strip() for p in clean.split('\n\n') if len(p.strip()) > 40]

    # Build summary — take first few paragraphs up to ~200 words
    summary_parts = []
    word_count = 0
    for p in paragraphs[:6]:
        words = p.split()
        if word_count + len(words) > 250:
            # Take partial if we have nothing yet
            if not summary_parts:
                summary_parts.append(' '.join(words[:200]))
            break
        summary_parts.append(p)
        word_count += len(words)
        if word_count >= 150:
            break

    summary_text = '\n\n'.join(summary_parts)

    # Extract key takeaways from body — look for numbers, quotes, key facts
    # Use subheadline + first few strong statements
    takeaways = []
    if subheadline:
        takeaways.append(subheadline)

    # Look for sentences with numbers, percentages, dollar signs — those are usually key facts
    sentences = re.split(r'(?<=[.!?])\s+', clean)
    fact_sentences = []
    for s in sentences:
        s = s.strip()
        if len(s) < 20 or len(s) > 200:
            continue
        # Prioritize sentences with numbers, money, or strong claims
        if re.search(r'\d+[%$]|\$\d|billion|million|crore|lakh|\d{4}', s):
            fact_sentences.append(s)
        elif any(w in s.lower() for w in ['first', 'record', 'largest', 'unprecedented', 'historic', 'banned', 'launched', 'announced']):
            fact_sentences.append(s)

    for fs in fact_sentences[:4]:
        if fs not in takeaways and len(takeaways) < 4:
            takeaways.append(fs)

    # If still short on takeaways, grab early sentences
    if len(takeaways) < 3:
        for s in sentences[1:10]:
            s = s.strip()
            if 30 < len(s) < 180 and s not in takeaways:
                takeaways.append(s)
            if len(takeaways) >= 4:
                break

    takeaways = takeaways[:4]

    # Compose the post
    lines = []
    lines.append(f"{emoji} {cat_label} | The Videshi")
    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("")
    lines.append(headline.upper() if len(headline) < 100 else headline)
    lines.append("")
    lines.append(summary_text)
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
    lines.append(f"📰 Full story: thevideshi.com/articles/{slug}")
    lines.append("")
    lines.append("The Videshi — Your daily source for Indian diaspora news")
    lines.append("🌐 thevideshi.com")

    text = '\n'.join(lines)

    # Trim if over 4000 chars
    if len(text) > 3900:
        # Shorten summary
        while len(text) > 3900 and summary_parts:
            summary_parts = summary_parts[:-1]
            summary_text = '\n\n'.join(summary_parts)
            lines_rebuilt = []
            lines_rebuilt.append(f"{emoji} {cat_label} | The Videshi")
            lines_rebuilt.append("")
            lines_rebuilt.append("━━━━━━━━━━━━━━━━━━━━━━━━")
            lines_rebuilt.append("")
            lines_rebuilt.append(headline.upper() if len(headline) < 100 else headline)
            lines_rebuilt.append("")
            lines_rebuilt.append(summary_text)
            lines_rebuilt.append("")
            lines_rebuilt.append("━━━━━━━━━━━━━━━━━━━━━━━━")
            lines_rebuilt.append("")
            lines_rebuilt.append("Key Takeaways:")
            lines_rebuilt.append("")
            for t in takeaways:
                lines_rebuilt.append(f"▸ {t}")
            lines_rebuilt.append("")
            lines_rebuilt.append("━━━━━━━━━━━━━━━━━━━━━━━━")
            lines_rebuilt.append("")
            lines_rebuilt.append(f"📰 Full story: thevideshi.com/articles/{slug}")
            lines_rebuilt.append("")
            lines_rebuilt.append("The Videshi — Your daily source for Indian diaspora news")
            lines_rebuilt.append("🌐 thevideshi.com")
            text = '\n'.join(lines_rebuilt)

    return text

# --- Image download ---
def download_image(image_url):
    """Download image to temp file, return path or None."""
    if not image_url:
        return None
    try:
        r = requests.get(image_url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=15, stream=True)
        r.raise_for_status()
        ct = r.headers.get("Content-Type", "")
        ext = ".jpg"
        if "png" in ct:
            ext = ".png"
        elif "webp" in ct:
            ext = ".webp"
        elif "gif" in ct:
            ext = ".gif"
        tf = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
        for chunk in r.iter_content(8192):
            tf.write(chunk)
        tf.close()
        # Check file size - X requires > 0 bytes
        if os.path.getsize(tf.name) < 100:
            os.unlink(tf.name)
            return None
        return tf.name
    except Exception as e:
        print(f"  ⚠ Image download failed: {e}")
        return None

# --- Main ---
def main():
    print("=" * 60)
    print("🐦 Videshi X Auto-Post — Long-Form Posts")
    print(f"   {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 60)

    # Fetch articles
    articles = fetch_untweeted_articles()
    print(f"\n📋 Found {len(articles)} untweeted articles")

    if not articles:
        print("Nothing to post. Done.")
        return

    # Filter: must have image_url
    eligible = [a for a in articles if a.get("image_url")]
    print(f"📸 {len(eligible)} have images (eligible)")

    if not eligible:
        print("No eligible articles with images. Done.")
        return

    to_post = eligible[:MAX_ARTICLES]
    print(f"🎯 Will post {len(to_post)} articles\n")

    # Set up tweepy
    client = tweepy.Client(
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET,
    )

    auth = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api_v1 = tweepy.API(auth)

    # Load tweet log
    tweet_log = {}
    if os.path.exists(TWEET_LOG_PATH):
        with open(TWEET_LOG_PATH) as f:
            tweet_log = json.load(f)

    posted = 0
    errors = []

    for i, article in enumerate(to_post):
        slug = article.get("slug", "???")
        headline = article.get("headline", "???")
        print(f"\n{'─' * 50}")
        print(f"[{i+1}/{len(to_post)}] {headline[:80]}")
        print(f"   slug: {slug}")
        print(f"   category: {article.get('category', '?')}")

        try:
            # Compose long-form post
            tweet_text = compose_tweet(article)
            print(f"   📝 Post length: {len(tweet_text)} chars")

            # Download and upload image
            media_ids = None
            img_path = download_image(article.get("image_url"))
            if img_path:
                try:
                    media = api_v1.media_upload(filename=img_path)
                    media_ids = [media.media_id]
                    print(f"   📸 Image uploaded (media_id: {media.media_id})")
                except Exception as e:
                    print(f"   ⚠ Image upload failed: {e}")
                finally:
                    if os.path.exists(img_path):
                        os.unlink(img_path)
            else:
                print("   📸 No image (posting without)")

            # Post tweet
            kwargs = {"text": tweet_text}
            if media_ids:
                kwargs["media_ids"] = media_ids

            response = client.create_tweet(**kwargs)
            tweet_id = response.data["id"]
            tweet_url = f"https://x.com/thevideshi/status/{tweet_id}"
            print(f"   ✅ Posted! {tweet_url}")

            # Mark tweeted in Supabase
            mark_tweeted(article["id"])
            print(f"   📝 Supabase updated (tweeted_at set)")

            # Log tweet
            tweet_log[str(tweet_id)] = {
                "article_id": article["id"],
                "slug": slug,
                "posted_at": datetime.now(timezone.utc).isoformat() + "Z",
            }

            posted += 1

            # Wait between posts
            if i < len(to_post) - 1:
                print(f"   ⏳ Waiting 30s before next post...")
                time.sleep(30)

        except Exception as e:
            err_msg = f"{slug}: {e}"
            errors.append(err_msg)
            print(f"   ❌ Error: {e}")

    # Save tweet log
    os.makedirs(os.path.dirname(TWEET_LOG_PATH), exist_ok=True)
    with open(TWEET_LOG_PATH, "w") as f:
        json.dump(tweet_log, f, indent=2)
    print(f"\n💾 Tweet log saved ({len(tweet_log)} total entries)")

    # Summary
    print(f"\n{'=' * 60}")
    print(f"📊 SUMMARY: {posted}/{len(to_post)} posted successfully")
    if errors:
        print(f"❌ Errors ({len(errors)}):")
        for e in errors:
            print(f"   • {e}")
    print("=" * 60)


if __name__ == "__main__":
    main()
