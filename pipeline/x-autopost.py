#!/usr/bin/env python3
"""Post recent Videshi articles to X as long-form premium posts with images."""

import os, json, time, tempfile, re, requests, tweepy
from datetime import datetime, timezone

# --- Config ---
SUPABASE_URL = 'https://lboecaekpynbpyijrbfz.supabase.co'
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
MAX_POSTS = 4
POST_DELAY = 30  # seconds between posts

CATEGORY_EMOJI = {
    'news': '🇮🇳', 'immigration': '🛂', 'nri-world': '🌏',
    'travel': '✈️', 'lifestyle': '🧘', 'markets': '📈',
    'technology': '💻', 'sports': '🏏', 'entertainment': '🎬', 'food': '🍛'
}

CATEGORY_LABEL = {
    'news': 'NEWS', 'immigration': 'IMMIGRATION', 'nri-world': 'NRI WORLD',
    'travel': 'TRAVEL', 'lifestyle': 'LIFESTYLE & HEALTH', 'markets': 'MARKETS & FINANCE',
    'technology': 'TECHNOLOGY', 'sports': 'SPORTS', 'entertainment': 'ENTERTAINMENT', 'food': 'FOOD'
}

# --- Auth ---
sb_headers = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json'
}

consumer_key = os.environ['TWITTER_CONSUMER_KEY']
consumer_secret = os.environ['TWITTER_CONSUMER_SECRET']
access_token = os.environ['TWITTER_ACCESS_TOKEN']
access_token_secret = os.environ['TWITTER_ACCESS_TOKEN_SECRET']

client = tweepy.Client(
    consumer_key=consumer_key, consumer_secret=consumer_secret,
    access_token=access_token, access_token_secret=access_token_secret
)
auth_v1 = tweepy.OAuth1UserHandler(consumer_key, consumer_secret, access_token, access_token_secret)
api_v1 = tweepy.API(auth_v1)

# --- Helpers ---
def strip_markdown(text):
    """Remove markdown formatting, keeping plain text."""
    if not text:
        return ''
    # Remove images
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    # Remove links but keep text
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    # Remove headers
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    # Remove bold/italic
    text = re.sub(r'\*{1,3}([^*]+)\*{1,3}', r'\1', text)
    text = re.sub(r'_{1,3}([^_]+)_{1,3}', r'\1', text)
    # Remove blockquotes
    text = re.sub(r'^>\s+', '', text, flags=re.MULTILINE)
    # Remove horizontal rules
    text = re.sub(r'^---+$', '', text, flags=re.MULTILINE)
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Collapse whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def extract_key_facts(body_text, subheadline):
    """Extract the most concrete facts (numbers, names, dates) from article."""
    # Split into sentences
    sentences = re.split(r'(?<=[.!?])\s+', body_text)
    # Prioritize sentences with numbers, dollar amounts, percentages
    fact_sentences = []
    for s in sentences:
        s = s.strip()
        if not s or len(s) < 20 or len(s) > 200:
            continue
        # Score based on concrete data
        score = 0
        if re.search(r'\$[\d,.]+', s): score += 3
        if re.search(r'\d+%', s): score += 3
        if re.search(r'\b\d{4}\b', s): score += 1  # years
        if re.search(r'\b\d+[,.]?\d*\s*(million|billion|crore|lakh|trillion)', s, re.I): score += 3
        if re.search(r'\b\d+', s): score += 1
        if score > 0:
            fact_sentences.append((score, s))
    
    fact_sentences.sort(key=lambda x: -x[0])
    facts = [s for _, s in fact_sentences[:4]]
    
    # If we don't have enough, pull from subheadline
    if len(facts) < 3 and subheadline:
        sub_parts = re.split(r'[.;]', subheadline)
        for p in sub_parts:
            p = p.strip()
            if p and len(p) > 15 and p not in facts:
                facts.append(p)
                if len(facts) >= 4:
                    break
    
    return facts[:4]

def compose_post(article):
    """Compose a long-form X post from article data."""
    cat = article.get('category', 'news')
    emoji = CATEGORY_EMOJI.get(cat, '📰')
    label = CATEGORY_LABEL.get(cat, cat.upper())
    headline = article['headline']
    slug = article['slug']
    subheadline = article.get('subheadline', '') or ''
    body = strip_markdown(article.get('body', '') or '')
    
    # Create a punchy rewritten headline
    # Take the original but make it more conversational/impactful
    punchy_headline = headline.upper() if len(headline) < 80 else headline
    
    # Extract opening paragraphs for summary (first 3-4 meaningful paragraphs)
    paragraphs = [p.strip() for p in body.split('\n\n') if p.strip() and len(p.strip()) > 40]
    
    # Build summary from first few paragraphs, targeting 150-250 words
    summary_parts = []
    word_count = 0
    for p in paragraphs[:6]:
        p_words = len(p.split())
        if word_count + p_words > 280:
            # Trim last paragraph if needed
            if word_count < 120:
                remaining = 250 - word_count
                words = p.split()[:remaining]
                summary_parts.append(' '.join(words) + '...')
            break
        summary_parts.append(p)
        word_count += p_words
        if word_count >= 150:
            break
    
    summary = '\n\n'.join(summary_parts)
    
    # If summary is too short, add more
    if word_count < 80 and subheadline:
        summary = subheadline + '\n\n' + summary
    
    # Extract key takeaways
    facts = extract_key_facts(body, subheadline)
    
    takeaways = ''
    if facts:
        takeaway_lines = [f'▸ {f}' for f in facts]
        takeaways = '\n'.join(takeaway_lines)
    
    # Compose full post
    post = f"""{emoji} {label} | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

{punchy_headline}

{summary}

━━━━━━━━━━━━━━━━━━━━━━━━

Key Takeaways:

{takeaways}

━━━━━━━━━━━━━━━━━━━━━━━━

📰 Full story: thevideshi.com/articles/{slug}

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""
    
    # Ensure within 4000 chars
    if len(post) > 3900:
        # Truncate summary
        over = len(post) - 3800
        summary = summary[:len(summary) - over] + '...'
        post = f"""{emoji} {label} | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

{punchy_headline}

{summary}

━━━━━━━━━━━━━━━━━━━━━━━━

Key Takeaways:

{takeaways}

━━━━━━━━━━━━━━━━━━━━━━━━

📰 Full story: thevideshi.com/articles/{slug}

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""
    
    return post

def upload_image(image_url):
    """Download and upload image to X, return media_id or None."""
    try:
        resp = requests.get(image_url, timeout=15)
        if resp.status_code != 200:
            print(f'  ⚠ Image download failed: HTTP {resp.status_code}')
            return None
        
        # Determine extension from content-type
        ct = resp.headers.get('content-type', 'image/jpeg')
        ext = '.jpg'
        if 'png' in ct: ext = '.png'
        elif 'webp' in ct: ext = '.webp'
        elif 'gif' in ct: ext = '.gif'
        
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as f:
            f.write(resp.content)
            tmp_path = f.name
        
        media = api_v1.media_upload(filename=tmp_path)
        os.unlink(tmp_path)
        return media.media_id
    except Exception as e:
        print(f'  ⚠ Image upload failed: {e}')
        try:
            os.unlink(tmp_path)
        except:
            pass
        return None

def update_supabase(article_id):
    """Mark article as tweeted in Supabase."""
    now = datetime.now(timezone.utc).isoformat()
    resp = requests.patch(
        f'{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article_id}',
        headers=sb_headers,
        json={'tweeted_at': now}
    )
    return resp.status_code in (200, 204)

def log_tweet(tweet_id, article):
    """Log tweet ID locally for future management."""
    log_path = os.path.expanduser('~/workspace/the-videshi-news/pipeline/tweet-log.json')
    tweet_log = {}
    if os.path.exists(log_path):
        with open(log_path) as f:
            tweet_log = json.load(f)
    
    tweet_log[str(tweet_id)] = {
        'article_id': article['id'],
        'slug': article['slug'],
        'posted_at': datetime.now(timezone.utc).isoformat() + 'Z'
    }
    
    with open(log_path, 'w') as f:
        json.dump(tweet_log, f, indent=2)

# --- Main ---
def main():
    print('=== The Videshi X Auto-Post ===')
    print(f'Time: {datetime.now(timezone.utc).isoformat()}Z\n')
    
    # Fetch untweeted articles
    resp = requests.get(
        f'{SUPABASE_URL}/rest/v1/p2_articles',
        params={
            'status': 'eq.published',
            'tweeted_at': 'is.null',
            'order': 'published_at.desc',
            'limit': '20',
            'select': 'id,slug,headline,subheadline,category,tags,image_url,body'
        },
        headers=sb_headers
    )
    
    if resp.status_code != 200:
        print(f'❌ Supabase fetch failed: {resp.status_code} {resp.text}')
        return
    
    articles = resp.json()
    print(f'Found {len(articles)} untweeted articles')
    
    # Filter: must have image_url
    eligible = [a for a in articles if a.get('image_url')]
    print(f'{len(eligible)} have images\n')
    
    if not eligible:
        print('No eligible articles to post.')
        return
    
    to_post = eligible[:MAX_POSTS]
    posted = 0
    errors = []
    
    for i, article in enumerate(to_post):
        print(f'--- Article {i+1}/{len(to_post)} ---')
        print(f'  Headline: {article["headline"][:80]}')
        print(f'  Category: {article["category"]}')
        print(f'  Slug: {article["slug"][:60]}')
        
        # Compose post
        post_text = compose_post(article)
        print(f'  Post length: {len(post_text)} chars')
        
        # Upload image
        media_id = None
        if article.get('image_url'):
            print(f'  Uploading image...')
            media_id = upload_image(article['image_url'])
            if media_id:
                print(f'  ✓ Image uploaded (media_id: {media_id})')
        
        # Post tweet
        try:
            kwargs = {'text': post_text}
            if media_id:
                kwargs['media_ids'] = [media_id]
            
            tweet_resp = client.create_tweet(**kwargs)
            tweet_id = tweet_resp.data['id']
            tweet_url = f'https://x.com/thevideshi/status/{tweet_id}'
            print(f'  ✓ Posted: {tweet_url}')
            
            # Update Supabase
            if update_supabase(article['id']):
                print(f'  ✓ Supabase updated')
            else:
                print(f'  ⚠ Supabase update may have failed')
            
            # Log locally
            log_tweet(tweet_id, article)
            print(f'  ✓ Logged to tweet-log.json')
            
            posted += 1
            
        except tweepy.errors.TooManyRequests as e:
            print(f'  ❌ Rate limited: {e}')
            errors.append((article['headline'][:50], 'Rate limited'))
            print('  Stopping to avoid further rate limits.')
            break
        except Exception as e:
            print(f'  ❌ Failed: {e}')
            errors.append((article['headline'][:50], str(e)))
        
        # Wait between posts
        if i < len(to_post) - 1:
            print(f'  Waiting {POST_DELAY}s...')
            time.sleep(POST_DELAY)
    
    print(f'\n=== Summary ===')
    print(f'Posted: {posted}/{len(to_post)}')
    if errors:
        print(f'Errors:')
        for headline, err in errors:
            print(f'  - {headline}: {err}')

if __name__ == '__main__':
    main()
