#!/usr/bin/env python3
"""Post recently published Videshi articles to X as long-form posts."""

import json, os, sys, time, tempfile, requests, tweepy, subprocess
try:
    import x_spend
except Exception:
    x_spend=None
from datetime import datetime, timezone


def download_image_curl(url):
    """Download an image via curl subprocess (proxy-friendly, Wikimedia-safe UA).

    requests-based fetches 429 on Wikimedia and time out elsewhere; curl with
    an explicit UA + hard timeouts is reliable from this box (verified 2026-10-08).
    Returns local temp path, or None on failure.
    """
    low = url.lower()
    suffix = '.png' if '.png' in low else ('.webp' if '.webp' in low else '.jpg')
    tmp = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    tmp_path = tmp.name
    tmp.close()
    try:
        r = subprocess.run(
            ['curl', '-sSL', '-A', 'TheVideshi/1.0 (thevideshi.com)',
             '--max-time', '30', '--connect-timeout', '10',
             '-f', '--retry', '2', '--retry-delay', '2',
             '-o', tmp_path, url],
            capture_output=True, timeout=60)
        if r.returncode == 0 and os.path.getsize(tmp_path) > 1024:
            return tmp_path
        print(f"    curl download failed (rc={r.returncode}, "
              f"{r.stderr.decode()[:120]})")
    except Exception as e:
        print(f"    curl download exception: {e}")
    try:
        os.unlink(tmp_path)
    except Exception:
        pass
    return None


def compress_for_upload(src_path):
    """Downscale + JPEG-compress so the X upload finishes before the proxy
    stalls it (2026-10-08: 60s read/write timeouts on upload.twitter.com).
    Returns the compressed path (src if compression fails)."""
    try:
        from PIL import Image
        im = Image.open(src_path).convert('RGB')
        w, h = im.size
        if max(w, h) > 1200:
            scale = 1200 / max(w, h)
            im = im.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
        out = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        out_path = out.name
        out.close()
        im.save(out_path, 'JPEG', quality=82, optimize=True)
        print(f"    compressed {os.path.getsize(src_path)//1024}KB -> "
              f"{os.path.getsize(out_path)//1024}KB")
        return out_path
    except Exception as e:
        print(f"    compression failed ({e}), uploading original")
        return src_path


def upload_image_file(api_v1, local_path):
    """Upload one local image to X, returning its media_id."""
    return api_v1.media_upload(filename=local_path).media_id

# --- Config ---
SUPABASE_URL = 'https://lboecaekpynbpyijrbfz.supabase.co'

def load_env(path):
    env = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                key, val = line.split('=', 1)
                key = key.replace('export ', '').strip()
                env[key] = val.strip()
    return env

twitter_env = load_env('~/workspace/.env.twitter')
supa_env = load_env('~/workspace/.env.supabase')

CONSUMER_KEY = twitter_env['TWITTER_CONSUMER_KEY']
CONSUMER_SECRET = twitter_env['TWITTER_CONSUMER_SECRET']
ACCESS_TOKEN = twitter_env['TWITTER_ACCESS_TOKEN']
ACCESS_TOKEN_SECRET = twitter_env['TWITTER_ACCESS_TOKEN_SECRET']
SUPABASE_KEY = supa_env['SUPABASE_SERVICE_ROLE_KEY']

SUPA_HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json'
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
    headers=SUPA_HEADERS
)
resp.raise_for_status()
all_articles = resp.json()
print(f"Fetched {len(all_articles)} untweeted articles")

# Pick up to 4 with images
articles = [a for a in all_articles if a.get('image_url')][:4]
print(f"Selected {len(articles)} articles to post")

if not articles:
    print("No articles to post. Exiting.")
    sys.exit(0)

# --- Init tweepy ---
client = tweepy.Client(
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET
)
auth = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api_v1 = tweepy.API(auth, timeout=60)  # explicit: upload.twitter.com stalls through the proxy; 60s then fail fast

# --- Compose posts ---
def extract_key_content(body_md):
    """Extract clean text from markdown body for summarization."""
    if not body_md:
        return ""
    import re
    lines = []
    for line in body_md.split('\n'):
        l = line.strip()
        # Skip markdown headers, images, empty lines
        if l.startswith('#') or l.startswith('![') or l.startswith('---'):
            continue
        # Skip HTML tags and blocks (data cards, divs, etc.)
        if l.startswith('<') and ('div' in l.lower() or 'span' in l.lower() or 'ul' in l.lower() or 'li' in l.lower() or l.startswith('</')):
            continue
        # Strip any remaining inline HTML tags
        l = re.sub(r'<[^>]+>', '', l)
        # Strip bold/italic markers for cleaner reading
        l = l.replace('**', '').replace('*', '')
        l = l.strip()
        if l:
            lines.append(l)
    return '\n'.join(lines)

def compose_post(article):
    """Compose a clean, X-native post from article data.

    Format: hook line, headline, tight summary, link. No dividers
    (they render as broken bars), no duplicated takeaways, no boilerplate.
    """
    cat = article.get("category", "news")
    emoji = CATEGORY_EMOJI.get(cat, "🇮🇳")
    headline = article["headline"]
    slug = article["slug"]
    body_text = extract_key_content(article.get("body", ""))

    # Extract sentences from body for summary
    sentences = []
    for para in body_text.split("\n"):
        para = para.strip()
        if len(para) > 40:
            sentences.append(para)

    # Tight summary: 2-3 sentences, max ~200 words
    summary_paras = []
    word_count = 0
    for s in sentences:
        words = len(s.split())
        if word_count + words > 200:
            break
        summary_paras.append(s)
        word_count += words
        if word_count >= 80 and len(summary_paras) >= 2:
            break
    summary = " ".join(summary_paras[:3])

    post = f"""{emoji} {headline}

{summary}

📰 Read the full story on The Videshi"""

    # Trim if over X's limit
    if len(post) > 3900:
        summary = " ".join(summary_paras[:2])
        post = f"""{emoji} {headline}

{summary}

📰 Read the full story on The Videshi"""
    return post


# --- Post loop ---
log_path = os.path.expanduser("~/workspace/the-videshi-news/pipeline/tweet-log.json")
tweet_log = json.load(open(log_path)) if os.path.exists(log_path) else {}

results = []

if x_spend and x_spend.over_budget():
    print(f"X-BUDGET ceiling reached ({x_spend.status_line()}); skipping autopost run.")
    sys.exit(0)

for i, article in enumerate(articles):
    print(f"\n--- Article {i+1}/{len(articles)} ---")
    print(f"  Headline: {article['headline'][:80]}...")
    print(f"  Category: {article['category']}")

    post_text = compose_post(article)
    print(f"  Post length: {len(post_text)} chars")

    # Check for carousel images from prebuilt_reels (up to 4 image slides)
    media_ids = []
    try:
        carousel_resp = requests.get(
            f'{SUPABASE_URL}/rest/v1/prebuilt_reels',
            params={
                'article_id': f'eq.{article["id"]}',
                'carousel_images': 'not.is.null',
                'select': 'carousel_images',
                'limit': '1'
            },
            headers=SUPA_HEADERS, timeout=10
        )
        carousel_data = carousel_resp.json()
        if carousel_data and carousel_data[0].get('carousel_images'):
            all_slides = carousel_data[0]['carousel_images']
            # Filter to image files only (skip .mp4 animated cards), pick up to 4 data-rich slides
            image_slides = [u for u in all_slides if u.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
            # Skip first (hook) and last (CTA) — use the middle data-rich slides
            if len(image_slides) > 5:
                image_slides = image_slides[1:-1]  # skip hook + CTA
            chosen = image_slides[:4]
            if chosen:
                print(f"  📸 Found {len(all_slides)} carousel slides, posting {len(chosen)} images")
                for ci, curl in enumerate(chosen):
                    tmp_path = up_path = None
                    try:
                        tmp_path = download_image_curl(curl)
                        if not tmp_path:
                            print(f"    Slide {ci}: download failed, skipping")
                            continue
                        up_path = compress_for_upload(tmp_path)
                        media_id = upload_image_file(api_v1, up_path)
                        media_ids.append(media_id)
                        print(f"    Slide {ci}: media_id={media_id}")
                    except Exception as e:
                        print(f"    Slide {ci} failed: {e}")
                    finally:
                        for p in {tmp_path, up_path}:
                            if p:
                                try:
                                    os.unlink(p)
                                except Exception:
                                    pass
    except Exception as e:
        print(f"  Carousel check failed ({e}), falling back to hero image")

    # Fall back to hero image if no carousel
    if not media_ids:
        image_url = article.get('image_url', '')
        if image_url:
            tmp_path = up_path = None
            try:
                tmp_path = download_image_curl(image_url)
                if not tmp_path:
                    print("  Image failed (download), posting without image")
                else:
                    up_path = compress_for_upload(tmp_path)
                    media_id = upload_image_file(api_v1, up_path)
                    media_ids.append(media_id)
                    print(f"  Hero image uploaded: media_id={media_id}")
            except Exception as e:
                print(f"  Image failed ({e}), posting without image")
            finally:
                for p in {tmp_path, up_path}:
                    if p:
                        try:
                            os.unlink(p)
                        except Exception:
                            pass

    # Post tweet
    try:
        kwargs = {'text': post_text}
        if media_ids:
            kwargs['media_ids'] = media_ids

        tweet_resp = client.create_tweet(**kwargs)
        tweet_id = str(tweet_resp.data['id'])
        if x_spend: x_spend.add(writes=1)
        tweet_url = f"https://x.com/thevideshi/status/{tweet_id}"
        print(f"  ✅ Posted: {tweet_url}")

        # Update Supabase
        patch_resp = requests.patch(
            f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article['id']}",
            headers=SUPA_HEADERS,
            json={"tweeted_at": datetime.now(timezone.utc).isoformat()}
        )
        print(f"  Supabase update: {patch_resp.status_code}")

        # Log locally
        tweet_log[tweet_id] = {
            "article_id": article['id'],
            "slug": article['slug'],
            "posted_at": datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        }
        with open(log_path, 'w') as f:
            json.dump(tweet_log, f, indent=2)

        results.append({"slug": article['slug'], "tweet_url": tweet_url, "status": "ok"})

    except Exception as e:
        print(f"  ❌ Failed: {e}")
        results.append({"slug": article['slug'], "error": str(e), "status": "failed"})

    # Wait 30s between posts (not after last)
    if i < len(articles) - 1:
        print("  Waiting 30s...")
        time.sleep(30)

# --- Summary ---
print(f"\n{'='*50}")
print(f"SUMMARY: {sum(1 for r in results if r['status']=='ok')}/{len(results)} posted successfully")
for r in results:
    if r['status'] == 'ok':
        print(f"  ✅ {r['slug'][:60]} → {r['tweet_url']}")
    else:
        print(f"  ❌ {r['slug'][:60]} → {r['error'][:80]}")
