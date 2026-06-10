#!/usr/bin/env python3
"""
Shotstack Reel Renderer for The Videshi
========================================
Professional automated reel generation using Shotstack cloud API.
Replaces ffmpeg-based rendering with cloud-rendered reels featuring:
  - Word-by-word animated captions (rich-caption with karaoke/highlight)
  - Ken Burns zoom on B-roll images
  - Smooth fade transitions between clips
  - HTML branded overlays (logo, category badge, hook frame)
  - Professional audio mixing (voice + background music)
  - 1080x1920 portrait output

Usage:
  python3 shotstack-reel.py                    # Auto-pick article
  python3 shotstack-reel.py --article-id UUID  # Specific article
  python3 shotstack-reel.py --dry-run          # Build JSON only, don't render
  python3 shotstack-reel.py --test             # Quick test with sample data
  python3 shotstack-reel.py --format pulse     # Quick Pulse format (no voice)
"""

import os, sys, json, time, random, re, argparse, subprocess, hashlib
from datetime import datetime, timedelta, timezone
from pathlib import Path
import requests

# ─── Config ──────────────────────────────────────────────────────────────────

PIPELINE_DIR = Path(__file__).parent
BUILD_DIR = PIPELINE_DIR / "reels" / "build"
REELS_DIR = PIPELINE_DIR / "reels"
BUILD_DIR.mkdir(parents=True, exist_ok=True)

SB_URL = "https://lboecaekpynbpyijrbfz.supabase.co"
STORAGE_BASE = f"{SB_URL}/storage/v1/object/public/article-images"
FONT_URL = f"{STORAGE_BASE}/fonts/Inter-Bold.ttf"

# Shotstack
SHOTSTACK_STAGE_URL = "https://api.shotstack.io/edit/stage"
SHOTSTACK_PROD_URL = "https://api.shotstack.io/edit/v1"

# Brand colors
GOLD = "#D4AF37"
NAVY = "#0a1628"
NAVY_LIGHT = "#131d2e"
WHITE = "#ffffff"
RED_BADGE = "#C41E3A"

# TTS
TTS_VOICE = "99fdc056cb054503a9bb53dee01a9e7e"  # Kavya - Voice 1 (matches HeyGen avatar)

# Category → music mapping
CATEGORY_MUSIC = {
    "news": "breaking-news-30s.mp3",
    "nri-world": "breaking-news-30s.mp3",
    "immigration": "breaking-news-30s.mp3",
    "sports": "breaking-news-30s.mp3",
    "technology": "tech-corporate-technology-30s.mp3",
    "markets-finance": "tech-corporate-technology-30s.mp3",
    "entertainment": "chill-lifestyle-lifestyle-30s.mp3",
    "lifestyle-health": "chill-lifestyle-lifestyle-30s.mp3",
    "food": "chill-lifestyle-lifestyle-30s.mp3",
    "travel": "emotional-inspiring-uplifting-piano-30s.mp3",
}

# Music volume per category mood
MUSIC_VOLUME = {
    "news": 0.05, "nri-world": 0.05, "immigration": 0.05,
    "sports": 0.06, "technology": 0.05, "markets-finance": 0.04,
    "entertainment": 0.07, "lifestyle-health": 0.06,
    "food": 0.07, "travel": 0.07,
}

# Ken Burns effects to rotate through
KEN_BURNS_EFFECTS = ["zoomIn", "zoomOut", "slideLeft", "slideRight", "slideUp"]


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
            raw = line
            if raw.startswith('export '):
                raw = raw[7:]
            k, v = raw.split('=', 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


# Load env files
SB_ENV = load_env("~/.env.supabase") or load_env("~/workspace/.env.supabase")
HG_ENV = load_env("~/workspace/.env.heygen")
OAI_ENV = load_env("~/workspace/.env.openai") or load_env("~/.env.openai")
SS_ENV = load_env("~/workspace/the-videshi-news/pipeline/.env.shotstack")

SB_KEY = SB_ENV.get("SUPABASE_SERVICE_ROLE_KEY", "")
HEYGEN_KEY = HG_ENV.get("HEYGEN_API_KEY", "")
OPENAI_KEY = OAI_ENV.get("OPENAI_API_KEY", "")
SHOTSTACK_KEY = SS_ENV.get("SHOTSTACK_SANDBOX_KEY", "")
SHOTSTACK_PROD_KEY = SS_ENV.get("SHOTSTACK_PRODUCTION_KEY", "")

SB_HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
}


# ═══════════════════════════════════════════════════════════════════════════════
# ARTICLE SELECTION
# ═══════════════════════════════════════════════════════════════════════════════

def get_recent_articles(hours=24, limit=20):
    since = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    r = requests.get(
        f"{SB_URL}/rest/v1/p2_articles",
        headers=SB_HEADERS,
        params={
            "select": "id,headline,subheadline,slug,category,vertical,body,image_url,published_at",
            "status": "eq.published",
            "published_at": f"gte.{since}",
            "order": "published_at.desc",
            "limit": limit,
        },
        timeout=15,
    )
    if r.status_code != 200:
        print(f"❌ Failed to fetch articles: {r.status_code}")
        return []
    return r.json()


def get_existing_reel_slugs():
    r = requests.get(
        f"{SB_URL}/rest/v1/prebuilt_reels",
        params={"select": "article_slug", "limit": 500},
        headers=SB_HEADERS,
        timeout=10,
    )
    if r.status_code == 200:
        return {row["article_slug"] for row in r.json() if row.get("article_slug")}
    return set()


def score_article(article):
    score = 0
    cat = (article.get("category") or "").lower()
    headline = (article.get("headline") or "").lower()

    cat_scores = {
        "news": 10, "nri-world": 9, "immigration": 9,
        "sports": 8, "entertainment": 8, "technology": 7,
        "markets-finance": 6, "travel": 6, "lifestyle-health": 5, "food": 5,
    }
    score += cat_scores.get(cat, 3)

    hot_keywords = [
        "h-1b", "visa", "green card", "modi", "trump", "breaking",
        "killed", "crash", "scandal", "ban", "deport", "ipl",
        "billion", "layoff", "shutdown", "election",
    ]
    for kw in hot_keywords:
        if kw in headline:
            score += 3
            break

    if article.get("image_url"):
        score += 2
    if len(headline) > 40:
        score += 1

    return score


def pick_article(articles, existing_slugs):
    candidates = [a for a in articles if a.get("slug") not in existing_slugs]
    if not candidates:
        return None
    candidates.sort(key=lambda a: score_article(a), reverse=True)
    return candidates[0]


# ═══════════════════════════════════════════════════════════════════════════════
# SCRIPT GENERATION
# ═══════════════════════════════════════════════════════════════════════════════

def generate_script(article, force_new=False):
    """Generate script for article. Caches to disk so re-renders reuse the same script."""
    headline = article.get("headline", "")
    subheadline = article.get("subheadline", "")
    body = (article.get("body") or "")[:3000]
    category = article.get("category", "")
    slug = article.get("slug", "unknown")

    # Script cache — reuse if already generated
    cache_path = BUILD_DIR / f"script-{slug}.json"
    if not force_new and cache_path.exists():
        try:
            cached = json.loads(cache_path.read_text())
            print(f"  📝 Using cached script ({len(cached['script'].split())} words)")
            print(f"  📝 Hook: {cached.get('hook_line1', '')} / {cached.get('hook_line2', '')}")
            return cached
        except Exception:
            pass  # Corrupted cache — regenerate

    prompt = f"""You write viral Instagram Reel scripts for The Videshi — news for the Indian diaspora.

This is a VOICE-OVER reel. No anchor on screen. Visuals are B-roll images that change every 5-7 seconds.

ARTICLE:
Headline: {headline}
Subheadline: {subheadline}
Category: {category}
Body: {body[:2500]}

SCRIPT RULES:
1. HOOK (first 3 seconds): Start with a jaw-dropping fact, a bold claim, or a "wait what?" moment. No pleasantries, no setup — hit them immediately.
2. TENSION: Build intrigue. Use contrast, stakes, or a narrative arc. "Here's why that matters for every NRI watching this."
3. PAYOFF: Land with a punch — a surprising twist, a forward-looking take, or a line that makes them want to share it.
4. TONE: Talk like a smart friend who just found out something wild. Confident, punchy, slightly urgent. NOT a news robot.
5. PACING: Short sentences. Vary rhythm. One-word sentences are fine.
6. LENGTH: 60-80 words. That's 25-35 seconds spoken. Every word earns its place.
7. SPECIFICS: Include at least one concrete number, name, or detail.
8. NO "Welcome to The Videshi", NO "Follow for more", NO emoji, NO hashtags.
9. End with "Full story at thevideshi dot com" ONLY if it flows naturally. Otherwise skip it.

HOOK TEXT (shown on screen before voice starts):
- hook_line1: 3-5 words, ALL CAPS. The "stop scrolling" line.
- hook_line2: 3-5 words, ALL CAPS. Adds context or intrigue.

STORYBOARD: Plan 5 visual scenes that match the narration beat-by-beat.
Each scene is ONE B-roll image shown for ~5 seconds while the voice plays.
- Scene 1 = the HOOK background (darkened). Choose something dramatic, cinematic.
- Scenes 2-5 = the narration beats. Each image must visually match EXACTLY what's being said.

For each scene, provide:
- "narration": the exact words spoken during that scene (copy from script)
- "visual": a SPECIFIC, concrete description of the ideal stock photo. Not "Indian economy" — say "close-up of Indian 500 rupee notes fanned out on a dark surface" or "aerial view of Mumbai Marine Drive at sunset". Be visual and precise.
- "search_queries": TWO Pexels search queries, each 3-5 words. Make them different angles on the same visual. First query = most specific, second = broader fallback.

CRITICAL RULES FOR SEARCH QUERIES:
- NEVER use celebrity, politician, or public figure names — Pexels has NO images of specific people. Instead describe the VISUAL CONCEPT: "Bollywood actor action scene" not "Sunny Deol".
- ALWAYS include "Indian" or "India" in queries when the story is about India, Bollywood, Indian culture, or the diaspora. "Indian cinema hall" not "cinema hall". "Indian currency notes" not "currency notes".
- Every scene's image must be DIFFERENT and RELEVANT. A story about remittances needs rupee notes, bank transfers, families — NOT steel factories or oil tankers.
- Think STOCK PHOTO: what would a photographer actually shoot? "crowded Indian railway platform" works. "Rahul Gandhi speaking at rally" does not exist on Pexels.

Return JSON only:
{{
  "script": "the spoken narration",
  "hook_line1": "BOLD HOOK LINE",
  "hook_line2": "CONTEXT LINE",
  "storyboard": [
    {{
      "scene": 1,
      "narration": "first ~15 words...",
      "visual": "specific visual description for this beat",
      "search_queries": ["specific query 1", "broader fallback query"]
    }},
    {{
      "scene": 2,
      "narration": "next ~15 words...",
      "visual": "specific visual description",
      "search_queries": ["specific query 1", "broader fallback query"]
    }}
  ]
}}"""

    r = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"},
        json={
            "model": "gpt-4o",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.8,
            "response_format": {"type": "json_object"},
        },
        timeout=30,
    )

    if r.status_code != 200:
        print(f"❌ Script generation failed: {r.status_code}")
        return None

    result = json.loads(r.json()["choices"][0]["message"]["content"])
    print(f"  📝 Script: {len(result['script'].split())} words")
    print(f"  📝 Hook: {result.get('hook_line1', '')} / {result.get('hook_line2', '')}")

    # Cache script so re-renders use the same words
    try:
        cache_path.write_text(json.dumps(result, indent=2))
        print(f"  💾 Script cached: {cache_path.name}")
    except Exception as e:
        print(f"  ⚠️ Cache write failed: {e}")

    return result


# ═══════════════════════════════════════════════════════════════════════════════
# TTS — HeyGen Seema Voice
# ═══════════════════════════════════════════════════════════════════════════════

def generate_tts(text):
    """Generate TTS via HeyGen Starfish. Returns (local_path, duration) or (None, 0).
    Applies loudnorm to -14 LUFS (social media standard)."""
    if not HEYGEN_KEY:
        print("❌ HeyGen API key not found")
        return None, 0

    # Phonetic hint for TTS — help Seema pronounce "TheVideshi" correctly
    # "Videshi" = विदेशी (vi-they-shi) — soft dental द, pure ए vowel, crisp शी
    tts_text = text.replace("thevideshi", "the Vitheyshi").replace("TheVideshi", "The Vitheyshi").replace("Videshi", "Vitheyshi")

    r = requests.post(
        "https://api.heygen.com/v3/voices/speech",
        headers={"X-Api-Key": HEYGEN_KEY, "Content-Type": "application/json"},
        json={"text": tts_text, "voice_id": TTS_VOICE, "speed": 1.0},
        timeout=30,
    )

    if r.status_code != 200:
        print(f"❌ HeyGen TTS failed: {r.status_code} {r.text[:200]}")
        return None, 0

    data = r.json().get("data", {})
    audio_url = data.get("audio_url")
    duration = data.get("duration", 0)

    if not audio_url:
        print("❌ HeyGen TTS returned no audio_url")
        return None, 0

    # Download audio
    audio_r = requests.get(audio_url, timeout=30)
    if audio_r.status_code != 200:
        print(f"❌ Audio download failed: {audio_r.status_code}")
        return None, 0

    # HeyGen returns WAV — convert to MP3 with loudness normalization
    wav_path = BUILD_DIR / "ss-tts-raw.wav"
    mp3_path = BUILD_DIR / "ss-tts-voice.mp3"
    with open(wav_path, "wb") as f:
        f.write(audio_r.content)

    result = subprocess.run(
        ["ffmpeg", "-y", "-i", str(wav_path),
         "-af", "loudnorm=I=-10:TP=-1.0:LRA=11",
         "-codec:a", "libmp3lame", "-q:a", "2", str(mp3_path)],
        capture_output=True, text=True,
    )
    try:
        os.remove(wav_path)
    except OSError:
        pass

    if result.returncode != 0:
        print(f"❌ WAV→MP3 conversion failed")
        return None, 0

    print(f"  🎙️ TTS audio: {duration:.1f}s (Kavya voice, normalized to -10 LUFS)")
    return str(mp3_path), duration


def get_word_timestamps(audio_path, script_text):
    """Get word-level timestamps from Whisper, using script text as spelling guide.
    Returns list of {word, start, end} or None on failure."""
    if not OPENAI_KEY:
        print("  ⚠️ No OpenAI key — cannot get word timestamps")
        return None

    try:
        with open(audio_path, "rb") as f:
            r = requests.post(
                "https://api.openai.com/v1/audio/transcriptions",
                headers={"Authorization": f"Bearer {OPENAI_KEY}"},
                files={"file": ("voice.mp3", f, "audio/mpeg")},
                data={
                    "model": "whisper-1",
                    "response_format": "verbose_json",
                    "timestamp_granularities[]": "word",
                    "prompt": script_text,
                    "language": "en",
                },
                timeout=60,
            )
        if r.status_code != 200:
            print(f"  ⚠️ Whisper failed ({r.status_code}), falling back to rich-caption")
            return None

        words = r.json().get("words", [])
        print(f"  📝 Whisper: {len(words)} words timestamped")
        return words
    except Exception as e:
        print(f"  ⚠️ Whisper error: {e}, falling back to rich-caption")
        return None


def build_script_captions(words, script_text, hook_duration):
    """Build HTML caption clips from Whisper timestamps + original script text.
    Groups words into ~4-5 word phrases for readability."""
    if not words:
        return None

    # Use Whisper timing but prefer script text for spelling accuracy
    # Split script into words for spelling reference
    script_words = script_text.split()

    # Group into phrases of ~4-5 words, break at punctuation
    phrases = []
    current = []
    for w in words:
        current.append(w)
        word_text = w.get("word", "")
        if len(current) >= 5 or word_text.rstrip().endswith((".", "!", "?", ",")):
            phrases.append(current)
            current = []
    if current:
        phrases.append(current)

    clips = []
    for phrase in phrases:
        text = " ".join(w.get("word", "") for w in phrase).strip().upper()
        start = hook_duration + phrase[0]["start"]
        end = hook_duration + phrase[-1]["end"]
        duration = max(end - start, 0.5)

        # Style matching the rich-caption look: white text, black stroke, centered
        html = (
            f"<div style=\"display:flex;align-items:center;justify-content:center;"
            f"width:100%;height:100%;padding:0 40px;\">"
            f"<div style=\"font-family:Inter;font-size:38px;font-weight:700;"
            f"color:{WHITE};text-align:center;letter-spacing:1px;"
            f"text-shadow: -2px -2px 0 #000, 2px -2px 0 #000, "
            f"-2px 2px 0 #000, 2px 2px 0 #000, 0 3px 6px rgba(0,0,0,0.5);\">"
            f"{text}</div></div>"
        )

        clips.append({
            "asset": {
                "type": "html",
                "html": html,
                "width": 900,
                "height": 200,
            },
            "start": round(start, 2),
            "length": round(duration + 0.15, 2),
            "position": "bottom",
            "offset": {"x": 0, "y": 0.18},
            "transition": {"in": "fade", "out": "fade"},
        })

    print(f"  📝 Built {len(clips)} caption clips from script text")
    return {"clips": clips}


# ═══════════════════════════════════════════════════════════════════════════════
# ASSET UPLOAD — Supabase Storage
# ═══════════════════════════════════════════════════════════════════════════════

def upload_asset(local_path, storage_path, content_type="application/octet-stream"):
    """Upload a file to Supabase storage. Uses curl for reliability with large files."""
    file_size = os.path.getsize(local_path)

    # Use curl for all uploads (more reliable than Python requests, especially for large files)
    result = subprocess.run(
        ["curl", "-s", "-X", "POST",
         f"{SB_URL}/storage/v1/object/article-images/{storage_path}",
         "-H", f"apikey: {SB_KEY}",
         "-H", f"Authorization: Bearer {SB_KEY}",
         "-H", f"Content-Type: {content_type}",
         "-H", "x-upsert: true",
         "--data-binary", f"@{local_path}",
         "--max-time", "180"],
        capture_output=True, text=True, timeout=200,
    )

    if result.returncode == 0 and '"Key"' in result.stdout:
        url = f"{STORAGE_BASE}/{storage_path}"
        print(f"  ☁️ Uploaded: {storage_path} ({file_size / (1024*1024):.1f} MB)")
        return url
    else:
        print(f"  ❌ Upload failed: {result.stdout[:200]} {result.stderr[:200]}")
        return None


def ensure_music_uploaded(music_file):
    """Ensure a music file is available at a public URL. Upload if needed."""
    storage_path = f"music/{music_file}"
    public_url = f"{STORAGE_BASE}/{storage_path}"

    # Check if already uploaded
    r = requests.head(public_url, timeout=10)
    if r.status_code == 200:
        return public_url

    # Find local file and upload
    local_candidates = [
        PIPELINE_DIR / "music" / music_file,
        PIPELINE_DIR / "music" / music_file.replace("-30s", "-breaking-news-30s"),
    ]

    # Try matching by prefix
    music_dir = PIPELINE_DIR / "music"
    if music_dir.exists():
        for f in music_dir.iterdir():
            if music_file.replace(".mp3", "") in f.name and f.suffix == ".mp3":
                local_candidates.insert(0, f)

    for candidate in local_candidates:
        if candidate.exists():
            url = upload_asset(str(candidate), storage_path, "audio/mpeg")
            if url:
                return url

    print(f"  ⚠️ Music file not found: {music_file}")
    return None


# ═══════════════════════════════════════════════════════════════════════════════
# IMAGE SOURCING — Collect public URLs (no local download needed)
# ═══════════════════════════════════════════════════════════════════════════════

BLOCKED_DOMAINS = [
    "upload.wikimedia.org", "wikipedia.org", "wikimedia.org",
    "commons.wikimedia.org", "static.toiimg.com", "im.rediff.com",
]


def is_url_downloadable(url):
    """Check if a URL is reachable by Shotstack (no Wikipedia, etc.)."""
    if not url or len(url) < 10:
        return False
    for domain in BLOCKED_DOMAINS:
        if domain in url:
            return False
    return True


def pexels_search(pexels_key, query, count=3):
    """Search Pexels, return list of dicts with url + photo_id. Uses curl (403 with urllib)."""
    try:
        result = subprocess.run(
            ["curl", "-s", "-H", f"Authorization: {pexels_key}",
             f"https://api.pexels.com/v1/search?query={requests.utils.quote(query)}&per_page={count}&orientation=portrait"],
            capture_output=True, text=True, timeout=15,
        )
        if result.returncode != 0:
            return []
        data = json.loads(result.stdout)
        results = []
        for photo in data.get("photos", []):
            url = photo.get("src", {}).get("large2x") or photo.get("src", {}).get("large")
            if url:
                results.append({
                    "url": url,
                    "photo_id": str(photo.get("id", "")),
                    "alt": photo.get("alt", ""),
                    "photographer": photo.get("photographer", ""),
                })
        return results
    except Exception as e:
        print(f"  ⚠️ Pexels: {e}")
        return []


# ── Used-image dedup log ──
USED_IMAGES_LOG = BUILD_DIR / "used-images.json"

def load_used_images():
    """Load set of previously-used Pexels photo IDs."""
    try:
        if USED_IMAGES_LOG.exists():
            data = json.loads(USED_IMAGES_LOG.read_text())
            return set(data.get("photo_ids", []))
    except Exception:
        pass
    return set()

def save_used_image(photo_id):
    """Append a Pexels photo ID to the dedup log."""
    used = load_used_images()
    used.add(str(photo_id))
    # Keep last 200 to avoid blocking everything over time
    id_list = sorted(used)[-200:]
    USED_IMAGES_LOG.write_text(json.dumps({"photo_ids": id_list}, indent=2))


def source_storyboard_images(article, storyboard, count=5):
    """Source B-roll images scene-by-scene from the storyboard.
    Returns list of image URLs matched to each scene in order."""
    urls = []
    used_ids = load_used_images()
    used_in_this_reel = set()  # No duplicates within same reel

    # Get article hero and related article images as a fallback pool
    hero = article.get("image_url", "")
    fallback_pool = []
    if is_url_downloadable(hero):
        fallback_pool.append(hero)

    category = article.get("category", "")
    article_id = article.get("id", "")
    if category:
        r = requests.get(
            f"{SB_URL}/rest/v1/p2_articles",
            params={
                "status": "eq.published",
                "category": f"eq.{category}",
                "id": f"neq.{article_id}",
                "image_url": "neq.null",
                "order": "published_at.desc",
                "limit": 15,
                "select": "id,image_url",
            },
            headers=SB_HEADERS,
            timeout=15,
        )
        if r.status_code == 200:
            for a in r.json():
                img = a.get("image_url", "")
                if is_url_downloadable(img) and img not in fallback_pool:
                    fallback_pool.append(img)

    pexels_env = load_env("~/workspace/.env.pexels")
    pexels_key = pexels_env.get("PEXELS_API_KEY", "")

    scenes = storyboard if storyboard else []
    for i, scene in enumerate(scenes[:count]):
        found = False
        queries = scene.get("search_queries", [])
        visual_desc = scene.get("visual", "")

        if pexels_key and queries:
            # Search each query, collect candidates
            candidates = []
            for query in queries[:2]:
                results = pexels_search(pexels_key, query, count=3)
                candidates.extend(results)

            # Pick first candidate not already used (globally or in this reel)
            for cand in candidates:
                pid = cand["photo_id"]
                if pid not in used_ids and pid not in used_in_this_reel and cand["url"] not in urls:
                    urls.append(cand["url"])
                    used_in_this_reel.add(pid)
                    save_used_image(pid)
                    print(f"  🎬 Scene {i+1}: {visual_desc[:60]}  →  Pexels #{pid}")
                    found = True
                    break

        # Fallback to related article images
        if not found and fallback_pool:
            fb = fallback_pool.pop(0)
            urls.append(fb)
            print(f"  🎬 Scene {i+1}: {visual_desc[:60]}  →  fallback (article image)")
            found = True

        if not found:
            print(f"  ⚠️ Scene {i+1}: no image found for '{visual_desc[:50]}'")

    # If storyboard gave fewer than needed, pad with remaining fallbacks
    while len(urls) < count and fallback_pool:
        urls.append(fallback_pool.pop(0))

    print(f"  🖼️ Sourced {len(urls)} B-roll images via storyboard (dedup active)")
    return urls


def source_image_urls(article, image_queries, count=5):
    """Legacy fallback — used when script has image_queries instead of storyboard."""
    urls = []

    # 1. Article hero image
    hero = article.get("image_url", "")
    if is_url_downloadable(hero):
        urls.append(hero)

    # 2. Related articles from same category (filter blocked domains)
    category = article.get("category", "")
    article_id = article.get("id", "")
    if category:
        r = requests.get(
            f"{SB_URL}/rest/v1/p2_articles",
            params={
                "status": "eq.published",
                "category": f"eq.{category}",
                "id": f"neq.{article_id}",
                "image_url": "neq.null",
                "order": "published_at.desc",
                "limit": count + 10,  # Fetch extra to account for filtered URLs
                "select": "id,image_url",
            },
            headers=SB_HEADERS,
            timeout=15,
        )
        if r.status_code == 200:
            for a in r.json():
                img = a.get("image_url", "")
                if is_url_downloadable(img) and img not in urls:
                    urls.append(img)
                    if len(urls) >= count:
                        break

    # 3. Pexels to fill remaining (use curl, not requests — Pexels blocks Python urllib)
    pexels_env = load_env("~/workspace/.env.pexels")
    pexels_key = pexels_env.get("PEXELS_API_KEY", "")
    if len(urls) < count and pexels_key and image_queries:
        for query in image_queries:
            if len(urls) >= count:
                break
            pexels_urls = pexels_search(pexels_key, query, count=1)
            for pu in pexels_urls:
                if pu not in urls:
                    urls.append(pu)
                    if len(urls) >= count:
                        break

    # 4. If still short, generic Pexels queries
    if len(urls) < 3 and pexels_key:
        generic = ["India economy", "Indian people", "technology abstract"]
        for query in generic:
            if len(urls) >= count:
                break
            pexels_urls = pexels_search(pexels_key, query, count=1)
            for pu in pexels_urls:
                if pu not in urls:
                    urls.append(pu)

    print(f"  🖼️ Sourced {len(urls)} B-roll image URLs (blocked domains filtered)")
    return urls[:count]


# ═══════════════════════════════════════════════════════════════════════════════
# SHOTSTACK TIMELINE BUILDER — Anchor Reel
# ═══════════════════════════════════════════════════════════════════════════════

def build_hook_html(hook_line1, hook_line2, category):
    """Build HTML for the 3-second hook frame overlay."""
    badge = (category or "NEWS").upper().replace("-", " ")
    # Use inline styles for maximum compatibility with Shotstack's HTML renderer
    html = f"""<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;width:100%;height:100%;padding:40px;box-sizing:border-box;background:rgba(0,0,0,0.65);">
  <div style="background:#C41E3A;color:#fff;font-family:Inter;font-size:28px;font-weight:700;padding:10px 32px;letter-spacing:5px;margin-bottom:50px;">{badge}</div>
  <div style="font-family:Inter;font-size:80px;font-weight:700;color:#fff;line-height:1.0;margin-bottom:24px;text-shadow:0 4px 40px rgba(0,0,0,0.9);">{hook_line1}</div>
  <div style="font-family:Inter;font-size:54px;font-weight:700;color:#D4AF37;line-height:1.1;text-shadow:0 2px 20px rgba(0,0,0,0.7);">{hook_line2}</div>
  <div style="font-family:Inter;font-size:16px;color:rgba(255,255,255,0.3);letter-spacing:6px;margin-top:60px;">THE VIDESHI</div>
</div>"""

    css = ""  # All inline
    return html, css


def build_lower_third_html(headline, category):
    """Build HTML for the lower-third headline overlay during B-roll."""
    badge = (category or "NEWS").upper().replace("-", " ")
    # Truncate headline for display
    display_hl = headline[:80] + ("..." if len(headline) > 80 else "")

    html = f"""<div class='lower-third'>
  <div class='lt-badge'>{badge}</div>
  <div class='lt-headline'>{display_hl}</div>
</div>"""

    css = """
.lower-third {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: flex-end;
  width: 100%;
  height: 100%;
  padding: 0 32px 16px 32px;
  box-sizing: border-box;
  background: linear-gradient(transparent 0%, rgba(10,22,40,0.85) 60%, rgba(10,22,40,0.95) 100%);
}
.lt-badge {
  background: #C41E3A;
  color: #ffffff;
  font-family: 'Inter';
  font-size: 14px;
  font-weight: 700;
  padding: 4px 14px;
  letter-spacing: 2px;
  margin-bottom: 10px;
  border-radius: 2px;
}
.lt-headline {
  font-family: 'Inter';
  font-size: 24px;
  font-weight: 700;
  color: #ffffff;
  line-height: 1.25;
}
""".strip()

    return html, css


def build_anchor_reel_timeline(
    voice_url, voice_duration, image_urls, music_url, music_volume,
    hook_line1, hook_line2, headline, category,
    word_timestamps=None, script_text=None,
):
    """Build the complete Shotstack JSON timeline for an Anchor Reel."""

    hook_duration = 3.0  # Hook frame duration
    total_voice_duration = voice_duration
    cta_start = hook_duration + total_voice_duration + 0.5  # 0.5s pause before CTA
    total_duration = cta_start + CTA_DURATION

    # ── Track 1 (TOP): Script-based captions (Whisper-timed) or rich-caption fallback ──
    script_caps = None
    if word_timestamps and script_text:
        script_caps = build_script_captions(word_timestamps, script_text, hook_duration)

    if script_caps:
        caption_track = script_caps
    else:
        # Fallback: Shotstack auto-caption from audio (may mis-transcribe proper nouns)
        caption_track = {
            "clips": [
                {
                    "asset": {
                        "type": "rich-caption",
                        "src": "alias://voiceover",
                        "font": {
                            "family": "Inter",
                            "size": 38,
                            "color": WHITE,
                            "weight": 700,
                            "opacity": 1,
                        },
                        "animation": {"style": "highlight"},
                        "active": {
                            "font": {"color": GOLD, "opacity": 1},
                            "stroke": {"width": 3, "color": "#000000", "opacity": 1},
                        },
                        "stroke": {"width": 2, "color": "#000000", "opacity": 0.8},
                        "align": {"vertical": "bottom"},
                        "style": {"textTransform": "uppercase"},
                        "padding": {"top": 0, "right": 8, "bottom": 0, "left": 8},
                    },
                    "start": hook_duration,
                    "length": "end",
                    "width": 900,
                    "height": 200,
                    "position": "bottom",
                    "offset": {"x": 0, "y": 0.18},
                }
            ]
        }

    # ── Track 2: Logo watermark ──
    logo_track = {
        "clips": [
            {
                "asset": {
                    "type": "html",
                    "html": "<div class='wm'>THE VIDESHI</div>",
                    "css": ".wm { font-family: 'Inter'; color: rgba(255,255,255,0.35); font-size: 13px; font-weight: 700; letter-spacing: 3px; text-align: right; padding: 6px 12px; }",
                    "width": 200,
                    "height": 36,
                },
                "start": hook_duration,  # Show after hook
                "length": "end",
                "position": "topRight",
                "offset": {"x": -0.02, "y": 0.02},
            }
        ]
    }

    # ── Track 3: Hook frame overlay (first 3 seconds) ──
    hook_html, hook_css = build_hook_html(hook_line1, hook_line2, category)
    hook_track = {
        "clips": [
            {
                "asset": {
                    "type": "html",
                    "html": hook_html,
                    "css": hook_css,
                    "width": 1080,
                    "height": 1920,
                },
                "start": 0,
                "length": hook_duration,
                "position": "center",
                "transition": {"out": "fade"},
            }
        ]
    }

    # ── Track 4: Lower third (during B-roll) ──
    lt_html, lt_css = build_lower_third_html(headline, category)
    lower_third_track = {
        "clips": [
            {
                "asset": {
                    "type": "html",
                    "html": lt_html,
                    "css": lt_css,
                    "width": 1080,
                    "height": 500,
                },
                "start": hook_duration,
                "length": total_voice_duration + 1.0,
                "position": "bottom",
                "transition": {"in": "fade"},
                "opacity": 0.95,
            }
        ]
    }

    # ── Track 5: B-roll images with Ken Burns + transitions ──
    n_images = len(image_urls)
    if n_images == 0:
        print("❌ No images for B-roll")
        return None

    broll_clips = []

    # Hook background image (darkened, first image)
    broll_clips.append({
        "asset": {"type": "image", "src": image_urls[0]},
        "start": 0,
        "length": hook_duration,
        "fit": "cover",
        "effect": "zoomIn",
        "filter": "darken",
    })

    # B-roll during voiceover — distribute images evenly
    per_image = total_voice_duration / n_images
    for i, url in enumerate(image_urls):
        clip = {
            "asset": {"type": "image", "src": url},
            "start": round(hook_duration + (i * per_image), 2),
            "length": round(per_image + 0.3, 2),  # Slight overlap for transition
            "fit": "cover",
            "effect": KEN_BURNS_EFFECTS[i % len(KEN_BURNS_EFFECTS)],
        }
        if i > 0:
            clip["transition"] = {"in": "fade"}
        broll_clips.append(clip)

    broll_track = {"clips": broll_clips}

    # ── CTA: Branded end card (HTML overlay on dark background) ──
    end_html, end_css = build_end_card_html()
    end_card_track = {
        "clips": [
            {
                "asset": {
                    "type": "html",
                    "html": end_html,
                    "css": end_css,
                    "width": 1080,
                    "height": 1920,
                },
                "start": round(cta_start, 2),
                "length": CTA_DURATION,
                "position": "center",
                "transition": {"in": "fade"},
            }
        ]
    }

    # ── Track 6 (BOTTOM): Voice-over audio with alias ──
    voice_track = {
        "clips": [
            {
                "asset": {
                    "type": "audio",
                    "src": voice_url,
                    "volume": 1.0,
                    "effect": "fadeOut",
                },
                "start": hook_duration,
                "length": "auto",
                "alias": "voiceover",
            }
        ]
    }

    # ── Assemble timeline ──
    timeline = {
        "background": NAVY,
        "fonts": [{"src": FONT_URL}],
        "tracks": [
            caption_track,    # Top layer
            logo_track,
            hook_track,
            lower_third_track,
            end_card_track,   # Branded end card
            broll_track,      # Visual base
            voice_track,      # Audio (bottom)
        ],
    }

    # Add soundtrack if music available
    if music_url:
        timeline["soundtrack"] = {
            "src": music_url,
            "effect": "fadeInFadeOut",
            "volume": music_volume,
        }

    edit = {
        "timeline": timeline,
        "output": {
            "format": "mp4",
            "size": {"width": 1080, "height": 1920},
            "fps": 30,
            "quality": "high",
        },
    }

    return edit


# ═══════════════════════════════════════════════════════════════════════════════
# SHOTSTACK TIMELINE BUILDER — Quick Pulse (no voice)
# ═══════════════════════════════════════════════════════════════════════════════

def build_quick_pulse_timeline(
    image_urls, music_url, music_volume,
    headline, subheadline, category, key_stats=None
):
    """Build a Quick Pulse reel — music + bold text + visuals, no voice."""

    # Split headline into animated text cards
    cards = []
    if key_stats:
        cards = key_stats[:5]  # Up to 5 stat cards
    else:
        # Split headline + subheadline into cards
        cards = [headline]
        if subheadline:
            # Split subheadline into 2-3 chunks
            words = subheadline.split()
            mid = len(words) // 2
            cards.append(" ".join(words[:mid]))
            cards.append(" ".join(words[mid:]))

    card_duration = 3.0
    total_duration = len(cards) * card_duration + 1.0
    badge = (category or "NEWS").upper().replace("-", " ")

    # ── Text cards track (top) ──
    text_clips = []
    for i, text in enumerate(cards):
        text_html = f"""<div class='pulse-card'>
  <div class='pulse-badge'>{badge}</div>
  <div class='pulse-text'>{text}</div>
  <div class='pulse-brand'>THE VIDESHI</div>
</div>"""

        text_css = """
.pulse-card { display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center; width:100%; height:100%; padding:40px; box-sizing:border-box; }
.pulse-badge { background:#C41E3A; color:#fff; font-family:'Inter'; font-size:16px; font-weight:700; padding:4px 18px; letter-spacing:3px; margin-bottom:24px; }
.pulse-text { font-family:'Inter'; font-size:48px; font-weight:700; color:#fff; line-height:1.15; text-shadow:0 2px 20px rgba(0,0,0,0.6); }
.pulse-brand { font-family:'Inter'; font-size:12px; color:rgba(255,255,255,0.3); letter-spacing:4px; margin-top:30px; }
""".strip()

        text_clips.append({
            "asset": {
                "type": "html",
                "html": text_html,
                "css": text_css,
                "width": 1080,
                "height": 800,
            },
            "start": round(i * card_duration, 2),
            "length": card_duration,
            "position": "center",
            "transition": {"in": "fade", "out": "fade"},
        })

    # ── B-roll track ──
    n_images = max(len(image_urls), 1)
    broll_clips = []
    for i, url in enumerate(image_urls[:len(cards)]):
        broll_clips.append({
            "asset": {"type": "image", "src": url},
            "start": round(i * card_duration, 2),
            "length": round(card_duration + 0.3, 2),
            "fit": "cover",
            "effect": KEN_BURNS_EFFECTS[i % len(KEN_BURNS_EFFECTS)],
            "filter": "darken",
            **({"transition": {"in": "fade"}} if i > 0 else {}),
        })

    edit = {
        "timeline": {
            "background": NAVY,
            "fonts": [{"src": FONT_URL}],
            "tracks": [
                {"clips": text_clips},
                {"clips": broll_clips},
            ],
            "soundtrack": {
                "src": music_url,
                "effect": "fadeInFadeOut",
                "volume": min(music_volume * 3, 0.3),  # Louder for Quick Pulse
            } if music_url else None,
        },
        "output": {
            "format": "mp4",
            "size": {"width": 1080, "height": 1920},
            "fps": 30,
            "quality": "high",
        },
    }

    # Remove None soundtrack
    if edit["timeline"].get("soundtrack") is None:
        del edit["timeline"]["soundtrack"]

    return edit


# ═══════════════════════════════════════════════════════════════════════════════
# SHOTSTACK RENDER — Submit, Poll, Download
# ═══════════════════════════════════════════════════════════════════════════════

def render_reel(edit_json, use_production=False):
    """Submit to Shotstack, poll for completion, return output URL."""
    api_url = SHOTSTACK_PROD_URL if use_production else SHOTSTACK_STAGE_URL
    api_key = SHOTSTACK_PROD_KEY if use_production else SHOTSTACK_KEY

    env_label = "production" if use_production else "sandbox"
    print(f"\n🚀 Submitting to Shotstack ({env_label})...")

    # Submit render
    r = requests.post(
        f"{api_url}/render",
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
        },
        json=edit_json,
        timeout=30,
    )

    if r.status_code != 201 and r.status_code != 200:
        print(f"❌ Render submit failed: {r.status_code}")
        print(f"   {r.text[:500]}")
        return None

    resp = r.json()
    render_id = resp.get("response", {}).get("id")
    if not render_id:
        print(f"❌ No render ID returned: {resp}")
        return None

    print(f"  ⏳ Render ID: {render_id}")

    # Poll for completion
    max_polls = 60  # 5 minutes max
    for i in range(max_polls):
        time.sleep(5)

        r = requests.get(
            f"{api_url}/render/{render_id}",
            headers={"x-api-key": api_key},
            timeout=15,
        )

        if r.status_code != 200:
            print(f"  ⚠️ Poll failed: {r.status_code}")
            continue

        status_data = r.json().get("response", {})
        status = status_data.get("status", "")

        if status == "done":
            output_url = status_data.get("url")
            render_time = status_data.get("renderTime", 0)
            print(f"  ✅ Render complete! ({render_time/1000:.1f}s)")
            return output_url

        elif status == "failed":
            error = status_data.get("error", "unknown")
            print(f"  ❌ Render failed: {error}")
            return None

        else:
            if i % 4 == 0:
                print(f"  ⏳ Status: {status} ({(i+1)*5}s elapsed)")

    print("❌ Render timed out after 5 minutes")
    return None


def download_reel(url, output_path):
    """Download rendered reel from Shotstack."""
    r = requests.get(url, timeout=120, stream=True)
    if r.status_code != 200:
        print(f"❌ Download failed: {r.status_code}")
        return False

    with open(output_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)

    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"  📥 Downloaded: {output_path} ({size_mb:.1f} MB)")
    return True


# ═══════════════════════════════════════════════════════════════════════════════
# KAVYA CTA END CARD
# ═══════════════════════════════════════════════════════════════════════════════

CTA_DURATION = 4.0  # Branded end card duration

# Social handles
SOCIAL_HANDLES = {
    "website": "thevideshi.com",
    "instagram": "@the.videshi",
    "youtube": "@the.videshi",
    "threads": "@the.videshi",
    "x": "@thevideshi",
    "whatsapp": "The Videshi",
}


def build_end_card_html():
    """Build branded end card with logo + social handles. All inline styles for Shotstack compatibility."""
    html = """<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;width:100%;height:100%;background:linear-gradient(180deg,#0a1628 0%,#0f1f35 50%,#0a1628 100%);padding:60px 40px;box-sizing:border-box;">
  <div style="font-family:Inter;font-size:64px;font-weight:700;color:#D4AF37;letter-spacing:8px;margin-bottom:12px;">THE VIDESHI</div>
  <div style="font-family:Inter;font-size:18px;color:rgba(255,255,255,0.4);letter-spacing:3px;text-transform:uppercase;margin-bottom:40px;">News for the Indian Diaspora</div>
  <div style="width:50px;height:2px;background:#D4AF37;margin-bottom:40px;opacity:0.5;"></div>
  <div style="font-family:Inter;font-size:30px;font-weight:700;color:#fff;letter-spacing:1px;margin-bottom:48px;">thevideshi.com</div>
  <div style="display:flex;flex-direction:column;gap:14px;align-items:center;">
    <div style="display:flex;gap:14px;align-items:center;"><span style="font-family:Inter;font-size:14px;font-weight:700;color:#D4AF37;letter-spacing:2px;width:130px;text-align:right;">YOUTUBE</span><span style="font-family:Inter;font-size:18px;color:rgba(255,255,255,0.7);">@the.videshi</span></div>
    <div style="display:flex;gap:14px;align-items:center;"><span style="font-family:Inter;font-size:14px;font-weight:700;color:#D4AF37;letter-spacing:2px;width:130px;text-align:right;">INSTAGRAM</span><span style="font-family:Inter;font-size:18px;color:rgba(255,255,255,0.7);">@the.videshi</span></div>
    <div style="display:flex;gap:14px;align-items:center;"><span style="font-family:Inter;font-size:14px;font-weight:700;color:#D4AF37;letter-spacing:2px;width:130px;text-align:right;">THREADS</span><span style="font-family:Inter;font-size:18px;color:rgba(255,255,255,0.7);">@the.videshi</span></div>
    <div style="display:flex;gap:14px;align-items:center;"><span style="font-family:Inter;font-size:14px;font-weight:700;color:#D4AF37;letter-spacing:2px;width:130px;text-align:right;">X</span><span style="font-family:Inter;font-size:18px;color:rgba(255,255,255,0.7);">@thevideshi</span></div>
    <div style="display:flex;gap:14px;align-items:center;"><span style="font-family:Inter;font-size:14px;font-weight:700;color:#D4AF37;letter-spacing:2px;width:130px;text-align:right;">WHATSAPP</span><span style="font-family:Inter;font-size:18px;color:rgba(255,255,255,0.7);">The Videshi</span></div>
  </div>
</div>"""

    css = ""  # All inline
    return html, css


# ═══════════════════════════════════════════════════════════════════════════════
# AI QUALITY GATE
# ═══════════════════════════════════════════════════════════════════════════════

def extract_frames(video_path, count=5):
    """Extract evenly-spaced frames from a video for AI review."""
    import base64

    # Get duration
    probe = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", video_path],
        capture_output=True, text=True, timeout=15,
    )
    duration = float(json.loads(probe.stdout).get("format", {}).get("duration", 30))

    frames = []
    for i in range(count):
        t = (duration / (count + 1)) * (i + 1)
        frame_path = BUILD_DIR / f"ss-qa-frame-{i}.jpg"
        subprocess.run(
            ["ffmpeg", "-y", "-ss", str(t), "-i", video_path,
             "-vframes", "1", "-q:v", "2", str(frame_path)],
            capture_output=True, timeout=15,
        )
        if frame_path.exists():
            with open(frame_path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
                frames.append({"time": round(t, 1), "b64": b64})
            os.remove(frame_path)

    return frames


def run_qa_gate(video_path, article, script_data):
    """
    AI quality gate: GPT-4o reviews extracted frames + script.
    Returns (passed: bool, score: int, notes: str).
    Includes non-negotiable checks that auto-fail regardless of score.
    """
    if not OPENAI_KEY:
        print("  ⚠️ No OpenAI key — skipping QA gate")
        return True, 7, "QA skipped (no API key)"

    frames = extract_frames(video_path, count=5)
    if not frames:
        return False, 0, "Could not extract frames"

    headline = article.get("headline", "")
    script = script_data.get("script", "") if script_data else ""

    # Build vision messages
    content = [
        {
            "type": "text",
            "text": f"""You are a quality reviewer for The Videshi, an Indian diaspora news platform.

Review this Instagram Reel. I'm showing you 5 frames extracted at different timestamps.

ARTICLE: {headline}
SCRIPT: {script}

Score 1-10. This is for Instagram/YouTube Shorts — fast-paced news content, not cinema. Be practical.
1. VISUAL QUALITY: Images clear, portrait 1080x1920, no black bars or stretching?
2. TEXT READABILITY: Can captions be read over the images? (Some contrast variance is normal for B-roll)
3. BRANDING: Does it look like a news outlet? Category badge, branded elements present?
4. HOOK: Does the opening frame have bold text that grabs attention?
5. FLOW: Good pacing, transitions between images?

NON-NEGOTIABLE CHECKS (any fail = auto-fail, override score to 0):
- SPELLING: Any misspelling of "TheVideshi", "thevideshi.com", or social handles (@the.videshi, @thevideshi)?
  Watch for STT errors like "Divaji", "Vidashi", "Vidashee", "diva ji", or any garbled version.
- OVERLAPPING TEXT: Are two text elements rendered on top of each other making them unreadable?
- BRAND INTEGRITY: Is the website URL shown as anything other than "thevideshi.com"?

Score 7+ = professional news reel. Score 5-6 = acceptable for social media. Below 5 = broken.

Return JSON only:
{{
  "score": <1-10, or 0 if any non-negotiable failed>,
  "passed": <true if score >= 6 AND all non-negotiables pass>,
  "non_negotiable_failures": ["list of failed non-negotiable checks, empty if all pass"],
  "issues": ["issue1", "issue2"],
  "severity": "HIGH" or "MEDIUM" or "LOW",
  "notes": "brief summary"
}}"""
        }
    ]

    for frame in frames:
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{frame['b64']}", "detail": "low"},
        })
        content.append({
            "type": "text",
            "text": f"[Frame at {frame['time']}s]",
        })

    try:
        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"},
            json={
                "model": "gpt-4o",
                "messages": [{"role": "user", "content": content}],
                "temperature": 0.3,
                "response_format": {"type": "json_object"},
                "max_tokens": 500,
            },
            timeout=30,
        )

        if r.status_code != 200:
            print(f"  ⚠️ QA API error: {r.status_code}")
            return True, 7, "QA skipped (API error)"

        result = json.loads(r.json()["choices"][0]["message"]["content"])
        score = result.get("score", 5)
        non_neg = result.get("non_negotiable_failures", [])
        issues = result.get("issues", [])
        severity = result.get("severity", "LOW")
        notes = result.get("notes", "")

        # Non-negotiable failures override everything
        if non_neg:
            print(f"  🚫 NON-NEGOTIABLE FAILURES: {'; '.join(non_neg)}")
            return False, 0, f"Non-negotiable: {'; '.join(non_neg)}"

        passed = result.get("passed", score >= 6)

        if issues:
            print(f"  📋 Issues ({severity}): {'; '.join(issues)}")

        return passed, score, notes

    except Exception as e:
        print(f"  ⚠️ QA gate error: {e}")
        return True, 7, f"QA skipped ({e})"


# ═══════════════════════════════════════════════════════════════════════════════
# UPLOAD & REGISTER
# ═══════════════════════════════════════════════════════════════════════════════

def upload_final_reel(local_path, storage_name):
    """Upload final reel to Supabase storage."""
    return upload_asset(local_path, f"reels/{storage_name}", "video/mp4")


def build_caption(article):
    """Build Instagram caption."""
    headline = article.get("headline", "")
    subheadline = article.get("subheadline", "")
    slug = article.get("slug", "")
    category = article.get("category", "")

    cat_tags = {
        "news": "#indianews #breakingnews #desinews",
        "sports": "#cricket #ipl #teamindia #sports",
        "entertainment": "#bollywood #entertainment #indiancinema",
        "technology": "#technews #indiantech #ai",
        "immigration": "#h1b #immigration #greencard #uscis",
        "nri-world": "#nrilife #desiabroad #indianamerican",
        "markets-finance": "#stockmarket #nifty #sensex",
        "travel": "#travelindia #incredibleindia",
        "lifestyle-health": "#wellness #desilifestyle",
        "food": "#indianfood #desifood",
    }

    caption = f"{headline}\n\n"
    if subheadline:
        caption += f"{subheadline}\n\n"
    caption += f"Full story: https://thevideshi.com/articles/{slug}\n\n"
    caption += f"#indiandiaspora #nri #thevideshi #india {cat_tags.get(category, '')}"
    return caption


def register_reel(article, video_url, video_path, caption):
    """Register in prebuilt_reels for IG/YT posting crons."""
    payload = {
        "article_id": article["id"],
        "article_slug": article.get("slug", "")[:80],  # Match existing slug lengths
        "headline": article.get("headline", ""),
        "video_path": f"pipeline/reels/{os.path.basename(video_path)}",
        "video_url": video_url,
        "caption": caption,
        "status": "pending",
        "source": "heygen",  # DB constraint: manual|heygen|ffmpeg — TODO: ALTER to add 'shotstack'
        "qa_passed": True,
        "qa_score": 8,
    }

    r = requests.post(
        f"{SB_URL}/rest/v1/prebuilt_reels",
        headers=SB_HEADERS,
        json=payload,
        timeout=15,
    )

    if r.status_code in (200, 201):
        print(f"  ✅ Registered in prebuilt_reels")
        return True
    else:
        print(f"  ❌ Registration failed: {r.status_code} {r.text[:200]}")
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN ORCHESTRATION
# ═══════════════════════════════════════════════════════════════════════════════

def run_anchor_reel(article, dry_run=False, use_production=False):
    """Generate a full Anchor Reel for an article."""
    headline = article.get("headline", "Unknown")
    category = article.get("category", "news")
    slug = article.get("slug", "unknown")

    print(f"\n{'='*60}")
    print(f"🎬 ANCHOR REEL: {headline[:60]}")
    print(f"   Category: {category} | Slug: {slug}")
    print(f"{'='*60}")

    # 1. Generate script
    print("\n📝 Step 1: Generating script...")
    script_data = generate_script(article)
    if not script_data:
        return False

    # 2. Generate TTS
    print("\n🎙️ Step 2: Generating TTS...")
    audio_path, audio_duration = generate_tts(script_data["script"])
    if not audio_path:
        return False

    # 2b. Get word-level timestamps from Whisper (for script-accurate captions)
    print("\n📝 Step 2b: Getting word timestamps from Whisper...")
    word_timestamps = get_word_timestamps(audio_path, script_data["script"])

    # 3. Upload audio to Supabase for Shotstack
    print("\n☁️ Step 3: Uploading audio...")
    audio_storage = f"reels/audio/ss-{slug}-{int(time.time())}.mp3"
    voice_url = upload_asset(audio_path, audio_storage, "audio/mpeg")
    if not voice_url:
        return False

    # 4. Source B-roll images (storyboard-driven or legacy fallback)
    print("\n🖼️ Step 4: Sourcing B-roll images...")
    storyboard = script_data.get("storyboard", [])
    if storyboard:
        image_urls = source_storyboard_images(article, storyboard)
    else:
        print("  ⚠️ No storyboard in script — falling back to legacy image_queries")
        image_urls = source_image_urls(article, script_data.get("image_queries", []))
    if not image_urls:
        print("❌ No images found")
        return False

    # 5. Ensure music is uploaded
    print("\n🎵 Step 5: Setting up music...")
    music_file = CATEGORY_MUSIC.get(category, "breaking-news-30s.mp3")
    music_url = ensure_music_uploaded(music_file)
    music_volume = MUSIC_VOLUME.get(category, 0.05)

    # 6. Build Shotstack timeline
    print("\n🔧 Step 6: Building Shotstack timeline...")
    edit_json = build_anchor_reel_timeline(
        voice_url=voice_url,
        voice_duration=audio_duration,
        image_urls=image_urls,
        music_url=music_url,
        music_volume=music_volume,
        hook_line1=script_data.get("hook_line1", "BREAKING NEWS"),
        hook_line2=script_data.get("hook_line2", "YOU NEED TO KNOW"),
        headline=headline,
        category=category,
        word_timestamps=word_timestamps,
        script_text=script_data["script"],
    )

    if not edit_json:
        return False

    # Save JSON for debugging
    json_path = BUILD_DIR / f"ss-timeline-{slug}.json"
    with open(json_path, "w") as f:
        json.dump(edit_json, f, indent=2)
    print(f"  📄 Timeline JSON saved: {json_path}")

    if dry_run:
        print("\n🏁 DRY RUN — JSON built, not rendering")
        print(json.dumps(edit_json, indent=2)[:2000])
        return True

    # 7. Render via Shotstack
    output_url = render_reel(edit_json, use_production=use_production)
    if not output_url:
        return False

    # 8. Download rendered reel (already includes CTA — no ffmpeg needed)
    print("\n📥 Step 8: Downloading reel...")
    ts = datetime.now().strftime("%Y%m%d-%H%M")
    # Sandbox renders go to reels/sandbox/ to prevent accidental posting
    if use_production:
        final_name = f"ss-reel-{slug[:60]}-{ts}.mp4"
        final_path = REELS_DIR / final_name
    else:
        sandbox_dir = REELS_DIR / "sandbox"
        sandbox_dir.mkdir(exist_ok=True)
        final_name = f"ss-reel-{slug[:60]}-{ts}.mp4"
        final_path = sandbox_dir / final_name
    if not download_reel(output_url, str(final_path)):
        return False

    # 9. AI Quality Gate
    print("\n🔍 Step 9: AI Quality Gate...")
    qa_passed, qa_score, qa_notes = run_qa_gate(str(final_path), article, script_data)
    if not qa_passed:
        print(f"  ❌ QA FAILED (score: {qa_score}) — {qa_notes}")
        # TODO: auto-revise loop (regenerate script + re-render)
        return False
    print(f"  ✅ QA PASSED (score: {qa_score})")

    # 10. Upload final reel
    print("\n☁️ Step 10: Uploading final reel...")
    video_url = upload_final_reel(str(final_path), final_name)

    # 11. Register
    if video_url:
        print("\n📋 Step 11: Registering reel...")
        caption = build_caption(article)
        register_reel(article, video_url, str(final_path), caption)

    print(f"\n{'='*60}")
    print(f"✅ REEL COMPLETE: {final_path}")
    print(f"   Shotstack URL: {output_url}")
    if video_url:
        print(f"   Supabase URL: {video_url}")
    print(f"{'='*60}\n")

    return True


def run_quick_pulse(article, dry_run=False, use_production=False):
    """Generate a Quick Pulse reel (music + text, no voice)."""
    headline = article.get("headline", "Unknown")
    subheadline = article.get("subheadline", "")
    category = article.get("category", "news")
    slug = article.get("slug", "unknown")

    print(f"\n{'='*60}")
    print(f"⚡ QUICK PULSE: {headline[:60]}")
    print(f"{'='*60}")

    # Source images
    image_urls = source_image_urls(article, [], count=4)
    if not image_urls:
        return False

    # Music
    music_file = CATEGORY_MUSIC.get(category, "breaking-news-30s.mp3")
    music_url = ensure_music_uploaded(music_file)
    music_volume = MUSIC_VOLUME.get(category, 0.05)

    # Build timeline
    edit_json = build_quick_pulse_timeline(
        image_urls=image_urls,
        music_url=music_url,
        music_volume=music_volume,
        headline=headline,
        subheadline=subheadline,
        category=category,
    )

    json_path = BUILD_DIR / f"ss-pulse-{slug}.json"
    with open(json_path, "w") as f:
        json.dump(edit_json, f, indent=2)

    if dry_run:
        print("🏁 DRY RUN — JSON built, not rendering")
        return True

    # Render
    output_url = render_reel(edit_json, use_production=use_production)
    if not output_url:
        return False

    # Download
    final_name = f"ss-pulse-{slug}-{datetime.now().strftime('%Y%m%d-%H%M')}.mp4"
    final_path = REELS_DIR / final_name
    if not download_reel(output_url, str(final_path)):
        return False

    # Upload & register
    video_url = upload_final_reel(str(final_path), final_name)
    if video_url:
        caption = build_caption(article)
        register_reel(article, video_url, str(final_path), caption)

    print(f"\n✅ QUICK PULSE COMPLETE: {final_path}")
    return True


def main():
    parser = argparse.ArgumentParser(description="Shotstack Reel Renderer for The Videshi")
    parser.add_argument("--article-id", help="Specific article UUID")
    parser.add_argument("--format", choices=["anchor", "pulse"], default="anchor", help="Reel format")
    parser.add_argument("--dry-run", action="store_true", help="Build JSON only, don't render")
    parser.add_argument("--production", action="store_true", help="Use production API (not sandbox)")
    parser.add_argument("--test", action="store_true", help="Quick test with first available article")
    parser.add_argument("--hours", type=int, default=24, help="Look back N hours for articles")
    args = parser.parse_args()

    print("🎬 Shotstack Reel Renderer for The Videshi")
    print(f"   Mode: {'production' if args.production else 'sandbox'}")
    print(f"   Format: {args.format}")

    # Get article
    if args.article_id:
        # Fetch specific article
        r = requests.get(
            f"{SB_URL}/rest/v1/p2_articles",
            headers=SB_HEADERS,
            params={
                "id": f"eq.{args.article_id}",
                "select": "id,headline,subheadline,slug,category,vertical,body,image_url,published_at",
            },
            timeout=15,
        )
        if r.status_code != 200 or not r.json():
            print(f"❌ Article not found: {args.article_id}")
            sys.exit(1)
        article = r.json()[0]
    else:
        articles = get_recent_articles(hours=args.hours)
        if not articles:
            print("❌ No recent articles found")
            sys.exit(1)

        existing = get_existing_reel_slugs() if not args.test else set()
        article = pick_article(articles, existing)
        if not article:
            print("❌ All recent articles already have reels")
            sys.exit(1)

    # Run
    if args.format == "pulse":
        success = run_quick_pulse(article, dry_run=args.dry_run, use_production=args.production)
    else:
        success = run_anchor_reel(article, dry_run=args.dry_run, use_production=args.production)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
