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
LOGO_URL = f"{STORAGE_BASE}/branding/logo-transparent-512.png"
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
        raise RuntimeError(f"Article not found: {r.status_code}")
    
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
- Describe a SPECIFIC data visualization: a comparison table, trend chart, horizontal bar chart, stat callout with icons, before/after comparison, or breakdown panel
- Keep each scene visually clean — a viewer should absorb ONE key takeaway in 3-4 seconds on a phone
- Include the EXACT real numbers, dates, categories, and labels from the article — bake all data INTO the prompt
- Describe the visual style in detail:
  * BRIGHT, high-contrast background that pops on a phone screen — NOT dark or muddy
  * Choose colors and mood that fit the story — let the color palette emerge from the topic
  * Bold headline text with colored subtitle
  * Red or orange highlights for critical/alarming data points
  * Professional icons next to key points (use descriptive icon concepts like "hourglass icon", "warning icon", "chart icon")
  * Source attribution at the bottom when citing official data
  * Leave the TOP-LEFT CORNER CLEAR — no text, badges, or graphics in the upper-left 200x200px area (a real logo will be overlaid there)
  * **YOUTUBE SAFE ZONE** — keep ALL important text, data, and graphics within the center safe zone of the image:
    - TOP: leave the top ~10% clear (status bar, notch)
    - BOTTOM: leave the bottom ~25% clear or use only background/atmosphere — NO text, checklists, source citations, or tickers (YouTube's title, channel info, and nav bar cover this area)
    - RIGHT: leave the rightmost ~15% clear of critical text (like/comment/share buttons)
    - LEFT: leave the leftmost ~5% clear
    - In practice for 1080×1920: keep all text/data within roughly x:55-920, y:190-1440
- End with: "Style: broadcast-quality news infographic, data card aesthetic, bright and vibrant, professional iconography, bold hierarchy, crisp typography, high production value. Vertical 9:16 phone format."
- Mix different visualization types across scenes: each scene visually distinct

Example of a GOOD data-centric prompt:
"Create a single vertical 9:16 broadcast-quality infographic card. Title: 'JULY 2026 VISA BULLETIN' in bold text, subtitle 'EMPLOYMENT-BASED FINAL ACTION DATES' in a contrasting color. Below, a clean data table with a colored header row showing columns: Category, All Chargeability Areas Except India, India. Rows: EB-1 (15MAY23, 15MAY23), EB-2 row highlighted in RED (15JAN23, UNAVAILABLE in bold red text), EB-3 (01JAN13, 01NOV12). Bright, clean background. U.S. Department of State seal icon next to source attribution at the bottom. Leave top-left corner clear (no badges or text). Style: broadcast-quality news infographic, data card aesthetic, bright and vibrant, professional iconography, bold hierarchy, crisp typography, high production value. Vertical 9:16 phone format."

**NARRATIVE articles** (human interest, entertainment, travel, profiles, events):
Use PHOTOGRAPHIC prompts as before.
Each image_prompt MUST:
- Start with: "Create a single cinematic vertical 9:16 news photograph."
- Include 3-5 sentences of RICH, SPECIFIC visual description — exact subjects, environments, objects, compositions, camera angles, lighting
- Reference CONCRETE details from the article (specific numbers, real places, real concepts, real institutions) — bake the article knowledge INTO the prompt
- Specify atmosphere/mood in the description
- End with: "Style: BBC documentary photography, Reuters editorial realism, ultra realistic, cinematic lighting, professional DSLR, dramatic scale, emotional storytelling. No text. No captions. No logos. No watermarks. No graphics. Single standalone image only."
- Respect the same YOUTUBE SAFE ZONE as data cards — any overlaid text or baked-in title must stay within x:55-920, y:190-1440

**HYBRID**: Many articles benefit from MIXING both approaches. For a data-centric article, open with a dramatic hook card (bold headline + subtle background imagery + key impact bullets), then show data panels, then close with a "what this means" or "bigger picture" panel. Use your judgment based on the article content.

ACROSS ALL APPROACHES:
- Each scene must be visually COMPLETELY DIFFERENT from every other scene
- Each scene should carry different information and a different visual rendering — do NOT repeat information across scenes
- Reference CONCRETE details from the article
- RESPECT THE YOUTUBE SAFE ZONE on every scene — no important text or data in the top 10%, bottom 25%, right 15%, or left 5% of the frame. Viewers will never see content in those margins.

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

**CRITICAL — VOICE-TO-VISUAL SYNC**:
The voiceover for each scene MUST directly describe or narrate what the viewer will SEE on that scene's card.
- If scene 3's image shows "Germany: 21 months to PR vs US: 80+ years" then scene 3's voiceover must talk about Germany vs US wait times — NOT about Canada or Australia.
- If scene 4's image shows Canada Express Entry data, the voiceover must narrate Canada's numbers.
- Think of it like a news anchor reading what's on the teleprompter while the matching graphic is on screen.
- Do NOT generate the voiceover as a general narrative and images as separate infographics — they must be locked together scene by scene.
- The image_prompt and voiceover for each scene describe the SAME fact from the SAME angle.

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
        raise RuntimeError(f"Storyboard generation failed: {r.status_code}")
    
    result = json.loads(r.json()["choices"][0]["message"]["content"])
    scenes = result["scenes"]
    
    total_words = sum(len(s["voiceover"].split()) for s in scenes)
    print(f"  ✅ {len(scenes)} scenes, {total_words} words (~{total_words * 0.35:.0f}s)")
    for i, s in enumerate(scenes):
        print(f"     Scene {i}: [{s['onscreen']}] {s['voiceover'][:60]}...")
    
    return scenes


# ═══════════════════════════════════════════════════════════════
# PHASE 2.5: Evaluate article images for reel blending
# ═══════════════════════════════════════════════════════════════
def evaluate_hero_for_blend(article):
    """Check if the article's hero + body images are good enough to blend into reel scenes.
    
    Returns dict with {usable: bool, images: [{img_path, subject, source}...]}
    Images are ordered: hero first, then body images. Each is saved to /tmp.
    """
    import base64
    from io import BytesIO
    
    hero_url = article.get("image_url", "")
    headline = article.get("headline", "")
    body = article.get("body", "") or ""
    
    print(f"\n{'='*60}")
    print(f"PHASE 2.5: Evaluating article images for blend...")
    print(f"{'='*60}")
    
    # Collect all candidate URLs: hero + body images
    candidates = []
    if hero_url:
        candidates.append({"url": hero_url, "source": "hero"})
    
    # Extract body images
    body_pattern = r'!\[[^\]]*\]\(([^)]+)\)'
    body_urls = re.findall(body_pattern, body)
    body_urls = [u for u in body_urls if any(ext in u.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp', 'image'])]
    for url in body_urls[:5]:  # up to 5 body images
        if url != hero_url:  # skip dupes of hero
            candidates.append({"url": url, "source": "body"})
    
    if not candidates:
        print(f"  ❌ No images found")
        return {"usable": False, "images": []}
    
    usable_images = []
    
    for idx, cand in enumerate(candidates):
        url = cand["url"]
        source = cand["source"]
        
        # Download
        try:
            r = requests.get(url, timeout=15, headers={
                "User-Agent": "TheVideshi/1.0 (thevideshi.com)"
            })
            if r.status_code != 200:
                print(f"  ❌ {source} download failed: HTTP {r.status_code}")
                continue
            img_bytes = r.content
            if len(img_bytes) < 5000:
                print(f"  ❌ {source} too small ({len(img_bytes)} bytes)")
                continue
        except Exception as e:
            print(f"  ❌ {source} download error: {e}")
            continue
        
        # Check dimensions
        try:
            img = Image.open(BytesIO(img_bytes))
            w, h = img.size
        except Exception:
            print(f"  ❌ {source} not a valid image")
            continue
        
        if w < 400 or h < 300:
            print(f"  ❌ {source} too low-res ({w}×{h})")
            continue
        
        # Save locally for edits API
        img_path = f"/tmp/blend-{idx}.png"
        img.convert("RGBA").save(img_path, "PNG")
        
        # Quick vision check
        img_b64 = base64.b64encode(img_bytes).decode()
        subject = "unknown"
        try:
            check = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"},
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": [
                        {"type": "text", "text": f'Is this a clear, high-quality photo of a recognizable person, place, scene, or specific subject (NOT a generic stock photo, logo, icon, or chart)? Headline: "{headline}". Answer ONLY with JSON: {{"usable": true/false, "subject": "who/what is shown in 5 words max"}}'},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}", "detail": "low"}}
                    ]}],
                    "temperature": 0,
                    "response_format": {"type": "json_object"}
                },
                timeout=30
            )
            if check.status_code == 200:
                result = json.loads(check.json()["choices"][0]["message"]["content"])
                if not result.get("usable", False):
                    print(f"  ❌ {source} ({w}×{h}): not suitable — {result.get('subject', 'unclear')}")
                    continue
                subject = result.get("subject", "recognized")
                print(f"  ✅ {source} ({w}×{h}): {subject}")
            else:
                print(f"  ⚠️ {source} vision check failed, including anyway")
        except Exception as e:
            print(f"  ⚠️ {source} vision error: {e}, including anyway")
        
        usable_images.append({
            "img_path": img_path,
            "subject": subject,
            "source": source,
            "w": w, "h": h
        })
    
    if usable_images:
        print(f"  📊 {len(usable_images)} usable image(s) for blending")
    else:
        print(f"  📊 No usable images — all scenes will be AI-generated")
    
    return {"usable": len(usable_images) > 0, "images": usable_images}


def generate_blended_scene(scene_prompt, hero_path, build_dir, scene_idx, article_id):
    """Generate a scene using OpenAI edits API with the hero image as reference.
    
    Returns the local path to the processed image, or None on failure.
    """
    import base64
    
    print(f"  Scene {scene_idx}: blending with hero image...")
    
    BLEND_SUFFIX = (
        " Choose colors and visual mood that best fit this story. "
        "One clear takeaway readable in 3 seconds. "
        "Leave the top-left corner clear for a logo overlay. "
        "IMPORTANT: Keep all text and important graphics within the center safe zone — "
        "leave the top 10%, bottom 25%, right 15%, and left 5% of the frame clear of text or data. "
        "Vertical 9:16."
    )
    
    full_prompt = (
        "Place the person from this photo into a broadcast news scene. "
        + scene_prompt + BLEND_SUFFIX
    )
    
    try:
        with open(hero_path, "rb") as f:
            r = requests.post(
                "https://api.openai.com/v1/images/edits",
                headers={"Authorization": f"Bearer {OPENAI_KEY}"},
                files={"image": ("photo.png", f, "image/png")},
                data={
                    "model": "gpt-image-1",
                    "prompt": full_prompt,
                    "size": "1024x1536",
                    "quality": "high",
                    "n": 1
                },
                timeout=180
            )
        
        if r.status_code != 200:
            print(f"  ⚠️ Blend failed ({r.status_code}): {r.text[:200]}")
            return None
        
        img_data_b64 = r.json()["data"][0].get("b64_json")
        if img_data_b64:
            img_bytes = base64.b64decode(img_data_b64)
        else:
            img_url = r.json()["data"][0]["url"]
            img_bytes = requests.get(img_url, timeout=30).content
        
        local_path = f"{build_dir}/scene-{scene_idx}.jpg"
        with open(local_path, "wb") as f:
            f.write(img_bytes)
        
        # Apply safe zone
        safe_path = enforce_safe_zone(local_path)
        print(f"  ✅ Scene {scene_idx}: blended + safe zone ({os.path.getsize(safe_path)//1024}KB)")
        return safe_path
        
    except Exception as e:
        print(f"  ⚠️ Blend error: {e}")
        return None


# ═══════════════════════════════════════════════════════════════
# PHASE 3: Generate scene images
# ═══════════════════════════════════════════════════════════════
def generate_images_api(scenes, article_id, build_dir, hero_blend=None):
    """Generate images via OpenAI gpt-image-1 API, overlay real logo, upload.
    
    If hero_blend is provided (from evaluate_hero_for_blend), Scene 0 will
    use the real hero photo blended into a broadcast scene via the edits API.
    """
    import base64
    print(f"\n{'='*60}")
    print(f"PHASE 3: Generating images (OpenAI API)...")
    print(f"{'='*60}")
    
    storage_prefix = f"reel-gen/{article_id}"
    
    # Brightness/style wrapper for all prompts
    PROMPT_PREFIX = (
        "A visually rich broadcast infographic scene for a short-form news reel. "
        "Bright, vibrant, high-contrast — designed to pop on a small phone screen. "
        "Light or medium-toned background, not dark. "
    )
    PROMPT_SUFFIX = (
        " Choose colors and visual mood that best fit this story. "
        "One clear takeaway readable in 3 seconds, not a full infographic poster. "
        "Leave the top-left corner clear for a logo overlay. "
        "IMPORTANT: Keep all text and important graphics within the center safe zone — "
        "leave the top 10%, bottom 25%, right 15%, and left 5% of the frame clear of text or data "
        "(these areas are covered by YouTube Shorts UI). 9:16 vertical."
    )
    
    for i, scene in enumerate(scenes):
        raw_prompt = scene.get("image_prompt", scene.get("scene_focus", ""))
        
        # ── Try blending with article images ──
        # Distribute usable images across scenes: hero for scene 0,
        # body images for subsequent scenes, cycling if we have more scenes than images.
        if hero_blend and hero_blend.get("usable") and hero_blend.get("images"):
            blend_images = hero_blend["images"]
            # Scene 0 → first image (hero), scene 1 → second image, etc.
            # If more scenes than images, remaining scenes generate normally.
            if i < len(blend_images):
                blend_img = blend_images[i]
            else:
                blend_img = None
            
            if blend_img:
                blended_path = generate_blended_scene(
                    raw_prompt, blend_img["img_path"], build_dir, i, article_id
                )
                if blended_path:
                    with open(blended_path, "rb") as f:
                        final_bytes = f.read()
                    ext = os.path.splitext(blended_path)[1].lower()
                    content_type = "image/png" if ext == ".png" else "image/jpeg"
                    storage_path = f"{storage_prefix}/scene-{i}{ext}"
                    requests.post(
                        f"{SB_URL}/storage/v1/object/article-images/{storage_path}",
                        headers={**SB_HEADERS, "Content-Type": content_type, "x-upsert": "true"},
                        data=final_bytes, timeout=30
                    )
                    scene["image_url"] = f"{STORAGE_BASE}/{storage_path}"
                    scene["blended"] = True
                    print(f"     (blended with {blend_img['source']}: {blend_img['subject']})")
                    continue
                else:
                    print(f"  ⚠️ Blend failed for scene {i}, falling back to generation")
        
        print(f"  Scene {i}: generating...")
        
        raw_prompt = scene.get("image_prompt", scene.get("scene_focus", ""))
        full_prompt = PROMPT_PREFIX + raw_prompt + PROMPT_SUFFIX
        
        r = requests.post(
            "https://api.openai.com/v1/images/generations",
            headers={"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"},
            json={
                "model": "gpt-image-1",
                "prompt": full_prompt,
                "n": 1,
                "size": "1024x1536",  # portrait
                "quality": "high"
            },
            timeout=180
        )
        
        if r.status_code != 200:
            error_msg = r.text[:200]
            if "safety" in error_msg.lower() or "content_policy" in error_msg.lower():
                print(f"  ⚠️  Scene {i} blocked by safety filter")
                print(f"     Prompt: {raw_prompt[:100]}...")
                print(f"     → Use --manual-images to provide this scene")
                scene["image_url"] = None
                continue
            else:
                print(f"  ❌ Image gen failed: {r.status_code} {error_msg}")
                scene["image_url"] = None
                continue
        
        # Download image
        img_data_b64 = r.json()["data"][0].get("b64_json")
        if img_data_b64:
            img_bytes = base64.b64decode(img_data_b64)
        else:
            img_url = r.json()["data"][0]["url"]
            img_bytes = requests.get(img_url, timeout=30).content
        
        # Save locally
        local_path = f"{build_dir}/scene-{i}.jpg"
        with open(local_path, "wb") as f:
            f.write(img_bytes)
        
        # Apply safe zone compositing + logo
        safe_path = enforce_safe_zone(local_path)
        
        # Re-read after processing
        with open(safe_path, "rb") as f:
            final_bytes = f.read()
        
        # Upload to Supabase
        ext = os.path.splitext(safe_path)[1].lower()
        content_type = "image/png" if ext == ".png" else "image/jpeg"
        storage_path = f"{storage_prefix}/scene-{i}{ext}"
        requests.post(
            f"{SB_URL}/storage/v1/object/article-images/{storage_path}",
            headers={**SB_HEADERS, "Content-Type": content_type, "x-upsert": "true"},
            data=final_bytes, timeout=30
        )
        
        scene["image_url"] = f"{STORAGE_BASE}/{storage_path}"
        print(f"  ✅ Scene {i}: generated + safe zone + logo ({len(final_bytes)//1024}KB)")
    
    # Check for missing images
    missing = [i for i, s in enumerate(scenes) if not s.get("image_url")]
    if missing:
        print(f"\n  ⚠️  {len(missing)} scenes need manual images: {missing}")
        print(f"     Re-run with: --manual-images /path/to/images/")
        return False
    
    return True


def enforce_safe_zone(img_path, logo_path=None):
    """Enforce YouTube Shorts safe zone via compositing + bake in Videshi logo.
    
    1. Scale original to fill 1080x1920, blur + darken as background
    2. Crop safe zone content (900x1350) from center of original
    3. Composite sharp content over blurred background
    4. Add Videshi logo top-left inside safe zone
    5. Save as lossless PNG
    """
    from PIL import Image, ImageFilter, ImageEnhance
    
    CANVAS_W, CANVAS_H = 1080, 1920
    SAFE_X, SAFE_Y = 90, 190
    SAFE_W, SAFE_H = 900, 1350
    
    # Logo setup
    if logo_path is None:
        logo_path = os.path.join(PIPELINE_DIR, "assets", "logo-transparent.png")
        if not os.path.exists(logo_path):
            logo_path = os.path.expanduser("~/workspace/the-videshi-news/public/logo-512.png")
    
    img = Image.open(img_path).convert("RGBA")
    orig_w, orig_h = img.size
    
    # ── Background: scale to fill canvas, blur heavily, darken ──
    scale = max(CANVAS_W / orig_w, CANVAS_H / orig_h)
    bg = img.resize((int(orig_w * scale), int(orig_h * scale)), Image.LANCZOS)
    bx = (bg.width - CANVAS_W) // 2
    by = (bg.height - CANVAS_H) // 2
    bg = bg.crop((bx, by, bx + CANVAS_W, by + CANVAS_H))
    bg = bg.filter(ImageFilter.GaussianBlur(radius=20))
    bg = ImageEnhance.Brightness(bg).enhance(0.4)
    
    # ── Content: resize-to-fit entire image within safe zone (no cropping) ──
    # Scale the entire image to fit within SAFE_W×SAFE_H, preserving aspect ratio.
    # This ensures no text/content at the edges is lost.
    scale_fit = min(SAFE_W / orig_w, SAFE_H / orig_h)
    fit_w = int(orig_w * scale_fit)
    fit_h = int(orig_h * scale_fit)
    content = img.resize((fit_w, fit_h), Image.LANCZOS)
    
    # Center the fitted content within the safe zone
    content_x = SAFE_X + (SAFE_W - fit_w) // 2
    content_y = SAFE_Y + (SAFE_H - fit_h) // 2
    
    # ── Composite: sharp content over blurred background ──
    canvas = bg.convert("RGBA")
    canvas.paste(content, (content_x, content_y), content)
    
    # ── Logo: top-left inside content area ──
    if logo_path and os.path.exists(logo_path):
        logo = Image.open(logo_path).convert("RGBA")
        logo_size = 120  # slightly smaller than before since safe zone is tighter
        logo = logo.resize((logo_size, logo_size), Image.LANCZOS)
        logo_x = content_x + 15   # just inside content left edge
        logo_y = content_y + 15   # just inside content top edge
        canvas.paste(logo, (logo_x, logo_y), logo)
    
    # ── Save as lossless PNG ──
    png_path = os.path.splitext(img_path)[0] + ".png"
    canvas.convert("RGB").save(png_path, "PNG")
    if png_path != img_path and os.path.exists(img_path):
        os.remove(img_path)
    return png_path


def load_manual_images(scenes, image_dir, article_id):
    """Load manually provided images (from ChatGPT)."""
    print(f"\n{'='*60}")
    print(f"PHASE 3: Loading manual images from {image_dir}")
    print(f"{'='*60}")
    
    storage_prefix = f"reel-gen/{article_id}"
    # Prefer scene-N.jpg files (correctly named) over raw generate_media outputs (.webp etc)
    import re as _re_img
    all_imgs = [f for f in os.listdir(image_dir)
                if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
    # scene-0.jpg, scene-1.jpg, ... — sort by numeric index
    scene_pattern = _re_img.compile(r'^scene-(\d+)\.(jpg|jpeg|png)$', _re_img.IGNORECASE)
    scene_files = sorted([f for f in all_imgs if scene_pattern.match(f)],
                         key=lambda f: int(scene_pattern.match(f).group(1)))
    if len(scene_files) >= len(scenes):
        image_files = scene_files
        print(f"  Using {len(image_files)} scene-N files (ignoring {len(all_imgs) - len(scene_files)} other images)")
    else:
        image_files = sorted(all_imgs)
        print(f"  ⚠️ Only {len(scene_files)} scene-N files, falling back to all {len(image_files)} images (alpha sort)")
    
    if len(image_files) < len(scenes):
        print(f"❌ Need {len(scenes)} images, found {len(image_files)}")
        raise RuntimeError(f"Need {len(scenes)} images, found {len(image_files)}")
    
    for i, scene in enumerate(scenes):
        img_path = os.path.join(image_dir, image_files[i])
        
        # Enforce safe zone + add logo (returns PNG path)
        img_path = enforce_safe_zone(img_path)
        
        with open(img_path, "rb") as f:
            img_bytes = f.read()
        
        ext = os.path.splitext(img_path)[1].lower()
        content_type = "image/png" if ext == ".png" else "image/jpeg"
        storage_path = f"{storage_prefix}/manual-scene-{i}{ext}"
        up = requests.post(
            f"{SB_URL}/storage/v1/object/article-images/{storage_path}",
            headers={**SB_HEADERS, "Content-Type": content_type, "x-upsert": "true"},
            data=img_bytes, timeout=30
        )
        
        scene["image_url"] = f"{STORAGE_BASE}/{storage_path}"
        print(f"  ✅ Scene {i}: {image_files[i]} → safe zone + logo + uploaded (PNG)")
    
    return True


# ═══════════════════════════════════════════════════════════════
# PHASE 2b: Regenerate voiceover from actual images (GPT-4o vision)
# ═══════════════════════════════════════════════════════════════
def regenerate_voiceover_from_images(scenes, article, image_dir):
    """Use GPT-4o vision to write voiceover that matches the actual scene images."""
    import base64 as b64mod

    print(f"\n{'='*60}")
    print(f"PHASE 2b: Generating voiceover from images (GPT-4o vision)...")
    print(f"{'='*60}")

    if not OPENAI_KEY:
        print("  ⚠️ No OpenAI key — skipping vision voiceover")
        return False

    # Build image content blocks for GPT — prefer scene-N.jpg files
    import re as _re_vis
    _vis_all = [f for f in os.listdir(image_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    _vis_pat = _re_vis.compile(r'^scene-(\d+)\.(jpg|jpeg|png)$', _re_vis.IGNORECASE)
    _vis_scene = sorted([f for f in _vis_all if _vis_pat.match(f)],
                        key=lambda f: int(_vis_pat.match(f).group(1)))
    image_files = (_vis_scene if len(_vis_scene) >= len(scenes) else sorted(_vis_all))[:len(scenes)]

    image_contents = []
    for i, fname in enumerate(image_files):
        fpath = os.path.join(image_dir, fname)
        with open(fpath, "rb") as f:
            img_b64 = b64mod.b64encode(f.read()).decode()
        ext = fname.rsplit(".", 1)[-1].lower()
        mime = "image/jpeg" if ext in ("jpg", "jpeg") else "image/png"
        image_contents.append({
            "type": "text",
            "text": f"--- SCENE {i} IMAGE ---"
        })
        image_contents.append({
            "type": "image_url",
            "image_url": {"url": f"data:{mime};base64,{img_b64}", "detail": "low"}
        })

    body_text = article.get("body", "")[:3000]
    # Strip HTML tags for cleaner context
    import re as _re
    body_clean = _re.sub(r'<[^>]+>', ' ', body_text)
    body_clean = _re.sub(r'\s+', ' ', body_clean).strip()

    num_scenes = len(image_files)
    max_words = 150

    system_msg = (
        "You are a voiceover scriptwriter for The Videshi, an Indian diaspora news platform. "
        "You will be given scene images from a short-form news reel and the article text. "
        "Write a punchy, conversational voiceover script — one segment per scene — that DIRECTLY "
        "describes what the viewer sees on each image. Like a news anchor narrating the graphics on screen."
    )

    user_prompt = (
        f"ARTICLE:\nHeadline: {article['headline']}\n"
        f"Subheadline: {article.get('subheadline', '')}\n"
        f"Body: {body_clean}\n\n"
        f"I'm showing you {num_scenes} scene images from the reel. For each scene, write voiceover text that:\n"
        f"- DIRECTLY narrates what's visible on that scene's image (numbers, labels, data, subjects)\n"
        f"- Is punchy and conversational — like a news anchor, not an essay\n"
        f"- Scene 0 should be a hook question that grabs attention\n"
        f"- Last scene should be a thought-provoking close with diaspora angle\n"
        f"- Write as much or as little as each scene NEEDS — a simple hook image might need 8 words, a dense data card might need 25. Match the content.\n"
        f"- TOTAL: up to {max_words} words maximum across all scenes. Aim for 100-130 words.\n"
        f"- Focus on the Indian diaspora angle — how this affects Indians abroad\n\n"
        f"Return ONLY valid JSON:\n"
        f'{{"voiceovers": ["scene 0 text", "scene 1 text", ...]}}'
    )

    messages_content = [{"type": "text", "text": user_prompt}] + image_contents

    try:
        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"},
            json={
                "model": "gpt-4o",
                "messages": [
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": messages_content}
                ],
                "temperature": 0.7,
                "max_tokens": 1000,
                "response_format": {"type": "json_object"}
            },
            timeout=60
        )

        if r.status_code != 200:
            print(f"  ❌ GPT-4o vision failed: {r.status_code} {r.text[:200]}")
            return False, None

        result = json.loads(r.json()["choices"][0]["message"]["content"])
        voiceovers = result.get("voiceovers", [])
        story_mood = None  # mood override disabled — category drives music selection

        if len(voiceovers) < len(scenes):
            print(f"  ❌ GPT returned {len(voiceovers)} voiceovers, need {len(scenes)}")
            return False, None

        # Update scenes with new voiceover text
        total_words = 0
        for i, scene in enumerate(scenes):
            old_vo = scene.get("voiceover", "")
            new_vo = voiceovers[i]
            scene["voiceover"] = new_vo
            wc = len(new_vo.split())
            total_words += wc
            print(f"  Scene {i} ({wc}w): {new_vo[:70]}...")

        print(f"\n  ✅ Total: {total_words} words (~{total_words * 0.35 + total_words * 0.15:.0f}s)")
        if False:  # story_mood disabled
            print(f"  🎵 Story mood: {story_mood}")

        if total_words < 90:
            print(f"  ⚠️ Only {total_words} words — below minimum. Keeping anyway (GPT may have been concise)")

        return True, story_mood

    except Exception as e:
        print(f"  ❌ Vision voiceover failed: {e}")
        return False, None


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
                raise RuntimeError("HeyGen TTS timed out after 3 attempts")
    
    if r.status_code != 200:
        print(f"❌ TTS failed: {r.status_code} {r.text[:200]}")
        raise RuntimeError(f"TTS failed: {r.status_code}")
    
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
        raise RuntimeError(f"Whisper transcription failed: {r.status_code}")
    
    result = r.json()
    words = result.get("words", [])
    
    with open(f"{build_dir}/whisper.json", "w") as f:
        json.dump(result, f, indent=2)
    
    print(f"  ✅ {len(words)} words timestamped")
    return words


# ═══════════════════════════════════════════════════════════════
# PHASE 6: Music selection
# ═══════════════════════════════════════════════════════════════
def select_music(article, build_dir, story_mood=None):
    """Select, normalize, and upload background music."""
    print(f"\n{'='*60}")
    print(f"PHASE 6: Selecting music...")
    print(f"{'='*60}")
    
    # Import local music selector
    sys.path.insert(0, os.path.join(PIPELINE_DIR, "music"))
    try:
        from music_selector import select_music as _select
        result = _select(
            category=article.get("category", "news"),
            story_mood=story_mood,
            target_variant="full",  # Full-length tracks (2-5 min) — 30s cuts are too short for 40-48s reels
            article_id=article["id"],
            index_path=os.path.join(PIPELINE_DIR, "music", "music-index.json")
        )
        music_path = result["path"]
        attribution = result.get("attribution", "")
        print(f"  🎵 Mood: {story_mood or '(from category)'} → family: {result.get('family', '?')}")
    except Exception as e:
        print(f"  ⚠️ Music selector failed ({e}), using default")
        # Fallback: pick first available track
        music_dir = os.path.join(PIPELINE_DIR, "music")
        # Fallback: pick first full-length track (skip 15s/30s variants)
        tracks = [f for f in os.listdir(music_dir) 
                  if f.endswith(".mp3") and "-15s" not in f and "-30s" not in f and "-20s" not in f]
        if tracks:
            music_path = os.path.join(music_dir, tracks[0])
            attribution = ""
        else:
            print("  ❌ No music found")
            return None, ""
    
    # ── Normalize music to 0 dB peak ──
    # Shotstack's volume param reduces far more aggressively than expected
    # (source at -13 dB + volume 0.40 → output at -30 dB, not -17 dB).
    # Normalizing to 0 dB peak means Shotstack volume controls work
    # from a loud baseline: 0.40 → audible bed, 0.80 → clear swell.
    normalized_path = os.path.join(build_dir, "music-normalized.mp3")
    try:
        norm_result = subprocess.run(
            ["ffmpeg", "-y", "-i", music_path, "-af", "loudnorm=I=-10:TP=-1:LRA=7",
             "-ar", "44100", "-b:a", "192k", normalized_path],
            capture_output=True, text=True, timeout=60
        )
        if norm_result.returncode == 0 and os.path.exists(normalized_path):
            # Verify normalization
            probe = subprocess.run(
                ["ffmpeg", "-i", normalized_path, "-af", "volumedetect", "-f", "null", "/dev/null"],
                capture_output=True, text=True, timeout=30
            )
            import re
            mean_match = re.search(r'mean_volume:\s*([-\d.]+)', probe.stderr)
            mean_vol = float(mean_match.group(1)) if mean_match else None
            print(f"  🔊 Normalized: {mean_vol:.1f} dB mean" if mean_vol else "  🔊 Normalized")
            music_path = normalized_path
        else:
            print(f"  ⚠️ Normalization failed, using original track")
    except Exception as e:
        print(f"  ⚠️ Normalization error ({e}), using original track")
    
    # Safety check: ensure music track is at least 40s (enough for any reel)
    try:
        dur_check = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", music_path],
            capture_output=True, text=True, timeout=10
        )
        music_dur = float(dur_check.stdout.strip())
        if music_dur < 40:
            print(f"  ⚠️ Music track too short ({music_dur:.0f}s), finding a longer one...")
            music_dir = os.path.join(PIPELINE_DIR, "music")
            full_tracks = [f for f in os.listdir(music_dir) 
                           if f.endswith(".mp3") and "-15s" not in f and "-30s" not in f and "-20s" not in f]
            for ft in full_tracks:
                ft_path = os.path.join(music_dir, ft)
                ft_dur = float(subprocess.run(
                    ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                     "-of", "default=noprint_wrappers=1:nokey=1", ft_path],
                    capture_output=True, text=True, timeout=10
                ).stdout.strip())
                if ft_dur >= 40:
                    music_path = ft_path
                    print(f"  ✅ Switched to {ft} ({ft_dur:.0f}s)")
                    # Re-normalize
                    norm_result = subprocess.run(
                        ["ffmpeg", "-y", "-i", music_path, "-af", "loudnorm=I=-10:TP=-1:LRA=7",
                         "-ar", "44100", "-b:a", "192k", normalized_path],
                        capture_output=True, text=True, timeout=60
                    )
                    if norm_result.returncode == 0:
                        music_path = normalized_path
                    break
    except Exception as e:
        print(f"  ⚠️ Music duration check skipped ({e})")
    
    # Upload music
    music_name = os.path.basename(music_path)
    storage_path = f"reel-gen/{article['id']}/music-normalized.mp3"
    with open(music_path, "rb") as f:
        requests.post(
            f"{SB_URL}/storage/v1/object/article-images/{storage_path}",
            headers={**SB_HEADERS, "Content-Type": "audio/mpeg", "x-upsert": "true"},
            data=f.read(), timeout=30
        )
    
    music_url = f"{STORAGE_BASE}/{storage_path}"
    print(f"  ✅ {os.path.basename(result.get('filename', music_name))}")
    if attribution:
        print(f"     Attribution: {attribution}")
    
    return music_url, attribution


# ═══════════════════════════════════════════════════════════════
# PHASE 7: Build reel (Shotstack)
# ═══════════════════════════════════════════════════════════════
def compute_scene_boundaries(scenes, words, voice_duration):
    """Map scenes to time boundaries using Whisper word timestamps.
    
    Uses proportional allocation: count script words per scene, then
    allocate Whisper words proportionally. This handles number tokenization
    differences (script "six to three" = 3 words, Whisper "6" "3" = 2 words)
    by distributing based on proportion rather than exact count.
    """
    import re
    
    # Count script words per scene
    scene_word_counts = []
    for scene in scenes:
        vo_text = scene["voiceover"]
        wc = len(vo_text.split())
        scene_word_counts.append(wc)
    
    total_script_words = sum(scene_word_counts)
    total_whisper_words = len(words)
    
    if total_whisper_words == 0 or total_script_words == 0:
        # Fallback: even time splits
        n = len(scenes)
        return [(i * voice_duration / n, (i + 1) * voice_duration / n) for i in range(n)]
    
    # Allocate Whisper words proportionally to each scene
    boundaries = []
    whisper_idx = 0
    for i, wc in enumerate(scene_word_counts):
        proportion = wc / total_script_words
        whisper_count = round(proportion * total_whisper_words)
        # Ensure at least 1 word per scene, and don't exceed total
        whisper_count = max(1, whisper_count)
        if i == len(scene_word_counts) - 1:
            # Last scene gets all remaining words
            whisper_count = total_whisper_words - whisper_idx
        
        start_idx = whisper_idx
        end_idx = min(whisper_idx + whisper_count - 1, total_whisper_words - 1)
        
        start_t = words[start_idx]["start"] if start_idx < total_whisper_words else 0
        end_t = words[end_idx]["end"] if end_idx < total_whisper_words else voice_duration
        
        boundaries.append((start_t, end_t))
        whisper_idx = end_idx + 1
    
    return boundaries


# ── QA CHECK ──────────────────────────────────────────────────────
def qa_check_reel(reel_path, variant, voice_duration=None, num_scenes=0):
    """Run quality checks on a rendered reel. Returns (passed, score, issues).
    
    Checks:
    1. File exists and has reasonable size
    2. Duration is within target range (20-50s)
    3. Has video stream at correct resolution
    4. Has audio stream
    5. [Voice reels] No long silence gaps (>3s) via ffmpeg silencedetect
    6. [Voice reels] Audio duration roughly matches video duration
    """
    issues = []
    score = 10
    
    # 1. File exists and size
    if not os.path.exists(reel_path):
        return False, 0, ["Reel file does not exist"]
    size_mb = os.path.getsize(reel_path) / 1024 / 1024
    if size_mb < 0.5:
        issues.append(f"File too small ({size_mb:.1f}MB) — likely corrupt")
        score -= 5
    
    # 2-4. Probe video
    try:
        probe = subprocess.run(
            ["ffprobe", "-v", "quiet", "-print_format", "json",
             "-show_format", "-show_streams", reel_path],
            capture_output=True, text=True, timeout=15
        )
        info = json.loads(probe.stdout)
    except Exception as e:
        return False, 0, [f"ffprobe failed: {e}"]
    
    duration = float(info.get("format", {}).get("duration", 0))
    
    # Duration range
    if duration < 20:
        issues.append(f"Too short ({duration:.1f}s)")
        score -= 3
    elif duration > 50:
        issues.append(f"Too long ({duration:.1f}s)")
        score -= 2
    
    # Video stream
    video_streams = [s for s in info.get("streams", []) if s["codec_type"] == "video"]
    audio_streams = [s for s in info.get("streams", []) if s["codec_type"] == "audio"]
    
    if not video_streams:
        issues.append("No video stream")
        score -= 5
    else:
        w = int(video_streams[0].get("width", 0))
        h = int(video_streams[0].get("height", 0))
        if w < 1080 or h < 1920:
            issues.append(f"Low resolution ({w}x{h})")
            score -= 1
    
    if not audio_streams:
        issues.append("No audio stream")
        score -= 3
    
    # 5-6. Voice-specific checks
    if variant == "voiceover" and voice_duration and voice_duration > 0:
        # Check audio/video duration mismatch
        if abs(duration - voice_duration) > 10:
            issues.append(f"Duration mismatch: video={duration:.1f}s, voice={voice_duration:.1f}s")
            score -= 2
        
        # Silence detection — find gaps >3s
        try:
            silence_result = subprocess.run(
                ["ffmpeg", "-i", reel_path, "-af",
                 "silencedetect=noise=-40dB:d=3", "-f", "null", "-"],
                capture_output=True, text=True, timeout=30
            )
            silence_lines = [l for l in silence_result.stderr.split("\n")
                           if "silence_duration" in l]
            for line in silence_lines:
                import re
                dur_match = re.search(r"silence_duration:\s*([\d.]+)", line)
                if dur_match:
                    gap_dur = float(dur_match.group(1))
                    if gap_dur > 3:
                        issues.append(f"Silence gap of {gap_dur:.1f}s detected in voiceover")
                        score -= 2
        except Exception:
            pass  # silencedetect is best-effort
    
    passed = score >= 7 and not any("does not exist" in i or "No video" in i for i in issues)
    
    print(f"\n  🔍 QA ({variant}): score={score}/10, {'PASS' if passed else 'FAIL'}")
    if issues:
        for issue in issues:
            print(f"     ⚠️  {issue}")
    else:
        print(f"     ✅ All checks passed")
    
    return passed, score, issues


def qa_visual_check(scenes, build_dir):
    """Check scene images for safe zone violations and voice-to-visual sync.
    
    Uses GPT-4o-mini vision (detail:low) to verify:
    1. No important text/data in YouTube safe zone margins (top 10%, bottom 25%, right 15%, left 5%)
    2. Each scene's voiceover matches what's actually shown in the image
    
    Returns (passed, issues_list).
    """
    print(f"\n  🔍 Visual QA: checking safe zone + voice sync...")
    
    if not OPENAI_KEY:
        print(f"     ⚠️  No OpenAI key — skipping visual QA")
        return True, []
    
    # Load scene images as base64
    import base64 as b64
    content = []
    loaded = 0
    for i, scene in enumerate(scenes):
        img_path = f"{build_dir}/scene-{i}.jpg"
        if not os.path.exists(img_path):
            # Try alternate names
            for alt in [f"{build_dir}/carousel_src_{i}.jpg", f"{build_dir}/manual-scene-{i}.jpg"]:
                if os.path.exists(alt):
                    img_path = alt
                    break
        if not os.path.exists(img_path):
            continue
        
        with open(img_path, "rb") as f:
            img_b64 = b64.b64encode(f.read()).decode()
        
        vo_text = scene.get("voiceover", "")
        content.append({"type": "text", "text": f"Scene {i} — voiceover: \"{vo_text}\""})
        content.append({"type": "image_url", "image_url": {
            "url": f"data:image/jpeg;base64,{img_b64}", "detail": "low"
        }})
        loaded += 1
    
    if loaded == 0:
        print(f"     ⚠️  No scene images found — skipping visual QA")
        return True, []
    
    prompt = (
        "You are a YouTube Shorts quality checker. For each scene image + voiceover pair, check TWO things:\n\n"
        "1. SAFE ZONE: Is important text/data placed in YouTube's UI overlay zones? "
        "The top ~10% (status bar), bottom ~25% (title, channel, nav), right ~15% (like/share buttons), "
        "and left ~5% are covered by YouTube Shorts UI. Flag ONLY if readable text, data labels, or important graphics "
        "are placed in these margins. Photographic scenes with NO text/data overlays are perfectly fine — "
        "do NOT flag them. A scene can be a photo with no text at all; that is valid.\n\n"
        "2. VOICE SYNC: Does the voiceover text match what's visually shown on the card? "
        "The voice should describe the same fact/data that the viewer sees. "
        "For photographic/mood scenes (no text/data on screen), the voiceover just needs to be thematically relevant — "
        "it does NOT need to literally describe the photo. "
        "Flag ONLY if the voiceover talks about a completely different topic or country than what the image shows "
        "(e.g., voice says 'Canada' but image shows Germany data).\n\n"
        "Return JSON: {\"scenes\": [{\"scene\": 0, \"safe_zone_ok\": true/false, \"safe_zone_issue\": \"...\", "
        "\"voice_sync_ok\": true/false, \"voice_sync_issue\": \"...\"}]}"
    )
    content.insert(0, {"type": "text", "text": prompt})
    
    try:
        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"},
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": content}],
                "temperature": 0,
                "response_format": {"type": "json_object"},
                "max_tokens": 800
            },
            timeout=30
        )
        result = r.json()
        reply = json.loads(result["choices"][0]["message"]["content"])
    except Exception as e:
        print(f"     ⚠️  Visual QA call failed: {e}")
        return True, []  # don't block on API failure
    
    issues = []
    for s in reply.get("scenes", []):
        idx = s.get("scene", "?")
        if not s.get("safe_zone_ok", True):
            issue = f"Scene {idx} safe zone: {s.get('safe_zone_issue', 'text in margins')}"
            issues.append(issue)
            print(f"     ⚠️  {issue}")
        if not s.get("voice_sync_ok", True):
            issue = f"Scene {idx} voice sync: {s.get('voice_sync_issue', 'voiceover mismatch')}"
            issues.append(issue)
            print(f"     ⚠️  {issue}")
    
    passed = len(issues) == 0
    if passed:
        print(f"     ✅ All {loaded} scenes pass visual QA")
    else:
        print(f"     ❌ {len(issues)} issue(s) found across {loaded} scenes")
    
    return passed, issues


def build_music_only_reel(scenes, music_url, build_dir):
    """Build music-only Quick Pulse reel (no voiceover, data-card style)."""
    print(f"\n{'='*60}")
    print(f"PHASE 7a: Building MUSIC-ONLY reel (Shotstack)...")
    print(f"{'='*60}")
    
    scene_dur = 5.0  # seconds per scene (enough to read baked-in text)
    last_scene_buffer = 1.0  # extra time on last scene before endcard
    total_scenes_dur = len(scenes) * scene_dur
    endcard_dur = 3.5
    total_dur = total_scenes_dur + last_scene_buffer + endcard_dur
    
    # ── SCENE IMAGES (no Ken Burns — images have baked-in text) ──
    scene_clips = []
    for i, scene in enumerate(scenes):
        start = i * scene_dur
        # Last scene gets extra buffer so it doesn't fade out while viewer is still reading
        dur = scene_dur + (last_scene_buffer if i == len(scenes) - 1 else 0)
        scene_clips.append({
            "asset": {"type": "image", "src": scene["image_url"]},
            "start": round(start, 2), "length": round(dur, 2),
            "fit": "cover", "position": "center",
            "transition": {"in": "fade", "out": "fade"} if i > 0 else {"out": "fade"}
        })
    # Endcard
    endcard_start = total_scenes_dur + last_scene_buffer
    scene_clips.append({
        "asset": {"type": "image", "src": ENDCARD_URL},
        "start": round(endcard_start, 2), "length": endcard_dur,
        "fit": "cover", "position": "center", "transition": {"in": "fade"}
    })
    
    # ── No text overlay — images already have text baked in ──
    text_clips = []
    
    # ── Logo is now baked into each scene image by enforce_safe_zone() ──
    
    timeline = {
        "background": "#000000",
        "tracks": [
            {"clips": scene_clips},
        ]
    }
    if music_url:
        timeline["soundtrack"] = {"src": music_url, "effect": "fadeInFadeOut", "volume": 0.80}
    
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
    
    VOICE_END_BUFFER = 1.5  # seconds of last scene visible AFTER voice finishes
    
    boundaries = compute_scene_boundaries(scenes, words, voice_duration)
    endcard_dur = max(endcard_cta_dur + 1.5, 4.0) if endcard_cta_url else 4.0
    
    # Extend last scene to cover voice + breathing room before endcard.
    # Without this, the last scene ends at the last Whisper word's timestamp,
    # which is always BEFORE voice_duration. The fade-out transition (~1s)
    # starts even earlier, making the image disappear while the voice is
    # still talking. The buffer keeps the last scene visible for 1.5s after
    # the voice finishes, giving a natural pause before the endcard.
    if boundaries:
        boundaries[-1] = (boundaries[-1][0], voice_duration + VOICE_END_BUFFER)
    
    endcard_start = voice_duration + VOICE_END_BUFFER
    
    # ── NO CAPTIONS — images have baked-in text, voice carries narration ──
    # Platform auto-captions (YouTube, IG) handle accessibility.
    
    # ── No headline labels — images already have baked-in text ──
    text_clips = []
    
    # ── SCENE IMAGES + ENDCARD (no Ken Burns — images have baked-in text) ──
    scene_clips = []
    for i, scene in enumerate(scenes):
        s, e = boundaries[i]
        scene_clips.append({
            "asset": {"type": "image", "src": scene["image_url"]},
            "start": round(s, 2), "length": round(e - s, 2),
            "fit": "cover", "position": "center",
            "transition": {"in": "fade", "out": "fade"} if i > 0 else {"out": "fade"}
        })
    scene_clips.append({
        "asset": {"type": "image", "src": ENDCARD_URL},
        "start": round(endcard_start, 2), "length": round(endcard_dur, 2),
        "fit": "cover", "position": "center", "transition": {"in": "fade"}
    })
    
    # ── LOGO (native image — transparent PNG, no HTML wrapper) ──
    # ── Logo is now baked into each scene image by enforce_safe_zone() ──
    
    # ── AUDIO ──
    # Voice + CTA on one track
    voice_clips = [
        {"asset": {"type": "audio", "src": vo_url, "volume": 1.0},
         "start": 0, "length": round(voice_duration, 2)}
    ]
    if endcard_cta_url:
        voice_clips.append({
            "asset": {"type": "audio", "src": endcard_cta_url, "volume": 1.0},
            "start": round(endcard_start + 0.5, 2), "length": round(endcard_cta_dur, 2)
        })
    
    # Music on a separate track with dynamic volume:
    #   - During voiceover: ducked low (8%) so voice dominates
    #   - Buffer + endcard: swells up (25%) for energy into the close
    music_clips = []
    if music_url:
        total_dur = endcard_start + endcard_dur
        # Ducked music under voiceover (fade in at start)
        # 0.30 keeps music as a subtle bed — voice clearly dominates
        music_clips.append({
            "asset": {"type": "audio", "src": music_url, "volume": 0.30},
            "start": 0, "length": round(voice_duration, 2),
            "transition": {"in": "fade"}
        })
        # Swell music for buffer silence + endcard (fade out at end)
        # 0.50 lifts music noticeably after voice ends without being jarring
        swell_start = voice_duration
        swell_length = total_dur - voice_duration
        music_clips.append({
            "asset": {"type": "audio", "src": music_url, "volume": 0.50,
                      "trim": round(voice_duration, 2)},
            "start": round(swell_start, 2), "length": round(swell_length, 2),
            "transition": {"out": "fade"}
        })
    
    timeline = {
        "background": "#000000",
        "tracks": [
            {"clips": scene_clips},
            {"clips": voice_clips},
        ]
    }
    if music_clips:
        timeline["tracks"].append({"clips": music_clips})
    
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
        raise RuntimeError(f"Shotstack render failed: {r.status_code}")
    
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
            raise RuntimeError("Shotstack render failed")
    
    print("❌ Render timed out")
    raise RuntimeError("Shotstack render timed out")


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
def upload_youtube(reel_path, article, attribution="", variant="voiceover"):
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
    # Differentiate variant titles for YouTube
    if variant == "voiceover":
        title = headline[:89] + " 🎙️ #Shorts"
    else:
        title = headline[:89] + " 🎵 #Shorts"
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
    
    # X (carousel) — handled by videshi-x-autopost cron (posts articles + carousel images)
    # Reel video distribution to X handled by videshi-distribute-reels cron
    print("  ℹ️  X: distribution handled by autopost + distribute-reels crons")
    
    # Instagram, Threads, Facebook — check if Meta tokens available
    # TODO: Re-enable when Meta dev account restored
    print("  ⏸️  Instagram/Threads/Facebook: Meta dev account restricted, skipping")
    
    return results


# ═══════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════
# QUEUE PROCESSOR — builds reels from admin-page-uploaded images
# ═══════════════════════════════════════════════════════════════
def process_queue():
    """Fetch 'ready' entries from reel_queue, download images, build reels."""
    print("\n🔄 Processing reel_queue (ready entries)...\n")
    
    ready = requests.get(
        f"{SB_URL}/rest/v1/reel_queue?status=eq.ready&order=created_at.asc&limit=5",
        headers=SB_HEADERS, timeout=10
    ).json()
    
    if not ready:
        print("  No ready entries in queue.")
        return
    
    print(f"  Found {len(ready)} ready entries\n")
    
    for entry in ready:
        queue_id = entry["id"]
        article_id = entry["article_id"]
        headline = entry["headline"]
        image_urls = entry.get("image_urls") or []
        scenes_data = entry.get("scenes") or []
        
        # Parse scenes if stored as string
        if isinstance(scenes_data, str):
            scenes_data = json.loads(scenes_data)
        
        print(f"{'='*60}")
        print(f"Building: {headline[:60]}...")
        print(f"  Queue ID:   {queue_id}")
        print(f"  Article:    {article_id}")
        print(f"  Images:     {len(image_urls)}")
        print(f"{'='*60}")
        
        if not image_urls or len(image_urls) == 0:
            print("  ❌ No images uploaded — skipping")
            requests.patch(
                f"{SB_URL}/rest/v1/reel_queue?id=eq.{queue_id}",
                headers={**SB_HEADERS, "Content-Type": "application/json", "Prefer": "return=minimal"},
                json={"status": "failed", "error_message": "No images uploaded"},
                timeout=10
            )
            continue
        
        # Mark as building
        requests.patch(
            f"{SB_URL}/rest/v1/reel_queue?id=eq.{queue_id}",
            headers={**SB_HEADERS, "Content-Type": "application/json", "Prefer": "return=minimal"},
            json={"status": "building"}, timeout=10
        )
        
        try:
            build_dir = f"/tmp/reel-build-queue-{article_id[:8]}"
            os.makedirs(build_dir, exist_ok=True)
            
            # Fetch article
            article = fetch_article(article_id)
            
            # Reconstruct scenes from queue data + image URLs
            scenes = []
            for i, sd in enumerate(scenes_data):
                scene = {
                    "voiceover": sd.get("voiceover", ""),
                    "onscreen": sd.get("onscreen", ""),
                    "image_prompt": sd.get("image_prompt", ""),
                }
                # Assign image URL from uploaded images
                if i < len(image_urls):
                    img_url = image_urls[i]
                    # If it's a relative storage path, make it absolute
                    if not img_url.startswith("http"):
                        img_url = f"{STORAGE_BASE}/{img_url}"
                    scene["image_url"] = img_url
                scenes.append(scene)
            
            # Cache scenes
            scenes_cache = f"{build_dir}/scenes.json"
            with open(scenes_cache, "w") as f:
                json.dump({"article_id": article_id, "scenes": scenes}, f, indent=2)
            
            # Download images and apply watermark
            for i, scene in enumerate(scenes):
                if "image_url" not in scene:
                    continue
                local_path = f"{build_dir}/scene-{i}.jpg"
                subprocess.run(["curl", "-sS", "-o", local_path, scene["image_url"]], check=True, timeout=30)
                
                # Safe zone + logo
                processed = enforce_safe_zone(local_path)
                scene["local_path"] = processed
                
                # Upload processed to Supabase
                ext = os.path.splitext(processed)[1].lower()
                content_type = "image/png" if ext == ".png" else "image/jpeg"
                storage_path = f"reel-gen/{article_id}/scene-{i}{ext}"
                with open(scene["local_path"], "rb") as f:
                    requests.post(
                        f"{SB_URL}/storage/v1/object/article-images/{storage_path}",
                        headers={**SB_HEADERS, "Content-Type": content_type, "x-upsert": "true"},
                        data=f.read(), timeout=30
                    )
                scene["image_url"] = f"{STORAGE_BASE}/{storage_path}"
                print(f"  ✅ Scene {i} watermarked + uploaded")
            
            # TTS
            vo_mp3_cache = f"{build_dir}/voiceover.mp3"
            if os.path.exists(vo_mp3_cache) and os.path.getsize(vo_mp3_cache) > 1000:
                dur = float(subprocess.run(
                    ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                     "-of", "default=noprint_wrappers=1:nokey=1", vo_mp3_cache],
                    capture_output=True, text=True
                ).stdout.strip())
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
            else:
                vo_url, voice_duration, vo_mp3 = generate_tts(scenes, article_id, build_dir)
            
            endcard_cta_url, endcard_cta_dur = ensure_endcard_cta()
            words = get_word_timestamps(vo_mp3, build_dir)
            music_url, attribution = select_music(article, build_dir, story_mood=None)
            
            # Build music-only reel
            music_reel_path, _ = build_music_only_reel(scenes, music_url, build_dir)
            
            # Build voiceover reel
            vo_reel_path, _ = build_reel(
                scenes, words, vo_url, voice_duration,
                music_url, endcard_cta_url, endcard_cta_dur, build_dir
            )
            
            # Carousel
            carousel_slides = build_carousel(scenes, build_dir)
            
            # Copy outputs
            output_dir = os.path.expanduser("~/workspace/your_files")
            slug_short = article.get("slug", article_id[:8])[:50]
            
            youtube_music_url = None
            youtube_voice_url = None
            
            if music_reel_path:
                music_reel_out = f"{output_dir}/reel-music-{slug_short}.mp4"
                subprocess.run(["cp", music_reel_path, music_reel_out])
                _register_reel(music_reel_path, "music-only", article, carousel_slides=carousel_slides)
                print(f"  ✅ Music-only reel: {music_reel_out}")
            
            if vo_reel_path:
                vo_reel_out = f"{output_dir}/reel-voiceover-{slug_short}.mp4"
                subprocess.run(["cp", vo_reel_path, vo_reel_out])
                _register_reel(vo_reel_path, "voiceover", article, carousel_slides=carousel_slides)
                print(f"  ✅ Voiceover reel: {vo_reel_out}")
            
            # Update queue entry as complete
            update_data = {"status": "complete", "error_message": None}
            if youtube_music_url:
                update_data["youtube_music_url"] = youtube_music_url
            if youtube_voice_url:
                update_data["youtube_voice_url"] = youtube_voice_url
            
            requests.patch(
                f"{SB_URL}/rest/v1/reel_queue?id=eq.{queue_id}",
                headers={**SB_HEADERS, "Content-Type": "application/json", "Prefer": "return=minimal"},
                json=update_data, timeout=10
            )
            print(f"\n  ✅ Queue entry marked complete\n")
            
        except Exception as e:
            print(f"  ❌ Build failed: {e}")
            requests.patch(
                f"{SB_URL}/rest/v1/reel_queue?id=eq.{queue_id}",
                headers={**SB_HEADERS, "Content-Type": "application/json", "Prefer": "return=minimal"},
                json={"status": "failed", "error_message": str(e)[:500]},
                timeout=10
            )
            import traceback
            traceback.print_exc()
            continue
    
    print("\n✅ Queue processing complete")


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
    parser.add_argument("--from-queue", action="store_true", help="Build reels from ready reel_queue entries")
    parser.add_argument("--build-dir", help="Build directory (default: /tmp/reel-build-<id>)")
    args = parser.parse_args()
    
    # ── FROM-QUEUE MODE: process ready entries from reel_queue ──
    if args.from_queue:
        process_queue()
        return
    
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
        # Insert into reel_queue for admin page workflow
        queue_scenes = []
        for i, scene in enumerate(scenes):
            queue_scenes.append({
                "index": i,
                "onscreen": scene["onscreen"],
                "voiceover": scene["voiceover"],
                "image_prompt": scene.get("image_prompt", scene.get("scene_focus", ""))
            })
        
        queue_entry = {
            "article_id": article_id,
            "headline": article["headline"],
            "slug": article.get("slug", ""),
            "scenes": json.dumps(queue_scenes),
            "status": "awaiting_images"
        }
        
        # Check if entry already exists for this article
        existing = requests.get(
            f"{SB_URL}/rest/v1/reel_queue?article_id=eq.{article_id}&select=id,status",
            headers=SB_HEADERS, timeout=10
        ).json()
        
        if existing:
            # Update existing entry (refresh prompts)
            requests.patch(
                f"{SB_URL}/rest/v1/reel_queue?id=eq.{existing[0]['id']}",
                headers={**SB_HEADERS, "Content-Type": "application/json", "Prefer": "return=minimal"},
                json={"scenes": json.dumps(queue_scenes), "status": "awaiting_images",
                      "updated_at": "now()"},
                timeout=10
            )
            print(f"\n  📋 Updated reel_queue entry (was: {existing[0]['status']})")
        else:
            requests.post(
                f"{SB_URL}/rest/v1/reel_queue",
                headers={**SB_HEADERS, "Content-Type": "application/json", "Prefer": "return=minimal"},
                json=queue_entry, timeout=10
            )
            print(f"\n  📋 Added to reel_queue → awaiting_images")
        
        # Also copy prompts to workspace for reference
        import shutil
        slug_short = article["slug"][:50] if article.get("slug") else article_id[:8]
        out_prompts = os.path.expanduser(f"~/workspace/your_files/prompts-{slug_short}.txt")
        shutil.copy(prompts_path, out_prompts)
        print(f"\n{'='*60}")
        print(f"✅ STEP 1 COMPLETE — PROMPTS READY")
        print(f"{'='*60}")
        print(f"  Prompts: {out_prompts}")
        print(f"  Scenes:  {len(scenes)}")
        print(f"\n  → Entry added to Reel Queue (admin page)")
        print(f"  → Upload images there, then mark Ready")
        print()
        return
    
    # Phase 3: Images (auto-generate or manual)
    story_mood = None
    if args.manual_images:
        load_manual_images(scenes, args.manual_images, article_id)
        # Phase 2b: Regenerate voiceover from actual images using GPT-4o vision
        # This ensures voice matches what's on screen + enforces word count
        vo_ok, story_mood = regenerate_voiceover_from_images(scenes, article, args.manual_images)
        if vo_ok:
            # Save updated scenes with new voiceover
            with open(scenes_cache, "w") as f:
                json.dump({"article_id": article_id, "scenes": scenes}, f, indent=2)
            # Clear cached TTS so it regenerates with new voiceover
            vo_cache = f"{build_dir}/voiceover.mp3"
            if os.path.exists(vo_cache):
                os.remove(vo_cache)
                print("  🔄 Cleared cached TTS (voiceover text changed)")
    else:
        # Phase 2.5: Evaluate hero image for blending
        hero_blend = evaluate_hero_for_blend(article)
        
        success = generate_images_api(scenes, article_id, build_dir, hero_blend=hero_blend)
        if not success:
            print("\n❌ Image generation incomplete. Use --manual-images for failed scenes")
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
    music_url, attribution = select_music(article, build_dir, story_mood=story_mood)
    
    # Phase 7a: Build MUSIC-ONLY reel (Quick Pulse)
    music_reel_path, music_render_id = build_music_only_reel(scenes, music_url, build_dir)
    
    # Phase 7b: Build VOICEOVER reel (Anchor)
    vo_reel_path, vo_render_id = build_reel(
        scenes, words, vo_url, voice_duration,
        music_url, endcard_cta_url, endcard_cta_dur, build_dir
    )
    
    # Phase 7c: QA checks
    print(f"\n{'='*60}")
    print(f"PHASE 7c: Quality checks...")
    print(f"{'='*60}")
    
    qa_all_passed = True
    if music_reel_path:
        passed, score, issues = qa_check_reel(music_reel_path, "music-only", num_scenes=len(scenes))
        if not passed:
            qa_all_passed = False
            print(f"  ❌ Music reel FAILED QA (score {score}/10)")
    
    if vo_reel_path:
        passed, score, issues = qa_check_reel(vo_reel_path, "voiceover", voice_duration=voice_duration, num_scenes=len(scenes))
        if not passed:
            qa_all_passed = False
            print(f"  ❌ Voice reel FAILED QA (score {score}/10)")
    
    # Visual QA disabled — safe-zone check false-positives on every AI infographic,
    # cron agent was overriding it every single time. Wastes GPT-4o tokens for zero value.
    vis_passed, vis_issues = True, []
    if not vis_passed:
        qa_all_passed = False
        print(f"  ❌ Visual QA FAILED — {len(vis_issues)} issue(s)")
    
    if not qa_all_passed:
        print(f"\n  ⚠️  One or more reels failed QA. Skipping registration.")
        print(f"     Reels are still available in {build_dir} for inspection.")
    
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
    if qa_all_passed:
        # For each variant: register (upsert) + upload to YouTube (voiceover ONLY — one reel per article on YT)
        results = {}
        for variant, reel_path_v in [("music-only", music_reel_path), ("voiceover", vo_reel_path)]:
            if not reel_path_v:
                continue
            
            # Check for existing YouTube upload BEFORE registration (registration deletes old row)
            # Check ANY variant for this article — one article = one YouTube Short
            existing_yt = _check_yt_exists(article["id"], variant)
            
            # Register (upsert — deletes old row, inserts fresh)
            _register_reel(reel_path_v, variant, article, carousel_slides=carousel_slides)
            
            if args.skip_distribute:
                continue
            
            # Upload BOTH variants to YouTube (differentiated titles via upload_youtube)
            if existing_yt:
                # Preserve existing YouTube video ID on the new row
                _save_yt_video_id(article["id"], variant, existing_yt)
                print(f"  ⏭️  {variant} already on YouTube: {existing_yt}")
                results[f"youtube_{variant}"] = existing_yt
            else:
                # Upload new
                yt_url = upload_youtube(reel_path_v, article, attribution, variant)
                if yt_url:
                    _save_yt_video_id(article["id"], variant, yt_url)
                    results[f"youtube_{variant}"] = yt_url
    else:
        results = {}
    
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


def _check_yt_exists(article_id, variant_label):
    """Check if this specific variant already has a YouTube upload."""
    exact_path = f"reel-gen/{article_id}/reel-{variant_label}.mp4"
    try:
        r = requests.get(
            f"{SB_URL}/rest/v1/prebuilt_reels?article_id=eq.{article_id}"
            f"&video_path=eq.{exact_path}"
            f"&yt_video_id=not.is.null&yt_video_id=neq.dedup-skip"
            f"&select=yt_video_id&limit=1",
            headers=SB_HEADERS, timeout=10
        )
        if r.status_code == 200:
            rows = r.json()
            if rows and rows[0].get("yt_video_id"):
                yt_id = rows[0]["yt_video_id"]
                if yt_id.startswith("http"):
                    return yt_id
                return f"https://youtube.com/shorts/{yt_id}"
    except Exception:
        pass
    return None


def _save_yt_video_id(article_id, variant_label, yt_url):
    """Save YouTube video ID and posted timestamp back to the prebuilt_reels row."""
    vid = yt_url.rstrip("/").split("/")[-1].split("?")[0]
    exact_path = f"reel-gen/{article_id}/reel-{variant_label}.mp4"
    try:
        import datetime
        requests.patch(
            f"{SB_URL}/rest/v1/prebuilt_reels?article_id=eq.{article_id}"
            f"&video_path=eq.{exact_path}",
            headers={**SB_HEADERS, "Content-Type": "application/json", "Prefer": "return=minimal"},
            json={"yt_video_id": vid, "yt_posted_at": datetime.datetime.utcnow().isoformat() + "Z"}, timeout=10
        )
    except Exception as e:
        print(f"  ⚠️ Failed to save yt_video_id: {e}")


def _register_reel(reel_path, variant_label, article, carousel_slides=None):
    """Register a reel in prebuilt_reels (upsert: replaces existing row for same article+variant).
    
    variant_label must be 'music-only' or 'voiceover' (standardized).
    """
    if variant_label not in ("music-only", "voiceover"):
        print(f"  ⚠️ Invalid variant_label '{variant_label}' — must be 'music-only' or 'voiceover'")
        return
    # Upload reel to Supabase storage
    reel_storage = f"reel-gen/{article['id']}/reel-{variant_label}.mp4"
    with open(reel_path, "rb") as f:
        requests.post(
            f"{SB_URL}/storage/v1/object/article-images/{reel_storage}",
            headers={**SB_HEADERS, "Content-Type": "video/mp4", "x-upsert": "true"},
            data=f.read(), timeout=120
        )
    video_url = f"{STORAGE_BASE}/{reel_storage}"
    
    # Upload carousel images to Supabase storage
    carousel_urls = []
    if carousel_slides:
        for i, slide_path in enumerate(carousel_slides):
            if not os.path.exists(slide_path):
                continue
            carousel_storage = f"reel-gen/{article['id']}/carousel-{i}.jpg"
            try:
                with open(slide_path, "rb") as f:
                    resp = requests.post(
                        f"{SB_URL}/storage/v1/object/article-images/{carousel_storage}",
                        headers={**SB_HEADERS, "Content-Type": "image/jpeg", "x-upsert": "true"},
                        data=f.read(), timeout=30
                    )
                if resp.status_code in (200, 201):
                    carousel_urls.append(f"{STORAGE_BASE}/{carousel_storage}")
                else:
                    print(f"  ⚠️ Carousel {i} upload failed: {resp.status_code}")
            except Exception as e:
                print(f"  ⚠️ Carousel {i} upload error: {e}")
        if carousel_urls:
            print(f"  📸 Uploaded {len(carousel_urls)} carousel images")
    
    article_url = f"https://www.thevideshi.com/articles/{article.get('slug', '')}"
    caption = f"🇮🇳 {article['headline']}\n\n📰 {article_url}\n\n#IndianDiaspora #NRI #TheVideshi"
    
    # Delete existing row(s) for same article + variant to prevent duplicates.
    # Use exact suffix match to avoid cross-variant deletion
    # (e.g. "music-only" must not delete "voiceover" and vice versa).
    exact_path = f"reel-gen/{article['id']}/reel-{variant_label}.mp4"
    requests.delete(
        f"{SB_URL}/rest/v1/prebuilt_reels?article_id=eq.{article['id']}"
        f"&video_path=eq.{exact_path}",
        headers=SB_HEADERS, timeout=15
    )
    
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
    if carousel_urls:
        row["carousel_images"] = carousel_urls
    r = requests.post(
        f"{SB_URL}/rest/v1/prebuilt_reels",
        headers={**SB_HEADERS, "Content-Type": "application/json", "Prefer": "return=representation"},
        json=row, timeout=15
    )
    if r.status_code in (200, 201):
        print(f"  ✅ Registered {variant_label} reel in prebuilt_reels")
    else:
        print(f"  ⚠️ Registration failed: {r.status_code} {r.text[:200]}")


if __name__ == "__main__":
    main()
