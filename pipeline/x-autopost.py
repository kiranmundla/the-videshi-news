#!/usr/bin/env python3
"""Post up to 4 recent Videshi articles to X as long-form premium posts with images."""

import os, json, time, tempfile, requests, tweepy
from datetime import datetime

# --- Load env ---
def load_env(path):
    env = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip()
    return env

tw_env = load_env('~/workspace/.env.twitter')
sb_env = load_env('~/workspace/.env.supabase')

CONSUMER_KEY = tw_env['TWITTER_CONSUMER_KEY']
CONSUMER_SECRET = tw_env['TWITTER_CONSUMER_SECRET']
ACCESS_TOKEN = tw_env['TWITTER_ACCESS_TOKEN']
ACCESS_TOKEN_SECRET = tw_env['TWITTER_ACCESS_TOKEN_SECRET']
SUPABASE_KEY = sb_env['SUPABASE_SERVICE_ROLE_KEY']
SUPABASE_URL = 'https://lboecaekpynbpyijrbfz.supabase.co'

# --- Category emoji map ---
EMOJI = {
    'news': '🇮🇳', 'immigration': '🛂', 'nri-world': '🌏',
    'travel': '✈️', 'lifestyle': '🧘', 'markets': '📈',
    'technology': '💻', 'sports': '🏏', 'entertainment': '🎬', 'food': '🍛'
}

CATEGORY_LABELS = {
    'news': 'NEWS', 'immigration': 'IMMIGRATION', 'nri-world': 'NRI WORLD',
    'travel': 'TRAVEL', 'lifestyle': 'LIFESTYLE & HEALTH', 'markets': 'MARKETS & FINANCE',
    'technology': 'TECHNOLOGY', 'sports': 'SPORTS', 'entertainment': 'ENTERTAINMENT', 'food': 'FOOD'
}

# --- Fetch articles ---
resp = requests.get(
    f'{SUPABASE_URL}/rest/v1/p2_articles',
    params={
        'status': 'eq.published',
        'tweeted_at': 'is.null',
        'order': 'published_at.desc',
        'limit': '20',
        'select': 'id,slug,headline,subheadline,category,tags,image_url,body'
    },
    headers={'apikey': SUPABASE_KEY, 'Authorization': f'Bearer {SUPABASE_KEY}'}
)
articles = resp.json()
print(f"Found {len(articles)} untweeted articles")

# Filter: must have image_url, pick top 4
candidates = [a for a in articles if a.get('image_url')][:4]
print(f"Selected {len(candidates)} articles to post")

if not candidates:
    print("No articles to post. Done.")
    exit(0)

# --- Setup tweepy ---
client = tweepy.Client(
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET
)
auth = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api_v1 = tweepy.API(auth)

# --- Compose post ---
def compose_post(article):
    cat = article.get('category', 'news')
    emoji = EMOJI.get(cat, '📰')
    label = CATEGORY_LABELS.get(cat, cat.upper())
    headline = article['headline']
    slug = article['slug']
    body = article.get('body', '') or ''
    subheadline = article.get('subheadline', '') or ''
    
    # Extract key content from body (strip markdown formatting)
    import re
    # Remove markdown headers, images, links formatting
    clean = re.sub(r'!\[.*?\]\(.*?\)', '', body)
    clean = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', clean)
    clean = re.sub(r'#{1,6}\s+', '', clean)
    clean = re.sub(r'\*\*([^*]+)\*\*', r'\1', clean)
    clean = re.sub(r'\*([^*]+)\*', r'\1', clean)
    clean = re.sub(r'<[^>]+>', '', clean)
    clean = re.sub(r'\n{3,}', '\n\n', clean)
    
    # Get paragraphs
    paragraphs = [p.strip() for p in clean.split('\n\n') if p.strip() and len(p.strip()) > 40]
    
    # Build summary from first few substantial paragraphs
    summary_parts = []
    total_len = 0
    for p in paragraphs[:6]:
        if total_len + len(p) > 800:
            break
        summary_parts.append(p)
        total_len += len(p)
    
    summary = '\n\n'.join(summary_parts[:3])
    
    # Truncate summary if still too long
    if len(summary) > 700:
        summary = summary[:697] + '...'
    
    # Extract key takeaways - look for strong facts with numbers, names, outcomes
    takeaways = []
    for p in paragraphs:
        # Prefer sentences with numbers, percentages, dollar amounts, or key names
        sentences = re.split(r'(?<=[.!?])\s+', p)
        for s in sentences:
            if len(s) > 30 and len(s) < 200 and any(c.isdigit() for c in s):
                takeaways.append(s.strip())
            if len(takeaways) >= 6:
                break
        if len(takeaways) >= 6:
            break
    
    # If not enough number-based takeaways, add from subheadline
    if subheadline and len(takeaways) < 3:
        takeaways.insert(0, subheadline)
    
    # Ensure 3-4 takeaways, trim to fit
    takeaways = takeaways[:4]
    takeaway_lines = '\n'.join(f'▸ {t}' for t in takeaways) if takeaways else ''
    
    # Build post
    post = f"""{emoji} {label} | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

{headline}

{summary}"""
    
    if takeaway_lines:
        post += f"""

━━━━━━━━━━━━━━━━━━━━━━━━

Key Takeaways:

{takeaway_lines}"""
    
    post += f"""

━━━━━━━━━━━━━━━━━━━━━━━━

📰 Full story: thevideshi.com/articles/{slug}

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""
    
    # Ensure under 4000 chars
    if len(post) > 3900:
        # Trim summary
        over = len(post) - 3800
        summary = summary[:len(summary) - over - 3] + '...'
        # Rebuild
        post = f"""{emoji} {label} | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

{headline}

{summary}"""
        if takeaway_lines:
            post += f"""

━━━━━━━━━━━━━━━━━━━━━━━━

Key Takeaways:

{takeaway_lines}"""
        post += f"""

━━━━━━━━━━━━━━━━━━━━━━━━

📰 Full story: thevideshi.com/articles/{slug}

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""
    
    return post

# --- Post loop ---
log_path = os.path.expanduser('~/workspace/the-videshi-news/pipeline/tweet-log.json')
tweet_log = json.load(open(log_path)) if os.path.exists(log_path) else {}

posted = 0
errors = []

for i, article in enumerate(candidates):
    slug = article['slug']
    headline = article['headline']
    print(f"\n--- Article {i+1}/{len(candidates)}: {headline[:60]}...")
    
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
                    ct = img_resp.headers.get('content-type', '')
                    ext = '.jpg'
                    if 'png' in ct: ext = '.png'
                    elif 'webp' in ct: ext = '.webp'
                    elif 'gif' in ct: ext = '.gif'
                    
                    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
                        tmp.write(img_resp.content)
                        tmp_path = tmp.name
                    
                    media = api_v1.media_upload(filename=tmp_path)
                    media_id = media.media_id
                    os.unlink(tmp_path)
                    print(f"  Image uploaded: media_id={media_id}")
                else:
                    print(f"  Image download failed: HTTP {img_resp.status_code}")
            except Exception as e:
                print(f"  Image upload error: {e}")
                if 'tmp_path' in locals() and os.path.exists(tmp_path):
                    os.unlink(tmp_path)
        
        # Post tweet
        tweet_kwargs = {'text': post_text}
        if media_id:
            tweet_kwargs['media_ids'] = [media_id]
        
        response = client.create_tweet(**tweet_kwargs)
        tweet_id = response.data['id']
        tweet_url = f"https://x.com/thevideshi/status/{tweet_id}"
        print(f"  ✅ Posted: {tweet_url}")
        
        # Update Supabase
        now_utc = datetime.utcnow().isoformat() + 'Z'
        patch_resp = requests.patch(
            f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article['id']}",
            json={'tweeted_at': now_utc},
            headers={
                'apikey': SUPABASE_KEY,
                'Authorization': f'Bearer {SUPABASE_KEY}',
                'Content-Type': 'application/json',
                'Prefer': 'return=minimal'
            }
        )
        print(f"  Supabase updated: {patch_resp.status_code}")
        
        # Log locally
        tweet_log[str(tweet_id)] = {
            'article_id': article['id'],
            'slug': slug,
            'posted_at': now_utc
        }
        with open(log_path, 'w') as f:
            json.dump(tweet_log, f, indent=2)
        
        posted += 1
        
        # Wait between posts
        if i < len(candidates) - 1:
            print("  Waiting 30s...")
            time.sleep(30)
    
    except Exception as e:
        err_msg = f"{headline[:50]}: {e}"
        errors.append(err_msg)
        print(f"  ❌ Error: {e}")

# --- Summary ---
print(f"\n{'='*50}")
print(f"SUMMARY: Posted {posted}/{len(candidates)} articles to X")
if errors:
    print(f"Errors ({len(errors)}):")
    for e in errors:
        print(f"  - {e}")
print("Done.")
