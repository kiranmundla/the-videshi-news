#!/usr/bin/env python3
"""Post recently published Videshi articles to X (@thevideshi) as long-form posts with images."""

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
            if not line or line.startswith('#'):
                continue
            if line.startswith('export '):
                line = line[7:]
            key, _, val = line.partition('=')
            env[key.strip()] = val.strip()
    return env

twitter_env = load_env("~/workspace/.env.twitter")
supabase_env = load_env("~/workspace/.env.supabase")

CONSUMER_KEY = twitter_env["TWITTER_CONSUMER_KEY"]
CONSUMER_SECRET = twitter_env["TWITTER_CONSUMER_SECRET"]
ACCESS_TOKEN = twitter_env["TWITTER_ACCESS_TOKEN"]
ACCESS_TOKEN_SECRET = twitter_env["TWITTER_ACCESS_TOKEN_SECRET"]
SUPABASE_KEY = supabase_env["SUPABASE_SERVICE_ROLE_KEY"]

CATEGORY_EMOJI = {
    "news": "🇮🇳",
    "immigration": "🛂",
    "nri-world": "🌏",
    "nri world": "🌏",
    "travel": "✈️",
    "lifestyle": "🧘",
    "lifestyle & health": "🧘",
    "markets": "📈",
    "markets & finance": "📈",
    "technology": "💻",
    "sports": "🏏",
    "entertainment": "🎬",
    "food": "🍛",
}

def get_emoji(category):
    if not category:
        return "📰"
    cat = category.lower().strip()
    return CATEGORY_EMOJI.get(cat, "📰")

def get_label(category):
    if not category:
        return "NEWS"
    return category.upper()

# --- Supabase helpers ---
SB_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}

def fetch_untweeted():
    url = (
        f"{SUPABASE_URL}/rest/v1/p2_articles"
        "?status=eq.published&tweeted_at=is.null&order=published_at.desc&limit=20"
        "&select=id,slug,headline,subheadline,category,tags,image_url,body"
    )
    r = requests.get(url, headers=SB_HEADERS, timeout=30)
    r.raise_for_status()
    return r.json()

def mark_tweeted(article_id):
    url = f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article_id}"
    ts = datetime.now(timezone.utc).isoformat()
    r = requests.patch(url, headers=SB_HEADERS, json={"tweeted_at": ts}, timeout=15)
    r.raise_for_status()
    return ts

# --- Tweet log ---
LOG_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/tweet-log.json")

def load_tweet_log():
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH) as f:
            return json.load(f)
    return {}

def save_tweet_log(log):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "w") as f:
        json.dump(log, f, indent=2)

# --- Content generation ---
def extract_body_text(body_md):
    """Extract clean text from markdown body, stripping images/links/headers for summarization."""
    if not body_md:
        return ""
    lines = []
    for line in body_md.split('\n'):
        line = line.strip()
        # Skip image lines
        if line.startswith('!['):
            continue
        # Skip empty headers
        if line.startswith('#') and len(line.replace('#', '').strip()) == 0:
            continue
        lines.append(line)
    return '\n'.join(lines)

def compose_post(article):
    """Compose a long-form X post from the article data. Returns the post text."""
    cat = article.get('category', 'news')
    emoji = get_emoji(cat)
    label = get_label(cat)
    headline = article.get('headline', '')
    subheadline = article.get('subheadline', '')
    slug = article.get('slug', '')
    body = article.get('body', '')
    
    # We'll construct the post using the body content
    body_text = extract_body_text(body)
    
    # Build the post - we'll use AI to generate the summary, but since we're in a script,
    # we'll do an extractive approach: take key paragraphs from the body
    paragraphs = [p.strip() for p in body_text.split('\n\n') if p.strip() and len(p.strip()) > 40]
    
    # Skip header-only paragraphs
    paragraphs = [p for p in paragraphs if not p.startswith('#')]
    
    # Build summary from first few meaningful paragraphs
    summary_parts = []
    char_count = 0
    for p in paragraphs[:6]:
        # Clean markdown formatting
        clean = p.replace('**', '').replace('*', '').replace('###', '').replace('##', '').replace('#', '').strip()
        if len(clean) < 30:
            continue
        if char_count + len(clean) > 800:
            break
        summary_parts.append(clean)
        char_count += len(clean)
    
    summary = '\n\n'.join(summary_parts[:3])
    
    # Extract key facts for takeaways - look for lines with numbers, names, or key info
    takeaways = []
    for p in paragraphs:
        clean = p.replace('**', '').replace('*', '').strip()
        # Look for sentences with numbers or key facts
        sentences = [s.strip() for s in clean.replace('. ', '.\n').split('\n') if s.strip()]
        for s in sentences:
            if len(s) > 40 and len(s) < 200:
                has_fact = any(c.isdigit() for c in s) or any(w in s.lower() for w in ['billion', 'million', 'percent', '%', 'announced', 'launched', 'first', 'largest', 'record'])
                if has_fact and len(takeaways) < 4:
                    takeaways.append(s)
    
    # If we couldn't find fact-heavy sentences, use subheadline and first sentences
    if len(takeaways) < 3:
        if subheadline:
            takeaways.insert(0, subheadline)
        for p in paragraphs[:4]:
            clean = p.replace('**', '').replace('*', '').strip()
            sentences = [s.strip() + '.' for s in clean.split('.') if len(s.strip()) > 30]
            for s in sentences:
                if s not in takeaways and len(takeaways) < 4:
                    takeaways.append(s[:180])
    
    takeaways = takeaways[:4]
    
    # Build the post
    post = f"""{emoji} {label} | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

{headline.upper()}

{summary}

━━━━━━━━━━━━━━━━━━━━━━━━

Key Takeaways:

"""
    for t in takeaways:
        post += f"▸ {t}\n"
    
    post += f"""
━━━━━━━━━━━━━━━━━━━━━━━━

📰 Full story: thevideshi.com/articles/{slug}

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""
    
    # Trim if over 4000 chars
    if len(post) > 3900:
        # Shorten summary
        summary = '\n\n'.join(summary_parts[:2])
        post = f"""{emoji} {label} | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

{headline.upper()}

{summary}

━━━━━━━━━━━━━━━━━━━━━━━━

Key Takeaways:

"""
        for t in takeaways[:3]:
            post += f"▸ {t}\n"
        post += f"""
━━━━━━━━━━━━━━━━━━━━━━━━

📰 Full story: thevideshi.com/articles/{slug}

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""
    
    return post

# --- Image handling ---
def download_image(image_url):
    """Download image to temp file, return path or None."""
    if not image_url:
        return None
    try:
        r = requests.get(image_url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=15, stream=True)
        r.raise_for_status()
        # Determine extension
        ct = r.headers.get('content-type', '')
        ext = '.jpg'
        if 'png' in ct:
            ext = '.png'
        elif 'webp' in ct:
            ext = '.webp'
        elif 'gif' in ct:
            ext = '.gif'
        
        tmp = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
        for chunk in r.iter_content(8192):
            tmp.write(chunk)
        tmp.close()
        
        # Check file size
        fsize = os.path.getsize(tmp.name)
        if fsize < 1000:
            print(f"  ⚠️  Image too small ({fsize} bytes), skipping image")
            os.unlink(tmp.name)
            return None
        
        print(f"  📸 Downloaded image: {fsize:,} bytes")
        return tmp.name
    except Exception as e:
        print(f"  ⚠️  Image download failed: {e}")
        return None

# --- Main ---
def main():
    print("=" * 60)
    print("🐦 The Videshi → X Autopost")
    print(f"   {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("=" * 60)
    
    # Fetch untweeted articles
    articles = fetch_untweeted()
    print(f"\n📋 Found {len(articles)} untweeted published articles")
    
    if not articles:
        print("Nothing to post. Done.")
        return
    
    # Filter: must have image_url
    eligible = [a for a in articles if a.get('image_url')]
    skipped = len(articles) - len(eligible)
    if skipped:
        print(f"   Skipped {skipped} articles with no image_url")
    
    # Take up to 4
    to_post = eligible[:4]
    print(f"   Will post {len(to_post)} articles\n")
    
    if not to_post:
        print("No eligible articles. Done.")
        return
    
    # Set up Twitter clients
    client = tweepy.Client(
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET,
    )
    auth = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api_v1 = tweepy.API(auth)
    
    tweet_log = load_tweet_log()
    posted = 0
    errors = []
    
    for i, article in enumerate(to_post):
        print(f"{'─' * 50}")
        print(f"📝 [{i+1}/{len(to_post)}] {article['headline']}")
        print(f"   Category: {article.get('category', 'N/A')} | Slug: {article['slug']}")
        
        # Compose post
        post_text = compose_post(article)
        print(f"   Post length: {len(post_text)} chars")
        
        # Download and upload image
        media_ids = None
        img_path = download_image(article.get('image_url'))
        if img_path:
            try:
                media = api_v1.media_upload(filename=img_path)
                media_ids = [media.media_id]
                print(f"  📤 Image uploaded to X (media_id: {media.media_id})")
            except Exception as e:
                print(f"  ⚠️  Image upload to X failed: {e}")
            finally:
                try:
                    os.unlink(img_path)
                except:
                    pass
        
        # Post tweet
        try:
            kwargs = {"text": post_text}
            if media_ids:
                kwargs["media_ids"] = media_ids
            response = client.create_tweet(**kwargs)
            tweet_id = response.data['id']
            tweet_url = f"https://x.com/thevideshi/status/{tweet_id}"
            print(f"  ✅ Posted! {tweet_url}")
            
            # Mark tweeted in Supabase
            ts = mark_tweeted(article['id'])
            print(f"  📝 Supabase updated (tweeted_at: {ts})")
            
            # Log locally
            tweet_log[str(tweet_id)] = {
                "article_id": article['id'],
                "slug": article['slug'],
                "posted_at": datetime.utcnow().isoformat() + "Z"
            }
            save_tweet_log(tweet_log)
            
            posted += 1
            
            # Wait between posts
            if i < len(to_post) - 1:
                print(f"  ⏳ Waiting 30s before next post...")
                time.sleep(30)
                
        except Exception as e:
            error_msg = f"{article['slug']}: {e}"
            errors.append(error_msg)
            print(f"  ❌ FAILED: {e}")
            # If rate limited, check for specific error
            if 'Too Many Requests' in str(e) or '429' in str(e):
                print("  🛑 Rate limited — stopping")
                break
    
    # Summary
    print(f"\n{'=' * 60}")
    print(f"📊 SUMMARY")
    print(f"   Posted: {posted}/{len(to_post)}")
    if errors:
        print(f"   Errors: {len(errors)}")
        for e in errors:
            print(f"     • {e}")
    print("=" * 60)

if __name__ == "__main__":
    main()
