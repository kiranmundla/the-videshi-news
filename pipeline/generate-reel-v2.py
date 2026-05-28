#!/usr/bin/env python3
"""
The Videshi — Reel Generator v2
Playwright-based HTML/CSS animation → video recording.
Produces 15-20s vertical reels (1080x1920) for IG/YouTube Shorts.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

# ── Config ──────────────────────────────────────────────────────────────────
W, H = 1080, 1920
TOTAL_DUR_MS = 22000  # 22 seconds of animation
OUTPUT_DIR = Path(__file__).parent / "reels"
OUTPUT_DIR.mkdir(exist_ok=True)

SUPABASE_URL = "https://lboecaekpynbpyijrbfz.supabase.co"

CATEGORY_EMOJI = {
    "news": "🇮🇳", "immigration": "🛂", "nri-world": "🌏", "travel": "✈️",
    "lifestyle-health": "🧘", "markets": "📈", "technology": "💻",
    "sports": "🏏", "entertainment": "🎬", "food": "🍛",
}

CATEGORY_COLORS = {
    "news": {"accent": "#D4A847", "g1": "#0a1628", "g2": "#1a2744"},
    "immigration": {"accent": "#4ECDC4", "g1": "#0a1a2e", "g2": "#163040"},
    "sports": {"accent": "#FF6B35", "g1": "#1a0a0a", "g2": "#2d1515"},
    "entertainment": {"accent": "#E040FB", "g1": "#1a0a28", "g2": "#2d1540"},
    "travel": {"accent": "#26C6DA", "g1": "#0a1a1e", "g2": "#142d30"},
    "markets": {"accent": "#66BB6A", "g1": "#0a1a10", "g2": "#152d18"},
    "technology": {"accent": "#42A5F5", "g1": "#0a1028", "g2": "#151d40"},
    "lifestyle-health": {"accent": "#AB47BC", "g1": "#1a0a20", "g2": "#2d1535"},
    "food": {"accent": "#FF7043", "g1": "#1a1008", "g2": "#2d2010"},
    "nri-world": {"accent": "#26A69A", "g1": "#0a1a1a", "g2": "#152d2d"},
}

DEFAULT_COLORS = {"accent": "#D4A847", "g1": "#0a1628", "g2": "#1a2744"}


def load_env():
    load_dotenv(os.path.expanduser("~/workspace/.env.supabase"))
    return os.environ["SUPABASE_SERVICE_ROLE_KEY"]


def fetch_article(slug: str, sb_key: str) -> dict:
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers={"apikey": sb_key, "Authorization": f"Bearer {sb_key}"},
        params=f"slug=ilike.*{slug}*&limit=1&select=id,slug,headline,subheadline,category,image_url",
        timeout=15,
    )
    r.raise_for_status()
    data = r.json()
    if not data:
        print(f"❌ No article found for slug: {slug}")
        sys.exit(1)
    return data[0]


def split_takeaways(subheadline: str) -> list[str]:
    if not subheadline:
        return []
    parts = re.split(r'(?<=[.!])\s+', subheadline.strip())
    bullets = [p.strip() for p in parts if len(p.strip()) > 15]
    return bullets[:3]


def extract_stats(subheadline: str) -> list[dict]:
    stats = []
    for m in re.finditer(r'(₹[\d,.]+(?:\s*(?:per|/)\s*\w+)?)', subheadline):
        stats.append({"value": m.group(1), "type": "currency"})
    for m in re.finditer(r'([\d,.]+\s*(?:percent|per cent|%))', subheadline, re.IGNORECASE):
        stats.append({"value": m.group(1), "type": "percent"})
    for m in re.finditer(r'(\d+)\s+(times?|days?|hikes?|states?|cities)', subheadline, re.IGNORECASE):
        stats.append({"value": m.group(0), "type": "count"})
    return stats[:3]


def shorten_headline(headline: str, max_chars: int = 100) -> str:
    if len(headline) > max_chars and "—" in headline:
        headline = headline.split("—")[0].strip()
    if len(headline) > max_chars and "." in headline:
        parts = headline.split(".")
        headline = parts[0].strip() + "."
    return headline[:max_chars]


def esc(s: str) -> str:
    """Escape HTML special chars."""
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def generate_html(article: dict) -> str:
    cat = article.get("category", "news")
    colors = CATEGORY_COLORS.get(cat, DEFAULT_COLORS)
    accent = colors["accent"]
    g1 = colors["g1"]
    g2 = colors["g2"]
    emoji = CATEGORY_EMOJI.get(cat, "📰")
    cat_label = cat.replace("-", " ").upper()

    headline = article.get("headline", "")
    short_hl = esc(shorten_headline(headline, 50))
    # Dynamic font size based on headline length
    hl_len = len(short_hl)
    if hl_len <= 25:
        hl_font = 160
    elif hl_len <= 35:
        hl_font = 140
    elif hl_len <= 50:
        hl_font = 120
    else:
        hl_font = 100
    subheadline = article.get("subheadline", "")
    takeaways = split_takeaways(subheadline)
    stats = extract_stats(subheadline)
    image_url = article.get("image_url", "")

    # Takeaway HTML for scene 2
    takeaway_html = ""
    for i, t in enumerate(takeaways):
        delay = 7.0 + i * 3.5
        takeaway_html += f'''
        <div class="tk-item" style="animation-delay:{delay}s">
            <div class="tk-dot"></div>
            <div class="tk-text">{esc(t)}</div>
        </div>'''

    # Stat badges
    stat_html = ""
    if stats:
        for i, s in enumerate(stats[:2]):
            delay = 5.8 + i * 0.8
            stat_html += f'''<div class="stat" style="animation-delay:{delay}s">{esc(s["value"])}</div>'''

    # Scene 2 image section (only if image exists)
    scene2_image = ""
    if image_url:
        scene2_image = f'''
    <div class="s2-img" style="background-image:url('{image_url}')"></div>
    <div class="s2-img-grad"></div>'''

    html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Playfair+Display:wght@700;800;900&display=swap');

*{{margin:0;padding:0;box-sizing:border-box}}

body{{
  width:{W}px;height:{H}px;overflow:hidden;
  font-family:'Inter',sans-serif;
  background:{g1};color:#fff;
}}

/* ══════ SCENE 1 — HOOK (0-4.5s) ══════ */
.s1{{
  position:absolute;inset:0;z-index:10;
  display:flex;flex-direction:column;
  justify-content:flex-start;
  padding:280px 56px 0;
  background:linear-gradient(160deg,{g1} 0%,{g2} 50%,{g1} 100%);
  animation:fadeOut .6s ease-in 4.7s forwards;
}}
.s1-dots{{
  position:absolute;inset:0;opacity:.03;
  background-image:radial-gradient(circle,{accent} 1px,transparent 1px);
  background-size:48px 48px;
  animation:drift 10s ease-in-out infinite;
}}
.brand{{
  position:absolute;top:72px;left:72px;
  font-family:'Playfair Display',serif;
  font-size:36px;font-weight:800;letter-spacing:4px;
  opacity:0;animation:slideDown .5s ease-out .15s forwards;
}}
.badge{{
  display:inline-flex;align-items:center;gap:10px;
  padding:10px 26px;
  background:{accent}20;border:1px solid {accent}40;
  border-radius:100px;
  font-size:24px;font-weight:700;letter-spacing:3px;color:{accent};
  opacity:0;animation:slideUp .5s ease-out .4s forwards;
  margin-bottom:28px;
}}
.hl-wrap{{
  opacity:0;animation:headIn .8s ease-out .7s forwards;
}}
.hl{{
  font-family:'Playfair Display',serif;
  font-size:{hl_font}px;font-weight:900;line-height:1.08;
}}
.hl-line{{
  width:0;height:4px;margin-top:32px;
  background:linear-gradient(90deg,{accent},{accent}00);
  animation:lineGrow .7s ease-out 1.6s forwards;
}}

/* ══════ SCENE 2 — FACTS (4.5-12.5s) ══════ */
.s2{{
  position:absolute;inset:0;z-index:5;
  background:{g1};
  opacity:0;animation:fadeIn .6s ease-out 4.7s forwards;
}}
.s2-img{{
  position:absolute;inset:0;
  background-size:cover;background-position:center top;
  transform:scale(1);
  animation:slowZoom 12s ease-in-out 5s forwards;
}}
.s2-img-grad{{
  position:absolute;inset:0;
  background:{g1}cc;
  z-index:1;
}}
.s2-content{{
  position:absolute;top:0;bottom:0;left:0;right:0;
  display:flex;flex-direction:column;
  justify-content:center;
  padding:0 56px;
  z-index:2;
}}
.stats-row{{
  display:flex;gap:14px;flex-wrap:wrap;
  margin-bottom:28px;
}}
.stat{{
  padding:10px 26px;
  background:{accent}15;border:1.5px solid {accent}55;
  border-radius:10px;
  font-size:28px;font-weight:800;color:{accent};
  opacity:0;animation:popIn .4s ease-out forwards;
}}
.tk-item{{
  display:flex;align-items:flex-start;gap:20px;
  margin-bottom:36px;
  opacity:0;transform:translateX(-24px);
  animation:slideRight .5s ease-out forwards;
}}
.tk-dot{{
  width:18px;height:18px;border-radius:50%;
  background:{accent};margin-top:18px;flex-shrink:0;
}}
.tk-text{{
  font-size:64px;font-weight:700;line-height:1.3;
  color:#fff;
}}

/* ══════ SCENE 3 — CTA (12.5-17s) ══════ */
.s3{{
  position:absolute;inset:0;z-index:3;
  display:flex;flex-direction:column;
  align-items:center;justify-content:center;
  background:linear-gradient(160deg,{g1},{g2});
  opacity:0;pointer-events:none;
  animation:ctaIn .5s ease-out 17s forwards;
}}
.s3-name{{
  font-family:'Playfair Display',serif;
  font-size:68px;font-weight:900;letter-spacing:3px;
  opacity:0;animation:slideUp .6s ease-out 17.1s forwards;
}}
.s3-tag{{
  font-size:24px;font-weight:500;
  color:rgba(255,255,255,.55);margin-top:10px;
  opacity:0;animation:slideUp .4s ease-out 17.4s forwards;
}}
.s3-div{{
  width:0;height:2px;background:{accent};
  margin:36px 0;
  animation:lineGrow .4s ease-out 17.6s forwards;
}}
.s3-url{{
  font-size:38px;font-weight:800;color:{accent};
  opacity:0;animation:slideUp .4s ease-out 17.8s forwards;
}}
.s3-socials{{
  margin-top:44px;display:flex;flex-direction:column;
  align-items:center;gap:16px;
  opacity:0;animation:slideUp .4s ease-out 18.1s forwards;
}}
.s3-soc{{
  font-size:22px;font-weight:500;color:rgba(255,255,255,.45);
}}
.s3-soc b{{color:rgba(255,255,255,.7);font-weight:700}}

/* ══════ KEYFRAMES ══════ */
@keyframes slideUp{{
  from{{opacity:0;transform:translateY(36px)}}
  to{{opacity:1;transform:translateY(0)}}
}}
@keyframes slideDown{{
  from{{opacity:0;transform:translateY(-24px)}}
  to{{opacity:1;transform:translateY(0)}}
}}
@keyframes slideRight{{
  from{{opacity:0;transform:translateX(-24px)}}
  to{{opacity:1;transform:translateX(0)}}
}}
@keyframes headIn{{
  from{{opacity:0;transform:translateY(40px) scale(.97)}}
  to{{opacity:1;transform:translateY(0) scale(1)}}
}}
@keyframes lineGrow{{
  from{{width:0}}to{{width:160px}}
}}
@keyframes fadeOut{{
  to{{opacity:0;visibility:hidden}}
}}
@keyframes fadeIn{{
  to{{opacity:1}}
}}
@keyframes ctaIn{{
  to{{opacity:1;z-index:20;pointer-events:auto}}
}}
@keyframes slowZoom{{
  from{{transform:scale(1)}}to{{transform:scale(1.08)}}
}}
@keyframes popIn{{
  from{{opacity:0;transform:scale(.85)}}
  to{{opacity:1;transform:scale(1)}}
}}
@keyframes drift{{
  0%,100%{{transform:translate(0,0)}}
  50%{{transform:translate(8px,8px)}}
}}
</style></head>
<body>

<!-- SCENE 1 -->
<div class="s1">
  <div class="s1-dots"></div>
  <div class="brand">THE VIDESHI</div>
  <div>
    <div class="badge"><span>{emoji}</span><span>{cat_label}</span></div>
    <div class="hl-wrap"><h1 class="hl">{short_hl}</h1></div>
    <div class="hl-line"></div>
  </div>
</div>

<!-- SCENE 2 -->
<div class="s2">
  {scene2_image}
  <div class="s2-content">
    {"<div class='stats-row'>" + stat_html + "</div>" if stat_html else ""}
    {takeaway_html}
  </div>
</div>

<!-- SCENE 3 -->
<div class="s3">
  <div class="s1-dots"></div>
  <div class="s3-name">THE VIDESHI</div>
  <div class="s3-tag">News for the Global Indian Diaspora</div>
  <div class="s3-div"></div>
  <div class="s3-url">TheVideshi.com</div>
  <div class="s3-socials">
    <div class="s3-soc">📸 Instagram · <b>@the.videshi</b></div>
    <div class="s3-soc">𝕏  X · <b>@thevideshi</b></div>
    <div class="s3-soc">🎬 YouTube · <b>@the.videshi</b></div>
    <div class="s3-soc">🧵 Threads · <b>@the.videshi</b></div>
  </div>
</div>

</body></html>"""
    return html


def record_video(html_path: str, output_webm_dir: str) -> str:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path="/usr/local/bin/google-chrome",
            headless=True,
            args=["--no-sandbox", "--disable-gpu"],
        )
        ctx = browser.new_context(
            viewport={"width": W, "height": H},
            record_video_dir=output_webm_dir,
            record_video_size={"width": W, "height": H},
        )
        page = ctx.new_page()
        page.goto(f"file://{html_path}", wait_until="networkidle")
        # Small pause to let fonts load
        page.wait_for_timeout(500)
        # Now wait for animation duration
        page.wait_for_timeout(TOTAL_DUR_MS + 1000)
        ctx.close()
        browser.close()

    webms = [f for f in os.listdir(output_webm_dir) if f.endswith(".webm")]
    if not webms:
        raise RuntimeError("No video recorded!")
    return os.path.join(output_webm_dir, webms[0])


def _pick_music_track(category: str = "", headline: str = "") -> str | None:
    """Pick background music based on article category/tone.
    
    Mood mapping:
    - Upbeat: Entertainment, Sports, Technology, Lifestyle, Food, Travel
    - Breaking/News: News, NRI World, Markets & Finance, general
    - Dramatic: sad/tragic/death/crisis/disaster keywords in headline
    - Indian beat: Culture, festivals, heritage, Bollywood
    """
    import random
    music_dir = os.path.join(os.path.dirname(__file__), "music")
    if not os.path.isdir(music_dir):
        return None

    cat_lower = (category or "").lower()
    headline_lower = (headline or "").lower()

    # Detect sad/dramatic tone from headline keywords
    dramatic_keywords = ["death", "dies", "killed", "tragedy", "tragic", "crisis",
                         "disaster", "flood", "earthquake", "attack", "victim",
                         "mourns", "fatal", "crash", "devastat", "war", "conflict"]
    is_dramatic = any(kw in headline_lower for kw in dramatic_keywords)

    # Detect Indian cultural content
    indian_keywords = ["bollywood", "festival", "diwali", "holi", "navratri",
                       "puja", "temple", "classical", "dance", "rangoli",
                       "garba", "bhangra", "cricket", "ipl"]
    is_indian = any(kw in headline_lower for kw in indian_keywords)

    if is_dramatic:
        pool = ["pixabay-dramatic-30s.mp3"]
    elif is_indian or cat_lower in ["entertainment", "food"]:
        pool = ["indian-beat-30s.mp3", "pixabay-upbeat-30s.mp3"]
    elif cat_lower in ["sports", "technology", "lifestyle & health", "travel"]:
        pool = ["pixabay-upbeat-30s.mp3"]
    elif cat_lower in ["news", "nri world", "markets & finance"]:
        pool = ["pixabay-breaking-30s.mp3"]
    else:
        # Default: mix of breaking news and upbeat
        pool = ["pixabay-breaking-30s.mp3", "pixabay-upbeat-30s.mp3"]

    # Verify files exist, fall back to any 15s track
    pool = [f for f in pool if os.path.isfile(os.path.join(music_dir, f))]
    if not pool:
        all_15s = [f for f in os.listdir(music_dir) if f.endswith(".mp3") and "15s" in f]
        pool = all_15s if all_15s else [f for f in os.listdir(music_dir) if f.endswith(".mp3")]

    if not pool:
        return None
    return os.path.join(music_dir, random.choice(pool))


def convert_to_mp4(webm_path: str, mp4_path: str, category: str = "", headline: str = ""):
    music = _pick_music_track(category=category, headline=headline)

    if music:
        # Two-pass: first convert video, then mix audio
        tmp_video = mp4_path + ".tmp.mp4"
        cmd_video = [
            "ffmpeg", "-y",
            "-ss", "0.7",
            "-i", webm_path,
            "-t", "17",
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "23",
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
            "-an",
            tmp_video,
        ]
        result = subprocess.run(cmd_video, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            print(f"ffmpeg video error: {result.stderr[-500:]}")
            raise RuntimeError("ffmpeg video conversion failed")

        # Mix music: fade in 0.5s, fade out last 2s, volume at 70%
        cmd_audio = [
            "ffmpeg", "-y",
            "-i", tmp_video,
            "-i", music,
            "-filter_complex",
            "[1:a]atrim=0:22,afade=t=in:st=0:d=0.5,afade=t=out:st=20:d=2,volume=0.7[bg];[bg]apad[a]",
            "-map", "0:v", "-map", "[a]",
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "128k",
            "-shortest",
            "-movflags", "+faststart",
            mp4_path,
        ]
        result = subprocess.run(cmd_audio, capture_output=True, text=True, timeout=120)
        os.remove(tmp_video)
        if result.returncode != 0:
            print(f"ffmpeg audio mix error: {result.stderr[-500:]}")
            print("  Falling back to video-only...")
            # Fallback: just rename the tmp if it existed, or redo without audio
            cmd_fallback = [
                "ffmpeg", "-y", "-ss", "0.7", "-i", webm_path,
                "-t", "17", "-c:v", "libx264", "-preset", "medium",
                "-crf", "23", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                "-an", mp4_path,
            ]
            subprocess.run(cmd_fallback, capture_output=True, text=True, timeout=120)
        else:
            print(f"  🎵 Music: {os.path.basename(music)}")
    else:
        cmd = [
            "ffmpeg", "-y",
            "-ss", "0.7",
            "-i", webm_path,
            "-t", "17",
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "23",
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
            "-an",
            mp4_path,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            print(f"ffmpeg error: {result.stderr[-500:]}")
            raise RuntimeError("ffmpeg conversion failed")


def extract_frames(mp4_path: str, out_dir: str) -> list[str]:
    os.makedirs(out_dir, exist_ok=True)
    times = [1, 3, 6, 9, 13, 15]
    paths = []
    for t in times:
        out = os.path.join(out_dir, f"frame_{t:02d}s.jpg")
        subprocess.run([
            "ffmpeg", "-y", "-ss", str(t), "-i", mp4_path,
            "-frames:v", "1", "-q:v", "2", out
        ], capture_output=True, timeout=30)
        if os.path.exists(out):
            paths.append(out)
    return paths


def main():
    parser = argparse.ArgumentParser(description="The Videshi Reel Generator v2")
    parser.add_argument("--slug", required=True, help="Article slug (or partial)")
    parser.add_argument("--upload", action="store_true", help="Upload to Supabase")
    args = parser.parse_args()

    print("🎬 The Videshi Reel Generator v2")
    print(f"   Slug: {args.slug}\n")

    sb_key = load_env()
    print("📡 Fetching article...")
    article = fetch_article(args.slug, sb_key)
    print(f"   ✅ {article['headline'][:80]}...")
    print(f"   Category: {article['category']}\n")

    slug = article["slug"]

    print("🎨 Generating HTML...")
    html = generate_html(article)
    html_dir = tempfile.mkdtemp()
    html_path = os.path.join(html_dir, "reel.html")
    with open(html_path, "w") as f:
        f.write(html)
    print(f"   ✅ {html_path}\n")

    print("📹 Recording (~20s)...")
    t0 = time.time()
    webm_dir = tempfile.mkdtemp()
    webm_path = record_video(html_path, webm_dir)
    print(f"   ✅ {time.time()-t0:.1f}s ({os.path.getsize(webm_path)/1024:.0f}KB webm)\n")

    print("🔄 Converting to MP4...")
    t0 = time.time()
    mp4_name = f"reel-{slug[:80]}.mp4"
    mp4_path = str(OUTPUT_DIR / mp4_name)
    convert_to_mp4(webm_path, mp4_path, category=article.get("category", ""), headline=article.get("headline", ""))
    mb = os.path.getsize(mp4_path) / (1024*1024)
    print(f"   ✅ {mb:.1f}MB ({time.time()-t0:.1f}s)\n   {mp4_path}\n")

    print("🖼️  Frames...")
    frame_dir = str(OUTPUT_DIR / f"preview-{slug[:40]}")
    frames = extract_frames(mp4_path, frame_dir)
    for fp in frames:
        print(f"   📸 {fp}")

    if args.upload:
        print("\n☁️  Uploading...")
        storage_path = f"reels/{mp4_name}"
        with open(mp4_path, "rb") as f:
            r = requests.post(
                f"{SUPABASE_URL}/storage/v1/object/article-images/{storage_path}",
                headers={
                    "apikey": sb_key, "Authorization": f"Bearer {sb_key}",
                    "Content-Type": "video/mp4", "x-upsert": "true",
                },
                data=f.read(),
            )
        if r.status_code in (200, 201):
            print(f"   ✅ {SUPABASE_URL}/storage/v1/object/public/article-images/{storage_path}")
        else:
            print(f"   ❌ {r.status_code}: {r.text[:200]}")

    print(f"\n✅ Done! {mp4_path}")
    return mp4_path


if __name__ == "__main__":
    main()
