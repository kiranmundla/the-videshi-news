#!/usr/bin/env python3
"""Post recent Videshi articles to X as long-form posts with images."""

import json, os, sys, time, tempfile, requests
from datetime import datetime, timezone

# --- Load env ---
def load_env(path):
    env = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.startswith('export '):
                line = line[7:]
            k, _, v = line.partition('=')
            env[k.strip()] = v.strip()
    return env

twitter_env = load_env('~/workspace/.env.twitter')
supa_env = load_env('~/workspace/.env.supabase')

CONSUMER_KEY = twitter_env['TWITTER_CONSUMER_KEY']
CONSUMER_SECRET = twitter_env['TWITTER_CONSUMER_SECRET']
ACCESS_TOKEN = twitter_env['TWITTER_ACCESS_TOKEN']
ACCESS_TOKEN_SECRET = twitter_env['TWITTER_ACCESS_TOKEN_SECRET']

SUPABASE_URL = 'https://lboecaekpynbpyijrbfz.supabase.co'
SERVICE_KEY = supa_env['SUPABASE_SERVICE_ROLE_KEY']

SUPA_HEADERS = {
    'apikey': SERVICE_KEY,
    'Authorization': f'Bearer {SERVICE_KEY}',
    'Content-Type': 'application/json',
}

# --- Fetch untweeted articles ---
print("Fetching untweeted articles...")
resp = requests.get(
    f"{SUPABASE_URL}/rest/v1/p2_articles",
    params={
        'status': 'eq.published',
        'tweeted_at': 'is.null',
        'order': 'published_at.desc',
        'limit': '20',
        'select': 'id,slug,headline,subheadline,category,tags,image_url,body',
    },
    headers=SUPA_HEADERS,
    timeout=30,
)
resp.raise_for_status()
articles = resp.json()
print(f"Found {len(articles)} untweeted articles")

# Filter: must have image_url, pick up to 4
candidates = [a for a in articles if a.get('image_url')]
selected = candidates[:4]
print(f"Selected {len(selected)} articles to post (with images)")

if not selected:
    print("No articles to post. Done.")
    sys.exit(0)

# --- Category emoji mapping ---
EMOJI = {
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

def get_emoji(cat):
    if not cat:
        return '📰'
    cat_lower = cat.lower().strip()
    return EMOJI.get(cat_lower, '📰')

def get_label(cat):
    if not cat:
        return 'NEWS'
    return cat.upper().replace('-', ' ')

# --- Compose long-form post ---
def compose_post(article):
    cat = article.get('category', 'news')
    emoji = get_emoji(cat)
    label = get_label(cat)
    headline = article.get('headline', '')
    subheadline = article.get('subheadline', '')
    slug = article.get('slug', '')
    body = article.get('body', '') or ''
    
    # Extract key content from body (strip markdown formatting)
    body_clean = body.replace('##', '').replace('**', '').replace('*', '').replace('> ', '')
    # Get first ~1500 chars of body for source material
    body_excerpt = body_clean[:2000]
    
    # Build summary from body - take meaningful paragraphs
    paragraphs = [p.strip() for p in body_excerpt.split('\n\n') if p.strip() and len(p.strip()) > 40]
    
    # Build 2-3 paragraph summary (150-250 words)
    summary_parts = []
    word_count = 0
    for p in paragraphs[:5]:
        p_words = len(p.split())
        if word_count + p_words > 250:
            break
        summary_parts.append(p)
        word_count += p_words
    
    if not summary_parts and subheadline:
        summary_parts = [subheadline]
    elif not summary_parts:
        summary_parts = [headline]
    
    summary = '\n\n'.join(summary_parts[:3])
    
    # Extract key takeaways from body
    takeaways = []
    sentences = body_clean.replace('\n', ' ').split('.')
    for s in sentences:
        s = s.strip()
        if len(s) > 30 and len(s) < 200 and any(c.isdigit() for c in s):
            takeaways.append(s.strip() + '.')
            if len(takeaways) >= 4:
                break
    
    # If not enough number-based facts, grab interesting sentences
    if len(takeaways) < 3:
        for s in sentences:
            s = s.strip()
            if len(s) > 40 and len(s) < 180 and s not in [t.rstrip('.') for t in takeaways]:
                takeaways.append(s.strip() + '.')
                if len(takeaways) >= 4:
                    break
    
    takeaways = takeaways[:4]
    takeaway_text = '\n'.join(f'▸ {t}' for t in takeaways) if takeaways else ''
    
    # Compose post
    post = f"""{emoji} {label} | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

{headline.upper()}

{summary}

━━━━━━━━━━━━━━━━━━━━━━━━"""
    
    if takeaway_text:
        post += f"""

Key Takeaways:

{takeaway_text}

━━━━━━━━━━━━━━━━━━━━━━━━"""
    
    post += f"""

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

📰 Full story: thevideshi.com/articles/{slug}

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""
    
    return post

# --- Setup tweepy ---
import tweepy

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
log_path = os.path.expanduser("~/workspace/the-videshi-news/pipeline/tweet-log.json")
tweet_log = json.load(open(log_path)) if os.path.exists(log_path) else {}

posted = 0
errors = []
results = []

for i, article in enumerate(selected):
    slug = article.get('slug', 'unknown')
    headline = article.get('headline', 'Untitled')
    article_id = article['id']
    image_url = article.get('image_url', '')
    
    print(f"\n--- Article {i+1}/{len(selected)}: {headline[:80]} ---")
    
    # Compose post
    post_text = compose_post(article)
    print(f"Post length: {len(post_text)} chars")
    
    # Try to upload image
    media_id = None
    tmp_path = None
    if image_url:
        try:
            print(f"Downloading image: {image_url[:80]}...")
            img_resp = requests.get(image_url, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
            img_resp.raise_for_status()
            
            # Determine extension
            ct = img_resp.headers.get('content-type', 'image/jpeg')
            ext = '.jpg'
            if 'png' in ct:
                ext = '.png'
            elif 'webp' in ct:
                ext = '.webp'
            elif 'gif' in ct:
                ext = '.gif'
            
            tmp_fd, tmp_path = tempfile.mkstemp(suffix=ext)
            with os.fdopen(tmp_fd, 'wb') as f:
                f.write(img_resp.content)
            
            print(f"Uploading image to X ({len(img_resp.content)} bytes)...")
            media = api_v1.media_upload(filename=tmp_path)
            media_id = media.media_id
            print(f"Media uploaded: {media_id}")
        except Exception as e:
            print(f"Image upload failed: {e} — posting without image")
            media_id = None
    
    # Post tweet
    try:
        kwargs = {'text': post_text}
        if media_id:
            kwargs['media_ids'] = [media_id]
        
        tweet_resp = client.create_tweet(**kwargs)
        tweet_id = tweet_resp.data['id']
        tweet_url = f"https://x.com/thevideshi/status/{tweet_id}"
        print(f"✅ Posted: {tweet_url}")
        
        # Update Supabase
        now_utc = datetime.now(timezone.utc).isoformat()
        patch_resp = requests.patch(
            f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article_id}",
            headers=SUPA_HEADERS,
            json={'tweeted_at': now_utc},
            timeout=15,
        )
        if patch_resp.status_code < 300:
            print(f"✅ Supabase updated: tweeted_at = {now_utc}")
        else:
            print(f"⚠️ Supabase update failed: {patch_resp.status_code} {patch_resp.text}")
        
        # Log tweet
        tweet_log[str(tweet_id)] = {
            'article_id': article_id,
            'slug': slug,
            'posted_at': now_utc,
        }
        with open(log_path, 'w') as f:
            json.dump(tweet_log, f, indent=2)
        
        posted += 1
        results.append({'headline': headline, 'url': tweet_url})
        
    except Exception as e:
        err_msg = f"Failed to post '{headline[:60]}': {e}"
        print(f"❌ {err_msg}")
        errors.append(err_msg)
    
    # Clean up temp file
    if tmp_path and os.path.exists(tmp_path):
        os.remove(tmp_path)
    
    # Wait between posts
    if i < len(selected) - 1:
        print("Waiting 30s before next post...")
        time.sleep(30)

# --- Summary ---
print(f"\n{'='*50}")
print(f"SUMMARY: Posted {posted}/{len(selected)} articles")
for r in results:
    print(f"  ✅ {r['headline'][:70]} → {r['url']}")
if errors:
    print(f"\nErrors ({len(errors)}):")
    for e in errors:
        print(f"  ❌ {e}")
print(f"{'='*50}")
