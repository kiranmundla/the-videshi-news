#!/usr/bin/env python3
"""Auto-post recently published Videshi articles to X (@thevideshi) as long-form posts."""

import json
import os
import sys
import time
import tempfile
import requests
from datetime import datetime, timezone

import tweepy

# --- Load env ---
def load_env(path):
    env = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip()
    return env

twitter_env = load_env('~/workspace/.env.twitter')
supa_env = load_env('~/workspace/.env.supabase')

CONSUMER_KEY = twitter_env['TWITTER_CONSUMER_KEY']
CONSUMER_SECRET = twitter_env['TWITTER_CONSUMER_SECRET']
ACCESS_TOKEN = twitter_env['TWITTER_ACCESS_TOKEN']
ACCESS_TOKEN_SECRET = twitter_env['TWITTER_ACCESS_TOKEN_SECRET']

SUPABASE_URL = 'https://lboecaekpynbpyijrbfz.supabase.co'
SUPABASE_KEY = supa_env['SUPABASE_SERVICE_ROLE_KEY']

SUPA_HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
}

CATEGORY_EMOJI = {
    'news': '🇮🇳',
    'immigration': '🛂',
    'nri-world': '🌏',
    'travel': '✈️',
    'lifestyle': '🧘',
    'markets': '📈',
    'technology': '💻',
    'sports': '🏏',
    'entertainment': '🎬',
    'food': '🍛',
}

# --- Fetch untweeted articles ---
print("Fetching untweeted articles...")
resp = requests.get(
    f"{SUPABASE_URL}/rest/v1/p2_articles",
    headers=SUPA_HEADERS,
    params={
        'status': 'eq.published',
        'tweeted_at': 'is.null',
        'order': 'published_at.desc',
        'limit': '20',
        'select': 'id,slug,headline,subheadline,category,tags,image_url,body',
    },
    timeout=30,
)
resp.raise_for_status()
articles = resp.json()
print(f"Found {len(articles)} untweeted articles")

# Filter: must have image_url
articles_with_img = [a for a in articles if a.get('image_url')]
print(f"  {len(articles_with_img)} have images")

# Pick up to 4 newest
to_post = articles_with_img[:4]
if not to_post:
    print("No articles to post. Done.")
    sys.exit(0)

print(f"Will post {len(to_post)} articles\n")

# --- Compose long-form post ---
def compose_post(article):
    """Generate the long-form X post content from article data."""
    cat = (article.get('category') or 'news').lower()
    emoji = CATEGORY_EMOJI.get(cat, '📰')
    cat_label = cat.upper().replace('-', ' ')
    
    headline = article.get('headline', '')
    subheadline = article.get('subheadline', '')
    slug = article.get('slug', '')
    body = article.get('body', '') or ''
    
    # Extract key content from body (strip markdown formatting)
    body_clean = body.replace('**', '').replace('##', '').replace('###', '').replace('*', '')
    # Get first ~1500 chars for context
    body_excerpt = body_clean[:2000]
    
    # Build the post using article content
    # Extract sentences for summary
    sentences = []
    for para in body_clean.split('\n\n'):
        para = para.strip()
        if para and len(para) > 30 and not para.startswith('!') and not para.startswith('['):
            sentences.append(para)
    
    # Build summary from first few meaningful paragraphs
    summary_paras = []
    char_count = 0
    for s in sentences[:5]:
        if char_count + len(s) > 600:
            break
        summary_paras.append(s)
        char_count += len(s)
    
    summary = '\n\n'.join(summary_paras) if summary_paras else subheadline
    
    # Extract key facts for takeaways
    # Pull from subheadline and early body content
    takeaways = []
    if subheadline:
        takeaways.append(subheadline)
    for s in sentences[1:8]:
        # Look for sentences with numbers, names, or key facts
        if any(c.isdigit() for c in s) or len(s) < 150:
            clean = s.strip()
            if clean and clean not in takeaways and len(clean) < 200:
                takeaways.append(clean)
        if len(takeaways) >= 4:
            break
    
    # Trim takeaways to 3-4
    takeaways = takeaways[:4]
    takeaway_lines = '\n'.join(f'▸ {t}' for t in takeaways) if takeaways else '▸ Read the full story for details'
    
    post = f"""{emoji} {cat_label} | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

{headline.upper()}

{summary}

━━━━━━━━━━━━━━━━━━━━━━━━

Key Takeaways:

{takeaway_lines}

━━━━━━━━━━━━━━━━━━━━━━━━

📰 Full story: thevideshi.com/articles/{slug}

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""

    # Ensure under 4000 chars
    if len(post) > 3900:
        # Trim summary
        summary = summary[:400] + '...'
        post = f"""{emoji} {cat_label} | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

{headline.upper()}

{summary}

━━━━━━━━━━━━━━━━━━━━━━━━

Key Takeaways:

{takeaway_lines}

━━━━━━━━━━━━━━━━━━━━━━━━

📰 Full story: thevideshi.com/articles/{slug}

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""
    
    return post[:4000]

# --- Setup tweepy clients ---
# v2 client for posting tweets
client = tweepy.Client(
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET,
)

# v1.1 API for media upload
auth = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api_v1 = tweepy.API(auth)

# --- Post articles ---
posted = []
errors = []

for i, article in enumerate(to_post):
    slug = article.get('slug', 'unknown')
    headline = article.get('headline', 'Unknown')
    print(f"[{i+1}/{len(to_post)}] Posting: {headline[:60]}...")
    
    try:
        # Compose post
        post_text = compose_post(article)
        print(f"  Post length: {len(post_text)} chars")
        
        # Try to upload image
        media_id = None
        image_url = article.get('image_url', '')
        if image_url:
            try:
                img_resp = requests.get(image_url, timeout=15)
                if img_resp.status_code == 200:
                    # Determine extension
                    content_type = img_resp.headers.get('content-type', '')
                    ext = '.jpg'
                    if 'png' in content_type:
                        ext = '.png'
                    elif 'webp' in content_type:
                        ext = '.webp'
                    
                    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
                        tmp.write(img_resp.content)
                        tmp_path = tmp.name
                    
                    media = api_v1.media_upload(filename=tmp_path)
                    media_id = media.media_id
                    os.unlink(tmp_path)
                    print(f"  Image uploaded (media_id: {media_id})")
                else:
                    print(f"  Image download failed ({img_resp.status_code}), posting without image")
            except Exception as e:
                print(f"  Image upload error: {e}, posting without image")
                try:
                    os.unlink(tmp_path)
                except:
                    pass
        
        # Post tweet
        tweet_kwargs = {'text': post_text}
        if media_id:
            tweet_kwargs['media_ids'] = [media_id]
        
        tweet_resp = client.create_tweet(**tweet_kwargs)
        tweet_id = tweet_resp.data['id']
        tweet_url = f"https://x.com/thevideshi/status/{tweet_id}"
        print(f"  ✅ Posted: {tweet_url}")
        
        # Update Supabase tweeted_at
        now_utc = datetime.now(timezone.utc).isoformat()
        patch_resp = requests.patch(
            f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article['id']}",
            headers=SUPA_HEADERS,
            json={'tweeted_at': now_utc},
            timeout=15,
        )
        if patch_resp.status_code < 300:
            print(f"  Supabase updated (tweeted_at)")
        else:
            print(f"  ⚠️ Supabase update failed: {patch_resp.status_code} {patch_resp.text}")
        
        # Log tweet locally
        log_path = os.path.expanduser('~/workspace/the-videshi-news/pipeline/tweet-log.json')
        tweet_log = {}
        if os.path.exists(log_path):
            with open(log_path) as f:
                tweet_log = json.load(f)
        tweet_log[str(tweet_id)] = {
            'article_id': article['id'],
            'slug': slug,
            'posted_at': datetime.utcnow().isoformat() + 'Z',
        }
        with open(log_path, 'w') as f:
            json.dump(tweet_log, f, indent=2)
        
        posted.append({'headline': headline, 'tweet_url': tweet_url, 'slug': slug})
        
        # Wait between posts
        if i < len(to_post) - 1:
            print("  Waiting 30s...")
            time.sleep(30)
    
    except Exception as e:
        err_msg = str(e)
        print(f"  ❌ Error: {err_msg}")
        errors.append({'headline': headline, 'slug': slug, 'error': err_msg})

# --- Summary ---
print(f"\n{'='*50}")
print(f"SUMMARY: {len(posted)} posted, {len(errors)} errors")
for p in posted:
    print(f"  ✅ {p['headline'][:50]} → {p['tweet_url']}")
for e in errors:
    print(f"  ❌ {e['headline'][:50]} → {e['error'][:100]}")
print(f"{'='*50}")
