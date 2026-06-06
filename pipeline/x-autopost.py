#!/usr/bin/env python3
"""Post recently published Videshi articles to X as long-form posts with images."""

import json, os, sys, time, tempfile, re
from datetime import datetime, timezone

import requests
import tweepy

# --- Config ---
SUPABASE_URL = "https://lboecaekpynbpyijrbfz.supabase.co"
MAX_ARTICLES = 4
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

twitter_env = load_env("~/workspace/.env.twitter")
supabase_env = load_env("~/workspace/.env.supabase")

CONSUMER_KEY = twitter_env["TWITTER_CONSUMER_KEY"]
CONSUMER_SECRET = twitter_env["TWITTER_CONSUMER_SECRET"]
ACCESS_TOKEN = twitter_env["TWITTER_ACCESS_TOKEN"]
ACCESS_TOKEN_SECRET = twitter_env["TWITTER_ACCESS_TOKEN_SECRET"]
SUPABASE_KEY = supabase_env["SUPABASE_SERVICE_ROLE_KEY"]

SB_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# --- Category emoji map ---
CATEGORY_EMOJI = {
    "news": "🇮🇳",
    "immigration": "🛂",
    "nri-world": "🌏",
    "travel": "✈️",
    "lifestyle-health": "🧘",
    "lifestyle": "🧘",
    "markets-finance": "📈",
    "markets": "📈",
    "technology": "💻",
    "sports": "🏏",
    "entertainment": "🎬",
    "food": "🍛",
}

CATEGORY_LABEL = {
    "news": "NEWS",
    "immigration": "IMMIGRATION",
    "nri-world": "NRI WORLD",
    "travel": "TRAVEL",
    "lifestyle-health": "LIFESTYLE & HEALTH",
    "lifestyle": "LIFESTYLE",
    "markets-finance": "MARKETS & FINANCE",
    "markets": "MARKETS",
    "technology": "TECHNOLOGY",
    "sports": "SPORTS",
    "entertainment": "ENTERTAINMENT",
    "food": "FOOD",
}

def strip_markdown(text):
    """Strip markdown formatting to plain text for X post."""
    if not text:
        return ""
    # Remove images
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    # Remove links but keep text
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    # Remove bold/italic
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    # Remove headers
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    # Remove horizontal rules
    text = re.sub(r'^[-*_]{3,}\s*$', '', text, flags=re.MULTILINE)
    # Remove blockquotes
    text = re.sub(r'^>\s*', '', text, flags=re.MULTILINE)
    # Collapse whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def extract_key_facts(body_text, headline, subheadline):
    """Extract key sentences/facts from the article body."""
    # Get plain text
    plain = strip_markdown(body_text)
    # Split into sentences
    sentences = re.split(r'(?<=[.!?])\s+', plain)
    # Filter for fact-rich sentences (contain numbers, names, dates)
    fact_sentences = []
    for s in sentences:
        s = s.strip()
        if len(s) < 20 or len(s) > 200:
            continue
        # Prefer sentences with numbers, percentages, dollar amounts
        if re.search(r'\d+', s) and len(s) > 30:
            fact_sentences.append(s)
        elif any(w in s.lower() for w in ['first', 'largest', 'record', 'billion', 'million', 'percent', 'announced', 'launched', 'signed']):
            fact_sentences.append(s)
    
    # Take top 4 unique facts
    seen = set()
    facts = []
    for s in fact_sentences:
        key = s[:40].lower()
        if key not in seen:
            seen.add(key)
            facts.append(s)
        if len(facts) >= 4:
            break
    
    # If we don't have enough, pull from subheadline
    if len(facts) < 3 and subheadline:
        sub_sentences = re.split(r'(?<=[.!?])\s+', subheadline)
        for s in sub_sentences:
            s = s.strip()
            if len(s) > 20 and s[:40].lower() not in seen:
                facts.append(s)
                seen.add(s[:40].lower())
            if len(facts) >= 4:
                break
    
    return facts[:4]

def compose_summary(body_text, headline):
    """Extract a 2-3 paragraph summary from the article body."""
    plain = strip_markdown(body_text)
    paragraphs = [p.strip() for p in plain.split('\n\n') if p.strip() and len(p.strip()) > 50]
    
    # Skip if first paragraph looks like the headline repeated
    start = 0
    if paragraphs and paragraphs[0].lower()[:30] in headline.lower():
        start = 1
    
    # Take 2-3 substantive paragraphs
    summary_paras = []
    word_count = 0
    for p in paragraphs[start:]:
        # Skip very short or metadata-like paragraphs
        if len(p) < 60:
            continue
        words = len(p.split())
        if word_count + words > 250:
            if summary_paras:
                break
        summary_paras.append(p)
        word_count += words
        if len(summary_paras) >= 3 or word_count >= 200:
            break
    
    # Trim each paragraph if too long
    trimmed = []
    for p in summary_paras:
        sentences = re.split(r'(?<=[.!?])\s+', p)
        # Take first 3-4 sentences per paragraph
        kept = []
        for s in sentences[:4]:
            kept.append(s)
            if len(' '.join(kept)) > 300:
                break
        trimmed.append(' '.join(kept))
    
    return '\n\n'.join(trimmed)

def rewrite_headline(headline):
    """Make the headline punchier for X."""
    # Remove trailing periods
    h = headline.rstrip('.')
    # If it's already impactful, use Title Case
    # Remove "The Videshi" or similar attribution if present
    h = re.sub(r'\s*[-—|]\s*The Videshi.*$', '', h)
    return h.upper() if len(h) < 80 else h

def compose_post(article):
    """Compose a long-form X post for an article."""
    cat = article.get('category', 'news')
    emoji = CATEGORY_EMOJI.get(cat, '📰')
    label = CATEGORY_LABEL.get(cat, cat.upper().replace('-', ' '))
    
    headline = rewrite_headline(article['headline'])
    body = article.get('body', '') or ''
    subheadline = article.get('subheadline', '') or ''
    slug = article['slug']
    
    # Compose summary
    summary = compose_summary(body, article['headline'])
    if not summary:
        summary = subheadline if subheadline else article['headline']
    
    # Extract key facts
    facts = extract_key_facts(body, article['headline'], subheadline)
    
    # Build the post
    parts = [
        f"{emoji} {label} | The Videshi",
        "",
        "━━━━━━━━━━━━━━━━━━━━━━━━",
        "",
        headline,
        "",
        summary,
        "",
        "━━━━━━━━━━━━━━━━━━━━━━━━",
        "",
    ]
    
    if facts:
        parts.append("Key Takeaways:")
        parts.append("")
        for f in facts:
            # Trim fact to reasonable length
            if len(f) > 150:
                f = f[:147] + "..."
            parts.append(f"▸ {f}")
        parts.append("")
        parts.append("━━━━━━━━━━━━━━━━━━━━━━━━")
        parts.append("")
    
    parts.extend([
        f"📰 Full story: thevideshi.com/articles/{slug}",
        "",
        "The Videshi — Your daily source for Indian diaspora news",
        "🌐 thevideshi.com"
    ])
    
    post_text = '\n'.join(parts)
    
    # Ensure under 4000 chars
    if len(post_text) > 3900:
        # Trim summary
        summary_words = summary.split()
        while len(post_text) > 3900 and len(summary_words) > 50:
            summary_words = summary_words[:-10]
            summary = ' '.join(summary_words) + '...'
            # Rebuild
            parts_rebuild = [
                f"{emoji} {label} | The Videshi",
                "",
                "━━━━━━━━━━━━━━━━━━━━━━━━",
                "",
                headline,
                "",
                summary,
                "",
                "━━━━━━━━━━━━━━━━━━━━━━━━",
                "",
            ]
            if facts:
                parts_rebuild.append("Key Takeaways:")
                parts_rebuild.append("")
                for f in facts:
                    if len(f) > 150:
                        f = f[:147] + "..."
                    parts_rebuild.append(f"▸ {f}")
                parts_rebuild.append("")
                parts_rebuild.append("━━━━━━━━━━━━━━━━━━━━━━━━")
                parts_rebuild.append("")
            parts_rebuild.extend([
                f"📰 Full story: thevideshi.com/articles/{slug}",
                "",
                "The Videshi — Your daily source for Indian diaspora news",
                "🌐 thevideshi.com"
            ])
            post_text = '\n'.join(parts_rebuild)
    
    return post_text

def download_image(image_url):
    """Download article image to temp file. Returns path or None."""
    try:
        resp = requests.get(image_url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=15, stream=True)
        if resp.status_code != 200:
            print(f"  ⚠ Image download failed: HTTP {resp.status_code}")
            return None
        # Determine extension
        content_type = resp.headers.get('Content-Type', '')
        ext = '.jpg'
        if 'png' in content_type:
            ext = '.png'
        elif 'webp' in content_type:
            ext = '.webp'
        elif 'gif' in content_type:
            ext = '.gif'
        
        tmp = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
        for chunk in resp.iter_content(8192):
            tmp.write(chunk)
        tmp.close()
        
        # Verify file size
        fsize = os.path.getsize(tmp.name)
        if fsize < 1000:
            print(f"  ⚠ Image too small ({fsize} bytes), skipping")
            os.unlink(tmp.name)
            return None
        
        print(f"  ✓ Image downloaded: {fsize/1024:.0f}KB")
        return tmp.name
    except Exception as e:
        print(f"  ⚠ Image download error: {e}")
        return None

def main():
    print("=" * 60)
    print("The Videshi → X Autopost")
    print(f"Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 60)
    
    # Fetch untweeted articles
    resp = requests.get(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        params={
            "status": "eq.published",
            "tweeted_at": "is.null",
            "order": "published_at.desc",
            "limit": "20",
            "select": "id,slug,headline,subheadline,category,tags,image_url,body"
        },
        headers=SB_HEADERS
    )
    
    if resp.status_code != 200:
        print(f"ERROR: Supabase fetch failed: {resp.status_code} {resp.text}")
        sys.exit(1)
    
    articles = resp.json()
    print(f"\nFound {len(articles)} untweeted articles")
    
    # Filter: must have image_url
    articles_with_img = [a for a in articles if a.get('image_url')]
    print(f"With images: {len(articles_with_img)}")
    
    # Pick top 4
    to_post = articles_with_img[:MAX_ARTICLES]
    print(f"Will post: {len(to_post)}")
    
    if not to_post:
        print("Nothing to post. Done.")
        return
    
    # Init tweepy
    client = tweepy.Client(
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET
    )
    
    auth = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api_v1 = tweepy.API(auth)
    
    # Post each article
    results = []
    for i, article in enumerate(to_post):
        print(f"\n{'─' * 50}")
        print(f"[{i+1}/{len(to_post)}] {article['headline'][:80]}")
        print(f"  Category: {article['category']} | Slug: {article['slug']}")
        
        # Compose post
        post_text = compose_post(article)
        print(f"  Post length: {len(post_text)} chars")
        
        # Download and upload image
        media_ids = None
        tmp_img_path = None
        if article.get('image_url'):
            tmp_img_path = download_image(article['image_url'])
            if tmp_img_path:
                try:
                    media = api_v1.media_upload(filename=tmp_img_path)
                    media_ids = [media.media_id]
                    print(f"  ✓ Image uploaded to X (media_id: {media.media_id})")
                except Exception as e:
                    print(f"  ⚠ Image upload to X failed: {e}")
                    media_ids = None
        
        # Post tweet
        try:
            kwargs = {"text": post_text}
            if media_ids:
                kwargs["media_ids"] = media_ids
            
            tweet_resp = client.create_tweet(**kwargs)
            tweet_id = tweet_resp.data['id']
            tweet_url = f"https://x.com/thevideshi/status/{tweet_id}"
            print(f"  ✅ Posted! {tweet_url}")
            
            # Update Supabase
            now_utc = datetime.now(timezone.utc).isoformat()
            patch_resp = requests.patch(
                f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article['id']}",
                headers=SB_HEADERS,
                json={"tweeted_at": now_utc}
            )
            if patch_resp.status_code in (200, 204):
                print(f"  ✓ Supabase updated (tweeted_at)")
            else:
                print(f"  ⚠ Supabase update failed: {patch_resp.status_code} {patch_resp.text}")
            
            # Log tweet
            log_path = os.path.expanduser("~/workspace/the-videshi-news/pipeline/tweet-log.json")
            tweet_log = {}
            if os.path.exists(log_path):
                with open(log_path) as f:
                    tweet_log = json.load(f)
            tweet_log[str(tweet_id)] = {
                "article_id": article['id'],
                "slug": article['slug'],
                "posted_at": now_utc
            }
            with open(log_path, 'w') as f:
                json.dump(tweet_log, f, indent=2)
            
            results.append({"status": "ok", "tweet_url": tweet_url, "headline": article['headline'][:60]})
            
        except tweepy.errors.TweepyException as e:
            print(f"  ❌ Tweet failed: {e}")
            results.append({"status": "error", "error": str(e), "headline": article['headline'][:60]})
        except Exception as e:
            print(f"  ❌ Unexpected error: {e}")
            results.append({"status": "error", "error": str(e), "headline": article['headline'][:60]})
        finally:
            # Clean up temp image
            if tmp_img_path and os.path.exists(tmp_img_path):
                os.unlink(tmp_img_path)
        
        # Wait between posts
        if i < len(to_post) - 1:
            print(f"  ⏳ Waiting {POST_DELAY}s before next post...")
            time.sleep(POST_DELAY)
    
    # Summary
    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print(f"{'=' * 60}")
    ok = [r for r in results if r['status'] == 'ok']
    err = [r for r in results if r['status'] == 'error']
    print(f"Posted: {len(ok)} | Errors: {len(err)}")
    for r in ok:
        print(f"  ✅ {r['headline']}...")
        print(f"     {r['tweet_url']}")
    for r in err:
        print(f"  ❌ {r['headline']}... — {r['error']}")

if __name__ == "__main__":
    main()
