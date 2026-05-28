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

def fetch_articles():
    """Fetch up to 20 recent published articles that haven't been tweeted."""
    url = (
        f"{SUPABASE_URL}/rest/v1/p2_articles"
        "?status=eq.published&tweeted_at=is.null&order=published_at.desc&limit=20"
        "&select=id,slug,headline,subheadline,category,tags,image_url,body"
    )
    resp = requests.get(url, headers=SUPABASE_HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.json()

def compose_post(article):
    """Compose a long-form X post from the article."""
    cat = (article.get("category") or "news").lower()
    emoji = CATEGORY_EMOJI.get(cat, "📰")
    label = CATEGORY_LABEL.get(cat, cat.upper())
    slug = article.get("slug", "")
    headline = article.get("headline", "")
    subheadline = article.get("subheadline", "")
    body = article.get("body", "") or ""

    # Extract first ~500 words of body for context
    body_text = body.replace("#", "").replace("*", "").replace("_", "")
    # Remove markdown links
    import re
    body_text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', body_text)
    body_text = re.sub(r'!\[[^\]]*\]\([^)]+\)', '', body_text)
    body_words = body_text.split()[:500]
    body_excerpt = " ".join(body_words)

    return headline, subheadline, body_excerpt, emoji, label, slug, cat

def build_post_text(headline, subheadline, body_excerpt, emoji, label, slug):
    """Build the actual post text using the article content."""
    # We'll construct the post intelligently from available content
    # Extract key sentences from body for the summary
    import re
    sentences = re.split(r'(?<=[.!?])\s+', body_excerpt)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]

    # Build summary paragraphs (2-3 paragraphs, ~150-250 words)
    summary_sentences = sentences[:8] if len(sentences) >= 8 else sentences
    
    # Split into paragraphs
    if len(summary_sentences) >= 6:
        para1 = " ".join(summary_sentences[:3])
        para2 = " ".join(summary_sentences[3:6])
        para3 = " ".join(summary_sentences[6:8]) if len(summary_sentences) > 6 else ""
    elif len(summary_sentences) >= 4:
        para1 = " ".join(summary_sentences[:2])
        para2 = " ".join(summary_sentences[2:4])
        para3 = ""
    elif len(summary_sentences) >= 2:
        para1 = " ".join(summary_sentences[:1])
        para2 = " ".join(summary_sentences[1:2])
        para3 = ""
    else:
        para1 = " ".join(summary_sentences) if summary_sentences else subheadline or headline
        para2 = ""
        para3 = ""

    # Build key takeaways from subheadline and early body content
    takeaway_candidates = []
    if subheadline:
        takeaway_candidates.append(subheadline)
    # Add shorter factual sentences
    for s in sentences[2:12]:
        s_clean = s.strip()
        if 30 < len(s_clean) < 200 and any(c.isdigit() for c in s_clean):
            takeaway_candidates.append(s_clean)
        elif 30 < len(s_clean) < 150:
            takeaway_candidates.append(s_clean)
    
    takeaways = takeaway_candidates[:4] if len(takeaway_candidates) >= 4 else takeaway_candidates[:3]
    if not takeaways and subheadline:
        takeaways = [subheadline]

    # Construct post
    lines = []
    lines.append(f"{emoji} {label} | The Videshi")
    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("")
    lines.append(headline.upper() if len(headline) < 100 else headline)
    lines.append("")
    lines.append(para1)
    if para2:
        lines.append("")
        lines.append(para2)
    if para3:
        lines.append("")
        lines.append(para3)
    
    if takeaways:
        lines.append("")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append("")
        lines.append("Key Takeaways:")
        lines.append("")
        for t in takeaways:
            # Truncate long takeaways
            if len(t) > 180:
                t = t[:177] + "..."
            lines.append(f"▸ {t}")
    
    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("")
    lines.append(f"📰 Full story: thevideshi.com/articles/{slug}")
    lines.append("")
    lines.append("The Videshi — Your daily source for Indian diaspora news")
    lines.append("🌐 thevideshi.com")

    text = "\n".join(lines)
    
    # Trim if over 4000 chars
    if len(text) > 3900:
        # Cut summary paragraphs shorter
        if para3:
            para3 = ""
        if len(text) > 3900 and para2:
            para2_words = para2.split()[:30]
            para2 = " ".join(para2_words)
        # Rebuild
        lines_trimmed = []
        lines_trimmed.append(f"{emoji} {label} | The Videshi")
        lines_trimmed.append("")
        lines_trimmed.append("━━━━━━━━━━━━━━━━━━━━━━━━")
        lines_trimmed.append("")
        lines_trimmed.append(headline.upper() if len(headline) < 100 else headline)
        lines_trimmed.append("")
        lines_trimmed.append(para1[:400])
        if para2:
            lines_trimmed.append("")
            lines_trimmed.append(para2[:300])
        if takeaways:
            lines_trimmed.append("")
            lines_trimmed.append("━━━━━━━━━━━━━━━━━━━━━━━━")
            lines_trimmed.append("")
            lines_trimmed.append("Key Takeaways:")
            lines_trimmed.append("")
            for t in takeaways[:3]:
                lines_trimmed.append(f"▸ {t[:150]}")
        lines_trimmed.append("")
        lines_trimmed.append("━━━━━━━━━━━━━━━━━━━━━━━━")
        lines_trimmed.append("")
        lines_trimmed.append(f"📰 Full story: thevideshi.com/articles/{slug}")
        lines_trimmed.append("")
        lines_trimmed.append("The Videshi — Your daily source for Indian diaspora news")
        lines_trimmed.append("🌐 thevideshi.com")
        text = "\n".join(lines_trimmed)

    return text

def download_image(url):
    """Download image to temp file, return path or None."""
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        content_type = resp.headers.get("content-type", "")
        ext = ".jpg"
        if "png" in content_type:
            ext = ".png"
        elif "webp" in content_type:
            ext = ".webp"
        elif "gif" in content_type:
            ext = ".gif"
        fd, path = tempfile.mkstemp(suffix=ext)
        with os.fdopen(fd, 'wb') as f:
            f.write(resp.content)
        return path
    except Exception as e:
        print(f"  ⚠️ Image download failed: {e}")
        return None

def mark_tweeted(article_id):
    """Mark article as tweeted in Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article_id}"
    ts = datetime.utcnow().isoformat() + "Z"
    resp = requests.patch(url, json={"tweeted_at": ts}, headers=SUPABASE_HEADERS, timeout=15)
    if resp.status_code < 300:
        print(f"  ✅ Marked tweeted_at in Supabase")
    else:
        print(f"  ⚠️ Supabase update failed: {resp.status_code} {resp.text}")

def log_tweet(tweet_id, article):
    """Log tweet ID locally."""
    log_path = os.path.expanduser("~/workspace/the-videshi-news/pipeline/tweet-log.json")
    tweet_log = {}
    if os.path.exists(log_path):
        try:
            with open(log_path) as f:
                tweet_log = json.load(f)
        except:
            tweet_log = {}
    tweet_log[str(tweet_id)] = {
        "article_id": article["id"],
        "slug": article["slug"],
        "posted_at": datetime.utcnow().isoformat() + "Z"
    }
    with open(log_path, 'w') as f:
        json.dump(tweet_log, f, indent=2)
    print(f"  📝 Logged tweet to tweet-log.json")

def main():
    print("=" * 60)
    print("🐦 The Videshi X Auto-Poster (Long-Form)")
    print(f"⏰ {datetime.utcnow().isoformat()}Z")
    print("=" * 60)

    # Fetch articles
    print("\n📥 Fetching untweeted articles...")
    articles = fetch_articles()
    print(f"   Found {len(articles)} untweeted articles")

    if not articles:
        print("\n✅ No articles to post. Done.")
        return

    # Filter: must have image_url
    eligible = [a for a in articles if a.get("image_url")]
    print(f"   {len(eligible)} have images (eligible)")
    
    if not eligible:
        print("\n⚠️ No articles with images. Done.")
        return

    # Pick up to 4 newest
    to_post = eligible[:4]
    print(f"\n📝 Will post {len(to_post)} articles:\n")
    for i, a in enumerate(to_post, 1):
        print(f"   {i}. [{a.get('category','')}] {a['headline'][:80]}")

    # Set up tweepy clients
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
    tweet_urls = []

    for i, article in enumerate(to_post, 1):
        print(f"\n{'─' * 50}")
        print(f"📤 [{i}/{len(to_post)}] Posting: {article['headline'][:70]}...")
        
        try:
            # Compose post
            headline, subheadline, body_excerpt, emoji, label, slug, cat = compose_post(article)
            post_text = build_post_text(headline, subheadline, body_excerpt, emoji, label, slug)
            
            print(f"   Category: {cat} | Length: {len(post_text)} chars")

            # Download and upload image
            media_ids = None
            image_url = article.get("image_url", "")
            if image_url:
                print(f"   📷 Downloading image...")
                img_path = download_image(image_url)
                if img_path:
                    try:
                        print(f"   📤 Uploading image to X...")
                        media = api_v1.media_upload(filename=img_path)
                        media_ids = [media.media_id]
                        print(f"   ✅ Image uploaded (media_id: {media.media_id})")
                    except Exception as e:
                        print(f"   ⚠️ Image upload failed: {e}")
                    finally:
                        os.unlink(img_path)

            # Post tweet
            kwargs = {"text": post_text}
            if media_ids:
                kwargs["media_ids"] = media_ids
            
            response = client.create_tweet(**kwargs)
            tweet_id = response.data["id"]
            tweet_url = f"https://x.com/thevideshi/status/{tweet_id}"
            tweet_urls.append(tweet_url)
            
            print(f"   ✅ Posted! {tweet_url}")

            # Mark tweeted in Supabase
            mark_tweeted(article["id"])
            
            # Log tweet
            log_tweet(tweet_id, article)

            posted += 1

        except Exception as e:
            print(f"   ❌ Error: {e}")
            errors += 1

        # Wait between posts
        if i < len(to_post):
            print(f"   ⏳ Waiting 30s before next post...")
            time.sleep(30)

    # Summary
    print(f"\n{'=' * 60}")
    print(f"📊 SUMMARY")
    print(f"   ✅ Posted: {posted}/{len(to_post)}")
    if errors:
        print(f"   ❌ Errors: {errors}")
    for url in tweet_urls:
        print(f"   🔗 {url}")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    main()
