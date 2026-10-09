#!/usr/bin/env python3
"""Upload unuploaded reels to YouTube Shorts for The Videshi.

Uses curl subprocess for all HTTP (Python urllib/requests fail through the proxy).
YouTube resumable upload requires part=snippet,status in the init URL.
"""

import json, os, sys, re, subprocess, time, glob, importlib.util
from datetime import datetime, timezone

# --- Import newsletter scoring (single source of truth for importance) ---
_newsletter_path = os.path.expanduser('~/workspace/the-videshi-news/pipeline/send-newsletter-daily.py')
_newsletter_spec = importlib.util.spec_from_file_location("newsletter_daily", _newsletter_path)
_newsletter = importlib.util.module_from_spec(_newsletter_spec)
try:
    _newsletter_spec.loader.exec_module(_newsletter)
    score_article = _newsletter.score_article
    _scoring_available = True
except Exception as e:
    print(f"WARN: could not import newsletter scoring: {e} — using fallback")
    score_article = None
    _scoring_available = False

def shorts_virality_boost(a):
    """Extra score for high-stakes, high-emotion stories that perform as Shorts.
    The two breakout hits (700+ views) were high-emotion, high-stakes stories."""
    boost = 0
    text = ((a.get("headline") or "") + " " + (a.get("subheadline") or "")).lower()

    # Breaking / urgent — highest Shorts potential
    if re.search(r'\b(breaking|exclusive|just in|developing|alert)\b', text):
        boost += 3

    # High-emotion, high-stakes topics
    high_stakes = ['trump', 'modi', 'deportation', 'deported', 'ban', 'banned', 'crisis',
                   'war', 'attack', 'killed', 'arrest', 'scam', 'fraud', 'protest',
                   'election', 'verdict', 'resigns', 'suspended', 'crash']
    if any(w in text for w in high_stakes):
        boost += 2

    # Immigration — core audience, consistently strong
    if re.search(r'\b(h-1b|h1b|visa|green card|uscis|immigration|opt|deportation)\b', text):
        boost += 2

    # Routine / low-emotion topics — penalize
    routine = ['gold price', 'silver price', 'market roundup', 'weather', 'sensex today',
               'nifty today', 'daily horoscope', 'petrol price', 'diesel price']
    if any(w in text for w in routine):
        boost -= 5

    return boost

def score_for_shorts(a):
    """Combined score: newsletter editorial quality + Shorts virality signals."""
    base = score_article(a) if _scoring_available and score_article else 0
    return base + shorts_virality_boost(a)

# --- Duration check ---
def get_duration_seconds(video_path):
    """Return video duration in seconds via ffprobe, or None on failure."""
    try:
        r = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
             '-of', 'default=noprint_wrappers=1:nokey=1', video_path],
            capture_output=True, text=True, timeout=30,
        )
        return float(r.stdout.strip())
    except Exception:
        return None

MAX_DURATION = 42   # hard skip — research target is 25-40s for the kinetic news format
PREFERRED_MIN = 25   # prefer 25-40s; completion rate drives reach, not raw shortness
PREFERRED_MAX = 40

def extract_slug_fragments(filename):
    name = re.sub(r'^reel-', '', filename.replace('.mp4', ''))
    name = re.sub(r'-\d{8}$', '', name)
    name = re.sub(r'-with-music(-v\d+)?$', '', name)
    return name.split('-')

def match_article(filename, articles):
    fragments = set(f.lower() for f in extract_slug_fragments(filename))
    best, best_score = None, 0
    for a in articles:
        slug_words = set((a.get('slug') or '').lower().split('-'))
        overlap = len(fragments & slug_words)
        score = overlap / max(len(fragments), 1)
        if score > best_score and score > 0.4:
            best, best_score = a, score
    return best

# --- Load credentials ---
def load_env(path):
    env = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip()
    return env

yt_env = load_env('~/workspace/.env.youtube')
sb_env = load_env('~/workspace/.env.supabase')

YOUTUBE_CLIENT_ID = yt_env.get('YOUTUBE_CLIENT_ID')
YOUTUBE_CLIENT_SECRET = yt_env.get('YOUTUBE_CLIENT_SECRET')
YOUTUBE_REFRESH_TOKEN = yt_env.get('YOUTUBE_REFRESH_TOKEN')
SUPABASE_URL = sb_env.get('SUPABASE_URL', 'https://lboecaekpynbpyijrbfz.supabase.co')
SB_KEY = sb_env.get('SUPABASE_SERVICE_ROLE_KEY', sb_env.get('SUPABASE_KEY', ''))

REELS_DIR = os.path.expanduser('~/workspace/the-videshi-news/pipeline/reels')
LOG_PATH = os.path.expanduser('~/workspace/the-videshi-news/pipeline/youtube-log.json')

DRY_RUN = '--dry-run' in sys.argv

def curl_json(args, input_data=None):
    """Run curl, return (status_code, parsed_json_or_text)."""
    result = subprocess.run(
        ['curl', '-sS', '-w', '\n%{http_code}', *args],
        input=input_data, capture_output=True, text=True, timeout=120,
    )
    out = result.stdout.strip().rsplit('\n', 1)
    body, code = (out[0], int(out[1])) if len(out) == 2 else ('', 0)
    try:
        return code, json.loads(body)
    except Exception:
        return code, body

def get_access_token():
    code, data = curl_json([
        '-X', 'POST', 'https://oauth2.googleapis.com/token',
        '-d', f'client_id={YOUTUBE_CLIENT_ID}',
        '-d', f'client_secret={YOUTUBE_CLIENT_SECRET}',
        '-d', f'refresh_token={YOUTUBE_REFRESH_TOKEN}',
        '-d', 'grant_type=refresh_token',
    ])
    if code != 200 or not isinstance(data, dict) or 'access_token' not in data:
        raise RuntimeError(f"Token refresh failed: HTTP {code} {str(data)[:200]}")
    return data['access_token']

def sb_get(path):
    code, data = curl_json([
        f'{SUPABASE_URL}/rest/v1/{path}',
        '-H', f'apikey: {SB_KEY}',
        '-H', f'Authorization: Bearer {SB_KEY}',
    ])
    if code != 200:
        raise RuntimeError(f"Supabase GET failed: HTTP {code}")
    return data if isinstance(data, list) else []

# --- Load tracking log ---
yt_log = json.load(open(LOG_PATH)) if os.path.exists(LOG_PATH) else {}

# --- Find unuploaded reels ---
all_reels = glob.glob(os.path.join(REELS_DIR, '*.mp4'))
all_reels.sort(key=lambda x: os.path.getmtime(x), reverse=True)

skip_patterns = ['test-social-embed', 'reel-v2-fixed', 'reel-v2-final']
unuploaded = []
for r in all_reels:
    fname = os.path.basename(r)
    if fname in yt_log:
        continue
    if any(p in fname for p in skip_patterns):
        print(f"Skipping test/misc reel: {fname}")
        yt_log[fname] = {"video_id": "skipped", "article_slug": "skipped",
                         "uploaded_at": datetime.now(timezone.utc).isoformat(), "url": "skipped"}
        continue
    unuploaded.append(r)

v2_bases = {os.path.basename(r).replace('-v2', '') for r in unuploaded if '-v2' in os.path.basename(r)}
final_unuploaded = []
for r in unuploaded:
    fname = os.path.basename(r)
    if fname in v2_bases:
        print(f"Skipping v1 (v2 exists): {fname}")
        yt_log[fname] = {"video_id": "skipped-v1-superseded", "article_slug": "skipped",
                         "uploaded_at": datetime.now(timezone.utc).isoformat(), "url": "skipped"}
        continue
    final_unuploaded.append(r)

if not final_unuploaded:
    print("No new reels to upload.")
    with open(LOG_PATH, 'w') as f:
        json.dump(yt_log, f, indent=2)
    sys.exit(0)

print(f"\nFound {len(final_unuploaded)} unuploaded reel(s).\n")

# --- Fetch recent articles (full fields for importance scoring) ---
print("Fetching recent articles from Supabase...")
try:
    articles = sb_get("p2_articles?status=eq.published&order=published_at.desc&limit=100"
                      "&select=id,slug,headline,subheadline,body,category,image_url,is_editorial,is_featured,published_at")
    print(f"  Got {len(articles)} recent articles")
except Exception as e:
    print(f"  Failed to fetch articles: {e}")
    articles = []

# --- Score, filter, and rank reels by story importance ---
print("Scoring reels by story importance...")
candidates = []
for reel_path in final_unuploaded:
    fname = os.path.basename(reel_path)

    # Skip voiceover variants — data shows 95% fewer views (3.9 avg vs 80.4)
    if 'voiceover' in fname.lower():
        print(f"  SKIP (voiceover variant): {fname}")
        yt_log[fname] = {"video_id": "skipped-voiceover", "article_slug": "skipped",
                         "uploaded_at": datetime.now(timezone.utc).isoformat(), "url": "skipped"}
        continue

    # Duration check — target 25-40s kinetic format, hard skip >42s
    dur = get_duration_seconds(reel_path)
    if dur is not None and dur > MAX_DURATION:
        print(f"  SKIP ({dur:.0f}s > {MAX_DURATION}s): {fname}")
        yt_log[fname] = {"video_id": "skipped-too-long", "article_slug": "skipped",
                         "uploaded_at": datetime.now(timezone.utc).isoformat(), "url": "skipped"}
        continue

    article = match_article(fname, articles)
    if article:
        score = score_for_shorts(article)
        headline = article.get('headline', '')
    else:
        score = 0
        headline = ''
    # Prefer videos in the 25-40s research window with a small tiebreak bonus
    if dur is not None and PREFERRED_MIN <= dur <= PREFERRED_MAX:
        score += 1
    candidates.append((score, reel_path, article, fname, dur))
    print(f"  score={score:3d} dur={dur:.0f}s  {fname[:60]}")

with open(LOG_PATH, 'w') as f:
    json.dump(yt_log, f, indent=2)

# Rank by score (desc), take top 2 — most important stories only
candidates.sort(key=lambda x: x[0], reverse=True)
to_upload = candidates[:2]

if not to_upload:
    print("No reels passed importance/duration filters.")
    sys.exit(0)

# Minimum bar: don't upload low-importance stories even if reels exist
MIN_SCORE = 3
to_upload = [c for c in to_upload if c[0] >= MIN_SCORE]
if not to_upload:
    print(f"No reels met minimum importance bar (score >= {MIN_SCORE}).")
    sys.exit(0)

print(f"\nUploading top {len(to_upload)} by importance:\n")

def generate_hashtags(category, headline):
    """Max 3 hashtags for the description: #Shorts + 2 topic tags.
    Research: hashtags in the title look spammy and reduce CTR; 3 max in
    the description is the evidenced limit."""
    base = ['#Shorts']
    cat_tags = {
        'news': ['#IndiaNews', '#BreakingNews'],
        'immigration': ['#H1B', '#GreenCard'],
        'nri-world': ['#NRILife', '#IndianAmerican'],
        'travel': ['#TravelIndia', '#IncredibleIndia'],
        'lifestyle-health': ['#DesiLifestyle', '#Wellness'],
        'markets-finance': ['#StockMarket', '#Nifty'],
        'technology': ['#TechNews', '#AI'],
        'sports': ['#Cricket', '#IPL'],
        'entertainment': ['#Bollywood', '#IndianCinema'],
        'food': ['#IndianFood', '#DesiFood'],
    }
    tags = base + cat_tags.get((category or '').lower(), ['#IndiaNews'])
    return ' '.join(tags[:3])

def rewrite_shorts_title(headline):
    """LLM rewrite: keyword-first, <=60 chars, curiosity/emotion.
    Falls back to plain truncation on any failure — upload never blocks."""
    fallback = (headline[:57] + '...') if len(headline) > 60 else headline
    api_key = getattr(_newsletter, 'OPENAI_API_KEY', '')
    if not api_key:
        return fallback
    prompt = (
        "Rewrite this news headline as a YouTube Shorts title.\n"
        "Rules: subject/keyword FIRST, max 60 characters, spark curiosity or "
        "emotion, no hashtags, no emojis, never invent facts, stay faithful.\n"
        f"Headline: {headline}\n"
        'Return JSON only: {"title": "..."}'
    )
    try:
        code, data = curl_json([
            '-X', 'POST', 'https://api.openai.com/v1/chat/completions',
            '-H', f'Authorization: Bearer {api_key}',
            '-H', 'Content-Type: application/json',
            '-d', json.dumps({
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 60,
                "temperature": 0.7,
                "response_format": {"type": "json_object"},
            }),
        ])
        if code == 200 and isinstance(data, dict):
            t = json.loads(data["choices"][0]["message"]["content"]).get("title", "")
            t = t.strip().strip('"')
            if t and len(t) <= 70:
                return t[:60]
    except Exception as e:
        print(f"  Title rewrite failed ({e}) — using fallback")
    return fallback

def generate_tags(category, headline):
    tags = ["The Videshi", "Indian Diaspora", "NRI", "India News", "Shorts"]
    if category:
        tags.append(category.replace('-', ' ').title())
    for w in re.findall(r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*', headline or '')[:4]:
        if w not in tags:
            tags.append(w)
    return tags[:12]

def youtube_upload(access_token, video_path, body):
    """Resumable upload via curl. Returns video_id."""
    file_size = os.path.getsize(video_path)
    # Session init — part=snippet,status is REQUIRED (400 unexpectedPart without it)
    init = subprocess.run([
        'curl', '-sS', '-D', '/tmp/yt-init-headers.txt', '-o', '/tmp/yt-init-body.json',
        '-w', '%{http_code}',
        '-X', 'POST',
        'https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status',
        '-H', f'Authorization: Bearer {access_token}',
        '-H', 'Content-Type: application/json; charset=UTF-8',
        '-H', 'X-Upload-Content-Type: video/mp4',
        '-H', f'X-Upload-Content-Length: {file_size}',
        '-d', json.dumps(body),
    ], capture_output=True, text=True, timeout=60)
    init_code = init.stdout.strip()
    upload_url = None
    try:
        for line in open('/tmp/yt-init-headers.txt').read().split('\n'):
            if line.lower().startswith('location:'):
                upload_url = line.split(':', 1)[1].strip()
                break
    except FileNotFoundError:
        pass
    if init_code != '200' or not upload_url:
        try:
            err_body = open('/tmp/yt-init-body.json').read()[:300]
        except Exception:
            err_body = '(no body)'
        raise RuntimeError(f"Upload init failed: HTTP {init_code} {err_body}")

    # Upload bytes
    up = subprocess.run([
        'curl', '-sS', '-w', '\n%{http_code}',
        '-X', 'PUT', upload_url,
        '-H', 'Content-Type: video/mp4',
        '--data-binary', f'@{video_path}',
    ], capture_output=True, text=True, timeout=600)
    out = up.stdout.strip().rsplit('\n', 1)
    up_body, up_code = (out[0], int(out[1])) if len(out) == 2 else ('', 0)
    if up_code not in (200, 201):
        raise RuntimeError(f"Upload failed: HTTP {up_code} {up_body[:300]}")
    return json.loads(up_body)['id']

# --- Main ---
if not all([YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN]):
    print("ERROR: missing YouTube OAuth credentials in ~/.env.youtube")
    sys.exit(1)

print("Refreshing YouTube OAuth token...")
access_token = get_access_token()
print("  Token OK")

uploaded, errors = 0, []
for score, reel_path, article, fname, dur in to_upload:
    print(f"\n{'='*60}\nProcessing (score={score}): {fname}")
    if article:
        headline = article.get('headline', '')
        subheadline = article.get('subheadline', '') or ''
        slug = article.get('slug', '')
        category = article.get('category', '')
        print(f"  Matched article: {headline[:80]}")
    else:
        headline = ' '.join(f.capitalize() for f in extract_slug_fragments(fname))
        subheadline, slug, category = '', 'unknown', 'news'
        print(f"  No article match, using filename: {headline[:80]}")

    title = rewrite_shorts_title(headline)
    hashtags = generate_hashtags(category, headline)
    article_url = f"https://www.thevideshi.com/articles/{slug}" if slug != 'unknown' else "https://www.thevideshi.com"
    description = (f"{subheadline}\n\nFull story: {article_url}\n\n"
                   f"The Videshi — News for the global Indian diaspora\n"
                   f"thevideshi.com\n\n{hashtags}")

    body = {
        "snippet": {"title": title, "description": description,
                    "tags": generate_tags(category, headline), "categoryId": "25"},
        "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False},
    }
    print(f"  Title: {title}")

    if DRY_RUN:
        print(f"  [DRY RUN] would upload {fname} ({os.path.getsize(reel_path)} bytes)")
        uploaded += 1
        continue

    try:
        video_id = youtube_upload(access_token, reel_path, body)
        yt_url = f"https://youtube.com/shorts/{video_id}"
        print(f"  Uploaded: {yt_url}")
        yt_log[fname] = {"video_id": video_id, "article_slug": slug or "unknown",
                         "uploaded_at": datetime.now(timezone.utc).isoformat(), "url": yt_url}
        with open(LOG_PATH, 'w') as f:
            json.dump(yt_log, f, indent=2)
        uploaded += 1
        if uploaded < 2 and len(to_upload) > 1:
            print("  Waiting 10s...")
            time.sleep(10)
    except Exception as e:
        msg = f"Failed to upload {fname}: {e}"
        print(f"  {msg}")
        errors.append(msg)

print(f"\n{'='*60}\nSUMMARY: uploaded={uploaded} errors={len(errors)}")
for e in errors:
    print(f"  {e}")
with open(LOG_PATH, 'w') as f:
    json.dump(yt_log, f, indent=2)
