#!/usr/bin/env python3
"""Post recently published Videshi articles to X as long-form posts with images."""

import json
import os
import sys
import time
import tempfile
from datetime import datetime, timezone

import requests
import tweepy

# ── Load env ──────────────────────────────────────────────────────────
def load_env(path):
    env = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env

twitter_env = load_env('~/workspace/.env.twitter')
supabase_env = load_env('~/workspace/.env.supabase')

CONSUMER_KEY = twitter_env['TWITTER_CONSUMER_KEY']
CONSUMER_SECRET = twitter_env['TWITTER_CONSUMER_SECRET']
ACCESS_TOKEN = twitter_env['TWITTER_ACCESS_TOKEN']
ACCESS_TOKEN_SECRET = twitter_env['TWITTER_ACCESS_TOKEN_SECRET']

SUPABASE_KEY = supabase_env['SUPABASE_SERVICE_ROLE_KEY']
SUPABASE_URL = 'https://lboecaekpynbpyijrbfz.supabase.co'

# ── Category emoji mapping ───────────────────────────────────────────
CATEGORY_EMOJI = {
    'news': '🇮🇳',
    'immigration': '🛂',
    'nri-world': '🌏',
    'travel': '✈️',
    'lifestyle-health': '🧘',
    'lifestyle': '🧘',
    'markets-finance': '📈',
    'markets': '📈',
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
    'lifestyle-health': 'LIFESTYLE & HEALTH',
    'lifestyle': 'LIFESTYLE',
    'markets-finance': 'MARKETS & FINANCE',
    'markets': 'MARKETS',
    'technology': 'TECHNOLOGY',
    'sports': 'SPORTS',
    'entertainment': 'ENTERTAINMENT',
    'food': 'FOOD',
}

# ── Fetch untweeted articles ─────────────────────────────────────────
headers = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
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
    timeout=30,
)
resp.raise_for_status()
articles = resp.json()
print(f"Found {len(articles)} untweeted articles")

# Filter out articles with no image_url, take up to 4
candidates = [a for a in articles if a.get('image_url')]
selected = candidates[:4]
print(f"Selected {len(selected)} articles to post (with images)")

if not selected:
    print("No articles to post. Done.")
    sys.exit(0)

# ── Set up tweepy clients ────────────────────────────────────────────
# v1.1 for media upload
auth = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api_v1 = tweepy.API(auth)

# v2 for tweet creation
client = tweepy.Client(
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET,
)

# ── Post each article ────────────────────────────────────────────────
posted = []
errors = []

for i, article in enumerate(selected):
    try:
        cat = (article.get('category') or 'news').lower()
        emoji = CATEGORY_EMOJI.get(cat, '📰')
        label = CATEGORY_LABEL.get(cat, cat.upper())
        headline = article['headline']
        subheadline = article.get('subheadline', '')
        slug = article['slug']
        body = article.get('body', '')
        image_url = article.get('image_url', '')

        # Build the body text — extract key content from markdown body
        # Strip markdown formatting for clean text
        body_clean = body.replace('**', '').replace('*', '').replace('##', '').replace('#', '').strip()
        
        # Take first ~600 chars of body for summary source (we'll compose manually)
        body_excerpt = body_clean[:2000] if body_clean else subheadline

        # Compose the post text - we'll use a template and fill it
        # The actual summary and takeaways will be composed from the body
        post_text = f"""{emoji} {label} | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

{headline.upper()}

{subheadline}

━━━━━━━━━━━━━━━━━━━━━━━━

📰 Full story: thevideshi.com/articles/{slug}

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""

        # For proper long-form posts, we need to compose better content
        # But since we can't call an LLM from here, we'll use subheadline + body excerpt
        # Extract paragraphs from body
        paragraphs = [p.strip() for p in body_clean.split('\n\n') if p.strip() and len(p.strip()) > 30]
        
        # Build summary from first 2-3 meaningful paragraphs
        summary_parts = []
        char_count = 0
        for p in paragraphs[:5]:
            # Skip very short lines or header-like lines
            if len(p) < 40:
                continue
            # Clean up the paragraph
            p_clean = p.replace('\n', ' ').strip()
            if char_count + len(p_clean) > 500:
                break
            summary_parts.append(p_clean)
            char_count += len(p_clean)
        
        summary_text = '\n\n'.join(summary_parts[:3]) if summary_parts else subheadline

        # Extract potential key facts from body (sentences with numbers, names)
        sentences = [s.strip() for s in body_clean.replace('\n', ' ').split('.') if len(s.strip()) > 20]
        # Pick sentences that have numbers or key indicators
        key_facts = []
        for s in sentences[:20]:
            if any(c.isdigit() for c in s) or any(kw in s.lower() for kw in ['percent', 'million', 'billion', 'according', 'announced', 'launched', 'reported']):
                fact = s.strip()
                if len(fact) > 120:
                    fact = fact[:117] + '...'
                key_facts.append(fact)
                if len(key_facts) >= 4:
                    break
        
        # If not enough number-based facts, grab first meaningful sentences
        if len(key_facts) < 3:
            for s in sentences[:15]:
                s_clean = s.strip()
                if s_clean not in key_facts and len(s_clean) > 30 and len(s_clean) < 130:
                    key_facts.append(s_clean)
                    if len(key_facts) >= 4:
                        break

        takeaways = '\n'.join(f'▸ {f}' for f in key_facts[:4]) if key_facts else f'▸ {subheadline}'

        post_text = f"""{emoji} {label} | The Videshi

━━━━━━━━━━━━━━━━━━━━━━━━

{headline.upper()}

{summary_text}

━━━━━━━━━━━━━━━━━━━━━━━━

Key Takeaways:

{takeaways}

━━━━━━━━━━━━━━━━━━━━━━━━

📰 Full story: thevideshi.com/articles/{slug}

The Videshi — Your daily source for Indian diaspora news
🌐 thevideshi.com"""

        # Trim if over 4000 chars
        if len(post_text) > 4000:
            post_text = post_text[:3990] + '...'

        print(f"\n--- Article {i+1}: {headline[:60]}... ---")
        print(f"Post length: {len(post_text)} chars")

        # Try to upload image
        media_id = None
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
                print(f"Image upload failed (posting without): {e}")
                if 'tmp_path' in locals() and os.path.exists(tmp_path):
                    os.unlink(tmp_path)

        # Post tweet
        tweet_kwargs = {'text': post_text}
        if media_id:
            tweet_kwargs['media_ids'] = [media_id]
        
        tweet_resp = client.create_tweet(**tweet_kwargs)
        tweet_id = tweet_resp.data['id']
        tweet_url = f"https://x.com/thevideshi/status/{tweet_id}"
        print(f"Posted: {tweet_url}")

        # Update Supabase
        patch_resp = requests.patch(
            f'{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article["id"]}',
            headers={
                'apikey': SUPABASE_KEY,
                'Authorization': f'Bearer {SUPABASE_KEY}',
                'Content-Type': 'application/json',
            },
            json={'tweeted_at': datetime.now(timezone.utc).isoformat()},
            timeout=15,
        )
        patch_resp.raise_for_status()
        print(f"Supabase updated for {article['id']}")

        # Log tweet ID
        log_path = os.path.expanduser('~/workspace/the-videshi-news/pipeline/tweet-log.json')
        tweet_log = {}
        if os.path.exists(log_path):
            with open(log_path) as f:
                tweet_log = json.load(f)
        tweet_log[str(tweet_id)] = {
            'article_id': article['id'],
            'slug': article['slug'],
            'posted_at': datetime.now(timezone.utc).isoformat() + 'Z',
        }
        with open(log_path, 'w') as f:
            json.dump(tweet_log, f, indent=2)

        posted.append({'headline': headline, 'tweet_url': tweet_url})

        # Wait between posts
        if i < len(selected) - 1:
            print("Waiting 30s before next post...")
            time.sleep(30)

    except Exception as e:
        errors.append({'headline': article.get('headline', '?'), 'error': str(e)})
        print(f"ERROR posting: {e}")

# ── Summary ──────────────────────────────────────────────────────────
print(f"\n{'='*50}")
print(f"SUMMARY: {len(posted)} posted, {len(errors)} errors")
for p in posted:
    print(f"  ✅ {p['headline'][:60]}... → {p['tweet_url']}")
for e in errors:
    print(f"  ❌ {e['headline'][:60]}... → {e['error']}")
