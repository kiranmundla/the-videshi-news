#!/usr/bin/env python3
"""Post recently published Videshi articles to X (@thevideshi) as long-form posts with images."""

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
MAX_FETCH = 20
MAX_POST = 4
DELAY_BETWEEN_POSTS = 30

# Load env
def load_env(path):
    env = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            line = line.removeprefix('export ')
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

# --- Tweepy setup ---
client = tweepy.Client(
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET
)

auth = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api_v1 = tweepy.API(auth)

# --- Fetch articles ---
print("Fetching unpublished articles from Supabase...")
resp = requests.get(
    f"{SUPABASE_URL}/rest/v1/p2_articles",
    headers=SUPABASE_HEADERS,
    params={
        "status": "eq.published",
        "tweeted_at": "is.null",
        "order": "published_at.desc",
        "limit": MAX_FETCH,
        "select": "id,slug,headline,subheadline,category,tags,image_url,body"
    }
)

if resp.status_code != 200:
    print(f"ERROR: Supabase fetch failed: {resp.status_code} {resp.text}")
    sys.exit(1)

articles = resp.json()
print(f"Found {len(articles)} untweeted articles.")

# Filter: must have image_url
articles_with_images = [a for a in articles if a.get("image_url")]
print(f"After filtering (image_url required): {len(articles_with_images)} articles.")

# Take up to MAX_POST
to_post = articles_with_images[:MAX_POST]
if not to_post:
    print("No articles to post. Done.")
    sys.exit(0)

print(f"Will post {len(to_post)} articles.\n")


def extract_summary_from_body(body, max_words=250):
    """Extract the most interesting content from article body for the summary."""
    if not body:
        return ""
    # Remove markdown formatting artifacts
    import re
    # Remove image markdown
    text = re.sub(r'!\[.*?\]\(.*?\)', '', body)
    # Remove links but keep text
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    # Remove headers
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    # Remove bold/italic markers
    text = re.sub(r'\*{1,3}([^*]+)\*{1,3}', r'\1', text)
    # Remove horizontal rules
    text = re.sub(r'^[-*_]{3,}\s*$', '', text, flags=re.MULTILINE)
    # Clean up multiple newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Get paragraphs
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip() and len(p.strip()) > 40]
    
    # Take first few paragraphs within word limit
    result = []
    word_count = 0
    for p in paragraphs[:6]:
        words = p.split()
        if word_count + len(words) > max_words:
            break
        result.append(p)
        word_count += len(words)
    
    return '\n\n'.join(result)


def extract_key_takeaways(body, subheadline, max_items=4):
    """Extract key facts from the article."""
    import re
    facts = []
    
    if not body:
        if subheadline:
            return [subheadline]
        return []
    
    # Look for bullet points or numbered items in the body
    bullets = re.findall(r'(?:^|\n)\s*[-•▸*]\s+(.+)', body)
    numbered = re.findall(r'(?:^|\n)\s*\d+[.)]\s+(.+)', body)
    
    candidates = bullets + numbered
    
    # Also extract sentences with numbers/stats (those make great takeaways)
    sentences = re.split(r'[.!?]\s+', body)
    for s in sentences:
        s = s.strip()
        if re.search(r'\$[\d,.]+|\d+%|\d{4}|billion|million|crore|lakh', s) and 20 < len(s) < 200:
            # Clean markdown
            s = re.sub(r'\*{1,3}([^*]+)\*{1,3}', r'\1', s)
            s = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', s)
            candidates.append(s)
    
    # Clean and deduplicate
    seen = set()
    for c in candidates:
        c = c.strip()
        c = re.sub(r'\*{1,3}([^*]+)\*{1,3}', r'\1', c)
        c = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', c)
        if len(c) > 15 and c not in seen and len(c) < 200:
            seen.add(c)
            facts.append(c)
            if len(facts) >= max_items:
                break
    
    # If we didn't find enough, add subheadline
    if len(facts) < 2 and subheadline:
        facts.insert(0, subheadline)
    
    return facts[:max_items]


def compose_post(article):
    """Compose a long-form X post for the article."""
    cat = (article.get("category") or "news").lower()
    emoji = CATEGORY_EMOJI.get(cat, "📰")
    label = CATEGORY_LABEL.get(cat, cat.upper())
    
    headline = article.get("headline", "")
    subheadline = article.get("subheadline", "")
    slug = article.get("slug", "")
    body = article.get("body", "")
    
    # Create a punchy rewritten headline (use original but make it more impactful)
    punchy_headline = headline.upper() if len(headline) < 80 else headline.title()
    
    # Extract summary from body
    summary = extract_summary_from_body(body, max_words=200)
    if not summary and subheadline:
        summary = subheadline
    
    # Extract key takeaways
    takeaways = extract_key_takeaways(body, subheadline)
    
    # Build the post
    parts = []
    parts.append(f"{emoji} {label} | The Videshi")
    parts.append("")
    parts.append("━━━━━━━━━━━━━━━━━━━━━━━━")
    parts.append("")
    parts.append(punchy_headline)
    parts.append("")
    
    if summary:
        parts.append(summary)
        parts.append("")
    
    if takeaways:
        parts.append("━━━━━━━━━━━━━━━━━━━━━━━━")
        parts.append("")
        parts.append("Key Takeaways:")
        parts.append("")
        for t in takeaways:
            parts.append(f"▸ {t}")
        parts.append("")
    
    parts.append("━━━━━━━━━━━━━━━━━━━━━━━━")
    parts.append("")
    parts.append(f"📰 Full story: thevideshi.com/articles/{slug}")
    parts.append("")
    parts.append("The Videshi — Your daily source for Indian diaspora news")
    parts.append("🌐 thevideshi.com")
    
    text = '\n'.join(parts)
    
    # Trim if over 4000 chars
    if len(text) > 3900:
        # Shorten summary
        summary_short = extract_summary_from_body(body, max_words=100)
        parts_short = []
        parts_short.append(f"{emoji} {label} | The Videshi")
        parts_short.append("")
        parts_short.append("━━━━━━━━━━━━━━━━━━━━━━━━")
        parts_short.append("")
        parts_short.append(punchy_headline)
        parts_short.append("")
        if summary_short:
            parts_short.append(summary_short)
            parts_short.append("")
        if takeaways:
            parts_short.append("━━━━━━━━━━━━━━━━━━━━━━━━")
            parts_short.append("")
            parts_short.append("Key Takeaways:")
            parts_short.append("")
            for t in takeaways[:3]:
                parts_short.append(f"▸ {t}")
            parts_short.append("")
        parts_short.append("━━━━━━━━━━━━━━━━━━━━━━━━")
        parts_short.append("")
        parts_short.append(f"📰 Full story: thevideshi.com/articles/{slug}")
        parts_short.append("")
        parts_short.append("The Videshi — Your daily source for Indian diaspora news")
        parts_short.append("🌐 thevideshi.com")
        text = '\n'.join(parts_short)
    
    return text[:4000]


def download_image(image_url):
    """Download image to temp file, return path or None."""
    try:
        resp = requests.get(
            image_url,
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=15,
            stream=True
        )
        if resp.status_code != 200:
            print(f"  Image download failed: HTTP {resp.status_code}")
            return None
        
        # Determine extension from content type
        ct = resp.headers.get("Content-Type", "image/jpeg")
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
        
        # Check file size
        fsize = os.path.getsize(tmp.name)
        if fsize < 1000:
            print(f"  Image too small ({fsize} bytes), skipping image.")
            os.unlink(tmp.name)
            return None
        
        print(f"  Image downloaded: {fsize} bytes -> {tmp.name}")
        return tmp.name
    except Exception as e:
        print(f"  Image download error: {e}")
        return None


def upload_media(image_path):
    """Upload image to X via v1.1 API, return media object or None."""
    try:
        media = api_v1.media_upload(filename=image_path)
        print(f"  Media uploaded: media_id={media.media_id}")
        return media
    except Exception as e:
        print(f"  Media upload error: {e}")
        return None


def post_tweet(text, media_ids=None):
    """Post tweet using v2 client."""
    kwargs = {"text": text}
    if media_ids:
        kwargs["media_ids"] = media_ids
    response = client.create_tweet(**kwargs)
    return response


def update_supabase(article_id):
    """Mark article as tweeted in Supabase."""
    now = datetime.now(timezone.utc).isoformat()
    resp = requests.patch(
        f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article_id}",
        headers=SUPABASE_HEADERS,
        json={"tweeted_at": now}
    )
    if resp.status_code in (200, 204):
        print(f"  Supabase updated: tweeted_at = {now}")
    else:
        print(f"  WARNING: Supabase update failed: {resp.status_code} {resp.text}")


def log_tweet(tweet_id, article):
    """Log tweet ID locally."""
    log_path = os.path.expanduser("~/workspace/the-videshi-news/pipeline/tweet-log.json")
    tweet_log = {}
    if os.path.exists(log_path):
        try:
            with open(log_path) as f:
                tweet_log = json.load(f)
        except:
            pass
    tweet_log[str(tweet_id)] = {
        "article_id": article["id"],
        "slug": article["slug"],
        "posted_at": datetime.utcnow().isoformat() + "Z"
    }
    with open(log_path, 'w') as f:
        json.dump(tweet_log, f, indent=2)
    print(f"  Logged to tweet-log.json")


# --- Main posting loop ---
posted = 0
errors = []
tweet_urls = []

for i, article in enumerate(to_post):
    print(f"\n--- Article {i+1}/{len(to_post)} ---")
    print(f"  Headline: {article['headline']}")
    print(f"  Category: {article.get('category', 'unknown')}")
    print(f"  Slug: {article['slug']}")
    
    # Compose post
    post_text = compose_post(article)
    print(f"  Post length: {len(post_text)} chars")
    
    # Download and upload image
    media_ids = None
    image_path = None
    if article.get("image_url"):
        image_path = download_image(article["image_url"])
        if image_path:
            media = upload_media(image_path)
            if media:
                media_ids = [media.media_id]
    
    # Post tweet
    try:
        response = post_tweet(post_text, media_ids=media_ids)
        tweet_id = response.data['id']
        tweet_url = f"https://x.com/thevideshi/status/{tweet_id}"
        print(f"  ✅ Posted! {tweet_url}")
        tweet_urls.append(tweet_url)
        
        # Update Supabase
        update_supabase(article["id"])
        
        # Log tweet
        log_tweet(tweet_id, article)
        
        posted += 1
    except Exception as e:
        err_msg = f"Tweet failed for '{article['headline']}': {e}"
        print(f"  ❌ {err_msg}")
        errors.append(err_msg)
    finally:
        # Clean up temp image
        if image_path and os.path.exists(image_path):
            os.unlink(image_path)
    
    # Wait between posts
    if i < len(to_post) - 1:
        print(f"  Waiting {DELAY_BETWEEN_POSTS}s before next post...")
        time.sleep(DELAY_BETWEEN_POSTS)

# --- Summary ---
print(f"\n{'='*50}")
print(f"SUMMARY: Posted {posted}/{len(to_post)} articles to @thevideshi")
if tweet_urls:
    print("Tweet URLs:")
    for url in tweet_urls:
        print(f"  {url}")
if errors:
    print(f"\nErrors ({len(errors)}):")
    for e in errors:
        print(f"  - {e}")
print(f"{'='*50}")
