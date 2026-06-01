#!/usr/bin/env python3
"""Post recent Videshi articles to X (@thevideshi) as long-form posts with images."""

import json, os, sys, time, tempfile, requests
from datetime import datetime, timezone

import tweepy

# ── Load env ──────────────────────────────────────────────────────────────
def load_env(path):
    env = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
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

# ── Category emoji mapping ────────────────────────────────────────────────
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

# ── Fetch untweeted articles ──────────────────────────────────────────────
print("Fetching untweeted articles from Supabase...")
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
print(f"Found {len(articles)} untweeted articles.")

# Filter: must have image_url, pick up to 4
candidates = [a for a in articles if a.get('image_url')][:4]
print(f"Selected {len(candidates)} articles to post.")

if not candidates:
    print("Nothing to post. Done.")
    sys.exit(0)

# ── Twitter clients ───────────────────────────────────────────────────────
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


def compose_post(article):
    """Compose a long-form X post from an article."""
    cat = (article.get('category') or 'news').lower()
    emoji = CATEGORY_EMOJI.get(cat, '📰')
    cat_label = cat.replace('-', ' ').upper()

    headline = article.get('headline', '')
    subheadline = article.get('subheadline', '')
    slug = article.get('slug', '')
    body = article.get('body', '') or ''

    # Extract meaningful content from body (strip markdown formatting)
    body_clean = body.replace('##', '').replace('**', '').replace('*', '')
    # Get first ~1500 chars of body for source material
    body_excerpt = body_clean[:2000]

    # Build the post - we'll let Claude compose it, but for automation
    # we create a structured summary from available fields
    paragraphs = []
    sentences = []

    # Split body into paragraphs, skip very short ones
    for p in body_clean.split('\n\n'):
        p = p.strip()
        if len(p) > 40:
            paragraphs.append(p)

    # Take first 2-3 meaningful paragraphs for summary (trimmed)
    summary_paras = []
    char_count = 0
    for p in paragraphs[:5]:
        if char_count > 600:
            break
        # Trim paragraph if too long
        if len(p) > 300:
            # Find sentence boundary
            end = p[:300].rfind('.')
            if end > 100:
                p = p[:end+1]
        summary_paras.append(p)
        char_count += len(p)

    summary_text = '\n\n'.join(summary_paras[:3])

    # Extract key facts from subheadline and early body
    key_facts = []
    # Use subheadline as first fact
    if subheadline:
        key_facts.append(subheadline)

    # Extract sentences with numbers, names, or key facts
    for p in paragraphs[1:6]:
        for sent in p.split('. '):
            sent = sent.strip()
            if len(sent) > 30 and len(sent) < 200:
                # Prioritize sentences with numbers or quotes
                has_number = any(c.isdigit() for c in sent)
                has_quote = '"' in sent or "'" in sent
                if (has_number or has_quote) and len(key_facts) < 5:
                    if not sent.endswith('.'):
                        sent += '.'
                    key_facts.append(sent)

    # Deduplicate and limit to 4
    seen = set()
    unique_facts = []
    for f in key_facts:
        f_lower = f.lower()[:50]
        if f_lower not in seen:
            seen.add(f_lower)
            unique_facts.append(f)
    key_facts = unique_facts[:4]

    # Build the post
    parts = [
        f"{emoji} {cat_label} | The Videshi",
        "",
        "━━━━━━━━━━━━━━━━━━━━━━━━",
        "",
        headline.upper() if len(headline) < 100 else headline,
        "",
        summary_text,
    ]

    if key_facts:
        parts.extend([
            "",
            "━━━━━━━━━━━━━━━━━━━━━━━━",
            "",
            "Key Takeaways:",
            "",
        ])
        for fact in key_facts:
            parts.append(f"▸ {fact}")

    parts.extend([
        "",
        "━━━━━━━━━━━━━━━━━━━━━━━━",
        "",
        f"📰 Full story: thevideshi.com/articles/{slug}",
        "",
        "The Videshi — Your daily source for Indian diaspora news",
        "🌐 thevideshi.com",
    ])

    post_text = '\n'.join(parts)

    # Trim if over 4000 chars
    if len(post_text) > 3900:
        # Shorten summary
        summary_text = '\n\n'.join(summary_paras[:2])
        parts[6] = summary_text
        post_text = '\n'.join(parts)

    if len(post_text) > 3900:
        post_text = post_text[:3900] + '…'

    return post_text


def download_image(url):
    """Download image to temp file, return path or None."""
    try:
        r = requests.get(url, timeout=15, stream=True)
        r.raise_for_status()
        # Determine extension
        ct = r.headers.get('content-type', '')
        ext = '.jpg'
        if 'png' in ct:
            ext = '.png'
        elif 'webp' in ct:
            ext = '.webp'
        elif 'gif' in ct:
            ext = '.gif'

        tmp = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
        for chunk in r.iter_content(8192):
            tmp.write(chunk)
        tmp.close()
        # Check file size
        size = os.path.getsize(tmp.name)
        if size < 1000:
            print(f"  Image too small ({size} bytes), skipping image.")
            os.unlink(tmp.name)
            return None
        print(f"  Downloaded image: {size} bytes")
        return tmp.name
    except Exception as e:
        print(f"  Image download failed: {e}")
        return None


# ── Post loop ─────────────────────────────────────────────────────────────
tweet_log_path = os.path.expanduser('~/workspace/the-videshi-news/pipeline/tweet-log.json')
if os.path.exists(tweet_log_path):
    with open(tweet_log_path) as f:
        tweet_log = json.load(f)
else:
    tweet_log = {}

posted = 0
errors = []

for i, article in enumerate(candidates):
    aid = article['id']
    slug = article.get('slug', '?')
    headline = article.get('headline', '?')
    print(f"\n[{i+1}/{len(candidates)}] Posting: {headline[:80]}...")

    try:
        post_text = compose_post(article)
        print(f"  Post length: {len(post_text)} chars")

        # Try to upload image
        media_id = None
        img_path = None
        if article.get('image_url'):
            img_path = download_image(article['image_url'])
            if img_path:
                try:
                    media = api_v1.media_upload(filename=img_path)
                    media_id = media.media_id
                    print(f"  Media uploaded: {media_id}")
                except Exception as e:
                    print(f"  Media upload failed: {e}")
                    media_id = None

        # Post tweet
        kwargs = {'text': post_text}
        if media_id:
            kwargs['media_ids'] = [media_id]

        tweet_resp = client.create_tweet(**kwargs)
        tweet_id = tweet_resp.data['id']
        tweet_url = f"https://x.com/thevideshi/status/{tweet_id}"
        print(f"  ✅ Posted: {tweet_url}")

        # Clean up temp image
        if img_path and os.path.exists(img_path):
            os.unlink(img_path)

        # Update Supabase
        now_utc = datetime.now(timezone.utc).isoformat()
        patch_resp = requests.patch(
            f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{aid}",
            json={'tweeted_at': now_utc},
            headers=SUPA_HEADERS,
            timeout=15,
        )
        if patch_resp.status_code < 300:
            print(f"  Supabase updated: tweeted_at = {now_utc}")
        else:
            print(f"  ⚠️ Supabase update failed: {patch_resp.status_code} {patch_resp.text}")

        # Log tweet
        tweet_log[str(tweet_id)] = {
            'article_id': aid,
            'slug': slug,
            'posted_at': datetime.utcnow().isoformat() + 'Z',
        }
        with open(tweet_log_path, 'w') as f:
            json.dump(tweet_log, f, indent=2)

        posted += 1

        # Wait between posts
        if i < len(candidates) - 1:
            print("  Waiting 30s...")
            time.sleep(30)

    except Exception as e:
        err_msg = f"{headline[:60]}: {e}"
        errors.append(err_msg)
        print(f"  ❌ Error: {e}")
        # Clean up temp image on error
        if 'img_path' in dir() and img_path and os.path.exists(img_path):
            os.unlink(img_path)

# ── Summary ───────────────────────────────────────────────────────────────
print(f"\n{'='*50}")
print(f"SUMMARY: {posted}/{len(candidates)} articles posted to X.")
if errors:
    print(f"Errors ({len(errors)}):")
    for e in errors:
        print(f"  - {e}")
print(f"{'='*50}")
