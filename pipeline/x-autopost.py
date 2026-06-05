#!/usr/bin/env python3
"""Post recently published Videshi articles to X (@thevideshi) as long-form posts."""

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
MAX_ARTICLES = 4
POST_DELAY = 30  # seconds between posts

# Load env
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
    "culture": "🧘",
    "lifestyle": "🧘",
    "economy": "📈",
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
    "culture": "LIFESTYLE & HEALTH",
    "lifestyle": "LIFESTYLE & HEALTH",
    "economy": "MARKETS & FINANCE",
    "markets": "MARKETS & FINANCE",
    "technology": "TECHNOLOGY",
    "sports": "SPORTS",
    "entertainment": "ENTERTAINMENT",
    "food": "FOOD",
}


def fetch_untweeted_articles():
    """Fetch up to 20 recent published articles not yet tweeted."""
    url = (
        f"{SUPABASE_URL}/rest/v1/p2_articles"
        f"?status=eq.published&tweeted_at=is.null"
        f"&order=published_at.desc&limit=20"
        f"&select=id,slug,headline,subheadline,category,tags,image_url,body"
    )
    resp = requests.get(url, headers=SUPA_HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.json()


def compose_post(article):
    """Compose a long-form X post from the article."""
    cat = (article.get("category") or "news").lower()
    emoji = CATEGORY_EMOJI.get(cat, "📰")
    label = CATEGORY_LABEL.get(cat, cat.upper())
    
    headline = article.get("headline", "").strip()
    subheadline = article.get("subheadline", "").strip()
    slug = article.get("slug", "")
    body = article.get("body", "") or ""
    
    # Extract key content from body (strip markdown formatting)
    body_clean = body.replace("##", "").replace("**", "").replace("*", "")
    # Get first ~1500 chars of body for context
    body_excerpt = body_clean[:2000]
    
    # Build summary from subheadline and body
    # We'll create a condensed version
    summary_parts = []
    if subheadline:
        summary_parts.append(subheadline)
    
    # Extract paragraphs from body (skip very short lines, headers)
    paragraphs = []
    for p in body.split('\n\n'):
        p = p.strip()
        if not p or p.startswith('#') or p.startswith('![') or p.startswith('---') or len(p) < 40:
            continue
        # Clean markdown
        clean = p.replace("##", "").replace("**", "").replace("*", "").strip()
        if clean:
            paragraphs.append(clean)
    
    # Build 2-3 paragraph summary from the article body
    summary_text = ""
    if paragraphs:
        # Take first 2-3 meaningful paragraphs, trim to ~250 words total
        selected = []
        word_count = 0
        for p in paragraphs[:5]:
            words = p.split()
            if word_count + len(words) > 250:
                break
            selected.append(p)
            word_count += len(words)
        summary_text = "\n\n".join(selected[:3])
    
    if not summary_text and subheadline:
        summary_text = subheadline
    
    # Extract key takeaways from the body
    takeaways = extract_takeaways(article)
    
    # Build the post
    separator = "━━━━━━━━━━━━━━━━━━━━━━━━"
    
    lines = [
        f"{emoji} {label} | The Videshi",
        "",
        separator,
        "",
        headline.upper() if len(headline) < 80 else headline,
        "",
        summary_text,
        "",
        separator,
        "",
        "Key Takeaways:",
        "",
    ]
    
    for t in takeaways:
        lines.append(f"▸ {t}")
    
    lines.extend([
        "",
        separator,
        "",
        f"📰 Full story: thevideshi.com/articles/{slug}",
        "",
        "The Videshi — Your daily source for Indian diaspora news",
        "🌐 thevideshi.com",
    ])
    
    post_text = "\n".join(lines)
    
    # Trim if over 4000 chars
    if len(post_text) > 3900:
        # Shorten summary
        if summary_text:
            words = summary_text.split()
            summary_text = " ".join(words[:120]) + "..."
            # Rebuild
            lines[6] = summary_text
            post_text = "\n".join(lines)
    
    return post_text


def extract_takeaways(article):
    """Extract 3-4 key takeaways from article body and subheadline."""
    takeaways = []
    body = article.get("body", "") or ""
    subheadline = article.get("subheadline", "") or ""
    
    # Look for sentences with numbers, names, or key facts
    all_text = subheadline + " " + body
    # Clean markdown
    all_text = all_text.replace("**", "").replace("*", "").replace("##", "").replace("#", "")
    
    sentences = []
    for chunk in all_text.split('. '):
        s = chunk.strip().rstrip('.')
        if len(s) > 20 and len(s) < 200:
            sentences.append(s + ".")
    
    # Prefer sentences with numbers, dollar signs, percentages
    priority = []
    normal = []
    for s in sentences:
        if any(c.isdigit() for c in s) or '$' in s or '%' in s:
            priority.append(s)
        else:
            normal.append(s)
    
    # Take from priority first, then normal
    candidates = priority[:4] + normal[:4]
    
    # Deduplicate and pick 3-4
    seen = set()
    for c in candidates:
        key = c[:50].lower()
        if key not in seen:
            seen.add(key)
            takeaways.append(c)
        if len(takeaways) >= 4:
            break
    
    # Fallback
    if len(takeaways) < 3:
        if subheadline and subheadline not in takeaways:
            takeaways.insert(0, subheadline)
    
    return takeaways[:4]


def download_image(image_url):
    """Download image to temp file, return path or None."""
    try:
        resp = requests.get(
            image_url,
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=15,
            stream=True,
        )
        resp.raise_for_status()
        
        # Determine extension
        content_type = resp.headers.get("Content-Type", "")
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
        size = os.path.getsize(tmp.name)
        if size < 1000:
            os.unlink(tmp.name)
            print(f"  Image too small ({size} bytes), skipping image")
            return None
        
        print(f"  Downloaded image: {size} bytes")
        return tmp.name
    except Exception as e:
        print(f"  Image download failed: {e}")
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
        print(f"  Uploaded media: {media.media_id}")
        return media
    except Exception as e:
        print(f"  Media upload failed: {e}")
        return None


def post_tweet(text, media_id=None):
    """Post tweet using tweepy v2 Client."""
    client = tweepy.Client(
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET,
    )
    kwargs = {"text": text}
    if media_id:
        kwargs["media_ids"] = [media_id]
    
    response = client.create_tweet(**kwargs)
    return response


def mark_tweeted(article_id):
    """Update tweeted_at in Supabase."""
    now = datetime.now(timezone.utc).isoformat()
    url = f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article_id}"
    resp = requests.patch(url, json={"tweeted_at": now}, headers=SUPA_HEADERS, timeout=15)
    resp.raise_for_status()
    print(f"  Marked tweeted_at in Supabase")


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
    
    with open(log_path, 'w') as f:
        json.dump(tweet_log, f, indent=2)
    print(f"  Logged to tweet-log.json")


def main():
    print(f"=== X Autopost — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} ===\n")
    
    # Fetch articles
    articles = fetch_untweeted_articles()
    print(f"Found {len(articles)} untweeted articles")
    
    # Filter: must have image_url
    eligible = [a for a in articles if a.get("image_url")]
    print(f"{len(eligible)} have images")
    
    if not eligible:
        print("Nothing to post.")
        return
    
    # Pick up to MAX_ARTICLES
    to_post = eligible[:MAX_ARTICLES]
    print(f"Will post {len(to_post)} articles\n")
    
    posted = 0
    errors = []
    
    for i, article in enumerate(to_post):
        print(f"--- [{i+1}/{len(to_post)}] {article['headline'][:80]} ---")
        print(f"  Category: {article.get('category', 'unknown')}")
        print(f"  Slug: {article['slug']}")
        
        # Compose post
        post_text = compose_post(article)
        print(f"  Post length: {len(post_text)} chars")
        
        # Download and upload image
        media_id = None
        image_url = article.get("image_url", "")
        if image_url:
            img_path = download_image(image_url)
            if img_path:
                media = upload_media(img_path)
                if media:
                    media_id = media.media_id
                os.unlink(img_path)
        
        # Post tweet
        try:
            response = post_tweet(post_text, media_id)
            tweet_id = response.data['id']
            tweet_url = f"https://x.com/thevideshi/status/{tweet_id}"
            print(f"  ✅ Posted: {tweet_url}")
            
            # Mark in Supabase
            mark_tweeted(article["id"])
            
            # Log locally
            log_tweet(tweet_id, article)
            
            posted += 1
            
        except Exception as e:
            error_msg = str(e)
            print(f"  ❌ Failed: {error_msg}")
            errors.append({"slug": article["slug"], "error": error_msg})
        
        # Wait between posts
        if i < len(to_post) - 1:
            print(f"  Waiting {POST_DELAY}s...")
            time.sleep(POST_DELAY)
    
    print(f"\n=== Summary ===")
    print(f"Posted: {posted}/{len(to_post)}")
    if errors:
        print(f"Errors: {len(errors)}")
        for e in errors:
            print(f"  - {e['slug']}: {e['error']}")


if __name__ == "__main__":
    main()
