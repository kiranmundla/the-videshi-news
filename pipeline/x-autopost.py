#!/usr/bin/env python3
"""Auto-post Videshi articles to X (@thevideshi) with long-form formatting and images."""

import json, os, sys, time, tempfile, requests, tweepy
from datetime import datetime

# --- Config ---
SUPABASE_URL = "https://lboecaekpynbpyijrbfz.supabase.co"
MAX_POSTS = 4
POST_DELAY = 30  # seconds between posts

# --- Load credentials ---
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
    "lifestyle": "🧘",
    "markets": "📈",
    "technology": "💻",
    "sports": "🏏",
    "entertainment": "🎬",
    "food": "🍛",
}

def fetch_untweeted():
    url = (f"{SUPABASE_URL}/rest/v1/p2_articles"
           f"?status=eq.published&tweeted_at=is.null"
           f"&order=published_at.desc&limit=20"
           f"&select=id,slug,headline,subheadline,category,tags,image_url,body")
    resp = requests.get(url, headers=SB_HEADERS)
    resp.raise_for_status()
    articles = resp.json()
    # Filter to those with image_url
    return [a for a in articles if a.get("image_url")]

def extract_key_facts(body, headline, subheadline):
    """Extract key sentences/facts from the article body for takeaways."""
    if not body:
        return []
    # Simple extraction: find sentences with numbers, names, or key terms
    lines = body.replace('\n\n', '\n').split('\n')
    facts = []
    for line in lines:
        line = line.strip().lstrip('#').lstrip('*').lstrip('-').strip()
        if not line or len(line) < 30:
            continue
        # Skip markdown artifacts
        if line.startswith('![') or line.startswith('[') or line.startswith('```'):
            continue
        facts.append(line)
    return facts

def compose_summary(article):
    """Create a 2-3 paragraph summary from the article body."""
    body = article.get("body", "") or ""
    headline = article.get("headline", "")
    subheadline = article.get("subheadline", "") or ""
    
    # Clean up markdown - extract readable paragraphs
    paragraphs = []
    current = []
    for line in body.split('\n'):
        line = line.strip()
        # Skip headings, images, code blocks, empty lines
        if (line.startswith('#') or line.startswith('![') or 
            line.startswith('```') or line.startswith('---') or
            line.startswith('> ') or not line):
            if current:
                paragraphs.append(' '.join(current))
                current = []
            continue
        # Strip bold/italic markers
        cleaned = line.replace('**', '').replace('__', '').replace('*', '').replace('_', '')
        # Skip very short lines (likely list items or captions)
        if len(cleaned) < 40:
            continue
        current.append(cleaned)
    if current:
        paragraphs.append(' '.join(current))
    
    # Take the first 2-3 substantial paragraphs
    good_paras = [p for p in paragraphs if len(p) > 60][:3]
    
    if not good_paras:
        # Fallback to subheadline
        return subheadline if subheadline else headline
    
    # Trim each paragraph to reasonable length
    result = []
    total_len = 0
    for p in good_paras:
        # Cap each paragraph at ~120 words
        words = p.split()
        if len(words) > 120:
            p = ' '.join(words[:120]) + '...'
        if total_len + len(p) > 1200:
            break
        result.append(p)
        total_len += len(p)
    
    return '\n\n'.join(result)

def extract_takeaways(article):
    """Extract 3-4 key takeaway bullet points."""
    body = article.get("body", "") or ""
    subheadline = article.get("subheadline", "") or ""
    
    # Look for sentences with numbers, percentages, dollar amounts, names
    import re
    sentences = re.split(r'(?<=[.!?])\s+', body.replace('\n', ' '))
    
    scored = []
    for s in sentences:
        s = s.strip().lstrip('#').lstrip('*').lstrip('-').strip()
        s = s.replace('**', '').replace('__', '')
        if len(s) < 30 or len(s) > 200:
            continue
        if s.startswith('![') or s.startswith('['):
            continue
        
        score = 0
        # Has numbers/stats
        if re.search(r'\d+', s):
            score += 2
        # Has dollar/percent
        if re.search(r'[\$%₹]', s):
            score += 2
        # Has proper nouns (rough heuristic)
        if re.search(r'[A-Z][a-z]+\s[A-Z]', s):
            score += 1
        # Not too generic
        if any(w in s.lower() for w in ['million', 'billion', 'percent', 'first', 'largest', 'record']):
            score += 1
        
        if score > 0:
            scored.append((score, s))
    
    scored.sort(key=lambda x: -x[0])
    
    # Take top 3-4, deduplicate
    takeaways = []
    for _, s in scored:
        # Trim to reasonable length
        if len(s) > 150:
            s = s[:147] + '...'
        # Check no near-duplicate
        if not any(s[:50] in t for t in takeaways):
            takeaways.append(s)
        if len(takeaways) >= 4:
            break
    
    # If we don't have enough, use subheadline
    if len(takeaways) < 2 and subheadline:
        takeaways.insert(0, subheadline)
    
    return takeaways[:4]

def compose_post(article):
    """Compose a long-form X Premium post."""
    category = article.get("category", "news")
    emoji = CATEGORY_EMOJI.get(category, "📰")
    category_label = category.upper().replace("-", " ")
    headline = article.get("headline", "")
    slug = article.get("slug", "")
    
    summary = compose_summary(article)
    takeaways = extract_takeaways(article)
    
    # Build the post
    parts = [
        f"{emoji} {category_label} | The Videshi",
        "",
        "━━━━━━━━━━━━━━━━━━━━━━━━",
        "",
        headline.upper() if len(headline) < 80 else headline,
        "",
        summary,
        "",
        "━━━━━━━━━━━━━━━━━━━━━━━━",
        "",
        "Key Takeaways:",
        "",
    ]
    
    for t in takeaways:
        parts.append(f"▸ {t}")
    
    parts.extend([
        "",
        "━━━━━━━━━━━━━━━━━━━━━━━━",
        "",
        f"📰 Full story: thevideshi.com/articles/{slug}",
        "",
        "The Videshi — Your daily source for Indian diaspora news",
        "🌐 thevideshi.com",
    ])
    
    post = '\n'.join(parts)
    
    # Ensure under 4000 chars
    if len(post) > 3900:
        # Trim summary
        summary_words = summary.split()
        while len(post) > 3900 and len(summary_words) > 50:
            summary_words = summary_words[:-10]
            trimmed_summary = ' '.join(summary_words) + '...'
            parts_copy = parts.copy()
            # Reconstruct
            post = '\n'.join(parts).replace(summary, trimmed_summary)
            if len(post) <= 3900:
                break
    
    return post[:3950]

def download_image(image_url):
    """Download article image to temp file."""
    try:
        resp = requests.get(image_url, 
                          headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
                          timeout=15, stream=True)
        resp.raise_for_status()
        
        # Determine extension
        content_type = resp.headers.get('content-type', 'image/jpeg')
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
        
        # Check file size
        size = os.path.getsize(tmp.name)
        if size < 1000:
            print(f"  ⚠️  Image too small ({size} bytes), skipping image")
            os.unlink(tmp.name)
            return None
        
        return tmp.name
    except Exception as e:
        print(f"  ⚠️  Image download failed: {e}")
        return None

def upload_image_to_x(tmp_path):
    """Upload image to X via v1.1 API."""
    try:
        auth = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        api_v1 = tweepy.API(auth)
        media = api_v1.media_upload(filename=tmp_path)
        return media.media_id
    except Exception as e:
        print(f"  ⚠️  Image upload to X failed: {e}")
        return None

def post_tweet(text, media_id=None):
    """Post tweet using tweepy v2."""
    client = tweepy.Client(
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET,
    )
    kwargs = {"text": text}
    if media_id:
        kwargs["media_ids"] = [media_id]
    
    response = client.create_tweet(**kwargs)
    return response

def update_supabase(article_id):
    """Mark article as tweeted in Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article_id}"
    ts = datetime.utcnow().isoformat() + "Z"
    resp = requests.patch(url, json={"tweeted_at": ts}, headers=SB_HEADERS)
    resp.raise_for_status()
    return ts

def log_tweet(tweet_id, article):
    """Log tweet to local JSON file."""
    log_path = os.path.expanduser("~/workspace/the-videshi-news/pipeline/tweet-log.json")
    tweet_log = {}
    if os.path.exists(log_path):
        with open(log_path) as f:
            tweet_log = json.load(f)
    
    tweet_log[str(tweet_id)] = {
        "article_id": article["id"],
        "slug": article["slug"],
        "posted_at": datetime.utcnow().isoformat() + "Z"
    }
    
    with open(log_path, 'w') as f:
        json.dump(tweet_log, f, indent=2)

def main():
    print("=" * 60)
    print("🐦 The Videshi X Auto-Post (Long-Form)")
    print(f"   {datetime.utcnow().isoformat()}Z")
    print("=" * 60)
    
    # Fetch articles
    articles = fetch_untweeted()
    print(f"\n📋 Found {len(articles)} untweeted articles with images")
    
    if not articles:
        print("Nothing to post. Done.")
        return
    
    # Pick up to MAX_POSTS
    to_post = articles[:MAX_POSTS]
    print(f"📝 Will post {len(to_post)} articles\n")
    
    posted = 0
    errors = []
    
    for i, article in enumerate(to_post):
        print(f"\n{'─' * 50}")
        print(f"[{i+1}/{len(to_post)}] {article['headline'][:70]}...")
        print(f"   Category: {article['category']} | Slug: {article['slug'][:50]}")
        
        # Compose post
        post_text = compose_post(article)
        print(f"   Post length: {len(post_text)} chars")
        
        # Download and upload image
        media_id = None
        if article.get("image_url"):
            print(f"   📷 Downloading image...")
            tmp_path = download_image(article["image_url"])
            if tmp_path:
                print(f"   📤 Uploading to X...")
                media_id = upload_image_to_x(tmp_path)
                # Clean up
                try:
                    os.unlink(tmp_path)
                except:
                    pass
                if media_id:
                    print(f"   ✅ Image uploaded (media_id: {media_id})")
        
        # Post tweet
        try:
            print(f"   🐦 Posting tweet...")
            response = post_tweet(post_text, media_id)
            tweet_id = response.data["id"]
            tweet_url = f"https://x.com/thevideshi/status/{tweet_id}"
            print(f"   ✅ Posted! {tweet_url}")
            
            # Update Supabase
            ts = update_supabase(article["id"])
            print(f"   📊 Supabase updated (tweeted_at: {ts})")
            
            # Log tweet
            log_tweet(tweet_id, article)
            print(f"   📝 Tweet logged")
            
            posted += 1
            
        except Exception as e:
            error_msg = f"Failed to post '{article['headline'][:50]}': {e}"
            print(f"   ❌ {error_msg}")
            errors.append(error_msg)
        
        # Wait between posts
        if i < len(to_post) - 1:
            print(f"\n   ⏳ Waiting {POST_DELAY}s before next post...")
            time.sleep(POST_DELAY)
    
    # Summary
    print(f"\n{'=' * 60}")
    print(f"📊 SUMMARY")
    print(f"   Posted: {posted}/{len(to_post)}")
    if errors:
        print(f"   Errors: {len(errors)}")
        for e in errors:
            print(f"     ⚠️  {e}")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    main()
