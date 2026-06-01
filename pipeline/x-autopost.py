#!/usr/bin/env python3
"""Post recent Videshi articles to X (@thevideshi) as long-form posts with images."""

import json, os, sys, time, tempfile, re
from datetime import datetime, timezone

import requests
import tweepy

# ── Load env ──────────────────────────────────────────────────────
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

tw_env = load_env("~/workspace/.env.twitter")
sb_env = load_env("~/workspace/.env.supabase")

CONSUMER_KEY = tw_env["TWITTER_CONSUMER_KEY"]
CONSUMER_SECRET = tw_env["TWITTER_CONSUMER_SECRET"]
ACCESS_TOKEN = tw_env["TWITTER_ACCESS_TOKEN"]
ACCESS_TOKEN_SECRET = tw_env["TWITTER_ACCESS_TOKEN_SECRET"]
SUPABASE_KEY = sb_env["SUPABASE_SERVICE_ROLE_KEY"]
SUPABASE_URL = "https://lboecaekpynbpyijrbfz.supabase.co"

# ── Category emoji map ────────────────────────────────────────────
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

# ── Fetch untweeted articles ──────────────────────────────────────
headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
}

resp = requests.get(
    f"{SUPABASE_URL}/rest/v1/p2_articles",
    headers=headers,
    params={
        "status": "eq.published",
        "tweeted_at": "is.null",
        "order": "published_at.desc",
        "limit": "20",
        "select": "id,slug,headline,subheadline,category,tags,image_url,body",
    },
    timeout=30,
)
resp.raise_for_status()
articles = resp.json()
print(f"Found {len(articles)} untweeted articles")

# Filter out articles with no image_url and pick up to 4
eligible = [a for a in articles if a.get("image_url")]
selected = eligible[:4]
print(f"Selected {len(selected)} articles to post (with images)")

if not selected:
    print("Nothing to post.")
    sys.exit(0)

# ── Helper: strip markdown to plain text ──────────────────────────
def strip_md(text):
    if not text:
        return ""
    # Remove markdown images
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    # Remove markdown links but keep text
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
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Collapse whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

# ── Helper: extract key facts from body ───────────────────────────
def extract_summary_and_facts(article):
    """Extract body text and prepare summary material."""
    body = strip_md(article.get("body", "") or "")
    headline = article.get("headline", "")
    subheadline = article.get("subheadline", "")
    
    # Get first ~800 words of body for context
    words = body.split()
    context = " ".join(words[:800])
    
    return {
        "headline": headline,
        "subheadline": subheadline,
        "body_excerpt": context,
        "full_body": body,
    }

# ── Compose post using article content ────────────────────────────
def compose_post(article):
    """Compose a long-form X post from article data."""
    cat = (article.get("category") or "news").lower()
    emoji = CATEGORY_EMOJI.get(cat, "📰")
    cat_label = cat.upper().replace("-", " ")
    slug = article.get("slug", "")
    
    info = extract_summary_and_facts(article)
    headline = info["headline"]
    subheadline = info["subheadline"] or ""
    body = info["full_body"]
    
    # Extract paragraphs from body (skip very short ones)
    paragraphs = [p.strip() for p in body.split('\n\n') if len(p.strip()) > 40]
    
    # Build summary: take first 2-3 substantive paragraphs, trim to ~200 words
    summary_paras = []
    word_count = 0
    for p in paragraphs[:6]:
        p_words = p.split()
        if word_count + len(p_words) > 250:
            # Trim this paragraph
            remaining = 250 - word_count
            if remaining > 20:
                summary_paras.append(" ".join(p_words[:remaining]) + "…")
            break
        summary_paras.append(p)
        word_count += len(p_words)
        if word_count > 150 and len(summary_paras) >= 2:
            break
    
    summary_text = "\n\n".join(summary_paras) if summary_paras else (subheadline or headline)
    
    # Extract key takeaways - look for sentences with numbers, names, or strong facts
    fact_candidates = []
    for p in paragraphs:
        sentences = re.split(r'(?<=[.!?])\s+', p)
        for s in sentences:
            s = s.strip()
            if len(s) > 30 and len(s) < 200:
                # Prefer sentences with numbers, percentages, dollar amounts, or proper nouns
                if re.search(r'\d+|percent|billion|million|crore|lakh|\$|₹', s, re.I):
                    fact_candidates.append(s)
    
    # Also use subheadline as a fact source
    if subheadline and len(subheadline) > 20:
        fact_candidates.insert(0, subheadline)
    
    # Pick 3-4 unique facts
    seen = set()
    facts = []
    for f in fact_candidates:
        f_key = f[:50].lower()
        if f_key not in seen:
            seen.add(f_key)
            facts.append(f)
        if len(facts) >= 4:
            break
    
    # If we don't have enough facts, pull from early paragraphs
    if len(facts) < 3:
        for p in paragraphs[:4]:
            sentences = re.split(r'(?<=[.!?])\s+', p)
            for s in sentences:
                s = s.strip()
                if len(s) > 30 and len(s) < 200 and s[:50].lower() not in seen:
                    seen.add(s[:50].lower())
                    facts.append(s)
                    if len(facts) >= 3:
                        break
            if len(facts) >= 3:
                break
    
    # Build the post
    divider = "━━━━━━━━━━━━━━━━━━━━━━━━"
    
    lines = [
        f"{emoji} {cat_label} | The Videshi",
        "",
        divider,
        "",
        headline.upper() if len(headline) < 80 else headline,
        "",
        summary_text,
        "",
        divider,
        "",
        "Key Takeaways:",
        "",
    ]
    
    for f in facts[:4]:
        # Trim fact if too long
        if len(f) > 180:
            f = f[:177] + "…"
        lines.append(f"▸ {f}")
    
    lines.extend([
        "",
        divider,
        "",
        f"📰 Full story: thevideshi.com/articles/{slug}",
        "",
        "The Videshi — Your daily source for Indian diaspora news",
        "🌐 thevideshi.com",
    ])
    
    post_text = "\n".join(lines)
    
    # Trim if over 4000 chars
    if len(post_text) > 3900:
        # Shorten summary
        summary_words = summary_text.split()
        summary_text = " ".join(summary_words[:100]) + "…"
        lines[6] = summary_text
        post_text = "\n".join(lines)
    
    if len(post_text) > 3900:
        post_text = post_text[:3900] + "…"
    
    return post_text

# ── Setup tweepy clients ──────────────────────────────────────────
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

# ── Post articles ─────────────────────────────────────────────────
log_path = os.path.expanduser("~/workspace/the-videshi-news/pipeline/tweet-log.json")
tweet_log = json.load(open(log_path)) if os.path.exists(log_path) else {}

posted = 0
errors = []

for i, article in enumerate(selected):
    slug = article.get("slug", "unknown")
    article_id = article["id"]
    image_url = article.get("image_url", "")
    
    print(f"\n{'='*60}")
    print(f"[{i+1}/{len(selected)}] Posting: {article.get('headline', slug)[:80]}")
    print(f"  Category: {article.get('category', 'unknown')}")
    print(f"  Slug: {slug}")
    
    # Compose post
    post_text = compose_post(article)
    print(f"  Post length: {len(post_text)} chars")
    
    # Try to upload image
    media_id = None
    tmp_path = None
    if image_url:
        try:
            print(f"  Downloading image: {image_url[:80]}...")
            img_resp = requests.get(image_url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
            img_resp.raise_for_status()
            
            # Determine extension from content type
            ct = img_resp.headers.get("Content-Type", "image/jpeg")
            ext = ".jpg"
            if "png" in ct:
                ext = ".png"
            elif "webp" in ct:
                ext = ".webp"
            elif "gif" in ct:
                ext = ".gif"
            
            tmp_fd, tmp_path = tempfile.mkstemp(suffix=ext)
            with os.fdopen(tmp_fd, 'wb') as f:
                f.write(img_resp.content)
            
            print(f"  Uploading image to X ({len(img_resp.content)} bytes)...")
            media = api_v1.media_upload(filename=tmp_path)
            media_id = media.media_id
            print(f"  Media uploaded: {media_id}")
        except Exception as e:
            print(f"  ⚠️ Image upload failed: {e} — posting without image")
            media_id = None
        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    # Post tweet
    try:
        kwargs = {"text": post_text}
        if media_id:
            kwargs["media_ids"] = [media_id]
        
        tweet_resp = client.create_tweet(**kwargs)
        tweet_id = tweet_resp.data["id"]
        tweet_url = f"https://x.com/thevideshi/status/{tweet_id}"
        print(f"  ✅ Posted: {tweet_url}")
        
        # Update Supabase
        now_utc = datetime.now(timezone.utc).isoformat()
        patch_resp = requests.patch(
            f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article_id}",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "return=minimal",
            },
            json={"tweeted_at": now_utc},
            timeout=15,
        )
        if patch_resp.status_code < 300:
            print(f"  ✅ Supabase updated (tweeted_at)")
        else:
            print(f"  ⚠️ Supabase update failed: {patch_resp.status_code} {patch_resp.text}")
        
        # Log tweet
        tweet_log[str(tweet_id)] = {
            "article_id": article_id,
            "slug": slug,
            "posted_at": now_utc,
        }
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        with open(log_path, 'w') as f:
            json.dump(tweet_log, f, indent=2)
        
        posted += 1
        
    except Exception as e:
        err_msg = f"Failed to post '{slug}': {e}"
        print(f"  ❌ {err_msg}")
        errors.append(err_msg)
    
    # Wait between posts
    if i < len(selected) - 1:
        print("  Waiting 30s before next post...")
        time.sleep(30)

# ── Summary ───────────────────────────────────────────────────────
print(f"\n{'='*60}")
print(f"SUMMARY: Posted {posted}/{len(selected)} articles to @thevideshi")
if errors:
    print(f"Errors ({len(errors)}):")
    for e in errors:
        print(f"  - {e}")
print(f"{'='*60}")
