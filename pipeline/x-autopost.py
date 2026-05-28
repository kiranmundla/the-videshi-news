#!/usr/bin/env python3
"""Post recent Videshi articles to X (@thevideshi) as long-form posts with images."""

import json
import os
import sys
import time
import tempfile
import requests
import tweepy
from datetime import datetime

# --- Config ---
SUPABASE_URL = "https://lboecaekpynbpyijrbfz.supabase.co"

def load_env(path):
    env = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
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

SUPABASE_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

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

def fetch_untweeted_articles():
    """Fetch up to 20 recent published articles not yet tweeted."""
    url = (
        f"{SUPABASE_URL}/rest/v1/p2_articles"
        f"?status=eq.published&tweeted_at=is.null"
        f"&order=published_at.desc&limit=20"
        f"&select=id,slug,headline,subheadline,category,tags,image_url,body"
    )
    resp = requests.get(url, headers=SUPABASE_HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.json()

def extract_key_facts(body_text, subheadline):
    """Extract key facts from the article body for takeaways."""
    # Simple extraction: look for sentences with numbers, names, or strong statements
    if not body_text:
        body_text = ""
    
    sentences = []
    for para in body_text.split('\n'):
        para = para.strip()
        if not para or para.startswith('#') or para.startswith('*') or para.startswith('-'):
            # Handle bullet points as sentences
            if para.startswith('- ') or para.startswith('* '):
                clean = para.lstrip('-* ').strip()
                if len(clean) > 20:
                    sentences.append(clean)
            continue
        # Split paragraph into sentences
        for s in para.replace('. ', '.\n').split('\n'):
            s = s.strip()
            if len(s) > 25:
                sentences.append(s)
    
    return sentences

def compose_summary(body_text):
    """Create a 2-3 paragraph summary from article body."""
    if not body_text:
        return ""
    
    # Clean markdown
    paragraphs = []
    current = []
    
    for line in body_text.split('\n'):
        line = line.strip()
        # Skip headers, images, empty lines
        if line.startswith('#') or line.startswith('![') or line.startswith('**Source') or not line:
            if current:
                paragraphs.append(' '.join(current))
                current = []
            continue
        # Skip markdown formatting artifacts
        if line.startswith('---') or line.startswith('***'):
            continue
        # Clean bold/italic markers for readability
        clean = line.replace('**', '').replace('*', '').strip()
        if clean and len(clean) > 15:
            current.append(clean)
    
    if current:
        paragraphs.append(' '.join(current))
    
    if not paragraphs:
        return ""
    
    # Take first 2-3 substantial paragraphs
    summary_paras = []
    total_words = 0
    for p in paragraphs:
        words = len(p.split())
        if total_words + words > 250:
            if not summary_paras:
                # At least include one paragraph, trimmed
                summary_paras.append(p)
            break
        summary_paras.append(p)
        total_words += words
        if len(summary_paras) >= 3:
            break
    
    return '\n\n'.join(summary_paras)

def compose_takeaways(body_text, subheadline):
    """Extract 3-4 key takeaway bullet points."""
    sentences = extract_key_facts(body_text, subheadline)
    
    # Prioritize sentences with numbers, percentages, dollar signs
    scored = []
    for s in sentences:
        score = 0
        if any(c.isdigit() for c in s):
            score += 2
        if '$' in s or '₹' in s or '%' in s:
            score += 2
        if any(word in s.lower() for word in ['billion', 'million', 'trillion', 'crore', 'lakh']):
            score += 2
        if len(s) < 120:
            score += 1  # Prefer concise statements
        scored.append((score, s))
    
    # Sort by score descending, take top 4
    scored.sort(key=lambda x: -x[0])
    takeaways = []
    seen = set()
    for _, s in scored:
        # Avoid near-duplicates
        key = s[:40].lower()
        if key not in seen:
            seen.add(key)
            # Trim to reasonable length
            if len(s) > 140:
                s = s[:137] + "..."
            takeaways.append(s)
            if len(takeaways) >= 4:
                break
    
    # If we didn't get enough from scoring, add from subheadline
    if len(takeaways) < 3 and subheadline:
        takeaways.insert(0, subheadline[:140])
    
    return takeaways[:4]

def compose_post(article):
    """Compose a long-form X post for an article."""
    cat = (article.get('category') or 'news').lower()
    emoji = CATEGORY_EMOJI.get(cat, '📰')
    label = CATEGORY_LABEL.get(cat, cat.upper())
    headline = article.get('headline', '')
    subheadline = article.get('subheadline', '')
    slug = article.get('slug', '')
    body = article.get('body', '') or ''
    
    # Rewrite headline for X - make it punchier
    display_headline = headline.upper() if len(headline) < 80 else headline.title()
    
    # Build summary from article body
    summary = compose_summary(body)
    if not summary and subheadline:
        summary = subheadline
    
    # Build takeaways
    takeaways = compose_takeaways(body, subheadline)
    
    # Compose the post
    parts = [
        f"{emoji} {label} | The Videshi",
        "",
        "━━━━━━━━━━━━━━━━━━━━━━━━",
        "",
        display_headline,
        "",
    ]
    
    if summary:
        parts.append(summary)
        parts.append("")
    
    if takeaways:
        parts.append("━━━━━━━━━━━━━━━━━━━━━━━━")
        parts.append("")
        parts.append("Key Takeaways:")
        parts.append("")
        for t in takeaways:
            parts.append(f"▸ {t}")
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
        if summary:
            words = summary.split()
            shortened = ' '.join(words[:int(len(words)*0.6)])
            post_text = post_text.replace(summary, shortened + "...")
    
    return post_text

def download_image(image_url):
    """Download image to a temp file, return path or None."""
    try:
        resp = requests.get(image_url, timeout=15)
        resp.raise_for_status()
        # Determine extension
        content_type = resp.headers.get('content-type', '')
        ext = '.jpg'
        if 'png' in content_type:
            ext = '.png'
        elif 'webp' in content_type:
            ext = '.webp'
        elif 'gif' in content_type:
            ext = '.gif'
        
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
        tmp.write(resp.content)
        tmp.close()
        return tmp.name
    except Exception as e:
        print(f"  ⚠ Image download failed: {e}")
        return None

def upload_media_to_x(image_path):
    """Upload image to X using v1.1 API, return media object or None."""
    try:
        auth = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        api_v1 = tweepy.API(auth)
        media = api_v1.media_upload(filename=image_path)
        return media
    except Exception as e:
        print(f"  ⚠ Media upload failed: {e}")
        return None

def mark_tweeted(article_id):
    """Update tweeted_at in Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article_id}"
    now = datetime.utcnow().isoformat() + "Z"
    resp = requests.patch(url, headers=SUPABASE_HEADERS, json={"tweeted_at": now}, timeout=15)
    if resp.status_code < 300:
        print(f"  ✓ Supabase updated (tweeted_at)")
    else:
        print(f"  ⚠ Supabase update failed: {resp.status_code} {resp.text}")

def log_tweet(tweet_id, article):
    """Append to local tweet log."""
    log_path = os.path.expanduser("~/workspace/the-videshi-news/pipeline/tweet-log.json")
    tweet_log = {}
    if os.path.exists(log_path):
        try:
            tweet_log = json.load(open(log_path))
        except:
            pass
    
    tweet_log[str(tweet_id)] = {
        "article_id": article['id'],
        "slug": article['slug'],
        "posted_at": datetime.utcnow().isoformat() + "Z"
    }
    with open(log_path, 'w') as f:
        json.dump(tweet_log, f, indent=2)

def main():
    print("=" * 50)
    print("X AUTOPOST — The Videshi (@thevideshi)")
    print(f"Run: {datetime.utcnow().isoformat()}Z")
    print("=" * 50)
    
    # Fetch articles
    print("\n📥 Fetching untweeted articles...")
    articles = fetch_untweeted_articles()
    print(f"   Found {len(articles)} untweeted articles")
    
    if not articles:
        print("\n✅ No articles to post. Done.")
        return
    
    # Filter: must have image_url, take up to 4
    eligible = [a for a in articles if a.get('image_url')]
    skipped_no_image = len(articles) - len(eligible)
    if skipped_no_image:
        print(f"   Skipped {skipped_no_image} articles with no image_url")
    
    to_post = eligible[:4]
    print(f"   Will post {len(to_post)} articles\n")
    
    # Init tweepy v2 client
    client = tweepy.Client(
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET
    )
    
    posted = 0
    errors = []
    
    for i, article in enumerate(to_post):
        print(f"{'─' * 50}")
        print(f"📝 [{i+1}/{len(to_post)}] {article['headline'][:80]}")
        print(f"   Category: {article.get('category', '?')} | Slug: {article['slug'][:50]}")
        
        # Compose post
        post_text = compose_post(article)
        print(f"   Post length: {len(post_text)} chars")
        
        # Download and upload image
        media_ids = None
        image_path = None
        if article.get('image_url'):
            print(f"   📷 Downloading image...")
            image_path = download_image(article['image_url'])
            if image_path:
                print(f"   📤 Uploading to X...")
                media = upload_media_to_x(image_path)
                if media:
                    media_ids = [media.media_id]
                    print(f"   ✓ Media uploaded: {media.media_id}")
        
        # Post tweet
        try:
            kwargs = {"text": post_text}
            if media_ids:
                kwargs["media_ids"] = media_ids
            
            response = client.create_tweet(**kwargs)
            tweet_id = response.data['id']
            tweet_url = f"https://x.com/thevideshi/status/{tweet_id}"
            print(f"   ✅ Posted! {tweet_url}")
            
            # Update Supabase
            mark_tweeted(article['id'])
            
            # Log locally
            log_tweet(tweet_id, article)
            
            posted += 1
            
        except Exception as e:
            error_msg = str(e)
            print(f"   ❌ Failed to post: {error_msg}")
            errors.append({"slug": article['slug'], "error": error_msg})
        
        finally:
            # Cleanup temp image
            if image_path and os.path.exists(image_path):
                os.remove(image_path)
        
        # Wait between posts
        if i < len(to_post) - 1:
            print("   ⏳ Waiting 30s before next post...")
            time.sleep(30)
    
    # Summary
    print(f"\n{'=' * 50}")
    print(f"SUMMARY")
    print(f"{'=' * 50}")
    print(f"  Posted: {posted}/{len(to_post)}")
    if errors:
        print(f"  Errors: {len(errors)}")
        for e in errors:
            print(f"    - {e['slug']}: {e['error'][:100]}")
    print(f"  Done at {datetime.utcnow().isoformat()}Z")

if __name__ == "__main__":
    main()
