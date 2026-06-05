#!/usr/bin/env python3
"""Post recently published Videshi articles to X as long-form posts with images."""

import json, os, sys, time, tempfile, re
from datetime import datetime, timezone

import requests
import tweepy

# --- Config ---
SUPABASE_URL = 'https://lboecaekpynbpyijrbfz.supabase.co'
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
TWITTER_CONSUMER_KEY = os.environ.get('TWITTER_CONSUMER_KEY', '')
TWITTER_CONSUMER_SECRET = os.environ.get('TWITTER_CONSUMER_SECRET', '')
TWITTER_ACCESS_TOKEN = os.environ.get('TWITTER_ACCESS_TOKEN', '')
TWITTER_ACCESS_TOKEN_SECRET = os.environ.get('TWITTER_ACCESS_TOKEN_SECRET', '')

MAX_POSTS = 4
DELAY_BETWEEN_POSTS = 30

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

TWEET_LOG_PATH = os.path.expanduser("~/workspace/the-videshi-news/pipeline/tweet-log.json")

def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                os.environ[k.strip()] = v.strip()

def supabase_headers():
    return {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal'
    }

def fetch_untweeted_articles():
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json'
    }
    resp = requests.get(
        f'{SUPABASE_URL}/rest/v1/p2_articles',
        headers=headers,
        params={
            'status': 'eq.published',
            'tweeted_at': 'is.null',
            'order': 'published_at.desc',
            'limit': '20',
            'select': 'id,slug,headline,subheadline,category,tags,image_url,body'
        }
    )
    resp.raise_for_status()
    return resp.json()

def strip_markdown(text):
    """Strip markdown formatting to plain text."""
    if not text:
        return ''
    # Remove images
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    # Remove links but keep text
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    # Remove headers
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    # Remove bold/italic
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    text = re.sub(r'__([^_]+)__', r'\1', text)
    # Remove blockquotes
    text = re.sub(r'^>\s*', '', text, flags=re.MULTILINE)
    # Remove horizontal rules
    text = re.sub(r'^[-*_]{3,}\s*$', '', text, flags=re.MULTILINE)
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Collapse whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def extract_key_facts(body_text, subheadline):
    """Extract key facts from article body - pull notable numbers, names, dates."""
    # Get clean paragraphs
    paragraphs = [p.strip() for p in body_text.split('\n\n') if p.strip() and len(p.strip()) > 40]
    
    # Look for sentences with numbers, percentages, dollar amounts - these are usually key facts
    fact_sentences = []
    for para in paragraphs:
        sentences = re.split(r'(?<=[.!?])\s+', para)
        for sent in sentences:
            # Prioritize sentences with hard facts
            if re.search(r'\$[\d,]+|\d+\s*(?:percent|%|billion|million|crore|lakh)', sent, re.I):
                fact_sentences.append(sent.strip())
            elif re.search(r'\d{4}|\d+,\d{3}', sent) and len(sent) < 200:
                fact_sentences.append(sent.strip())
    
    return fact_sentences[:8]  # Return up to 8 candidate facts

def compose_long_post(article):
    """Compose a long-form X post from an article."""
    cat = article.get('category', 'news')
    emoji = CATEGORY_EMOJI.get(cat, '📰')
    cat_label = cat.upper().replace('-', ' ')
    headline = article.get('headline', '')
    subheadline = article.get('subheadline', '')
    slug = article.get('slug', '')
    body = strip_markdown(article.get('body', ''))
    
    # Get first ~600 words of body for summary material
    words = body.split()
    summary_source = ' '.join(words[:600]) if len(words) > 600 else body
    
    # Extract key paragraphs (skip very short ones)
    paragraphs = [p.strip() for p in summary_source.split('\n\n') if len(p.strip()) > 50]
    
    # Build 2-3 paragraph summary from article content
    summary_paras = []
    total_words = 0
    for p in paragraphs[:5]:
        p_words = len(p.split())
        if total_words + p_words > 250:
            break
        summary_paras.append(p)
        total_words += p_words
    
    if not summary_paras and paragraphs:
        summary_paras = [paragraphs[0][:500]]
    
    summary_text = '\n\n'.join(summary_paras)
    
    # Extract key facts
    fact_candidates = extract_key_facts(body, subheadline)
    
    # Build key takeaways - use subheadline and fact sentences
    takeaways = []
    if subheadline and len(subheadline) < 150:
        takeaways.append(subheadline)
    for fact in fact_candidates:
        if len(fact) < 150 and fact not in takeaways:
            takeaways.append(fact)
        if len(takeaways) >= 4:
            break
    
    # If still short on takeaways, extract from first paragraphs
    if len(takeaways) < 3:
        for p in paragraphs[:3]:
            sentences = re.split(r'(?<=[.!?])\s+', p)
            for s in sentences:
                s = s.strip()
                if 30 < len(s) < 150 and s not in takeaways:
                    takeaways.append(s)
                if len(takeaways) >= 4:
                    break
            if len(takeaways) >= 4:
                break
    
    takeaways = takeaways[:4]
    
    # Compose the post
    takeaway_lines = '\n'.join(f'▸ {t}' for t in takeaways)
    
    post = f"""{emoji} {cat_label} | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

{headline.upper() if len(headline) < 100 else headline}

{summary_text}

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
        summary_text = summary_text[:1500] + '...'
        post = f"""{emoji} {cat_label} | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

{headline.upper() if len(headline) < 100 else headline}

{summary_text}

━━━━━━━━━━━━━━━━━━━━━━━━

Key Takeaways:

{takeaway_lines}

━━━━━━━━━━━━━━━━━━━━━━━━

📰 Full story: thevideshi.com/articles/{slug}

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""
    
    return post

def download_image(image_url):
    """Download article image to temp file. Returns path or None."""
    if not image_url:
        return None
    try:
        resp = requests.get(image_url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=15)
        resp.raise_for_status()
        
        # Determine extension from content-type
        ct = resp.headers.get('Content-Type', '')
        ext = '.jpg'
        if 'png' in ct:
            ext = '.png'
        elif 'webp' in ct:
            ext = '.webp'
        elif 'gif' in ct:
            ext = '.gif'
        
        tmp = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
        tmp.write(resp.content)
        tmp.close()
        
        # Verify file size > 1KB (not an error page)
        if os.path.getsize(tmp.name) < 1024:
            os.unlink(tmp.name)
            return None
        
        return tmp.name
    except Exception as e:
        print(f"  ⚠ Image download failed: {e}")
        return None

def post_to_x(client, api_v1, text, image_path=None):
    """Post a tweet with optional image. Returns tweet response."""
    media_ids = None
    if image_path:
        try:
            media = api_v1.media_upload(filename=image_path)
            media_ids = [media.media_id]
            print(f"  ✓ Image uploaded (media_id: {media.media_id})")
        except Exception as e:
            print(f"  ⚠ Image upload failed, posting without: {e}")
            media_ids = None
    
    response = client.create_tweet(text=text, media_ids=media_ids)
    return response

def update_supabase(article_id):
    """Mark article as tweeted in Supabase."""
    now = datetime.now(timezone.utc).isoformat()
    resp = requests.patch(
        f'{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article_id}',
        headers=supabase_headers(),
        json={'tweeted_at': now}
    )
    resp.raise_for_status()
    return now

def log_tweet(tweet_id, article):
    """Log tweet ID locally."""
    tweet_log = {}
    if os.path.exists(TWEET_LOG_PATH):
        try:
            tweet_log = json.load(open(TWEET_LOG_PATH))
        except:
            tweet_log = {}
    
    tweet_log[str(tweet_id)] = {
        "article_id": article['id'],
        "slug": article['slug'],
        "posted_at": datetime.now(timezone.utc).isoformat() + "Z"
    }
    
    os.makedirs(os.path.dirname(TWEET_LOG_PATH), exist_ok=True)
    with open(TWEET_LOG_PATH, 'w') as f:
        json.dump(tweet_log, f, indent=2)

def main():
    # Load environment
    load_env(os.path.expanduser('~/workspace/.env.twitter'))
    load_env(os.path.expanduser('~/workspace/.env.supabase'))
    
    # Re-read after loading env files
    global SUPABASE_KEY, TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET
    SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
    TWITTER_CONSUMER_KEY = os.environ.get('TWITTER_CONSUMER_KEY', '')
    TWITTER_CONSUMER_SECRET = os.environ.get('TWITTER_CONSUMER_SECRET', '')
    TWITTER_ACCESS_TOKEN = os.environ.get('TWITTER_ACCESS_TOKEN', '')
    TWITTER_ACCESS_TOKEN_SECRET = os.environ.get('TWITTER_ACCESS_TOKEN_SECRET', '')
    
    if not all([SUPABASE_KEY, TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET]):
        print("ERROR: Missing required environment variables")
        sys.exit(1)
    
    # Init tweepy clients
    client = tweepy.Client(
        consumer_key=TWITTER_CONSUMER_KEY,
        consumer_secret=TWITTER_CONSUMER_SECRET,
        access_token=TWITTER_ACCESS_TOKEN,
        access_token_secret=TWITTER_ACCESS_TOKEN_SECRET
    )
    
    auth = tweepy.OAuth1UserHandler(
        TWITTER_CONSUMER_KEY,
        TWITTER_CONSUMER_SECRET,
        TWITTER_ACCESS_TOKEN,
        TWITTER_ACCESS_TOKEN_SECRET
    )
    api_v1 = tweepy.API(auth)
    
    # Fetch articles
    print("Fetching untweeted articles...")
    articles = fetch_untweeted_articles()
    print(f"Found {len(articles)} untweeted articles")
    
    # Filter to those with images, pick top 4
    eligible = [a for a in articles if a.get('image_url')]
    print(f"Eligible (with images): {len(eligible)}")
    
    to_post = eligible[:MAX_POSTS]
    if not to_post:
        print("No articles to post.")
        return
    
    print(f"\nPosting {len(to_post)} articles to X...\n")
    
    posted = 0
    errors = []
    
    for i, article in enumerate(to_post):
        print(f"--- Article {i+1}/{len(to_post)} ---")
        print(f"  Headline: {article['headline'][:80]}...")
        print(f"  Category: {article['category']}")
        print(f"  Slug: {article['slug']}")
        
        # Compose post
        post_text = compose_long_post(article)
        print(f"  Post length: {len(post_text)} chars")
        
        # Download image
        img_path = download_image(article.get('image_url'))
        if img_path:
            print(f"  ✓ Image downloaded: {os.path.getsize(img_path)} bytes")
        
        try:
            # Post to X
            response = post_to_x(client, api_v1, post_text, img_path)
            tweet_id = response.data['id']
            tweet_url = f"https://x.com/thevideshi/status/{tweet_id}"
            print(f"  ✓ Posted! {tweet_url}")
            
            # Update Supabase
            ts = update_supabase(article['id'])
            print(f"  ✓ Supabase updated (tweeted_at: {ts})")
            
            # Log tweet
            log_tweet(tweet_id, article)
            print(f"  ✓ Tweet logged")
            
            posted += 1
            
        except Exception as e:
            err_msg = str(e)
            print(f"  ✗ Error posting: {err_msg}")
            errors.append({"headline": article['headline'][:60], "error": err_msg})
        finally:
            # Cleanup temp image
            if img_path and os.path.exists(img_path):
                os.unlink(img_path)
        
        # Wait between posts
        if i < len(to_post) - 1:
            print(f"  Waiting {DELAY_BETWEEN_POSTS}s...")
            time.sleep(DELAY_BETWEEN_POSTS)
    
    # Summary
    print(f"\n{'='*50}")
    print(f"SUMMARY: Posted {posted}/{len(to_post)} articles to X")
    if errors:
        print(f"Errors ({len(errors)}):")
        for e in errors:
            print(f"  - {e['headline']}: {e['error']}")
    print(f"{'='*50}")

if __name__ == '__main__':
    main()
