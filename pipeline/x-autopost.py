#!/usr/bin/env python3
"""Post recently published Videshi articles to X (@thevideshi) as long-form Premium posts."""

import json, os, sys, time, tempfile, re
import requests
import tweepy
from datetime import datetime

# --- Config ---
SUPABASE_URL = 'https://lboecaekpynbpyijrbfz.supabase.co'
MAX_POSTS = 4
POST_DELAY = 30  # seconds between posts

# Load env files
def load_env(path):
    env = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
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

# Category emoji mapping
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

def strip_markdown(text):
    """Strip markdown formatting to get clean text for X post."""
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
    text = re.sub(r'^[-*_]{3,}\s*$', '', text, flags=re.MULTILINE)
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Clean up whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def extract_key_facts(body_text, headline, subheadline):
    """Extract key facts from article body for takeaways."""
    lines = body_text.split('\n')
    facts = []
    
    # Look for sentences with numbers, names, or strong facts
    for line in lines:
        line = line.strip()
        if not line or len(line) < 20:
            continue
        # Prioritize lines with numbers, percentages, dollar amounts, dates
        if re.search(r'(\d+[%$₹]|\$\d|₹\d|\d{4}|\d+ (million|billion|crore|lakh|percent))', line):
            # Clean up and truncate
            fact = line[:200].strip()
            if fact not in facts:
                facts.append(fact)
    
    # Also extract from subheadline
    if subheadline:
        for part in subheadline.split('.'):
            part = part.strip()
            if len(part) > 15 and part not in facts:
                facts.append(part)
    
    return facts[:6]  # Return up to 6 candidates

def compose_post(article):
    """Compose a long-form X Premium post for the article."""
    category = (article.get('category') or 'news').lower()
    emoji = CATEGORY_EMOJI.get(category, '📰')
    cat_label = category.upper().replace('-', ' ')
    
    headline = article['headline']
    subheadline = article.get('subheadline', '')
    slug = article['slug']
    body = strip_markdown(article.get('body', ''))
    
    # Build summary from body — take first ~300 words, shape into 2-3 paragraphs
    sentences = re.split(r'(?<=[.!?])\s+', body)
    
    # Skip very short "sentences" and title-like fragments
    good_sentences = [s for s in sentences if len(s) > 25 and not s.isupper()]
    
    # Build 2-3 paragraphs of summary (~150-250 words)
    summary_sentences = []
    word_count = 0
    for s in good_sentences:
        words = len(s.split())
        if word_count + words > 250:
            break
        summary_sentences.append(s)
        word_count += words
        if word_count < 30:
            continue
    
    # Split into 2-3 paragraphs
    if len(summary_sentences) >= 4:
        mid = len(summary_sentences) // 2
        para1 = ' '.join(summary_sentences[:mid])
        para2 = ' '.join(summary_sentences[mid:])
        summary = f"{para1}\n\n{para2}"
    else:
        summary = ' '.join(summary_sentences)
    
    # If summary is too short, use subheadline as supplement
    if len(summary) < 100 and subheadline:
        summary = f"{subheadline}\n\n{summary}" if summary else subheadline
    
    # Extract key takeaways
    facts = extract_key_facts(body, headline, subheadline)
    takeaways = []
    for f in facts[:4]:
        # Truncate long facts
        if len(f) > 120:
            f = f[:117] + '...'
        takeaways.append(f"▸ {f}")
    
    # If we don't have enough facts, try to extract from summary
    if len(takeaways) < 3:
        for s in good_sentences:
            if len(takeaways) >= 3:
                break
            candidate = s.strip()
            if len(candidate) > 30 and candidate not in [t[2:] for t in takeaways]:
                if len(candidate) > 120:
                    candidate = candidate[:117] + '...'
                takeaways.append(f"▸ {candidate}")
    
    takeaway_block = '\n'.join(takeaways[:4])
    
    # Make headline punchier — title case, remove trailing periods
    punchy_headline = headline.rstrip('.')
    
    post = f"""{emoji} {cat_label} | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

{punchy_headline}

{summary}

━━━━━━━━━━━━━━━━━━━━━━━━

Key Takeaways:

{takeaway_block}

━━━━━━━━━━━━━━━━━━━━━━━━

📰 Full story: thevideshi.com/articles/{slug}

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""
    
    # Ensure under 4000 chars
    if len(post) > 3900:
        # Trim summary
        summary = summary[:summary.rfind('.', 0, len(summary) - 200) + 1]
        post = f"""{emoji} {cat_label} | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

{punchy_headline}

{summary}

━━━━━━━━━━━━━━━━━━━━━━━━

Key Takeaways:

{takeaway_block}

━━━━━━━━━━━━━━━━━━━━━━━━

📰 Full story: thevideshi.com/articles/{slug}

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""
    
    return post[:4000]

def download_image(url):
    """Download image to temp file, return path or None."""
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        # Determine extension
        ct = r.headers.get('content-type', 'image/jpeg')
        ext = '.jpg'
        if 'png' in ct:
            ext = '.png'
        elif 'webp' in ct:
            ext = '.webp'
        elif 'gif' in ct:
            ext = '.gif'
        
        tmp = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
        tmp.write(r.content)
        tmp.close()
        print(f"  Downloaded image ({len(r.content)} bytes) -> {tmp.name}")
        return tmp.name
    except Exception as e:
        print(f"  Image download failed: {e}")
        return None

def main():
    # Fetch untweeted articles
    r = requests.get(
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
    articles = r.json()
    print(f"Found {len(articles)} untweeted articles")
    
    # Filter: must have image_url
    articles_with_img = [a for a in articles if a.get('image_url')]
    print(f"  {len(articles_with_img)} have images")
    
    # Pick up to MAX_POSTS
    to_post = articles_with_img[:MAX_POSTS]
    if not to_post:
        print("No articles to post. Done.")
        return
    
    print(f"\nWill post {len(to_post)} articles:\n")
    for a in to_post:
        print(f"  - [{a['category']}] {a['headline'][:80]}")
    
    # Set up tweepy
    client = tweepy.Client(
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET
    )
    
    auth = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api_v1 = tweepy.API(auth)
    
    # Tweet log
    log_path = os.path.expanduser("~/workspace/the-videshi-news/pipeline/tweet-log.json")
    tweet_log = {}
    if os.path.exists(log_path):
        with open(log_path) as f:
            tweet_log = json.load(f)
    
    posted = 0
    errors = []
    
    for i, article in enumerate(to_post):
        print(f"\n--- Posting {i+1}/{len(to_post)}: {article['headline'][:60]}... ---")
        
        # Compose post
        post_text = compose_post(article)
        print(f"  Post length: {len(post_text)} chars")
        
        # Download and upload image
        media_id = None
        tmp_path = None
        if article.get('image_url'):
            tmp_path = download_image(article['image_url'])
            if tmp_path:
                try:
                    media = api_v1.media_upload(filename=tmp_path)
                    media_id = media.media_id
                    print(f"  Uploaded media: {media_id}")
                except Exception as e:
                    print(f"  Media upload failed: {e}")
        
        # Post tweet
        try:
            kwargs = {'text': post_text}
            if media_id:
                kwargs['media_ids'] = [media_id]
            
            response = client.create_tweet(**kwargs)
            tweet_id = response.data['id']
            tweet_url = f"https://x.com/thevideshi/status/{tweet_id}"
            print(f"  ✅ Posted! {tweet_url}")
            
            # Update Supabase
            patch_r = requests.patch(
                f'{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article["id"]}',
                headers=sb_headers,
                json={'tweeted_at': datetime.utcnow().isoformat() + 'Z'}
            )
            print(f"  Supabase updated: {patch_r.status_code}")
            
            # Log tweet
            tweet_log[str(tweet_id)] = {
                'article_id': article['id'],
                'slug': article['slug'],
                'posted_at': datetime.utcnow().isoformat() + 'Z'
            }
            with open(log_path, 'w') as f:
                json.dump(tweet_log, f, indent=2)
            
            posted += 1
            
        except Exception as e:
            err_msg = f"Failed to post '{article['headline'][:50]}': {e}"
            print(f"  ❌ {err_msg}")
            errors.append(err_msg)
        
        # Cleanup temp file
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)
        
        # Wait between posts
        if i < len(to_post) - 1:
            print(f"  Waiting {POST_DELAY}s...")
            time.sleep(POST_DELAY)
    
    # Summary
    print(f"\n{'='*50}")
    print(f"SUMMARY: Posted {posted}/{len(to_post)} articles to X")
    if errors:
        print(f"Errors ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")
    print(f"{'='*50}")

if __name__ == '__main__':
    main()
