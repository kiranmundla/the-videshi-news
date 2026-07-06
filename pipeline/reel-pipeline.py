#!/usr/bin/env python3
"""
Unified Reel + Carousel Pipeline for The Videshi
================================================

One script: article ID → storyboard → images → reel → carousel → distribute.

Usage:
    python3 reel-pipeline.py --article-id <UUID>
    python3 reel-pipeline.py --article-id <UUID> --manual-images /path/to/dir/
    python3 reel-pipeline.py --article-id <UUID> --skip-distribute
    python3 reel-pipeline.py --article-id <UUID> --carousel-only

Env files sourced:
    ~/workspace/.env.supabase, .env.openai, .env.heygen, .env.youtube
    pipeline/.env.shotstack
"""

import argparse, json, os, re, subprocess, sys, time, hashlib
from pathlib import Path

# ── Load environment ──
def load_env(path):
    path = os.path.expanduser(path)
    if not os.path.exists(path):
        return {}
    env = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                v = v.strip().strip("'\"")
                env[k] = v
                os.environ[k] = v
    return env

ENV_FILES = [
    "~/workspace/.env.supabase",
    "~/workspace/.env.openai",
    "~/workspace/.env.heygen",
    "~/workspace/.env.youtube",
    "~/workspace/.env.google-ai",
]
for ef in ENV_FILES:
    load_env(ef)

# Shotstack env is in pipeline dir
PIPELINE_DIR = os.path.dirname(os.path.abspath(__file__))
load_env(os.path.join(PIPELINE_DIR, ".env.shotstack"))

import requests
from PIL import Image, ImageDraw, ImageFont

# ── Constants ──
SB_URL = os.environ.get("SUPABASE_URL", "")
SB_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
SB_HEADERS = {"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"}
OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "")
HEYGEN_KEY = os.environ.get("HEYGEN_API_KEY", "")
SHOTSTACK_KEY = os.environ.get("SHOTSTACK_PRODUCTION_KEY", "")
STORAGE_BASE = f"{SB_URL}/storage/v1/object/public/article-images"

TTS_VOICE = "cb9diBQeYWIGJS9i52kX"  # HeyGen Indian Anchorwoman
ENDCARD_URL = f"{STORAGE_BASE}/branding/endcard-v2.png"
LOGO_URL = f"{STORAGE_BASE}/branding/logo-512.png"
LOGO_LOCAL = os.path.join(PIPELINE_DIR, "..", "public", "logo-512.png")

FONT_BOLD = "/usr/share/fonts/truetype/inter/Inter-Bold.ttf"
FONT_HEAVY = "/usr/share/fonts/truetype/inter/Inter-ExtraBold.ttf"

# Pre-recorded endcard CTA - reused for all reels
ENDCARD_CTA_TEXT = "For the full story, follow us at The Videshi dot com."
ENDCARD_CTA_STORAGE = "branding/endcard-cta-vo.mp3"


# ═══════════════════════════════════════════════════════════════
# AUTO-PICK: Select best article for reel generation
# ═══════════════════════════════════════════════════════════════
def auto_pick_article():
    """Pick a recent published article that doesn't already have a reel."""
    print(f"\n{'='*60}")
    print(f"AUTO-PICK: Finding best article for reel...")
    print(f"{'='*60}")
    
    # Priority categories (from editorial strategy)
    priority_cats = ["immigration", "entertainment", "technology", "markets-finance", "nri-world", "news"]
    
    # Get recent published articles (last 48h)
    r = requests.get(
        f"{SB_URL}/rest/v1/p2_articles?select=id,headline,slug,category,published_at"
        f"&status=eq.published&order=published_at.desc&limit=30",
        headers=SB_HEADERS, timeout=15
    )
    if r.status_code != 200 or not r.json():
        print("  ❌ No articles found")
        return None
    
    articles = r.json()
    
    # Get existing reels to avoid duplicates
    r2 = requests.get(
        f"{SB_URL}/rest/v1/prebuilt_reels?select=article_id&order=created_at.desc&limit=50",
        headers=SB_HEADERS, timeout=15
    )
    existing_ids = set()
    if r2.status_code == 200 and r2.json():
        existing_ids = {r["article_id"] for r in r2.json() if r.get("article_id")}
    
    # Score and pick
    for cat in priority_cats:
        for art in articles:
            if art["id"] not in existing_ids and art.get("category") == cat:
                print(f"  ✅ Picked: [{cat}] {art['headline'][:60]}...")
                return art["id"]
    
    # Fallback: any article without a reel
    for art in articles:
        if art["id"] not in existing_ids:
            print(f"  ✅ Picked: [{art.get('category','?')}] {art['headline'][:60]}...")
            return art["id"]
    
    print("  ⚠️ All recent articles already have reels")
    return None


# ═══════════════════════════════════════════════════════════════
# PHASE 1: Fetch article
# ═══════════════════════════════════════════════════════════════
def fetch_article(article_id):
    print(f"\n{'='*60}")
    print(f"PHASE 1: Fetching article {article_id[:8]}...")
    print(f"{'='*60}")
    
    cols = "id,headline,subheadline,slug,category,body,image_url"
    r = requests.get(
        f"{SB_URL}/rest/v1/p2_articles?id=eq.{article_id}&select={cols}",
        headers=SB_HEADERS, timeout=15
    )
    if r.status_code != 200 or not r.json():
        print(f"❌ Article not found: {r.status_code}")
        sys.exit(1)
    
    article = r.json()[0]
    print(f"  ✅ {article['headline'][:80]}")
    return article


# ═══════════════════════════════════════════════════════════════
# PHASE 2: Generate storyboard
# ═══════════════════════════════════════════════════════════════
def generate_storyboard(article):
    print(f"\n{'='*60}")
    print(f"PHASE 2: Generating storyboard...")
    print(f"{'='*60}")
    
    body_text = article.get("body", "")[:4000]
    
    prompt = f"""You are a video producer for The Videshi, an Indian diaspora news platform.

Create a short-form video storyboard (25-35 seconds total voiceover) for this article.

ARTICLE:
Headline: {article['headline']}
Subheadline: {article.get('subheadline', '')}
Body: {body_text}

OUTPUT FORMAT (JSON):
{{
    "scenes": [
        {{
            "voiceover": "spoken text for this scene (punchy, conversational)",
            "onscreen": "SHORT HEADLINE (2-5 words, scene topic)",
            "image_prompt": "VERY detailed, self-contained image generation prompt (see rules below)"
        }}
    ]
}}

IMAGE PROMPT RULES — THIS IS CRITICAL:
The image prompts will be pasted into ChatGPT by someone who does NOT have the article.
Each prompt must be completely SELF-CONTAINED with all the context needed to generate the right image.

FIRST, decide the visual approach based on the article content:

**DATA-CENTRIC articles** (immigration policy, visa bulletins, market moves, financial analysis, statistics-heavy stories, policy comparisons):
Use RICH INFOGRAPHIC-STYLE prompts. These should produce broadcast-quality data cards — the kind you'd see on CNN, Bloomberg, or The Economist's video desk.
Each image_prompt MUST:
- Start with: "Create a single vertical 9:16 broadcast-quality infographic card."
- Describe a SPECIFIC data visualization: a comparison table with colored header rows and highlighted cells, a trend line chart with labeled axes, a horizontal bar chart with color-coded categories, a stat callout with icons, a before/after comparison, a breakdown panel with icon-text pairs
- Keep each scene visually clean — don't overload a single frame with too many numbers. A viewer should absorb the key takeaway in a few seconds on a phone
- Include the EXACT real numbers, dates, categories, and labels from the article — bake all data INTO the prompt
- Describe the visual style in detail:
  * Deep navy/dark blue background with subtle gradient or texture
  * Bold white title text with colored subtitle (gold or yellow)
  * Red or orange highlights for critical/alarming data points
  * Rounded-corner cards or panels for grouping related info
  * Professional icons next to key points (use descriptive icon concepts like "hourglass icon", "warning icon", "chart icon")
  * Subtle background imagery where it adds context (e.g. a faded Statue of Liberty for immigration, a faded stock chart for markets) — NOT the main focus, just atmosphere
  * Source attribution at the bottom when citing official data
  * Scene number badge in the top-left corner (e.g. a red rounded square with the scene number)
- End with: "Style: broadcast-quality news infographic, CNN/Bloomberg data card aesthetic, rich gradients, professional iconography, bold hierarchy, crisp typography, high production value. Vertical 9:16 phone format."
- Mix different visualization types across scenes: one data table, one trend chart, one icon-explanation panel, one bar chart, one big stat callout — each scene visually distinct and telling a different part of the story

Example of a GOOD data-centric prompt:
"Create a single vertical 9:16 broadcast-quality infographic card. Title: 'JULY 2026 VISA BULLETIN' in bold white, subtitle 'EMPLOYMENT-BASED FINAL ACTION DATES' in gold. Below, a clean data table with a blue header row showing columns: Category, All Chargeability Areas Except India, India. Rows: EB-1 (15MAY23, 15MAY23), EB-2 row highlighted in RED (15JAN23, UNAVAILABLE in bold red text), EB-3 (01JAN13, 01NOV12), EB-3 Other Workers (01NOV20, 01JUN16), EB-5 Unreserved (01APR22, 01JAN22). Deep navy background with subtle American flag texture. U.S. Department of State seal icon next to source attribution 'Source: U.S. Department of State — Visa Bulletin July 2026' at the bottom. Scene number '2' in a red badge top-left corner. Style: broadcast-quality news infographic, CNN/Bloomberg data card aesthetic, rich gradients, professional iconography, bold hierarchy, crisp typography, high production value. Vertical 9:16 phone format."

**NARRATIVE articles** (human interest, entertainment, travel, profiles, events):
Use PHOTOGRAPHIC prompts as before.
Each image_prompt MUST:
- Start with: "Create a single cinematic vertical 9:16 news photograph."
- Include 3-5 sentences of RICH, SPECIFIC visual description — exact subjects, environments, objects, compositions, camera angles, lighting
- Reference CONCRETE details from the article (specific numbers, real places, real concepts, real institutions) — bake the article knowledge INTO the prompt
- Specify atmosphere/mood in the description
- End with: "Style: BBC documentary photography, Reuters editorial realism, ultra realistic, cinematic lighting, professional DSLR, dramatic scale, emotional storytelling. No text. No captions. No logos. No watermarks. No graphics. Single standalone image only."

**HYBRID**: Many articles benefit from MIXING both approaches. For a data-centric article, open with a dramatic hook card (bold headline + subtle background imagery + key impact bullets), then show data panels, then close with a "what this means" or "bigger picture" panel. Use your judgment based on the article content.

ACROSS ALL APPROACHES:
- Each scene must be visually COMPLETELY DIFFERENT from every other scene
- Each scene should carry different information and a different visual rendering — do NOT repeat information across scenes
- Reference CONCRETE details from the article

Example of a BAD prompt:
"A concerned Indian professional looking at documents, dramatic lighting" — TOO VAGUE, no context, no specifics.

STORYBOARD RULES:
- 6-8 scenes total
- Scene 0 must be a HOOK question that grabs attention
- Last scene should be a thought-provoking closing
- Total voiceover: 100-120 words (25-35 seconds)
- Each scene voiceover: 10-20 words
- Focus on the DIASPORA angle — how this affects Indians abroad
- On-screen text: 2-5 words, uppercase topic label

Return ONLY valid JSON, no markdown."""

    r = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"},
        json={
            "model": "gpt-4o",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "response_format": {"type": "json_object"}
        },
        timeout=60
    )
    
    if r.status_code != 200:
        print(f"❌ Storyboard generation failed: {r.status_code}")
        sys.exit(1)
    
    result = json.loads(r.json()["choices"][0]["message"]["content"])
    scenes = result["scenes"]
    
    total_words = sum(len(s["voiceover"].split()) for s in scenes)
    print(f"  ✅ {len(scenes)} scenes, {total_words} words (~{total_words * 0.35:.0f}s)")
    for i, s in enumerate(scenes):
        print(f"     Scene {i}: [{s['onscreen']}] {s['voiceover'][:60]}...")
    
    return scenes


# ═══════════════════════════════════════════════════════════════
# PHASE 3: Generate scene images
# ═══════════════════════════════════════════════════════════════
def generate_images_api(scenes, article_id, build_dir):
    """Generate images via OpenAI gpt-image-1 API."""
    print(f"\n{'='*60}")
    print(f"PHASE 3: Generating images (OpenAI API)...")
    print(f"{'='*60}")
    
    storage_prefix = f"reel-gen/{article_id}"
    
    for i, scene in enumerate(scenes):
        print(f"  Scene {i}: generating...")
        
        r = requests.post(
            "https://api.openai.com/v1/images/generations",
            headers={"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"},
            json={
                "model": "gpt-image-1",
                "prompt": scene.get("image_prompt", scene.get("scene_focus", "")),
                "n": 1,
                "size": "1024x1536",  # portrait
                "quality": "high"
            },
            timeout=120
        )
        
        if r.status_code != 200:
            error_msg = r.text[:200]
            if "safety" in error_msg.lower() or "content_policy" in error_msg.lower():
                print(f"  ⚠️  Scene {i} blocked by safety filter")
                print(f"     Prompt: {scene.get('image_prompt', scene.get('scene_focus', ''))[:100]}...")
                print(f"     → Use --manual-images to provide this scene")
                scene["image_url"] = None
                continue
            else:
                print(f"  ❌ Image gen failed: {r.status_code} {error_msg}")
                scene["image_url"] = None
                continue
        
        # Download and upload to Supabase
        img_data_b64 = r.json()["data"][0].get("b64_json")
        if img_data_b64:
            import base64
            img_bytes = base64.b64decode(img_data_b64)
        else:
            img_url = r.json()["data"][0]["url"]
            img_bytes = requests.get(img_url, timeout=30).content
        
        # Save locally
        local_path = f"{build_dir}/scene-{i}.jpg"
        with open(local_path, "wb") as f:
            f.write(img_bytes)
        
        # Upload to Supabase
        storage_path = f"{storage_prefix}/scene-{i}.jpg"
        up = requests.post(
            f"{SB_URL}/storage/v1/object/article-images/{storage_path}",
            headers={**SB_HEADERS, "Content-Type": "image/jpeg", "x-upsert": "true"},
            data=img_bytes, timeout=30
        )
        
        scene["image_url"] = f"{STORAGE_BASE}/{storage_path}"
        print(f"  ✅ Scene {i}: uploaded ({len(img_bytes)//1024}KB)")
    
    # Check for missing images
    missing = [i for i, s in enumerate(scenes) if not s.get("image_url")]
    if missing:
        print(f"\n  ⚠️  {len(missing)} scenes need manual images: {missing}")
        print(f"     Re-run with: --manual-images /path/to/images/")
        return False
    
    return True


def watermark_image(img_path, logo_path=None):
    """Add Videshi logo watermark to top-right corner of an image."""
    from PIL import Image
    
    if logo_path is None:
        logo_path = os.path.expanduser("~/workspace/the-videshi-news/public/logo-512.png")
    
    if not os.path.exists(logo_path):
        print(f"  ⚠️  Logo not found at {logo_path}, skipping watermark")
        return img_path
    
    img = Image.open(img_path).convert("RGBA")
    logo = Image.open(logo_path).convert("RGBA")
    
    # Size logo to ~8% of image width
    logo_size = int(img.width * 0.08)
    logo = logo.resize((logo_size, logo_size), Image.LANCZOS)
    
    # Make semi-transparent (70% opacity)
    logo_data = logo.getdata()
    new_data = [(r, g, b, int(a * 0.7)) for r, g, b, a in logo_data]
    logo.putdata(new_data)
    
    # Position: top-right corner with padding
    padding = int(img.width * 0.03)
    x = img.width - logo_size - padding
    y = padding
    
    # Paste with transparency
    img.paste(logo, (x, y), logo)
    
    # Save back as RGB (for JPEG)
    out = img.convert("RGB")
    out.save(img_path, "JPEG", quality=92)
    return img_path


def load_manual_images(scenes, image_dir, article_id):
    """Load manually provided images (from ChatGPT)."""
    print(f"\n{'='*60}")
    print(f"PHASE 3: Loading manual images from {image_dir}")
    print(f"{'='*60}")
    
    storage_prefix = f"reel-gen/{article_id}"
    image_files = sorted([f for f in os.listdir(image_dir) 
                         if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))])
    
    if len(image_files) < len(scenes):
        print(f"❌ Need {len(scenes)} images, found {len(image_files)}")
        sys.exit(1)
    
    for i, scene in enumerate(scenes):
        img_path = os.path.join(image_dir, image_files[i])
        
        # Watermark with Videshi logo
        watermark_image(img_path)
        
        with open(img_path, "rb") as f:
            img_bytes = f.read()
        
        storage_path = f"{storage_prefix}/manual-scene-{i}.jpg"
        up = requests.post(
            f"{SB_URL}/storage/v1/object/article-images/{storage_path}",
            headers={**SB_HEADERS, "Content-Type": "image/jpeg", "x-upsert": "true"},
            data=img_bytes, timeout=30
        )
        
        scene["image_url"] = f"{STORAGE_BASE}/{storage_path}"
        print(f"  ✅ Scene {i}: {image_files[i]} → watermarked + uploaded")
    
    return True


# ═══════════════════════════════════════════════════════════════
# PHASE 4: TTS (HeyGen Indian Anchorwoman)
# ═══════════════════════════════════════════════════════════════
def generate_tts(scenes, article_id, build_dir):
    """Generate voiceover via HeyGen."""
    print(f"\n{'='*60}")
    print(f"PHASE 4: Generating TTS...")
    print(f"{'='*60}")
    
    # Combine all scene voiceovers
    full_text = " ".join(s["voiceover"] for s in scenes)
    
    # Acronym expansion
    acronym_map = {
        "NRI": "N.R.I.", "NRIs": "N.R.I.s", "H-1B": "H-1-B",
        "UAE": "U.A.E.", "UK": "U.K.", "US": "U.S.",
        "AI": "A.I.", "CEO": "C.E.O.",
    }
    for acr, exp in acronym_map.items():
        full_text = re.sub(r'\b' + re.escape(acr) + r'\b', exp, full_text)
    
    # Generate main voiceover
    for attempt in range(3):
        try:
            r = requests.post(
                f"https://api.heygen.com/v2/voices/{TTS_VOICE}/preview",
                headers={"X-Api-Key": HEYGEN_KEY, "Content-Type": "application/json"},
                json={"text": full_text, "voice_id": TTS_VOICE, "text_type": "text"},
                timeout=60
            )
            break
        except requests.exceptions.ReadTimeout:
            if attempt < 2:
                print(f"  ⏳ TTS timeout (attempt {attempt+1}/3)...")
                time.sleep(3)
            else:
                print("❌ HeyGen TTS timed out")
                sys.exit(1)
    
    if r.status_code != 200:
        print(f"❌ TTS failed: {r.status_code} {r.text[:200]}")
        sys.exit(1)
    
    data = r.json().get("data", {})
    audio_url = data.get("audio_url")
    duration = data.get("duration", 0)
    
    # Download WAV
    wav_path = f"{build_dir}/voiceover.wav"
    subprocess.run(["curl", "-sS", "-o", wav_path, audio_url], check=True)
    
    # Convert to MP3 with loudnorm
    mp3_path = f"{build_dir}/voiceover.mp3"
    subprocess.run([
        "ffmpeg", "-y", "-i", wav_path,
        "-af", "loudnorm=I=-11:TP=-1.0:LRA=11",
        "-ar", "44100", "-b:a", "192k", mp3_path
    ], check=True, capture_output=True)
    
    # Get actual duration
    dur = float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", mp3_path],
        capture_output=True, text=True
    ).stdout.strip())
    
    # Upload to Supabase
    storage_path = f"reel-gen/{article_id}/voiceover.mp3"
    with open(mp3_path, "rb") as f:
        requests.post(
            f"{SB_URL}/storage/v1/object/article-images/{storage_path}",
            headers={**SB_HEADERS, "Content-Type": "audio/mpeg", "x-upsert": "true"},
            data=f.read(), timeout=30
        )
    
    vo_url = f"{STORAGE_BASE}/{storage_path}"
    print(f"  ✅ Voiceover: {dur:.1f}s")
    
    return vo_url, dur, mp3_path


def ensure_endcard_cta():
    """Generate endcard CTA voiceover once, reuse forever."""
    cta_url = f"{STORAGE_BASE}/{ENDCARD_CTA_STORAGE}"
    
    # Check if already exists
    r = requests.head(cta_url, timeout=10)
    if r.status_code == 200:
        return cta_url, 3.3  # Known duration
    
    print("  Generating endcard CTA (one-time)...")
    r = requests.post(
        f"https://api.heygen.com/v2/voices/{TTS_VOICE}/preview",
        headers={"X-Api-Key": HEYGEN_KEY, "Content-Type": "application/json"},
        json={"text": ENDCARD_CTA_TEXT, "voice_id": TTS_VOICE, "text_type": "text"},
        timeout=60
    )
    
    if r.status_code != 200:
        print(f"  ⚠️ Endcard CTA generation failed, continuing without")
        return None, 0
    
    audio_url = r.json()["data"]["audio_url"]
    
    wav_path = "/tmp/endcard_cta.wav"
    mp3_path = "/tmp/endcard_cta.mp3"
    subprocess.run(["curl", "-sS", "-o", wav_path, audio_url], check=True)
    subprocess.run([
        "ffmpeg", "-y", "-i", wav_path,
        "-af", "loudnorm=I=-11:TP=-1.0:LRA=11",
        "-ar", "44100", "-b:a", "192k", mp3_path
    ], check=True, capture_output=True)
    
    dur = float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", mp3_path],
        capture_output=True, text=True
    ).stdout.strip())
    
    with open(mp3_path, "rb") as f:
        requests.post(
            f"{SB_URL}/storage/v1/object/article-images/{ENDCARD_CTA_STORAGE}",
            headers={**SB_HEADERS, "Content-Type": "audio/mpeg", "x-upsert": "true"},
            data=f.read(), timeout=30
        )
    
    return cta_url, dur


# ═══════════════════════════════════════════════════════════════
# PHASE 5: Whisper word timestamps
# ═══════════════════════════════════════════════════════════════
def get_word_timestamps(mp3_path, build_dir):
    """Get word-level timestamps via Whisper API."""
    print(f"\n{'='*60}")
    print(f"PHASE 5: Word timestamps (Whisper)...")
    print(f"{'='*60}")
    
    with open(mp3_path, "rb") as f:
        r = requests.post(
            "https://api.openai.com/v1/audio/transcriptions",
            headers={"Authorization": f"Bearer {OPENAI_KEY}"},
            files={"file": ("voiceover.mp3", f, "audio/mpeg")},
            data={"model": "whisper-1", "response_format": "verbose_json",
                  "timestamp_granularities[]": "word"},
            timeout=60
        )
    
    if r.status_code != 200:
        print(f"❌ Whisper failed: {r.status_code}")
        sys.exit(1)
    
    result = r.json()
    words = result.get("words", [])
    
    with open(f"{build_dir}/whisper.json", "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"  ✅ {len(words)} words timestamped")
    return words


# ═══════════════════════════════════════════════════════════════
# PHASE 6: Music selection
# ═══════════════════════════════════════════════════════════════
def select_music(article, build_dir):
    """Select and upload background music."""
    print(f"\n{'='*60}")
    print(f"PHASE 6: Selecting music...")
    print(f"{'='*60}")
    
    # Import local music selector
    sys.path.insert(0, os.path.join(PIPELINE_DIR, "music"))
    try:
        from music_selector import select_music as _select
        result = _select(
            category=article.get("category", "news"),
            article_id=article["id"],
            index_path=os.path.join(PIPELINE_DIR, "music", "music-index.json")
        )
        music_path = result["path"]
        attribution = result.get("attribution", "")
    except Exception as e:
        print(f"  ⚠️ Music selector failed ({e}), using default")
        # Fallback: pick first available track
        music_dir = os.path.join(PIPELINE_DIR, "music")
        tracks = [f for f in os.listdir(music_dir) if f.endswith(".mp3")]
        if tracks:
            music_path = os.path.join(music_dir, tracks[0])
            attribution = ""
        else:
            print("  ❌ No music found")
            return None, ""
    
    # Upload music
    music_name = os.path.basename(music_path)
    storage_path = f"reel-gen/{article['id']}/music-{music_name}"
    with open(music_path, "rb") as f:
        requests.post(
            f"{SB_URL}/storage/v1/object/article-images/{storage_path}",
            headers={**SB_HEADERS, "Content-Type": "audio/mpeg", "x-upsert": "true"},
            data=f.read(), timeout=30
        )
    
    music_url = f"{STORAGE_BASE}/{storage_path}"
    print(f"  ✅ {os.path.basename(music_path)}")
    if attribution:
        print(f"     Attribution: {attribution}")
    
    return music_url, attribution


# ═══════════════════════════════════════════════════════════════
# PHASE 7: Build reel (Shotstack)
# ═══════════════════════════════════════════════════════════════
def compute_scene_boundaries(scenes, words, voice_duration):
    """Map scenes to time boundaries using Whisper word timestamps.
    
    Normalizes word counting to match Whisper's tokenization:
    - Hyphens become spaces (per-country -> per country = 2 words)
    - Punctuation stripped (U.S. -> US = 1 word)
    - Contractions kept as-is (What's = 1 word)
    """
    import re
    boundaries = []
    word_idx = 0
    for scene in scenes:
        vo_text = scene["voiceover"].replace("-", " ")
        vo_words = re.findall(r"[a-zA-Z0-9']+", vo_text)
        
        start_t = words[word_idx]["start"] if word_idx < len(words) else 0
        end_idx = min(word_idx + len(vo_words), len(words)) - 1
        end_t = words[end_idx]["end"] if end_idx < len(words) else voice_duration
        boundaries.append((start_t, end_t))
        word_idx = end_idx + 1
    return boundaries


def build_music_only_reel(scenes, music_url, build_dir):
    """Build music-only Quick Pulse reel (no voiceover, data-card style)."""
    print(f"\n{'='*60}")
    print(f"PHASE 7a: Building MUSIC-ONLY reel (Shotstack)...")
    print(f"{'='*60}")
    
    scene_dur = 3.5  # seconds per scene
    total_scenes_dur = len(scenes) * scene_dur
    endcard_dur = 3.5
    total_dur = total_scenes_dur + endcard_dur
    
    # ── SCENE IMAGES with zoomIn/slideLeft alternating ──
    scene_clips = []
    for i, scene in enumerate(scenes):
        start = i * scene_dur
        scene_clips.append({
            "asset": {"type": "image", "src": scene["image_url"]},
            "start": round(start, 2), "length": scene_dur,
            "fit": "cover", "position": "center",
            "effect": "zoomIn" if i % 2 == 0 else "slideLeft",
            "transition": {"in": "fade", "out": "fade"} if i > 0 else {"out": "fade"}
        })
    # Endcard
    scene_clips.append({
        "asset": {"type": "image", "src": ENDCARD_URL},
        "start": round(total_scenes_dur, 2), "length": endcard_dur,
        "fit": "cover", "position": "center", "transition": {"in": "fade"}
    })
    
    # ── LARGE ON-SCREEN TEXT: bold, centered, data-card style ──
    text_clips = []
    for i, scene in enumerate(scenes):
        start = i * scene_dur
        headline = scene["onscreen"]
        # Extract any number/stat from voiceover for big display
        vo = scene["voiceover"]
        
        html = (
            '<div style="'
            "display:flex;flex-direction:column;align-items:center;justify-content:center;"
            "width:100%;height:100%;padding:30px 20px;box-sizing:border-box;"
            '">'
            # Category label
            '<div style="'
            "font-family:'Inter',sans-serif;font-size:22px;font-weight:800;"
            "color:#D4AF37;text-transform:uppercase;letter-spacing:4px;"
            "text-shadow:0 0 10px rgba(0,0,0,0.9),2px 2px 5px rgba(0,0,0,0.9);"
            "margin-bottom:12px;"
            f'">{headline}</div>'
            # Voiceover as readable text
            '<div style="'
            "font-family:'Inter',sans-serif;font-size:34px;font-weight:900;"
            "color:#FFFFFF;text-align:center;line-height:1.2;"
            "text-shadow:0 0 12px rgba(0,0,0,0.95),0 0 30px rgba(0,0,0,0.8),"
            "3px 3px 6px rgba(0,0,0,0.9),-3px -3px 6px rgba(0,0,0,0.9);"
            f'">{vo}</div>'
            '</div>'
        )
        text_clips.append({
            "asset": {"type": "html", "html": html, "width": 580, "height": 450},
            "start": round(start, 2), "length": scene_dur,
            "fit": "none", "position": "bottom", "offset": {"y": 0.28},
            "transition": {"in": "fade"}
        })
    
    # ── LOGO ──
    logo_html = f'<div><img src="{LOGO_URL}" style="width:48px;height:48px;border-radius:50%;opacity:0.85;" /></div>'
    logo_clip = {
        "asset": {"type": "html", "html": logo_html, "width": 80, "height": 80},
        "start": 0, "length": round(total_scenes_dur, 2),
        "fit": "none", "position": "topLeft", "offset": {"x": 0.02, "y": -0.02}
    }
    
    timeline = {
        "background": "#000000",
        "tracks": [
            {"clips": text_clips},
            {"clips": [logo_clip]},
            {"clips": scene_clips},
        ]
    }
    if music_url:
        timeline["soundtrack"] = {"src": music_url, "effect": "fadeInFadeOut", "volume": 0.30}
    
    payload = {
        "timeline": timeline,
        "output": {"format": "mp4", "resolution": "1080", "aspectRatio": "9:16", "fps": 30,
                   "size": {"width": 1080, "height": 1920}}
    }
    
    # Submit render
    r = requests.post(
        "https://api.shotstack.io/v1/render",
        headers={"x-api-key": SHOTSTACK_KEY, "Content-Type": "application/json"},
        json=payload, timeout=30
    )
    if r.status_code not in (200, 201):
        print(f"❌ Music-only render failed: {r.status_code} {r.text[:300]}")
        return None, None
    
    render_id = r.json()["response"]["id"]
    print(f"  ⏳ Rendering music-only... ({total_dur:.0f}s, ID: {render_id})")
    
    # Poll
    for i in range(60):
        time.sleep(10)
        r = requests.get(
            f"https://api.shotstack.io/v1/render/{render_id}",
            headers={"x-api-key": SHOTSTACK_KEY}, timeout=15
        )
        status = r.json()["response"]["status"]
        if status == "done":
            reel_url = r.json()["response"]["url"]
            reel_path = f"{build_dir}/reel-music-only.mp4"
            subprocess.run(["curl", "-sS", "-o", reel_path, reel_url], check=True)
            size_mb = os.path.getsize(reel_path) / 1024 / 1024
            print(f"  ✅ Music-only reel: {total_dur:.0f}s, {size_mb:.1f}MB")
            return reel_path, render_id
        elif status == "failed":
            print(f"❌ Music-only render failed")
            return None, None
    
    print("❌ Music-only render timed out")
    return None, None


def build_reel(scenes, words, vo_url, voice_duration, music_url, endcard_cta_url, endcard_cta_dur, build_dir):
    """Build voiceover reel (Anchor format) via Shotstack."""
    print(f"\n{'='*60}")
    print(f"PHASE 7b: Building VOICEOVER reel (Shotstack)...")
    print(f"{'='*60}")
    
    boundaries = compute_scene_boundaries(scenes, words, voice_duration)
    endcard_dur = max(endcard_cta_dur + 1.5, 4.0) if endcard_cta_url else 4.0
    
    # ── CAPTIONS: bottom, transparent, text-shadow only ──
    caption_clips = []
    pill_words = []
    pill_start = 0
    for i, w in enumerate(words):
        if not pill_words:
            pill_start = w["start"]
        pill_words.append(w["word"])
        if len(pill_words) >= 4 or i == len(words) - 1:
            pill_end = w["end"]
            text = " ".join(pill_words)
            html = (
                '<div style="'
                "font-family:'Inter',sans-serif;font-size:40px;font-weight:800;"
                'color:#FFFFFF;text-align:center;overflow:hidden;text-overflow:ellipsis;'
                'text-shadow:0 0 8px rgba(0,0,0,0.95),0 0 20px rgba(0,0,0,0.8),'
                '2px 2px 4px rgba(0,0,0,0.9),-2px -2px 4px rgba(0,0,0,0.9),'
                '0 3px 6px rgba(0,0,0,0.7);'
                f'">{text}</div>'
            )
            caption_clips.append({
                "asset": {"type": "html", "html": html, "width": 580, "height": 120},
                "start": round(pill_start, 2),
                "length": round(max(pill_end - pill_start, 0.3), 2),
                "fit": "none", "position": "bottom", "offset": {"y": 0.27}
            })
            pill_words = []
    
    # ── HEADLINES: bottom, above captions, gold ──
    text_clips = []
    for i, scene in enumerate(scenes):
        s, e = boundaries[i]
        html = (
            '<div style="'
            "font-family:'Inter',sans-serif;font-size:28px;font-weight:900;"
            'color:#D4AF37;text-align:center;text-transform:uppercase;'
            'letter-spacing:3px;'
            'text-shadow:0 0 10px rgba(0,0,0,0.95),0 0 25px rgba(0,0,0,0.8),'
            '2px 2px 5px rgba(0,0,0,0.9),-2px -2px 5px rgba(0,0,0,0.9);'
            f'">{scene["onscreen"]}</div>'
        )
        text_clips.append({
            "asset": {"type": "html", "html": html, "width": 580, "height": 80},
            "start": round(s, 2), "length": round(e - s, 2),
            "fit": "none", "position": "bottom", "offset": {"y": 0.31}
        })
    
    # ── SCENE IMAGES + ENDCARD ──
    scene_clips = []
    for i, scene in enumerate(scenes):
        s, e = boundaries[i]
        scene_clips.append({
            "asset": {"type": "image", "src": scene["image_url"]},
            "start": round(s, 2), "length": round(e - s, 2),
            "fit": "cover", "position": "center",
            "effect": "zoomIn" if i % 2 == 0 else "slideLeft",
            "transition": {"in": "fade", "out": "fade"} if i > 0 else {"out": "fade"}
        })
    scene_clips.append({
        "asset": {"type": "image", "src": ENDCARD_URL},
        "start": round(voice_duration, 2), "length": round(endcard_dur, 2),
        "fit": "cover", "position": "center", "transition": {"in": "fade"}
    })
    
    # ── LOGO ──
    logo_html = f'<div><img src="{LOGO_URL}" style="width:48px;height:48px;border-radius:50%;opacity:0.85;" /></div>'
    logo_clip = {
        "asset": {"type": "html", "html": logo_html, "width": 80, "height": 80},
        "start": 0, "length": round(voice_duration, 2),
        "fit": "none", "position": "topLeft", "offset": {"x": 0.02, "y": -0.02}
    }
    
    # ── AUDIO ──
    audio_clips = [
        {"asset": {"type": "audio", "src": vo_url, "volume": 1.0},
         "start": 0, "length": round(voice_duration, 2)}
    ]
    if endcard_cta_url:
        audio_clips.append({
            "asset": {"type": "audio", "src": endcard_cta_url, "volume": 1.0},
            "start": round(voice_duration + 0.5, 2), "length": round(endcard_cta_dur, 2)
        })
    
    timeline = {
        "background": "#000000",
        "tracks": [
            {"clips": caption_clips},
            {"clips": [logo_clip]},
            {"clips": text_clips},
            {"clips": scene_clips},
            {"clips": audio_clips}
        ]
    }
    if music_url:
        timeline["soundtrack"] = {"src": music_url, "effect": "fadeInFadeOut", "volume": 0.05}
    
    payload = {
        "timeline": timeline,
        "output": {"format": "mp4", "resolution": "1080", "aspectRatio": "9:16", "fps": 30,
                   "size": {"width": 1080, "height": 1920}}
    }
    
    # Submit render
    r = requests.post(
        "https://api.shotstack.io/v1/render",
        headers={"x-api-key": SHOTSTACK_KEY, "Content-Type": "application/json"},
        json=payload, timeout=30
    )
    if r.status_code not in (200, 201):
        print(f"❌ Render failed: {r.status_code} {r.text[:300]}")
        sys.exit(1)
    
    render_id = r.json()["response"]["id"]
    total = voice_duration + endcard_dur
    print(f"  ⏳ Rendering... ({total:.0f}s reel, ID: {render_id})")
    
    # Poll for completion
    for i in range(60):
        time.sleep(10)
        r = requests.get(
            f"https://api.shotstack.io/v1/render/{render_id}",
            headers={"x-api-key": SHOTSTACK_KEY}, timeout=15
        )
        status = r.json()["response"]["status"]
        if status == "done":
            reel_url = r.json()["response"]["url"]
            # Download
            reel_path = f"{build_dir}/reel.mp4"
            subprocess.run(["curl", "-sS", "-o", reel_path, reel_url], check=True)
            size_mb = os.path.getsize(reel_path) / 1024 / 1024
            print(f"  ✅ Reel ready: {total:.0f}s, {size_mb:.1f}MB")
            return reel_path, render_id
        elif status == "failed":
            print(f"❌ Render failed")
            sys.exit(1)
    
    print("❌ Render timed out")
    sys.exit(1)


# ═══════════════════════════════════════════════════════════════
# PHASE 8: Build carousel images
# ═══════════════════════════════════════════════════════════════
def build_carousel(scenes, build_dir):
    """Generate carousel slides with text overlay."""
    print(f"\n{'='*60}")
    print(f"PHASE 8: Building carousel images...")
    print(f"{'='*60}")
    
    carousel_dir = f"{build_dir}/carousel"
    os.makedirs(carousel_dir, exist_ok=True)
    
    W, H = 1080, 1350  # 4:5 portrait (works on all platforms)
    
    def wrap_text(text, font, max_width):
        words = text.split()
        lines, current = [], ""
        for word in words:
            test = f"{current} {word}".strip()
            if font.getbbox(test)[2] <= max_width:
                current = test
            else:
                if current: lines.append(current)
                current = word
        if current: lines.append(current)
        return lines
    
    headline_font = ImageFont.truetype(FONT_HEAVY, 32)
    vo_font = ImageFont.truetype(FONT_BOLD, 38)
    slide_font = ImageFont.truetype(FONT_BOLD, 22)
    
    slides = []
    for i, scene in enumerate(scenes):
        # Download scene image
        img_path = f"{build_dir}/carousel_src_{i}.jpg"
        subprocess.run(["curl", "-sS", "-o", img_path, scene["image_url"]], check=True)
        
        img = Image.open(img_path).convert("RGB")
        iw, ih = img.size
        
        # Center crop to 4:5
        target_ratio = W / H
        current_ratio = iw / ih
        if current_ratio < target_ratio:
            new_h = int(iw / target_ratio)
            top = (ih - new_h) // 2
            img = img.crop((0, top, iw, top + new_h))
        else:
            new_w = int(ih * target_ratio)
            left = (iw - new_w) // 2
            img = img.crop((left, 0, left + new_w, ih))
        
        img = img.resize((W, H), Image.LANCZOS)
        
        # Bottom gradient
        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        for y in range(H - 400, H):
            alpha = int(200 * (y - (H - 400)) / 400)
            od.rectangle([(0, y), (W, y+1)], fill=(0, 0, 0, min(alpha, 200)))
        
        img = img.convert("RGBA")
        img = Image.alpha_composite(img, overlay)
        d = ImageDraw.Draw(img)
        
        # Text layout
        hl_lines = wrap_text(scene["onscreen"].upper(), headline_font, W - 80)
        vo_lines = wrap_text(scene["voiceover"], vo_font, W - 80)
        
        vo_y = H - 60 - len(vo_lines) * 48
        hl_y = vo_y - 20 - len(hl_lines) * 40
        
        # Gold headline
        for j, line in enumerate(hl_lines):
            tw = headline_font.getbbox(line)[2]
            x = (W - tw) // 2
            d.text((x+2, hl_y + j*40 + 2), line, font=headline_font, fill=(0,0,0,200))
            d.text((x, hl_y + j*40), line, font=headline_font, fill=(212,175,55,255))
        
        # White voiceover
        for j, line in enumerate(vo_lines):
            tw = vo_font.getbbox(line)[2]
            x = (W - tw) // 2
            d.text((x+2, vo_y + j*48 + 2), line, font=vo_font, fill=(0,0,0,200))
            d.text((x, vo_y + j*48), line, font=vo_font, fill=(255,255,255,255))
        
        # Logo
        if os.path.exists(LOGO_LOCAL):
            logo = Image.open(LOGO_LOCAL).convert("RGBA").resize((56,56), Image.LANCZOS)
            mask = Image.new("L", (56,56), 0)
            ImageDraw.Draw(mask).ellipse((0,0,56,56), fill=255)
            img.paste(logo, (24,24), mask)
        
        # Slide number
        d.text((W-80, 30), f"{i+1}/{len(scenes)}", font=slide_font, fill=(255,255,255,200))
        
        out = f"{carousel_dir}/slide-{i}.jpg"
        img.convert("RGB").save(out, "JPEG", quality=92)
        slides.append(out)
        print(f"  ✅ Slide {i+1}/{len(scenes)}: {scene['onscreen']}")
    
    return slides


# ═══════════════════════════════════════════════════════════════
# PHASE 9: Distribute
# ═══════════════════════════════════════════════════════════════
def upload_youtube(reel_path, article, attribution="", variant="voice"):
    """Upload reel to YouTube as a Short."""
    print(f"\n  📺 YouTube upload ({variant})...")
    
    client_id = os.environ.get("YOUTUBE_CLIENT_ID", "")
    client_secret = os.environ.get("YOUTUBE_CLIENT_SECRET", "")
    refresh_token = os.environ.get("YOUTUBE_REFRESH_TOKEN", "")
    
    if not all([client_id, client_secret, refresh_token]):
        print("  ⚠️ YouTube credentials missing, skipping")
        return None
    
    # Refresh token
    r = requests.post("https://oauth2.googleapis.com/token", data={
        "client_id": client_id, "client_secret": client_secret,
        "refresh_token": refresh_token, "grant_type": "refresh_token"
    }, timeout=15)
    if r.status_code != 200:
        print(f"  ❌ YT token refresh failed: {r.status_code}")
        return None
    
    access_token = r.json()["access_token"]
    
    headline = article["headline"]
    title = headline[:91] + " #Shorts"
    article_url = f"https://www.thevideshi.com/articles/{article['slug']}"
    
    desc = f"""{headline}

{article.get('subheadline', '')}

Read the full article: {article_url}

{f'Music: {attribution}' if attribution else ''}

#TheVideshi #IndianDiaspora #DiasporaNews #NRI"""
    
    metadata = {
        "snippet": {
            "title": title, "description": desc.strip(),
            "categoryId": "25",
            "tags": ["Indian diaspora", "NRI", "The Videshi", "diaspora news"]
        },
        "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False}
    }
    
    file_size = os.path.getsize(reel_path)
    
    init_r = requests.post(
        "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=UTF-8",
            "X-Upload-Content-Length": str(file_size),
            "X-Upload-Content-Type": "video/mp4"
        },
        json=metadata, timeout=30
    )
    
    if init_r.status_code != 200:
        print(f"  ❌ YT init failed: {init_r.status_code}")
        return None
    
    upload_url = init_r.headers["Location"]
    
    with open(reel_path, "rb") as f:
        up_r = requests.put(upload_url, headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "video/mp4", "Content-Length": str(file_size)
        }, data=f.read(), timeout=120)
    
    if up_r.status_code in (200, 201):
        vid = up_r.json()["id"]
        yt_url = f"https://youtube.com/shorts/{vid}"
        print(f"  ✅ YouTube: {yt_url}")
        return yt_url
    else:
        print(f"  ❌ YT upload failed: {up_r.status_code}")
        return None


def distribute(reel_path, carousel_slides, article, attribution="", skip=False):
    """Distribute reel + carousel to all platforms."""
    print(f"\n{'='*60}")
    print(f"PHASE 9: Distribution")
    print(f"{'='*60}")
    
    if skip:
        print("  ⏭️  Distribution skipped (--skip-distribute)")
        return {}
    
    results = {}
    
    # YouTube (reel)
    if reel_path:
        yt_url = upload_youtube(reel_path, article, attribution)
        if yt_url:
            results["youtube"] = yt_url
    
    # X (carousel) — check if credits available
    # TODO: Re-enable when X API credits restored
    print("  ⏸️  X: credits depleted, skipping")
    
    # Instagram, Threads, Facebook — check if Meta tokens available
    # TODO: Re-enable when Meta dev account restored
    print("  ⏸️  Instagram/Threads/Facebook: Meta dev account restricted, skipping")
    
    return results


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════
def main():
    parser = argparse.ArgumentParser(description="The Videshi Reel + Carousel Pipeline")
    parser.add_argument("--article-id", help="Article UUID (auto-picks if omitted)")
    parser.add_argument("--manual-images", help="Directory with manually generated scene images")
    parser.add_argument("--skip-distribute", action="store_true", help="Skip distribution")
    parser.add_argument("--carousel-only", action="store_true", help="Only build carousel (skip reel)")
    parser.add_argument("--prompts-only", action="store_true", help="Stop after generating storyboard prompts (Step 1)")
    parser.add_argument("--build-dir", help="Build directory (default: /tmp/reel-build-<id>)")
    args = parser.parse_args()
    
    article_id = args.article_id
    
    # Auto-pick if no article specified
    if not article_id:
        article_id = auto_pick_article()
        if not article_id:
            print("❌ No suitable article found for reel generation")
            sys.exit(0)
    
    build_dir = args.build_dir or f"/tmp/reel-build-{article_id[:8]}"
    os.makedirs(build_dir, exist_ok=True)
    
    print(f"\n🎬 The Videshi Reel + Carousel Pipeline")
    print(f"   Article: {article_id}")
    print(f"   Build:   {build_dir}\n")
    
    # Phase 1: Fetch article
    article = fetch_article(article_id)
    
    # Phase 2: Storyboard (reuse cached if available)
    scenes_cache = f"{build_dir}/scenes.json"
    if os.path.exists(scenes_cache) and not args.prompts_only:
        with open(scenes_cache) as f:
            cached = json.load(f)
        scenes = cached["scenes"] if isinstance(cached, dict) and "scenes" in cached else cached
        print(f"\n{'='*60}")
        print(f"PHASE 2: Reusing cached storyboard ({len(scenes)} scenes)")
        print(f"{'='*60}")
        for i, s in enumerate(scenes):
            print(f"     Scene {i}: [{s['onscreen']}] {s['voiceover'][:60]}...")
    else:
        scenes = generate_storyboard(article)
        # Save scenes
        with open(scenes_cache, "w") as f:
            json.dump({"article_id": article_id, "scenes": scenes}, f, indent=2)
    
    # Output ChatGPT prompts
    prompts_path = f"{build_dir}/chatgpt-prompts.txt"
    with open(prompts_path, "w") as f:
        f.write(f"ARTICLE: {article['headline']}\n")
        f.write(f"ID: {article_id}\n")
        f.write(f"SCENES: {len(scenes)}\n")
        f.write(f"{'='*60}\n\n")
        f.write("Paste each prompt into ChatGPT one at a time.\n")
        f.write("Save each image as scene-0.jpg, scene-1.jpg, etc.\n\n")
        for i, scene in enumerate(scenes):
            f.write(f"{'─'*60}\n")
            f.write(f"SCENE {i} — {scene['onscreen']}\n")
            f.write(f"{'─'*60}\n")
            f.write(f"Voiceover: {scene['voiceover']}\n\n")
            f.write(f"IMAGE PROMPT (paste this into ChatGPT):\n\n")
            f.write(f"{scene['image_prompt']}\n\n")
    
    print(f"\n  📋 ChatGPT prompts saved: {prompts_path}")
    
    if args.prompts_only:
        # Copy prompts to workspace for easy access
        import shutil
        slug_short = article["slug"][:50] if article.get("slug") else article_id[:8]
        out_prompts = os.path.expanduser(f"~/workspace/your_files/prompts-{slug_short}.txt")
        shutil.copy(prompts_path, out_prompts)
        print(f"\n{'='*60}")
        print(f"✅ STEP 1 COMPLETE — PROMPTS READY")
        print(f"{'='*60}")
        print(f"  Prompts: {out_prompts}")
        print(f"  Scenes:  {len(scenes)}")
        print(f"\n  Next: paste each prompt into ChatGPT, save images,")
        print(f"  then run:")
        print(f"    python3 reel-pipeline.py --article-id {article_id} --manual-images /path/to/images/")
        print()
        return
    
    # Phase 3: Images (manual only)
    if args.manual_images:
        load_manual_images(scenes, args.manual_images, article_id)
    else:
        print("\n❌ Image generation requires --manual-images or --prompts-only")
        print(f"   Run with --prompts-only first, then --manual-images /path/")
        sys.exit(1)
    
    # Phase 8: Carousel (can run before reel since it's independent)
    carousel_slides = build_carousel(scenes, build_dir)
    
    if args.carousel_only:
        print(f"\n✅ Carousel only — {len(carousel_slides)} slides ready")
        print(f"   {build_dir}/carousel/")
        return
    
    # Phase 4: TTS (reuse cached if available)
    vo_mp3_cache = f"{build_dir}/voiceover.mp3"
    if os.path.exists(vo_mp3_cache) and os.path.getsize(vo_mp3_cache) > 1000:
        print(f"\n{'='*60}")
        print(f"PHASE 4: Reusing cached voiceover")
        print(f"{'='*60}")
        dur = float(subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", vo_mp3_cache],
            capture_output=True, text=True
        ).stdout.strip())
        # Upload to Supabase (in case it's not there)
        storage_path = f"reel-gen/{article_id}/voiceover.mp3"
        with open(vo_mp3_cache, "rb") as f:
            requests.post(
                f"{SB_URL}/storage/v1/object/article-images/{storage_path}",
                headers={**SB_HEADERS, "Content-Type": "audio/mpeg", "x-upsert": "true"},
                data=f.read(), timeout=30
            )
        vo_url = f"{STORAGE_BASE}/{storage_path}"
        voice_duration = dur
        vo_mp3 = vo_mp3_cache
        print(f"  ✅ Voiceover: {dur:.1f}s (cached)")
    else:
        vo_url, voice_duration, vo_mp3 = generate_tts(scenes, article_id, build_dir)
    
    # Endcard CTA
    endcard_cta_url, endcard_cta_dur = ensure_endcard_cta()
    
    # Phase 5: Whisper
    words = get_word_timestamps(vo_mp3, build_dir)
    
    # Phase 6: Music
    music_url, attribution = select_music(article, build_dir)
    
    # Phase 7a: Build MUSIC-ONLY reel (Quick Pulse)
    music_reel_path, music_render_id = build_music_only_reel(scenes, music_url, build_dir)
    
    # Phase 7b: Build VOICEOVER reel (Anchor)
    vo_reel_path, vo_render_id = build_reel(
        scenes, words, vo_url, voice_duration,
        music_url, endcard_cta_url, endcard_cta_dur, build_dir
    )
    
    # Copy outputs
    output_dir = os.path.expanduser("~/workspace/your_files")
    slug_short = article["slug"][:50] if article.get("slug") else article_id[:8]
    
    if music_reel_path:
        music_reel_out = f"{output_dir}/reel-music-{slug_short}.mp4"
        subprocess.run(["cp", music_reel_path, music_reel_out])
    
    if vo_reel_path:
        vo_reel_out = f"{output_dir}/reel-voice-{slug_short}.mp4"
        subprocess.run(["cp", vo_reel_path, vo_reel_out])
    
    carousel_out = f"{output_dir}/carousel-{slug_short}"
    os.makedirs(carousel_out, exist_ok=True)
    for slide in carousel_slides:
        subprocess.run(["cp", slide, carousel_out])
    
    # Phase 9: Register in prebuilt_reels + distribute
    def register_reel(reel_path, variant_label, article):
        """Register a reel in prebuilt_reels for the distributor."""
        # Upload reel to Supabase storage
        reel_storage = f"reel-gen/{article['id']}/reel-{variant_label}.mp4"
        with open(reel_path, "rb") as f:
            requests.post(
                f"{SB_URL}/storage/v1/object/article-images/{reel_storage}",
                headers={**SB_HEADERS, "Content-Type": "video/mp4", "x-upsert": "true"},
                data=f.read(), timeout=120
            )
        video_url = f"{STORAGE_BASE}/{reel_storage}"
        
        article_url = f"https://www.thevideshi.com/articles/{article.get('slug', '')}"
        caption = f"🇮🇳 {article['headline']}\n\n📰 {article_url}\n\n#IndianDiaspora #NRI #TheVideshi"
        
        row = {
            "article_id": article["id"],
            "article_slug": article.get("slug", ""),
            "headline": article["headline"],
            "video_path": reel_storage,
            "video_url": video_url,
            "caption": caption[:2200],
            "source": "pipeline",
            "qa_passed": True,
            "status": "ready"
        }
        r = requests.post(
            f"{SB_URL}/rest/v1/prebuilt_reels",
            headers={**SB_HEADERS, "Content-Type": "application/json", "Prefer": "return=representation"},
            json=row, timeout=15
        )
        if r.status_code in (200, 201):
            print(f"  ✅ Registered {variant_label} reel in prebuilt_reels")
        else:
            print(f"  ⚠️ Registration failed: {r.status_code} {r.text[:200]}")
    
    # Register both reels
    if music_reel_path:
        register_reel(music_reel_path, "music-only", article)
    if vo_reel_path:
        register_reel(vo_reel_path, "voiceover", article)
    
    # Direct YouTube upload
    results = {}
    if not args.skip_distribute:
        if music_reel_path:
            results["youtube_music"] = upload_youtube(music_reel_path, article, attribution, "music-only")
        if vo_reel_path:
            results["youtube_voice"] = upload_youtube(vo_reel_path, article, attribution, "voiceover")
    
    # Summary
    print(f"\n{'='*60}")
    print(f"✅ PIPELINE COMPLETE — TWO REEL VERSIONS")
    print(f"{'='*60}")
    if music_reel_path:
        print(f"  🎵 Music-only:  {music_reel_out}")
        print(f"     Render ID:   {music_render_id}")
    if vo_reel_path:
        print(f"  🎙️  Voiceover:   {vo_reel_out}")
        print(f"     Render ID:   {vo_render_id}")
    print(f"  🖼️  Carousel:    {carousel_out}/ ({len(carousel_slides)} slides)")
    for platform, url in results.items():
        if url:
            print(f"  {platform}: {url}")
    print()


if __name__ == "__main__":
    main()
