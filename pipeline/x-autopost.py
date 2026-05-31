#!/usr/bin/env python3
"""Post recently published Videshi articles to X as long-form posts with images."""

import json
import os
import sys
import time
import tempfile
import requests
import tweepy
from datetime import datetime

# --- Config ---
SUPABASE_URL = 'https://lboecaekpynbpyijrbfz.supabase.co'
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']
TWITTER_CK = os.environ['TWITTER_CONSUMER_KEY']
TWITTER_CS = os.environ['TWITTER_CONSUMER_SECRET']
TWITTER_AT = os.environ['TWITTER_ACCESS_TOKEN']
TWITTER_ATS = os.environ['TWITTER_ACCESS_TOKEN_SECRET']

CATEGORY_EMOJI = {
    'news': '🇮🇳',
    'immigration': '🛂',
    'nri-world': '🌏',
    'travel': '✈️',
    'lifestyle-health': '🧘',
    'markets-finance': '📈',
    'technology': '💻',
    'sports': '🏏',
    'entertainment': '🎬',
    'food': '🍛',
}

CATEGORY_LABELS = {
    'news': 'NEWS',
    'immigration': 'IMMIGRATION',
    'nri-world': 'NRI WORLD',
    'travel': 'TRAVEL',
    'lifestyle-health': 'LIFESTYLE & HEALTH',
    'markets-finance': 'MARKETS & FINANCE',
    'technology': 'TECHNOLOGY',
    'sports': 'SPORTS',
    'entertainment': 'ENTERTAINMENT',
    'food': 'FOOD',
}

TWEET_LOG_PATH = os.path.expanduser('~/workspace/the-videshi-news/pipeline/tweet-log.json')

SB_HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
}


def fetch_untweeted_articles():
    r = requests.get(
        f'{SUPABASE_URL}/rest/v1/p2_articles',
        headers=SB_HEADERS,
        params={
            'status': 'eq.published',
            'tweeted_at': 'is.null',
            'order': 'published_at.desc',
            'limit': '20',
            'select': 'id,slug,headline,subheadline,category,tags,image_url,body'
        }
    )
    r.raise_for_status()
    return r.json()


def extract_key_facts(body_text, headline, subheadline):
    """Extract key facts from the markdown body for takeaways."""
    lines = (body_text or '').split('\n')
    facts = []
    for line in lines:
        line = line.strip()
        # Skip headers, empty lines, short lines
        if not line or line.startswith('#') or len(line) < 30:
            continue
        # Lines with numbers, percentages, dollar amounts are good facts
        import re
        if re.search(r'(\$[\d,.]+|₹[\d,.]+|\d+%|\d+,\d{3}|\d+ (million|billion|crore|lakh|percent))', line):
            # Clean markdown
            clean = re.sub(r'\*\*([^*]+)\*\*', r'\1', line)
            clean = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', clean)
            clean = clean.strip('- *>')
            if 30 < len(clean) < 200:
                facts.append(clean)
    return facts[:6]


def compose_post(article):
    """Compose a long-form X post from the article."""
    cat = article.get('category', 'news')
    emoji = CATEGORY_EMOJI.get(cat, '📰')
    label = CATEGORY_LABELS.get(cat, cat.upper())
    headline = article['headline']
    subheadline = article.get('subheadline', '')
    slug = article['slug']
    body = article.get('body', '') or ''

    # Clean body markdown for reading
    import re
    body_clean = re.sub(r'\*\*([^*]+)\*\*', r'\1', body)
    body_clean = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', body_clean)
    body_clean = re.sub(r'^#{1,4}\s+', '', body_clean, flags=re.MULTILINE)
    body_clean = re.sub(r'\n{3,}', '\n\n', body_clean)

    # Extract paragraphs (skip very short ones)
    paragraphs = [p.strip() for p in body_clean.split('\n\n') if len(p.strip()) > 50]

    # Build summary - take first 2-3 substantial paragraphs, trim to ~200 words
    summary_paras = []
    word_count = 0
    for p in paragraphs[:5]:
        p = p.replace('\n', ' ').strip()
        if p.startswith('- ') or p.startswith('> '):
            continue
        words = len(p.split())
        if word_count + words > 250:
            break
        summary_paras.append(p)
        word_count += words
        if word_count >= 150:
            break

    summary = '\n\n'.join(summary_paras)

    # Extract key takeaways
    facts = extract_key_facts(body, headline, subheadline)
    # If not enough from body, use subheadline parts
    if len(facts) < 3 and subheadline:
        sub_parts = [s.strip() for s in subheadline.replace('. ', '.\n').split('\n') if len(s.strip()) > 20]
        facts = (facts + sub_parts)[:4]

    # If still not enough, extract from summary
    if len(facts) < 3:
        for p in paragraphs[1:6]:
            sentences = [s.strip() for s in p.split('.') if len(s.strip()) > 25]
            for s in sentences:
                clean_s = re.sub(r'\n', ' ', s).strip()
                if len(clean_s) > 25 and clean_s not in facts:
                    facts.append(clean_s)
                    if len(facts) >= 4:
                        break
            if len(facts) >= 4:
                break

    facts = facts[:4]

    # Rewrite headline - make it punchier
    punchy_headline = headline.upper() if len(headline) < 80 else headline.title()

    # Build the post
    separator = '━━━━━━━━━━━━━━━━━━━━━━━━'

    takeaways = '\n'.join(f'▸ {f}' for f in facts) if facts else ''

    post = f"""{emoji} {label} | The Videshi

{separator}

{punchy_headline}

{summary}

{separator}

Key Takeaways:

{takeaways}

{separator}

📰 Full story: thevideshi.com/articles/{slug}

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""

    # Trim if too long (4000 char limit)
    if len(post) > 3900:
        # Shorten summary
        words = summary.split()
        while len(post) > 3900 and len(words) > 50:
            words = words[:-10]
            summary = ' '.join(words)
            post = f"""{emoji} {label} | The Videshi

{separator}

{punchy_headline}

{summary}

{separator}

Key Takeaways:

{takeaways}

{separator}

📰 Full story: thevideshi.com/articles/{slug}

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""

    return post


def download_image(url):
    """Download image to temp file, return path or None."""
    try:
        r = requests.get(url, timeout=15, stream=True)
        r.raise_for_status()
        content_type = r.headers.get('content-type', 'image/jpeg')
        ext = '.jpg'
        if 'png' in content_type:
            ext = '.png'
        elif 'webp' in content_type:
            ext = '.webp'
        elif 'gif' in content_type:
            ext = '.gif'

        tmp = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
        for chunk in r.iter_content(8192):
            tmp.write(chunk)
        tmp.close()

        # Check file size
        size = os.path.getsize(tmp.name)
        if size < 1000:
            print(f"  ⚠️ Image too small ({size} bytes), skipping image")
            os.unlink(tmp.name)
            return None
        return tmp.name
    except Exception as e:
        print(f"  ⚠️ Image download failed: {e}")
        return None


def main():
    # Fetch articles
    articles = fetch_untweeted_articles()
    print(f"Found {len(articles)} untweeted articles")

    # Filter to those with images, pick top 4
    candidates = [a for a in articles if a.get('image_url')]
    to_post = candidates[:4]
    print(f"Selected {len(to_post)} articles to post")

    if not to_post:
        print("No articles to post.")
        return

    # Set up Twitter clients
    client = tweepy.Client(
        consumer_key=TWITTER_CK,
        consumer_secret=TWITTER_CS,
        access_token=TWITTER_AT,
        access_token_secret=TWITTER_ATS,
    )

    auth = tweepy.OAuth1UserHandler(TWITTER_CK, TWITTER_CS, TWITTER_AT, TWITTER_ATS)
    api_v1 = tweepy.API(auth)

    # Load tweet log
    if os.path.exists(TWEET_LOG_PATH):
        with open(TWEET_LOG_PATH) as f:
            tweet_log = json.load(f)
    else:
        tweet_log = {}

    posted = 0
    errors = []

    for i, article in enumerate(to_post):
        print(f"\n--- Article {i+1}/{len(to_post)} ---")
        print(f"  [{article['category']}] {article['headline'][:80]}")

        # Compose post
        post_text = compose_post(article)
        print(f"  Post length: {len(post_text)} chars")

        # Download and upload image
        media_ids = None
        img_path = None
        if article.get('image_url'):
            img_path = download_image(article['image_url'])
            if img_path:
                try:
                    media = api_v1.media_upload(filename=img_path)
                    media_ids = [media.media_id]
                    print(f"  ✅ Image uploaded (media_id: {media.media_id})")
                except Exception as e:
                    print(f"  ⚠️ Image upload failed: {e}")
                    media_ids = None

        # Post tweet
        try:
            kwargs = {'text': post_text}
            if media_ids:
                kwargs['media_ids'] = media_ids

            response = client.create_tweet(**kwargs)
            tweet_id = response.data['id']
            tweet_url = f"https://x.com/thevideshi/status/{tweet_id}"
            print(f"  ✅ Posted! {tweet_url}")
            posted += 1

            # Update Supabase
            now_utc = datetime.utcnow().isoformat() + 'Z'
            patch_r = requests.patch(
                f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article['id']}",
                headers=SB_HEADERS,
                json={'tweeted_at': now_utc}
            )
            if patch_r.status_code < 300:
                print(f"  ✅ Supabase updated (tweeted_at)")
            else:
                print(f"  ⚠️ Supabase update failed: {patch_r.status_code} {patch_r.text}")

            # Log tweet
            tweet_log[str(tweet_id)] = {
                'article_id': article['id'],
                'slug': article['slug'],
                'posted_at': now_utc,
            }
            os.makedirs(os.path.dirname(TWEET_LOG_PATH), exist_ok=True)
            with open(TWEET_LOG_PATH, 'w') as f:
                json.dump(tweet_log, f, indent=2)

        except Exception as e:
            error_msg = f"[{article['slug']}] {e}"
            print(f"  ❌ Post failed: {e}")
            errors.append(error_msg)

        # Clean up temp image
        if img_path and os.path.exists(img_path):
            os.unlink(img_path)

        # Wait between posts
        if i < len(to_post) - 1:
            print("  ⏳ Waiting 30s...")
            time.sleep(30)

    print(f"\n{'='*50}")
    print(f"SUMMARY: {posted}/{len(to_post)} articles posted")
    if errors:
        print(f"ERRORS ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")


if __name__ == '__main__':
    main()
