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
MAX_POSTS = 4
DELAY_BETWEEN_POSTS = 30

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

supa_headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

# Category emoji mapping
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

CATEGORY_LABELS = {
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


def fetch_untweeted():
    """Fetch untweeted published articles from Supabase."""
    resp = requests.get(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        params={
            "status": "eq.published",
            "tweeted_at": "is.null",
            "order": "published_at.desc",
            "limit": "20",
            "select": "id,slug,headline,subheadline,category,tags,image_url,body"
        },
        headers=supa_headers
    )
    resp.raise_for_status()
    return resp.json()


def extract_key_facts(body, subheadline):
    """Extract key facts from article body for takeaways."""
    # Combine sources
    text = (body or "") + "\n" + (subheadline or "")
    
    # Look for sentences with numbers, names, or strong facts
    import re
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    # Filter for informative sentences (contain numbers, proper nouns, or key phrases)
    fact_sentences = []
    for s in sentences:
        s = s.strip()
        if not s or len(s) < 20 or len(s) > 200:
            continue
        # Skip markdown headers and formatting
        if s.startswith('#') or s.startswith('**') or s.startswith('- '):
            s = re.sub(r'[#*\-]+\s*', '', s).strip()
        if not s:
            continue
        # Prefer sentences with numbers, percentages, dollar amounts, dates
        has_data = bool(re.search(r'\d', s))
        has_quote = bool(re.search(r'[""]', s))
        # Score it
        if has_data or has_quote:
            fact_sentences.append(s)
    
    # If not enough data-heavy sentences, add others
    if len(fact_sentences) < 4:
        for s in sentences:
            s = s.strip()
            if s and len(s) >= 30 and len(s) <= 180 and s not in fact_sentences:
                s = re.sub(r'[#*\-]+\s*', '', s).strip()
                if s and not s.startswith('!['): # skip image refs
                    fact_sentences.append(s)
            if len(fact_sentences) >= 6:
                break
    
    return fact_sentences[:4]


def compose_summary(body):
    """Extract a 2-3 paragraph summary from article body."""
    import re
    if not body:
        return ""
    
    # Remove markdown formatting
    text = body
    text = re.sub(r'^#+\s+.*$', '', text, flags=re.MULTILINE)  # headers
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)  # images
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)  # links -> text
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # bold
    text = re.sub(r'\*([^*]+)\*', r'\1', text)  # italic
    text = re.sub(r'^>\s+', '', text, flags=re.MULTILINE)  # blockquotes
    text = re.sub(r'^[-*]\s+', '', text, flags=re.MULTILINE)  # list items
    text = re.sub(r'\n{3,}', '\n\n', text)  # excess newlines
    
    # Split into paragraphs
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip() and len(p.strip()) > 40]
    
    if not paragraphs:
        return ""
    
    # Take first 2-3 substantive paragraphs (the article lead)
    summary_paras = []
    total_len = 0
    for p in paragraphs[:5]:
        if total_len + len(p) > 800:
            break
        summary_paras.append(p)
        total_len += len(p)
        if len(summary_paras) >= 3:
            break
    
    return "\n\n".join(summary_paras)


def compose_post(article):
    """Compose a long-form X post for an article."""
    cat = article.get("category", "news")
    emoji = CATEGORY_EMOJI.get(cat, "📰")
    label = CATEGORY_LABELS.get(cat, cat.upper())
    headline = article.get("headline", "")
    slug = article.get("slug", "")
    body = article.get("body", "")
    subheadline = article.get("subheadline", "")
    
    # Rewrite headline for X - make it punchier
    # Use title case, trim if needed
    x_headline = headline.upper() if len(headline) < 70 else headline
    
    # Get summary paragraphs
    summary = compose_summary(body)
    
    # Get key takeaways
    facts = extract_key_facts(body, subheadline)
    takeaways = "\n".join([f"▸ {f}" for f in facts]) if facts else ""
    
    # Build post
    parts = [
        f"{emoji} {label} | The Videshi",
        "",
        "━━━━━━━━━━━━━━━━━━━━━━━━",
        "",
        x_headline,
        "",
    ]
    
    if summary:
        parts.append(summary)
        parts.append("")
    
    if takeaways:
        parts.append("━━━━━━━━━━━━━━━━━━━━━━━━")
        parts.append("")
        parts.append("Key Takeaways:")
        parts.append("")
        parts.append(takeaways)
        parts.append("")
    
    parts.append("━━━━━━━━━━━━━━━━━━━━━━━━")
    parts.append("")
    parts.append(f"📰 Full story: thevideshi.com/articles/{slug}")
    parts.append("")
    parts.append("The Videshi — Your daily source for Indian diaspora news")
    parts.append("🌐 thevideshi.com")
    
    post_text = "\n".join(parts)
    
    # Trim if over 4000 chars
    if len(post_text) > 3900:
        # Shorten summary
        summary_short = compose_summary(body)
        if summary_short:
            # Take only first paragraph
            first_para = summary_short.split('\n\n')[0]
            parts_short = [
                f"{emoji} {label} | The Videshi",
                "",
                "━━━━━━━━━━━━━━━━━━━━━━━━",
                "",
                x_headline,
                "",
                first_para,
                "",
            ]
            if takeaways:
                parts_short.append("━━━━━━━━━━━━━━━━━━━━━━━━")
                parts_short.append("")
                parts_short.append("Key Takeaways:")
                parts_short.append("")
                parts_short.append(takeaways)
                parts_short.append("")
            parts_short.append("━━━━━━━━━━━━━━━━━━━━━━━━")
            parts_short.append("")
            parts_short.append(f"📰 Full story: thevideshi.com/articles/{slug}")
            parts_short.append("")
            parts_short.append("The Videshi — Your daily source for Indian diaspora news")
            parts_short.append("🌐 thevideshi.com")
            post_text = "\n".join(parts_short)
    
    return post_text


def download_image(url):
    """Download image to temp file, return path or None."""
    try:
        resp = requests.get(url, timeout=15, stream=True)
        resp.raise_for_status()
        
        # Determine extension
        content_type = resp.headers.get('content-type', '')
        if 'png' in content_type:
            ext = '.png'
        elif 'gif' in content_type:
            ext = '.gif'
        elif 'webp' in content_type:
            ext = '.webp'
        else:
            ext = '.jpg'
        
        tmp = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
        for chunk in resp.iter_content(8192):
            tmp.write(chunk)
        tmp.close()
        
        # Check file size
        size = os.path.getsize(tmp.name)
        if size < 1000:  # too small, probably an error page
            os.unlink(tmp.name)
            return None
        
        return tmp.name
    except Exception as e:
        print(f"  ⚠️ Image download failed: {e}")
        return None


def upload_media(image_path):
    """Upload image to X via v1.1 API, return media object or None."""
    try:
        auth = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        api_v1 = tweepy.API(auth)
        media = api_v1.media_upload(filename=image_path)
        return media
    except Exception as e:
        print(f"  ⚠️ Media upload failed: {e}")
        return None


def post_tweet(text, media_id=None):
    """Post tweet via v2 API, return response."""
    client = tweepy.Client(
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET
    )
    kwargs = {"text": text}
    if media_id:
        kwargs["media_ids"] = [media_id]
    
    response = client.create_tweet(**kwargs)
    return response


def mark_tweeted(article_id):
    """Update tweeted_at in Supabase."""
    now = datetime.utcnow().isoformat() + "Z"
    resp = requests.patch(
        f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article_id}",
        headers=supa_headers,
        json={"tweeted_at": now}
    )
    if resp.status_code < 300:
        print(f"  ✅ Supabase updated (tweeted_at={now})")
    else:
        print(f"  ⚠️ Supabase update failed: {resp.status_code} {resp.text}")


def log_tweet(tweet_id, article):
    """Log tweet to local JSON file."""
    log_path = os.path.expanduser("~/workspace/the-videshi-news/pipeline/tweet-log.json")
    try:
        tweet_log = json.load(open(log_path)) if os.path.exists(log_path) else {}
    except:
        tweet_log = {}
    
    tweet_log[str(tweet_id)] = {
        "article_id": article["id"],
        "slug": article["slug"],
        "posted_at": datetime.utcnow().isoformat() + "Z"
    }
    
    with open(log_path, "w") as f:
        json.dump(tweet_log, f, indent=2)


def main():
    print("=" * 50)
    print("🐦 The Videshi — X Autopost")
    print(f"⏰ {datetime.utcnow().isoformat()}Z")
    print("=" * 50)
    
    # Fetch articles
    articles = fetch_untweeted()
    print(f"\n📥 Found {len(articles)} untweeted articles")
    
    if not articles:
        print("Nothing to post.")
        return
    
    # Filter: must have image_url
    eligible = [a for a in articles if a.get("image_url")]
    print(f"📋 {len(eligible)} have images (eligible)")
    
    if not eligible:
        print("No eligible articles with images.")
        return
    
    # Pick top N
    to_post = eligible[:MAX_POSTS]
    print(f"🎯 Will post {len(to_post)} articles\n")
    
    posted = 0
    errors = 0
    
    for i, article in enumerate(to_post):
        print(f"\n{'─' * 40}")
        print(f"📝 [{i+1}/{len(to_post)}] {article['headline'][:70]}...")
        print(f"   Category: {article['category']} | Slug: {article['slug'][:50]}")
        
        # Compose post
        post_text = compose_post(article)
        print(f"   Post length: {len(post_text)} chars")
        
        # Download and upload image
        media_id = None
        image_path = None
        if article.get("image_url"):
            print(f"   📷 Downloading image...")
            image_path = download_image(article["image_url"])
            if image_path:
                print(f"   📤 Uploading to X...")
                media = upload_media(image_path)
                if media:
                    media_id = media.media_id
                    print(f"   ✅ Media uploaded (id={media_id})")
        
        # Post tweet
        try:
            print(f"   🐦 Posting tweet...")
            response = post_tweet(post_text, media_id)
            tweet_id = response.data["id"]
            tweet_url = f"https://x.com/thevideshi/status/{tweet_id}"
            print(f"   ✅ Posted! {tweet_url}")
            
            # Update Supabase
            mark_tweeted(article["id"])
            
            # Log locally
            log_tweet(tweet_id, article)
            
            posted += 1
            
        except Exception as e:
            print(f"   ❌ Failed to post: {e}")
            errors += 1
        
        finally:
            # Clean up temp file
            if image_path and os.path.exists(image_path):
                os.unlink(image_path)
        
        # Delay between posts
        if i < len(to_post) - 1:
            print(f"   ⏳ Waiting {DELAY_BETWEEN_POSTS}s...")
            time.sleep(DELAY_BETWEEN_POSTS)
    
    print(f"\n{'=' * 50}")
    print(f"📊 Summary: {posted} posted, {errors} errors out of {len(to_post)} attempted")
    print("=" * 50)


if __name__ == "__main__":
    main()
