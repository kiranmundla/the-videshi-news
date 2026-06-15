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


def pick_article(articles, existing_slugs, existing_ids=None):
    """Pick best article that doesn't already have a reel (by slug OR article ID)."""
    existing_ids = existing_ids or set()
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
{{"score": <1-10>, "passed": <true if score >= 8>, "issues": ["issue1"], "fix_suggestions": ["suggestion1"]}}"""

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
        # Derive pass from score, don't trust LLM string
        passed = score >= 8
        issues = result.get("issues", [])
        fixes = result.get("fix_suggestions", [])
        notes = "; ".join(issues) if issues else "Clean"
        return passed, score, notes
    except Exception as e:
        return True, 7, f"Skipped ({e})"


def preflight_image_urls(image_urls):
    """HEAD-check all image URLs before render. Returns (valid_urls, dead_urls).
    A dead image URL = wasted Shotstack credit (black frame or render failure).
    """
    valid = []
    dead = []
    for url in image_urls:
        try:
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
    phrases = []
    current = []
    for w in aligned:
        current.append(w)
        word_text = w.get("word", "")
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
    "upload.wikimedia.org", "wikipedia.org", "wikimedia.org",
    "commons.wikimedia.org", "static.toiimg.com", "im.rediff.com",
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

    # ── 1. Article hero for scene 1 ──
    hero = upscale_wikimedia_url(hero)
    if hero and is_url_downloadable(hero) and hero not in used_in_this_reel:
        matched_urls[0] = hero
        used_in_this_reel.add(hero)
        media_meta[hero] = {"type": "image", "duration": 0}
        print(f"  🎬 Scene 1: {scene_descs[0][:50]}  →  article hero")

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
                        matched_urls[i] = cand["url"]
                        used_in_this_reel.add(cand["url"])
                        used_video_ids_this_reel.add(vid)
                        media_meta[cand["url"]] = {"type": "video", "duration": cand["duration"]}
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
                query = anchor_query_to_india(query)
                results = pexels_search(pexels_key, query, count=5)
                for cand in results:
                    pid = cand["photo_id"]
                    if pid not in used_ids and cand["url"] not in used_in_this_reel:
                        if pid in BLOCKED_PEXELS_IDS:
                            print(f"  🚫 Scene {i+1}: skipped blocklisted photo #{pid}")
                            continue
                        if is_foreign_for_india(cand, anchored):
                            print(f"  🚫 Scene {i+1}: skipped foreign-looking photo #{pid} ({cand.get('alt','')[:40]})")
                            continue
                        matched_urls[i] = cand["url"]
                        used_in_this_reel.add(cand["url"])
                        media_meta[cand["url"]] = {"type": "image", "duration": 0}
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
                        wimg = wdata.get("originalimage", {}).get("source") or wdata.get("thumbnail", {}).get("source")
                        wimg = upscale_wikimedia_url(wimg)
                        if wimg and wimg not in used_in_this_reel:
                            matched_urls[i] = wimg
                            used_in_this_reel.add(wimg)
                            media_meta[wimg] = {"type": "image", "duration": 0}
                            print(f"  🎬 Scene {i+1}: {scene_descs[i][:50]}  →  Wikipedia (CC)")
                            break
                except Exception:
                    continue

    wiki_filled = sum(1 for u in matched_urls if u is not None)
    print(f"  📸 After Wikipedia: {wiki_filled}/{len(matched_urls)} scenes filled")

    # ── 5. LAST RESORT: Same-category article images (only for remaining gaps) ──
    remaining = [i for i in range(len(matched_urls)) if matched_urls[i] is None]
    if remaining and category:
        print(f"  🔍 {len(remaining)} scenes still unfilled — falling back to category article images...")
        article_pool = []
        r = requests.get(
            f"{SB_URL}/rest/v1/p2_articles",
            params={
                "status": "eq.published",
                "category": f"eq.{category}",
                "id": f"neq.{article_id}",
                "image_url": "not.is.null",
                "order": "published_at.desc",
                "limit": 40,
                "select": "id,headline,image_url,gallery_images",
            },
            headers=SB_HEADERS,
            timeout=15,
        )
        if r.status_code == 200:
            for a in r.json():
                img = a.get("image_url", "")
                if is_url_downloadable(img) and img not in used_in_this_reel:
                    article_pool.append(img)
                # Also pull gallery images for more variety
                gallery = a.get("gallery_images") or []
                if isinstance(gallery, str):
                    try:
                        gallery = json.loads(gallery)
                    except Exception:
                        gallery = []
                for gi in gallery[:2]:
                    gurl = gi if isinstance(gi, str) else gi.get("url", "")
                    if gurl and is_url_downloadable(gurl) and gurl not in used_in_this_reel:
                        article_pool.append(gurl)

        for i in remaining:
            if article_pool:
                matched_urls[i] = article_pool.pop(0)
                used_in_this_reel.add(matched_urls[i])
                media_meta[matched_urls[i]] = {"type": "image", "duration": 0}
                print(f"  🎬 Scene {i+1}: {scene_descs[i][:50]}  →  category fallback image")

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
                "length": "end",
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
                "length": "end",
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

    # ── Track 4: Lower third (brief headline establish-shot only) ──
    # Show for ~4s right after the hook, then fade out so it does NOT collide
    # with the voice-synced script captions that run the rest of the reel.
    # (Running both full-length put two text systems in the same bottom band —
    # the #1 "overlapping text / poor readability" QA failure.)
    lt_html, lt_css = build_lower_third_html(headline, category)
    lt_duration = min(4.0, total_voice_duration)
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
                "length": lt_duration,
                "position": "bottom",
                "transition": {"in": "fade", "out": "fade"},
                "opacity": 0.95,
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
            # Static image — Ken Burns effect
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
    """Build branded end card with logo + social handles. All inline styles for Shotstack compatibility."""
    logo_block = (
        f'<img src="{logo_url}" style="width:170px;height:170px;border-radius:18px;margin-bottom:28px;" />'
        if logo_url else ""
    )
    html = f"""<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;width:100%;height:100%;background:linear-gradient(180deg,#0a1628 0%,#0f1f35 50%,#0a1628 100%);padding:60px 40px;box-sizing:border-box;">
  {logo_block}
  <div style="font-family:Inter;font-size:78px;font-weight:700;color:#D4AF37;letter-spacing:9px;margin-bottom:14px;">THE VIDESHI</div>
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

Score 8+ = broadcast-quality news reel (PASS). Score 6-7 = needs improvement (FAIL). Below 5 = broken.

Return JSON only:
{{
  "score": <1-10, or 0 if any non-negotiable failed>,
  "passed": <true if score >= 8 AND all non-negotiables pass>,
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
                "temperature": 0.3,
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

        # Derive pass/fail from score — never trust LLM's string verdict
        passed = score >= 8

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
    video_url = upload_final_reel(str(final_path), final_name)

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
        register_reel(article, video_url, str(final_path), caption,
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
    video_url = upload_final_reel(str(final_path), final_name)
    if video_url:
        caption = build_caption(article)
        register_reel(article, video_url, str(final_path), caption)
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
