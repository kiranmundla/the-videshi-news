#!/usr/bin/env python3
"""
Reel Orchestrator for The Videshi
=================================
Central reel generation pipeline that mixes methods:
  1. Image-based reels (existing generate-reel.py)
  2. HeyGen avatar reels (Kavya + future avatars from reel_avatars DB)

Picks articles, decides method, generates, assembles (hook + content + end card + music + captions),
uploads to Supabase, and inserts into prebuilt_reels for ig-autopost/yt-upload to pick up.

Usage:
  python3 reel-orchestrator.py                # Auto-pick article + method
  python3 reel-orchestrator.py --method avatar # Force avatar reel
  python3 reel-orchestrator.py --method image  # Force image reel
  python3 reel-orchestrator.py --article-id UUID  # Specific article
  python3 reel-orchestrator.py --dry-run       # Preview without generating
"""

import os, sys, json, time, random, re, argparse, subprocess, tempfile, hashlib
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

# ─── Config ──────────────────────────────────────────────────────────────────

PIPELINE_DIR = Path(__file__).parent
BUILD_DIR = PIPELINE_DIR / "reels" / "build"
REELS_DIR = PIPELINE_DIR / "reels"
MUSIC_DIR = PIPELINE_DIR / "music"
BUILD_DIR.mkdir(parents=True, exist_ok=True)

# Method split: probability of avatar vs image reel
AVATAR_PROBABILITY = 0.4  # 40% avatar, 60% image

# Categories that strongly prefer avatar reels
AVATAR_PREFERRED_CATEGORIES = {
    "news", "technology", "nri-world", "markets-finance"
}

# Music profiles per mood
MUSIC_PROFILES = {
    "breaking": {
        "hook": ("breaking-news-breaking-news-30s.mp3", 0.7),
        "underscore": ("dramatic-dark-suspense-thriller-30s.mp3", 0.08),
        "outro": ("breaking-news-breaking-news-30s.mp3", 0.5),
    },
    "tech": {
        "hook": ("breaking-news-breaking-news-30s.mp3", 0.6),
        "underscore": ("dramatic-dark-suspense-thriller-30s.mp3", 0.06),
        "outro": ("breaking-news-breaking-news-30s.mp3", 0.4),
    },
    "lifestyle": {
        "hook": ("breaking-news-breaking-news-30s.mp3", 0.5),
        "underscore": ("dramatic-dark-suspense-thriller-30s.mp3", 0.05),
        "outro": ("breaking-news-breaking-news-30s.mp3", 0.4),
    },
}

# Category → music profile mapping
CATEGORY_MUSIC = {
    "news": "breaking",
    "nri-world": "breaking",
    "technology": "tech",
    "markets-finance": "tech",
    "sports": "breaking",
    "entertainment": "lifestyle",
    "lifestyle-health": "lifestyle",
    "food": "lifestyle",
    "travel": "lifestyle",
}


def load_env(path):
    env = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                raw = line
                if raw.startswith('export '):
                    raw = raw[7:]
                k, v = raw.split('=', 1)
                env[k] = v.strip('"').strip("'")
    return env


# Load all env files
SB = load_env("~/.env.supabase") if os.path.exists(os.path.expanduser("~/.env.supabase")) else load_env("~/workspace/.env.supabase")
HEYGEN = load_env("~/workspace/.env.heygen")
OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "")
if not OPENAI_KEY:
    for p in ["~/workspace/.env.openai", "~/.env.openai"]:
        ep = os.path.expanduser(p)
        if os.path.exists(ep):
            e = load_env(p)
            OPENAI_KEY = e.get("OPENAI_API_KEY", "")
            if OPENAI_KEY:
                break

SUPABASE_URL = SB['SUPABASE_URL']
SB_KEY = SB['SUPABASE_SERVICE_ROLE_KEY']
HEYGEN_KEY = HEYGEN['HEYGEN_API_KEY']

SB_HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
}


# ─── Article Selection ───────────────────────────────────────────────────────

def get_recent_articles(hours=24, limit=20):
    """Fetch recent published articles without prebuilt reels."""
    since = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=SB_HEADERS,
        params={
            "select": "id,headline,subheadline,slug,category,vertical,body,published_at",
            "status": "eq.published",
            "published_at": f"gte.{since}",
            "order": "published_at.desc",
            "limit": limit,
        }
    )
    if r.status_code != 200:
        print(f"❌ Failed to fetch articles: {r.status_code} {r.text[:200]}")
        return []
    return r.json()


def get_existing_reels():
    """Get article IDs that already have prebuilt reels."""
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/prebuilt_reels",
        headers=SB_HEADERS,
        params={"select": "article_id", "limit": 200}
    )
    if r.status_code != 200:
        return set()
    return {row['article_id'] for row in r.json() if row.get('article_id')}


def score_article(article):
    """Score article for reel-worthiness. Higher = better candidate."""
    score = 0
    cat = (article.get('category') or '').lower()
    headline = (article.get('headline') or '').lower()

    # Category boost
    if cat in ('news', 'nri-world'):
        score += 3
    elif cat in ('technology', 'markets-finance'):
        score += 2
    elif cat in ('sports', 'entertainment'):
        score += 1

    # Keyword boost
    hot_keywords = ['h-1b', 'visa', 'green card', 'modi', 'trump', 'breaking',
                    'killed', 'crash', 'scandal', 'ban', 'deport', 'ipl',
                    'billion', 'layoff', 'shutdown', 'election']
    for kw in hot_keywords:
        if kw in headline:
            score += 2
            break

    # Headline length (shorter = punchier = better for reels)
    if len(headline) < 60:
        score += 1

    return score


def pick_article(articles, existing_reel_ids):
    """Pick the best article that doesn't have a reel yet."""
    candidates = [a for a in articles if a['id'] not in existing_reel_ids]
    if not candidates:
        return None

    # Score and sort
    scored = [(score_article(a), random.random(), a) for a in candidates]
    scored.sort(key=lambda x: (-x[0], x[1]))

    return scored[0][2]


# ─── Method Selection ────────────────────────────────────────────────────────

def pick_method(article, force_method=None):
    """Decide: 'avatar' or 'image' reel."""
    if force_method:
        return force_method

    cat = (article.get('category') or '').lower()

    # Category-based bias
    if cat in AVATAR_PREFERRED_CATEGORIES:
        prob = min(AVATAR_PROBABILITY + 0.2, 0.7)  # Boost for serious categories
    else:
        prob = max(AVATAR_PROBABILITY - 0.1, 0.2)  # Lower for lifestyle

    return 'avatar' if random.random() < prob else 'image'


# ─── Avatar Selection ────────────────────────────────────────────────────────

def pick_avatar(article_category):
    """Pick an avatar look from reel_avatars DB, weighted by category match and recency."""
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/reel_avatars",
        headers=SB_HEADERS,
        params={
            "select": "*",
            "active": "eq.true",
            "order": "last_used_at.asc.nullsfirst",
        }
    )
    if r.status_code != 200 or not r.json():
        print(f"⚠️ No active avatars found, falling back to image reel")
        return None

    avatars = r.json()
    cat = (article_category or '').lower()

    # Score each avatar
    weighted = []
    for av in avatars:
        w = av.get('weight', 1.0)
        cats = av.get('categories', [])

        # Category match bonus
        if cat in cats:
            w *= 2.0
        elif not cats:  # Universal avatar
            w *= 1.0
        else:
            w *= 0.3  # Mismatch penalty

        # Recency penalty (recently used = lower weight)
        if av.get('last_used_at'):
            hours_ago = (datetime.now(timezone.utc) - datetime.fromisoformat(av['last_used_at'].replace('Z', '+00:00'))).total_seconds() / 3600
            if hours_ago < 8:
                w *= 0.2  # Strong penalty for used in last 8h
            elif hours_ago < 24:
                w *= 0.6

        weighted.append((w, av))

    # Weighted random selection
    total = sum(w for w, _ in weighted)
    if total == 0:
        return weighted[0][1]

    r_val = random.random() * total
    cumulative = 0
    for w, av in weighted:
        cumulative += w
        if r_val <= cumulative:
            return av

    return weighted[-1][1]


# ─── Script Generation ───────────────────────────────────────────────────────

def generate_anchor_script(article):
    """GPT generates a 20-30s anchor script from the article."""
    headline = article.get('headline', '')
    body = (article.get('body') or '')[:3000]
    category = article.get('category', '')

    prompt = f"""You are a scriptwriter for The Videshi, an Indian diaspora news platform.
Write a 20-30 second news anchor script (spoken aloud) for this article.

Rules:
- Open with the most compelling fact or hook — NO greetings, NO "breaking news"
- Speak directly to Indian diaspora viewers in the US/UK/Canada
- End with "Full story at thevideshi.com"
- Keep it between 60-90 words (sweet spot for 20-30 seconds)
- Use natural conversational tone, not stiff broadcast style
- Include one specific number, name, or detail to ground it
- NO emoji, NO hashtags — this is spoken word

Article headline: {headline}
Category: {category}
Article body:
{body}

Return ONLY the script text, nothing else."""

    r = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"},
        json={
            "model": "gpt-4o",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 300,
        },
        timeout=30
    )
    if r.status_code != 200:
        print(f"❌ GPT script generation failed: {r.status_code}")
        return None

    return r.json()['choices'][0]['message']['content'].strip().strip('"')


# ─── Hook Frame Generation ──────────────────────────────────────────────────

def generate_hook_text(article):
    """GPT generates punchy hook text for the opening frame."""
    headline = article.get('headline', '')

    prompt = f"""Write a 2-line hook for an Instagram Reel opening frame.
Line 1: punchy, provocative, max 6 words. ALL CAPS.
Line 2: brief context, max 8 words. Title case.

Article: {headline}

Return exactly 2 lines, nothing else."""

    r = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"},
        json={
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.8,
            "max_tokens": 60,
        },
        timeout=15
    )
    if r.status_code != 200:
        return headline.upper()[:40], ""

    text = r.json()['choices'][0]['message']['content'].strip()
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    line1 = lines[0] if lines else headline.upper()[:40]
    line2 = lines[1] if len(lines) > 1 else ""
    return line1, line2


def create_hook_frame(line1, line2, output_path):
    """Create 1080x1920 hook frame PNG using ffmpeg."""
    # Escape text for ffmpeg drawtext
    l1 = line1.replace("'", "'\\''").replace(":", "\\:")
    l2 = line2.replace("'", "'\\''").replace(":", "\\:")

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"color=c=#1a1a2e:s=1080x1920:d=1",
        "-vf",
        f"drawtext=text='{l1}':fontsize=64:fontcolor=#d4af37:x=(w-text_w)/2:y=(h-text_h)/2-60:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf,"
        f"drawtext=text='{l2}':fontsize=36:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2+40:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf,"
        f"drawtext=text='THE VIDESHI':fontsize=28:fontcolor=#d4af37:x=(w-text_w)/2:y=h-120:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "-frames:v", "1",
        str(output_path)
    ]
    subprocess.run(cmd, capture_output=True, timeout=15)
    return output_path.exists()


def create_hook_video(hook_png, output_path, duration=3, fps=25):
    """Convert hook PNG to video segment."""
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", str(hook_png),
        "-f", "lavfi", "-i", f"anullsrc=r=48000:cl=stereo",
        "-t", str(duration),
        "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p",
        "-r", str(fps), "-s", "1080x1920",
        "-c:a", "aac", "-b:a", "128k",
        "-shortest",
        str(output_path)
    ]
    subprocess.run(cmd, capture_output=True, timeout=30)
    return output_path.exists()


# ─── HeyGen Video Generation ────────────────────────────────────────────────

def generate_heygen_video(script, avatar):
    """Submit HeyGen v2 video generation and return video_id."""
    payload = {
        "video_inputs": [{
            "character": {
                "type": "avatar",
                "avatar_id": avatar['avatar_id'],
                "avatar_style": "normal"
            },
            "voice": {
                "type": "text",
                "input_text": script,
                "voice_id": avatar['voice_id'],
                "speed": 1.0
            }
        }],
        "dimension": {"width": 1080, "height": 1920},
        "aspect_ratio": avatar.get('aspect_ratio', '9:16'),
        "test": False
    }

    r = requests.post(
        "https://api.heygen.com/v2/video/generate",
        headers={"X-Api-Key": HEYGEN_KEY, "Content-Type": "application/json"},
        json=payload,
        timeout=30
    )

    if r.status_code not in (200, 201):
        print(f"❌ HeyGen submit failed: {r.status_code} {r.text[:200]}")
        return None

    data = r.json().get('data', {})
    video_id = data.get('video_id')
    print(f"  HeyGen video submitted: {video_id}")
    return video_id


def poll_heygen_video(video_id, max_wait=600):
    """Poll HeyGen until video is ready. Returns download URL or None."""
    print(f"  Polling HeyGen for {video_id}...")
    start = time.time()
    while time.time() - start < max_wait:
        r = requests.get(
            f"https://api.heygen.com/v1/video_status.get?video_id={video_id}",
            headers={"X-Api-Key": HEYGEN_KEY},
            timeout=15
        )
        if r.status_code == 200:
            data = r.json().get('data', {})
            status = data.get('status', '')
            if status == 'completed':
                url = data.get('video_url', '')
                print(f"  ✅ HeyGen ready: {url[:80]}...")
                return url
            elif status == 'failed':
                print(f"  ❌ HeyGen failed: {data.get('error', 'unknown')}")
                return None
            else:
                elapsed = int(time.time() - start)
                print(f"  ⏳ {status} ({elapsed}s)")
        time.sleep(15)

    print(f"  ❌ HeyGen timed out after {max_wait}s")
    return None


def download_heygen_video(url, output_path):
    """Download HeyGen video to local path."""
    r = requests.get(url, stream=True, timeout=120)
    with open(output_path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    return output_path.exists()


# ─── Captions (Whisper + ffmpeg) ─────────────────────────────────────────────

def generate_captions_srt(video_path, script_text):
    """Use Whisper API for word-level timestamps → SRT file."""
    srt_path = video_path.with_suffix('.srt')

    # Use OpenAI Whisper API
    try:
        r = requests.post(
            "https://api.openai.com/v1/audio/transcriptions",
            headers={"Authorization": f"Bearer {OPENAI_KEY}"},
            files={"file": ("audio.mp4", open(video_path, "rb"), "video/mp4")},
            data={
                "model": "whisper-1",
                "response_format": "srt",
                "language": "en"
            },
            timeout=60
        )
        if r.status_code == 200:
            with open(srt_path, 'w') as f:
                f.write(r.text)
            print(f"  ✅ Captions generated: {srt_path}")
            return srt_path
        else:
            print(f"  ⚠️ Whisper failed ({r.status_code}), skipping captions")
            return None
    except Exception as e:
        print(f"  ⚠️ Whisper error: {e}, skipping captions")
        return None


def burn_captions(video_path, srt_path, output_path):
    """Burn SRT captions into video with branded styling."""
    # Gold text on semi-transparent navy bar
    style = (
        "FontName=DejaVu Sans,FontSize=20,PrimaryColour=&H0037AFD4,"
        "OutlineColour=&H802E1A1A,BackColour=&H802E1A1A,"
        "Bold=1,Outline=1,Shadow=0,MarginV=80,Alignment=2"
    )

    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-vf", f"subtitles={srt_path}:force_style='{style}'",
        "-c:v", "libx264", "-crf", "22", "-preset", "fast",
        "-c:a", "copy",
        str(output_path)
    ]
    result = subprocess.run(cmd, capture_output=True, timeout=120, text=True)
    if result.returncode != 0:
        print(f"  ⚠️ Caption burn failed: {result.stderr[-200:]}")
        return False
    return output_path.exists()


# ─── Assembly ────────────────────────────────────────────────────────────────

def get_video_duration(path):
    """Get video duration in seconds."""
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", str(path)],
        capture_output=True, text=True, timeout=15
    )
    data = json.loads(result.stdout)
    return float(data['format']['duration'])


def normalize_segment(input_path, output_path, fps=25, size="1080x1920"):
    """Normalize video segment to consistent format."""
    cmd = [
        "ffmpeg", "-y", "-i", str(input_path),
        "-c:v", "libx264", "-r", str(fps), "-s", size, "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-ar", "48000", "-ac", "2",
        "-preset", "fast",
        str(output_path)
    ]
    subprocess.run(cmd, capture_output=True, timeout=300)
    return output_path.exists()


def concat_segments(segments, output_path):
    """Concatenate video segments via concat demuxer."""
    # Convert to .ts for seamless concat
    ts_files = []
    for i, seg in enumerate(segments):
        ts_path = BUILD_DIR / f"seg_{i}.ts"
        cmd = [
            "ffmpeg", "-y", "-i", str(seg),
            "-c:v", "copy", "-c:a", "copy",
            "-bsf:v", "h264_mp4toannexb",
            "-f", "mpegts",
            str(ts_path)
        ]
        subprocess.run(cmd, capture_output=True, timeout=30)
        ts_files.append(ts_path)

    # Concat
    concat_str = "|".join(str(f) for f in ts_files)
    cmd = [
        "ffmpeg", "-y",
        "-i", f"concat:{concat_str}",
        "-c", "copy",
        "-movflags", "+faststart",
        str(output_path)
    ]
    subprocess.run(cmd, capture_output=True, timeout=120)

    # Cleanup
    for f in ts_files:
        f.unlink(missing_ok=True)

    return output_path.exists()


def add_music(video_path, output_path, category, kavya_duration=None):
    """Add music layers: hook sting + underscore + outro sting."""
    profile_name = CATEGORY_MUSIC.get(category, "breaking")
    profile = MUSIC_PROFILES[profile_name]

    hook_file, hook_vol = profile["hook"]
    under_file, under_vol = profile["underscore"]
    outro_file, outro_vol = profile["outro"]

    hook_path = MUSIC_DIR / hook_file
    under_path = MUSIC_DIR / under_file
    outro_path = MUSIC_DIR / outro_file

    total_dur = get_video_duration(video_path)
    hook_dur = 3.0
    end_dur = 3.0
    kavya_dur = kavya_duration or (total_dur - hook_dur - end_dur)
    outro_start_ms = int((total_dur - end_dur) * 1000)

    filter_complex = (
        f"[0:a]volume=1.0[voice];"
        f"[1:a]atrim=0:{hook_dur},asetpts=PTS-STARTPTS,volume={hook_vol},afade=t=out:st={hook_dur-0.5}:d=0.5[hook_sting];"
        f"[2:a]atrim=0:{kavya_dur},asetpts=PTS-STARTPTS,volume={under_vol},afade=t=in:st=0:d=1,afade=t=out:st={kavya_dur-1.2}:d=1.2[underscore];"
        f"[3:a]atrim=25:28,asetpts=PTS-STARTPTS,volume={outro_vol},afade=t=in:st=0:d=0.3,afade=t=out:st=2.5:d=0.5[outro_sting];"
        f"[hook_sting]adelay=0|0[hook_delayed];"
        f"[underscore]adelay={int(hook_dur*1000)}|{int(hook_dur*1000)}[under_delayed];"
        f"[outro_sting]adelay={outro_start_ms}|{outro_start_ms}[outro_delayed];"
        f"[voice][hook_delayed][under_delayed][outro_delayed]amix=inputs=4:duration=first:dropout_transition=0:weights=1 1 1 1,volume=4.0[audio_out]"
    )

    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-i", str(hook_path),
        "-i", str(under_path),
        "-i", str(outro_path),
        "-filter_complex", filter_complex,
        "-map", "0:v", "-map", "[audio_out]",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        str(output_path)
    ]
    result = subprocess.run(cmd, capture_output=True, timeout=60, text=True)
    if result.returncode != 0:
        print(f"  ⚠️ Music mix failed: {result.stderr[-200:]}")
        return False
    return output_path.exists()


# ─── Upload & Register ───────────────────────────────────────────────────────

def upload_to_supabase(local_path, storage_name):
    """Upload video to Supabase storage, return public URL."""
    with open(local_path, 'rb') as f:
        r = requests.post(
            f"{SUPABASE_URL}/storage/v1/object/article-images/{storage_name}",
            headers={
                "apikey": SB_KEY,
                "Authorization": f"Bearer {SB_KEY}",
                "Content-Type": "video/mp4",
                "x-upsert": "true"
            },
            data=f.read(),
            timeout=120
        )
    if r.status_code in (200, 201):
        url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{storage_name}"
        print(f"  ✅ Uploaded: {url}")
        return url
    else:
        print(f"  ❌ Upload failed: {r.status_code} {r.text[:200]}")
        return None


def register_prebuilt_reel(article_id, video_url, caption, method, avatar_name=None):
    """Insert into prebuilt_reels for posting pipeline."""
    payload = {
        "article_id": article_id,
        "video_url": video_url,
        "caption": caption,
        "status": "pending",
        "method": method,
    }
    if avatar_name:
        payload["avatar_name"] = avatar_name

    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/prebuilt_reels",
        headers={**SB_HEADERS, "Prefer": "return=representation"},
        json=payload
    )
    if r.status_code in (200, 201):
        print(f"  ✅ Registered prebuilt reel")
        return True
    else:
        print(f"  ⚠️ Register failed: {r.status_code} {r.text[:200]}")
        return False


def update_avatar_last_used(avatar_id_db):
    """Update last_used_at for the selected avatar."""
    requests.patch(
        f"{SUPABASE_URL}/rest/v1/reel_avatars?id=eq.{avatar_id_db}",
        headers={**SB_HEADERS, "Prefer": "return=minimal"},
        json={"last_used_at": datetime.now(timezone.utc).isoformat()},
    )


def build_caption(article):
    """Build Instagram caption from article."""
    headline = article.get('headline', '')
    subheadline = article.get('subheadline', '')
    category = (article.get('category') or '').lower()
    slug = article.get('slug', '')

    caption = f"""{headline}

{subheadline}

Full story at thevideshi.com (link in bio)

"""
    # Category tags
    cat_tags = {
        "news": "#india #news #breaking #nri #indiandiaspora",
        "technology": "#tech #ai #siliconvalley #indiantech #nri",
        "nri-world": "#nri #indiandiaspora #immigration #expat",
        "markets-finance": "#markets #stocks #nifty #sensex #investing",
        "sports": "#cricket #ipl #sports #india #teamindia",
        "entertainment": "#bollywood #entertainment #celebrity #india",
        "lifestyle-health": "#health #lifestyle #wellness #india",
        "food": "#indianfood #food #recipe #desi #cooking",
        "travel": "#travel #india #wanderlust #diaspora",
    }
    tags = cat_tags.get(category, "#india #nri #thevideshi")
    caption += f"{tags} #thevideshi"

    return caption.strip()


# ─── End Card ────────────────────────────────────────────────────────────────

def get_or_create_end_card():
    """Get or create the standard Videshi end card."""
    end_card = BUILD_DIR / "end_card_25fps_silent.mp4"
    if end_card.exists():
        return end_card

    # Create one
    png = BUILD_DIR / "end_card.png"
    cmd_png = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "color=c=#1a1a2e:s=1080x1920:d=1",
        "-vf",
        "drawtext=text='THE VIDESHI':fontsize=56:fontcolor=#d4af37:x=(w-text_w)/2:y=(h/2)-60:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf,"
        "drawtext=text='thevideshi.com':fontsize=32:fontcolor=white:x=(w-text_w)/2:y=(h/2)+20:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf,"
        "drawtext=text='Follow for more':fontsize=24:fontcolor=#aaaaaa:x=(w-text_w)/2:y=(h/2)+80:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "-frames:v", "1", str(png)
    ]
    subprocess.run(cmd_png, capture_output=True, timeout=15)

    cmd_vid = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", str(png),
        "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
        "-t", "3", "-c:v", "libx264", "-tune", "stillimage",
        "-pix_fmt", "yuv420p", "-r", "25", "-s", "1080x1920",
        "-c:a", "aac", "-b:a", "128k", "-shortest",
        str(end_card)
    ]
    subprocess.run(cmd_vid, capture_output=True, timeout=30)
    return end_card


# ─── Main Orchestrator ───────────────────────────────────────────────────────

def run(args):
    print("=" * 60)
    print(f"🎬 Reel Orchestrator — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    # 1. Get articles
    if args.article_id:
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/p2_articles",
            headers=SB_HEADERS,
            params={"select": "*", "id": f"eq.{args.article_id}"}
        )
        articles = r.json() if r.status_code == 200 else []
        if not articles:
            print(f"❌ Article {args.article_id} not found")
            return
        article = articles[0]
    else:
        articles = get_recent_articles(hours=24)
        existing = get_existing_reels()
        print(f"📰 {len(articles)} recent articles, {len(existing)} already have reels")

        article = pick_article(articles, existing)
        if not article:
            print("ℹ️ No articles need reels right now")
            return

    headline = article.get('headline', '')[:80]
    category = article.get('category', '')
    slug = article.get('slug', '')
    print(f"\n📝 Selected: {headline}")
    print(f"   Category: {category} | Slug: {slug}")

    # 2. Pick method
    method = pick_method(article, force_method=args.method)
    print(f"\n🎯 Method: {method.upper()}")

    if args.dry_run:
        if method == 'avatar':
            avatar = pick_avatar(category)
            if avatar:
                print(f"   Avatar: {avatar['avatar_name']} — {avatar['look_name']}")
        print("\n🏁 Dry run complete")
        return

    # 3. Generate based on method
    if method == 'avatar':
        avatar = pick_avatar(category)
        if not avatar:
            print("⚠️ No avatar available, falling back to image reel")
            method = 'image'

    if method == 'avatar':
        print(f"\n🤖 Avatar: {avatar['avatar_name']} — {avatar['look_name']}")

        # 3a. Generate script
        print("  Generating anchor script...")
        script = generate_anchor_script(article)
        if not script:
            print("❌ Script generation failed")
            return
        print(f"  Script ({len(script.split())} words): {script[:100]}...")

        # 3b. Generate hook frame
        print("  Creating hook frame...")
        line1, line2 = generate_hook_text(article)
        hook_png = BUILD_DIR / "hook.png"
        hook_vid = BUILD_DIR / "hook_25fps.mp4"
        create_hook_frame(line1, line2, hook_png)
        create_hook_video(hook_png, hook_vid)

        # 3c. Submit to HeyGen
        print("  Submitting to HeyGen...")
        video_id = generate_heygen_video(script, avatar)
        if not video_id:
            print("❌ HeyGen submission failed")
            return

        # 3d. Poll for completion
        video_url = poll_heygen_video(video_id)
        if not video_url:
            return

        # 3e. Download
        raw_avatar = BUILD_DIR / f"avatar-raw-{video_id}.mp4"
        print("  Downloading HeyGen video...")
        download_heygen_video(video_url, raw_avatar)
        kavya_dur = get_video_duration(raw_avatar)
        print(f"  Duration: {kavya_dur:.1f}s")

        # 3f. Generate captions
        print("  Generating captions...")
        srt_path = generate_captions_srt(raw_avatar, script)

        # 3g. Burn captions if available
        if srt_path:
            captioned = BUILD_DIR / f"avatar-captioned-{video_id}.mp4"
            if burn_captions(raw_avatar, srt_path, captioned):
                avatar_video = captioned
            else:
                avatar_video = raw_avatar
        else:
            avatar_video = raw_avatar

        # 3h. Normalize avatar video
        normalized_avatar = BUILD_DIR / "avatar_normalized.mp4"
        normalize_segment(avatar_video, normalized_avatar)

        # 3i. Assemble: hook + avatar + end card
        end_card = get_or_create_end_card()
        assembled = REELS_DIR / f"reel-{slug[:60]}.mp4"
        print("  Assembling segments...")
        concat_segments([hook_vid, normalized_avatar, end_card], assembled)

        # 3j. Add music
        final = REELS_DIR / f"reel-{slug[:60]}-final.mp4"
        print("  Adding music...")
        add_music(assembled, final, category, kavya_duration=kavya_dur)

        # 3k. Update avatar last_used
        update_avatar_last_used(avatar['id'])
        avatar_name = avatar['avatar_name']

    elif method == 'image':
        # Delegate to existing generate-reel.py
        print("\n🖼️ Generating image-based reel...")
        result = subprocess.run(
            ["python3", str(PIPELINE_DIR / "generate-reel.py"), "--article-id", article['id']],
            capture_output=True, text=True, timeout=300,
            cwd=str(PIPELINE_DIR)
        )
        print(result.stdout[-500:] if result.stdout else "")
        if result.returncode != 0:
            print(f"❌ Image reel generation failed: {result.stderr[-200:]}")
            return

        # Find the output file
        pattern = f"reel-{slug[:40]}"
        candidates = sorted(REELS_DIR.glob(f"{pattern}*-final.mp4"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not candidates:
            candidates = sorted(REELS_DIR.glob(f"{pattern}*.mp4"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not candidates:
            print("❌ Could not find generated image reel")
            return
        final = candidates[0]
        avatar_name = None

    # 4. Upload to Supabase
    storage_name = f"reel-{slug[:60]}-{method}-{int(time.time())}.mp4"
    print(f"\n📤 Uploading to Supabase...")
    public_url = upload_to_supabase(final, storage_name)
    if not public_url:
        return

    # 5. Register in prebuilt_reels
    caption = build_caption(article)
    register_prebuilt_reel(article['id'], public_url, caption, method, avatar_name)

    # 6. Summary
    file_size = final.stat().st_size / (1024 * 1024)
    duration = get_video_duration(final)
    print(f"\n{'='*60}")
    print(f"✅ REEL COMPLETE")
    print(f"   Method: {method}")
    if avatar_name:
        print(f"   Avatar: {avatar_name} — {avatar.get('look_name', '')}")
    print(f"   Article: {headline}")
    print(f"   Duration: {duration:.1f}s | Size: {file_size:.1f}MB")
    print(f"   File: {final}")
    print(f"   URL: {public_url}")
    print(f"{'='*60}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reel Orchestrator for The Videshi")
    parser.add_argument("--method", choices=["avatar", "image"], help="Force reel method")
    parser.add_argument("--article-id", help="Specific article UUID")
    parser.add_argument("--dry-run", action="store_true", help="Preview without generating")
    args = parser.parse_args()
    run(args)
