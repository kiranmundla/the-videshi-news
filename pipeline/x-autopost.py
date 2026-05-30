#!/usr/bin/env python3
"""Post recent Videshi articles to X (@thevideshi) as long-form posts with images."""

import json
import os
import sys
import time
import tempfile
import requests
import tweepy
from datetime import datetime, timezone

# --- Load env files ---
def load_env(path):
    env = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, val = line.split('=', 1)
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                env[key] = val
    return env

twitter_env = load_env('~/workspace/.env.twitter')
supabase_env = load_env('~/workspace/.env.supabase')

CONSUMER_KEY = twitter_env['TWITTER_CONSUMER_KEY']
CONSUMER_SECRET = twitter_env['TWITTER_CONSUMER_SECRET']
ACCESS_TOKEN = twitter_env['TWITTER_ACCESS_TOKEN']
ACCESS_TOKEN_SECRET = twitter_env['TWITTER_ACCESS_TOKEN_SECRET']

SUPABASE_URL = 'https://lboecaekpynbpyijrbfz.supabase.co'
SUPABASE_KEY = supabase_env['SUPABASE_SERVICE_ROLE_KEY']

CATEGORY_EMOJI = {
    'news': '🇮🇳',
    'immigration': '🛂',
    'nri-world': '🌏',
    'travel': '✈️',
    'lifestyle': '🧘',
    'lifestyle-health': '🧘',
    'markets': '📈',
    'markets-finance': '📈',
    'technology': '💻',
    'sports': '🏏',
    'entertainment': '🎬',
    'food': '🍛',
}

CATEGORY_LABEL = {
    'news': 'NEWS',
    'immigration': 'IMMIGRATION',
    'nri-world': 'NRI WORLD',
    'travel': 'TRAVEL',
    'lifestyle': 'LIFESTYLE',
    'lifestyle-health': 'LIFESTYLE & HEALTH',
    'markets': 'MARKETS & FINANCE',
    'markets-finance': 'MARKETS & FINANCE',
    'technology': 'TECHNOLOGY',
    'sports': 'SPORTS',
    'entertainment': 'ENTERTAINMENT',
    'food': 'FOOD',
}

# --- Fetch untweeted articles ---
headers = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
}

resp = requests.get(
    f'{SUPABASE_URL}/rest/v1/p2_articles',
    params={
        'status': 'eq.published',
        'tweeted_at': 'is.null',
        'order': 'published_at.desc',
        'limit': '20',
        'select': 'id,slug,headline,subheadline,category,tags,image_url,body',
    },
    headers=headers,
)
resp.raise_for_status()
articles = resp.json()
print(f"Found {len(articles)} untweeted articles")

# Filter: must have image_url, pick up to 4
eligible = [a for a in articles if a.get('image_url')]
to_post = eligible[:4]
print(f"Will post {len(to_post)} articles (with images)")

if not to_post:
    print("Nothing to post. Done.")
    sys.exit(0)

# --- Setup tweepy ---
client = tweepy.Client(
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET,
)

auth = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api_v1 = tweepy.API(auth)

# --- Compose post from article ---
def extract_summary_and_takeaways(article):
    """Extract key content from the article body for the X post."""
    body = article.get('body', '') or ''
    headline = article.get('headline', '')
    subheadline = article.get('subheadline', '')
    
    # Clean markdown: remove images, headers markers, links
    import re
    clean = body
    clean = re.sub(r'!\[.*?\]\(.*?\)', '', clean)  # images
    clean = re.sub(r'#{1,6}\s+', '', clean)  # headers
    clean = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', clean)  # links -> text
    clean = re.sub(r'\*\*([^*]+)\*\*', r'\1', clean)  # bold
    clean = re.sub(r'\*([^*]+)\*', r'\1', clean)  # italic
    clean = re.sub(r'\n{3,}', '\n\n', clean)  # excess newlines
    
    # Get paragraphs (non-empty lines)
    paragraphs = [p.strip() for p in clean.split('\n\n') if p.strip() and len(p.strip()) > 40]
    
    # Build a condensed version for the summary - take first few substantial paragraphs
    summary_parts = []
    char_count = 0
    for p in paragraphs[:8]:
        if char_count > 600:
            break
        summary_parts.append(p)
        char_count += len(p)
    
    summary_text = '\n\n'.join(summary_parts[:3])
    
    # Truncate summary to ~250 words
    words = summary_text.split()
    if len(words) > 250:
        summary_text = ' '.join(words[:250]) + '…'
    
    # Extract key facts for takeaways from remaining paragraphs
    all_text = ' '.join(paragraphs)
    
    return summary_text, all_text


def compose_post(article):
    """Compose a long-form X post for an article."""
    cat = (article.get('category') or 'news').lower()
    emoji = CATEGORY_EMOJI.get(cat, '📰')
    label = CATEGORY_LABEL.get(cat, cat.upper())
    slug = article.get('slug', '')
    headline = article.get('headline', '')
    subheadline = article.get('subheadline', '')
    
    summary_text, full_text = extract_summary_and_takeaways(article)
    
    # Build post
    post = f"""{emoji} {label} | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

{headline.upper()}

{summary_text}

━━━━━━━━━━━━━━━━━━━━━━━━

📰 Full story: thevideshi.com/articles/{slug}

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""
    
    # Ensure we're within 4000 chars
    if len(post) > 3900:
        # Trim summary
        excess = len(post) - 3800
        summary_text = summary_text[:len(summary_text) - excess] + '…'
        post = f"""{emoji} {label} | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

{headline.upper()}

{summary_text}

━━━━━━━━━━━━━━━━━━━━━━━━

📰 Full story: thevideshi.com/articles/{slug}

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""
    
    return post


# --- Post articles ---
log_path = os.path.expanduser('~/workspace/the-videshi-news/pipeline/tweet-log.json')
tweet_log = {}
if os.path.exists(log_path):
    with open(log_path) as f:
        tweet_log = json.load(f)

posted = 0
errors = []
tweet_urls = []

for i, article in enumerate(to_post):
    try:
        post_text = compose_post(article)
        print(f"\n--- Article {i+1}/{len(to_post)}: {article['headline'][:80]} ---")
        print(f"Post length: {len(post_text)} chars")
        
        # Try to attach image
        media_id = None
        image_url = article.get('image_url', '')
        if image_url:
            try:
                img_resp = requests.get(image_url, timeout=15)
                img_resp.raise_for_status()
                
                # Determine extension from content type
                ct = img_resp.headers.get('content-type', 'image/jpeg')
                ext = '.jpg'
                if 'png' in ct:
                    ext = '.png'
                elif 'webp' in ct:
                    ext = '.webp'
                elif 'gif' in ct:
                    ext = '.gif'
                
                with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
                    tmp.write(img_resp.content)
                    tmp_path = tmp.name
                
                media = api_v1.media_upload(filename=tmp_path)
                media_id = media.media_id
                os.unlink(tmp_path)
                print(f"Image uploaded: media_id={media_id}")
            except Exception as e:
                print(f"Image upload failed (posting without image): {e}")
                if 'tmp_path' in locals() and os.path.exists(tmp_path):
                    os.unlink(tmp_path)
        
        # Post tweet
        kwargs = {'text': post_text}
        if media_id:
            kwargs['media_ids'] = [media_id]
        
        tweet_resp = client.create_tweet(**kwargs)
        tweet_id = tweet_resp.data['id']
        tweet_url = f"https://x.com/thevideshi/status/{tweet_id}"
        print(f"✅ Posted: {tweet_url}")
        tweet_urls.append(tweet_url)
        
        # Update Supabase
        patch_resp = requests.patch(
            f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article['id']}",
            headers={
                'apikey': SUPABASE_KEY,
                'Authorization': f'Bearer {SUPABASE_KEY}',
                'Content-Type': 'application/json',
                'Prefer': 'return=minimal',
            },
            json={'tweeted_at': datetime.now(timezone.utc).isoformat()},
        )
        patch_resp.raise_for_status()
        print(f"Supabase updated: tweeted_at set for {article['id']}")
        
        # Log tweet
        tweet_log[str(tweet_id)] = {
            'article_id': article['id'],
            'slug': article['slug'],
            'posted_at': datetime.now(timezone.utc).isoformat() + 'Z',
        }
        with open(log_path, 'w') as f:
            json.dump(tweet_log, f, indent=2)
        
        posted += 1
        
        # Wait between posts
        if i < len(to_post) - 1:
            print("Waiting 30 seconds...")
            time.sleep(30)
    
    except Exception as e:
        err_msg = f"Error posting '{article.get('headline', '?')[:60]}': {e}"
        print(f"❌ {err_msg}")
        errors.append(err_msg)

# --- Summary ---
print(f"\n{'='*50}")
print(f"SUMMARY: Posted {posted}/{len(to_post)} articles")
if tweet_urls:
    print("Tweet URLs:")
    for url in tweet_urls:
        print(f"  {url}")
if errors:
    print("Errors:")
    for e in errors:
        print(f"  {e}")
