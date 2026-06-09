#!/usr/bin/env python3
"""
Voice-Over Reel Builder for The Videshi

Generates reels using TTS voice-over (Kavya's voice) + B-roll images.
No HeyGen avatar — saves credits. Same quality captions, music, hook/end card.

Flow:
1. Pick article (reuse orchestrator scoring)
2. Generate segmented script (all BROLL, no ANCHOR segments)
3. TTS → audio (OpenAI tts-1-hd or ElevenLabs)
4. Source B-roll images from article + Pexels
5. Render B-roll frames with Ken Burns
6. Whisper → SRT captions
7. Assemble: B-roll video + voice audio + captions + hook + end card + music
8. Upload & register in prebuilt_reels
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

# ── Load env ──────────────────────────────────────────────────────────────────

def load_env(path):
    env = {}
    p = os.path.expanduser(path)
    if not os.path.exists(p):
        return env
    with open(p) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env

OAI = load_env("~/workspace/.env.openai")
SB = load_env("~/workspace/.env.supabase")
PEXELS = load_env("~/workspace/.env.pexels")
HG = load_env("~/workspace/.env.heygen")

OPENAI_KEY = OAI.get("OPENAI_API_KEY", "")
SB_URL = "https://lboecaekpynbpyijrbfz.supabase.co"
SB_KEY = SB.get("SUPABASE_SERVICE_ROLE_KEY", "") or SB.get("SUPABASE_ANON_KEY", "")
PEXELS_KEY = PEXELS.get("PEXELS_API_KEY", "")
HEYGEN_KEY = HG.get("HEYGEN_API_KEY", "")

PIPELINE_DIR = Path(__file__).parent
BUILD_DIR = PIPELINE_DIR / "reels" / "build"
REELS_DIR = PIPELINE_DIR / "reels"
BUILD_DIR.mkdir(parents=True, exist_ok=True)

# TTS config — HeyGen Starfish is default (best quality)
TTS_PROVIDER = "heygen"  # "heygen", "openai", or "elevenlabs"
TTS_VOICE = "d2f4f24783d04e22ab49ee8fdc3715e0"  # HeyGen: Chill Brian (Starfish); OpenAI: nova; ElevenLabs: cb9diBQeYWIGJS9i52kX
TTS_MODEL = "tts-1-hd"
TTS_SPEED = 1.0

# ── Article Selection (reuse from orchestrator) ──────────────────────────────

def get_recent_articles(hours=24, limit=20):
    r = requests.get(
        f"{SB_URL}/rest/v1/p2_articles",
        params={
            "status": "eq.published",
            "order": "published_at.desc",
            "limit": limit,
            "select": "id,slug,headline,subheadline,body,category,tags,image_url,published_at"
        },
        headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"},
        timeout=15
    )
    return r.json() if r.status_code == 200 else []


def get_existing_reel_slugs():
    r = requests.get(
        f"{SB_URL}/rest/v1/prebuilt_reels",
        params={"select": "article_slug", "limit": 200},
        headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"},
        timeout=10
    )
    if r.status_code == 200:
        return {row['article_slug'] for row in r.json() if row.get('article_slug')}
    return set()


def score_article(article):
    """Score articles for reel-worthiness."""
    score = 0
    cat = article.get('category', '')
    headline = article.get('headline', '')
    
    # Category weights
    cat_scores = {
        'news': 10, 'nri-world': 9, 'immigration': 9,
        'sports': 8, 'entertainment': 8, 'technology': 7,
        'markets-finance': 6, 'travel': 6, 'lifestyle-health': 5, 'food': 5
    }
    score += cat_scores.get(cat, 3)
    
    # Headline quality
    if len(headline) > 40:
        score += 2
    if any(w in headline.lower() for w in ['breaking', 'exclusive', 'just in', 'diaspora', 'nri']):
        score += 3
    if article.get('image_url'):
        score += 2
    
    return score


def pick_article(articles, existing_slugs):
    candidates = [a for a in articles if a.get('slug') not in existing_slugs]
    if not candidates:
        return None
    candidates.sort(key=lambda a: score_article(a), reverse=True)
    return candidates[0]


# ── Script Generation ────────────────────────────────────────────────────────

def generate_voiceover_script(article):
    """Generate a voice-over script optimized for viral Instagram Reels."""
    headline = article.get('headline', '')
    subheadline = article.get('subheadline', '')
    body = (article.get('body') or '')[:3000]
    category = article.get('category', '')
    
    prompt = f"""You write viral Instagram Reel scripts for The Videshi — news for the Indian diaspora.

This is a VOICE-OVER reel. No anchor on screen. Visuals are B-roll images that change every 5-7 seconds.

ARTICLE:
Headline: {headline}
Subheadline: {subheadline}
Category: {category}
Body: {body[:2500]}

SCRIPT RULES:
1. HOOK (first 3 seconds): Start with a jaw-dropping fact, a bold claim, or a "wait what?" moment. This decides if people keep watching. No pleasantries, no setup — hit them immediately.
2. TENSION: Build intrigue. Use contrast, stakes, or a narrative arc. "Here's why that matters for every NRI watching this."
3. PAYOFF: Land with a punch — a surprising twist, a forward-looking take, or a line that makes them want to share it.
4. TONE: Talk like a smart friend who just found out something wild and is telling you about it. Confident, punchy, slightly urgent. NOT a news robot. NOT a YouTuber begging for likes.
5. PACING: Short sentences. Vary rhythm. One-word sentences are fine. Let the voice breathe.
6. LENGTH: 60-80 words. That's 25-30 seconds spoken. Tight. Every word earns its place.
7. SPECIFICS: Include at least one concrete number, name, or detail. Vague = boring.
8. NO "Welcome to The Videshi", NO "Follow for more", NO emoji, NO hashtags — this is spoken word.
9. End with "Full story at thevideshi dot com" ONLY if it flows naturally. Otherwise skip it.

HOOK TEXT (shown on screen before voice starts):
- hook_line1: 3-5 words, ALL CAPS. The "stop scrolling" line. Bold, surprising, specific.
- hook_line2: 3-5 words, ALL CAPS. Adds context or intrigue.
- Bad examples: "BREAKING NEWS TODAY" (generic), "YOU WON'T BELIEVE THIS" (clickbait)
- Good examples: "₹304 CRORE. CANCELLED SHOWS." / "HE STILL BROKE RECORDS"

IMAGE QUERIES: 4-5 search terms for Pexels stock photos that would make strong B-roll behind the narration. Be specific and visual — "crowded Indian movie theater" not "cinema". Avoid searching for specific celebrities (stock sites won't have them).

Return JSON only:
{{
  "script": "the spoken narration",
  "image_queries": ["specific visual query 1", "query 2", "query 3", "query 4"],
  "hook_line1": "BOLD HOOK LINE",
  "hook_line2": "CONTEXT LINE"
}}"""

    r = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"},
        json={
            "model": "gpt-4o",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.8,
            "response_format": {"type": "json_object"}
        },
        timeout=30
    )
    
    if r.status_code != 200:
        print(f"❌ Script generation failed: {r.status_code}")
        return None
    
    result = json.loads(r.json()["choices"][0]["message"]["content"])
    print(f"  Script: {len(result['script'].split())} words")
    print(f"  Hook: {result.get('hook_line1', '')} / {result.get('hook_line2', '')}")
    print(f"  Script text: {result['script'][:150]}...")
    return result


# ── TTS Voice Generation ─────────────────────────────────────────────────────

def generate_tts(text, output_path):
    """Generate voice-over audio from text using configured TTS provider."""
    
    if TTS_PROVIDER == "openai":
        return _tts_openai(text, output_path)
    elif TTS_PROVIDER == "elevenlabs":
        return _tts_elevenlabs(text, output_path)
    else:
        print(f"❌ Unknown TTS provider: {TTS_PROVIDER}")
        return False


def _tts_openai(text, output_path):
    """Generate audio via OpenAI TTS."""
    r = requests.post(
        "https://api.openai.com/v1/audio/speech",
        headers={"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"},
        json={
            "model": TTS_MODEL,
            "input": text,
            "voice": TTS_VOICE,
            "speed": TTS_SPEED,
            "response_format": "mp3"
        },
        timeout=60
    )
    
    if r.status_code != 200:
        print(f"❌ OpenAI TTS failed: {r.status_code} {r.text[:200]}")
        return False
    
    with open(output_path, 'wb') as f:
        f.write(r.content)
    
    size_kb = os.path.getsize(output_path) / 1024
    print(f"  ✅ TTS audio: {output_path} ({size_kb:.0f} KB)")
    return True


def _tts_elevenlabs(text, output_path):
    """Generate audio via ElevenLabs (for exact Kavya voice match)."""
    el_env = load_env("~/workspace/.env.elevenlabs")
    el_key = el_env.get("ELEVENLABS_API_KEY", "")
    if not el_key:
        print("❌ ElevenLabs API key not found. Set up ~/workspace/.env.elevenlabs")
        return False
    
    voice_id = "cb9diBQeYWIGJS9i52kX"  # Indian Anchorwoman = Kavya
    r = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
        headers={"xi-api-key": el_key, "Content-Type": "application/json"},
        json={
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
        },
        timeout=60
    )
    
    if r.status_code != 200:
        print(f"❌ ElevenLabs TTS failed: {r.status_code} {r.text[:200]}")
        return False
    
    with open(output_path, 'wb') as f:
        f.write(r.content)
    
    print(f"  ✅ ElevenLabs TTS audio: {output_path}")
    return True


# ── Image Sourcing ───────────────────────────────────────────────────────────

def source_images(image_queries, article, count=5):
    """Source B-roll images from article + Pexels. Returns list of local paths."""
    images = []
    
    # 1. Article's own image first
    article_img = article.get('image_url', '')
    if article_img:
        img_path = BUILD_DIR / "vo-broll-0.jpg"
        if _download_image(article_img, img_path):
            images.append(str(img_path))
    
    # 2. Pexels for remaining
    for i, query in enumerate(image_queries[:count - len(images)]):
        img_path = BUILD_DIR / f"vo-broll-{len(images)}.jpg"
        if _fetch_pexels_image(query, img_path):
            images.append(str(img_path))
    
    print(f"  Sourced {len(images)} B-roll images")
    return images


def _download_image(url, output_path):
    try:
        r = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code == 200 and len(r.content) > 5000:
            with open(output_path, 'wb') as f:
                f.write(r.content)
            return True
    except Exception as e:
        print(f"  ⚠️ Image download failed: {e}")
    return False


def _fetch_pexels_image(query, output_path):
    """Fetch a landscape image from Pexels using requests (urllib gets 403, curl loses env)."""
    if not PEXELS_KEY:
        return False
    try:
        r = requests.get(
            "https://api.pexels.com/v1/search",
            params={"query": query, "per_page": 3, "orientation": "landscape"},
            headers={"Authorization": PEXELS_KEY},
            timeout=15
        )
        if r.status_code != 200:
            print(f"  ⚠️ Pexels API {r.status_code} for '{query}'")
            return False
        photos = r.json().get('photos', [])
        if photos:
            url = photos[0].get('src', {}).get('large2x') or photos[0].get('src', {}).get('large')
            if url:
                return _download_image(url, output_path)
    except Exception as e:
        print(f"  ⚠️ Pexels fetch failed for '{query}': {e}")
    return False


# ── B-Roll Video Assembly ────────────────────────────────────────────────────

def get_audio_duration(path):
    """Get duration of audio file in seconds."""
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True
    )
    return float(result.stdout.strip())


def render_broll_video(images, audio_path, output_path, headline, category):
    """
    Render 9:16 B-roll video synchronized to voice-over audio duration.
    Each image gets equal time. Ken Burns zoom (3%, no jitter).
    Bottom third: headline overlay + category badge.
    """
    audio_dur = get_audio_duration(audio_path)
    n_images = len(images)
    if n_images == 0:
        print("❌ No images for B-roll")
        return False
    
    per_image = audio_dur / n_images
    fps = 25
    
    # For each image: render a Ken Burns 9:16 video segment
    segments = []
    for i, img_path in enumerate(images):
        seg_path = BUILD_DIR / f"vo-seg-{i}.mp4"
        if not _render_ken_burns_segment(img_path, seg_path, per_image, fps, headline, category):
            print(f"  ⚠️ Failed to render segment {i}, skipping")
            continue
        segments.append(str(seg_path))
    
    if not segments:
        print("❌ No segments rendered")
        return False
    
    # Concatenate with crossfade
    _concat_with_crossfade(segments, audio_path, output_path, fps)
    return os.path.exists(output_path)


def _render_ken_burns_segment(image_path, output_path, duration, fps, headline, category):
    """Render a single image as a 9:16 Ken Burns video with branded overlay.
    Two-pass: 1) Ken Burns zoom → raw video, 2) overlay text with drawtext.
    Split to avoid shell escaping nightmares in one giant filter_complex.
    """
    frames = int(duration * fps)
    zoom_inc = 0.03 / frames  # 3% total zoom

    # Pass 1: Ken Burns zoom + dark gradient (no text — no escaping issues)
    raw = str(output_path) + ".raw.mp4"
    filter1 = (
        f"scale=1920:1080,setsar=1,"
        f"zoompan=z='zoom+{zoom_inc:.10f}':"
        f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
        f"d={frames}:s=1080x1920:fps={fps},"
        f"drawbox=x=0:y=ih*0.72:w=iw:h=ih*0.28:color=black@0.6:t=fill"
    )
    cmd1 = [
        "ffmpeg", "-y", "-loop", "1", "-i", str(image_path),
        "-vf", filter1,
        "-t", str(duration),
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-pix_fmt", "yuv420p", raw
    ]
    r1 = subprocess.run(cmd1, capture_output=True, text=True, timeout=120)
    if r1.returncode != 0:
        print(f"    ffmpeg pass1 error: {r1.stderr[-300:]}")
        return False

    # Pass 2: overlay text via drawtext textfile (avoids inline escaping)
    badge = (category or "NEWS").upper().replace('-', ' ')

    # Write headline to temp file for drawtext textfile= param
    clean_headline = headline.encode('ascii', 'ignore').decode('ascii').strip()
    words = clean_headline.split()
    line1_words, line2_words = [], []
    cur_len = 0
    for w in words:
        if cur_len + len(w) + 1 <= 30:
            line1_words.append(w)
            cur_len += len(w) + 1
        elif len(line2_words) == 0 or sum(len(x)+1 for x in line2_words) + len(w) + 1 <= 30:
            line2_words.append(w)
        else:
            break
    hl_line1 = " ".join(line1_words)
    hl_line2 = " ".join(line2_words)

    # Use chained drawtext — pass each line as textfile to avoid escaping
    # Use absolute paths (ffmpeg textfile= needs them)
    hl1_file = str(BUILD_DIR / "vo-hl1.txt")
    hl2_file = str(BUILD_DIR / "vo-hl2.txt")
    badge_file = str(BUILD_DIR / "vo-badge.txt")
    with open(hl1_file, 'w') as f: f.write(hl_line1)
    with open(hl2_file, 'w') as f: f.write(hl_line2)
    with open(badge_file, 'w') as f: f.write(badge)

    font_bold = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    font_reg = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

    # Use absolute pixel positions for 1080x1920:
    # gradient: y=1382 (72%), badge: y=1421 (74%), badge text: y=1431,
    # headline1: y=1574 (82%), headline2: y=1616 (82%+42)
    filter2_parts = [
        f"drawbox=x=40:y=1421:w=200:h=44:color=#C41E3A:t=fill",
        f"drawtext=textfile={badge_file}:fontsize=22:fontcolor=white:x=50:y=1431:fontfile={font_bold}",
        f"drawtext=textfile={hl1_file}:fontsize=32:fontcolor=white:x=40:y=1574:fontfile={font_bold}",
    ]
    if hl_line2:
        filter2_parts.append(
            f"drawtext=textfile={hl2_file}:fontsize=32:fontcolor=white:x=40:y=1616:fontfile={font_bold}"
        )
    filter2_parts.append(
        f"drawtext=text=THE VIDESHI:fontsize=16:fontcolor=white@0.5:x=w-tw-20:y=20:fontfile={font_reg}"
    )
    filter2 = ",".join(filter2_parts)

    cmd2 = [
        "ffmpeg", "-y", "-i", raw,
        "-vf", filter2,
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-pix_fmt", "yuv420p", str(output_path)
    ]
    r2 = subprocess.run(cmd2, capture_output=True, text=True, timeout=120)

    # Clean up raw
    try: os.remove(raw)
    except: pass

    if r2.returncode != 0:
        print(f"    ffmpeg pass2 error: {r2.stderr[-300:]}")
        return False
    return True


def _concat_with_crossfade(video_segments, audio_path, output_path, fps):
    """Concatenate video segments + mux voice-over audio. Clean concat (no xfade to avoid sync issues)."""
    # Write concat list
    concat_file = BUILD_DIR / "vo-concat.txt"
    with open(concat_file, 'w') as f:
        for seg in video_segments:
            f.write(f"file '{seg}'\n")
    
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", str(concat_file),
        "-i", str(audio_path),
        "-map", "0:v", "-map", "1:a",
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        "-pix_fmt", "yuv420p",
        str(output_path)
    ]
    
    subprocess.run(cmd, capture_output=True, text=True, timeout=120)


def _wrap_headline(text, max_chars=30, max_lines=2):
    """Wrap headline for ffmpeg drawtext (escape special chars)."""
    # Strip problematic unicode first
    text = text.encode('ascii', 'ignore').decode('ascii')
    words = text.split()
    lines = []
    current = ""
    for w in words:
        if len(current) + len(w) + 1 > max_chars:
            lines.append(current.strip())
            current = w
            if len(lines) >= max_lines:
                break
        else:
            current += " " + w
    if current.strip() and len(lines) < max_lines:
        lines.append(current.strip())
    
    result = "\\n".join(lines)
    # Escape ffmpeg drawtext special chars
    result = result.replace("\\", "\\\\\\\\")
    result = result.replace("'", "\\'")
    result = result.replace(":", "\\:")
    result = result.replace("%", "%%")
    result = result.replace('"', '\\"')
    result = result.replace(';', '\\;')
    return result


# ── Captions ──────────────────────────────────────────────────────────────────

def generate_srt_from_audio(audio_path, script_text):
    """Whisper transcription → SRT file."""
    srt_path = str(audio_path).rsplit('.', 1)[0] + '.srt'
    
    r = requests.post(
        "https://api.openai.com/v1/audio/transcriptions",
        headers={"Authorization": f"Bearer {OPENAI_KEY}"},
        files={"file": ("audio.mp3", open(audio_path, "rb"), "audio/mp3")},
        data={"model": "whisper-1", "response_format": "srt", "prompt": script_text},
        timeout=60
    )
    
    if r.status_code == 200 and r.text.strip():
        with open(srt_path, 'w') as f:
            f.write(r.text)
        entries = len([l for l in r.text.strip().split('\n') if l.strip().isdigit()])
        print(f"  ✅ SRT captions: {entries} entries")
        return srt_path
    else:
        print(f"  ⚠️ Whisper failed: {r.status_code}")
        return None


def burn_captions(video_path, srt_path, output_path, margin_v=250):
    """Burn SRT captions using portrait_fix ASS layout."""
    try:
        from portrait_fix import burn_captions_news_layout
        return burn_captions_news_layout(video_path, srt_path, output_path, margin_v=margin_v)
    except Exception as e:
        print(f"  ⚠️ Caption burn failed: {e}, using ffmpeg subtitles filter")
        cmd = [
            "ffmpeg", "-y", "-i", str(video_path),
            "-vf", f"subtitles={srt_path}:force_style='FontSize=22,Alignment=2,MarginV={margin_v},"
                   f"PrimaryColour=&HFFFFFF&,OutlineColour=&H000000&,Outline=2,Shadow=1,"
                   f"FontName=DejaVu Sans'",
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-c:a", "copy", str(output_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        return result.returncode == 0


# ── Hook & End Card (reuse from orchestrator) ────────────────────────────────

def create_hook_frame(line1, line2, output_path):
    """Create a hook frame PNG (9:16 with bold text)."""
    filter_str = (
        f"color=c=#1a1a2e:s=1080x1920:d=1[bg];"
        f"[bg]drawtext=text='{_esc(line1)}':fontsize=64:fontcolor=#C41E3A:"
        f"x=(w-tw)/2:y=h/2-80:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf,"
        f"drawtext=text='{_esc(line2)}':fontsize=48:fontcolor=white:"
        f"x=(w-tw)/2:y=h/2+20:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf,"
        f"drawtext=text='THE VIDESHI':fontsize=20:fontcolor=white@0.4:"
        f"x=(w-tw)/2:y=h-100:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    )
    cmd = ["ffmpeg", "-y", "-f", "lavfi", "-i", f"color=c=#1a1a2e:s=1080x1920:d=1",
           "-vf", f"drawtext=text='{_esc(line1)}':fontsize=64:fontcolor=#C41E3A:"
                  f"x=(w-tw)/2:y=h/2-80:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf,"
                  f"drawtext=text='{_esc(line2)}':fontsize=48:fontcolor=white:"
                  f"x=(w-tw)/2:y=h/2+20:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf,"
                  f"drawtext=text='THE VIDESHI':fontsize=20:fontcolor=white@0.4:"
                  f"x=(w-tw)/2:y=h-100:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
           "-frames:v", "1", str(output_path)]
    subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return os.path.exists(output_path)


def _esc(text):
    """Escape text for ffmpeg drawtext."""
    for ch in ["'", ":", "%", "\\"]:
        text = text.replace(ch, f"\\{ch}")
    return text


def create_hook_video(hook_png, output_path, duration=2.5, fps=25):
    """Static hook frame → short video."""
    cmd = [
        "ffmpeg", "-y", "-loop", "1", "-i", str(hook_png),
        "-t", str(duration), "-r", str(fps),
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-pix_fmt", "yuv420p", str(output_path)
    ]
    subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return os.path.exists(output_path)


def get_or_create_end_card():
    """Get the standard end card video."""
    end_card = REELS_DIR / "end-card.mp4"
    if end_card.exists():
        return str(end_card)
    
    # Create simple end card
    end_png = BUILD_DIR / "end-card.png"
    cmd = [
        "ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=#1a1a2e:s=1080x1920:d=1",
        "-vf", "drawtext=text='THE VIDESHI':fontsize=56:fontcolor=white:"
               "x=(w-tw)/2:y=h/2-40:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf,"
               "drawtext=text='thevideshi.com':fontsize=28:fontcolor=#C41E3A:"
               "x=(w-tw)/2:y=h/2+40:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf,"
               "drawtext=text='Follow for more':fontsize=22:fontcolor=white@0.6:"
               "x=(w-tw)/2:y=h/2+90:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "-frames:v", "1", str(end_png)
    ]
    subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    
    cmd = [
        "ffmpeg", "-y", "-loop", "1", "-i", str(end_png),
        "-t", "2.5", "-r", "25",
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-pix_fmt", "yuv420p", str(end_card)
    ]
    subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    return str(end_card) if end_card.exists() else None


# ── Music ─────────────────────────────────────────────────────────────────────

def add_music_and_hook(content_video, hook_video, end_card_video, output_path, category):
    """
    Final assembly: hook + content + end card, with background music underneath.
    Audio from content_video (voice-over + captions) stays on top.
    Hook/end card get silent audio added for concat compatibility.
    """
    # Pick music
    music_dir = PIPELINE_DIR / "music"
    if category == 'sports':
        music_file = music_dir / "breaking-news-breaking-news-30s.mp3"
    else:
        music_file = music_dir / "dramatic-dark-suspense-thriller.mp3"
    
    if not music_file.exists():
        music_file = None
    
    # Helper: add silent audio track to video-only files
    def ensure_audio(video_path, out_path):
        """Add silent audio if the file has no audio stream."""
        probe = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "a",
             "-show_entries", "stream=codec_type", "-of", "csv=p=0", str(video_path)],
            capture_output=True, text=True, timeout=10
        )
        if "audio" in probe.stdout:
            return str(video_path)  # already has audio
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(video_path),
             "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
             "-c:v", "copy", "-c:a", "aac", "-shortest", str(out_path)],
            capture_output=True, text=True, timeout=30
        )
        return str(out_path) if os.path.exists(out_path) else str(video_path)
    
    # Prepare segments with audio
    segments_for_concat = []
    
    if hook_video and os.path.exists(hook_video):
        hook_with_audio = str(BUILD_DIR / "vo-hook-audio.mp4")
        segments_for_concat.append(ensure_audio(hook_video, hook_with_audio))
    
    segments_for_concat.append(str(content_video))
    
    if end_card_video and os.path.exists(end_card_video):
        ec_with_audio = str(BUILD_DIR / "vo-endcard-audio.mp4")
        segments_for_concat.append(ensure_audio(end_card_video, ec_with_audio))
    
    # Concat all segments
    concat_file = BUILD_DIR / "vo-final-concat.txt"
    with open(concat_file, 'w') as f:
        for seg in segments_for_concat:
            f.write(f"file '{seg}'\n")
    
    concat_out = BUILD_DIR / "vo-concatenated.mp4"
    cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file),
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        str(concat_out)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    
    if not concat_out.exists():
        print(f"❌ Concat failed: {result.stderr[-200:]}")
        return False
    
    # Add background music (low volume under voice)
    if music_file:
        cmd = [
            "ffmpeg", "-y",
            "-i", str(concat_out),
            "-stream_loop", "-1", "-i", str(music_file),
            "-filter_complex",
            "[0:a]volume=1.0[voice];"
            "[1:a]volume=0.12[music];"
            "[voice][music]amix=inputs=2:duration=first:dropout_transition=2[audio]",
            "-map", "0:v", "-map", "[audio]",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            "-shortest",
            str(output_path)
        ]
    else:
        cmd = ["cp", str(concat_out), str(output_path)]
    
    subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    
    # Normalize audio to -14 LUFS
    if os.path.exists(output_path):
        try:
            from portrait_fix import normalize_audio_social
            normalized = str(output_path).replace('.mp4', '-norm.mp4')
            if normalize_audio_social(str(output_path), normalized):
                os.replace(normalized, str(output_path))
                print("  ✅ Audio normalized to -14 LUFS")
        except Exception as e:
            print(f"  ⚠️ Audio normalization skipped: {e}")
    
    return os.path.exists(output_path)


# ── Upload & Register ─────────────────────────────────────────────────────────

def upload_to_supabase(local_path, storage_name):
    with open(local_path, 'rb') as f:
        data = f.read()
    
    r = requests.post(
        f"{SB_URL}/storage/v1/object/article-images/reels/{storage_name}",
        headers={
            "apikey": SB_KEY,
            "Authorization": f"Bearer {SB_KEY}",
            "Content-Type": "video/mp4",
            "x-upsert": "true"
        },
        data=data,
        timeout=120
    )
    
    if r.status_code in (200, 201):
        url = f"{SB_URL}/storage/v1/object/public/article-images/reels/{storage_name}"
        print(f"  ✅ Uploaded: {storage_name}")
        return url
    else:
        print(f"  ❌ Upload failed: {r.status_code} {r.text[:200]}")
        return None


def build_caption_text(article):
    """Build Instagram caption."""
    headline = article.get('headline', '')
    subheadline = article.get('subheadline', '')
    slug = article.get('slug', '')
    category = article.get('category', '')
    
    base_tags = "#indiandiaspora #nri #thevideshi #india"
    cat_tags = {
        'news': '#indianews #breakingnews #desinews',
        'sports': '#cricket #ipl #teamindia #sports',
        'entertainment': '#bollywood #entertainment #indiancinema',
        'technology': '#technews #indiantech #ai',
        'immigration': '#h1b #immigration #greencard #uscis',
        'nri-world': '#nrilife #desiabroad #indianamerican',
        'markets-finance': '#stockmarket #nifty #sensex',
        'travel': '#travelindia #incredibleindia',
        'lifestyle-health': '#wellness #desilifestyle',
        'food': '#indianfood #desifood'
    }
    
    caption = f"{headline}\n\n"
    if subheadline:
        caption += f"{subheadline}\n\n"
    caption += f"Full story: https://thevideshi.com/articles/{slug}\n\n"
    caption += f"{base_tags} {cat_tags.get(category, '')}"
    
    return caption


def register_reel(article, video_url, video_path, caption):
    """Register in prebuilt_reels for IG/YT crons to pick up."""
    payload = {
        "article_id": article['id'],
        "article_slug": article.get('slug', ''),
        "headline": article.get('headline', ''),
        "video_path": video_path,
        "video_url": video_url,
        "caption": caption,
        "status": "pending",
        "source": "voiceover",
        "qa_passed": True,
        "qa_score": 8
    }
    
    r = requests.post(
        f"{SB_URL}/rest/v1/prebuilt_reels",
        headers={
            "apikey": SB_KEY,
            "Authorization": f"Bearer {SB_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        },
        json=payload,
        timeout=15
    )
    
    if r.status_code in (200, 201):
        reel_id = r.json()[0]['id'] if isinstance(r.json(), list) else r.json().get('id')
        print(f"  ✅ Registered: {reel_id}")
        return reel_id
    else:
        print(f"  ❌ Registration failed: {r.status_code} {r.text[:200]}")
        return None


# ── Main ──────────────────────────────────────────────────────────────────────

def run(args):
    print("=" * 60)
    print(f"🎙️ Voice-Over Reel Builder — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"   TTS: {TTS_PROVIDER} / {TTS_VOICE}")
    print("=" * 60)
    
    # 1. Pick article
    if args.article_id:
        r = requests.get(
            f"{SB_URL}/rest/v1/p2_articles?id=eq.{args.article_id}&select=*",
            headers={"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"},
            timeout=10
        )
        articles = r.json() if r.status_code == 200 else []
        article = articles[0] if articles else None
    else:
        articles = get_recent_articles(hours=48, limit=30)
        existing = get_existing_reel_slugs()
        article = pick_article(articles, existing)
    
    if not article:
        print("❌ No article found")
        return
    
    print(f"\n📰 Article: {article['headline'][:80]}")
    print(f"   Category: {article.get('category')} | Slug: {article.get('slug', '')[:50]}")
    
    # 2. Generate script
    print("\n📝 Generating voice-over script...")
    script_data = generate_voiceover_script(article)
    if not script_data:
        print("❌ Script generation failed")
        return
    
    script = script_data['script']
    
    # 3. TTS → audio
    print(f"\n🎙️ Generating TTS audio ({TTS_PROVIDER})...")
    audio_path = BUILD_DIR / "vo-audio.mp3"
    if not generate_tts(script, str(audio_path)):
        print("❌ TTS failed")
        return
    
    audio_dur = get_audio_duration(str(audio_path))
    print(f"  Duration: {audio_dur:.1f}s")
    
    # 4. Source B-roll images
    print("\n🖼️ Sourcing B-roll images...")
    images = source_images(
        script_data.get('image_queries', []),
        article,
        count=5
    )
    
    if len(images) < 2:
        print("❌ Not enough images for B-roll")
        return
    
    # 5. Render B-roll video
    print("\n🎬 Rendering B-roll video...")
    broll_video = BUILD_DIR / "vo-broll-assembled.mp4"
    if not render_broll_video(images, str(audio_path), str(broll_video),
                             article['headline'], article.get('category', '')):
        print("❌ B-roll render failed")
        return
    
    # 6. Generate captions
    print("\n📝 Generating captions (Whisper)...")
    srt_path = generate_srt_from_audio(str(audio_path), script)
    
    # 7. Burn captions onto B-roll video
    captioned = BUILD_DIR / "vo-captioned.mp4"
    if srt_path:
        print("  Burning captions...")
        burn_captions(str(broll_video), srt_path, str(captioned), margin_v=250)
    else:
        captioned = broll_video
    
    content_video = str(captioned) if captioned.exists() else str(broll_video)
    
    # 8. Hook + end card + music
    print("\n🎵 Final assembly (hook + content + end card + music)...")
    hook_png = BUILD_DIR / "vo-hook.png"
    hook_video = BUILD_DIR / "vo-hook.mp4"
    
    line1 = script_data.get('hook_line1', article['headline'][:25].upper())
    line2 = script_data.get('hook_line2', 'THE VIDESHI')
    
    create_hook_frame(line1, line2, str(hook_png))
    create_hook_video(str(hook_png), str(hook_video))
    
    end_card = get_or_create_end_card()
    
    # Slug for filename
    slug_short = article.get('slug', 'unknown')[:60]
    final_name = f"reel-vo-{slug_short}.mp4"
    final_path = REELS_DIR / final_name
    
    if not add_music_and_hook(content_video, str(hook_video), end_card,
                              str(final_path), article.get('category', '')):
        print("❌ Final assembly failed")
        return
    
    # 9. Stats
    size_mb = os.path.getsize(str(final_path)) / (1024 * 1024)
    dur = get_audio_duration(str(final_path))
    print(f"\n✅ Voice-over reel complete!")
    print(f"   📁 {final_path}")
    print(f"   ⏱️ {dur:.1f}s | 📦 {size_mb:.1f} MB")
    
    # 10. Upload & register
    if not args.no_upload:
        print("\n☁️ Uploading to Supabase...")
        storage_name = final_name
        video_url = upload_to_supabase(str(final_path), storage_name)
        
        if video_url:
            caption = build_caption_text(article)
            reel_id = register_reel(article, video_url, str(final_path), caption)
            if reel_id:
                print(f"\n🎉 Done! Reel registered as pending — crons will post it.")
                print(f"   Video: {video_url}")
    else:
        print("\n   (--no-upload: skipping Supabase upload)")
    
    return str(final_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Voice-Over Reel Builder")
    parser.add_argument("--article-id", help="Specific article UUID")
    parser.add_argument("--no-upload", action="store_true", help="Skip Supabase upload")
    parser.add_argument("--voice", default="nova", help="TTS voice (default: nova)")
    parser.add_argument("--provider", default="openai", choices=["openai", "elevenlabs"],
                        help="TTS provider")
    args = parser.parse_args()
    
    if args.voice:
        TTS_VOICE = args.voice
    if args.provider:
        TTS_PROVIDER = args.provider
    
    run(args)
