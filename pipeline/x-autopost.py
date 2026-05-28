#!/usr/bin/env python3
"""Post recently published Videshi articles to X as long-form Premium posts."""

import json, os, sys, time, tempfile, re
from datetime import datetime

import requests
import tweepy

# --- Config ---
SUPABASE_URL = "https://lboecaekpynbpyijrbfz.supabase.co"
MAX_POSTS = 4
DELAY_BETWEEN = 30  # seconds

# Load env
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

sb_headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# Category emoji mapping
CATEGORY_EMOJI = {
    "news": "🇮🇳",
    "immigration": "🛂",
    "nri-world": "🌏",
    "travel": "✈️",
    "lifestyle": "🧘",
    "lifestyle-health": "🧘",
    "markets": "📈",
    "markets-finance": "📈",
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
    "lifestyle": "LIFESTYLE",
    "lifestyle-health": "LIFESTYLE & HEALTH",
    "markets": "MARKETS & FINANCE",
    "markets-finance": "MARKETS & FINANCE",
    "technology": "TECHNOLOGY",
    "sports": "SPORTS",
    "entertainment": "ENTERTAINMENT",
    "food": "FOOD",
}


def strip_markdown(text):
    """Rough markdown to plain text."""
    if not text:
        return ""
    # Remove images
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    # Remove links but keep text
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    # Remove headers
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    # Remove bold/italic markers
    text = re.sub(r'\*{1,3}([^*]+)\*{1,3}', r'\1', text)
    text = re.sub(r'_{1,3}([^_]+)_{1,3}', r'\1', text)
    # Remove blockquotes
    text = re.sub(r'^>\s*', '', text, flags=re.MULTILINE)
    # Remove horizontal rules
    text = re.sub(r'^[-*_]{3,}\s*$', '', text, flags=re.MULTILINE)
    # Clean up whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def extract_key_facts(body_text, subheadline):
    """Extract key facts from article body for takeaways."""
    facts = []
    # Look for sentences with numbers, names, dates
    sentences = re.split(r'(?<=[.!?])\s+', body_text)
    
    # Prioritize sentences with numbers/stats
    stat_sentences = [s for s in sentences if re.search(r'\$[\d,.]+|\d+%|\d+,\d{3}|billion|million|trillion|crore|lakh', s, re.I)]
    name_sentences = [s for s in sentences if re.search(r'[A-Z][a-z]+ [A-Z][a-z]+', s) and len(s) < 200]
    
    seen = set()
    for s in stat_sentences[:3] + name_sentences[:3]:
        clean = s.strip()
        if len(clean) > 40 and len(clean) < 180 and clean not in seen:
            facts.append(clean)
            seen.add(clean)
        if len(facts) >= 4:
            break
    
    # Fallback: use subheadline parts
    if len(facts) < 3 and subheadline:
        parts = subheadline.split('. ')
        for p in parts:
            p = p.strip()
            if len(p) > 20 and p not in seen:
                facts.append(p)
                seen.add(p)
            if len(facts) >= 4:
                break
    
    return facts[:4]


def compose_summary(body_text, headline):
    """Extract 2-3 paragraphs from body for the summary section."""
    paragraphs = [p.strip() for p in body_text.split('\n\n') if p.strip() and len(p.strip()) > 60]
    
    # Skip if body is too short
    if not paragraphs:
        return ""
    
    # Take first 2-3 substantial paragraphs, trim each
    summary_parts = []
    total_len = 0
    for p in paragraphs[:5]:
        # Clean up the paragraph
        p = re.sub(r'\s+', ' ', p).strip()
        if len(p) < 50:
            continue
        # Truncate long paragraphs
        if len(p) > 400:
            # Find a sentence break near 350 chars
            end = p.find('. ', 250)
            if end > 0:
                p = p[:end+1]
            else:
                p = p[:350].rsplit(' ', 1)[0] + '.'
        
        summary_parts.append(p)
        total_len += len(p)
        if total_len > 600 or len(summary_parts) >= 3:
            break
    
    return '\n\n'.join(summary_parts)


def compose_post(article):
    """Compose a long-form X Premium post."""
    cat = article.get('category', 'news') or 'news'
    emoji = CATEGORY_EMOJI.get(cat, '📰')
    label = CATEGORY_LABEL.get(cat, cat.upper())
    headline = article.get('headline', '')
    subheadline = article.get('subheadline', '')
    slug = article.get('slug', '')
    body = strip_markdown(article.get('body', '') or '')
    
    # Build punchy headline
    punchy_headline = headline.upper() if len(headline) < 80 else headline
    
    # Build summary from body
    summary = compose_summary(body, headline)
    if not summary and subheadline:
        summary = subheadline
    
    # Extract key takeaways
    facts = extract_key_facts(body, subheadline)
    
    # Compose the post
    parts = []
    parts.append(f"{emoji} {label} | The Videshi")
    parts.append("")
    parts.append("━━━━━━━━━━━━━━━━━━━━━━━━")
    parts.append("")
    parts.append(punchy_headline)
    parts.append("")
    
    if summary:
        parts.append(summary)
        parts.append("")
    
    if facts:
        parts.append("━━━━━━━━━━━━━━━━━━━━━━━━")
        parts.append("")
        parts.append("Key Takeaways:")
        parts.append("")
        for fact in facts:
            parts.append(f"▸ {fact}")
        parts.append("")
    
    parts.append("━━━━━━━━━━━━━━━━━━━━━━━━")
    parts.append("")
    parts.append(f"📰 Full story: thevideshi.com/articles/{slug}")
    parts.append("")
    parts.append("The Videshi — Your daily source for Indian diaspora news")
    parts.append("🌐 thevideshi.com")
    
    post_text = '\n'.join(parts)
    
    # Trim if over 4000 chars
    if len(post_text) > 3900:
        # Shorten summary
        summary_short = summary[:300].rsplit(' ', 1)[0] + '...'
        parts_short = []
        parts_short.append(f"{emoji} {label} | The Videshi")
        parts_short.append("")
        parts_short.append("━━━━━━━━━━━━━━━━━━━━━━━━")
        parts_short.append("")
        parts_short.append(punchy_headline)
        parts_short.append("")
        parts_short.append(summary_short)
        parts_short.append("")
        if facts:
            parts_short.append("━━━━━━━━━━━━━━━━━━━━━━━━")
            parts_short.append("")
            parts_short.append("Key Takeaways:")
            parts_short.append("")
            for fact in facts[:3]:
                parts_short.append(f"▸ {fact}")
            parts_short.append("")
        parts_short.append("━━━━━━━━━━━━━━━━━━━━━━━━")
        parts_short.append("")
        parts_short.append(f"📰 Full story: thevideshi.com/articles/{slug}")
        parts_short.append("")
        parts_short.append("The Videshi — Your daily source for Indian diaspora news")
        parts_short.append("🌐 thevideshi.com")
        post_text = '\n'.join(parts_short)
    
    return post_text


def download_image(url):
    """Download image to temp file, return path or None."""
    try:
        r = requests.get(url, timeout=15)
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
        tmp.write(r.content)
        tmp.close()
        return tmp.name
    except Exception as e:
        print(f"  ⚠ Image download failed: {e}")
        return None


def main():
    # Fetch untweeted articles
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=sb_headers,
        params={
            "status": "eq.published",
            "tweeted_at": "is.null",
            "order": "published_at.desc",
            "limit": "20",
            "select": "id,slug,headline,subheadline,category,tags,image_url,body"
        }
    )
    articles = r.json()
    print(f"Found {len(articles)} untweeted articles")
    
    # Filter to those with images, take up to MAX_POSTS
    eligible = [a for a in articles if a.get('image_url')]
    to_post = eligible[:MAX_POSTS]
    print(f"Will post {len(to_post)} articles (with images)")
    
    if not to_post:
        print("Nothing to post.")
        return
    
    # Set up tweepy
    client = tweepy.Client(
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET
    )
    
    # v1.1 API for media upload
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
        headline = article.get('headline', '')[:80]
        slug = article['slug']
        print(f"\n--- [{i+1}/{len(to_post)}] {headline}...")
        
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
                    print(f"  ✓ Image uploaded (media_id: {media.media_id})")
                except Exception as e:
                    print(f"  ⚠ Media upload failed: {e}")
                    media_ids = None
        
        # Post tweet
        try:
            kwargs = {"text": post_text}
            if media_ids:
                kwargs["media_ids"] = media_ids
            
            resp = client.create_tweet(**kwargs)
            tweet_id = resp.data['id']
            tweet_url = f"https://x.com/thevideshi/status/{tweet_id}"
            print(f"  ✅ Posted: {tweet_url}")
            
            # Update Supabase
            now_utc = datetime.utcnow().isoformat() + "Z"
            patch_r = requests.patch(
                f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article['id']}",
                headers=sb_headers,
                json={"tweeted_at": now_utc}
            )
            if patch_r.status_code < 300:
                print(f"  ✓ Supabase updated (tweeted_at)")
            else:
                print(f"  ⚠ Supabase update returned {patch_r.status_code}: {patch_r.text}")
            
            # Log tweet
            tweet_log[str(tweet_id)] = {
                "article_id": article['id'],
                "slug": slug,
                "posted_at": now_utc
            }
            with open(log_path, 'w') as f:
                json.dump(tweet_log, f, indent=2)
            
            posted += 1
            
        except Exception as e:
            err_msg = f"Tweet failed for '{headline}': {e}"
            print(f"  ❌ {err_msg}")
            errors.append(err_msg)
        
        # Cleanup temp image
        if img_path and os.path.exists(img_path):
            os.unlink(img_path)
        
        # Wait between posts
        if i < len(to_post) - 1:
            print(f"  Waiting {DELAY_BETWEEN}s...")
            time.sleep(DELAY_BETWEEN)
    
    # Summary
    print(f"\n{'='*50}")
    print(f"SUMMARY: Posted {posted}/{len(to_post)} articles to @thevideshi")
    if errors:
        print(f"Errors ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
