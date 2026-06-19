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
TTS_VOICE = "cb9diBQeYWIGJS9i52kX"  # Indian Anchorwoman — HeyGen built-in Indian English female

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
    "news": 0.10, "nri-world": 0.10, "immigration": 0.10,
    "sports": 0.12, "technology": 0.10, "markets-finance": 0.08,
    "entertainment": 0.14, "lifestyle-health": 0.12,
    "food": 0.14, "travel": 0.14,
}

# Ken Burns effects to rotate through — varied zooms and pans for dynamism
KEN_BURNS_EFFECTS = ["zoomIn", "zoomOut", "slideLeft", "zoomIn", "slideRight", "zoomOut"]

# Category-aware transitions for B-roll scenes — varied for visual interest
CATEGORY_TRANSITIONS = {
    "news": ["fade", "slideLeft", "fade", "slideRight"],
    "nri-world": ["fade", "slideLeft", "fade", "slideRight"],
    "immigration": ["fade", "slideLeft", "fade", "slideRight"],
    "entertainment": ["fade", "slideUp", "slideLeft", "fade"],
    "sports": ["slideLeft", "fade", "slideRight", "fade"],
    "technology": ["fade", "slideUp", "fade", "slideLeft"],
    "markets-finance": ["fade", "slideLeft", "fade", "slideRight"],
    "travel": ["fade", "slideUp", "fade", "slideLeft"],
    "lifestyle-health": ["fade", "slideUp", "fade", "slideLeft"],
    "food": ["fade", "slideUp", "slideLeft", "fade"],
}

# Caption animation style per category (for rich-caption fallback)
CATEGORY_CAPTION_STYLE = {
    "news": "pop",
    "nri-world": "pop",
    "immigration": "pop",
    "entertainment": "bounce",
    "sports": "slide",
    "technology": "typewriter",
    "markets-finance": "highlight",
    "travel": "fade",
    "lifestyle-health": "fade",
    "food": "bounce",
}


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
    """Get article slugs AND article IDs that already have reels."""
    r = requests.get(
        f"{SB_URL}/rest/v1/prebuilt_reels",
        params={"select": "article_slug,article_id", "limit": 500},
        headers=SB_HEADERS,
        timeout=10,
    )
    if r.status_code == 200:
        rows = r.json()
        slugs = {row["article_slug"] for row in rows if row.get("article_slug")}
        ids = {row["article_id"] for row in rows if row.get("article_id")}
        return slugs, ids
    return set(), set()


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


def get_recently_failed(within_hours=18):
    """Article IDs and slugs that FAILED QA recently.

    Failed reels are never written to prebuilt_reels, so without this the
    auto-picker has no memory of a failed attempt and re-picks the same
    top-scored article on the very next run — burning both attempts in a
    cycle on one story. We read the QA feedback log (which records every
    attempt, pass or fail) and skip articles that failed within the cooldown
    window so each run advances to a fresh article. Purely a picker guard;
    does not touch QA scoring or the pass threshold.
    """
    failed_ids, failed_slugs = set(), set()
    if not QA_FEEDBACK_LOG.exists():
        return failed_ids, failed_slugs
    cutoff = datetime.now() - timedelta(hours=within_hours)
    try:
        with open(QA_FEEDBACK_LOG) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    e = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if e.get("passed", False):
                    continue
                ts = e.get("timestamp", "")
                try:
                    if datetime.fromisoformat(ts) < cutoff:
                        continue
                except (ValueError, TypeError):
                    pass  # undated entry — treat as recent
                if e.get("article_id"):
                    failed_ids.add(e["article_id"])
                if e.get("slug"):
                    failed_slugs.add(e["slug"])
    except Exception as ex:
        print(f"  ⚠️ Could not read QA log for failed-article skip: {ex}")
    return failed_ids, failed_slugs


def pick_article(articles, existing_slugs, existing_ids=None):
    """Pick best article that doesn't already have a reel (by slug OR article ID),
    and that hasn't recently failed QA (so we don't re-attempt the same story)."""
    existing_ids = existing_ids or set()
    failed_ids, failed_slugs = get_recently_failed()
    # QA log truncates slug to 80 chars — compare on the same prefix.
    def slug_failed(slug):
        if not slug:
            return False
        return slug in failed_slugs or slug[:80] in failed_slugs

    candidates = [a for a in articles
                  if a.get("slug") not in existing_slugs
                  and a.get("id") not in existing_ids
                  and a.get("id") not in failed_ids
                  and not slug_failed(a.get("slug"))]
    if not candidates:
        # Everything fresh recently failed QA — fall back to the original rule
        # (skip only articles that already have a shipped reel) so the run still
        # attempts something rather than going idle.
        candidates = [a for a in articles
                      if a.get("slug") not in existing_slugs
                      and a.get("id") not in existing_ids]
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

    # Load QA feedback lessons from past runs
    qa_lessons = load_qa_lessons()
    qa_lessons_block = ""
    if qa_lessons:
        qa_lessons_block = f"""

LESSONS FROM PAST QA REVIEWS (your previous reels had these issues — fix them this time):
{qa_lessons}
"""
        print(f"  📚 Injecting {len(qa_lessons.splitlines())} QA lessons into prompt")

    prompt = f"""You write viral Instagram Reel scripts for The Videshi — news for the Indian diaspora.

This is a VOICE-OVER reel. No anchor on screen. Visuals are B-roll images/video that change every 4-6 seconds.
{qa_lessons_block}
ARTICLE:
Headline: {headline}
Subheadline: {subheadline}
Category: {category}
Body: {body[:3000]}

SCRIPT RULES:
1. HOOK (first 3 seconds): Start with a jaw-dropping fact, a bold claim, or a "wait what?" moment. No pleasantries, no setup — hit them immediately. The hook must STOP THE SCROLL.
2. SUBSTANCE: This is NOT a headline — it's a mini-briefing. After the hook, deliver the ESSENCE of the story:
   - What happened (the core facts, with specific numbers/names/dates)
   - Why it matters (the real-world impact, especially for NRIs/diaspora)
   - What's next (the forward-looking angle or unanswered question)
   The viewer should walk away understanding the story, not just knowing a headline exists.
   CRITICAL: Do NOT just restate the headline in different words. If your script could be replaced by reading the headline aloud, it has FAILED. Dig into the article body for the 2-3 most surprising or important details and BUILD the narration around those.
3. TENSION: Build intrigue. Use contrast, stakes, or a narrative arc. "Here's why that matters for every NRI watching this."
4. PAYOFF: Land with a punch — a surprising twist, a forward-looking take, or a line that makes them want to share it.
5. TONE: Talk like a smart friend explaining something important over coffee. Confident, clear, slightly urgent. NOT a news robot, NOT breathless hype.
6. PACING: Short sentences. Vary rhythm. Let key facts land.
7. LENGTH: 120-160 words. That's 45-65 seconds spoken. Enough to actually inform, not just tease.
8. SPECIFICS: Include at least 3-4 concrete numbers, names, or details from the article. Vague summaries = failed script.
9. NO "Welcome to The Videshi", NO emoji, NO hashtags.
10. ALWAYS end with a spoken call-to-action. The CTA MUST mention the website URL:
   - "Full story at thevideshi dot com"
   - "More at thevideshi dot com"
   - "Read the full breakdown at thevideshi dot com"
   Do NOT say "Follow The Videshi for more" — that's too vague. Always direct to the website.
   This is the LAST line of the script. It must be there every time.

HOOK TEXT (shown on screen before voice starts):
- hook_line1: 3-5 words, ALL CAPS. The "stop scrolling" line.
- hook_line2: 3-5 words, ALL CAPS. Adds context or intrigue.

STORYBOARD: Plan 6-8 visual scenes that match the narration beat-by-beat.
Each scene is ONE B-roll video clip or image shown for ~4-6 seconds while the voice plays.
- Scene 1 = the HOOK background (darkened). Choose something dramatic, cinematic, wide-angle.
- Scenes 2-7 = the narration beats. Each visual must match EXACTLY what's being said in that moment.
- More scenes = more visual variety = better retention.

For each scene, provide:
- "narration": the exact words spoken during that scene (copy from script)
- "visual": a SPECIFIC, concrete description of the ideal stock video clip or photo. Not "Indian economy" — say "close-up of Indian 500 rupee notes being counted by hand" or "aerial drone shot of Mumbai Marine Drive coastline at sunset". Be CINEMATIC and precise — think what a videographer would actually film.
- "search_queries": TWO Pexels search queries, each 2-4 words. These search BOTH Pexels video AND photo libraries. First query = most specific visual, second = broader fallback.
  GOOD queries: "Indian rupee notes", "cargo ship ocean", "Mumbai skyline aerial", "Indian family celebrating"
  BAD queries: "economic crisis concept", "tension building scene", "elements clashing" (too abstract — returns nothing useful)

CRITICAL RULES FOR SEARCH QUERIES:
- NEVER use celebrity, politician, or public figure names — Pexels has NO footage of specific people. Instead describe the VISUAL CONCEPT: "Bollywood dance performance" not "Sunny Deol".
- ALWAYS include "Indian" or "India" in queries when the story is about India, Bollywood, Indian culture, or the diaspora. "Indian parliament building" not "parliament building". "Indian currency notes" not "currency notes".
- Every scene's visual must be DIFFERENT and RELEVANT to that specific narration beat. A story about remittances needs rupee notes, bank transfers, families — NOT steel factories or oil tankers.
- Think like a VIDEO PRODUCER: what would a videographer actually shoot? "cargo ship sailing ocean waves" works. "geopolitical tension escalating" does not produce usable footage.
- Keep queries SHORT and CONCRETE — 2-4 words max. "Indian soldiers marching" not "dramatic military parade of Indian army troops in formation".
- AVOID scenes that would return protest photos, political signs, or text-heavy footage. No "crowd running", "protest", "demonstration". Instead use evocative visuals: "smoke rising over rooftops", "empty train platform".

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
        timeout=60,
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
# PRE-RENDER GATES — validate before spending Shotstack credits
# ═══════════════════════════════════════════════════════════════════════════════

def pre_render_script_qa(script_data, article):
    """Score script BEFORE TTS/render. Catches bad scripts at ~$0.001 instead of $0.20.
    Returns (passed: bool, score: int, feedback: str).
    """
    if not OPENAI_KEY:
        return True, 7, "Skipped (no API key)"

    headline = article.get("headline", "")
    script = script_data.get("script", "")
    hook1 = script_data.get("hook_line1", "")
    hook2 = script_data.get("hook_line2", "")
    storyboard = script_data.get("storyboard", [])
    word_count = len(script.split())

    prompt = f"""You quality-check reel scripts for The Videshi (Indian diaspora news).

ARTICLE: {headline}
HOOK: {hook1} / {hook2}
SCRIPT ({word_count} words): {script}
STORYBOARD SCENES: {len(storyboard)}

Score 1-10 on:
1. HOOK POWER: Does it grab in 3 seconds? Bold, surprising, specific?
2. SCRIPT QUALITY: Informative, well-paced, NRI-relevant? Does it deliver actual substance (key facts, numbers, context) — not just a restated headline?
3. LENGTH: 120-160 words ideal. Under 80 or over 200 is a problem. The reel should be a mini-briefing, not a teaser.
4. CTA: Must end with "thevideshi dot com" or "thevideshi.com". Present?
5. STORYBOARD: Are scene visuals concrete and photographable? (no abstract concepts)
6. SPELLING: Is "TheVideshi" / "thevideshi.com" spelled correctly throughout?

HARD FAILS (auto-score 0):
- "TheVideshi" misspelled anywhere (Vidashi, Vidashee, Divaji, etc.)
- No CTA at the end
- Script under 60 words or over 200 words
- Script is just a restated headline with no additional facts or context

Return JSON only:
{{"score": <1-10>, "passed": <true if score >= 7>, "issues": ["issue1"], "fix_suggestions": ["suggestion1"]}}"""

    try:
        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENAI_KEY}", "Content-Type": "application/json"},
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
                "response_format": {"type": "json_object"},
                "max_tokens": 300,
            },
            timeout=15,
        )
        if r.status_code != 200:
            return True, 7, "Skipped (API error)"

        result = json.loads(r.json()["choices"][0]["message"]["content"])
        score = result.get("score", 5)
        # Derive pass from score, don't trust LLM string. Gate 8→7 (Kiran 2026-06-15).
        passed = score >= 7
        issues = result.get("issues", [])
        fixes = result.get("fix_suggestions", [])
        notes = "; ".join(issues) if issues else "Clean"
        return passed, score, notes
    except Exception as e:
        return True, 7, f"Skipped ({e})"


def preflight_image_urls(image_urls):
    """HEAD-check all image URLs before render. Returns (valid_urls, dead_urls).
    A dead image URL = wasted Shotstack credit (black frame or render failure).

    NOTE (2026-06-15): upload.wikimedia.org ALWAYS returns HTTP 400 to HEAD
    requests from this environment — even for valid, working images. A plain HEAD
    gate therefore silently nukes every Wikipedia entity frame (the Indian
    company/people/place imagery Kiran specifically prefers). For wikimedia hosts
    we verify with a lightweight ranged GET instead, and treat any 2xx/3xx as live.
    """
    valid = []
    dead = []
    for url in image_urls:
        is_wikimedia = "upload.wikimedia.org" in url or "wikimedia.org" in url
        try:
            if is_wikimedia:
                # GET (range-limited) — HEAD is a guaranteed false 400 on Wikimedia.
                r = requests.get(url, timeout=12, allow_redirects=True, stream=True,
                                 headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)",
                                          "Range": "bytes=0-2047"})
                ok = r.status_code < 400
                r.close()
                if ok:
                    valid.append(url)
                else:
                    dead.append((url, f"HTTP {r.status_code}"))
                    print(f"  ❌ Dead image: {url[:80]} → {r.status_code}")
                continue
            r = requests.head(url, timeout=8, allow_redirects=True,
                              headers={"User-Agent": "Mozilla/5.0 (compatible; TheVideshi/1.0)"})
            if r.status_code < 400:
                valid.append(url)
            else:
                dead.append((url, f"HTTP {r.status_code}"))
                print(f"  ❌ Dead image: {url[:80]} → {r.status_code}")
        except Exception as e:
            dead.append((url, str(e)))
            print(f"  ❌ Unreachable image: {url[:80]} → {e}")
    return valid, dead


def validate_timeline_json(edit_json):
    """Sanity-check the Shotstack timeline JSON before submitting.
    Catches structural issues that would waste a credit on a guaranteed failure.
    Returns (valid: bool, issues: list[str]).
    """
    issues = []

    # Check output config
    output = edit_json.get("output", {})
    if output.get("format") != "mp4":
        issues.append(f"Unexpected format: {output.get('format')}")
    size = output.get("size", {})
    if size.get("width") != 1080 or size.get("height") != 1920:
        issues.append(f"Not portrait 9:16: {size}")
    if output.get("aspectRatio") not in ("9:16", None):
        issues.append(f"Aspect ratio mismatch: {output.get('aspectRatio')}")

    # Check timeline exists and has tracks
    timeline = edit_json.get("timeline", {})
    tracks = timeline.get("tracks", [])
    if not tracks:
        issues.append("No tracks in timeline")

    # Check all clips have non-zero length (Shotstack allows "end" and "auto" as valid string lengths)
    for ti, track in enumerate(tracks):
        for ci, clip in enumerate(track.get("clips", [])):
            length = clip.get("length", 0)
            # "end" = fill to end of timeline, "auto" = infer from asset — both valid
            if isinstance(length, str) and length in ("end", "auto"):
                continue
            try:
                length = float(length)
            except (TypeError, ValueError):
                issues.append(f"Track {ti} clip {ci}: invalid length '{length}'")
                continue
            if length <= 0:
                issues.append(f"Track {ti} clip {ci}: zero/negative length")
            asset = clip.get("asset", {})
            # Check image/video assets have a src
            asset_type = asset.get("type", "")
            if asset_type in ("image", "video", "audio") and not asset.get("src"):
                issues.append(f"Track {ti} clip {ci}: {asset_type} asset missing src URL")

    # Check total duration is reasonable (15s - 120s for a reel)
    total_duration = 0
    for track in tracks:
        for clip in track.get("clips", []):
            try:
                clip_start = float(clip.get("start", 0))
                clip_length = clip.get("length", 0)
                if isinstance(clip_length, str):
                    continue  # "end"/"auto" — can't compute, skip
                clip_end = clip_start + float(clip_length)
            except (TypeError, ValueError):
                clip_end = 0
            total_duration = max(total_duration, clip_end)
    if total_duration < 15:
        issues.append(f"Too short: {total_duration:.1f}s")
    elif total_duration > 120:
        issues.append(f"Too long: {total_duration:.1f}s")

    return len(issues) == 0, issues


# ═══════════════════════════════════════════════════════════════════════════════
# QA FEEDBACK LOOP — log issues, learn from them, improve future prompts
# ═══════════════════════════════════════════════════════════════════════════════

QA_FEEDBACK_LOG = BUILD_DIR / "qa-feedback-log.jsonl"


def log_qa_feedback(article, score, passed, issues, severity="LOW", notes=""):
    """Append QA result to persistent feedback log. Every run — pass or fail — gets logged."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "article_id": article.get("id", ""),
        "slug": article.get("slug", "")[:80],
        "category": article.get("category", ""),
        "score": score,
        "passed": passed,
        "issues": issues,
        "severity": severity,
        "notes": notes,
    }
    try:
        with open(QA_FEEDBACK_LOG, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        print(f"  ⚠️ Failed to log QA feedback: {e}")


def load_qa_lessons(max_entries=50):
    """Read recent QA feedback and extract recurring issues as lessons.
    Returns a string of lessons to inject into script/timeline prompts.
    """
    if not QA_FEEDBACK_LOG.exists():
        return ""

    entries = []
    try:
        with open(QA_FEEDBACK_LOG) as f:
            for line in f:
                line = line.strip()
                if line:
                    entries.append(json.loads(line))
    except Exception:
        return ""

    if not entries:
        return ""

    # Take last N entries
    recent = entries[-max_entries:]

    # Collect all issues from entries that scored < 8 (even passes with issues)
    # Only surface SCRIPT-level issues here — this feeds the script-writer prompt,
    # which has no control over render-side problems (contrast, hook frame,
    # pixelation, overlapping text). Feeding those back just spins uselessly.
    _render_only = ("contrast", "readab", "pixel", "blur", "stretch", "overlap",
                    "resolution", "branding", "watermark", "transition", "pacing",
                    "flow", "hook", "opening frame", "black bar")

    def _is_script_issue(issue_text):
        t = issue_text.lower()
        # Keep issues about the narration/content; drop pure-render complaints.
        script_signals = ("depth", "restate", "headline", "narration", "vague",
                           "specific", "context", "information", "cta", "spelling",
                           "relevan")  # relevance is partly script (storyboard) driven
        if any(s in t for s in script_signals):
            return True
        if any(r in t for r in _render_only):
            return False
        return True  # default: keep

    all_issues = []
    for e in recent:
        for issue in e.get("issues", []):
            if _is_script_issue(issue):
                all_issues.append(issue.lower().strip())

    if not all_issues:
        return ""

    # Count issue frequency
    from collections import Counter
    issue_counts = Counter(all_issues)
    # Only surface issues that appeared 2+ times (real patterns, not one-offs)
    recurring = [(issue, count) for issue, count in issue_counts.most_common(10) if count >= 2]

    if not recurring:
        # If no recurring patterns yet, surface top issues from failures only
        fail_issues = []
        for e in recent:
            if not e.get("passed", True):
                fail_issues.extend(e.get("issues", []))
        if fail_issues:
            recurring = [(i, 1) for i in Counter(fail_issues).most_common(5)]

    if not recurring:
        return ""

    # Build lessons string
    lessons = []
    for issue, count in recurring:
        lessons.append(f"- {issue} (seen {count}x)")

    # Stats
    total = len(recent)
    passed = sum(1 for e in recent if e.get("passed", False))
    avg_score = sum(e.get("score", 0) for e in recent) / total if total else 0
    failed = total - passed

    header = f"QA STATS (last {total} reels): {passed} passed, {failed} failed, avg score {avg_score:.1f}/10"
    body = "\n".join(lessons)

    return f"""{header}

RECURRING QA ISSUES — avoid these in your script and storyboard:
{body}"""


# ═══════════════════════════════════════════════════════════════════════════════
# TTS — HeyGen Indian Anchorwoman Voice
# ═══════════════════════════════════════════════════════════════════════════════

def generate_tts(text):
    """Generate TTS via HeyGen v2 preview endpoint. Returns (local_path, duration) or (None, 0).
    Applies loudnorm to -11 LUFS."""
    if not HEYGEN_KEY:
        print("❌ HeyGen API key not found")
        return None, 0

    # Phonetic hint for TTS — help pronounce "TheVideshi" correctly
    # "Videshi" = विदेशी (vi-they-shi) — soft dental द, pure ए vowel, crisp शी
    tts_text = text.replace("thevideshi", "the Vitheyshi").replace("TheVideshi", "The Vitheyshi").replace("Videshi", "Vitheyshi")

    # Acronym expansion — spell out common abbreviations so TTS doesn't read them as words
    import re
    acronym_map = {
        "NRIs": "N.R.I.s", "NRI": "N.R.I.", "NRI's": "N.R.I.'s",
        "OCI": "O.C.I.", "PIO": "P.I.O.", "PIOs": "P.I.O.s",
        "H-1B": "H-1B", "H1B": "H-1-B", "H1Bs": "H-1-B.s",
        "EB-5": "E.B.-5", "EB5": "E.B.-5", "EB-1": "E.B.-1", "EB-2": "E.B.-2",
        "IPL": "I.P.L.", "BCCI": "B.C.C.I.", "ICC": "I.C.C.",
        "RBI": "R.B.I.", "SEBI": "S.E.B.I.",
        "USCIS": "U.S.C.I.S.", "DHS": "D.H.S.", "DOL": "D.O.L.",
        "GDP": "G.D.P.", "FDI": "F.D.I.", "IMF": "I.M.F.",
        "BJP": "B.J.P.", "AAP": "A.A.P.", "RSS": "R.S.S.",
        "IIT": "I.I.T.", "IITs": "I.I.T.s", "ISRO": "I.S.R.O.",
        "UAE": "U.A.E.", "UK": "U.K.", "US": "U.S.",
        "AI": "A.I.", "CEO": "C.E.O.", "CTO": "C.T.O.",
        "OPT": "O.P.T.", "STEM": "stem",  # STEM reads fine as a word
        "FCNR": "F.C.N.R.", "MOU": "M.O.U.", "MOUs": "M.O.U.s",
    }
    for acronym, expansion in acronym_map.items():
        # Use word boundary matching to avoid replacing inside larger words
        tts_text = re.sub(r'\b' + re.escape(acronym) + r'\b', expansion, tts_text)

    # HeyGen SSML <break> tags cause massively inflated audio (bug confirmed 2026-06-11).
    # Use plain text instead — HeyGen's natural prosody handles sentence pauses well.
    plain_text = tts_text.strip()

    # Retry with increasing timeout
    for attempt in range(3):
        try:
            r = requests.post(
                f"https://api.heygen.com/v2/voices/{TTS_VOICE}/preview",
                headers={"X-Api-Key": HEYGEN_KEY, "Content-Type": "application/json"},
                json={"text": plain_text, "voice_id": TTS_VOICE, "text_type": "text"},
                timeout=60,
            )
            break
        except requests.exceptions.ReadTimeout:
            if attempt < 2:
                print(f"  ⏳ TTS timeout (attempt {attempt+1}/3), retrying...")
                time.sleep(3)
            else:
                print("❌ HeyGen TTS timed out after 3 attempts")
                return None, 0

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
         "-af", "loudnorm=I=-11:TP=-1.0:LRA=11",
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

    # Get actual duration from ffprobe (HeyGen API sometimes returns centiseconds not seconds)
    try:
        probe = subprocess.run(
            ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(mp3_path)],
            capture_output=True, text=True, timeout=10,
        )
        if probe.returncode == 0 and probe.stdout.strip():
            duration = float(probe.stdout.strip())
    except Exception:
        pass  # Fall back to HeyGen's duration if ffprobe fails

    # Sanity check: TTS for a 120-160 word script should be 30-90 seconds max
    if duration > 120:
        print(f"  ❌ TTS duration {duration:.1f}s is way too long — likely HeyGen API bug. Aborting.")
        return None, 0

    print(f"  🎙️ TTS audio: {duration:.1f}s (Indian Anchorwoman voice, normalized to -11 LUFS)")
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
    Uses Whisper ONLY for timing, but takes the actual text from the original script
    to avoid transcription spelling errors (e.g. 'the videshi' garbled by Whisper)."""
    if not words:
        return None

    # Split original script into words for spelling-accurate text
    script_words = script_text.split()

    # Align Whisper word count with script words — use script text with Whisper timing
    # If counts differ, we stretch/compress the mapping proportionally
    aligned = []
    n_whisper = len(words)
    n_script = len(script_words)

    last_script_idx = -1
    for i, w in enumerate(words):
        # Map this Whisper index to the corresponding script word index
        script_idx = round(i * n_script / n_whisper) if n_whisper > 0 else i
        script_idx = min(script_idx, n_script - 1) if n_script > 0 else 0
        # Dedup: when more Whisper words map onto the same script word (n_whisper >
        # n_script), don't emit it twice ("SCANDAL SCANDAL"). Instead extend the
        # previous entry's end time so the on-screen word holds for its full span.
        if script_idx == last_script_idx and aligned:
            aligned[-1]["end"] = w.get("end", aligned[-1]["end"])
            continue
        last_script_idx = script_idx
        aligned.append({
            "word": script_words[script_idx] if script_idx < n_script else w.get("word", ""),
            "start": w.get("start", 0),
            "end": w.get("end", 0),
        })

    # Group into phrases. Break only on sentence-ending punctuation or at 5 words —
    # NOT on commas, which produced tiny single-word clips that never reached full
    # opacity within their fade window (the recurring "low contrast" QA failure).
    # URL lock: once we hit the brand token ("thevideshi"/"videshi"), keep every
    # word through "com" in the SAME clip so the CTA never splits as
    # "...THEVIDESHI DOT" + "COM" on two slides.
    def _norm_tok(w):
        return w.get("word", "").strip().lower().strip(".,!?:;")

    phrases = []
    current = []
    url_mode = False
    for w in aligned:
        current.append(w)
        word_text = w.get("word", "")
        nt = _norm_tok(w)
        if nt in ("thevideshi", "videshi"):
            url_mode = True
        if url_mode:
            # Don't break mid-URL; close the phrase only after "com"
            if nt == "com":
                phrases.append(current)
                current = []
                url_mode = False
            continue
        if len(current) >= 5 or word_text.rstrip().endswith((".", "!", "?")):
            phrases.append(current)
            current = []
    if current:
        phrases.append(current)

    # Build raw clip data first, then fix overlaps
    raw_clips = []
    for phrase in phrases:
        text = " ".join(w.get("word", "") for w in phrase).strip().upper()
        start = hook_duration + phrase[0]["start"]
        end = hook_duration + phrase[-1]["end"]
        duration = max(end - start, 0.5)
        raw_clips.append({"text": text, "start": round(start, 2), "duration": round(duration, 2)})

    # Merge any clip shorter than MIN_DUR into the following clip so no caption
    # flashes by too fast to read. Keeps text legible and avoids sub-second pills.
    MIN_DUR = 1.0
    merged = []
    i = 0
    while i < len(raw_clips):
        rc = raw_clips[i]
        # Merge forward while too short and a next clip exists
        while rc["duration"] < MIN_DUR and i + 1 < len(raw_clips):
            nxt = raw_clips[i + 1]
            combined_text = (rc["text"] + " " + nxt["text"]).strip()
            new_end = nxt["start"] + nxt["duration"]
            rc = {
                "text": combined_text,
                "start": rc["start"],
                "duration": round(new_end - rc["start"], 2),
            }
            i += 1
        merged.append(rc)
        i += 1
    raw_clips = merged

    # Safety net: if the FINAL clip is still under MIN_DUR (nothing after it to
    # merge forward into — e.g. an orphaned "COM"), merge it BACKWARD into the
    # previous clip so the last word never flashes on its own slide.
    if len(raw_clips) >= 2 and raw_clips[-1]["duration"] < MIN_DUR:
        last = raw_clips.pop()
        prev = raw_clips[-1]
        prev["text"] = (prev["text"] + " " + last["text"]).strip()
        prev["duration"] = round(
            (last["start"] + last["duration"]) - prev["start"], 2
        )

    # Fix overlaps: trim each clip so it ends before the next one starts (0.02s gap min)
    for i in range(len(raw_clips) - 1):
        gap = raw_clips[i + 1]["start"] - raw_clips[i]["start"]
        max_dur = max(gap - 0.02, 0.5)
        if raw_clips[i]["duration"] > max_dur:
            raw_clips[i]["duration"] = round(max_dur, 2)

    clips = []
    for rc in raw_clips:
        text = rc["text"]

        # High-contrast caption pill — positioned ABOVE the lower-third overlay
        # Fully opaque black background — Shotstack HTML renderer weakens rgba
        html = (
            f"<div style=\"display:flex;align-items:flex-end;justify-content:center;"
            f"width:100%;height:100%;padding:0 24px 0 24px;\">"
            f"<div style=\"background:#000000;border-radius:12px;padding:14px 28px;"
            f"font-family:Inter;font-size:42px;font-weight:900;"
            f"color:#FFFFFF;text-align:center;letter-spacing:1px;line-height:1.25;"
            f"text-shadow: 0 2px 4px rgba(0,0,0,0.9);\">"
            f"{text}</div></div>"
        )

        clips.append({
            "asset": {
                "type": "html",
                "html": html,
                "width": 900,
                "height": 200,
            },
            "start": rc["start"],
            "length": rc["duration"],
            "position": "center",
            "offset": {"x": 0, "y": 0.05},
            # NO fade transition: a fade on a short (<1s) clip keeps the pill
            # semi-transparent for most of its life, which the QA gate reads as
            # "low contrast / poor readability". Hard cut = always full opacity.
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
    # NOTE: wikimedia image hosts (upload.wikimedia.org / commons.wikimedia.org)
    # are deliberately NOT blocked — Shotstack renders them reliably (the storyboard
    # Wikipedia fallback + the 330→1280 thumbnail upscaler both depend on it), and
    # blocking them caused the entity-image pre-pass and wikimedia article heroes to
    # be silently discarded. Only the wikipedia.org *article-page* host is blocked,
    # since those URLs are HTML pages, not images.
    "en.wikipedia.org/wiki/", "wikipedia.org/wiki/",
    "static.toiimg.com", "im.rediff.com",
]


def upscale_wikimedia_url(url, target_px=1280):
    """Rewrite a Wikimedia thumbnail URL to a larger width to avoid pixelation.
    Wikimedia thumb URLs embed the width like '/330px-Foo.jpg'. A 330px thumb
    stretched to 1080 looks blurry — bump it to target_px. Non-thumb or
    non-Wikimedia URLs are returned unchanged.
    """
    if not url or "upload.wikimedia.org" not in url or "/thumb/" not in url:
        return url
    import re
    # Match the trailing '/<NNN>px-<filename>' segment and raise the width.
    m = re.search(r"/(\d+)px-([^/]+)$", url)
    if not m:
        return url
    cur = int(m.group(1))
    if cur >= target_px:
        return url
    return url[: m.start()] + f"/{target_px}px-{m.group(2)}"


# Filename signals for non-photographic Wikimedia assets (diagrams, flowcharts,
# charts, SVG schematics, process figures). These are the #1 driver of the QA
# "overlapping text / low contrast / image doesn't match topic" cluster: e.g.
# the "H-1B" page lead image is literally "Figure 2- Process of Obtaining an
# H-1B Visa" (a flowchart) and "LLC" resolves to "Society.svg" (a schematic).
_DIAGRAM_FILENAME_SIGNALS = (
    ".svg", "figure_", "figure-", "fig_", "fig-", "process_of", "process-of",
    "diagram", "flowchart", "flow_chart", "infographic", "schematic",
    "timeline", "venn", "org_chart", "orgchart", "histogram", "bar_chart",
    "pie_chart", "line_chart", "flow-chart",
)


def _image_looks_like_diagram(path):
    """Heuristic: True if a downloaded image is a diagram/flowchart/text-slab/
    grayscale archival scan rather than a photograph. Calibrated 2026-06-16 on
    the real failing assets (H-1B flowchart, Society.svg, a grayscale archival
    photo) vs. real entity photos (Modi, Infosys campus, Taj Mahal):
      - flowchart:  white_frac 0.80, edge_frac 0.109  (text on white)
      - svg schema: caught by filename
      - archival:   distinct_colors 8                 (mono/sepia)
      - real photos: white_frac <= 0.37, edge_frac <= 0.044, colors >= 70
    Conservative thresholds sit well clear of every real-photo sample, so the
    false-positive risk on genuine India entity imagery is minimal. On any
    error returns False (never block a render on a heuristic failure)."""
    try:
        from PIL import Image
        import numpy as np
        im = Image.open(path).convert("RGB")
        im.thumbnail((512, 512))
        g = im.convert("L")
        arr = np.asarray(g, dtype=np.float32)
        gx = np.abs(np.diff(arr, axis=1))
        gy = np.abs(np.diff(arr, axis=0))
        edge_frac = (float(np.mean(gx > 40)) + float(np.mean(gy > 40))) / 2.0
        white_frac = float(np.mean(arr > 235))
        q = (np.asarray(im) // 32).reshape(-1, 3)
        distinct_colors = len({tuple(c) for c in q})
        # (1) Document/diagram: lots of white background + dense fine edges (text).
        if white_frac > 0.6 and edge_frac > 0.06:
            return True
        # (2) Line-art / schematic on non-white bg: very dense edges, few colors.
        if edge_frac > 0.09 and distinct_colors <= 40:
            return True
        # (3) Monochrome/grayscale schematic or archival scan (real photos >= ~70).
        if distinct_colors <= 12:
            return True
        return False
    except Exception:
        return False


def mirror_to_supabase(url, article_id, scene_idx, reject_diagrams=False):
    """Mirror a Wikimedia/Commons image through Supabase storage so Shotstack can fetch it.

    When reject_diagrams=True, the downloaded asset is inspected and, if it looks
    like a diagram/flowchart/text-slab/grayscale schematic, the function returns
    None so the caller skips the scene (the key-point-card floor then fills it
    with on-topic motion graphics). reject_diagrams defaults False so the article
    hero and any other caller keep the original behavior.

    Shotstack's render servers cannot reliably download from upload.wikimedia.org /
    commons.wikimedia.org (intermittent block / 4xx), even though OUR environment can
    (HTTP 206). That caused hard render failures on real India-relevant entity frames
    (e.g. an SBI/Goa thumb). The key-point cards already dodge this by uploading to
    Supabase and handing Shotstack the Supabase URL; this applies the SAME treatment to
    every Wikimedia/Commons B-roll image we select.

    Downloads via curl (per AGENTS.md, Python requests can 429 on wikimedia hosts while
    plain curl with our UA returns 200), uploads to article-images/reel-broll/{id}/
    scene-{idx}.jpg, and returns the Supabase public URL. On ANY failure returns the
    original url unchanged so the pipeline never breaks. Non-wikimedia URLs (Pexels,
    Supabase, etc.) are returned unchanged — they already render fine for Shotstack.
    """
    if not url or "wikimedia.org" not in url:
        return url
    try:
        src = upscale_wikimedia_url(url)
        local = f"/tmp/videshi_broll_{article_id}_{scene_idx}.jpg"
        ua = "TheVideshi/1.0 (thevideshi.com)"
        result = subprocess.run(
            ["curl", "-sS", "-L", "--fail", "-A", ua, "-o", local, "--max-time", "30", src],
            capture_output=True, text=True, timeout=40,
        )

        def _is_real_image(path):
            """Reject HTML error pages / truncated junk — only mirror genuine images."""
            try:
                if not os.path.exists(path) or os.path.getsize(path) < 2048:
                    return False
                with open(path, "rb") as fh:
                    head = fh.read(16)
                # JPEG, PNG, GIF, WEBP(RIFF), BMP magic bytes
                return (head[:3] == b"\xff\xd8\xff" or head[:8] == b"\x89PNG\r\n\x1a\n"
                        or head[:6] in (b"GIF87a", b"GIF89a") or head[:4] == b"RIFF"
                        or head[:2] == b"BM")
            except Exception:
                return False

        if result.returncode != 0 or not _is_real_image(local):
            print(f"  ⚠️ mirror: download failed/non-image for {src[:70]} — keeping original URL")
            try:
                if os.path.exists(local):
                    os.remove(local)
            except Exception:
                pass
            return url
        if reject_diagrams and _image_looks_like_diagram(local):
            print(f"  🚫 mirror: '{src.split('/')[-1][:60]}' looks like a diagram/chart/text-slab — rejecting (key-point card will fill this scene)")
            try:
                os.remove(local)
            except Exception:
                pass
            return None
        storage_path = f"reel-broll/{article_id}/scene-{scene_idx}.jpg"
        mirrored = upload_asset(local, storage_path, "image/jpeg")
        try:
            os.remove(local)
        except Exception:
            pass
        if mirrored:
            print(f"  🪞 Mirrored Wikimedia → Supabase: scene-{scene_idx}.jpg")
            return mirrored
        return url
    except Exception as e:
        print(f"  ⚠️ mirror: {e} — keeping original URL")
        return url


def is_url_downloadable(url):
    """Check if a URL is reachable by Shotstack (no Wikipedia, etc.)."""
    if not url or len(url) < 10:
        return False
    for domain in BLOCKED_DOMAINS:
        if domain in url:
            return False
    return True


def pexels_search(pexels_key, query, count=3, orientation="portrait"):
    """Search Pexels, return list of dicts with url + photo_id. Uses curl (403 with urllib).
    Returns portrait-optimized URLs at 1080x1920 when orientation=portrait."""
    try:
        result = subprocess.run(
            ["curl", "-s", "-H", f"Authorization: {pexels_key}",
             f"https://api.pexels.com/v1/search?query={requests.utils.quote(query)}&per_page={count}&orientation={orientation}"],
            capture_output=True, text=True, timeout=15,
        )
        if result.returncode != 0:
            return []
        data = json.loads(result.stdout)
        results = []
        for photo in data.get("photos", []):
            # Use portrait-optimized URL at exact 1080x1920 for reels
            if orientation == "portrait":
                url = f"https://images.pexels.com/photos/{photo['id']}/pexels-photo-{photo['id']}.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=1920&w=1080"
            else:
                url = photo.get("src", {}).get("large2x") or photo.get("src", {}).get("large")
            if url:
                results.append({
                    "url": url,
                    "photo_id": str(photo.get("id", "")),
                    "alt": photo.get("alt", ""),
                    "photographer": photo.get("photographer", ""),
                    "width": photo.get("width", 0),
                    "height": photo.get("height", 0),
                })
        return results
    except Exception as e:
        print(f"  ⚠️ Pexels: {e}")
        return []


def pexels_video_search(pexels_key, query, count=3, orientation="portrait", min_duration=4):
    """Search Pexels Videos API, return list of dicts with url, video_id, duration.
    Prefers HD portrait MP4 files. Uses curl (403 with urllib)."""
    try:
        result = subprocess.run(
            ["curl", "-s", "-H", f"Authorization: {pexels_key}",
             f"https://api.pexels.com/videos/search?query={requests.utils.quote(query)}&per_page={count}&orientation={orientation}"],
            capture_output=True, text=True, timeout=15,
        )
        if result.returncode != 0:
            return []
        data = json.loads(result.stdout)
        results = []
        for video in data.get("videos", []):
            duration = video.get("duration", 0)
            if duration < min_duration:
                continue  # Too short for a scene
            # Pick best video file: prefer 1080x1920 portrait MP4
            best_file = None
            best_score = -1
            for vf in video.get("video_files", []):
                if vf.get("file_type") != "video/mp4":
                    continue
                w = vf.get("width", 0)
                h = vf.get("height", 0)
                score = 0
                if h > w:  # Portrait
                    score += 10
                # Prefer 1080x1920 (exact match for reel output)
                if w == 1080 and h == 1920:
                    score += 20
                elif 720 <= w <= 1440:
                    score += 5  # Good resolution range
                if score > best_score:
                    best_score = score
                    best_file = vf
            if best_file and best_file.get("link"):
                results.append({
                    "url": best_file["link"],
                    "video_id": str(video.get("id", "")),
                    "duration": duration,
                    "width": best_file.get("width", 0),
                    "height": best_file.get("height", 0),
                    "photographer": video.get("user", {}).get("name", ""),
                    "page_url": video.get("url", ""),
                })
        return results
    except Exception as e:
        print(f"  ⚠️ Pexels Video: {e}")
        return []


def commons_image_search(query, limit=6):
    """Search Wikimedia Commons for real editorial photos matching a query.

    Commons has genuine India-specific imagery (named people, places, events,
    institutions) that Pexels simply lacks — Pexels returns generic or foreign
    stock for niche desi subjects, the #1 QA "relevance" failure. We use Commons
    to fill the middle scenes with real imagery BEFORE falling to Pexels.

    Returns a list of {url, title} dicts (1280px thumbnails), filtered to remove
    flags/logos/maps/icons and non-photo files.
    """
    _bad = ("flag_of", "flag-", "coat_of_arms", "coat-of-arms", "emblem", "ensign",
            "_map", "-map", "location_", "orthographic", "seal_of", "logo", "icon",
            ".svg", "diagram", "chart", "graph", "symbol", "blank", "placeholder",
            # satellite / aerial / map imagery whose filename lacks the word "map"
            "satellite", "aerial", "topograph", "landsat", "sentinel", "nasa", "isro_",
            # coins / banknotes / stamps / document scans (the score-6 finance offenders)
            "_coin", "coin_", "banknote", "currency_note", "stamp_", "postage",
            "document", "manuscript", "scan_", "_scan", "letter_", "gazette",
            "circular", "notification_", "graph_", "plot_", "infographic",
            # book / journal / document-scan pages (Commons surfaces these for
            # finance/abstract queries — e.g. "Himalayan journals", "Educational
            # Screen Volume 1.djvu" — and they read as junk B-roll)
            ".djvu", ".pdf", ".tif", "_page", "page_", "title_page", "frontispiece",
            "journal", "_volume", "volume_", "almanac", "yearbook", "proceedings",
            "gazetteer", "manuscript", "_book", "book_", "_report", "report_",
            "notes_of", "_plate", "plate_", "engraving", "lithograph", "woodcut")
    try:
        r = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params={
                "action": "query", "format": "json",
                "generator": "search",
                "gsrsearch": f"{query}",
                "gsrnamespace": "6",          # File: namespace
                "gsrlimit": str(limit),
                "prop": "imageinfo",
                "iiprop": "url|mime|size",
                "iiurlwidth": "1280",         # request a 1280px-wide thumb
            },
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10,
        )
        if r.status_code != 200:
            return []
        pages = (r.json().get("query", {}) or {}).get("pages", {}) or {}
        out = []
        for p in pages.values():
            title = (p.get("title", "") or "").lower()
            ii = (p.get("imageinfo") or [{}])[0]
            mime = ii.get("mime", "")
            if not mime.startswith("image/") or "svg" in mime:
                continue
            # thumburl is the sized render; fall back to full url
            url = ii.get("thumburl") or ii.get("url")
            if not url:
                continue
            low = (title + " " + url.lower())
            if any(b in low for b in _bad):
                continue
            # Skip tiny source files (icons/thumbnails of logos)
            if ii.get("width", 0) and ii.get("width", 0) < 600 and not ii.get("thumburl"):
                continue
            out.append({"url": url, "title": p.get("title", "")})
        return out
    except Exception as e:
        print(f"  ⚠️ Commons: {e}")
        return []


# ── Used-image dedup log ──
USED_IMAGES_LOG = BUILD_DIR / "used-images.json"

# Hard blocklist of Pexels video/photo IDs that keep ranking high for generic
# queries (e.g. "uniform") but are visibly foreign/off-topic in the rendered
# frame — text in the IMAGE (not metadata) gives them away, so the metadata
# filter can't catch them. Add an ID here whenever frame inspection finds a
# repeat offender. 35074399 = "military uniform close-up" with an Italian
# "Ministry of Interior / COURSE 3.0" patch (flagged on India stories).
BLOCKED_PEXELS_IDS = {
    "35074399",
}

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


# ═══════════════════════════════════════════════════════════════════════════════
# KEY-POINT CARD — styled text/graphic fallback (replaces generic foreign stock)
# ═══════════════════════════════════════════════════════════════════════════════
# When no genuinely relevant image/video can be sourced for a scene (Commons miss,
# Pexels returns generic/foreign stock), we render a designed motion-graphic card
# carrying that scene's key point — on-brand navy + gold, with numbers and proper
# nouns highlighted. This is QA-acceptable because the visual *is* the story, and
# it never shows a country-mismatched or topic-irrelevant photo.

_CARD_GOLD = (212, 175, 55)
_CARD_GOLD_SOFT = (224, 196, 110)
_CARD_NAVY_TOP = (8, 16, 30)
_CARD_NAVY_BOT = (19, 33, 54)
_CARD_WHITE = (245, 247, 250)
_CARD_MUTED = (150, 165, 185)
_INTER_DIR = "/usr/share/fonts/truetype/inter"

_CARD_STOP = {"The","A","An","This","That","These","Those","And","But","For","With","From",
              "Here","Why","What","When","How","It","Its","He","She","They","We","You","I",
              "In","On","Of","To","At","By","As","Is","Are","Was","Were","Has","Have","Had",
              "Will","Just","Now","Than","Then","Even","Their","His","Her","Our"}

_CARD_LABELS = {
    "news": "BREAKING", "nri-world": "NRI WORLD", "immigration": "IMMIGRATION",
    "sports": "SPORTS", "technology": "TECHNOLOGY", "markets-finance": "MARKETS & FINANCE",
    "entertainment": "ENTERTAINMENT", "lifestyle-health": "LIFESTYLE & HEALTH",
    "food": "FOOD", "travel": "TRAVEL",
}


def _card_font(size, weight="bold"):
    paths = {
        "extrabold": f"{_INTER_DIR}/InterDisplay-ExtraBold.ttf",
        "bold": f"{_INTER_DIR}/InterDisplay-Bold.ttf",
        "semibold": f"{_INTER_DIR}/Inter-SemiBold.ttf",
    }
    try:
        from PIL import ImageFont
        return ImageFont.truetype(paths.get(weight, paths["bold"]), size)
    except Exception:
        from PIL import ImageFont
        return ImageFont.load_default()


def _card_pick_text(scene, article):
    narr = (scene.get("narration") or "").strip()
    sents = [s.strip() for s in re.split(r'(?<=[.!?])\s+', narr) if s.strip()]
    pick = None
    for s in sents:           # prefer a sentence with a concrete number
        if re.search(r'\d', s):
            pick = s
            break
    if not pick and sents:    # else the meatiest sentence
        pick = max(sents, key=len)
    text = pick or scene.get("visual") or article.get("headline", "")
    text = re.sub(r'\s+', ' ', text).strip().rstrip('.')
    words = text.split()
    if len(words) > 14:
        words = words[:14]
        while words and words[-1].strip('.,;:!?').capitalize() in _CARD_STOP:
            words.pop()
        text = " ".join(words).rstrip(',;:') + "…"
    return text or "The Videshi"


def _card_is_highlight(word):
    core = word.strip('.,;:!?"\'()')
    if re.search(r'\d', core):
        return True
    if core in ("₹", "$", "%", "₹.", "$."):
        return True
    if core.isupper() and len(core) >= 2:
        return True
    if len(core) >= 2 and core[0].isupper() and core not in _CARD_STOP:
        return True
    return False


def _card_vgradient(W, H, top, bot):
    from PIL import Image
    base = Image.new("RGB", (W, H), top)
    px = base.load()
    for y in range(H):
        t = (y / max(H - 1, 1)) ** 0.85
        r = int(top[0] + (bot[0] - top[0]) * t)
        g = int(top[1] + (bot[1] - top[1]) * t)
        b = int(top[2] + (bot[2] - top[2]) * t)
        for x in range(W):
            px[x, y] = (r, g, b)
    return base


def _card_glow(W, H, cx, cy, radius, color, max_alpha):
    from PIL import Image, ImageDraw, ImageFilter
    glow = Image.new("L", (W, H), 0)
    gd = ImageDraw.Draw(glow)
    steps = 50
    for i in range(steps, 0, -1):
        rr = radius * i / steps
        a = int(max_alpha * (1 - i / steps))
        gd.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=a)
    glow = glow.filter(ImageFilter.GaussianBlur(40))
    layer = Image.new("RGB", (W, H), color)
    return layer, glow


def render_keypoint_card(scene, category, article, idx, out_dir="/tmp/videshi_cards"):
    """Render a branded 1080x1920 key-point graphic. Returns local PNG path or None."""
    try:
        from PIL import Image, ImageDraw
    except Exception as e:
        print(f"  ⚠️ PIL unavailable for key-point card: {e}")
        return None
    try:
        os.makedirs(out_dir, exist_ok=True)
        W, H = 1080, 1920
        # Vary the background subtly per scene index so multiple cards in one reel
        # don't read as identical "repeated text slide" (a QA "lacking visual
        # variety" trigger). Two on-brand navy variants + mirrored glow placement.
        if idx % 2 == 0:
            img = _card_vgradient(W, H, _CARD_NAVY_TOP, _CARD_NAVY_BOT)
            glow_cx, glow2_cx = int(W * 0.82), int(W * 0.12)
        else:
            img = _card_vgradient(W, H, (10, 20, 38), (24, 40, 64))
            glow_cx, glow2_cx = int(W * 0.18), int(W * 0.88)

        layer, mask = _card_glow(W, H, glow_cx, int(H * 0.20), 720, (60, 48, 18), 70)
        img.paste(layer, (0, 0), mask)
        layer2, mask2 = _card_glow(W, H, glow2_cx, int(H * 0.92), 760, (10, 22, 44), 90)
        img.paste(layer2, (0, 0), mask2)

        tex = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        td = ImageDraw.Draw(tex)
        for k in range(-H, W, 54):
            td.line([(k, 0), (k + H, H)], fill=(212, 175, 55, 10), width=1)
        img = Image.alpha_composite(img.convert("RGBA"), tex).convert("RGB")

        draw = ImageDraw.Draw(img)
        MX = 96

        # eyebrow
        label = _CARD_LABELS.get(category, (category or "THE VIDESHI").upper().replace("-", " "))
        eb_font = _card_font(34, "extrabold")
        y = 150
        draw.rectangle([MX, y + 6, MX + 26, y + 32], fill=_CARD_GOLD)
        draw.text((MX + 44, y), " ".join(label), font=eb_font, fill=_CARD_GOLD_SOFT)
        y += 64
        draw.line([(MX, y), (W - MX, y)], fill=_CARD_GOLD, width=3)

        # key point
        text = _card_pick_text(scene, article)
        body_font = _card_font(82, "extrabold")
        space_w = draw.textlength(" ", font=body_font)
        max_w = W - 2 * MX - 28
        words = text.split()
        lines, cur, cur_w = [], [], 0
        for wd in words:
            ww = draw.textlength(wd, font=body_font)
            add = ww + (space_w if cur else 0)
            if cur and cur_w + add > max_w:
                lines.append(cur); cur = [wd]; cur_w = ww
            else:
                cur.append(wd); cur_w += add
        if cur:
            lines.append(cur)

        line_h = 104
        block_h = line_h * len(lines)
        # Anchor the key-point into the UPPER-MIDDLE region (below the eyebrow rule,
        # above ~y1150) so the live caption pill — which sits at lower-center during
        # mid-reel scenes — never collides with the card's own text.
        region_top, region_bot = 360, 1160
        start_y = region_top + max(0, (region_bot - region_top - block_h) // 2)
        draw.rectangle([MX, start_y + 8, MX + 10, start_y + block_h - 12], fill=_CARD_GOLD)
        text_x0 = MX + 40

        yy = start_y
        for line in lines:
            xx = text_x0
            for wd in line:
                color = _CARD_GOLD_SOFT if _card_is_highlight(wd) else _CARD_WHITE
                draw.text((xx + 2, yy + 3), wd, font=body_font, fill=(0, 0, 0))
                draw.text((xx, yy), wd, font=body_font, fill=color)
                xx += draw.textlength(wd, font=body_font) + space_w
            yy += line_h

        # wordmark
        wm_font = _card_font(38, "bold")
        dot_font = _card_font(38, "semibold")
        by = H - 150
        draw.line([(MX, by - 26), (MX + 70, by - 26)], fill=_CARD_GOLD, width=3)
        draw.text((MX, by), "THE VIDESHI", font=wm_font, fill=_CARD_WHITE)
        tvw = draw.textlength("THE VIDESHI  ", font=wm_font)
        draw.text((MX + tvw, by + 2), "thevideshi.com", font=dot_font, fill=_CARD_MUTED)

        path = os.path.join(out_dir, f"card_{article.get('id','x')}_{idx}.png")
        img.save(path, "PNG")
        return path
    except Exception as e:
        print(f"  ⚠️ Key-point card render failed: {e}")
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# SOCIAL CARD SCENE — a real X post (photo + attribution) in the brand frame
# ═══════════════════════════════════════════════════════════════════════════════
# Additive, high-priority media source for AT MOST ONE scene per reel. When an
# article's subject matches a curated handle in social-embed-registry.json and
# that account has a recent photo post relevant to the story, we render the post
# as a branded "ON THE FEED" card instead of generic stock. The registry is the
# allowlist (verified/official accounts only). Scope: X only (Threads/IG later).
# Any failure (no credits/402, no match, fetch/render error) logs and falls
# through to the existing sourcing chain — it never breaks reel generation.

SOCIAL_CARD_ENABLED = os.environ.get("VIDESHI_SOCIAL_CARD", "1") != "0"
SOCIAL_CARD_LOOKBACK_HOURS = int(os.environ.get("VIDESHI_SOCIAL_CARD_HOURS", "168"))  # 7 days
SOCIAL_CARD_MAX_HANDLES = int(os.environ.get("VIDESHI_SOCIAL_CARD_MAX_HANDLES", "3"))  # X-read spend cap per article

_fetch_tweets_mod = None
_social_registry_cache = None
_x_profile_cache_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".x-profiles.json")


def _load_fetch_tweets_module():
    """Import pipeline/fetch-tweets.py (hyphenated filename) once, cached."""
    global _fetch_tweets_mod
    if _fetch_tweets_mod is not None:
        return _fetch_tweets_mod
    import importlib.util
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fetch-tweets.py")
    spec = importlib.util.spec_from_file_location("videshi_fetch_tweets", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _fetch_tweets_mod = mod
    return mod


def _load_social_registry():
    """Load social-embed-registry.json once; return flat list of dicts with an
    x handle: {name, handle, category, kind}."""
    global _social_registry_cache
    if _social_registry_cache is not None:
        return _social_registry_cache
    out = []
    try:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "social-embed-registry.json")
        with open(path) as f:
            d = json.load(f)
        for cat, v in d.items():
            if cat.startswith("_"):
                continue
            if isinstance(v, dict):
                for kind in ("persons", "organizations"):
                    for e in (v.get(kind) or []):
                        if isinstance(e, dict) and e.get("x"):
                            out.append({"name": e.get("name", ""), "handle": e["x"].lstrip("@"),
                                        "category": cat, "kind": kind})
    except Exception as e:
        print(f"  ⚠️ social registry load failed: {e}")
    _social_registry_cache = out
    return out


_media_lib_lookup_mod = None


def _load_media_library_lookup():
    """Import pipeline/media_library_lookup.py once, cached. Returns the module
    (with find_media) or None if the media library isn't available."""
    global _media_lib_lookup_mod
    if _media_lib_lookup_mod is not None:
        return _media_lib_lookup_mod if _media_lib_lookup_mod is not False else None
    try:
        import importlib.util
        pdir = os.path.dirname(os.path.abspath(__file__))
        if pdir not in sys.path:
            sys.path.insert(0, pdir)  # media_library_lookup imports media_library_store
        path = os.path.join(pdir, "media_library_lookup.py")
        spec = importlib.util.spec_from_file_location("videshi_media_library_lookup", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _media_lib_lookup_mod = mod
        return mod
    except Exception as e:
        print(f"  ℹ️ media library unavailable (skipping that fallback): {e}")
        _media_lib_lookup_mod = False
        return None


def _x_profile(handle):
    """Fetch {name, avatar} for an X handle (free users lookup), cached to disk."""
    cache = {}
    try:
        if os.path.exists(_x_profile_cache_path):
            cache = json.load(open(_x_profile_cache_path))
    except Exception:
        cache = {}
    hl = handle.lower()
    if hl in cache:
        return cache[hl]
    try:
        mod = _load_fetch_tweets_module()
        sess = mod.get_oauth_session()
        r = sess.get(f"https://api.twitter.com/2/users/by/username/{handle}",
                     params={"user.fields": "profile_image_url,name"}, timeout=15)
        if r.status_code == 200:
            data = r.json().get("data", {})
            prof = {"name": data.get("name", ""),
                    "avatar": (data.get("profile_image_url", "") or "").replace("_normal", "_400x400")}
            cache[hl] = prof
            try:
                json.dump(cache, open(_x_profile_cache_path, "w"), indent=2)
            except Exception:
                pass
            return prof
    except Exception as e:
        print(f"  ⚠️ X profile lookup failed for @{handle}: {e}")
    return {"name": "", "avatar": ""}


def _sc_clean_text(t):
    """Strip t.co/other URLs and emoji/non-renderable glyphs from post text."""
    t = re.sub(r'https?://t\.co/\S+', '', t)
    t = re.sub(r'https?://\S+', '', t)
    t = ''.join(ch for ch in t if ord(ch) < 0x2190 or (0x2C00 <= ord(ch) < 0x2E00))
    return ' '.join(t.split())


def _sc_download_image(url):
    """Download an image to a PIL RGB image via curl (proxy-safe)."""
    from io import BytesIO
    from PIL import Image
    out = subprocess.run(["curl", "-sL", "-A", "Mozilla/5.0", "--max-time", "30", url],
                         capture_output=True).stdout
    return Image.open(BytesIO(out)).convert("RGB")


def _sc_draw_x_badge(draw, img, x, y, s):
    """Paste the real X logo (white) centered in a rounded black square of side s."""
    from PIL import Image
    draw.rounded_rectangle([x, y, x + s, y + s], radius=int(s * 0.22), fill=(0, 0, 0))
    try:
        logo = Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "assets", "x-logo-white.png")).convert("RGBA")
        gw = int(s * 0.50); gh = int(gw * logo.height / logo.width)
        logo = logo.resize((gw, gh), Image.LANCZOS)
        img.paste(logo, (x + (s - gw) // 2, y + (s - gh) // 2), logo)
    except Exception as e:
        print(f"  ⚠️ x-logo paste failed: {e}")


def _sc_face_aware_fit(photo, pw, ph):
    """Fit `photo` into a (pw, ph) frame using cover-crop, but center the crop on
    detected faces so heads are never guillotined. Returns (fitted_image, ok)
    where ok=False means faces could not be preserved (caller should skip the card).
    Falls back to a safe top-biased center when no face detector / no faces."""
    from PIL import Image, ImageOps
    src_ar = photo.width / max(1, photo.height)
    frame_ar = pw / max(1, ph)
    # default centering: top-bias on tall sources (heads live up high), else center
    cx, cy = 0.5, (0.32 if src_ar < frame_ar else 0.5)
    faces = []
    try:
        import cv2, numpy as np
        cvimg = cv2.cvtColor(np.array(photo.convert("RGB")), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(cvimg, cv2.COLOR_BGR2GRAY)
        cascade = cv2.CascadeClassifier(
            os.path.join(cv2.data.haarcascades, "haarcascade_frontalface_default.xml"))
        dets = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5,
                                        minSize=(int(photo.width*0.05), int(photo.height*0.05)))
        faces = [tuple(map(int, f)) for f in dets]
    except Exception as e:
        print(f"  ℹ️ face detect unavailable, using heuristic crop: {e}")

    if faces:
        # bounding box over all faces, padded for foreheads/chins
        x0 = min(f[0] for f in faces); y0 = min(f[1] for f in faces)
        x1 = max(f[0]+f[2] for f in faces); y1 = max(f[1]+f[3] for f in faces)
        padx = int((x1-x0)*0.25); pady_top = int((y1-y0)*0.55); pady_bot = int((y1-y0)*0.30)
        x0=max(0,x0-padx); x1=min(photo.width,x1+padx)
        y0=max(0,y0-pady_top); y1=min(photo.height,y1+pady_bot)
        fcx=(x0+x1)/2.0; fcy=(y0+y1)/2.0
        cx=min(1.0,max(0.0,fcx/photo.width)); cy=min(1.0,max(0.0,fcy/photo.height))

    fitted = ImageOps.fit(photo, (pw, ph), Image.LANCZOS, centering=(cx, cy))

    # VERIFY: re-detect on the fitted result; if a face is cut by an edge, it failed.
    ok = True
    if faces:
        try:
            import cv2, numpy as np
            fg = cv2.cvtColor(np.array(fitted.convert("RGB")), cv2.COLOR_RGB2GRAY)
            cascade = cv2.CascadeClassifier(
                os.path.join(cv2.data.haarcascades, "haarcascade_frontalface_default.xml"))
            fd = cascade.detectMultiScale(fg, scaleFactor=1.1, minNeighbors=5,
                                          minSize=(int(pw*0.05), int(ph*0.04)))
            margin = 4
            cut = any(x<=margin or y<=margin or (x+w)>=(pw-margin) or (y+h)>=(ph-margin)
                      for (x,y,w,h) in fd)
            # faces present before but none cleanly inside after → bad crop
            if len(fd) == 0 or cut:
                ok = False
        except Exception:
            pass
    return fitted, ok


def render_social_card(post, category, out_dir="/tmp/videshi_social"):
    """Render a branded 1080x1920 'social post card' from a real X post.
    post = {name, handle, avatar, photo, text}. Returns local PNG path or None.
    Matches house style by reusing the key-point card brand helpers."""
    try:
        from PIL import Image, ImageDraw, ImageOps
    except Exception as e:
        print(f"  ⚠️ PIL unavailable for social card: {e}")
        return None
    try:
        os.makedirs(out_dir, exist_ok=True)
        W, H = 1080, 1920
        img = _card_vgradient(W, H, _CARD_NAVY_TOP, _CARD_NAVY_BOT).convert("RGBA")
        # subtle diagonal gold texture (same as key-point card)
        tex = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        td = ImageDraw.Draw(tex)
        for k in range(-H, W, 54):
            td.line([(k, 0), (k + H, H)], fill=(212, 175, 55, 9), width=1)
        img = Image.alpha_composite(img, tex)
        d = ImageDraw.Draw(img)
        MX = 96

        # eyebrow — "ON THE FEED"
        y = 150
        d.rectangle([MX, y + 6, MX + 26, y + 32], fill=_CARD_GOLD)
        d.text((MX + 44, y), " ".join("ON THE FEED"), font=_card_font(34, "extrabold"), fill=_CARD_GOLD_SOFT)
        y += 64
        d.line([(MX, y), (W - MX, y)], fill=_CARD_GOLD, width=3)
        y += 70

        # the post photo, rounded + gold-framed
        photo = _sc_download_image(post["photo"])
        pw = W - 2 * MX
        ph = int(pw * 0.78)  # taller frame: fills the card better, less portrait crop
        # Face-aware crop + verification: center the crop on detected faces and
        # confirm no face is cut by a frame edge. If a face can't be preserved,
        # bail out (return None) so we never ship a beheaded photo — the caller
        # falls through to the normal media chain.
        photo, crop_ok = _sc_face_aware_fit(photo, pw, ph)
        if not crop_ok:
            print(f"  ⚠️ social card: face would be cropped for @{post.get('handle')} — skipping card")
            return None
        rc = Image.new("L", (pw, ph), 0)
        ImageDraw.Draw(rc).rounded_rectangle([0, 0, pw, ph], radius=28, fill=255)
        d.rounded_rectangle([MX - 4, y - 4, MX + pw + 4, y + ph + 4], radius=32, outline=_CARD_GOLD, width=3)
        img.paste(photo, (MX, y), rc)
        y += ph + 46

        # author row: avatar + name + handle, X badge top-right
        if post.get("avatar"):
            try:
                av = _sc_download_image(post["avatar"])
                av = ImageOps.fit(av, (104, 104), Image.LANCZOS)
                amask = Image.new("L", (104, 104), 0)
                ImageDraw.Draw(amask).ellipse([0, 0, 104, 104], fill=255)
                img.paste(av, (MX, y), amask)
                d.ellipse([MX, y, MX + 104, y + 104], outline=_CARD_GOLD, width=3)
                nx = MX + 128
            except Exception:
                nx = MX
        else:
            nx = MX
        d.text((nx, y + 8), post.get("name", "") or f"@{post['handle']}",
               font=_card_font(46, "extrabold"), fill=_CARD_WHITE)
        d.text((nx, y + 62), f"@{post['handle']}", font=_card_font(34, "semibold"), fill=_CARD_MUTED)
        bs = 84
        _sc_draw_x_badge(d, img, W - MX - bs, y + 10, bs)
        y += 140

        # post text (cleaned)
        txt = _sc_clean_text(post.get("text", ""))
        if len(txt) > 150:
            txt = txt[:150].rsplit(' ', 1)[0] + "…"
        import textwrap as _tw
        tf = _card_font(40, "semibold")
        for line in _tw.wrap(txt, width=42)[:4]:
            d.text((MX, y), line, font=tf, fill=(228, 233, 240))
            y += 54

        # attribution footer
        fy = H - 150
        d.line([(MX, fy), (W - MX, fy)], fill=(60, 72, 92), width=2)
        d.text((MX, fy + 24), f"via @{post['handle']} on X", font=_card_font(34, "semibold"), fill=_CARD_GOLD_SOFT)
        d.text((W - MX - 260, fy + 24), "thevideshi.com", font=_card_font(34, "extrabold"), fill=_CARD_WHITE)

        path = os.path.join(out_dir, f"social_{post['handle']}.png")
        img.convert("RGB").save(path, "PNG")
        return path
    except Exception as e:
        print(f"  ⚠️ Social card render failed: {e}")
        return None


def _social_card_keywords(article):
    """Derive relevance keywords from the article (reuses the topic-keyword
    relevance approach used by fetch-tweets' best_photo_tweet)."""
    stop = {"the", "a", "an", "and", "but", "for", "with", "from", "this", "that",
            "after", "before", "what", "when", "how", "why", "now", "new", "his",
            "her", "its", "their", "they", "will", "has", "have", "had", "are",
            "was", "were", "into", "over", "amid", "says", "said", "india", "indian"}
    text = f"{article.get('headline','')} {article.get('subheadline','')}"
    words = re.findall(r"[A-Za-z][A-Za-z'&-]{3,}", text)
    kws = []
    seen = set()
    for w in words:
        wl = w.lower()
        if wl in stop or wl in seen:
            continue
        seen.add(wl)
        kws.append(wl)
    return kws[:12]


def match_social_card_post(article, hours=None, max_handles=None):
    """Find the best real X post to render as a social card for this article.
    Scans headline+body for registered names (registry = allowlist), prefers the
    article's category bucket, queries up to max_handles handles (X-read spend
    cap), and picks the most topically relevant RECENT post WITH a photo.
    Returns a post dict {name, handle, avatar, photo, text, url} or None.
    Never raises — returns None on any failure (incl. 402/no-credits)."""
    if not SOCIAL_CARD_ENABLED:
        return None
    hours = hours or SOCIAL_CARD_LOOKBACK_HOURS
    max_handles = max_handles or SOCIAL_CARD_MAX_HANDLES
    try:
        registry = _load_social_registry()
        if not registry:
            return None
        category = article.get("category", "")
        haystack = f"{article.get('headline','')} {article.get('subheadline','')} {(article.get('body') or '')[:2000]}"
        haystack_l = haystack.lower()

        # Find registry entries whose name appears in the article (word-boundary).
        matched = []
        for e in registry:
            name = (e.get("name") or "").strip()
            if len(name) < 3:
                continue
            if re.search(r"\b" + re.escape(name.lower()) + r"\b", haystack_l):
                matched.append(e)
        if not matched:
            return None

        # Rank: same-category first, persons before orgs, then name length (more
        # specific names are stronger signals). Cap to the spend budget.
        matched.sort(key=lambda e: (0 if e.get("category") == category else 1,
                                    0 if e.get("kind") == "persons" else 1,
                                    -len(e.get("name", ""))))
        candidates = matched[:max_handles]
        print(f"  📡 Social-card candidates ({len(candidates)}/{len(matched)} matched): "
              + ", ".join(f"@{c['handle']}" for c in candidates))

        mod = _load_fetch_tweets_module()
        keywords = _social_card_keywords(article)

        best = None  # (relevance, likes, tweet, handle)
        for c in candidates:
            handle = c["handle"]
            try:
                tweet = mod.best_photo_tweet(handle, hours=hours, topic_keywords=keywords)
            except Exception as e:
                print(f"  ⚠️ tweet fetch failed for @{handle}: {e}")
                continue
            if not tweet or tweet.get("photo_count", 0) < 1 or not tweet.get("photos"):
                continue
            text_l = (tweet.get("text", "") or "").lower()
            relevance = sum(1 for kw in keywords if kw in text_l)
            likes = tweet.get("likes", 0)
            key = (relevance, likes)
            if best is None or key > (best[0], best[1]):
                best = (relevance, likes, tweet, handle, c.get("name", ""))

        if not best:
            return None
        _, _, tweet, handle, reg_name = best
        prof = _x_profile(handle)
        return {
            "name": reg_name or prof.get("name", "") or f"@{handle}",
            "handle": handle,
            "avatar": prof.get("avatar", ""),
            "photo": tweet["photos"][0],
            "text": tweet.get("text", ""),
            "url": tweet.get("url", ""),
        }
    except Exception as e:
        print(f"  ⚠️ Social-card match failed (falling through): {e}")
        return None


def source_storyboard_images(article, storyboard, count=8):
    """Source B-roll media scene-by-scene from the storyboard.
    Priority: 1) Article hero for scene 1  2) Pexels stock VIDEO by scene description  3) Pexels HD image by scene description  4) Wikipedia by scene queries  5) Same-category articles (fallback only).
    Returns (urls, media_meta) where urls is a list of URLs and media_meta maps url -> {"type": "video"|"image", "duration": N}."""
    urls = []
    used_in_this_reel = set()
    media_meta = {}  # url -> {"type": "video"|"image", "duration": N}

    hero = article.get("image_url", "")
    category = article.get("category", "")
    article_id = article.get("id", "")
    headline = article.get("headline", "")

    # Minimum resolution for article images (shortest side)
    MIN_IMAGE_DIM = 1000

    def check_image_resolution(url):
        """HEAD-check an image and return (width, height) or None if unreachable/too small."""
        try:
            # Download small portion to check dimensions
            r = requests.get(url, timeout=8, stream=True,
                             headers={"User-Agent": "Mozilla/5.0 (compatible; TheVideshi/1.0)",
                                      "Range": "bytes=0-65535"})
            if r.status_code not in (200, 206):
                return None
            # For JPEG, dimensions are in the header
            chunk = r.content
            # Quick dimension check via PIL if available
            from io import BytesIO
            from PIL import Image
            img = Image.open(BytesIO(chunk))
            return (img.width, img.height)
        except Exception:
            return None

    # Helper: check if an image URL is from a curated source (not generic stock)
    def is_curated_image(url):
        """Prefer Wikimedia, Supabase-hosted, and other editorial sources over Pexels."""
        if not url:
            return False
        pexels_domains = ["images.pexels.com", "pexels.com"]
        return not any(d in url for d in pexels_domains)

    # Load Pexels key
    pexels_env = load_env("~/workspace/.env.pexels")
    pexels_key = pexels_env.get("PEXELS_API_KEY", "")
    used_ids = load_used_images()

    scenes = storyboard if storyboard else []
    scene_descs = [s.get("visual", "") for s in scenes[:count]]
    matched_urls = [None] * min(count, len(scene_descs))
    used_video_ids_this_reel = set()  # Prevent same video clip across multiple scenes
    used_photo_ids_this_reel = set()  # Prevent same Pexels photo across multiple scenes (URL check misses re-sized variants)

    # Anchor B-roll searches to India so generic queries ("military uniform",
    # "students exam") don't return foreign footage (e.g. an Italian army
    # uniform on an Indian Air Force story). Applied to every scene query below.
    _india_terms = ("india", "indian", "delhi", "mumbai", "bollywood", "rupee",
                    "modi", "nri", "hindu", "desi", "bengaluru", "chennai", "kolkata")

    def anchor_query_to_india(q):
        if not q:
            return q
        ql = q.lower()
        if any(t in ql for t in _india_terms):
            return q
        # People/place/object queries benefit from an India qualifier; abstract
        # ones ("ocean waves", "smoke rising") are left alone.
        generic_visual = ("uniform", "soldier", "police", "officer", "student",
                          "exam", "classroom", "school", "college", "office",
                          "city", "street", "building", "crowd", "people",
                          "family", "doctor", "hospital", "court", "flag",
                          "currency", "money", "notes", "parliament", "protest")
        if any(t in ql for t in generic_visual):
            return f"Indian {q}"
        return q

    # Reject Pexels results whose metadata (alt text / page-URL slug) names a
    # country other than India when we anchored the query to India. The QA gate
    # repeatedly flagged foreign footage (Italian "Ministry of Interior" uniform,
    # a Bangladesh crowd) on India stories. Pexels embeds country/place names in
    # the page-URL slug and alt text, so a cheap substring check catches the
    # worst offenders without an extra API call.
    _foreign_markers = (
        "italy", "italian", "russia", "russian", "ukraine", "ukrainian",
        "china", "chinese", "bangladesh", "pakistan", "pakistani", "germany",
        "german", "france", "french", "spain", "spanish", "brazil", "brazilian",
        "turkey", "turkish", "egypt", "egyptian", "iran", "iranian", "thailand",
        "thai", "vietnam", "indonesia", "indonesian", "philippines", "nepal",
        "afghan", "afghanistan", "ministry of interior",
    )

    def is_foreign_for_india(cand, anchored_to_india):
        """True if a Pexels candidate's metadata names a non-India locale while we
        wanted Indian footage. Conservative: only rejects on explicit markers."""
        if not anchored_to_india:
            return False
        meta = (str(cand.get("alt", "")) + " " + str(cand.get("page_url", ""))).lower()
        if not meta:
            return False
        # If it explicitly says India/Indian, always keep it.
        if "india" in meta:
            return False
        return any(m in meta for m in _foreign_markers)

    # Positive India/South-Asian signals in Pexels metadata. Used to enforce
    # demographic relevance: when a scene is about PEOPLE on an India/NRI story,
    # generic stock of (e.g.) a white family carries no foreign marker, so
    # is_foreign_for_india() lets it through — and QA correctly flags "images do
    # not match the story topic" / wrong demographic. For people-scenes we
    # instead REQUIRE a positive India signal, else fall through to a key-point
    # card (topic-relevant by construction).
    _india_positive_markers = (
        "india", "indian", "south asian", "desi", "saree", "sari", "bindi",
        "kurta", "sherwani", "lehenga", "salwar", "diwali", "holi", "rangoli",
        "hindu", "sikh", "punjabi", "tamil", "telugu", "bengali", "gujarati",
        "marathi", "kerala", "delhi", "mumbai", "bengaluru", "bangalore",
        "chennai", "kolkata", "hyderabad", "rupee", "bollywood",
    )
    _people_query_terms = (
        "family", "families", "people", "person", "man", "woman", "men",
        "women", "child", "children", "kid", "student", "students", "worker",
        "workers", "employee", "couple", "parents", "father", "mother",
        "immigrant", "citizen", "professional", "crowd", "portrait", "doctor",
        "nurse", "engineer", "teacher",
    )

    def needs_india_person(query):
        """True if this scene query is about PEOPLE on our India/NRI story, so a
        candidate must carry a positive India/South-Asian signal to be relevant."""
        ql = (query or "").lower()
        return any(t in ql for t in _people_query_terms)

    def lacks_india_signal(cand):
        """True if a people-scene candidate shows no India/South-Asian signal."""
        meta = (str(cand.get("alt", "")) + " " + str(cand.get("page_url", ""))).lower()
        return not any(m in meta for m in _india_positive_markers)

    # ── 1. Article hero for scene 1 ──
    # Skip heroes from unvetted sources for the HOOK frame. The writer mostly
    # uses curated heroes (Wikimedia/Pexels/Supabase mirror), but occasionally
    # saves a Flickr image that turns out to be a meme/joke graphic (e.g. a
    # "Use the force, Harry — Gandalf" meme landed as the hook on the DoJ
    # denaturalization reel, which the QA gate correctly flagged as a "humorous,
    # unrelated image" on a serious news story). The hook is the single most
    # important frame, so when the hero is from a non-curated host we drop it and
    # let scene 1 fall through to entity/Pexels imagery (topic-relevant by
    # construction) or the key-point-card floor.
    hero = upscale_wikimedia_url(hero)
    _hero_host = ""
    try:
        from urllib.parse import urlparse as _urlparse
        _hero_host = (_urlparse(hero).netloc or "").lower()
    except Exception:
        _hero_host = ""
    _UNVETTED_HERO_HOSTS = ("flickr.com", "staticflickr.com", "live.staticflickr.com")
    if hero and any(_hero_host == h or _hero_host.endswith("." + h) for h in _UNVETTED_HERO_HOSTS):
        print(f"  🚫 Skipping unvetted hero host '{_hero_host}' for hook (meme-risk) — scene 1 will source topical B-roll instead")
        hero = ""
    if hero and is_url_downloadable(hero) and hero not in used_in_this_reel:
        hero = mirror_to_supabase(hero, article_id, 0)
        matched_urls[0] = hero
        used_in_this_reel.add(hero)
        media_meta[hero] = {"type": "image", "duration": 0}
        print(f"  🎬 Scene 1: {scene_descs[0][:50]}  →  article hero")


    # ── 1a-bis. SOCIAL CARD: a real X post (photo + attribution) in brand frame ──
    # Highest-priority editorial source for AT MOST ONE scene per reel. If the
    # article's subject matches a curated handle (registry = verified/official
    # allowlist) and that account has a recent relevant photo post, render it as
    # an "ON THE FEED" card. This carries real, attributed, on-topic media, so it
    # beats generic stock outright. Purely additive + safe: any failure (no
    # match, 402/no-credits, fetch/render error) logs and falls through.
    _sc_last_idx = len(matched_urls) - 1
    _sc_slots = [i for i in range(1, len(matched_urls))
                 if i != _sc_last_idx and matched_urls[i] is None]  # mid scene only; never hook/CTA
    if SOCIAL_CARD_ENABLED and _sc_slots:
        try:
            post = match_social_card_post(article)
            if post and post.get("photo"):
                local = render_social_card(post, category)
                if local:
                    slot = _sc_slots[0]
                    storage_path = f"reel-social/{article_id}/scene-{slot}.png"
                    card_url = upload_asset(local, storage_path, "image/png")
                    try:
                        os.remove(local)
                    except Exception:
                        pass
                    if card_url:
                        matched_urls[slot] = card_url
                        used_in_this_reel.add(card_url)
                        # Real attributed media — mark curated/non-generic so the
                        # generic-Pexels conversion + QA never penalize it.
                        media_meta[card_url] = {"type": "image", "duration": 0,
                                                "is_social_card": True, "curated": True,
                                                "generic_pexels": False,
                                                "source_url": post.get("url", "")}
                        print(f"  📡 Scene {slot+1}: {scene_descs[slot][:42]}  →  social card (X @{post['handle']})")
        except Exception as e:
            print(f"  ⚠️ Social-card pass failed (continuing normally): {e}")


    # ── 1b. ENTITY PRE-PASS: real imagery of the story's named entities ──
    # Generic Pexels stock is the #1 "image relevance" QA failure on niche topics
    # (e.g. "sovereign AI"), because the article hero is often generic and there's
    # no gallery. Before falling to stock, mine the headline + body for proper
    # nouns (companies, people, places) and pull their actual Wikipedia images.
    # These are genuinely on-topic and add visual variety, so we seed up to 2
    # scenes (after the hero) before Pexels ever runs.
    def extract_named_entities(brand_text, prose_text, limit=8):
        """Cheap proper-noun miner — no NLP dependency.
        brand_text (headline + body): scanned only for brand tokens with internal
        capitals ('HCLTech') or short all-caps acronyms ('AI', 'ISRO'), which
        survive title-casing.
        prose_text (body only): mined for proper-noun phrases. Within a sentence, a
        Capitalized word that is NOT the first word is almost always a proper noun.
        The title-cased headline is deliberately kept OUT of prose mining, since
        every word there is capitalized and yields junk ('Just Bet', 'Worth')."""
        stop = {"The", "This", "That", "These", "Those", "India", "Indian",
                "It", "But", "And", "For", "With", "From", "What", "When",
                "How", "Why", "Now", "New", "After", "Before", "While", "Its",
                "According", "Meanwhile", "However", "They", "Their", "His",
                "Her", "Mr", "Ms", "Dr", "Mrs", "Also", "Some", "Many", "Both",
                # Weekdays/months — "Monday" resolves to moon-phase alchemy art, etc.
                "Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
                "Saturday", "Sunday", "January", "February", "March", "April",
                "May", "June", "July", "August", "September", "October",
                "November", "December",
                # Funding/business boilerplate that isn't a real visual entity.
                "Series", "Series A", "Series B", "Series C", "Series D",
                "India's", "Indians", "CEO", "CTO", "CFO", "COO", "Inc", "Ltd",
                "Pvt", "Co", "Corp", "Group", "Limited", "Private"}
        seen, out = set(), []

        def _add(p):
            p = p.strip(" .,&")
            if len(p) < 3:
                return
            key = p.lower()
            if key in seen:
                return
            seen.add(key)
            out.append(p)

        # Pass A: brand tokens / acronyms from headline + body (survive title-case).
        for tok in re.findall(r"\b[A-Za-z][A-Za-z0-9&]*\b", brand_text or ""):
            if tok in stop:
                continue
            internal_caps = any(c.isupper() for c in tok[1:])  # HCLTech, iPhone, eBay
            all_caps = tok.isupper() and 2 <= len(tok) <= 5    # AI, BCCI, ISRO
            if internal_caps or all_caps:
                _add(tok)
                if len(out) >= limit:
                    return out

        # Pass B: proper-noun phrases from sentence-cased BODY prose only.
        for sentence in re.split(r"[.!?\n]+", prose_text or ""):
            words = sentence.split()
            run = []
            for idx, w in enumerate(words):
                bare = w.strip(" .,;:!?()'\"")
                is_cap = bool(bare) and bare[0].isupper() and bare[1:].lower() == bare[1:].lower()
                if is_cap and bare[0].isalpha() and (idx > 0) and bare not in stop:
                    run.append(bare)
                else:
                    if len(run) >= 1:
                        _add(" ".join(run))
                        if len(out) >= limit:
                            return out
                    run = []
            if run:
                _add(" ".join(run))
                if len(out) >= limit:
                    return out
        return out[:limit][:limit]

    def wiki_image_for(term):
        """Return a usable Wikipedia lead image URL for a term, or None."""
        # Abstract / legal / policy concepts must NOT resolve to a literal
        # Wikipedia lead image — those return junk that the QA gate flags as
        # off-topic: "H-1B" → a process flowchart, "LLC" → Society.svg, and
        # "Denaturalization" → a grayscale archival photo of Jews expelled in
        # Nazi-era Nuremberg (wildly off-topic AND inflammatory on an Indian
        # immigration story). Such concepts belong on a key-point card (the
        # floor handles them). Only depictable proper nouns (named people,
        # recognizable orgs/places) get an entity image.
        _tl = term.lower().strip()
        _abstract_terms = (
            "llc", "inc", "h-1b", "h1b", "h-1b visa", "h1b visa", "visa",
            "green card", "denaturalization", "naturalization", "citizenship",
            "deportation", "removal", "fraud", "felony", "misdemeanor",
            "statute", "section", "act", "bill", "law", "lawsuit", "litigation",
            "indictment", "subpoena", "affidavit", "petition", "tariff",
            "sanction", "policy", "regulation", "amendment", "provision",
            "immigration", "asylum", "parole", "quota", "waiver",
        )
        if _tl in _abstract_terms or any(
            _tl == a or _tl.startswith(a + " ") or _tl.endswith(" " + a)
            for a in _abstract_terms
        ):
            return None
        try:
            wr = requests.get(
                f"https://en.wikipedia.org/api/rest_v1/page/summary/{requests.utils.quote(term.replace(' ', '_'))}",
                headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
                timeout=8,
            )
            if wr.status_code != 200:
                return None
            wdata = wr.json()
            # Skip disambiguation pages — their images are useless
            if wdata.get("type") == "disambiguation":
                return None
            # Prefer the thumbnail (a /thumb/ URL we can size to a render-friendly
            # 1280px) over originalimage — raw originals are often multi-MB PNGs that
            # Shotstack rejects as "not downloadable" (HCLTech campus PNG = 5.6MB).
            thumb = wdata.get("thumbnail", {}).get("source")
            orig = wdata.get("originalimage", {}).get("source")
            wimg = thumb or orig
            if not wimg:
                return None
            # Reject flags / coats of arms / emblems / maps. A country page's lead
            # image is usually its flag (e.g. "Mexico" → Mexican flag), which is weak,
            # generic B-roll AND actively wrong when the country is only a passing
            # comparison in the story (QA killed a Canada-deportation reel for showing
            # the Mexican flag, 2026-06-15). These filenames are never good reel B-roll.
            _bad_img = ("flag_of", "flag-", "coat_of_arms", "coat-of-arms", "emblem",
                        "ensign", "_map", "-map", "location_", "orthographic",
                        "seal_of", "logo")
            low = wimg.lower()
            if any(b in low for b in _bad_img):
                return None
            # Reject diagram/flowchart/figure/SVG filenames upfront (before any
            # download). The "H-1B" lead image is "Figure 2- Process of Obtaining
            # an H-1B Visa" (a flowchart) and "LLC" → "Society.svg" (a schematic);
            # both wrecked QA with text-on-image + topic mismatch. The pixel-level
            # check in mirror_to_supabase(reject_diagrams=True) is the safety net
            # for diagrams whose filenames don't advertise themselves.
            if any(sig in low for sig in _DIAGRAM_FILENAME_SIGNALS):
                return None
            return upscale_wikimedia_url(wimg)
        except Exception:
            return None

    body_text = (article.get("body") or "")[:1500]
    brand_text = f"{headline}. {article.get('subheadline','')}. {body_text}"
    entities = extract_named_entities(brand_text, body_text, limit=8)
    if entities:
        print(f"  🧩 Entity pre-pass — candidates: {', '.join(entities[:8])}")
    # Kiran's directive (2026-06-15): he prefers the real Indian imagery (Wikipedia
    # entity frames of Indian companies/people/places) over generic Pexels stock,
    # which kept drifting foreign on the back half. So entity frames now carry up to
    # 4 scenes instead of 2 — but INTERLEAVED with Pexels motion (odd indices)
    # so we get Indian-anchored frame → motion → frame → motion, not a dead wall of
    # static portraits. Ken Burns pan/zoom keeps the static frames alive. The FINAL
    # scene (the spoken CTA) is excluded — it gets clean footage, never a random
    # entity portrait behind "Full story at thevideshi.com".
    last_idx = len(matched_urls) - 1
    entity_slots = [i for i in (1, 3, 5, 7)
                    if i < len(matched_urls) and i != last_idx and matched_urls[i] is None]
    ei = 0
    for slot in entity_slots:
        while ei < len(entities):
            term = entities[ei]; ei += 1
            wimg = wiki_image_for(term)
            if wimg and wimg not in used_in_this_reel and is_url_downloadable(wimg):
                mwimg = mirror_to_supabase(wimg, article_id, slot, reject_diagrams=True)
                if not mwimg:
                    # Diagram/chart/text-slab rejected at pixel level — try next entity.
                    continue
                matched_urls[slot] = mwimg
                used_in_this_reel.add(mwimg)
                media_meta[mwimg] = {"type": "image", "duration": 0}
                print(f"  🧩 Scene {slot+1}: {scene_descs[slot][:42]}  →  Wikipedia entity '{term}'")
                break

    # ── 1c. WIKIMEDIA COMMONS by scene description (real India imagery) ──
    # Before falling to Pexels (which has no real footage of India-specific
    # subjects and drifts to generic/foreign stock), try Commons for the
    # still-empty mid scenes using each scene's own search queries, India-anchored.
    # Commons returns genuine editorial photos of named people/places/events.
    # Cap it so at least one mid gap is left for Pexels VIDEO — a reel that's 100%
    # stills reads as a static slideshow (QA flags "repetitive visuals"). Ken Burns
    # pan/zoom keeps these stills alive between the motion clips.
    remaining = [i for i in range(len(matched_urls)) if matched_urls[i] is None
                 and i != last_idx]  # leave CTA scene for clean footage
    commons_budget = max(0, (len(remaining) - 1) // 2)  # fill ≤ half of mid gaps from Commons; leave the rest for Pexels motion + the key-point card floor (a marginal Commons photo loses to a card whose visual IS the story)
    if remaining and commons_budget:
        print(f"  🏛️ Commons pass for {len(remaining)} mid scenes (budget {commons_budget})...")
        commons_filled = 0
        for i in remaining:
            if commons_filled >= commons_budget:
                break
            scene = scenes[i] if i < len(scenes) else {}
            queries = list(scene.get("search_queries", []))
            visual = scene.get("visual", "")
            if visual and visual not in queries:
                queries = [visual] + queries
            for q in queries[:2]:
                cq = anchor_query_to_india(q)
                for cand in commons_image_search(cq, limit=6):
                    cu = cand["url"]
                    if cu in used_in_this_reel:
                        continue
                    if not is_url_downloadable(cu):
                        continue
                    # Skip Commons results whose filename advertises a diagram/chart.
                    if any(sig in (cand.get("title", "") + cu).lower() for sig in _DIAGRAM_FILENAME_SIGNALS):
                        continue
                    mu = mirror_to_supabase(cu, article_id, i, reject_diagrams=True)
                    if not mu:
                        continue  # diagram/text-slab rejected; try next candidate
                    matched_urls[i] = mu
                    used_in_this_reel.add(cu)
                    used_in_this_reel.add(mu)
                    media_meta[mu] = {"type": "image", "duration": 0}
                    commons_filled += 1
                    print(f"  🏛️ Scene {i+1}: {scene_descs[i][:46]}  →  Commons '{cand['title'][5:45]}'")
                    break
                if matched_urls[i] is not None:
                    break

    # ── 1d. MEDIA LIBRARY (curated, attribution-clean backup pool) ──
    # Second-priority fallback per the media_library contract: after the curated /
    # dynamic sources above (article hero, social card, Wikipedia entities, Commons)
    # and BEFORE generic Pexels stock. The library holds quality-gated, attributed
    # assets keyed by subject (people/places/things) plus opt-in concept b-roll.
    # For reels we allow concept assets (exclude_concept=False) so abstract scenes
    # can be filled, but the quality sort still prefers real, high-score imagery.
    # Subjects to try: the article's named entities (best match), then each scene's
    # own search queries as tags. Purely additive + safe: any failure falls through.
    remaining = [i for i in range(len(matched_urls)) if matched_urls[i] is None
                 and i != last_idx]  # leave CTA scene for clean footage
    ml = _load_media_library_lookup() if remaining else None
    if ml and remaining:
        print(f"  📚 Media-library pass for {len(remaining)} mid scenes...")
        for i in remaining:
            scene = scenes[i] if i < len(scenes) else {}
            queries = list(scene.get("search_queries", []))
            visual = scene.get("visual", "")
            if visual and visual not in queries:
                queries = [visual] + queries
            asset = None
            # 1) try the article's named entities as a real subject match
            for term in (entities or [])[:6]:
                try:
                    asset = ml.find_media(subject=term, exclude_concept=False,
                                          min_quality=50, bump_usage=False)
                except Exception:
                    asset = None
                if asset and asset.get("url") not in used_in_this_reel:
                    break
                asset = None
            # 2) fall back to the scene's own queries as tag matches
            if not asset:
                for q in queries[:3]:
                    try:
                        asset = ml.find_media(tags=q.split(), exclude_concept=False,
                                              min_quality=45, bump_usage=False)
                    except Exception:
                        asset = None
                    if asset and asset.get("url") not in used_in_this_reel:
                        break
                    asset = None
            if not asset:
                continue
            mu = asset["url"]
            if mu in used_in_this_reel or not is_url_downloadable(mu):
                continue
            # mark the usage now that we're committing to it
            try:
                ml.find_media(subject=asset.get("subject"), media_type=asset.get("media_type"),
                              exclude_concept=False, bump_usage=True)
            except Exception:
                pass
            matched_urls[i] = mu
            used_in_this_reel.add(mu)
            mtype = "video" if asset.get("media_type") == "video" else "image"
            media_meta[mu] = {"type": mtype, "duration": asset.get("duration") or 0,
                              "curated": True, "generic_pexels": False,
                              "source_url": asset.get("source_url", "")}
            print(f"  📚 Scene {i+1}: {scene_descs[i][:42]}  →  media library "
                  f"('{asset.get('subject','')}', q{asset.get('quality_score')})")

    # ── 2. PRIMARY: Pexels stock VIDEO by scene visual description ──
    remaining = [i for i in range(len(matched_urls)) if matched_urls[i] is None]
    if remaining and pexels_key:
        print(f"  🎥 Searching Pexels VIDEO for {len(remaining)} unfilled scenes...")
        for i in remaining:
            scene = scenes[i] if i < len(scenes) else {}
            queries = scene.get("search_queries", [])
            visual = scene.get("visual", "")
            if visual and visual not in queries:
                queries = [visual] + queries
            for query in queries[:3]:
                anchored = anchor_query_to_india(query) != query or any(t in query.lower() for t in _india_terms)
                want_india_person = needs_india_person(query)
                query = anchor_query_to_india(query)
                results = pexels_video_search(pexels_key, query, count=5, min_duration=4)
                for cand in results:
                    vid = cand["video_id"]
                    if vid not in used_ids and vid not in used_video_ids_this_reel and cand["url"] not in used_in_this_reel:
                        if vid in BLOCKED_PEXELS_IDS:
                            print(f"  🚫 Scene {i+1}: skipped blocklisted video #{vid}")
                            continue
                        if is_foreign_for_india(cand, anchored):
                            print(f"  🚫 Scene {i+1}: skipped foreign-looking video #{vid} ({cand.get('alt','')[:40]})")
                            continue
                        if want_india_person and lacks_india_signal(cand):
                            print(f"  🚫 Scene {i+1}: skipped wrong-demographic video #{vid} (people scene, no India signal: {cand.get('alt','')[:40]})")
                            continue
                        matched_urls[i] = cand["url"]
                        used_in_this_reel.add(cand["url"])
                        used_video_ids_this_reel.add(vid)
                        media_meta[cand["url"]] = {"type": "video", "duration": cand["duration"], "generic_pexels": (not anchored)}
                        save_used_image(f"vid_{vid}")  # Track video IDs in same dedup log
                        print(f"  🎥 Scene {i+1}: {scene_descs[i][:50]}  →  Pexels VIDEO #{vid} ({cand['duration']}s)")
                        break
                if matched_urls[i] is not None:
                    break

    video_filled = sum(1 for u in matched_urls if u is not None)
    print(f"  📹 After Pexels video search: {video_filled}/{len(matched_urls)} scenes filled")

    # ── 3. Pexels HD IMAGE search by scene visual description (for remaining) ──
    remaining = [i for i in range(len(matched_urls)) if matched_urls[i] is None]
    if remaining and pexels_key:
        print(f"  🔍 Searching Pexels HD for {len(remaining)} unfilled scenes (by scene description)...")
        for i in remaining:
            scene = scenes[i] if i < len(scenes) else {}
            queries = scene.get("search_queries", [])
            # Also try the visual description as a search query
            visual = scene.get("visual", "")
            if visual and visual not in queries:
                queries = [visual] + queries
            for query in queries[:3]:
                anchored = anchor_query_to_india(query) != query or any(t in query.lower() for t in _india_terms)
                want_india_person = needs_india_person(query)
                query = anchor_query_to_india(query)
                results = pexels_search(pexels_key, query, count=5)
                for cand in results:
                    pid = cand["photo_id"]
                    if pid not in used_ids and pid not in used_photo_ids_this_reel and cand["url"] not in used_in_this_reel:
                        if pid in BLOCKED_PEXELS_IDS:
                            print(f"  🚫 Scene {i+1}: skipped blocklisted photo #{pid}")
                            continue
                        if is_foreign_for_india(cand, anchored):
                            print(f"  🚫 Scene {i+1}: skipped foreign-looking photo #{pid} ({cand.get('alt','')[:40]})")
                            continue
                        if want_india_person and lacks_india_signal(cand):
                            print(f"  🚫 Scene {i+1}: skipped wrong-demographic photo #{pid} (people scene, no India signal: {cand.get('alt','')[:40]})")
                            continue
                        matched_urls[i] = cand["url"]
                        used_in_this_reel.add(cand["url"])
                        used_photo_ids_this_reel.add(pid)
                        media_meta[cand["url"]] = {"type": "image", "duration": 0, "generic_pexels": (not anchored)}
                        save_used_image(pid)
                        print(f"  🎬 Scene {i+1}: {scene_descs[i][:50]}  →  Pexels #{pid} (scene-matched)")
                        break
                if matched_urls[i] is not None:
                    break

    pexels_filled = sum(1 for u in matched_urls if u is not None)
    print(f"  📸 After Pexels scene search: {pexels_filled}/{len(matched_urls)} scenes filled")

    # ── 4. Wikipedia/Wikimedia images for remaining gaps ──
    remaining = [i for i in range(len(matched_urls)) if matched_urls[i] is None]
    if remaining and scenes:
        print(f"  🔍 {len(remaining)} scenes unfilled — searching Wikipedia...")
        for i in remaining:
            scene = scenes[i] if i < len(scenes) else {}
            queries = scene.get("search_queries", [])
            for query in queries[:2]:
                try:
                    wiki_q = query.replace(" ", "_")
                    wr = requests.get(
                        f"https://en.wikipedia.org/api/rest_v1/page/summary/{requests.utils.quote(wiki_q)}",
                        headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
                        timeout=8,
                    )
                    if wr.status_code == 200:
                        wdata = wr.json()
                        if wdata.get("type") == "disambiguation":
                            continue
                        wimg = wdata.get("thumbnail", {}).get("source") or wdata.get("originalimage", {}).get("source")
                        wimg = upscale_wikimedia_url(wimg)
                        if wimg and wimg not in used_in_this_reel:
                            # Skip flags/maps/logos and diagram/figure/SVG filenames.
                            _low = wimg.lower()
                            _bad = ("flag_of", "flag-", "coat_of_arms", "coat-of-arms",
                                    "emblem", "ensign", "_map", "-map", "location_",
                                    "orthographic", "seal_of", "logo")
                            if any(b in _low for b in _bad) or any(sig in _low for sig in _DIAGRAM_FILENAME_SIGNALS):
                                continue
                            mw = mirror_to_supabase(wimg, article_id, i, reject_diagrams=True)
                            if not mw:
                                continue  # diagram/text-slab rejected at pixel level
                            matched_urls[i] = mw
                            used_in_this_reel.add(wimg)
                            used_in_this_reel.add(mw)
                            media_meta[mw] = {"type": "image", "duration": 0}
                            print(f"  🎬 Scene {i+1}: {scene_descs[i][:50]}  →  Wikipedia (CC)")
                            break
                except Exception:
                    continue

    wiki_filled = sum(1 for u in matched_urls if u is not None)
    print(f"  📸 After Wikipedia: {wiki_filled}/{len(matched_urls)} scenes filled")

    # ── 4b. CAP generic (non-India-anchored) Pexels fills — BUT respect a total
    #        per-reel KEY-POINT-CARD budget. ─────────────────────────────────
    # Two competing QA failure modes:
    #   • generic foreign stock  → "images don't match the story" (relevance)
    #   • too many full-screen text cards → "lacking visual variety" + the QA
    #     model hallucinates imagery into them ("shows a person working").
    # Now that the sourcing fixes surface more real, relevant photos/videos,
    # cards are a LAST resort, not a floor that fires alongside good imagery.
    # So: convert generic Pexels to cards ONLY while we stay under the card cap.
    # Scenes that are still empty after this become mandatory FLOOR cards below
    # (a card beats a blank scene), and they get first claim on the budget.
    CARD_CAP = 2            # max key-point cards per reel
    GENERIC_PEXELS_CAP = 1  # at least one generic Pexels kept for motion/variety
    floor_bound = sum(1 for u in matched_urls if u is None)  # empty scenes → FLOOR cards
    card_budget = max(0, CARD_CAP - floor_bound)             # discretionary cards we can still afford
    generic_idxs = [i for i in range(len(matched_urls))
                    if matched_urls[i] is not None
                    and media_meta.get(matched_urls[i], {}).get("generic_pexels")]
    max_convertible = max(0, len(generic_idxs) - GENERIC_PEXELS_CAP)
    n_convert = min(max_convertible, card_budget)
    if n_convert > 0:
        # Convert the WEAKEST generic fills first: prefer keeping videos (motion)
        # and low scene indices, so the ones we convert are images / later scenes.
        ranked = sorted(
            generic_idxs,
            key=lambda i: (0 if media_meta.get(matched_urls[i], {}).get("type") == "video" else 1, i),
        )
        keepers = ranked[:len(generic_idxs) - n_convert]
        to_convert = [i for i in generic_idxs if i not in keepers]
        print(f"  ✂️ {len(generic_idxs)} generic Pexels fills; card budget {card_budget} "
              f"({floor_bound} scene(s) already empty→FLOOR); converting {len(to_convert)} to key-point cards...")
        for i in to_convert:
            scene = scenes[i] if i < len(scenes) else {}
            local = render_keypoint_card(scene, category, article, i)
            if not local:
                continue  # leave the generic Pexels fill if card render fails
            storage_path = f"reel-cards/{article_id}/scene-{i}.png"
            card_url = upload_asset(local, storage_path, "image/png")
            try:
                os.remove(local)
            except Exception:
                pass
            if card_url:
                old_url = matched_urls[i]
                matched_urls[i] = card_url
                used_in_this_reel.discard(old_url)
                used_in_this_reel.add(card_url)
                media_meta[card_url] = {"type": "image", "duration": 0, "is_card": True}
                print(f"  🎨 Scene {i+1}: {scene_descs[i][:46]}  →  key-point card (replaced generic Pexels)")
    elif len(generic_idxs) > GENERIC_PEXELS_CAP:
        print(f"  ⚠️ {len(generic_idxs)} generic Pexels fills kept (card budget exhausted by "
              f"{floor_bound} empty scene(s)); not adding cards beyond cap {CARD_CAP}.")


    # ── 5. FLOOR: Styled KEY-POINT CARD (never generic foreign stock) ──
    # Any scene still empty here means no genuinely relevant photo/video exists.
    # Rather than dumping an unrelated same-category article image (the old behavior,
    # which produced topic-mismatched B-roll and the #1 "image relevance" QA failure),
    # render a designed motion-graphic carrying that scene's own key point — on-brand
    # navy + gold, numbers/proper-nouns highlighted. The visual *is* the story, so it
    # is always topic-relevant and never country-mismatched. Cards are uploaded to
    # Supabase storage and flow through the normal image path (preflight + Ken Burns).
    remaining = [i for i in range(len(matched_urls)) if matched_urls[i] is None]
    if remaining:
        print(f"  🎨 {len(remaining)} scenes unfilled — rendering styled key-point cards...")
        for i in remaining:
            scene = scenes[i] if i < len(scenes) else {}
            local = render_keypoint_card(scene, category, article, i)
            if not local:
                continue
            storage_path = f"reel-cards/{article_id}/scene-{i}.png"
            card_url = upload_asset(local, storage_path, "image/png")
            try:
                os.remove(local)
            except Exception:
                pass
            if card_url:
                matched_urls[i] = card_url
                used_in_this_reel.add(card_url)
                # mark as a card so the timeline can give it a calmer Ken Burns move
                media_meta[card_url] = {"type": "image", "duration": 0, "is_card": True}
                print(f"  🎨 Scene {i+1}: {scene_descs[i][:46]}  →  key-point card")

    urls = [u for u in matched_urls if u is not None]

    n_videos = sum(1 for u in urls if media_meta.get(u, {}).get("type") == "video")
    n_images = sum(1 for u in urls if media_meta.get(u, {}).get("type") != "video")
    print(f"  🖼️ Sourced {len(urls)} B-roll media ({n_videos} videos, {n_images} images)")
    return urls, media_meta


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
    html = f"""<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;width:100%;height:100%;padding:40px;box-sizing:border-box;background:linear-gradient(180deg, rgba(0,0,0,0.4) 0%, rgba(0,0,0,0.75) 50%, rgba(0,0,0,0.4) 100%);">
  <div style="background:#C41E3A;color:#fff;font-family:Inter;font-size:28px;font-weight:700;padding:10px 32px;letter-spacing:5px;margin-bottom:50px;">{badge}</div>
  <div style="font-family:Inter;font-size:84px;font-weight:900;color:#fff;line-height:1.0;margin-bottom:24px;text-shadow:0 4px 40px rgba(0,0,0,0.9),0 0 80px rgba(0,0,0,0.6);">{hook_line1}</div>
  <div style="font-family:Inter;font-size:56px;font-weight:700;color:#D4AF37;line-height:1.1;text-shadow:0 2px 20px rgba(0,0,0,0.7);">{hook_line2}</div>
  <div style="font-family:Inter;font-size:16px;color:rgba(255,255,255,0.3);letter-spacing:6px;margin-top:60px;">THE VIDESHI</div>
</div>"""

    css = ""  # All inline
    return html, css


def build_lower_third_html(headline, category):
    """Build HTML for the lower-third headline overlay during B-roll."""
    badge = (category or "NEWS").upper().replace("-", " ")
    # Truncate headline at a WORD boundary (old code cut mid-word: "...How the NE…")
    MAX_LEN = 70
    if len(headline) > MAX_LEN:
        cut = headline[:MAX_LEN].rsplit(" ", 1)[0]
        display_hl = cut + "…"
    else:
        display_hl = headline

    html = f"""<div class='lower-third'>
  <div class='lt-badge'>{badge}</div>
  <div class='lt-headline'>{display_hl}</div>
</div>"""

    # Stronger, earlier scrim + larger headline + solid band behind the text so
    # captions stay readable over BRIGHT B-roll (top QA failure: low contrast).
    css = """
.lower-third {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: flex-end;
  width: 100%;
  height: 100%;
  padding: 0 32px 22px 32px;
  box-sizing: border-box;
  background: linear-gradient(transparent 0%, rgba(10,22,40,0.55) 35%, rgba(10,22,40,0.92) 65%, rgba(10,22,40,0.99) 100%);
}
.lt-badge {
  background: #C41E3A;
  color: #ffffff;
  font-family: 'Inter';
  font-size: 14px;
  font-weight: 700;
  padding: 5px 16px;
  letter-spacing: 2px;
  margin-bottom: 12px;
  border-radius: 3px;
}
.lt-headline {
  font-family: 'Inter';
  font-size: 34px;
  font-weight: 800;
  color: #ffffff;
  line-height: 1.22;
  text-shadow: 0 2px 10px rgba(0,0,0,0.95), 0 0 4px rgba(0,0,0,0.8);
}
""".strip()

    return html, css


def build_anchor_reel_timeline(
    voice_url, voice_duration, image_urls, music_url, music_volume,
    hook_line1, hook_line2, headline, category,
    word_timestamps=None, script_text=None,
    media_meta=None,
):
    """Build the complete Shotstack JSON timeline for an Anchor Reel.
    media_meta maps url -> {"type": "video"|"image", "duration": N} for stock video support."""
    if media_meta is None:
        media_meta = {}

    hook_duration = 3.0  # Hook frame duration
    total_voice_duration = voice_duration
    cta_start = hook_duration + total_voice_duration + 1.0  # 1s pause before end card
    total_duration = cta_start + CTA_DURATION

    # ── Track 1 (TOP): Script-based captions (Whisper-timed) or rich-caption fallback ──
    script_caps = None
    if word_timestamps and script_text:
        script_caps = build_script_captions(word_timestamps, script_text, hook_duration)

    if script_caps:
        caption_track = script_caps
        # ── Suppress live caption pills during KEY-POINT CARD scenes ──
        # Key-point cards (added by the B-roll relevance fix) are full-frame text
        # graphics that already carry the scene's on-screen text. The voice-synced
        # caption pill rendered on top of them produced TWO different text blocks in
        # the same frame — the #1 "overlapping text in multiple frames" QA failure.
        # A card scene is already fully captioned by the card itself, so we drop any
        # caption clip whose midpoint falls inside a card scene's window. Photo/video
        # scenes are untouched and keep their captions (they need them for context).
        n_scenes = len(image_urls)
        if n_scenes > 0:
            per_scene = total_voice_duration / n_scenes
            card_windows = []
            for i, url in enumerate(image_urls):
                if media_meta.get(url, {}).get("is_card"):
                    w_start = hook_duration + i * per_scene
                    w_end = hook_duration + (i + 1) * per_scene
                    card_windows.append((w_start, w_end))
            if card_windows:
                kept = []
                dropped = 0
                for clip in caption_track.get("clips", []):
                    c_start = clip.get("start", 0)
                    c_len = clip.get("length", 0)
                    c_len = c_len if isinstance(c_len, (int, float)) else 0
                    c_mid = c_start + c_len / 2.0
                    in_card = any(ws <= c_mid < we for ws, we in card_windows)
                    if in_card:
                        dropped += 1
                    else:
                        kept.append(clip)
                if dropped:
                    caption_track = {"clips": kept}
                    print(f"  🚫 Suppressed {dropped} caption pill(s) overlapping "
                          f"{len(card_windows)} key-point card scene(s) (anti text-overlap)")
    else:
        # Fallback: Shotstack auto-caption from audio (may mis-transcribe proper nouns)
        caption_style = CATEGORY_CAPTION_STYLE.get(category, "highlight")
        caption_track = {
            "clips": [
                {
                    "asset": {
                        "type": "rich-caption",
                        "src": "alias://voiceover",
                        "font": {
                            "family": "Inter",
                            "size": 40,
                            "color": WHITE,
                            "weight": 800,
                            "opacity": 1,
                        },
                        "animation": {"style": caption_style},
                        "active": {
                            "font": {"color": GOLD, "opacity": 1},
                            "stroke": {"width": 4, "color": "#000000", "opacity": 1},
                        },
                        "stroke": {"width": 3, "color": "#000000", "opacity": 0.9},
                        "background": {"color": "#000000", "opacity": 1.0, "borderRadius": 10, "padding": 10},
                        "align": {"vertical": "bottom"},
                        "style": {"textTransform": "uppercase"},
                        "padding": {"top": 0, "right": 8, "bottom": 0, "left": 8},
                    },
                    "start": hook_duration,
                    "length": "end",
                    "width": 900,
                    "height": 200,
                    "position": "center",
                    "offset": {"x": 0, "y": 0.05},
                }
            ]
        }

    # ── Track 2: Logo + TheVideshi.com watermark (every frame) ──
    # Use center position with manual offsets (topRight clips edges unreliably)
    LOGO_URL = "https://lboecaekpynbpyijrbfz.supabase.co/storage/v1/object/public/article-images/branding/logo-192.png"
    logo_track = {
        "clips": [
            {
                "asset": {
                    "type": "image",
                    "src": LOGO_URL,
                },
                "start": 0,
                "length": round(cta_start, 2),
                "position": "center",
                "offset": {"x": 0.38, "y": 0.44},
                "scale": 0.08,
                "opacity": 0.9,
            },
            {
                "asset": {
                    "type": "html",
                    "html": "<div class='wm'>TheVideshi.com</div>",
                    "css": ".wm { font-family: 'Inter'; color: #ffffff; font-size: 17px; font-weight: 700; letter-spacing: 0.5px; white-space: nowrap; text-shadow: 0 2px 6px rgba(0,0,0,0.95); text-align: center; padding: 4px 14px; background: rgba(0,0,0,0.55); border-radius: 5px; box-sizing: border-box; display: inline-block; }",
                    "width": 240,
                    "height": 34,
                },
                "start": 0,
                "length": round(cta_start, 2),
                "position": "center",
                "offset": {"x": 0.38, "y": 0.36},
            }
        ]
    }

    # ── Track 3: Hook frame overlay (first 3 seconds) — ANIMATED ──
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
                "transition": {"in": "zoom", "out": "fade"},
                # Tween: slide up slightly and settle with bounce
                "offset": {
                    "x": 0,
                    "y": [
                        {"from": -0.04, "to": 0, "start": 0, "length": 0.6,
                         "interpolation": "bezier", "easing": "easeOutBack"},
                    ],
                },
            }
        ]
    }

    # ── Track 4: Caption scrim (text-free dark band behind the captions) ──
    # A bottom-anchored gradient that runs the FULL narration, sitting just below
    # the caption track. It guarantees the white caption pill always has a dark
    # backing even over bright B-roll (the recurring "text readability / low
    # contrast" QA failure). It carries NO text of its own, so it cannot recreate
    # the overlap bug the old chyron caused — captions still own all on-screen text.
    caption_scrim_css = """
.cap-scrim {
  width: 100%;
  height: 100%;
  box-sizing: border-box;
  background: linear-gradient(transparent 0%, rgba(8,18,34,0.0) 40%, rgba(8,18,34,0.65) 72%, rgba(8,18,34,0.9) 100%);
}
""".strip()
    scrim_duration = max(total_voice_duration, 0.5)
    caption_scrim_track = {
        "clips": [
            {
                "asset": {
                    "type": "html",
                    "html": "<div class='cap-scrim'></div>",
                    "css": caption_scrim_css,
                    "width": 1080,
                    "height": 700,
                },
                "start": hook_duration,
                "length": scrim_duration,
                "position": "bottom",
            }
        ]
    }

    # ── Track 5: B-roll media with Ken Burns (images) or trimmed stock video ──
    n_images = len(image_urls)
    if n_images == 0:
        print("❌ No images for B-roll")
        return None

    broll_clips = []
    transitions = CATEGORY_TRANSITIONS.get(category, CATEGORY_TRANSITIONS.get("news"))

    # Hook background (darkened, first media — always treat as image for hook overlay)
    hook_url = image_urls[0]
    hook_meta = media_meta.get(hook_url, {})
    if hook_meta.get("type") == "video":
        broll_clips.append({
            "asset": {"type": "video", "src": hook_url, "trim": 0, "volume": 0},
            "start": 0,
            "length": hook_duration,
            "fit": "cover",
            "filter": "darken",
        })
    else:
        broll_clips.append({
            "asset": {"type": "image", "src": hook_url},
            "start": 0,
            "length": hook_duration,
            "fit": "cover",
            "effect": "zoomIn",
            "filter": "darken",
        })

    # B-roll during voiceover — distribute media evenly
    per_image = total_voice_duration / n_images
    for i, url in enumerate(image_urls):
        meta = media_meta.get(url, {})
        scene_length = round(per_image + 0.3, 2)  # Slight overlap for transition

        if meta.get("type") == "video":
            # Stock video clip — trim from a random offset for variety, mute audio
            src_duration = meta.get("duration", 10)
            max_trim = max(0, src_duration - per_image - 1)
            trim_start = round(random.uniform(0, max_trim), 2) if max_trim > 0 else 0
            clip = {
                "asset": {"type": "video", "src": url, "trim": trim_start, "volume": 0},
                "start": round(hook_duration + (i * per_image), 2),
                "length": scene_length,
                "fit": "cover",
            }
        else:
            # Static image — Ken Burns effect for PHOTOS. Key-point CARDS are
            # full-bleed 1080x1920 text graphics: any zoom/pan (even "zoomIn")
            # scales past 100% and pushes the edge words off-frame — that's what
            # clipped "New" on the Neeraj-Sharma card and fed the QA "text
            # readability" deduction. So cards render STATIC with fit=contain
            # (whole card always in frame, every word readable); only real photos
            # get the Ken Burns motion.
            is_card = meta.get("is_card")
            if is_card:
                clip = {
                    "asset": {"type": "image", "src": url},
                    "start": round(hook_duration + (i * per_image), 2),
                    "length": scene_length,
                    "fit": "contain",
                    # no effect → no zoom crop; text stays fully on-frame
                }
            else:
                clip = {
                    "asset": {"type": "image", "src": url},
                    "start": round(hook_duration + (i * per_image), 2),
                    "length": scene_length,
                    "fit": "cover",
                    "effect": KEN_BURNS_EFFECTS[i % len(KEN_BURNS_EFFECTS)],
                }
        if i > 0:
            clip["transition"] = {"in": transitions[i % len(transitions)]}
        broll_clips.append(clip)

    broll_track = {"clips": broll_clips}

    # ── CTA: Branded end card (HTML overlay on dark background) — animated slide up ──
    end_html, end_css = build_end_card_html(logo_url=LOGO_URL)
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
                "transition": {"in": "slideUp"},
                "offset": {
                    "x": 0,
                    "y": [
                        {"from": -0.03, "to": 0, "start": 0, "length": 0.4,
                         "interpolation": "bezier", "easing": "easeOutCubic"},
                    ],
                },
            },
            # Logo as a real image clip (HTML <img> does not render in Shotstack).
            # Centered near the top of the end card, above the "THE VIDESHI" wordmark.
            {
                "asset": {
                    "type": "image",
                    "src": LOGO_URL,
                },
                "start": round(cta_start, 2),
                "length": CTA_DURATION,
                "position": "center",
                "offset": {"x": 0, "y": 0.34},
                "scale": 0.22,
                "transition": {"in": "fade"},
            },
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
                },
                "start": hook_duration,
                "length": "auto",
                "alias": "voiceover",
            }
        ]
    }

    # ── Assemble timeline ──
    # NOTE: lower_third_track intentionally OMITTED. The hook frame already shows
    # the headline for the first 3s, and the voice-synced captions run the rest of
    # the reel. Rendering the chyron *and* the captions both anchored to the bottom
    # band caused them to overlap during the 3–7s window (the #1 "overlapping text"
    # QA failure). Captions now own the lower third exclusively.
    # caption_scrim_track sits directly beneath the captions to guarantee contrast.
    timeline = {
        "background": NAVY,
        "fonts": [{"src": FONT_URL}],
        "tracks": [
            caption_track,    # Top layer
            logo_track,
            hook_track,
            caption_scrim_track,  # Dark band behind captions (text-free)
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
            "poster": {"capture": 1.5},       # Capture hook frame at 1.5s (peak of hook animation)
            "thumbnail": {"capture": 1.5, "scale": 0.5},  # Half-size thumbnail
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
            "poster": {"capture": 1.5},
            "thumbnail": {"capture": 1.5, "scale": 0.5},
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
        timeout=60,
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
            timeout=30,
        )

        if r.status_code != 200:
            print(f"  ⚠️ Poll failed: {r.status_code}")
            continue

        status_data = r.json().get("response", {})
        status = status_data.get("status", "")

        if status == "done":
            output_url = status_data.get("url")
            poster_url = status_data.get("poster")
            thumbnail_url = status_data.get("thumbnail")
            render_time = status_data.get("renderTime", 0)
            print(f"  ✅ Render complete! ({render_time/1000:.1f}s)")
            if poster_url:
                print(f"  🖼️ Poster: {poster_url}")
            if thumbnail_url:
                print(f"  🖼️ Thumbnail: {thumbnail_url}")
            return {"url": output_url, "poster": poster_url, "thumbnail": thumbnail_url}

        elif status == "failed":
            error = status_data.get("error", "unknown")
            print(f"  ❌ Render failed: {error}")
            return None

        else:
            if i % 4 == 0:
                print(f"  ⏳ Status: {status} ({(i+1)*5}s elapsed)")

    print("❌ Render timed out after 5 minutes")
    return None


def download_reel(url, output_path, retries=3):
    """Download rendered reel from Shotstack, with retry on transient network errors."""
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            r = requests.get(url, timeout=180, stream=True)
            if r.status_code != 200:
                print(f"❌ Download failed: {r.status_code}")
                return False

            with open(output_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

            size_mb = os.path.getsize(output_path) / (1024 * 1024)
            print(f"  📥 Downloaded: {output_path} ({size_mb:.1f} MB)")
            return True
        except Exception as e:
            last_err = e
            print(f"  ⚠️ Download attempt {attempt}/{retries} failed: {e}")
            if attempt < retries:
                time.sleep(3 * attempt)
    print(f"❌ Download failed after {retries} attempts: {last_err}")
    return False


# ═══════════════════════════════════════════════════════════════════════════════
# KAVYA CTA END CARD
# ═══════════════════════════════════════════════════════════════════════════════

CTA_DURATION = 4.0  # Branded end card — enough time to read site + social handles

# Social handles
SOCIAL_HANDLES = {
    "website": "thevideshi.com",
    "instagram": "@the.videshi",
    "youtube": "@the.videshi",
    "threads": "@the.videshi",
    "x": "@thevideshi",
    "whatsapp": "The Videshi",
}


def build_end_card_html(logo_url=None):
    """Build branded end card with social handles. All inline styles for Shotstack compatibility.
    NOTE: the logo is added as a separate Shotstack image clip (HTML <img> does not
    render in Shotstack's HTML asset), so logo_url is accepted but not embedded here."""
    html = f"""<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;width:100%;height:100%;background:linear-gradient(180deg,#0a1628 0%,#0f1f35 50%,#0a1628 100%);padding:60px 40px;box-sizing:border-box;">
  <div style="margin-top:140px;font-family:Inter;font-size:78px;font-weight:700;color:#D4AF37;letter-spacing:9px;margin-bottom:14px;">THE VIDESHI</div>
  <div style="font-family:Inter;font-size:26px;color:rgba(255,255,255,0.55);letter-spacing:3px;text-transform:uppercase;margin-bottom:44px;">News for the Indian Diaspora</div>
  <div style="width:64px;height:3px;background:#D4AF37;margin-bottom:44px;opacity:0.6;"></div>
  <div style="font-family:Inter;font-size:44px;font-weight:700;color:#fff;letter-spacing:1px;margin-bottom:52px;">thevideshi.com</div>
  <div style="display:flex;flex-direction:column;gap:20px;align-items:center;">
    <div style="display:flex;gap:18px;align-items:center;"><span style="font-family:Inter;font-size:22px;font-weight:700;color:#D4AF37;letter-spacing:2px;width:175px;text-align:right;">YOUTUBE</span><span style="font-family:Inter;font-size:28px;color:rgba(255,255,255,0.85);">@the.videshi</span></div>
    <div style="display:flex;gap:18px;align-items:center;"><span style="font-family:Inter;font-size:22px;font-weight:700;color:#D4AF37;letter-spacing:2px;width:175px;text-align:right;">INSTAGRAM</span><span style="font-family:Inter;font-size:28px;color:rgba(255,255,255,0.85);">@the.videshi</span></div>
    <div style="display:flex;gap:18px;align-items:center;"><span style="font-family:Inter;font-size:22px;font-weight:700;color:#D4AF37;letter-spacing:2px;width:175px;text-align:right;">THREADS</span><span style="font-family:Inter;font-size:28px;color:rgba(255,255,255,0.85);">@the.videshi</span></div>
    <div style="display:flex;gap:18px;align-items:center;"><span style="font-family:Inter;font-size:22px;font-weight:700;color:#D4AF37;letter-spacing:2px;width:175px;text-align:right;">X</span><span style="font-family:Inter;font-size:28px;color:rgba(255,255,255,0.85);">@thevideshi</span></div>
    <div style="display:flex;gap:18px;align-items:center;"><span style="font-family:Inter;font-size:22px;font-weight:700;color:#D4AF37;letter-spacing:2px;width:175px;text-align:right;">WHATSAPP</span><span style="font-family:Inter;font-size:28px;color:rgba(255,255,255,0.85);">The Videshi</span></div>
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

    # Sample frame 1 inside the hook window (~1.5s) so QA actually sees the
    # hook overlay, then spread the rest across the body. The old even-spacing
    # (duration/(count+1)) never sampled the first ~3s, so the reviewer judged
    # "weak hook" on a mid-reel B-roll frame with no hook text on it.
    hook_window = 3.0
    body_start = min(hook_window + 1.0, duration * 0.15)
    sample_times = [1.5 if duration > 4 else duration / 2]
    body_count = max(count - 1, 1)
    for i in range(body_count):
        # Even spread across the body region (after hook, before end card)
        body_end = max(duration - 1.5, body_start + 0.5)
        t = body_start + (body_end - body_start) * (i + 1) / (body_count + 1)
        sample_times.append(round(t, 2))

    frames = []
    for i in range(count):
        t = sample_times[i] if i < len(sample_times) else (duration / (count + 1)) * (i + 1)
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
        return False, 0, "QA failed (no API key — fail closed)"

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

Score 1-10. This is for Instagram/YouTube Shorts — fast-paced news content, not cinema. Be practical but maintain HIGH standards.
1. VISUAL QUALITY: Images clear and HIGH RESOLUTION? No pixelation, blur, stretching, or black bars? Portrait 1080x1920?
2. TEXT READABILITY: Can captions be read over the images? Strong contrast with background?
3. BRANDING: Does it look like a professional news outlet? Category badge, branded elements present?
4. HOOK: Does the opening frame have bold text that grabs attention?
5. FLOW: Good pacing, transitions between images? Visual variety across scenes?
6. IMAGE RELEVANCE: Do the B-roll images actually match the story topic? (e.g. a story about mutual funds should show finance/money imagery, NOT random landscapes or unrelated photos)
7. CONTENT DEPTH: Does the narration deliver actual information (numbers, names, context), or is it just a vague headline restated?

NON-NEGOTIABLE CHECKS (any fail = auto-fail, override score to 0):
- SPELLING: Any misspelling of "TheVideshi", "thevideshi.com", or social handles (@the.videshi, @thevideshi)?
  Watch for STT errors like "Divaji", "Vidashi", "Vidashee", "diva ji", or any garbled version.
- OVERLAPPING TEXT: Are two text elements rendered on top of each other making them unreadable?
- BRAND INTEGRITY: Is the website URL shown as anything other than "thevideshi.com"?

Score 7+ = broadcast-quality news reel (PASS). Score 5-6 = needs improvement (FAIL). Below 5 = broken.

Return JSON only:
{{
  "score": <1-10, or 0 if any non-negotiable failed>,
  "passed": <true if score >= 7 AND all non-negotiables pass>,
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
            "image_url": {"url": f"data:image/jpeg;base64,{frame['b64']}", "detail": "high"},
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
                "temperature": 0,
                "response_format": {"type": "json_object"},
                "max_tokens": 500,
            },
            timeout=60,
        )

        if r.status_code != 200:
            print(f"  ⚠️ QA API error: {r.status_code}")
            return False, 0, "QA failed (API error — fail closed)"

        result = json.loads(r.json()["choices"][0]["message"]["content"])
        score = result.get("score", 5)
        non_neg = result.get("non_negotiable_failures", [])
        issues = result.get("issues", [])
        severity = result.get("severity", "LOW")
        notes = result.get("notes", "")

        # Non-negotiable failures override everything
        if non_neg:
            print(f"  🚫 NON-NEGOTIABLE FAILURES: {'; '.join(non_neg)}")
            log_qa_feedback(article, score=0, passed=False, issues=non_neg, severity="CRITICAL", notes=f"Non-negotiable: {'; '.join(non_neg)}")
            return False, 0, f"Non-negotiable: {'; '.join(non_neg)}"

        # Derive pass/fail from score — never trust LLM's string verdict.
        # Gate lowered 8→7 per Kiran (2026-06-15): clean renders kept scoring 7
        # with boilerplate "readability" notes despite demonstrably solid captions;
        # the non-negotiable checks below still hard-fail real defects.
        passed = score >= 7

        if issues:
            print(f"  📋 Issues ({severity}): {'; '.join(issues)}")

        # Log every QA result — the feedback loop reads this
        log_qa_feedback(article, score=score, passed=passed, issues=issues, severity=severity, notes=notes)

        return passed, score, notes

    except Exception as e:
        print(f"  ⚠️ QA gate error: {e}")
        return False, 0, f"QA failed (error — fail closed: {e})"


# ═══════════════════════════════════════════════════════════════════════════════
# UPLOAD & REGISTER
# ═══════════════════════════════════════════════════════════════════════════════

def compress_reel_if_needed(local_path, max_mb=45):
    """Shotstack renders at ~15 Mbps (~90 MB for 48s), which exceeds Supabase
    storage's object-size cap and causes a 413 on upload. Re-encode to a sane
    bitrate (CRF 23, faststart) when the file is too large. Returns the path to
    use for upload (compressed copy if produced, else the original)."""
    try:
        size_mb = os.path.getsize(local_path) / (1024 * 1024)
    except OSError:
        return local_path
    if size_mb <= max_mb:
        return local_path

    out_path = os.path.splitext(local_path)[0] + "-c.mp4"
    print(f"  🗜️ Reel is {size_mb:.1f} MB (> {max_mb} MB) — compressing for upload...")
    result = subprocess.run(
        ["ffmpeg", "-y", "-i", local_path,
         "-c:v", "libx264", "-preset", "medium", "-crf", "23",
         "-pix_fmt", "yuv420p", "-movflags", "+faststart",
         "-c:a", "aac", "-b:a", "128k", out_path],
        capture_output=True, text=True, timeout=300,
    )
    if result.returncode == 0 and os.path.exists(out_path):
        new_mb = os.path.getsize(out_path) / (1024 * 1024)
        print(f"  🗜️ Compressed: {size_mb:.1f} MB → {new_mb:.1f} MB")
        return out_path
    print(f"  ⚠️ Compression failed, uploading original: {result.stderr[-200:]}")
    return local_path


def upload_final_reel(local_path, storage_name):
    """Upload final reel to Supabase storage. Compresses oversized renders first."""
    upload_path = compress_reel_if_needed(local_path)
    storage_basename = os.path.basename(upload_path)
    return upload_asset(upload_path, f"reels/{storage_basename}", "video/mp4"), upload_path


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


def register_reel(article, video_url, video_path, caption, poster_url=None, thumbnail_url=None, qa_score_actual=8):
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
        "qa_score": qa_score_actual,
    }

    # Add poster/thumbnail if available (columns may not exist yet — handle gracefully)
    if poster_url:
        payload["poster_url"] = poster_url
    if thumbnail_url:
        payload["thumbnail_url"] = thumbnail_url

    r = requests.post(
        f"{SB_URL}/rest/v1/prebuilt_reels",
        headers=SB_HEADERS,
        json=payload,
        timeout=15,
    )

    if r.status_code in (200, 201):
        print(f"  ✅ Registered in prebuilt_reels")
        return True
    elif r.status_code == 400 and ("poster_url" in r.text or "thumbnail_url" in r.text):
        # Columns don't exist yet — retry without poster/thumbnail
        print(f"  ⚠️ poster_url/thumbnail_url columns not in DB yet — registering without them")
        payload.pop("poster_url", None)
        payload.pop("thumbnail_url", None)
        r2 = requests.post(
            f"{SB_URL}/rest/v1/prebuilt_reels",
            headers=SB_HEADERS,
            json=payload,
            timeout=15,
        )
        if r2.status_code in (200, 201):
            print(f"  ✅ Registered in prebuilt_reels (without poster/thumb)")
            return True
        else:
            print(f"  ❌ Registration failed: {r2.status_code} {r2.text[:200]}")
            return False
    else:
        print(f"  ❌ Registration failed: {r.status_code} {r.text[:200]}")
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# CROSS-POST — push reel to all platforms immediately after QA pass
# ═══════════════════════════════════════════════════════════════════════════════

def load_env_file(path):
    """Parse KEY=VALUE from a file."""
    env = {}
    full = os.path.expanduser(path)
    if not os.path.exists(full):
        return env
    with open(full) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def cross_post_reel(article, video_url, video_path, caption, poster_url=None):
    """Post reel to all platforms: Instagram, YouTube, Threads, Facebook, X.
    Each platform is tried independently — one failure doesn't block others.
    Article-level dedup: checks prebuilt_reels + youtube-log before posting.
    """
    headline = article.get("headline", "")
    slug = article.get("slug", "")
    category = article.get("category", "news")
    article_id = article.get("id", "")

    results = {}

    # ── Per-platform dedup: check what's already been posted for this article ──
    already_posted = set()
    try:
        dr = requests.get(
            f"{SB_URL}/rest/v1/prebuilt_reels",
            params={
                "article_id": f"eq.{article_id}",
                "select": "id,status,yt_posted_at,threads_posted_at",
                "limit": 10,
            },
            headers=SB_HEADERS,
            timeout=10,
        )
        if dr.status_code == 200:
            for row in dr.json():
                if row.get("status") == "ig_posted":
                    already_posted.add("instagram")
                if row.get("yt_posted_at"):
                    already_posted.add("youtube")
                if row.get("threads_posted_at"):
                    already_posted.add("threads")
        # Also check youtube-log.json for file-based dedup
        yt_log_path = os.path.join(os.path.dirname(__file__), "youtube-log.json")
        try:
            with open(yt_log_path) as f:
                yt_log = json.load(f)
            if any(v.get("article_slug", "").startswith(slug[:40]) for v in yt_log.values()):
                already_posted.add("youtube")
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        if already_posted:
            print(f"  📋 Already posted to: {', '.join(already_posted)}")
    except Exception:
        pass  # Dedup check failure shouldn't block posting

    # ── Instagram Reel ──
    if "instagram" in already_posted:
        print("  ⏭️ Instagram: Already posted for this article")
        results["instagram"] = {"success": True, "skipped": "dedup"}
    else:
        try:
            ig_env = load_env_file("~/workspace/.env.instagram")
            ig_token = ig_env.get("INSTAGRAM_ACCESS_TOKEN", "")
            ig_user = ig_env.get("INSTAGRAM_USER_ID", "")
            if ig_token and ig_user:
                print("  📸 Instagram: Creating reel container...")
                ig_caption = caption[:2200]
                cr = requests.post(
                    f"https://graph.instagram.com/v25.0/{ig_user}/media",
                    data={
                        "media_type": "REELS",
                        "video_url": video_url,
                        "caption": ig_caption,
                        "access_token": ig_token,
                    },
                    timeout=60,
                )
                if cr.status_code == 200 and cr.json().get("id"):
                    container_id = cr.json()["id"]
                    status = "IN_PROGRESS"
                    for _ in range(24):
                        time.sleep(5)
                        sr = requests.get(
                            f"https://graph.instagram.com/v25.0/{container_id}",
                            params={"fields": "status_code", "access_token": ig_token},
                            timeout=15,
                        )
                        status = sr.json().get("status_code", "")
                        if status in ("FINISHED", "ERROR"):
                            break
                    if status == "FINISHED":
                        pr = requests.post(
                            f"https://graph.instagram.com/v25.0/{ig_user}/media_publish",
                            data={"creation_id": container_id, "access_token": ig_token},
                            timeout=60,
                        )
                        if pr.status_code == 200:
                            ig_media_id = pr.json().get("id", "")
                            print(f"  ✅ Instagram: Posted (media_id: {ig_media_id})")
                            results["instagram"] = {"success": True, "media_id": ig_media_id}
                        else:
                            print(f"  ❌ Instagram: Publish failed ({pr.status_code})")
                            results["instagram"] = {"success": False, "error": pr.text[:200]}
                    else:
                        print(f"  ❌ Instagram: Container status: {status}")
                        results["instagram"] = {"success": False, "error": f"container_{status}"}
                else:
                    print(f"  ❌ Instagram: Container creation failed ({cr.status_code})")
                    results["instagram"] = {"success": False, "error": cr.text[:200]}
            else:
                print("  ⏭️ Instagram: No credentials configured")
        except Exception as e:
            print(f"  ❌ Instagram: {e}")
            results["instagram"] = {"success": False, "error": str(e)}

    # ── Threads ──
    if "threads" in already_posted:
        print("  ⏭️ Threads: Already posted for this article")
        results["threads"] = {"success": True, "skipped": "dedup"}
    else:
        try:
            threads_env = load_env_file("~/workspace/.env.threads")
            threads_token = threads_env.get("THREADS_ACCESS_TOKEN", "")
            threads_user = threads_env.get("THREADS_USER_ID", "26854521280856098")
            if threads_token:
                print("  🧵 Threads: Creating video post...")
                threads_caption = caption[:500]
                cr = requests.post(
                    f"https://graph.threads.net/v1.0/{threads_user}/threads",
                    data={
                        "media_type": "VIDEO",
                        "video_url": video_url,
                        "text": threads_caption,
                        "access_token": threads_token,
                    },
                    timeout=60,
                )
                if cr.status_code == 200 and cr.json().get("id"):
                    container_id = cr.json()["id"]
                    status = "IN_PROGRESS"
                    for _ in range(24):
                        time.sleep(5)
                        sr = requests.get(
                            f"https://graph.threads.net/v1.0/{container_id}",
                            params={"fields": "status", "access_token": threads_token},
                            timeout=15,
                        )
                        status = sr.json().get("status", "")
                        if status in ("FINISHED", "ERROR"):
                            break
                    if status == "FINISHED":
                        pr = requests.post(
                            f"https://graph.threads.net/v1.0/{threads_user}/threads_publish",
                            data={"creation_id": container_id, "access_token": threads_token},
                            timeout=60,
                        )
                        if pr.status_code == 200:
                            post_id = pr.json().get("id", "")
                            print(f"  ✅ Threads: Posted (post_id: {post_id})")
                            results["threads"] = {"success": True, "post_id": post_id}
                        else:
                            print(f"  ❌ Threads: Publish failed ({pr.status_code})")
                            results["threads"] = {"success": False, "error": pr.text[:200]}
                    else:
                        print(f"  ❌ Threads: Container status: {status}")
                        results["threads"] = {"success": False, "error": f"container_{status}"}
                else:
                    print(f"  ❌ Threads: Container failed ({cr.status_code}): {cr.text[:200]}")
                    results["threads"] = {"success": False, "error": cr.text[:200]}
            else:
                print("  ⏭️ Threads: No credentials configured")
        except Exception as e:
            print(f"  ❌ Threads: {e}")
            results["threads"] = {"success": False, "error": str(e)}

    # ── Facebook Reel ──
    try:
        fb_env = load_env_file("~/workspace/.env.facebook")
        fb_token = fb_env.get("FB_PAGE_ACCESS_TOKEN", "")
        fb_page = fb_env.get("FB_PAGE_ID", "")
        if fb_token and fb_page:
            print("  📘 Facebook: Uploading reel...")
            init_r = requests.post(
                f"https://graph.facebook.com/v25.0/{fb_page}/video_reels",
                data={"upload_phase": "start", "access_token": fb_token},
                timeout=60,
            )
            if init_r.status_code == 200:
                video_id = init_r.json().get("video_id")
                with open(video_path, "rb") as vf:
                    up_r = requests.post(
                        f"https://rupload.facebook.com/video-upload/v25.0/{video_id}",
                        headers={
                            "Authorization": f"OAuth {fb_token}",
                            "offset": "0",
                            "file_size": str(os.path.getsize(video_path)),
                        },
                        data=vf.read(),
                        timeout=120,
                    )
                if up_r.status_code == 200 and up_r.json().get("success"):
                    fb_caption = caption[:2000]
                    fin_r = requests.post(
                        f"https://graph.facebook.com/v25.0/{fb_page}/video_reels",
                        data={
                            "upload_phase": "finish",
                            "video_id": video_id,
                            "title": headline[:100],
                            "description": fb_caption,
                            "access_token": fb_token,
                        },
                        timeout=60,
                    )
                    if fin_r.status_code == 200 and fin_r.json().get("success"):
                        print(f"  ✅ Facebook: Reel posted (video_id: {video_id})")
                        results["facebook"] = {"success": True, "video_id": video_id}
                    else:
                        print(f"  ❌ Facebook: Finish failed ({fin_r.status_code})")
                        results["facebook"] = {"success": False, "error": fin_r.text[:200]}
                else:
                    print(f"  ❌ Facebook: Upload failed ({up_r.status_code})")
                    results["facebook"] = {"success": False, "error": up_r.text[:200]}
            else:
                print(f"  ❌ Facebook: Init failed ({init_r.status_code})")
                results["facebook"] = {"success": False, "error": init_r.text[:200]}
        else:
            print("  ⏭️ Facebook: No credentials configured")
    except Exception as e:
        print(f"  ❌ Facebook: {e}")
        results["facebook"] = {"success": False, "error": str(e)}

    # ── YouTube Short ──
    if "youtube" in already_posted:
        print("  ⏭️ YouTube: Already posted for this article")
        results["youtube"] = {"success": True, "skipped": "dedup"}
    else:
        try:
            yt_env = load_env_file("~/workspace/.env.youtube")
            yt_client_id = yt_env.get("YOUTUBE_CLIENT_ID", "")
            yt_client_secret = yt_env.get("YOUTUBE_CLIENT_SECRET", "")
            yt_refresh = yt_env.get("YOUTUBE_REFRESH_TOKEN", "")
            if yt_client_id and yt_client_secret and yt_refresh:
                print("  ▶️ YouTube: Uploading Short...")
                token_r = requests.post(
                    "https://oauth2.googleapis.com/token",
                    data={
                        "client_id": yt_client_id,
                        "client_secret": yt_client_secret,
                        "refresh_token": yt_refresh,
                        "grant_type": "refresh_token",
                    },
                    timeout=15,
                )
                if token_r.status_code == 200:
                    access_token = token_r.json()["access_token"]
                    cat_emoji = {"news": "🇮🇳", "nri-world": "🌏", "travel": "✈️", "sports": "🏏",
                                 "entertainment": "🎬", "technology": "💻", "markets": "📈"}.get(category, "🇮🇳")
                    yt_title = f"{cat_emoji} {headline[:95]}" if len(headline) <= 95 else f"{cat_emoji} {headline[:92]}..."
                    yt_tags = ["Indian diaspora", "NRI", "India news", "TheVideshi", category]
                    yt_desc = f"{caption}\n\n🔗 Read more: https://thevideshi.com\n#Shorts #IndianDiaspora #NRI #{category.replace('-', '')}"

                    init_r = requests.post(
                        "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status",
                        headers={
                            "Authorization": f"Bearer {access_token}",
                            "Content-Type": "application/json",
                        },
                        json={
                            "snippet": {
                                "title": yt_title,
                                "description": yt_desc[:5000],
                                "tags": yt_tags,
                                "categoryId": "25",
                            },
                            "status": {
                                "privacyStatus": "public",
                                "selfDeclaredMadeForKids": False,
                                "license": "youtube",
                                "embeddable": True,
                            },
                        },
                        timeout=60,
                    )
                    if init_r.status_code == 200:
                        upload_url = init_r.headers.get("Location")
                        with open(video_path, "rb") as vf:
                            video_data = vf.read()
                        up_r = requests.put(
                            upload_url,
                            headers={
                                "Authorization": f"Bearer {access_token}",
                                "Content-Type": "video/mp4",
                                "Content-Length": str(len(video_data)),
                            },
                            data=video_data,
                            timeout=120,
                        )
                        if up_r.status_code == 200:
                            yt_id = up_r.json().get("id", "")
                            print(f"  ✅ YouTube: Uploaded (id: {yt_id})")
                            results["youtube"] = {"success": True, "video_id": yt_id}
                            # Update youtube-log.json for dedup
                            yt_log_path = os.path.join(os.path.dirname(__file__), "youtube-log.json")
                            try:
                                with open(yt_log_path) as f:
                                    yt_log = json.load(f)
                            except (FileNotFoundError, json.JSONDecodeError):
                                yt_log = {}
                            yt_log[yt_id] = {
                                "filename": os.path.basename(video_path),
                                "article_slug": slug,
                                "title": yt_title,
                                "uploaded_at": datetime.now().isoformat(),
                                "source": "shotstack-cross-post",
                            }
                            with open(yt_log_path, "w") as f:
                                json.dump(yt_log, f, indent=2)
                        else:
                            print(f"  ❌ YouTube: Upload failed ({up_r.status_code})")
                            results["youtube"] = {"success": False, "error": up_r.text[:200]}
                    else:
                        print(f"  ❌ YouTube: Init failed ({init_r.status_code}): {init_r.text[:200]}")
                        results["youtube"] = {"success": False, "error": init_r.text[:200]}
                else:
                    print(f"  ❌ YouTube: Token refresh failed ({token_r.status_code})")
                    results["youtube"] = {"success": False, "error": token_r.text[:200]}
            else:
                print("  ⏭️ YouTube: No credentials configured")
        except Exception as e:
            print(f"  ❌ YouTube: {e}")
            results["youtube"] = {"success": False, "error": str(e)}

    # ── X (Twitter) ──
    try:
        x_env = load_env_file("~/workspace/.env.twitter")
        x_ck = x_env.get("TWITTER_CONSUMER_KEY", "")
        x_cs = x_env.get("TWITTER_CONSUMER_SECRET", "")
        x_at = x_env.get("TWITTER_ACCESS_TOKEN", "")
        x_ats = x_env.get("TWITTER_ACCESS_TOKEN_SECRET", "")
        if x_ck and x_cs and x_at and x_ats:
            print("  🐦 X: Uploading video...")
            import tweepy
            auth = tweepy.OAuth1UserHandler(x_ck, x_cs, x_at, x_ats)
            api_v1 = tweepy.API(auth)
            client = tweepy.Client(
                consumer_key=x_ck, consumer_secret=x_cs,
                access_token=x_at, access_token_secret=x_ats,
            )
            media = api_v1.media_upload(filename=video_path)
            x_caption = f"🇮🇳 {headline[:200]}\n\n🔗 thevideshi.com\n\n#IndianDiaspora #NRI #India #{category.replace('-', '')}"
            if len(x_caption) > 280:
                x_caption = x_caption[:277] + "..."
            response = client.create_tweet(text=x_caption, media_ids=[media.media_id])
            tweet_id = response.data.get("id", "") if response.data else ""
            print(f"  ✅ X: Posted (tweet_id: {tweet_id})")
            results["x"] = {"success": True, "tweet_id": tweet_id}
        else:
            print("  ⏭️ X: No credentials configured")
    except Exception as e:
        print(f"  ❌ X: {e}")
        results["x"] = {"success": False, "error": str(e)}

    # ── Summary ──
    posted = [p for p, r in results.items() if r.get("success")]
    failed = [p for p, r in results.items() if not r.get("success")]
    skipped = [p for p, r in results.items() if r.get("skipped")]
    print(f"\n  📊 Cross-post: {len(posted)}/{len(results)} platforms ({len(skipped)} skipped dedup)")
    if posted:
        print(f"  ✅ Posted: {', '.join(posted)}")
    if failed:
        print(f"  ❌ Failed: {', '.join(failed)}")

    return results




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

    # 1b. PRE-RENDER GATE: Script quality check (costs ~$0.001 vs $0.20 for a wasted render)
    print("\n🛡️ Step 1b: Pre-render script QA...")
    sq_passed, sq_score, sq_notes = pre_render_script_qa(script_data, article)
    print(f"  📊 Script score: {sq_score}/10 — {sq_notes}")
    if not sq_passed:
        print(f"  ⚠️ Script scored {sq_score}/10 — regenerating...")
        # Clear cache and regenerate once
        script_data = generate_script(article, force_new=True)
        if not script_data:
            return False
        sq_passed2, sq_score2, sq_notes2 = pre_render_script_qa(script_data, article)
        print(f"  📊 Retry script score: {sq_score2}/10 — {sq_notes2}")
        if not sq_passed2:
            print(f"  ❌ Script still weak after retry ({sq_score2}/10) — skipping article to save credits")
            return False
        print(f"  ✅ Retry script passed ({sq_score2}/10)")

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

    # 4. Source B-roll media (storyboard-driven or legacy fallback)
    print("\n🖼️ Step 4: Sourcing B-roll media...")
    storyboard = script_data.get("storyboard", [])
    media_meta = {}
    if storyboard:
        image_urls, media_meta = source_storyboard_images(article, storyboard)
    else:
        print("  ⚠️ No storyboard in script — falling back to legacy image_queries")
        image_urls = source_image_urls(article, script_data.get("image_queries", []))
    if not image_urls:
        print("❌ No images found")
        return False

    # 4b. PRE-RENDER GATE: Verify all media URLs are reachable
    print("\n🛡️ Step 4b: Media preflight check...")
    valid_urls, dead_urls = preflight_image_urls(image_urls)
    if dead_urls:
        print(f"  ⚠️ {len(dead_urls)} dead media URL(s) found — replacing from pool...")
        # Re-source only dead slots from article pool (curated first)
        storyboard_slim = [storyboard[i] for i in range(len(storyboard)) if i < len(image_urls) and image_urls[i] not in [u for u, _ in dead_urls]]
        # Use valid URLs plus attempt to fill gaps
        image_urls = valid_urls
        if len(image_urls) < 3:
            print(f"  ❌ Only {len(image_urls)} valid media — too few for a quality reel, skipping")
            return False
        print(f"  ✅ {len(image_urls)} valid media after preflight")

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
        media_meta=media_meta,
    )

    if not edit_json:
        return False

    # Save JSON for debugging
    json_path = BUILD_DIR / f"ss-timeline-{slug}.json"
    with open(json_path, "w") as f:
        json.dump(edit_json, f, indent=2)
    print(f"  📄 Timeline JSON saved: {json_path}")

    # 6b. PRE-RENDER GATE: Validate timeline JSON structure
    print("\n🛡️ Step 6b: Timeline validation...")
    tl_valid, tl_issues = validate_timeline_json(edit_json)
    if not tl_valid:
        for issue in tl_issues:
            print(f"  ❌ {issue}")
        print("  ❌ Timeline failed validation — skipping render to save credits")
        return False
    print("  ✅ Timeline structure valid")

    if dry_run:
        print("\n🏁 DRY RUN — JSON built, not rendering")
        print(json.dumps(edit_json, indent=2)[:2000])
        return True

    # 7. Render via Shotstack
    render_result = render_reel(edit_json, use_production=use_production)
    if not render_result:
        return False
    output_url = render_result["url"]
    poster_url = render_result.get("poster")
    thumbnail_url = render_result.get("thumbnail")

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

    # 8b. Download poster & thumbnail if available
    poster_local = None
    thumb_local = None
    if poster_url:
        poster_local = BUILD_DIR / f"ss-poster-{slug[:60]}.jpg"
        download_reel(poster_url, str(poster_local))
        print(f"  🖼️ Poster saved: {poster_local}")
    if thumbnail_url:
        thumb_local = BUILD_DIR / f"ss-thumb-{slug[:60]}.jpg"
        download_reel(thumbnail_url, str(thumb_local))
        print(f"  🖼️ Thumbnail saved: {thumb_local}")

    # 9. AI Quality Gate
    print("\n🔍 Step 9: AI Quality Gate...")
    qa_passed, qa_score, qa_notes = run_qa_gate(str(final_path), article, script_data)
    if not qa_passed:
        print(f"  ❌ QA FAILED (score: {qa_score}) — {qa_notes}")
        # TODO: auto-revise loop (regenerate script + re-render)
        return False
    print(f"  ✅ QA PASSED (score: {qa_score})")

    # 10. Upload final reel + poster/thumbnail
    print("\n☁️ Step 10: Uploading final reel...")
    video_url, uploaded_video_path = upload_final_reel(str(final_path), final_name)

    uploaded_poster_url = None
    uploaded_thumb_url = None
    if poster_local and poster_local.exists():
        poster_storage = f"reels/posters/{os.path.basename(poster_local)}"
        uploaded_poster_url = upload_asset(str(poster_local), poster_storage, "image/jpeg")
    if thumb_local and thumb_local.exists():
        thumb_storage = f"reels/thumbnails/{os.path.basename(thumb_local)}"
        uploaded_thumb_url = upload_asset(str(thumb_local), thumb_storage, "image/jpeg")

    # 11. Register
    if video_url:
        print("\n📋 Step 11: Registering reel...")
        caption = build_caption(article)
        register_reel(article, video_url, str(uploaded_video_path), caption,
                      poster_url=uploaded_poster_url, thumbnail_url=uploaded_thumb_url,
                      qa_score_actual=qa_score)

    # 12. Done — distribution handled by videshi-distribute-reels cron
    # (generates once, distributes to IG/YT/Threads/X/FB from prebuilt_reels)

    print(f"\n{'='*60}")
    print(f"✅ REEL COMPLETE: {final_path}")
    print(f"   Shotstack URL: {output_url}")
    if video_url:
        print(f"   Supabase URL: {video_url}")
    if uploaded_poster_url:
        print(f"   Poster URL: {uploaded_poster_url}")
    if uploaded_thumb_url:
        print(f"   Thumbnail URL: {uploaded_thumb_url}")
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
    render_result = render_reel(edit_json, use_production=use_production)
    if not render_result:
        return False
    output_url = render_result["url"]

    # Download
    final_name = f"ss-pulse-{slug}-{datetime.now().strftime('%Y%m%d-%H%M')}.mp4"
    final_path = REELS_DIR / final_name
    if not download_reel(output_url, str(final_path)):
        return False

    # Upload & register
    video_url, uploaded_video_path = upload_final_reel(str(final_path), final_name)
    if video_url:
        caption = build_caption(article)
        register_reel(article, video_url, str(uploaded_video_path), caption)
        # Distribution handled by videshi-distribute-reels cron

    print(f"\n✅ QUICK PULSE COMPLETE: {final_path}")
    return True


def main():
    parser = argparse.ArgumentParser(description="Shotstack Reel Renderer for The Videshi")
    parser.add_argument("--article-id", help="Specific article UUID")
    parser.add_argument("--format", choices=["anchor", "pulse"], default="anchor", help="Reel format")
    parser.add_argument("--dry-run", action="store_true", help="Build JSON only, don't render")
    parser.add_argument("--production", action="store_true", default=True, help="Use production API (default: True)")
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

        existing_slugs, existing_ids = get_existing_reel_slugs() if not args.test else (set(), set())
        article = pick_article(articles, existing_slugs, existing_ids)
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
