#!/usr/bin/env python3
"""Post recently published Videshi articles to X with long-form posts + images."""

import json
import os
import sys
import tempfile
import time
from datetime import datetime, timezone

import requests
import tweepy

# === Config ===
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
    """Fetch up to 20 recent published articles without tweeted_at."""
    url = (
        f"{SUPABASE_URL}/rest/v1/p2_articles"
        "?status=eq.published"
        "&tweeted_at=is.null"
        "&order=published_at.desc"
        "&limit=20"
        "&select=id,slug,headline,subheadline,category,tags,image_url,body"
    )
    r = requests.get(url, headers=SUPA_HEADERS, timeout=30)
    r.raise_for_status()
    return r.json()


def extract_summary_and_takeaways(article):
    """Use the article body to create a journalist-style summary and key takeaways."""
    body = article.get("body") or ""
    headline = article.get("headline", "")
    subheadline = article.get("subheadline", "")
    
    # Clean markdown from body for text extraction
    import re
    clean = body
    # Remove markdown headers
    clean = re.sub(r'^#{1,6}\s+', '', clean, flags=re.MULTILINE)
    # Remove bold/italic markers
    clean = re.sub(r'\*{1,3}([^*]+)\*{1,3}', r'\1', clean)
    # Remove links but keep text
    clean = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', clean)
    # Remove images
    clean = re.sub(r'!\[[^\]]*\]\([^)]+\)', '', clean)
    # Remove horizontal rules
    clean = re.sub(r'^---+$', '', clean, flags=re.MULTILINE)
    # Collapse whitespace
    clean = re.sub(r'\n{3,}', '\n\n', clean)
    
    # Get paragraphs
    paragraphs = [p.strip() for p in clean.split('\n\n') if p.strip() and len(p.strip()) > 40]
    
    # Build summary from first meaningful paragraphs
    summary_parts = []
    total_chars = 0
    for p in paragraphs[:6]:
        if total_chars > 600:
            break
        # Skip very short or section-header-like paragraphs
        if len(p) < 50:
            continue
        summary_parts.append(p)
        total_chars += len(p)
    
    summary = "\n\n".join(summary_parts[:3])
    
    # Trim summary if too long
    if len(summary) > 800:
        sentences = summary.split('. ')
        trimmed = []
        running = 0
        for s in sentences:
            if running + len(s) > 700:
                break
            trimmed.append(s)
            running += len(s) + 2
        summary = '. '.join(trimmed)
        if not summary.endswith('.'):
            summary += '.'
    
    # Extract key takeaways - look for bullet points, numbers, key facts
    takeaways = []
    
    # Try to find factual sentences with numbers, names, percentages
    fact_patterns = [
        r'(?:.*\d+(?:\.\d+)?%.*)',  # percentages
        r'(?:.*\$[\d,.]+\s*(?:billion|million|trillion|crore|lakh)?.*)',  # money
        r'(?:.*\d{4}.*)',  # years
    ]
    
    all_sentences = []
    for p in paragraphs:
        for s in p.split('. '):
            s = s.strip()
            if len(s) > 30 and len(s) < 200:
                all_sentences.append(s)
    
    # Pick interesting sentences as takeaways
    scored = []
    for s in all_sentences:
        score = 0
        if any(c.isdigit() for c in s):
            score += 2
        if '$' in s or '%' in s or 'billion' in s.lower() or 'million' in s.lower():
            score += 3
        if any(w in s.lower() for w in ['first', 'largest', 'record', 'new', 'launch', 'announce']):
            score += 1
        if s not in summary:
            score += 1
        scored.append((score, s))
    
    scored.sort(key=lambda x: -x[0])
    
    for score, s in scored:
        if len(takeaways) >= 4:
            break
        # Avoid duplicating summary content
        if s in summary:
            continue
        if not s.endswith('.'):
            s += '.'
        takeaways.append(s)
    
    # If we don't have enough takeaways, use subheadline
    if len(takeaways) < 3 and subheadline:
        takeaways.insert(0, subheadline)
    
    # Ensure at least 3
    while len(takeaways) < 3 and all_sentences:
        s = all_sentences.pop(0)
        if s not in summary and s not in takeaways:
            if not s.endswith('.'):
                s += '.'
            takeaways.append(s)
    
    return summary, takeaways[:4]


def compose_post(article):
    """Compose a long-form X post for the article."""
    cat = article.get("category", "news") or "news"
    emoji = CATEGORY_EMOJI.get(cat, "📰")
    label = CATEGORY_LABEL.get(cat, cat.upper())
    headline = article.get("headline", "")
    slug = article.get("slug", "")
    
    summary, takeaways = extract_summary_and_takeaways(article)
    
    # Build the post
    lines = []
    lines.append(f"{emoji} {label} | The Videshi")
    lines.append("")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("")
    lines.append(headline.upper() if len(headline) < 80 else headline)
    lines.append("")
    lines.append(summary)
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
    
    post = "\n".join(lines)
    
    # Trim if over 4000 chars
    if len(post) > 3900:
        summary, takeaways = summary[:500], takeaways[:3]
        # Rebuild
        lines = []
        lines.append(f"{emoji} {label} | The Videshi")
        lines.append("")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append("")
        lines.append(headline.upper() if len(headline) < 80 else headline)
        lines.append("")
        lines.append(summary)
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
        post = "\n".join(lines)
    
    return post


def download_image(url):
    """Download image to temp file, return path or None."""
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        content_type = r.headers.get("Content-Type", "image/jpeg")
        ext = ".jpg"
        if "png" in content_type:
            ext = ".png"
        elif "webp" in content_type:
            ext = ".webp"
        elif "gif" in content_type:
            ext = ".gif"
        
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
        tmp.write(r.content)
        tmp.close()
        return tmp.name
    except Exception as e:
        print(f"  ⚠ Image download failed: {e}")
        return None


def upload_media(image_path):
    """Upload image to X using v1.1 API, return media object or None."""
    try:
        auth = tweepy.OAuth1UserHandler(
            CONSUMER_KEY, CONSUMER_SECRET,
            ACCESS_TOKEN, ACCESS_TOKEN_SECRET
        )
        api_v1 = tweepy.API(auth)
        media = api_v1.media_upload(filename=image_path)
        return media
    except Exception as e:
        print(f"  ⚠ Media upload failed: {e}")
        return None


def post_tweet(text, media_ids=None):
    """Post tweet using v2 client."""
    client = tweepy.Client(
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET,
    )
    kwargs = {"text": text}
    if media_ids:
        kwargs["media_ids"] = media_ids
    response = client.create_tweet(**kwargs)
    return response


def update_supabase(article_id):
    """Mark article as tweeted in Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article_id}"
    now = datetime.now(timezone.utc).isoformat()
    r = requests.patch(url, json={"tweeted_at": now}, headers=SUPA_HEADERS, timeout=15)
    r.raise_for_status()
    return now


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
        "posted_at": datetime.now(timezone.utc).isoformat() + "Z",
    }
    with open(log_path, "w") as f:
        json.dump(tweet_log, f, indent=2)


def main():
    print("=" * 60)
    print("X AUTOPOST — The Videshi")
    print(f"Run time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 60)
    
    # Fetch articles
    articles = fetch_articles()
    print(f"\n📋 Found {len(articles)} untweeted published articles")
    
    if not articles:
        print("✅ Nothing to post — all caught up!")
        return
    
    # Filter: must have image_url and slug
    eligible = [a for a in articles if a.get("image_url") and a.get("slug")]
    print(f"📎 {len(eligible)} have images + slugs (eligible)")
    
    if not eligible:
        print("⚠ No eligible articles (all missing images or slugs)")
        return
    
    # Pick up to 4
    to_post = eligible[:4]
    print(f"🎯 Will post {len(to_post)} articles\n")
    
    posted = 0
    errors = []
    tweet_urls = []
    
    for i, article in enumerate(to_post):
        print(f"\n{'─' * 50}")
        print(f"[{i+1}/{len(to_post)}] {article['headline'][:80]}...")
        print(f"  Category: {article.get('category', '?')} | Slug: {article['slug'][:50]}")
        
        # Compose post
        post_text = compose_post(article)
        print(f"  Post length: {len(post_text)} chars")
        
        # Download and upload image
        media_ids = None
        image_path = None
        if article.get("image_url"):
            print(f"  📸 Downloading image...")
            image_path = download_image(article["image_url"])
            if image_path:
                print(f"  📤 Uploading to X...")
                media = upload_media(image_path)
                if media:
                    media_ids = [media.media_id]
                    print(f"  ✅ Media uploaded (ID: {media.media_id})")
        
        # Post tweet
        try:
            print(f"  🐦 Posting tweet...")
            response = post_tweet(post_text, media_ids=media_ids)
            tweet_id = response.data["id"]
            tweet_url = f"https://x.com/thevideshi/status/{tweet_id}"
            print(f"  ✅ Posted! {tweet_url}")
            tweet_urls.append(tweet_url)
            
            # Update Supabase
            ts = update_supabase(article["id"])
            print(f"  📝 Supabase updated (tweeted_at: {ts})")
            
            # Log tweet
            log_tweet(tweet_id, article)
            print(f"  📋 Tweet logged")
            
            posted += 1
            
        except Exception as e:
            err_msg = f"Failed to post '{article['headline'][:50]}': {e}"
            print(f"  ❌ {err_msg}")
            errors.append(err_msg)
        
        # Clean up temp image
        if image_path and os.path.exists(image_path):
            os.unlink(image_path)
        
        # Wait between posts
        if i < len(to_post) - 1:
            print(f"  ⏳ Waiting 30s before next post...")
            time.sleep(30)
    
    # Summary
    print(f"\n{'=' * 60}")
    print(f"SUMMARY")
    print(f"{'=' * 60}")
    print(f"✅ Posted: {posted}/{len(to_post)}")
    if errors:
        print(f"❌ Errors: {len(errors)}")
        for e in errors:
            print(f"  • {e}")
    if tweet_urls:
        print(f"\n📎 Tweet URLs:")
        for u in tweet_urls:
            print(f"  {u}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
