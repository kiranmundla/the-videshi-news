#!/usr/bin/env python3
"""Distribute prebuilt reels to IG, YT, Threads, X."""

import os, sys, json, time, tempfile, requests
from datetime import datetime, timezone

# --- Load env files ---
def load_env(path):
    d = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                k, v = line.split('=', 1)
                k = k.replace('export ', '').strip()
                d[k] = v.strip()
    return d

sb = load_env('~/workspace/.env.supabase')
ig = load_env('~/workspace/.env.instagram')
yt = load_env('~/workspace/.env.youtube')
th = load_env('~/workspace/.env.threads')
tw = load_env('~/workspace/.env.twitter')

SUPABASE_URL = sb['SUPABASE_URL']
SUPABASE_KEY = sb['SUPABASE_SERVICE_ROLE_KEY']
SB_HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=minimal'
}

IG_TOKEN = ig['INSTAGRAM_ACCESS_TOKEN']
IG_USER_ID = ig['INSTAGRAM_USER_ID']
THREADS_TOKEN = th['THREADS_ACCESS_TOKEN']
THREADS_USER_ID = '26854521280856098'

YT_LOG_PATH = os.path.expanduser('~/workspace/the-videshi-news/pipeline/youtube-log.json')

results = []

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def patch_reel(reel_id, data):
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/prebuilt_reels?id=eq.{reel_id}",
        headers=SB_HEADERS, json=data
    )
    if r.status_code not in (200, 204):
        print(f"  PATCH error {r.status_code}: {r.text}")

# --- Fetch ALL qa_passed reels for dedup ---
print("Fetching all qa_passed reels for article-level dedup...")
all_reels_resp = requests.get(
    f"{SUPABASE_URL}/rest/v1/prebuilt_reels?qa_passed=eq.true&select=id,article_id,article_slug,ig_posted_at,yt_posted_at,threads_posted_at,x_posted_at&limit=500",
    headers={k: v for k, v in SB_HEADERS.items() if k != 'Prefer'}
)
all_reels = all_reels_resp.json()
print(f"  Total qa_passed reels: {len(all_reels)}")

# Build article-level posted sets
ig_posted_articles = set()
yt_posted_articles = set()
threads_posted_articles = set()
x_posted_articles = set()

for r in all_reels:
    aid = r['article_id']
    if r.get('ig_posted_at'): ig_posted_articles.add(aid)
    if r.get('yt_posted_at'): yt_posted_articles.add(aid)
    if r.get('threads_posted_at') and r.get('threads_post_id') != 'skipped-duplicate':
        threads_posted_articles.add(aid)
    if r.get('x_posted_at') and r.get('x_tweet_id') not in ('dedup-skip', None):
        x_posted_articles.add(aid)

print(f"  Articles with IG: {len(ig_posted_articles)}, YT: {len(yt_posted_articles)}, Threads: {len(threads_posted_articles)}")

# --- Pick reels to distribute ---
# YouTube: ONE variant per article, alternating voiceover/music-only across articles.
# X is handled separately by x-autopost (article text + carousel only, no video).
# IG/Threads: one video per article (voiceover preferred).
candidates_resp = requests.get(
    f"{SUPABASE_URL}/rest/v1/prebuilt_reels?qa_passed=eq.true&order=created_at.desc&limit=10&select=id,article_id,article_slug,headline,video_url,video_path,caption,status,carousel_images,ig_posted_at,yt_posted_at,yt_video_id,threads_posted_at,threads_post_id,x_posted_at,x_tweet_id",
    headers={k: v for k, v in SB_HEADERS.items() if k != 'Prefer'}
)
candidates = candidates_resp.json()

seen_articles_social = set()  # dedup IG/Threads per article (one variant)

# Alternate YouTube variants: count existing YT uploads to decide next variant
yt_upload_count = len(yt_posted_articles)

work_queue = []
# First pass: collect all candidates per article for YT variant selection
yt_candidates_by_article = {}
for reel in candidates:
    aid = reel['article_id']
    if aid not in yt_posted_articles and not reel.get('yt_posted_at'):
        yt_candidates_by_article.setdefault(aid, []).append(reel)

# Pick one variant per article for YouTube, alternating voice/music
yt_selected_reel_ids = set()
for aid, reels in yt_candidates_by_article.items():
    want_voiceover = (yt_upload_count % 2 == 0)
    # Try preferred variant first, fall back to whatever's available
    picked = None
    for r in reels:
        vp = r.get('video_path') or ''
        if ('voiceover' in vp) == want_voiceover:
            picked = r
            break
    if not picked:
        picked = reels[0]  # fallback to whatever variant exists
    yt_selected_reel_ids.add(picked['id'])
    yt_upload_count += 1

for reel in candidates:
    aid = reel['article_id']
    
    needs = []
    # YouTube: ONE per article, alternating voiceover/music-only
    if reel['id'] in yt_selected_reel_ids:
        needs.append('yt')
    # IG/Threads: one per article
    if aid not in seen_articles_social:
        if aid not in ig_posted_articles and not reel.get('ig_posted_at'):
            needs.append('ig')
        if aid not in threads_posted_articles and not reel.get('threads_posted_at'):
            needs.append('threads')
    # X: NO video reels — handled by x-autopost (article + carousel only)
    # X CAROUSEL: if this reel has carousel_images and article hasn't had a carousel posted
    if reel.get('carousel_images') and aid not in x_posted_articles:
        needs.append('x_carousel')
    
    if needs:
        reel['_needs'] = needs
        work_queue.append(reel)
        if 'ig' in needs or 'threads' in needs:
            seen_articles_social.add(aid)
        if 'x_carousel' in needs:
            x_posted_articles.add(aid)
    
    if len(work_queue) >= 6:
        break

if not work_queue:
    print("No reels need distribution. Done.")
    sys.exit(0)

print(f"\nWill distribute {len(work_queue)} reels:")
for reel in work_queue:
    print(f"  {reel['headline'][:60]}... → {reel['_needs']}")

# --- Platform posting functions ---

def post_instagram_reel(reel, video_url, caption):
    """Post reel to Instagram."""
    print(f"  [IG] Creating container...")
    r = requests.post(
        f"https://graph.instagram.com/v22.0/{IG_USER_ID}/media",
        data={
            'media_type': 'REELS',
            'video_url': video_url,
            'caption': caption[:2200],
            'access_token': IG_TOKEN,
        }
    )
    if r.status_code != 200:
        return f"IG container error: {r.status_code} {r.text}"
    container_id = r.json().get('id')
    if not container_id:
        return f"IG no container ID: {r.json()}"
    print(f"  [IG] Container {container_id}, polling status...")
    
    for attempt in range(24):  # 2 min max
        time.sleep(5)
        sr = requests.get(
            f"https://graph.instagram.com/v22.0/{container_id}",
            params={'fields': 'status_code,status', 'access_token': IG_TOKEN}
        )
        status = sr.json().get('status_code', '')
        print(f"  [IG] Poll {attempt+1}: {status}")
        if status == 'FINISHED':
            break
        if status == 'ERROR':
            return f"IG container error: {sr.json()}"
    else:
        return "IG timeout waiting for container"
    
    print(f"  [IG] Publishing...")
    pr = requests.post(
        f"https://graph.instagram.com/v22.0/{IG_USER_ID}/media_publish",
        data={'creation_id': container_id, 'access_token': IG_TOKEN}
    )
    if pr.status_code != 200:
        return f"IG publish error: {pr.status_code} {pr.text}"
    media_id = pr.json().get('id')
    patch_reel(reel['id'], {'ig_posted_at': now_iso(), 'ig_media_id': str(media_id)})
    return f"OK (media_id={media_id})"



def letterbox_for_youtube(vertical_path):
    """Convert 9:16 vertical video to 16:9 landscape with branded navy side panels for YouTube.
    YouTube auto-classifies vertical ≤3min as Shorts; horizontal → regular Video."""
    import subprocess
    landscape_path = vertical_path.replace('.mp4', '_landscape.mp4')
    # Navy side panels (#0a1628), vertical video centered in 1920x1080 frame
    cmd = [
        'ffmpeg', '-y', '-i', vertical_path,
        '-vf', 'split[original][blur];'
               '[blur]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,boxblur=40[bg];'
               '[original]scale=-2:1080[fg];'
               '[bg][fg]overlay=(W-w)/2:(H-h)/2',
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
        '-c:a', 'aac', '-b:a', '128k',
        '-movflags', '+faststart',
        landscape_path
    ]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if r.returncode != 0:
            # Fallback: simple navy padding instead of blurred background
            cmd_simple = [
                'ffmpeg', '-y', '-i', vertical_path,
                '-vf', 'pad=1920:1080:(1920-iw)/2:(1080-ih)/2:color=0a1628,scale=1920:1080',
                '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
                '-c:a', 'aac', '-b:a', '128k',
                '-movflags', '+faststart',
                landscape_path
            ]
            r2 = subprocess.run(cmd_simple, capture_output=True, text=True, timeout=120)
            if r2.returncode != 0:
                print(f"  [YT] Letterbox failed: {r2.stderr[-300:]}")
                return None
        print(f"  [YT] Letterboxed to 16:9: {os.path.getsize(landscape_path)} bytes")
        return landscape_path
    except Exception as e:
        print(f"  [YT] Letterbox error: {e}")
        return None


def post_youtube_video(reel, video_path, headline, caption):
    """Post video to YouTube as a regular Video (vertical, no letterboxing)."""
    print(f"  [YT] Refreshing OAuth token...")
    token_r = requests.post('https://oauth2.googleapis.com/token', data={
        'client_id': yt['YOUTUBE_CLIENT_ID'],
        'client_secret': yt['YOUTUBE_CLIENT_SECRET'],
        'refresh_token': yt['YOUTUBE_REFRESH_TOKEN'],
        'grant_type': 'refresh_token',
    })
    if token_r.status_code != 200:
        return f"YT token error: {token_r.status_code} {token_r.text}"
    access_token = token_r.json()['access_token']
    
    slug = reel.get('article_slug') or ''
    
    # Detect variant from video_path
    vpath = reel.get('video_path') or ''
    is_voiceover = 'voiceover' in vpath
    variant_tag = 'voiceover' if is_voiceover else 'music-only'
    
    # Check youtube-log.json for slug+variant dedup
    yt_log = {}
    if os.path.exists(YT_LOG_PATH):
        with open(YT_LOG_PATH) as f:
            yt_log = json.load(f)
    dedup_key = f"{slug}:{variant_tag}"
    for vid, info in yt_log.items():
        log_slug = info.get('article_slug', '')
        log_variant = info.get('variant', '')
        # Match on slug+variant combo
        if log_slug == slug and log_variant == variant_tag:
            patch_reel(reel['id'], {'yt_posted_at': now_iso(), 'yt_video_id': f'dedup-log-{vid}'})
            return f"SKIP (slug+variant already in youtube-log: {vid})"
    
    # YouTube hard-limits titles to 100 chars.
    # Differentiate variants: voiceover gets "🎙️" suffix, music gets "🎵"
    variant_suffix = " 🎙️" if is_voiceover else " 🎵"
    max_headline = 100 - len(variant_suffix)
    title = headline[:max_headline].rstrip() + variant_suffix
    
    # Category-specific hashtags
    caption_lower = caption.lower()
    extra_tags = []
    if any(w in caption_lower for w in ['h1b', 'visa', 'green card', 'immigration', 'uscis', 'eb-2', 'eb2']):
        extra_tags = ['H1B', 'GreenCard', 'Immigration', 'USCIS', 'EB2']
    elif any(w in caption_lower for w in ['cricket', 'ipl', 'bcci', 'kohli', 'rohit']):
        extra_tags = ['Cricket', 'IPL', 'BCCI']
    elif any(w in caption_lower for w in ['bollywood', 'actor', 'actress', 'film', 'movie']):
        extra_tags = ['Bollywood', 'Entertainment', 'Movies']
    elif any(w in caption_lower for w in ['market', 'stock', 'fund', 'investor', 'equity', 'mutual fund', 'sip']):
        extra_tags = ['StockMarket', 'MutualFunds', 'Investing', 'IndianMarkets']
    elif any(w in caption_lower for w in ['remittance', 'gulf', 'economy', 'rbi']):
        extra_tags = ['IndianEconomy', 'Remittances', 'RBI']
    
    tags = ['The Videshi', 'Indian Diaspora', 'NRI', 'India News'] + extra_tags
    tags = tags[:12]
    
    description = f"{caption}\n\n#TheVideshi #IndianDiaspora #NRI #IndiaNews"
    for t in extra_tags[:5]:
        description += f" #{t}"
    
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': tags,
            'categoryId': '25',
        },
        'status': {
            'privacyStatus': 'public',
            'selfDeclaredMadeForKids': False,
        }
    }
    
    file_size = os.path.getsize(video_path)
    print(f"  [YT] Starting resumable upload ({file_size} bytes)...")
    
    init_r = requests.post(
        'https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status',
        headers={
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json; charset=UTF-8',
            'X-Upload-Content-Type': 'video/mp4',
            'X-Upload-Content-Length': str(file_size),
        },
        json=body
    )
    if init_r.status_code != 200:
        return f"YT upload init error: {init_r.status_code} {init_r.text}"
    
    upload_url = init_r.headers.get('Location')
    if not upload_url:
        return "YT no upload URL in response"
    
    with open(video_path, 'rb') as f:
        up_r = requests.put(upload_url, data=f, headers={
            'Content-Type': 'video/mp4',
            'Content-Length': str(file_size),
        })
    
    if up_r.status_code not in (200, 201):
        return f"YT upload error: {up_r.status_code} {up_r.text[:500]}"
    
    video_id = up_r.json().get('id')
    print(f"  [YT] Uploaded: {video_id}")
    
    patch_reel(reel['id'], {'yt_posted_at': now_iso(), 'yt_video_id': video_id})
    
    # Log to youtube-log.json
    yt_log[reel['id']] = {
        'article_slug': slug,
        'variant': variant_tag,
        'uploaded_at': now_iso(),
        'video_id': video_id,
    }
    with open(YT_LOG_PATH, 'w') as f:
        json.dump(yt_log, f, indent=2)
    
    return f"OK (video_id={video_id})"


def post_threads(reel, video_url, caption):
    """Post to Threads."""
    print(f"  [Threads] Creating container...")
    r = requests.post(
        f"https://graph.threads.net/v1.0/{THREADS_USER_ID}/threads",
        data={
            'media_type': 'VIDEO',
            'video_url': video_url,
            'text': caption[:500],
            'access_token': THREADS_TOKEN,
        }
    )
    if r.status_code != 200:
        return f"Threads container error: {r.status_code} {r.text}"
    container_id = r.json().get('id')
    if not container_id:
        return f"Threads no container ID: {r.json()}"
    
    print(f"  [Threads] Container {container_id}, polling...")
    for attempt in range(30):  # 5 min max
        time.sleep(10)
        sr = requests.get(
            f"https://graph.threads.net/v1.0/{container_id}",
            params={'fields': 'status', 'access_token': THREADS_TOKEN}
        )
        status = sr.json().get('status', '')
        print(f"  [Threads] Poll {attempt+1}: {status}")
        if status == 'FINISHED':
            break
        if status == 'ERROR':
            return f"Threads container error: {sr.json()}"
    else:
        return "Threads timeout waiting for container"
    
    print(f"  [Threads] Publishing...")
    pr = requests.post(
        f"https://graph.threads.net/v1.0/{THREADS_USER_ID}/threads_publish",
        data={'creation_id': container_id, 'access_token': THREADS_TOKEN}
    )
    if pr.status_code != 200:
        return f"Threads publish error: {pr.status_code} {pr.text}"
    post_id = pr.json().get('id')
    patch_reel(reel['id'], {'threads_posted_at': now_iso(), 'threads_post_id': str(post_id)})
    return f"OK (post_id={post_id})"


def post_x_tweet(reel, video_path, headline, slug):
    """Post to X/Twitter."""
    # Pre-flight: check spend meter before uploading large video files
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("x_spend", os.path.join(os.path.dirname(__file__), "x_spend.py"))
        if spec and spec.loader:
            xm = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(xm)
            pct = xm.current_spend_pct()
            if pct >= 97:
                return f"SKIP (X spend at {pct:.0f}% — credits likely depleted, skipping video upload)"
    except Exception:
        pass  # spend meter unavailable — proceed anyway
    import tweepy
    
    auth = tweepy.OAuth1UserHandler(
        tw['TWITTER_CONSUMER_KEY'], tw['TWITTER_CONSUMER_SECRET'],
        tw['TWITTER_ACCESS_TOKEN'], tw['TWITTER_ACCESS_TOKEN_SECRET']
    )
    api_v1 = tweepy.API(auth)
    
    client = tweepy.Client(
        consumer_key=tw['TWITTER_CONSUMER_KEY'],
        consumer_secret=tw['TWITTER_CONSUMER_SECRET'],
        access_token=tw['TWITTER_ACCESS_TOKEN'],
        access_token_secret=tw['TWITTER_ACCESS_TOKEN_SECRET'],
    )
    
    print(f"  [X] Uploading video (chunked, 1MB)...")
    # Manual chunked upload with requests for proxy compatibility
    upload_url = 'https://upload.twitter.com/1.1/media/upload.json'
    file_size = os.path.getsize(video_path)
    
    # INIT
    init_r = requests.post(upload_url, auth=auth.apply_auth(), data={
        'command': 'INIT',
        'media_type': 'video/mp4',
        'total_bytes': str(file_size),
        'media_category': 'tweet_video',
    })
    if init_r.status_code not in (200, 201, 202):
        return f"X INIT error: {init_r.status_code} {init_r.text}"
    media_id = init_r.json()['media_id_string']
    
    # APPEND in 1MB chunks
    chunk_size = 1 * 1024 * 1024
    segment = 0
    with open(video_path, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            for retry in range(3):
                try:
                    app_r = requests.post(upload_url, auth=auth.apply_auth(),
                        data={'command': 'APPEND', 'media_id': media_id, 'segment_index': str(segment)},
                        files={'media': ('chunk.mp4', chunk, 'application/octet-stream')},
                        timeout=30,
                    )
                    if app_r.status_code in (200, 201, 202, 204):
                        break
                except Exception as e:
                    if retry == 2:
                        return f"X APPEND error seg {segment}: {e}"
                    time.sleep(2 ** retry)
            segment += 1
    
    # FINALIZE
    fin_r = requests.post(upload_url, auth=auth.apply_auth(), data={
        'command': 'FINALIZE', 'media_id': media_id
    })
    if fin_r.status_code not in (200, 201):
        return f"X FINALIZE error: {fin_r.status_code} {fin_r.text}"
    
    proc = fin_r.json().get('processing_info')
    if proc:
        for _ in range(30):
            wait = proc.get('check_after_secs', 5)
            time.sleep(wait)
            st_r = requests.get(upload_url, auth=auth.apply_auth(), params={
                'command': 'STATUS', 'media_id': media_id
            })
            proc = st_r.json().get('processing_info', {})
            state = proc.get('state', '')
            print(f"  [X] Processing: {state}")
            if state == 'succeeded':
                break
            if state == 'failed':
                return f"X processing failed: {proc}"
    
    # Tweet
    tweet_text = f"🇮🇳 {headline[:220]}\n\n#IndianDiaspora #NRI #TheVideshi"
    if len(tweet_text) > 280:
        tweet_text = f"🇮🇳 {headline[:200]}\n\n#IndianDiaspora #NRI"
    
    print(f"  [X] Tweeting ({len(tweet_text)} chars)...")
    tweet_r = client.create_tweet(text=tweet_text, media_ids=[media_id])
    tweet_id = tweet_r.data['id']
    
    patch_reel(reel['id'], {'x_posted_at': now_iso(), 'x_tweet_id': str(tweet_id)})
    return f"OK (tweet_id={tweet_id})"


def post_x_carousel(reel, headline, slug):
    """Post carousel images to X as a multi-image tweet."""
    carousel_images = reel.get('carousel_images') or []
    # Filter to image files only (skip .mp4 animated cards)
    image_urls = [u for u in carousel_images if u.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
    if not image_urls:
        return "SKIP (no carousel images)"
    
    # Skip first (hook) and last (CTA), take up to 4 data-rich slides
    if len(image_urls) > 5:
        image_urls = image_urls[1:-1]
    chosen = image_urls[:4]
    
    # Pre-flight spend check
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("x_spend", os.path.join(os.path.dirname(__file__), "x_spend.py"))
        if spec and spec.loader:
            xm = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(xm)
            pct = xm.current_spend_pct()
            if pct >= 97:
                return f"SKIP (X spend at {pct:.0f}%)"
    except Exception:
        pass
    
    import tweepy
    auth = tweepy.OAuth1UserHandler(
        tw['TWITTER_CONSUMER_KEY'], tw['TWITTER_CONSUMER_SECRET'],
        tw['TWITTER_ACCESS_TOKEN'], tw['TWITTER_ACCESS_TOKEN_SECRET']
    )
    api_v1 = tweepy.API(auth)
    client = tweepy.Client(
        consumer_key=tw['TWITTER_CONSUMER_KEY'],
        consumer_secret=tw['TWITTER_CONSUMER_SECRET'],
        access_token=tw['TWITTER_ACCESS_TOKEN'],
        access_token_secret=tw['TWITTER_ACCESS_TOKEN_SECRET'],
    )
    
    # Upload carousel images
    media_ids = []
    print(f"  [X-CAROUSEL] Uploading {len(chosen)} images...")
    for ci, img_url in enumerate(chosen):
        try:
            r = requests.get(img_url, headers={"User-Agent": "TheVideshi/1.0"}, timeout=15)
            r.raise_for_status()
            ext = '.png' if 'png' in r.headers.get('content-type', '') else '.jpg'
            with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
                tmp.write(r.content)
                tmp_path = tmp.name
            media = api_v1.media_upload(filename=tmp_path)
            media_ids.append(media.media_id)
            os.unlink(tmp_path)
            print(f"    Slide {ci}: media_id={media.media_id}")
        except Exception as e:
            print(f"    Slide {ci} failed: {e}")
    
    if not media_ids:
        return "SKIP (all image uploads failed)"
    
    tweet_text = f"📊 {headline[:220]}\n\n#IndianDiaspora #NRI #TheVideshi"
    if len(tweet_text) > 280:
        tweet_text = f"📊 {headline[:200]}\n\n#IndianDiaspora #NRI"
    
    print(f"  [X-CAROUSEL] Tweeting with {len(media_ids)} images...")
    tweet_r = client.create_tweet(text=tweet_text, media_ids=media_ids)
    tweet_id = tweet_r.data['id']
    
    # Mark as posted
    patch_reel(reel['id'], {'x_posted_at': now_iso(), 'x_tweet_id': str(tweet_id)})
    
    # Track spend
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("x_spend", os.path.join(os.path.dirname(__file__), "x_spend.py"))
        if spec and spec.loader:
            xm = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(xm)
            xm.add(writes=1)
    except Exception:
        pass
    
    return f"OK (tweet_id={tweet_id}, {len(media_ids)} images)"


# --- Main distribution loop ---
errors = []

for i, reel in enumerate(work_queue):
    print(f"\n{'='*60}")
    print(f"Reel {i+1}/{len(work_queue)}: {reel['headline'][:70]}")
    print(f"  ID: {reel['id']}")
    print(f"  Needs: {reel['_needs']}")
    
    video_url = reel['video_url']
    caption = reel.get('caption') or ''
    headline = reel.get('headline') or ''
    slug = reel.get('article_slug', '')
    
    # Download video once for platforms that need local file
    local_video = None
    if 'yt' in reel['_needs']:
        print(f"  Downloading video...")
        tmp = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
        vr = requests.get(video_url, stream=True)
        for chunk in vr.iter_content(8192):
            tmp.write(chunk)
        tmp.close()
        local_video = tmp.name
        print(f"  Downloaded: {os.path.getsize(local_video)} bytes")
    
    # Post to each needed platform
    # NOTE: X video posting removed — X only gets article text + carousel via x-autopost
    for platform in reel['_needs']:
        try:
            if platform == 'ig':
                result = post_instagram_reel(reel, video_url, caption)
            elif platform == 'yt':
                # Upload vertical as-is — YouTube handles vertical natively.
                # On mobile: plays full-screen. On desktop: YouTube adds clean pillarboxing.
                # No more manual letterboxing (looked terrible on phone).
                result = post_youtube_video(reel, local_video, headline, caption)
            elif platform == 'threads':
                result = post_threads(reel, video_url, caption)
            elif platform == 'x_carousel':
                result = post_x_carousel(reel, headline, slug)
            
            print(f"  [{platform.upper()}] Result: {result}")
            results.append((reel['headline'][:50], platform, result))
            
            if not result.startswith('OK') and not result.startswith('SKIP'):
                errors.append(f"{platform.upper()}: {result}")
        except Exception as e:
            err_msg = f"{platform.upper()} exception: {e}"
            print(f"  [{platform.upper()}] ERROR: {e}")
            errors.append(err_msg)
            results.append((reel['headline'][:50], platform, f"ERROR: {e}"))
        
        # Wait between platforms
        time.sleep(15)
    
    # Clean up temp file
    if local_video and os.path.exists(local_video):
        os.unlink(local_video)

# --- Summary ---
print(f"\n{'='*60}")
print("DISTRIBUTION SUMMARY")
print(f"{'='*60}")
for headline, platform, result in results:
    status = "✅" if result.startswith("OK") else "⏭️" if result.startswith("SKIP") else "❌"
    print(f"  {status} {headline}... → {platform.upper()}: {result}")

if errors:
    print(f"\n❌ ERRORS ({len(errors)}):")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
else:
    print(f"\n✅ All done. {len(results)} posts across {len(work_queue)} reels.")
