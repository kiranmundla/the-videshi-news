#!/usr/bin/env python3
"""Post recently published Videshi articles to X as long-form Premium posts."""

import json, os, sys, time, tempfile, re
import requests
import tweepy
from datetime import datetime

# --- Config ---
SUPABASE_URL = 'https://lboecaekpynbpyijrbfz.supabase.co'
MAX_POSTS = 4
POST_DELAY = 30  # seconds between posts

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
supabase_env = load_env('~/workspace/.env.supabase')

CONSUMER_KEY = twitter_env['TWITTER_CONSUMER_KEY']
CONSUMER_SECRET = twitter_env['TWITTER_CONSUMER_SECRET']
ACCESS_TOKEN = twitter_env['TWITTER_ACCESS_TOKEN']
ACCESS_TOKEN_SECRET = twitter_env['TWITTER_ACCESS_TOKEN_SECRET']
SUPABASE_KEY = supabase_env['SUPABASE_SERVICE_ROLE_KEY']

sb_headers = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json'
}

# --- Twitter clients ---
client = tweepy.Client(
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET
)

auth = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api_v1 = tweepy.API(auth)

# --- Category emoji mapping ---
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

def clean_markdown(text):
    """Strip markdown formatting for plain text."""
    if not text:
        return ''
    # Remove images
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    # Remove links but keep text
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    # Remove headers
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    # Remove bold/italic markers
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    # Remove horizontal rules
    text = re.sub(r'^[-*_]{3,}\s*$', '', text, flags=re.MULTILINE)
    # Remove blockquotes
    text = re.sub(r'^>\s?', '', text, flags=re.MULTILINE)
    # Collapse multiple newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def extract_key_facts(body, subheadline):
    """Extract key sentences/facts from the article body for takeaways."""
    clean = clean_markdown(body)
    sentences = re.split(r'(?<=[.!?])\s+', clean)
    # Filter for sentences with numbers, names, or strong facts
    fact_sentences = []
    for s in sentences:
        s = s.strip()
        if len(s) < 20 or len(s) > 200:
            continue
        # Prefer sentences with numbers, percentages, dollar amounts, names
        if re.search(r'\d|%|\$|₹|billion|million|crore|lakh', s, re.I):
            fact_sentences.append(s)
        elif len(fact_sentences) < 6 and any(w in s.lower() for w in ['first', 'largest', 'record', 'announced', 'launched', 'according']):
            fact_sentences.append(s)
    
    # Also consider subheadline
    if subheadline:
        fact_sentences.insert(0, subheadline)
    
    return fact_sentences[:6]  # Return more than needed, we'll pick best 3-4

def compose_summary(body, headline):
    """Extract 2-3 paragraphs of engaging summary from article body."""
    clean = clean_markdown(body)
    paragraphs = [p.strip() for p in clean.split('\n\n') if p.strip() and len(p.strip()) > 50]
    
    if not paragraphs:
        return ''
    
    # Take first 2-3 substantive paragraphs (skip very short ones)
    summary_paras = []
    total_words = 0
    for p in paragraphs:
        words = len(p.split())
        if words < 15:
            continue
        summary_paras.append(p)
        total_words += words
        if total_words >= 150 or len(summary_paras) >= 3:
            break
    
    # Trim if too long - aim for 150-250 words
    result = '\n\n'.join(summary_paras)
    words = result.split()
    if len(words) > 280:
        # Cut to ~250 words at sentence boundary
        truncated = ' '.join(words[:260])
        last_period = truncated.rfind('.')
        if last_period > len(truncated) * 0.6:
            result = truncated[:last_period + 1]
    
    return result

def compose_post(article):
    """Compose a long-form X Premium post for an article."""
    cat = article.get('category', 'news')
    emoji = CATEGORY_EMOJI.get(cat, '📰')
    cat_label = cat.upper().replace('-', ' ')
    slug = article['slug']
    headline = article['headline']
    subheadline = article.get('subheadline', '')
    body = article.get('body', '')
    
    # Rewrite headline for X - punchier
    # Keep original but clean it up, make it title case if not already
    x_headline = headline.strip()
    if len(x_headline) > 120:
        # Truncate at natural break
        for sep in [' — ', ' – ', ': ', ', ']:
            idx = x_headline.find(sep, 60)
            if idx > 0 and idx < 120:
                x_headline = x_headline[:idx]
                break
    
    # Build summary from body
    summary = compose_summary(body, headline)
    
    # Extract key takeaways
    facts = extract_key_facts(body, subheadline)
    takeaways = facts[:4] if len(facts) >= 3 else facts[:3]
    
    # Format takeaways
    takeaway_lines = '\n'.join(f'▸ {t}' for t in takeaways)
    
    # Build the post
    post = f"""{emoji} {cat_label} | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

{x_headline}

{summary}

━━━━━━━━━━━━━━━━━━━━━━━━

Key Takeaways:

{takeaway_lines}

━━━━━━━━━━━━━━━━━━━━━━━━

📰 Full story: thevideshi.com/articles/{slug}

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""
    
    # Safety: ensure under 4000 chars
    if len(post) > 3900:
        # Trim summary
        summary_words = summary.split()
        while len(post) > 3800 and len(summary_words) > 80:
            summary_words = summary_words[:len(summary_words) - 20]
            trimmed = ' '.join(summary_words)
            last_period = trimmed.rfind('.')
            if last_period > 0:
                trimmed = trimmed[:last_period + 1]
            post = f"""{emoji} {cat_label} | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

{x_headline}

{trimmed}

━━━━━━━━━━━━━━━━━━━━━━━━

Key Takeaways:

{takeaway_lines}

━━━━━━━━━━━━━━━━━━━━━━━━

📰 Full story: thevideshi.com/articles/{slug}

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""
    
    return post

def upload_image(image_url):
    """Download and upload image to X, return media_id or None."""
    if not image_url:
        return None
    try:
        resp = requests.get(image_url, timeout=15)
        resp.raise_for_status()
        
        # Determine extension from content type
        ct = resp.headers.get('content-type', 'image/jpeg')
        ext = '.jpg'
        if 'png' in ct:
            ext = '.png'
        elif 'webp' in ct:
            ext = '.webp'
        elif 'gif' in ct:
            ext = '.gif'
        
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as f:
            f.write(resp.content)
            tmp_path = f.name
        
        media = api_v1.media_upload(filename=tmp_path)
        os.unlink(tmp_path)
        return media.media_id
    except Exception as e:
        print(f"  ⚠️ Image upload failed: {e}")
        try:
            os.unlink(tmp_path)
        except:
            pass
        return None

def update_supabase(article_id):
    """Mark article as tweeted in Supabase."""
    ts = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S') + 'Z'
    resp = requests.patch(
        f'{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article_id}',
        headers=sb_headers,
        json={'tweeted_at': ts}
    )
    return resp.status_code < 300

def log_tweet(tweet_id, article):
    """Log tweet ID locally."""
    log_path = os.path.expanduser('~/workspace/the-videshi-news/pipeline/tweet-log.json')
    tweet_log = {}
    if os.path.exists(log_path):
        with open(log_path) as f:
            tweet_log = json.load(f)
    
    tweet_log[str(tweet_id)] = {
        'article_id': article['id'],
        'slug': article['slug'],
        'posted_at': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S') + 'Z'
    }
    
    with open(log_path, 'w') as f:
        json.dump(tweet_log, f, indent=2)

# --- Main ---
def main():
    # Fetch untweeted articles
    resp = requests.get(
        f'{SUPABASE_URL}/rest/v1/p2_articles',
        headers=sb_headers,
        params={
            'status': 'eq.published',
            'tweeted_at': 'is.null',
            'order': 'published_at.desc',
            'limit': '20',
            'select': 'id,slug,headline,subheadline,category,tags,image_url,body'
        }
    )
    articles = resp.json()
    print(f"Found {len(articles)} untweeted articles")
    
    # Filter: must have image_url
    articles_with_img = [a for a in articles if a.get('image_url')]
    print(f"With images: {len(articles_with_img)}")
    
    # Pick top 4
    to_post = articles_with_img[:MAX_POSTS]
    if not to_post:
        print("No articles to post.")
        return
    
    print(f"\nPosting {len(to_post)} articles to X...\n")
    
    posted = 0
    errors = []
    
    for i, article in enumerate(to_post):
        print(f"--- [{i+1}/{len(to_post)}] {article['headline'][:70]}...")
        
        # Compose post
        post_text = compose_post(article)
        print(f"  Post length: {len(post_text)} chars")
        
        # Upload image
        media_id = upload_image(article.get('image_url'))
        if media_id:
            print(f"  ✅ Image uploaded (media_id: {media_id})")
        
        # Post tweet
        try:
            kwargs = {'text': post_text}
            if media_id:
                kwargs['media_ids'] = [media_id]
            
            response = client.create_tweet(**kwargs)
            tweet_id = response.data['id']
            tweet_url = f"https://x.com/thevideshi/status/{tweet_id}"
            print(f"  ✅ Posted: {tweet_url}")
            
            # Update Supabase
            if update_supabase(article['id']):
                print(f"  ✅ Supabase updated (tweeted_at set)")
            else:
                print(f"  ⚠️ Supabase update may have failed")
            
            # Log locally
            log_tweet(tweet_id, article)
            print(f"  ✅ Logged to tweet-log.json")
            
            posted += 1
            
        except Exception as e:
            err_msg = str(e)
            print(f"  ❌ Error: {err_msg}")
            errors.append({'article': article['headline'][:60], 'error': err_msg})
        
        # Wait between posts
        if i < len(to_post) - 1:
            print(f"  ⏳ Waiting {POST_DELAY}s...")
            time.sleep(POST_DELAY)
    
    # Summary
    print(f"\n{'='*50}")
    print(f"SUMMARY: {posted}/{len(to_post)} articles posted to X")
    if errors:
        print(f"Errors ({len(errors)}):")
        for e in errors:
            print(f"  - {e['article']}: {e['error']}")
    print(f"{'='*50}")

if __name__ == '__main__':
    main()
