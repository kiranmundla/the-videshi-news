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

SB_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}

# --- Fetch articles ---
print("Fetching untweeted articles...")
resp = requests.get(
    f"{SUPABASE_URL}/rest/v1/p2_articles",
    params={
        "status": "eq.published",
        "tweeted_at": "is.null",
        "order": "published_at.desc",
        "limit": "20",
        "select": "id,slug,headline,subheadline,category,tags,image_url,body",
    },
    headers=SB_HEADERS,
)
resp.raise_for_status()
articles = resp.json()
print(f"Found {len(articles)} untweeted articles")

# Filter out articles with no image_url and pick up to 4
candidates = [a for a in articles if a.get("image_url")]
to_post = candidates[:4]
print(f"Selected {len(to_post)} articles to post (with images)")

if not to_post:
    print("No articles to post. Done.")
    sys.exit(0)

# Print selected articles
for i, a in enumerate(to_post):
    print(f"  {i+1}. [{a['category']}] {a['headline'][:80]}...")

# --- Setup tweepy ---
client = tweepy.Client(
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET,
)
auth = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api_v1 = tweepy.API(auth)

LOG_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/tweet-log.json")

def load_tweet_log():
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH) as f:
            return json.load(f)
    return {}

def save_tweet_log(log):
    with open(LOG_PATH, 'w') as f:
        json.dump(log, f, indent=2)

def compose_post(article):
    """Compose a long-form X post from article data."""
    cat = article.get("category", "news")
    emoji = CATEGORY_EMOJI.get(cat, "📰")
    cat_label = cat.upper().replace("-", " ")
    
    headline = article.get("headline", "")
    subheadline = article.get("subheadline", "")
    slug = article.get("slug", "")
    body = article.get("body", "")
    
    # We'll use the body to extract key info. Truncate body for processing.
    body_text = body[:3000] if body else ""
    
    # Build the post - return components for the caller to assemble
    return {
        "emoji": emoji,
        "cat_label": cat_label,
        "headline": headline,
        "subheadline": subheadline,
        "slug": slug,
        "body_text": body_text,
        "category": cat,
    }

def download_image(url):
    """Download image to temp file, return path or None."""
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        # Determine extension
        ct = r.headers.get("content-type", "")
        ext = ".jpg"
        if "png" in ct:
            ext = ".png"
        elif "webp" in ct:
            ext = ".webp"
        elif "gif" in ct:
            ext = ".gif"
        
        tmp = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
        tmp.write(r.content)
        tmp.close()
        return tmp.name
    except Exception as e:
        print(f"  ⚠ Image download failed: {e}")
        return None

# --- Post articles ---
posted = 0
errors = []
tweet_log = load_tweet_log()

for idx, article in enumerate(to_post):
    print(f"\n--- Posting {idx+1}/{len(to_post)}: {article['headline'][:60]}... ---")
    
    info = compose_post(article)
    
    # Build the post text
    # Extract a concise summary and key takeaways from the body
    body_text = info["body_text"]
    
    # Remove markdown formatting for cleaner text
    import re
    clean_body = re.sub(r'!\[.*?\]\(.*?\)', '', body_text)  # remove images
    clean_body = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', clean_body)  # links to text
    clean_body = re.sub(r'#{1,6}\s+', '', clean_body)  # remove headers
    clean_body = re.sub(r'\*\*([^*]+)\*\*', r'\1', clean_body)  # bold
    clean_body = re.sub(r'\*([^*]+)\*', r'\1', clean_body)  # italic
    clean_body = re.sub(r'\n{3,}', '\n\n', clean_body)  # collapse newlines
    clean_body = clean_body.strip()
    
    # Get first ~600 chars of clean body for summary material
    paragraphs = [p.strip() for p in clean_body.split('\n\n') if p.strip() and len(p.strip()) > 30]
    
    # Build summary from first few paragraphs
    summary_parts = []
    char_count = 0
    for p in paragraphs[:5]:
        if char_count + len(p) > 800:
            break
        summary_parts.append(p)
        char_count += len(p)
    
    summary = '\n\n'.join(summary_parts[:3]) if summary_parts else info["subheadline"]
    
    # Extract key facts for takeaways
    # Use subheadline + first few paragraphs
    takeaway_source = (info["subheadline"] or "") + "\n" + "\n".join(paragraphs[:6])
    
    # Find sentences with numbers, names, or key facts
    sentences = re.split(r'(?<=[.!?])\s+', takeaway_source)
    key_sentences = []
    for s in sentences:
        s = s.strip()
        if len(s) > 20 and len(s) < 200:
            # Prefer sentences with numbers, dollar signs, percentages, or proper nouns
            if re.search(r'[\d$%₹]|million|billion|first|largest|record|launched|announced', s, re.I):
                key_sentences.append(s)
    
    # If not enough fact-heavy sentences, take any meaningful ones
    if len(key_sentences) < 3:
        for s in sentences:
            s = s.strip()
            if len(s) > 30 and len(s) < 200 and s not in key_sentences:
                key_sentences.append(s)
            if len(key_sentences) >= 4:
                break
    
    takeaways = key_sentences[:4]
    
    # Rewrite headline - make it punchier
    punchy_headline = info["headline"].upper() if len(info["headline"]) < 80 else info["headline"]
    
    # Assemble the post
    post_lines = [
        f'{info["emoji"]} {info["cat_label"]} | The Videshi',
        '',
        '━━━━━━━━━━━━━━━━━━━━━━━━',
        '',
        punchy_headline,
        '',
    ]
    
    if summary:
        post_lines.append(summary)
        post_lines.append('')
    
    post_lines.append('━━━━━━━━━━━━━━━━━━━━━━━━')
    post_lines.append('')
    
    if takeaways:
        post_lines.append('Key Takeaways:')
        post_lines.append('')
        for t in takeaways:
            # Clean up the takeaway
            t = t.strip().rstrip('.')
            post_lines.append(f'▸ {t}')
        post_lines.append('')
        post_lines.append('━━━━━━━━━━━━━━━━━━━━━━━━')
        post_lines.append('')
    
    post_lines.append(f'📰 Full story: thevideshi.com/articles/{info["slug"]}')
    post_lines.append('')
    post_lines.append('The Videshi — Your daily source for Indian diaspora news')
    post_lines.append('🌐 thevideshi.com')
    
    post_text = '\n'.join(post_lines)
    
    # Trim if over 4000 chars
    if len(post_text) > 4000:
        # Shorten summary
        post_text = post_text[:3950] + '\n\n🌐 thevideshi.com'
    
    print(f"  Post length: {len(post_text)} chars")
    
    # Download and upload image
    media_ids = None
    tmp_path = None
    if article.get("image_url"):
        tmp_path = download_image(article["image_url"])
        if tmp_path:
            try:
                media = api_v1.media_upload(filename=tmp_path)
                media_ids = [media.media_id]
                print(f"  ✓ Image uploaded (media_id: {media.media_id})")
            except Exception as e:
                print(f"  ⚠ Image upload failed: {e}")
                media_ids = None
    
    # Post tweet
    try:
        kwargs = {"text": post_text}
        if media_ids:
            kwargs["media_ids"] = media_ids
        
        response = client.create_tweet(**kwargs)
        tweet_id = response.data['id']
        print(f"  ✓ Posted! Tweet ID: {tweet_id}")
        print(f"  🔗 https://x.com/thevideshi/status/{tweet_id}")
        
        # Update Supabase
        patch_resp = requests.patch(
            f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article['id']}",
            headers=SB_HEADERS,
            json={"tweeted_at": datetime.utcnow().isoformat() + "Z"},
        )
        if patch_resp.status_code < 300:
            print(f"  ✓ Supabase updated (tweeted_at set)")
        else:
            print(f"  ⚠ Supabase update failed: {patch_resp.status_code} {patch_resp.text}")
        
        # Log tweet
        tweet_log[str(tweet_id)] = {
            "article_id": article["id"],
            "slug": article["slug"],
            "posted_at": datetime.utcnow().isoformat() + "Z",
        }
        save_tweet_log(tweet_log)
        
        posted += 1
        
    except Exception as e:
        err_msg = f"Failed to post '{article['headline'][:50]}': {e}"
        print(f"  ✗ {err_msg}")
        errors.append(err_msg)
    
    # Clean up temp file
    if tmp_path and os.path.exists(tmp_path):
        os.unlink(tmp_path)
    
    # Wait between posts
    if idx < len(to_post) - 1:
        print("  ⏳ Waiting 30s...")
        time.sleep(30)

# --- Summary ---
print(f"\n{'='*50}")
print(f"SUMMARY: Posted {posted}/{len(to_post)} articles to X")
if errors:
    print(f"Errors ({len(errors)}):")
    for e in errors:
        print(f"  - {e}")
print(f"{'='*50}")
